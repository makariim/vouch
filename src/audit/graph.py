"""The audit as a LangGraph state graph (decision 0001).

    extract -> search -> judge -> verify -> (retry, or next requirement) -> report

Three things about LangGraph shape the code here, and they are worth naming
because this is the first LangGraph in the project:

1. **State is one typed dict, and nodes return partial updates.** A node never
   mutates state; it returns the keys it changed and LangGraph merges them.
2. **A reducer decides how a key merges.** Every key overwrites by default.
   `events` is annotated with `operator.add`, so each node's events are appended
   rather than replacing the list. That is what makes the trace accumulate.
3. **A conditional edge is how a decision becomes visible.** The retry loop is
   an edge chosen by a function, not an `if` buried in a node, which is what
   lets us point at the decision when asked where the agent decides anything.

Because every node returns its own events, streaming the graph with
`stream_mode="updates"` yields exactly the new events per step -- that is the
whole streaming implementation, see `run_stream`.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Iterator, TypedDict

from langgraph.graph import END, START, StateGraph

from . import events as ev
from .index import Line, LineIndex
from .ingest import index_resume
from .model import Model
from .product import is_required, summarise

# Decision: a requirement gets at most this many searches before we stop and
# record it rather than looping for ever. The brief fixes it at three.
MAX_ATTEMPTS = 3


class AuditError(Exception):
    """Input we refuse to audit. Raised before any model call is made."""


class AuditState(TypedDict, total=False):
    post: str
    resume: str
    post_index: LineIndex
    resume_index: LineIndex

    requirements: list[dict[str, Any]]
    # A second pass over ONE requirement (decision 0006). Set means: audit
    # only this id, then report. Never called a retry -- decision 0007 is
    # explicit that a person asking for another pass and the agent deciding
    # mid-run are two different things, and naming them the same would be
    # claiming the agent did something a human did.
    only_id: int | None
    cursor: int  # which requirement we are on -- the loop counts these, not turns
    attempts: int  # searches spent on the current requirement
    tried: list[str]  # query terms already used for the current requirement
    seen: list[dict[str, Any]]  # lines already rejected for the current requirement

    retrieved: list[dict[str, Any]]
    judgement: dict[str, Any]
    next_action: str

    verdicts: list[dict[str, Any]]
    counts: dict[str, int]
    summary: dict[str, Any]
    events: Annotated[list[dict[str, Any]], operator.add]


def _as_lines(rows: list[dict[str, Any]]) -> list[Line]:
    return [Line(number=r["number"], text=r["text"]) for r in rows]


def _current(state: AuditState) -> dict[str, Any]:
    return state["requirements"][state["cursor"]]


def _resume_at(
    state: AuditState,
    requirements: list[dict[str, Any]],
    post_index: LineIndex,
    resume_index: LineIndex,
) -> dict[str, Any]:
    """Start the graph part-way in, on requirements that are already extracted.

    Everything downstream then behaves exactly as it does in a full run: the
    same search, judge and verify nodes, and the same retry edge. That is the
    reason a re-run is routed back through the graph rather than given a
    second, shorter copy of the control flow -- there stays one place where
    the audit decides anything, which is what decision 0001 points at.

    `verdicts` is deliberately not reset here. A re-run is seeded with the
    earlier verdicts for every OTHER requirement, so that when `report` runs
    it computes the summary over the whole audit rather than over the single
    requirement that was re-run.
    """
    only_id = state.get("only_id")
    if only_id is None:
        return {
            "post_index": post_index,
            "resume_index": resume_index,
            "requirements": requirements,
            "cursor": 0,
            "attempts": 0,
            "tried": [],
            "seen": [],
            "events": [ev.requirements_event(requirements)],
        }

    cursor = next(
        (i for i, r in enumerate(requirements) if r["id"] == only_id), None
    )
    if cursor is None:
        raise AuditError(f"no requirement {only_id} in this audit")

    return {
        "post_index": post_index,
        "resume_index": resume_index,
        "requirements": requirements,
        "cursor": cursor,
        "attempts": 0,
        "tried": [],
        "seen": [],
        # The client is told about the one requirement being re-run, not the
        # whole list it already holds. Decision 0006 says "the same event
        # stream ... for that one requirement" and does not settle which of
        # the two this means; see report 0012.
        "events": [ev.requirements_event([requirements[cursor]])],
    }


def build_nodes(model: Model) -> dict[str, Any]:
    """Node functions closed over the model, so the graph itself never knows
    whether it is talking to Anthropic or to a scripted stand-in."""

    def extract(state: AuditState) -> dict[str, Any]:
        post, resume = state["post"], state["resume"]

        # Checked here rather than in a node downstream so that an empty input
        # costs nothing and fails loudly, instead of producing an empty audit
        # that looks like a real result.
        if not post.strip():
            raise AuditError("post is empty")
        if not resume.strip():
            raise AuditError("resume is empty")

        # Repair before indexing, never after. The quotes we publish are
        # sliced out of this index, so if the index were built on the raw
        # extraction the line numbers in a verdict and the line numbers a
        # human reads in GET /resumes/{id} would drift apart. One seam,
        # `index_resume`, is what keeps them the same document.
        post_index = LineIndex(post)
        resume_index, repaired = index_resume(resume)

        given = state.get("requirements") or []
        if given:
            # A second pass (decision 0006). The requirement list came in with
            # the request, so extraction is skipped: no model call, and -- the
            # part that matters -- the ids cannot shift under the client,
            # because they are the same ids it was given. Re-extracting would
            # renumber the moment the model split one sentence differently,
            # and requirement 3 would silently become a different sentence.
            return _resume_at(state, given, post_index, resume_index)

        extraction = model.extract(post)

        requirements: list[dict[str, Any]] = []
        trace: list[dict[str, Any]] = []
        for raw in extraction.requirements:
            # The text we keep is sliced out of the post, not copied from the
            # model. A requirement we cannot find in the post is dropped and
            # said so -- inventing one is the failure this guards.
            canonical = post_index.locate(raw)
            if canonical is None:
                trace.append(
                    ev.step_event(0, "dropped", f"not found verbatim in the post: {raw!r}")
                )
                continue
            requirements.append(
                {
                    "id": len(requirements) + 1,
                    "text": canonical,
                    # Decision 0005. Decided from the post's words, not the
                    # model's opinion -- see product.is_required.
                    "required": is_required(canonical, post_index),
                }
            )

        if not requirements:
            raise AuditError("no requirements could be read from the post")

        # The repair step is announced AFTER the requirement list, not before
        # it. `requirements` being the first event of the stream is what the
        # page and the extension are written against, and repair is not worth
        # changing that for.
        repair_trace = (
            [
                ev.step_event(
                    0,
                    "repair",
                    f"{len(repaired.changes)} damaged line(s) mechanically repaired "
                    "before indexing",
                )
            ]
            if repaired.changes
            else []
        )

        # Through the same seam as a re-run, so that `only_id` is honoured
        # whether the requirement list was handed in or extracted just now.
        # Without this, asking to re-run requirement 3 of a post the backend
        # has never audited would quietly audit all of them.
        seeded = _resume_at(state, requirements, post_index, resume_index)
        seeded["events"] = trace + seeded["events"] + repair_trace
        return seeded

    def search(state: AuditState) -> dict[str, Any]:
        requirement = _current(state)
        tried = state.get("tried", [])
        chosen = model.choose_query(
            requirement["text"], tried, _as_lines(state.get("seen", []))
        )
        lines = state["resume_index"].search(chosen.query)

        detail = chosen.query if not tried else f"{chosen.query} ({chosen.reason})"
        return {
            "retrieved": [{"number": ln.number, "text": ln.text} for ln in lines],
            "tried": tried + [chosen.query],
            "attempts": state.get("attempts", 0) + 1,
            "events": [ev.step_event(requirement["id"], "search", detail)],
        }

    def judge(state: AuditState) -> dict[str, Any]:
        requirement = _current(state)
        result = model.judge(requirement["text"], _as_lines(state["retrieved"]))
        return {
            "judgement": result.model_dump(),
            "events": [
                ev.step_event(
                    requirement["id"], "judge", f"{result.verdict} -- {result.reason}"
                )
            ],
        }

    def verify(state: AuditState) -> dict[str, Any]:
        """Always runs, and is not the model's call (decision 0001).

        The quote is checked against the resume by line number. What we then
        emit is the resume's own text for that line, so the published quote is
        verbatim by construction rather than by trust.
        """
        requirement = _current(state)
        judgement = state["judgement"]
        resume_index = state["resume_index"]
        attempts = state.get("attempts", 0)
        trace: list[dict[str, Any]] = []

        verdict = judgement["verdict"]
        claimed_number = judgement.get("line_number")
        claimed_text = judgement.get("line")

        line: Line | None = None
        failure: str | None = None

        if verdict == "not_evidenced" or claimed_number is None:
            # No quote to check. A verdict of not_evidenced with no line is a
            # correct answer, so this is a pass, not a failure.
            trace.append(ev.step_event(requirement["id"], "verify", "no quote to check"))
        else:
            line = resume_index.get(claimed_number)
            if line is None:
                failure = f"line {claimed_number} is not in the resume"
            elif not resume_index.contains_verbatim(line.text):
                failure = f"line {claimed_number} is not verbatim in the resume"
            elif claimed_text and resume_index.locate(claimed_text) != line.text:
                failure = f"quoted text does not match line {claimed_number}"
            else:
                trace.append(
                    ev.step_event(
                        requirement["id"], "verify", f"line {claimed_number} confirmed"
                    )
                )

        # The retry decision, and decision 0007 replaces half of it.
        #
        # It used to fire on `evidence_weak`: the model's own report that its
        # evidence was thin. That fired zero times in three real runs -- 0 of
        # 21, 0 of 23, 0 of 21 -- including on requirements where the verdict
        # was wrong and the model's own written reason said "does not
        # mention". A self-report nobody can check is not a trigger, and the
        # strongest claim in the project was resting on it.
        #
        # What replaces it is observable in data the graph already holds: a
        # first pass that found nothing. `not_evidenced` on the first attempt
        # means the search terms may simply have missed, and looking again
        # with different terms is the correct behaviour -- it is the exact
        # case that produced the wrong FastAPI verdict before BM25.
        #
        # Only the first attempt, so a requirement the resume genuinely does
        # not cover costs one extra search-and-judge, never two. The failed
        # quote trigger below is unchanged and still has all three attempts.
        #
        # `evidence_weak` stays in the schema and is now ignored here. Taking
        # it out of the model is a separate change and this is the last wave.
        found_nothing_first_time = verdict == "not_evidenced" and attempts == 1
        room_left = attempts < MAX_ATTEMPTS

        if (failure or found_nothing_first_time) and room_left:
            # Written for a person watching the demo, not for a log. The step
            # detail is rendered verbatim in the trace by both clients.
            reason = failure or (
                "the first search found nothing -- looking again with different terms"
            )
            trace.append(ev.step_event(requirement["id"], "retry", reason))
            return {
                "next_action": "retry",
                "seen": state.get("seen", []) + state.get("retrieved", []),
                "events": trace,
            }

        if failure:
            # Out of attempts with a quote we could not confirm. Recorded as
            # not_evidenced with no line: three verdicts, never a fourth.
            trace.append(
                ev.step_event(
                    requirement["id"],
                    "failed",
                    f"{failure}; giving up after {attempts} attempts",
                )
            )
            settled = ev.verdict_event(
                requirement["id"],
                "not_evidenced",
                None,
                None,
                f"could not confirm a supporting line after {attempts} attempts",
            )
        else:
            settled = ev.verdict_event(
                requirement["id"],
                verdict,
                line.text if line else None,
                line.number if line else None,
                judgement["reason"],
            )

        trace.append(settled)
        return {
            "next_action": "advance",
            "verdicts": state.get("verdicts", []) + [settled],
            "events": trace,
        }

    def advance(state: AuditState) -> dict[str, Any]:
        """Move to the next requirement, or finish. The loop counts
        requirements, so nothing here can end the run early.

        The one exception is a re-run of a single requirement, where finishing
        after one is the whole request rather than an early exit.
        """
        cursor = state["cursor"] + 1
        done = state.get("only_id") is not None or cursor >= len(state["requirements"])
        return {
            "cursor": cursor,
            "attempts": 0,
            "tried": [],
            "seen": [],
            "next_action": "report" if done else "search",
        }

    def report(state: AuditState) -> dict[str, Any]:
        """`done`, then `summary`. In that order, because a client may render
        the counts and ignore the product layer entirely."""
        counts = ev.empty_counts()
        for verdict in state.get("verdicts", []):
            counts[verdict["verdict"]] += 1

        summary = summarise(
            state.get("requirements", []),
            state.get("verdicts", []),
            state["resume_index"],
        )
        return {
            "counts": counts,
            "summary": summary,
            "events": [ev.done_event(counts), ev.summary_event(**{
                k: v for k, v in summary.items() if k != "type"
            })],
        }

    return {
        "extract": extract,
        "search": search,
        "judge": judge,
        "verify": verify,
        "advance": advance,
        "report": report,
    }


def build_graph(model: Model):
    nodes = build_nodes(model)
    graph = StateGraph(AuditState)
    for name, fn in nodes.items():
        graph.add_node(name, fn)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "search")
    graph.add_edge("search", "judge")
    graph.add_edge("judge", "verify")

    # The two conditional edges are the control flow the demo points at.
    graph.add_conditional_edges(
        "verify",
        lambda state: state["next_action"],
        {"retry": "search", "advance": "advance"},
    )
    graph.add_conditional_edges(
        "advance",
        lambda state: state["next_action"],
        {"search": "search", "report": "report"},
    )
    graph.add_edge("report", END)

    # A requirement can cost 3 searches x 4 nodes, plus extract and report.
    # The cap is a backstop against a graph bug, never the thing that ends a
    # normal run -- `advance` is what ends a normal run.
    return graph.compile()


def recursion_budget(requirements: int) -> int:
    return 8 + requirements * (MAX_ATTEMPTS + 1) * 4


def run_stream(
    model: Model,
    post: str,
    resume: str,
    *,
    requirements: list[dict[str, Any]] | None = None,
    verdicts: list[dict[str, Any]] | None = None,
    only_id: int | None = None,
) -> Iterator[dict[str, Any]]:
    """Run the audit, yielding contract events as they happen.

    `stream_mode="updates"` gives one dict per node execution, keyed by node
    name, holding only that node's returned update -- so its `events` list is
    exactly the new events. No extra plumbing is needed to stream.

    The three keyword arguments are the second pass from decision 0006, and
    they are all one idea: hand the graph an audit that already happened, and
    it will redo one part of it. `requirements` skips extraction and fixes the
    ids, `verdicts` carries the results being kept so the closing `summary`
    covers the whole audit, and `only_id` says which one to do again.
    """
    graph = build_graph(model)
    initial: AuditState = {"post": post, "resume": resume, "events": []}
    if requirements is not None:
        initial["requirements"] = requirements
    if verdicts is not None:
        initial["verdicts"] = verdicts
    if only_id is not None:
        initial["only_id"] = only_id

    try:
        for update in graph.stream(
            initial,
            stream_mode="updates",
            config={"recursion_limit": recursion_budget(400)},
        ):
            for node_update in update.values():
                if not isinstance(node_update, dict):
                    continue
                for event in node_update.get("events", []):
                    yield event
    except AuditError as exc:
        yield ev.error_event(str(exc))
    except Exception as exc:  # the demo must not die on a stack trace
        yield ev.error_event(f"{type(exc).__name__}: {exc}")


def run(model: Model, post: str, resume: str) -> dict[str, Any]:
    """Run to completion and return the whole audit. Used by the CLI and the
    tests; the server uses `run_stream` instead."""
    collected = list(run_stream(model, post, resume))
    requirements: list[dict[str, Any]] = []
    verdicts: list[dict[str, Any]] = []
    counts = ev.empty_counts()
    summary: dict[str, Any] | None = None
    error: str | None = None

    for event in collected:
        if event["type"] == "requirements":
            requirements = event["items"]
        elif event["type"] == "verdict":
            verdicts.append(event)
        elif event["type"] == "done":
            counts = event["counts"]
        elif event["type"] == "summary":
            summary = event
        elif event["type"] == "error":
            error = event["message"]

    return {
        "requirements": requirements,
        "verdicts": verdicts,
        "counts": counts,
        "summary": summary,
        "events": collected,
        "error": error,
    }

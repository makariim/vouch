"""The checks brief 0001 section 4 asks for, as automated tests.

The two that matter most are `test_every_quote_is_verbatim_in_the_resume` and
`test_every_requirement_is_verbatim_in_the_post`. The brief calls for those by
name: an automated check, not an eyeball.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from audit.events import VERDICTS
from audit.graph import MAX_ATTEMPTS, run, run_stream
from audit.testing import ScriptedModel

DATA = Path(__file__).parent / "data"
POST = (DATA / "post.txt").read_text(encoding="utf-8")
RESUME = (DATA / "resume.txt").read_text(encoding="utf-8")
UNRELATED = (DATA / "resume_unrelated.txt").read_text(encoding="utf-8")


@pytest.fixture
def result():
    return run(ScriptedModel(), POST, RESUME)


# --- the two verbatim checks -------------------------------------------------


def test_every_quote_is_verbatim_in_the_resume(result):
    quoted = [v for v in result["verdicts"] if v["line"]]
    assert quoted, "no quotes at all -- this check would pass for the wrong reason"
    for verdict in quoted:
        assert verdict["line"] in RESUME, f"not in the resume: {verdict['line']!r}"


def test_every_requirement_is_verbatim_in_the_post(result):
    assert result["requirements"]
    for requirement in result["requirements"]:
        assert requirement["text"] in POST, f"not in the post: {requirement['text']!r}"


def test_a_quote_that_is_not_in_the_resume_is_caught():
    """The verify node, shown rejecting a bad input rather than assumed to."""
    target = "5+ years of professional Python experience"
    outcome = run(ScriptedModel(bad_line_once={target}), POST, RESUME)

    for verdict in outcome["verdicts"]:
        assert verdict["line"] is None or verdict["line"] in RESUME

    steps = [e for e in outcome["events"] if e["type"] == "step"]
    assert any(s["step"] == "retry" for s in steps), "verify did not force a retry"


# --- verdict bookkeeping -----------------------------------------------------


def test_one_verdict_per_requirement_and_nothing_else(result):
    assert len(result["verdicts"]) == len(result["requirements"])

    ids = [v["requirement_id"] for v in result["verdicts"]]
    assert sorted(ids) == [r["id"] for r in result["requirements"]]

    for verdict in result["verdicts"]:
        assert verdict["verdict"] in VERDICTS

    assert sum(result["counts"].values()) == len(result["requirements"])


def test_the_run_does_not_end_early(result):
    """The loop counts requirements, not model turns."""
    assert len(result["requirements"]) == 6
    assert len(result["verdicts"]) == 6


# --- the disjoint pair -------------------------------------------------------


def test_a_resume_with_nothing_in_common_evidences_nothing():
    outcome = run(ScriptedModel(), POST, UNRELATED)

    assert outcome["verdicts"]
    for verdict in outcome["verdicts"]:
        assert verdict["verdict"] == "not_evidenced"
        assert verdict["line"] is None
        assert verdict["line_number"] is None

    assert outcome["counts"]["evidenced"] == 0
    assert outcome["counts"]["partly_evidenced"] == 0


# --- empty input -------------------------------------------------------------


@pytest.mark.parametrize(
    "post,resume,expected",
    [
        (POST, "", "resume is empty"),
        (POST, "   \n\n ", "resume is empty"),
        ("", RESUME, "post is empty"),
        ("\n\n", RESUME, "post is empty"),
    ],
)
def test_empty_input_fails_loudly(post, resume, expected):
    outcome = run(ScriptedModel(), post, resume)

    assert outcome["error"] == expected
    # The failure mode this guards: an empty audit that looks like a real one.
    assert outcome["verdicts"] == []
    assert outcome["requirements"] == []
    assert [e["type"] for e in outcome["events"]] == ["error"]


def test_a_post_with_no_readable_requirements_fails():
    outcome = run(ScriptedModel(), "We are hiring. Send a CV.", RESUME)
    assert outcome["error"] == "no requirements could be read from the post"


# --- the trace ---------------------------------------------------------------


def test_the_trace_shows_a_retry():
    """Decision 0007 changed what makes the agent look again.

    This test used to drive the retry with `weak_once` -- the model reporting
    its own evidence as thin. That trigger is gone, because in three real runs
    it fired zero times out of 21, 23 and 21. The trigger now is a first pass
    that came back `not_evidenced`, which is data the graph can see rather
    than an opinion the model volunteers.
    """
    target = "Hands-on Kubernetes in production"
    outcome = run(ScriptedModel(blank_once={target}), POST, RESUME)

    retries = [
        e for e in outcome["events"] if e["type"] == "step" and e["step"] == "retry"
    ]
    assert retries, "the agent never decided to look again"
    # Among, not first: any requirement whose first pass finds nothing now
    # triggers one, so pinning the order would pin the stand-in's scoring
    # rather than the behaviour under test.
    forced = [e for e in retries if e["requirement_id"] == 4]
    assert forced, "the requirement whose first pass was blanked never retried"
    # In plain words, because this string is rendered in the demo.
    assert "looking again" in forced[0]["detail"]


def test_the_retry_is_what_changes_the_verdict():
    """The point of going round again, rather than just the fact of it.

    Requirement 2 is one the resume really does cover, so a first pass that
    returns nothing is a search that missed -- exactly the case decision 0007
    describes, and the case that produced the wrong FastAPI verdict before
    BM25. The second pass has to recover it, or the retry is only costing
    money.
    """
    target = "Strong SQL and data modelling skills"
    outcome = run(ScriptedModel(blank_once={target}), POST, RESUME)

    settled = next(v for v in outcome["verdicts"] if v["requirement_id"] == 2)
    assert settled["verdict"] != "not_evidenced", "the second pass found nothing"
    assert settled["line"] in RESUME


def test_the_self_report_no_longer_makes_the_agent_look_again():
    """`evidence_weak` stays in the schema and is ignored as a trigger.

    Decision 0007 keeps the field -- removing it is a separate change -- so
    the thing worth pinning is that setting it no longer does anything. A
    requirement whose first pass found evidence is settled on that pass.
    """
    target = "Hands-on Kubernetes in production"
    outcome = run(ScriptedModel(weak_once={target}), POST, RESUME)

    retries = [
        e
        for e in outcome["events"]
        if e["type"] == "step" and e["step"] == "retry" and e["requirement_id"] == 4
    ]
    assert retries == []


def test_a_requirement_the_resume_does_not_cover_costs_one_extra_pass_only():
    """Decision 0007's known cost, held to one extra pass rather than two.

    The trigger is the FIRST pass finding nothing. A second pass that also
    finds nothing settles the requirement instead of going round again, so a
    post full of things the resume lacks doubles the work at most.
    """
    outcome = run(ScriptedModel(), POST, UNRELATED)
    for requirement in outcome["requirements"]:
        searches = [
            e
            for e in outcome["events"]
            if e["type"] == "step"
            and e["step"] == "search"
            and e["requirement_id"] == requirement["id"]
        ]
        assert len(searches) == 2, f"requirement {requirement['id']} searched {len(searches)}x"


def test_retrying_stops_and_does_not_loop_for_ever():
    every = [
        line.strip()[2:].strip()
        for line in POST.splitlines()
        if line.strip().startswith("- ")
    ]
    outcome = run(ScriptedModel(bad_line_once=set(every)), POST, RESUME)

    assert len(outcome["verdicts"]) == len(every)
    for requirement in every:
        searches = [
            e
            for e in outcome["events"]
            if e["type"] == "step" and e["step"] == "search"
        ]
        assert len(searches) <= len(every) * MAX_ATTEMPTS


def test_the_trace_covers_every_node_and_is_ordered():
    outcome = run(ScriptedModel(), POST, RESUME)
    types = [e["type"] for e in outcome["events"]]

    assert types[0] == "requirements"
    # `summary` closes the stream since decision 0005; `done` is the one
    # before it. A client may render the counts and ignore the product layer.
    assert types[-1] == "summary"
    assert types[-2] == "done"

    steps = {e["step"] for e in outcome["events"] if e["type"] == "step"}
    assert {"search", "judge", "verify"} <= steps

    # Every step and verdict names a requirement that exists.
    ids = {r["id"] for r in outcome["requirements"]}
    for event in outcome["events"]:
        if event["type"] == "verdict":
            assert event["requirement_id"] in ids


def test_every_event_is_json_and_matches_the_contract(result):
    allowed = {"requirements", "step", "verdict", "done", "summary", "error"}
    for event in result["events"]:
        assert event["type"] in allowed
        json.dumps(event)  # must survive the wire

    done = [e for e in result["events"] if e["type"] == "done"]
    assert len(done) == 1
    assert set(done[0]["counts"]) == set(VERDICTS)


def test_streaming_yields_the_same_events_as_the_batch_run(result):
    streamed = list(run_stream(ScriptedModel(), POST, RESUME))
    assert streamed == result["events"]

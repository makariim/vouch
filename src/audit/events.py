"""The wire contract from decision 0004.

Every event is one JSON object with a `type`. The frontend is being written
against these shapes in another session right now, so this file is the one
place they are constructed. Nothing here may change without going back to
decision 0004 first.

Decision 0005 adds the sixth type, `summary`, and one field, `required`, on
each requirement. That decision counts the types rather than claiming a number:
`requirements`, `step`, `verdict`, `done`, `summary`, `error`. All six are
built here.
"""

from __future__ import annotations

from typing import Any, Literal

VERDICTS = ("evidenced", "partly_evidenced", "not_evidenced")

Verdict = Literal["evidenced", "partly_evidenced", "not_evidenced"]

# Decision 0006 item 5. Two closed sets that were already true of the code and
# had never been written down, so no client could check itself against them.
# They live here rather than in `prescreen.py` and `graph.py` because this is
# the file that is the contract; a set defined next to one of its producers is
# a set the other client has to go and read code to discover.
SIGNALS = ("worth_a_look", "maybe", "skip")

# Decision 0008 closes the gap brief 0012 left open. `repair` is emitted by
# `graph.extract` when a damaged resume line is mechanically fixed, and it was
# missing from decision 0006's list because that list was read off the code and
# this one was missed. Brief 0012 kept it in a second name, `EMITTED_STEPS`, so
# the difference between "what the decision says" and "what the code emits"
# stayed visible rather than being quietly resolved. Decision 0008 resolves it
# in the direction the code was already going: seven steps, one set.
STEPS = ("search", "judge", "verify", "retry", "failed", "dropped", "repair")

# The old name, kept pointing at the one set. A second name for the same tuple
# cannot drift; a second tuple can, which is what this brief just removed.
EMITTED_STEPS = STEPS

# Decision 0006 item 7. A requirement with no `required` key is required.
# The rule is a function rather than a sentence in a document, so that the two
# places that need it cannot drift apart.
REQUIRED_BY_DEFAULT = True


def requirement_is_required(requirement: dict[str, Any]) -> bool:
    """Absent means required -- the safe reading, applied in one place."""
    return bool(requirement.get("required", REQUIRED_BY_DEFAULT))


def requirements_event(items: list[dict[str, Any]]) -> dict[str, Any]:
    """The requirement list, emitted once after extraction.

    Each item carries `required` since decision 0005: false when the post's own
    words called it a plus, a preference or a nice-to-have.
    """
    return {"type": "requirements", "items": items}


def step_event(requirement_id: int, step: str, detail: str) -> dict[str, Any]:
    """One node doing one thing. This is the trace the demo shows."""
    return {
        "type": "step",
        "requirement_id": requirement_id,
        "step": step,
        "detail": detail,
    }


def verdict_event(
    requirement_id: int,
    verdict: Verdict,
    line: str | None,
    line_number: int | None,
    reason: str,
) -> dict[str, Any]:
    """One requirement settled. `line` is always text taken from the resume
    itself, or None -- never text echoed back by the model."""
    return {
        "type": "verdict",
        "requirement_id": requirement_id,
        "verdict": verdict,
        "line": line,
        "line_number": line_number,
        "reason": reason,
    }


def done_event(counts: dict[str, int]) -> dict[str, Any]:
    return {"type": "done", "counts": counts}


def summary_item(
    requirement_id: int,
    text: str | None = None,
    line: str | None = None,
    line_number: int | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """One row of `blockers`, `strengths` or `undersells`.

    Decision 0006 item 3: all three lists carry the same five fields, with
    `null` where a field does not apply. Before this, each list had its own
    shape and neither client could render a summary it held on its own --
    brief 0008 had to invent a fixture to join `strengths` back against the
    requirement list. One builder is what stops the three drifting again.

    `line` is always text taken from the resume index, never from the model,
    for the same reason `verdict_event.line` is.
    """
    return {
        "requirement_id": requirement_id,
        "text": text,
        "line": line,
        "line_number": line_number,
        "reason": reason,
    }


def summary_event(
    fit: str,
    fit_reason: str,
    blockers: list[dict[str, Any]],
    strengths: list[dict[str, Any]],
    undersells: list[dict[str, Any]],
) -> dict[str, Any]:
    """The product layer, emitted once after `done` (decision 0005).

    Computed in `product.py` and shaped here, so the wire format still has
    exactly one place it is written.
    """
    return {
        "type": "summary",
        "fit": fit,
        "fit_reason": fit_reason,
        "blockers": blockers,
        "strengths": strengths,
        "undersells": undersells,
    }


def error_event(message: str) -> dict[str, Any]:
    return {"type": "error", "message": message}


def empty_counts() -> dict[str, int]:
    return {name: 0 for name in VERDICTS}

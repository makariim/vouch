"""From a table of verdicts to an answer a job seeker can act on.

21 rows of verdicts is a report. This module turns it into the three things
somebody actually wants before they spend an evening on an application:

    should I apply            -> fit, fit_reason
    what will sink me         -> blockers
    where am I selling myself -> undersells
                                 short, and strengths for the cover letter

Decision 0005 puts this in the backend on purpose: two clients render it and
neither may compute it, or the same judgement drifts into two versions.

NOTHING HERE CALLS A MODEL. Every rule below is arithmetic over the verdicts
the graph already produced, which means the summary costs nothing, cannot
hallucinate, and can be explained to the person reading it. Where a rule needs
a number, the number is written down here with its reasoning, and it was fixed
before the real run rather than tuned until the output looked good.
"""

from __future__ import annotations

import re
from typing import Any

from . import events as ev
from .index import Line, LineIndex, tokenize

# The post's own words for "you do not actually need this". Decision 0005 is
# explicit that the post decides, not us.
OPTIONAL_MARKERS = (
    "a strong plus",
    "a big plus",
    "a plus",
    "nice to have",
    "nice-to-have",
    "preferred",
    "preferable",
    "desirable",
    "desired",
    "bonus",
    "advantageous",
    "not required",
    "optional",
    "ideally",
    "would be great",
)

# A heading is short and ends in a colon. `Preferred Qualifications:` makes
# everything under it optional, and the requirement sentences beneath will not
# repeat the word, so the heading has to be consulted.
_HEADING_MAX = 90

# What makes a supporting line WEAK rather than absent. A resume that lists a
# skill among twenty others states it; a resume that shows the work proves it.
# So: a line that is mostly a run of short comma-separated fragments is a
# skills dump, and evidence found only there is evidence stated weakly.
MIN_LIST_ITEMS = 4
SHORT_ITEM_WORDS = 4
LIST_ITEM_SHARE = 0.7

# How many unmet REQUIRED items stop being a gap and start being a wall.
# One missing box is not a rejection; the post itself says so. Three is.
BLOCKERS_FOR_WEAK = 3
STRONG_EVIDENCED_SHARE = 0.5
WEAK_EVIDENCED_SHARE = 0.25


def _heading_above(post_index: LineIndex, text: str) -> str:
    """The nearest section heading above where this requirement sits."""
    at = post_index.source.find(text)
    if at == -1:
        return ""
    before = post_index.source[:at].splitlines()
    for raw in reversed(before):
        line = raw.strip()
        if not line:
            continue
        if line.endswith(":") and len(line) <= _HEADING_MAX:
            return line
        if len(line) > _HEADING_MAX:
            break  # a paragraph, not a heading: stop looking
    return ""


def is_required(text: str, post_index: LineIndex) -> bool:
    """Does the post insist on this, or merely hope for it?

    Two places carry the answer and both are the post's own words: the
    requirement sentence itself (`... is a strong plus`) and the heading it
    sits under (`Nice to have:`). Nothing else is consulted -- in particular no
    model is asked, because this is a word-matching job and a model would make
    it non-deterministic for no gain.
    """
    haystack = f"{text} {_heading_above(post_index, text)}".lower()
    return not any(marker in haystack for marker in OPTIONAL_MARKERS)


def is_weakly_stated(line_text: str) -> bool:
    """Is this line a skills list rather than a piece of evidence?

    `Docker, Kubernetes, Helm, GitHub Actions, ...` is a list: the skill is
    named and nothing is shown. `Redesigned its concurrency model, isolating
    GIL-bound image work in a bounded process pool` is evidence: same subject,
    but it shows the work and a result.

    The mechanical difference is shape. A list is many short comma-separated
    fragments; a sentence is few long ones.
    """
    items = [part.strip() for part in line_text.split(",") if part.strip()]
    if len(items) < MIN_LIST_ITEMS:
        return False
    short = sum(1 for item in items if len(item.split()) <= SHORT_ITEM_WORDS)
    return short / len(items) >= LIST_ITEM_SHARE


def _fit(evidenced: int, required_total: int, blockers: int) -> str:
    """One word, never a percentage. Decision 0005: a number invites a
    precision this cannot support."""
    share = evidenced / required_total if required_total else 0.0
    if blockers >= BLOCKERS_FOR_WEAK or share < WEAK_EVIDENCED_SHARE:
        return "weak"
    if blockers == 0 and share >= STRONG_EVIDENCED_SHARE:
        return "strong"
    return "worth_applying"


def _fit_sentence(fit: str, evidenced: int, total: int, blockers: list[dict]) -> str:
    """Plain English, assembled from the counts. A template, not a model: the
    sentence has to be true, and the only things that make it true are the
    numbers immediately above it.

    Decision 0008 rewrites the wording and nothing else. This is the largest
    sentence on the page, it is rendered verbatim by both clients -- rewriting
    a backend judgement in a client is what decision 0006 forbids -- and it was
    the one place in the product still saying "requirements are evidenced".
    `design/README.md` bans "evidence" as a verb outright and sets the register
    as "your resume shows this", so the sentence now says that. The numbers,
    the denominators and the branches are untouched; only the words changed.

    Decision 0006 item 6: `evidenced` and `total` here count EVERY
    requirement, not just the required ones. The live page shows this sentence
    beside the counts row, and until now the two used different denominators
    -- "0 of 3" next to a row totalling 4. Both were defensible and together
    they read as a bug. Required-versus-preferred is what `blockers` carries,
    and the tail of this sentence says so.
    """
    body = f"Your resume shows {evidenced} of {total} things they ask for"
    if not blockers:
        tail = ", and nothing they need is missing."
    elif len(blockers) == 1:
        tail = f", and they need one more thing: {blockers[0]['text'][:70]}."
    else:
        tail = f", and they need {len(blockers)} things you cannot show."

    lead = {
        "strong": "Worth applying, and you are a close match.",
        "worth_applying": "Worth applying.",
        "weak": "A long shot on paper.",
    }[fit]
    return f"{lead} {body}{tail}"


def summarise(
    requirements: list[dict[str, Any]],
    verdicts: list[dict[str, Any]],
    resume_index: LineIndex,
) -> dict[str, Any]:
    """The `summary` event from decision 0005, computed once, here.

    Decision 0006 changes two things about it. Every row of all three lists is
    built by `events.summary_item`, so the three have one shape; and the
    sentence counts all requirements while `fit` and `blockers` still count
    the required ones. Those are deliberately different sets and the variable
    names below keep them apart.
    """
    by_id = {v["requirement_id"]: v for v in verdicts}
    # Decision 0006 item 7: absent means required, decided in one place.
    required_ids = {r["id"] for r in requirements if ev.requirement_is_required(r)}
    text_of = {r["id"]: r["text"] for r in requirements}

    def quoted(verdict: dict[str, Any]) -> tuple[str | None, int | None]:
        """The supporting line, read back out of the resume rather than out of
        the verdict. Same guarantee as `verify`: a quote in the summary can
        only be a line the indexed resume really contains."""
        number = verdict.get("line_number")
        line = resume_index.get(number) if number else None
        return (line.text if line else None), (line.number if line else None)

    blockers: list[dict[str, Any]] = []
    strengths: list[dict[str, Any]] = []
    undersells: list[dict[str, Any]] = []
    evidenced_required = 0  # drives `fit`
    evidenced_all = 0  # drives the sentence

    for requirement in requirements:
        rid = requirement["id"]
        verdict = by_id.get(rid)
        if verdict is None:
            continue

        if verdict["verdict"] == "evidenced":
            evidenced_all += 1
            if rid in required_ids:
                evidenced_required += 1
            line, number = quoted(verdict)
            if number:
                strengths.append(
                    ev.summary_item(
                        rid,
                        text=text_of[rid],
                        line=line,
                        line_number=number,
                        reason=verdict.get("reason"),
                    )
                )

        elif verdict["verdict"] == "not_evidenced" and rid in required_ids:
            # A blocker has no line by construction: not_evidenced is settled
            # with no quote. `line` and `line_number` are the null case the
            # one shape exists to carry.
            blockers.append(
                ev.summary_item(rid, text=text_of[rid], reason=verdict.get("reason"))
            )

        elif verdict["verdict"] == "partly_evidenced":
            line, number = quoted(verdict)
            # The evidence has to actually be there -- a line we can point at
            # in the resume -- before we tell somebody their resume undersells
            # them. Without this, `undersells` would be a synonym for
            # `partly_evidenced` and would say nothing.
            if line is not None and is_weakly_stated(line):
                undersells.append(
                    ev.summary_item(
                        rid,
                        text=text_of[rid],
                        line=line,
                        line_number=number,
                        reason=(
                            "the evidence is on this line, but it is listed among "
                            "other skills rather than shown in your experience"
                        ),
                    )
                )

    fit = _fit(evidenced_required, len(required_ids), len(blockers))
    return {
        "type": "summary",
        "fit": fit,
        "fit_reason": _fit_sentence(fit, evidenced_all, len(requirements), blockers),
        "blockers": blockers,
        "strengths": strengths,
        "undersells": undersells,
    }

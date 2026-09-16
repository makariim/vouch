"""The fast speed. BM25 only, no model, no network, milliseconds.

Decision 0005 calls this the thing that runs while somebody scrolls a job
board, where a 58-second model call per post is unusable and expensive. The
full audit is what runs when they stop scrolling.

The two speeds are the architecture, not a slide. So the constraint is
structural: this module imports nothing from `model`, and there is a test that
fails if anything under it tries to open a socket.

What it gives up, said plainly: the requirement list here is guessed from the
shape of the post rather than read by a model, so it will over- and
under-count. It answers "is this worth 58 seconds", which is a question a
rough count can answer. It does not answer anything else.
"""

from __future__ import annotations

from typing import Any

from .index import LineIndex, tokenize

# A requirement is a sentence about the candidate. Below this many content
# words a line is a heading, a label, or a bullet character.
MIN_REQUIREMENT_TOKENS = 4

# How many of a requirement's own words a resume line must share before it
# counts as a hit. One is a coincidence: BM25 already only returns lines
# sharing a term, so a one-word overlap matched every requirement in the real
# post -- 26 of 26 -- which is a signal that says nothing. Two discriminates:
# the same run gives 17 of 26 for the real resume and 0 of 26 for an unrelated
# one. Measured before the threshold was chosen, and written down in report
# 0007 with both numbers.
MIN_SHARED_TERMS = 2

# Lines in a job post that are never requirements.
_BOILERPLATE = (
    "equal opportunity",
    "benefits",
    "we encourage",
    "apply",
    "privacy",
    "compensation",
    "salary range",
    "about us",
    "our mission",
)

# Where the rough count turns into one word.
WORTH_A_LOOK = 0.6
MAYBE = 0.3


def candidate_requirements(post: str) -> list[str]:
    """Lines of the post that look like something asked of the candidate.

    Deliberately crude. A heading ends in a colon; boilerplate says so in its
    own words; anything short is a label. What survives is roughly the
    requirement paragraphs, which is all the count needs.
    """
    out: list[str] = []
    for raw in post.splitlines():
        line = raw.strip()
        if not line or line.endswith(":"):
            continue
        lowered = line.lower()
        if any(phrase in lowered for phrase in _BOILERPLATE):
            continue
        if len(tokenize(line)) < MIN_REQUIREMENT_TOKENS:
            continue
        out.append(line)
    return out


def prescreen(post: str, resume_index: LineIndex) -> dict[str, Any]:
    """How many of the post's requirements the resume has a keyword hit for.

    One BM25 search per requirement against an index that is already built.
    There is no model call here and there is nothing to wait for, which is the
    entire point: the cost of an answer is a few milliseconds of arithmetic.
    """
    requirements = candidate_requirements(post)
    matched = 0
    for text in requirements:
        hits = resume_index.search(text, limit=1)
        if not hits:
            continue
        shared = set(tokenize(text)) & set(tokenize(hits[0].text))
        if len(shared) >= MIN_SHARED_TERMS:
            matched += 1
    total = len(requirements)
    share = matched / total if total else 0.0

    if share >= WORTH_A_LOOK:
        signal = "worth_a_look"
    elif share >= MAYBE:
        signal = "maybe"
    else:
        signal = "skip"

    return {"signal": signal, "matched": matched, "total": total}

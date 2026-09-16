"""Line-indexed text, and the search tool the graph queries.

Decision 0001 makes the resume a *tool*, not a prompt argument. The whole
verbatim guarantee rests on this file: the judge node can only cite a line
number that search actually returned, and the text we finally emit is sliced
out of the source here -- never copied from what the model typed back.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi


@dataclass(frozen=True)
class Line:
    """One non-empty line of the source, with its 1-based number."""

    number: int
    text: str


_WORD = re.compile(r"[a-z0-9+#.]+")

# Words too common in job posts and resumes to carry signal. Kept small on
# purpose: an aggressive list hides real matches.
_STOPWORDS = frozenset(
    """a an and are as at be by for from has have in is it its of on or that the
    to with you your we our their they this will can able experience years year
    strong good excellent using use used work working ability plus must should""".split()
)


def tokenize(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS]


class LineIndex:
    """A document addressed by line number, searchable by keyword.

    Blank lines are skipped but numbering follows the original file, so a line
    number in the trace points at the real line a human can open and check.
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.lines: list[Line] = [
            Line(number=i, text=raw.strip())
            for i, raw in enumerate(source.splitlines(), start=1)
            if raw.strip()
        ]
        self._tokens = {line.number: set(tokenize(line.text)) for line in self.lines}
        self._by_number = {line.number: line for line in self.lines}

    def __len__(self) -> int:
        return len(self.lines)

    def get(self, number: int) -> Line | None:
        """The real line at this number, or None. This is what makes a quote
        verbatim: we look the text up here rather than trusting the model."""
        return self._by_number.get(number)

    def search(self, query: str, limit: int = 6) -> list[Line]:
        """BM25 over the lines, best first.

        Was plain keyword overlap, which scored every query word the same. On
        the real run that lost requirement 12: a 22-word query buried `fastapi`
        under generic terms and line 77 was never retrieved. BM25 weights a
        term by how rare it is in this document, so one specific word outranks
        three common ones. Scoring is `rank_bm25`'s, not ours -- see report
        0004 for why a hand-rolled one was not acceptable.

        Still deliberately not embeddings: decision 0002 allows exactly one
        outbound call, the model call, and an embedding API would be a second.

        `k1` and `b` are the library defaults. Brief 0004 forbids tuning them
        to make one requirement come out right, and they are not tuned.
        """
        wanted = set(tokenize(query))
        if not wanted or not self.lines:
            return []

        bm25, numbers = self._bm25()
        scores = bm25.get_scores(sorted(wanted))

        scored: list[tuple[float, int, Line]] = []
        for number, score in zip(numbers, scores):
            # A line sharing no query term is not a hit, whatever BM25 says:
            # Okapi IDF can go negative for a term on most lines, which would
            # otherwise let an unrelated line outscore a matching one.
            if not (wanted & self._tokens[number]):
                continue
            scored.append((float(score), -number, self._by_number[number]))

        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [line for _, _, line in scored[:limit]]

    def _bm25(self) -> tuple[BM25Okapi, list[int]]:
        """The corpus index, built once and kept.

        Built here rather than in `__init__` because `self._tokens` holds sets
        and BM25 needs term counts -- it has to weigh a word said twice
        differently from a word said once.
        """
        cached = getattr(self, "_bm25_cache", None)
        if cached is None:
            corpus = [tokenize(line.text) for line in self.lines]
            numbers = [line.number for line in self.lines]
            cached = (BM25Okapi(corpus), numbers)
            self._bm25_cache = cached
        return cached

    def contains_verbatim(self, quote: str) -> bool:
        """Is this text present in the source, character for character?"""
        return bool(quote) and quote in self.source

    def locate(self, quote: str) -> str | None:
        """Find `quote` in the source and return the *source's* own wording.

        Returns the exact slice when the quote is already verbatim. Otherwise
        it retries ignoring differences in whitespace only -- which is how a
        hard-wrapped job post breaks an otherwise correct extraction -- and
        returns the original span, so what we emit always comes from the file.
        Returns None when the text is simply not there.
        """
        if not quote.strip():
            return None
        if quote in self.source:
            return quote

        # Map each non-space character of the source back to its offset, then
        # match on the whitespace-free forms and slice the original span.
        offsets = [i for i, ch in enumerate(self.source) if not ch.isspace()]
        squeezed = "".join(self.source[i] for i in offsets)
        needle = "".join(ch for ch in quote if not ch.isspace())
        if not needle:
            return None

        at = squeezed.find(needle)
        if at == -1:
            return None
        return self.source[offsets[at] : offsets[at + len(needle) - 1] + 1]

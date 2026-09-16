"""Mechanical repair of text pulled out of a PDF. No model call, ever.

A PDF has no lines and no columns -- it has glyphs at coordinates. Any
extractor has to guess where a line ends and where a column boundary was, and
it guesses wrong in two ways that cost us verdicts:

    a word split across a line break     ...on-prem and air-
                                         gapped deployment
    a table row flattened into one line  AI systems Languages Backend & data...

Both are damage, not content. Repairing them is arithmetic over characters,
which is why this file exists and why nothing in it asks a model anything.

Brief 0007 is explicit about the reason: a model that rewrites the resume
destroys the verbatim guarantee, which is the whole product. The quotes we
publish are sliced out of whatever text this module returns, so this module is
allowed to join and split lines and is allowed to do nothing else. It never
invents a character.

Repair runs BEFORE indexing. The line numbers a human sees in
`GET /resumes/{id}` are the numbers of the repaired text, so the index, the
quotes and the human's own reading all agree.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

# A wrapped line is a line that ran out of page, so it ends near the page's
# right margin. A SHORT line ending without punctuation is something else -- a
# heading, a job title, a table cell -- and must not be glued to the next one.
#
# The margin is not a constant we can pick: it depends on the document's font
# and page size. So we measure it from the document itself, and require a line
# to reach most of that measure before treating its ending as an accident.
# On the real resume the measure is 133 characters and the bar is 113, which is
# what keeps the Frontend row of the skills table off the Quality row below it.
WRAP_MEASURE_PERCENTILE = 0.90
WRAP_MEASURE_FRACTION = 0.85

# A flattened row has to be long before it is worth suspecting at all, and so
# does a wrapped line. The measured margin above adapts to the document; this
# is the floor under it, for a document that never wraps at all and whose
# measure is therefore just the length of its longest sentence.
MIN_ROW_LENGTH = 60

# A column label is a heading: Title Case, and short.
MAX_LABEL_WORDS = 3

# A flattened table row carries the column headers of the table glued together.
# Three or more of those boundaries in one line is the signature; one or two is
# ordinary prose with a proper noun in it.
MIN_COLUMN_BOUNDARIES = 3

# Characters that are already a column separator. If the extractor kept one,
# the columns in that line survived and there is nothing to reconstruct --
# every boundary we could "find" in it would be a Title Case job title being
# cut into single words. This guard is why `Software Tech Lead | Software
# Engineer II | ...` is left alone.
_ALREADY_DELIMITED = re.compile(r"\||\t|\u2502|   ")

# Words that join a two-word column label. A capital after one of these is part
# of the same label ("Backend & data"), not the start of the next column.
_CONNECTORS = frozenset(
    {"&", "and", "of", "or", "/", "-", "the", "to", "in", "on", "for", "with", "at"}
)

# A run of column labels is mostly capitals -- that is what makes it a run of
# headings. Prose is mostly lower case with the odd proper noun in it.
MIN_CAPITAL_SHARE = 0.6

# pypdf does not separate words with spaces -- it separates them with TAB
# characters, so a line out of a real PDF reads
# `Riyadh,\tSaudi\tArabia\t\t|\t\tAug\t2025`. That is the extractor's artefact,
# not something the document says, and every quote we publish is sliced out of
# the text this module returns -- so the tabs have to go here, before indexing,
# or they end up on screen inside every quote.
#
# Collapsing a run of whitespace to one space changes no word and invents no
# character, which is the only kind of edit this file is allowed to make.
_WHITESPACE_RUN = re.compile(r"\s+")

_ENDS_SENTENCE = ".?!:;•"
_HYPHEN_TAIL = re.compile(r"[A-Za-z0-9]-$")
_STARTS_LOWER = re.compile(r"^[a-z]")
_WORDISH = re.compile(r"[A-Za-z]{3,}")


@dataclass(frozen=True)
class Change:
    """One repair, recorded so the report can show it rather than claim it."""

    kind: str  # rejoin-hyphen | rejoin-wrap | split-row
    source_line: int  # where it was in the extracted text
    before: str
    after: str


@dataclass
class Repair:
    text: str
    changes: list[Change] = field(default_factory=list)


def _word_at_end(text: str) -> str:
    return re.split(r"[\s]", text.rstrip())[-1] if text.strip() else ""


def _word_at_start(text: str) -> str:
    return re.split(r"[\s]", text.strip())[0] if text.strip() else ""


def _appears_elsewhere(needle: str, haystack: str, ignoring: str) -> bool:
    """Does `needle` occur in the document somewhere other than the split we
    are repairing? `ignoring` is the text of the split itself."""
    if not needle:
        return False
    pattern = re.compile(rf"(?<![A-Za-z0-9]){re.escape(needle)}(?![A-Za-z0-9])", re.I)
    return bool(pattern.search(haystack.replace(ignoring, " ")))


def _join_hyphenated(head: str, tail: str, document: str) -> str:
    """Rejoin `air-` + `gapped deployment`, and decide about the hyphen.

    A hyphen at a line end is ambiguous and no rule can be right every time.
    `environ-` / `ment` wants the hyphen dropped; `air-` / `gapped` wants it
    kept, because `air-gapped` is a real hyphenated word.

    So we ask the document rather than a dictionary or a model: if the joined
    form appears somewhere else in this same resume, use that form. This resume
    answers its own question -- `air-gapped model serving` is written out in
    full further up, so line 79 resolves to `air-gapped` on evidence.

    With no evidence either way we keep the hyphen, because keeping it destroys
    nothing: the tokenizer splits on `-`, so `air-gapped` and `air gapped`
    search identically. Dropping it would fuse two real words into one that is
    in neither the resume nor any query.
    """
    stem = head.rstrip()[:-1]  # the line without its trailing hyphen
    left_word = _word_at_end(stem)
    right_word = _word_at_start(tail)
    fused = f"{left_word}{right_word}"
    hyphenated = f"{left_word}-{right_word}"
    split_text = f"{left_word}-\n{right_word}"

    if _appears_elsewhere(fused, document, split_text):
        return stem + tail.lstrip()
    return stem + "-" + tail.lstrip()


def page_measure(lines: list[str]) -> float:
    """How wide this document's text actually runs, in characters.

    The 90th percentile rather than the maximum: one freak long line (a
    flattened table row, say) should not raise the bar for every real wrap.
    """
    lengths = sorted(len(line.rstrip()) for line in lines if line.strip())
    if not lengths:
        return 0.0
    at = min(int(WRAP_MEASURE_PERCENTILE * len(lengths)), len(lengths) - 1)
    return float(lengths[at])


def _continues(previous: str, nxt: str, wrap_min: float) -> str | None:
    """Is `nxt` the rest of `previous`, and if so how were they broken apart?

    Both tests are about `previous`, the line that ran out of room -- a trailing
    hyphen, or an ending that reached the margin without any punctuation. The
    only thing asked of `nxt` is that it starts in lower case, because a
    continuation always does and a new line almost never does.
    """
    head, tail = previous.rstrip(), nxt.strip()
    if not head or not tail or not _STARTS_LOWER.match(tail):
        return None
    if _HYPHEN_TAIL.search(head):
        return "rejoin-hyphen"
    if len(head) >= wrap_min and head[-1] not in _ENDS_SENTENCE:
        return "rejoin-wrap"
    return None


def _rejoin(lines: list[str], document: str) -> tuple[list[str], list[Change]]:
    """Pull continuation lines up onto the line they belong to.

    A cell can wrap more than once, so this groups a run of physical lines and
    merges the whole run. Each junction is judged on the physical line that
    ends it, never on the growing merged text -- otherwise the first join makes
    the line long, and a long line passes the margin test automatically, and
    the repair starts swallowing whatever follows.

    A merged line keeps the number of the line it started on and leaves empty
    lines behind. `LineIndex` skips empty lines without renumbering, so every
    line the repair did not touch keeps the number it had in the extracted
    text, and a human can still check it against the original by eye.
    """
    out = list(lines)
    changes: list[Change] = []
    wrap_min = max(page_measure(lines) * WRAP_MEASURE_FRACTION, MIN_ROW_LENGTH)

    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue

        # How far this run of continuations goes.
        run: list[tuple[str, str]] = []  # (kind of break, the continuing line)
        j = i + 1
        previous = lines[i]
        while j < len(lines):
            kind = _continues(previous, lines[j], wrap_min)
            if kind is None:
                break
            run.append((kind, lines[j]))
            previous = lines[j]
            j += 1

        if run:
            merged = lines[i].rstrip()
            for kind, tail in run:
                if kind == "rejoin-hyphen":
                    merged = _join_hyphenated(merged, tail, document)
                else:
                    merged = merged + " " + tail.strip()

            before = " \u23ce ".join([lines[i].rstrip()] + [t.strip() for _, t in run])
            changes.append(
                Change(
                    kind=run[0][0] if len({k for k, _ in run}) == 1 else "rejoin-mixed",
                    source_line=i + 1,
                    before=before,
                    after=merged,
                )
            )
            out[i] = merged
            for k in range(i + 1, j):
                out[k] = ""

        i = j if run else i + 1

    return out, changes


def _column_boundaries(words: list[str]) -> list[int]:
    """Indices where one column label ends and the next begins.

    The signature of a flattened row is a run of capitalised labels with no
    punctuation between them -- `systems Languages`, `data Infrastructure`,
    `Frontend Quality`. Punctuation is what normally separates things a human
    wrote on purpose, so its absence is the tell.
    """
    marks: list[int] = []
    for i in range(1, len(words)):
        previous, word = words[i - 1], words[i]
        if not word[:1].isupper():
            continue
        if previous.lower() in _CONNECTORS:
            continue
        if previous[-1:] in ",.;:&/-":
            continue
        marks.append(i)
    return marks


def _split_row(line: str) -> list[str] | None:
    """Unflatten one table row, or return None if this is not one.

    Only the run of labels at the FRONT of the line is split. Everything from
    the first comma onward is the first cell's contents and is left whole --
    splitting inside it would cut a sentence apart.
    """
    if len(line) < MIN_ROW_LENGTH or _ALREADY_DELIMITED.search(line):
        return None

    cut = min(
        (line.find(c) for c in ",.;" if line.find(c) != -1),
        default=len(line),
    )
    region = line[:cut]
    words = region.split()
    if len(words) < 2:
        return None

    marks = _column_boundaries(words)
    if len(marks) < MIN_COLUMN_BOUNDARIES:
        return None

    # The label run is everything up to the last boundary. If it is not mostly
    # capitalised it is a sentence with proper nouns in it, not a row of
    # headings -- `Built and operated REST APIs in Python serving 2M requests`
    # is the line that made this guard necessary.
    label_run = words[: marks[-1]]
    capitals = sum(1 for word in label_run if word[:1].isupper())
    if capitals / len(label_run) < MIN_CAPITAL_SHARE:
        return None

    pieces: list[str] = []
    bounds = [0, *marks, len(words)]
    for start, end in zip(bounds, bounds[1:]):
        pieces.append(" ".join(words[start:end]))

    # Three guards, and each one exists because it caught a real line that was
    # fine. Any failure refuses the WHOLE split: half-splitting a sentence is
    # worse than leaving a flattened row flattened.
    #
    #   no real word    `T E C H N I C A L` is a letter-spaced heading, not a
    #                   row of one-letter columns.
    #   lower-case head a column label never begins in lower case. This is what
    #                   tells `AI systems | Languages | Backend & data` from
    #                   `Built and operated REST APIs in Python serving ...`,
    #                   which splits into a piece starting `in Python`.
    #   a long label    a label is a heading, so it is short. Prose capitals
    #                   sit inside long lower-case runs; column labels do not.
    if not all(_WORDISH.search(piece) for piece in pieces):
        return None
    if not all(piece[:1].isupper() for piece in pieces):
        return None
    if any(len(piece.split()) > MAX_LABEL_WORDS for piece in pieces[:-1]):
        return None

    pieces[-1] = pieces[-1] + line[cut:]
    return pieces


def _unflatten(lines: list[str]) -> tuple[list[str], list[Change]]:
    out: list[str] = []
    changes: list[Change] = []
    for number, line in enumerate(lines, start=1):
        pieces = _split_row(line)
        if pieces is None:
            out.append(line)
            continue
        changes.append(
            Change(kind="split-row", source_line=number, before=line, after=" ⏎ ".join(pieces))
        )
        out.extend(pieces)
    return out, changes


def _normalise(line: str) -> str:
    """One space between words, and nothing hanging off either end.

    Whitespace only: no word is touched, nothing is invented, nothing is
    dropped. An all-whitespace line becomes empty, which `LineIndex` already
    skips without renumbering, so the line numbers do not move.
    """
    return _WHITESPACE_RUN.sub(" ", line).strip()


def repair(text: str) -> Repair:
    """Repair extraction damage, and record every change made.

    Three passes, and the ORDER is the whole of it.

    Rejoining first, because a table row whose first cell wrapped onto the next
    line is not fully present until the wrap is pulled up -- splitting it
    before that would cut a row we had only half of.

    Normalising LAST, and never before the other two. `_ALREADY_DELIMITED`
    recognises a column separator the extractor managed to keep, and a tab is
    one of the separators it looks for. Collapse the whitespace first and that
    signal is gone, `_split_row` stops seeing rows that are already intact, and
    it goes back to cutting up the Title Case job titles that brief 0007 took
    three attempts to protect. Row work first, whitespace second.

    The recorded changes are normalised too, so the before/after a person reads
    in "see how we read it" is the whitespace the text actually ended up with,
    rather than a third version of the line that exists nowhere.
    """
    lines = text.splitlines()
    joined, join_changes = _rejoin(lines, text)
    split, split_changes = _unflatten(joined)
    tidied = [_normalise(line) for line in split]
    changes = [
        replace(change, before=_normalise(change.before), after=_normalise(change.after))
        for change in join_changes + split_changes
    ]
    return Repair(
        text="\n".join(tidied) + ("\n" if text.endswith("\n") else ""),
        changes=changes,
    )

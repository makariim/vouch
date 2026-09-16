---
status: done
date: 2026-09-16
---

# 0020 — Read the PDF in reading order

> **You own `src/`, `tests/` and `pyproject.toml`.** Do not touch `web/`,
> `extension/`, `design/` or `fixtures/`.
>
> **One function changes:** `extract_text` in `src/audit/ingest.py`. If you find
> yourself changing anything else, stop and say so.

## 1. Goal

A PDF holds drawing instructions, not text. Pulling text out means deciding an
order, and `pypdf` uses the order the instructions sit in the file — which is
the order the design tool wrote them, not the order a person reads.

The author's real resume is laid out in two columns. It comes out shuffled:

```
   1  Mozn
   2  , AI Platform Engineer III
   3  Riyadh, Saudi Arabia | Aug 2025 to Present
   4  Microsoft
   5  Egypt | May 2022 to Aug 2025
   6  Muhammad Abdulkariim
   7  AI ENGINEER
```

His name is on line 6, under two employers. Line 2 begins with a comma.

**Nothing is missing. It is all there, in the wrong order.**

**`repair.py` cannot fix this and must not try.** It joins broken lines and
splits glued rows. It never moves a line, because moving lines means guessing
what belongs where.

**What it costs:** 160 fragmented lines where the same resume as plain text
gives 56 clean ones. Quotes come out as `", AI Platform Engineer III"`. And a
sentence split across two lines means retrieval only ever sees half the
evidence, which pushes verdicts toward `partly`.

**If we do not do this:** the product asks for a PDF and then reads it badly,
which is the one file type everybody has.

## 2. Scope

**Swap the PDF reader to `pdfplumber`.**

It keeps the position of every word on the page, so text can be ordered the way
a person reads: top to bottom, then left to right. `pypdf` only knows the order
the file was written.

**This was predicted before any PDF existed.** Report `0007`:

> `pdfplumber` keeps glyph coordinates and can reconstruct columns, which would
> have prevented the flattened row rather than repaired it. **This is the one to
> revisit.**

Change only `extract_text` in `src/audit/ingest.py`, plus the dependency in
`pyproject.toml`.

**Keep `pypdf` or remove it — your call, and say which and why.** If the new one
turns out worse on some file, being able to fall back is worth the line.

**Leave the errors as they are.** The four calm messages the page already shows
must keep working: not a PDF, corrupt file, a scanned PDF with no text layer,
not UTF-8. `pdfplumber` raises different exceptions; map them to the same
`IngestError` messages.

**Out of scope:**

- `repair.py`. It runs after this and stays exactly as it is
- OCR, or any attempt to read a scanned PDF. That error message stays
- anything in `web/`, `extension/`, `design/`, `fixtures/`
- tuning anything to make one resume look good

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything, no
changing a check because it failed, NOT ESTABLISHED rather than an estimate.

- **Do not reorder lines anywhere except inside the PDF reader**, using real
  positions from the file. Anywhere else it is guessing.
- **Do not change a word.** Extraction and repair both move text around; neither
  ever edits it.
- **Do not commit `private/`, `.env`, `resumes/`, `audits/`, or any PDF.**
- **Do not weaken the verbatim guarantees.** Whatever comes out is indexed, and
  quotes come from the index. That chain does not change.

## 4. Done when

- **The author's real resume comes out in reading order.** His name is on an
  early line, not under two employers, and no line begins with a stray comma.
- **The line count drops from 160 towards the 56 the plain-text version gives.**
  Say both numbers. They do not have to match — the point is the direction.
- All four error messages still appear for the four bad files.
- **The 172 existing tests still pass.** If one asserts something only true of
  `pypdf`, edit it and **say so in the report**.
- One real run through Groq on the re-read resume.

**What would tell us it failed:** the order is still wrong, or something that
used to read correctly now reads worse. Check a one-column document too, not
only the two-column one.

## 5. Checked by

`formwork check` and `pytest tests/ -q`.

Neither can see whether the order is right. The evidence is the first fifteen
lines, printed in the report.

## 6. The report must contain

The standing list, plus:

- **the first fifteen lines, before and after.** This is the whole brief
- **the line count and the repair count**, before and after, against 160 and 26
- **what happened to a one-column document** — confirmation that nothing that
  was fine got worse
- whether `pypdf` stayed or went, and why
- the counts on the real DataRobot post afterwards, against
  `8 evidenced / 12 partly / 3 not`, and whether `partly` fell

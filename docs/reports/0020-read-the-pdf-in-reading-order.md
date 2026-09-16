---
status: open
date: 2026-09-16
brief: 0020-read-the-pdf-in-reading-order
---

# 0020 — Read the PDF in reading order

**The author's name is now on line 1, and `partly` fell from 17 to 13 on the
real DataRobot post.** The reader is `pdfplumber`, ordering by where the
characters actually sit on the page. `repair.py` was not touched.

## The first fifteen lines, before and after

This is the whole brief, so it goes first.

**Before — `pypdf`, the order the file was written in:**

```
  1  'Mozn'
  2  ',\tAI\tPlatform\tEngineer\tIII'
  3  'Riyadh,\tSaudi\tArabia\t\t|\t\tAug\t2025\tto\tPresent'
  4  'Microsoft'
  5  'Egypt\t\t|\t\tMay\t2022\tto\tAug\t2025'
  6  'Muhammad\tAbdulkariim'
  7  'AI\tENGINEER'
  8  'Riyadh,\tSaudi\tArabia\t'
  9  '|'
 10  '\tmakariim214@gmail.com\t'
 11  '|'
 12  '\t+966\t55\t068\t9505\t'
 13  '|'
 14  '\tlinkedin.com/in/makariim\t'
 15  '|'
```

**After — `pdfplumber`, top to bottom then left to right:**

```
  1  'Muhammad Abdulkariim'
  2  'AI ENGINEER'
  3  'Riyadh, Saudi Arabia | makariim214@gmail.com | +966 55 068 9505 | linkedin.com/in/makariim | github.com/makariim'
  4  'SUMMARY'
  5  'AI engineer with six years building and operating production systems at scale. Core engineer on an enterprise knowledge intelligence'
  6  'platform for government and regulated customers, owning it end to end: ingestion and indexing across large corpora, agentic question'
  7  'answering, text-to-SQL, model serving and evaluation, and the deployment path into cloud, on-premise and fully air-gapped'
  8  "environments. Forward deployed into new accounts, where a demo built from independent research on the customer's own problem"
  9  'has replaced the proof-of-concept phase outright, taking accounts from a first meeting to procurement. Previously at Microsoft on high-'
 10  'traffic backend and data platforms, and among the first engineers to ship product on Copilot. Sets engineering standards and mentors,'
 11  'with five years teaching algorithms and systems across three universities and a public channel.'
 12  'EXPERIENCE'
 13  'Mozn, AI Platform Engineer III Riyadh, Saudi Arabia | Aug 2025 to Present'
 14  "Core engineer on OSOS, Mozn's enterprise knowledge intelligence platform, deployed to government and enterprise customers in cloud,"
 15  'on-premise and fully air-gapped environments.'
```

**The name is on line 1. No line begins with a stray comma.** The contact row
that was seven fragments is one line. The tabs are gone at source: **1,130
before, 0 after** — which is the same 1,130 brief `0018` stopped at the screen,
now never produced in the first place.

**Line 13 is still a flattened row** — title on the left, dates on the right,
joined into one line. That is correct and deliberate. It is the row `repair.py`
splits, and it is the thing the demo shows working.

## The counts

| | raw lines | indexed lines | repairs | tabs |
|---|---|---|---|---|
| before — `pypdf` | 188 | **160** | **26** | 1,130 |
| after — `pdfplumber` | 94 | **51** | **21** | 0 |
| the same resume as plain text | 94 | 56 | 23 | 0 |

**160 → 51, against the 56 the plain text gives.** The direction is the point
and it overshot slightly: the PDF wraps its lines at a different width than the
plain text file does, so repair joins a slightly different set. Both are now in
the same range, which they were not before.

Repairs fell 26 → 21. They did not fall to zero and should not have: 21 of them
are real broken lines and flattened rows in a correctly-ordered document.

## What happened to a one-column document

Nothing, which is what was wanted. The control is the author's other CV,
`Muhammad_Abdulkariim_Software_Engineer_AI_Platform_CV.pdf`, a single-column
document `pypdf` already read correctly.

| | non-blank lines | indexed lines | repairs |
|---|---|---|---|
| before | 108 | 89 | 32 |
| after | 108 | 89 | 32 |

**Zero differing lines** on a line-by-line diff, ignoring trailing whitespace.
The only change at all is that `pypdf` left trailing spaces on every line and
`pdfplumber` does not. Nothing that was fine got worse.

## The four errors

All four still appear, with the same wording:

```
a .docx                        unsupported file type .docx: upload .pdf or .txt
a corrupt PDF                  could not read resume.pdf as a PDF: No /Root object! - Is this really a PDF?
a scanned PDF (no text layer)  scan.pdf has no extractable text. A scanned PDF needs OCR,
                               which this tool does not do -- paste the text instead.
a .txt that is not UTF-8       resume.txt is not UTF-8 text: 'utf-8' codec can't decode byte 0xff...
```

The corrupt-PDF line now carries pdfminer's wording after the colon instead of
pypdf's. The sentence the user reads — *could not read X as a PDF* — is
unchanged, and it is the only part the page shows.

## `pypdf` stayed, as a fallback only

**Kept.** Not out of caution — I found the file that justifies it, and it was
already in this repository.

pdfminer, underneath pdfplumber, is the stricter parser. A PDF whose objects
run `>>endobj` together with no delimiter between them is malformed; `pypdf`
shrugs and reads it, pdfminer refuses the file outright. **This project's own
hand-built test PDF was exactly such a file** — `make_pdf` in
`tests/test_ingest.py` emitted `>>endobj`, and pdfplumber returned zero
characters from it.

So the reader tries pdfplumber, and falls back to pypdf only when pdfplumber
produced nothing at all — by raising, or by handing back empty pages. In front
of a demo, text in the wrong order beats a dead end.

**It never fires quietly.** A silent fallback would hand back shuffled text
while this function claims to have fixed exactly that, so it logs a warning
naming the file and saying the order is not reading order. There is a test that
asserts the warning, not just the text.

## The real run through Groq

The brief asks for the counts against `8 evidenced / 12 partly / 3 not`. That
baseline was measured in an earlier session, and the standing brief warns that
requirement extraction is a model call that varies — 23, then 21, then 22 on
this same post. So I ran **both** extractions through Groq today, same post,
same model, minutes apart, and that pair is the evidence:

| resume text | requirements | evidenced | partly | not | fit |
|---|---|---|---|---|---|
| before — `pypdf`, shuffled | 22 | 3 | **17** | 2 | weak |
| after — `pdfplumber` | 21 | **6** | **13** | 2 | worth applying |

**`partly` fell, 17 → 13. Evidenced doubled, 3 → 6.** The verdict moved from
*weak* to *worth applying* on the same resume and the same post — the only
thing that changed is the order the lines came out of the file.

This is the brief's own hypothesis confirmed: a sentence split across two lines
means retrieval sees half the evidence, and half the evidence scores `partly`.

**Against the recorded `8 / 12 / 3`, today's after-run of `6 / 13 / 2` looks
flat.** Do not read that as no improvement, and do not read it as a regression
either — it is two different runs of a model call on different days with a
different requirement count. **The controlled pair above is the only comparison
here that holds anything still.**

## What changed

- `src/audit/ingest.py` — `extract_text` now reads through `pdfplumber` and
  orders by character position, with `pypdf` behind it as a logged fallback.
  Two small helpers, one per reader, so each one's ordering rule is named. The
  module docstring's "which PDF library, and why" section was rewritten; it
  argued for the old choice.
- `pyproject.toml` — `pdfplumber>=0.11` added. `pypdf>=6.0` left in place.
- `tests/test_ingest.py` — `make_pdf` now emits a valid `\nendobj`, and takes
  `malformed=True` to emit the old broken form on purpose. One new test covers
  the fallback and its warning.

Nothing else was touched. `repair.py` is byte-for-byte unchanged, and so is
everything in `web/`, `extension/`, `design/` and `fixtures/`.

## What was run

```
uv pip install "pdfplumber>=0.11"        # + pdfminer.six, cryptography, charset-normalizer
.venv/bin/python -m pytest tests/ -q
formwork check
```

Two audits ran against Groq. Both wrote their JSON to the session scratchpad,
not into the repository, and the re-extracted resume text stayed there too — it
is the author's real resume and decision `0002` keeps it off disk here.

## The check

`formwork check` — **green. All 12 checks.**

`pytest tests/ -q` — **173 passed.** The 172 that existed all still pass; the
173rd is the new fallback test.

## Git status

Nothing staged.

```
 M docs/briefs/0020-read-the-pdf-in-reading-order.md
 M pyproject.toml
 M src/audit/ingest.py
 M tests/test_ingest.py
?? docs/reports/0020-read-the-pdf-in-reading-order.md
```

(alongside the files already modified before this brief started)

## The three that matter

**Done but not asked for.**

- **The fallback to `pypdf`, and the test for it.** The brief left the keep-or-
  remove call to me and said a fallback was worth the line if the new reader
  turned out worse on some file. It did, on a specific and reproducible class of
  file, so I built the fallback rather than just keeping the dependency
  declared and unused. The warning log is mine too: a fallback nobody can see
  fire is worse than no fallback.
- **`make_pdf` gained a `malformed` switch.** Needed to test the fallback at
  all. It is the exact bytes the helper used to emit.

**Asked for but not done.** Nothing.

**Wrong in the brief.** Two things, one of them worth acting on.

- **"laid out in two columns" is not quite what the file is.** I dumped the
  character coordinates before changing anything. It is a single column of
  *rows*, where each row has a left-hand title and a right-hand date, and the
  design tool emitted the employer blocks before the header. Sorting by
  position top-to-bottom then left-to-right fixes it completely — which is what
  the brief asked for, and why the fix worked. But the distinction matters for
  the next file.
- **This does not handle a true sidebar resume, and that is NOT ESTABLISHED.**
  On a resume with a genuine full-height left sidebar, sorting by y-then-x
  interleaves the two columns line by line. pdfplumber's default does not
  detect columns, and I did not add detection: there is no such file here to
  test against, and building a column detector against zero examples is the
  "tuning to make one resume look good" the brief rules out — just in the other
  direction. **Worth a brief of its own if a sidebar resume ever shows up.**

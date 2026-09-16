---
status: open
date: 2026-09-16
brief: 0017-upload-a-pdf-resume
---

# 0017 — Upload a PDF resume

**A real PDF uploads from the page, the line count and the repair count both
appear, an audit runs against it by `resume_id`, and "see how we read it"
shipped.** All four error paths show a calm sentence. Pasting still works and
the recordings still run.

**No backend change. Nothing outside `web/` was touched.**

The one thing this brief said it could break — a verdict citing a line number
that does not match the resume view — was checked rather than assumed. **14
verdicts, 14 line numbers, 14 identical lines.** How that was done is below.

## The numbers a real PDF produced

**56 lines. 23 repairs.** The same 56 and the same 23 the backend gets from
`private/resume.txt`, which is what that file already is: the raw pypdf
extraction of the real resume.

I had no `.pdf` to upload. There is none in the repository and there must not
be, so I built one in the scratchpad that holds the raw extracted lines, one
text operator each, and let `pypdf` extract it back for itself. It round-trips:
`index_resume` on the uploaded PDF and `index_resume` on `private/resume.txt`
both give 56 lines and 23 changes. The generator is
`scratchpad/mkpdf.py`; it is not in the repository and neither is its output.

    POST /resumes  ->  {"id":"resume","lines":56,"repaired":23,"default":true}

The rail says it like this:

    resume.pdf
    56 lines · your default
    23 lines came out of the file broken. We put them back.

Not the brief's own sentence, "your PDF lost 23 line breaks". One of the 23 is
a flattened table row, and repairing that one *adds* line breaks rather than
restoring lost ones. "Came out broken" is true of both kinds.

## Three of the repairs, before and after

**A word split across a line break** (`rejoin-hyphen`). `⏎` is where the file
had its break.

    out of the PDF   ... GCP Secret Manager, on-prem and air- ⏎ gapped deployment
    what we read     ... GCP Secret Manager, on-prem and air-gapped deployment

**A table row flattened into one line** (`split-row`). Six column headings had
been glued to each other and to the first cell's contents:

    out of the PDF   AI systems Languages Backend & data Infrastructure Frontend
                     Quality LLM orchestration, DSPy and ReAct agents, RAG and
                     hybrid retrieval, ...

    what we read     AI systems ⏎ Languages ⏎ Backend & data ⏎ Infrastructure ⏎
                     Frontend ⏎ Quality ⏎ LLM orchestration, DSPy and ReAct
                     agents, RAG and hybrid retrieval, ...

**A line that ran off the page** (`rejoin-wrap`), the commonest kind, 19 of the
23:

    out of the PDF   Core engineer on OSOS, Mozn's enterprise knowledge
                     intelligence platform, deployed to government and
                     enterprise customers in cloud, ⏎ on-premise and fully
                     air-gapped environments.
    what we read     Core engineer on OSOS, Mozn's enterprise knowledge
                     intelligence platform, deployed to government and
                     enterprise customers in cloud, on-premise and fully
                     air-gapped environments.

The 23 are 19 `rejoin-wrap`, 2 `rejoin-mixed`, 1 `rejoin-hyphen`, 1
`split-row`.

## The line numbers match. Checked, not assumed.

This is the one failure the brief names, so it was measured through the page
rather than reasoned about.

A browser uploaded the PDF through the page's own file input, filled the post
box, ran a live audit, then opened "see how we read it". The script then read
every quote the page had drawn, took the number printed on it, and compared it
to the text of the row carrying that number in `#resume-lines`.

    line   3  SAME      line  29  SAME      line  41  SAME
    line   5  SAME      line  33  SAME      line  43  SAME
    line  16  SAME      line  37  SAME      line  48  SAME
    line  20  SAME      line  38  SAME      line  53  SAME
    line  24  SAME      line  27  SAME
                                            14 matched, 0 did not

**The model was scripted, not called.** The claim under test is that
`index_resume` has exactly one caller, so a verdict's numbers and the view's
numbers come from one place — that is a claim about the seam, not about the
model. `ScriptedModel` drives the real graph, the real `LineIndex`, the real
store and both real endpoints, and it costs nothing and needs no key. A Groq
run would have tested the same seam with a slower, dearer and less repeatable
judge.

**And the page will not colour a line it cannot vouch for.** The view paints a
quoted line in its answer's colour only when the run that produced the answer
was run against *this* document. `ranAgainst` holds the resume id the last run
actually used, or `''` for pasted text, or `null` for a recording. Checked:
answers produced from pasted text colour **0** lines in the stored file's view.
That guard is the thing standing between this brief and two copies of one
resume on screen.

## "See how we read it" shipped

Not dropped. It has:

- every line, numbered, in mono, `pre-wrap`, character for character
- blank rows where the file had blank lines, so no number ever shifts.
  `GET /resumes/{id}` sends only the lines with something on them, keeping
  their own numbers, so a gap in the numbering *is* a blank line
- `⏎` beside a number where repair changed where that line begins or ends
- **what repair changed**, folded, `23 changes` on the button, each one with
  what came out of the PDF and what we read instead
- the lines quoted by the last run, in that answer's colour

**One thing it deliberately does not show: a repair's `source_line`.** That
number counts lines in the text *before* repair ran, so it is not the number in
the view and printing it would be exactly the two-sets-of-line-numbers failure
this brief is most able to cause. Repairs are listed with no line number at
all.

The `⏎` marks are placed by matching a repair's `after` text against the
displayed lines, and only where that text appears exactly once in the document.
Ambiguous ones are left unmarked and still listed in full. **28 glyphs for 23
changes** — splitting one flattened row puts six lines on screen from one
change — so the legend says what the glyph means rather than implying a count.

## The values `tokens.css` did not have

**One, and it is a real gap.** `design/canvas/Web.dc.html` caps the resume view
at `max-width: 800px`. `tokens.css` section 8 has `--v-answer-max: 760px` and
`--v-page-max: 1240px`, and nothing at 800.

I did not invent it. The view uses `--v-answer-max`, and the comment above it
says so. It is 40px narrower than the board. **Report it to design: either the
board should be 760, or section 8 needs a step for a reading column that is
wider than the answer column.**

Everything else was covered. The drop zone in particular:
`--v-bg-205`'s own comment in `tokens.css` names it — *"an inset well: the drop
zone, the empty paste box, the resume text"* — so the value was written for
this and was waiting.

Two literals I wrote and did not tokenise, both component padding, which
section 7 explicitly leaves to the component: `14px 16px` on the resume card,
matching the board's card, and `26px 18px` on the drop zone, matching the
board's drop zone. `web/styles.css` already does this and says why in its
header.

## What changed

Three files, all in `web/`.

- **`web/index.html`** — a drop zone and file input, the stored-resume card, a
  place for a refused upload, and the paste box kept underneath with its own
  label. A new `#resume-view` section in the answer column.
- **`web/styles.css`** — the drop zone, the card, the refusal block, the resume
  view, the numbered lines and the repair list. No literal colour, no font
  stack; 244 lines.
- **`web/app.js`** — upload, the refusal copy, the resume view, and the
  `resume_id` wiring through `/audit` and `/audit/requirement`.

**`app.js` does not touch the resume text.** It does not trim, join, split or
clean it. Repair is mechanical and lives in the backend, because the line
numbers every verdict cites are the numbers of the text repair produced.

## The four calm errors

The backend's own message picks the sentence; it is matched, never
re-diagnosed. Anything unrecognised is shown exactly as it arrived rather than
dressed up as something we understood. Driven through the page's file input:

| uploaded | what the page says |
|---|---|
| `notes.docx` | We can only read a PDF or a plain text file. |
| a truncated PDF | We could not open that PDF. |
| a PDF with graphics and no text | That PDF is a picture of your resume, not text. |
| a file that is not UTF-8 | We could not read the letters in that file. |

Each has a second line saying what to do, and every one of them offers the
paste box. The card stays hidden and nothing is stored.

## What was run

Nothing that wrote to the repository. Everything below wrote only to the
scratchpad.

    formwork/fw check

    # two throwaway servers, both storing resumes outside the repository
    AUDIT_RESUMES=<scratchpad>/resumes  uvicorn audit.server:app --port 8111
    AUDIT_RESUMES=<scratchpad>/resumes2 uvicorn scripted_server:app --port 8112

    # a browser, to drive the real page. Installed into its own scratchpad
    # venv, not the project's, so pyproject.toml and .venv are untouched.
    python3 -m venv <scratchpad>/pw && pip install playwright
    playwright install chromium

## The check

`formwork check`: **green. 12 checks.**

    ok    config-shape        ok    predictions-first
    ok    decision-ids        ok    role-shape
    ok    doc-links           ok    rule-labels
    ok    generated-current   ok    standing-current
    ok    guard-wired         ok    style-pointed
    ok    kit-integrity       ok    work-paired

**The gate cannot see a web page.** It says nothing about this brief. The
evidence is the sections above.

## Git status

    M docs/briefs/0010-learn-the-system.md
    M docs/briefs/0017-upload-a-pdf-resume.md
    M web/app.js
    M web/index.html
    M web/styles.css
    ?? docs/briefs/0018-pdf-tabs-and-nice-to-have.md
    ?? docs/reports/0017-upload-a-pdf-resume.md

Nothing staged. `0010` and `0018` were already in the tree and are not mine.
`resumes/` and `private/` are both in `.gitignore`, so no resume and nothing
built from one can reach a commit.

## The three that matter

**Done but not asked for.**

- **`ranAgainst`, and the rule that a line is only coloured when the answers
  came from the same document.** The brief asked for the coloured lines; it did
  not say what happens when the last run was on pasted text. Painting them
  anyway would have been the exact failure the brief names, so the guard went
  in and was tested.
- **A note in the rail when a file and pasted text are both on screen.** The
  backend prefers the id when both arrive. That is a silent choice, so the page
  says which one it will check, and offers to stop using the file.
- **Blank rows in the resume view.** Not asked for. Without them the numbering
  jumps and the view looks broken at exactly the moment a person is checking a
  number.
- **`⏎` marks on repaired lines.** The brief says "the repairs marked"; the
  canvas does not draw this and the API gives no mapping, so the marking is by
  unique text match and refuses to guess.

**Asked for but not done.**

- **The page does not pick up an already-stored resume on load.** Upload a
  file, reload, and the rail is empty again though the backend still has it.
  The brief put "several resumes, switching the default" out of scope and this
  sits next to that. It also makes "stop using this file" honest — it stops
  using it here, and deletes nothing. `GET /resumes` exists if this should
  change; say so and it is small.
- **Nothing else.** Every done-when item is closed.

**Wrong in the brief.**

- **"Your PDF lost 23 line breaks" is not true of all 23.** One is a flattened
  table row, where repair adds breaks. The copy on screen says "came out of the
  file broken" instead.
- **The brief says `GET /resumes/{id}` returns "every line with its number".**
  It returns every *non-blank* line. Blank ones are skipped by `LineIndex` and
  their numbers simply do not appear. Not a fault — the numbering is
  untouched — but a client that assumed a dense list would draw the resume
  wrong.
- **The canvas caps this view at 800px and `tokens.css` has no such step.** See
  above.

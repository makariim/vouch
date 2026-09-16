---
status: open
date: 2026-09-16
brief: 0018-pdf-tabs-and-nice-to-have
---

# 0018 — Tabs from PDFs, and headings without a colon

**Both bugs are fixed, both traps were checked rather than avoided, and both
fixes are mechanical — no model goes near either one.** 172 tests pass, the
gate is green, and the audit ran twice through Groq afterwards.

**Only `src/audit/repair.py`, `src/audit/product.py`, `tests/test_repair.py`
and `tests/test_product.py` were touched.** Nothing in `web/`, `extension/`,
`design/` or `fixtures/`.

## Bug one — the tabs are gone

A third pass, `_normalise`, collapses every run of whitespace on a line to a
single space and strips the ends. It changes no word and invents no character,
which is the only kind of edit that file is allowed to make.

The real uploaded resume, straight out of `pypdf`:

    line 1    'Mozn'
    line 2    ',\tAI\tPlatform\tEngineer\tIII'
    line 3    'Riyadh,\tSaudi\tArabia\t\t|\t\tAug\t2025\tto\tPresent'

The same lines as a quote is now sliced out of them:

    line 1    'Mozn'
    line 2    ', AI Platform Engineer III'
    line 3    'Riyadh, Saudi Arabia | Aug 2025 to Present'

**1,130 tab characters in the file. 0 in the text the index is built from.**
The document still reads **160 lines and 26 repairs** — the same two numbers
the brief quotes, so nothing but whitespace moved.

### The trap, and why the order is the fix

`_ALREADY_DELIMITED` recognises a column separator the extractor managed to
keep, and a tab is one of the separators it looks for. Collapse the whitespace
first and that signal is gone, `_split_row` stops seeing rows that are already
intact, and it goes back to cutting Title Case job titles into single words.

So **`_normalise` runs last**, after both repair passes, and there is a test
holding it there: a tab-delimited row of job titles is left unsplit, and comes
out with its tabs turned to spaces and nothing else done to it.

### The three clean documents are still untouched

Not asserted — run:

    tests/data/resume.txt              changes=  0   text identical=True
    tests/data/resume_unrelated.txt    changes=  0   text identical=True
    tests/data/post.txt                changes=  0   text identical=True

`test_every_clean_document_is_still_untouched` now checks all three rather than
just the resume, which is what the brief asked to be proved.

**The recorded changes are normalised too.** A person reading "see how we read
it" compares a before and an after; if the text kept one whitespace and the
change record showed another, they would be reading a third version of the line
that exists nowhere.

## Bug two — a heading without a colon

`_heading_above` now asks `_is_heading`, and a heading is recognised by shape
as well as by a colon: at most 60 characters, at most six words, not ending the
way a sentence ends, and at least half its words capitalised.

Every one of those is holding something back rather than reaching for cases.
Drop the capital share and `Remote work is preferred here` becomes a heading
and marks a whole section optional. The length limit and the stop-at-a-paragraph
rule are both unchanged.

### The split on that post, before and after

The post itself is not in the repository — decision 0002, it is personal data.
What is stored is its audit, `resumes/audits/92cec4ae….json`, which holds the
eleven requirement texts. So the section was reconstructed from those texts plus
the heading the brief quotes, hard-wrapped at 72 characters the way a pasted
post is:

    before    11 required, 0 nice to have
    after      7 required, 4 nice to have   (requirements 8, 9, 10, 11)

All four resolve to the heading `Nice to Have`, and the item above it stays
required.

**Why all four and not only the first.** The items below the first one reach
the heading by walking up through the *wrapped* lines of the item above — each
one short, none of them heading-shaped. That is also what the 60-character cap
is for: the line `Experience in a forward-deployed, solutions engineering,
consulting, or` ends without punctuation and would otherwise pass.

### A short ordinary line above a required item

`test_a_short_ordinary_line_above_a_requirement_is_not_a_heading`. The line is
`We work remotely and travel is preferred` — short, carrying an optional
marker, sitting directly above the requirement. One capitalised word in seven,
so it is not a heading, the walk continues past it, and the requirement below
stays **required**.

## The real DataRobot post

**No required flag moved.** Checked against the 21 requirements in
`fixtures/trace-real.json`, under the old rule and the new one:

    21 requirements | required 20, nice to have 1 | flags changed: 0

The post does contain ten bare headings the new rule now sees — `Wow Our
Customers`, `Set High Standards`, `Deliver Results` and the rest of the
operating principles. None of them sits above a requirement and none carries an
optional marker, so nothing downstream of them changed.

## Two real runs through Groq

**Against the PDF-uploaded resume** (160 lines, the one with the tabs). Every
quote on screen is clean. The one that shows it:

    PART 21. DataRobot Experience: Familiarity with the DataRobot AI Platform
             is a strong plus.
             resume line 2: , AI Platform Engineer III

Before this change that line read `,\tAI\tPlatform\tEngineer\tIII`.

    evidenced 5   partly 16   not evidenced 1     (22 requirements)

**Against `private/resume.txt`**, which is the resume the `8 / 12 / 3` baseline
was measured on:

    evidenced 4   partly 14   not evidenced 3     (21 requirements)

**The counts moved, and nothing in this change can have moved them.** Two
things say so. Repair makes **zero changes** to `private/resume.txt` — it has
no run of whitespace anywhere in it, so `_normalise` is a no-op on that file
and the text handed to the model is byte-identical to before. And no required
flag on that post changed, measured above. What moved is the requirement count
itself: **23 in the standing brief, 21 in this run, 22 in the other** — the
extraction is a model call, and it is not deterministic. The verdict counts are
not comparable run to run and never were. **NOT ESTABLISHED** that the fix
changed them; established that it could not have.

## The gate

    ok    config-shape        ok    predictions-first
    ok    decision-ids        ok    role-shape
    ok    doc-links           ok    rule-labels
    ok    generated-current   ok    standing-current
    ok    guard-wired         ok    style-pointed
    ok    kit-integrity       ok    work-paired

    GATE: green. 12 check(s)

    172 passed in 1.99s

The brief says 154 tests. There were 164 in the tree before this work; eight
were added here.

## Git status

    M docs/briefs/0010-learn-the-system.md
    M src/audit/product.py
    M src/audit/repair.py
    M tests/test_product.py
    M tests/test_repair.py
    M web/app.js
    M web/index.html
    M web/styles.css
    ?? docs/briefs/0017-upload-a-pdf-resume.md
    ?? docs/briefs/0018-pdf-tabs-and-nice-to-have.md
    ?? docs/briefs/0019-page-demo-safety.md
    ?? docs/reports/0017-upload-a-pdf-resume.md
    ?? docs/reports/0018-pdf-tabs-and-nice-to-have.md
    ?? docs/reports/0019-page-demo-safety.md

Nothing staged, nothing committed. Of those, only the four files above the line
and this report are mine. The `web/` and `0010` changes, and everything numbered
`0017` or `0019`, were already in the tree. `private/`, `resumes/` and `audits/` are all in
`.gitignore`; both audit runs wrote their JSON to the scratchpad, not the
repository.

## The three that matter

**Done but not asked for.**

- **The recorded changes are normalised, not just the text.** The brief asked
  for tab-free quotes. The repairs are on screen too, in the same view, and
  showing a before/after in whitespace the text does not have would be worse
  than showing tabs.
- **The clean-document test now covers all three documents.** It covered one.
  The brief asked for the proof on three, so the test is the proof rather than
  a paragraph in this report.

**Asked for but not done.**

- **The four-nice-to-have number is from a reconstruction, not from the post.**
  The post is not stored anywhere — only its audit is, and that keeps the
  requirement texts and not the source. The reconstruction uses those exact
  texts and the heading the brief quotes, and the wrapping is the assumption in
  it: at 72 characters all four items resolve, and **if that post was pasted
  unwrapped, only the first would**. Paste the post once and this becomes a
  measurement instead of an argument.
- **Nothing else.** Every other done-when item is closed.

**Wrong in the brief.**

- **"The 154 existing tests still pass" is the wrong number.** There were 164
  before this work. 172 now.
- **Fixing the colon alone does not give four nice to have.** It gives one. The
  other three only arrive because the requirement above them is hard-wrapped
  into short lines that the walk can pass through. On an unwrapped post the
  same fix marks **one of the four optional and the other three required** —
  measured, both ways, on the same eleven texts. The brief treats the four as a
  consequence of the
  colon rule; it is a consequence of the colon rule **and** how that post was
  pasted.
- **`repair.py` line 61 does not "never turn the tabs back into spaces"
  wrongly.** It was never that function's job — the line is a guard, and the
  brief's own trap section says why touching it would be the wrong fix. The
  missing pass was missing, not broken.

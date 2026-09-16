---
status: done
date: 2026-09-16
---

# 0018 — Tabs from PDFs, and headings without a colon

> **You own `src/` and `tests/`.** Do not touch `web/`, `extension/`,
> `design/` or `fixtures/`.
>
> **Two bugs, both found by uploading a real PDF and auditing a real post.**
> Both are on the demo path. Both are small and both have a trap in them.

## 1. Goal

Uploading the real resume as a PDF worked — 160 lines, 26 repairs. Two things
came out wrong, and a person watching would see both.

**If we do not do this:** every quote on screen is full of tab characters, and
a post with a "Nice to Have" section reports nothing as nice to have.

## 2. Bug one — tabs survive into every quote

`pypdf` returns words separated by **tab characters**, not spaces. The
"See how we read it" view shows it plainly:

```
Muhammad	Abdulkariim
AI	ENGINEER
Riyadh,	Saudi	Arabia		|		Aug	2025	to	Present
```

`repair.py` line 61 treats a tab as a delimiter that is already there:

```python
_ALREADY_DELIMITED = re.compile(r"\||\t|│|   ")
```

That stops it wrongly splitting a row. **It never turns the tabs back into
spaces.** So the index keeps them, and every quote published on screen keeps
them.

**The fix:** collapse runs of whitespace into a single space, mechanically. No
word changes. It must happen **before indexing**, like every other repair, so
the line numbers and the quotes stay consistent with each other.

> **The trap.** `_ALREADY_DELIMITED` uses the tab to recognise a table row. If
> you collapse whitespace first, that signal is gone and repair will start
> splitting rows it should leave alone — the exact bug report `0007` took three
> attempts to stop.
>
> **Do the row work first, normalise second.** And prove it: after the change,
> repair must still make **zero changes** to `tests/data/resume.txt`,
> `resume_unrelated.txt` and `post.txt`.

## 3. Bug two — a heading without a colon is invisible

A real post carries this:

```
Nice to Have

Experience in a forward-deployed, solutions engineering, consulting, or
customer-facing technical role.
...
```

The page reported **"11 things they ask for · 11 required, 0 nice to have"**.

`_heading_above` in `product.py` only accepts a heading that ends with a colon:

```python
if line.endswith(":") and len(line) <= _HEADING_MAX:
    return line
```

`Nice to Have` has no colon, so it is skipped. The search walks further up,
hits a paragraph, and stops. `"nice to have"` is in `OPTIONAL_MARKERS` and never
gets the chance to match.

**The fix:** a short line above a requirement is a heading whether or not it
ends with a colon. `Nice to Have`, `Preferred Qualifications`, `Bonus points`
and `Nice-to-haves` are all real headings on real posts.

> **The trap.** Loosen it too far and an ordinary short sentence becomes a
> heading, and one stray "preferred" marks a whole section optional. Keep the
> length limit, keep the stop-at-a-paragraph rule, and **test a post where a
> short ordinary line sits above a required item** — it must stay required.

## 4. Must not happen

Standing ones apply: no writing to version control, no deciding anything, no
changing a check because it failed, NOT ESTABLISHED rather than an estimate.

- **Do not let a model near either of these.** Both are word and whitespace
  work. `product.py` says so in its own comment and it is right.
- **Do not change any word of a resume or a post.** Whitespace only.
- **Do not weaken the verbatim guarantees.** Normalising before indexing keeps
  the index and the quotes in step. Anything after indexing breaks them.
- **Do not commit `private/`, `.env`, `resumes/`, `audits/` or audit output.**

## 5. Done when

- A quote from a PDF-uploaded resume has **no tab characters in it**.
- Repair still makes **zero changes** to the three clean test documents.
- The real post with a `Nice to Have` section reports **four nice to have, not
  zero**.
- A short ordinary line above a required item does **not** make it optional.
  Write that test.
- **The 154 existing tests still pass.**
- One real run through Groq afterwards.

**What would tell us it failed:** repair starts splitting rows it used to leave
alone, or a required item is reported as nice to have.

## 6. Checked by

`formwork check` and `pytest tests/ -q`.

## 7. The report must contain

The standing list, plus:

- **a quote from the PDF resume, before and after** — showing the tabs gone
- **the required / nice-to-have split** on that post, before and after
- confirmation the three clean documents are still untouched by repair
- whether the counts moved on the real DataRobot post, against
  `8 evidenced / 12 partly / 3 not`

---
status: done
date: 2026-09-15
---

# 0007 — Backend: ingestion and the product layer

> **Wave 1, stream 2.** Runs at the same time as `0006`, `0008`, `0009`.
> **You own `src/`, `tests/`, `pyproject.toml` and `fixtures/`.** Do not touch
> `web/`, `extension/` or `design/` — three other sessions are in them now.

## 1. Goal

Two things. Fix the quality floor, then turn a report into an answer.

**The floor:** the resume comes from a PDF and the extraction is damaged. Line 73
is a flattened table row, line 79 ends mid-word on `air-`. Quotes read as
fragments and it is costing verdicts.

**The answer:** 21 rows of verdicts is a report. A job seeker wants to know
whether to apply, what would sink it, and where their resume undersells them.

**If we do not do this:** the demo shows broken quotes, and the output is a table
nobody can act on.

## 2. Scope

Decision `0005` is the contract. Build exactly what it specifies.

**Ingestion**

- **PDF upload and text extraction.** Pick a library; say which and why.
- **Mechanical line repair** — rejoin a word split across lines, split a
  flattened multi-column row. **No model call.** A model that rewrites the
  resume destroys the verbatim guarantee, which is the whole product.
- **Resume storage as plain local files**, with a default. Not a database.
- **`GET /resumes/{id}`** returns the indexed lines, numbered, so a human can see
  what the tool sees before trusting a verdict.

**The product layer**

- **`required` on every requirement.** The post's own words decide it —
  *a strong plus*, *preferred*, *nice to have* mean `false`.
- **The `summary` event:** `fit`, `fit_reason`, `blockers`, `strengths`,
  **`undersells`**.
- **`undersells` is the headline.** A `partly_evidenced` where the evidence is
  genuinely present and the resume states it weakly. If this comes out empty or
  nonsense on a real run, **say so** — decision `0005` says that changes the
  product claim, not the wording.

**The pre-screen**

- **`POST /prescreen`** — BM25 only, no model call, no network. Milliseconds.
- Prove it makes no model call. A test that fails if one is attempted.

**Out of scope:**

- the retry trigger and `evidence_weak`. Still broken, still deliberate
- prompt rewriting to improve verdicts
- anything in `web/`, `extension/`, `design/`
- the tailor

## 3. Must not happen

- **Do not weaken the verbatim guarantees.** Quotes are looked up by line number
  and read out of the resume. Line repair happens **before** indexing, so the
  index and the quotes stay consistent with each other.
- **Do not let a model touch the resume text.** Repair is mechanical or it does
  not happen.
- **Do not commit `private/`, `.env`, resumes, or audit output.**
- **Do not change decision `0005`.** Three sessions are building against it.
  Report a problem, do not fix it alone.
- Do not add a database.

## 4. Done when

- A PDF uploads, extracts, repairs and indexes, and `GET /resumes/{id}` shows the
  lines a human can check.
- **Line 79's `air-` / `gapped deployment` split is repaired**, with a test.
- Every requirement carries `required`.
- `summary` is emitted with all five fields.
- `POST /prescreen` returns in **under 100ms** with no model call, proven by a
  test that fails if one is attempted.
- The existing 38 tests still pass.
- One real run on the real post, with the new output in the report.

**What would tell us it failed:** repair mangles a line that was fine, or
`undersells` names things that are not actually in the resume. Either is worse
than not shipping the feature.

## 5. Checked by

`formwork check` and `pytest tests/ -q`.

Neither can tell whether `fit` is a fair call. The evidence is the real run in
section 6.

## 6. The report must contain

The standing list, plus:

- **the full real run**, with the summary block
- **the before and after of line repair** — which lines changed, shown
- **what `undersells` actually returned**, item by item, and whether each is true
- which PDF library, and what it did to the damaged lines
- the pre-screen timing, measured
- whether the retry fired. It has not in three runs

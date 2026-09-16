---
status: open
date: 2026-09-15
---

# 0015 — Backend: the last four gaps

> **You own `src/` and `tests/`.** Do not touch `web/`, `extension/`,
> `design/` or `fixtures/`.
>
> **Decision `0008` governs this brief and must be `accepted` before you start.**
>
> **This is small on purpose.** Four changes, all of them named by wave 2, none
> of them new design. If it grows, stop and say so.

## 1. Goal

Wave 2 shipped. Four gaps came back, each one field or one word wide, each one
blocking something visible.

**If we do not do this:** the panel draws two-thirds of its design, and the
largest sentence on the page breaks the product's own writing rule.

## 2. Scope

**1. `POST /summary` returns `counts` and `requirements`.** Both already sit in
the stored file. `requirements` is id, text, required — the same shape the
`requirements` event carries. Nothing recomputed.

**2. `repair` joins the step set.** `events.py` has `STEPS` as decision `0006`
wrote it and `EMITTED_STEPS` with `repair` added, kept apart deliberately by
brief `0012`. Decision `0008` rules that `repair` is a step. Make them one set.

**3. `GET /resumes` items carry `name`.** The filename the resume came from, or
the id where there is nothing better. The panel says what it checked you against
and can only show `resume` today.

**4. `fit_reason` stops using "evidence" as a verb.** It produces *"0 of 4
requirements are evidenced in your resume"*. Plain English, as `design/README.md`
sets out — *"Your resume shows 0 of 4 things they ask for"* is the register. The
page renders this verbatim and is right to.

**Out of scope:**

- the retry, the graph, the prompts. They work
- anything in `web/`, `extension/`, `design/`, `fixtures/`
- a cap on retries. Decision `0007` names it as the fix if the retry ever fires
  everywhere; the disjoint pair fires 6 of 6 and the real post fires 3 of 23.
  **Not now** — it needs a number from a run we have not done
- serving `design/` from the backend. Two clients now hold copies of
  `tokens.css`. Real, and not worth touching in the last wave

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything, no
changing a check because it failed, NOT ESTABLISHED rather than an estimate.

- **Do not weaken the verbatim guarantees.**
- **Do not recompute a judgement to fill a field.** `counts` and `requirements`
  are read from the stored file or they do not ship.
- **Do not commit `private/`, `.env`, `resumes/`, `audits/` or audit output.**
- **Do not rewrite `fit` itself.** Only the sentence's wording changes.

## 4. Done when

- `POST /summary` returns `counts` and `requirements` for a known post, and
  still `{"known": false}` for an unknown one.
- One step set, with `repair` in it.
- `GET /resumes` items carry `name`.
- No `fit_reason` string uses "evidence", "evidenced" or "evidencing" as a verb.
  Assert it in a test over every branch, not by reading the code once.
- **The 154 existing tests still pass.**
- One real run through Groq, and the new `fit_reason` quoted in the report.

**What would tell us it failed:** a field is computed rather than read, or the
new wording reads worse than what it replaced.

## 5. Checked by

`formwork check` and `pytest tests/ -q`.

## 6. The report must contain

The standing list, plus:

- **the new `fit_reason` sentence**, quoted, from a real run
- what `POST /summary` now returns, as JSON
- whether anything in decision `0008` turned out wrong
- the run time and the counts, against `8 evidenced / 12 partly / 3 not`

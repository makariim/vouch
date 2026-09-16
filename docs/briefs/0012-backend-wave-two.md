---
status: done
date: 2026-09-15
---

# 0012 — Backend: the retry, and the contract's holes

> **You own `src/`, `tests/`, `pyproject.toml` and `fixtures/`.** Do not touch
> `web/`, `extension/` or `design/` — other sessions are in them.
>
> **Two decisions govern this brief: `0006` and `0007`.** Both must be
> `accepted` before you start. If either still says `proposed`, stop and say so.

## 1. Goal

Two things, and they are in one brief because they are both `src/` and a second
session in there would collide.

**The retry has never fired.** Three real runs, 0 of 21, 0 of 23, 0 of 21. The
agent claim in decision `0001` rests on it. Decision `0007` changes what
triggers it.

**Two clients cannot render what they were built to render.** Decision `0006`
closes seven gaps found by briefs `0008` and `0009`.

**If we do not do this:** the strongest claim in the project has never happened,
and the extension shows a word count where its answer should be.

## 2. Scope

### The retry — decision `0007`

`src/audit/graph.py`, the `verify` node, line 219 today:

```python
weak = bool(judgement.get("evidence_weak")) and verdict != "evidenced"
```

**Replace the trigger.** Go round again when the first pass returns
`not_evidenced`. Keep the failed-quote trigger exactly as it is. Drop
`evidence_weak` as a trigger.

Leave `evidence_weak` in the schema. Removing it is a separate change and this
is the last wave.

**The retry step event must say why**, in plain words, because it appears in the
demo. Something a person reads and understands, not a flag name.

### The contract — decision `0006`

- **`POST /summary`** `{post, resume_id}` → the stored summary, or
  `{"known": false}`. Keyed on a hash of the post text plus the resume id,
  stored as a local file beside the resumes. Written whenever an audit finishes.
- **`POST /audit/requirement`** `{post, resume_id|resume, requirement_id}` →
  the same event stream as `/audit`, for that one requirement. **It re-emits
  `summary` when it finishes.**
- **One shape for the three summary lists.** `blockers`, `strengths` and
  `undersells` all carry `requirement_id`, `text`, `line`, `line_number`,
  `reason`, with `null` where a field does not apply.
- **`fit_reason` counts every requirement**, the same set the counts row shows.
  Not required-only. Two different totals on one screen read as a bug.
- **`signal`** is `worth_a_look | maybe | skip`. **`step`** is
  `search | judge | verify | retry | failed | dropped`. Both already true of the
  code; write them into `events.py` so they are checkable.
- **`required` absent means required.**

**Out of scope:**

- prompt rewriting. Same rule as every brief before this
- anything in `web/`, `extension/`, `design/`
- removing `evidence_weak` from the schema
- the tailor, Langfuse, the extension

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything — stop
and report, no changing a check because it failed, and where something cannot be
established, say so rather than estimating.

Specific to this work:

- **Do not weaken the verbatim guarantees.** Quotes are still looked up by line
  number and read out of the resume.
- **Do not commit `private/`, `.env`, `resumes/`, or any audit output.** The
  stored summaries are audit output and must be ignored too.
- **Do not let a stored summary answer for a resume it was not built from.** The
  key includes the resume id. If a stored answer cannot be trusted, return
  `{"known": false}` rather than something stale.
- **Do not call the re-run endpoint a retry**, in code, comments or events. A
  person asking for a second pass is not the agent deciding. Decision `0007`.

## 4. Done when

- **The retry fires on the real post**, without anybody pressing anything, and
  appears in the trace as a `retry` step with a readable reason.
- `POST /summary` returns a stored answer for a post already audited, and
  `{"known": false}` for one that has not been.
- `POST /audit/requirement` streams one requirement and ends with a fresh
  `summary`.
- All three summary lists carry the same five fields.
- **The 114 existing tests still pass.** Where one asserts a shape decision
  `0006` changes, edit it and **say so in the report** — the last brief hit this
  and it was not anticipated.
- One real run on the real post, through Groq.

**What would tell us it failed:** the retry fires everywhere and the run takes
three minutes, or a stored summary answers with something that is no longer
true.

## 5. Checked by

`formwork check` and `pytest tests/ -q`.

Neither can tell whether the retry fired for a good reason. The evidence is the
real run in section 6.

## 6. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- **how many times the retry fired on the real post, and on which
  requirements.** This is the whole point of the brief
- **what the agent searched for the second time**, in its own words, for each
  one — and whether the second pass changed the verdict
- **how much longer the run took** than the 58 seconds it took before
- the new counts, against `6 evidenced / 13 partly / 2 not`
- whether `undersells` still returns the false positive that brief `0007`
  predicted line repair would remove
- anything in decision `0006` or `0007` that turned out wrong

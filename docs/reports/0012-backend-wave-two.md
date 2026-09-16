---
status: open
date: 2026-09-15
brief: 0012-backend-wave-two
---

# 0012 — Backend: the retry, and the contract's holes

**The retry fired. Three times on the real post, without anybody pressing
anything.** Requirements 3, 20 and 22. It is in the trace as a `retry` step
with a sentence a person can read.

Both decisions were `accepted` before I started, so nothing was blocked.

**All seven contract gaps in decision `0006` are closed**, and both new
endpoints are tested against the real handlers.

**One thing the brief did not anticipate, and it is the most interesting thing
in here.** The new trigger broke a test that had nothing to do with either
decision — the disjoint pair. Investigating it found a real defect, but not
where it looked. Section *The three that matter* has it.

## What changed

Everything is in `src/`, `tests/` and `.gitignore`. Nothing in `web/`,
`extension/` or `design/` was opened.

- `src/audit/graph.py` — the retry trigger is now a first pass returning
  `not_evidenced`, and the failed-quote trigger is untouched. `evidence_weak`
  is no longer read here. The graph also learned to run one requirement, via
  `only_id` and a new `_resume_at` seam.
- `src/audit/store.py` — new. Finished audits as JSON files in
  `resumes/audits/`, keyed on a hash of the post plus the resume id.
- `src/audit/server.py` — `POST /summary` and `POST /audit/requirement`, and
  `/audit` now remembers what it finished.
- `src/audit/events.py` — `SIGNALS`, `STEPS`, `summary_item`, and
  `requirement_is_required` so the absent-means-required rule lives in one
  place.
- `src/audit/product.py` — all three summary lists built by `summary_item`;
  `fit_reason` counts every requirement.
- `src/audit/cli.py` — renders the new list shape without joining back
  against the verdicts.
- `src/audit/testing.py` — a `blank_once` mode so the new trigger can be
  exercised offline, and one fix to the stand-in's judge. See below.
- `.gitignore` — `audits/`, for the case where `AUDIT_RESUMES` points outside
  `resumes/`.

### Why the re-run goes back through the graph

`/audit/requirement` does not have its own copy of search-judge-verify. It
seeds the same graph with the requirement list and the earlier verdicts, sets
`only_id`, and lets `advance` finish after one.

Two reasons, and the second is the one that matters.

In LangGraph a node returns a partial state update and the rest persists, so
seeding `verdicts` with the other requirements' results means `report`
computes the closing `summary` over the whole audit with one verdict replaced
— which is exactly what decision `0006` asks for, with no extra code.

And the retry edge is the thing decision `0001` points at when asked where the
agent decides anything. A second copy of the control flow would mean two
answers to that question.

Skipping extraction also keeps the ids stable. Re-extracting would renumber
the moment the model split a sentence differently, and the client's
requirement 3 would silently become a different sentence.

## What was run

- `pytest tests/ -q` — **154 passed**.
- `./formwork/fw check` — green, below.
- Three real runs through Groq, on the real post and resume in `private/`.
  Output went to the scratchpad, not the repository.

## The check

```
ok    config-shape          ok    role-shape
ok    decision-ids          ok    rule-labels
ok    doc-links             ok    standing-current
ok    generated-current     ok    style-pointed
ok    guard-wired           ok    work-paired
ok    kit-integrity
ok    predictions-first

GATE: green. 12 check(s), each shown to reject the wrong and accept the right.
```

## Git status

Nothing staged. No `resumes/`, no `audits/`, no `private/`, no `.env`.

```
 M .claude/agents/director.md
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
 M formwork/limits.md
 M formwork/roles/method/director.md
?? .gitignore
?? docs/briefs/0012-backend-wave-two.md
?? docs/reports/0012-backend-wave-two.md
?? src/
?? tests/
   ... and the other untracked briefs, decisions and reports from wave 1
```

`src/` and `tests/` are untracked as whole folders, so the new files inside
them do not list separately. That is how the tree already was.

---

## The retry, on the real post

**Three times, on requirements 3, 20 and 22.** All three were `not_evidenced`
on the first pass, and no human touched anything.

What it searched the second time, in its own words:

**Requirement 3** — agentic AI on DataRobot, using LangGraph, CrewAI, Llama
Index.

> ReAct agents, DSPy, RAG, retrieval-augmented generation, LLM orchestration,
> prompt engineering, vLLM, LiteLLM, agentic query, multi-step OCR,
> embeddings, VLM — *"These terms appear in the resume and map to the required
> agentic AI frameworks and deployment skills, offering alternative keywords
> not yet tried."*

**Requirement 20** — a Master's or Ph.D.

> M.Sc. MSc MEng M.Eng Doctorate "Graduate degree" "Postgraduate degree"
> "Advanced degree" ... — *"These terms capture master's and Ph.D.
> qualifications using alternative abbreviations and phrasing not previously
> tried."*

**Requirement 22** — familiarity with the DataRobot AI Platform.

> DataRobot Model Management, DataRobot API, DataRobot Predict, DataRobot
> Model Deployment ... — *"Uses alternative component names and related terms
> for the DataRobot platform that may appear in a resume instead of the
> generic product name."*

**No second pass changed a verdict.** All three stayed `not_evidenced`.

That is the honest outcome and I think it is the better one to present. The
three it went back for are the three things this candidate genuinely does not
have. The agent looked again, with terms a person would recognise as sensible,
and confirmed the answer instead of talking itself into one.

**The failed-quote trigger also fired, on a second run.** Requirement 18, the
model quoted text that did not match line 16, and that second pass *did*
change the outcome — it came back `evidenced` on line 16, verified. So both
triggers have now been seen working on real input.

### How much longer it took

| | Requirements | Retries | Seconds |
|---|---|---|---|
| Before, from the brief | 21 | 0 | 58 |
| Run 1 | 23 | 3 | **79.8** |
| Run 2 | 23 | 3 | **76.6** |

**About 20 seconds more**, for three extra search-and-judge pairs. Roughly 7
seconds each, which matches the per-requirement cost of the rest of the run.

The brief's failure signal was "the retry fires everywhere and the run takes
three minutes". It did not. On the real post it fired on 3 of 23.

**But it does fire everywhere when the resume is wrong for the job.** On the
disjoint pair — the pastry chef resume against the backend post — it fired on
**6 of 6**, and the run took 28 seconds instead of about 15. Decision `0007`
predicted this and named a cap as the fix. The number for that cap should come
from a run like this one, and now there is one.

### The new counts

| | evidenced | partly | not |
|---|---|---|---|
| Brief's baseline | 6 | 13 | 2 |
| This run | **8** | **12** | **3** |

23 requirements, 22 of them required. The one optional item is requirement 22,
DataRobot familiarity, and `is_required` correctly kept it out of `blockers`.

`fit` is `worth_applying`. The sentence reads:

> Worth applying. 8 of 23 requirements are evidenced in your resume, and 2
> required items are missing.

8 + 12 + 3 = 23. **The sentence and the counts row now agree**, which is what
decision `0006` item 6 was for.

### The `undersells` false positive is gone

Report `0007` predicted that line repair would remove it, and named the exact
mechanism: requirement 2 was pointing at line 7, a wrapped fragment of a prose
paragraph, and a fragment of prose looks list-shaped.

**It is gone.** After repair, line 7 has no independent existence. Requirement
2 now points at line 85, which is a real flattened skills row.

`undersells` came back with **4 items, down from 8**, and all four point at
genuine skills rows:

| | Requirement | Line |
|---|---|---|
| 2 | Build & deploy end-to-end AI solutions | 85 — `Docker, Kubernetes, Helm, GitHub Actions, AWS ECR ...` |
| 10 | Practical Generative AI, LLMs | 79 — `LLM orchestration, DSPy and ReAct agents, RAG ...` |
| 12 | Developing and deploying applications | 83 — `FastAPI, Hatchet workflow orchestration, Elasticsearch ...` |
| 15 | Secure application development | 85 — same infrastructure row |

The prediction held.

---

## The three that matter

### Done but not asked for

**A fix to the scripted test double, and this is the finding of the brief.**

The new trigger broke `test_a_resume_with_nothing_in_common_evidences_nothing`
— the disjoint pair. A pastry chef resume started coming back
`partly_evidenced` for "Strong SQL and data modelling skills".

I did not edit the test. It asserts something the project needs to be true.

The cause: the retry searched a second time, the second query was `data
modelling skills`, and it reached a line whose entire text is the heading
`Skills`. One shared word out of four. `ScriptedModel.judge` called any
non-zero overlap partial evidence, so a section heading became evidence.

**So I ran the same disjoint pair through Groq to find out which of the two
was wrong.** All six requirements came back `not_evidenced`, after all six
retried. The real judge prompt already says not to do this — *"not_evidenced
with no line is a correct answer. Do not stretch a weak line to avoid it."*

The stand-in was the thing that was wrong, and the retry only exposed it
because nothing had ever searched a second time before.

The fix applies the project's own existing threshold, `MIN_SHARED_TERMS = 2`
from `prescreen.py`, which was measured and written down rather than picked
here: one shared word matched 26 of 26 requirements and said nothing.

The test now passes **unedited**.

A cost worth naming: the stand-in is stricter than it was, so it now returns
`not_evidenced` for a couple of requirements on the matched fixture pair that
it used to pass. It still tells the two pairs apart clearly, and the verbatim
and bookkeeping tests still have real quotes to check.

**40 new tests.** The store declining to answer, both endpoints, the one
shape across three lists, and both closed sets.

**An `audits/` line in `.gitignore`**, for the case where `AUDIT_RESUMES`
points outside `resumes/`.

### Asked for but not done

**Nothing in the brief's scope was skipped.**

Two deliberate narrowings, both flagged rather than decided:

`POST /summary` returns the stored summary and nothing else. The counts and
the requirement list are in the same file and are not returned, because
widening a contract is decision work. Both are one line here if brief `0014`
finds it needs them.

**An audit of pasted resume text is not remembered.** The key is the post plus
the resume id, and pasted text has no id. Two pastes are two documents and
nothing here can tell them apart, so it stores nothing rather than guessing.
This matters more than it sounds — see below.

### Wrong in the brief

**The `step` set in decision `0006` is missing `repair`.** The decision says
the set was read off the code. The code emits seven step kinds, not six:
`graph.extract` emits `repair` when a damaged resume line is fixed, and that
step is on screen in the demo.

I did not quietly widen the set. `events.py` has `STEPS` as the decision wrote
it and `EMITTED_STEPS` with `repair` added, so the difference stays visible.
**This needs a ruling**, and it is a one-word change either way.

**Decision `0006` does not say what `/audit/requirement` emits as its
`requirements` event** — the whole list, or just the one being re-run. I chose
just the one, since the decision says "for that one requirement". A page that
rebuilds its whole list from that event would show one row. Brief `0013` owns
that page and should be told.

**`POST /summary` cannot answer for the page's main flow.** The page pastes
resume text; the key needs an id. So the endpoint that exists to give the
panel a live headline is, today, only usable by the extension. Decision `0006`
frames it as the panel's fix and that is fine, but the page will find it
empty.

**`/audit/requirement` on a post that was never audited returns a `summary`
computed from one verdict.** It works — extraction runs and the ids come out
the same way a fresh audit's would — but the closing summary then describes a
one-requirement job post. Decision `0006` assumes a prior audit and does not
say so.

**`fit` and `fit_reason` now count different sets, on purpose.** Decision
`0006` item 6 moved the sentence's denominator to all requirements and left
`fit` alone, which is right — missing an optional extra is not evidence
against applying. But it means a resume can read *"A long shot on paper. 18 of
23 requirements are evidenced"*. It did not happen on this run. It is possible
on a post with many optional items, and it is the same class of thing item 6
was fixing.

**`evidence_weak` is still in the schema and is now asked for and ignored**,
exactly as decision `0007` says. A test pins that setting it no longer causes
a retry, so removing the field later cannot quietly change behaviour.

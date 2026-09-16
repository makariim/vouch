---
brief: 0001
date: 2026-09-15
by: working session
---

# 0001 — Evidence audit core

**The brief is not done. Status stays `open`.** The graph, the endpoint and the
checks are built and green. The one thing section 4 asks for that cannot be
produced here is the real run: there are no model credentials on this machine
and no DataRobot post or resume in the repository. Details below.

---

## Say this first

Four things conflict with what the brief assumed. None was fixed quietly.

**1. The frontend folder is `web/`, not `frontend/`.** Brief 0001 says "serve
whatever static file is in the frontend folder" without naming it. The brief
0002 session has already landed `web/index.html`, `web/styles.css`,
`web/app.js`. The server reads `web/` and was confirmed serving those three
real files over HTTP.

**2. `fixtures/trace-sample.json` is claimed by both briefs.** Brief 0001 says
save a real run there. Brief 0002 says hand-write it from decision 0004. The
briefs also say the two sessions "never touch the same files". Brief 0002 wrote
it first, 39 events. **It was not overwritten.** The recorder script defaults to
`fixtures/trace-real.json` instead, and the owner can decide where the real run
lands.

**3. Decision 0004 says "Six types". It lists five.** Its example block has six
lines, but two of them are `step` — once as a search, once as a retry. The
distinct types are `requirements`, `step`, `verdict`, `done`, `error`. Five are
implemented, matching the shapes actually shown. The contract was not edited.

**4. The two sides disagree on one optional field.** On a `not_evidenced`
verdict, brief 0002's fixture omits `line` and `line_number`; this backend sends
them as `null`, because decision 0004's example always shows both. Both read the
same from JavaScript, so the page works either way. Not changed unilaterally —
this is the round trip through decision 0004 the record asks for.

---

## What changed

Everything below is new. No existing file was modified.

| File | Why |
|---|---|
| `pyproject.toml` | Dependencies, the `audit` entry point, pytest config. |
| `.gitignore` | Keeps `__pycache__`, `.venv` and **audit output** out of a public repo. Real resumes are personal data (decision 0002). |
| `src/audit/index.py` | The resume as a *tool*: line index, keyword search, verbatim checks. Decision 0001's structural guarantee lives here. |
| `src/audit/events.py` | The decision 0004 wire shapes, constructed in exactly one place. |
| `src/audit/model.py` | The three model calls behind one `Model` protocol — the single place to audit for network access. |
| `src/audit/graph.py` | The LangGraph state graph: nodes, the retry edge, streaming. |
| `src/audit/cli.py` | Two file paths in, audit printed, JSON written. |
| `src/audit/server.py` | `POST /audit` streaming SSE, `GET /` serving `web/`. |
| `src/audit/testing.py` | Scripted model. Lets the whole graph run with no key, no network, no cost. |
| `src/audit/__init__.py` | Package exports. |
| `tests/test_index.py` | The retrieval tool, including `locate()` on a hard-wrapped post. |
| `tests/test_audit.py` | The two verbatim checks, verdict bookkeeping, empty input, the retry. |
| `tests/test_server.py` | The endpoint, SSE framing, and integration against the real `web/` files. |
| `tests/test_cli.py` | The entry point end to end. |
| `tests/data/*.txt` | A post, a matching resume, and an unrelated resume for the disjoint pair. |
| `scripts/record_trace.py` | Records one real run's events. Refuses to substitute the test double. |

## How the graph is shaped, and why

```
extract → search → judge → verify → (retry, or next requirement) → report
```

**The verbatim rule is structural in both directions.** Nothing the model types
is ever published. Extraction returns requirement text, but what is kept is the
slice `LineIndex.locate()` finds *in the post* — which also repairs a
hard-wrapped requirement that is really there but is not a literal substring. A
requirement not found at all is dropped and said so, never invented. Judging
returns a line number, but the quote emitted is read back out of the resume at
that number.

**Three verdicts is enforced by the schema, not the prompt.** `Judgement.verdict`
is a `Literal`, so it becomes an enum in the JSON schema that structured outputs
constrains the reply to. A fourth verdict cannot come back.

**The retry is an edge, not an `if`.** `verify` sets `next_action`, and a
LangGraph conditional edge routes to `search` or `advance`. When asked "where
does your agent decide anything", the answer is a node and an edge.

**Two reasons to go round again:** the quote did not check out, or the agent
itself flagged the evidence as thin and chose different search terms. Cap is
three attempts; out of attempts with an unconfirmed quote is recorded as
`not_evidenced` with no line — three verdicts, never a fourth. **That last
mapping is an interpretation of "recorded as failed", made because section 3
forbids a fourth verdict. Flagging it as a choice.**

**The loop counts requirements.** `advance` is what ends a run. The recursion
limit is a backstop against a graph bug, not the thing that stops it.

**Streaming needed no plumbing.** `events` carries an `operator.add` reducer, so
`graph.stream(stream_mode="updates")` yields exactly the new events per node.

## What was run

```
uv venv --python 3.12
uv pip install -e ".[dev]"      # langgraph 1.2.11, anthropic 1.5.0, fastapi 0.141.1
.venv/bin/python -m pytest tests/ -q
./formwork/fw check
```

A uvicorn server was started on 127.0.0.1:8777 and stopped again. **No model
call was made, and nothing left the machine.**

## The check

`formwork check` — **green.**

```
ok    config-shape       ok    kit-integrity
ok    decision-ids       ok    predictions-first
ok    doc-links          ok    role-shape
ok    generated-current  ok    standing-current
ok    guard-wired        ok    style-pointed
                         ok    rule-labels
                         ok    work-paired

GATE: green. 12 check(s), each shown to reject the wrong and accept the right.
```

The two verbatim checks section 4 asks for, written as tests:

```
.venv/bin/python -m pytest tests/ -q
38 passed, 1 warning in 0.50s
```

- `test_every_quote_is_verbatim_in_the_resume`
- `test_every_requirement_is_verbatim_in_the_post`
- `test_a_quote_that_is_not_in_the_resume_is_caught` — the verify node shown
  rejecting a bad input, not assumed to

Both verbatim tests assert on a non-empty set first, so they cannot pass by
finding nothing.

## Git status

Nothing staged, nothing committed.

```
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
?? .gitignore
?? docs/briefs/0002-audit-frontend.md
?? docs/decisions/0001-audit-is-a-state-graph.md
?? docs/decisions/0002-nothing-leaves-the-machine.md
?? docs/decisions/0003-the-audit-governs-the-tailor.md
?? docs/decisions/0004-the-api-contract.md
?? docs/reports/0002-audit-frontend.md
?? fixtures/
?? pyproject.toml
?? scripts/
?? src/
?? tests/
?? web/
```

The three modified `docs/` files and `web/`, `fixtures/`, `docs/reports/0002-*`
were already changed before this session started. This session added
`.gitignore`, `pyproject.toml`, `scripts/`, `src/`, `tests/`.

---

## Done when — item by item

| Section 4 item | State |
|---|---|
| Entry point on two paths → audit and JSON | **done** — `tests/test_cli.py` |
| Every quote verbatim in the resume, checked automatically | **done** |
| Every requirement verbatim in the post, checked automatically | **done** |
| One of three verdicts each, count equals requirement count | **done** |
| Disjoint pair → all `not_evidenced`, quotes nothing | **done** — `tests/data/resume_unrelated.txt` |
| Empty resume and empty post each fail clearly | **done** — four cases |
| Trace shows the retry at least once | **done** on scripted input; **not seen on a real model run** |
| `POST /audit` streams the event types, EventSource-readable | **done** — confirmed over a real socket |
| `fixtures/trace-sample.json` exists, holds a real run | **not done** — see below |
| Run once on the real DataRobot post and resume | **not done** — blocked |

## The real run — blocked, and why

Two things are missing and neither can be invented:

- **No model credentials.** `ANTHROPIC_API_KEY` is unset, `ANTHROPIC_AUTH_TOKEN`
  is unset, and the `ant` CLI is not installed, so there is no OAuth profile
  either.
- **No inputs.** There is no DataRobot job post and no resume anywhere in the
  repository.

So these parts of section 6 cannot be filled in and are not estimated:

- the full output of the real run — **NOT ESTABLISHED**
- the trace from that run — **NOT ESTABLISHED**
- the requirement list real extraction produces — **NOT ESTABLISHED**
- where the judging was shaky, named one by one — **NOT ESTABLISHED**

Everything on the machine side is ready. Once a key and the two text files
exist, it is two commands:

```
export ANTHROPIC_API_KEY=...            # or: ant auth login
.venv/bin/python -m audit.cli <post.txt> <resume.txt> --trace fixtures/trace-real.json
```

**What the scripted run looks like today** (`tests/data`, six requirements, one
retry forced) — shape only, the verdicts are keyword logic, not a model:

```
PART   1. 5+ years of professional Python experience
         resume line 10: Wrote Python services continuously since 2019.
YES    2. Strong SQL and data modelling skills
         resume line 8: Designed the SQL schema and data modelling for the ledger service.
PART   3. Experience building and operating REST APIs
         resume line 7: Built and operated REST APIs in Python serving 2M requests a day.
NO     4. Hands-on Kubernetes in production
NO     5. Experience with Apache Kafka or similar streaming systems
PART   6. Comfortable mentoring junior engineers
         resume line 9: Ran weekly mentoring sessions for two junior engineers.

evidenced 1   partly 3   not evidenced 2
```

The retry, as it appears in the trace and on the wire:

```
[4] search   hands kubernetes production
[4] judge    partly_evidenced -- scripted weak evidence
[4] verify   no quote to check
[4] retry    evidence looks weak, trying different terms
[4] search   kubernetes production (attempt 2)
[4] judge    not_evidenced -- nothing in the resume covers this
[4] VERDICT  not_evidenced
```

## How long it took

**Exact wall clock: NOT ESTABLISHED** — not measured.

What matters for decision 0001's fallback: **the graph runs end to end now**, in
one session, streaming over HTTP into the real page. The Pydantic AI fallback is
not triggered. The remaining risk is not LangGraph — it is that the model's
verdicts have never been read by a human.

## What turned out to be the wrong shape

- **"Serve whatever is in the frontend folder"** needed a name. It is `web/`.
- **`fixtures/trace-sample.json` was double-booked.** The briefs' no-collision
  promise does not hold for that one path.
- **Section 3 forbids a fourth verdict; section 2 says an exhausted requirement
  is "recorded as failed".** Those two need reconciling. Read here as
  `not_evidenced` with no line and a `failed` step in the trace.
- **`judge` has no step type in the fixture.** This backend emits a `judge` step;
  brief 0002's page renders any step name generically, so it displays, just
  unstyled. Harmless, worth knowing.
- **A `dropped` requirement is invisible on the page.** It is emitted with
  `requirement_id: 0`, and the page ignores steps for requirements it never saw.

## The three that matter

**Done but not asked for:**

- `.gitignore` — the repo is public and audit output contains a real resume.
  Decision 0002 makes that a leak, so it is excluded before it can be committed.
- `src/audit/testing.py` and `scripts/record_trace.py` — not named in the brief.
  The first is the only way to prove the verify node rejects a bad quote without
  a key; the second makes the blocked real run a single command.
- `tests/test_server.py` integration tests against the real `web/` files —
  outside the letter of the brief, but the two sessions join there and nobody
  else was going to check it.

**Asked for but not done:**

- **The real DataRobot run**, and the four section 6 items that depend on it.
  Blocked on credentials and on the two input files. Not estimated.
- **`fixtures/trace-sample.json` holding a real run.** Blocked by the same thing,
  and the path is owned by brief 0002. Not overwritten.

**Wrong in the brief:** the five points under "Say this first" and the five under
"What turned out to be the wrong shape".

## What this session did not touch

No HTML, CSS or frontend JavaScript. No Langfuse. No tailoring. No PDF or URL
parsing. No scoring or percentage. No storage or cache. `web/` was read only.
Nothing was written to version control.

---

## Closed 2026-09-15

The one outstanding item — the real DataRobot run — was completed under brief
`0003`. See `docs/reports/0003-groq-and-the-first-real-run.md`. Nothing else in
this brief was left open.

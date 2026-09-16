---
status: done
date: 2026-09-15
---

# 0001 — Evidence audit core

> **Revised 2026-09-15.** The first version was one model call returning JSON —
> extraction, not an agent. This version is the graph in decision `0001`, plus
> the endpoint in decision `0004`.
>
> **This runs at the same time as brief 0002, the frontend.** The two never
> touch the same files. They meet only at the contract in decision `0004`, and
> neither session may change that contract alone.

## 1. Goal

Take a job post as text and a resume as text. Pull out the discrete requirements
the post is asking for. For each one, say whether the resume evidences it,
partly evidences it, or does not, and quote the exact resume line that supports
it when there is one.

Build it as a **LangGraph state graph** that emits a step-by-step trace, because
that trace is the demo and a later frontend will render it.

**If we do not do this at all:** there is no product. Everything else in the
project reads this step's output.

## 2. Scope

**The graph.** Nodes, and the edges between them:

```
extract → search → judge → verify → (retry, or next requirement) → report
```

- **extract** — post text in, a list of discrete requirements out. Each keeps
  its text **verbatim from the post**. Runs once.
- **search** — a **tool**, not an argument. Index the resume by line. The node
  queries it for the current requirement and gets back real lines with line
  numbers. **Do not put the whole resume in the prompt.**
- **judge** — requirement plus retrieved lines in. One of `evidenced`,
  `partly_evidenced`, `not_evidenced`, the supporting line, and one sentence of
  reason.
- **verify** — is that quoted line actually in the resume, character for
  character? On a mismatch the requirement goes back to **search**, at most
  three attempts, then it is recorded as failed rather than retried for ever.
- **the agent decides how hard to look.** When retrieved evidence is weak,
  search again with different terms. The model chooses the terms and chooses
  when to stop. This is the decision nobody told it to make, and it must appear
  in the trace.

**The loop counts requirements, not model turns.** Twelve requirements is twelve
passes. Nothing may end the run early.

**The trace.** Every node emits a named event: which step, which requirement,
what it decided. Stream it. A later brief renders it; this one only has to emit
it in a shape a frontend can consume.

**The entry point.** Two file paths in, the audit printed, the JSON written.

**The HTTP layer.** Exactly what decision `0004` specifies, and nothing more:

- `POST /audit` takes `{"post": "...", "resume": "..."}` and streams
  server-sent events.
- Every event is one JSON object with a `type`. Six types, listed in `0004`.
- `GET /` serves whatever static file is in the frontend folder. **Serve it,
  do not write it.** Brief 0002 owns that file.
- **Save one real run's events to `fixtures/trace-sample.json`** as soon as the
  stream works. The frontend session is waiting on it.

**Out of scope — do not touch, do not add:**

- **any HTML, CSS or frontend JavaScript.** Brief 0002 owns those, in another
  session, right now. Touching them causes a collision.
- Langfuse, or any observability wiring — its own brief, after this one works
- tailoring, rewriting, drafting, cover letters
- PDF, DOCX or HTML parsing; reading a job post from a URL
- scoring, percentages, an overall match number
- storing resumes, caching runs, any database
- multiple languages

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything — stop
and report, no changing a check because it failed, and where something cannot be
established, say so rather than estimating.

Specific to this work:

- **A supporting line that is not in the resume.** Every quote must be present
  character for character. The retrieval tool is what makes this structural; the
  verify node is what proves it.
- **A requirement that is not in the post.** Same rule, other direction.
- **A fourth verdict.** Three, always. `not_evidenced` with no line is a correct
  answer, not a failure.
- **Any network call other than the model call.** Decision `0002`.
- **Changing the contract in decision `0004` alone.** The frontend is being
  built against it at this moment. A mismatch is reported, not fixed quietly.
- **Ending the run before every requirement has a verdict.**
- **Writing the resume or post anywhere on disk** other than where they already
  are.

## 4. Done when

- The entry point runs on two text file paths and produces an audit and JSON.
- **Every quoted supporting line is a verbatim substring of the resume file.**
  Automated check, not an eyeball. Write it.
- **Every extracted requirement is a verbatim substring of the post file.** Same.
- Every requirement carries exactly one of the three verdicts, and the count of
  verdicts equals the count of requirements.
- A resume with nothing in common with the post returns all `not_evidenced` and
  quotes nothing. Build that pair as a test input.
- An empty resume, and an empty post, each fail with a clear message rather than
  returning an empty audit that looks like a real result.
- **The trace shows the retry happening at least once** on a real input. If it
  never fires, the decision the agent makes is not demonstrable and the agent
  claim is weak.
- **`POST /audit` streams the five event types from decision `0004`**, as
  `data:` frames. **Not `EventSource`** — it is GET only and cannot send a body,
  so the contract rules it out. The page uses `fetch()` and reads the body as a
  stream. This line was wrong in the original brief.
- **`fixtures/trace-real.json` exists** and holds a real run's events.
  `fixtures/trace-sample.json` is brief 0002's hand-written fixture and stays.
- It has been run once on the **real DataRobot job post** and the real resume,
  and the whole output is in the report.

**What would tell us it failed:** the human reads that run and disagrees with
the verdicts; or extraction invents requirements, merges two, or drops one that
is plainly in the post; or the trace is too sparse to show in a demo.

**How many disagreements is too many is NOT ESTABLISHED.** No bar has been set
and guessing one here would be inventing evidence. Record the run so a bar can
be set from it.

## 5. Checked by

`formwork check` as a whole, plus the two verbatim checks in section 4.

The gate cannot tell whether a verdict is *right*. It can only tell whether the
quoted text is real. The real evidence is the one hand-read run, which is why
section 6 asks for it in full.

## 6. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- the full output of the real DataRobot run, not a summary
- the trace from that run, so the steps can be judged as a demo
- the requirement list extraction produced, so splitting can be judged apart
  from judging
- **where the judging was shaky** — requirements where the call between
  `partly_evidenced` and a neighbour was close, named one by one
- **how long it took**, because decision `0001` names a fallback to Pydantic AI
  if the graph is not running end to end by the end of day one
- anything in section 2 that turned out to be the wrong shape once built

---
status: done
date: 2026-09-15
---

# 0005 — The presentation

## 1. Goal

Fifteen minutes with a live demo, for the DataRobot Professional Services
interview. **This is the last piece of work. Nothing else gets built.**

The application is done and has been run three times on the real post. What is
missing is the half of the deliverable that is not code — and it is the half
carrying four of the five scoring criteria: problem-solving acumen, strategic
vision, technical credibility, creativity and passion.

**If we do not do this:** there is a working application and no submission.

## 2. Scope

**Produce two things:**

- **the slides** — few, plain, readable from the back of a room
- **a demo script** — the exact clicks, in order, with what to say over each step

**The shape, and the time it gets:**

| Part | Minutes |
|---|---|
| The problem, and why the obvious build is wrong | 2 |
| **The live demo** | 5 |
| How it works — the graph, the tool, the verify step | 4 |
| What it got wrong, and what I would do next | 3 |
| Questions | rest |

**The demo path, exactly:**

1. Server already running, page already open, both boxes already filled. **Do
   not paste 90 lines of text in front of people.**
2. Press Audit. Talk over the first few requirements as they stream.
3. Land on **requirement 12** — FastAPI, found on line 77. That is the one that
   was wrong before BM25 and is right now.
4. Land on **requirement 18 or 20** — a clean `not evidenced` with no quote.
   That is the product refusing to invent something.
5. Let it finish. Show the three counts.

**The argument to make, in this order:**

- the obvious build is one model call over post plus resume — and you cannot
  tell whether the resume said it or the model wanted it to
- so the resume is a **tool**, not a prompt argument
- the model returns a **line number**, never text. The quote is read back out of
  the file
- **a fabricated quote is therefore impossible**, not unlikely
- `verify` always runs, and is not the model's decision
- the loop counts requirements, so nothing can stop early

**Out of scope — do not build, do not start:**

- any code change. The application is finished
- the tailor, Langfuse, the browser extension. They are slides, not features
- a new frontend, styling, animation
- rehearsing away the findings in section 3. They are the strongest material

## 3. The honest part, and it is the strongest part

**Do not present this as having worked first time.** Four findings, and each one
scores better than a claim of success:

- **The retry has never fired. 0 of 21, three runs running.** The loop is real —
  a conditional edge in the graph — and it depends on the model flagging its own
  evidence as weak. It never did, not once, even when it was wrong. **The fix is
  to stop trusting a model's self-report and trigger on something observable.**
  That is the best sentence in the talk.
- **Retrieval used to rank by word count, so `python` outranked `fastapi`.** It
  reported a gap that was not a gap. BM25 fixed it, and `rank_bm25` is a library,
  **not your code — say so.**
- **About 60% land on `partly evidenced`.** The middle verdict absorbs both ends.
  Known, not solved.
- **Extraction is not deterministic.** The same post gave 21, then 23, then 21
  requirements. **Do not put a requirement count on a slide.**

## 4. Must not happen

- **Do not claim authorship of `rank_bm25`** or of any library.
- **Do not promise a number** of requirements or verdicts before the run.
- **Do not paste the resume live.** Have it loaded already.
- **Do not demo from `file://`.** The page must be served or it silently fails.
- **Do not show the fixture as if it were a live run.** If fixture mode is used
  as a fallback, say that is what it is.
- Do not claim production readiness. They said they do not expect it.

## 5. Done when

- The slides exist and have been read aloud once, against a clock, in under
  fifteen minutes.
- **The demo has been run start to finish at least twice**, on the real post,
  without stopping. Once is not a rehearsal.
- **The fallback has been tested**: model slow or down, switch to fixture mode,
  keep talking. This is the thing that saves the session.
- The two-metre test has been done by a human.

**What would tell us it failed:** the demo needs narrating to be followed, or a
question about how it works cannot be answered by pointing at a node.

## 6. Checked by

`formwork check` for the repository.

**Nothing can check a presentation.** The evidence is a rehearsal against a
clock, which is why section 5 asks for two full runs rather than a read-through.

## 7. The report must contain

- where the slides and the script are
- **how long the rehearsal actually took**, measured, not estimated
- what was cut to fit fifteen minutes
- which questions could not be answered while rehearsing — those are the ones to
  prepare, and they are worth more than the slides

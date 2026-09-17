---
status: draft
date: 2026-09-17
brief: 0024-the-vision-and-the-tools
---

# Slides — Vouch

Fifteen minutes, DataRobot Professional Services.

**How to use this file.** One `---` block is one slide. Nothing on a slide is
read out; the words to say are in
[`demo-script.md`](demo-script.md). If a line here cannot be read from
the back of the room, it is too long — cut it, do not shrink it.

**Two rules that override everything below.**

- No requirement count and no verdict count appears on any slide. Extraction is
  not deterministic: the same post gave 21, then 23, then 21. Numbers on slides
  are only for runs that already happened, and they are labelled with the date.
- `rank_bm25` is a library. So are LangGraph, FastAPI and Groq. Say "library"
  out loud every time one is on screen.

**The shape and the clock.**

| Part | Slides | Minutes |
|---|---|---|
| The problem, and why the obvious build is wrong | 1–3 | 1 |
| The live demo | 4 | 5 |
| How it works | 5–9 | 2½ |
| Why these libraries | 10 | ½ |
| What it got wrong | 11–13 | 1½ |
| What I learned | 14 | ½ |
| How it was built | 15 | 1½ |
| Where this goes | 16–17 | 2 |

**Fourteen and a half minutes. Questions are after the fifteen, not inside it.**

If the panel wants questions inside the fifteen there is half a minute, which is
nothing. In that case cut slide 10 — its argument becomes one spoken sentence
over slide 8 — and fold slide 14 into slide 16. That buys a minute and a half.

**Do not buy time from the demo, and do not buy it from slides 11 to 13.** The
honesty is why the last two slides are believable.

**This clock is a budget, not a measurement.** Nothing here has been spoken
against a stopwatch. That is still item 1 of `docs/standing.md`.

---

## Slide 1

# Checking a resume against a job post

Every requirement. One line of evidence. Or nothing.

> Muhammad Abdulkariim · DataRobot Professional Services

---

## Slide 2 — The problem

A job post asks for twenty-odd things.

A person reads it once and guesses.

# The guess is the product.

Not the writing — the checking.

I built this because I am job hunting. **The demo runs on your job post.**

---

## Slide 3 — Why the obvious build is wrong

The obvious build: one model call, over the post and the resume together.

Then it says "yes, strong match on Kubernetes".

# And you cannot tell whether the resume said it or the model wanted it to.

That is the whole problem. Everything else here is a consequence.

---

## Slide 4

# DEMO

(blank slide, or the app itself)

Five minutes, in two parts: **the extension on a real job post, 45 seconds**,
then the page for the rest. The clicks are in `demo-script.md`.

**Nothing is read from this slide.**

---

## Slide 5 — The resume is a tool, not a prompt argument

# The resume is never pasted into the prompt.

It is indexed by line number, and the agent **searches** it.

So the model sees six lines it asked for, not a document it can drift over.

---

## Slide 6 — The model returns a number, never text

The judge returns a **line number** and a verdict.

The quote you see is read back out of the file at that number.

# A fabricated quote is therefore impossible.

Not unlikely. Impossible.

---

## Slide 7 — How the file is cut into lines decides the answer

Slide 6 says the quote has to be a real line. So the line breaks are not a
detail — they are the answer. Two readers, same PDF: file order, versus
position on the page.

| 16 September | lines | evidenced | partly | the call |
|---|---|---|---|---|
| `pypdf` | 160 | 3 | 17 | **weak** |
| `pdfplumber` | **51** | **6** | **13** | **worth applying** |

> Same resume, same post, same model. Runs minutes apart.

# The verdict changed and nothing about the model did.

---

## Slide 8 — The graph

```
extract → search → judge → verify ─┬→ (retry) → search
                                   └→ advance → next requirement
                                                      ↓
                                                    report
```

# `verify` always runs.

It is not the model's decision.

The retry is a **conditional edge**, not an `if` inside a node. That is why I
can point at where the agent decides anything.

---

## Slide 9 — Why this is an agent

# Not because it calls a model.

Three reasons, and each one is on slide 8.

**It has tools and picks how to use them.** It writes its own search terms, per
requirement.

**It takes several steps with state between them.** The loop counts
requirements, not model turns — so nothing stops early and nothing decides it
has done enough.

**It goes back on its own.** Up to three searches, and it chooses when a first
look found nothing.

---

## Slide 10 — Why these libraries, and not the other four

# LangGraph.

Over LangChain, CrewAI, Pydantic AI and LlamaIndex — and over
DSPy ReAct, which I know best and which is not on their list anyway.

Because the audit is a **cyclic graph with a real decision in it**, and a
framework that hides control flow cannot show you where.

Because **the trace is the demo** — LangGraph streams state node by node.

The rest is libraries too: FastAPI, `rank_bm25`, Groq. **None of it is my code.**

> Written down before I built it: `docs/decisions/0001`.

---

## Slide 11 — What it got wrong: the trigger nobody could check

The retry used to fire on the model reporting its own evidence as weak.

**It fired zero times. 0 of 21, 0 of 23, 0 of 21** — including on verdicts that
were wrong, where the model's own written reason said "does not mention".

# A self-report nobody can check is not a trigger.

---

## Slide 12 — The fix, and the number it moved

It now triggers on something observable: a first pass that **found nothing**,
and a quote that **failed verification**.

# It fired three times. Nobody pressed anything.

> Same post, 15 September.

One of those flipped an answer from not-evidenced to evidenced, on a verified
line.

**And no second pass talked itself into a match.** Three stayed negative.

---

## Slide 13 — Three more things that are wrong

**Retrieval used to rank by word count.** So `python` outranked `fastapi`, and
it reported a gap that was not a gap. Fixed with BM25 — `rank_bm25`, **a
library, not my code**.

**About 60% land in the middle verdict.** "Partly evidenced" absorbs both ends.
Known, not solved.

**Nothing budgets retries across a run.** Three searches per requirement is
capped. How many requirements retry is not. One resume retried on 6 of 6.

# All three were found by running it, not by reading it.

---

## Slide 14 — What I learned

Almost everything that looked like a model problem was a **data problem**.

How the PDF was read moved the verdict from weak to worth applying — slide 7.
Retrieval closed a gap that was not a gap. Repaired line breaks removed a false
finding.

# The model never changed. Not once.

That is the thing I would carry into a customer deployment.

---

## Slide 15 — How it was built

# I built this by directing agents.

> `FORMWORK.md`, at the root.

Every piece was **briefed before it started** and **reported when it finished** —
including what the brief got wrong. The guardrails refuse rather than advise: a
turn cannot end on a red check.

**What it caught.** 18 of 22 reports name something the brief got wrong. The
planning role offered to start building four times — **I** caught that, not the
kit.

I briefed it, I read every report, I rejected work. **`docs/` is the handover
artifact**: 24 briefs, 8 decisions, 23 reports.

---

## Slide 16 — What this actually is

# Not a resume tool.

**It audits a document against a rulebook and returns a
per-item verdict with cited evidence — and refuses to cite what is not there.**

A job post is a rulebook. So is a policy, a tender, a regulation.

Every pilot dies on one sentence: *"how do I know it didn't make that up?"*
Prompting answers it with a probability. **This answers it with architecture:
the model has no channel to emit text.**

I have shipped this shape before — a bilingual compliance engine auditing
documents against an uploaded rulebook, for regulated customers.

---

## Slide 17 — Scaling it, honestly

**Parallel by construction.** One document, one graph run, nothing shared.

**The two speeds are the business case.** A free local screen decides whether a
paid call is worth making. At a customer's ten thousand documents, that is the
whole argument for productizing it.

**What it would need, and has none of yet:** an evaluation set with gold
answers. Measured token usage. Durable orchestration. A human review gate.
Per-tenant isolation.

Vouch refuses to claim what it cannot evidence. The method refuses to let a turn
end on a red gate.

# Make the guarantee structural, not a promise.

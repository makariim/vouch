---
status: draft
date: 2026-09-16
brief: 0005-the-presentation
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
| The problem, and why the obvious build is wrong | 1–3 | 2 |
| The live demo | 4 | 5 |
| How it works | 5–8 | 4 |
| What it got wrong, and what is next | 9–12 | 3 |
| Questions | 13 | rest |

---

## Slide 1 — Title

# Checking a resume against a job post

Every requirement. One line of evidence. Or nothing.

Muhammad Elsherif · DataRobot Professional Services

---

## Slide 2 — The problem

A job post asks for twenty-odd things.

A person reads it once and guesses.

**The guess is the product.** Not the writing — the checking.

---

## Slide 3 — Why the obvious build is wrong

The obvious build: one model call, over the post and the resume together.

Then it says "yes, strong match on Kubernetes".

**And you cannot tell whether the resume said it or the model wanted it to.**

That is the whole problem. Everything else here is a consequence.

---

## Slide 4 — DEMO

(blank slide, or the app itself)

Five minutes. The clicks are in `demo-script.md`.

**Nothing is read from this slide.**

---

## Slide 5 — The resume is a tool, not a prompt argument

The resume is never pasted into the prompt.

It is indexed by line number, and the agent **searches** it.

So the model sees six lines it asked for, not a document it can drift over.

---

## Slide 6 — The model returns a number, never text

The judge returns a **line number** and a verdict.

The quote you see is read back out of the file at that number.

**A fabricated quote is therefore impossible.** Not unlikely. Impossible.

---

## Slide 7 — The graph

```
extract → search → judge → verify ─┬→ (retry) → search
                                   └→ advance → next requirement
                                                      ↓
                                                    report
```

`verify` **always runs**. It is not the model's decision.

The retry is a **conditional edge**, not an `if` inside a node. That is why I
can point at where the agent decides anything.

---

## Slide 8 — The loop counts requirements

The loop is over the requirement list, not over model turns.

Nothing can stop early, and nothing can decide it has done enough.

Three searches per requirement, then it records what it has and moves on.

---

## Slide 9 — What it got wrong: the trigger nobody could check

The retry used to fire on the model reporting its own evidence as weak.

**It fired zero times. 0 of 21, 0 of 23, 0 of 21** — including on verdicts that
were wrong, where the model's own written reason said "does not mention".

**A self-report nobody can check is not a trigger.**

---

## Slide 10 — The fix, and the number it moved

It now triggers on something observable: a first pass that **found nothing**,
and a quote that **failed verification**.

Same post, 15 September: it fired **three times**, nobody pressing anything.

One of those flipped an answer from not-evidenced to evidenced, on a verified
line.

**And no second pass talked itself into a match.** Three stayed negative.

---

## Slide 11 — Two more things that are wrong

**Retrieval used to rank by word count.** So `python` outranked `fastapi`, and
it reported a gap that was not a gap. Fixed with BM25 — `rank_bm25`, **a
library, not my code**.

**About 60% land in the middle verdict.** "Partly evidenced" absorbs both ends.
Known. Not solved.

---

## Slide 12 — What I would do next

**Cap the retries.** A resume in the wrong field retried on 6 of 6. A real cap
needs a number from a real run, and now there is one.

**Split the middle verdict.** It is doing two jobs.

**Record token usage.** Cost is currently NOT ESTABLISHED, and I will not
estimate it at you.

---

## Slide 13 — Questions

**Not production ready, and not pretending to be.**

The guarantee is narrow and it holds: the quote is the file's, not the model's.

Thank you.

---
status: open
date: 2026-09-16
---

# 0010 — Hand Vouch over to someone who has never seen it

> **Run this in a fresh session.** It builds nothing and touches no file.

## 1. Goal

**Treat the person you are talking to as brand new.** They have never seen
Vouch, never read a line of it, and know nothing about how it was built. They
are taking it over.

**By the end they must be able to stand in front of anyone — present it, and
defend it under questions.** Not read notes. Talk.

Assume nothing. If something was obvious to whoever built it, say it anyway.

## 2. How this session runs

**One small step, then stop and wait.** Do not start the next step until they
say so.

Three words, and **repeat them at the end of every step** so they never have to
remember:

| They say | You do |
|---|---|
| **next** | go on to the next step |
| **deeper** | more detail on that same step, then stop again |
| **again** | say the same thing differently, simpler |

**Start shallow every time.** The first version of a step is the short one.
Detail only when asked. Finishing every step lightly beats stopping halfway
because one went deep.

**There is no clock.** Do not rush them and do not say how long anything takes.

## 3. How to write

**They read English as a second language.**

- Short sentences. One idea each.
- Common words. If a word has a simpler twin, use the twin.
- **No new word without explaining it in the same breath.** Never drop
  "reducer", "conditional edge" or "index" on them bare.
- Blank line between blocks. Give it room.

**Show the real thing. Do not describe it.** Real requirement, real resume line,
the real words the model chose. Real text explains itself; a sentence about it
does not.

Code snippets: **five lines maximum**, only where they help. Many steps need
none.

## 4. What they bring with them

A software engineer who moved into AI about a year ago. Works daily in **DSPy
and Hatchet**. **Has never used LangGraph.**

- A LangGraph node is like a Hatchet step, and the state is like the workflow
  context. Say what is **different**, not what it is.
- Do not explain what an agent, a tool call or an API is.
- **One trap:** `dspy.ReAct` is an agent too, so "you need an agent framework"
  sounds to them like "you already have one". The real difference is **who
  chooses what happens next.** In ReAct the model chooses. Here a person chose,
  and the model only answers small questions inside each step.

## 5. The steps, in order

Use the real run in `audit.json`. Pick **one** requirement early and follow that
same one throughout. Never switch examples.

**Part A — the product.** They should be able to present this part on its own.

| | Step | What they can say afterwards |
|---|---|---|
| 1 | The problem, and who has it | a job post asks for twenty-odd things; a person reads it once and guesses |
| 2 | What Vouch does | three answers per requirement, and the resume line that proves it — or nothing at all |
| 3 | **Why one big model call does not work** | you cannot tell whether the resume said it or the model wanted it to. **This is the argument the whole product rests on** |
| 4 | The two ways in | the **page**, where you paste the post and upload your PDF resume; the **extension**, where you paste nothing |
| 5 | **Why the extension is not a scraper** | the page is already open and you are already signed in. Nothing is fetched. There is nothing to get past |
| 6 | What is on screen at the end | the call, what is missing, what proves you fit, and **which lines of your resume undersell you** |
| 7 | The two speeds | an instant word match that is free and local; the full audit that costs money and takes about ninety seconds |

**Part B — how it works.**

| | Step | What they can say afterwards |
|---|---|---|
| 8 | The shape | six steps: extract, search, judge, verify, advance, report |
| 9 | **extract** | the model proposes a requirement; we keep the post's own words, and drop anything we cannot find in the post |
| 10 | **search** | the resume is never in the prompt. The model picks search words; we do the looking and hand back six lines |
| 11 | **judge** | the one step where the model's opinion is the product |
| 12 | **verify** | the model returns a line **number**. The text on screen is read out of the file. **A made-up quote is impossible, not unlikely** |
| 13 | advance and report | the loop counts requirements, so nothing can stop early |
| 14 | **Where it decides for itself** | when the first look finds nothing, it looks again with different words — and that choice is a branch in the graph you can point at |

**Part C — the honest part. Do not skip it.**

| | Step | What they can say afterwards |
|---|---|---|
| 15 | What is wrong with it today | the self-report that never fired, the middle verdict doing two jobs, extraction not being deterministic |
| 16 | What we chose not to build, and why | `docs/future.md` — eight things, each with the reason |

**Part D — taking it over.**

| | Step | What they can say afterwards |
|---|---|---|
| 17 | Where everything lives | `src/` the audit, `web/` the page, `extension/`, `design/`, and **`docs/decisions/` for why anything is the way it is** |

**Steps 3, 12 and 14 are the three that matter most.** If they tire, those are
the three to protect.

## 6. Then make them present it

When the steps are done, say this:

> Now present it back to me. Two minutes, as if I am the panel and I have never
> heard of it. I will not help.

**Let them finish without interrupting.** Then say what was missing, once.

## 7. Then three questions, cold

No looking back.

1. **Why can this tool not make up a quote?**
2. **Where does it decide something nobody told it to decide?**
3. **What is wrong with it today?**

For question 3, this is the answer:

> I asked the model to tell me when its evidence was weak. It never did — not
> once in three runs, even when it was wrong. So I stopped trusting what it said
> about itself, and made it look again whenever the first look found nothing.
> Then it fired three times on the real post.

If an answer is thin, say what was missing in two lines. **Do not teach it
again.** Write it down for the report.

## 8. Must not happen

- **Do not write or edit any file.**
- **Do not run two steps together.** One step, then stop. Every time.
- **Do not assume they know anything.** They are new.
- **Do not go deep unless asked.**
- **Do not use a word they have not met without explaining it.**
- **Do not tell them it is all fine.** Step 15 exists for the opposite reason.

## 9. Done when

- All seventeen steps covered, or they stop and you say where you got to.
- **They presented it back in two minutes, unaided.**
- **They answered the three questions in their own words.**

**What would tell us it failed:** they can repeat the sentences but cannot
answer a question asked in different words.

## 10. The report must contain

Three things, short.

- which steps were covered, and where it stopped
- **what they could not explain back**, named step by step. **This is the most
  valuable thing in the report** — it is what they revise from
- anything in the code that could not be explained in plain words. If a piece
  cannot be defended out loud, that is a finding about the code, not about them

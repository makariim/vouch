---
status: open
date: 2026-09-17
---

# 0022 — Revise the presentation

> **You own `docs/presentation/` and this brief's own report.** Nothing else.
>
> **This is a revision, not a rewrite.** The deck is good. Slide 6 is the best
> thing in it and slides 9 and 10 turn the weakest finding into the strongest
> two minutes. Keep the voice, keep the shape, keep the clock.

## 1. Goal

The deck was written before three things happened, and it does not know about
any of them. One of them is the strongest argument the project has.

**If we do not do this:** the presentation is honest about a product that has
since changed, and the best result goes unsaid.

## 2. What is missing or wrong

### The extension appears zero times

Checked: the word does not occur in either file.

It is the thing nobody else has — *"it audits the job post you are already
looking at, and it is not a scraper because the page is already open and you are
already signed in."* That answers creativity and strategic vision, neither of
which is code.

**Put it first in the demo, forty-five seconds**, and only the **instant word
match**. Milliseconds, no model call, no network — the one thing in the whole
product that cannot hang and cannot be slow.

> "This is a real job post, right now. That number took milliseconds and cost
> nothing. It has not read anything yet."

Then click through to the page and the script continues exactly as written.

**If Brave misbehaves you have lost forty-five seconds.** That is the whole risk,
and it is why this goes first and stays small.

Two facts the script must carry, because they will happen live:

- **Demo it in Brave.** Work Chrome blocks unpacked extensions by corporate
  policy and always will.
- **On LinkedIn, click "… more" before running.** Collapsed, the post reads 13
  requirements; expanded, 25. Measured.

### The reading-order result is not in the deck

The strongest number this project produced, and it is nowhere:

| | indexed lines | evidenced | partly | the call |
|---|---|---|---|---|
| before | 160 | 3 | 17 | **weak** |
| after | **51** | **6** | **13** | **worth applying** |

Same resume, same post, same model, both runs minutes apart.

**The verdict changed and nothing about the model did.** Only how the file was
read — `pdfplumber` orders text by where it sits on the page; `pypdf` returns it
in the order the file was written.

**This belongs beside slide 6**, because slide 6 already says the quote must be
a real line — and this is what follows from that: if the quote must be a real
line, how the file is cut into lines decides the answer.

Give it a slide or fold it into 6. **Your call, and say which and why.**

### Cost is no longer NOT ESTABLISHED

Slide 12 says *"Cost is currently NOT ESTABLISHED, and I will not estimate it at
you."*

It is established now: **47 model calls, about 17,000 tokens — 12,500 in, 4,100
out — and under half a cent a run** on `openai/gpt-oss-120b` at Groq's
$0.15/$0.60 per million. About nine cents for twenty posts.

**Still say what it is.** It is a calculation from token counts and a price
list, not a metered bill — nothing in the code records usage, and recording it
is a one-line change that has not been made. Say the number and say that.

### The name on slide 1

It says **Muhammad Elsherif**. The resume says **Muhammad Abdulkariim**.

Make them match. It is a title slide next to a document they will read.

## 3. What must not change

- **The shape and the clock.** Five minutes of demo, and the running order.
- **Slide 6.** Do not touch it.
- **Slides 9 and 10.** The self-report that never fired, and the fix. That arc
  is the best answer in the deck.
- **"When it breaks."** Every row of it stays.
- **The four things that must not happen** — no library claimed as your own, no
  count promised, nothing pasted live, never `file://`.

## 4. Must not happen

- **Do not touch any file outside `docs/presentation/`**, except this brief's
  own report.
- **Do not add a slide without removing time from somewhere.** Fifteen minutes
  is fifteen minutes, and the demo keeps its five.
- **Do not put a requirement count or a verdict count on a slide.** Extraction
  is a model call: 23, then 21, then 22 on the same post. A number tied to a
  dated run, labelled, is fine.
- **Do not claim the extension is finished.** It has never been walked across
  five job posts, and on one company's careers page it read four lines of a long
  post and reported a number anyway. That is item 9 in `docs/future.md`.

## 5. Done when

- The extension is in the demo script, first, at forty-five seconds, with Brave
  and the "… more" click both written down.
- The reading-order result is in the deck, beside or inside slide 6.
- Slide 12 carries the real cost and says what kind of number it is.
- The name matches the resume.
- **Read aloud against a clock, it still fits fifteen minutes.** Say what it
  timed at.

**What would tell us it failed:** it runs long, or the demo grew a second risky
step.

## 6. Checked by

`formwork check`.

Nothing can check a presentation. The evidence is the timing in section 7.

## 7. The report must contain

Short.

- **what it timed at**, read aloud against a clock. Not estimated
- what was cut to make room
- where the reading-order result went, and why there
- anything else in the deck that is no longer true

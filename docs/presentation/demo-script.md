---
status: draft
date: 2026-09-17
brief: 0024-the-vision-and-the-tools
---

# Demo script

Five minutes of the fifteen, in two parts: **the extension, 45 seconds**, then
the page for the rest. Every click, in order, with the words to say over it. The
slides are [`slides.md`](slides.md).

**The extension goes first because it is the part that cannot be slow.** It is a
word match — no model call, no network. If it misbehaves you have lost 45
seconds and the page demo is untouched. That is why it is first and why it stays
small.

**Read the last section, "When it breaks", before the first rehearsal.** It is
the part that saves the session.

---

## Before anybody is in the room

Do all of this. None of it happens on stage.

| | |
|---|---|
| 1 | `GROQ_API_KEY` is exported in the shell you are about to use |
| 2 | `uv run uvicorn audit.server:app --port 8000`, and leave it running |
| 3 | Open **`http://127.0.0.1:8000`**. Never `file://` — the page silently fails |
| 4 | Set the mode radio to **"A real run"**. It defaults to "A recording" |
| 5 | Paste the resume into **Your resume**. Now, not on stage |
| 6 | Paste the whole DataRobot post into **The job post**. Gaps included |
| 7 | Scroll both boxes back to the top so the page looks untouched |
| 8 | Browser zoom up until the verdict lines read from two metres |
| 9 | Notifications off. One window. No terminal on screen |

**The extension, in Brave.** Work Chrome blocks unpacked extensions by corporate
policy and always will, so this half of the demo is Brave and only Brave.

| | |
|---|---|
| 10 | Load `extension/` unpacked in **Brave**, and pin Vouch to the toolbar |
| 11 | Open a **real job post** in a second Brave tab. LinkedIn is the safe one |
| 12 | On LinkedIn, click **"… more"** to expand the post. Collapsed it reads 13 requirements; expanded, 25. Measured |
| 13 | Click the Vouch mark once now, check the panel answers, then close it |

**A second browser tab, already open, on `http://127.0.0.1:8000/?fixture=summary`.**
That is the fallback. Do not open it now — just have the tab there.

---

## Part one — the extension, 45 seconds

**In Brave, on the real job post tab. The clock is 45 seconds. Do not overrun
it.**

### 1. Click the Vouch mark in the toolbar

The panel opens and the word match is already done. Nothing was pressed to start
it.

> "This is a real job post, right now, on the page I was already reading."

### 2. Point at the number in the panel

> "That number took milliseconds and cost nothing. It has not read anything
> yet."

**Do not say the number before it is on screen**, and do not promise it will be
the same on another post. Same rule as the page.

### 3. Say why it is not a scraper

This is the sentence the whole 45 seconds exists for:

> "It audits the job post I am already looking at. It is not a scraper — the
> page is already open and I am already signed in. Nothing fetches anything."

### 4. Say what it is not, then leave

> "It is not finished. On one company's careers page it read four lines of a
> long post and reported a number anyway, with no hedge. That is written down as
> the next thing to fix."

Then switch to the page tab and carry on. **Do not click anything else in the
panel.** The full audit is a click and a minute, and it belongs on the page.

---

## Part two — the page, click by click

### 1. Press "Check my fit"

Nothing is pasted in front of anybody. Say why:

> "Both boxes are already filled — the real post, the real resume. I am not
> going to make you watch me paste ninety lines of text."

Then press it.

> "This takes about ninety seconds. It is 47 model calls and about
> seventeen thousand tokens — under half a cent, and that is a
> calculation from the token counts, not a bill."

### 2. Talk over the first requirements as they stream

They appear one at a time, each with a verdict, a reason and a resume line.

> "Every one of these is one requirement pulled out of the post. It searches
> the resume for it, judges what comes back, and then verifies."

> "The important part is the last one. Verify always runs. It is not the
> model's decision."

### 3. Point at any line that carries a quote

> "That quote was not written by the model. The model returned a **line
> number**. The text you are reading was read back out of the resume file at
> that number."

> "Which means a made-up quote is impossible here. Not unlikely — impossible."

### 4. Watch for the retry, and say the sentence either way

If the live line reads **"It threw away its own answer and is searching
again"**, stop and point at it:

> "There. It found nothing on the first pass, so it went back with different
> search terms. That is a conditional edge in the graph — I can show you the
> line."

**If it does not fire this run, say so rather than waiting:**

> "It fired three times when I ran this on the fifteenth. It may not today —
> and that is the honest version. Slide eleven is about exactly this trigger."

Do not stall the demo waiting for it.

### 5. Land on a clean "not evidenced"

Find one with a reason and **no quote at all**. Point at the empty space.

> "No line. It did not reach for the nearest thing and call it a match. It
> searched, it found nothing, and it said nothing."

> "That empty space is the product working."

### 6. Let it finish. Show the three counts and the sentence

> "Three counts, and the sentence at the top is the call: is this worth
> applying for, and what is missing."

**Do not read the numbers off as if they were promised.** Say what they are:

> "That is this resume against this post, today."

### 7. Optional, only if you are ahead of the clock

Open one requirement and press **"Look again at this one"**.

> "Same graph, one requirement, other answers untouched."

**Skip this if you are at four minutes.** It is not worth the clock.

---

## When it breaks

**You have one job: keep talking.** Nobody in the room knows what was supposed
to happen next.

| What went wrong | What you do |
|---|---|
| The model is slow, or hangs | Give it fifteen seconds, then switch to the fallback tab |
| The model is down, or the key fails | Straight to the fallback tab |
| The page is blank | You are on `file://`. Go to `http://127.0.0.1:8000` |
| The server died | Fallback tab, and do not go back to the terminal |
| The panel is empty, or Brave will not load the extension | **Drop part one and go to the page.** Say "the extension is the same audit in the page you are about to see" and move. Never spend more than the 45 seconds on it |
| The panel says Vouch is not running | The server. Same fallback, or drop part one |

**Switching to the fallback, out loud, every time:**

> "That is the live model being slow, so I am switching to a recording of a run
> from last week. Same page, same trace — it is a recording and I am telling you
> it is a recording."

Then carry straight on with steps 3, 5 and 6. The recording shows the same
things.

**Never present the recording as a live run.** It is the one thing in this demo
that would actually cost you the interview.

---

## The four things that must not happen

- **Do not claim `rank_bm25`, LangGraph, FastAPI or Groq as your work.** Say
  "library" out loud.
- **Do not promise a count** before the run finishes. Extraction is not
  deterministic — 21, then 23, then 21.
- **Do not paste anything live.**
- **Do not demo from `file://`.**

---

## Questions you will get, and where to point

| Question | Point at |
|---|---|
| "Where does the agent actually decide anything?" | The two conditional edges in `build_graph` |
| "How do you know it did not make the quote up?" | `verify` — the quote is sliced out of the file by line number |
| "What if the model lies about the line number?" | Then verification fails, and that is itself a retry trigger |
| "Why not just one big prompt?" | Slide 3 — you cannot tell the resume from the model |
| "How much does a run cost?" | 47 calls, ~17,000 tokens, **under half a cent** on Groq. Say it is a calculation from token counts, not a metered bill — nothing records usage |
| "Is this production ready?" | No, and slide 17 is the list of what it would need. Do not soften it and do not apologise for it |
| "Where would this go beyond resumes?" | Slide 16. A document against a rulebook. **Lead with the guarantee, not with a list of industries** |
| "Have you done this for a customer?" | The bilingual compliance engine on the resume — same shape, regulated customers. **Do not invent a second one** |
| "How would it scale?" | Slide 17. Parallel by construction, and the free local screen is what makes the paid call affordable |
| "Why LangGraph and not X?" | Slide 10, and `docs/decisions/0001` is the written argument with the options that lost |
| "Did you write this, or did the agents?" | Slide 15. I briefed it, read every report and rejected work — and the repository is the evidence. One example worth having ready: two sessions found the same hole in the API contract independently, and both reports say so |
| "What did you learn?" | Slide 14. Almost every model problem was a data problem |

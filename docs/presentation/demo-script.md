---
status: draft
date: 2026-09-16
brief: 0005-the-presentation
---

# Demo script

Five minutes of the fifteen. Every click, in order, with the words to say over
it. The slides are [`slides.md`](slides.md).

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

**A second browser tab, already open, on `http://127.0.0.1:8000/?fixture=summary`.**
That is the fallback. Do not open it now — just have the tab there.

---

## The run, click by click

### 1. Press "Check my fit"

Nothing is pasted in front of anybody. Say why:

> "Both boxes are already filled — the real post, the real resume. I am not
> going to make you watch me paste ninety lines of text."

Then press it.

> "This takes about ninety seconds, and it costs a fraction of a cent."

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
> and that is the honest version. Slide nine is about exactly this trigger."

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
| "How much does a run cost?" | **NOT ESTABLISHED.** Nothing records token usage. Say that, do not estimate |
| "Is this production ready?" | No. Slide 13 |

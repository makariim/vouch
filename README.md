# Vouch

Paste a job post. Point it at your resume. Vouch answers every requirement in
the post with *your resume shows this*, *shows part of this*, or *does not show
this* — and names the resume line that proves it.

Where there is no evidence it says so, and quotes nothing. That refusal is the
product.

## What it does

A job post goes in as pasted text. A resume goes in as a PDF or as plain text.

Every requirement in the post comes back with a verdict, the exact resume line
that supports it, and that line's number. A requirement nothing in the resume
supports is marked not evidenced and carries no line at all.

It then says whether the job is worth your evening: what would sink the
application, what proves you fit, and which lines of your resume hold real
evidence but state it too weakly to count.

## Why it is built this way

The obvious build is one model call over the post and the resume together. Do
that and you cannot tell whether the resume said it or the model wanted it to.

So the resume is not an argument. It is a tool:

1. The resume is split into numbered lines and indexed.
2. For each requirement the agent searches that index and gets real lines back.
   This is BM25 word matching through the `rank_bm25` library. No model call.
3. The model sees only the lines that came back, and answers with a **line
   number** — not with text.
4. The line shown on screen is read back out of the indexed resume at that
   number. A number that is not in the resume, or a quote that does not match
   the line, sends the requirement round again.

A fabricated quote is not unlikely here. It is impossible. The model never
supplies the words that reach the screen.

The audit is a state graph on LangGraph, not one call:

```
extract → search → judge → verify → (look again, or next requirement) → report
```

The verify step always runs and is not the model's decision. The loop counts
requirements, not model turns, so it cannot quietly stop half way down the post.

The one thing the agent decides on its own is when to look again. A first pass
that finds nothing gets a second search with different words, chosen by the
model. That is a conditional edge in the graph, so the answer to *where does
your agent decide anything* is a line of code rather than a claim.

FastAPI serves it, uvicorn runs it, `pdfplumber` reads the PDF, and the model
call goes to Groq. All of those are other people's libraries.

Because the quote has to be a real line, how the resume is cut into lines
decides the whole answer. Swapping the PDF reader for one that orders text by
where it sits on the page — reading order, top to bottom — took the same resume
from 160 indexed lines to 51, and its verdict on the same job post from *weak*
to *worth applying*. Same post, same resume, same model, minutes apart. Nothing
about the model changed. Only how the file was read.

## Run it

Python 3.12 or newer, and [uv](https://docs.astral.sh/uv/).

```
uv sync --extra dev
uv run pytest
```

173 tests. They drive the whole graph with a scripted stand-in for the model,
so that needs no key and no network.

The audit itself needs a key for the model call:

```
export GROQ_API_KEY=...
uv run uvicorn audit.server:app --port 8000
```

Open `http://localhost:8000`. Drop a resume PDF on the left or paste the text,
paste the job post under it, and press the button. One audit takes about a
minute and it costs money, so it only ever runs when you ask.

Set `AUDIT_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` to use Claude instead.
The code was written against Anthropic; Groq is the key that was available.

Uploaded resumes are plain files under `resumes/`. Nothing is hosted, there are
no accounts, and the only thing that leaves your machine is the model call.

### The browser extension

It notices you are on a job post and gives you one glance at it. Load it
unpacked:

1. Open `chrome://extensions`.
2. Turn on **Developer mode**, top right.
3. Click **Load unpacked**.
4. Choose the `extension/` folder — the one holding `manifest.json`.
5. Pin **Vouch** to the toolbar.

It talks to `localhost:8000` and nowhere else. It never runs a full audit by
itself. There is no build step and no npm.

## What is wrong with it

**Most verdicts land in the middle.** On the last real run, 13 of 21
requirements came back partly evidenced. That verdict is absorbing two
different things — evidence that is thin, and evidence that is there but stated
badly — and it should be split.

**Extraction is not deterministic.** The same job post gave 23 requirements,
then 21, then 22. Pulling the requirements out of a post is itself a model
call. So the count is not a property of this tool, and nothing here should be
read as one.

**The agent used to grade its own work, and that failed.** Looking again was
triggered by the model flagging its own evidence as thin. It never did — 0
times out of 21, 23 and 21 across three runs, including where its own written
reason said the resume did not mention the thing. The trigger is now a first
pass that found nothing, which is observable in the data.

**Cost is NOT ESTABLISHED.** Nothing in the pipeline records token usage, so
there is no figure for what one audit costs. Any number would be a guess.

**It is not production ready**, and was never meant to be.

## Where the reasoning is

`docs/decisions/` — eight records: what was decided, what was rejected, what it
cost, and what would make us change our mind.

`docs/future.md` — eight things that were designed and deliberately not built,
each with the reason it is not in this version.

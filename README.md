# Vouch

**Every answer here arrives with the line that proves it, or it arrives empty.**

Not a borrowed word. To vouch for someone is to say you can back the claim up —
and to be asked, reasonably, *back it up with what?* This tool has to answer that
question on every single line it writes.

## What it looks like

Three requirements from one real job post, judged against one real resume:

```
EVIDENCED      Approximately 6-8 years of hands-on experience in AI Application
               development, software engineering, machine learning engineering …

               resume line 5: AI engineer with six years building and operating
               production systems at scale. Core engineer on an enterprise
               knowledge intelligence


PARTLY         Predictive AI: Developing and deploying classic machine learning
               models for use cases like forecasting, churn prediction, and
               fraud detection.

               resume line 65: Built fraud detection and campaign infrastructure
               for the Microsoft Rewards loyalty programme, modernised
               Notifications Platform


NOT EVIDENCED  A Master's Degree or Ph.D. in Computer Science, Statistics,
               Artificial Intelligence, Engineering, or a related quantitative
               field.


```

Look at the last one. No quote, no line number, nothing.

**That empty space is the product.** Anything can tell you that you are a good
fit. This is built so that it cannot say where the evidence is when there is
none.

*Three rows, word for word, out of the 21-requirement run written down in report
[`0003`](docs/reports/0003-groq-and-the-first-real-run.md) — the only run whose
every verdict is recorded here line by line. It predates the PDF reader change
below, so its counts are not the current ones. Requirement text is trimmed at the
`…`; the quotes and line numbers are untouched. `EVIDENCED` / `PARTLY` /
`NOT EVIDENCED` are the tool's `evidenced` / `partly_evidenced` /
`not_evidenced`.*

## The whole thing in three

| A document against a rulebook | A verdict on every line | A quote it cannot fake |
|---|---|---|
| A resume is checked against a job post, requirement by requirement. Nothing is scored out of ten. | Every requirement in the post comes back judged, with the resume line that supports it and that line's number. | The model answers with a **line number**. The words on screen are read back out of the resume at that number. |

## Who this is for

| If you are | Start at |
|---|---|
| Deciding whether a job is worth your evening | [What it does](#what-it-does), then [Run it](#run-it) |
| Judging whether the person who built it can think | [Why it is built this way](#why-it-is-built-this-way) and `docs/decisions/` |
| Looking for what it gets wrong | [What is wrong with it](#what-is-wrong-with-it) — it is a real section, not a disclaimer |

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

| Step | What happens | Model involved |
|---|---|---|
| 1 | The resume is split into numbered lines and indexed | no |
| 2 | Each requirement searches that index and gets real lines back — BM25 word matching, through `rank_bm25` | no |
| 3 | The model sees only the lines that came back, and answers with a **line number** | yes |
| 4 | The line shown on screen is read back out of the indexed resume at that number | no |

A number that is not in the resume, or a quote that does not match the line,
sends the requirement round again.

> [!IMPORTANT]
> A fabricated quote is not unlikely here. It is impossible. The model never
> supplies the words that reach the screen.

The audit is a state graph on LangGraph, not one call:

```
extract → search → judge → verify → (look again, or next requirement) → report
```

The verify step always runs and is not the model's decision. The loop counts
requirements, not model turns, so it cannot quietly stop half way down the post.

The one thing the agent decides on its own is when to look again. A first pass
that finds nothing gets a second search with different words, chosen by the
model. That is a conditional edge in
[`src/audit/graph.py`](src/audit/graph.py), so the answer to *where does your
agent decide anything* is a line of code rather than a claim.

### Other people's libraries

LangGraph, FastAPI, uvicorn, `rank_bm25`, `pdfplumber`, and Groq for the model
call. None of those are mine, and nothing here claims them.

### How the resume is read decides the answer

Because the quote has to be a real line, how the resume is cut into lines
decides the whole answer. Swapping the PDF reader for one that orders text by
where it sits on the page — reading order, top to bottom — took the same resume
from 160 indexed lines to 51, and its verdict on the same job post from *weak*
to *worth applying*. Same post, same resume, same model, minutes apart. Nothing
about the model changed. Only how the file was read.

*Both runs, side by side: report [`0020`](docs/reports/0020-read-the-pdf-in-reading-order.md).*

## Run it

Python 3.12 or newer, and [uv](https://docs.astral.sh/uv/).

```
uv sync --extra dev
uv run pytest
```

**181 tests**, in about 3 seconds. They drive the whole graph with a scripted
stand-in for the model, so that needs no key and no network.

The audit itself needs a key for the model call. Put it in a `.env` file at the
repository root:

```
GROQ_API_KEY=...
```

```
uv run uvicorn audit.server:app --port 8000
```

> [!TIP]
> A `GROQ_API_KEY` already exported in your shell wins over the file, and the
> server says on startup which of the two it used. That is the confusing failure
> worth ruling out first: a stale key exported months ago, quietly beating the
> good one on disk.

Open `http://localhost:8000`. Drop a resume PDF on the left or paste the text,
paste the job post under it, and press the button.

> [!WARNING]
> One audit takes about a minute and it spends real money, so it only ever runs
> when you press the button. Nothing runs on a timer.

Set `AUDIT_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` to use Claude instead.
The code was written against Anthropic; Groq is the key that was available.

Uploaded resumes are plain files under `resumes/`. Nothing is hosted, there are
no accounts, and the only thing that leaves your machine is the model call.

### The browser extension

It notices you are on a job post and gives you one glance at it.

**Load it unpacked in [Brave](https://brave.com/).** That is where it was built
and where it is demonstrated. A work Chrome managed by corporate policy will
refuse an unpacked extension no matter what you click — that is the policy doing
its job, not a fault in this.

1. Open the browser's extensions page and turn on **Developer mode**.
2. Click **Load unpacked**.
3. Choose the `extension/` folder — the one holding `manifest.json`.
4. Pin **Vouch** to the toolbar.

It never runs a full audit by itself. There is no build step and no npm.

> [!IMPORTANT]
> **It is injected into every page you open**, not only job pages. The content
> script's `matches` in `manifest.json` are `http://*/*` and `https://*/*`,
> because a thing that tells you *this is a job post* has to read the page
> before it can know that. Nobody asks it to look.
>
> **Looking is the whole of what it can do.** `host_permissions` is
> `http://localhost/*` and `http://127.0.0.1/*` — those two and nothing else —
> so the browser blocks any request to anywhere but your own machine before it
> reaches the network. There is no key in it, and nothing it reads has anywhere
> to go.
>
> Both halves are in `extension/manifest.json`, which is 35 lines. Read it
> rather than taking this paragraph's word for it.

## What is wrong with it

Every number below carries the command or the report that produced it. Anything
not measured says it is not measured.

**Most verdicts land in the middle.** On the last real run, 13 of 21
requirements came back partly evidenced — report
[`0020`](docs/reports/0020-read-the-pdf-in-reading-order.md). That verdict is
absorbing two different things — evidence that is thin, and evidence that is
there but stated badly — and it should be split.

**Extraction is not deterministic.** The same job post gave 23 requirements,
then 21, then 22 on one post — report
[`0020`](docs/reports/0020-read-the-pdf-in-reading-order.md). Pulling the
requirements out of a post is itself a model call. So the count is not a
property of this tool, and nothing here should be read as one.

**The agent used to grade its own work, and that failed.** Looking again was
triggered by the model flagging its own evidence as thin. It never did — 0 of
21, 0 of 23, 0 of 21 across three real runs, including where its own written
reason said the resume did not mention the thing. The trigger is now a first
pass that found nothing, which is observable in the data. Decision
[`0007`](docs/decisions/0007-the-agent-stops-grading-itself.md).

**What a run costs is a calculation, not a bill.** About 47 model calls and
17,000 tokens for one audit, which is under half a cent at Groq's list price for
`openai/gpt-oss-120b` — report
[`0022`](docs/reports/0022-revise-the-presentation.md).

> [!IMPORTANT]
> That figure is arithmetic over token counts and a published price list.
> **Nothing in the pipeline records usage**, so no run here has ever been
> measured against an actual invoice. Recording it is a small change that has
> not been made.

**It is a demonstration.** It was built to be looked at and argued with, not to
be put in front of users.

## Where the reasoning is

`docs/decisions/` — eight records: what was decided, what was rejected, what it
cost, and what would make us change our mind.

`docs/future.md` — nine things that were designed and deliberately not built,
each with the reason it is not in this version.

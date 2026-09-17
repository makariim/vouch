---
status: open
date: 2026-09-17
brief: 0030-the-readme-again
---

# 0030 — The README again

**The page now opens with three real verdicts, one of them empty, before it
explains anything. The name is explained. Every command in it was run here
today. Four false things were false; a fifth was too.**

Only `README.md`, this report and this brief's status line were touched.

## The reference was not in the session

The brief says the author's `formwork` README "has been pasted into the session
that hands you this brief." **It was not.** I did not ask for it and did not
stop.

What I used instead: **`FORMWORK.md` in this repository**, which is the same
author's page for the same kit and carries the shape the brief describes —
short sections, tables where a paragraph is a list, `> [!NOTE]` and `> [!TIP]`
callouts, bold lead-ins used sparingly, a *what it costs* section that says what
is unmeasured, and a *what it cannot do* section. Plus the brief's own
description of the reference, which is detailed enough to build from.

**If the real README differs, the thing most likely wrong here is the running
order**, not the ingredients.

## Commands I ran, and what they printed

| Command | Printed |
|---|---|
| `uv run pytest` | **181 passed, 1 warning in 3.05s** |
| `uv sync --extra dev` | `Resolved 66 packages` · `Audited 64 packages` |
| `uv run uvicorn audit.server:app --port 8000`, key unexported | `audit: read .env -- set GROQ_API_KEY`, then `GET /` → **200, 10,292 bytes**, `GET /resumes` → **200** |
| `formwork check` | **green, 12 checks** |

The uvicorn run was done with `env -u GROQ_API_KEY`, so the `.env` path is what
was actually exercised — not a shell variable that happened to be set.

**No audit was run against Groq.** That is a paid call and the brief did not ask
for one. Every verdict on the page comes out of `docs/reports/`, which is what
the brief asked for.

## Where each row of the example came from

All three are from the 21-requirement run in report
[`0003`](0003-groq-and-the-first-real-run.md), which is **the only report that
writes down every verdict line by line**. Reports `0018` and `0020` give counts,
not rows.

| Row | Source | Verbatim? |
|---|---|---|
| `EVIDENCED` — 6-8 years | `0003`, requirement 17, `resume line 5` | quote and number untouched; requirement text trimmed at `…` |
| `PARTLY` — predictive AI | `0003`, requirement 5, `resume line 65` | quote, number and requirement text all whole |
| `NOT EVIDENCED` — Master's or Ph.D. | `0003`, requirement 18 | requirement text whole; **no quote and no line, because the run produced none** |

**The honesty problem with those rows, named on the page.** Report `0003`'s run
predates the reading-order change in report `0020`, so its counts are not the
current ones. The README says so in the caption under the block rather than
quietly presenting an old run as today's. I chose stale-but-real over
fresh-but-invented, because the brief forbids the second and only asks that the
source be named.

Requirement 5 was picked for the `PARTLY` row over the other twelve because its
quote is one whole readable sentence. Several of the others cite `resume line
73`, a run-together skills list that reads as noise.

## The four false things

| Was | Now | Checked by |
|---|---|---|
| 173 tests | **181 tests** | `uv run pytest` today |
| Cost is NOT ESTABLISHED | 47 calls, ~17,000 tokens, under half a cent, **in an `[!IMPORTANT]` callout saying it is arithmetic over a price list and that nothing records usage** | report `0022` |
| `export GROQ_API_KEY=...` | a `.env` at the repository root, with a `[!TIP]` that a shell value still wins and that the server says which it used | report `0028`, and run above |
| `chrome://extensions` | **Brave**, said as where it was built and demonstrated, with managed Chrome named as policy doing its job | demo script, brief `0022` |

Both halves of the cost claim are on the page, as the brief required. The number
and the caveat are not in the same breath — the caveat has its own callout, so
it cannot be skimmed past.

## What else was not true

**`docs/future.md` has nine items, not eight.** The README said eight. Item 9,
*Notice when it has read almost nothing*, was added by brief `0022`. Fixed.
`docs/decisions/` really does hold eight; that one was right.

**The brief's own source pointer is wrong.** Section 4 sources the cost figure
to report `0024`. It is not there — `0024` mentions token recording once, as a
deferred item. The figure originates in **brief `0022`** and is recorded in
**report `0022`**. The README cites `0022`.

**The extension runs on every page you visit.** `manifest.json` has
`host_permissions` of `localhost` and `127.0.0.1` only, so the old line *"it
talks to `localhost:8000` and nowhere else"* is true about the network. But the
content script's `matches` are `http://*/*` and `https://*/*` — it is injected
everywhere, to notice job posts. The README now says the hosts claim is about
`manifest.json`; **it still does not say the content script is universal.** That
is a sentence somebody should add, and it was past what this brief fenced me to
decide.

**`extension/README.md` still says `chrome://extensions`**, at its line 14, with
the same five steps the main README just lost. Out of my fence. It is the second
place a reader is sent to a browser that will refuse them.

**Two run figures coexist and neither is wrong.** Report `0003`'s run was 43
model calls in 58 seconds; the cost figure is 47 calls. Different runs, different
requirement counts. The README gives 47 with its source and does not mention 43,
so nothing on the page collides — but anyone reading `0003` next to the README
will see both numbers.

## What I did not do

No code, no tests, no `extension/`, no `web/`, no `design/`, no
`docs/presentation/`. No badge, no emoji header, no screenshot. No library
claimed — there is a named *Other people's libraries* subsection. No requirement
count promised. The phrase *production ready* does not appear; the section ends
on **"It is a demonstration."**

Nothing from the reference's wording, subject or claims was copied. The one
structural borrowing the brief asked for — a transcript before an explanation —
holds entirely different content.

## The check

`formwork check` — **green. All 12 checks**, including `doc-links` over the six
repository links the page now carries.

Nothing staged.

---

## Correction, 2026-09-17

Added after the report above was written, on the director's instruction, with
the fence widened to include `extension/README.md`.

**Two things this report named as findings and left alone are now done.** They
were not out of scope because they were wrong to do; they were out of scope
because brief `0030` fenced the session to `README.md`.

### 1. The content script disclosure is now on the page

`README.md`, an `[!IMPORTANT]` callout in *The browser extension*. Both halves,
as the brief's framing requires:

- **It is injected into every page**, not only job pages — `matches` of
  `http://*/*` and `https://*/*`. A thing that tells you *this is a job post*
  has to read the page before it can know that, and nobody asks it to look.
- **Looking is all it can do** — `host_permissions` is `http://localhost/*` and
  `http://127.0.0.1/*` and nothing else, so the browser blocks any request off
  the machine before it reaches the network.

The callout ends by pointing at `extension/manifest.json`, all 35 lines of it
(`wc -l`), rather than asking to be believed.

The old sentence *"It talks to `localhost:8000` and nowhere else"* is gone. It
was true about the network and silent about the injection, which is the half a
reader would have wanted first.

### 2. `extension/README.md` no longer sends anyone to `chrome://extensions`

Its *Load it* section now opens with Brave, in the same words the main README
uses, and the five steps are four — the first step was the `chrome://extensions`
URL itself.

Two consequential edits came with it, both to keep the page true rather than
merely consistent:

| Line | Was | Now | Why |
|---|---|---|---|
| Opening sentence | "A **Chrome** extension that notices…" | "An **MV3** extension that notices…" | the page no longer tells you to use Chrome |
| *Run it against the backend* | "fails in **Chrome** before it reaches the network" | "fails in **the browser**…" | same |

**The `--load-extension` note still says Chrome, deliberately.** It is about
Chrome 137's command-line behaviour and about `extension/tools/`, which assumes
Chrome for Testing. That one is a true statement about Chrome, not a
recommendation to use it. Only its "five steps above" became "four steps
above".

### 3. The brief's cost pointer

Recorded here so it is not rediscovered a third time.

**Brief `0030`, section 4, sources the cost figure to report `0024`. That is
wrong.** `0024` mentions token recording exactly once, as an item deferred into
slide 17's list of what is not done. It carries no cost figure.

**The figure originates in brief `0022`** — 47 model calls, about 17,000 tokens,
12,500 in and 4,100 out, under half a cent on `openai/gpt-oss-120b` at Groq's
$0.15/$0.60 per million — **and is recorded in report `0022`.** `README.md`
cites `0022`.

### The check

`formwork check` — **green. All 12 checks**, re-run after all three edits.

Still no code, no tests, no `web/`, no `design/`, no `docs/presentation/`.
Nothing staged.

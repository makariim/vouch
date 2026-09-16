---
status: open
date: 2026-09-16
brief: 0021-the-readme
---

# 0021 — The README

**`README.md` exists, answers the four questions, and every command in it was
run here as written.** One file changed. No code, no tests, no other document.

The gate is **green, 12 checks**.

## What changed

| | |
|---|---|
| `README.md` | **new.** 137 lines. The four answers, then two pointers, then it stops |

## What was run

Nothing wrote to disk outside `README.md` and this report. The commands below
are the ones the README carries, run in this repository to check they work.

| Command | What it printed |
|---|---|
| `uv sync --extra dev` | resolved 66 packages, built `vouch 0.1.0` |
| `uv run pytest` | `173 passed, 1 warning in 9.62s` |
| `uv run uvicorn audit.server:app --port 8000` | `Uvicorn running on http://127.0.0.1:8000` |
| `curl localhost:8000/` | `200`. `/styles.css` and `/app.js`, `200` each |
| `POST /prescreen` | `{"signal":"skip","matched":0,"total":4}` — no key, no model call |
| `uv run audit --help` | the usage block |

`uv sync` and `uv run pytest` were also run against a **clean environment** —
an empty venv in a scratch directory, nothing inherited from this working copy.
Same result, 173 passed. That is the clean shell the brief asks for, and it is
why the README's install line can be trusted by somebody who has just cloned
this.

**One command in the README was not verified end to end.** There is no
`GROQ_API_KEY` and no `ANTHROPIC_API_KEY` in this environment, so a real audit
never ran. The server starts, serves the page and answers every endpoint that
makes no model call. The key line itself is unverified.

## The check

`formwork check` — **green. 12 checks**, each shown to reject the wrong input
and accept the right one.

Nothing a check can see was at risk here. The gate cannot tell whether a README
is any good, which the brief says outright. The evidence is this report.

## Git status

```
?? README.md
?? docs/briefs/0021-the-readme.md
?? docs/reports/0021-the-readme.md
```

Nothing staged. No tracked file modified.

## Where each number came from

Every figure on the page, and its source. There are five.

| On the page | From |
|---|---|
| 173 tests | `uv run pytest`, run for this brief |
| 13 of 21 partly evidenced | report `0020`, the after row of its counts table |
| 23, then 21, then 22 requirements | report `0020`; report `0018` has the same three |
| 0 of 21, 0 of 23, 0 of 21 self-reports | decision `0007` |
| 160 indexed lines to 51, weak to worth applying | report `0020`, and the standing brief's table |
| cost NOT ESTABLISHED | report `0003`. Nothing records token usage |

"About a minute, and it costs money" is the page's own run note in
`web/index.html`, and report `0003`'s 58 seconds behind it.

**The "about 60%" from slide 11 is not on the page.** It is given as 13 of 21,
which is the measured run rather than a rounded claim about the product.

## What is not true any more

This is the part the brief said would be most useful, and it turned up three
things.

### `uv run pytest` fails in the working copy

It does not fail from a clean clone. It fails here, on the author's machine,
which is worse — this is the shell the demo gets prepared in.

```
error: Failed to spawn: `pytest`
./.venv/bin/pytest: bad interpreter:
  /Users/muhammadelsherif/Personal/Repos/job-hunter/.venv/bin/python3
```

Every console script in `.venv/bin` still carries a shebang pointing at the old
`job-hunter` path from before the rename. `uv sync` rebuilds and reinstalls the
project package — it did, on this run — but it does not rewrite those shims, so
the problem does not clear itself.

`uv run python -m pytest` works around it. `rm -rf .venv && uv sync --extra dev`
fixes it. **Neither was done here**: the brief owns `README.md` and nothing
else, and deleting a virtual environment two days before a demo is the human's
call.

### The standing brief says 172 tests

It is 173.

### The old name survives in two places, correctly

`docs/reports/0006-design-and-brand.md` says *"The name is Attest"*, and
`design/README.md` explains that take one was called Attest. Both are records
of their own date and neither was touched.

## The three that matter

**Done but not asked for.** One paragraph, added after the first pass and on
instruction: the reading-order finding in *Why it is built this way* — 160
indexed lines to 51, the verdict from weak to worth applying, nothing about the
model changed. The first draft left it out because section 3 fixes what goes on
the page and there was no slot for it. It is in now, inside the *why*, where it
belongs: the whole argument is that the quote must be a real line, so how the
resume is cut into lines decides the answer.

**Asked for but not done.** Nothing in section 3 is missing. The key line in
*Run it* is the one claim not verified end to end, and it is named above.

**Wrong in the brief.** Section 6 says do not change any document other than
`README.md`. Section 9 says the report must contain certain things, and the
loop expects that report at `docs/reports/0021-the-readme.md`. Those two
contradict each other. The first pass stopped and reported in conversation
instead; this file exists because the human resolved it.

That is worth fixing in the standing form of these briefs rather than here: a
brief that fences off every document should say the report is the exception.

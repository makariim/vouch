---
status: done
date: 2026-09-15
---

# 0009 — Page: the summary, and re-running one requirement

> **Wave 1, stream 4.** Runs at the same time as `0006`, `0007`, `0008`.
> **You own `web/` and nothing else.** Do not touch `src/`, `extension/` or
> `design/` — three other sessions are in them now.
>
> **Do not wait for the backend.** Build against a hand-written fixture.

## 1. Goal

Two things the page needs before it is shown to anyone.

**A summary at the top**, so the answer comes before the evidence. Right now you
read 21 rows to find the three that matter.

**A button that re-runs one requirement**, so the agent's retry loop can be seen
happening. It has never fired on its own in three runs. This makes it fire when
you press it.

**If we do not do this:** the page is a table, and the most interesting thing
about the system is invisible in the demo.

## 2. Scope

**The summary block**, above the requirement list, fed by the new `summary`
event in decision `0005`:

- the fit call and its one-sentence reason
- **blockers** — required and missing
- **where your resume undersells you** — the evidence is there, the wording is
  weak. Give this the most space. It is the thing nobody else does
- strongest cards

**Required vs preferred.** A requirement carrying `required: false` must read
differently from a hard one. A missing *"strong plus"* is not a missing degree.

**Re-run one requirement.** A small control on each row. Pressing it re-audits
that requirement alone and streams the new steps into the same row.

- the search terms must be visibly **different** from last time
- **the retry must look like a retry** — the amber block the fixture already has
- the old verdict is replaced, and the counts update

**Out of scope:**

- **restyling.** Brief `0006` is designing this right now. Structure the markup
  so tokens can be dropped in later, and change no colours or fonts yourself
- clicking a line number to open the resume. Roadmap
- showing the lines the agent rejected. Roadmap
- the tailor, any Python, anything in `extension/` or `design/`

## 3. Must not happen

- **Do not change decision `0005`.** Three sessions build against it. Report a
  problem, do not fix it alone.
- **Do not compute the summary in JavaScript.** It arrives in the `summary`
  event. Two implementations of one judgement will drift.
- **Do not invent a verdict the events did not carry.**
- **No CDN, no external font.** Decision `0002`, and the page must work offline.
- Do not remove fixture mode. It is the demo's safety net.

## 4. Done when

- The summary block renders from the fixture, including the empty cases —
  no blockers, no undersells.
- Required and preferred requirements are visibly different.
- **Re-running one requirement works end to end** and the retry is legible.
- The page still runs the original full fixture without regression.
- **Run against the real backend once `0007` lands**, with any mismatch reported.
- Nothing fetched except `/audit` and the new endpoints.

**What would tell us it failed:** somebody watching from two metres cannot tell,
without narration, that the agent went back and searched again.

## 5. Checked by

`formwork check`.

**The gate cannot see a web page.** The evidence is watching it once on a screen,
from across a room.

## 6. The report must contain

The standing list, plus:

- what the summary block looks like in each state, described
- **what re-running one requirement looks like** — the sequence on screen
- **what decision `0005` got wrong**, missing, or awkward to render
- whether it has run against the real backend, or fixture only
- what was left structurally awkward for brief `0006`'s tokens to fix

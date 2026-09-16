---
status: done
date: 2026-09-15
---

# 0014 — The extension: apply the design, get its answer back

> **You own `extension/` and nothing else.** Do not touch `src/`, `tests/`,
> `web/`, `design/` or `fixtures/` — three other sessions are in them.
>
> **Read `design/README.md` first.**

## 1. Goal

The extension is written and has never been opened in a browser. `design/` now
holds take two, including the panel and the badge.

Apply it, and close the one thing that stopped the panel working in live mode.

**If we do not do this:** the extension shows a word count where its answer
should be, in default styling, and it is the part of the product nobody else
has.

## 2. Scope

### The gap that mattered

Brief `0008` found it: `summary` only exists inside the audit stream, and the
panel may not start an audit. So the panel had no live source for its headline.

**Decision `0006` closes it.** `POST /summary {post, resume_id}` returns the
stored answer for a post already audited, or `{"known": false}`.

- **Ask for it when the panel opens.** If it comes back, show the whole answer —
  the call, what they need that you cannot show, what proves you fit, the lines
  to fix.
- **If it comes back `{"known": false}`**, show the instant word match and the
  button to run the audit. That is the state the panel has today.
- **Never run the audit automatically.** A minute and real money per job post.
  The button stays a button.

### Apply the design

- **Import `design/tokens.css`.** `design/canvas/Extension.dc.html` is the
  reference for the panel, and the badge is on the same board.
- **If you need a value that is not in `tokens.css`, stop and report it.**
- **Rewrite the copy to the plain-English rules in `design/README.md`.**
- **Draw the icons.** The extension ships with no PNGs, so Chrome shows a puzzle
  piece. `design/assets/` has the mark.

### Two things the contract changed under you

- **All three summary lists now carry `text` and `line`.** Decision `0006`.
  `extension/fixtures/requirements.json` was a workaround for that gap — it can
  go.
- **`signal` is `worth_a_look | maybe | skip`.** Written down now, so it can be
  rendered rather than ignored.

**Out of scope:** any Python, anything in `src/`, `web/`, `design/`. Highlighting
requirements on the job page — roadmap, and flaky. Publishing to the store.

## 3. Must not happen

Standing ones apply.

- **No model call from the extension, ever.** No key in a browser. It talks to
  `localhost` and nothing else.
- **No CDN, no external font, no analytics.**
- **Never run a full audit automatically.** The pre-screen may be automatic.
- **Fixture mode is a switch, never an automatic fallback.** Brief `0008` made
  this call and it was right: a panel that quietly shows invented numbers when
  the server is down would have you reading fabricated results out loud. The
  FIXTURES flag stays visible while it is on.
- **Do not edit `design/tokens.css`.** Report a gap.

## 4. Done when

- **It loads unpacked in Chrome**, and the badge changes state on a real
  LinkedIn job post. This has never been done.
- The panel shows the full answer when `POST /summary` knows the post, and the
  word match when it does not.
- Every state renders: no job post, job post, no default resume, server down,
  fixture mode.
- It has been **walked across five real job posts**, LinkedIn first.
- The panel matches `design/canvas/Extension.dc.html`, every value from
  `tokens.css`.
- Icons exist. No puzzle piece.

**What would tell us it failed:** you are on a job post and cannot tell in five
seconds whether to apply.

## 5. Checked by

`formwork check`.

**The gate cannot see an extension.** The evidence is loading it in Chrome and
using it on real job posts, which is what section 6 asks about.

## 6. The report must contain

The standing list, plus:

- **how detection performed on five real job posts** — what it caught, what it
  missed. This has never been measured and is marked NOT ESTABLISHED today
- **any value `tokens.css` did not have**
- what the panel looks like in each state
- **how to load it**, exactly, because it will be done live
- whether it has run against the real backend, or fixture only

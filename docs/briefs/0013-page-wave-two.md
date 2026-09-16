---
status: done
date: 2026-09-15
---

# 0013 — The page: apply the design, close the gaps

> **You own `web/` and nothing else.** Do not touch `src/`, `tests/`,
> `extension/`, `design/` or `fixtures/` — three other sessions are in them.
>
> **Read `design/README.md` first.** It is one page and it is the whole job.

## 1. Goal

The page works and looks like a form. `design/` now holds take two — a dark
theme, a mark, and `tokens.css` with every value the boards use.

Apply it. Then close the two gaps brief `0009` reported and could not fix.

**If we do not do this:** the design was drawn and never shipped, and the page
shown live is the one that made you wince.

## 2. Scope

### Apply the design

- **Import `design/tokens.css`.** Every colour, size and radius comes from it.
  `design/canvas/Web.dc.html` is the reference for what the page should look
  like.
- **If you need a value that is not in `tokens.css`, stop and report it.**
  That file claims full coverage, verified mechanically. A gap is a finding.
- **Three bare `#fff` values** are in `web/styles.css` today — `.step`,
  `.evidence` and `button.run`. Brief `0009` flagged them. They go.
- **Rewrite the copy to the plain-English rules in `design/README.md`.** This
  matters as much as the colours. No invented nouns, no "evidence" as a verb,
  "line 22" not "L22", short sentences.

### Close the two gaps

- **Read `#post=` from the URL** and fill the job post box with it. The
  extension opens `http://localhost:8000/#post=<encoded>`. A fragment never
  reaches the server, which is why it was chosen. Decision `0006`.
- **Point the re-run button at `POST /audit/requirement`.** `RERUN_ENDPOINT` at
  the top of `app.js` is the line. Brief `0012` is building it now. Until it
  lands, the fixture path must keep working.

### Two things the contract changed under you

- **All three summary lists now carry the same five fields** —
  `requirement_id`, `text`, `line`, `line_number`, `reason`. You no longer join
  against the verdict events to get the words. Decision `0006`.
- **Never call the re-run button a retry.** In the copy, in the code, anywhere.
  A person asking for a second pass is not the agent deciding. Decision `0007`.

### Two things `0009` left for a designer to settle

- **An empty Strongest cards panel** currently renders as a green box saying
  "None called out." It looks wrong even though it is right. The design decides.
- **Five full-width blocks push the requirement list below the fold.** `0009`
  suggested two columns. Follow the boards.

**Out of scope:** any Python, anything in `src/`, `extension/`, `design/` or
`fixtures/`. New features. The tailor.

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything, no
changing a check because it failed, and say NOT ESTABLISHED rather than estimate.

- **Do not compute the summary in JavaScript.** It arrives in the `summary`
  event. Counting verdicts already on screen is arithmetic and stays allowed.
- **Do not invent a verdict the events did not carry.**
- **Nothing fetched from the network** except the local endpoints. No CDN, no
  web font. The page must work with the wifi off.
- **Do not remove fixture mode.** It is the demo's safety net.
- **Do not edit `design/tokens.css`.** Report a gap, do not fill it.

## 4. Done when

- The page matches `design/canvas/Web.dc.html` and every value comes from
  `tokens.css`.
- All copy follows the plain-English rules. Read it out loud once.
- Opening `/#post=<something>` fills the job post box.
- The re-run button calls `POST /audit/requirement`, and still works on the
  fixture when the backend does not have it yet.
- The three verdicts are tellable apart **in greyscale**. Check it.
- The page still runs every existing fixture without regression.

**What would tell us it failed:** a value had to be invented, or somebody
watching from two metres cannot follow what the agent is doing.

## 5. Checked by

`formwork check`.

**The gate cannot see a web page.** The evidence is the greyscale check and a
human watching it once from across a room.

## 6. The report must contain

The standing list, plus:

- **any value you needed that `tokens.css` did not have.** The most useful thing
  in this report
- what the page looks like at each stage, described
- what the plain-English pass changed, with two or three before-and-afters
- whether it has run against the real backend, or fixture only

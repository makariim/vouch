---
status: done
date: 2026-09-15
brief: 0002-audit-frontend
---

# 0002 — Audit frontend

The page is built and runs the whole fixture end to end. It has also been run
against a **stand-in** backend over real server-sent events, not against the
real one, which does not exist yet.

## What changed

- `web/index.html` — the page. Two text areas, the Audit button, the
  fixture/live switch, and the three empty regions the events fill in.
- `web/styles.css` — large type, heavy contrast, and the three verdict colours.
  No fonts or stylesheets from anywhere; system fonts only.
- `web/app.js` — loads the fixture, reads the live stream, and renders both
  through one function so the two modes cannot drift apart.
- `fixtures/trace-sample.json` — hand-written from the examples in decision
  `0004`. Twelve requirements, two retries, all three verdicts, and a `done`
  event whose counts are computed from the verdicts above it.

Three files and a fixture. No build step, no framework, no package manager,
nothing to install.

## What was run

- `python3 -m http.server 8731` — served the repository so the page and fixture
  could be loaded. Wrote nothing.
- Headless Google Chrome, four screenshot runs at different points in the
  replay. Wrote only to the scratchpad.
- A stand-in backend in the scratchpad (`fake_backend.py`) that replays the
  fixture as real `text/event-stream` frames on `POST /audit`. **It is in the
  scratchpad, not in this repository**, because brief 0001 owns anything
  server-side.
- `formwork check`.

Nothing was installed. Nothing outside the repository was touched except the
scratchpad.

## The check

`formwork check` — **green**, as a whole. Twelve checks, all `ok`.

## Git status

```
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
?? docs/briefs/0002-audit-frontend.md
?? docs/decisions/0001-audit-is-a-state-graph.md
?? docs/decisions/0002-nothing-leaves-the-machine.md
?? docs/decisions/0003-the-audit-governs-the-tailor.md
?? docs/decisions/0004-the-api-contract.md
?? docs/reports/0002-audit-frontend.md
?? fixtures/
?? pyproject.toml
?? src/
?? web/
```

Nothing staged, nothing committed.

**`src/` and `pyproject.toml` are not mine.** They appeared in this working
tree while this work was running - brief 0001's session is writing into the
same checkout. Nothing of mine touches them and nothing of theirs touches
`web/`, but the two sessions are less separated than the briefs assume: they
share one working tree, so whoever stages next picks up both halves at
whatever state they happen to be in.

## What the page looks like at each stage

**Before the run.** Two labelled boxes side by side, a black Audit button, the
Fixture/Live switch, and the word "Ready." Nothing else on screen.

**The moment `requirements` arrives.** Twelve grey rows appear at once, numbered,
each carrying the requirement wording verbatim. Nothing is filled in yet, so the
shape of the whole job is visible before any verdict exists.

**While a requirement is being worked.** Its row turns pale blue with a blue
bar down the left and a blinking dot beside the text. Under the requirement, a
trail of chips builds left to right: `SEARCH python years experience`, then
`VERIFY checking the quoted line is in the resume`. The chips stay. You can read
back what the agent did after it has moved on.

**A retry.** This is the loud one. It is not a chip in the row — it breaks onto
its own full-width line, amber on amber, three-pixel border, with a `↻` and the
agent's own words: `RETRY only a tools list matched, no framework named —
searching again`. Then the next `SEARCH` chip appears below it with different
terms. Two of these fire in the fixture, on requirements 3 and 5. It stays on
screen for the rest of the run.

**A verdict.** The row takes its colour — green, amber or red — and a word plus
a mark lands on the right: `✓ EVIDENCED`, `– PARTLY`, `✗ NOT EVIDENCED`. When a
line came with it, the quote sits in a white box in monospace with `resume line
11` under it. The one-sentence reason sits below in grey. A `not_evidenced` row
shows a reason and no quote, which is a correct answer and looks like one.

**`done`.** Three large count cards appear above the list — 6, 3, 3 in the
fixture — in the same three colours. The status line reads "Done."

**`error`.** A red banner across the top with the message in large bold, and
**the work already done stays on screen underneath it.** Never a blank page.

## What decision `0004` got wrong, missing or awkward

This is the part worth reading.

**1. `EventSource` cannot do this, and brief 0001 says it should.** Brief 0001
asks for a stream "a browser's `EventSource` can read". `EventSource` only issues
GET requests and cannot send a body. The contract puts the post and the resume
in a `POST` body, so `EventSource` is ruled out by the contract itself. The page
uses `fetch()` and reads the response body as a stream instead. **Nothing needs
to change on the backend** — this is a note for whoever writes brief 0001's
endpoint, so they do not build toward a client that cannot exist.

**2. The frame format is not written down.** `0004` shows six JSON objects but
never says how they sit on the wire — `data:` prefixed frames separated by a
blank line, or one JSON object per line. The parser accepts both, and ignores
`:` keepalives and `event:` lines. So either choice by the backend works. Worth
settling in the record anyway.

**3. `step` has no list of allowed values.** `0004` shows `search` and `retry`.
Brief 0002 also names "verifying" as a state to show. The page styles `search`,
`retry` and `verify`, and renders any other value in a neutral chip rather than
dropping it. If the graph emits `extract` or `judge` steps they will appear,
unstyled but visible.

**4. `error` carries no `requirement_id`.** So an error is always whole-run and
always fatal to the page's view of the run. If a single requirement can fail
while the others continue, the contract cannot express it and the page cannot
show it.

**5. `verdict` with no `line`.** `0004`'s only `verdict` example has a line. A
`not_evidenced` verdict has nothing to quote. The page treats `line` and
`line_number` as optional and shows the reason alone. Confirmed correct against
brief 0001, which says `not_evidenced` with no line is a correct answer.

**6. `done.counts` may disagree with the verdicts that arrived.** The page
prints the counts the backend sent and does not recount, per "do not invent a
verdict the events did not carry". If the backend's arithmetic is wrong, the
demo shows it. Flagging rather than silently fixing.

**7. Nothing says where the page lives.** `0004` says `GET /` serves the page;
brief 0001 says "whatever static file is in the frontend folder". The folder is
now **`web/`** — `web/index.html`, plus `styles.css` and `app.js` beside it, and
`fixtures/trace-sample.json` two levels up. **The backend session has to be told
this**, and it is the one thing that will break the join if it is not.

## Run against the real backend?

**No. Fixture only, plus a stand-in.**

The stand-in replayed the fixture as real SSE frames over a real `POST /audit`,
and the page rendered the whole run live from it. That proves the transport and
the parser. It does **not** prove anything about the real graph, because the
stand-in is the fixture wearing a costume — it agrees with the contract by
construction.

The real run still has to happen once brief 0001 lands.

## The three that matter

**Done but not asked for.**

- **A `?auto=` query parameter** (`?auto=fixture`, `?auto=error`). The page can
  start itself on load. Added because there is no browser driver on this machine
  and it was the only way to capture the real rendered page rather than claim it
  works. It also means the demo can be opened already running. Roughly six lines.
  Say the word and it comes out.
- **A "Preview error state" button.** Section 5 requires the `error` event to
  render, and a recorded run that finishes contains no error. The button replays
  the first few events then renders an error event, so the state can be shown
  without breaking the backend. The error is page-generated and says so in the
  code.
- **The fixture loader tries three paths** and accepts either a bare array or
  `{"events": [...]}`, so whatever brief 0001 records drops in without an edit.

**Asked for but not done.**

- **"Run it against the real backend."** Blocked — brief 0001 has not landed.
  Section 5 says this, and expects it.
- **"Watch it on a shared screen from two metres."** I cannot do this. I have
  looked at the rendered screenshots at full size and the type is large, the
  three verdict colours are far apart, and the retry is a full-width amber block
  that cannot be missed. But **the two-metre test has not been run by a human**,
  and section 6 is explicit that this is the real evidence. It is yours to do,
  and it takes one minute.

**Wrong in the brief.**

- **Two briefs own `fixtures/trace-sample.json`.** Brief 0002 says hand-write it.
  Brief 0001 says the backend writes a real run to that same path. Same file,
  two owners, and the briefs promise the sessions share no files. The
  hand-written one is there now; brief 0001's session will overwrite it, which
  is fine and probably what you want — but it was not deliberate, and if both
  sessions write it at once one of them loses. The loader accepts both shapes so
  the overwrite costs nothing.
- **Section 3 says "one HTML file, one CSS file, one JS file"** but never says
  which folder. Chose `web/`. See point 7 above.
- **The wifi-off claim needs an asterisk.** Section 4 says the page must work
  with the wifi off — it does, nothing is fetched from a network. But the fixture
  is read with `fetch`, which a browser blocks on a `file://` page. So the page
  must be *served*, not double-clicked: `python3 -m http.server 8000` from the
  repository root, then open `/web/`. Still local, still no network. Worth
  knowing before the morning of the demo rather than during it.

## What was cut to fit the day

Nothing in the brief was cut. Everything in section 3 is built.

Deliberately not built, all of it out of scope in section 3: the extension, file
upload, dark mode, and any animation beyond the blinking dot on the row being
worked.

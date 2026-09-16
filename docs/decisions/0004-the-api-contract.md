---
status: accepted
date: 2026-09-15
deciders: [makariim]
consulted: [director]
informed: []
---

# 0004. One endpoint, streamed, fixed before either side is built

## What made this a decision

The frontend and the backend are being built at the same time, in two sessions
that cannot see each other.

Parallel work fails for one reason: each side guesses a different shape, and the
mismatch is found at the end, on the last day, with no time to fix it.

So the shape is written down first and neither side may change it alone.

## What matters here

- Both sessions start now. Neither can wait for the other.
- The demo is the trace arriving live, so the transport has to stream.
- One day. The contract must be small enough to hold in your head.

## Options we looked at

- **WebSocket** — two-way, and we only need one direction.
- **Server-sent events** — one-way, plain HTTP, no extra library.
- **Poll a job id** — simplest to write, and the trace arrives in lumps.
- **Do nothing**, and let the backend session decide. Then the frontend guesses,
  and that is the failure this record exists to prevent.

## What we chose, and why

**Server-sent events over one endpoint.** One direction is all we need, it rides
on plain HTTP, and nothing extra has to be installed on either side.

```
GET  /            the page
POST /audit       {"post": "...", "resume": "..."}  →  text/event-stream
```

Every event is one JSON object with a `type`:

```json
{"type":"requirements","items":[{"id":1,"text":"5+ years Python"}]}
{"type":"step","requirement_id":1,"step":"search","detail":"python backend"}
{"type":"step","requirement_id":1,"step":"retry","detail":"weak, retrying"}
{"type":"verdict","requirement_id":1,"verdict":"partly_evidenced",
 "line":"Built services in Python since 2021","line_number":14,
 "reason":"shows Python, not the span"}
{"type":"done","counts":{"evidenced":5,"partly_evidenced":3,"not_evidenced":4}}
{"type":"error","message":"resume is empty"}
```

**Five types** — see the correction at the end. `verdict` is one of
`evidenced`, `partly_evidenced`, `not_evidenced`.

**Rules while both sessions are running:**

- Neither side changes this alone. A change comes back here first.
- The backend is the source of truth if they ever disagree.
- The frontend builds against a **recorded fixture** of these events, so it never
  waits for the backend to exist.

## What follows

**Good:**

- Both sessions start now, and the join at the end is mechanical.
- The frontend can be finished and demoable before the graph works.
- The event list doubles as the brief for what the trace must show.

**Bad:**

- The shape is guessed before either side is built, so some of it will be wrong.
- Fixing a mismatch costs a round trip through this record, which is slow on the
  last day.
- Six event types is more than the minimum. Some may never be used.

## What would make us revisit this

If the graph turns out to produce something this cannot carry — nested steps, or
partial verdicts — the contract is wrong and gets a new record rather than a
quiet edit. A contract two sessions rely on is not changed in place.

---

## Correction, 2026-09-15

Both working sessions found the same errors in this record. Written here rather
than edited away, because two sessions built against the original wording.

**It said six types and listed five.** The example block has six lines, but two
of them are `step` — once a search, once a retry. The types are `requirements`,
`step`, `verdict`, `done`, `error`. Five. The implementation is right; the count
was wrong.

**The frame format was never stated.** `data:` prefixed frames with a blank line
between them. The frontend parser also accepts one object per line and ignores
`:` keepalives, so either works, but this is the shape.

**`step` has no fixed list of values.** `search`, `retry` and `verify` are
styled by the page. Anything else — `extract`, `judge` — renders in a neutral
chip. Not an error, but the record implied a closed set and there is none.

**`line` and `line_number` are optional.** They are absent or `null` on a
`not_evidenced` verdict. Both read the same in JavaScript and the page handles
either. **Backend sends `null`.**

**`error` carries no `requirement_id`,** so an error is always whole-run. A
single requirement cannot fail while others continue. Left as is; nothing needs
it yet.

**The page lives in `web/`.** `web/index.html`, with `styles.css` and `app.js`
beside it. This record said `GET /` serves the page and never said from where.

**The fixture path was double-booked** by briefs 0001 and 0002. Settled:
`fixtures/trace-sample.json` is the hand-written one and stays — it is the demo
safety net if the model is slow or down. A real recorded run goes to
`fixtures/trace-real.json`. Two files, two purposes, neither overwrites the
other.

---
status: proposed
date: 2026-09-15
deciders: [makariim]
consulted: [director]
informed: []
---

# 0008. The stored answer carries the whole answer

## What made this a decision

Two wave-2 sessions reached the same conclusion without contact.

Brief `0012` built `POST /summary` and deliberately returned only the three
lists, writing in the code: *"the counts and the requirement list are also
sitting in the same file — they are deliberately not returned, because widening
a contract is decision work."*

Brief `0014` tried to draw the panel from it and reported: *"It needs them."*
The artboard's top line is the answer word, one sentence **and a counts row**.
Its bottom is the folded list of everything asked for. Neither is in the reply.

The panel cannot derive them. The three lists are a shortlist, not the whole
set, and re-deriving a judgement in a client is what decision `0006` forbids in
its second line.

## What matters here

- Two sessions, no contact, same conclusion. That is about as clear a signal as
  this project produces.
- The data already exists in the stored file. Nothing has to be computed again.
- One wave left. Whatever this adds must be one line, not a redesign.

## Options we looked at

- **Return the whole stored audit.** Simplest, and it ships every verdict and
  every step to a panel that wants two numbers.
- **Add `counts` and `requirements` to the reply.** Two fields, already in the
  file.
- **Let the panel count the three lists.** Wrong answer — they are a shortlist,
  so the arithmetic would be wrong as well as forbidden.
- **Do nothing.** The panel draws two-thirds of its own design, for want of two
  fields that already exist.

## What we chose, and why

**`POST /summary` returns `counts` and `requirements` alongside the three
lists.** `requirements` is the list as the `requirements` event carries it —
id, text, required — and nothing more.

Both come out of the stored file unchanged. No judgement is recomputed anywhere,
and no client derives anything.

**Three smaller things settled at the same time**, all of them one word or one
field, all found by wave 2:

- **`repair` is a seventh step.** Decision `0006` listed six, taken from the
  code, and missed the one `extract` emits when it fixes a damaged resume line.
  That step is on screen in the demo. The set is
  `search | judge | verify | retry | failed | dropped | repair`.
- **`GET /resumes` items carry `name`.** They carry `id`, `lines` and `default`
  today. The panel promises to say what it checked you against and can only show
  `resume`.
- **`fit_reason` may not use "evidence" as a verb.** It currently produces
  *"0 of 4 requirements are evidenced in your resume"*, which is the largest
  sentence on the page and breaks the writing rule the rest of the product now
  follows. The page renders it verbatim and must — rewriting the backend's
  judgement in a client is exactly what it is forbidden to do.

## What follows

**Good:**

- The panel draws what it was designed to draw.
- Nothing is recomputed in a client; the fields are read from a file.
- The demo's largest sentence stops breaking the product's own writing rule.

**Bad:**

- `POST /summary` now returns more than its name suggests. It is an audit
  summary plus a requirement list.
- Four changes in the last wave, with no time to find what they got wrong.

## What would make us revisit this

If the panel later wants the verdicts too, this endpoint has become "return the
stored audit" by increments, and it should be renamed rather than widened a
fourth time.

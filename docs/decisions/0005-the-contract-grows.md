---
status: accepted
date: 2026-09-15
deciders: [makariim]
consulted: [director]
informed: []
---

# 0005. The contract grows, before four sessions start

## What made this a decision

Four sessions are about to run at once: design, backend, extension, page. Three
of them render or produce the same data.

Decision `0004` is why the first two sessions joined cleanly. Same reason, more
sessions, higher stakes. The shape is fixed first.

## What matters here

- Three streams must start now and none may wait for another.
- The product layer — fit, blockers, undersells — is computed once, in the
  backend, and rendered twice. It must not be re-derived in each client.
- Resumes are now stored. Decision `0002` still holds: stored means **on this
  machine**, never hosted.

## Options we looked at

- **Extend `done` with the product fields.** Backward compatible, and it buries
  a new concern inside an existing event.
- **A new `summary` event.** One more type, explicit, easy to ignore.
- **Let each client compute its own summary.** Two implementations of one
  judgement, drifting. No.
- **Do nothing** and let the backend session decide. That is the failure this
  record exists to prevent.

## What we chose, and why

### One new field on each requirement

```json
{"type":"requirements","items":[
  {"id":1,"text":"...","required":true}
]}
```

`required: false` means the post said *preferred*, *a plus*, *nice to have*.
It changes what a missing item means, and nothing else.

### One new event, `summary`, after `done`

```json
{"type":"summary",
 "fit":"strong",
 "fit_reason":"one sentence, plain",
 "blockers":[{"requirement_id":18,"text":"Master's Degree or Ph.D."}],
 "strengths":[{"requirement_id":17,"line_number":5}],
 "undersells":[{"requirement_id":12,"line_number":77,
                "reason":"the evidence is there but the resume states it weakly"}]}
```

`fit` is one of `strong`, `worth_applying`, `weak`. **Not a percentage.** A
number invites a precision this cannot support.

**`undersells` is the product.** A `partly_evidenced` verdict where the evidence
really is present and the resume states it badly. It is the one thing here a
job seeker cannot get anywhere else.

**So there are now six event types**, and this time that is counted rather than
claimed: `requirements`, `step`, `verdict`, `done`, `summary`, `error`.

### A second endpoint, with no model call

```
POST /prescreen   {"post":"...","resume_id":"default"}
                  →  {"signal":"worth_a_look","matched":14,"total":21}
```

BM25 only. Milliseconds, no cost, no network. This is what runs while somebody
scrolls a job board. The full audit is what runs when they stop.

**Two speeds, on purpose.** A 58-second model call per job while scrolling is
unusable and expensive, and saying so is a better answer than building it.

### Resumes are stored, locally, as files

```
GET  /resumes              list
POST /resumes              upload .pdf or .txt, returns an id
GET  /resumes/{id}         the indexed lines, numbered
POST /resumes/{id}/default make it the default
```

Plain files in a local folder, not a database. Inspectable, deletable by hand,
and obviously not hosted.

`POST /audit` takes `resume_id` **or** inline `resume` text. The page may keep
pasting; the extension will not.

## What follows

**Good:**

- Four sessions start at once and the join at the end is mechanical.
- The product judgement lives in one place and is rendered twice.
- The two speeds are visible in the architecture, not just in a slide.

**Bad:**

- More surface guessed before anything is built. Some of it will be wrong.
- `fit` is a judgement call rendered as one word. It will sometimes read wrong.
- Storing resumes is new state in a product that had none, and state is where
  privacy promises usually break.

## What would make us revisit this

If `undersells` turns out to be empty or wrong on real runs, the headline
feature does not exist and the product claim has to change rather than the
wording. Check it on the first real run, not the day before.

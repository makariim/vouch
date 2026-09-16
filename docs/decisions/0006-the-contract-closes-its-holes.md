---
status: accepted
date: 2026-09-15
deciders: [makariim]
consulted: [director]
informed: []
---

# 0006. The contract closes its holes

## What made this a decision

Three wave-1 sessions built against decision `0005` and all three sent back the
same kind of finding: the record defines endpoints and event shapes, and leaves
out the joins between them.

One of those gaps stops the extension's best half working at all. Another
means half of brief `0009` has nothing to call. Both were reported rather than
patched around, which is what the briefs asked for and why they are fixable now
instead of on demo morning.

## What matters here

- Two clients render the same data and neither may re-derive a judgement.
- The extension may not run an audit by itself — 58 seconds and real money.
- Nothing leaves the machine. Decision `0002` still governs.
- Whatever this adds must be small. There is one wave left.

## The holes, and what closes each

### 1. The panel's headline has no live source

`summary` exists only inside the `POST /audit` stream. The panel leads with the
fit call, and the panel may not start an audit. So in live mode it can show a
word count and nothing else.

**The backend remembers the last audit.**

```
POST /summary   {"post": "...", "resume_id": "default"}
                →  the stored summary event, or {"known": false}
```

Keyed on a hash of the post text plus the resume id. Stored as a local file
beside the resumes, like everything else here.

**This is a better product, not a patch.** Audit a job once, come back to it
later, and the answer is there instantly and for free.

### 2. There is no way to re-run one requirement

Brief `0009` built the control and the whole second pass. There is nothing to
call, and this is the feature that makes the retry loop visible on demand —
the retry has never once fired on its own in three real runs.

```
POST /audit/requirement   {"post": "...", "resume_id": "...",
                           "requirement_id": 3}
                          →  the same event stream
```

**It re-emits `summary` when it finishes.** Otherwise the fit call, the blockers
and the undersells go stale the moment a verdict changes, and the page is left
either lying or apologising.

### 3. The summary's three lists have three shapes

`blockers` carries `text`. `strengths` carries a `line_number` and no words.
`undersells` carries both plus a `reason`. Neither client can render a summary
it holds alone — brief `0008` had to invent a fixture to join against.

**One shape for all three:**

```json
{"requirement_id": 3, "text": "...", "line": "...",
 "line_number": 77, "reason": "..."}
```

`line`, `line_number` and `reason` are `null` where they do not apply. `text`
is always the requirement, verbatim, as it already is in `blockers`.

### 4. Nothing said how a job post reaches the page

Brief `0008` proposed it and built it; brief `0009` never heard.

**Adopt it.** The extension opens `http://localhost:8000/#post=<encoded>`. A URL
fragment is never sent to a server by the browser, so the post reaches the page
without a request. Over 12,000 characters, open the page bare.

**Brief `0009`'s page must read `#post=`.** It does not yet.

### 5. Two closed sets were never written down

```
signal : worth_a_look | maybe | skip
step   : search | judge | verify | retry | failed | dropped
```

Both taken from what the code actually emits, not invented here. `fit` already
had its three and keeps them.

### 6. Two denominators on one screen

The live page shows `fit_reason` saying "0 of 3 requirements are evidenced"
beside a counts row totalling 4. One counts required items, the other counts
all of them. Both are defensible; together they read as a bug.

**`fit_reason` counts every requirement**, the same set the counts row shows.
Required-versus-preferred is what `blockers` is for, and it says so there.

### 7. `required` has no default

**Absent means required.** The safe reading, now a rule rather than an
assumption each client makes alone.

## What follows

**Good:**

- The panel works in live mode, which is most of what the product is.
- The retry becomes demoable on purpose rather than waited for.
- One shape for three lists is less for two clients to get wrong.
- Re-visiting an audited post is free and instant.

**Bad:**

- Stored audits are new state in a product that keeps promising it has none.
  Local files, but it is one more thing to delete by hand.
- `POST /summary` means the extension sends the post text to the local backend
  on every panel open. Local, but it is traffic that did not exist.
- Two new endpoints in the last wave, with no time to find out what they got
  wrong.

## What would make us revisit this

If the stored summary ever answers with a resume the user has since changed,
the answer is wrong and looks authoritative. The key includes the resume id but
not its contents. First thing to fix if resumes become editable.

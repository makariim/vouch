---
status: done
date: 2026-09-15
---

# 0004 — BM25 retrieval

## 1. Goal

`LineIndex.search` scores a line by how many query words it contains. Every word
counts the same, so `python` counts as much as `fastapi`.

On the real run this produced a wrong verdict: requirement 12 asks for FastAPI,
the resume says FastAPI on line 77, and line 77 was never retrieved. See
`docs/reports/0003-groq-and-the-first-real-run.md`.

Replace the scoring with **BM25**, using a published library.

**If we do not do this:** the audit reports a gap that is not a gap. That is the
one failure this product cannot afford, because the whole claim is that it does
not invent things in either direction.

## 2. What BM25 is, in plain words

A scoring function for "how well does this line match this query". It is the
default in Elasticsearch, so it is the thing quietly deciding results in most
search boxes.

**What we do now:**

```
score = how many query words are on this line
        ───────────────────────────────────────
              total words in the query
```

The bottom is the same for every line, so it cancels. The ranking is just *count
the matches*. Every word is worth the same.

**BM25 adds three ideas.**

**1. Rare words count more.** A word appearing on few lines is informative. One
on many lines is not.

- `fastapi` appears once in the resume → heavy
- `python` appears all over it → nearly weightless

This is the part that fixes requirement 12, and it is the whole reason for the
change.

**2. Repeats stop counting after a while.** A line saying "python, python,
python" is not three times more about Python than one saying it once. The gain
flattens off. The constant `k1` sets how fast.

**3. Long lines are penalised.** A long line matches more words by luck alone,
so the score is divided by how long the line is against the average. The
constant `b` sets how hard.

**A risk specific to this resume, which the report must address.** Idea 3 cuts
against us here. The most informative lines are the long flattened skills rows —
73, 77, 79 — precisely the ones length normalisation punishes. If BM25 with the
standard `b=0.75` pushes them *down*, that is worth knowing and saying, not
quietly tuning away.

## 3. Scope

**Install a published BM25.** `rank_bm25` is the expected choice — small,
widely used, pure Python. Another is fine if there is a reason; **say which and
why in the report.**

Do not hand-roll it. An implementation nobody has reviewed, written hours before
a demo, is a worse answer than a library thousands of people run.

**`src/audit/index.py`, the `search` method.** That is the only code change.

Keep the existing tokenizer and stopword list. Keep `get`, `locate` and
`contains_verbatim` exactly as they are — **the verbatim guarantee lives there
and this brief does not touch it.**

**Before running anything**, copy `fixtures/trace-real.json` to
`fixtures/trace-before-bm25.json`. The old run is the comparison and it has to
survive.

**Out of scope — do not touch:**

- the prompts in `model.py`. Section 3 of brief 0003 still applies: a tuned
  prompt makes the evidence worthless
- the retry trigger and `evidence_weak`. Known broken, deliberately left. It is
  a finding for the presentation, not a change to make hours before a demo
- `graph.py`, `events.py`, `server.py`, anything in `web/`
- decision `0004`, the contract
- embeddings or vector search. Decision `0002` allows one outbound call

## 4. Must not happen

Standing ones apply: no writing to version control, no deciding anything — stop
and report, no changing a check because it failed, and where something cannot be
established, say so rather than estimating.

Specific to this work:

- **Do not weaken the verbatim guarantees.** Quotes are still looked up by line
  number and read out of the resume.
- **Do not commit `private/`, `.env`, or any audit output.**
- **Do not tune `k1` or `b` to make one requirement come out right.** Use the
  library defaults. If they are wrong for short lines, say so and leave them.
- **Do not claim authorship of the library** anywhere in the report or the code
  comments.

## 5. Done when

- `search` scores with BM25 from a library, and the change is confined to that
  method.
- **The 38 existing tests still pass**, no key, no network.
- **Requirement 12 retrieves line 77.** The falsifiable one. Prove it by
  replaying the search offline — no model call, no cost.
- The real audit has been run once more, end to end, on the same two files.

**What would tell us it failed:** verdicts get worse overall, or something that
was right before is now wrong. Better on one and worse on three is a failure,
not a trade.

## 6. Checked by

`formwork check` and `pytest tests/ -q`.

Neither can tell whether a verdict is right. The evidence is the before-and-after
comparison below.

## 7. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- **the two runs side by side** — every requirement, old verdict against new.
  Not a summary. This is the point of the brief
- **what moved, and in which direction.** Name every requirement whose verdict
  changed, and say whether it got better or worse
- **whether requirement 12 now finds line 77**
- **what happened to lines 73, 77 and 79** under length normalisation — the risk
  in section 2
- **whether the retry fired this time**, and if not, that it still did not
- the new counts, against `evidenced 2 / partly 16 / not 3`
- which library, which version, and why that one
- how long it took and roughly what it cost, or NOT ESTABLISHED

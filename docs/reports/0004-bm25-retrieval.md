---
status: open
date: 2026-09-15
brief: 0004-bm25-retrieval
---

# 0004 — BM25 retrieval

**BM25 is in. The falsifiable test failed.**

Requirement 12 still does not retrieve line 77. It moved from unranked-past-6
to **rank 7**, missing the cut by 0.19 points behind line 76. The two things
that would carry it over — turning length normalisation off, or widening the
cut to 8 — are the two things section 4 forbids me to decide.

So this stops here. `search` is BM25, the 38 tests pass, the gate is green, and
the one number the brief asked for is still wrong.

**The real audit was not re-run.** There is no Groq key on this machine — no
`.env`, nothing in the environment. Everything below is the offline replay,
which costs nothing and makes no model call.

The brief stays `open`. Two of its five done-when items are unmet and neither
is mine to wave through.

## What changed

- `src/audit/index.py` — `search` scores with `BM25Okapi` from `rank_bm25`
  instead of counting query-word overlap. Plus a private `_bm25()` that builds
  the corpus index once and keeps it.
- `pyproject.toml` — added `rank-bm25>=0.2.2`.
- `.gitignore` — added `fixtures/trace-before-bm25.json`. See the three that
  matter.
- `fixtures/trace-before-bm25.json` — the copy the brief asked for, taken
  before anything else ran. Ignored, so it cannot be committed.

`get`, `locate` and `contains_verbatim` are untouched. The tokenizer and the
stopword list are untouched. Nothing outside `index.py` changed.

## Why `_bm25()` exists, since the brief said one method

`self._tokens` holds **sets**. BM25 needs term *counts* — idea 2 in the brief,
repeats flattening off, is meaningless if you cannot see a repeat. Rebuilding
the corpus on every one of 21 searches was the alternative.

It is a private helper called only by `search`, built lazily, and it adds no
behaviour of its own. If that reads as outside the brief, it is the one place
to push back.

## Which library, which version, why

**`rank_bm25` 0.2.2**, the `BM25Okapi` class. It pulled in `numpy 2.5.3`.

It is what the brief expected and I found no reason to argue. Pure Python over
numpy, no index format, no server, no build step — you hand it lists of tokens
and it hands back scores. The alternatives are search engines (Whoosh,
Elasticsearch) that want a document store this project does not have and does
not want.

`k1=1.5`, `b=0.75`. **Library defaults, untouched.** That is section 4, and it
is also why requirement 12 still fails.

## Requirement 12: what actually happens now

The query the model produced on the real run, replayed offline:

```
Flask, FastAPI, REST API, API development, model serving, ML model deployment,
TensorFlow Serving, MLflow, Docker, Kubernetes, AWS Lambda, Python,
Django REST framework
```

The full ranking, scored:

```
line  78  15.896  len  4  hits [api, python, rest]
line  79  11.438  len 13  hits [aws, docker, kubernetes]
line  75   8.961  len  4  hits [model, serving]
line   7   8.169  len 14  hits [deployment, model, serving]
line  80   4.413  len  2  hits [deployment]
line  76   4.312  len  7  hits [python]          <- the cut is here
line  77   4.125  len 11  hits [fastapi]
```

**Idea 1 worked exactly as the brief said it would.** `fastapi` has the top
IDF tier — 4.132, one line out of 94:

```
fastapi     df=1   idf=4.132        api        df=2   idf=3.611
docker      df=1   idf=4.132        python     df=2   idf=3.611
rest        df=1   idf=4.132        deployment df=5   idf=2.789
flask       df=0   idf=0.000        model      df=5   idf=2.789
```

Rare words now count more. It was not enough. **One rare hit still loses to
three rare hits**, and lines 78 and 79 each have three.

The old scorer put line 77 nowhere near the top 6 either. BM25 moved it from
invisible to seventh. That is progress and it is not the bar the brief set.

## The risk in section 2, confirmed — and inverted

The brief predicted length normalisation would punish the long flattened
skills rows, 73 / 77 / 79. **It did not. It punished line 77 by rewarding
everything shorter.**

```
line 73: 20 tokens     line 77: 11 tokens     line 79: 13 tokens
average line: 10.96 tokens over 94 lines
```

Line 77 is **average length**. Length normalisation is very nearly neutral on
it. The damage comes from the other side: line 76 is 7 tokens and line 78 is
4, so `b=0.75` inflates both, and line 76 — one hit on `python`, IDF 3.611 —
lands above line 77's one hit on `fastapi`, IDF 4.132.

**A short line beat a more informative word.** That is the mechanism, and the
brief called the family of it correctly even if the direction is reversed.

Retrieval counts across all 21 queries, old scorer against new:

```
line 73:  old 4   new 4
line 77:  old 1   new 1
line 79:  old 8   new 9
```

The flattened rows did not sink. Line 79 is retrieved slightly more than
before. The concentration that report 0003 flagged — half the quotes from four
lines — is not improved by this change.

## The two levers I did not pull

Both were measured. **Neither is shipped.** Both are diagnostics.

**`b=0.0`, length normalisation off:**

```
req 12 -> [79, 78, 7, 75, 66, 77]      line 77 retrieved
```

**`b=0.75`, cut widened to 8:**

```
req 12 -> [78, 79, 75, 7, 80, 76, 77, 66]    line 77 retrieved
```

The first is exactly what section 4 forbids: tuning `b` so one requirement
comes out right. The brief's own words are *if they are wrong for short lines,
say so and leave them*, so they are said and left.

The second is a `limit` change, not a scoring change, and the brief scoped this
work to the scoring. It is also not free — six lines per judgement is a prompt
budget, not an arbitrary number, and widening it changes what every requirement
sees.

**Both are decisions. Neither is mine.**

## The two runs side by side

**This is the section the brief called the point of the work, and I cannot
fill it.** There is no second run. What follows is retrieval, not verdicts.

Old scorer against BM25, all 21 queries from the real trace, replayed offline
against the same resume. `(Nt)` is the number of distinct query tokens.

```
 req        old                        new
  1 (23t)  [41, 13,  5, 49, 55, 70]   [41, 49, 70, 39, 18, 57]
  2 (22t)  [78,  7, 75, 79, 80, 76]   [78, 75,  7, 79, 80, 76]
  3 (12t)  [73, 55, 74, 71, 47, 13]   [73, 74, 55, 66, 47,  6]
  4 (32t)  [73, 35, 69,  5, 55, 85]   [73, 35, 34,  5, 69, 85]
  5 (23t)  [65, 78,  2,  4, 12, 76]   [65, 78, 76, 61,  4, 89]
  6 (23t)  [13,  7, 57, 45, 80, 75]   [57,  7, 13, 45, 80, 75]
  7 (20t)  [64, 70,  9, 39, 60, 24]   [60, 64, 82, 39, 53, 70]
  8 (28t)  [88, 11, 69, 89, 55, 39]   [88, 89, 55, 11, 69, 45]
  9 ( 6t)  [78, 76]                   [78, 76]
 10 (21t)  [73, 78, 77, 36, 74, 33]   [73, 78, 77, 74, 33, 36]
 11 (15t)  [47, 79, 73, 80, 13,  5]   [79, 47, 73, 80, 66,  6]
 12 (18t)  [78, 79,  7, 75, 80, 76]   [78, 79, 75,  7, 80, 76]
 13 ( 7t)  [79, 49]                   [79, 49]
 14 (32t)  [79, 78, 49, 31, 36, 82]   [79, 78, 49, 31, 82, 36]
 15 (23t)  [41,  8, 11, 89, 17, 55]   [41,  8, 89, 55, 11, 79]
 16 (19t)  [ 8, 17, 70, 60, 61, 86]   [ 8, 17, 70, 60, 61, 86]
 17 (27t)  [79,  7, 68, 13,  5, 14]   [79,  7, 52,  5, 68, 13]
 18 (17t)  [93,  5, 55, 14,  4, 50]   [93,  5, 14, 55, 13, 89]
 19 (17t)  [65, 14, 79, 20, 51, 13]   [79, 20, 65, 14, 66, 51]
 20 ( 6t)  [13, 36, 78,  5, 55, 65]   [36, 78, 13, 55,  5, 41]
 21 (26t)  [ 8, 79, 45, 75, 64,  5]   [79, 64, 13, 45, 75, 25]
```

**Reading it:**

- **9, 13, 16 are identical.** All three are short queries — 6, 7 and 19
  tokens. Report 0003 said short specific queries already worked. They still
  do, and BM25 does not disturb them.
- **12 is unchanged in membership.** Only the order of 75 and 7 swapped. The
  one requirement the brief was written for gained nothing that reaches the
  judge.
- **Eleven requirements changed which lines they see** — 1, 3, 5, 6, 7, 8, 11,
  17, 18, 19, 20, 21. Every one of those verdicts is now unpredictable from
  the old run.
- **Requirement 1 changed four of six.** 13, 5, 55 out; 39, 18, 57 in. The
  largest swing in the set.

## What moved, and in which direction

**NOT ESTABLISHED, for every requirement.**

A verdict comes from the model reading the retrieved lines. Without the second
run there are no new verdicts, so I cannot say a single one got better or
worse. Naming eleven requirements as *changed* is retrieval. Calling any of
them *improved* would be me guessing at the model's reasoning, which is the
exact thing this product exists not to do.

Eleven of 21 see different evidence. The brief's failure condition is *better
on one and worse on three*. **Whether that happened is unknown, and eleven
moving lines is a wide enough door for it.**

## Whether requirement 12 now finds line 77

**No.** Rank 7 of 94, 0.19 points short of the cut.

## Whether the retry fired

**NOT ESTABLISHED.** The retry fires during a run and there was no run.

Nothing in this change touches either trigger. `verify` still checks quotes by
line number, and the `evidence_weak` self-report is still the model's to set.
There is no mechanism by which BM25 would make it fire, so the honest
expectation is that it still does not — but that is reasoning, not a
measurement, and report 0003's finding stands unchanged.

## The new counts

**NOT ESTABLISHED.** `evidenced 2 / partly 16 / not 3` is still the only
distribution this project has ever measured.

## How long, and what it cost

**Zero.** No model call was made. The offline replay runs in about two seconds
and the whole of this work touched the network once, to install `rank_bm25`.

The end-to-end cost remains NOT ESTABLISHED, for the same reason report 0003
gave: nothing records token usage.

## What was run

- `uv pip install --python .venv/bin/python "rank-bm25>=0.2.2"`. Installed
  `rank-bm25==0.2.2` and `numpy==2.5.3`.
- `cp fixtures/trace-real.json fixtures/trace-before-bm25.json`, **first**,
  before any code changed.
- `pytest tests/ -q` — **38 passed**, no key, no network.
- Offline replays of `LineIndex.search` against `private/resume.txt`, using the
  21 queries recorded in the before-trace. No model call.
- `formwork check`.

**Not run: the real audit.** No key.

## The check

`formwork check` — **green**. 12 checks.

Worth repeating from report 0003, because it is truer here than it was there:
**green means the documents hang together.** It cannot tell whether a verdict
is right. The 38 tests cannot either — none of them exercises BM25 against a
document where ranking is the question. The gate is green and the brief's own
falsifiable test is red.

## Git status

Nothing staged, nothing committed.

```
 M .claude/agents/director.md
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
 M formwork/limits.md
 M formwork/roles/method/director.md
?? .gitignore
?? docs/briefs/0002-audit-frontend.md
?? docs/briefs/0003-groq-and-the-first-real-run.md
?? docs/briefs/0004-bm25-retrieval.md
?? docs/decisions/0001-audit-is-a-state-graph.md
?? docs/decisions/0002-nothing-leaves-the-machine.md
?? docs/decisions/0003-the-audit-governs-the-tailor.md
?? docs/decisions/0004-the-api-contract.md
?? docs/reports/0001-evidence-audit-core.md
?? docs/reports/0002-audit-frontend.md
?? docs/reports/0003-groq-and-the-first-real-run.md
?? fixtures/
?? pyproject.toml
?? scripts/
?? src/
?? tests/
?? web/
```

`fixtures/` is untracked as a directory; inside it, both `trace-real.json` and
the new `trace-before-bm25.json` are individually ignored. Neither can reach
the public repository. Decision `0002` holds.

## The three that matter

**Done but not asked for.**

Two things, both small.

`_bm25()`, the private helper, argued above.

**`.gitignore`.** The brief told me to copy `fixtures/trace-real.json` to
`fixtures/trace-before-bm25.json`. `trace-real.json` is ignored by name; the
copy was not, so the instruction as written created an untracked file full of
the real resume and the real post one `git add fixtures/` away from a public
repository. Section 4 says do not commit any audit output. I added the line.
If that counts as changing something to make a rule pass, it is the one place
to look.

**Asked for but not done.**

**The second real run**, and everything downstream of it — the verdict
comparison, what moved and in which direction, whether the retry fired, the new
counts. No Groq key on this machine. Nothing to estimate from, so nothing is
estimated.

**Requirement 12 retrieving line 77.** The falsifiable one. Reported as failed
rather than tuned into passing.

**Wrong in the brief.**

**Section 2's risk is real but points the other way.** Length normalisation
does not punish lines 73, 77 and 79 — 73 is unchanged at 4 retrievals, 79
gained one. It punishes line 77 by *inflating the short lines above it*. The
brief expected the long informative rows to sink and told me to say so if they
did; what actually happened is the mirror image, and it produced the same
failure.

**Section 5 assumed BM25 alone would retrieve line 77.** It does not. Rare-word
weighting is necessary and it is not sufficient — one rare term loses to three
rare terms, whatever their IDF. The change the brief specified cannot reach the
result the brief requires.

## What this leaves open

- **Requirement 12 is still wrong**, and BM25 alone will not fix it. The three
  candidate levers: `b`, the `limit` of 6, or the 22-token query itself. The
  standing brief already named the query cap as the cheapest fix with the
  largest effect, and this work is evidence for that rather than against it —
  **18 distinct tokens, 6 of them matching nothing in the resume at all**
  (`flask`, `django`, `lambda`, `ml`, `mlflow`, `tensorflow`, all IDF 0).
- **Eleven requirements now see different lines** and nobody has looked at the
  consequences. Until the run happens, this change is unvalidated on the thing
  it exists to improve.
- **No test covers ranking.** 38 tests pass and none of them would have caught
  a BM25 that ranked backwards. The suite proves `search` returns matching
  lines, never that it returns the right ones first.
- **The retry, the 76% `partly`, and the fragment quotes** are all exactly
  where report 0003 left them.

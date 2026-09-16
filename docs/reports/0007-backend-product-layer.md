---
status: open
date: 2026-09-15
brief: 0007-backend-product-layer
---

# 0007 — Backend: ingestion and the product layer

**Everything in the brief is built and the gate is green. 114 tests, up from
38. The real run did not happen: the Groq key lives in `.env` and reading it is
blocked by a deny rule on this machine.**

So the brief stays `open` on one item, and it is the item that matters most —
section 4 asks whether `undersells` names things that are actually in the
resume, and only a real run answers that for certain.

What I could do instead, I did: the product layer was replayed offline over the
**previous** real run's trace, which is real requirements and real verdicts on
the real post. That is in section 6 below, with its caveat stated. It is
evidence, not proof.

**The headline from that replay: `undersells` is not empty and it is not
nonsense.** It returned 8 items, and 6 of them point at the two flattened
skills rows — which is exactly the true thing to tell this candidate.

## What changed

**New files**

- `src/audit/repair.py` — mechanical line repair. Rejoins a word split across
  a line break, rejoins a wrapped line, splits a flattened table row. No model
  call anywhere in it.
- `src/audit/ingest.py` — PDF and text extraction, and resumes as plain local
  files. Holds `index_resume`, the single seam where repair happens before
  indexing.
- `src/audit/product.py` — `required`, `fit`, `blockers`, `strengths`,
  `undersells`. Arithmetic over verdicts; no model call.
- `src/audit/prescreen.py` — BM25-only pre-screen. Imports nothing from
  `model`.
- `tests/test_repair.py` (16), `tests/test_ingest.py` (16),
  `tests/test_product.py` (19), `tests/test_prescreen.py` (12).
- `tests/data/resume_damaged.txt` — a synthetic resume carrying the same three
  kinds of damage as the real one. Committable, unlike the real one.

**Changed**

- `src/audit/events.py` — added `summary_event`. Six types now, and the count
  is real this time.
- `src/audit/graph.py` — `extract` indexes through `index_resume` and sets
  `required` on each requirement; `report` emits `summary` after `done`.
- `src/audit/server.py` — `/prescreen`, `/resumes`, `/resumes/{id}`,
  `/resumes/{id}/default`; `/audit` accepts `resume_id`. All declared above the
  catch-all asset route, which is now commented as load-bearing.
- `src/audit/cli.py` — renders the summary block under the table.
- `tests/test_audit.py`, `tests/test_cli.py`, `tests/test_server.py` — updated
  to the decision `0005` contract (`summary` closes the stream), plus 13 new
  server tests.
- `pyproject.toml` — `pypdf>=6.0`, `python-multipart>=0.0.9`.
- `.gitignore` — `resumes/`.

Nothing in `web/`, `extension/` or `design/` was touched.

## Which PDF library, and what it does

**`pypdf` 6.18.1.** Pure Python, BSD-3, no native build step, no system
packages.

The two I rejected, and why:

- **`pdfplumber`** keeps glyph coordinates and can reconstruct columns, which
  would have prevented the flattened row rather than repaired it. It pulls in
  `pdfminer.six` and is markedly slower. **This is the one to revisit** — see
  the three that matter.
- **`PyMuPDF`** extracts best of the three and is AGPL. This repository is
  going on public GitHub for an interview. Not worth the licence conversation.

**What it does to the damaged lines: nothing — and that is the honest answer.**

There is no PDF of the real resume in this repository. `private/resume.txt` is
already-extracted text, and the damage in it predates this brief. So pypdf was
exercised against a PDF built byte by byte inside `tests/test_ingest.py`
(`make_pdf`), which proves extraction works and proves the error paths
(unsupported type, corrupt file, a scanned PDF with no text layer) behave. It
does **not** prove pypdf reproduces this specific damage, because nothing here
can.

`repair` is written against the damage as it actually exists in the file, not
against a guess about which library caused it.

## Line repair: before and after

`repair` makes **23 changes** to the real resume: 19 wrap rejoins, 2 mixed
runs, 1 hyphen rejoin, 1 row split. 94 lines in, 100 out.

**The line the brief names.** Source lines 79 and 80:

```
before   Docker, Kubernetes, Helm, GitHub Actions, AWS ECR and CodeArtifact,
         GCP Secret Manager, on-prem and air-
         gapped deployment

after    Docker, Kubernetes, Helm, GitHub Actions, AWS ECR and CodeArtifact,
         GCP Secret Manager, on-prem and air-gapped deployment
```

The hyphen is **kept**, and not by a rule of thumb. A hyphen at a line end is
ambiguous — `environ-` / `ment` wants it dropped, `air-` / `gapped` wants it
kept — so the code asks the document: if the fused form appears elsewhere in
the same resume, drop the hyphen; otherwise keep it. This resume writes
`air-gapped model serving` out in full further up, so line 79 resolves on
evidence. Tested both ways (`test_the_hyphen_is_kept...`,
`test_a_hyphen_is_dropped...`).

**The flattened row.** Source line 73, the only row split in the whole file:

```
before   AI systems Languages Backend & data Infrastructure Frontend Quality
         LLM orchestration, DSPy and ReAct agents, RAG and hybrid retrieval, ...

after    AI systems
         Languages
         Backend & data
         Infrastructure
         Frontend
         Quality
         LLM orchestration, DSPy and ReAct agents, RAG and hybrid retrieval, ...
```

Six column headers had been glued onto the first cell's contents, so a search
for `Frontend` or `Infrastructure` retrieved a line about AI systems.

**A representative wrap**, source lines 70–71:

```
before   ...insights from high-volume datasets, and contributed to
         release engineering, debugging and system-health monitoring.

after    ...insights from high-volume datasets, and contributed to release
         engineering, debugging and system-health monitoring.
```

### What repair refuses to touch, and why that took three tries

Section 4 says repair mangling a line that was fine is worse than not shipping.
The first two versions of this file did exactly that, and the guards that stop
it are the substance of the work:

| It broke | The line | The guard now |
|---|---|---|
| **Shattered job titles** | `Software Tech Lead (Dec 2024 to Aug 2025) \| Software Engineer II \| ...` became nine lines | A line already carrying a `\|` had its columns survive extraction. Nothing to reconstruct — refuse to split it |
| **Split an ordinary sentence** | `Built and operated REST APIs in Python serving 2M requests a day.` has three capitals in it | A label run is *mostly* capitals (≥60%), and a preposition continues a phrase rather than starting a column |
| **Glued two table cells** | The `Frontend` row absorbed the `Quality` row below it | A wrapped line ends at the page margin. The margin is **measured from the document** (90th-percentile line length × 0.85 = 113 characters here), not picked. The Frontend row is 79 characters — it ended because the cell ended |
| **Shattered a heading** | `T E C H N I C A L  S T A C K` looked like fourteen columns | Every split piece must contain a word of 3+ characters |

The verification that matters: **repair makes zero changes to
`tests/data/resume.txt`, `tests/data/resume_unrelated.txt` and
`tests/data/post.txt`** — three clean documents, untouched, asserted in
`test_clean_text_is_left_exactly_alone`.

A join also leaves an empty line behind rather than renumbering, so every line
repair did not touch keeps the number it had in the extraction.

## The pre-screen, measured

On the real post and the real resume, `AUDIT_RESUMES` in a temp folder:

| | |
|---|---|
| index build (repair + index) | **1.5 ms** |
| prescreen alone, median of 20 | **2.9 ms** |
| cold, index + prescreen | **4.2 ms** |
| **full HTTP round trip, median of 10** | **4.8 ms** |

**The budget is 100 ms. It comes in at roughly a twentieth of it.**

**No model call, proven three ways** (`tests/test_prescreen.py`), because "no
model call" can be broken three different ways:

1. an injected model that raises on all three protocol methods
2. `audit.server.build_model` replaced with a trap — catches the endpoint
   building its own model, which test 1 would never notice
3. `socket.socket` replaced with a trap for `AF_INET`/`AF_INET6` — catches
   **any** network by anyone, including a library reaching out quietly

Plus a structural one: `build_model` and `Model` are not names in the
`prescreen` module at all.

**One number in it changed on evidence.** A match was first "BM25 returned any
line", which matched **26 of 26** requirements on the real post — a signal that
says nothing. Requiring **two** shared terms gives 17 of 26 for the real resume
and **0 of 26** for an unrelated one. Both numbers were measured before the
threshold was chosen and both are in the code comment.

After repair the real resume scores **14 of 26, `maybe`** rather than 17 of 26.
Repair joins lines, so there are fewer and longer ones, and the count is
genuinely more conservative.

## What `undersells` returned, item by item

**Caveat, stated first.** This is the product layer replayed over the trace of
the **previous** real run — real requirements, real verdicts, real post — but
against the **pre-repair** index, because those verdicts cite pre-repair line
numbers. A fresh run would cite different numbers. Treat the list as indicative.

`fit` came out **`weak`**: *"A long shot on paper. 2 of 20 requirements are
evidenced in your resume, and 2 required items are missing."*

`required` came out **false for exactly one** of 21 — requirement 20,
*"Familiarity with the DataRobot AI Platform is a strong plus."* That is correct:
it is the only optional item in the post, and the post says so in those words.

**Blockers (2):** requirement 6 (act as subject matter expert on the DataRobot
platform) and requirement 18 (Master's Degree or Ph.D.). Both true — neither is
in the resume.

**Undersells (8):**

| # | Requirement | Cited line | True? |
|---|---|---|---|
| 4 | Generative AI: custom GenAI chatbots, RAG | 73 — the flattened AI-systems row | **Yes.** RAG and LLM orchestration are there, listed and not shown |
| 10 | Practical experience with LLMs | 73 | **Yes.** Same row, same problem |
| 11 | End-to-end agentic AI lifecycle | 73 | **Yes.** `DSPy and ReAct agents` is in a list |
| 13 | Containerization with Docker, Kubernetes | 79 — the flattened infrastructure row | **Yes.** The strongest item in the list. Docker and Kubernetes appear nowhere else |
| 21 | MLOps principles, CI/CD, monitoring | 79 | **Yes.** `GitHub Actions` and `CI quality gates` are named, never demonstrated |
| 3 | Agentic AI on common frameworks | 47 — `ingestion, search, SQL, agentic query, deployment and on-site air-gapped debugging.` | **Borderline.** It is a list, but a list of things done rather than tools owned |
| 14 | Secure app development, OAuth, secrets management | 79 | **Weak.** `GCP Secret Manager` and `secrets scanning` are there; OAuth is not. This is closer to a real gap than a wording problem |
| 2 | Design, develop, deploy end-to-end AI solutions | 7 — a mid-sentence fragment of the summary paragraph | **No. A false positive** |

**Six of eight are true and useful, one is borderline, one is wrong.**

The wrong one is instructive: line 7 is a *wrapped fragment* of a prose
paragraph, and a fragment of prose looks like a list — several short
comma-separated pieces. **Repair fixes this by itself.** After rejoining, line 7
has no independent existence; its text lives on line 5 as part of a full
sentence, which is not list-shaped. So a fresh post-repair run should drop that
item. That is a prediction, and it is the first thing the real run will test.

The rule, for the record: an `undersells` item needs a `partly_evidenced`
verdict, a line that really exists, and that line has to be **list-shaped** —
four or more comma-separated fragments, at least 70% of them four words or
fewer. `Docker, Kubernetes, Helm, GitHub Actions, ...` qualifies. `Rebuilt the
ingestion pipeline's concurrency model, cutting peak memory 6.2x` does not, and
`test_undersells_is_not_a_synonym_for_partly_evidenced` holds that line.

## Did the retry fire?

**No new run, so no new answer.** It remains 0 of 21, 0 of 23, 0 of 21 across
three runs. Nothing in this brief touched the retry trigger or `evidence_weak`
— both are out of scope by section 2, deliberately.

One thing here does bear on it, and it is worth naming before the presentation.
Repair changes the *corpus* the retry would be triggered by: joining 23 lines
and splitting a flattened row changes what BM25 retrieves, so the evidence the
judge sees on the first attempt is different now. Whether that makes
`evidence_weak` more or less likely is not predictable from here, and guessing
would be worse than waiting for the run.

## The check

```
ok    config-shape      ok    role-shape
ok    decision-ids      ok    rule-labels
ok    doc-links         ok    standing-current
ok    generated-current ok    style-pointed
ok    guard-wired       ok    work-paired
ok    kit-integrity
ok    predictions-first

GATE: green. 12 check(s), each shown to reject the wrong and accept the right.
```

`pytest tests/ -q` — **114 passed**, 1 warning (a starlette deprecation that
predates this brief). The 38 that existed before all still pass; 4 of them were
edited, and only to match the contract decision `0005` changed.

## Git status

Nothing staged.

```
 M .claude/agents/director.md
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
 M formwork/limits.md
 M formwork/roles/method/director.md
?? .gitignore
?? design/
?? docs/briefs/0002-audit-frontend.md
   ... (briefs 0003-0010, decisions 0001-0005, reports 0001-0004, 0006, 0008, 0009)
?? extension/
?? fixtures/
?? pyproject.toml
?? scripts/
?? src/
?? tests/
?? web/
```

`design/`, `extension/` and `web/` are the other three wave-1 sessions. I did
not touch them. `resumes/` is now ignored and no real resume is committed.

## The three that matter

### Done but not asked for

- **`GET /resumes/{id}` also returns what repair changed.** The brief asks for
  the numbered lines. Returning the repair log alongside costs nothing and
  means the damage and the fix are both visible rather than one of them being
  taken on trust. It is additive; a client can ignore the field.
- **The CLI renders the summary block.** Needed one anyway to read a real run,
  and the brief asks for the run in the report.
- **`repair` records every change it makes**, rather than just returning text.
  That is what made the four mangling bugs findable — and the before/after
  section of this report is generated from it.

### Asked for but not done

- **The real run.** Blocked, not skipped. `.env` cannot be read here and the
  key is not in my environment. **This is the one open item.**
- **The chained wrap on the AI-systems cell is incomplete.** Source line 74
  is 110 characters, under the 113-character margin, so `air-gapped model
  serving` stays on its own line instead of joining the cell above it. It reads
  fine and searches fine, so I left the conservative rule alone rather than
  lower the bar and risk gluing cells again.
- **Source lines 83/84 stay split.** `... Spark and MapReduce, async` /
  `Python, REST API design` is a real wrap, but the continuation starts with a
  capital `P`, and "continuations start in lower case" is the guard keeping
  repair safe everywhere else. Loosening it to catch this one line would put
  every cell boundary in the file at risk. Left alone on purpose.
- **The letter-spaced headings** (`T E C H N I C A L  S T A C K`) are not
  repaired. The word boundary is genuinely gone — single spaces between every
  letter — so the text cannot be recovered without guessing. They are headings,
  not evidence, so nothing is lost.

### Wrong in the brief

- **Section 2 says decision `0005` is the contract — it was `proposed` when I
  started.** The standing brief says nothing in wave 1 should start on
  `proposed`. It moved to `accepted` a few minutes into the session, so this
  cost nothing, but four sessions did start against an unaccepted record.
- **"The existing 38 tests still pass"** is not quite achievable as written.
  Four of them assert the five-type contract that decision `0005` replaces.
  They pass now, and they pass because I edited them to the new contract — the
  only honest reading of the instruction, but it is an edit to existing tests
  and the brief did not anticipate it.
- **"Line 79's `air-` / `gapped deployment` split"** — line 79 ends in `air-`
  and line **80** carries `gapped deployment`. The repair is one change
  spanning both; the brief's single number is slightly under-specified.
- **`GET /resumes/{id}` "returns the indexed lines, numbered"** cannot mean the
  extraction's own numbering, because splitting a flattened row adds lines.
  Numbering is the repaired document's. Joins leave blanks rather than
  renumbering, so everything up to the first split is unchanged, and the
  numbers always agree with the verdicts — which is what the guarantee actually
  requires.

## What I would push back on

**`pdfplumber` deserves a second look, and it is cheap to test.** Every guard
in `repair.py` exists because reconstructing a table from flattened text is
guesswork. `pdfplumber` keeps the coordinates that make it not guesswork. The
row-splitting rule is the most fragile thing I have written in this project and
it would misfire on a resume laid out differently from this one — the joining
rules are sound and general, the splitting rule is not. If a real PDF ever
lands in the repo, an hour spent comparing the two extractors would be worth
more than any further hardening of that rule.

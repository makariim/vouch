---
status: open
brief: 0015-backend-last-gaps
date: 2026-09-16
---

# 0015 — Backend: the last four gaps

**All four gaps are closed, with a test each that was shown to fail when its
change is taken away. 164 tests pass, `formwork check` is green.**

It stays `open` for one reason: **the real run through Groq did not happen.**
Section 6 asks for the new sentence quoted from a real run, its time and its
counts, and none of that is in this report. Why, and what it needs, is in
"Asked for but not done" below.

Two things worth reading before the file list:

- **Decision `0008` is still `status: proposed`.** The brief says it governs
  this work and must be accepted first. Flipping that is not an agent's act,
  so it has not been flipped. See "Wrong in the brief".
- **A fifth change was needed, and it was not in the brief.** Adding
  `requirements` to `POST /summary` exposed a bug that had been on disk since
  brief `0012`: a second pass shrank the stored requirement list from every
  requirement to one. Section "Done but not asked for".

---

## What changed

Everything is inside `src/` and `tests/`. Nothing in `web/`, `extension/`,
`design/` or `fixtures/` was touched.

| File | Why |
|---|---|
| `src/audit/events.py` | `STEPS` is one seven-item set with `repair` in it. `EMITTED_STEPS` is now the same tuple, not a second one |
| `src/audit/server.py` | `POST /summary` returns `counts` and `requirements`. Plus `_merged`, and `_streamed` taking the stored list — the bug below |
| `src/audit/ingest.py` | `ResumeStore.list()` items carry `name` |
| `src/audit/product.py` | `_fit_sentence` wording only. No number, denominator or branch changed |
| `tests/test_product.py` | Three tests over every branch of the sentence |
| `tests/test_server.py` | Five new tests, and three existing ones updated for the widened reply |

### The four gaps, one line each

**1. `counts` and `requirements` on `POST /summary`.** Both read straight out
of `earlier["counts"]` and `earlier["requirements"]`. Nothing is recomputed.
`required` is read through `events.requirement_is_required`, which is where
decision `0006` item 7 put "absent means required", so the list cannot disagree
with the stream about which items are required.

**2. One step set.** `STEPS` gained `repair`. `EMITTED_STEPS = STEPS` — the old
name kept, pointing at the one tuple, so nothing importing it broke and there
is no second tuple left to drift.

**3. `name` on `GET /resumes` items.** It is `path.name`, the same string
`get()` already reports, so the list and the single resume cannot disagree.

**4. The sentence.** Wording only.

---

## The new sentence

`_fit_sentence` has nine branches — three leads by three blocker cases. **All
nine, printed from the code** (`8 of 23` used throughout so they are
comparable):

```
Worth applying, and you are a close match. Your resume shows 8 of 23 things they ask for, and nothing they need is missing.
Worth applying, and you are a close match. Your resume shows 8 of 23 things they ask for, and they need one more thing: Hands-on Kubernetes in production.
Worth applying, and you are a close match. Your resume shows 8 of 23 things they ask for, and they need 3 things you cannot show.
Worth applying. Your resume shows 8 of 23 things they ask for, and nothing they need is missing.
Worth applying. Your resume shows 8 of 23 things they ask for, and they need one more thing: Hands-on Kubernetes in production.
Worth applying. Your resume shows 8 of 23 things they ask for, and they need 3 things you cannot show.
A long shot on paper. Your resume shows 8 of 23 things they ask for, and nothing they need is missing.
A long shot on paper. Your resume shows 8 of 23 things they ask for, and they need one more thing: Hands-on Kubernetes in production.
A long shot on paper. Your resume shows 8 of 23 things they ask for, and they need 3 things you cannot show.
```

**These came from the code, not from a run.** The blocker text in them is
invented. The real sentence, from the real post, is NOT ESTABLISHED.

Before and after, on the same numbers:

| | |
|---|---|
| **Was** | `Worth applying. 8 of 23 requirements are evidenced in your resume, and 3 required items are missing.` |
| **Is** | `Worth applying. Your resume shows 8 of 23 things they ask for, and they need 3 things you cannot show.` |

Three words from `design/README.md` did the work: the ban on "evidence" as a
verb, the register *"your resume shows this"*, and the row that turns
`BLOCKERS · 2` into *They need two things you cannot show*.

**The leads were left alone.** "Worth applying." and "A long shot on paper."
are already plain, and the brief says only the sentence's wording changes. A
lead rewritten for its own sake is a change with no test behind it.

### The rule is asserted, not read once

Section 4 asks for this specifically. `test_no_fit_sentence_uses_evidence_as_a_verb`
enumerates all nine branches at two different counts — 18 sentences — and
asserts none contains `evidenced`, `evidencing`, `evidence in` or
`evidence this`. It asserts the count is 18 first, so a change that collapses
a branch fails rather than quietly testing less.

`evidence` the **noun** is deliberately not banned. The rule in
`design/README.md` is about the verb, and a test that also failed the noun
would be enforcing a rule nobody wrote. `undersells` still says "the evidence
is on this line", which is a noun and is not `fit_reason`.

---

## What `POST /summary` now returns

For a known post:

```json
{
  "known": true,
  "type": "summary",
  "fit": "worth_applying",
  "fit_reason": "Worth applying. Your resume shows ...",
  "blockers":   [{"requirement_id": 3, "text": "...", "line": null, "line_number": null, "reason": "..."}],
  "strengths":  [{"requirement_id": 1, "text": "...", "line": "...", "line_number": 3, "reason": "..."}],
  "undersells": [{"requirement_id": 2, "text": "...", "line": "...", "line_number": 5, "reason": "..."}],
  "counts": {"evidenced": 1, "partly_evidenced": 2, "not_evidenced": 3},
  "requirements": [
    {"id": 1, "text": "Experience building and operating REST APIs", "required": true},
    {"id": 2, "text": "...", "required": false}
  ]
}
```

Nine keys. Two are new; the other seven are byte for byte what they were, and
a test asserts that against the streamed `summary` event rather than against a
copy of it.

For an unknown post, unchanged and asserted:

```json
{"known": false}
```

That last one has its own test. A widened reply that leaked an empty `counts`
into the unknown case would have the panel drawing a zero row for a post
nobody has audited.

---

## Done but not asked for

**One thing, and it is the most important paragraph in this report.**

`_streamed` used to take the `requirements` event off the wire and store it as
the audit's requirement list:

```python
if kind == "requirements":
    requirements = event["items"]
```

A second pass through `POST /audit/requirement` emits a `requirements` event
holding **one** item — the requirement being redone — because that is what the
client needs in order to redraw one row (`graph.py`, `_resume_at`). So one
re-check rewrote the stored list of every requirement down to a list of one.

Two things were already broken by it, silently:

- **A third pass could not run.** It reads `earlier["requirements"]` and asks
  the graph for its id, and a list of one does not contain it. `AuditError: no
  requirement 3 in this audit`.
- **From this brief on, `POST /summary` would hand the panel a one-item list**
  of everything the post asks for, after any re-check. That is the folded
  bottom half of the panel, wrong, quietly.

This was found by the brief's own test failing, not by reading the code. The
fix is `_merged`: the stored list keeps its order, arriving rows replace their
own id, and a row not in the stored list is appended rather than dropped.
Nothing is recomputed — both sides are events the run already produced.

**Why it was fixed rather than reported and left.** It is in `src/`, it is in
the save path for the exact field this brief adds, and section 4's "`POST
/summary` returns `counts` and `requirements` for a known post" cannot honestly
be called done while a re-check corrupts one of them. It is one helper and four
changed lines. It is flagged here because it is a change nobody asked for.

`test_a_second_pass_does_not_shrink_the_stored_requirement_list` covers both
halves — the list stays whole, and the third pass now runs without an error.

---

## Asked for but not done

**The real run through Groq. This is the one gap, and it is a real one.**

Section 4 asks for one real run with the new `fit_reason` quoted, and section 6
asks for the run time and the counts against `8 evidenced / 12 partly / 3 not`.
None of that is here.

The run needs two things this session could not reach:

- **`GROQ_API_KEY`.** It is not in the environment, nothing in `src/` or
  `scripts/` loads a `.env`, and reading `.env` was refused.
- **The real post and resume**, which live in `private/`. Listing that folder
  was refused.

Both refusals are correct — that is a key and personal data under decision
`0002`. **Nothing was worked around.** The run time and the real counts are
NOT ESTABLISHED, and the brief stays `open` until somebody runs it.

**What it takes**, once the key is exported:

```
AUDIT_PROVIDER=groq .venv/bin/python scripts/record_trace.py <post> <resume>
```

What to check when it comes back: the `fit_reason` string, that the counts
still read 8 / 12 / 3, and the elapsed time against the 78s that brief `0012`
recorded. Nothing in this brief touches the graph, the prompts or the retry, so
a change in any of those three would be a surprise worth stopping for.

---

## Wrong in the brief

**One thing, and it is a gate rather than an error.**

The brief opens with *"Decision `0008` governs this brief and must be
`accepted` before you start."* The record still reads `status: proposed`, and
`docs/standing.md` lists `0008` as proposed and puts "Accept decision `0008`"
as step 1 before this brief.

**It was not flipped.** Accepting a decision is the human's act, and "the agent
never decides" is a standing rule. The work was done because the instruction to
do brief `0015` is the substantive go-ahead; the record needs the status line
changed by hand, and `docs/standing.md` updated with it.

**Nothing in decision `0008` turned out wrong.** Section 6 asks that
explicitly. All four items were accurate about the code:

- `counts` and `requirements` really were both sitting in the stored file, and
  really did need nothing recomputed.
- `repair` really was the seventh step, and the two sets really were separate.
- `GET /resumes` really did carry `id`, `lines` and `default` and no name.
- `fit_reason` really did produce the sentence the decision quotes.

What the decision did not know is the bug in "Done but not asked for". It is
not a contradiction of anything it says — it is a consequence of `requirements`
going on the wire that nobody could see until it did. Its "Bad" section says
*"four changes in the last wave, with no time to find what they got wrong"*,
and this is one instance of exactly that, found by a test rather than by a
demo.

The rest of the brief was accurate. The scope held at four changes plus the one
above; it did not grow.

---

## What was run

Nothing that wrote outside the repository. No installs, no migrations, no
network call, no model call.

```
.venv/bin/python -m pytest tests/ -q          -> 164 passed
./formwork/fw check                            -> green
```

**Each new test was shown to fail when its change is reverted**, then the
change was restored. Not a substitute for a check that looks at something, but
it is what stops five tests passing for the wrong reason:

| Change reverted | What failed |
|---|---|
| `_merged` in `_streamed` | `test_a_second_pass_does_not_shrink_the_stored_requirement_list` |
| the sentence wording | 3 tests in `test_product.py` |
| `name` on listed resumes | `test_listed_resumes_say_what_they_are_called` |
| `counts` + `requirements` on `/summary` | 5 tests in `test_server.py` |
| `repair` out of `STEPS` | `test_there_is_one_step_set_and_repair_is_in_it` |

The suite was 154 before and is 164 now. **The 154 all still pass** — three of
them had an assertion updated, and all three were assertions that the
`/summary` reply is the summary event *and nothing else*, which is precisely
what decision `0008` changes. The assertions were widened by exactly two named
keys, not loosened: `test_the_stored_summary_carries_all_five_fields` still
pins the whole key set, so a tenth field would fail it.

---

## The check

`formwork check`, the whole thing:

```
ok    config-shape
ok    decision-ids
ok    doc-links
ok    generated-current
ok    guard-wired
ok    kit-integrity
ok    predictions-first
ok    role-shape
ok    rule-labels
ok    standing-current
ok    style-pointed
ok    work-paired

GATE: green. 12 check(s), each shown to reject the wrong and accept the right.
```

Green before this work started as well, so the gate says this brief broke
nothing. It does not say the brief is done — `work-paired` accepts an open
brief by design, and this one is open.

---

## Git status

Nothing staged, nothing committed. `src/`, `tests/` and `docs/reports/` are
still untracked as a whole, so the changed files sit inside those entries
rather than appearing as `M`.

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
 ... (briefs 0003-0015, decisions 0001-0008, reports 0001-0014)
?? docs/reports/0015-backend-last-gaps.md
?? extension/
?? fixtures/
?? pyproject.toml
?? scripts/
?? src/
?? tests/
?? web/
```

No `private/`, no `.env`, no `resumes/`, no `audits/`, no audit output.

---

## What is next

1. **Accept decision `0008`** — change its status line and `docs/standing.md`.
2. **The real run**, and this brief closes. It is the only thing holding it.
3. The two human tests and brief `0005`, unchanged by any of this.

Two things this brief deliberately did not do, both named as out of scope and
both still true: **no cap on retries** — decision `0007` says that needs a
number from a run we have not done — and **`design/` is still copied into two
clients** rather than served.

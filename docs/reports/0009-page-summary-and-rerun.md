---
status: open
date: 2026-09-15
brief: 0009-page-summary-and-rerun
---

# 0009 — Page: the summary, and re-running one requirement

**Both are in, and both have been run against the real backend.**

Brief `0007` landed the `summary` event and `required` while this was being
built, so the "fixture only" answer the brief expected is not the answer. The
page was driven against the real `/audit` endpoint, and the summary it renders
came off that stream.

**The one done-when item I cannot close is the two-metre test.** It needs a
person standing across a room, and I am not one. I watched it full size on a
screen, which is a weaker thing, and I say what I saw below rather than
claiming the test passed.

## What changed

Everything is inside `web/`. Nothing in `src/`, `tests/`, `fixtures/`,
`extension/` or `design/` was touched — read only, and only to see what the
real stream carries.

- `web/app.js` — the summary block, required-vs-preferred, and re-running one
  requirement. `renderSummary` is new, `renderVerdict` now replaces rather than
  appends, and the live reader was split into a general `stream(url, body)` so
  the re-run can use the same SSE parsing as `/audit`.
- `web/styles.css` — layout for the summary panels, the two passes over one
  requirement, the required/preferred tags and the re-run button. **No new
  colour and no new font.** Every value is one of the eleven variables already
  at the top of that file.
- `web/index.html` — a fixture picker in the controls row, so the empty case
  can be shown without editing a file.
- `web/fixtures/trace-summary.json` — the recorded run plus what decision
  `0005` adds: `required` on each item, and a `summary` event.
- `web/fixtures/trace-clean.json` — the empty case. Strong fit, no blockers, no
  undersells, and one *preferred* item that is missing and must not appear as a
  blocker.
- `web/fixtures/rerun.json` — the second pass over one requirement, keyed by
  requirement id.

**The fixtures are in `web/fixtures/`, not `fixtures/`.** The standing brief
gives `fixtures/` to brief `0007` alone. Two sessions collided there last time;
this folder cannot collide with anything.

## What was run

Nothing that wrote outside the repository. No install, no migration, no
network.

- `python3 -m http.server 8778` — the repository root, to serve the page.
- The real backend, offline, with the scripted model from `src/audit/testing.py`
  instead of Groq: `create_app(ScriptedModel(...))` on port 8779. **No key, no
  model call, no cost.** The script for it lives in the scratchpad, not here.
- Two Playwright drivers, also in the scratchpad, in real Chrome:
  **34 assertions against the fixtures, 10 against the live backend. All pass.**
  Screenshots of all eight states were taken and read.

Neither driver is committed. They are throwaway evidence, and a browser test
suite is not something this brief asked for.

## The check

`formwork check` — **green.** All 12 checks.

```
ok    config-shape        ok    role-shape
ok    decision-ids        ok    rule-labels
ok    doc-links           ok    standing-current
ok    generated-current   ok    style-pointed
ok    guard-wired         ok    work-paired
ok    kit-integrity
ok    predictions-first

GATE: green. 12 check(s), each shown to reject the wrong and accept the right.
```

**The gate cannot see a web page.** It says nothing about anything in this
report except that the repository is still in order.

## Git status

Nothing staged, nothing committed.

```
?? web/
```

`web/` has never been committed, so the whole folder is still untracked. The
rest of the working tree is the other three wave-1 sessions and the director.

## The summary block, state by state

**With a real problem** (`trace-summary.json`, and the shape of a real run):

1. **Worth applying**, large, over one sentence of reason. Amber.
2. The three counts, unchanged from before.
3. **Blockers** — two lines, bold, on red. Required and missing, nothing else.
4. **Where your resume undersells you** — the largest block on the page.
   Three entries, each: the requirement, the resume line quoted in monospace
   with its line number, then why the wording is weak.
5. **Strongest cards** — three, requirement and quoted line.

**Nothing to fix** (`trace-clean.json`): *Strong fit* in green, and the two
empty panels say something rather than sitting blank:

- Blockers: "None. Every required item has a line behind it."
- Undersells: "Nothing. Where the evidence is there, the resume says so plainly."

**Nothing good either** (the live run against the real backend): *Weak fit*,
two blockers, no undersells, and **Strongest cards reading "None called out."**
A green panel saying nothing is the worst-looking state on the page. It is
honest, and brief `0006` should decide whether an empty strengths panel should
render at all.

**No summary at all** (`trace-sample.json`, the original recording): the page
renders exactly what it rendered before. Counts, no panels, no tags. Verified,
not assumed.

## Re-running one requirement, as it appears

Pressing **↻ Re-run** on requirement 3:

1. The verdict word `– PARTLY` greys out and is struck through. It stays there.
2. The steps already on the row get the label **FIRST PASS** and fade to half
   opacity. **They do not disappear** — that is what makes the new search terms
   visibly different rather than a claim in the narration.
3. A new strip opens under them, labelled **RE-RUN**, set in behind a blue rule.
4. New search: "agent framework named LangGraph state machine". Different from
   both terms of the first pass.
5. **The amber retry block**, full width, the same one the fixture already had:
   "the skills list has no framework in it — searching the projects section
   instead".
6. A second new search, a verify, then the new verdict **✓ EVIDENCED** replaces
   the struck-through one, with a new quoted line.
7. The counts move **6/3/3 → 7/2/3**.
8. A line appears under the summary: *"Counts updated after re-running
   requirement 3. The call, the blockers and the undersells above are from the
   first run — they are the backend's judgement, and this page does not
   recalculate them."*

**A re-run that changes nothing** works too — requirement 11 searches twice,
retries, and comes back `not_evidenced` with "still nothing. The resume does not
answer this one, and a second pass cannot invent it."

**If the same terms were ever searched twice**, the chip says so in red, on the
chip. It has never fired. It is there because a second pass that searches for
the same thing is not a second pass, and I would rather see that than not.

**Against the live backend the button fails honestly**: there is no endpoint
(see below), so the banner reads "The backend answered 405 Method Not Allowed
for /audit/requirement." and the row keeps the verdict it had.

## What decision 0005 got wrong, or left out

**Reported, not fixed. Three sessions are building against this record.**

1. **There is no re-run endpoint in it.** `0005` adds `/prescreen` and four
   `/resumes` routes, and nothing for re-auditing one requirement — which is
   half of what brief `0009` exists to build. The page assumes
   `POST /audit/requirement {post, resume|resume_id, requirement_id}` returning
   the same event stream, and `RERUN_ENDPOINT` at the top of `app.js` is the one
   line to change. **This needs a decision, and it is not mine.**

2. **Nothing says what a re-run re-emits.** If it sends a fresh `summary`, the
   page renders it and everything is consistent. If it does not, the counts are
   stale the moment a verdict changes. The page tallies the counts itself —
   that is arithmetic over verdicts it has already been given, not judgement —
   and says in plain words that the fit, the blockers and the undersells above
   are from the first run. **It never recomputes the judgement.** But the
   contract should say which of the two happens.

3. **`undersells` and `strengths` carry a `line_number` and no line.** The page
   can only quote because the same requirement's `verdict` event carried the
   line earlier. That join works, and it breaks after a re-run: a stale summary
   points at a line number the row no longer has as evidence. Either the summary
   carries the text, or a re-run re-emits the summary.

4. **Three shapes for the same join.** `blockers` carries `text`,
   `strengths` carries `line_number`, `undersells` carries both plus `reason`.
   The page handles all three. One shape would be less to get wrong.

5. **`required` has no stated default.** The old recording has no such field.
   The page treats absent as required and renders no tag at all, which is the
   safe reading but is an assumption, not a rule.

6. **Two denominators on one screen.** The live backend's `fit_reason` reads
   "0 of 3 requirements are evidenced" while the counts row next to it totals 4.
   It is counting hard requirements only. Both numbers are defensible and
   together they look like a bug. That is `0007`'s wording, but the contract
   does not say which denominator `fit_reason` uses.

7. **A step type nobody wrote down.** The real stream carries `step: "judge"`.
   `0004` and `0005` count event *types* but never enumerate step *values*. The
   page renders it with the default chip and does not guess — no break, worth
   knowing.

## Run against the real backend

**Yes.** `create_app(ScriptedModel())` on port 8779, serving `web/` at `/`, with
the real `/audit` endpoint and the real graph. No key, no network.

What matched: `required` on every item, and the backend marked "A doctorate is a
plus" as **preferred** by itself. The `summary` event arrived with the fields
`0005` promised and rendered without a change to the page.

What did not: item 6 above, and the missing re-run endpoint.

**This is not the same as a Groq run.** `ScriptedModel` is a test double —
extraction is "every line starting with a dash". The event *shapes* are real;
the judgement in them is not. The first real-model run through this page has
still not happened.

## What is left awkward for brief 0006

- **Every colour is a variable, except three that were already there.**
  `.step`, `.evidence` and `button.run` use a bare `#fff`, from before this
  brief. I did not touch them. They are the three places tokens will not reach.
- **The hooks:** `.fit` and `.fit-strong|worth_applying|weak`, `.panel` and
  `.panel.blockers|undersells|strengths`, `.counts`/`.count`,
  `.tag.required|preferred`, `.pass`/`.pass-label`/`.pass.past`,
  `button.rerun`, `.stale-note`, `.step.same-terms`, `.verdict.stale`.
- **One palette is doing four jobs.** Green/amber/red means the verdict on a
  row, the count card, the fit call, *and* the panel kind. If the fit call
  should have its own colour, `.fit-*` has to be pulled off the verdict
  variables first.
- **The summary is five full-width blocks stacked.** At 1100px it pushes the
  requirement list well below the fold. Two columns — call and counts beside
  blockers and undersells — is the obvious move and is a design decision, not
  mine.
- **Preferred is marked with a dashed border and a pill, required with quiet
  small caps.** The exception is marked and the normal case is nearly silent.
  That was a judgement about clutter with ten required rows on screen, and it
  is the first thing to overrule if it reads as an oversight.
- **An empty Strongest cards panel** renders as a green box saying "None called
  out." It looks wrong even though it is right.

## The three that matter

**Done but not asked for.**

- **A fixture picker in the page.** The brief wants the empty case shown, and
  the only alternative was editing a file mid-demo. Three options, one select.
  It dims itself in live mode.
- **The counts are tallied by the page after a re-run.** The brief forbids
  computing the *summary* in JavaScript and I have not: fit, blockers,
  undersells and strengths are rendered exactly as they arrive and are never
  recalculated. Counting verdicts already on screen is arithmetic, it is the
  only way the counts can move when a verdict does, and the page says out loud
  that the judgement above it is now behind.
- **The "same terms as last time" warning.** Small, never fired, and the
  cheapest way to stop the brief's own requirement from silently rotting.
- **Running the real backend offline with the scripted model.** The brief said
  do not wait for the backend. It had already landed, so waiting was not the
  question.

**Asked for but not done.**

- **The two-metre test.** It is the brief's own falsifier and it needs a human.
  Unrun.
- **A run through the real model.** There is no Groq key on this machine.
  `ScriptedModel` gives real event shapes and fake judgement.

**Wrong in the brief.**

- **"Do not wait for the backend. Build against a hand-written fixture."**
  Brief `0007` landed `summary` and `required` before this finished. Both were
  done: the fixtures exist and the live path is verified.
- **"the new `summary` event in decision `0005`"** implies `0005` covers this
  brief's second half. It does not — there is no re-run endpoint in it. That is
  the largest gap in this report.
- **"the amber block the fixture already has"** — the fixture in `fixtures/`
  has amber retries, but that folder belongs to `0007`. The amber block is in
  `web/styles.css`, which is mine, and the re-run fixture in `web/fixtures/`
  produces one on demand.

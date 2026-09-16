---
status: open
date: 2026-09-15
brief: 0013-page-wave-two
---

# 0013 — The page: apply the design, close the gaps

**The design is applied, both gaps are closed, and both of them have been run
against the real backend.**

The brief expected `/audit/requirement` not to exist yet. It does — brief `0012`
landed it while this was being built — so the answer is not "recording only".
The second look was driven against the real endpoint, and it re-emits `summary`
exactly as decision `0006` promised.

**The one done-when item I cannot close is the two-metre test.** It needs a
person standing across a room. I checked it in greyscale, which is the half of
that test a machine can do, and I say below what I saw rather than claiming the
test passed.

## The value `tokens.css` did not have

The brief calls this the most useful thing in the report, so it goes first.

**`tokens.css` has no page-level sans role at 13px.** I checked every literal in
`design/canvas/Web.dc.html` against the file mechanically:

- **46 colour literals, all 46 covered.** The one apparent miss is
  `oklch(0.250 0.008 250 / 0)`, which is `--v-bg-2` at zero alpha inside a
  fade-out gradient. Derived, not missing. **Colour coverage is real.**
- **Every font size has a token.** But 13px has only two, and neither fits the
  page: `--v-text-quote`, which its own comment reserves for mono, and
  `--v-text-p-note`, which is the panel's cut.

**The board itself sets 13px sans text in eighteen places** — the header note,
the rail's sub-lines, every quote caption, the run button's meta, the trace
lines. The panel has `--v-text-p-note` for exactly this. The page has nothing.

I did not invent a number. `web/styles.css` declares one alias,
`--page-note: var(--v-text-p-note)`, commented as the gap it is, so the value
still has a single source. **If design adds `--v-text-page-note`, that one line
is the only thing that changes.**

Two smaller things, reported rather than acted on:

- **The board's own gaps are off the space scale.** `18px`, `26px` and `32px`
  gaps between things, where section 7 says the scale governs gaps between
  things. Component padding is explicitly excused by that same section; these
  are not padding. I followed the board and used scale tokens for the section
  rhythm, which lands on `--v-s-7` exactly.
- **The board breaks the accessibility rule it ships with.** The header's tab
  buttons are about 26px tall against `--v-tap-min: 44px`. I matched the board
  for the header strip, which carries only demo controls, and held 44px on
  every control that is part of the product.

## Two things this could not have found on its own

**The design's own import line cannot work on the demo path.**
`design/README.md` says to import `"../design/tokens.css"`. That resolves when
the repository root is served. It cannot resolve when the backend serves the
page, because `GET /{asset:path}` in `src/audit/server.py` refuses anything
above `web/` — and the backend is what listens on port 8000, which is where the
extension sends people. I confirmed it:

```
404 ../design/tokens.css from the backend
{"error":"not found"}   /design/tokens.css
```

So the page would have been served **with no tokens at all** on exactly the path
the demo uses.

**What I did:** `web/tokens.css` is a byte-for-byte copy of `design/tokens.css`
with a header saying so and how to refresh it. Verified verbatim with `diff`.
`design/` was not touched.

**This needs somebody's decision, and it is not mine.** Either the backend
serves `design/` too — one line, brief `0012`'s file — or the copy stays and
something has to notice when it drifts. Today nothing would.

**The backend's `fit_reason` breaks the plain-English rules.** A real run put
this in the largest sentence on the page:

> A long shot on paper. 0 of 4 requirements are **evidenced** in your resume,
> and one required item is missing.

`design/README.md` says never use "evidence" as a verb. The page renders
`fit_reason` verbatim and must — rewriting the backend's judgement here is
exactly the thing this page is not allowed to do. **The fix belongs in `src/`,
which I do not own.**

## What changed

Everything is inside `web/`. Nothing in `src/`, `tests/`, `fixtures/`,
`extension/` or `design/` was touched — read only, and only to see what the
real stream carries and what the boards look like.

- `web/index.html` — rebuilt to the board: a sticky header with the mark, a
  332px left rail to set the run up, and the answer column. The demo controls
  moved into the header's control slot. The favicon is inline as a data URI,
  because a `<link>` to a file is a fetch and a missing one is a 404 per load.
- `web/styles.css` — rewritten. **No colour literal, no font stack.** Every
  colour, type step and radius is a variable. The three bare `#fff` values
  brief `0009` flagged are gone with the rules that held them.
- `web/tokens.css` — new. The verbatim copy described above.
- `web/app.js` — the phase model, the trace in sentences, `#post=`, the
  collapsed working, and the copy rewrite.
- `web/fixtures/trace-summary.json`, `trace-clean.json` — the three summary
  lists rebuilt to decision `0006`'s five fields. The page no longer joins
  against verdict events to get the words, so the recordings had to carry them.
- `web/fixtures/rerun.json` — one reason line reworded off "evidenced".

### The two gaps

**`#post=` is read.** The fragment fills the job post box, then is cleared from
the URL so a refresh cannot silently paste it back over something typed since.
Driven against the backend-served page: the box filled exactly, and **no
request carried the post text**, which is the whole reason decision `0006` chose
a fragment.

**`RERUN_ENDPOINT` was already `/audit/requirement`.** Brief `0009` guessed the
shape and said so; decision `0006` then named the same thing. The line did not
change. Its comment did — it now cites `0006` instead of apologising for a
guess. The recording path still works, and I kept it working on purpose.

### One real bug the live run found

`POST /audit/requirement` opens with its own `requirements` event naming the one
requirement it is re-checking. `renderRequirements` treated that as a new list
and **drew a fifth row for a requirement already on screen**, clobbering the
first row's handles and throwing on the next verdict. The header read
"Stopped at 4 of 5".

It is now idempotent per id: an id already drawn lands in the row that is
already there. Only the opening list writes the "4 things they ask for" strip,
so a single-requirement re-check cannot rewrite it to "1 thing they ask for".

**A recording would never have caught this.** It only exists because the real
endpoint landed early.

## The two things `0009` left for a designer

**The empty Strongest cards panel is gone, along with all the panels.** The
design does not have coloured boxes at this level — it has a heading, a lead
sentence, and quote blocks with a coloured left edge. So an empty section is a
heading and one plain line, on the page ground. No green box saying nothing.

The gap section goes further and changes its own heading: *They need two things
you cannot show* becomes **You can show everything they need** when the list is
empty. That is the strongest true thing to say, and it says it in the position
where the bad news would have been.

**The five full-width blocks are fixed by the layout, not by two columns.** The
board splits setting-the-run-up into a left rail and puts the answer on the
right, and it puts the requirement list at level three, **collapsed**. The list
is no longer above anything. It opens by itself while the run is going, because
that minute is the interesting part, and folds away when the run finishes.
Once a person opens or closes it themselves, their choice wins.

## What the page looks like, stage by stage

**Nothing loaded.** One slab sentence about what the tool does, then the three
answers with their marks and one line each, then the line about fit being a
word and not a score. The rail shows two empty wells.

**Working.** A rose callout at the top: "Working", the seconds ticking, "2 of 12
done", and the requirement being looked at in slab. Under it the list is open,
finished rows carrying their answer and their quoted line, the row in hand
washed rose with its mark breathing and empty, and the rest waiting in grey
brackets. The run button has become **Stop**.

**It changes its mind.** The callout switches to "It changed its mind" and the
row prints, in rose, at full strength: *It threw away its own answer and is
searching again: only a tools list matched, no framework named.* Then the new
search terms underneath it. **You can read it happening from across the room.**

**Finished.** The call in 38px slab — *Worth applying.* — one sentence, then
three counts with their marks. Then the three sections. Then a rule, and
"Everything they asked for · 12 of 12 checked", folded.

**Looking again at one.** Every other row drops to half opacity, the answer
above dims, and the one row runs its trace. Against the real backend the answer
then rewrites itself, because the endpoint re-emits `summary`. On a recording
there is no new summary, so the page says so instead of quietly lying.

**It broke.** A red callout: where it stopped, one slab line, then *The two
answers already on screen are finished. They will not change. Nothing was
guessed to fill the gap.* The detail in its own block, and one way out.

**A trace is only kept after the fact on a row where it changed its mind**, and
then the rose comes out of it — the README says the rose leaves the screen when
the run ends. Everywhere else the trace is removed once the answer lands. This
is a judgement I made: the boards draw the trace only while working, and a
change of mind that vanishes is the one thing this product most wants to show.

## What the plain-English pass changed

It changed more than the colours did. Three of them:

| Before | After |
|---|---|
| `BLOCKERS` · a red box | **They need two things you cannot show** |
| `Where your resume undersells you` | **Fix these lines in your resume** |
| `✓ EVIDENCED` | **Your resume shows this** |

And three more that matter as much:

- `↻ Re-run` → **Look again at this one**. Decision `0007`: a person asking for
  a second pass is not the agent deciding. **The word "retry" is nowhere in the
  page** — the drive asserts it.
- `resume line 11` → **Line 11, word for word**. The caption now says what the
  block is for, not what it is.
- `Auditing…` → **Stop**, with the seconds counting beside it. The old label
  named a state. This one says what the button does.

The steps became sentences. `search · langchain langgraph crewai` now reads
*It searched your resume for: LangChain LangGraph CrewAI.* Same data, and
nothing to decode.

## What was run

Nothing that wrote outside the repository. No install, no migration, no
network call.

- `python3 -m http.server 8778` at the repository root, to serve the page.
- The **real backend**, offline, with the scripted model from
  `src/audit/testing.py` in place of Groq, on port 8779. **No key, no model
  call, no cost.** The launcher lives in the scratchpad, not here.
- Two Playwright drivers in real Chrome, also in the scratchpad:
  **42 assertions against the recordings, 12 against the real backend. All 54
  pass.** Screenshots of every state were taken and read.

Neither driver is committed. They are throwaway evidence, and a browser test
suite is not what this brief asked for.

### What the drivers actually assert

Worth naming, because "all pass" is worth nothing without it.

- The post arrives by fragment and **no request carries the post text**.
- Nothing is fetched off this machine, on any state. No CDN, no web font.
- No JavaScript errors and no 404s, on any state.
- The three marks have **three distinct fill heights** — the greyscale check.
- A thing they cannot show **renders no quote block at all**.
- The call sits above the working, and the working is collapsed when finished.
- The old recording still renders its counts and its rows, and **invents no
  call and no sections** where no `summary` arrived.
- No sideways scrollbar at 420px.

### The greyscale check

Done, with colour stripped in the browser and the result read. The three
answers are **full bracket, half bracket, empty bracket** and they are plainly
different with no colour at all. Every row also spells its answer out in words.
`--v-not` has no hue, so it is already grey and stays grey.

**This is the half of the two-metre test a machine can do.** The other half is
a person, and it is still not done.

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

**The gate cannot see a web page.** It says nothing about anything above except
that the repository is still in order.

## Git status

Nothing staged, nothing committed.

```
?? web/
```

`web/` has never been committed, so the whole folder is still untracked.

## The three that matter

**Done but not asked for.**

- `web/tokens.css`, the copy. Forced by the backend's static route, explained
  above. Without it the demo path serves an unstyled page.
- The `[hidden] { display: none !important; }` rule. Half the blocks here carry
  their own `display`, which silently beats the browser's `[hidden]` default —
  an element hidden in the markup and on screen anyway. It cost three of the
  first six driver failures.
- **Stop actually stops now.** `cancelled` existed and nothing ever set it. The
  board has a Stop button, so it is wired.
- The two recordings were rewritten to decision `0006`'s five-field shape. The
  brief said to stop joining against verdict events; that is only possible if
  the recordings carry the words.

**Asked for but not done.**

- **The two-metre test.** Not something I can do.
- **Three things on the board have no data behind them** and are not built: the
  PDF drop zone, "See how we read it →" with the resume shown line by line, and
  the post card's parsed title and company. This page takes pasted text and the
  backend sends no document metadata. The rail shows two wells instead, using
  the board's own empty and filled treatments. **If the resume view is wanted,
  it needs an endpoint first.**
- **The error state's "Carry on from number 7" is one button, not two.**
  Nothing can resume a stream part way. I render "Start again" alone rather
  than a button that would lie.

**Wrong in the brief.**

- **"Brief `0012` is building it now. Until it lands, the recording path must
  keep working."** It has landed. Both paths work, and the live one is better
  than the brief expected: it re-emits `summary`, so the answer updates instead
  of going behind.
- **"`RERUN_ENDPOINT` at the top of `app.js` is the line."** That line was
  already right. The work was the request body, not the URL: decision `0006`
  writes `resume_id`, and this page has no resume id because it has no upload.
  It sends `post`, `resume` and `requirement_id`, the same shape `/audit`
  takes, and the real endpoint accepted it.
- **"Three bare `#fff` values."** Correct, and there were no others. The whole
  stylesheet was replaced, so it is moot.

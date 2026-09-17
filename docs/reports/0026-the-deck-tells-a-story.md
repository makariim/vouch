---
status: open
date: 2026-09-17
brief: 0026-the-deck-tells-a-story
---

# 0026 — The deck tells a story

**Sixteen slides. Every one has a headline, every one fits, nothing is fetched,
`Cmd+P` still gives sixteen pages.**

The spine in section 3 is followed as written. Nothing was dropped, no number
moved, no limitation softened. What changed is the order, the sentences, and
the shape of a slide.

**Two rulings landed after the first pass and both are in.** Slide 8 is
**"LangGraph, because the audit goes back."** and slide 2 is **"Nobody checks a
job post. They read it once and guess."**

**The slide 8 ruling cost 55px** — it is 40 characters and wrapped to two
lines, which put the slide over the screen. **It was not paid for with words.**
The headline measure went from `34ch` to `40ch`, so the ruling renders on one
line exactly as written. Nothing else on slide 8 moved, and all sixteen still
fit. `34ch` was my own guess at what the broken value below was meant to be;
a ruling is better evidence of the right measure than a guess is.

**What this replaced.** Your spine asked slide 8 to argue *"because the audit is
a cyclic graph with a decision in it"*. The word *cyclic* is not in the deck;
*goes back* is the plain twin of it, and it now matches slide 7's third block,
`IT GOES BACK`, word for word.

## Every headline, in order

Read this block on its own. That is the test.

```
 1  Vouch checks a resume against a job post, one requirement at a time.
 2  Nobody checks a job post. They read it once and guess.
 3  One model call answers. Nothing shows where it came from.
 4  So the model never writes the answer. It returns a line number.
 5  DEMO
 6  So how the file is cut into lines decides the answer.
 7  It is an agent for three reasons. Calling a model is not one of them.
 8  LangGraph, because the audit goes back.
 9  The old retry asked the model to grade itself. It never fired.
10  It fired three times. Nobody pressed anything.
11  All three were found by running it, not by reading it.
12  Almost every model problem turned out to be a data problem.
13  I built this by directing agents, under a method I wrote first.
14  This is not a resume tool. It audits a document against a rulebook.
15  "It cannot invent a citation" is what makes a model usable in a
    regulated industry.
16  Make the guarantee structural, not a promise.
```

**Where the chain is load-bearing**, and what I changed to make it hold:

- **3 → 4.** Slide 3's old headline was *"And you cannot tell whether the resume
  said it or the model wanted it to."* Read on its own it has no subject — *tell
  what?* It is now **"One model call answers. Nothing shows where it came
  from."**, which stands alone and hands slide 4 its *"So"*. The old sentence
  did not die; it is the accent line on the same slide, plainer: *"You cannot
  tell if the resume said it, or the model made it up."*
- **9 → 10.** Your ruling from brief 0025 — *"It fired three times. Nobody
  pressed anything."* — is kept word for word as slide 10's headline. It only
  reads as a fix because slide 9 now ends on **"It never fired."** That pairing
  is the reason slide 9's headline changed.
- **14 → 15.** Old slide 16 carried the generalisation and the commercial case
  in one block. Split, so slide 14 says *what it is* and slide 15 says *why
  anyone pays*, which is the one place the old deck made the room do the work.

## What was merged, split and dropped

| | |
|---|---|
| old 5 + old 6 → **new 4** | Both said one thing: the model gets lines and returns a number. Two slides for one idea |
| old 8 + old 10 → **new 8** | The graph drawing was the evidence for the library choice and sat three slides away from it. Now the drawing is on the slide that argues from it |
| old 16 → **new 14 + new 15** | See above. One slide was carrying two arguments |
| old 4 (demo) → **new 5** | Moved one later. Slide 4 now earns the demo instead of preceding it |

**Nothing was dropped.** Two things were shortened and both are named here:

- The graph drawing lost its two-line tail (`↓ report` on its own line) and is
  now two lines. Same nodes, same branch, same decision point.
- Slide 8's footnote lost *"which I know best and which is not on their list
  anyway"* from the DSPy clause. It now reads *"— and DSPy ReAct."* The
  honesty is intact and the sentence is one line. **The cut clause is worth
  saying out loud**; it is not worth two lines of footnote.

## The accent

**Violet, `oklch(0.800 0.115 285)`, declared deck-only in `build.py`.**

Every hue `tokens.css` owns is spoken for: 160 and 80 are two of the three
answers, 25 means something broke, 330 means the app is working on this right
now. 285 is the one direction none of them occupy, and on a projector it reads
as blue against a pink — no chance of being mistaken for rose, and nowhere near
green or amber.

It marks exactly three things, and nothing else in the deck carries a hue:

- **the eyebrow** — the dim step, `oklch(0.660 0.075 285)`
- **a block label** — the same dim step, so labels and eyebrows read as one
  system
- **the one line per slide that matters** — the bright step, written `==like
  this==` in `slides.md`. **At most one per slide**, and eleven of sixteen have
  one. Five have none; the headline was already the only thing that mattered.

The three verdict colours still appear exactly where they always did: the
column headings of slide 6's table, which is the product's own language.

## How a slide is built now

`LABEL :: text` in `slides.md` is a labelled block, and a run of them is one
stack. That is the one new convention, and it is the reference's `.stack` —
a name down the left in the accent, the text beside it in ordinary body.

**Fourteen of sixteen slides carry a stack of named blocks.** The two that do
not are the two where a block would be a lie about the content: slide 1, which
is a headline and two sentences, and slide 6, where the table *is* the evidence.
Fourteen carry an eyebrow — slides 1 and 5 do not, as before.

## What changed

| File | Why |
|---|---|
| `docs/presentation/slides.md` | Rewritten. Sixteen slides, the spine's order, plain sentences, labelled blocks, a source under each claim |
| `docs/presentation/build.py` | Three additions: `LABEL :: text` → a stack, `==text==` → the accent span, and the deck-only accent tokens with the comment saying why it is deck-only. Two CSS bugs fixed, below |
| `docs/presentation/slides.html` | Rebuilt by `build.py`. Not hand-edited |
| `docs/presentation/demo-script.md` | Six stale slide numbers in the questions table. Nothing else touched |

**Two CSS bugs that were already there**, found because the new slides made
them visible:

- `h1 { max-width: 34 58ch }` — not a value. Headlines had no measure at all
  and ran the full 1240px. Now `40ch`, set by the slide 8 ruling.
- `p, ul { max-width: ch }` — also not a value, same effect. Now `62ch`.

**Fixing them cost height**, because paragraphs that had been running full-width
now wrap. That is paid for in content, not in type size — slides 8 and 13 were
over and were cut until they fit.

## What was run

```
python3 docs/presentation/build.py --check
  docs/presentation/slides.html: 16 slides, 44,901 bytes,
  running order dropped (59 lines).
  fit: all 16 slides fit at 1440x810, type unchanged
  fetched by the page: 0 (nothing)
```

Three slides were also screenshotted headless at 1440x810 and looked at — 2, 8
and 13 — because a fit measurement says a slide fits, not that it reads. The
files are in the session scratchpad, not in the repository.

## The check

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

## Git status

Nothing staged. Nothing committed.

```
 M docs/presentation/build.py
 M docs/presentation/demo-script.md
 M docs/presentation/slides.html
 M docs/presentation/slides.md
?? docs/briefs/0026-the-deck-tells-a-story.md
?? docs/reports/0026-the-deck-tells-a-story.md
```

## The three that matter

**Done but not asked for.**

- **Six slide numbers in `demo-script.md`.** Renumbering 17 slides to 16 left
  that file pointing at the wrong slides for six of its twelve likely
  questions — *"Is this production ready?"* pointed at a slide that no longer
  exists. It is inside `docs/presentation/`, so it is inside the fence.
- **The two CSS bugs above.** Neither was in the brief. Both were silently
  wrong and both affect how a headline wraps, which is the thing the brief is
  about.

**Asked for but not done.**

- **"Read the deck out loud once, end to end."** I read every line and rewrote
  the ones that stumbled. **I cannot hear it.** This is the same gap as item 1
  of `docs/standing.md` — the deck has still never been spoken by a person, and
  section 8's other criteria are all measurable while this one is not.

**Wrong in the brief.**

- **Section 3's slide 8 does not fit as written.** The headline it proposes is
  two lines and takes slide 8 over the screen. Reported above as the one
  judgement call.
- **Section 4 quotes *"The guess is the product. Not the writing — the
  checking."* as the example of an aphorism to kill.** *"The guess is the
  product"* was slide 2's headline and the whole slide's argument, so it could
  not simply be deleted. It is now stated plainly as **"Nobody checks them.
  They read it once and guess."** — the same claim, no decoding. The
  second half, *"Not the writing — the checking"*, is gone. It was the part
  that cost three seconds.

## One sentence I could not make plain without losing the fact

**Slide 15: *"It cannot invent a citation" is what makes a model usable in a
regulated industry.***

*Citation* and *regulated industry* are both the industry's own words, and both
are the point — the person who asks this question in a room says it exactly
that way. Every plainer version I tried (*"it cannot make up a quote"*) said
something smaller: a quote is a resume line, a citation is what a bank's
auditor needs. It is 82 characters and runs to three lines on the slide.

## What would tell us this failed

Section 8's own test: the headlines read as a table of contents rather than an
argument. The block at the top of this report is the only evidence, and it is
yours to judge — read it without the slides, and if any line does not follow
from the one above it, that line is the bug.

---
status: open
date: 2026-09-17
brief: 0024-the-vision-and-the-tools
---

# 0024 — What the presentation does not say

**All six gaps are in the deck. The clock closes at fourteen and a half
minutes, and it closes by declaring that questions are after the fifteen, not
inside it.** Under the other reading there is half a minute for questions, which
is nothing — so the file names the next two cuts rather than pretending.

The deck is **seventeen slides**, up from fourteen, and **all seventeen fit the
stage**. Slides 6, 10 and 11 were not touched; the last two are now numbered 11
and 12, and nothing in their bodies moved. **Slide 7 was trimmed to fit after
the director released the constraint** — see below.

## The six gaps, and where each one landed

| Gap | Where | New or edited |
|---|---|---|
| 1 — the vision | **slides 16 and 17**, the close | new, two slides |
| 2 — why is this an agent | **slide 9** | new, absorbing old slide 9 |
| 3 — why these tools | **slide 10** | new |
| 4 — the learning | **slide 14** | new, replacing old slide 13 |
| 5 — why this problem | **slide 2**, one line | edited |
| 6 — how it was built | **slide 15** | new |

**Gap 1 is two slides, not one.** *What this actually is* — a document against a
rulebook, per-item verdict, cited evidence, and a refusal to cite what is not
there — then *Scaling it, honestly*. Splitting it was a fit decision before it
was an editorial one: as one slide it overran the stage by 107px. It reads
better split, because the argument and the caveats are different beats.

**Gap 2 absorbed old slide 9 rather than being added to it.** Old slide 9 said
the loop counts requirements and nothing can stop early. That is not a separate
point from *why is this an agent* — it is one of the three answers. So the slide
was rewritten around the question, and the loop is the middle bullet. That is
where half of the compression came from.

**Gap 4 replaced old slide 13** — *What I would do next*. Its three items did not
die: the retry cap and the middle verdict moved up to slide 13 with the other
known defects, and *record token usage* moved down into slide 17's list of what
productizing would need. It was in the wrong place; the same sentence reads as
an excuse under "next" and as a requirement under "what it would take".

**The email's own vocabulary.** The brief counted *customer*, *scale*,
*productize* and *DataRobot* at twice in fourteen slides. Now: customer 3, scal-
1, productiz- 1, DataRobot 2, agent 4.

## What was compressed to pay for it, named

| Part | Before | After |
|---|---|---|
| The problem | 2 min | **1** |
| The demo | 5 min | **5 — untouched** |
| How it works, slides 5–9 | 4½ min | **2½** |
| What it got wrong | 2½ min | **1½** |
| Questions slide | ½ min | **deleted** |

**The only structural cut is old slide 14**, the Questions slide, which opened
*"Not production ready, and not pretending to be."* That sentence is now nowhere
on a slide. The honesty it carried is on slides 11, 12, 13 and 17 — slide 17
lists five things the thing does not have — and none of that is the last thing
in the room any more.

Everything else is budget, not deletion. **No slide was cut to make room**, and
neither the demo nor slides 11–13 gave up a second.

**Three sentences were cut to make slides fit the stage**, and they are content,
so they are named:

- *"Two sessions found the same hole in the API contract, independently"* — cut
  from slide 15. **It is now a prepared answer** in the demo script's question
  table, under *"Did you write this, or did the agents?"*, which is where it
  actually gets asked
- *"a control framework"* — cut from slide 16's list of rulebooks. Three
  examples make the point; four made a fifth line
- *"so cost is measured not calculated"* — cut from slide 17. Slide 13 and the
  demo script both still say it
- **slide 7's two-reader sentence**, compressed rather than cut — *"One returns
  the text in the order the file was written. The other orders it by where it
  sits on the page"* became *"file order, versus position on the page"*. Same
  mechanism, one line instead of two. Its own section below

## The new clock

| Part | Slides | Minutes |
|---|---|---|
| The problem, and why the obvious build is wrong | 1–3 | 1 |
| The live demo | 4 | 5 |
| How it works | 5–9 | 2½ |
| Why these libraries | 10 | ½ |
| What it got wrong | 11–13 | 1½ |
| What I learned | 14 | ½ |
| How it was built | 15 | 1½ |
| Where this goes | 16–17 | 2 |

**14½ minutes. Questions are after the fifteen.** That is written at the top of
`slides.md`, which is what the brief asked for.

**If the panel means questions inside the fifteen, it does not close**, and the
file says what goes: slide 10 becomes a spoken sentence over slide 8, and slide
14 folds into slide 16. That buys 1½ minutes and leaves two for questions. It
does not touch the demo and it does not touch slides 11–13.

**This is a budget, not a measurement, and the deck now says so on its own first
page.** Nothing has been spoken against a stopwatch — the same hole report `0022`
reported, unchanged, and still item 1 of `docs/standing.md`. **Gap 1 was budgeted
at 2–3 minutes by the brief and got 2.** That is the one place the arithmetic
squeezed something the brief asked for.

## Still not covered

**The email's five topics and four criteria are covered. Three things are not,
and two of them are deliberate.**

- **No DataRobot product, and no customer scenario.** The deck argues the
  pattern — a document against a rulebook — and stops. Section 5 forbids
  inventing one, and the honest position is that mapping it onto their portfolio
  is a conversation, not a slide. **It is not prepared, and it is the most
  likely question off slide 16.** Worth ten minutes on their product pages before
  the day
- **"Productized" is answered as engineering, not as a product.** Slide 17 says
  what it would need to be trustworthy at scale. It says nothing about
  packaging, pricing or deployment model. That is beyond anything measured here
- **The timing.** Still never spoken. Everything above is arithmetic

## Wrong in the brief

**Three things, and the first one is a claim I could not evidence.**

**1. "The turn-end gate refused three times over a missing integrity record."**
Section 2, Gap 6. I could not find it. Nothing in the 22 reports records a gate
refusal, and `formwork/limits.md` describes *three times* as the gate's **budget
per session** — it refuses three times, then stands aside — which is a different
statement and is a documented hole rather than a catch. **It is not on the
slide.** Putting an unverifiable specific on a slide about a method for not
making unverifiable claims was the one thing that slide could not survive. The
two catches that are on it are both evidenced: the planning role's four offers
are written in `formwork/limits.md`, and the report count was counted.

**2. The counts are a session out of date.** The brief says *"24 briefs, 8
decision records, 21 reports, across 23 commits."* Reports are **22** on disk and
**23** once this one lands, so the slide says 23. **The commit count is not on
the slide at all** — committing this work changes it, and a number that is wrong
by the time it is presented is worse than no number.

**3. "Gap 4 is one paragraph on an existing slide."** There was no existing slide
that could take it. Slide 7 is the evidence and is protected; slides 11 and 12
are protected; slide 13 is a defect list. It is its own slide, and it costs half
a minute rather than nothing.

**And one thing the brief could not have known.** Old slide 13 said *"Cap the
retries"*, which reads as though nothing caps them. `MAX_ATTEMPTS = 3` in
`src/audit/graph.py:37` caps searches **per requirement**. What is uncapped is
how many requirements retry in a run. Slide 13 now says that, and slide 9's
*"up to three searches"* agrees with the code.

## Slide 7, and how it was trimmed

Report `0023` measured slide 7 over by 52px and named the cut: **delete the
second paragraph**, on the grounds that the table's columns already say it. The
first pass of this brief could not act on it — `0024` protected slide 7 — and
the report said so. **The director then released the constraint: do not lose the
argument, do not lose the table, do not lose the last line.**

**I did not take `0023`'s cut.** The table's columns are `pypdf` and
`pdfplumber` — two library names. They say which reader won; they do not say
*why*, and the why is the whole point: one returns text in the order the file
was written, the other by where it sits on the page. Deleting that paragraph
would have left a slide that asserts a result with no mechanism.

So it was compressed instead, in three steps, measured after each:

| | need | |
|---|---|---|
| start | 737px | over by 52 |
| the two-reader sentence cut to one line | 691px | over by 6 |
| shortening the opening sentence | 691px | **no change** |
| merging the two opening paragraphs | **671px** | fits, with 14px spare |

**The second step taught me something worth writing down.** Shortening the
opening from 103 characters to 73 moved nothing, because at the deck's body size
the column already holds well over 103 — it was one rendered line either way.
**Source line breaks in `slides.md` have nothing to do with rendered height.**
What costs height is a rendered line or a paragraph gap, and only removing one of
those helps.

So the last 6px came from **merging the two opening paragraphs into one**, which
removes a paragraph gap and no words at all. The original wording — *"not a
detail — they are the answer"* — was restored once that was understood; the
shortened version had been paying for nothing.

**Nothing was lost.** The table, the control line and the closing line are
untouched, and the mechanism survives in a shorter sentence.

## What was run

| | |
|---|---|
| `python3 docs/presentation/build.py --check` | **17 slides, all 17 fit at 1440x810. 0 fetched** |
| the same, nine times | after each trim. Slides 7, 15, 16 and 17 each overran and were cut back, by sentence or by paragraph gap, never by type size |
| `grep` over `docs/reports/` | **18 of 22 reports name something the brief got wrong.** The number on slide 15 |
| `grep` over `src/audit/graph.py` | `MAX_ATTEMPTS = 3`, which corrected slide 13 |
| the four protected slides, read back | bodies identical. Only the `Slide N —` prefix moved on two of them, and `0023` established that prefix is dropped on screen |

## The check

`formwork check` — **green. 12 checks**, each shown to reject the wrong input and
accept the right one. Section 7 of the brief says outright that nothing in it can
check a presentation. The evidence is everything above.

## What changed

| | |
|---|---|
| `docs/presentation/slides.md` | 14 slides to 17. Six gaps, the new clock, the questions ruling |
| `docs/presentation/slides.html` | regenerated. 38,443 bytes, still one file, still fetches nothing |
| `docs/presentation/demo-script.md` | slide references renumbered, and **seven new rows** in the question table |

Nothing outside `docs/presentation/` and this report was written.

## Git status

```
 M docs/future.md
 M docs/presentation/demo-script.md
 M docs/presentation/slides.md
 M docs/standing.md
?? docs/briefs/0022…0024
?? docs/presentation/build.py
?? docs/presentation/slides.html
?? docs/reports/0022…0024
```

Nothing staged. **`docs/future.md` and `docs/standing.md` are brief `0022`'s and
were not opened here.** Of the rest, three are mine: `slides.md`,
`demo-script.md`, `slides.html`, plus this report.

## The three that matter

**Done but not asked for.** Seven rows on the demo script's question table. Every
new slide invites a question the deck cannot answer on its own — *have you done
this for a customer*, *did you write this or did the agents*, *why LangGraph* —
and three of them have a wrong answer that is easy to give under pressure.
Each row says where to point and, where it matters, what not to say.

**Asked for but not done.** Gap 1 got 2 minutes against a brief that budgeted
2–3. That is the one place the arithmetic squeezed something the brief asked
for, and it is named above.

**Wrong in the brief.** The gate claim in Gap 6, which is not evidenced anywhere
in this repository and is not on a slide. Section "Wrong in the brief".

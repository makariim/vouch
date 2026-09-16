---
status: open
date: 2026-09-16
brief: 0005-the-presentation
---

# 0005 — The presentation

**The slides and the demo script exist. Neither has been rehearsed, and no
rehearsal is possible from here.**

Section 5 of the brief has four done-when items. All four are human acts — read
aloud against a clock, two full demo runs, a tested fallback, the two-metre
test. An agent cannot do any of them, and pretending otherwise would be the one
failure this repository exists to prevent.

So this report gives you the two artefacts, the arithmetic that stands in for a
rehearsal until you do one, and — the part worth reading — **three things in the
brief that no longer match the files.**

The brief stays `open` until you have run it twice.

## What changed

| File | Why |
|---|---|
| `docs/presentation/slides.md` | 13 slides, few and plain. One `---` block per slide, and the running order with minutes |
| `docs/presentation/demo-script.md` | The setup checklist, the clicks in order, the words over each one, the fallback, and the questions |
| `docs/standing.md` | "Where we are now" and "What is next" — the presentation now exists as a draft, the rehearsal does not |

Nothing in `src/`, `web/`, `extension/`, `design/` or `tests/` was opened. No
code changed, per section 2.

## What was run

`formwork check` and word counts. **No model call, no server, no audit.**

## The check

`formwork check` — **green. 12 checks.**

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

Section 6 of the brief is right that nothing can check a presentation. The gate
says the repository is consistent. It says nothing about whether the talk works.

## How long the rehearsal took

**NOT ESTABLISHED. There was no rehearsal.**

What exists instead is arithmetic, and it is not the same thing:

| | Words |
|---|---|
| Scripted speech in the demo script | 312 |
| Slide text, all 13 | 628 |
| Total scripted | **940** |

At 140 words a minute that is about **seven minutes of scripted material** for
a fifteen-minute slot. The remaining eight minutes are you talking over a
stream, and **that is the half that has never been timed.**

The brief asked for measured, not estimated. This is estimated. Treat the seven
minutes as a floor, not a duration.

## What was cut to fit fifteen minutes

- **The tailor, Langfuse and the browser extension.** The brief made them slides
  rather than features; they are not even slides now. Nothing in the fifteen
  minutes needs them, and each one opens a question you cannot answer in the
  time. Mention them only if asked.
- **The extension's real-page detection** — report `0016`, the 79-to-25 result.
  Genuinely good work, and it is a second demo, not a slide.
- **The re-run of one requirement.** Demoted to step 7, marked optional, skip if
  at four minutes.
- **The design work.** Nothing about tokens, artboards or brand. The page is on
  screen for five minutes and speaks for itself.
- **The architecture of the frontend.** Not one slide. Nobody asked.

## Questions that could not be answered

These are worth more than the slides, and they are the ones to prepare:

- **"What does a run cost?"** NOT ESTABLISHED, and the script tells you to say
  so rather than estimate. Nothing records token usage. This is the weakest
  answer in the set and it is a known hole in the product, not a gap in the
  talk.
- **"Why is 60% in the middle verdict?"** Slide 11 names it as known and not
  solved. If they push on *why*, there is no measured answer — only that the
  middle absorbs both ends.
- **"How do you know extraction found the right requirements?"** Nothing checks
  the extraction step. The whole verification story is about the *evidence*,
  not about the requirement list, and the requirement list is where the
  non-determinism lives.
- **"Would it work on a post you have not seen?"** One post, one resume, three
  runs. Report `0016` is the only evidence of generality and it is a
  reconstruction, by its own admission.

## The three that matter

### Done but not asked for

- **`docs/standing.md` updated.** Required by `standing-current`, and the
  position genuinely changed.
- **A "questions and where to point" table** at the end of the demo script.
  Section 7 asked which questions cannot be answered *while rehearsing*; I
  cannot rehearse, so I wrote down the ones the material provokes and where the
  answer lives. It is not what was asked for and it is the nearest honest thing.

### Asked for but not done

- **All four items in section 5.** Rehearsal against a clock, two full demo
  runs, a tested fallback, the two-metre test. Human acts. This is the whole
  reason the brief stays `open`.
- **The measured rehearsal time in section 7.** See above — arithmetic, not a
  measurement, and labelled as such.

### Wrong in the brief

Three, and the first one changes the best slide in the talk.

**1. Section 3 says the retry has never fired. It fires now.** That finding was
true on 2026-09-15 when the brief was written; report `0012`, later the same
day, replaced the trigger. The self-report trigger fired 0 of 21, 0 of 23, 0 of
21. The observable trigger — a first pass that found nothing, plus a quote that
failed verification — **fired three times on the real post**, and one
failed-quote retry flipped requirement 18 to `evidenced` on a verified line.

The brief called "stop trusting a model's self-report and trigger on something
observable" the best sentence in the talk. **It still is — but the tense
changed.** It is now a thing that was done and measured, not a thing to do.
Slides 9 and 10 are written that way, and it is a stronger pair than the brief
imagined: a claim that rested on nothing, caught by measuring, replaced, and
then confirmed.

**2. The demo path in section 2 anchors on requirement 12 finding line 77.
Report `0004` says it does not.** BM25 moved line 77 from unranked to rank 7,
**0.19 points short of the cut**. The brief's step 3 — "requirement 12, FastAPI,
found on line 77, wrong before BM25 and right now" — would have you point at
something on stage that is not there. That step is not in the script. The BM25
story stays, on slide 11, as the fix that removed a false gap, which is true.

**3. The counts in section 3 are the old ones.** 21 requirements, 6/13/2. It is
23 and 8/12/3 as of the fifteenth. It does not matter for the slides, because
no count goes on a slide — but the brief's own numbers would have been the ones
you quoted.

One smaller thing: the page defaults its mode radio to **"A recording"**. The
brief does not mention it, and a demo started without switching to "A real run"
shows a fixture while you describe a live model. It is item 4 on the setup
checklist for that reason.

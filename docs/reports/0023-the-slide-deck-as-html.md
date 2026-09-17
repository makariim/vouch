---
status: open
date: 2026-09-17
brief: 0023-the-slide-deck-as-html
---

# 0023 — The slide deck, as a file you can present from

**One slide does not fit: slide 7.** It is over by 52px at 1440×810, and the
type was not shrunk to hide it. Everything else in the brief is done.
`slides.html` opens from disk, fetches nothing, and prints one slide per page.

## Slide 7 does not fit

`How the file is cut into lines decides the answer` — the slide brief `0022`
added. It needs 737px of a slide that has 685px.

Measured with the deck's own type, at the size it is presented at. It is over
by two lines of body text, and nothing in it is decoration: a title, two
paragraphs of setup, a five-column table, then two closing lines.

**That is content, for `0022`.** The obvious cut is the second paragraph —
*"Two readers, same PDF…"* — which the table's own columns already say.

The other thirteen fit with room.

## Nothing is fetched

**The wifi was not switched off.** Turning off the network on the author's
machine is not mine to do. What was done instead answers the same question
harder:

- the page was asked, on load, what it had fetched —
  `performance.getEntriesByType('resource')`. **Zero entries.** That is every
  request the document made, and it is attributable to the document, unlike a
  browser-wide net log, which is full of Chrome's own housekeeping
- `build.py` refuses to write the file at all if the HTML contains `http:`,
  `https:`, `url(`, `@import`, `src=` or `<link>` outside a comment. It is
  checked before the file reaches disk, so a deck that would fetch never exists

`design/tokens.css` is inlined, comments and all. Its `@font-face` block is
still commented out there, so every type stack falls through to a face already
on the machine — the same look the artboards render with.

## The command

```
python3 docs/presentation/build.py          # rebuild slides.html
python3 docs/presentation/build.py --check  # and measure the fit
```

It is in the docstring at the top of `build.py`. `slides.md` stays the source;
`slides.html` carries a comment saying not to edit it.

`--check` needs a Chrome on the machine and says so when there is none. It
drives one headless, with Chrome's own background networking off, and reports
two things: which slides overflow, and what the page fetched.

## What tokens.css did not have

**The slide type scale.** `tokens.css` is sized for a 1240px app page and stops
at 38px. A line read from the back of a room needs more, so the deck sets five
values, in one block at the top of the stylesheet, and nothing else:

| | | |
|---|---|---|
| `--d-title`  | 56px | the one line on a slide |
| `--d-body`   | 30px | body. The brief's floor is 28px |
| `--d-table`  | 28px | |
| `--d-code`   | 27px | the graph on slide 8 |
| `--d-kicker` | 20px | the slide's title where it has no `#` heading, and the number |

Colour, space, radius, the faces and the line heights are all tokens. The stage
is 1440×810 — also not in `tokens.css`, which has `--v-page-max: 1240px` for a
page, not a screen. The slide column is that 1240px.

**Two rules in `tokens.css` pulled against each other.** Mono is reserved there
for lines quoted out of a resume. A deck has neither, but it has `rank_bm25`
and it has the graph. So inline code is set in the UI face on a `--v-bg-2`
chip, and only the fenced graph on slide 8 is mono — it is drawn with
characters and has to align.

**Two of the three verdict colours are unused.** `--v-shown` marks the title
rule and the progress bar. Nothing on a slide is a verdict, so `--v-partly`
and `--v-not` had no honest job and were not given a decorative one.

## What changed

| | |
|---|---|
| `docs/presentation/build.py` | **new.** 503 lines, standard library only. Splits `slides.md`, renders the markdown it uses, inlines the tokens, and `--check` measures fit |
| `docs/presentation/slides.html` | **new, generated.** 34,889 bytes, one file, no dependency |

The block above the first `---` in `slides.md` — the running order, the clock,
the two rules — **is not a slide and is not in the deck.** It is instructions to
the person presenting.

## What was run

| | |
|---|---|
| `python3 docs/presentation/build.py --check` | 14 slides written. Slide 7 over by 52px. 0 fetched |
| keys, simulated in the page | forward through `s1`…`s14` on arrows and space, back to `s1` on arrows, stopping at both ends |
| `--print-to-pdf` | **14 pages for 14 slides.** One per page |
| three screenshots at 1440×810 | slides 1, 7 and 8, read back. Slide 7 visibly runs to both edges |

Nothing wrote outside `docs/presentation/` and this report. The screenshots and
the PDF went to the scratch directory.

## The check

`formwork check` — **green. 12 checks**, each shown to reject the wrong input
and accept the right one.

The gate cannot see a slide deck, which the brief says outright. The evidence is
everything above.

## Git status

```
M docs/future.md
 M docs/presentation/demo-script.md
 M docs/presentation/slides.md
 M docs/standing.md
?? docs/briefs/0022-revise-the-presentation.md
?? docs/briefs/0023-the-slide-deck-as-html.md
?? docs/briefs/0024-the-vision-and-the-tools.md
?? docs/presentation/build.py
?? docs/presentation/slides.html
?? docs/reports/0022-revise-the-presentation.md
?? docs/reports/0023-the-slide-deck-as-html.md
```

Nothing staged. The four modified files are brief `0022`'s, untouched here.
Brief `0024` appeared during this session and is not mine.

## The three that matter

**Done but not asked for.** `--check`. The brief asks the report to name the
slides that do not fit, and an eye on a screenshot is not a measurement — so
the answer is measured in the page, in the deck's own type, and can be
re-measured after any edit to `slides.md`. Also: the `Slide N —` half of each
`## Slide N — Title` line is dropped on screen. The number is already in the
corner, and the rest of that line is the only title twelve of the fourteen
slides have.

**Asked for but not done.** The wifi was not switched off, and `Cmd+P` was not
pressed — the print was driven headless. Both are named above with what was
measured instead. Neither would change the finding; both are worth one minute
on the machine before the day.

**Wrong in the brief.** Section 7 says *"all thirteen"*. The deck is **fourteen
slides** — `0022` added slide 7, which is the one that does not fit. Its own
report says so.

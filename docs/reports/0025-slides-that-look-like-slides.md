---
status: open
date: 2026-09-17
brief: 0025-slides-that-look-like-slides
---

# 0025 — Slides that look like slides

**All 17 slides have a headline. All 17 fit. Nothing is fetched, and `Cmd+P`
still gives 17 pages.** No argument lost a word.

**Read the correction first.** My first pass reported sixteen headlines. That
was wrong, and it was wrong because of a bug I shipped — slide 17's headline was
never a headline. Section *"The one I got wrong"* below.

The three rulings are in. Slides 13, 12 and 15 now carry the headlines you
wrote, and slide 15 uses the short form because the long one wrapped.

## How the source marks a headline

**A line starting with `# ` is the headline.** No new syntax, and the renderer
already had it — slide 1 carried a `#` heading before this brief.

That was the reason to choose it over a marker of my own. `slides.md` is read by
a person more often than by `build.py`, and `# ` already means "the biggest
thing here" to anyone who has seen markdown. A `!!` or a `{headline}` would have
been a convention only this repository knows.

Promoting is mechanical and loses nothing: `**The guess is the product.**`
becomes `# The guess is the product.` The `**` markers go, the words do not.

**The headline renders where it stands in the source.** Nothing was reordered.
That matters more than it sounds: on ten slides the headline is the *last* thing
on the slide, and it stays last — small build-up, then the punch. Moving it to
the top would have changed the order of an argument, which section 7 forbids.

Two more conventions came with it, both markdown:

| Source | What it draws |
|---|---|
| `## Slide N — Title` | the **eyebrow**, as before |
| `## Slide N` alone | **no eyebrow.** Slides 1 and 4 |
| `# …` | the **headline** |
| `> …` | the **footnote** — a source, a date, a caveat |
| anything else | body, as before |

**A slide with no `#` still renders**, eyebrow and body, nothing broken. No
slide needs that now, but slide 13 proved it before your ruling landed.

## The one I got wrong

**Slide 17's headline was never drawn.** Its bold line sat on the tail of a
paragraph in `slides.md`, so `# Make the guarantee structural, not a promise.`
came out as body text with a literal `#` in front of it. **The closing line of
the deck, printed with a stray hash on it.**

Nothing caught it. It fit, it fetched nothing, the gate was green, and my own
report counted sixteen headlines without asking which slide was missing one.
**I found it only because your ruling made me count the headlines by machine
rather than by eye.**

**`build.py` now refuses it.** A `#` that ends up inside a rendered paragraph
stops the build and names the slide:

```
slide 9: a '#' is inside a paragraph. A headline must start its own line
in slides.md.
```

That is the same shape as the two checks already in `build()` — the deck refuses
to reach disk rather than warning about itself.

**Fixing it cost 99px.** A sentence that had been rendering as 30px body became
a real 54px headline on the tightest slide in the deck. How that was paid for is
below, and it was not paid for with type size.

## The three rulings

**Slide 13** now closes on *"All three were found by running it, not by reading
it."* It sits after the three defects, where "all three" has something to point
at.

**Slide 12** now leads its evidence with *"It fired three times. Nobody pressed
anything."*, and *"And no second pass talked itself into a match."* is back in
the body, joined to *"Three stayed negative"* as it was originally written.

**One judgement inside that ruling, and it is yours to overturn.** The sentence
you promoted replaced *"Same post, 15 September: it fired three times, nobody
pressing anything."* Keeping both would have said the same number twice on one
slide. **The date is evidence, so it did not die — it is now the footnote,
`Same post, 15 September.`** No other words on the slide moved.

**Slide 15 wrapped, so it took the cut.** *"I built this by directing agents,
under a method I wrote."* is 57 characters and rendered as two lines, measured,
not guessed. It is now **"I built this by directing agents."** — one line.

**What the cut costs:** the word *method* is gone from that slide's headline.
The footnote still reads `FORMWORK.md, at the root.` and the body still says
every piece was briefed and reported. **The method is on the slide; it is no
longer in the largest type on it.**

## Every headline, and how it reads

| | Lines | |
|---|---|---|
| 1 | 1 | Checking a resume against a job post |
| 2 | 1 | The guess is the product. |
| 3 | 2 | And you cannot tell whether the resume said it… |
| 4 | 1 | **DEMO** — the eyebrow became the headline. No word invented |
| 5 | 2 | The resume is never pasted into the prompt. — no bold line existed; its first sentence is the argument |
| 6 | 1 | A fabricated quote is therefore impossible. |
| 7 | 2 | The verdict changed and nothing about the model did. |
| 8 | 1 | `verify` always runs. |
| 9 | 1 | Not because it calls a model. — three parallel bold leads, so the opener was a call |
| 10 | 1 | **LangGraph.** — one word, answering the question the eyebrow asks |
| 11 | 2 | A self-report nobody can check is not a trigger. |
| 12 | 2 | It fired three times. Nobody pressed anything. — **your ruling** |
| 13 | 2 | All three were found by running it, not by reading it. — **your ruling** |
| 14 | 1 | The model never changed. Not once. |
| 15 | 1 | I built this by directing agents. — **your ruling, short form** |
| 16 | 1 | Not a resume tool. |
| 17 | 2 | Make the guarantee structural, not a promise. |

**Ten are one line, seven are two.** Nothing runs to three.

## The value `tokens.css` did not have

**An accent the deck may use. Every hue in that file is spoken for.**

- rose is **RESERVED** by section 3, in those words: it means *the app is
  working on this right now*, and *"never decoration"*
- the three answer colours mean the three answers, and one of them appears on a
  slide in this deck as data
- red lives in section 4 and means something broke

So a deck eyebrow has no colour it can take without diluting a signal the demo
itself relies on, five minutes later in the same room. **I did not invent one.**

**The hierarchy is built from contrast instead** — size, weight, the display
face, and the ink steps, all of which `tokens.css` does have. That is also what
survives greyscale and the back row, so it is not purely a consolation.

**The deck lost the green it had been borrowing.** The progress bar, the code
block's left rule and the headline rule were using `--v-shown` as decoration.
They are neutral now. Green and amber appear **once in seventeen slides**: the
`evidenced` and `partly` column headings on slide 7, where the word and the
colour say the same thing. That is the brief's rule in section 5, applied
literally.

**Type scale is still set in `build.py` and nowhere else**, as report `0023`
reported. `tokens.css` tops out at 38px for a 1240px app page; the headline is
54px. Unchanged gap, same reason.

## How the fit was paid for, and it was never type size

**Slide 7 fits**, with the words report `0024` fought to keep. It never needed a
content cut, which is the one thing section 6 of the brief got wrong.

Three overruns happened and each was fixed by **measure** — how wide a column of
text is allowed to be — which changes how many lines a paragraph wraps to
without changing how big anything is:

| | What overran | What fixed it |
|---|---|---|
| headline measure | slide 15, by 29px | 24ch → **34ch**. Its sentence went from four lines to three |
| eyebrow measure | slide 7's eyebrow wrapped to two lines | the eyebrow stopped inheriting the body's measure |
| body measure | **slide 17, by 99px**, once its headline was real | 54ch → **58ch** |

**Body is still 30px, table 28px, code 27px — every one unchanged from before
this brief.** A footnote is 24px, but a footnote is a new part, not a shrunk
one.

**The margins are healthier than my first pass reported.** Every slide now has
at least 40px of spare height at 810px; the tightest is slide 17 with 42px. The
first pass had three slides under 25px.

## What changed

| | |
|---|---|
| `docs/presentation/slides.md` | 17 headlines, 5 footnotes. **No word added, removed or reordered**, beyond the three you ruled on and the one demotion named above. Two `## Slide N — Title` lines lost a placeholder title: slide 1's said `Title`, slide 4's said `DEMO` and is now on the slide |
| `docs/presentation/build.py` | `>` → footnote; the eyebrow is always drawn; verdict columns keep their hue; the type scale rewritten around four parts; **a new guard that refuses a `#` stranded inside a paragraph** |
| `docs/presentation/slides.html` | regenerated. 39,531 bytes, one file, fetches nothing |

Nothing outside `docs/presentation/` and this report was written.

## What was run

| | |
|---|---|
| `python3 docs/presentation/build.py --check` | **17 slides, all 17 fit at 1440x810. 0 fetched** |
| the same, fourteen times | after each change. Every overrun was fixed by measure, never by type size |
| the same probe at 1440x**780** and **740** | to find the thin margins. Only slide 17 shows, and only at 740 |
| a headline probe, counting rendered lines per `h1` | **this is what found slide 17's missing headline.** The table above is its output |
| Chrome `--print-to-pdf` over the file | **17 pages.** One slide per page |
| Chrome `--screenshot` on slides 1, 3, 4, 7, 12, 13, 15, 17 | read as slides at back-of-the-room distance |
| the same, with `filter: grayscale(1)` | slide 7. The two coloured headings stay legible and the words carry the meaning without them |
| the new guard, on a slide built to break it | **refuses, naming the slide.** Shown above |

The fetch count is measured from inside the page —
`performance.getEntriesByType('resource')` — which is what "opens with the wifi
off" means in practice. **It is zero.**

## The check

`formwork check` — **green. 12 checks**, each shown to reject the wrong input and
accept the right one. Section 9 of the brief says outright the gate cannot see a
slide deck; the evidence is the two sections above.

## Git status

```
 M docs/presentation/build.py
 M docs/presentation/slides.html
 M docs/presentation/slides.md
 M docs/reports/0024-the-vision-and-the-tools.md
?? docs/briefs/0025-slides-that-look-like-slides.md
?? docs/reports/0025-slides-that-look-like-slides.md
```

Nothing staged. **`docs/reports/0024…` is not mine** — it was already modified
when this brief started and was not opened here.

## The three that matter

**Done but not asked for.** The build now refuses a headline stranded inside a
paragraph. Nothing asked for that, and the deck shipped one round with exactly
that defect in its closing line. A check that costs four lines and would have
caught it is worth more than my promise to look harder.

**Asked for but not done.** Nothing outstanding. Every slide has a headline,
which is section 8's first line, and it took your three rulings to get there —
sections 4 and 7 of the brief are why I stopped short rather than writing them
myself.

**Wrong in the brief.** **Section 6 predicted slide 7 would be the fit problem.
It was not** — `0024` had already trimmed it. The slide the new scale broke was
**17**, which the brief never mentions, and it only broke once I fixed my own
bug. Nothing else in the brief turned out not to match the files.

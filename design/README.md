# Vouch — applying the design

One page. Read it, then build.

This is take two. Take one was called "Attest" and was a light theme; it is
gone. Nothing in this folder refers to it.

---

## What is here

| File | What it is |
|---|---|
| `tokens.css` | Every colour, type step, space, radius and duration. Import it once at the root of both surfaces. |
| `assets/mark.svg` | The mark, 32px box. Inherits `currentColor`. |
| `assets/favicon.svg` | The 16px cut, with its own stroke weights and a baked tile. |
| `canvas/Foundations.dc.html` | The mark, the palette, the three answers, the type, the writing rules. |
| `canvas/Web.dc.html` | The full page, all seven states. Switch them in the header. |
| `canvas/Extension.dc.html` | All six panel states, each at the real 380px. |
| `canvas/canvas.json` | Where the three artboards sit on the canvas. |

**If you need a value that is not in `tokens.css`, that is a bug in the file.
Say so. Do not invent one.**

---

## How to use the tokens

Import once, at the root of each surface. Then never write a literal.

```css
@import "../design/tokens.css";
```

`tokens.css` has two layers:

- **Roles** — `--v-ink-2`, `--v-bg-1`, `--v-shown`. Named for the job they do.
  Reach for these. They are what the design is written in.
- **Steps** — `--v-ink-700`, `--v-bg-212`. Named for their own lightness. There
  for when you are matching an artboard pixel for pixel and no role fits yet.

A role is an alias for a step. They are never two different colours.

Sizes work the same way: `--v-text-body` on the page, `--v-text-p-body` in the
panel. Anything prefixed `--v-*-p-*` is the panel's cut of that value.

### Fonts

Three families, and **nothing is fetched at runtime**. No hosted font, no CDN,
no `<link>`. No font file ships today, so every stack in `tokens.css` falls
through to a face already on the machine — a slab serif, a grotesque, a mono.
That is what the artboards render with and it is the intended look.

To bundle real faces later: drop four `.woff2` files in `assets/fonts/` and
uncomment the `@font-face` block at the bottom of `tokens.css`. Nothing else
changes.

| Token | Role |
|---|---|
| `--v-font-display` | Slab serif, 700 only. The answer word, section headings. |
| `--v-font-ui` | Sans, 400 and 500. **Everything else** — body, labels, buttons, counts, filenames, the trace. |
| `--v-font-mono` | Mono, 400. **Quoted resume lines and their line numbers. Nothing else.** |

The mono rule matters more than it looks. Mono means *this came out of your
resume and we did not touch it*. Using it for labels and buttons made the whole
product feel like a terminal. It is meant to feel like a careful second opinion.

---

## The three answers

```
your resume shows this           [█]   full bracket    --v-shown
your resume shows part of this   [▌]   half bracket    --v-partly
your resume does not show this   [ ]   empty bracket   --v-not
```

Build the mark from the `--v-mark-*` tokens: a square box holding three
absolutely-positioned pieces — a left arm, a right arm, and a fill bar that
rises from the bottom to 100% / 50% / 0%. Three sizes, each with its own arm
width and stroke; never scale one of the others with a transform, the stroke
goes wrong.

The fill level carries the meaning in greyscale and for a colour-blind reader.
Test with colour off. The foundations artboard draws every mark twice, once
with the colour removed, so you can check.

**`--v-not` has no hue on purpose. Do not make it red.** Nothing went wrong;
the resume just does not say it. Red lives only in `--v-error-*`, for when the
run itself breaks.

Never a fourth answer. No "likely", no "unclear".

---

## Quotes

Mono, on `--v-bg-2` (`--v-bg-252` in the panel), a `--v-quote-edge` left edge in
the answer's colour, `white-space: pre-wrap` so the resume's own spacing
survives. No italics, no smart quotes, no ellipsis, no trimming. Character for
character. Label it "line 22, word for word" and mean it.

When the answer is *does not show this*, render **no quote block at all**. Not
an empty box, not a dash, not "no match found". One plain sentence of reasoning
and nothing else. That silence is the product.

---

## Three levels of reading

Build every screen so the first two levels work without reading a full sentence.

1. **One glance** — should I apply. The word, one sentence, three counts.
2. **Five seconds** — the few things that decide it. Three sections, one line
   per item, capped at three items each.
3. **Only if I ask** — the reasoning, the search terms, the trace, the full list
   of everything they asked for. **Collapsed by default.** The
   requirement-by-requirement list is reference material. It must never sit
   above the answer.

The one exception: while it is working, level three opens by itself. That
minute is the interesting part.

---

## No numbers where there is no precision

The answer is one of three words — strong, worth applying, weak — plus one
sentence. No percentage, no score, no ring. The only digits in the product are:
counts of things asked for, resume line numbers, page counts, elapsed seconds,
and the quick word match (6 of 9).

---

## The rose

`--v-agent` and its family mean one thing: **the app is working on this right
now.** The words it searched for, the line it is reading, the moment it throws
away its own answer and tries again. When the run finishes, the rose leaves the
screen.

It is never an answer, never a plain button, never decoration. The one other
place it appears is the focus ring, because focus is also about what is
happening now.

---

## The panel

380px, fixed. Chrome decides that. Design to 344px of content inside
`--v-ext-pad-x` gutters. Never a sideways scrollbar — long job titles truncate,
quotes wrap.

**The panel carries the whole answer.** Somebody applying to fifteen jobs will
not open the app fifteen times. The call, the counts, what they need that you
cannot show, what proves you fit, which lines to fix — all of it, one line per
item, three items per section. If something needs more room it expands inside
the panel. Never "open the app to see this". The link to the full page is quiet,
at the bottom, and is not the main action.

Two things happen on their own: spotting a job post, and the quick word match.
Nothing else. Checking your fit is always a click, every time, because it takes
a minute and costs money. There is no setting to change that.

---

## States to build

**Page** — nothing loaded · ready · working, with answers arriving · finished ·
one thing being looked at again · something went wrong · how we read your
resume.

**Panel** — no job post here · found a job post · quick match only · full
answer · no resume saved · Vouch is not running.

---

## How to write the words

This matters as much as the layout. Our user reads English as a second language
and is skimming.

- Short sentences. One idea each.
- Common words. If a word has a simpler twin, use the twin.
- Never use "evidence" as a verb. "You can evidence this" is not plain English.
- No invented vocabulary. Not "undersells", not "blockers", not "lead with
  these". Say what the section does: *They need two things you cannot show.*
  *This is what proves you fit.* *Fix these lines in your resume.*
- "line 22", not "L22".
- Every sentence says what to do, not what state something is in.

Before and after, so there is no doubt:

| Do not write | Write |
|---|---|
| BLOCKERS · 2 | They need two things you cannot show |
| LEAD WITH THESE | This is what proves you fit |
| UNDERSELLS · 3 | Fix these lines in your resume |
| Required. The closest line is L22, and it is written too vaguely to count. | They need this. Line 22 comes close, but it is too vague. |
| Words matching words. Not a verdict. | This is only a word match. Nothing has been read or judged yet. |

---

## Accessibility

- **Colour is never the only signal.** The bracket's fill level carries every
  answer, and each answer also has its word in full.
- **Motion.** The only animation says the app is working. `tokens.css` zeroes
  every duration under `prefers-reduced-motion: reduce`; do not reintroduce a
  hard-coded duration that escapes it.
- **Focus.** One ring, `--v-focus-ring`, everywhere, never removed.
- **Targets.** Nothing clickable is smaller than `--v-tap-min`.
- The ink ramp stops at `--v-ink` (0.915), not white, on purpose. Do not raise
  it, and do not use anything below `--v-ink-4` for text a person has to read.

---

## Not in scope, ever

No accounts, no login, no cloud, no sync. There is nowhere to sign in, so do not
leave a hole shaped like a sign-in.

Nothing comes from the internet. No hosted fonts, no remote files. It works with
the wifi off, because that is the only way the promise holds.

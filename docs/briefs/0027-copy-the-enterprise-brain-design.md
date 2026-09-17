---
status: done
date: 2026-09-17
---

# 0027 — Copy the Enterprise Brain design

> **You own `docs/presentation/` and this brief's own report.** Nothing else.
>
> **The words are finished.** Brief `0026` settled the argument, the order and
> the sentences. **Do not change a headline, a block or a footnote.** This brief
> is only how it looks.
>
> **The reference is `~/Downloads/enterprise-brain-v6.html`.** It is the
> author's own deck from another project. **Copy its visual system.** Earlier
> briefs told sessions not to — that instruction is withdrawn.

## 1. Goal

The deck reads as an argument now and still looks like text on black. The title
slide is a sentence floating in the middle of nothing.

**If we do not do this:** sixteen good slides that look unconsidered, for a talk
whose argument is that care was taken.

## 2. Take the system, not the words

Open the reference and read its `<style>` block. These are its values.

**Colour**

```
--ink        #10141B   the slide
--ink2       #1A212B   a block inside a slide
body         #080A0E   behind the slide
--paper      #EDEAE3   headline and strong text, warm off-white
--muted      #8B94A1   secondary text
--signal     #D4A342   the accent
--signal-dim #5A4820   the body block's left rule
--live       #5E9E8F   a second accent
--edge       #2A323D   borders and grid gaps
```

**Type**

```
kicker  14px  700  letter-spacing .17em  accent
h1     102px  800  line-height .95   the title slide only
h2      58px  700  line-height 1.05  max-width 24ch   every headline
h3      23px  600
.lead   29px       line-height 1.36  max-width 38ch
.body  17.5px serif  left rule 2px in signal-dim, 22px padding
.src    15px  serif italic, muted    sources and caveats
```

**Structure**

- a fixed **1600×900 stage**, scaled to fit the window
- a **header bar** across the top: 46px, a bottom border, the section label at
  12px/700/.16em
- the **slide number** bottom right, 12px/700/.14em
- padding `94px 84px 74px`

**Components — use them instead of paragraphs**

- `.stack` / `.row` — a label in muted small caps at a fixed width, then the
  text, with a bottom border between rows
- `.two` — two panels side by side, 2px gap so the edge colour shows through
- `.layer` — a row on `--ink2` with a 4px coloured left rule
- `.cols` — three or four columns

## 3. The fonts must be embedded, not fetched

The reference loads **Archivo** and **Source Serif 4** from Google Fonts.
**Do not copy that.** It would put a network fetch back into the demo.

Both are open licence. **Download them once at build time and embed them in the
HTML as data URIs**, so the finished file fetches nothing.

- keep it to the weights actually used
- `build.py` may download on a rebuild; **`slides.html` must not**
- if a font cannot be embedded, **say so and fall back to a system stack** —
  do not ship a `<link>`

**Verify it:** open the file with the wifi off and confirm zero requests.

## 4. Slide 1 is a title slide, not a sentence

The reference does this:

```
APPLIED AI / OSOS · FOR DECISION · SEPTEMBER 2026
The Enterprise
Brain
The knowledge layer everyone is racing to build is free to download...
That is the part we would automate.
```

A kicker with metadata. **The product name at 102px.** Then the thesis.

Vouch's slide 1 has the name buried inside a sentence at headline size.

**Rebuild it with the same three parts.** The words are already written — the
name, the existing headline, and the two lines under it. **Set them, do not
rewrite them.** The byline stays.

## 5. One collision to watch

`--signal` is gold and the deck already shows **amber** on one slide, where it
means *partly evidenced*. Those two must not be confused.

**The verdict colours win on that slide.** They mean something the demo relies
on twenty minutes later. If gold sits badly beside them there, **say so** — do
not quietly change either.

## 6. Must not happen

- **Do not change a single word.** Not a headline, not a block, not a footnote.
  Brief `0026` settled the writing.
- **Do not touch any file outside `docs/presentation/`**, except this brief's
  own report.
- **Nothing fetched at runtime.** Wifi off, zero requests.
- **Do not hand-edit `slides.html`.** `build.py` writes it.
- **Do not copy the reference's content, subject or sources.** Its look only.

## 7. Done when

- The deck looks like the reference: header bar, kicker, large headline, named
  blocks, serif footnotes, slide number.
- **Slide 1 is a title slide** — kicker, the name set large, the thesis.
- Opened with the wifi off, **zero requests**, fonts correct.
- All 16 slides fit. Still prints one slide per page.
- `build.py` rebuilds everything in one command.

**What would tell us it failed:** it fetches anything when opened, or a word
changed.

## 8. Checked by

`formwork check`.

The gate cannot see a deck. The evidence is section 9.

## 9. The report must contain

Short.

- confirmation of **zero requests with the wifi off**, and how you checked
- which fonts were embedded, at what weights, and the file size
- whether gold sits badly beside the verdict colours on that slide
- anything in the reference you could not reproduce, and why

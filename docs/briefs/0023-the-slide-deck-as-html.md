---
status: open
date: 2026-09-17
---

# 0023 — The slide deck, as a file you can present from

> **You own `docs/presentation/` and this brief's own report.** Nothing else.
>
> **Run this after brief `0022` lands**, or rebuild once it does. `0022` changes
> what the slides say; this brief changes how they are shown.

## 1. Goal

`slides.md` is a markdown file with `---` between slides. It cannot be presented
from and it is hard to audit — you cannot see whether a line fits on screen or
reads from the back of a room until it is on a screen.

**Produce `docs/presentation/slides.html`: one file, opened from disk, arrow
keys to advance.**

**If we do not do this:** he presents from a text file, or from something hosted,
and finds out on the day that a line does not fit.

## 2. The rule that decides the whole design

**It must work with the wifi off, opened by double-clicking the file.**

That is not a preference. It is the same rule as the product — decision `0002` —
and it would be absurd to argue nothing leaves the machine from slides served
off somebody's CDN.

So:

- **one file.** No `<link>`, no `<script src>`, no font fetch, no image fetch
- **the design tokens are inlined**, copied from `design/tokens.css`. A `<link>`
  to it is a fetch and fails on `file://`
- **nothing from `node_modules`, no framework, no build step beyond section 3**

## 3. Keep one source

`slides.md` stays the source. The HTML is generated from it.

Write **`docs/presentation/build.py`** — standard library only — that reads
`slides.md` and writes `slides.html`. Run it after any edit.

**Why not hand-write the HTML:** two files saying the same thing drift, and the
one you are not looking at is the one that is wrong on the day.

The format is already there: `---` separates slides, the first `## Slide N —
Title` line names one. The block above the first slide is the running order and
the rules — **it is not a slide.** Keep it out of the deck, or make it slide
zero and say so.

## 4. What it has to do

- **Arrow keys, and space, to advance.** Backwards too.
- **A slide number**, small, in a corner.
- **`f` for full screen**, or whatever the browser gives you for free.
- **It prints.** `Cmd+P` to PDF, one slide per page, as a backup that needs no
  browser at all. This is the fallback if something goes wrong on the day.
- **Readable from the back of a room.** Body text no smaller than 28px at
  1440px wide. If a slide does not fit, **do not shrink it** — report which one,
  because that is a content problem for `0022`, not a layout problem for you.

## 5. What it must look like

Use `design/tokens.css` — the dark ground, the ink, the three verdict colours.
It should look like the product it is about.

**Do not design something new.** If a value is not in `tokens.css`, report the
gap rather than inventing one.

**No transitions, no animation, no build-ins.** They eat time and they fail in
front of people.

## 6. Must not happen

- **Do not touch any file outside `docs/presentation/`**, except this brief's
  own report.
- **Do not change what a slide says.** That is brief `0022`. If a slide is
  wrong, report it.
- **Nothing fetched at runtime.** Test it with the wifi actually off.
- **No JavaScript that matters.** Keys and the counter only. If the script fails,
  the slides must still be readable by scrolling.

## 7. Done when

- `slides.html` opens by double-clicking, **with the wifi off**, and every slide
  renders.
- Arrows and space move through all thirteen, both directions.
- `Cmd+P` gives one slide per page.
- **Every slide fits without shrinking the type.** Name any that do not.
- `build.py` regenerates it from `slides.md` in one command, and that command is
  in a comment at the top of the file.

**What would tell us it failed:** a slide only fits because the type got smaller,
or anything at all is fetched when it opens.

## 8. Checked by

`formwork check`.

The gate cannot see a slide deck. The evidence is section 9.

## 9. The report must contain

Short.

- **which slides did not fit**, if any. The most useful thing here
- confirmation it was opened with the wifi off and nothing was requested
- the command that rebuilds it
- any value `tokens.css` did not have

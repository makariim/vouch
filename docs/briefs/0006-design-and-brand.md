---
status: done
date: 2026-09-15
---

# 0006 — Design and brand

> **Wave 1, stream 1.** Runs at the same time as briefs `0007`, `0008`, `0009`.
> **You own `design/` and nothing else.** Do not touch `web/`, `src/`,
> `extension/`, or any document in `docs/`.

## 1. Goal

The tool works and looks like a form. It will be shown live to an interview
panel, and it currently gives away nothing about the care underneath it.

Produce a name, a mark, and a visual system — **and the assets to apply it**, so
two other sessions can drop it in without redesigning anything.

**If we do not do this:** the strongest thing about the product, that it refuses
to invent evidence, is presented in default system font on white.

## 2. What it is

An evidence audit for job seekers. It reads a job post and a resume, and for
every requirement says evidenced, partly evidenced, or not evidenced, quoting
the exact resume line. **It never claims anything the resume does not support.**

The feeling to design for: **a careful second opinion**, not a hype machine.
Closer to a legal or accounting tool than to a growth product.

Three verdicts carry the whole visual language. They must be distinguishable
**from two metres, at a glance, and to a colour-blind viewer** — so never colour
alone. Shape, weight or mark as well.

## 3. Scope

Use the `design` skill to produce a canvas. Artboards:

1. **The name.** Three candidates, one recommended. Short, sayable, not a pun on
   "resume". It will be said out loud in an interview.
2. **The mark.** Simple enough to read at 16px in a browser toolbar, because that
   is where it mostly lives.
3. **The page**, full width — job post and resume input, the three counts, the
   summary block (fit, blockers, undersells), and the requirement rows with their
   trace and quoted line.
4. **A requirement row**, close up, in all three verdict states plus mid-run.
5. **The extension panel**, 380px wide — fit call, blockers, strongest cards, and
   a button through to the full page. Small surface, most of the product.
6. **The toolbar badge**, in both states: no job post detected, job post detected.

**Then the part that matters more than the pictures:**

- `design/tokens.css` — **CSS custom properties.** Colour, type scale, spacing,
  radius, the three verdict states. This is what the other two sessions import.
- `design/README.md` — how to apply it, in one page.
- `design/assets/` — the mark as SVG, and a favicon.

**Out of scope:**

- writing or editing any application code
- illustration, marketing pages, a website
- animation beyond what makes a live trace readable
- dark mode, unless it costs nothing

## 4. Must not happen

- **No web fonts, no CDN, no external asset.** Decision `0002`: nothing leaves
  the machine, and the page must work with the wifi off. System font stacks only.
- **Do not rename anything in the code.** Propose the name; it is applied later.
- **Do not build a component framework.** Tokens and a stylesheet. The two client
  sessions have hours, not days.
- Do not design a feature that does not exist. The list is in `docs/standing.md`.

## 5. Done when

- All six artboards exist.
- `design/tokens.css` exists and **a stranger could apply it without asking a
  question.**
- The three verdicts are distinguishable in greyscale. Check it.
- The mark is legible at 16px. Check it at 16px, not scaled down on a canvas.
- One name is recommended, with the reason in a sentence.

**What would tell us it failed:** the other two sessions have to invent values
that are not in the tokens file, or the design cannot be applied without
rewriting markup.

## 6. Checked by

`formwork check` for the repository.

**Nothing can check a design.** The evidence is the tokens file being usable and
the greyscale test, which is why section 5 names both.

## 7. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- the three names, and which one is recommended and why
- what is in `tokens.css`, named
- **what the other two sessions must do to apply it** — the exact steps
- anything designed that the current backend cannot supply

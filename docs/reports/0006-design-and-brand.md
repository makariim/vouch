---
brief: 0006
date: 2026-09-15
---

# 0006 — Design and brand

The name is **Attest**. The tokens are in `design/tokens.css`. The canvas is at
https://claude.ai/artifact/JqaTgAP4sMMwUrNnwu25Pf

**The old palette failed the greyscale test** and four hex values had to move.
That is the one thing in here that changes somebody else's file.

## What changed

Everything is inside `design/`, except this report.

| File | Why |
|---|---|
| `design/tokens.css` | The deliverable. Colour, type, space, radius, the three verdicts, focus, layout. Every value carries its measured contrast in a comment. |
| `design/README.md` | How to apply it, in one page: what to import, a table mapping tokens onto the class names that already exist, and the three-signal verdict pattern. |
| `design/assets/mark.svg` | The mark. 16px grid, integer coordinates, `currentColor`. |
| `design/assets/favicon.svg` | The mark knocked out of a solid ground, for a tab and a toolbar. |
| `design/canvas/*.dc.html` | Six artboards. Source for the canvas. |
| `design/canvas/canvas.json` | Artboard layout and two sticky notes. |
| `design/canvas/.gitignore` | Ignores the 2.4 MB seeded canvas, which is a build artifact. Scoped to this folder so it cannot collide with the root file three other sessions share. |
| `docs/reports/0006-design-and-brand.md` | This. |
| `docs/briefs/0006-design-and-brand.md` | `status: open` → `done`. |

Nothing in `web/`, `src/`, `extension/` or `fixtures/` was touched.

## What was run

```
formwork/fw check                                    (twice — before and after)
node seed-canvas.mjs --template … --out …            wrote the seeded canvas
node seed-canvas.mjs --check attest-design-system.html
Artifact publish                                     → claude.ai/artifact/JqaTgAP4sMMwUrNnwu25Pf
```

Plus, in the scratchpad and not in the repository: three Python scripts that
computed contrast and L\*, and Chrome headless runs that rasterised the mark at
16px and rendered the verdict rows in greyscale.

Nothing was installed. Nothing left the machine except the canvas publish.

## The check

`formwork check` — **GATE: green. 12 checks**, each shown to reject the wrong
and accept the right. Green before the work and green after it.

```
ok config-shape   ok decision-ids  ok doc-links        ok generated-current
ok guard-wired    ok kit-integrity ok predictions-first ok role-shape
ok rule-labels    ok standing-current ok style-pointed  ok work-paired
```

## Git status

```
 M docs/briefs/0006-design-and-brand.md
?? design/
?? docs/reports/0006-design-and-brand.md
```

Nothing staged. (Plus the files other wave 1 sessions are changing, untouched
by this one.)

---

## The three names

| Name | Verdict |
|---|---|
| **Attest** | **Recommended** |
| Vouch | Runner-up |
| Margin | Third |

**Attest, because to attest is to state that something is true and stand behind
it — which is the single promise this tool makes and the one it refuses to
break.** Two syllables, one stress, no spelling it out down a phone line, and
it sits in the register of audit and law rather than growth.

Vouch is the same idea and warmer, but vouching is a favour, and this tool is
deliberately not doing you a favour — it will tell you no. Margin is the
careful reader's notes down the side of the page and matches the left rule the
whole interface is built on, but "margin" already means profit and error to
everyone in the room; it buys an explanation you then have to give.

**Nothing in the code was renamed.** The brief said propose, not apply.

## What is in `tokens.css`

Named, because the brief asked for them named.

- **Type** — `--font-sans`, `--font-mono`; ten sizes `--text-xs` (15px) to
  `--text-5xl` (44px); four weights `--weight-normal` (500) to `--weight-heavy`
  (800); four line heights; two letter-spacings.
- **Space** — `--space-1` (4px) to `--space-13` (96px).
- **Shape** — `--radius-sm/md/pill`, `--border-thin/thick`, `--rule` (10px).
- **Ink and ground** — `--ink`, `--ink-soft`, `--ink-faint`, `--ink-invert`,
  `--page`, `--panel`, `--line`.
- **The three verdicts**, four tokens each — `-ink`, `-surface`, `-edge`,
  `-fill` — for `--evidenced-*`, `--partly-*`, `--not-*`, plus `--working-*`
  for a requirement mid-run.
- **The fit call** from decision `0005` — `--fit-strong-*`, `--fit-worth-*`,
  `--fit-weak-*`.
- **Focus** — `--focus-ring`, `--focus-offset`.
- **Layout** — `--page-max` (1100px), `--panel-width` (380px), `--badge-size`
  (16px), `--tap-min` (44px).
- **Motion** — `--pulse-duration`, forced to `0s` under
  `prefers-reduced-motion`.

## What the other two sessions must do

Both, in order. Full detail with copy-paste CSS is in `design/README.md`.

1. **Add two lines to the page head** — the `tokens.css` link *above* your own
   stylesheet, and the favicon link.
2. **Delete the `:root` block at the top of `web/styles.css`.** Replace eight
   variable names using the table in the README: `--yes` → `--evidenced-ink`,
   `--yes-bg` → `--evidenced-surface`, and so on. `--ink`, `--ink-soft`,
   `--page`, `--panel` and `--line` keep their names. **Four hex values change**
   — see the failure below.
3. **Leave `VERDICT_MARK` alone.** `✓ – ✗` already satisfies "never colour
   alone", it is already shipped, and it costs nothing. The square marks on the
   artboards are an optional upgrade with copy-paste CSS in the README.
4. **Set the four row colours** from the tokens. Four one-line rules. This is
   the five-minute version and it is correct.
5. **Optional, and the only change needing new markup:** the textured left
   rules — solid, dashed, sparse, hatched. One `.rule` div and one `.body` div
   inside each `.req`.

Steps 1, 2 and 4 are the whole job. Nothing else in the markup changes, which
was the brief's stated failure condition.

## The two checks the brief named

**Greyscale — passed, after the palette was changed to make it pass.** Surfaces
sit on a lightness ramp, 96.7 → 90.5 → 83.8 L\*; pairwise separation 6.2, 6.7
and 12.9, all clearing 5. Verified twice: computed, then rendered in
`grayscale(1)` and looked at. In the grey render all four states stay
unambiguous from rule texture and mark fill alone.

**The mark at 16px — passed, at 16px.** Rasterised to a true 16×16 PNG with
headless Chrome and magnified nearest-neighbour, so what was judged was real
pixels rather than a scaled drawing.

## The three that matter

**Done but not asked for.**

- **A `.gitignore` in `design/canvas/`.** The seeded canvas is 2.4 MB of
  editor payload and regenerable. This repository goes on GitHub as an
  interview deliverable; a 2.4 MB build artifact in it is a bad first
  impression. Scoped to my own folder rather than the root file, because three
  other sessions are live in this tree.
- **`--working-*` and the fit tokens.** The brief named three verdict states.
  A requirement mid-run is a fourth thing the page must render, and decision
  `0005` adds the fit call. Both would otherwise have been invented by session
  `0009`, which is the failure the brief names.
- **The dashed and hatched rule textures.** The brief asked for shape as well
  as colour. Marked optional so it cannot block anyone.

**Asked for but not done.**

- **Dark mode.** Explicitly "unless it costs nothing". It does not cost
  nothing: the surface ramp is the mechanism that passes greyscale, and it
  would have to be re-derived and re-measured against a dark ground. Not done,
  and the README says so.

**Wrong in the brief.**

1. **The existing palette fails the brief's own greyscale test, and the brief
   assumed it would be kept.** `--yes-bg` and `--part-bg` in `web/styles.css`
   are **0.3 L\* apart** — the same grey. The inks are worse: `--yes` and
   `--part` are **0.6 L\* apart**. A colour-blind viewer, a greyscale
   projector, or the back of the room sees two of the three verdicts as one.
   The file's own header comment says "no grey on grey", so this was intended
   and missed. Four values moved to fix it, and the migration is one table.
2. **"Do not touch any document in `docs/`" contradicts sections 6 and 7**,
   which require a report in `docs/reports/` and the template requires flipping
   the brief's own `status`. Read the ban as covering other streams' documents
   and did both. Worth rewording for wave 2, since all four wave 1 briefs carry
   the same sentence.
3. **Artboard 3 asks for "job post and resume input", but decision `0005`
   replaced the resume textarea with stored resumes and a `resume_id`.** Drew
   the post as a textarea and the resume as a chosen stored file. Flagged
   rather than guessed.
4. **The mark channel already exists in the code.** The brief treats the
   three-verdict visual language as new; `app.js` has shipped `VERDICT_MARK`
   (`✓ – ✗`) since brief `0002`. So the cheapest correct change for wave 2 is
   smaller than the brief implies — keep the glyphs, add the rules.

## Designed that the backend cannot supply

Everything on the artboards is real except these. All four are `0007`'s work,
and if any slips, the design degrades to what exists rather than breaking.

- **`fit`, `fit_reason`, `blockers`, `undersells`** — decision `0005`, accepted
  today, not yet built. The summary block on artboards 3 and 5 renders all
  four.
- **`required: true/false`** — not rendered anywhere yet. The panel's
  "Blockers" list is only meaningful once a missing *preferred* item can be
  told from a missing *required* one.
- **The resume picker** — `GET /resumes` and friends, from `0005`.
- **The retry chip on artboard 4.** It has **never fired** in three real runs,
  which the standing brief calls the strongest thing to talk about. It is drawn
  because the design must not be the reason it cannot be shown. **It is drawn
  from the event shape, not from anything observed.**

One thing on the artboards is a sample value and should not be read as a
result: the counts **6 / 13 / 2**. They are the real numbers from the most
recent run, but extraction is not deterministic — 21, 23, 21 across three runs
— so the standing brief's rule holds: do not put a count on a slide.

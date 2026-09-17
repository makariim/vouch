---
status: done
date: 2026-09-17
---

# 0025 — Slides that look like slides

> **You own `docs/presentation/` and this brief's own report.** Nothing else.
>
> **Do not change one word of an argument.** Every sentence in `slides.md`
> stays. This brief is about which sentence is large and which is small.

## 1. Goal

`slides.html` renders. It fits. It fetches nothing. It is also four grey
paragraphs on black, every line the same size, with nothing to look at in the
first second.

**Brief `0023` asked for a file that renders. It never asked for a slide.** That
is the gap, and it is the director's, not that session's.

**If we do not do this:** a deck that reads as a text dump on a projector, for a
talk whose whole argument is that care was taken.

## 2. The diagnosis, in one line

**There is no headline.**

Slide 3 says this, in four equal paragraphs:

```
The obvious build: one model call, over the post and the resume together.
Then it says "yes, strong match on Kubernetes".
And you cannot tell whether the resume said it or the model wanted it to.
That is the whole problem. Everything else here is a consequence.
```

The third line **is** the argument. It is bold, and it is the same size as the
rest, so it reads as one paragraph among four.

**Almost every slide already has its headline. It is the bold line, and it has
nowhere to go.**

## 3. What a slide needs

Four parts, and not every slide uses all of them.

| Part | What it is |
|---|---|
| **Eyebrow** | small, uppercase, accent colour. The section — the `## Slide N — Title` text already there |
| **Headline** | **large and bold.** The argument, in one sentence. Read in one second |
| **Body** | smaller, quieter. Supports the headline |
| **Block** | optional: a table, or label-and-value rows with a coloured left rule |
| **Footnote** | optional: smaller and set apart. Sources, caveats, "this is a calculation not a bill" |
| **Number** | small, in a corner |

**The test:** look at a slide for one second and cover everything but the
headline. You should still know what the slide says.

## 4. How the source carries it

`slides.md` is prose today and has no way to say "this line is the headline."

**Give it one.** A convention or a marker — your call, and say which and why.
Whatever you choose:

- **it must not require rewriting the arguments.** Promoting the existing bold
  line is the expected move for most slides
- **`build.py` stays the only thing that writes `slides.html`.** Never
  hand-edit the output
- a slide with no headline must still render sensibly, not break

**Where a slide has no obvious headline, report it rather than inventing one.**
That is a content question for the director, not a layout decision for you.

## 5. What it must look like

**Use `design/tokens.css`.** The Vouch dark ground, the ink steps, the accent.

**Do not copy the reference deck the author showed.** It uses a gold accent and
belongs to another project. What is being borrowed is the **hierarchy**, not the
palette.

- the three verdict colours are already the product's language — the full, half
  and empty marks. Use them where a slide is about the three answers
- **no animation, no transitions, no build-ins.** They eat time and fail in
  front of people
- readable from the back of a room, and still readable in greyscale

## 6. What this also fixes

**Slide 7 overflows by 52px** and brief `0024` protected it from being trimmed.
With a real headline and body scale it should fit without losing a word. **If it
still does not, say so** — then it is a content cut and the director's call.

## 7. Must not happen

- **Do not touch any file outside `docs/presentation/`**, except this brief's
  own report.
- **Do not change, cut or reword an argument.** Promote, demote, and lay out.
- **Do not invent a design value.** `tokens.css` claims full coverage; report a
  gap rather than filling it.
- **Nothing fetched at runtime.** It still has to open from disk with the wifi
  off, and still print one slide per page.
- **Do not hand-edit `slides.html`.**

## 8. Done when

- Every slide has a headline you can read in one second from the back of a room.
- Eyebrow, headline, body and footnote are visibly different in size and weight.
- **All 17 fit.** Name any that do not.
- Opens from disk with the wifi off. `Cmd+P` still gives one slide per page.
- Greyscale still works.
- `build.py` regenerates everything in one command.

**What would tell us it failed:** a slide still reads as one block of even text,
or a slide only fits because the type got smaller.

## 9. Checked by

`formwork check`.

The gate cannot see a slide deck. The evidence is section 10.

## 10. The report must contain

Short.

- **how the source now marks a headline**, and why that way
- which slides had no obvious headline, if any
- confirmation all 17 fit, with the wifi off, and print one per page
- any value `tokens.css` did not have

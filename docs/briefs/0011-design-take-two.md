---
status: open
date: 2026-09-15
---

# 0011 — Design, take two

> **Brief `0006` over-specified.** It gave the mood, the layout, the artboard
> list and the visual metaphor, and got back something competent and safe.
>
> **This brief gives you the product and the flow. The look is yours.** Do not
> ask what it should feel like. Decide.

## 1. What to keep

**The name `Vouch`.** It is good. Change it only if you have something better,
and say why.

Everything visual is open. Start again if you want to.

## 2. What the product is

A person is applying for jobs. They paste a job post and give us their resume.

For every requirement in the post we say **evidenced**, **partly evidenced**, or
**not evidenced**, and quote the exact line of their resume that supports it.

**It never claims anything the resume does not support.** When there is no
evidence, it says so and quotes nothing. That refusal is the product.

It runs entirely on the person's own machine.

## 3. The flow, and the two surfaces

**Surface one — the extension.** They are scrolling a job board. The extension
notices a job post on its own. They want one thing: *should I bother with this
one?* Five seconds, then back to scrolling.

**Surface two — the page.** They have stopped on one job and want to work. Load
a resume, run the full audit, read the evidence, decide what to write.

## 4. What exists to show

This is the data. Nothing else exists, and everything here does.

**While it runs** — roughly sixty seconds, arriving live, requirement by
requirement:

- the list of requirements, each marked **required** or **preferred**
- what the agent is doing right now on each one: searching (and the terms it
  chose), judging, verifying a quote, or going back to search again
- a verdict per requirement: one of the three, the quoted resume line, its line
  number, and one sentence of reasoning

**When it finishes:**

- three counts
- **fit** — one of strong / worth applying / weak, plus one sentence
- **blockers** — required things with no evidence
- **strengths** — the best evidenced lines, to lead with
- **undersells** — *you have this, your resume states it too weakly.* **This is
  the most valuable thing the product produces**
- sometimes an error instead

**In the extension, before any of that:** an instant local signal — how many
requirements look plausible, computed in milliseconds with no model call.

**Also:** a stored resume with a name and a page count, and the ability to see it
the way the tool sees it, line by line, numbered.

## 5. Three moments worth designing for

- **It is thinking, and it takes a minute.** Somebody is watching it work. That
  minute is either interesting or it is a spinner.
- **It goes back and searches again**, having decided the evidence was thin. It
  is the only moment the thing visibly makes its own decision.
- **It finds nothing, and says so.** No quote, no hedge. Every other tool in
  this space would have written something.

## 6. Hard constraints, all technical

These are not taste. Breaking one breaks the product.

- **Nothing loads from the internet.** No web fonts, no CDN, no hosted asset. It
  must work with the wifi off. System font stacks or nothing.
- **The extension panel is about 380px wide.** Chrome decides that, not us.
- **The mark appears at 16px in a browser toolbar.** That is its main home.
- **The three verdicts must be tellable apart without colour** — greyscale, and
  colour-blind. Use shape or mark as well. This is accessibility, not style.

## 7. What to hand over

The pictures are not the deliverable. **Two other sessions have to apply this in
hours, without asking a question.**

- **`design/tokens.css`** — CSS custom properties. If they have to invent a value
  that is not in here, this brief failed.
- **`design/README.md`** — how to apply it. One page.
- **`design/assets/`** — the mark, and a favicon.

## 8. Must not happen

- Do not write or edit application code. Other sessions own `src/`, `web/`,
  `extension/`.
- Do not design a feature that is not in section 4. There is no data for it.
- Do not build a component framework. Tokens and a stylesheet.

## 9. Done when

- Both surfaces are designed, including the three moments in section 5.
- `design/tokens.css` exists and a stranger could apply it.
- The three verdicts survive a greyscale test. Check it, do not assume it.
- The mark is legible at 16px. Check it at 16px.

**What would tell us it failed:** it looks like the last one, or the other
sessions have to invent values to apply it.

## 10. Checked by

`formwork check` for the repository.

Nothing can check a design. The evidence is the greyscale test, the 16px test,
and the tokens file being usable.

## 11. The report must contain

- what you changed from take one, and why
- what is in `tokens.css`
- **the exact steps** the page and extension sessions follow to apply it
- anything you designed that section 4's data cannot supply

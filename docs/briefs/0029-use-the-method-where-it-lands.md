---
status: open
date: 2026-09-17
---

# 0029 — Use the method where it lands

> **You own `docs/presentation/`, this brief's own report, and this brief's
> status line.** Nothing else.
>
> **No new slide.** Three edits. If it grows past them, stop and say so.

## 1. Goal

Slide 13 covers the method well, and slide 16 already closes on the through-line
— *Vouch refuses to claim what it cannot evidence; the method refuses to let a
turn end on a red check.*

**What is missing is the Professional Services argument**, which is a different
point from either: how the method changes what a customer is left holding.

The assignment asks *"how would you apply this thinking to solve a DataRobot
customer's problem?"* The method is a direct answer and the deck never makes it.

**If we do not do this:** the strongest PS-specific sentence available goes
unsaid, in the criterion the role is built around.

## 2. Edit one — a row on slide 16

Slide 16 has three rows: `WHAT ALREADY WORKS`, `THE BUSINESS CASE`, `WHAT IT
DOES NOT HAVE`.

**Add a fourth**, in the deck's own voice. The point it has to make:

> A Professional Services engagement is judged by what the customer's team can
> run after you leave. Briefed before it starts, decisions written down with the
> reason, reports that say what went wrong — that record is the handover, and it
> exists because the method demanded it rather than because somebody remembered
> at the end.

**One row. Two sentences at most.** Label it for what it is — how the work is
delivered, not how the product scales.

Nothing else on slide 16 moves. The closing headline and the through-line stay
exactly as they are.

## 3. Edit two — ten seconds in the demo

The demo shows the product and never shows the repository.

**Add one step**, after the audit finishes and before the closing, in
`demo-script.md`:

- open `docs/decisions/` on screen
- one sentence: eight numbered records, every choice has one, with the reason
- **ten seconds.** Then move

**Evidence beats a slide about evidence.** This costs no slide time and it is
the only moment in fifteen minutes where the panel sees the thing itself rather
than a claim about it.

**Put it in "When it breaks" too:** if the demo has gone badly, this is a safe
ten seconds that cannot fail — it is a folder.

## 4. Edit three — one row in the questions table

Somebody will ask whether the method is available.

Add a row: **"Is that method open source?"** → it is published as `formwork-kit`.

Nothing more. It is an answer, not an opening.

## 5. Must not happen

- **Do not add a slide.**
- **Do not change slide 13**, or slide 16's headline, or the through-line.
- **Do not let the method become the subject.** The talk is about Vouch. Every
  mention of the method is evidence for a claim about Vouch or about how he
  works — never a product in its own right.
- **Do not claim adoption, users or results for it.** It is published. That is
  all that is known.
- Nothing outside `docs/presentation/`, except this brief's report and status.
- **Do not hand-edit `slides.html`.** `build.py` writes it.

## 6. Done when

- Slide 16 has a fourth row making the handover argument, and still fits.
- The demo script has the ten-second `docs/decisions/` step, in the run and in
  "When it breaks".
- The questions table has the open-source row.
- All 16 slides still fit. Nothing fetched. Still prints one per page.

**What would tell us it failed:** slide 16 runs over, or the method starts
reading as the thing being presented.

## 7. Checked by

`formwork check`.

## 8. The report must contain

Short.

- the fourth row, quoted
- where the ten seconds sits in the script, and what it costs the clock
- confirmation slide 16 still fits

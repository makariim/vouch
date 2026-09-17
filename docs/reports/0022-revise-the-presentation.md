---
status: open
date: 2026-09-17
brief: 0022-revise-the-presentation
---

# 0022 — Revise the presentation

**The deck was not read aloud against a clock, so it has no timing.** That is
the one thing in section 5 this session could not do, and the rest of the report
is worth less because of it. Everything else in the brief is done.

## What it timed at

**Nothing. It was never spoken.** An agent cannot read a deck aloud, and an
estimate dressed up as a timing would be exactly the thing slide 13 now refuses
to do about cost.

What was measured instead is the demo script's **spoken words** — the
blockquoted lines, which are the only sentences in the deck written to be read
out. At 140 words a minute:

| | spoken words | at 140 wpm | budget |
|---|---|---|---|
| part one, the extension | 93 | 40s | 45s |
| part two, the page | 267 | 114s | 255s |

Part two's remaining 140 seconds are the run itself — about ninety seconds of
streaming, plus pointing and pauses. Both parts fit **on paper**.

**This does not establish the fifteen minutes.** Slides 1–3 and 10–14 have no
script at all; the speaker talks over them, and how long that takes is unknown.
The rehearsal is still the only thing that can answer it, and it remains item 1
and item 3 of `standing.md`.

## What was cut to make room

One slide was added, so time came off the last part of the deck:

| Part | before | after |
|---|---|---|
| How it works | 4 min | 4½ min |
| What it got wrong, and what is next | 3 min | 2½ min |

Nothing was deleted. The half minute is affordable because slide 13's cost item
shrank from a stance — *"I will not estimate it at you"* — to a number and one
sentence about what kind of number it is.

**The demo keeps its five minutes**, split 45 seconds for the extension and the
rest for the page. The extension's time is not new time; it comes out of the
page's share, which had slack — its optional step 7, "Look again at this one",
was already written to be dropped at four minutes.

## Where the reading-order result went, and why

**A new slide 7, immediately after slide 6. Not folded in.**

Slide 6 was left untouched, as the brief required. It is the cleanest slide in
the deck and its three lines carry the whole guarantee; a five-column table
underneath them would have buried it.

The new slide opens by naming its parent — *"Slide 6 says the quote has to be a
real line"* — and then draws the consequence: if the quote must be a real line,
how the file is cut into lines decides the answer. It is the only table in the
deck, and it is labelled **16 September**, per the rule about numbers on slides.

Slides 7 through 13 became 8 through 14. The two references to slide numbers in
the demo script were moved with them.

## What else in the deck was no longer true

- **The name on slide 1** was Muhammad Elsherif. It is now Muhammad Abdulkariim,
  matching the resume they will be reading.
- **Cost on slide 13** said NOT ESTABLISHED. It now says 47 model calls, about
  17,000 tokens, under half a cent, and — in its own paragraph — that this is a
  calculation from token counts against a price list, not a metered bill.
- **The cost question** in the demo script's question table said *"do not
  estimate"*. Same replacement.
- **The cost line spoken over the run** said *"a fraction of a cent"*. It now
  says the number and says what kind of number it is.
- **The extension appeared zero times.** It is now part one of the demo, with
  Brave and the "… more" click both written into the pre-flight as rows 10–13,
  and with an honest closing line about the careers page where it read four
  lines and reported a number anyway — item 9 of `docs/future.md`.

## The new failure rows

The demo grew a step, so "When it breaks" grew two rows. Every existing row is
untouched.

Both new rows say the same thing: **drop part one and go to the page.** The
extension is a word match with no model call and no network, so the only ways it
can fail are Brave refusing the unpacked extension or the server being down —
and neither is worth more than the 45 seconds already budgeted.

## Checked by

`formwork check` — green, 12 checks.

Nothing there can check a presentation. The only real evidence would have been
the timing, and there is none.

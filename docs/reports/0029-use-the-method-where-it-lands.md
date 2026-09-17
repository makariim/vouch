---
status: open
date: 2026-09-17
brief: 0029-use-the-method-where-it-lands
---

# 0029 — Use the method where it lands

**Three edits, no new slide. Slide 16 grew from 539px to 625px and still has
107px of headroom. All 16 slides fit, nothing is fetched. Gate green.**

## The fourth row, quoted

On slide 16, last in the stack, after `WHAT IT DOES NOT HAVE`:

> **WHAT THE CUSTOMER KEEPS** :: A Professional Services engagement is judged
> by what the team can run after you leave. The briefs, the decisions and the
> reports are that handover — written as the work happened, because the method
> demanded it.

Two sentences. The label names the delivery, not the product, which is what
separates it from `THE BUSINESS CASE` two rows above.

**The subject stays Vouch.** The row's subject is the customer's team and what
they are left holding; the method appears once, in a subordinate clause, as the
reason the record exists. It claims no adoption, no users and no results.

It went last on purpose. The stack now ends on what the customer keeps and hands
straight to the closing line about the method refusing a red check, which was
already there and did not move.

## Where the ten seconds sits, and what it costs the clock

`demo-script.md`, **part two, new step 7** — after step 6 finishes the run and
shows the three counts, before the optional "Look again at this one", which is
renumbered 8.

It is in the run, not in the optional tail. Leaving the browser, the folder, one
sentence naming eight numbered records and the reason each carries, then move.
It says explicitly not to open a file and not to read a title out.

**The clock.** It costs the demo ten seconds of its five minutes and costs slide
time nothing — no slide was added and the 14½-minute budget in `slides.md` is
unchanged. The ten seconds comes out of the page's share, which is where the
declared slack already was: step 8 is marked optional and "skip this if you are
at four minutes". So the order to drop under pressure is step 8 first, and this
step is cheap enough to survive it.

**One thing the step carries that the brief did not specify:** it says to have
the folder window open behind the browser beforehand. Without that it is a hunt
on stage, and the prep table says "no terminal on screen". I put it inside the
step rather than adding a fourteenth prep row, because a prep row would have
been a change the brief did not ask for.

**In "When it breaks"** there is now a row: the demo has gone badly and you need
ground back → `docs/decisions/`, step 7, ten seconds that cannot fail, because
it is a folder and not a running thing.

## The open-source row

In the questions table, directly after "Did you write this, or did the agents?",
which is the only other place the method comes up:

> "Is that method open source?" → Yes — it is published as `formwork-kit`.
> **One sentence, then stop.** It is an answer, not an opening — do not claim
> anybody else uses it.

`formwork-kit` is the name the kit's own `formwork/troubleshooting.md` installs
under, so the claim is checkable rather than remembered.

## Confirmation slide 16 still fits

Measured with `build.py`'s own probe, before and after, headless at 1600×900:

| | slide 16 needs | of | headroom |
|---|---|---|---|
| before | 539px | 732px | 193px |
| after | **625px** | 732px | **107px** |

`fit: all 16 slides fit at 1600x900, type unchanged`, and `fetched by the page:
0 (nothing)`. Type was not shrunk and no slide was added — still 16, still one
per page.

**107px is the tightest slide in the deck now.** Slide 8 was the previous
tightest at 146px. Anything further added to slide 16 should be measured, not
estimated.

## What changed

- `docs/presentation/slides.md` — one row on slide 16.
- `docs/presentation/demo-script.md` — new step 7, the old step 7 renumbered 8,
  one row in "When it breaks", one row in the questions table.
- `docs/presentation/slides.html` — rebuilt by `build.py`. Not hand-edited.

## What was run

```
python3 docs/presentation/build.py --check     (twice: baseline, then after)
formwork check
```

## The check

`formwork check`: **green.** 12 checks, each shown to reject the wrong and
accept the right.

## Git status

```
 M docs/presentation/demo-script.md
 M docs/presentation/slides.html
 M docs/reports/0029-use-the-method-where-it-lands.md  (new)
 M docs/briefs/0029-use-the-method-where-it-lands.md   (status line)
```

`slides.md` is **not** listed, and that needs explaining — see below.

## The three that matter

**Done but not asked for.** Nothing beyond the three edits. The readiness
sentence inside step 7 is the one addition, argued above.

**Asked for but not done.** Nothing.

**Wrong in the brief.** Nothing wrong in it. Two things it could not have known:

- **A commit landed mid-session.** `309d8d1` "Read GROQ_API_KEY from .env, and
  finish the deck" was made while this brief was being worked, and it swept up
  the slide 16 row in `slides.md` — but **not** the rebuilt `slides.html`, which
  was still being measured. So that commit's tree has a `slides.html` one row
  behind its `slides.md`. The working tree is consistent and `generated-current`
  is green; the staleness is inside that one commit, and it is yours to resolve
  since the agent does not write to version control.
- **Slide 13's document counts have drifted.** It reads "26 briefs, 8 decisions,
  24 reports"; the repository now holds **29 briefs, 8 decisions, 27 reports**
  including this one. The brief forbade changing slide 13, so it was not
  touched. It is a small number said out loud next to a folder the panel can now
  see on screen, which is exactly the pairing that invites someone to count.
  Worth its own one-line brief before the rehearsal.

---

## Correction — 17 September

**Two director's rulings landed after this report was written.** The paragraph
above about slide 13 stands as it was written, and is now out of date. It is
left in place rather than rewritten, because what it recorded was true when the
work stopped and the correction is the part worth reading.

**Slide 13's counts were replaced, not left alone.** Where the report says the
drift was "worth its own one-line brief before the rehearsal", the ruling went
further and removed the reason to count at all:

> `docs/` is the handover:
> a brief, a decision record and a report for every piece of work.

The rule is stronger than the count, and it cannot go stale. That matters more
now that edit two puts `docs/decisions/` on screen next to a spoken number.

**Slide 13's other number was dated rather than removed.** "18 of 22 reports
name something the brief got wrong" is a measurement of a sample, not an
inventory of a folder, so the fix is different: its footnote now reads
*"Counted 17 September, in report `0024`."* Dating it makes it permanently
true. That is the treatment slide 9 already gives its own counts, and slide 6
its table.

**Measured after both rulings:** slide 13 is **unchanged at 539px of 732px,
193px of headroom**. Neither edit cost it a pixel — the replacement line wraps
to the same two lines as the counts it replaced, and the lengthened footnote
still fits on one. All 16 slides fit at 1600×900, nothing fetched, type
unchanged. `formwork check` green.

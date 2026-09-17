---
status: done
date: 2026-09-17
---

# 0026 — The deck has to tell a story

> **You own `docs/presentation/` and this brief's own report.** Nothing else.
>
> **This is a rewrite of the writing, not of the facts.** Every number, every
> finding and every honest limitation stays. What changes is the order, the
> sentences, and the shape of a slide.
>
> **Read `~/Downloads/enterprise-brain-v6.html` first.** It is the standard.
> Study what it does, not what it says — it belongs to another project.

## 1. Goal

The deck is accurate, sourced, honest, and it does not land. The author has said
so twice.

Three things are wrong and they are all the director's:

1. **It has no story.** It is a tour of a system. The headlines do not chain.
2. **The English is clever instead of plain.** Aphorisms you have to decode.
3. **Slide 1 never says what Vouch is.**

**If we do not do this:** fifteen minutes of true statements that nobody can
follow, for four criteria that are all about whether he can explain things.

## 2. What the reference does, and this must do

**Read only the headlines and you should get the whole argument.** In the
reference they chain:

> the layer everyone is racing to build is free → every vendor sells the same
> layer and keeps nothing → two of four ontology layers are free, two are not →
> the schema was never the hard part, the mapping is → nobody fills the model
> automatically → most of this is free, we build the missing part

**Its sentences are short and plain.** *"The schema was never the hard part.
The mapping is."* Subject, verb, object. No decoding.

**Its slides are labelled blocks, not paragraphs.** `THE PRODUCTS / THE RESULT /
THE REASON / THE FIX`. `GAP 1–4`. `WE REUSE / WE BUILD`. `1 · ARRIVE / 2 · FILL
/ 3 · TUNE`.

**Its claims carry sources**, and where there is no number it says so as a
strength: *"We are deliberately not putting a percentage on this slide.
Measuring it is the point."*

## 3. The spine — the argument, in order

**This is the director's proposal. Follow it unless you have a better one, and
say so if you do.** Each headline must follow from the one before.

| | The slide argues |
|---|---|
| 1 | **What Vouch is**, in two sentences. It checks every requirement in a job post against one line of your resume — or says it cannot |
| 2 | A job post asks twenty-odd things. Nobody checks them. The guess is the product |
| 3 | The obvious build is one model call — and then you cannot tell whether the resume said it or the model wanted it to |
| 4 | So the model never writes the answer. It returns a line number |
| 5 | **DEMO** |
| 6 | Which is why how the file is cut into lines decides the answer |
| 7 | And why this is an agent: it has tools, it takes steps, it goes back on its own |
| 8 | These libraries, and not the other four, because the audit is a cyclic graph with a decision in it |
| 9 | What it got wrong: a trigger nobody could check, which fired zero times |
| 10 | The fix: it fired three times, nobody pressed anything |
| 11 | Three more things are wrong, and all three were found by running it |
| 12 | What I learned: almost every model problem was a data problem |
| 13 | How it was built: I directed agents, under a method I wrote |
| 14 | **What this actually is**: auditing a document against a rulebook, with cited evidence |
| 15 | Why that is commercial: "it cannot fabricate a citation" is what makes a model usable in a regulated industry |
| 16 | Scaling it, honestly — what works, and what it would need |

**Sixteen, not seventeen.** Merging is expected where two slides make one point.

**The demo keeps its five minutes.** The talk is 14½ and questions are after the
fifteen — that ruling is already in the file and stands.

## 4. How to write a sentence here

`design/README.md` already sets these rules for the product. **The deck has not
been following them.**

- **Short sentences. One idea each.** Subject, verb, object.
- **Common words.** If a word has a simpler twin, use the twin.
- **No aphorisms.** *"The guess is the product. Not the writing — the checking."*
  is clever and it costs the room three seconds. Say it plainly.
- **No sentence a listener has to decode.** If it needs a pause to parse, rewrite
  it.
- Read every line out loud. If you stumble, it is wrong.

**The author reads English as a second language.** So does at least one person
in most rooms.

## 5. How to build a slide

**Eyebrow · headline · labelled blocks · footnote.**

**Prefer labelled blocks to paragraphs.** Most slides have two to four parts and
each part has a name. `WHAT IT DID / WHAT IT COST / WHAT I CHANGED`. Name them.

**Put the source under the claim.** The reports are in `docs/reports/` and the
decisions in `docs/decisions/`. A footnote citing `report 0020` is stronger than
a bare number.

**Where there is no number, say so with confidence.** Cost is a calculation, not
a bill. Accuracy has no gold set. Extraction is not deterministic. Those are
strengths, said plainly.

## 6. The accent

**There is no accent a deck may use, and that is why it looks pale.** The
session that found this was right to refuse the verdict colours — borrowing
"partly evidenced" amber for a rule would teach the room the wrong thing twenty
minutes before the demo uses it for real.

**So add one, declared deck-only.** One hue, not green, amber, red or rose. It
marks eyebrows, block labels and the one line per slide that matters.

**Put it in `docs/presentation/` as a deck-local token with a comment saying it
is deck-only and why.** Do not edit `design/tokens.css` — that file belongs to
the product.

The three verdict colours still appear exactly where they mean what they always
mean.

## 7. Must not happen

- **Do not touch any file outside `docs/presentation/`**, except this brief's
  own report.
- **Do not change a fact, drop a limitation, or soften an admission.** Slides 9
  to 12 in the new order are why the rest is believable.
- **Do not add a claim without a source** in `docs/`.
- **Do not promise a count.** Extraction is a model call.
- **Do not copy the reference's palette, wording or subject.** Its hierarchy and
  its plainness, nothing else.
- **Do not hand-edit `slides.html`.** `build.py` writes it.
- Nothing fetched at runtime. Still opens from disk, still prints one per page.

## 8. Done when

- **Reading only the headlines gives the whole argument**, in order, with no
  gaps. Paste them into the report so it can be checked.
- **Slide 1 says what Vouch is** and a stranger would understand it.
- No sentence needs decoding. Read the deck out loud once, end to end.
- Every slide is eyebrow, headline, and named blocks — not paragraphs.
- The deck has one accent, deck-only, and it is not a verdict colour.
- All slides fit. Nothing fetched. Prints one per page.

**What would tell us it failed:** the headlines still read as a table of
contents rather than an argument.

## 9. Checked by

`formwork check`.

Nothing can check whether a talk lands. The evidence is the headline chain in
section 10, read on its own.

## 10. The report must contain

- **every headline, in order, as one block** — so the chain can be read
- what was merged or dropped, and why
- the accent you chose
- any sentence you could not make plain without losing the fact

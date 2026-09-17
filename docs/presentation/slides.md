---
status: draft
date: 2026-09-17
brief: 0026-the-deck-tells-a-story
---

# Slides — Vouch

Fifteen minutes, DataRobot Professional Services.

**How to use this file.** One `---` block is one slide. Nothing on a slide is
read out; the words to say are in
[`demo-script.md`](demo-script.md). If a line here cannot be read from
the back of the room, it is too long — cut it, do not shrink it.

**The headlines are the argument.** Read every `#` line in this file, in order,
and you get the whole talk. If a headline does not follow from the one before
it, that is a bug in the deck, not in the reading.

**How a slide is written.**

| In this file | On the slide |
|---|---|
| `## Slide N — Title` | the eyebrow, small and quiet above the headline |
| `## Slide N` alone | no eyebrow |
| `# …` | the headline. The argument, read in one second |
| `LABEL :: text` | a labelled block. A run of them is one stack |
| `==text==` | the accent. **One per slide**, on the line that matters |
| `> …` | the footnote — a source, a date, a caveat |

**How to write a sentence here.** Short. One idea each. Common words. Nothing
the listener has to decode. Read it out loud; if you stumble, it is wrong. The
room includes people reading English as a second language, and so does the
author.

**Two rules that override everything below.**

- No requirement count and no verdict count appears on any slide. Extraction is
  not deterministic: the same post gave 21, then 23, then 21. Numbers on slides
  are only for runs that already happened, and they are labelled with the date.
- `rank_bm25` is a library. So are LangGraph, FastAPI and Groq. Say "library"
  out loud every time one is on screen.

**The shape and the clock.**

| Part | Slides | Minutes |
|---|---|---|
| What it is, and why the obvious build is wrong | 1–4 | 1½ |
| The live demo | 5 | 5 |
| Why it behaves the way it does | 6–8 | 2 |
| What it got wrong | 9–11 | 1½ |
| What I learned, and how it was built | 12–13 | 2 |
| What this really is, and where it goes | 14–16 | 2½ |

**Fourteen and a half minutes. Questions are after the fifteen, not inside it.**

If the panel wants questions inside the fifteen there is half a minute, which is
nothing. In that case cut slide 8 — its argument becomes one spoken sentence
over slide 7 — and fold slide 12 into slide 14. That buys a minute and a half.

**Do not buy time from the demo, and do not buy it from slides 9 to 11.** The
honesty is why the last three slides are believable.

**This clock is a budget, not a measurement.** Nothing here has been spoken
against a stopwatch. That is still item 1 of `docs/standing.md`.

---

## Slide 1

# Vouch checks a resume against a job post, one requirement at a time.

For each thing the post asks for, it finds the line of the resume that proves
it. If there is no such line, it says so.

> Muhammad Abdulkariim · DataRobot Professional Services

---

## Slide 2 — The problem

THE POST :: A job post asks for twenty-odd separate things.
THE READER :: A person reads it once and forms an impression.
THE ANSWER :: "I think I am a good fit." Nothing was checked item by item.

# Nobody checks a job post. They read it once and guess.

I built this because I am job hunting. ==The demo runs on your job post.==

---

## Slide 3 — Why the obvious build is wrong

THE BUILD :: One model call. The post and the resume go in together.
WHAT IT SAYS :: "Yes. Strong match on Kubernetes."
THE PROBLEM :: The resume may not say Kubernetes anywhere.

# One model call answers. Nothing shows where it came from.

==You cannot tell if the resume said it, or the model made it up.==
Everything else in this project follows from that one sentence.

---

## Slide 4 — How the answer is made

THE RESUME :: Never pasted into the prompt. It is split into numbered lines, and the agent searches it.
THE MODEL :: Sees the six lines it asked for. Not a document it can drift over.
WHAT IT RETURNS :: A line number and a verdict. No text of its own.
THE QUOTE :: Read back out of the file at that number, after the model is finished.

# So the model never writes the answer. It returns a line number.

==The model has no way to write a quote. So it cannot invent one.==

> Decided before the code was written: decision `0001`.

---

## Slide 5

# DEMO

FIRST :: The extension, on a real job post. 45 seconds.
THEN :: The page, for the rest of the five minutes.

Nothing on this slide is read out. The clicks are in `demo-script.md`.

---

## Slide 6 — Reading the file

A quote has to be a real line. So where the lines break is not a detail. It is
the answer. Two readers, same PDF: file order, or position on the page.

| 16 September | lines | evidenced | partly | the call |
|---|---|---|---|---|
| `pypdf` | 160 | 3 | 17 | **weak** |
| `pdfplumber` | **51** | **6** | **13** | **worth applying** |

# So how the file is cut into lines decides the answer.

The verdict changed. Nothing about the model did.

> Same resume, same post, same model. Runs minutes apart. Report `0020`.

---

## Slide 7 — Why this is an agent

# It is an agent for three reasons. Calling a model is not one of them.

IT HAS TOOLS :: It writes its own search terms, one requirement at a time.
IT TAKES STEPS :: It keeps state between them. The loop counts requirements, not model turns, so nothing stops early.
IT GOES BACK :: Up to three searches, and ==it chooses when the first one found nothing.==

---

## Slide 8 — Why LangGraph, and not the other four

# LangGraph, because the audit goes back.

```
extract → search → judge → verify ─┬→ retry ──→ search
                                   └→ advance → next requirement → report
```

THE DECISION :: An edge in the graph, not an `if` inside a node.
THE CHECK :: `verify` always runs. It is not the model's call.
THE TRACE :: LangGraph streams state node by node. ==The trace is the demo.==
THE REST :: FastAPI, `rank_bm25`, Groq — libraries. **Not my code.**

> Over LangChain, CrewAI, Pydantic AI, LlamaIndex — and DSPy ReAct. Decision `0001`.

---

## Slide 9 — What it got wrong

THE OLD TRIGGER :: Go round again when the model reports its own evidence as weak.
WHAT HAPPENED :: Nothing. 0 of 21, 0 of 23, 0 of 21.
THE BAD PART :: It stayed silent on verdicts that were wrong — where the model's own written reason said "does not mention".

# The old retry asked the model to grade itself. It never fired.

> Three real runs, 15 September. Decision `0007`.

---

## Slide 10 — The fix

# It fired three times. Nobody pressed anything.

THE NEW TRIGGER :: A first pass that found nothing, or a quote that failed its check. ==Both are things I can see in the data.==
WHAT IT MOVED :: One answer went from not evidenced to evidenced, on a line that was checked.
WHAT I WATCHED FOR :: No second pass talked itself into a match. Three stayed negative.

> Same post, 15 September. Report `0005`.

---

## Slide 11 — Three more things that are wrong

RANKING :: Retrieval used to rank by word count, so `python` beat `fastapi`. It reported a gap that was not a gap. Fixed with BM25 — `rank_bm25`, **a library, not my code**.
THE MIDDLE :: About 60% of answers land in "partly evidenced". It absorbs both ends. Known, not solved.
NO BUDGET :: Three searches per requirement is capped. How many requirements retry is not. One resume retried on 6 of 6.

# All three were found by running it, not by reading it.

> Reports `0004`, `0021` and `0012`.

---

## Slide 12 — What I learned

# Almost every model problem turned out to be a data problem.

THE PDF :: How the file was read moved the verdict from weak to worth applying. Slide 6.
RETRIEVAL :: Better ranking closed a gap that was not a gap.
LINE BREAKS :: Repairing them removed a false finding.

==The model never changed. Not once.== That is the thing I would carry into a
customer deployment.

---

## Slide 13 — How it was built

# I built this by directing agents, under a method I wrote first.

THE LOOP :: Brief, work, check, report, stop. Every piece, every time.
THE GUARDRAILS :: They refuse, not advise. A turn cannot end on a red check.
WHAT IT CAUGHT :: 18 of 22 reports name something the brief got wrong.
WHAT IT MISSED :: The planning role offered to build, four times. ==I caught it, not the kit.==

I briefed it, I read every report, I rejected work. `docs/` is the handover:
26 briefs, 8 decisions, 24 reports.

> `FORMWORK.md`, at the root.

---

## Slide 14 — What this really is

# This is not a resume tool. It audits a document against a rulebook.

THE RULEBOOK :: A job post. Or a policy, a tender, a regulation.
THE DOCUMENT :: A resume. Or a contract, a filing, a submission.
THE OUTPUT :: One verdict per item, each carrying the line it came from — ==or it says there is none.==

I have shipped this shape before: a bilingual compliance engine, auditing
documents against an uploaded rulebook, for regulated customers.

---

## Slide 15 — Why that is commercial

THE QUESTION :: Every pilot dies on one sentence. "How do I know it did not make that up?"
PROMPTING ANSWERS IT :: With a probability. The model is told to behave, and usually does.
THIS ANSWERS IT :: With architecture. The model cannot write text at all.

# "It cannot invent a citation" is what makes a model usable in a regulated industry.

==A guarantee you can point at beats a number you have to trust.==

---

## Slide 16 — Scaling it, honestly

WHAT ALREADY WORKS :: One document, one graph run, nothing shared. It is parallel by construction.
THE BUSINESS CASE :: A free local screen decides whether a paid call is worth making. At ten thousand documents, that is the whole argument.
WHAT IT DOES NOT HAVE :: An evaluation set with gold answers. Measured token cost. Durable orchestration. A human review gate. Per-tenant isolation.
WHAT THE CUSTOMER KEEPS :: A Professional Services engagement is judged by what the team can run after you leave. The briefs, the decisions and the reports are that handover — written as the work happened, because the method demanded it.

# Make the guarantee structural, not a promise.

Vouch refuses to claim what it cannot evidence. The method refuses to let a turn
end on a red check.

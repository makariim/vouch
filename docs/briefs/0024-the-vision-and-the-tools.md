---
status: done
date: 2026-09-17
---

# 0024 — What the presentation does not say

> **You own `docs/presentation/` and this brief's own report.** Nothing else.
>
> **Run after `0022`.** If `0023` has built `slides.html`, rebuild it after this.
>
> **This is a revision.** Slides 6, 7, 10 and 11 are the best of it. Do not
> touch them.

## 1. Goal

The deck was audited line by line against the assignment email. It is strong on
*how it works* — five slides — and near silent on six things the email either
names outright or scores.

**If we do not do this:** the strongest arguments go unsaid in the criteria the
role is built around, and the talk ends on an apology.

## 2. The six gaps, biggest first

### Gap 1 — The Vision. Named in the email, absent from the deck.

> *"How would you apply this thinking to solve a DataRobot customer's problem?
> How could a solution like this be scaled and productized?"*

"customer", "scale", "productize" and "DataRobot" appear **twice in fourteen
slides.** Slide 13 is product roadmap, not customer vision.

**The material:**

**The generalisation.** This is not a resume tool. It is **auditing a document
against a rulebook and returning a per-item verdict with cited evidence** — and
refusing to cite what is not there. A job post is a rulebook. A resume is the
document. Swap them and it is a contract against a policy, an RFP response
against a tender, a filing against a regulation, a vendor's answers against a
control framework.

**Why it is the enterprise blocker.** Every enterprise GenAI pilot dies on the
same sentence: *"great demo, how do I know it didn't make that up?"* The usual
answers are probabilistic — careful prompting, a measured hallucination rate —
and neither survives a compliance officer. **This answer is architectural: the
model has no channel to emit text.** That is the difference between a pilot and
a contract.

> "It cannot fabricate a citation" is not a feature. It is what makes a language
> model usable in a regulated industry at all.

**Why he is credible saying it.** From his own resume, verbatim in substance:
he designed and built a bilingual compliance engine that audits a submitted
document against an uploaded rulebook and returns a per-rule verdict with cited
evidence, in Arabic and English, for government and regulated customers. **He
has shipped this shape before.** Say so.

**Scaling, honestly.** It is parallel by construction — one document, one graph
run, nothing shared. **The two speeds are the unit economics**: a free local
screen decides whether a paid call is worth making, which at ten documents is a
nicety and at ten thousand is the whole business case.

**And what it would need, said out loud:** an evaluation set with gold answers
so accuracy is a number; recorded token usage so cost is measured not
calculated; durable orchestration; a human review gate; per-tenant isolation.
**"Here is what it does, here is what it would need, and I know the difference"
is the Professional Services answer.** Claiming it is ready is not.

### Gap 2 — Why is this an agent? The assignment is called "Build an AI Agent".

The deck says graph, node, conditional edge. It never says the word, or answers
the question a panel is holding a checklist for.

**Say it plainly, once:** it is an agent because it has **tools it chooses how
to use** — it picks its own search terms; because it takes **several steps with
state between them**; and because it **decides to go back on its own** when a
first look finds nothing. Not because it calls a model.

Slides 8 and 9 already carry the evidence. What is missing is the sentence that
names it.

### Gap 3 — Why these tools. Asked for outright.

> *"Briefly explain the agent's architecture, the tools you used, and why you
> chose them."*

**Decision `0001` is the whole argument and none of it is on a slide.** Short:
LangGraph over DSPy ReAct, CrewAI, Pydantic AI and LlamaIndex, because the audit
is a cyclic graph with a real decision in it, because the trace is the demo, and
because "where does your agent decide anything" has to be answerable by
pointing rather than arguing.

Name every library as a library.

### Gap 4 — The learning. The email asks; the deck reports obstacles instead.

> *"What obstacles did you face, and what did you learn?"*

Slides 10–13 say what is wrong. Slide 10 draws a real lesson — *a self-report
nobody can check is not a trigger*. The rest state facts and stop.

**The biggest learning of the whole project is unstated, and slide 7 is sitting
on it:**

> Almost everything that looked like a model-quality problem was a data-quality
> problem. Changing how the PDF was read moved the verdict from weak to worth
> applying. Changing retrieval fixed a gap that was not a gap. Repairing broken
> lines removed a false finding. **The model never changed.**

That is the sentence a Professional Services engineer earns on customer
deployments, and it is true here and measured.

### Gap 5 — Why this problem. "Creativity & Passion" is a scored criterion with nothing addressing it.

The deck never says why **he** cares.

The honest answer is the strongest one available: **he is job hunting, he built
it for himself, and the demo runs on the job post he is interviewing for.** The
tool is being used for real, on them, in the room.

One line on slide 2 or slide 1. Do not labour it.

### Gap 6 — How it was built. The repository already says it; the deck does not.

**The author wrote and published Formwork, a method for running a project with
coding agents. This whole application was built with it, by him, directing.**

At the root of the repository a reviewer will see `FORMWORK.md`, and under
`docs/`: **24 briefs, 8 decision records, 21 reports, across 23 commits.**

**They will ask.** A deck that does not mention it looks like a candidate
avoiding the question of who wrote the code. Lead with it.

**What to say, and it is four beats:**

**One — the method exists and it is his.** Every piece of work was briefed
before it started: what it is for, what must not happen, and **how anyone could
tell it failed**. Every piece came back as a report naming what was done without
being asked, what was skipped, and **what the brief got wrong**.

**Two — the guardrails are enforced, not advised.** A command refuses to let a
turn end while the check suite is red. Every check ships with an input that
breaks it, so a check that examines nothing cannot pass. An agent cannot write
to version control.

**Three — name what it actually caught**, because a method with no catches is a
slide about discipline:

- the planning role offered to start building four times; the rule is written on
  its own page and **the human caught it, not the kit** — that failure is now
  recorded in the kit's own limits file
- the turn-end gate refused three times over a missing integrity record, rather
  than letting the session close on a red check
- **every report has a "what the brief got wrong" section, and most of them are
  not empty** — including one where two sessions independently found the same
  hole in a contract, with no contact between them

**Four — why it matters here.** Professional Services is going into a customer,
building fast, and leaving something their team can run afterwards. **The
`docs/decisions/` folder is that handover artifact**, and it exists because the
method demanded it, not because somebody remembered at the end.

**The through-line worth saying once:**

> Vouch refuses to claim what it cannot evidence. Formwork refuses to let a turn
> end on a red gate. Both are the same instinct — make the guarantee structural,
> not a promise.

**Two risks, and the brief is explicit about both:**

- **Do not let this become a Formwork pitch.** The talk is about Vouch. This is
  how Vouch was made. **Ninety seconds, not four minutes.**
- **Frame it as direction, not delegation.** *"I briefed it, I read every report,
  I rejected work and I caught it drifting"* — with the repository as the
  evidence. Anything that sounds like *"the agents built it"* costs more than it
  earns.

## 3. Two smaller things found in the audit

**The ending is an apology.** Slide 14 closes on *"not production ready, and not
pretending to be."* True, and the wrong last thing to leave in the room. The
honesty belongs earlier — it is already all over slides 10 to 13. **End on the
pattern and where it goes**, which is Gap 1.

**The clock does not add up to what they asked for.** The shape table totals
**14 minutes before questions**, and the email says a 15-minute presentation. If
questions are inside the fifteen, there is one minute for them. **Decide which,
say which in the file, and make the arithmetic hold.**

## 4. Where the time comes from

**The demo keeps its five minutes.**

"How it works" is **five slides and 4½ minutes** — 5, 6, 7, 8, 9. That is the
only slack. Compress it. **Do not cut slide 6 and do not cut slide 7.**

Gaps 2, 3 and 5 are a sentence each and cost almost nothing. Gap 4 is one
paragraph on an existing slide. **Gap 1 needs two to three minutes and Gap 6
needs ninety seconds** — those two are the real spend.

**If the arithmetic will not close, say so and name what else should go.** Do
not shrink the demo and do not shrink the honesty.

## 5. Must not happen

- **Do not touch any file outside `docs/presentation/`**, except this brief's
  own report.
- **Do not invent a customer story, an industry he has worked in, or a
  deployment.** The compliance engine is real. A healthcare project is not.
- **Do not say "production ready".**
- **Do not promise a number** for accuracy or cost beyond what is measured.
- **Do not turn the vision into a list of industries.** A list with no argument
  is worse than nothing. The argument is the guarantee; the industries are
  examples of it.
- **Do not let Gap 6 become a pitch for Formwork**, and do not phrase it as
  agents having built the thing. Direction, with the repository as evidence.
- **Do not cut the honesty.** Slides 10 to 13 are why the vision is believable.

## 6. Done when

- All six gaps are covered, each in the deck's own voice.
- The talk ends on the pattern, not on a limitation.
- **The clock arithmetic holds**, and the file says whether questions are inside
  the fifteen.
- Slides 6, 7, 10 and 11 are untouched.

**What would tell us it failed:** it runs long, the vision reads as a list of
industries, or it claims experience he does not have.

## 7. Checked by

`formwork check`.

Nothing can check a presentation. The evidence is section 8.

## 8. The report must contain

Short.

- what was added for each of the six gaps, and where
- **what was compressed to pay for it**, named
- the new clock arithmetic, and whether questions are inside the fifteen
- anything in the email's five topics or four criteria **still** not covered

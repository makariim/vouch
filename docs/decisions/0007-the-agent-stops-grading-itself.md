---
status: accepted
date: 2026-09-15
deciders: [makariim]
consulted: [director]
informed: []
---

# 0007. The agent stops grading itself

## What made this a decision

Decision `0001` says the audit is an agent because it decides, without being
told, when to look again. That decision is a conditional edge in the graph and
it has two triggers: a quote that failed verification, or the model setting
`evidence_weak` on its own judgement.

**It has never fired. Three real runs: 0 of 21, 0 of 23, 0 of 21.**

The quote trigger correctly had nothing to fire on — every quote checked out.
The self-report trigger stayed silent even where the verdict was wrong, and
even where the model's own written reason said *"does not mention"*.

So the thing decision `0001` rests on has never happened on real input.

## What matters here

- The agent claim has to be true, not argued for.
- It has to be **visible** in a fifteen-minute demo.
- A human pressing a button is not the agent deciding, and presenting it as one
  would be dishonest.
- Extra model calls cost time in a demo that already takes a minute.

## Options we looked at

- **Ask the model harder.** Rewrite the judge prompt to demand the flag when the
  reason contains a negation. Still a self-report, and still unfalsifiable until
  the next run.
- **Trigger on something observable.** Drop the self-report; go round again on a
  condition we can see in the data.
- **A re-run button instead.** Build a control that makes a second pass happen
  when a person asks. Useful, and it proves nothing about the agent.
- **Do nothing**, and present the silence as a finding. Honest, and it leaves
  the strongest claim in the project unevidenced.

## What we chose, and why

**The agent goes round again when the first pass finds nothing.**

`not_evidenced` on the first attempt means the search terms may simply have
missed. Looking once more with different terms is the correct behaviour, and it
is the exact case that produced the wrong FastAPI verdict before BM25.

The quote-failed trigger stays. `evidence_weak` is dropped as a trigger.

**Why this and not a better prompt:**

- **It is observable.** The verdict is data the graph already holds. Nothing
  depends on a model's opinion of its own work.
- **It will fire.** On the last real run, 2 to 3 requirements come back
  `not_evidenced`. The demo shows the agent going back on its own because it
  does, not because somebody pressed something.
- **It is cheap.** Two or three extra calls, not double. A prompt-based fix
  could fire anywhere between never and everywhere.

**The re-run button stays, and is never called a retry.** Two different things:
the agent deciding mid-run, and a person asking for another pass.

**What this gives the presentation**, and it is better than a loop that worked
first time:

> I asked the model to tell me when its evidence was thin. It never did, not
> once in three runs, including when it was wrong. So I stopped trusting its
> self-report and triggered on something I could observe.

## What follows

**Good:**

- The claim in decision `0001` becomes true rather than argued.
- The retry is visible in the demo without anyone touching anything.
- One less thing depending on a model's self-assessment.

**Bad:**

- Every genuinely absent requirement now costs an extra search and judge. On a
  post asking for things the resume does not have, the run gets slower.
- A second pass that finds nothing is a dead end the user watches happen.
- `evidence_weak` stays in the schema, asked for and ignored. Dead weight, and
  worth removing later rather than in the last wave.

## What would make us revisit this

If a post produces mostly `not_evidenced`, this doubles the work for no gain.
A cap — retry at most the first few — would be the fix, and the number should
come from a real run rather than from here.

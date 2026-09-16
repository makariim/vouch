---
status: accepted
date: 2026-09-14
deciders: [makariim]
consulted: [director]
informed: []
---

# 0003. The audit governs the tailor

## What made this a decision

The tool drafts tailored resume and cover letter text. Every tool in this space
does that, and most of them will happily write that you have five years of
Kubernetes because the post asked for five years of Kubernetes.

The thing that makes this project worth showing is that it refuses to.

## What matters here

- A claim in a cover letter is something the human will have to defend in a room.
- The audit already knows which claims are supported and which are not.
- If the rule lives only in a prompt, it holds most of the time, and most of the
  time is not good enough for this particular promise.

## Options we looked at

- **Tailor freely, warn afterwards** — what most tools do.
- **Tailor only from evidenced material**, and refuse the rest.
- **Ask the human per gap** — honest, and too slow for a fifteen minute demo.
- **Do nothing**, and ship the audit alone. This stays available and is the
  fallback if time runs out.

## What we chose, and why

**The tailor may use only material the audit marked evidenced, and must refuse
to claim anything marked not evidenced.**

Structural, not prompted: the tailoring step receives only the evidenced items.
It cannot write about the rest because it never sees the rest.

Where a requirement is not evidenced, the correct output is to say so, not to
find a form of words that sounds close enough.

**The audit must work end to end before any tailoring work starts.** If time
runs out, the tailor is the thing dropped. An audit with no tailor is a smaller
product that still works. A tailor with a shaky audit is the thing this project
exists not to be.

## What follows

**Good:**

- The product has a spine, and it is one sentence long.
- It is the answer to "how is this different from asking a chatbot".
- Dropping the tailor under time pressure costs a feature, not the point.

**Bad:**

- The drafted text will be thinner than a competitor's, and sometimes visibly.
- Users who want the gap filled will not get what they came for.
- It puts more weight on audit accuracy, which is NOT ESTABLISHED.

## What would make us revisit this

If real use shows the audit marks things not evidenced that plainly are, the
problem is the audit, and tightening this rule further would be fixing the wrong
end. Fix the audit first.

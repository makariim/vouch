---
updated: 2026-09-15
---

# What we would build next

Everything here was designed and deliberately not built. It is a record of where
the product goes, not a list of things we forgot.

Each one says what it is, why it matters, and **why it is not in the first
version** — because the second half is the part that is worth reading.

---

## 1. Highlight requirements on the job page itself

You are reading a real job post. Each requirement is coloured **where it sits**,
green, amber or red, against your own resume.

**Why it matters:** nobody else does this. The audit stops being a separate
screen and becomes an overlay on the thing you were already reading.

**Why not yet:** it is the flakiest idea we have. Job boards load content
dynamically and split text across elements, so the highlight breaks in ways that
are invisible until a live demo. The offsets are already computable — the
extraction step finds each requirement's exact span in the post — so this is a
rendering problem, not an architecture one.

## 2. The tailor

Draft resume bullets and cover letter text **from evidenced material only**, and
refuse to claim anything marked not evidenced.

**Why it matters:** it is the actual job to be done. The audit tells you where
you stand; the tailor is what you send.

**Why not yet:** it is a second product on top of the first. The audit had to be
trustworthy before anything was allowed to write from it, and that ordering is
recorded in `decisions/0003-the-audit-governs-the-tailor.md`.

## 3. A retry that does not trust the model

Today the loop goes round again when the model flags its own evidence as thin.
**It never has — not once in three runs, including when it was wrong.**

**The fix:** stop asking a model to grade itself. Trigger on something
observable — a first-pass verdict of not evidenced, a retrieval score below a
floor, a query that matched nothing.

**Why not yet:** it changes how the agent behaves, and it was found hours before
a demo. Changing agent behaviour under that clock is how demos break.

## 4. Several resumes, and picking between them

Store more than one, switch per application, and see which resume answers a
given post best.

**Why not yet:** one default resume covers the demo. More is product surface
that does not change the argument.

## 5. Click a citation, open the resume there

`resume line 41` becomes a link that opens your resume with that line lit up.

**Why not yet:** polish. The citation is already checkable by hand.

## 6. Show what the agent rejected

Every verdict expands to show the lines that were retrieved and turned down, not
only the one that won.

**Why it matters:** it is the transparency claim made visible, and it is how you
would catch a wrong verdict yourself.

**Why not yet:** the data already exists in the graph's state. It is a rendering
job, and rendering time went to the summary instead.

## 7. Auditing while you scroll

A fast local signal on every job post you pass, with no model call.

**The first version has half of this** — the pre-screen endpoint. What is missing
is running it continuously while browsing and keeping a list of what looked good.

**Why not yet:** the half we built is the half that proves the idea.

## 8. A resume that fixes itself

The audit knows which lines are doing no work for a given post, and which
experience is stated too weakly to count. That is enough to suggest how to
rewrite a resume — **as a suggestion, against evidence, never as a rewrite.**

**Why not yet:** it needs the tailor first, and it needs a rule about what the
tool may change on your behalf. That rule does not exist yet, and shipping this
without one is how an honest product becomes a dishonest one.

---

## What is deliberately not on this list

**Applying on your behalf.** Auto-filling applications, generating cover letters
at volume, anything that increases how much a person sends rather than how well
they send it.

The whole premise is that a claim should be defensible in a room. A tool that
helps you send two hundred applications is arguing the opposite.

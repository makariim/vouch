---
status: accepted
date: 2026-09-14
deciders: [makariim]
consulted: [director]
informed: []
---

# 0002. Nothing leaves the machine except the model call

## What made this a decision

The tool handles a real resume and real job posts. That is personal data about
one identifiable person, and in the demo that person is the author.

Several ordinary choices would quietly send it to a third party: a hosted trace
service, fetching a job post from a URL, any cloud storage. Each is convenient
and each breaks the same thing.

## What matters here

- The project promised local only, no accounts, no hosted data. That promise is
  worth nothing if it is not enforced by what we actually build.
- The demo runs live on the real DataRobot job post, gaps included.
- A demo that depends on the network can fail in the worst possible minute.

## Options we looked at

- **Langfuse Cloud** for observability — one line to wire, and it ships the
  resume text off the machine.
- **LangSmith** — same convenience, same problem, and it is the native option
  so it will keep being suggested.
- **Self-hosted Langfuse** — Docker on the machine, nothing leaves.
- **No observability at all** — nothing leaks and nothing is visible either.
- **Do nothing**, and decide each case as it comes up. This is how the promise
  erodes one convenient choice at a time.

## What we chose, and why

**One rule: the only outbound network call is to the language model.**

That settles four things at once, which is why it is one record and not four:

- **Observability is Langfuse, self-hosted.** Docker on the machine. Cloud is
  refused, and so is LangSmith, for the same reason and not a different one.
- **No URL fetching of job posts.** Pasted text only. This also removes live
  scraping from the demo path, where it would fail badly.
- **No hosted storage, no accounts, no telemetry.**
- The model call itself is the one exception, and it is unavoidable. It is worth
  saying out loud in the presentation rather than hoping nobody asks.

## What follows

**Good:**

- The promise is now checkable. One rule, and a reviewer can test it.
- The demo path has one network dependency instead of four.
- It is a good answer to a Professional Services interviewer, who will have sat
  in rooms where this question decides whether a thing can be used at all.

**Bad:**

- Self-hosting Langfuse is several containers to stand up, and that is time.
- No shared trace link to send anyone. Screenshots only.
- Pasting a job post is a worse experience than pasting a URL, and we are
  choosing the worse one on purpose.

## What would make us revisit this

If this ever stops being a single-user local tool and becomes something other
people run, this record is the first thing to reopen, because a hosted product
cannot keep this rule and should not pretend to.

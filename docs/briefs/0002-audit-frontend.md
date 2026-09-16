---
status: done
date: 2026-09-15
---

# 0002 — Audit frontend

> **This runs at the same time as brief 0001, the backend.** The two never touch
> the same files. They meet only at the contract in decision `0004`, and neither
> session may change that contract alone.
>
> **Do not wait for the backend.** Section 2 says how to start without it.

## 1. Goal

One page. Paste a job post, paste a resume, press a button, and watch the audit
happen — requirement by requirement, live, as the events arrive.

This page **is the demo.** Fifteen minutes in front of people who are scoring
four things that are not code. A screen showing the agent working is worth more
than any feature behind it.

**If we do not do this at all:** the assignment requires a frontend and a
backend. Without this there is no submission.

## 2. Start here, before the backend exists

Hand-write `fixtures/trace-sample.json` from the example events in decision
`0004`. Twelve requirements, a couple of retries, a mix of all three verdicts.

Build the whole page against that file. Add a switch:

- **fixture mode** — replay the file with a short delay between events, so it
  looks live
- **live mode** — the real `POST /audit`

Fixture mode is not throwaway. **Keep it.** It is the thing that saves the demo
if the model API is slow or down in the room.

## 3. Scope

**One HTML file, one CSS file, one JS file.** No build step, no framework, no
npm install. Fewest things that can break in a live demo, and nothing to compile
on the morning.

**The page:**

- two text areas, job post and resume, and an **Audit** button
- a requirements list that appears when the `requirements` event arrives
- each requirement showing its live state as `step` events come in: searching,
  retrying, verifying
- a verdict on each one when its `verdict` event arrives — the three states
  clearly different at a glance, and the supporting line quoted underneath with
  its line number
- a summary when `done` arrives
- the `error` event shown as a message, not a blank screen

**The retry has to be visible.** When the agent decides to search again, that
must be legible on screen. It is the moment that proves this is an agent and not
a pipeline. Do not let it flash past.

**Readable from across a room.** Someone will be looking at a shared screen.
Large enough type, enough contrast, no dense grey-on-grey.

**Out of scope — do not touch, do not add:**

- **any Python, any backend file, anything under the graph.** Brief 0001 owns
  those, in another session, right now.
- a browser extension. Later, and only if everything else is done.
- editing or uploading files, PDF parsing, a URL box
- accounts, settings, history, saved runs
- any frontend framework, bundler or package manager
- dark mode, animations beyond what makes the trace readable

## 4. Must not happen

Standing ones apply: no writing to version control, no deciding anything — stop
and report, no changing a check because it failed, and where something cannot be
established, say so rather than estimating.

Specific to this work:

- **Do not change the contract in decision `0004`.** If something is missing,
  report it. The backend is being built against it at this moment.
- **Do not invent a verdict the events did not carry.** The page renders what
  arrives and nothing else.
- **Do not load anything from a CDN.** No fonts, no libraries, no stylesheets.
  Decision `0002`: nothing leaves the machine. It also means the page works with
  the wifi off.
- **Do not block the whole page on one slow event.** Requirements render as they
  arrive.

## 5. Done when

- The page runs the full fixture end to end and looks live.
- Every one of the six event types from `0004` renders, including `error`.
- The three verdicts are distinguishable at a glance from two metres away.
- A retry is visibly a retry, not a flicker.
- **It has been run against the real backend** once brief 0001 lands, and any
  mismatch with `0004` is written in the report rather than patched over.
- Nothing is fetched from the network except `/audit`.

**What would tell us it failed:** you watch it on a shared screen and cannot
follow what the agent is doing without narrating it. If the page needs you to
explain it, it is not the demo.

## 6. Checked by

`formwork check`, as a whole.

**The gate cannot see a web page.** It cannot tell whether this is legible or
whether the retry reads clearly. The real evidence is you watching the fixture
run once, on a screen, from across the room. Section 7 asks for what that
showed.

## 7. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- what the page looks like at each stage — described, since a screenshot cannot
  travel in a report
- **anything in decision `0004` that was wrong, missing, or awkward to render.**
  This is the most useful thing this session can send back, and it is wanted
  whether or not the backend has landed.
- whether it has been run against the real backend yet, or fixture only
- what was cut to fit the day

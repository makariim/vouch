---
status: done
date: 2026-09-15
---

# 0008 — Browser extension

> **Wave 1, stream 3.** Runs at the same time as `0006`, `0007`, `0009`.
> **You own `extension/` and nothing else.** Do not touch `src/`, `web/` or
> `design/` — three other sessions are in them now.
>
> **Do not wait for the backend.** Section 3 says how to start without it.

## 1. Goal

A Chrome extension that notices you are on a job post, tells you quietly, and
gives you a one-glance answer: should you apply, what would sink it, what to
lead with.

**Why an extension and not a scraper:** you are already signed in and already
looking at the page. Nothing is scraped, no terms are broken, no bot detection
exists to beat. That argument is worth more in the interview than the code.

**If we do not do this:** the product is a page you paste into, which is what
everything else in this space already is.

## 2. Start here, before the backend exists

Hand-write `extension/fixtures/summary.json` from the `summary` example in
decision `0005`, and `prescreen.json` from the same record.

Build the whole panel against those. Keep a fixture mode switch. **It is also
the demo fallback if the model is slow in the room.**

## 3. Scope

Manifest V3. No build step, no framework, no npm. Plain JS, HTML, CSS.

- **Detect a job post.** URL patterns plus page shape. LinkedIn first, then
  anything that looks like one. Getting it wrong quietly is fine; getting it
  wrong loudly is not.
- **A badge on the toolbar icon**, two states: nothing here, job post detected.
  **No notifications.** A popup per job post is what makes people uninstall an
  extension.
- **The panel**, about 380px:
  - the fit call and its one-sentence reason
  - blockers — required and missing, usually two or three
  - strongest cards — what to lead with
  - which resume it checked against
  - a button: **open the full audit** in the page, with the post carried over
- **The default resume.** Read from the backend's resume list. If none is set,
  say so and link to the page rather than asking for a paste.
- **The pre-screen while browsing.** `POST /prescreen`, no model call, so it can
  run as you move between posts. **The full audit only on purpose, never
  automatically** — it is 58 seconds and it costs money.

**Out of scope:**

- **highlighting requirements in place on the job page.** It is the best idea we
  have and the flakiest. Roadmap, not this brief
- storing or uploading resumes. The backend owns that
- any Python, anything in `web/`, anything in `design/`
- publishing to the Chrome Web Store
- Firefox or Safari

## 4. Must not happen

- **No model calls from the extension.** No API key in a browser, ever. It talks
  to `localhost` and nothing else.
- **No CDN, no external font, no analytics.** Decision `0002`.
- **Do not change decision `0005`.** The backend is being built against it now.
  Report a mismatch, do not patch around it.
- **Do not run a full audit automatically.** Pre-screen may be automatic. The
  audit is always a deliberate click.
- Do not send the resume anywhere. The extension never holds it.

## 5. Done when

- It loads unpacked in Chrome and the badge changes state on a real LinkedIn job
  post.
- The panel renders the whole fixture, including an empty-blockers case and a
  no-default-resume case.
- **It has been run against the real backend once `0007` lands**, and any
  mismatch with decision `0005` is written in the report rather than patched.
- Nothing is fetched from the network except `localhost`.
- **It fails visibly and calmly when the backend is not running.** That will
  happen in the demo if the server was not started.

**What would tell us it failed:** you are on a job post and cannot tell in five
seconds whether to apply.

## 6. Checked by

`formwork check`.

**The gate cannot see a browser extension.** The evidence is loading it unpacked
and using it on a real job post, which is what section 7 asks about.

## 7. The report must contain

The standing list, plus:

- **how to load it** — the exact steps, because it will be done live
- what the panel looks like in each state, described
- **what decision `0005` got wrong**, missing or awkward. The most useful thing
  this session can send back
- how detection performs on real pages: what it caught, what it missed
- whether it has run against the real backend, or fixture only

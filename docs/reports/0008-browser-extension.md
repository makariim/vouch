---
status: open
date: 2026-09-15
brief: 0008-browser-extension
---

# 0008 — Browser extension

**The extension is written and the gate is green. It has never been loaded in a
browser, and no browser was available in this session.**

So the two done-when items that are evidence — the badge changing on a real
LinkedIn post, and a run against the real backend — are both unmet. The brief
stays `open`. Section 6 says the gate cannot see a browser extension, and it is
right: green here means the repository is consistent, not that the extension
works.

**The most useful thing in this report is section "What decision `0005` got
wrong".** One of the five findings means the panel's headline cannot be built
as briefed. Please read that before the code notes.

## What changed

All new, all inside `extension/`. Nothing in `src/`, `web/`, `design/` or
`fixtures/` was touched.

| File | Why |
|---|---|
| `extension/manifest.json` | MV3. `host_permissions` is localhost only |
| `extension/README.md` | how to load it, and the fixture switch |
| `extension/src/detect.js` | content script. Is this a job post, what is its text |
| `extension/src/background.js` | service worker. The badge, and the pre-screen |
| `extension/src/panel.js` | the panel and every state it renders |
| `extension/src/panel.html` | panel markup, 380px |
| `extension/src/panel.css` | neutral styling, no external font |
| `extension/src/api.js` | the two endpoints, plus fixture reads |
| `extension/src/config.js` | backend address, timeout, mode switch |
| `extension/fixtures/summary.json` | hand-written from decision `0005` |
| `extension/fixtures/summary-clear.json` | the empty-blockers case |
| `extension/fixtures/prescreen.json` | the `/prescreen` reply from `0005` |
| `extension/fixtures/resumes.json` | a resume list with a default |
| `extension/fixtures/resumes-empty.json` | the no-default-resume case |
| `extension/fixtures/requirements.json` | requirement text, needed for the join — see below |

## What was run

```
node --check   on all five JS files          all pass
python3 -m json.tool  on all seven JSON files  all pass
formwork/fw check
```

Nothing was installed. No package manager ran. No model was called and no
network request was made from this session.

## The check

`formwork check` — **green.** 12 checks, all ok: `config-shape`,
`decision-ids`, `doc-links`, `generated-current`, `guard-wired`,
`kit-integrity`, `predictions-first`, `role-shape`, `rule-labels`,
`standing-current`, `style-pointed`, `work-paired`.

## Git status

Nothing staged. `extension/` is untracked, alongside the other wave 1 folders.

## What decision `0005` got wrong

Section 7 asks for this and it is the part worth your time. Reported, not
patched around — brief section 4.

### 1. There is no way to get a `summary` without running the audit

`summary` is an event **inside the `POST /audit` stream**. That is the only
place it exists.

The brief's panel leads with the fit call, the blockers and the cards. All three
come from `summary`. The brief also forbids the extension to run an audit by
itself, correctly — 58 seconds and real money per job post.

**So the panel's headline has no live source.** In fixture mode it renders in
full. Against a real backend it can only show the pre-screen count and say the
fit call needs the audit.

This is not a bug in the code and I could not fix it inside `extension/`.

**What would fix it**, cheapest first:

- the backend keeps the last audit per post and serves `GET /summary?url=`,
  so a post audited once stays answered when you come back to it
- or the page writes the summary back somewhere the extension can read

Either is a change to `0005` and belongs to you, not to me.

### 2. `strengths` and `undersells` carry no text

```json
"strengths":[{"requirement_id":17,"line_number":5}]
```

A requirement id and a line number. To render "what to lead with" a client needs
the requirement's words, which arrive in the `requirements` event earlier in the
same stream, and ideally the resume line, which needs `GET /resumes/{id}`.

**Any client holding only a summary cannot render the summary.** That is why
`extension/fixtures/requirements.json` exists — the panel joins against it. It
is a workaround for a gap in the record.

`blockers` already carries `text`. Doing the same on `strengths` and
`undersells` would close this in one line each.

I chose not to show the resume line itself, only "line 5". One glance does not
need the sentence, and it avoids a second request.

### 3. `signal` has no set of values

`/prescreen` returns `"signal":"worth_a_look"` and the record never says what
else it can be. `fit` gets a closed set of three; `signal` gets one example.

A client cannot style what it cannot enumerate. **The panel ignores `signal`
entirely** and renders `matched` of `total`, which is honest and needs no list.
If `signal` is meant to be shown, it needs its values written down.

### 4. Nothing says how a post gets from the extension to the page

The brief asks for a button that opens the full audit "with the post carried
over". `0005` defines the endpoints and never mentions the handoff.

**What I built, as a proposal:** the button opens
`http://localhost:8000/#post=<encoded>`. A URL fragment is never sent to the
server by the browser, so the post reaches the page without a request, which
keeps decision `0002` clean. Over 12,000 characters it opens the page bare
rather than build an absurd URL.

**Brief `0009` owns the other end and does not know this exists.** Until the
page reads `#post=`, the button opens an empty page. This needs to reach that
session.

### 5. The `GET /resumes` response shape is not written down

`0005` says "list" and stops. I assumed:

```json
{"resumes":[{"id":"...","name":"...","default":true}]}
```

A bare array, or `is_default`, or no `name` field, all break the panel's
"Checked against …" line. **Ask `0007` what it actually built** — a one-line
mismatch, but it is in the demo path.

Smaller, same family: `POST /prescreen` takes `"resume_id":"default"`. I read
that as the literal string `default` being accepted by the server, rather than
the client resolving the id first. If `0007` read it the other way, the
pre-screen 400s.

## How detection performs on real pages

**NOT ESTABLISHED.** No browser ran in this session, so nothing was caught and
nothing was missed. Anyone who reads a number into the rules below is reading
something that is not there.

What exists is two tests, both in `detect.js`:

**By URL**, thirteen patterns — LinkedIn's three shapes including the SPA list
view, Greenhouse, Lever, Ashby, Workable, Workday, SmartRecruiters, Indeed,
Wellfound. A match settles it.

**By page shape**, everywhere else: fourteen heading phrases a job post has and
an article about jobs does not, and the bar is **four of them plus 1,200
characters**. Deliberately high. Getting it wrong quietly is fine; a badge
lighting up on a news article is what gets an extension uninstalled.

The known weak spot is the fallback: when no site selector matches, the post
text is the whole visible body, capped at 30,000 characters, navigation and
footer included. BM25 over that is noisier than over a real description.

## Whether it has run against the real backend

**No. Fixture only.**

`/prescreen`, `/resumes` and the product layer are brief `0007` and do not exist
in `src/audit/server.py` yet — `server.py` today has `/`, a static asset route
and `/audit`. There was nothing to run against.

The whole live path is one small module, `src/api.js`, so the first real test is
cheap. It should happen the moment `0007` lands, and the five findings above
should be checked at the same time.

## What the panel looks like, state by state

- **Not a job post** — one grey line, "No job post on this page." Badge empty.
- **Job post, server down** — a calm box: the server is not running, the exact
  command to start it, a Try again button. No red, no stack trace. This is the
  demo state if the server was never started.
- **Job post, no default resume** — says so, and offers a button to the page.
  It never asks for a paste. The backend owns resumes.
- **Job post, live** — matched-of-total in a grey block, one line saying the fit
  call needs the audit, then **Open the full audit** with "about 58 seconds, and
  it calls the model" beneath it. See finding 1 for why this is thinner than the
  brief wanted.
- **Job post, fixture mode** — the full panel. Fit word in colour, one-sentence
  reason, blockers with a red rule, "Lead with" cards with a green rule,
  "Stated too weakly" for undersells, the resume name at the foot.
- **FIXTURES flag** sits in the header the entire time fixture mode is on.

## The three that matter

### Done but not asked for

**A `requirements.json` fixture.** Not in the brief's list of two. Finding 2 is
why: without it the cards have no words.

**The "Try again" button and the 900ms retry when the panel opens.** An MV3
service worker sleeps after about thirty seconds, and a report from the page
while it is asleep is dropped. Without the retry the panel says "no job post" on
an obvious job post perhaps one time in five. It reads like a bug and it is the
kind of thing that happens on stage.

**A fixture case dropdown**, three cases. The brief asked for a fixture mode
switch; done-when asks the panel to render the empty-blockers and
no-default-resume cases. The dropdown is how those are reached without editing a
file mid-demo.

**Fixture mode is a switch, never an automatic fallback.** Worth flagging as a
judgement call I made alone: a panel that quietly shows invented numbers when
the server is down would have you reading fabricated results out loud in the
room. So the mode is deliberate, and the header says FIXTURES while it is on.

### Asked for but not done

**Loading it in Chrome, the badge on a real post, the run against the backend.**
No browser, and `0007` has not landed. These are the three done-when items and
they are why the brief stays `open`.

**Icons.** The extension ships with no PNGs, so Chrome shows its default puzzle
piece. The badge sits on it correctly. Drawing them is `0006` and wave 2.

**The fit call, blockers and cards against a live server.** Finding 1. Not
skipped — not reachable.

### Wrong in the brief

**Nothing wrong. One thing missing, and it is finding 1.** The brief asks the
panel to lead with the fit call and forbids running the audit automatically, and
`0005` provides no third way to obtain one. Both instructions are right on their
own; together they leave the panel's best half unreachable in live mode.

Section 3's "open the full audit in the page, with the post carried over" also
assumes a handoff nobody has specified. Finding 4 proposes one.

## What I would do next, in order

1. **Settle finding 1.** Everything else on this panel is smaller than it.
2. Tell `0009` about `#post=`, or replace it with something better.
3. Load it in Chrome and walk five real job posts, LinkedIn first.
4. Run it against `0007` and check findings 2, 3 and 5 against what was built.

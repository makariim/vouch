---
status: open
brief: 0014-extension-wave-two
date: 2026-09-15
---

# 0014 — The extension: apply the design, get its answer back

**The design is applied, the live answer works end to end against the real
backend, and the icons exist. The extension has now been loaded in a browser,
which had never been done.**

It has **not** been walked across five real job posts, and that is the thing
section 6 asks for first. It stays `open` for that reason and that reason only.

Two things worth reading before the code notes:

- **The panel cannot draw two parts of the artboard**, because `POST /summary`
  does not carry them. Section "What the contract still does not have" below.
  The backend session found the same hole from its own side, independently.
- **`GET /resumes` has no name field**, so the panel's header cannot show a
  filename. Same family of gap, one field further on.

---

## What changed

All inside `extension/`. Nothing in `src/`, `tests/`, `web/`, `design/` or
`fixtures/` was touched.

### The design

| File | Why |
|---|---|
| `tokens.css` | **new.** A byte-for-byte copy of `design/tokens.css`. See below |
| `src/panel.css` | rewritten. 89 tokens, no colour or type literal anywhere |
| `src/panel.html` | rewritten. The header strip, the mark inline, the fixture switch |
| `src/panel.js` | rewritten. Six states, the mark, quote blocks, plain-English copy |

### The answer

| File | Why |
|---|---|
| `src/api.js` | `POST /summary` added. Three answers: known, not known, no server |
| `src/config.js` | a fourth fixture case, `quick-match`. `requirements.json` gone |
| `src/background.js` | the toolbar mark instead of badge text. Passes the HTTP status on |

### The icons

| File | Why |
|---|---|
| `icons/*.png` | **new.** Eight files: quiet and found, at 16/32/48/128 |
| `tools/make-icons.py` | **new.** What draws them. No image library, none installed |
| `manifest.json` | declares the icons. Renamed to Vouch. Version 0.2.0 |

### The fixtures

| File | Why |
|---|---|
| `fixtures/summary.json` | decision `0006`'s one shape. `text` and `line` on all three lists |
| `fixtures/summary-clear.json` | the same, nothing missing |
| `fixtures/summary-unknown.json` | **new.** `{"known": false}` |
| `fixtures/resumes.json` | changed to what the server actually sends. See below |
| `fixtures/requirements.json` | **deleted.** The workaround decision `0006` removed the need for |

### The evidence

| File | Why |
|---|---|
| `tools/browser/` | **new, and not asked for.** Three scripts that drive a real browser |
| `README.md` | rewritten. How to load it, the drift check, the three endpoints |

---

## Copying `tokens.css` instead of importing it

The brief says to import `design/tokens.css`. It cannot be imported.

A Chrome extension can only read files inside its own folder. `@import
"../../design/tokens.css"` resolves to a `chrome-extension://` URL outside the
package, and it fails **silently** — no error, just an unstyled panel.

So it is copied, byte for byte, and the drift check is a `diff`:

```
diff design/tokens.css extension/tokens.css && echo "in step"
```

Both files hash to `f28c2ee3a5df0e0a…`. `design/` still owns the values.

---

## What the contract still does not have

This is the main finding.

The artboard's level one is the answer word, one sentence, **and a counts row**
— 5 your resume shows, 1 shows part of it, 3 does not show. Level three is
**All nine things they asked for**, folded away.

Neither is in what `POST /summary` returns.

Decision `0006` gives the summary three lists — blockers, strengths, undersells.
Those three are the shortlist, not the whole set, so the counts cannot be
derived from their lengths, and deriving them would be a client re-deriving a
judgement, which decision `0006` forbids in its second line.

**So the panel renders the answer word, the sentence and the three sections, and
omits the counts row and the folded list.** Everything the brief's own section 2
lists is there. Two things the artboard draws are not.

The backend session reached the same place from the other side, and left this in
`src/audit/server.py`:

> the counts and the requirement list are also sitting in the same file — they
> are deliberately not returned, because widening a contract is decision work
> and this is the last wave. Both are one line here if brief `0014` finds it
> needs them.

**It needs them.** Two sessions, no contact, same conclusion — that is about as
clear as a signal gets. It is a decision, not a patch, so it stops here.

### And a second, smaller one

`GET /resumes` is specified in decision `0005` as the word "list". What one item
holds was never written down. The running backend answers:

```json
{"id": "resume", "lines": 19, "default": true}
```

There is no `name`. The artboard's header shows `maya-okonkwo-2026.pdf`, and
brief `0008`'s fixture invented a `name` field to match — the same shape of
workaround as `requirements.json`.

The panel now shows `name || id`, so it says `resume` rather than `undefined` in
the one place it promises to tell you what it checked you against. The fixture
was changed to match the server rather than the artboard, because a fixture that
shows a field the server never sends is how the last workaround happened.

---

## What was run

Nothing was installed. No package manager ran. No model was called and no
request left this machine.

```
python3 extension/tools/make-icons.py          8 PNGs
node --check  on all five JS files             all pass
python3 -m json.tool  on all seven JSON files  all pass
formwork/fw check                              green
```

Token coverage, mechanically:

```
tokens defined in design/tokens.css : 156
tokens used by extension/src/panel.css : 89
used but not defined : none
px / colour / ms literals outside the one named block : none
```

A backend was started on `[::1]:8000` for the live run and **stopped again**.
Port 8000 was already held by another session on IPv4; binding IPv6 let both run
without touching theirs. Its resume store was a scratch folder, not the
project's. Confirmed afterwards that their server is still up and mine is gone.

---

## The check

`formwork check` — **green.** 12 checks, all ok: `config-shape`, `decision-ids`,
`doc-links`, `generated-current`, `guard-wired`, `kit-integrity`,
`predictions-first`, `role-shape`, `rule-labels`, `standing-current`,
`style-pointed`, `work-paired`.

**The gate cannot see an extension**, and section 5 of the brief says so. Green
means the repository is consistent. Everything below is the evidence it cannot
produce.

---

## It has been loaded in a browser

This had never been done. It has now.

```
17 of 17 checks passed     extension/tools/browser/panel_states.py
```

- The extension loads unpacked, enabled, **no errors** on the extensions page.
- The MV3 service worker starts.
- The toolbar shows the mark. **No puzzle piece.**
- The title changes to "Vouch — a job post is on this page" on a job post and
  back to "Vouch" off one.
- No page errors in any state.

**One caveat, and it is not small.** This is Playwright's Chromium, not Google
Chrome. **Chrome 137 removed `--load-extension` from the command line**, so a
scripted Chrome cannot load an unpacked extension at all — the flag is accepted
and ignored, and the extensions page stays empty. This was confirmed here, twice,
including with the documented re-enable flag.

Loading it by hand through `chrome://extensions` is unaffected, and is what
`extension/README.md` describes. **Somebody should still click through those
five steps once in real Chrome before the demo.**

---

## It has run against the real backend

Not fixture only. `extension/tools/browser/live_run.py`:

```
11 of 11 checks passed

  ok   mode is 'live', not fixture
  ok   backend reachable from the worker: 'up'
  ok   default resume found: {'default': True, 'id': 'resume', 'lines': 19}
  ok   live prescreen: {'matched': 5, 'signal': 'maybe', 'total': 14}
  ok   the FIXTURES flag is NOT showing
  ok   the stored answer rendered from POST /summary
  ok   the blockers came through
  ok   a resume line is quoted word for word

  requests the extension made to localhost:8000:
    GET  http://localhost:8000/resumes
    POST http://localhost:8000/prescreen
    POST http://localhost:8000/summary
```

All three endpoints, live, from a real extension in a real browser. The panel's
headline came out of `POST /summary` — the hole brief `0008` reported is closed
and the closing is demonstrated, not assumed.

`{"known": false}` was confirmed separately: the same post hashed differently
answers not-known, and the panel falls back to the word match. That is the store
behaving, not failing.

---

## How detection performed

**Not on five real job posts.** That needs a signed-in browser on the live
sites. It stays NOT ESTABLISHED, and it is the only reason this brief is still
open.

What was measured instead, in two halves, both honest about what they are.

### The URL rules, offline

Twelve URLs in the real formats of the boards `detect.js` lists, and eight that
must stay quiet. **The URLs were written from the known formats. None was
visited.**

```
caught 12/12   missed 0   false positives 0/8
```

Quiet on: LinkedIn feed, a LinkedIn profile, the LinkedIn jobs home, a company
careers index, a Greenhouse board index, an Indeed search, a news article,
Hacker News.

### The shape heuristic, in the browser

Five hand-written pages served from localhost, so no URL rule can fire and only
the four-heading-words-and-1200-characters bar is being tested.

| page | is it | said | verdict |
|---|---|---|---|
| a full job post, all the usual headings | yes | yes | correct, by shape, 1356 chars |
| a real but very short job post | yes | no | **missed** |
| an engineering blog post about microservices | no | no | correct |
| a news article about hiring | no | no | correct |
| a careers index listing five roles | no | no | correct |

**4 of 5.** The miss is the short post, and it is the bar working as written:
`detect.js` says the bar without a URL match is high on purpose, because a badge
lighting up on a news article is what makes people uninstall an extension. A
four-line job post on a site with no URL rule will be missed. On LinkedIn,
Greenhouse, Lever, Ashby, Workable, Workday, SmartRecruiters, Indeed and
Wellfound the URL settles it and the shape bar never applies.

The three hard negatives are the useful result. A careers index is the one most
likely to fire falsely — it has the headings and the length — and it did not.

---

## What the panel looks like, state by state

All six render. One screenshot each, from the harness.

**No job post on this page** — a big quiet empty bracket, centred, at 45%
opacity. Two sentences. A divider, then the resume name and "Open Vouch".

**Found a job post** — "On this page", the job title in the slab face, then the
rose line "Checking your resume on this computer…" breathing above a sweeping
bar. Rose is the only thing moving, and it means one thing: working now.

**Quick word match** — "Quick word match, on this computer", then **6** and
"of 9", the tick meter, the signal line, and "This is only a word match. Nothing
has been read or judged yet." Then the one button, "Check my fit properly",
with "about 1 minute" on its right.

**The whole answer** — "Worth applying." in the slab face at 28px, one sentence
under it, then the three sections: *They need two things you cannot show* with
empty brackets and a plain sentence each and **no quote block**; *This is what
proves you fit* with green-edged mono quotes; *Fix these lines in your resume*
with amber-edged ones. A quiet link at the bottom.

**No resume saved** — the header says "No resume", the job heading stays, then
a dashed well and "Choose a resume".

**Vouch is not running** — the mark and wordmark go quiet, "Not connected" in
red in the header, the slab heading, a red detail block, the command to start
it, then "Open Vouch" and "Try again".

Every one measured at 380px of content with no sideways scroll.

---

## Values `tokens.css` did not have

**None, of the kinds it claims.** Every colour, type size, line height,
duration, radius and focus ring the panel needs was already there. 89 tokens
used, nothing missing. No colour literal, no type literal and no duration
literal exists anywhere in `panel.css`.

**Seventeen in-component lengths are not tokens**, and by `design/README.md`
section 7 they should not be — padding and gaps inside a component are
properties of that component, not steps on the 4px scale. They are read off the
artboard and collected in one named block at the top of `panel.css` so they are
countable rather than scattered: section padding 20/15/22, gaps 11/14/16/9,
quote padding 11/13, the 7px note gap, the 1px hair, the 3px sweep bar, the 7px
tick and its 4px gap, and five one-off column widths.

**One real discrepancy, and it is in `design/`, not here.**
`design/assets/favicon.svg` bakes `#22262e` and `#f4f5f7`, saying they are
`--v-bg-1` and `--v-ink` "flattened to hex". Converted properly from oklch those
are `#171a1d` and `#e0e3e6` — noticeably darker and slightly duller. The
conversion was checked against all five sRGB primaries and white and black, and
round-trips exactly on all seven.

**The icons use the token values, not the baked ones**, since `tokens.css` is
the stated authority. Somebody who owns `design/` should reconcile the two. I
did not touch it.

---

## How to load it, exactly

1. `chrome://extensions`
2. **Developer mode**, top right, on.
3. **Load unpacked**.
4. Choose `extension/` — the folder holding `manifest.json`.
5. Pin **Vouch** to the toolbar.

After editing a file, press the reload arrow on its card. A `detect.js` change
also needs the job page reloaded.

For the live path, first:

```
uv run uvicorn audit.server:app --port 8000
```

Then leave Fixture mode off. With it on, the header shows `FIXTURES` the whole
time, and it never turns itself on.

---

## Git status

Nothing staged. Nothing outside `extension/` changed by this session — the
modified files below were already modified before it started.

```
 M .claude/agents/director.md
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
 M formwork/limits.md
 M formwork/roles/method/director.md
?? extension/
?? design/  src/  web/  tests/  fixtures/  scripts/  docs/...
```

---

## The three that matter

### Done but not asked for

**`extension/tools/browser/` — three scripts and five test pages.** The brief
asks for numbers about detection and about every state rendering, and a number
with no command behind it cannot be checked by anybody. Without these, nothing
in this report is reproducible after the session ends. They write nothing into
the repository. **Delete them if you disagree** — nothing in `src/` depends on
them.

**The start command on the "not running" screen.** The artboard does not have
it. A panel that names the problem and not the fix sends you to a README, and
this is the screen most likely to appear thirty seconds before a demo.

**`name || id` for the resume.** Strictly a workaround for the contract gap
above. Chosen over showing `undefined`.

**The product is called Vouch now**, in `manifest.json` and in the panel. The
design is take two throughout and take one is gone; the manifest still said Job
Hunter. The repository and the folder are untouched.

### Asked for but not done

**Five real job posts, LinkedIn first.** No signed-in browser, and fetching
LinkedIn from this session would be both a network action nobody authorised and
a login I do not have. This is the brief's own "what would tell us it failed"
test and it is unrun. **It is twenty minutes with the extension loaded by hand.**

**Loaded in Google Chrome specifically.** Chromium only, for the reason above.
The manual path is unaffected but unproven.

**The counts row and the folded requirement list.** No source. Section above.

### Wrong in the brief

**"Show the whole answer."** Section 2 lists the call, what they cannot show,
what proves you fit, and the lines to fix — all four are there. But the artboard
also draws a counts row and a folded list of everything asked for, and the brief
reads as though applying the artboard and rendering `POST /summary` are the same
job. They are not, by two elements.

**"The badge changes state."** There is no badge in the design. The artboard and
`favicon.svg` both describe a dot drawn onto the icon, and `favicon.svg` says in
words that the extension draws it. Chrome's badge is a coloured pill with text
and can be neither. It is now an icon swap, which is what the design asked for
and what the done-when meant.

**`extension/fixtures/requirements.json` "can go" — correct**, and it has. It
existed only to join `requirement_id` to text, and decision `0006` put `text` on
all three lists.

**Icon ownership.** The brief assigns the icons here; `extension/README.md` said
they were brief `0006`'s. Brief `0014` wins and the README no longer says it.

# Driving the extension in a real browser

`formwork check` cannot see an extension. Brief `0014` section 5 says so, and it
is right — a green gate means the repository is consistent, not that anything
works in Chrome. These three scripts are the part the gate cannot do.

They need Playwright and its Chromium:

```
pip install playwright && playwright install chromium
```

Chromium, not Google Chrome, and that is not a preference. **Chrome 137 removed
`--load-extension` from the command line**, so a scripted Chrome cannot load an
unpacked extension any more. Loading it by hand through `chrome://extensions`
still works and is what `extension/README.md` describes.

Nothing is written into the repository. Profiles and screenshots go to a
temporary folder, printed at the end of every run; set `VOUCH_WORK` to put them
somewhere you can find again.

| | |
|---|---|
| `panel_states.py` | every panel state renders, one screenshot each, plus the toolbar mark changing |
| `detection.py` | the shape half of detection, on pages with no URL clue |
| `url_rules.py` | the URL half, offline. Reads the regular expressions out of `detect.js` and runs them in node |
| `extraction.py` | **what the extension sends as the post, with the known-site list switched off** |
| `live_run.py` | the whole thing against a running backend, in live mode |

`extraction.py` copies the extension to a temporary folder, sets
`USE_KNOWN_SELECTORS` to false in the copy, and loads that. Nothing in the
repository is edited and the fast path cannot rescue anything. It needs the
backend's `candidate_requirements` to count, so run it in the project
environment:

```
uv run --with playwright==<the version whose chromium you installed> \
  python extraction.py
```

`url_rules.py` needs node and nothing else.

## `live_run.py` needs a backend

It reads `POST /summary`, so something has to have been audited. The script
stores one itself, keyed on the post text the extension actually extracted —
which is not the same string as the HTML file on disk, so hashing the file
instead gets you a truthful `{"known": false}`.

```
uv run uvicorn audit.server:app --port 8000
VOUCH_RESUMES=<the server's resumes folder> python3 live_run.py
```

The backend must be the one on `localhost:8000`: `config.js` is the contract and
is not edited for a test.

> [!TIP]
> **If port 8000 is taken by another session**, bind yours to IPv6 —
> `uvicorn ... --host ::1 --port 8000`. `localhost` resolves to `::1` first, so
> the extension reaches yours while an IPv4 server on the same port carries on
> undisturbed.

## What these pages are, and are not

`pages/` holds eight hand-written pages. They are **not real job posts** and no
measurement taken from them should be reported as if they were.

The first five establish something narrow: that the shape heuristic separates a
job post from three things that look like one.

The three added by brief `0016` — `linkedin-shaped.html`, `ashby-shaped.html`
and `northwind-careers.html` — are **reconstructions**. They were built to carry
the furniture the real pages carry: a nav bar, a right rail of related jobs, a
Premium-style upsell, a similar-jobs list, a footer. The description inside all
three is the same twenty-two-requirement post, so that the only thing changing
between them is the furniture around it.

> [!WARNING]
> **A reconstruction cannot establish that the scorer works on LinkedIn.** It
> was written by the same session that wrote the scorer, which is the exact
> shape of mistake `formwork/limits.md` describes: a check written by whoever
> wrote the thing it checks tends to pass for the wrong reason. What it
> establishes is that the scorer prefers prose to links on a page laid out like
> a real one. The real measurement still needs a signed-in browser.

The real measurement — five real job posts, LinkedIn first — needs a signed-in
browser on the live sites, and is still NOT ESTABLISHED. To do it, load the
extension by hand and walk the posts; `detection.py` is the wrong tool for it.

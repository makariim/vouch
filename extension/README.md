# The extension

A Chrome extension that notices you are on a job post and gives you one glance:
should you apply, what they need that you cannot show, what proves you fit,
which lines to fix.

**Why an extension.** You are already signed in and already looking at the page.
Nothing is scraped, no terms are broken, and there is no bot detection to beat.

## Load it

1. Open `chrome://extensions`.
2. Turn on **Developer mode**, top right.
3. Click **Load unpacked**.
4. Choose this folder — `extension/`, the one holding `manifest.json`.
5. Pin **Vouch** to the toolbar so the mark is visible.

After editing any file, press the reload arrow on the extension's card. A
content script change also needs the job page reloaded.

There is no build step, no npm, no framework. Plain JS, HTML and CSS.

> [!NOTE]
> **Chrome 137 and later ignore `--load-extension` on the command line.** That
> only affects scripted launches, not the five steps above. If you are
> automating it, Chrome for Testing and Chromium still accept the flag; this is
> what `extension/tools/` assumes.

## The toolbar mark

Two states and only two. Quiet is the mark in `--v-ink-520`. When a job post is
on the page it goes to `--v-ink` and grows a `--v-agent` dot on the corner.

That is the entire interruption this thing is allowed to make: no notification,
no popup per job post, no sound.

The PNGs are generated, not drawn by hand:

```
python3 extension/tools/make-icons.py
```

It needs no library — a PNG writer built out of `zlib` and `struct`, because the
mark is four rectangles and a circle. Colours are converted from
`design/tokens.css` at run time rather than pasted as hex, so there is one
source for them. **Do not hand-edit `icons/*.png`; change the script.**

## The design

`extension/tokens.css` is a **byte-for-byte copy** of `design/tokens.css`. A
Chrome extension can only read files inside its own folder, so it cannot be
imported across the repository — `@import "../../design/tokens.css"` resolves
outside the package and fails silently.

Check it has not drifted:

```
diff design/tokens.css extension/tokens.css && echo "in step"
```

If that prints a difference, copy `design/tokens.css` over the top. Never edit
either copy to resolve it — `design/` owns the values.

## Run it against the backend

```
uv run uvicorn audit.server:app --port 8000
```

The extension talks to `localhost:8000` and nothing else — `host_permissions` in
`manifest.json` lists localhost only, so a fetch anywhere else fails in Chrome
before it reaches the network.

If the server is not running the panel says so and offers the command. It does
not fall back to fixtures on its own.

### The three endpoints

| | |
|---|---|
| `GET /resumes` | which resume is the default. Read only — the backend owns the files |
| `POST /prescreen` | the word match. BM25, no model, milliseconds. Runs by itself |
| `POST /summary` | the stored answer for a post already audited, or `{"known": false}` |

`POST /summary` is decision `0006` and it is why the panel works at all. Before
it, `summary` existed only inside the `POST /audit` stream and the panel is not
allowed to start an audit, so live mode could show a word count and nothing
else.

## Run it without the backend

The panel has a **Fixture mode** switch at the bottom. Turned on, it reads
`fixtures/*.json` instead of the server and works with nothing running. The
header shows `FIXTURES` the whole time it is on, so the panel can never quietly
show invented numbers.

The dropdown beside it picks which case to render:

| Case | Shows |
|---|---|
| the whole answer | the fit call, what you cannot show, what proves you fit, lines to fix |
| nothing missing | the same, with an empty first section |
| word match only | `{"known": false}` — the count and the button |
| no resume saved | the state where no resume is set |

Two of the six panel states are deliberately **not** cases here. "No job post on
this page" is decided by the content script, and "Vouch is not running" is what
live mode does when nothing answers. Making either one a fixture would let the
panel show it while it was not true.

This is also the demo fallback if the model is slow in the room.

## What it does and does not do

- **Pre-screen runs by itself** as you move between posts. `POST /prescreen`,
  BM25 only, no model call, milliseconds.
- **The full audit never runs by itself.** It is about a minute and it costs
  money, so it is always a click, and it happens in the page rather than here.
  There is no setting that changes that.
- **No model call ever leaves this extension.** There is no API key in a
  browser.
- **It never holds your resume.** It reads the list from `GET /resumes` to name
  the default. The backend owns the files.
- No CDN, no external font, no analytics. Decision `0002`.

## Files

| | |
|---|---|
| `manifest.json` | MV3. Permissions, icons, and the localhost-only host rule |
| `tokens.css` | a copy of `design/tokens.css`. Never edited here |
| `icons/` | generated PNGs, two states at four sizes |
| `tools/make-icons.py` | what generates them |
| `src/detect.js` | content script. Is this a job post, and what is its text |
| `src/background.js` | service worker. The toolbar mark, and the pre-screen |
| `src/panel.js` | the panel, and every state it can be in |
| `src/panel.html` | panel markup, 380px |
| `src/panel.css` | the design, in tokens |
| `src/api.js` | the three endpoints, plus fixture reads |
| `src/config.js` | backend address, timeout, mode switch |
| `fixtures/` | hand-written, in decision `0006`'s shape |

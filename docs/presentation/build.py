#!/usr/bin/env python3
"""Build slides.html from slides.md.

    python3 docs/presentation/build.py

Standard library only. Nothing is fetched, at build time or at run time:
the design tokens are inlined from design/tokens.css, because a <link> to it
is a fetch and a fetch fails on file:// with the wifi off (decision 0002).

slides.md is the source. Never hand-edit slides.html.

To check that every slide fits on screen, and that opening the file requests
nothing, run with a Chrome on the machine:

    python3 docs/presentation/build.py --check
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import time
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = HERE / "slides.md"
TARGET = HERE / "slides.html"
TOKENS = ROOT / "design" / "tokens.css"

# The deck is laid out against this. 16:9, and the size the fit check uses.
STAGE_W = 1440
STAGE_H = 810


# ---------------------------------------------------------------------------
# splitting the source
# ---------------------------------------------------------------------------

def split_source(text: str) -> tuple[str, list[str]]:
    """Return (the block above the first slide, the slides).

    A line that is exactly `---` separates slides. Two things also look like
    that and are not separators: the YAML frontmatter at the top of the file,
    which is stripped first, and a table's `|---|---|` rule, which starts
    with a pipe.
    """
    if text.startswith("---\n"):
        end = text.index("\n---\n", 3)
        text = text[end + len("\n---\n"):]

    chunks = re.split(r"^---[ \t]*$", text, flags=re.MULTILINE)
    chunks = [c.strip("\n") for c in chunks]
    return chunks[0], [c for c in chunks[1:] if c.strip()]


# ---------------------------------------------------------------------------
# markdown, the small part of it this deck uses
# ---------------------------------------------------------------------------

def inline(text: str) -> str:
    """Bold, the accent mark, inline code and links. The rest is as written."""
    out = html.escape(text)
    out = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", out)
    # ==like this== is the accent. One per slide, on the line that matters.
    out = re.sub(r"==([^=]+)==", lambda m: f'<span class="hi">{m.group(1)}</span>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1), out)
    return out


# The only hue in the deck. A column called "evidenced" or "partly" is the
# product's own language, so it keeps the product's own colour (brief 0025).
VERDICT = {"evidenced": "shown", "partly": "partly",
           "partly evidenced": "partly", "not evidenced": "not"}


# A labelled block: a short label, `::`, then the text. The label is a name,
# not a sentence, so it is capped short — a line with a `::` in prose is a
# paragraph and must stay one.
ROW = re.compile(r"^([A-Z0-9][^:\n]{0,38}?)\s*::\s+(\S.*)$")


def render_table(rows: list[str]) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]  # cells[1] is the |---|---| rule
    out = ["<table><thead><tr>"]
    out += [(f'<th class="v-{VERDICT[c.lower()]}">{inline(c)}</th>'
             if c.lower() in VERDICT else f"<th>{inline(c)}</th>") for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_blocks(lines: list[str]) -> str:
    """Blocks: headline, footnote, fenced code, table, bullet list, paragraph."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if line.startswith("```"):
            j = i + 1
            code: list[str] = []
            while j < len(lines) and not lines[j].startswith("```"):
                code.append(lines[j])
                j += 1
            out.append("<pre>" + html.escape("\n".join(code)) + "</pre>")
            i = j + 1
            continue

        if line.startswith("# "):
            out.append(f"<h1>{inline(line[2:].strip())}</h1>")
            i += 1
            continue

        # A blockquote is the footnote: a source, a date, a caveat. Smaller and
        # set apart, so it cannot be mistaken for the argument.
        if line.startswith(">"):
            j = i
            note: list[str] = []
            while j < len(lines) and lines[j].startswith(">"):
                note.append(lines[j].lstrip(">").strip())
                j += 1
            out.append(f'<p class="foot">{inline(" ".join(note))}</p>')
            i = j
            continue

        if line.startswith("|"):
            j = i
            rows: list[str] = []
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(lines[j])
                j += 1
            out.append(render_table(rows))
            i = j
            continue

        # `LABEL :: text` — a labelled block. A run of them is one stack.
        # Most slides are two to four parts and each part has a name; naming
        # them beats a paragraph the room has to parse.
        if ROW.match(line):
            j = i
            rows: list[str] = []
            while j < len(lines) and ROW.match(lines[j]):
                m = ROW.match(lines[j])
                rows.append(f'<div class="row"><span class="t">{inline(m.group(1))}'
                            f'</span><span>{inline(m.group(2))}</span></div>')
                j += 1
            out.append('<div class="stack">' + "".join(rows) + "</div>")
            i = j
            continue

        if line.lstrip().startswith(("- ", "* ")):
            j = i
            items: list[str] = []
            while j < len(lines) and lines[j].lstrip().startswith(("- ", "* ")):
                items.append(lines[j].lstrip()[2:].strip())
                j += 1
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
            i = j
            continue

        para: list[str] = []
        while (i < len(lines) and lines[i].strip()
               and not lines[i].startswith(("|", "```", "# ", ">"))
               and not ROW.match(lines[i])):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "".join(out)


def render_slide(raw: str, number: int, total: int) -> str:
    """One `## Slide N — Title` block becomes one <section>.

    The `Slide N` half is dropped: the number is already in the corner. What
    is left is the eyebrow — the section, small and quiet above the headline.

    `## Slide N` with nothing after it draws no eyebrow. That is for a slide
    whose headline is the whole slide: slides 1 and 4.
    """
    lines = raw.split("\n")
    kicker = ""
    if lines and lines[0].startswith("## "):
        kicker = lines[0][3:].strip()
        lines = lines[1:]

    label = kicker
    kicker = re.sub(r"^Slide\s+\d+\s*[—-]?\s*", "", kicker)

    body = render_blocks(lines)

    # A headline left on the tail of a paragraph renders as a literal "#" on
    # the slide, and nothing else complains. It shipped once. Refuse it.
    if "# " in re.sub(r"<pre>.*?</pre>", "", body, flags=re.DOTALL):
        raise SystemExit(
            f"slide {number}: a '#' is inside a paragraph. A headline must "
            f"start its own line in slides.md.")

    pct = round(number / total * 100, 2)
    return (
        f'<section class="slide" id="s{number}" aria-label="{html.escape(label)}">'
        f'<div class="stage">'
        + (f'<p class="eyebrow">{inline(kicker)}</p>' if kicker else "")
        + f'<div class="body">{body}</div>'
        f'</div>'
        f'<p class="num">{number} / {total}</p>'
        f'<div class="bar"><span style="width:{pct}%"></span></div>'
        f"</section>"
    )


# ---------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------

# Slide type is not in tokens.css — that file is sized for a 1240px app page,
# where the largest value is 38px. A deck read from the back of a room needs
# a bigger scale, so one is set here and only here. Reported as a gap.
DECK_CSS = """
/* ---- the deck's own scale. Everything else comes from tokens.css -------- */
:root {
  --d-head:    54px;  /* the headline. The argument, read in one second      */
  --d-body:    30px;  /* body. The floor is 28px: readable from the back     */
  --d-table:   28px;
  --d-code:    27px;  /* the graph on slide 8. Mono, because it is drawn     */
  --d-foot:    24px;  /* a source, a date, a caveat. Never the argument      */
  --d-eyebrow: 20px;  /* which section this is. Not read out                 */
  --d-label:   19px;  /* the name of a block. A label, never a sentence      */
  --d-stage:  1240px; /* --v-page-max: the column the product uses           */

  /* ---- the accent. DECK ONLY. Never in the product, never in tokens.css --
     Every hue in tokens.css is spoken for: 160 and 80 are two of the three
     answers, 25 means something broke, 330 means the app is working on this
     right now. Borrowing any of them would teach the room a meaning twenty
     minutes before the demo uses it for real. So the deck takes the one
     direction none of them occupy — violet, 285 — and takes it nowhere else.
     It marks three things: the eyebrow, a block label, and the one line on
     a slide that matters. Nothing else in the deck carries a hue except the
     three answer colours, where they mean the three answers.              */
  --d-accent:      oklch(0.800 0.115 285);  /* the line that matters        */
  --d-accent-dim:  oklch(0.660 0.075 285);  /* eyebrow, block label         */
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  background: var(--v-bg-0);
  color: var(--v-ink);
  font-family: var(--v-font-ui);
  font-size: var(--d-body);
  line-height: var(--v-lh-lead);
}

.slide {
  position: relative;
  width: 100vw;
  height: 100vh;
  padding: var(--v-s-8) var(--v-s-8) var(--v-s-7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;           /* a slide that does not fit is a content bug */
  border-bottom: 1px solid var(--v-line);   /* only seen when scrolling */
}

.stage { width: 100%; max-width: var(--d-stage); margin: 0 auto; }

/* ---- the four parts of a slide ------------------------------------------
   Eyebrow, headline, body, footnote. They are told apart by size, weight and
   ink step — not by hue. Every hue in tokens.css is spoken for: rose means
   "working right now", the three answer colours mean the three answers, red
   means something broke. A deck has no accent of its own, so the hierarchy is
   built from contrast, which is also what survives greyscale and the back row.
   ------------------------------------------------------------------------ */

.eyebrow {
  margin: 0 0 var(--v-s-5);
  max-width: none;          /* a section label never wraps if it can help it */
  font-size: var(--d-eyebrow);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--d-accent-dim);
}

h1 {
  margin: 0 0 var(--v-s-5);
  max-width: 40ch;      /* 40, not 34: a ruling headline sets the measure */
  font-family: var(--v-font-display);
  font-weight: var(--v-weight-bold);
  font-size: var(--d-head);
  line-height: var(--v-lh-answer);
  color: var(--v-ink-strong);
}

/* A headline that follows body copy is the punchline, not the title. It gets
   air above it so the eye lands on it last and hardest. */
:not(h1) + h1 { margin-top: var(--v-s-6); }

p, ul { margin: 0 0 var(--v-s-5); max-width: 62ch; color: var(--v-ink-2); }
.body > :last-child { margin-bottom: 0; }
li { margin-bottom: var(--v-s-2); }
strong { color: var(--v-ink-strong); font-weight: var(--v-weight-medium); }

/* ---- labelled blocks ----------------------------------------------------
   Two to four parts, each with a name. The name is the accent, small and
   in caps; the text beside it is ordinary body. A room reads the names down
   the left and knows the shape of the slide before hearing a word of it.
   ------------------------------------------------------------------------ */

.stack { margin: 0 0 var(--v-s-6); }
.row {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: var(--v-s-5);
  align-items: baseline;
  padding: var(--v-s-3) 0;
  border-bottom: 1px solid var(--v-line);
  color: var(--v-ink-2);
  line-height: var(--v-lh-body);
}
.row:first-child { border-top: 1px solid var(--v-line); }
.row .t {
  font-size: var(--d-label);
  font-weight: var(--v-weight-medium);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--d-accent-dim);
}

/* The one line on a slide that matters, when it is not the headline. */
.hi { color: var(--d-accent); }

.foot {
  max-width: 62ch;
  font-size: var(--d-foot);
  line-height: var(--v-lh-body);
  color: var(--v-ink-4);
}
h1 + /* ---- labelled blocks ----------------------------------------------------
   Two to four parts, each with a name. The name is the accent, small and
   in caps; the text beside it is ordinary body. A room reads the names down
   the left and knows the shape of the slide before hearing a word of it.
   ------------------------------------------------------------------------ */

.stack { margin: 0 0 var(--v-s-6); }
.row {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: var(--v-s-5);
  align-items: baseline;
  padding: var(--v-s-3) 0;
  border-bottom: 1px solid var(--v-line);
  color: var(--v-ink-2);
  line-height: var(--v-lh-body);
}
.row:first-child { border-top: 1px solid var(--v-line); }
.row .t {
  font-size: var(--d-label);
  font-weight: var(--v-weight-medium);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--d-accent-dim);
}

/* The one line on a slide that matters, when it is not the headline. */
.hi { color: var(--d-accent); }

.foot { margin-top: calc(var(--v-s-5) * -1 + var(--v-s-3)); }

/* Inline code stays in the UI face on purpose. tokens.css reserves mono for
   lines quoted out of a resume, and a library name is not one. */
code {
  padding: 0.08em 0.32em;
  background: var(--v-bg-2);
  border-radius: var(--v-radius-2);
  color: var(--v-ink);
  font-family: inherit;
}

pre {
  margin: 0 0 var(--v-s-5);
  padding: var(--v-s-5);
  background: var(--v-bg-205);
  border-left: var(--v-quote-edge) solid var(--v-line-strong);
  border-radius: var(--v-radius-3);
  font-family: var(--v-font-mono);   /* drawn with characters. It must align */
  font-size: var(--d-code);
  line-height: var(--v-lh-body);
  color: var(--v-ink);
  overflow: hidden;
}

table {
  width: 100%;
  margin: 0 0 var(--v-s-5);
  border-collapse: collapse;
  font-size: var(--d-table);
}
th, td { padding: var(--v-s-3) var(--v-s-4); text-align: left; }
th {
  font-size: var(--d-eyebrow);
  font-weight: var(--v-weight-medium);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--v-ink-4);
  border-bottom: 1px solid var(--v-line-strong);
}
td { color: var(--v-ink-2); border-bottom: 1px solid var(--v-line); }

/* The three answers, and nothing else in the deck, carry a hue. */
th.v-shown  { color: var(--v-shown); }
th.v-partly { color: var(--v-partly); }
th.v-not    { color: var(--v-not); }
tbody tr:nth-child(odd) td { background: var(--v-bg-212); }

.num {
  position: absolute;
  right: var(--v-s-6);
  bottom: var(--v-s-5);
  margin: 0;
  font-size: var(--d-eyebrow);
  color: var(--v-ink-4);
}

.bar {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: var(--v-quote-edge);
  background: var(--v-bg-2);
}
.bar span { display: block; height: 100%; background: var(--v-ink-4); }

/* ---- presenting ---------------------------------------------------------
   Without the script the page is still the whole deck, scrolled. The script
   only hides the other slides; it decides nothing.
   ------------------------------------------------------------------------ */
body.js .slide { display: none; }
body.js .slide.on { display: flex; }

/* ---- Cmd+P: one slide per page, the backup that needs no browser -------- */
@media print {
  @page { size: 1440px 810px; margin: 0; }
  html, body { background: #fff; }
  body.js .slide, body.js .slide.on { display: flex; }
  .slide {
    width: 1440px;
    height: 810px;
    border: 0;
    break-after: page;
    page-break-after: always;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: var(--v-bg-0);
  }
  .slide:last-child { break-after: auto; page-break-after: auto; }
}
"""

SCRIPT = """
// Keys and the counter. Nothing else. If this never runs, the deck is still
// the whole deck, top to bottom, by scrolling.
(function () {
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  if (!slides.length) return;
  document.body.classList.add('js');
  var at = 0;
  function show(n) {
    at = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (s, i) { s.classList.toggle('on', i === at); });
    if (location.hash !== '#s' + (at + 1)) history.replaceState(null, '', '#s' + (at + 1));
  }
  var m = /^#s(\\d+)$/.exec(location.hash);
  show(m ? parseInt(m[1], 10) - 1 : 0);
  document.addEventListener('keydown', function (e) {
    var k = e.key;
    if (k === 'ArrowRight' || k === 'ArrowDown' || k === ' ' || k === 'PageDown') { show(at + 1); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'ArrowUp' || k === 'Backspace' || k === 'PageUp') { show(at - 1); e.preventDefault(); }
    else if (k === 'Home') { show(0); }
    else if (k === 'End') { show(slides.length - 1); }
    else if (k === 'f' || k === 'F') {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    }
  });
  document.addEventListener('click', function () { show(at + 1); });
})();
"""


def build() -> int:
    preamble, raws = split_source(SOURCE.read_text(encoding="utf-8"))
    total = len(raws)
    slides = "".join(render_slide(r, i + 1, total) for i, r in enumerate(raws))

    tokens = TOKENS.read_text(encoding="utf-8")
    if "url(" in re.sub(r"/\*.*?\*/", "", tokens, flags=re.DOTALL):
        raise SystemExit("tokens.css has a live url() — it would be fetched. Stop.")

    title = "Slides — Vouch"
    page = (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width={STAGE_W}">'
        f"<title>{title}</title>\n"
        "<!-- Generated by build.py from slides.md. Do not edit this file. -->\n"
        f"<style>\n{tokens}\n{DECK_CSS}</style></head>\n"
        f"<body>{slides}<script>{SCRIPT}</script></body></html>\n"
    )
    # Nothing may point off this machine. Checked before it is written, so a
    # bad deck never reaches disk.
    live = re.sub(r"/\*.*?\*/|<!--.*?-->", "", page, flags=re.DOTALL)
    outside = re.findall(r'(?:https?:|url\(|@import|src=|<link)', live)
    if outside:
        raise SystemExit(f"slides.html would reference something external: {outside}")

    TARGET.write_text(page, encoding="utf-8")

    # The running order at the top of slides.md is not a slide. It is dropped.
    print(f"{TARGET.relative_to(ROOT)}: {total} slides, "
          f"{len(page.encode()):,} bytes, running order dropped "
          f"({len(preamble.splitlines())} lines).")
    return total


# ---------------------------------------------------------------------------
# --check: does every slide fit, and is anything fetched
# ---------------------------------------------------------------------------

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROBE = """
<style>.slide { height: %dpx !important; }</style>
<script>
window.addEventListener('load', function () {
  var out = [].slice.call(document.querySelectorAll('.slide')).map(function (s, i) {
    s.classList.add('on');
    var st = s.querySelector('.stage');
    return {n: i + 1,
            need: Math.ceil(st.getBoundingClientRect().height),
            have: s.clientHeight - %d,
            wide: Math.ceil(st.scrollWidth) > Math.ceil(st.clientWidth)};
  });
  // Everything this document fetched, asked of the document. A net log cannot
  // be used for this: it also carries Chrome's own housekeeping, which has
  // nothing to do with the deck.
  var got = performance.getEntriesByType('resource').map(function (e) { return e.name; });
  document.title = 'FIT ' + JSON.stringify({slides: out, fetched: got});
});
</script>
"""


def _chrome(args: list[str], out: Path, wait: float = 45.0) -> str:
    """Run Chrome headless and stop it once it has dumped.

    It does not reliably exit on its own on this machine, so it is started,
    watched for output, and then asked to stop.
    """
    with out.open("w") as fh:
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--no-first-run", "--no-default-browser-check",
             # Chrome's own housekeeping. Off, so the machine stays quiet while
             # a file:// page is being looked at.
             "--disable-background-networking", "--disable-component-update",
             "--disable-sync", "--disable-default-apps", "--disable-extensions",
             "--disable-client-side-phishing-detection", "--metrics-recording-only",
             "--disable-features=Translate,OptimizationHints,MediaRouter"] + args,
            stdout=fh, stderr=subprocess.DEVNULL)
        deadline = time.time() + wait
        while time.time() < deadline:
            if proc.poll() is not None or out.stat().st_size > 0:
                break
            time.sleep(0.5)
        time.sleep(1.5)
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
    return out.read_text(errors="replace")


def check(total: int) -> None:
    if not Path(CHROME).exists():
        print("no Chrome on this machine; fit not measured")
        return

    pad = 72 + 52  # --v-s-8 top, --v-s-7 bottom: the slide's own padding
    probe = TARGET.read_text(encoding="utf-8").replace(
        "</body>", (PROBE % (STAGE_H, pad)) + "</body>")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        page = tmp / "probe.html"
        page.write_text(probe, encoding="utf-8")

        dom = _chrome([f"--user-data-dir={tmp}/profile",
                       f"--window-size={STAGE_W},{STAGE_H}",
                       "--virtual-time-budget=3000",
                       "--dump-dom", page.as_uri()], tmp / "dom.html")

    m = re.search(r"<title>FIT (.*?)</title>", dom, re.DOTALL)
    if not m:
        print("fit NOT measured: the probe did not report")
        return

    got = json.loads(html.unescape(m.group(1)))
    bad = [s for s in got["slides"] if s["need"] > s["have"] or s["wide"]]
    for s in bad:
        print(f"  slide {s['n']}: needs {s['need']}px, has {s['have']}px, "
              f"over by {s['need'] - s['have']}px"
              + (" — and too wide" if s["wide"] else ""))
    if bad:
        print(f"fit: {len(bad)} of {total} slides do not fit at "
              f"{STAGE_W}x{STAGE_H}. That is content, for brief 0022. "
              "Do not shrink the type.")
    else:
        print(f"fit: all {total} slides fit at {STAGE_W}x{STAGE_H}, type unchanged")

    print(f"fetched by the page: {len(got['fetched'])}"
          + (f" — {got['fetched']}" if got["fetched"] else " (nothing)"))


if __name__ == "__main__":
    n = build()
    if "--check" in sys.argv:
        check(n)

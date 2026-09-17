#!/usr/bin/env python3
"""Build slides.html from slides.md.

    python3 docs/presentation/build.py

Standard library only. Nothing is fetched when the deck is opened: the design
tokens are inlined from design/tokens.css and the two typefaces are inlined as
base64 data URIs, because a <link> or a url(https://…) is a fetch and a fetch
fails on file:// with the wifi off (decision 0002).

The faces are Archivo and Source Serif 4, both open licence. They are
downloaded once into docs/presentation/fonts/ and cached there. Only this
script ever goes to the network, and only when that cache is empty:

    python3 docs/presentation/build.py --fonts     refresh the cache

If the cache is empty and the download fails, the build still succeeds and
says so — the deck falls back to a system stack rather than shipping a <link>.

slides.md is the source. Never hand-edit slides.html.

To check that every slide fits on the stage, and that opening the file requests
nothing, run with a Chrome on the machine:

    python3 docs/presentation/build.py --check
"""

from __future__ import annotations

import base64
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
FONTS = HERE / "fonts"

# The stage is a fixed rectangle, scaled to fit whatever window it is opened
# in. Laying out against a fixed size is the only way a deck can be checked:
# "does it fit" has no answer until the box has a size.
STAGE_W = 1600
STAGE_H = 900
PAD_T, PAD_B = 94, 74          # the stage's own padding, top and bottom


# ---------------------------------------------------------------------------
# the two faces
# ---------------------------------------------------------------------------

# Google Fonts serves each family cut into unicode subsets. Only `latin` is
# kept: this deck is English, and latin already carries the punctuation it
# uses — the en dash, the middot, the curly quotes.
#
# Both families are variable fonts, so all the weights of one style arrive in
# a single file. One @font-face per file, with a weight *range*, is what keeps
# the base64 from being repeated once per weight.
GOOGLE = (
    "https://fonts.googleapis.com/css2"
    "?family=Archivo:wght@400;600;700;800"
    "&family=Source+Serif+4:ital,wght@0,400;0,600;1,400"
    "&display=block"
)
# Without it Google serves .ttf, which is roughly three times the size.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

MANIFEST = FONTS / "faces.json"


def _curl(url: str) -> bytes:
    """Fetch, with curl rather than urllib.

    The python.org build on this machine carries no root certificates, so
    urllib cannot open an https connection at all. curl uses the system trust
    store and is already here.
    """
    out = subprocess.run(["curl", "-fsS", "-A", UA, url],
                         capture_output=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode(errors="replace").strip())
    return out.stdout


def fetch_fonts() -> list[dict]:
    """Download the latin faces into the cache. Returns the manifest."""
    css = _curl(GOOGLE).decode()
    faces: dict[tuple[str, str, str], list[int]] = {}
    for subset, block in re.findall(r"/\* (\S+) \*/\s*(@font-face \{.*?\})",
                                    css, re.DOTALL):
        if subset != "latin":
            continue
        fam = re.search(r"font-family: '([^']+)'", block).group(1)
        style = re.search(r"font-style: (\S+);", block).group(1)
        weight = int(re.search(r"font-weight: (\S+);", block).group(1))
        url = re.search(r"src: url\((\S+)\)", block).group(1)
        faces.setdefault((fam, style, url), []).append(weight)
    if not faces:
        raise RuntimeError("no latin @font-face in the Google Fonts reply")

    FONTS.mkdir(exist_ok=True)
    manifest = []
    for (fam, style, url) in faces:
        weights = faces[(fam, style, url)]
        name = f"{fam.lower().replace(' ', '-')}-{style}.woff2"
        (FONTS / name).write_bytes(_curl(url))
        manifest.append({"family": fam, "style": style, "file": name,
                         "weights": [min(weights), max(weights)]})
    manifest.sort(key=lambda f: (f["family"], f["style"]))
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def font_css(refresh: bool) -> tuple[str, list[str]]:
    """Return (the @font-face rules, a line per face for the build report).

    An empty rule set is not a failure. It means the faces could not be had,
    and the stacks below fall through to what is on the machine. Shipping a
    <link> instead is the one thing that is not allowed.
    """
    manifest = None
    if not refresh and MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        if any(not (FONTS / f["file"]).exists() for f in manifest):
            manifest = None
    if manifest is None:
        try:
            manifest = fetch_fonts()
        except Exception as exc:                      # offline, or blocked
            return "", [f"fonts NOT embedded ({exc}); "
                        f"falling back to the system stack"]

    rules, said = [], []
    for f in manifest:
        raw = (FONTS / f["file"]).read_bytes()
        b64 = base64.b64encode(raw).decode()
        lo, hi = f["weights"]
        rules.append(
            f'@font-face{{font-family:"{f["family"]}";'
            f'font-style:{f["style"]};'
            f'font-weight:{lo}{"" if lo == hi else f" {hi}"};'
            f'font-stretch:100%;font-display:block;'
            f'src:url("data:font/woff2;base64,{b64}") format("woff2")}}')
        said.append(f'{f["family"]} {f["style"]} '
                    f'{lo}{"" if lo == hi else f"-{hi}"}, '
                    f'{len(raw):,} B raw / {len(b64):,} B inlined')
    return "\n".join(rules) + "\n", said


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


def deck_name(preamble: str) -> str:
    """The product name, off the `# Slides — Vouch` line. Slide 1 sets it big."""
    m = re.search(r"^#\s+.*?[—-]\s*(\S.*?)\s*$", preamble, flags=re.MULTILINE)
    return m.group(1) if m else "Vouch"


def sections(preamble: str, total: int) -> list[str]:
    """The header bar text for each slide, from the shape table in slides.md.

    The table already says which slides belong to which part of the talk.
    That part name is what the reference deck puts in its header bar: it does
    not change slide to slide, so the room can see which movement it is in.
    """
    out = [""] * total
    rows = [r for r in preamble.splitlines() if r.startswith("|")]
    head = next((i for i, r in enumerate(rows) if "Slides" in r), None)
    if head is None:
        return out
    for row in rows[head + 2:]:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        m = re.match(r"^(\d+)(?:\s*[–—-]\s*(\d+))?$", cells[1])
        if not m:
            break                     # the shape table has ended
        lo = int(m.group(1))
        hi = int(m.group(2) or m.group(1))
        for n in range(lo, hi + 1):
            if 1 <= n <= total:
                out[n - 1] = cells[0]
    return out


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


# The only hue in the deck that is not the accent. A column called "evidenced"
# or "partly" is the product's own language, so it keeps the product's own
# colour (brief 0025).
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
    """Blocks: headline, footnote, fenced code, table, bullet list, paragraph.

    Two kinds of paragraph, because the reference deck has two. `.lead` is the
    thesis — large, short measure, the sentence the room is meant to take
    away. `.body` is the reasoning underneath it — serif, small, set in a
    ruled block so it cannot be mistaken for the headline's equal.

    A paragraph is a lead if it sits directly under the headline, or if it
    carries the slide's accent. Both are the same test in different words:
    is this the line that matters.
    """
    out: list[str] = []
    i = 0
    prev = ""
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
            prev = "pre"
            i = j + 1
            continue

        if line.startswith("# "):
            out.append(f"<h2>{inline(line[2:].strip())}</h2>")
            prev = "h"
            i += 1
            continue

        # A blockquote is the footnote: a source, a date, a caveat. Serif,
        # italic and quiet, so it cannot be mistaken for the argument.
        if line.startswith(">"):
            j = i
            note: list[str] = []
            while j < len(lines) and lines[j].startswith(">"):
                note.append(lines[j].lstrip(">").strip())
                j += 1
            out.append(f'<p class="src">{inline(" ".join(note))}</p>')
            prev = "src"
            i = j
            continue

        if line.startswith("|"):
            j = i
            rows: list[str] = []
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(lines[j])
                j += 1
            out.append(render_table(rows))
            prev = "table"
            i = j
            continue

        # `LABEL :: text` — a labelled block. A run of them is one stack.
        # Most slides are two to four parts and each part has a name; naming
        # them beats a paragraph the room has to parse.
        if ROW.match(line):
            j = i
            rows = []
            while j < len(lines) and ROW.match(lines[j]):
                m = ROW.match(lines[j])
                rows.append(f'<div class="row"><span class="t">{inline(m.group(1))}'
                            f'</span><span>{inline(m.group(2))}</span></div>')
                j += 1
            out.append('<div class="stack">' + "".join(rows) + "</div>")
            prev = "stack"
            i = j
            continue

        if line.lstrip().startswith(("- ", "* ")):
            j = i
            items: list[str] = []
            while j < len(lines) and lines[j].lstrip().startswith(("- ", "* ")):
                items.append(lines[j].lstrip()[2:].strip())
                j += 1
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
            prev = "ul"
            i = j
            continue

        para: list[str] = []
        while (i < len(lines) and lines[i].strip()
               and not lines[i].startswith(("|", "```", "# ", ">"))
               and not ROW.match(lines[i])):
            para.append(lines[i].strip())
            i += 1
        text = inline(" ".join(para))
        if prev == "h" or "hi" in re.findall(r'class="(\w+)"', text):
            out.append(f'<p class="lead">{text}</p>')
        else:
            out.append(f'<div class="body"><p>{text}</p></div>')
        prev = "p"

    return "".join(out)


def guard(body: str, number: int) -> None:
    """A headline left on the tail of a paragraph renders as a literal "#" on
    the slide, and nothing else complains. It shipped once. Refuse it."""
    if "# " in re.sub(r"<pre>.*?</pre>", "", body, flags=re.DOTALL):
        raise SystemExit(
            f"slide {number}: a '#' is inside a paragraph. A headline must "
            f"start its own line in slides.md.")


def render_title(raw: str, name: str) -> str:
    """Slide 1. A kicker of metadata, the product name set large, the thesis.

    Every word here is already in slides.md. The byline becomes the kicker,
    because that is what it is — who, and for whom. The headline becomes the
    lead. The paragraph under it stays where it is. Nothing is rewritten; the
    only thing that changes is which size each part is set at.
    """
    lines = [l for l in raw.split("\n") if not l.startswith("## ")]
    head = next((l[2:].strip() for l in lines if l.startswith("# ")), "")
    byline = " ".join(l.lstrip(">").strip() for l in lines if l.startswith(">"))
    rest = [l for l in lines
            if l.strip() and not l.startswith(("# ", ">"))]
    return (
        f'<p class="kicker">{inline(byline)}</p>'
        f"<h1>{inline(name)}</h1>"
        f'<p class="lead wide">{inline(head)}</p>'
        f'<div class="body"><p>{inline(" ".join(s.strip() for s in rest))}</p></div>'
    )


def render_slide(raw: str, number: int, total: int, name: str,
                 section: str) -> str:
    """One `## Slide N — Title` block becomes one <section>.

    The `Slide N` half is dropped: the number is already in the corner. What
    is left is the kicker — what this slide is, small and gold above the
    headline. The header bar above it carries the part of the talk, which
    does not change slide to slide.

    `## Slide N` with nothing after it draws no kicker. That is for a slide
    whose headline is the whole slide: slides 1 and 5.
    """
    lines = raw.split("\n")
    kicker = ""
    if lines and lines[0].startswith("## "):
        kicker = lines[0][3:].strip()
        lines = lines[1:]

    label = kicker
    kicker = re.sub(r"^Slide\s+\d+\s*[—-]?\s*", "", kicker)

    if number == 1:
        flow = render_title(raw, name)
        guard(flow, number)
        cls = " title"
    else:
        body = render_blocks(lines)
        guard(body, number)
        flow = (f'<p class="kicker">{inline(kicker)}</p>' if kicker else "") + body
        cls = ""

    hdr = section or name
    return (
        f'<section class="slide" id="s{number}" aria-label="{html.escape(label)}">'
        f'<div class="stage">'
        f'<div class="hdr">{inline(hdr)}</div>'
        f'<div class="flow{cls}">{flow}</div>'
        f'<div class="num">{number:02d} / {total:02d}</div>'
        f"</div></section>"
    )


# ---------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------

# The deck's look is taken wholesale from the author's own Enterprise Brain
# deck (brief 0027): the palette, the type scale, the fixed stage, the header
# bar, and the four components a slide is built out of. Only the verdict
# colours are Vouch's own, and they come from tokens.css — they mean something
# the demo relies on twenty minutes later.
DECK_CSS = """
/* ---- the deck's own palette. Not the product's; a deck is not an app ----- */
:root {
  --ink:        #10141B;   /* the slide                                      */
  --ink2:       #1A212B;   /* a block inside a slide                         */
  --paper:      #EDEAE3;   /* headline and strong text, warm off white       */
  --muted:      #8B94A1;   /* secondary text                                 */
  --signal:     #D4A342;   /* the accent                                     */
  --signal-dim: #5A4820;   /* the body block's left rule                     */
  --live:       #5E9E8F;   /* a second accent                                */
  --edge:       #2A323D;   /* borders, and the gaps a grid shows through     */
  --dim:        #6C7683;   /* a footnote, a slide number                     */
  --read:       #B8BFC8;   /* serif body copy                                */
  --k: 1;                  /* the stage's scale. The script sets it          */

  --ui:    "Archivo", system-ui, -apple-system, "Helvetica Neue", sans-serif;
  --serif: "Source Serif 4", Georgia, "Times New Roman", serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: #080A0E;
  color: var(--paper);
  font-family: var(--ui);
  -webkit-font-smoothing: antialiased;
}
body { overflow: hidden; }

/* ---- the stage ----------------------------------------------------------
   A slide is a fixed 1600x900 rectangle, scaled to whatever window it is
   opened in. Laying out against a fixed size is the only way "does it fit"
   has an answer at all: a percentage cannot be checked.
   ------------------------------------------------------------------------ */

.slide { height: 100vh; display: grid; place-items: center; overflow: hidden; }

.stage {
  position: relative;
  width: 1600px;
  height: 900px;
  flex: none;
  transform: scale(var(--k));
  transform-origin: center center;
  background: var(--ink);
  padding: 94px 84px 74px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;        /* a slide that does not fit is a content bug */
}

/* The part of the talk. It does not change slide to slide, so the room can
   see which movement it is in without being told. */
.hdr {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 46px;
  padding: 0 84px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--edge);
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.num {
  position: absolute;
  right: 84px; bottom: 24px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #4E5764;
}

/* ---- the parts of a slide ----------------------------------------------- */

.kicker {
  margin-bottom: 24px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.17em;
  text-transform: uppercase;
  color: var(--signal);
}

h1 {          /* the title slide only */
  font-size: 102px;
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
}

h2 {          /* every headline. The argument, read in one second */
  font-size: 58px;
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.027em;
  max-width: 24ch;
}

h3 { font-size: 23px; font-weight: 600; line-height: 1.18; }

/* A headline that follows anything is the punchline, not the title. It gets
   air above it, so the eye lands on it last and hardest. */
.flow > * + h2 { margin-top: 38px; }

/* The thesis: the sentence the room is meant to leave with. */
.lead { font-size: 29px; line-height: 1.36; max-width: 38ch; margin-top: 24px; }
.lead.wide { max-width: 52ch; }

/* The reasoning under the thesis. Serif and small on purpose: it is read, not
   glanced at, and it must not compete with the headline. */
.body {
  margin-top: 24px;
  padding-left: 22px;
  border-left: 2px solid var(--signal-dim);
  max-width: 78ch;
  font-family: var(--serif);
  font-size: 17.5px;
  line-height: 1.58;
  color: var(--read);
}
.body p + p { margin-top: 0.55em; }
.body strong { color: var(--paper); font-weight: 600; }

/* A source, a date, a caveat. Never the argument. */
.src {
  margin-top: 14px;
  font-family: var(--serif);
  font-style: italic;
  font-size: 15px;
  line-height: 1.45;
  color: var(--dim);
}
.src strong { font-style: normal; color: var(--muted); }
/* A box around a report number inside an italic footnote is one box too many.
   The footnote is already set apart; the code just stands upright. */
.src code { padding: 0; background: none; font-style: normal; color: var(--muted); }

/* The one line on a slide that matters, when it is not the headline. */
.hi { color: var(--signal); }
strong { color: var(--paper); font-weight: 700; }

/* ---- labelled blocks ----------------------------------------------------
   Two to four parts, each with a name. The room reads the names down the
   left and knows the shape of the slide before hearing a word of it.
   ------------------------------------------------------------------------ */

.stack { display: flex; flex-direction: column; margin-top: 24px; }
.row {
  display: flex;
  align-items: baseline;
  gap: 22px;
  padding: 13px 0;
  border-bottom: 1px solid var(--edge);
  font-size: 22px;
  line-height: 1.33;
}
.row .t {
  min-width: 230px;
  flex: none;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.13em;
  color: var(--muted);
}

ul { list-style: none; margin-top: 20px; }
li {
  padding: 9px 0;
  border-top: 1px solid var(--edge);
  font-size: 19px;
  line-height: 1.4;
  color: #C3CAD3;
}
li:first-child { border-top: none; }

/* Inline code stays in the UI face on purpose. tokens.css reserves mono for
   lines quoted out of a resume, and a library name is not one. */
code {
  padding: 0.08em 0.34em;
  background: var(--ink2);
  border-radius: 3px;
  color: var(--paper);
  font-family: inherit;
  font-size: 0.94em;
}

/* Slide 8's graph. Drawn with characters, so it must align. */
pre {
  margin-top: 24px;
  padding: 22px 24px;
  background: var(--ink2);
  border-left: 4px solid var(--signal-dim);
  font-family: var(--v-font-mono);
  font-size: 19px;
  line-height: 1.55;
  color: var(--read);
  overflow: hidden;
}

/* ---- the one table, on slide 6 ------------------------------------------
   The three answer colours are the product's own, out of tokens.css. They
   mean on this slide exactly what they mean in the demo twenty minutes
   later, so nothing here borrows them and nothing here overrides them.
   ------------------------------------------------------------------------ */

table {
  width: 100%;
  margin-top: 24px;
  border-collapse: collapse;
  font-size: 20px;
  background: var(--ink2);
}
th, td { padding: 13px 18px; text-align: left; line-height: 1.35; }
th {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted);
  border-bottom: 1px solid var(--edge);
}
td { color: var(--read); border-bottom: 1px solid var(--edge); }
tr:last-child td { border-bottom: none; }
th.v-shown  { color: var(--v-shown); }
th.v-partly { color: var(--v-partly); }
th.v-not    { color: var(--v-not); }

/* ---- presenting ---------------------------------------------------------
   Without the script the page is still the whole deck, scrolled. The script
   scales the stage and hides the other slides; it decides nothing.
   ------------------------------------------------------------------------ */
body.js { overflow: hidden; }
body.js .slide { display: none; }
body.js .slide.on { display: grid; }
body:not(.js) { overflow: auto; }

/* ---- Cmd+P: one slide per page, the backup that needs no browser -------- */
@media print {
  @page { size: 1600px 900px; margin: 0; }
  html, body { overflow: visible; background: #fff; }
  :root { --k: 1; }
  body.js .slide, body.js .slide.on, .slide {
    display: block;
    width: 1600px;
    height: 900px;
    break-after: page;
    page-break-after: always;
  }
  .stage {
    transform: none;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .slide:last-child { break-after: auto; page-break-after: auto; }
}
"""

SCRIPT = """
// The scale, the keys and the counter. Nothing else. If this never runs, the
// deck is still the whole deck, top to bottom, by scrolling.
(function () {
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  if (!slides.length) return;
  function scale() {
    document.documentElement.style.setProperty(
      '--k', Math.min(window.innerWidth / 1600, window.innerHeight / 900));
  }
  scale();
  window.addEventListener('resize', scale);
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


def build(refresh_fonts: bool = False) -> int:
    preamble, raws = split_source(SOURCE.read_text(encoding="utf-8"))
    total = len(raws)
    name = deck_name(preamble)
    parts = sections(preamble, total)
    slides = "".join(render_slide(r, i + 1, total, name, parts[i])
                     for i, r in enumerate(raws))

    tokens = TOKENS.read_text(encoding="utf-8")
    if "url(" in re.sub(r"/\*.*?\*/", "", tokens, flags=re.DOTALL):
        raise SystemExit("tokens.css has a live url() — it would be fetched. Stop.")

    faces, said = font_css(refresh_fonts)

    title = f"Slides — {name}"
    page = (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width={STAGE_W}">'
        f"<title>{html.escape(title)}</title>\n"
        "<!-- Generated by build.py from slides.md. Do not edit this file. -->\n"
        f"<style>\n{faces}{tokens}\n{DECK_CSS}</style></head>\n"
        f"<body>{slides}<script>{SCRIPT}</script></body></html>\n"
    )
    # Nothing may point off this machine. Checked before it is written, so a
    # bad deck never reaches disk. A data: URI is not off the machine — it is
    # the file itself — so those are removed first and everything else that
    # smells of a fetch is refused.
    live = re.sub(r"/\*.*?\*/|<!--.*?-->", "", page, flags=re.DOTALL)
    live = re.sub(r'url\("data:[^"]*"\)', "", live)
    outside = re.findall(r'(?:https?:|url\(|@import|src=|<link)', live)
    if outside:
        raise SystemExit(f"slides.html would reference something external: {outside}")

    TARGET.write_text(page, encoding="utf-8")

    # The running order at the top of slides.md is not a slide. It is dropped.
    print(f"{TARGET.relative_to(ROOT)}: {total} slides, "
          f"{len(page.encode()):,} bytes, running order dropped "
          f"({len(preamble.splitlines())} lines).")
    for line in said:
        print(f"  font: {line}")
    return total


# ---------------------------------------------------------------------------
# --check: does every slide fit, and is anything fetched
# ---------------------------------------------------------------------------

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROBE = """
<style>:root{--k:1 !important}</style>
<script>
window.addEventListener('load', function () {
  var out = [].slice.call(document.querySelectorAll('.slide')).map(function (s, i) {
    s.classList.add('on');
    var f = s.querySelector('.flow');
    // offsetHeight, not a bounding rect: the stage is scaled, and a rect
    // would report the scaled size rather than the laid-out one.
    return {n: i + 1,
            need: f.offsetHeight,
            have: %d,
            wide: Math.ceil(f.scrollWidth) > Math.ceil(f.clientWidth)};
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

    room = STAGE_H - PAD_T - PAD_B
    probe = TARGET.read_text(encoding="utf-8").replace(
        "</body>", (PROBE % room) + "</body>")

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
    n = build("--fonts" in sys.argv)
    if "--check" in sys.argv:
        check(n)

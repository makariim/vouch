---
status: open
date: 2026-09-17
brief: 0027-copy-the-enterprise-brain-design
---

# 0027 — Copy the Enterprise Brain design

**The deck wears the reference's system. Zero requests with networking dead.
All 16 slides fit. `Cmd+P` still gives 16 pages. No slide word changed.**

One thing to rule on: **gold and amber collide on slide 6**, and it is worse in
the file than it sounded in the brief. Section *"The collision"*.

## Zero requests, and how it was checked

Three ways, because one of them proves less than it looks.

**Chrome with no network at all.** The page was rendered with DNS mapped to
nothing and the proxy pointed at a dead port:

```
--host-resolver-rules="MAP * ~NOTFOUND" --proxy-server="socks5://127.0.0.1:1"
```

The screenshot came out **byte-identical** to the one rendered with the network
up — same SHA-256. If a font were still being fetched, the offline render would
have fallen back to a system face and the two files would differ.

**The page asked itself.** `build.py --check` reads
`performance.getEntriesByType('resource')` after load and reports what the
document fetched. It says `0 (nothing)`.

**The file was read.** No `http`, no `https`, no `<link>`. Every `url(` in
`slides.html` is either a `data:` URI or inside a comment — `build.py` refuses
to write the file otherwise, and that guard now strips `data:` first so it
still rejects everything else.

I did **not** turn the wifi off with `networksetup`. That would have cut your
machine off mid-session, and killing DNS and the proxy inside Chrome is the
same test with a smaller blast radius. If you want the literal version, say so
and I will run it.

## The fonts

Both are variable fonts, so every weight of one style lives in one file. That
is why there are three files and not eight.

| Face | Weights | Raw | Inlined (base64) |
|---|---|---|---|
| Archivo, normal | 400–800 | 34,940 B | 46,588 B |
| Source Serif 4, normal | 400–600 | 50,924 B | 67,900 B |
| Source Serif 4, italic | 400 | 20,132 B | 26,844 B |

**`slides.html` is 187,006 bytes**, up from 45,724. The fonts are 141 KB of
that.

Two things kept it that small. Only the **`latin`** subset is kept — the deck is
English, and `latin` already carries the en dash, the middot and the curly
quotes it uses. And **Source Serif is requested without its optical-size axis**:
asking for `ital,wght` instead of `ital,opsz,wght` took that file from 122 KB to
51 KB, and nothing in the deck varies optical size.

The files are cached in `docs/presentation/fonts/` and committed. `build.py`
downloads them only when that cache is empty; `--fonts` forces a refresh. If the
download fails the build still succeeds, prints `fonts NOT embedded`, and the
stacks fall through to the system faces. It never writes a `<link>`.

One thing you should know: the download goes through **`curl`, not `urllib`**.
The python.org build on this machine carries no root certificates, so `urllib`
cannot open an HTTPS connection at all — it fails the handshake before it sends
a byte. `curl` uses the system trust store.

## The collision

**Gold sits badly beside the verdict colours on slide 6. It is a real problem,
not a near miss.**

`--signal` is `#D4A342`. `--v-partly` is `oklch(0.815 0.125 80)`. Those are the
same hue family. On slide 6 the table header **PARTLY** and the accent line
**"The verdict changed. Nothing about the model did."** read as one colour from
a metre away. A room that has just been taught *gold means the line that
matters* will meet amber twenty minutes later meaning *partly evidenced*.

I changed neither, as instructed. The three ways out, for you to pick:

- **Drop the accent on slide 6.** The headline already carries that slide. One
  slide loses its `==…==`, which is a slides.md change and therefore yours.
- **Move `--signal` off hue 80.** It stops being the reference's gold.
- **Leave it and say it out loud** in the demo script when slide 6 is up.

## What else changed

**`build.py`** — new palette, type scale, fixed stage and components, all from
the reference; the title slide; the header bar; the font pipeline; the fit
check now measures against the fixed 900px stage instead of the viewport.

While rewriting the stylesheet I found **the old `DECK_CSS` had a block pasted
into itself twice**, which turned the `.foot` rule into `h1 + .stack`. It is
gone with the rest of that stylesheet. It was never visible.

**`slides.html`** — regenerated. `slides.md` — untouched.

**Two things the source did not have, taken from the source anyway.** The
header bar needs a section name and the title slide needs a product name.
Rather than invent either, `build.py` reads them out of the preamble of
`slides.md`: the part names come from the shape table, the product name from
the `# Slides — Vouch` line. Nothing was written for this deck.

**Proof no word moved.** Every word in `slides.html` was counted against every
word in the slides half of `slides.md`. The only extras are the slide numbers,
those six part names, and "Vouch". The only word in the source and not the deck
is "Slide", from the `## Slide N` prefix, which the old build dropped too.

## What was run

```
python3 docs/presentation/build.py --check
```

That is the only command that wrote to the repository. It downloaded the three
`.woff2` files into `docs/presentation/fonts/` on its first run and has not
gone to the network since.

## The check

```
GATE: green. 12 check(s), each shown to reject the wrong and accept the right.
```

## Git status

```
 M docs/presentation/build.py
 M docs/presentation/slides.html
?? docs/briefs/0027-copy-the-enterprise-brain-design.md
?? docs/presentation/fonts/
?? docs/reports/0027-copy-the-enterprise-brain-design.md
```

Nothing staged.

## The three that matter

**Done but not asked for.** Air above a headline that follows a stack, and the
box taken off inline code inside a footnote. Both were the reference's spacing
applied to shapes the reference does not have — Vouch puts the headline *after*
the labelled blocks on nine slides, and the reference never does. Without the
first fix the headline sat on the last row's border.

**Asked for but not done.** `formwork/templates/report.md` says to set the
brief's `status` to `done`. Brief 0027 fences me to `docs/presentation/` and
this report, and the brief file is neither, so I left it `open`. The gate is
fine with that — `work-paired` only complains about a brief marked done with no
report. **Flip it yourself, or tell me the fence excepts it.**

**Wrong in the brief.** Nothing wrong, but one value did not survive contact.
The brief's type scale is the reference's, and the reference sets body copy at
17.5px on a 1600px stage. The old Vouch deck set 30px on a 1440px stage,
deliberately, "readable from the back". **The new deck's body copy is about
two-thirds the relative size of the old one.** I followed the brief, because the
brief is explicit and section 7 judges it against the reference. If the room is
deep, that is the number to revisit — not the headline, which got bigger.

Everything in the reference reproduced. The components Vouch has no content for
— `.two`, `.cols`, `.layer`, `.phases`, `.ask` — were not carried over, because
copying a component with nothing to put in it is copying the subject, which
section 6 forbids.

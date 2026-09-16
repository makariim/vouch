---
status: open
date: 2026-09-16
brief: 0016-detection-on-real-pages
---

# 0016 — Find the job post on any page

**The mechanism is replaced and it works. It has not been run on a real
LinkedIn page, because no session can reach one.**

Read that first, because every number below comes from a **reconstruction** —
a page I built to be laid out like a real one. The brief asked for real posts.
No network was used, per section 3, and no signed-in browser exists here. What
I could do instead, I did: build the furniture the real pages carry, switch the
known-site list off, and measure.

> **A reconstruction written by the session that wrote the scorer is exactly
> the failure `formwork/limits.md` names** — a check written by whoever wrote
> the thing it checks tends to pass for the wrong reason. Treat these numbers
> as "the rule separates prose from links on a page shaped like a real one",
> not as "it works on LinkedIn".

The real measurement is twenty minutes with a browser, by hand. It is the last
item in this report.

## The counts, with the site list switched off

`extension/tools/browser/extraction.py`. It copies the extension to a temporary
folder, sets `USE_KNOWN_SELECTORS` to false **in the copy**, and loads that.
Nothing in the repository is edited and the fast path cannot rescue anything.

Both counts are taken the way the panel takes its own — `candidate_requirements`
from `src/audit/prescreen.py`, over the text the extension actually sent.

| page | before | after |
|---|---|---|
| a LinkedIn job view, reconstructed | **45** | **27** |
| an Ashby posting, reconstructed | **40** | **27** |
| Northwind, a careers page nobody coded for | **57** | **27** |
| the plain job post from brief `0014` | 14 | 14 |
| a careers index — must not detect | — | **not detected** |
| an engineering blog post — must not detect | — | **not detected** |
| a news article about hiring — must not detect | — | **not detected** |

*before* is the old mechanism, reproduced in the harness and evaluated in the
page, so it is measured rather than remembered.

**27 is the honest number and 22 of it is the post.** The description in all
three pages is the same twenty-two-requirement post, which is why the three
*after* numbers are identical: the furniture is the variable, the post is not.
The five over twenty-two are the title line, the company-and-location line and
three lines of surrounding prose.

**What I cannot tell you is the real before.** The brief measured 79, 44 and 23
on real pages. My reconstructions carry less furniture than LinkedIn does, so
they start at 45 and 40. The direction is the same and the ratio is not.

## How the scorer decides

Four lines, as asked.

1. **Throw the furniture away first** — `nav`, `header`, `footer`, `aside`,
   `form`, `script`, `style`, and anything with a navigation, banner,
   complementary or contentinfo role. Removed before anything is measured, so a
   nav bar cannot lend its length to the block around it.
2. **Measure every remaining block on two numbers**: how many characters it
   holds, and what fraction of those sit inside a link.
3. **Score it `length × (1 − link density)³`**, length capped at 12,000, and
   reject anything at half links or more outright.
4. **Take the winner**, and read its text back with `innerText` so the line
   breaks survive — the pre-screen counts lines.

Two things in there were not guesses.

**The cube.** Squared was not enough. A wrapper holding the description *and* a
related-jobs list is longer than the description alone, and a gentle penalty
lets that length win. Cubed, a third of the characters being links costs about
two thirds of the score, and the description wins.

**Scoring reads `textContent`, not `innerText`.** `innerText` asks the browser
for layout, and this runs on every block of every page once a second. Only the
winner pays for layout. There is also a cache keyed on the URL plus the page's
total text length, so the work happens when a job changes and not otherwise.
**I did not measure the cost in milliseconds** — that needs a real page with a
real DOM, and it is on the same list as everything else here.

The known-site selectors stay, as a fast path only. **I removed `article` and
`main` from that list**, because they are not known-site selectors — they are
catch-alls, and they are precisely what swallowed the sidebar on both sites.

## The URL rules

`extension/tools/browser/url_rules.py`, new. It reads `URL_RULES` out of
`detect.js` and runs them in node, so what is tested is the shipped expressions
rather than a copy that can drift.

```
caught 14/14   false positives 0/10
```

**The four URLs from section 4 all detect**, including the two that missed:

| | |
|---|---|
| `linkedin.com/jobs/search-results/?currentJobId=…` | one pattern, mirrors the three LinkedIn rules already there |
| `…/careers?ashby_jid=…` | the job id **is** the rule |

The Ashby pattern is not tied to a host, because the point of an embedded board
is that the host is the company's own domain. It cannot fire on an index: an
index page carries no `ashby_jid`.

**The eight negatives are still quiet** — LinkedIn feed, a LinkedIn profile, the
LinkedIn jobs home, a company careers index, a Greenhouse board index, an Indeed
search, a news article, Hacker News. I added two more, because a new pattern is
a new way to fire on an index: **an Ashby board index** and **LinkedIn
search-results with no job open**. Both quiet.

**The detection bar is untouched.** Four heading words and 1,200 characters,
exactly as it was. `detection.py` re-run: **4 of 5, the same result as brief
`0014`**, the same miss — the very short post — and the three hard negatives
still correct.

## Where it still gets it wrong

The most useful part of this report, and it is a measured failure, not a
worry.

**A related-jobs list where only the title is a link defeats it.** Link density
is counted in characters. If the company name and the location sit *outside*
the anchor, a card list reads as two-thirds prose and the wrapper beats the
description. I hit this on my own first reconstruction: **57 before, 83 after.
Worse than the bug.**

`pages/cards-not-linked.html` is that page, kept deliberately, and it is in
every run of the harness. The fix is the same rule one level up: **a list item
that is thirty percent or more link counts entirely as link text.** A
description bullet with one inline link is untouched; a card is not. That page
now reads **27**, the same as the others.

Three places it can still go wrong, none of them fixed:

- **A description with no wrapper of its own** — headings and paragraphs
  directly under `body`. The scorer needs a block to win, and `body` is
  excluded. It falls back to the whole page, which is the old behaviour.
- **A page whose navigation is prose.** A careers index with a paragraph under
  each role would score like a description. The detection bar is what stops the
  badge there, not the scorer, and the index page in the harness is still
  quiet.
- **Text hidden by CSS.** Scoring reads `textContent`, which sees hidden
  templates; LinkedIn ships plenty. It could skew a score. Unmeasured.

## What I could not fix without leaving `extension/`

- **The real measurement.** LinkedIn needs a signed-in browser and Chrome 137
  removed `--load-extension`, so no scripted session can do it. It is the same
  twenty minutes by hand that standing has been carrying since wave two, and
  this brief does not clear it. **NOT ESTABLISHED.**
- **The brief points at the wrong document.** Section 4 says "the eight
  negatives brief `0008` lists". Brief `0008` lists none; the eight are in
  **report `0014`**, under *The URL rules, offline*. I tested those eight.
- **The four minutes.** Twenty-seven requirements at 3.4 seconds is about 90
  seconds, against a panel that promises about one minute. Better than four
  minutes and still not the promise. Whether that sentence changes or the audit
  gets faster is a backend or a copy question, and both are outside this folder.

## What changed

All inside `extension/`.

| File | Why |
|---|---|
| `src/detect.js` | the scorer; two URL patterns; `article` and `main` out of the fast path |
| `tools/browser/extraction.py` | new. The counts above, with the site list off |
| `tools/browser/url_rules.py` | new. The URL rules, read out of `detect.js` |
| `tools/browser/pages/make_shaped_pages.py` | new. Writes the four pages below, reproducibly |
| `tools/browser/pages/linkedin-shaped.html` | new, a reconstruction |
| `tools/browser/pages/ashby-shaped.html` | new, a reconstruction |
| `tools/browser/pages/northwind-careers.html` | new, a reconstruction |
| `tools/browser/pages/cards-not-linked.html` | new, the failure above |
| `tools/browser/README.md` | the two new scripts, and what a reconstruction is not |

The scorer is about 75 lines of code — the brief said fifty. The extra is the
card rule and the cache, and both earned their place above.

## What was run

```
node --check extension/src/detect.js               passes
tools/browser/url_rules.py       14/14 caught, 0/10 false positives
tools/browser/detection.py       4 of 5, unchanged from 0014
tools/browser/extraction.py      the table above
formwork/fw check                green, 12 checks
```

No model was called. No network request was made. Nothing was installed into
the project: `extraction.py` needs Playwright, and it is run with
`uv run --with playwright==<version>` so `pyproject.toml` is untouched.

## Git status

Nothing staged. `extension/` is untracked, as it was.

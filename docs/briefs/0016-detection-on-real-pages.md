---
status: done
date: 2026-09-16
---

# 0016 — Find the job post on any page

> **You own `extension/` and nothing else.**
>
> **This is urgent. The demo is today.**
>
> **The point of this brief is that it must work on a site nobody has coded
> for.** A list of per-site selectors is not the answer and is explicitly out of
> scope as the mechanism.

## 1. Goal

The extension was used on real job boards for the first time. It detects the
page, then sends **the whole visible page** as the job post.

Measured, in the panel's own pre-screen:

| Page | It reported |
|---|---|
| A real LinkedIn post | **79 things they ask for** |
| A real Ashby post | **44** |
| The real DataRobot post, as a text file | **23** |

Those numbers are navigation, the sidebar, the Premium advert, related jobs and
the footer, all counted as requirements.

**What it costs live:** pressing *Check my fit properly* on that LinkedIn post
is 79 requirements at roughly 3.4 seconds each. **Over four minutes**, mostly on
page furniture. The panel promises about one minute.

## 2. Scope — one general method, no site list

`POST_SELECTORS` in `detect.js` is eleven CSS selectors ending in `article` and
`main`. On both sites it fell through to one of those.

**Replace the mechanism with a general one.** The rule that does the work:

> Navigation, sidebars and related-job lists are mostly **links**.
> A job description is mostly **prose**.

So walk the block elements and score each on two numbers:

- **how much text it holds** — longer is better, up to a point
- **link density** — what fraction of its characters sit inside an `<a>`.
  High means navigation. Low means prose

Take the highest scorer. Strip `nav`, `header`, `footer`, `aside`, `script`,
`style`, `form` and anything with `role="navigation"` before scoring.

This is the core of what Firefox Reader Mode does. **Write it — about fifty
lines, no dependency, nothing fetched.** Do not add a library; decision `0002`
forbids anything off this machine and vendoring a 100KB file for this is not
worth it.

**The known-site selectors may stay as a fast path, and only as that.** The
general scorer has to work with the list switched off, and section 4 is tested
that way.

### Two URL patterns, while you are in there

Detection is a different question from extraction and its shape heuristic is
sound. Two addresses are simply missing from the fast list:

```
linkedin.com/jobs/search-results/?currentJobId=…      missed
ashbyhq.com/careers?ashby_jid=…                       missed
```

One pattern each. **Do not widen them into something that fires on a board's
index page.**

## 3. Must not happen

Standing ones apply.

- Anything outside `extension/`.
- **No per-site rule as the mechanism.** If the general scorer only works
  because a selector caught it first, this brief failed.
- **No model call, no network, no library.** Localhost only.
- **Do not lower the detection bar.** The four-headings-and-1200-characters rule
  caught three hard negatives and stays.
- Do not run a full audit automatically.

## 4. Done when

- **With the known-site list switched off**, a real LinkedIn post and a real
  Ashby post both report a pre-screen count **in the tens, not near a hundred**.
  Both numbers in the report.
- **It works on a third site nobody coded for.** Pick any company careers page
  that is not LinkedIn, Ashby, Greenhouse or Lever, and report the count.
- The four URLs — the two that worked and the two that missed — all detected.
- The eight negatives brief `0008` lists are still quiet. Re-run its checks.

**What would tell us it failed:** the counts are still near a hundred, or it only
works where a selector already matched, or a badge lights up on a careers index.

## 5. Checked by

`formwork check`, and `extension/tools/browser/` which brief `0014` left behind.

**The gate cannot see this.** The evidence is the counts in section 4, measured
with the site list off.

## 6. The report must contain

Short. Five things:

- **the pre-screen count before and after**, for LinkedIn, Ashby, and a third
  site nobody coded for — **with the site list switched off**
- how the scorer decides, in three or four lines a person can follow
- confirmation the eight negatives are still quiet
- **where it still gets it wrong**, if anywhere. A general method that fails
  somewhere is worth more than a claim that it never does
- anything you could not fix without leaving `extension/`

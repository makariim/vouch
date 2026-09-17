---
status: done
date: 2026-09-16
---

# 0021 — The README

> **You own `README.md` at the repository root, and nothing else.**
>
> **Do not change a line of code.** If something is wrong, write it down and
> report it.

## 1. Goal

The repository is public and a DataRobot interviewer will open it before they
meet the author. Today they see a folder list and *"No description, website, or
topics provided."*

**One page. It has to answer four questions**, and stop:

1. What does this do?
2. Why is it built this way and not the obvious way?
3. How do I run it?
4. What is wrong with it?

**If we do not do this:** the best thing about this project — the reasoning
behind it — is buried in `docs/` where nobody will look first.

## 2. Who reads it

**A senior engineer who has ten minutes and has never heard of this.** They are
deciding whether the person who wrote it can think.

They are not a user. They will not install it. They will read the README, open
one or two files, and form an opinion.

## 3. What goes in it

**Read `docs/decisions/` first — all eight.** They are the argument, and this
page is the short version of it.

**The four answers, in this order:**

**What it does.** A job post and a resume in. Every requirement comes back as
*your resume shows this / shows part of this / does not show this*, with the
exact resume line that proves it. **When there is no evidence it says so and
quotes nothing.** That refusal is the product.

**Why it is built this way.** The obvious build is one model call over the post
and the resume together — and then you cannot tell whether the resume said it or
the model wanted it to. So: the resume is indexed by line and searched as a
tool, the model returns a **line number**, and the text on screen is read back
out of the file. **A fabricated quote is impossible, not unlikely.** This is the
most important paragraph on the page.

**How to run it.** The real commands, tested by running them. Python version,
install, a key, start the server, open the page. Then how to load the extension
unpacked, in five steps. Short enough that somebody actually does it.

**What is wrong with it.** Named, not softened. About 60% of verdicts land in
the middle. Extraction is not deterministic — the same post gave 23, then 21,
then 22. The retry used to depend on the model reporting its own weak evidence
and it never once did, so it now triggers on something observable. Cost is
**NOT ESTABLISHED** because nothing records token usage.

**Then two pointers and stop:** `docs/decisions/` for why anything is the way it
is, and `docs/future.md` for the eight things that were designed and not built.

## 4. What must not be in it

- **No badges, no emoji headers, no "✨ Features" list.**
- **No claim the author wrote a library.** `rank_bm25`, `pdfplumber`,
  LangGraph, FastAPI and Groq are libraries. Say so where they appear.
- **No screenshots.** They rot, and this page is about reasoning.
- **No count promised as a property of the product.** Extraction varies.
- **No "production ready".** It is not, and they were told not to expect it.
- **Nothing in it that is not true today.** If a command does not run, it does
  not go in.

## 5. How to write it

- **Short sentences. Plain words.** `docs/style.md` governs, as everywhere else.
- **One page.** If it needs a table of contents, it is too long.
- Every command in it must have been **run**, in this repository, as written.

## 6. Must not happen

Standing ones apply.

- **Do not change code, tests, or any document other than `README.md`.**
- **Do not commit** `private/`, `.env`, `resumes/`, `audits/`, or a resume.
- **Do not invent a number.** Every figure comes from a report in `docs/reports/`
  or from a command you ran, and the report says which.

## 7. Done when

- `README.md` exists and answers the four questions in section 1.
- **Every command in it has been run and works**, in a clean shell.
- A stranger could say what the guarantee is after reading it once.
- It fits on one page.

**What would tell us it failed:** it reads like a product page. This is a
repository an engineer is judging, not a thing being sold.

## 8. Checked by

`formwork check`.

Nothing can check whether a README is good. The evidence is section 9.

## 9. The report must contain

Short.

- **which commands you ran to verify the instructions**, and what they printed
- where each number came from
- anything you found while writing it that is **not true any more** — a stale
  command, a renamed thing, a claim the code no longer supports. That is the
  most useful thing this brief can turn up

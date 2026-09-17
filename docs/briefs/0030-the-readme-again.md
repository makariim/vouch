---
status: done
date: 2026-09-17
---

# 0030 — The README again

> **You own `README.md`, this brief's own report, and this brief's status line.**
> Nothing else.
>
> **Do not change any code.** If something in the README is not true, that is a
> finding — write it down, do not fix the code.
>
> **The reference is `README.md` in the author's `formwork` repository**, and he
> has pasted it into the session that hands you this brief. Copy how it is
> built, not what it says.

## 1. Goal

The README says the right things and is shaped like a document. The author's own
Formwork README is shaped like a front door, and he wants this one to match.

**If we do not do this:** the page an interviewer opens first explains a refusal
for a hundred lines and never shows one.

## 2. The one thing missing, before anything else

**It describes the product and never shows it.**

Formwork's README shows a transcript:

```
you:    commit this for me
agent:  REFUSED by the version-control boundary: git commit changes
        the repository.
```

and then one line under it: *"Nobody read you a rule. You watched it work."*

**Vouch's equivalent is three real rows from a real run**, near the top, before
any explanation:

- one **evidenced**, with the quoted line and its number
- one **partly evidenced**
- one **not evidenced**, with **no quote and no line number at all**

Then one line pointing at the empty space. Something like *that gap is the
product* — in the README's own voice.

**Take the rows from `docs/reports/`**, so they are real and cite where they came
from. Do not invent an example.

## 3. What else to take from the reference

**A hook, and the name.** Formwork opens with a line you remember, then explains
its own name: *"Not a typo. Builders use formwork to hold a shape until it can
stand on its own."*

**Vouch has the same gift and does not use it.** To vouch for someone is to say
you can back the claim up. Say it.

**A summary near the top.** Formwork puts three columns above the fold — *A team
· A way of working · Rules that refuse*. Vouch's three are its own to find.

**Who it is for.** Formwork addresses three kinds of reader in three lines. This
page is read by somebody deciding whether the author can think, so say who it is
for and what they will find.

**Tables instead of paragraphs**, wherever a paragraph is really a list.

**Callouts** — the reference uses Important, Tip and Warning. Use them where
something would cost the reader time.

**What it will not pretend.** The existing "What is wrong with it" is good and
keeps its content. Take the reference's framing: every number comes with the
command that made it, and anything unmeasured says so.

## 4. Four things in it are now false

Check every claim, not only these.

| It says | It is |
|---|---|
| 173 tests | **181.** `uv run pytest` |
| Cost is NOT ESTABLISHED | **Established.** 47 model calls, about 17,000 tokens, under half a cent per audit on Groq's list price. **It is a calculation from token counts, not a metered bill** — nothing records usage. Say both halves. Source: report `0024` |
| `export GROQ_API_KEY=...` | The key now loads from `.env` at the repository root if it is there. A shell variable still wins. Brief `0028` |
| Load the extension in `chrome://extensions` | Managed Chrome blocks unpacked extensions by corporate policy. **Brave** is what this was developed and demonstrated on. Say so plainly, without making it sound like a defect |

**Every number gets the command that produced it**, the way the reference does.

## 5. Must not happen

- **Do not change code, tests, or any file but `README.md`**, this brief's report
  and this brief's status line.
- **Do not invent an example run.** Every row, number and quote comes from
  `docs/reports/` or from a command you ran, and the report says which.
- **Do not claim a library as the author's.** `rank_bm25`, `pdfplumber`,
  LangGraph, FastAPI, uvicorn, Groq.
- **Do not promise a requirement count.** Extraction is a model call.
- **Do not say "production ready".**
- **Do not copy the reference's wording, subject or claims.** Its shape only.
- **Do not add a badge, an emoji header or a screenshot.**

## 6. Done when

- **A reader sees a real verdict, including one with nothing in it, before any
  explanation.**
- The name is explained.
- Every command in it has been run, as written, in this repository.
- The four false things are true, and nothing else is stale.
- Every number carries the command or the report it came from.
- It still fits one page of reading — headings, tables, callouts, no wall.

**What would tell us it failed:** it reads like a product page, or a number in
it cannot be traced to something that produced it.

## 7. Checked by

`formwork check`.

Nothing can check whether a README lands. The evidence is section 8.

## 8. The report must contain

Short.

- **which commands you ran to verify it**, and what they printed
- where each row of the example run came from
- anything else you found that is no longer true. **The most useful thing here**

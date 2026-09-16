---
updated: 2026-09-16
by: report 0005
---

# Standing brief

## What we are building

A local tool for one job seeker. It reads a job post and a resume, checks every
requirement in the post against evidence in the resume, and says exactly which
line supports it or marks it not evidenced. It then drafts tailored resume and
cover letter text using only the evidenced material. Single user, runs on the
user's own machine. No accounts, no hosted data, English only.

**Why it exists:** it is a technical assignment for a DataRobot Professional
Services interview. The deliverable is a working application plus a fifteen
minute presentation with a live demo, and the code goes on GitHub at
`makariim/job-hunter`.

**Fixed by the assignment, not by us:**

- a complete application, **frontend and backend both**. A notebook or a bare
  command line tool does not satisfy this.
- **code-first, on an open-source agent framework** — LangChain, LangGraph,
  CrewAI, Pydantic AI or LlamaIndex.
- scored on problem-solving acumen, strategic vision, technical credibility,
  creativity and passion. **Four of those five are not code.** They said
  explicitly they do not expect production quality.

**What that scoring means in practice:** a demo that breaks live costs far more
than a feature that is missing. Build for the demo path, not for coverage.

**The demo will be run live on the DataRobot job post itself, gaps included.**
So the tool must work from pasted text and must not fetch the post over the
network.

**Time available is evenings only.** Size every brief for that.

## Where we are now

**The product is finished. The presentation is drafted and has never been
rehearsed.** That is the whole position on the day of the working deadline.

**The slides and the demo script are in `docs/presentation/`** — 13 slides and a
click-by-click script with a fallback. Report `0005` has what was cut and the
four questions that have no good answer.

**What works, measured:**

- the LangGraph audit, the page, the extension, the design, all of it
- **the retry fires on its own** — 3 times on the real post, requirements 3, 20
  and 22, nobody pressing anything
- **8 evidenced, 12 partly, 3 not** of 23 requirements on the real DataRobot post
- `undersells` down from 8 items to 4, the false positive gone as predicted
- the extension runs in **Brave** — work Chrome blocks unpacked extensions by
  corporate policy, and always will
- 154 tests, `formwork check` green

**Brief `0016` is confirmed on a real page.** The count on a real LinkedIn post
went **79 → 25**. The general scorer works: strip the furniture, score every
block on length and how little of it is clickable, take the winner. No per-site
rules.

**A demo rule, learned by measuring:** LinkedIn collapses the description behind
`... more`. Collapsed it reads **13**; expanded, **25**. The extension reads what
the page has rendered. **Click "... more" before running an audit on LinkedIn.**
Not fixed — the general fix is to expand before reading, and it is roadmap.

**What is left is all human, and none of it is optional:**

1. **Two full demo runs**, start to finish, on the real post. Once is not a
   rehearsal.
2. **The slides read aloud against a clock.** 940 words are scripted, about
   seven minutes. **The other eight minutes have never been timed.**
3. **The fallback tested** — model slow, switch to the recording tab, keep
   talking.
4. **The two-metre test.** One minute.

Brief `0015` — four small backend gaps — is optional and none of them is on the
demo path.

**Known and accepted, not fixed:**

- a full audit is about **90 seconds**; the panel says "about 1 minute"
- the scorer fails where a related-jobs list links only the title. Found,
  measured, fixed one level up, and three other failure modes are named in
  report `0016`

## What is decided

All four accepted 2026-09-15. The records hold the reasoning.

- `0001` the audit is a LangGraph state graph, not one model call
- `0002` nothing leaves the machine except the model call
- `0003` the audit governs the tailor
- `0004` one endpoint, streamed, fixed before either side is built
- `0005` the contract grows, before four sessions start
- `0006` the contract closes its holes
- `0007` the agent stops grading itself
- `0008` the stored answer carries the whole answer — **`proposed`**

## What is open

- **Is the output showable?** The human's call, and the only one that matters.
  NOT ESTABLISHED.
- **Normalising the resume is the tool's job, not the user's.** Agreed in
  conversation, not yet briefed. It must be **mechanical**, not a model call —
  a model that rewrites the resume destroys the verbatim guarantee, which is
  the whole product.
- **The `evidence_weak` self-report does not work.** Either the prompt earns it
  or the retry triggers on something observable instead.
- **`LineIndex.search` rewards generic lines** when the query is long.
- **Cost is NOT ESTABLISHED.** Nothing records token usage.
- **The two-metre test.** Still not done. The page has never been watched by a
  human, and the real trace has never been seen in it at all.
- **The presentation has never been spoken.** It exists on disk. Nothing about
  the clock, the room or the fallback is established.

## What is next

**Stop building. Rehearse.** The writing is done; brief `0005` stays open until
the demo has been run twice and the talk has been timed.

Brief `0015` is optional — its four gaps are small and none of them is on the
demo path.

## What we tried and stopped

Nothing yet.

**Anthropic as the model provider.** The code was written against it; the only
key available is Groq. `AnthropicModel` stays in the tree behind the `Model`
protocol, so two providers is now a thing to show rather than a thing lost.

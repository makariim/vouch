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
`makariim/vouch`.

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

**The product is finished. Nothing is left to build.**

Backend, page, extension, design, PDF upload, the resume view. 172 tests,
`formwork check` green, everything committed and pushed.

**Reading the PDF in the right order changed the verdict.** `pdfplumber` sorts
text by its position on the page — reading order — where `pypdf` returned it in
the order the file was written. Same resume, same post, same model, both runs
minutes apart:

| | lines | requirements | evidenced | partly | fit |
|---|---|---|---|---|---|
| before | 160 | 22 | 3 | 17 | **weak** |
| after | **51** | 21 | **6** | **13** | **worth applying** |

**Nothing about the model changed. Only how the file was read.** That is the
strongest thing this project has to say.

**A true sidebar resume would still interleave.** Sorting by position fixes a
single-column layout with left titles and right dates, which is what this one
is. NOT ESTABLISHED for a full-height sidebar; there is no such file to test.

**What the last round fixed:** tabs from PDF extraction no longer reach the
screen (1,130 in the file, 0 in the index); a "Nice to Have" heading without a
colon is now found; the page shows a loud amber banner while a recording is on;
and a reload no longer loses the uploaded resume.

**Two things to say carefully, both found by measuring:**

- **Do not promise a nice-to-have count.** The heading fix is real, but on that
  post four items resolved partly because it was pasted hard-wrapped. Unwrapped,
  the same fix gives one. Heading attribution depends on line wrapping.
- **Do not promise a requirement count.** Extraction is a model call: 23, then
  21, then 22 on the same post.

**Four things left, and every one of them is the human's:**

1. **Rehearse the presentation twice, against a clock.** Never done. This is the
   only real risk left in the project.
2. The two-metre test on the page.
3. One reload after an upload, to confirm brief `0019`.
4. Check one quote's line number against the resume view, **on the real PDF** —
   the seam was proven on a simpler file the session built itself.

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

**Rehearse. Nothing else.**

The slides and the demo script are in `docs/presentation/`. The script has the
clicks, the words, the fallback and the questions. It has never been read aloud
against a clock.

The presentation carries four of the five scoring criteria and it is the only
part of the deliverable that has never been tested.

## What we tried and stopped

Nothing yet.

**Anthropic as the model provider.** The code was written against it; the only
key available is Groq. `AnthropicModel` stays in the tree behind the `Model`
protocol, so two providers is now a thing to show rather than a thing lost.

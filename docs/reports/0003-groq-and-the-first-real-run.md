---
status: open
date: 2026-09-15
brief: 0003-groq-and-the-first-real-run
---

# 0003 — Groq, and the first real run

**It ran.** 21 requirements, 58 seconds, clean exit, on the real DataRobot post
and the real resume.

**The verdicts are readable and mostly defensible. Two things are wrong, and
one of them is the feature the whole design argument rests on.**

- **The retry loop never fired. Not once in 21 requirements.**
- **At least one verdict is wrong because retrieval missed the evidence**, not
  because the model misjudged what it saw.

The brief stays `open`. Section 4 says the failure test is a human reading the
output and deciding it is not showable. That call is not mine.

## What changed

- `src/audit/model.py` — `GroqModel` beside `AnthropicModel`, and
  `build_model()`, which reads `AUDIT_PROVIDER` and returns one of the two.
  Groq is the default. The two prompt builders moved to module level
  (`_query_prompt`, `_judge_prompt`) so both providers send the same bytes.
- `src/audit/cli.py`, `src/audit/server.py`, `scripts/record_trace.py` — one
  line each, `AnthropicModel()` to `build_model()`.
- `tests/test_cli.py` — the helper patched `cli.AnthropicModel`, now patches
  `cli.build_model`. The seam moved. No assertion changed.
- `pyproject.toml` — added `langchain-groq>=1.1`.
- `.gitignore` — added `private/` and `.env`, so the real inputs and the key
  cannot be committed. Decision `0002`.
- `fixtures/trace-real.json` — written by the run. Ignored, as the brief says.

## Which library, and why

**`langchain-groq`, not the `groq` SDK.** LangChain core is already in the tree
under LangGraph, so `uv` resolved 35 packages and installed **2**. It also
gives `with_structured_output(schema)`, the same shape `messages.parse` gave
Anthropic — a Pydantic class in, an instance out.

## Which model, and whether the guarantee held

**`openai/gpt-oss-120b`. Verdicts were schema-constrained, not validated after
the fact.**

Groq offers constrained decoding (`method="json_schema"`, `strict=True`) on
exactly two models, and `langchain-groq` **silently drops `strict` on any
other**. So the default is one of the two and `GroqModel.constrained` records
which path is live.

On the wire:

```
response_format type: json_schema | strict: True
verdict enum: ['evidenced', 'partly_evidenced', 'not_evidenced']
```

Across 21 judgements and 43 model calls, **every reply validated**.
`validation_retries` stayed at 0 and the JSON-mode fallback was never entered.
A fourth verdict was never possible.

## The run

```
GROQ_API_KEY=... PYTHONPATH=src .venv/bin/python -m audit.cli \
    private/post.txt private/resume.txt --trace fixtures/trace-real.json
```

**58 seconds. Exit 0.** 43 model calls: 1 extract, 21 search, 21 judge.

**Cost is NOT ESTABLISHED.** Nothing in the pipeline records token usage — the
events carry no usage field and I did not capture the raw responses. Order of
magnitude, from input sizes, is a fraction of a US cent on Groq pricing. That
is an estimate, not a measurement, and the fix is to record usage on the
response rather than to guess better.

## The full output

```
PART   1. Partner with Customers: Collaborate closely with customer stakeholders to understand their business goals, identify high-impact use cases, and define technical requirements for AI solutions.
         Shows delivery of client‑facing AI products, indicating some customer interaction but does not explicitly describe collaboration to define goals or requirements.
         resume line 41: Deliver client-facing AI products against fixed demo dates, including a multi-step document analysis workflow with a human review

PART   2. Build & Deploy AI Solutions: Design, develop, and deploy end-to-end AI solutions using the DataRobot platform and open-source tools. This includes:
         Shows model serving and deployment of AI solutions using open-source tools, but does not mention the DataRobot platform
         resume line 7: answering, text-to-SQL, model serving and evaluation, and the deployment path into cloud, on-premise and fully air-gapped

PART   3. Agentic AI:  Developing and deploying agents on DataRobot leveraging common frameworks such as Langgraph, CrewAI, Llama Index
         Shows work with agentic queries and deployment, but does not mention DataRobot or the specified frameworks.
         resume line 47: ingestion, search, SQL, agentic query, deployment and on-site air-gapped debugging.

PART   4. Generative AI: Building custom GenAI chatbots, Retrieval-Augmented Generation (RAG) systems.
         The line mentions RAG and LLM orchestration with agents, indicating experience with retrieval-augmented generation but does not explicitly state building custom GenAI chatbots.
         resume line 73: AI systems Languages Backend & data Infrastructure Frontend Quality LLM orchestration, DSPy and ReAct agents, RAG and hybrid retrieval, BM25 and dense reranking, LSH,

PART   5. Predictive AI: Developing and deploying classic machine learning models for use cases like forecasting, churn prediction, and fraud detection.
         The line mentions building fraud detection infrastructure, indicating work on a fraud detection use case, but does not specify developing or deploying classic machine learning models.
         resume line 65: Built fraud detection and campaign infrastructure for the Microsoft Rewards loyalty programme, modernised Notifications Platform

NO     6. Serve as a Technical Expert: Act as a subject matter expert on the DataRobot platform and modern AI/ML development, guiding customers on best practices for MLOps, model governance, and scaling AI initiatives.
         No line mentions DataRobot platform or guiding customers on MLOps, model governance, or scaling AI initiatives.

PART   7. Deliver Value: Ensure that the solutions you build are robust, scalable, and directly contribute to the customer's business objectives.
         Shows design of a scalable platform delivering insights that support business goals, but does not explicitly state robustness
         resume line 70: Designed and implemented a data-analysis platform to extract and visualise insights from high-volume datasets, and contributed to

PART   8. Communicate & Collaborate: Clearly communicate complex technical concepts and project outcomes to both technical and non-technical audiences, from data scientists to C-level executives.
         Shows presenting project outcomes to a senior organization, indicating communication to high-level (potentially non‑technical) audience.
         resume line 55: engineering, against a fixed deadline. Presented it to the Microsoft AI organisation; it secured immediate investment in Shopping

PART   9. Strong proficiency in Python and common data science libraries (e.g., pandas, scikit-learn, NumPy, etc.).
         The line shows Python proficiency but does not mention the required data science libraries.
         resume line 78: Python, REST API design

PART  10. Practical experience with Generative AI technologies, including Large Language Models (LLMs), vector databases,
         Shows experience with LLM orchestration and related retrieval techniques, indicating practical work with generative AI LLMs but does not mention vector databases.
         resume line 73: AI systems Languages Backend & data Infrastructure Frontend Quality LLM orchestration, DSPy and ReAct agents, RAG and hybrid retrieval, BM25 and dense reranking, LSH,

PART  11. Solid understanding of the end-to-end agentic AI lifecycle from building agents in  frameworks like LangGraph or CrewAI, to at scale deployment and monitoring.
         Shows experience with agent frameworks and LLM orchestration, indicating partial alignment with building agents and deployment, but does not mention LangGraph/CrewAI or full lifecycle monitoring.
         resume line 73: AI systems Languages Backend & data Infrastructure Frontend Quality LLM orchestration, DSPy and ReAct agents, RAG and hybrid retrieval, BM25 and dense reranking, LSH,

PART  12. Demonstrable experience developing and deploying applications, including building REST APIs (e.g., using Flask, FastAPI) to serve ML models and GenAI logic.
         Shows REST API design experience but does not specify Flask/FastAPI or serving ML models.
         resume line 78: Python, REST API design

PART  13. Proficiency with containerization using Docker and experience deploying and managing applications on container orchestration platforms like Kubernetes (K8s).
         The line mentions Docker and Kubernetes, indicating skill, but does not describe actual deployment or management experience.
         resume line 79: Docker, Kubernetes, Helm, GitHub Actions, AWS ECR and CodeArtifact, GCP Secret Manager, on-prem and air-

PART  14. Solid understanding of secure application development practices, including authentication/authorization (e.g., OAuth, API keys), secrets management, and securing public-facing endpoints.
         Shows experience with secrets management (GCP Secret Manager), a key part of secure application development.
         resume line 79: Docker, Kubernetes, Helm, GitHub Actions, AWS ECR and CodeArtifact, GCP Secret Manager, on-prem and air-

PART  15. Experience in a client-facing or consulting role with exceptional verbal and written communication skills. You must be comfortable leading technical discussions and presenting to diverse audiences.
         Shows presenting to a technical audience, indicating comfort leading technical discussions, but does not explicitly mention communication skills or client‑facing consulting role.
         resume line 55: engineering, against a fixed deadline. Presented it to the Microsoft AI organisation; it secured immediate investment in Shopping

PART  16. A deep curiosity and a passion for solving complex, unstructured problems.
         Shows independent research and building a demo on a customer's own problem, indicating a drive to tackle complex, unstructured issues
         resume line 8: environments. Forward deployed into new accounts, where a demo built from independent research on the customer's own problem

YES   17. Approximately 6-8 years of hands-on experience in AI Application development, software engineering, machine learning engineering, or a similar role with a proven track record of deploying AI solutions or applications into production.
         The line states six years of hands‑on AI engineering building and operating production systems, matching the required 6‑8 years and deployment experience.
         resume line 5: AI engineer with six years building and operating production systems at scale. Core engineer on an enterprise knowledge intelligence

NO    18. A Master’s Degree or Ph.D. in Computer Science, Statistics, Artificial Intelligence, Engineering, or a related quantitative field.
         The resume only lists a B.Sc. degree and does not mention a Master's or Ph.D. in the required fields.

YES   19. Hands-on experience with a major cloud platform (AWS, Azure, or GCP).
         The line lists AWS and GCP services, showing hands‑on experience with major cloud platforms.
         resume line 79: Docker, Kubernetes, Helm, GitHub Actions, AWS ECR and CodeArtifact, GCP Secret Manager, on-prem and air-

NO    20. Familiarity with the DataRobot AI Platform is a strong plus.
         The resume does not mention DataRobot AI Platform.

PART  21. Understanding of MLOps principles and tools for model CI/CD, monitoring, and governance.
         Lists CI/CD and deployment tools used, indicating MLOps knowledge, but does not mention monitoring or governance.
         resume line 79: Docker, Kubernetes, Helm, GitHub Actions, AWS ECR and CodeArtifact, GCP Secret Manager, on-prem and air-

evidenced 2   partly 16   not evidenced 3
```

**evidenced 2 · partly_evidenced 16 · not_evidenced 3**

## The requirement list, judged on its own

Extraction is the strongest part of the run. 21 requirements, **none invented**
— `post_index.locate()` dropped nothing, so every one was found verbatim in the
post.

Two blemishes, both inherited from the post rather than introduced:

- Requirements 2 and 3 carry their heading prefix (`Build & Deploy AI
  Solutions:`, `Agentic AI:`) and 2 ends on the fragment `This includes:`.
  Faithful to the source, awkward to read back.
- Requirement 10 stops mid-sentence at `vector databases,` — **because line 37
  of the post does**. The post itself is truncated there. Correct behaviour.

Responsibilities and qualifications were both picked up, and the company blurb
and benefits were correctly skipped.

## Where the judging was shaky

**16 of 21 came back `partly_evidenced` — 76%.** The middle verdict is
absorbing both ends. Named one by one, the close calls:

- **5, fraud detection.** Cited line 65, which says "Built fraud detection and
  campaign infrastructure". The verdict reads "does not specify developing or
  deploying classic machine learning models". Defensible, but this is the
  closest `partly` / `evidenced` call in the run.
- **14, secure application development.** `partly` on the strength of `GCP
  Secret Manager` appearing in a tools list. Nothing about auth, OAuth or
  securing endpoints — and the resume contains no `OAuth` at all. This is the
  closest `partly` / `not_evidenced` call, and it leans generous.
- **9, Python and data science libraries.** `pandas`, `scikit-learn` and
  `NumPy` are **absent from the resume**. The verdict is `partly` on Python
  alone.
- **1, 7, 8, 15, 16** — all judged from a single prose line about a different
  achievement. Not wrong, but thin.

The pattern: the judge is honest about what it was shown, and what it was shown
is often one line that is adjacent to the requirement rather than on it. That
produces `partly` almost every time.

## The one wrong verdict

**Requirement 12 asks for FastAPI. The resume has FastAPI, on line 77. The
verdict says it does not.**

```
PART  12. ... building REST APIs (e.g., using Flask, FastAPI) ...
          Shows REST API design experience but does not specify Flask/FastAPI
          resume line 78: Python, REST API design
```

The judge was not lying. **Line 77 was never retrieved**, so it never saw it.
Replaying the search offline, the top 6 for requirement 12 are lines 78, 79, 7,
75, 80, 76. Line 77 is not among them.

Why: the model returned a 22-token grab-bag query. `LineIndex.search` scores
`len(hits) / len(query tokens)`, so line 78 (`Python, REST API design`) matches
three generic terms and line 77 matches one specific term — `fastapi` — and
loses.

The proof it is a scoring artefact and not an indexing one: **requirement 10
retrieved line 77 without trouble**, on a query that had nothing to do with web
frameworks.

Contrast requirement 13, whose query was only 8 tokens: it returned line 79
cleanly and judged well. **Short specific queries work. Long grab-bag queries
bury the decisive term.**

Not fixed here. Section 3 forbids tuning the prompts to improve the first run,
and rightly — this is the evidence.

## Whether the retry fired

**No. Zero retries across 21 requirements.** Decision `0001` rests on this loop
being visible, and on the first real run it is invisible.

The trace is 86 events: 21 `search`, 21 `judge`, 21 `verify`, 21 `verdict`,
plus `requirements` and `done`. **No `retry`, no `failed`, no `dropped`.**

Both triggers stayed silent, for different reasons:

- **`verify` never rejected a quote.** 18 quotes, all confirmed against the
  resume by line number; 3 verdicts carried no quote. The model never cited a
  line that was not there. That is the guarantee working — and it means the
  first trigger correctly had nothing to fire on.
- **The model never set `evidence_weak`.** Not once, despite writing "does not
  mention" or "does not specify" in 16 of 21 reasons.

That second point is the finding. Requirement 12 is **exactly** the case the
retry exists for — right evidence in the resume, wrong lines retrieved — and
the model reported `partly_evidenced` with complete confidence instead of
flagging thin evidence. The loop is sound; nothing asked it to run.

## Half the quotes come from four lines

```
line 79 x4   line 73 x3   line 78 x2   line 55 x2   (nine of eighteen)
```

Lines 73 and 79 are damaged by PDF extraction. Line 73 is a flattened
multi-column table header:

```
AI systems Languages Backend & data Infrastructure Frontend Quality LLM
orchestration, DSPy and ReAct agents, RAG and hybrid retrieval, ...
```

Line 79 ends mid-word on `on-prem and air-`, with `gapped deployment` orphaned
on line 80.

The audit is correct to quote them — that is what the file says. But a quote
that reads as a fragment undercuts the one thing this tool is for, and in a
demo it is the first thing an interviewer will notice. **This is a property of
the input file, not of the code.**

## What was run

- `uv pip install langchain-groq>=1.1` into `.venv`. Installed `groq==0.37.1`
  and `langchain-groq==1.1.3`.
- `pytest tests/ -q` — **38 passed**, no key, no network.
- The real audit, once. Wrote `audit.json` and `fixtures/trace-real.json`, both
  ignored.
- Offline replays of `LineIndex.search`, which make no model call.
- `formwork check`.

## The check

`formwork check` — **green**. 12 checks.

Green means the documents hang together. **It cannot tell whether a verdict is
right**, and neither can the 38 tests — they drive the graph with a stand-in
that has never seen a model. Requirement 12 is wrong and everything stayed
green.

## Git status

Nothing staged, nothing committed.

```
 M .claude/agents/director.md
 M docs/briefs/0001-evidence-audit-core.md
 M docs/standing.md
 M docs/style.md
 M formwork/limits.md
 M formwork/roles/method/director.md
?? .gitignore
?? docs/briefs/0002-audit-frontend.md
?? docs/briefs/0003-groq-and-the-first-real-run.md
?? docs/decisions/0001-audit-is-a-state-graph.md
?? docs/decisions/0002-nothing-leaves-the-machine.md
?? docs/decisions/0003-the-audit-governs-the-tailor.md
?? docs/decisions/0004-the-api-contract.md
?? docs/reports/0001-evidence-audit-core.md
?? docs/reports/0002-audit-frontend.md
?? docs/reports/0003-groq-and-the-first-real-run.md
?? fixtures/
?? pyproject.toml
?? scripts/
?? src/
?? tests/
?? web/
```

The resume, the post and the key are in `private/` and `.env`, both ignored.
`audit.json` and `fixtures/trace-real.json` were already ignored. Nothing
personal can reach the public repository. Decision `0002` holds.

## The three that matter

**Done but not asked for.**

Three call sites plus the test helper, one line each — `AUDIT_PROVIDER` would
otherwise have been read by nothing. The `.gitignore` entries for `private/`
and `.env`, added before the files arrived. Lifting the prompt builders to
module level.

**Asked for but not done.**

Cost. Nothing records token usage, so the figure is an estimate and is marked
NOT ESTABLISHED rather than invented.

**Wrong in the brief.**

The command in section 2 does not run as written — the package is not installed
in the venv, and only `pytest` reaches it via `pythonpath = ["src"]`. It needs
`PYTHONPATH=src`, which is what was used.

## What this leaves open

- **The `evidence_weak` signal does not work.** The retry loop is the design
  argument and it did not execute. Either the judge prompt has to earn the flag
  or the trigger has to stop depending on the model's self-report.
- **`LineIndex.search` rewards generic lines** when the query is long. One
  wrong verdict is traceable to it.
- **76% `partly_evidenced`** is not a useful distribution to show.
- **The resume's line breaks** make half the quotes read as fragments.
- **No bar exists.** Section 4 said this run is what a bar would be set from.
  It now can be.

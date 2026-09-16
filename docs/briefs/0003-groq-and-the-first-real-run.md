---
status: done
date: 2026-09-15
---

# 0003 — Groq, and the first real run

## 1. Goal

`src/audit/model.py` talks to Anthropic. The only key available is **Groq**.

Add a Groq implementation of the existing `Model` protocol, then **run the real
audit for the first time** on the DataRobot job post and the real resume.

**This is the last thing standing between a built application and a demo.**
Everything works and nothing has ever been judged by a model. Until this runs,
nobody knows whether the product is any good.

## 2. Scope

**`src/audit/model.py`** — add a `GroqModel` beside `AnthropicModel`. Same three
methods, same Pydantic schemas, same prompts. Choose the provider from an
environment variable, default Groq.

**Keep `AnthropicModel`.** Do not delete it. Two providers behind one protocol is
a better answer in an interview than one, and it costs nothing to leave.

**`pyproject.toml`** — the dependency. `langchain-groq` is preferred, because
LangChain is already underneath LangGraph and one ecosystem is one story. The
`groq` SDK is acceptable if it is simpler. **Say in the report which, and why.**

**The three-verdict guarantee must survive.** Today `Judgement.verdict` is a
`Literal`, so the API is constrained by the JSON schema and a fourth verdict
cannot come back. Keep that if the chosen Groq model supports JSON-schema
structured output.

If it does not:

- fall back to JSON mode plus Pydantic validation, and **retry once** on a reply
  that does not validate
- **say plainly in the report that the guarantee moved from constrained to
  validated.** That is a real weakening and it belongs in the presentation, not
  hidden in a commit.

**Then run it:**

```
.venv/bin/python -m audit.cli <post.txt> <resume.txt> --trace fixtures/trace-real.json
```

The human supplies the two text files. If they are not in the repository when
this session starts, **stop and say so** rather than inventing inputs.

**Out of scope — do not touch:**

- `src/audit/graph.py`, `events.py`, `index.py` — the graph and the wire shapes
- anything in `web/`, and `fixtures/trace-sample.json`
- decision `0004`, the contract
- Langfuse, the tailor, the extension
- prompt rewriting to chase a better result. If the prompts are wrong, report it

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything — stop
and report, no changing a check because it failed, and where something cannot be
established, say so rather than estimating.

Specific to this work:

- **Do not weaken the verbatim guarantees.** Quotes are still read back out of
  the resume by line number. Nothing the model types is published.
- **Do not let a fourth verdict become possible** without saying so in the report
  in those words.
- **Do not commit the resume or the job post**, and do not remove their
  `.gitignore` entries. The repository is public. Decision `0002`.
- **Do not tune the prompts to make the first run look better.** The first
  honest run is the evidence. A flattering one is worth nothing.

## 4. Done when

- `GroqModel` implements all three protocol methods.
- **The 38 existing tests still pass**, with no key and no network, on the
  scripted stand-in.
- One real run has produced an audit and `fixtures/trace-real.json`.
- The report names the model used and says whether verdicts were
  **schema-constrained or validated after the fact**.

**What would tell us it failed:** the verdicts are wrong often enough that you
would not show them to an interviewer, or extraction produces requirements that
are not really in the post.

**How wrong is too wrong is NOT ESTABLISHED.** No bar exists. This run is what a
bar would be set from.

## 5. Checked by

`formwork check` as a whole, plus `pytest tests/ -q`.

**Neither can tell whether a verdict is right.** The real evidence is a human
reading the output, which is why section 6 asks for all of it.

## 6. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- **the full output of the real run**, every requirement and verdict, not a
  summary
- **the trace**, so the steps can be judged as a demo
- **the requirement list extraction produced**, judged apart from the judging
- **where the judging was shaky** — requirements where the call between
  `partly_evidenced` and a neighbour was close, named one by one
- **whether the retry fired on real input**, and what the agent searched for the
  second time. Decision `0001` rests on this being visible
- which model, which library, and whether structured output held
- roughly what the run cost and how long it took

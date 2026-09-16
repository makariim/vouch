---
status: accepted
date: 2026-09-14
deciders: [makariim]
consulted: [director]
informed: []
---

# 0001. The audit is a LangGraph state graph, not one model call

## What made this a decision

The assignment requires a code-first application on an open-source agent
framework, and names five: LangChain, LangGraph, CrewAI, Pydantic AI,
LlamaIndex.

Brief 0001 as first written was two strings in, one model call, JSON out. That
is extraction, not an agent, and an interviewer will say so in the first two
minutes.

## What matters here

- It has to be an agent: several steps, real tool use, and at least one decision
  the system makes without being told.
- Two project rules are hard rules and should be structural, not polite requests
  inside a prompt: every quote must be real, and the tailor may use only
  evidenced material.
- The demo is fifteen minutes and lives or dies on being watchable.
- Two days of build time.

## Options we looked at

- **DSPy ReAct** — one loop, the model owns the path. Also not on the allowed
  list, which settles it on its own.
- **LangGraph** — typed state, nodes, conditional edges, streaming, checkpoints.
- **Pydantic AI** — typed agents, lighter, less graph and trace out of the box.
- **CrewAI** — roles and tasks, highest level, hides the control flow.
- **Do nothing** — keep the single call, and fail the agent requirement.

## What we chose, and why

**LangGraph**, with the audit as a state graph:

```
extract → search → judge → verify → (retry, or next requirement) → report
```

Four things follow from that shape, and they are the reasons:

- **The resume is a tool, not an argument.** It is indexed by line. The agent
  searches it per requirement and gets back real lines with line numbers. The
  model cannot quote a line it never retrieved, so the verbatim rule stops being
  a test run afterwards and becomes a property of the design.
- **The agent decides how hard to look.** Weak evidence means re-query with
  different words, and it chooses when to stop. That is the decision nobody told
  it to make, and it is visible.
- **Verify always runs.** A quote not present in the resume sends that
  requirement back round. Not optional, not the model's call.
- **The loop counts requirements, not model turns.** Twelve requirements means
  twelve passes. It cannot quietly stop at requirement eight, which is the
  failure mode of a ReAct loop with an iteration cap.

Chosen over **Pydantic AI** because the demo needs a visible trace and LangGraph
streams node-by-node state updates without being asked. Over **CrewAI** because
"what decision does your agent make, and where?" has to be answerable by
pointing at a node and an edge.

One more reason, and it is honest rather than technical: the human has spent a
year on DSPy and Hatchet and has not used LangGraph. Learning it is a stated
goal of this project.

## What follows

**Good:**

- The strongest correctness guarantee comes from the architecture, not a prompt.
- The trace the frontend shows is a by-product of the design, not extra work.
- Checkpointing means a failed step in a live demo can resume, not restart.
- It answers the agent question in the interviewer's own vocabulary.

**Bad:**

- Four times the code of the single-call version, on a two day budget.
- LangGraph is the steepest of the five to learn, and it is new to us.
- More moving parts is more that can break live.
- Some of the graph is ceremony a single call would not need.

## What would make us revisit this

Two days in, if the graph is not running end to end, the fallback is Pydantic AI
with a hand-written loop. Less trace, far less to learn, same verdicts. Decide
that by the end of day one, not on the morning of the demo.

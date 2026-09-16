---
status: open
date: 2026-09-15
---

# 0010 — Learn the system, one unit at a time

> **Run this in a fresh session, on its own.** It is not part of wave 1 and it
> touches no files those sessions own.
>
> **This brief builds nothing.** The thing being produced is a person who can
> explain this system under questioning.

## 1. Goal

Muhammad had this built by agents while short of time. It works. He cannot yet
explain all of it, and in a few days he has to defend it to an interview panel
who will ask why it is shaped this way.

**The deliverable is his understanding, not a document.**

**If we do not do this:** he presents work he cannot answer questions about,
which is worse than presenting something smaller that he can.

## 2. Who you are teaching

A software engineer who moved into AI a year ago. Daily stack is **DSPy and
Hatchet**.

- **Lean on that.** Signatures, modules, durable steps, workers, DAGs — that
  vocabulary lands. LangGraph state is close to a Hatchet workflow context.
- **Do not explain** what an agent is, what a tool call is, what an API is, or
  how Python works.
- **Do explain** what is *different* about a thing, not what it is.
- One known blind spot: `dspy.ReAct` is an agent, so "you need an agent
  framework" reads as "I already have one". The real distinction is **who owns
  the control flow**, not whether it qualifies as an agent.

Write short. Blank line between blocks. Headings and bullets, not stacked bold
paragraphs. `docs/style.md` is his, and it wins.

## 3. How to run it

**One unit at a time. Stop after each one.**

For each unit:

1. Say what it does, in **three or four lines**. Not a tour of the file.
2. Show **the few lines that matter**, not the whole file.
3. Say **why it is shaped that way** — the decision behind it. This is the part
   an interviewer asks about.
4. **Ask him one question** an interviewer would ask, and wait for his answer.
5. If the answer is thin, explain the gap and move on. Do not re-teach twice.

**Do not dump a file and narrate it.** He has read the reports already. What is
missing is the reasoning, not the contents.

**Units are in dependency order. They are also resumable** — if he stops at 4,
a later session starts at 5.

### The units

| # | Unit | The thing he must be able to say |
|---|---|---|
| 1 | `src/audit/index.py` | the resume is a **tool**, not a prompt argument, and the verbatim guarantee lives here |
| 2 | `src/audit/model.py` | three calls, Pydantic schemas, and why `Literal` makes a fourth verdict **impossible** rather than unlikely |
| 3 | `src/audit/events.py` | one place constructs the wire shapes, and why that mattered with parallel sessions |
| 4 | `graph.py` — state and reducers | nodes return **partial updates**; `operator.add` on `events` is the entire trace mechanism |
| 5 | `graph.py` — nodes and edges | the six nodes, and **which three never call the model** |
| 6 | `graph.py` — `verify` and the retry edge | the model returns a **line number**, never text; a conditional edge is why "where does it decide" has a pointable answer |
| 7 | `src/audit/server.py` | one request, many replies; why `EventSource` could not be used |
| 8 | `web/app.js` | reading a stream with `fetch`, splitting frames by hand |
| 9 | The five decision records | the arguments, not the outcomes |
| 10 | What is wrong with it | the retry never firing, 60% `partly`, non-determinism, BM25 being a library |

**Unit 10 is not optional and not last because it matters least.** It is the
material that scores highest, and he must be able to say it without flinching.

## 4. Must not happen

- **Do not write or edit any code.** Four sessions own `src/`, `web/`,
  `extension/` and `design/` right now. Touching any of them causes a collision.
- **Do not edit `docs/standing.md`.** That belongs to the director.
- **Do not lecture.** If a unit runs past a few minutes without a question,
  it has become a lecture.
- **Do not tell him it is all fine.** Unit 10 exists for the opposite reason.
- **Do not skip a unit because it seems obvious.** Units 4 and 6 look obvious and
  are where the interview questions land.

## 5. Done when

- All ten units covered, or he stops and the session says where it stopped.
- **He has answered a question on each unit in his own words.**
- **He can answer three questions cold**, without looking:
  - why is a fabricated quote impossible, rather than unlikely?
  - where exactly does your agent make a decision nobody told it to make?
  - what is wrong with this system today?

**What would tell us it failed:** he can repeat the words and cannot answer a
question phrased differently from how it was taught.

## 6. Checked by

`formwork check`, only to prove nothing was touched.

**Nothing can check understanding.** The evidence is in section 7.

## 7. The report must contain

Short. Three things:

- **which units were covered**, and where it stopped
- **what he could not explain back** — named, unit by unit. **This is the most
  valuable thing in the report.** Those are exactly the questions that will sink
  him in the room, and they are what to prepare
- anything in the code that could not be justified while explaining it. If a
  piece cannot be defended out loud, that is a finding about the code, not about
  him

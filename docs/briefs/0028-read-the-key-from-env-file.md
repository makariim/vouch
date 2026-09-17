---
status: done
date: 2026-09-17
---

# 0028 — Read the key from `.env`

> **You own `src/`, `tests/`, this brief's own report, and this brief's status
> line.** Nothing else.
>
> **This is small on purpose.** If it grows past one function and its tests,
> stop and say so.

## 1. Goal

`.env` holds `GROQ_API_KEY`. **Nothing in the code reads it.** The key only
exists if somebody exported it into the shell first.

It already failed once today, at a keyboard:

```
groq.GroqError: The api_key client option must be set either by passing
api_key to the client or by setting the GROQ_API_KEY environment variable
```

That is a Python traceback, thirty seconds into an audit. On a shared screen it
is the demo over.

**Pre-flight item 1 of the demo script is "`GROQ_API_KEY` is exported in the
shell you are about to use."** A checklist item is a weak defence for something
that costs the room, and it is the same argument that put a loud banner on the
page instead of trusting a radio button.

**If we do not do this:** the most likely way the demo dies stays one thing he
has to remember under pressure.

## 2. Scope

**Load `.env` from the repository root at startup, if it is there.**

- **Standard library only.** No new dependency for ten lines.
- `KEY=value` per line. **Strip surrounding quotes** — this `.env` has
  `GROQ_API_KEY="gsk_..."` and the quotes must not reach the client.
- Ignore blank lines and `#` comments.
- **A real environment variable always wins.** If `GROQ_API_KEY` is already set
  in the shell, `.env` does not override it. That keeps the current behaviour
  working and makes the file a fallback, not an authority.
- **Missing file is not an error.** No file, no change, no message.
- **A malformed line is skipped, not fatal.** Never crash on startup because a
  line had no `=`.

**Where it goes.** Early enough that `build_model()` sees it, and in one place.
`src/audit/model.py` reads the environment at module level, so this must run
before that module is imported, or be read inside the function. **Pick one, and
say which and why.**

**Say it out loud once, at startup.** A single line naming which keys came from
`.env` — the names, **never the values**. Silent magic is worse than no magic;
a person should be able to see where the key came from.

**Out of scope:**

- any new dependency, `python-dotenv` included
- `.env` files anywhere but the repository root
- anything in `web/`, `extension/`, `design/`, `docs/presentation/`
- changing what any key is called

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything, no
changing a check because it failed, NOT ESTABLISHED rather than an estimate.

- **Never print a key value.** Not in a log, not in an error, not truncated.
- **Do not commit `.env`**, and do not remove it from `.gitignore`.
- **Do not let `.env` override a real environment variable.**
- **Do not read a `.env` from anywhere but this repository.** Not the home
  directory, not a parent folder.
- **Do not fetch anything.** Decision `0002` is untouched by reading a local
  file, and it stays that way.

## 4. Done when

- With `GROQ_API_KEY` **not** exported and `.env` present, the server starts and
  a real audit runs.
- With the variable exported to something different, **the shell value wins**.
  Test it.
- With no `.env` at all, nothing changes and nothing complains.
- A line with no `=`, a blank line and a `#` comment are all survived.
- **A key value appears nowhere in any output.** Assert it.
- **The 173 existing tests still pass.**

**What would tell us it failed:** a key reaching a log, or `.env` silently
overriding something a person set on purpose.

## 5. Checked by

`formwork check` and `pytest tests/ -q`.

## 6. The report must contain

Short.

- where the load happens, and why there
- the startup line it prints, quoted
- confirmation a shell variable still wins, tested
- anything about `.env` parsing you had to decide

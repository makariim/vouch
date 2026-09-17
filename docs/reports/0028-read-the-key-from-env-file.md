---
status: open
date: 2026-09-17
brief: 0028-read-the-key-from-env-file
---

# 0028 — Read the key from `.env`

**`.env` is read at package import. The traceback in the brief no longer
happens with the key unexported. A shell value still wins, tested in a real
interpreter. 181 tests pass — the 173 that existed, plus 8.**

One function and its tests, as the brief asked. `src/audit/env.py`, 40 lines of
standard library, and one line wiring it into `src/audit/__init__.py`.

## Where the load happens, and why there

`src/audit/__init__.py`, **above the first `from .`**.

The brief offered two options — before `model.py` is imported, or inside
`build_model()` — and asked for one, with the reason.

The package `__init__` is the option that is *reliably* first. Importing
`audit.anything` runs `audit/__init__.py` before the submodule body, and that
is a language guarantee rather than a convention somebody has to maintain. So
the CLI, the server, `scripts/record_trace.py` and the test suite all get it
without any of them knowing it exists. There is no entry point to forget.

Inside `build_model()` would have been late. `model.py` reads the environment
at **module level** — `AUDIT_PROVIDER`, `AUDIT_MODEL`, `AUDIT_GROQ_MODEL` on
lines 28–30 — so by the time a function in it runs, those three have already
been decided against an environment that did not have the file's values in it.
Only the key itself would have been fixed, and `AUDIT_PROVIDER=anthropic` in a
`.env` would have been read and silently ignored. One place that fixes all
four beats one place that fixes one of them.

The cost is real and worth naming: **importing `audit` now has a side effect**
on `os.environ` and writes a line to stderr. That is unusual for a library. It
is right here because this is an application that happens to be laid out as a
package, and the alternative is the failure the brief is about.

The root is `Path(__file__).resolve().parents[2]` — derived from where the
package sits, not searched for. Nothing walks up looking for a `.env`, so there
is no path by which a home directory's file or a parent project's file can be
read. That was a *must not happen*, and making the root a constant rather than
a search is what makes it structurally true rather than a rule to keep.

## The line it prints

With the key unexported, on stderr, once:

```
audit: read .env -- set GROQ_API_KEY
```

With a key already in the shell, the file's copy is not used, and it says so:

```
audit: read .env -- the shell already had GROQ_API_KEY
```

Both halves in one line when both apply:

```
audit: read .env -- set AUDIT_PROVIDER; the shell already had GROQ_API_KEY
```

**Names only.** No value, whole or truncated, in either branch. `tests/test_env.py`
asserts the absence of the fake key *and* of its first eight characters, and the
real-interpreter test reads the actual key out of the actual `.env` purely so it
can assert that exact string appears in neither stdout nor stderr.

The second clause was a judgement, and it goes slightly past the brief's "name
which keys came from `.env`". The brief asked for one line naming what the file
supplied; this also names what it *did not* supply because the shell got there
first. The reason: the confusing failure at a keyboard is not a missing key, it
is a stale one already exported, quietly beating the good one on disk. A person
staring at an auth error needs to be told that. It stays one line.

## The shell still wins — tested

Two tests, and the one that matters runs a fresh interpreter:

```
GROQ_API_KEY=set-by-a-person-on-purpose python -c "import audit, os; print(os.environ['GROQ_API_KEY'])"
-> set-by-a-person-on-purpose
```

with `the shell already had GROQ_API_KEY` on stderr. The `.env` in this
repository holds a different value and did not win.

## What was checked

| Done-when | Result |
|---|---|
| Key unexported, `.env` present → the key reaches the client | `build_model()` returns `GroqModel`, `openai/gpt-oss-120b`, `constrained=True`, no `GroqError` |
| Key unexported → the server starts | `GET /` 200 (10,292 bytes), `GET /resumes` 200 |
| Exported to something different → shell wins | tested, above |
| No `.env` at all → nothing changes, nothing complains | tested: returns `[]`, prints nothing |
| No `=`, blank line, `#` comment survived | tested |
| No key value in any output | asserted, against both a fake key and the real one |
| The 173 existing tests still pass | **181 passed** (173 + 8) |

**NOT ESTABLISHED: a live audit end to end.** The traceback in the brief came
from client construction, and that path is now clear with the key unexported —
but "a real audit runs" means a paid call to Groq over the network, and I did
not spend one unasked. The three model calls are unchanged by this brief; what
changed is only whether the key reaches them. Run one before the demo if you
want the whole chain witnessed.

## What `.env` parsing forced a decision on

**Quotes.** Stripped only when the first and last character match and are `"`
or `'`. A value with a quote on one side only keeps it — that is likelier to be
part of the secret than a typo we should silently repair.

**`export KEY=value`.** Accepted. A `.env` that is also `source`-able is a
normal thing to have, and refusing the prefix would set a variable literally
named `export GROQ_API_KEY`, which fails as a missing key with no clue why.

**Whitespace.** Stripped from both name and value. A value that genuinely needs
leading spaces can quote them; an API key that arrived with a trailing space is
the far more common case, and it produces an auth error that reads like a bad
key.

**No interpolation, no multi-line values, no `\n` escapes.** `python-dotenv` has
all three. This is ten lines for a key, and each of those is a parser feature
with its own edge cases. If a value ever needs one, that is a new brief.

**Malformed lines.** Skipped silently, including `=novalue` with an empty name.
Startup is not the place to die over a stray line, and it is not the place for
a warning about a line nobody will look at either.

## What I did not touch

No dependency added. `.gitignore` unchanged and `.env` uncommitted. Nothing in
`web/`, `extension/`, `design/` or `docs/presentation/`. No key renamed. No
check changed. Nothing fetched — decision `0002` is untouched: reading a local
file is not an outbound call, and the count of those is still one.

`formwork/fw check` is green, 12 checks.

"""Read `.env` from the repository root, once, at import.

Why this exists: `.env` held `GROQ_API_KEY` and nothing read it. The key only
reached the client if somebody had exported it into the shell first, which made
the most likely way a demo dies a thing a person had to remember under
pressure.

Why no dependency: this is a `KEY=value` file with quotes to strip. That is ten
lines of standard library, and `python-dotenv` is a package in the tree
forever in exchange.

Three rules that are not arbitrary:

- **A real environment variable wins.** `.env` is a fallback, never an
  authority. Something a person set on purpose -- a different key, a different
  provider -- must survive a file sitting on disk. That also means the previous
  behaviour is untouched: if you export the key, nothing here does anything.
- **A missing file is not an error.** No file, no change, no message.
- **A malformed line is skipped.** Startup is not the place to die over a line
  with no `=` in it.

And one rule about output: the names of the keys are printed, the values never
are. Silent magic is worse than no magic, and a key in a log is worse than
both.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# The repository root, derived from where this file sits -- `src/audit/env.py`,
# so two levels up. Derived, not searched: walking up until a `.env` turns up
# would eventually read one out of a home directory or somebody else's project,
# which is the failure this file must not have.
ROOT = Path(__file__).resolve().parents[2]


def parse(text: str) -> dict[str, str]:
    """`KEY=value` per line, into a dict. Nothing that is not that is fatal."""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        # `export FOO=bar` is what you get when a file is written to be sourced
        # by a shell as well as read by this. Cheap to allow.
        name = name.strip()
        if name.startswith("export "):
            name = name[len("export ") :].strip()
        if not name:
            continue
        value = value.strip()
        # Quotes belong to the file format, not to the value. This `.env` has
        # GROQ_API_KEY="gsk_...", and a client handed a key with quotes around
        # it fails in a way that looks like a bad key.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[name] = value
    return values


def load(root: Path | None = None, stream=None) -> list[str]:
    """Put anything in `.env` that is not already set into `os.environ`.

    Returns the names it set, in file order. Names only ever leave this
    function; values never do.
    """
    path = (root or ROOT) / ".env"
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError, PermissionError):
        return []

    parsed = parse(text)
    set_here = [name for name in parsed if name not in os.environ]
    kept = [name for name in parsed if name in os.environ]
    for name in set_here:
        os.environ[name] = parsed[name]

    if set_here or kept:
        parts = []
        if set_here:
            parts.append("set " + ", ".join(set_here))
        if kept:
            # Worth a word. The confusing failure is not a missing key, it is a
            # stale one already in the shell quietly winning over the file.
            parts.append("the shell already had " + ", ".join(kept))
        print(
            f"audit: read .env -- {'; '.join(parts)}",
            file=stream or sys.stderr,
        )
    return set_here

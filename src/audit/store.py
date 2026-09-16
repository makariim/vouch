"""The backend remembering an audit it already did (decision 0006).

WHY THIS EXISTS. `summary` is only produced at the end of a `POST /audit`
stream, and the extension's panel leads with the fit call while never being
allowed to start an audit itself -- 58 seconds and real money on every page
the user opens. So in live mode the panel had a headline with no source and
showed a word count instead. This is the source.

WHAT IT IS ALLOWED TO BE. Decision 0002 still governs: plain JSON files in a
folder on the user's own disk, beside the resumes, nothing that leaves the
machine and nothing a person cannot delete in Finder. No database, no index,
no expiry daemon -- one file per audited (post, resume) pair.

THE FAILURE THIS IS BUILT AROUND. A stored answer that is no longer true, read
back with the authority of a fresh one. Three things guard it, and all three
prefer saying nothing over saying something stale:

  * the key includes the resume id, so an answer can never cross resumes;
  * a file that will not parse, or that was written by an older shape of this
    code, is treated as absent rather than repaired;
  * a write goes to a temporary file and is renamed into place, so a crash
    half way through leaves the previous answer or none, never half of one.

What none of them guard is the resume's CONTENTS changing under a stable id.
Decision 0006 names that as the first thing to fix if resumes become editable,
and it is still true.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

# Bumped whenever the stored shape changes. An audit stored by an older
# version is unreadable rather than half-understood -- this brief changed the
# shape of all three summary lists, and a summary from before it would render
# with three fields missing and no complaint.
SCHEMA = 1

FOLDER = "audits"


def _normalise(post: str) -> str:
    """Line endings and surrounding whitespace, and nothing else.

    A browser textarea and a clipboard disagree about `\\r\\n` and about
    trailing blank lines, and two pastes of the same post should not be two
    different audits. Anything cleverer -- collapsing inner whitespace, case
    folding -- starts letting a genuinely different post collide with a stored
    answer, which is the one failure this file is supposed to prevent.
    """
    return "\n".join(line.rstrip() for line in post.replace("\r\n", "\n").split("\n")).strip()


def key_for(post: str, resume_id: str) -> str:
    """The stored name for one (post, resume) pair.

    The resume id is inside the hash rather than beside it in the filename, so
    there is no way to read a file for one resume while believing it belongs
    to another. The separator is a newline because a resume id cannot contain
    one -- see `_ID_OK` in `ingest.py` -- so no id can forge a different pair.
    """
    material = f"{resume_id}\n{_normalise(post)}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:32]


class AuditStore:
    """Finished audits as files in one folder beside the resumes."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root) / FOLDER

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def save(
        self,
        post: str,
        resume_id: str,
        requirements: list[dict[str, Any]],
        verdicts: list[dict[str, Any]],
        counts: dict[str, int],
        summary: dict[str, Any],
    ) -> str:
        """Record one finished audit. Returns the key it was stored under.

        The requirements and verdicts are stored, not just the summary, and
        that is what makes `POST /audit/requirement` possible: a second pass
        over one requirement needs the ids the client is holding and the other
        verdicts to rebuild a summary from.
        """
        self.root.mkdir(parents=True, exist_ok=True)
        key = key_for(post, resume_id)
        body = {
            "schema": SCHEMA,
            "key": key,
            "resume_id": resume_id,
            "requirements": requirements,
            "verdicts": verdicts,
            "counts": counts,
            "summary": summary,
        }

        # Rename, not write-in-place: a reader either sees the whole previous
        # audit or the whole new one.
        target = self._path(key)
        temporary = target.with_suffix(".json.part")
        temporary.write_text(json.dumps(body, indent=2), encoding="utf-8")
        os.replace(temporary, target)
        return key

    def get(self, post: str, resume_id: str) -> dict[str, Any] | None:
        """The stored audit for this pair, or None. Never an exception and
        never a partial answer: every way of failing to read one is the same
        answer to the caller, which is that we do not know."""
        path = self._path(key_for(post, resume_id))
        if not path.is_file():
            return None
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(body, dict) or body.get("schema") != SCHEMA:
            return None
        if not body.get("summary"):
            return None
        return body

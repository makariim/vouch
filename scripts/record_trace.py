#!/usr/bin/env python3
"""Record one run's events to a file, in the decision 0004 shape.

    python scripts/record_trace.py post.txt resume.txt

Brief 0001 asks for this at `fixtures/trace-sample.json`. That path is NOT the
default here, because the brief 0002 session hand-wrote that file first and
both briefs forbid the two sessions touching the same file. Default output is
`fixtures/trace-real.json`; pass --out to override once the owner agrees.

Needs a real model. It will not quietly substitute the scripted test double --
a recorded trace that is not a real run would be the wrong kind of evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from audit.graph import run_stream  # noqa: E402
from audit.model import build_model  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("post", type=Path)
    parser.add_argument("resume", type=Path)
    parser.add_argument("--out", type=Path, default=Path("fixtures/trace-real.json"))
    args = parser.parse_args(argv)

    for path in (args.post, args.resume):
        if not path.is_file():
            print(f"no such file: {path}", file=sys.stderr)
            return 2

    try:
        model = build_model()
    except Exception as exc:
        print(f"no usable model credentials: {exc}", file=sys.stderr)
        return 3

    events = list(
        run_stream(
            model,
            args.post.read_text(encoding="utf-8"),
            args.resume.read_text(encoding="utf-8"),
        )
    )

    failed = [e for e in events if e["type"] == "error"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(events, indent=2), encoding="utf-8")
    print(f"wrote {len(events)} events to {args.out}", file=sys.stderr)

    if failed:
        print(f"run reported an error: {failed[0]['message']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

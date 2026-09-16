"""Two file paths in, the audit printed, the JSON written."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .graph import run
from .model import build_model

_MARK = {
    "evidenced": "YES ",
    "partly_evidenced": "PART",
    "not_evidenced": "NO  ",
}


def render(result: dict) -> str:
    if result.get("error"):
        return f"audit failed: {result['error']}"

    by_id = {v["requirement_id"]: v for v in result["verdicts"]}
    out: list[str] = []
    for requirement in result["requirements"]:
        verdict = by_id.get(requirement["id"])
        mark = _MARK.get(verdict["verdict"], "????") if verdict else "????"
        out.append(f"{mark} {requirement['id']:>3}. {requirement['text']}")
        if verdict:
            out.append(f"         {verdict['reason']}")
            if verdict["line"]:
                out.append(f"         resume line {verdict['line_number']}: {verdict['line']}")
        out.append("")

    counts = result["counts"]
    out.append(
        "evidenced {evidenced}   partly {partly_evidenced}   "
        "not evidenced {not_evidenced}".format(**counts)
    )

    summary = result.get("summary")
    if summary:
        out += ["", "-" * 72, f"FIT: {summary['fit'].replace('_', ' ')}", "",
                summary["fit_reason"], ""]
        # Since decision 0006 every row of all three lists carries the same
        # five fields, so nothing here has to join back against the
        # requirement list or the verdicts to render a line.
        if summary["blockers"]:
            out.append("WHAT WOULD SINK IT")
            for item in summary["blockers"]:
                out.append(f"  {item['requirement_id']:>3}. {item['text']}")
            out.append("")

        if summary["undersells"]:
            out.append("WHERE YOUR RESUME UNDERSELLS YOU")
            for item in summary["undersells"]:
                out.append(f"  {item['requirement_id']:>3}. {item['text']}")
                if item["line"]:
                    out.append(f"       line {item['line_number']}: {item['line']}")
                out.append(f"       {item['reason']}")
            out.append("")

        if summary["strengths"]:
            ids = ", ".join(str(s["requirement_id"]) for s in summary["strengths"])
            out.append(f"STRENGTHS: requirements {ids}")

    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="audit", description="Check a resume against a job post, line by line."
    )
    parser.add_argument("post", type=Path, help="path to the job post, as text")
    parser.add_argument("resume", type=Path, help="path to the resume, as text")
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("audit.json"),
        help="where to write the full result (default: audit.json)",
    )
    parser.add_argument(
        "--trace",
        type=Path,
        default=None,
        help="also write just the event stream here, in the decision 0004 shape",
    )
    args = parser.parse_args(argv)

    for path in (args.post, args.resume):
        if not path.is_file():
            print(f"no such file: {path}", file=sys.stderr)
            return 2

    result = run(
        build_model(),
        args.post.read_text(encoding="utf-8"),
        args.resume.read_text(encoding="utf-8"),
    )

    print(render(result))

    args.json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nwrote {args.json}", file=sys.stderr)

    if args.trace:
        args.trace.write_text(json.dumps(result["events"], indent=2), encoding="utf-8")
        print(f"wrote {args.trace}", file=sys.stderr)

    return 1 if result.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())

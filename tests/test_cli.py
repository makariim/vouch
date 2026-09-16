"""The entry point: two file paths in, the audit printed, the JSON written."""

from __future__ import annotations

import json
from pathlib import Path

from audit import cli
from audit.testing import ScriptedModel

DATA = Path(__file__).parent / "data"


def use_scripted(monkeypatch, **kwargs):
    # The CLI now asks `build_model()` which provider to use, so that is the
    # seam. Same substitution as before, one name along.
    monkeypatch.setattr(cli, "build_model", lambda *a, **k: ScriptedModel(**kwargs))


def test_it_runs_on_two_paths_and_writes_json(tmp_path, monkeypatch, capsys):
    use_scripted(monkeypatch)
    out = tmp_path / "audit.json"

    code = cli.main([str(DATA / "post.txt"), str(DATA / "resume.txt"), "--json", str(out)])

    assert code == 0
    printed = capsys.readouterr().out
    assert "5+ years of professional Python experience" in printed
    assert "evidenced" in printed

    saved = json.loads(out.read_text(encoding="utf-8"))
    assert len(saved["verdicts"]) == len(saved["requirements"]) == 6
    assert sum(saved["counts"].values()) == 6


def test_it_can_also_write_just_the_trace(tmp_path, monkeypatch, capsys):
    use_scripted(monkeypatch)
    trace = tmp_path / "trace.json"

    cli.main(
        [
            str(DATA / "post.txt"),
            str(DATA / "resume.txt"),
            "--json",
            str(tmp_path / "audit.json"),
            "--trace",
            str(trace),
        ]
    )

    events = json.loads(trace.read_text(encoding="utf-8"))
    assert events[0]["type"] == "requirements"
    assert events[-1]["type"] == "summary"
    assert events[-2]["type"] == "done"


def test_a_missing_file_is_reported_not_a_stack_trace(tmp_path, monkeypatch, capsys):
    use_scripted(monkeypatch)
    code = cli.main([str(tmp_path / "nope.txt"), str(DATA / "resume.txt")])

    assert code == 2
    assert "no such file" in capsys.readouterr().err


def test_an_empty_resume_exits_nonzero(tmp_path, monkeypatch, capsys):
    use_scripted(monkeypatch)
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")

    code = cli.main(
        [str(DATA / "post.txt"), str(empty), "--json", str(tmp_path / "a.json")]
    )

    assert code == 1
    assert "resume is empty" in capsys.readouterr().out

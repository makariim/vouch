"""`.env` is a fallback, not an authority, and it never says a value out loud."""

from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from audit import env

REPO = Path(__file__).resolve().parents[1]

# A key-shaped string that is not a key. Used so the "never printed" assertions
# have something specific to look for.
FAKE = "gsk_thisisnotarealkey_0123456789"


@pytest.fixture(autouse=True)
def restore_environment():
    """`load()` writes to `os.environ` on purpose, so put it back afterwards.

    `monkeypatch` cannot: it only undoes what it did itself, and the whole
    subject here is a function that sets variables nobody told it about.
    """
    before = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(before)


def write(root: Path, text: str) -> Path:
    (root / ".env").write_text(text, encoding="utf-8")
    return root


def load(root: Path) -> tuple[list[str], str]:
    said = io.StringIO()
    return env.load(root, stream=said), said.getvalue()


def real_env_key() -> str | None:
    """The actual key in the actual `.env`, or None.

    A test may read it. Nothing may print it -- which is why it is read at all:
    it is the only way to assert that one specific secret is absent from
    output.
    """
    try:
        text = (REPO / ".env").read_text(encoding="utf-8")
    except OSError:
        return None
    return env.parse(text).get("GROQ_API_KEY")


def test_a_key_in_the_file_reaches_the_environment(tmp_path):
    os.environ.pop("GROQ_API_KEY", None)
    write(tmp_path, f'GROQ_API_KEY="{FAKE}"\n')

    names, _ = load(tmp_path)

    assert names == ["GROQ_API_KEY"]
    assert os.environ["GROQ_API_KEY"] == FAKE


def test_quotes_belong_to_the_file_not_to_the_value(tmp_path):
    for name in ("A", "B", "C"):
        os.environ.pop(name, None)
    write(tmp_path, f'A="{FAKE}"\nB=\'{FAKE}\'\nC={FAKE}\n')

    load(tmp_path)

    assert os.environ["A"] == os.environ["B"] == os.environ["C"] == FAKE


def test_the_shell_wins(tmp_path):
    os.environ["GROQ_API_KEY"] = "set-by-a-person-on-purpose"
    write(tmp_path, f'GROQ_API_KEY="{FAKE}"\n')

    names, said = load(tmp_path)

    assert names == []
    assert os.environ["GROQ_API_KEY"] == "set-by-a-person-on-purpose"
    assert "the shell already had GROQ_API_KEY" in said
    assert FAKE not in said


def test_no_file_is_no_error_and_no_message(tmp_path):
    names, said = load(tmp_path)

    assert names == []
    assert said == ""


def test_junk_lines_are_survived(tmp_path):
    for name in ("REAL", "EXPORTED"):
        os.environ.pop(name, None)
    write(
        tmp_path,
        "\n"
        "# a comment\n"
        "   \n"
        "a line with no equals sign\n"
        "=novalue\n"
        "export EXPORTED=yes\n"
        "REAL=here\n",
    )

    names, _ = load(tmp_path)

    assert names == ["EXPORTED", "REAL"]
    assert os.environ["REAL"] == "here"
    assert os.environ["EXPORTED"] == "yes"


def test_the_line_it_prints_names_the_key_and_never_the_value(tmp_path):
    os.environ.pop("GROQ_API_KEY", None)
    write(tmp_path, f'GROQ_API_KEY="{FAKE}"\n')

    _, said = load(tmp_path)

    assert said.strip() == "audit: read .env -- set GROQ_API_KEY"
    assert FAKE not in said
    # Not truncated either. No prefix of a key is a thing we print.
    assert FAKE[:8] not in said


def test_importing_the_package_reads_the_repository_env(tmp_path):
    """The real path, in a real interpreter: no key exported, `.env` on disk.

    A subprocess because the import in this process already happened, and the
    claim is about what a fresh start does. The repository root rather than a
    `tmp_path`, because the root is derived from where the package lives and
    that is the point -- a test that pointed it elsewhere would be testing
    something we do not ship.
    """
    key = real_env_key()
    if key is None:
        pytest.skip("no .env with a GROQ_API_KEY here; nothing to load")

    clean = {k: v for k, v in os.environ.items() if k != "GROQ_API_KEY"}
    clean["PYTHONPATH"] = str(REPO / "src")

    done = subprocess.run(
        [
            sys.executable,
            "-c",
            "import audit, os; import audit.model;"
            "print('KEY_LEN', len(os.environ.get('GROQ_API_KEY', '')));"
            "print('QUOTED', os.environ.get('GROQ_API_KEY', '')[:1] in ('\\'', '\"'))",
        ],
        cwd=tmp_path,
        env=clean,
        capture_output=True,
        text=True,
    )

    assert done.returncode == 0, done.stderr
    # Loaded, from the repository, from a working directory that is not it.
    assert f"KEY_LEN {len(key)}" in done.stdout
    assert "QUOTED False" in done.stdout
    assert "audit: read .env -- set GROQ_API_KEY" in done.stderr
    # The value is nowhere. Not whole, not truncated.
    everything = done.stdout + done.stderr
    assert key not in everything
    assert key[:8] not in everything


def test_the_shell_wins_in_a_real_interpreter(tmp_path):
    """The other half, and the half that would be a quiet disaster if it broke:
    a person exported a key and a file on disk overrode it."""
    if real_env_key() is None:
        pytest.skip("no .env with a GROQ_API_KEY here; nothing to override")

    mine = "set-by-a-person-on-purpose"
    shell = {**os.environ, "GROQ_API_KEY": mine, "PYTHONPATH": str(REPO / "src")}

    done = subprocess.run(
        [sys.executable, "-c", "import audit, os; print(os.environ['GROQ_API_KEY'])"],
        cwd=tmp_path,
        env=shell,
        capture_output=True,
        text=True,
    )

    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == mine
    assert "the shell already had GROQ_API_KEY" in done.stderr

"""The backend remembering a finished audit (decision 0006).

The whole risk in this file is one failure: a stored answer that is no longer
true, handed back with the authority of a fresh one. So most of what is tested
here is the store declining to answer.
"""

from __future__ import annotations

import json

from audit.store import SCHEMA, AuditStore, key_for

POST = "We need Python and SQL.\n"
SUMMARY = {"type": "summary", "fit": "strong", "fit_reason": "x",
           "blockers": [], "strengths": [], "undersells": []}
COUNTS = {"evidenced": 1, "partly_evidenced": 0, "not_evidenced": 0}
REQUIREMENTS = [{"id": 1, "text": "Python", "required": True}]
VERDICTS = [{"type": "verdict", "requirement_id": 1, "verdict": "evidenced",
             "line": "Python", "line_number": 3, "reason": "stated"}]


def save(store: AuditStore, post: str = POST, resume_id: str = "alex") -> str:
    return store.save(post, resume_id, REQUIREMENTS, VERDICTS, COUNTS, SUMMARY)


# --- the key -----------------------------------------------------------------


def test_the_same_post_and_resume_key_the_same():
    assert key_for(POST, "alex") == key_for(POST, "alex")


def test_a_different_resume_is_a_different_key():
    """The failure this prevents: an answer built from one resume being handed
    back for another. Decision 0006 puts the id inside the hash for this."""
    assert key_for(POST, "alex") != key_for(POST, "sam")


def test_a_different_post_is_a_different_key():
    assert key_for(POST, "alex") != key_for(POST + " And Go.", "alex")


def test_line_endings_and_trailing_space_are_not_a_different_post():
    """A textarea and a clipboard disagree about these, and two pastes of one
    post must not be two audits."""
    assert key_for("Python  \r\nSQL\n\n", "alex") == key_for("Python\nSQL", "alex")


def test_an_id_cannot_forge_another_pairs_key():
    """The separator is a newline, which `ingest._ID_OK` forbids in an id, so
    no id can be chosen that hashes to a different pair."""
    assert key_for(POST, "alex") != key_for("", "alex\n" + POST)


# --- storing and reading back ------------------------------------------------


def test_what_goes_in_comes_back(tmp_path):
    store = AuditStore(tmp_path)
    save(store)
    got = store.get(POST, "alex")
    assert got is not None
    assert got["summary"] == SUMMARY
    assert got["counts"] == COUNTS
    # The requirements and verdicts are stored too -- a second pass over one
    # requirement needs the ids the client holds and the other verdicts.
    assert got["requirements"] == REQUIREMENTS
    assert got["verdicts"] == VERDICTS


def test_a_post_that_was_never_audited_is_not_known(tmp_path):
    assert AuditStore(tmp_path).get(POST, "alex") is None


def test_a_stored_answer_never_crosses_resumes(tmp_path):
    store = AuditStore(tmp_path)
    save(store, resume_id="alex")
    assert store.get(POST, "sam") is None


def test_re_auditing_replaces_rather_than_accumulates(tmp_path):
    store = AuditStore(tmp_path)
    save(store)
    fresher = dict(SUMMARY, fit="weak")
    store.save(POST, "alex", REQUIREMENTS, VERDICTS, COUNTS, fresher)
    assert store.get(POST, "alex")["summary"]["fit"] == "weak"
    assert len(list((tmp_path / "audits").glob("*.json"))) == 1


# --- declining to answer -----------------------------------------------------


def test_a_file_that_will_not_parse_is_not_an_answer(tmp_path):
    store = AuditStore(tmp_path)
    key = save(store)
    (tmp_path / "audits" / f"{key}.json").write_text("{ half a fi", encoding="utf-8")
    assert store.get(POST, "alex") is None


def test_an_audit_stored_by_an_older_shape_is_not_an_answer(tmp_path):
    """This brief changed the shape of all three summary lists. A summary
    written before it would render with three fields missing and no
    complaint, which is worse than saying nothing."""
    store = AuditStore(tmp_path)
    key = save(store)
    path = tmp_path / "audits" / f"{key}.json"
    body = json.loads(path.read_text(encoding="utf-8"))
    body["schema"] = SCHEMA - 1
    path.write_text(json.dumps(body), encoding="utf-8")
    assert store.get(POST, "alex") is None


def test_a_record_with_no_summary_is_not_an_answer(tmp_path):
    store = AuditStore(tmp_path)
    key = store.save(POST, "alex", REQUIREMENTS, VERDICTS, COUNTS, {})
    assert (tmp_path / "audits" / f"{key}.json").is_file()
    assert store.get(POST, "alex") is None


def test_nothing_is_left_behind_half_written(tmp_path):
    store = AuditStore(tmp_path)
    save(store)
    leftovers = list((tmp_path / "audits").glob("*.part"))
    assert leftovers == []


def test_the_folder_sits_beside_the_resumes(tmp_path):
    """Decision 0002: plain files on the user's disk, in one place they can
    open in Finder and delete by hand."""
    store = AuditStore(tmp_path)
    save(store)
    assert (tmp_path / "audits").is_dir()

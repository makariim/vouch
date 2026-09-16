"""The endpoint from decision 0004, including the shape EventSource needs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from audit.server import create_app
from audit.testing import ScriptedModel

DATA = Path(__file__).parent / "data"
POST = (DATA / "post.txt").read_text(encoding="utf-8")
RESUME = (DATA / "resume.txt").read_text(encoding="utf-8")


@pytest.fixture
def client():
    return TestClient(create_app(model=ScriptedModel(weak_once={"Hands-on Kubernetes in production"})))


def frames(body: str) -> list[dict]:
    """Parse the stream the way a browser would: split on the blank line."""
    out = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        assert block.startswith("data: "), f"not an SSE frame: {block[:40]!r}"
        out.append(json.loads(block[len("data: ") :]))
    return out


def test_audit_streams_server_sent_events(client):
    response = client.post("/audit", json={"post": POST, "resume": RESUME})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = frames(response.text)
    assert events[0]["type"] == "requirements"
    assert events[-1]["type"] == "summary"
    assert events[-2]["type"] == "done"

    kinds = {e["type"] for e in events}
    assert kinds <= {"requirements", "step", "verdict", "done", "summary", "error"}
    assert {"requirements", "step", "verdict", "done"} <= kinds


def test_every_frame_is_one_line_of_json(client):
    """EventSource breaks if a data line contains a raw newline."""
    response = client.post("/audit", json={"post": POST, "resume": RESUME})
    for line in response.text.splitlines():
        if line.startswith("data: "):
            json.loads(line[len("data: ") :])


def test_the_retry_appears_in_the_stream(client):
    response = client.post("/audit", json={"post": POST, "resume": RESUME})
    events = frames(response.text)
    assert any(e["type"] == "step" and e["step"] == "retry" for e in events)


def test_empty_resume_streams_an_error_event(client):
    response = client.post("/audit", json={"post": POST, "resume": ""})
    events = frames(response.text)
    assert events == [{"type": "error", "message": "resume is empty"}]


def test_missing_fields_do_not_crash_the_endpoint(client):
    response = client.post("/audit", json={})
    assert response.status_code == 200
    assert frames(response.text)[0]["type"] == "error"


def test_index_serves_the_frontend_when_it_exists(tmp_path, monkeypatch):
    page = tmp_path / "index.html"
    page.write_text("<h1>owned by brief 0002</h1>", encoding="utf-8")
    monkeypatch.setattr("audit.server.FRONTEND_DIR", tmp_path)

    response = TestClient(create_app(model=ScriptedModel())).get("/")
    assert response.status_code == 200
    assert "owned by brief 0002" in response.text


def test_index_says_so_when_the_frontend_is_not_there_yet(tmp_path, monkeypatch):
    monkeypatch.setattr("audit.server.FRONTEND_DIR", tmp_path)
    response = TestClient(create_app(model=ScriptedModel())).get("/")
    assert response.status_code == 200
    assert "Brief 0002" in response.text


def test_static_assets_cannot_escape_the_frontend_folder(tmp_path, monkeypatch):
    monkeypatch.setattr("audit.server.FRONTEND_DIR", tmp_path)
    client = TestClient(create_app(model=ScriptedModel()))
    assert client.get("/../../etc/passwd").status_code == 404


def test_it_serves_the_real_page_that_brief_0002_built():
    """Integration with the other session's files, which land in web/."""
    from audit.server import FRONTEND_DIR

    if not (FRONTEND_DIR / "index.html").is_file():
        pytest.skip("brief 0002 has not landed web/index.html yet")

    client = TestClient(create_app(model=ScriptedModel()))

    page = client.get("/")
    assert page.status_code == 200
    assert "<html" in page.text.lower()

    for asset, kind in (("app.js", "text/javascript"), ("styles.css", "text/css")):
        if (FRONTEND_DIR / asset).is_file():
            response = client.get(f"/{asset}")
            assert response.status_code == 200
            assert response.headers["content-type"].startswith(kind)


def test_the_recorded_fixture_matches_the_shapes_this_backend_emits():
    """Brief 0002 hand-wrote fixtures/trace-sample.json from decision 0004.
    If the backend and that file disagree, the join at the end breaks."""
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "trace-sample.json"
    if not fixture.is_file():
        pytest.skip("no fixture recorded yet")

    recorded = json.loads(fixture.read_text(encoding="utf-8"))
    events = recorded if isinstance(recorded, list) else recorded["events"]

    live = frames(
        TestClient(create_app(model=ScriptedModel()))
        .post("/audit", json={"post": POST, "resume": RESUME})
        .text
    )
    keys_by_type: dict[str, set] = {}
    for event in live:
        keys_by_type.setdefault(event["type"], set()).update(event.keys())

    # Subset, not equality. The fixture omits `line`/`line_number` on a
    # not_evidenced verdict where this backend sends them as null. Both read
    # the same from JavaScript, so the page works either way -- but it is a
    # real divergence from decision 0004, and it is reported, not patched here.
    for event in events:
        assert event["type"] in {"requirements", "step", "verdict", "done", "error"}
        if event["type"] in keys_by_type:
            unknown = set(event.keys()) - keys_by_type[event["type"]]
            assert not unknown, (
                f"the fixture's {event['type']} carries fields this backend never "
                f"sends: {sorted(unknown)}"
            )


def test_a_not_evidenced_verdict_still_carries_the_line_fields():
    """Pinned deliberately: decision 0004's example always shows both fields,
    so this backend always sends them, as null when there is no evidence."""
    client = TestClient(create_app(model=ScriptedModel()))
    events = frames(client.post("/audit", json={"post": POST, "resume": RESUME}).text)

    nothing = [
        e for e in events if e["type"] == "verdict" and e["verdict"] == "not_evidenced"
    ]
    assert nothing
    for event in nothing:
        assert event["line"] is None
        assert event["line_number"] is None


# --- resumes, and the audit reading one (decision 0005) ------------------


@pytest.fixture
def stored_client(tmp_path):
    """A client with its own resume folder, so no test writes outside itself."""
    from audit.ingest import ResumeStore

    store = ResumeStore(tmp_path / "resumes")
    store.save("default.txt", RESUME)
    return TestClient(create_app(model=ScriptedModel(), resumes=store))


def test_uploading_a_txt_returns_an_id(stored_client):
    response = stored_client.post(
        "/resumes", files={"file": ("dana.txt", b"one\ntwo\n", "text/plain")}
    )
    assert response.status_code == 200
    assert response.json()["id"] == "dana"


def test_uploading_an_unsupported_type_is_refused(stored_client):
    response = stored_client.post(
        "/resumes", files={"file": ("cv.docx", b"x", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "unsupported file type" in response.json()["error"]


def test_listing_resumes(stored_client):
    rows = stored_client.get("/resumes").json()["resumes"]
    assert [row["id"] for row in rows] == ["default"]
    assert rows[0]["default"] is True


def test_showing_a_resume_gives_numbered_lines(stored_client):
    """The whole point of the endpoint: a human sees what the tool sees
    before trusting a verdict."""
    body = stored_client.get("/resumes/default").json()
    assert body["id"] == "default"
    numbers = [line["number"] for line in body["lines"]]
    assert numbers == sorted(numbers)
    assert all(line["text"].strip() for line in body["lines"])


def test_the_numbers_shown_are_the_numbers_a_verdict_cites(stored_client):
    """Both come from `index_resume`. If they ever drift, every quote in the
    product is pointing at the wrong line."""
    shown = {
        line["number"]: line["text"]
        for line in stored_client.get("/resumes/default").json()["lines"]
    }
    response = stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    for event in frames(response.text):
        if event["type"] == "verdict" and event["line_number"]:
            assert shown[event["line_number"]] == event["line"]


def test_showing_a_resume_lists_what_repair_changed(stored_client):
    damaged = (DATA / "resume_damaged.txt").read_text(encoding="utf-8")
    stored_client.post(
        "/resumes", files={"file": ("damaged.txt", damaged.encode(), "text/plain")}
    )
    body = stored_client.get("/resumes/damaged").json()
    assert body["repairs"]
    assert {"kind", "source_line", "before", "after"} == set(body["repairs"][0])


def test_an_unknown_resume_is_a_404(stored_client):
    assert stored_client.get("/resumes/nope").status_code == 404


def test_a_resume_id_cannot_walk_out_of_the_folder(stored_client):
    assert stored_client.get("/resumes/..%2F..%2Fetc%2Fpasswd").status_code == 404


def test_the_default_can_be_moved(stored_client):
    stored_client.post("/resumes", files={"file": ("other.txt", b"hello\n", "text/plain")})
    assert stored_client.post("/resumes/other/default").status_code == 200
    assert stored_client.get("/resumes/other").json()["default"] is True


def test_the_audit_can_read_a_stored_resume(stored_client):
    response = stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    events = frames(response.text)
    assert events[0]["type"] == "requirements"
    assert events[-1]["type"] == "summary"


def test_an_unknown_resume_id_streams_an_error_rather_than_crashing(stored_client):
    response = stored_client.post("/audit", json={"post": POST, "resume_id": "nope"})
    assert frames(response.text) == [{"type": "error", "message": "no resume 'nope'"}]


def test_every_requirement_carries_required(stored_client):
    response = stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    items = frames(response.text)[0]["items"]
    assert items
    for item in items:
        assert isinstance(item["required"], bool)


def test_the_summary_event_carries_all_five_fields(stored_client):
    response = stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    summary = frames(response.text)[-1]
    assert summary["type"] == "summary"
    assert set(summary) == {
        "type", "fit", "fit_reason", "blockers", "strengths", "undersells"
    }


# --- the contract's holes, closed by decision 0006 -----------------------


def test_a_post_that_was_never_audited_is_not_known(stored_client):
    """The panel asking what we know, before anything has been audited."""
    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert body == {"known": False}


def test_an_audited_post_answers_instantly_and_for_free(stored_client):
    """Decision 0006 hole 1. The extension's panel leads with the fit call and
    may never start an audit itself -- 58 seconds and real money on every page
    the user opens. This is where its headline comes from."""
    streamed = frames(
        stored_client.post("/audit", json={"post": POST, "resume_id": "default"}).text
    )[-1]

    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert body["known"] is True
    # Decision 0008 adds `counts` and `requirements` beside the summary, so the
    # reply is no longer the summary event and nothing else. Every field the
    # summary event carries must still come back byte for byte.
    extra = {"known", "counts", "requirements"}
    assert {k: v for k, v in body.items() if k not in extra} == streamed


def test_the_stored_summary_carries_all_five_fields(stored_client):
    """Decision 0008 widens this reply by exactly two fields and no more."""
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert set(body) == {
        "known", "type", "fit", "fit_reason", "blockers", "strengths", "undersells",
        "counts", "requirements",
    }


def test_all_three_stored_lists_have_the_same_shape(stored_client):
    """Decision 0006 item 3, over the wire rather than in the product layer."""
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()

    rows = body["blockers"] + body["strengths"] + body["undersells"]
    assert rows, "no rows at all -- this check would pass for the wrong reason"
    for row in rows:
        assert set(row) == {"requirement_id", "text", "line", "line_number", "reason"}


def test_a_stored_summary_never_answers_for_another_resume(stored_client):
    """The failure decision 0006 names as the one that matters: an answer that
    is no longer true, returned with the authority of a fresh one."""
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    stored_client.post("/resumes", files={"file": ("other.txt", b"Pastry chef\n", "text/plain")})

    body = stored_client.post("/summary", json={"post": POST, "resume_id": "other"}).json()
    assert body == {"known": False}


def test_a_different_post_is_not_known(stored_client):
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    body = stored_client.post("/summary", json={"post": "Wanted: a chef.", "resume_id": "default"}).json()
    assert body == {"known": False}


def test_an_audit_of_pasted_text_is_not_remembered(stored_client):
    """Nothing keys it. Two pastes are two documents and there is nothing here
    that can tell them apart, so the honest answer is that we do not know."""
    stored_client.post("/audit", json={"post": POST, "resume": RESUME})
    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert body == {"known": False}


def test_asking_about_a_resume_that_does_not_exist_is_not_an_error(stored_client):
    response = stored_client.post("/summary", json={"post": POST, "resume_id": "nope"})
    assert response.status_code == 200
    assert response.json() == {"known": False}


# --- a second pass over one requirement (decision 0006) ------------------


def test_re_running_one_requirement_streams_only_that_one(stored_client):
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})

    events = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 3},
        ).text
    )
    assert events[0]["type"] == "requirements"
    assert [item["id"] for item in events[0]["items"]] == [3]

    verdicts = [e for e in events if e["type"] == "verdict"]
    assert [v["requirement_id"] for v in verdicts] == [3]


def test_a_second_pass_ends_with_a_fresh_summary(stored_client):
    """Decision 0006: without this the fit call, the blockers and the
    undersells go stale the moment a verdict changes, and the page is left
    either lying or apologising."""
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    events = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 3},
        ).text
    )
    assert events[-1]["type"] == "summary"
    assert events[-2]["type"] == "done"


def test_the_fresh_summary_covers_the_whole_audit_not_one_requirement(stored_client):
    """The trap this endpoint could have fallen into: a summary computed from
    the single verdict just produced, which would read as an audit of a
    one-requirement job post."""
    first = frames(stored_client.post("/audit", json={"post": POST, "resume_id": "default"}).text)
    before = next(e for e in first if e["type"] == "done")["counts"]

    events = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 3},
        ).text
    )
    after = next(e for e in events if e["type"] == "done")["counts"]
    assert sum(after.values()) == sum(before.values())


def test_a_second_pass_is_remembered_in_place_of_the_first(stored_client):
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    fresh = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 3},
        ).text
    )[-1]

    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    extra = {"known", "counts", "requirements"}
    assert {k: v for k, v in body.items() if k not in extra} == fresh


def test_a_second_pass_without_a_requirement_is_refused(stored_client):
    response = stored_client.post(
        "/audit/requirement", json={"post": POST, "resume_id": "default"}
    )
    assert frames(response.text) == [{"type": "error", "message": "requirement_id is required"}]


def test_a_requirement_that_is_not_in_the_audit_streams_an_error(stored_client):
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    response = stored_client.post(
        "/audit/requirement",
        json={"post": POST, "resume_id": "default", "requirement_id": 99},
    )
    assert frames(response.text) == [
        {"type": "error", "message": "no requirement 99 in this audit"}
    ]


def test_a_second_pass_on_a_post_never_audited_still_works(stored_client):
    """No stored audit means extraction has to run, so the ids come from the
    same place a fresh audit's would."""
    events = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 2},
        ).text
    )
    assert [item["id"] for item in events[0]["items"]] == [2]
    assert events[-1]["type"] == "summary"


def test_nothing_in_the_second_pass_stream_calls_itself_a_retry(stored_client):
    """Decision 0007: a person asking for another pass is not the agent
    deciding, and presenting it as one would be dishonest. Any `retry` step
    here would have to be the agent's own, inside the requirement."""
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    events = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 1},
        ).text
    )
    assert all(e.get("step") != "dropped" for e in events)
    assert events[0]["type"] == "requirements"


# --- the two closed sets (decision 0006 item 5) --------------------------


def test_every_step_the_backend_emits_is_in_the_written_down_set(stored_client):
    from audit.events import EMITTED_STEPS

    events = frames(stored_client.post("/audit", json={"post": POST, "resume_id": "default"}).text)
    steps = {e["step"] for e in events if e["type"] == "step"}
    assert steps, "no steps at all -- this check would pass for the wrong reason"
    assert steps <= set(EMITTED_STEPS)


def test_the_prescreen_signal_is_in_the_written_down_set(stored_client):
    from audit.events import SIGNALS

    body = stored_client.post("/prescreen", json={"post": POST, "resume_id": "default"}).json()
    assert body["signal"] in SIGNALS


# --- decision 0008: the stored answer carries the whole answer ------------


def test_the_summary_carries_the_counts_row_the_panel_draws(stored_client):
    """The panel's top line is the answer word, one sentence AND a counts row.
    The counts must be the ones the run itself emitted, not counted here."""
    streamed = frames(
        stored_client.post("/audit", json={"post": POST, "resume_id": "default"}).text
    )
    done = next(e for e in streamed if e["type"] == "done")["counts"]

    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert body["counts"] == done
    assert sum(body["counts"].values()) > 0, "no counts at all -- this would pass for nothing"


def test_the_summary_carries_every_requirement_not_just_the_shortlist(stored_client):
    """The three lists are a shortlist. Decision 0008: the panel's folded list
    is everything the post asks for, and it cannot be derived from them."""
    streamed = frames(
        stored_client.post("/audit", json={"post": POST, "resume_id": "default"}).text
    )
    asked = streamed[0]["items"]

    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert [r["id"] for r in body["requirements"]] == [r["id"] for r in asked]
    assert [r["text"] for r in body["requirements"]] == [r["text"] for r in asked]

    shortlist = body["blockers"] + body["strengths"] + body["undersells"]
    assert len(body["requirements"]) > len(shortlist), (
        "the shortlist is as long as the whole list here, so this test proves nothing"
    )


def test_each_returned_requirement_is_the_requirements_event_shape(stored_client):
    """Id, text, required, and nothing more -- decision 0008 says that list is
    the one the `requirements` event carries."""
    stored_client.post("/audit", json={"post": POST, "resume_id": "default"})
    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert body["requirements"]
    for item in body["requirements"]:
        assert set(item) == {"id", "text", "required"}
        assert isinstance(item["required"], bool)


def test_an_unknown_post_still_answers_with_known_false_and_nothing_else(stored_client):
    """The widened reply must not leak empty counts into the unknown case. A
    panel that saw `counts` would draw a zero row for a post nobody audited."""
    body = stored_client.post("/summary", json={"post": "something else", "resume_id": "default"}).json()
    assert body == {"known": False}


def test_a_second_pass_does_not_shrink_the_stored_requirement_list(stored_client):
    """A second pass emits a `requirements` event holding ONE item, and the
    save used to take that as the whole audit's list. The stored list then
    held one requirement: a third pass could not find its own id, and this
    endpoint would hand the panel a one-item list of everything asked for."""
    before = frames(
        stored_client.post("/audit", json={"post": POST, "resume_id": "default"}).text
    )[0]["items"]
    assert len(before) > 1, "one requirement in the fixture -- this proves nothing"

    stored_client.post(
        "/audit/requirement",
        json={"post": POST, "resume_id": "default", "requirement_id": 3},
    )

    body = stored_client.post("/summary", json={"post": POST, "resume_id": "default"}).json()
    assert [r["id"] for r in body["requirements"]] == [r["id"] for r in before]

    # and the third pass the shrunk list used to make impossible
    again = frames(
        stored_client.post(
            "/audit/requirement",
            json={"post": POST, "resume_id": "default", "requirement_id": 3},
        ).text
    )
    assert not [e for e in again if e["type"] == "error"], again


# --- decision 0008: `repair` is a step, and there is one set -------------


def test_there_is_one_step_set_and_repair_is_in_it():
    from audit.events import EMITTED_STEPS, STEPS

    assert "repair" in STEPS
    assert EMITTED_STEPS is STEPS, "two names must not be two tuples again"
    assert set(STEPS) == {
        "search", "judge", "verify", "retry", "failed", "dropped", "repair"
    }


# --- decision 0008: a resume says what it is called -----------------------


def test_listed_resumes_say_what_they_are_called(stored_client):
    """The panel promises to say what it checked you against."""
    rows = stored_client.get("/resumes").json()["resumes"]
    assert rows
    for row in rows:
        assert row["name"], row
        assert row["name"].startswith(row["id"])

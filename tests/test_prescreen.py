"""The fast speed, and the proof that it really is one.

Brief 0007 asks for a test that fails if a model call is attempted. There are
three here, at three different depths, because "no model call" can be broken
in three different ways:

    a model that explodes if touched     catches a call through the injected model
    build_model replaced with a trap     catches a call that builds its own
    socket() replaced with a trap        catches ANY network, by anyone, including
                                         a library doing it quietly

The third is the one that would survive somebody refactoring the other two.
"""

from __future__ import annotations

import socket
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from audit import prescreen as prescreen_module
from audit.index import LineIndex
from audit.ingest import ResumeStore
from audit.prescreen import candidate_requirements, prescreen
from audit.server import create_app

DATA = Path(__file__).parent / "data"
POST = (DATA / "post.txt").read_text(encoding="utf-8")
RESUME = (DATA / "resume.txt").read_text(encoding="utf-8")
UNRELATED = (DATA / "resume_unrelated.txt").read_text(encoding="utf-8")


class ExplodingModel:
    """Every method on the Model protocol, and every one of them a failure."""

    def extract(self, post):
        raise AssertionError("prescreen called the model")

    def choose_query(self, requirement, tried, seen):
        raise AssertionError("prescreen called the model")

    def judge(self, requirement, lines):
        raise AssertionError("prescreen called the model")


@pytest.fixture
def client(tmp_path):
    store = ResumeStore(tmp_path / "resumes")
    store.save("default.txt", RESUME)
    return TestClient(create_app(model=ExplodingModel(), resumes=store))


# --- what it answers -----------------------------------------------------


def test_a_matching_resume_scores_above_an_unrelated_one():
    """The only thing a rough count has to get right: the ordering."""
    matching = prescreen(POST, LineIndex(RESUME))
    unrelated = prescreen(POST, LineIndex(UNRELATED))
    assert matching["total"] == unrelated["total"] > 0
    assert matching["matched"] > unrelated["matched"]


def test_one_shared_word_is_not_a_match():
    """A single overlapping word matched every requirement in the real post,
    which is a signal that says nothing. Two words is the bar."""
    post = "You must have deep experience with Kubernetes and Helm in production.\n"
    resume = LineIndex("Wrote Python services and maintained deployment scripts.\n")
    assert prescreen(post, resume)["matched"] == 0


def test_an_unrelated_resume_is_a_skip():
    result = prescreen(POST, LineIndex(UNRELATED))
    assert result["signal"] == "skip"


def test_headings_and_boilerplate_are_not_counted_as_requirements():
    post = (
        "Requirements:\n\n"
        "You will build and operate REST APIs in Python daily.\n\n"
        "We are an equal opportunity employer and we encourage everyone to apply.\n"
    )
    assert candidate_requirements(post) == [
        "You will build and operate REST APIs in Python daily."
    ]


def test_the_endpoint_returns_the_decision_0005_shape(client):
    response = client.post("/prescreen", json={"post": POST, "resume_id": "default"})
    assert response.status_code == 200
    assert set(response.json()) == {"signal", "matched", "total"}


def test_an_empty_post_is_refused_rather_than_scored(client):
    assert client.post("/prescreen", json={"post": "", "resume_id": "default"}).status_code == 400


def test_an_unknown_resume_is_a_404(client):
    assert client.post("/prescreen", json={"post": POST, "resume_id": "nope"}).status_code == 404


# --- no model call, proven three ways ------------------------------------


def test_the_endpoint_does_not_call_the_model(client):
    """The injected model raises on every method. A model call fails here."""
    assert client.post("/prescreen", json={"post": POST, "resume_id": "default"}).status_code == 200


def test_the_endpoint_does_not_build_a_model_of_its_own(monkeypatch, client):
    """Catches the other half: calling `build_model()` instead of the injected
    one, which the injected-model test above would never notice."""

    def trap(*args, **kwargs):
        raise AssertionError("prescreen built a model")

    monkeypatch.setattr("audit.server.build_model", trap)
    assert client.post("/prescreen", json={"post": POST, "resume_id": "default"}).status_code == 200


def test_the_endpoint_opens_no_socket(monkeypatch, client):
    """The broadest of the three: no network at all, by anybody, including a
    library reaching out on its own. Decision 0002 allows exactly one outbound
    call in this project and it is the model call, which is not here."""

    def trap(*args, **kwargs):
        raise AssertionError("prescreen opened a socket")

    # Only network families. The test client runs the app on an in-process
    # anyio portal that uses an AF_UNIX socketpair, which is plumbing, not a
    # call leaving the machine.
    real_socket = socket.socket

    def guarded(family=socket.AF_INET, *args, **kwargs):
        if family in (socket.AF_INET, socket.AF_INET6):
            trap()
        return real_socket(family, *args, **kwargs)

    monkeypatch.setattr(socket, "socket", guarded)
    monkeypatch.setattr(socket, "create_connection", trap)
    assert client.post("/prescreen", json={"post": POST, "resume_id": "default"}).status_code == 200


def test_the_prescreen_module_cannot_reach_a_model_at_all():
    """Structural, not behavioural: there is no name in the module that could
    become a model call in a later edit."""
    names = dir(prescreen_module)
    assert "build_model" not in names
    assert "Model" not in names


# --- and that it is fast -------------------------------------------------


def test_it_answers_in_well_under_a_hundred_milliseconds(client):
    """Brief 0007's number. Measured over the whole HTTP round trip, after a
    warm-up call so import and route resolution are not counted as work the
    user waits for on every job post."""
    payload = {"post": POST, "resume_id": "default"}
    client.post("/prescreen", json=payload)

    best = min(
        (
            (lambda t0: (client.post("/prescreen", json=payload), time.perf_counter() - t0)[1])(
                time.perf_counter()
            )
        )
        for _ in range(5)
    )
    assert best < 0.100, f"prescreen took {best * 1000:.1f}ms"

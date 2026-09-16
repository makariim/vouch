"""The product layer: required, fit, blockers, strengths, undersells.

None of this calls a model, so all of it is testable exactly.
"""

from __future__ import annotations

from audit.index import LineIndex
from audit.product import is_required, is_weakly_stated, summarise

POST = """Requirements:

Demonstrable experience building REST APIs (e.g., using Flask, FastAPI) to serve ML models.

Proficiency with containerization using Docker and Kubernetes (K8s).

A Master's Degree or Ph.D. in Computer Science or a related quantitative field.

DataRobot Experience: Familiarity with the DataRobot AI Platform is a strong plus.

Nice to have:

Experience with Apache Kafka or similar streaming systems.
"""

RESUME = """Dana Okafor

Rebuilt the ingestion pipeline's concurrency model, cutting peak memory 6.2x.
FastAPI, Elasticsearch, Redis, PostgreSQL, Kafka, Spark, async Python
Docker, Kubernetes, Helm, GitHub Actions, AWS ECR, GCP Secret Manager
"""


def requirement(text: str, rid: int, post_index: LineIndex) -> dict:
    return {"id": rid, "text": text, "required": is_required(text, post_index)}


# --- required ------------------------------------------------------------


def test_a_plain_requirement_is_required():
    index = LineIndex(POST)
    text = "Proficiency with containerization using Docker and Kubernetes (K8s)."
    assert is_required(text, index) is True


def test_the_posts_own_words_make_it_optional():
    """`is a strong plus` is in the requirement sentence itself."""
    index = LineIndex(POST)
    text = "DataRobot Experience: Familiarity with the DataRobot AI Platform is a strong plus."
    assert is_required(text, index) is False


def test_a_heading_makes_everything_under_it_optional():
    """`Nice to have:` -- the sentence below it never repeats the words, so
    the heading has to be consulted."""
    index = LineIndex(POST)
    text = "Experience with Apache Kafka or similar streaming systems."
    assert is_required(text, index) is False


def test_a_heading_above_does_not_leak_onto_earlier_requirements():
    index = LineIndex(POST)
    assert is_required("A Master's Degree or Ph.D. in Computer Science", index) is True


# --- weakly stated -------------------------------------------------------


def test_a_skills_list_is_a_weak_statement():
    assert is_weakly_stated(
        "Docker, Kubernetes, Helm, GitHub Actions, AWS ECR, GCP Secret Manager"
    )


def test_a_sentence_showing_the_work_is_not_weak():
    assert not is_weakly_stated(
        "Rebuilt the ingestion pipeline's concurrency model, cutting peak memory 6.2x."
    )


def test_a_short_list_is_not_a_dump():
    assert not is_weakly_stated("Python, TypeScript")


# --- the summary event ---------------------------------------------------


def build(verdicts: list[dict]) -> dict:
    post_index = LineIndex(POST)
    resume_index = LineIndex(RESUME)
    requirements = [
        requirement("Demonstrable experience building REST APIs (e.g., using Flask, FastAPI) to serve ML models.", 1, post_index),
        requirement("Proficiency with containerization using Docker and Kubernetes (K8s).", 2, post_index),
        requirement("A Master's Degree or Ph.D. in Computer Science or a related quantitative field.", 3, post_index),
        requirement("DataRobot Experience: Familiarity with the DataRobot AI Platform is a strong plus.", 4, post_index),
    ]
    return summarise(requirements, verdicts, resume_index)


def verdict(rid: int, kind: str, line_number: int | None = None) -> dict:
    return {
        "type": "verdict",
        "requirement_id": rid,
        "verdict": kind,
        "line": None,
        "line_number": line_number,
        "reason": "because",
    }


def test_the_summary_carries_all_five_fields():
    summary = build([verdict(1, "evidenced", 3)])
    assert set(summary) == {
        "type", "fit", "fit_reason", "blockers", "strengths", "undersells"
    }
    assert summary["type"] == "summary"


def test_a_missing_required_item_is_a_blocker():
    summary = build([verdict(3, "not_evidenced")])
    assert [b["requirement_id"] for b in summary["blockers"]] == [3]


def test_a_missing_optional_item_is_not_a_blocker():
    """Requirement 4 is `a strong plus`. Missing it changes nothing."""
    summary = build([verdict(4, "not_evidenced")])
    assert summary["blockers"] == []


def test_an_evidenced_requirement_is_a_strength():
    summary = build([verdict(1, "evidenced", 3)])
    assert [s["requirement_id"] for s in summary["strengths"]] == [1]
    assert summary["strengths"][0]["line_number"] == 3


def test_all_three_lists_have_the_same_five_fields():
    """Decision 0006 item 3. Before this, `blockers` carried `text`,
    `strengths` carried a line number and no words, and `undersells` carried
    both plus a reason -- so neither client could render a summary it was
    holding on its own, and brief 0008 invented a fixture to join against."""
    summary = build(
        [verdict(1, "evidenced", 3), verdict(2, "partly_evidenced", 5), verdict(3, "not_evidenced")]
    )
    shape = {"requirement_id", "text", "line", "line_number", "reason"}

    rows = summary["blockers"] + summary["strengths"] + summary["undersells"]
    assert len(rows) == 3, "one of the three lists is empty; this would pass emptily"
    for row in rows:
        assert set(row) == shape


def test_a_blocker_carries_the_requirement_and_no_line():
    """`null` where a field does not apply, rather than a missing key: a
    not_evidenced verdict is settled with no quote by construction."""
    row = build([verdict(3, "not_evidenced")])["blockers"][0]
    assert row["text"] in POST
    assert row["line"] is None and row["line_number"] is None


def test_a_strength_quotes_the_resume_verbatim():
    row = build([verdict(1, "evidenced", 3)])["strengths"][0]
    assert row["line"] in RESUME


def test_undersells_names_evidence_that_is_there_but_stated_weakly():
    """Line 5 of the resume is the Docker/Kubernetes skills row: the evidence
    is genuinely present, and the resume only lists it."""
    summary = build([verdict(2, "partly_evidenced", 5)])
    assert len(summary["undersells"]) == 1
    assert summary["undersells"][0]["requirement_id"] == 2
    assert summary["undersells"][0]["line_number"] == 5
    assert "listed among" in summary["undersells"][0]["reason"]


def test_undersells_is_not_a_synonym_for_partly_evidenced():
    """Line 3 shows the work. Partly evidenced there is a real gap, not a
    wording problem, and telling somebody to reword it would be wrong."""
    summary = build([verdict(1, "partly_evidenced", 3)])
    assert summary["undersells"] == []


def test_undersells_needs_a_line_that_actually_exists():
    summary = build([verdict(2, "partly_evidenced", None)])
    assert summary["undersells"] == []


def test_fit_is_one_of_three_words_and_never_a_number():
    for verdicts in ([], [verdict(1, "evidenced", 3)], [verdict(3, "not_evidenced")]):
        assert build(verdicts)["fit"] in ("strong", "worth_applying", "weak")


def test_three_missing_required_items_is_weak():
    summary = build(
        [verdict(1, "not_evidenced"), verdict(2, "not_evidenced"), verdict(3, "not_evidenced")]
    )
    assert summary["fit"] == "weak"


def test_everything_evidenced_and_nothing_missing_is_strong():
    summary = build(
        [verdict(1, "evidenced", 3), verdict(2, "evidenced", 5), verdict(3, "evidenced", 3)]
    )
    assert summary["fit"] == "strong"


def test_one_missing_required_item_is_not_a_rejection():
    summary = build(
        [verdict(1, "evidenced", 3), verdict(2, "evidenced", 5), verdict(3, "not_evidenced")]
    )
    assert summary["fit"] == "worth_applying"


def test_the_fit_reason_is_a_plain_sentence_with_the_numbers_in_it():
    """Decision 0006 item 6 changed the denominator here from 3 to 4.

    It used to count only the required items while the counts row beside it on
    screen counted all of them -- "1 of 3" next to a row totalling 4. Both
    were defensible and together they read as a bug. The sentence now counts
    every requirement, the same set the counts row shows, and
    required-versus-preferred is left to `blockers`.
    """
    summary = build([verdict(1, "evidenced", 3), verdict(3, "not_evidenced")])
    reason = summary["fit_reason"]
    assert reason.endswith(".")
    assert "1 of 4" in reason
    assert "%" not in reason


def test_the_fit_reason_counts_the_same_requirements_the_counts_row_does():
    """The failure decision 0006 item 6 exists to stop: two denominators on
    one screen. There are four requirements in POST, one of them optional."""
    verdicts = [
        verdict(1, "evidenced", 3),
        verdict(2, "evidenced", 5),
        verdict(3, "not_evidenced"),
        verdict(4, "evidenced", 3),
    ]
    summary = build(verdicts)
    assert f"{len(verdicts)}" in summary["fit_reason"]
    assert "3 of 4" in summary["fit_reason"]


def test_fit_still_weighs_only_the_required_items():
    """The sentence's denominator moved; the judgement's did not. Missing an
    optional extra is not evidence against applying."""
    summary = build(
        [verdict(1, "evidenced", 3), verdict(2, "evidenced", 5), verdict(3, "evidenced", 3),
         verdict(4, "not_evidenced")]
    )
    assert summary["fit"] == "strong"
    assert summary["blockers"] == []


# --- the wording rule (decision 0008 item 4) -----------------------------

# `design/README.md`: "Never use 'evidence' as a verb." The three spellings a
# verb takes. "evidence" the NOUN is not in this list on purpose -- the ban is
# on the verb, and a test that also failed the noun would be testing a rule
# nobody wrote.
EVIDENCE_AS_A_VERB = ("evidenced", "evidencing", "evidence in", "evidence this")


def every_fit_sentence() -> list[str]:
    """Every sentence `_fit_sentence` can produce: three leads by three tails.

    Enumerated rather than read off one run, because the failure this guards
    is one branch keeping the old wording while the others change. A single
    real run exercises exactly one of these nine.
    """
    from audit.product import _fit_sentence

    # Requirement text is ours, not a post's. A real post may itself contain
    # the word, and the rule is about what WE write.
    blockers = [
        {"text": "Kubernetes in production"},
        {"text": "A Master's degree"},
        {"text": "Five years of Go"},
    ]
    return [
        _fit_sentence(fit, shown, 23, blockers[:n])
        for fit in ("strong", "worth_applying", "weak")
        for n in (0, 1, 3)
        for shown in (0, 8)
    ]


def test_no_fit_sentence_uses_evidence_as_a_verb():
    sentences = every_fit_sentence()
    assert len(sentences) == 18, "the branches were not all reached"
    for sentence in sentences:
        low = sentence.lower()
        for banned in EVIDENCE_AS_A_VERB:
            assert banned not in low, f"{banned!r} in {sentence!r}"


def test_every_fit_sentence_says_what_the_resume_shows():
    """The register `design/README.md` sets: "your resume shows this"."""
    for sentence in every_fit_sentence():
        assert "your resume shows" in sentence.lower()
        assert sentence.endswith(".")


def test_the_real_fit_reason_goes_through_the_same_rule():
    """The sentence as `summarise` actually builds it, not as a helper can be
    called directly -- so this cannot pass while the real path differs."""
    summary = build([verdict(1, "evidenced", 3), verdict(3, "not_evidenced")])
    low = summary["fit_reason"].lower()
    for banned in EVIDENCE_AS_A_VERB:
        assert banned not in low
    assert "your resume shows 1 of 4" in low

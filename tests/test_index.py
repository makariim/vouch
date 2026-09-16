"""The retrieval tool. Every guarantee above it rests on these behaviours."""

from __future__ import annotations

from audit.index import LineIndex

RESUME = """Alex Carter

Built and operated REST APIs in Python serving 2M requests a day.
Designed the SQL schema for the ledger service.
"""


def test_line_numbers_follow_the_original_file():
    index = LineIndex(RESUME)
    assert [line.number for line in index.lines] == [1, 3, 4]
    assert index.get(3).text.startswith("Built and operated REST APIs")
    assert index.get(2) is None  # blank line, skipped but not renumbered


def test_search_finds_the_relevant_line():
    index = LineIndex(RESUME)
    hits = index.search("python rest apis")
    assert hits
    assert "REST APIs in Python" in hits[0].text


def test_search_returns_nothing_for_unrelated_terms():
    index = LineIndex(RESUME)
    assert index.search("chocolate tempering pastry") == []


def test_search_on_stopwords_only_returns_nothing():
    """Otherwise 'experience with' would match every line in the file."""
    assert LineIndex(RESUME).search("experience with the") == []


def test_contains_verbatim_is_character_for_character():
    index = LineIndex(RESUME)
    assert index.contains_verbatim("Designed the SQL schema for the ledger service.")
    assert not index.contains_verbatim("Designed the SQL schemas for the ledger service.")
    assert not index.contains_verbatim("")


def test_locate_returns_the_source_wording_not_the_query():
    post = "We want:\n- 5+ years of\n  professional Python experience\n"
    index = LineIndex(post)

    # A hard-wrapped requirement is not a literal substring, but it is really
    # there. locate() finds it and hands back the post's own characters.
    found = index.locate("5+ years of professional Python experience")
    assert found is not None
    assert found in post
    assert found == "5+ years of\n  professional Python experience"


def test_locate_refuses_text_that_is_not_there():
    index = LineIndex(RESUME)
    assert index.locate("ten years of Kubernetes") is None
    assert index.locate("   ") is None

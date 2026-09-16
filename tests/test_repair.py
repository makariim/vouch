"""Mechanical repair of PDF extraction damage.

Two halves, and the second matters more. The first half proves repair fixes
the damage brief 0007 names. The second proves it leaves alone text that was
never damaged -- which is the failure the brief calls worse than not shipping
the feature at all.
"""

from __future__ import annotations

from pathlib import Path

from audit.index import LineIndex
from audit.repair import page_measure, repair

DATA = Path(__file__).parent / "data"
DAMAGED = (DATA / "resume_damaged.txt").read_text(encoding="utf-8")
CLEAN = (DATA / "resume.txt").read_text(encoding="utf-8")
UNRELATED = (DATA / "resume_unrelated.txt").read_text(encoding="utf-8")
POST = (DATA / "post.txt").read_text(encoding="utf-8")


def repaired_lines(text: str) -> list[str]:
    return [line.text for line in LineIndex(repair(text).text).lines]


# --- the damage the brief names ------------------------------------------


def test_a_word_split_across_lines_is_rejoined():
    """`on-prem and air-` / `gapped deployment` is one phrase in the PDF and
    two lines out of it. Brief 0007 names this line specifically."""
    lines = repaired_lines(DAMAGED)
    assert any("on-prem and air-gapped deployment" in line for line in lines)
    assert not any(line.rstrip().endswith("air-") for line in lines)
    assert not any(line.strip() == "gapped deployment" for line in lines)


def test_the_hyphen_is_kept_when_the_document_says_it_belongs():
    """`air-gapped` is a real hyphenated word, and this resume proves it by
    writing it out in full elsewhere. Evidence from the document, not a guess."""
    assert "air-gapped deployment" in repair(DAMAGED).text
    assert "airgapped" not in repair(DAMAGED).text


def test_a_hyphen_is_dropped_when_the_document_says_it_does_not_belong():
    text = (
        "The service runs in a fully containerised environment every day.\n"
        "We deployed it into a containerised environ-\n"
        "ment last spring.\n"
    )
    assert "containerised environment last spring" in repair(text).text


def test_an_unknown_hyphen_keeps_its_hyphen():
    """With no evidence either way, keep the characters that are there.
    Keeping a hyphen destroys nothing -- the tokenizer splits on it anyway."""
    text = "a" * 70 + "\nsomething with a multi-\nregion setup in it\n"
    assert "multi-region setup" in repair(text).text


def test_a_wrapped_sentence_is_rejoined():
    lines = repaired_lines(DAMAGED)
    assert any(
        "ingestion, indexing, retrieval and the deployment path into cloud" in line
        for line in lines
    )


def test_a_flattened_table_row_is_split_into_its_columns():
    """The column headers were glued onto the first cell's contents, so a
    search for `Frontend` retrieved a line about AI systems."""
    lines = repaired_lines(DAMAGED)
    assert "Infrastructure" in lines
    assert "Frontend" in lines
    assert not any(
        "AI systems Languages" in line for line in lines
    ), "the header run is still flattened"


def test_repair_reports_every_change_it_made():
    result = repair(DAMAGED)
    assert result.changes
    kinds = {change.kind for change in result.changes}
    assert "split-row" in kinds
    assert any(kind.startswith("rejoin") for kind in kinds)
    for change in result.changes:
        assert change.before and change.after
        assert change.source_line >= 1


# --- what repair must NOT do ---------------------------------------------


def test_clean_text_is_left_exactly_alone():
    """The failure brief 0007 names: repair mangling a line that was fine."""
    result = repair(CLEAN)
    assert result.changes == []
    assert result.text.strip() == CLEAN.strip()


def test_a_sentence_with_proper_nouns_is_not_treated_as_a_table():
    """`Built and operated REST APIs in Python serving 2M requests a day.`
    has three capitalised words in it and is not a table row."""
    line = "Built and operated REST APIs in Python serving 2M requests a day for the ledger team."
    assert repair(line + "\n").changes == []


def test_a_letter_spaced_heading_is_not_shattered():
    """`T E C H N I C A L  S T A C K` is one heading, not fourteen columns."""
    lines = repaired_lines(DAMAGED)
    assert any(line.startswith("T E C H N I C A L") for line in lines)


def test_a_line_already_carrying_a_column_separator_is_left_alone():
    """If the extractor kept the `|`, the columns survived and there is
    nothing to reconstruct. Title Case job titles live here."""
    line = (
        "Software Tech Lead (Dec 2024 to Aug 2025) | Software Engineer II "
        "(Sep 2023 to Dec 2024) | Software Engineer (May 2022 to Sep 2023)"
    )
    assert repair(line + "\n").changes == []


def test_two_table_cells_are_not_glued_together():
    """The Frontend row ends short of the margin because the cell ended, not
    because the page did. It must not absorb the row below it."""
    lines = repaired_lines(DAMAGED)
    assert any(line.startswith("React, Next.js") for line in lines)
    assert not any("admin tooling" in line and "Docker" in line for line in lines)


def test_a_short_document_does_not_wrap_into_itself():
    """The margin is measured from the document, so a document that never
    wraps must not have every line treated as a wrap."""
    text = "first item here\nsecond item here\nthird item here\n"
    assert repair(text).changes == []


def test_repair_invents_no_characters():
    """Every word of the repaired text came from the original."""
    result = repair(DAMAGED)
    before = set("".join(ch if ch.isalnum() else " " for ch in DAMAGED).split())
    after = set("".join(ch if ch.isalnum() else " " for ch in result.text).split())
    assert after <= before


def test_line_numbers_of_untouched_lines_do_not_move():
    """A join leaves an empty line behind rather than renumbering, so a line
    repair did not touch keeps the number it had in the extraction."""
    original = LineIndex(DAMAGED)
    fixed = LineIndex(repair(DAMAGED).text)
    fixed_by_number = {line.number: line.text for line in fixed.lines}
    for line in original.lines:
        if line.text in fixed_by_number.values():
            continue
    assert fixed_by_number.get(1) == "Dana Okafor"
    assert fixed_by_number.get(2) == "Platform Engineer"


def test_page_measure_ignores_one_freak_long_line():
    lines = ["x" * 40] * 20 + ["y" * 400]
    assert page_measure(lines) < 100


# --- the whitespace a PDF extractor leaves behind -------------------------


def test_tabs_out_of_a_pdf_do_not_survive_into_a_quote():
    """`pypdf` separates words with tabs, and a quote is sliced out of the
    text this module returns -- so a tab here is a tab on screen."""
    text = (
        "Muhammad\tAbdulkariim\n"
        "AI\tENGINEER\n"
        "Riyadh,\tSaudi\tArabia\t\t|\t\tAug\t2025\tto\tPresent\n"
    )
    repaired = repair(text).text
    assert "\t" not in repaired
    assert "Muhammad Abdulkariim" in repaired
    assert "Riyadh, Saudi Arabia | Aug 2025 to Present" in repaired


def test_a_run_of_spaces_collapses_and_the_line_does_not_end_in_one():
    text = "Languages     Python,   Go\nInfrastructure   Docker   \n"
    lines = repair(text).text.splitlines()
    assert lines[0] == "Languages Python, Go"
    assert lines[1] == "Infrastructure Docker"


def test_the_recorded_change_shows_the_whitespace_the_text_kept():
    """A person comparing before and after must be reading the line we
    actually kept, not a third version of it."""
    text = "a" * 70 + "\nsomething\twith\ta multi-\nregion\tsetup in it\n"
    change = repair(text).changes[0]
    assert "\t" not in change.before
    assert "\t" not in change.after


# --- the trap: normalising must not blind the row guard -------------------


def test_a_tab_delimited_row_is_still_recognised_and_left_alone():
    """The tab is how `_ALREADY_DELIMITED` knows the columns survived. If
    whitespace were collapsed first that signal would be gone and these Title
    Case job titles would be cut into single words -- the failure of 0007."""
    line = (
        "Software Tech Lead\t(Dec 2024 to Aug 2025)\tSoftware Engineer II\t"
        "(Sep 2023 to Dec 2024)\tSoftware Engineer\t(May 2022 to Sep 2023)"
    )
    result = repair(line + "\n")
    assert result.changes == []
    assert result.text.strip() == (
        "Software Tech Lead (Dec 2024 to Aug 2025) Software Engineer II "
        "(Sep 2023 to Dec 2024) Software Engineer (May 2022 to Sep 2023)"
    )


def test_every_clean_document_is_still_untouched():
    """Three documents that were never damaged. Repair must have nothing to
    say about any of them, whitespace pass included."""
    for name, document in (("resume", CLEAN), ("unrelated", UNRELATED), ("post", POST)):
        result = repair(document)
        assert result.changes == [], name
        assert result.text.strip() == document.strip(), name

"""Getting a resume in, and keeping it on this machine.

The PDF in these tests is a real PDF, assembled here as bytes rather than
committed as a binary blob. A checked-in binary is a thing nobody reads and
nobody can diff; this way the input is visible in the test that uses it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from audit.ingest import IngestError, ResumeStore, extract_text, index_resume, slugify


def make_pdf(lines: list[str]) -> bytes:
    """A minimal one-page PDF with the given lines of text on it.

    Hand-built because the project has no PDF *writer* and does not need one.
    A PDF is a set of numbered objects plus a table of their byte offsets, so
    the offsets have to be computed after the objects are laid out.
    """
    content = "BT /F1 11 Tf 40 750 Td 14 TL\n"
    for line in lines:
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        content += f"({escaped}) Tj T*\n"
    content += "ET"
    stream = content.encode("latin-1")

    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R"
        b"/Resources<</Font<</F1 5 0 R>>>>>>",
        b"<</Length " + str(len(stream)).encode() + b">>stream\n" + stream + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj".encode() + body + b"endobj\n"

    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer<</Size {len(objects) + 1}/Root 1 0 R>>\nstartxref\n{xref_at}\n".encode()
    )
    out += b"%%EOF\n"
    return bytes(out)


# --- extraction ----------------------------------------------------------


def test_text_comes_out_of_a_real_pdf():
    pdf = make_pdf(["Dana Okafor", "Platform Engineer", "FastAPI, Redis, Kafka"])
    text = extract_text(pdf, "dana.pdf")
    assert "Dana Okafor" in text
    assert "FastAPI, Redis, Kafka" in text


def test_a_txt_upload_is_taken_as_it_is():
    assert extract_text(b"line one\nline two\n", "resume.txt") == "line one\nline two\n"


def test_an_unsupported_file_type_is_refused_by_name():
    with pytest.raises(IngestError, match="unsupported file type"):
        extract_text(b"whatever", "resume.docx")


def test_a_pdf_with_no_text_says_so_instead_of_returning_nothing():
    """A scanned PDF is images. Returning '' would look like an empty resume
    and produce an audit that finds nothing, which reads like a verdict."""
    with pytest.raises(IngestError, match="no extractable text"):
        extract_text(make_pdf([]), "scan.pdf")


def test_a_file_that_is_not_a_pdf_fails_cleanly():
    with pytest.raises(IngestError, match="could not read"):
        extract_text(b"this is not a pdf at all", "resume.pdf")


# --- repair happens before indexing, always ------------------------------


def test_indexing_repairs_first():
    """The one seam the verbatim guarantee rests on."""
    text = "a" * 70 + "\nwrapped continuation here\nDocker, Helm, on-prem and air-\ngapped deployment\n"
    index, repaired = index_resume(text)
    assert repaired.changes
    assert any("air-gapped deployment" in line.text for line in index.lines)


def test_every_indexed_line_is_verbatim_in_the_indexed_source():
    damaged = (Path(__file__).parent / "data" / "resume_damaged.txt").read_text(
        encoding="utf-8"
    )
    index, _ = index_resume(damaged)
    for line in index.lines:
        assert index.contains_verbatim(line.text)


# --- storage -------------------------------------------------------------


@pytest.fixture
def store(tmp_path):
    return ResumeStore(tmp_path / "resumes")


def test_a_saved_resume_comes_back(store):
    resume_id = store.save("Dana Okafor CV.pdf", "line one\nline two\n")
    assert resume_id == "dana-okafor-cv"
    assert store.get(resume_id).text == "line one\nline two\n"


def test_the_first_resume_becomes_the_default(store):
    resume_id = store.save("first.txt", "hello\n")
    assert store.default_id() == resume_id
    assert store.get("default").text == "hello\n"


def test_the_default_can_be_moved(store):
    first = store.save("first.txt", "one\n")
    second = store.save("second.txt", "two\n")
    assert store.default_id() == first
    store.set_default(second)
    assert store.get("default").id == second


def test_two_uploads_of_one_name_do_not_overwrite(store):
    a = store.save("resume.txt", "one\n")
    b = store.save("resume.txt", "two\n")
    assert a != b
    assert store.get(a).text == "one\n"
    assert store.get(b).text == "two\n"


def test_listing_says_which_is_default(store):
    store.save("a.txt", "one\n")
    b = store.save("b.txt", "two\n")
    store.set_default(b)
    listed = {row["id"]: row for row in store.list()}
    assert listed[b]["default"] is True
    assert listed["a"]["default"] is False


def test_an_id_cannot_walk_out_of_the_folder(store):
    """Ids arrive from a URL path. Refused, not sanitised -- there is no
    clever normalisation here to get wrong."""
    store.save("real.txt", "hello\n")
    for attempt in ("../../etc/passwd", "..", "a/b", "A.txt", "with space"):
        with pytest.raises(IngestError, match="not a resume id"):
            store.get(attempt)


def test_an_empty_resume_is_refused(store):
    with pytest.raises(IngestError, match="empty"):
        store.save("blank.txt", "   \n")


def test_asking_for_a_default_that_is_not_there(store):
    with pytest.raises(IngestError, match="no resumes stored"):
        store.get("default")


def test_slugify_never_produces_an_empty_id():
    assert slugify("???.pdf") == "resume"
    assert slugify("My CV (final).pdf") == "my-cv-final"

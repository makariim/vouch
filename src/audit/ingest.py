"""Getting a resume into the tool, and keeping it on this machine.

Decision 0005 adds stored resumes. Decision 0002 still governs what "stored"
is allowed to mean: plain files in a folder on the user's own disk, no
database, no upload, nothing that leaves. A folder you can open in Finder and
delete by hand is a privacy promise a person can check for themselves, which
is worth more than a sentence in a README.

WHICH PDF LIBRARY, AND WHY
--------------------------
`pdfplumber`. A PDF holds drawing instructions, not text, so pulling text out
means choosing an order. `pypdf` uses the order the instructions sit in the
file -- which is the order the design tool wrote them, and on a resume laid out
as rows of left-hand title and right-hand dates that is not the order a person
reads. The author's own resume came out with his name on line 6, underneath two
employers, and a line beginning with a stray comma. Nothing was missing; it was
all there in the wrong order.

`pdfplumber` keeps the position of every character on the page, so the text can
be ordered the way a person reads it: top to bottom, then left to right. That
ordering is the whole reason it is here. Report 0007 predicted this before any
PDF existed and called it "the one to revisit".

  pypdf     still declared, and still used -- but only as a fallback, below.
  PyMuPDF   the best extraction of the three, and AGPL. This code goes in a
            public GitHub repository for an interview. Not worth the licence
            conversation.

WHY pypdf IS STILL HERE
-----------------------
pdfminer, underneath pdfplumber, is the stricter parser of the two. It refuses
files pypdf reads: a PDF whose objects run `>>endobj` together with no
delimiter is malformed, and pdfminer rejects it outright where pypdf shrugs and
carries on. This project's own hand-built test PDF was exactly such a file.

So pypdf is the fallback, and only the fallback. In front of a demo, text in
the wrong order beats no text at all -- but a fallback that fires silently
would hand back shuffled text while the product claims to have fixed that, so
it says so in the log when it fires.

Ordering is still only ever positional. Neither reader moves a line on a guess,
and neither ever changes a word. `repair` runs after this and is unchanged: it
joins lines broken mid-sentence and splits glued rows, and it still never moves
a line. The flattened row survives extraction on purpose, because repairing it
mechanically is a thing we can show working.
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

from .index import LineIndex
from .repair import Repair, repair

# An id becomes a file name and arrives from a URL path. Anything outside this
# alphabet is refused rather than cleaned, so there is no clever normalisation
# to get wrong and no way to walk out of the folder.
_ID_OK = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SLUG_STRIP = re.compile(r"[^a-z0-9]+")

_log = logging.getLogger(__name__)

DEFAULT_ROOT = Path("resumes")
DEFAULT_POINTER = "default"


class IngestError(Exception):
    """A resume we will not accept. Never a stack trace in front of a demo."""


def _pdf_text_in_reading_order(data: bytes) -> str:
    """Every page's text, ordered by where the characters actually sit.

    pdfplumber hands back each page's characters with their coordinates and
    orders them top to bottom, then left to right. That is the only ordering
    rule here, and it comes from the file rather than from a guess about what
    belongs where.

    The tolerances are left at their defaults on purpose. Tuning them would be
    tuning against one resume, and the next file would be the one that broke.
    """
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _pdf_text_in_file_order(data: bytes) -> str:
    """The fallback: pypdf, which reads some malformed files pdfminer refuses.

    The order is whatever order the drawing instructions sit in the file, so
    this can be shuffled. It is still better than a dead end in front of a
    demo -- but only just, which is why the caller says so in the log.
    """
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text(data: bytes, filename: str) -> str:
    """Text out of an uploaded .pdf or .txt. No repair yet -- that is separate
    on purpose, so what the library produced can be shown next to what we made
    of it."""
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IngestError(f"{filename} is not UTF-8 text: {exc}") from exc

    if suffix != ".pdf":
        raise IngestError(f"unsupported file type {suffix or '(none)'}: upload .pdf or .txt")

    # Both readers get a go, and only the four calm messages ever come out.
    # pdfplumber first because it is the one that gets the order right; pypdf
    # only if pdfplumber produced nothing at all, whether by raising or by
    # handing back an empty page.
    try:
        text = _pdf_text_in_reading_order(data)
        first_error: Exception | None = None
    except Exception as exc:
        text, first_error = "", exc

    if not text.strip():
        try:
            fallback = _pdf_text_in_file_order(data)
        except Exception as exc:
            raise IngestError(
                f"could not read {filename} as a PDF: {first_error or exc}"
            ) from (first_error or exc)
        if fallback.strip():
            _log.warning(
                "%s: pdfplumber read nothing (%s); fell back to pypdf, so the "
                "line order is the order the file was written in, not reading "
                "order.",
                filename,
                first_error or "no text on any page",
            )
            text = fallback

    if not text.strip():
        # Neither reader found a character. A scanned PDF is images, and
        # returning "" would look like an empty resume and produce an audit
        # that finds nothing, which reads like a verdict.
        raise IngestError(
            f"{filename} has no extractable text. A scanned PDF needs OCR, "
            "which this tool does not do -- paste the text instead."
        )
    return text


def index_resume(text: str) -> tuple[LineIndex, Repair]:
    """Repair, then index. Always in that order, and always through here.

    This is the single seam the verbatim guarantee depends on. Quotes are
    sliced out of the index, and the index is built from the repaired text, so
    a quote can only ever be a line the repaired document really contains. If
    some other caller indexed the raw text instead, the numbers a human reads
    in `GET /resumes/{id}` would stop meaning the same thing as the numbers in
    a verdict. One function, both callers.
    """
    repaired = repair(text)
    return LineIndex(repaired.text), repaired


def slugify(name: str) -> str:
    stem = _SLUG_STRIP.sub("-", Path(name).stem.lower()).strip("-")
    return (stem or "resume")[:48]


@dataclass(frozen=True)
class StoredResume:
    id: str
    name: str
    text: str
    is_default: bool


class ResumeStore:
    """Resumes as files in one folder. `default` is a file holding an id."""

    def __init__(self, root: Path | str = DEFAULT_ROOT) -> None:
        self.root = Path(root)

    def _path(self, resume_id: str) -> Path:
        if not _ID_OK.match(resume_id):
            raise IngestError(f"not a resume id: {resume_id!r}")
        return self.root / f"{resume_id}.txt"

    def _pointer(self) -> Path:
        return self.root / DEFAULT_POINTER

    def save(self, name: str, text: str) -> str:
        """Store the extracted text under an id derived from the file name.

        The raw extracted text is what goes on disk, not the repaired version.
        Repair is a view, applied at index time, so it can be changed later
        without the stored file having quietly baked in an older version of it.
        """
        if not text.strip():
            raise IngestError("that resume is empty")

        self.root.mkdir(parents=True, exist_ok=True)
        base = slugify(name)
        resume_id, n = base, 2
        while self._path(resume_id).exists():
            resume_id = f"{base}-{n}"
            n += 1

        self._path(resume_id).write_text(text, encoding="utf-8")
        if not self._pointer().exists():
            self.set_default(resume_id)  # the first resume is the default
        return resume_id

    def get(self, resume_id: str) -> StoredResume:
        resume_id = self.resolve(resume_id)
        path = self._path(resume_id)
        if not path.is_file():
            raise IngestError(f"no resume {resume_id!r}")
        return StoredResume(
            id=resume_id,
            name=path.name,
            text=path.read_text(encoding="utf-8"),
            is_default=resume_id == self.default_id(),
        )

    def resolve(self, resume_id: str) -> str:
        """`default` is a name for whichever resume is current."""
        if resume_id in ("", DEFAULT_POINTER):
            current = self.default_id()
            if current is None:
                raise IngestError("no resumes stored yet")
            return current
        return resume_id

    def default_id(self) -> str | None:
        pointer = self._pointer()
        if not pointer.is_file():
            return None
        value = pointer.read_text(encoding="utf-8").strip()
        return value if value and self._path(value).is_file() else None

    def set_default(self, resume_id: str) -> None:
        if not self._path(resume_id).is_file():
            raise IngestError(f"no resume {resume_id!r}")
        self.root.mkdir(parents=True, exist_ok=True)
        self._pointer().write_text(resume_id, encoding="utf-8")

    def list(self) -> list[dict]:
        if not self.root.is_dir():
            return []
        current = self.default_id()
        out = []
        for path in sorted(self.root.glob("*.txt")):
            resume_id = path.stem
            out.append(
                {
                    "id": resume_id,
                    # Decision 0008. The panel promises to say what it checked
                    # you against and could only show the id. This is the file
                    # on disk, the same string `get()` already reports, so the
                    # list and the single resume cannot disagree.
                    #
                    # It is NOT the name the file was uploaded under: `save()`
                    # slugifies that into the id and keeps nothing else, so the
                    # original is genuinely gone. The brief says "the id where
                    # there is nothing better", and there is nothing better
                    # without a sidecar file, which this wave is not opening.
                    "name": path.name,
                    "lines": len(LineIndex(path.read_text(encoding="utf-8"))),
                    "default": resume_id == current,
                }
            )
        return out

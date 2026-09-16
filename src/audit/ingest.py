"""Getting a resume into the tool, and keeping it on this machine.

Decision 0005 adds stored resumes. Decision 0002 still governs what "stored"
is allowed to mean: plain files in a folder on the user's own disk, no
database, no upload, nothing that leaves. A folder you can open in Finder and
delete by hand is a privacy promise a person can check for themselves, which
is worth more than a sentence in a README.

WHICH PDF LIBRARY, AND WHY
--------------------------
`pypdf`. Pure Python, BSD-3, no native build step, no system packages, and it
is the maintained continuation of PyPDF2 so it is the thing most environments
already resolve to.

The two alternatives were both rejected on this project's constraints:

  pdfplumber  better at tables, because it keeps glyph coordinates and can
              reconstruct columns. It also pulls in pdfminer.six and is
              markedly slower. Worth revisiting -- see the report.
  PyMuPDF     the best extraction of the three, and AGPL. This code goes in a
              public GitHub repository for an interview. Not worth the licence
              conversation.

pypdf gives us damaged text: a word split at a line break stays split, and a
table row comes out flattened. That damage is exactly what `repair` exists to
undo, and repairing it mechanically is a thing we can show working. A library
that hid the problem would have left us nothing to demonstrate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .index import LineIndex
from .repair import Repair, repair

# An id becomes a file name and arrives from a URL path. Anything outside this
# alphabet is refused rather than cleaned, so there is no clever normalisation
# to get wrong and no way to walk out of the folder.
_ID_OK = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SLUG_STRIP = re.compile(r"[^a-z0-9]+")

DEFAULT_ROOT = Path("resumes")
DEFAULT_POINTER = "default"


class IngestError(Exception):
    """A resume we will not accept. Never a stack trace in front of a demo."""


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

    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise IngestError("pypdf is not installed") from exc

    import io

    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise IngestError(f"could not read {filename} as a PDF: {exc}") from exc

    text = "\n".join(pages)
    if not text.strip():
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

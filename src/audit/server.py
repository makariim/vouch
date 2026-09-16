"""The HTTP layer. Exactly what decisions 0004 and 0005 specify, nothing more.

    GET  /                       the page  (owned by brief 0002 -- served, never written)
    POST /audit                  {"post":..., "resume"|"resume_id":...} -> text/event-stream
    POST /audit/requirement      the same stream, for one requirement       (0006)
    POST /summary                {"post":..., "resume_id":...}  -> a stored summary (0006)
    POST /prescreen              {"post":..., "resume_id":...}  -> JSON, no model call
    GET  /resumes                list
    POST /resumes                upload .pdf or .txt, returns an id
    GET  /resumes/{id}           the indexed lines, numbered
    POST /resumes/{id}/default   make it the default

ROUTE ORDER MATTERS HERE. The last route is a catch-all that serves the page's
own CSS and JS, and FastAPI matches in the order routes are declared. Every
real endpoint is therefore declared above it; move one below and it silently
becomes a request for a file named `prescreen`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from . import events as ev
from .graph import run_stream
from .index import LineIndex
from .ingest import DEFAULT_ROOT, IngestError, ResumeStore, extract_text, index_resume
from .model import Model, build_model
from .prescreen import prescreen as run_prescreen
from .store import AuditStore

# Brief 0002 owns everything in here -- index.html, styles.css, app.js. This
# module reads that folder and never writes to it.
FRONTEND_DIR = Path(os.environ.get("AUDIT_FRONTEND", "web"))
RESUME_DIR = Path(os.environ.get("AUDIT_RESUMES", str(DEFAULT_ROOT)))

_WAITING = """<!doctype html>
<meta charset="utf-8"><title>Vouch</title>
<body style="font:16px system-ui;padding:3rem;max-width:40rem">
<h1>Backend is up.</h1>
<p>No page found in <code>{folder}</code>. Brief 0002 owns that file;
this server only serves it.</p>
<p><code>POST /audit</code> is live and streaming.</p>
"""


class AuditRequest(BaseModel):
    post: str = ""
    resume: str = ""
    resume_id: str = ""


class PrescreenRequest(BaseModel):
    post: str = ""
    resume: str = ""
    resume_id: str = "default"


class SummaryRequest(BaseModel):
    """Decision 0006: the panel asking what it already knows about this post."""

    post: str = ""
    resume_id: str = "default"


class RequirementRequest(BaseModel):
    """Decision 0006: a person asking for a second pass over one requirement.

    Not a retry. Decision 0007 is explicit that the agent deciding mid-run and
    a person pressing a control are two different things, and this is the
    second one -- nothing in this file, in the events it produces, or in the
    graph calls it a retry.
    """

    post: str = ""
    resume: str = ""
    resume_id: str = ""
    requirement_id: int = 0


def sse(event: dict) -> str:
    """One contract event as one SSE frame.

    A browser's EventSource splits on a blank line, so every frame must end
    with two newlines, and the JSON must not contain a raw newline.
    """
    return f"data: {json.dumps(event)}\n\n"


def create_app(
    model: Model | None = None,
    resumes: ResumeStore | None = None,
    audits: AuditStore | None = None,
) -> FastAPI:
    """The model and both stores are injectable so tests can drive the real
    endpoints without a key, a network call, or a folder outside the test."""
    app = FastAPI(title="Vouch audit")
    store = resumes or ResumeStore(RESUME_DIR)
    remembered = audits or AuditStore(store.root)

    def _resume_for(inline: str, resume_id: str) -> tuple[str, str]:
        """The resume text, and the id it is filed under -- or "" for text
        that was pasted rather than stored.

        A stored audit is keyed on that id, so an audit of pasted text has no
        key and is not remembered. That is the honest outcome rather than a
        gap: two different pastes are two different documents and there is
        nothing here that can tell them apart.
        """
        if resume_id.strip():
            stored = store.get(resume_id)
            return stored.text, stored.id
        return inline, ""

    def _resume_text(inline: str, resume_id: str) -> str:
        """Inline text, or a stored id. Decision 0005: the page may keep
        pasting, the extension will not.

        An id is only consulted when one was actually sent. A request with an
        empty `resume` and no id is a request with no resume in it, and it has
        to keep failing with `resume is empty` rather than quietly auditing
        whichever resume happens to be the default -- silently auditing the
        wrong document is a worse outcome than an error.
        """
        if resume_id.strip():
            return store.get(resume_id).text
        return inline

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        for name in ("index.html", "audit.html"):
            page = FRONTEND_DIR / name
            if page.is_file():
                return HTMLResponse(page.read_text(encoding="utf-8"))
        return HTMLResponse(_WAITING.format(folder=FRONTEND_DIR), status_code=200)

    def _merged(known: list[dict] | None, arriving: list[dict]) -> list[dict]:
        """The stored requirement list with the arriving rows written over it.

        Order comes from the stored list, because that is the order the post
        was read in and the order both clients already drew. A row that is not
        in the stored list is appended rather than dropped -- that cannot
        happen today, and silently losing a requirement is the worse failure.
        """
        if not known:
            return arriving
        replacing = {item["id"]: item for item in arriving}
        out = [replacing.pop(item["id"], item) for item in known]
        return out + [item for item in arriving if item["id"] in replacing]

    def _streamed(
        events: Iterator[dict],
        post: str,
        resume_id: str,
        known: list[dict] | None = None,
    ) -> Iterator[str]:
        """Send every event on, and keep the finished audit on the way past.

        The audit is assembled from the events rather than from graph state,
        because the events are the thing both clients already agree on. If a
        run ends in an `error`, or never reaches `summary`, nothing is stored
        -- a half-finished audit read back later would be indistinguishable
        from a complete one.

        `known` is the requirement list already on file, and it is only passed
        by the second-pass endpoint. A second pass emits a `requirements` event
        holding ONE item -- the requirement being redone -- because that is
        what the client needs to redraw. Taking that event as the audit's
        requirement list shrank the stored list from every requirement to one,
        which quietly broke two things: a third pass could not find its
        requirement in a list of one, and (found by this brief) `POST /summary`
        would hand the panel a one-item list of everything the post asks for.
        Merging by id keeps the stored list whole and lets the new item replace
        its own row. Nothing is recomputed -- both sides are events that were
        already produced.
        """
        requirements: list[dict] = []
        verdicts: list[dict] = []
        counts: dict | None = None
        summary: dict | None = None
        failed = False

        try:
            for event in events:
                kind = event.get("type")
                if kind == "requirements":
                    requirements = _merged(known, event["items"])
                elif kind == "verdict":
                    verdicts.append(event)
                elif kind == "done":
                    counts = event["counts"]
                elif kind == "summary":
                    summary = event
                elif kind == "error":
                    failed = True
                yield sse(event)
        except Exception as exc:  # never end a demo on a broken pipe
            yield sse(ev.error_event(f"{type(exc).__name__}: {exc}"))
            return

        if failed or summary is None or counts is None or not resume_id:
            return
        try:
            remembered.save(post, resume_id, requirements, verdicts, counts, summary)
        except OSError:
            # Remembering is a convenience. A disk that will not take the file
            # must not turn a finished audit into a failed request.
            pass

    def _event_stream(events: Iterator[str]) -> StreamingResponse:
        return StreamingResponse(
            events,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/audit")
    def audit(request: AuditRequest) -> StreamingResponse:
        engine = model or build_model()

        def stream() -> Iterator[str]:
            try:
                resume, resume_id = _resume_for(request.resume, request.resume_id)
            except IngestError as exc:
                yield sse(ev.error_event(str(exc)))
                return
            yield from _streamed(
                run_stream(engine, request.post, resume), request.post, resume_id
            )

        return _event_stream(stream())

    @app.post("/audit/requirement")
    def audit_requirement(request: RequirementRequest) -> StreamingResponse:
        """A second pass over one requirement, decision 0006.

        Every earlier verdict is handed back to the graph, so the `summary`
        this ends with is computed over the whole audit with one verdict
        replaced -- not over the single requirement that was re-run. Without
        that, the fit call, the blockers and the undersells would go stale the
        moment a verdict changed, and the page would be left either lying or
        apologising.
        """
        engine = model or build_model()

        def stream() -> Iterator[str]:
            try:
                resume, resume_id = _resume_for(request.resume, request.resume_id)
            except IngestError as exc:
                yield sse(ev.error_event(str(exc)))
                return
            if request.requirement_id <= 0:
                yield sse(ev.error_event("requirement_id is required"))
                return

            earlier = remembered.get(request.post, resume_id) if resume_id else None
            requirements = earlier["requirements"] if earlier else None
            kept = (
                [
                    v
                    for v in earlier["verdicts"]
                    if v["requirement_id"] != request.requirement_id
                ]
                if earlier
                else None
            )

            yield from _streamed(
                run_stream(
                    engine,
                    request.post,
                    resume,
                    requirements=requirements,
                    verdicts=kept,
                    only_id=request.requirement_id,
                ),
                request.post,
                resume_id,
                known=requirements,
            )

        return _event_stream(stream())

    @app.post("/summary")
    def summary(request: SummaryRequest):
        """What the backend already knows about this post, or that it does not.

        No model is constructed and none is called, the same as `/prescreen`:
        this is a file read. That is what makes it usable on every panel open.
        """
        try:
            _, resume_id = _resume_for("", request.resume_id or "default")
        except IngestError:
            # An id we cannot resolve is not an error here. The caller asked
            # whether we know this pair, and we do not.
            return JSONResponse({"known": False})

        earlier = remembered.get(request.post, resume_id) if resume_id else None
        if earlier is None:
            return JSONResponse({"known": False})
        # Decision 0008. Brief 0014 did find it needed them: the panel's top
        # line is the answer word, one sentence AND a counts row, and its
        # bottom is the folded list of everything the post asks for. Neither
        # was in the reply, and neither can be derived in a client -- the three
        # lists are a shortlist, so counting them would be arithmetic over the
        # wrong set as well as the judgement-in-a-client decision 0006 forbids.
        #
        # Both come straight out of the stored file. Nothing here recomputes a
        # judgement; if a field is missing from an older file it stays missing
        # rather than being filled in from something else.
        return JSONResponse(
            {
                "known": True,
                **earlier["summary"],
                "counts": earlier["counts"],
                "requirements": [
                    # The `requirements` event's own shape and nothing more,
                    # built through the same function the stream uses so the
                    # panel cannot see two versions of one list. `required` is
                    # read through `requirement_is_required`, which is where
                    # decision 0006 item 7 put "absent means required".
                    {
                        "id": item["id"],
                        "text": item["text"],
                        "required": ev.requirement_is_required(item),
                    }
                    for item in earlier["requirements"]
                ],
            }
        )

    @app.post("/prescreen")
    def prescreen(request: PrescreenRequest):
        """The fast speed. No model is constructed and none is called -- note
        that `build_model` is not reachable from this function at all."""
        try:
            resume = _resume_text(request.resume, request.resume_id)
        except IngestError as exc:
            return JSONResponse({"error": str(exc)}, status_code=404)
        if not request.post.strip():
            return JSONResponse({"error": "post is empty"}, status_code=400)

        resume_index, _ = index_resume(resume)
        return JSONResponse(run_prescreen(request.post, resume_index))

    @app.get("/resumes")
    def list_resumes():
        return JSONResponse({"resumes": store.list()})

    @app.post("/resumes")
    async def upload_resume(file: UploadFile):
        try:
            text = extract_text(await file.read(), file.filename or "resume.txt")
            resume_id = store.save(file.filename or "resume.txt", text)
        except IngestError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        stored = store.get(resume_id)
        resume_index, repaired = index_resume(stored.text)
        return JSONResponse(
            {
                "id": resume_id,
                "lines": len(resume_index),
                "repaired": len(repaired.changes),
                "default": stored.is_default,
            }
        )

    @app.get("/resumes/{resume_id}")
    def show_resume(resume_id: str):
        """The lines a human can check before trusting a verdict.

        This is the whole reason the endpoint exists: the numbers here are the
        numbers a verdict cites, because both come from `index_resume`. What
        repair changed is listed alongside, so the damage and the fix are both
        visible rather than one of them being taken on trust.
        """
        try:
            stored = store.get(resume_id)
        except IngestError as exc:
            return JSONResponse({"error": str(exc)}, status_code=404)

        resume_index, repaired = index_resume(stored.text)
        return JSONResponse(
            {
                "id": stored.id,
                "default": stored.is_default,
                "lines": [
                    {"number": line.number, "text": line.text}
                    for line in resume_index.lines
                ],
                "repairs": [
                    {
                        "kind": change.kind,
                        "source_line": change.source_line,
                        "before": change.before,
                        "after": change.after,
                    }
                    for change in repaired.changes
                ],
            }
        )

    @app.post("/resumes/{resume_id}/default")
    def make_default(resume_id: str):
        try:
            store.set_default(resume_id)
        except IngestError as exc:
            return JSONResponse({"error": str(exc)}, status_code=404)
        return JSONResponse({"id": resume_id, "default": True})

    @app.get("/{asset:path}", response_class=HTMLResponse)
    def static_asset(asset: str):
        """The page's own CSS and JS, which brief 0002 also owns.

        Declared last on purpose -- see the module docstring.
        """
        candidate = (FRONTEND_DIR / asset).resolve()
        root = FRONTEND_DIR.resolve()
        if not str(candidate).startswith(str(root)) or not candidate.is_file():
            return JSONResponse({"error": "not found"}, status_code=404)
        kinds = {".css": "text/css", ".js": "text/javascript", ".json": "application/json"}
        media = kinds.get(candidate.suffix, "text/plain")
        return HTMLResponse(candidate.read_text(encoding="utf-8"), media_type=media)

    return app


app = create_app()

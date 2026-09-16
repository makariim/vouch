"""The extension in LIVE mode against the real backend.

The backend is on 8001, not 8000: another session already holds 8000 and taking
it would break their work. The extension is hardcoded to 8000 by config.js
(which is the contract, and is not changed for a test), so every request to
localhost:8000 is redirected to 8001 at the browser. Nothing in extension/ is
modified for this run.
"""
import functools
import json
import http.server
import pathlib
import threading
import time

from playwright.sync_api import sync_playwright

import os
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
EXT = HERE.parents[1]                      # extension/
PAGES = HERE / "pages"
# Profiles and screenshots are throwaway. They never go in the repository.
WORK = pathlib.Path(os.environ.get("VOUCH_WORK") or tempfile.mkdtemp(prefix="vouch-"))
SHOTS = WORK / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)

BACKEND = "http://127.0.0.1:8001"

PORT = 8732
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(PAGES))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

results = []


def note(ok, what):
    results.append((ok, what))
    print(("  ok   " if ok else "  FAIL ") + what)


with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=str(WORK / "profile"),
        headless=False,
        args=[
            f"--disable-extensions-except={EXT}",
            f"--load-extension={EXT}",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        viewport={"width": 1100, "height": 900},
    )

    # No interception at all. The backend is bound to [::1]:8000, which is what
    # `localhost:8000` resolves to here, so config.js's real address is used
    # unmodified. Nothing in extension/ is changed for this run.
    seen = []
    ctx.on("request", lambda r: seen.append(r.method + " " + r.url)
           if "localhost:8000" in r.url else None)

    worker = None
    for _ in range(40):
        if ctx.service_workers:
            worker = ctx.service_workers[0]
            break
        try:
            worker = ctx.wait_for_event("serviceworker", timeout=1000)
            break
        except Exception:
            pass
    ext_id = worker.url.split("/")[2]

    # live mode, explicitly. This is the whole point of the run.
    setup = ctx.new_page()
    setup.goto(f"chrome-extension://{ext_id}/src/panel.html")
    setup.evaluate("async () => await chrome.storage.local.set({mode: 'live'})")
    mode = setup.evaluate("async () => await chrome.storage.local.get('mode')")
    note(mode.get("mode") == "live", f"mode is {mode.get('mode')!r}, not fixture")
    setup.close()

    job = ctx.new_page()
    job.goto(f"http://127.0.0.1:{PORT}/jobpost.html")
    time.sleep(3.5)

    found = worker.evaluate(
        """async () => {
            const all = await chrome.storage.session.get(null);
            for (const [k, v] of Object.entries(all))
                if (v && v.url && v.url.includes('jobpost.html')) return { key: k, state: v };
            return null;
        }"""
    )
    note(found is not None, "the worker stored a state for the job page")
    state = found["state"] if found else {}
    note(state.get("isJobPost") is True, "detected as a job post")
    note(state.get("backend") == "up", f"backend reachable from the worker: {state.get('backend')!r}")
    note(bool(state.get("resume")), f"default resume found: {state.get('resume')}")
    note(bool(state.get("prescreen")), f"live prescreen: {state.get('prescreen')}")

    # Store an audit for the post text the extension ACTUALLY extracted. The
    # key is a hash of the post, so hashing the raw HTML file instead gives a
    # different key and POST /summary correctly answers "not known". That is
    # the store behaving, not failing.
    # store.py by file path: importing `audit.store` normally pulls in the
    # package __init__, which imports the graph, which needs langgraph. The
    # store itself is stdlib only.
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "audit_store", str(EXT.parent / "src" / "audit" / "store.py")
    )
    _store_mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_store_mod)
    AuditStore = _store_mod.AuditStore

    AuditStore(pathlib.Path(pathlib.Path(os.environ.get("VOUCH_RESUMES", "resumes")))).save(
        state["post"],
        state["resume"]["id"],
        requirements=[],
        verdicts=[],
        counts={"shown": 2, "partly": 1, "not": 3},
        summary=json.loads(HERE / "stored-summary.json".read_text()),
    )
    print("  stored an audit for the extracted post text")

    # now the panel, pointed at that tab
    page = ctx.new_page()
    page.add_init_script(
        "const realSend = chrome.runtime.sendMessage.bind(chrome.runtime);\n"
        "chrome.runtime.sendMessage = async (msg) => {\n"
        "  if (msg && msg.kind === 'get-state') return realSend({kind:'get-state', tabId: "
        + str(int(found["key"].split(":")[1]))
        + "});\n"
        "  return realSend(msg);\n"
        "};\n"
        "chrome.tabs.query = async () => [{ id: "
        + str(int(found["key"].split(":")[1]))
        + " }];\n"
    )
    page.goto(f"chrome-extension://{ext_id}/src/panel.html")
    page.wait_for_timeout(2500)

    text = page.evaluate("() => document.body.innerText")
    note("FIXTURES" not in text, "the FIXTURES flag is NOT showing")
    note("Worth applying." in text, "the stored answer rendered from POST /summary")
    note("Kubernetes" in text, "the blockers came through")
    note("Black Friday" in text, "a resume line is quoted word for word")

    box = page.evaluate("() => ({w: document.body.scrollWidth, h: document.body.scrollHeight})")
    page.set_viewport_size({"width": 380, "height": min(max(box["h"], 200), 2400)})
    page.wait_for_timeout(300)
    page.screenshot(path=str(SHOTS / "live-whole-answer.png"), full_page=True)
    note(box["w"] <= 380, f"no sideways scroll ({box['w']}px)")

    print("\n  requests the extension made to localhost:8000:")
    for s in dict.fromkeys(seen):
        print("    " + s)

    httpd.shutdown()
    ctx.close()

print("\n" + "=" * 60)
bad = [w for ok, w in results if not ok]
print(f"{len(results) - len(bad)} of {len(results)} checks passed")
for w in bad:
    print("  FAILED: " + w)

print(f"\nartefacts: {WORK}")

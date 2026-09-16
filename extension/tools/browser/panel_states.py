"""Load the extension unpacked in real Chrome and see whether it works.

Part A: does it load, does the worker run, does the icon change on a job post.
Part B: does every panel state render. Screenshots for each.
"""
import json
import pathlib
import sys
import time
import threading
import functools
import http.server

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


results = []

# The content script matches http and https only, so a file:// page never runs
# it. That is correct -- but it means these pages have to be served.
PORT = 8731
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(PAGES))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}"


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

    errors = []
    ctx.on("weberror", lambda e: errors.append(str(e)))

    # --- the extension loaded at all -------------------------------------
    worker = None
    for _ in range(50):
        if ctx.service_workers:
            worker = ctx.service_workers[0]
            break
        try:
            worker = ctx.wait_for_event("serviceworker", timeout=1000)
            break
        except Exception:
            pass
    note(worker is not None, "the service worker started")
    if worker is None:
        ctx.close()
        sys.exit(1)

    ext_id = worker.url.split("/")[2]
    print(f"  extension id: {ext_id}")

    manifest = worker.evaluate("() => chrome.runtime.getManifest()")
    note(manifest["name"] == "Vouch — evidence audit", f"manifest name: {manifest['name']}")
    note("icons" in manifest, "manifest declares icons")


    def stored(fragment):
        return worker.evaluate(
            """async (frag) => {
                const all = await chrome.storage.session.get(null);
                for (const [k, v] of Object.entries(all)) {
                    if (v && v.url && v.url.includes(frag)) return { key: k, state: v };
                }
                return null;
            }""",
            fragment,
        )

    # --- Part A: detection on a real page --------------------------------
    print("\nPart A — detection and the toolbar icon")

    job = ctx.new_page()
    job.goto(f"{BASE}/jobpost.html")
    time.sleep(2.5)

    found = stored("jobpost.html")
    note(found is not None, "the worker stored a state for the job page")
    job_tab_id = int(found["key"].split(":")[1]) if found else None
    state = found["state"] if found else None
    if state:
        note(state.get("isJobPost") is True, f"job page detected (how: {state.get('how')})")
        note(len(state.get("post", "")) > 400, f"post text captured: {len(state.get('post',''))} chars")

    title = worker.evaluate("async (id) => await chrome.action.getTitle({tabId: id})", job_tab_id)
    note("job post is on this page" in title, f"toolbar title on a job post: {title!r}")

    # a page that is not a job post
    blog = ctx.new_page()
    blog.goto(f"{BASE}/blog.html")
    time.sleep(2.5)
    found_blog = stored("blog.html")
    blog_tab_id = int(found_blog["key"].split(":")[1]) if found_blog else None
    blog_state = found_blog["state"] if found_blog else None
    note(
        bool(blog_state) and blog_state.get("isJobPost") is False,
        "a blog post about engineering is NOT called a job post",
    )
    blog_title = worker.evaluate(
        "async (id) => await chrome.action.getTitle({tabId: id})", blog_tab_id
    )
    note(blog_title == "Vouch", f"toolbar title stays quiet off a job post: {blog_title!r}")

    job.close()
    blog.close()

    # --- Part B: every panel state renders --------------------------------
    print("\nPart B — the panel, state by state")

    STATES = {
        "1-no-job-post": {"isJobPost": False},
        "2-found-checking": {
            "isJobPost": True, "how": "url", "title": "Senior Platform Engineer",
            "post": "x" * 3000, "backend": "up",
            "resume": {"id": "r_1", "name": "makariim-2026-09.pdf", "default": True},
            "prescreen": None,
        },
        "3-quick-match": {
            "isJobPost": True, "how": "url", "title": "Senior Platform Engineer",
            "post": "x" * 3000, "backend": "up",
            "resume": {"id": "r_1", "name": "makariim-2026-09.pdf", "default": True},
            "prescreen": {"signal": "worth_a_look", "matched": 6, "total": 9},
        },
        "4-whole-answer": {
            "isJobPost": True, "how": "url", "title": "Senior Platform Engineer",
            "post": "x" * 3000, "backend": "up",
            "resume": {"id": "r_1", "name": "makariim-2026-09.pdf", "default": True},
            "prescreen": {"signal": "worth_a_look", "matched": 6, "total": 9},
        },
        "5-no-resume": {
            "isJobPost": True, "how": "url", "title": "Senior Platform Engineer",
            "post": "x" * 3000, "backend": "up", "resume": None, "prescreen": None,
        },
        "6-not-running": {
            "isJobPost": True, "how": "url", "title": "Senior Platform Engineer",
            "post": "x" * 3000, "backend": "unreachable", "resume": None, "prescreen": None,
        },
        "7-nothing-missing": {
            "isJobPost": True, "how": "url", "title": "Senior Platform Engineer",
            "post": "x" * 3000, "backend": "up",
            "resume": {"id": "r_1", "name": "makariim-2026-09.pdf", "default": True},
            "prescreen": {"signal": "worth_a_look", "matched": 8, "total": 9},
        },
    }
    CASE = {
        "2-found-checking": "quick-match",
        "3-quick-match": "quick-match",
        "4-whole-answer": "full",
        "7-nothing-missing": "no-blockers",
        "5-no-resume": "no-resume",
    }

    for name, state in STATES.items():
        page = ctx.new_page()
        # The panel asks the worker for this tab's state. Opened as an ordinary
        # tab there is no job page behind it, so the reply is stubbed and what
        # is being exercised is the real stylesheet and the real render code.
        page.add_init_script(
            "window.__state = " + json.dumps(state) + ";\n"
            "const realSend = chrome.runtime.sendMessage.bind(chrome.runtime);\n"
            "chrome.runtime.sendMessage = async (msg) => {\n"
            "  if (msg && (msg.kind === 'get-state' || msg.kind === 'recheck')) return window.__state;\n"
            "  return realSend(msg);\n"
            "};\n"
            "chrome.tabs.query = async () => [{ id: 1 }];\n"
        )
        page.goto(f"chrome-extension://{ext_id}/src/panel.html")
        page.evaluate(
            """async (c) => await chrome.storage.local.set({mode: 'fixture', fixtureCase: c})""",
            CASE.get(name, "full"),
        )
        page.reload()
        page.wait_for_timeout(1400)

        box = page.evaluate(
            "() => ({w: document.body.scrollWidth, h: document.body.scrollHeight,"
            " text: document.body.innerText.slice(0, 400)})"
        )
        page.set_viewport_size({"width": 380, "height": min(max(box["h"], 200), 2400)})
        page.wait_for_timeout(350)
        page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=True)

        note(box["w"] <= 380, f"{name}: no sideways scroll (content {box['w']}px)")
        print("      " + box["text"].replace("\n", " / ")[:220])
        page.close()

    note(not errors, f"page errors: {errors or 'none'}")

    httpd.shutdown()
    ctx.close()

print("\n" + "=" * 60)
bad = [w for ok, w in results if not ok]
print(f"{len(results) - len(bad)} of {len(results)} checks passed")
for w in bad:
    print("  FAILED: " + w)

print(f"\nartefacts: {WORK}")

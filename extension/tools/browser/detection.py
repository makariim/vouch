"""The shape half of detection, in a real browser, on pages with no URL clue.

Every page here is served from 127.0.0.1, so no URL rule can fire and the only
thing being measured is shapeSaysJobPost: four heading words and 1200
characters.
"""
import functools
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


PORT = 8733
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(PAGES))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

# page, is it really a job post
CASES = [
    ("jobpost.html", True, "a full job post, all the usual headings"),
    ("short-post.html", True, "a real but very short job post"),
    ("blog.html", False, "an engineering blog post about microservices"),
    ("news-hiring.html", False, "a news article about hiring"),
    ("careers-index.html", False, "a careers index listing five roles"),
]

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
    )
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

    rows = []
    for name, truth, what in CASES:
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{PORT}/{name}")
        time.sleep(2.2)
        found = worker.evaluate(
            """async (frag) => {
                const all = await chrome.storage.session.get(null);
                for (const [k, v] of Object.entries(all))
                    if (v && v.url && v.url.includes(frag)) return v;
                return null;
            }""",
            name,
        )
        got = bool(found and found.get("isJobPost"))
        how = (found or {}).get("how", "-")
        chars = len((found or {}).get("post", "") or "")
        verdict = "correct" if got == truth else ("MISSED" if truth else "FALSE POSITIVE")
        rows.append((what, truth, got, how, chars, verdict))
        page.close()

    httpd.shutdown()
    ctx.close()

print(f"{'page':<46} {'is':<5} {'said':<5} {'how':<6} {'chars':>6}  verdict")
print("-" * 86)
for what, truth, got, how, chars, verdict in rows:
    print(f"{what:<46} {str(truth):<5} {str(got):<5} {how:<6} {chars:>6}  {verdict}")

ok = sum(1 for r in rows if r[5] == "correct")
print(f"\n{ok} of {len(rows)} correct")
for r in rows:
    if r[5] != "correct":
        print(f"  {r[5]}: {r[0]}")

print(f"\nartefacts: {WORK}")

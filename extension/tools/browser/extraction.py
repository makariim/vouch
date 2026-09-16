"""What the extension sends as the job post, with the known-site list off.

Brief 0016 asks one question: does a general scorer find the description on a
site nobody wrote a selector for? So this script copies the extension to a
temporary folder, flips `USE_KNOWN_SELECTORS` to false in the copy, and loads
*that*. The fast path cannot rescue anything here.

For every page it prints two counts, both taken the way the panel takes its
own: `candidate_requirements` from the backend's pre-screen, run over the text
the extension actually extracted.

    before   the old mechanism -- the eleven selectors ending in `article`
             and `main`, reproduced below and evaluated in the page
    after    what the scorer picks

> The three `*-shaped.html` pages are RECONSTRUCTIONS, not real job posts.
> Read `pages/README.md` before quoting a number from them anywhere.
"""
import functools
import http.server
import os
import pathlib
import re
import shutil
import sys
import tempfile
import threading
import time

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
EXT = HERE.parents[1]                      # extension/
ROOT = EXT.parent                          # the repository
PAGES = HERE / "pages"
sys.path.insert(0, str(ROOT / "src"))
from audit.prescreen import candidate_requirements  # noqa: E402

WORK = pathlib.Path(os.environ.get("VOUCH_WORK") or tempfile.mkdtemp(prefix="vouch-"))

# The extension, with the fast path switched off. Nothing in the repository is
# edited: the flag is a plain const in the shipped file and the copy is what
# gets loaded.
NOFAST = WORK / "extension-no-fast-path"
if NOFAST.exists():
    shutil.rmtree(NOFAST)
shutil.copytree(EXT, NOFAST, ignore=shutil.ignore_patterns("tools", "__pycache__"))
detect = NOFAST / "src" / "detect.js"
source = detect.read_text()
patched = source.replace(
    "const USE_KNOWN_SELECTORS = true;", "const USE_KNOWN_SELECTORS = false;"
)
if patched == source:
    sys.exit("could not find USE_KNOWN_SELECTORS in detect.js -- refusing to "
             "measure with the fast path in an unknown state")
detect.write_text(patched)

# The mechanism this brief replaces, kept here so `before` is measured and not
# remembered. Eleven selectors, the last two of which caught everything.
OLD_EXTRACT = """() => {
  const OLD = [
    ".jobs-description__content", ".jobs-box__html-content", "#job-details",
    "[data-automation-id='jobPostingDescription']", "#content .section-wrapper",
    ".posting-page", "#job_description", ".job-description",
    "[class*='jobDescription']", "article", "main",
  ];
  const visible = (n) => (n.innerText || "").replace(/\\s+\\n/g, "\\n").trim();
  for (const s of OLD) {
    const n = document.querySelector(s);
    if (n) { const t = visible(n); if (t.length > 400) return t.slice(0, 30000); }
  }
  return visible(document.body).slice(0, 30000);
}"""

PORT = 8734
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(PAGES))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

CASES = [
    ("linkedin-shaped.html", "a LinkedIn job view, reconstructed"),
    ("ashby-shaped.html", "an Ashby posting, reconstructed"),
    ("northwind-careers.html", "a company careers page nobody coded for"),
    ("jobpost.html", "the plain job post from brief 0014"),
    # The known failure, kept in the run rather than in a footnote.
    ("cards-not-linked.html", "the same LinkedIn page, card titles linked only"),
    # Three the badge must stay off. The scorer changes what gets measured, so
    # the negatives are re-measured here too rather than assumed.
    ("careers-index.html", "a careers index -- must NOT detect"),
    ("blog.html", "an engineering blog post -- must NOT detect"),
    ("news-hiring.html", "a news article about hiring -- must NOT detect"),
]

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=str(WORK / "profile"),
        headless=False,
        args=[
            f"--disable-extensions-except={NOFAST}",
            f"--load-extension={NOFAST}",
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
    for name, what in CASES:
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{PORT}/{name}")
        time.sleep(2.2)
        before = page.evaluate(OLD_EXTRACT)
        found = worker.evaluate(
            """async (frag) => {
                const all = await chrome.storage.session.get(null);
                for (const [k, v] of Object.entries(all))
                    if (v && v.url && v.url.includes(frag)) return v;
                return null;
            }""",
            name,
        )
        after = (found or {}).get("post", "") or ""
        rows.append((
            what,
            len(candidate_requirements(before)), len(before),
            len(candidate_requirements(after)), len(after),
            bool(found and found.get("isJobPost")),
        ))
        page.close()

    httpd.shutdown()
    ctx.close()

print(f"{'page':<50} {'before':>7} {'chars':>7} {'after':>7} {'chars':>7}  detected")
print("-" * 90)
for what, nb, cb, na, ca, seen in rows:
    print(f"{what:<50} {nb:>7} {cb:>7} {na:>7} {ca:>7}  {seen}")

print("\nthe known-site list was OFF for every `after` above")
print(f"artefacts: {WORK}")

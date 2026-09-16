"""The URL half of detection, offline.

The rules are read out of `detect.js` and run in node, so what is tested is the
shipped regular expressions and not a copy of them that could drift.

**The URLs were written from the known formats of each board. None was
visited.** That is the same caveat report 0014 carried and it still applies:
this establishes that the patterns say yes and no where they should, not that
any of these pages exists.

    uv run python url_rules.py          (node is the only other requirement)
"""
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DETECT = HERE.parents[1] / "src" / "detect.js"

# should it fire, url, what it is
CASES = [
    # The four from brief 0016 section 4: two that already worked, two that
    # missed and are the reason this list grew.
    (True, "https://www.linkedin.com/jobs/view/4021884571/", "LinkedIn, a job view"),
    (True, "https://jobs.ashbyhq.com/datarobot/6f1e0b2a-77c4-4b31-9a0e-2d1f3c8e5a90",
     "Ashby, a hosted post"),
    (True, "https://www.linkedin.com/jobs/search-results/?currentJobId=4021884571&keywords=ml",
     "LinkedIn search-results -- MISSED before 0016"),
    (True, "https://www.acmeanalytics.com/careers?ashby_jid=6f1e0b2a-77c4-4b31-9a0e-2d1f3c8e5a90",
     "Ashby embedded on a company site -- MISSED before 0016"),
    # The rest of the twelve report 0014 measured.
    (True, "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4021884571",
     "LinkedIn collections"),
    (True, "https://www.linkedin.com/jobs/search/?currentJobId=4021884571", "LinkedIn search"),
    (True, "https://boards.greenhouse.io/datarobot/jobs/5512233", "Greenhouse"),
    (True, "https://job-boards.greenhouse.io/acme/jobs/4412289", "Greenhouse, new host"),
    (True, "https://jobs.lever.co/acme/2f8c1d40-9a77-4b0e-8c51-7d2e9f3a1b64", "Lever"),
    (True, "https://acme.workable.com/j/3F1C9A77B2", "Workable"),
    (True, "https://acme.wd1.myworkdayjobs.com/en-US/careers/job/Remote/ML-Engineer_R-10422",
     "Workday"),
    (True, "https://www.smartrecruiters.com/AcmeAnalytics/744000012345678", "SmartRecruiters"),
    (True, "https://www.indeed.com/viewjob?jk=9f2c1d40a9774b0e", "Indeed"),
    (True, "https://wellfound.com/jobs/1234567-machine-learning-engineer", "Wellfound"),
    # The eight that must stay quiet.
    (False, "https://www.linkedin.com/feed/", "LinkedIn feed"),
    (False, "https://www.linkedin.com/in/muhammad-elsherif/", "a LinkedIn profile"),
    (False, "https://www.linkedin.com/jobs/", "the LinkedIn jobs home"),
    (False, "https://www.acmeanalytics.com/careers", "a company careers index"),
    (False, "https://boards.greenhouse.io/datarobot", "a Greenhouse board index"),
    (False, "https://www.indeed.com/jobs?q=machine+learning&l=Remote", "an Indeed search"),
    (False, "https://www.theverge.com/2026/9/1/tech-hiring-is-changing", "a news article"),
    (False, "https://news.ycombinator.com/item?id=41234567", "Hacker News"),
    # Two more, because brief 0016 added two patterns and a new pattern is a
    # new way to fire on an index.
    (False, "https://jobs.ashbyhq.com/datarobot", "an Ashby board index"),
    (False, "https://www.linkedin.com/jobs/search-results/?keywords=ml&location=Remote",
     "LinkedIn search-results with no job open"),
]

source = DETECT.read_text()
block = re.search(r"const URL_RULES = \[(.*?)\n  \];", source, re.S)
if not block:
    sys.exit("could not find URL_RULES in detect.js")

script = (
    "const URL_RULES = [" + block.group(1) + "];\n"
    "const cases = " + json.dumps([[u] for _, u, _ in CASES]) + ";\n"
    "console.log(JSON.stringify(cases.map(([u]) => URL_RULES.some(r => r.test(u)))));"
)
got = json.loads(subprocess.run(
    ["node", "-e", script], capture_output=True, text=True, check=True
).stdout)

print(f"{'url':<62} {'should':<7} {'did':<7} verdict")
print("-" * 92)
bad = 0
for (want, url, what), fired in zip(CASES, got):
    ok = want == fired
    bad += not ok
    verdict = "ok" if ok else ("MISSED" if want else "FALSE POSITIVE")
    print(f"{url[:60]:<62} {str(want):<7} {str(fired):<7} {verdict}   {what}")

fires = sum(1 for (w, _, _) in CASES if w)
print(f"\ncaught {sum(g for (w, _, _), g in zip(CASES, got) if w)}/{fires}   "
      f"false positives {sum(g for (w, _, _), g in zip(CASES, got) if not w)}"
      f"/{len(CASES) - fires}")
sys.exit(1 if bad else 0)

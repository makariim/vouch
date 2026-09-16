"""Writes the three reconstruction pages `extraction.py` measures.

These are NOT real job posts. They are pages laid out the way a real job
board lays one out -- a nav bar, a right rail of related jobs, an upsell, a
similar-jobs list, a footer -- wrapped around one description. The point is
that the furniture is the variable and the description is not.

It is here so the fixtures can be read rather than trusted. See the warning in
`../README.md` about what a reconstruction can and cannot establish.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent

CSS = """
body{font:16px/1.5 system-ui;margin:0;color:#111}
a{color:#0a66c2}
nav,header,footer{background:#f3f2ef;padding:12px}
.rail{float:right;width:300px}
.wrap{max-width:1100px;margin:0 auto;padding:16px}
li{margin:8px 0}
"""

# --- the job description itself -------------------------------------------
# Twenty-two lines that really are asks of the candidate, plus the prose a
# description carries around them.
REQUIREMENTS = [
    "You have five or more years of experience building production machine learning systems.",
    "You are fluent in Python and comfortable reading somebody else's code before changing it.",
    "You have shipped and operated services on Kubernetes in a production environment.",
    "You have worked with a cloud provider such as AWS, GCP or Azure at meaningful scale.",
    "You can design a data pipeline that survives bad input without a human watching it.",
    "You have experience with distributed training or large scale batch inference.",
    "You write tests for the parts of a system that would be expensive to get wrong.",
    "You have led a technical project end to end, including the part where it goes wrong.",
    "You can explain a model's behaviour to somebody who does not build models.",
    "You have worked directly with customers or internal stakeholders on their own problems.",
    "You are comfortable with SQL and can profile a query that has become slow.",
    "You have used a workflow orchestrator such as Airflow, Dagster or Prefect.",
    "You have experience with monitoring and alerting for systems you own.",
    "You understand the trade offs between batch and streaming for a given problem.",
    "You have mentored engineers earlier in their career than you.",
    "Experience with large language models or retrieval systems is a strong plus.",
    "Familiarity with feature stores and the problems they exist to solve is welcome.",
    "You are willing to travel occasionally to customer sites within the region.",
    "You hold a degree in a quantitative field, or equivalent practical experience.",
    "You communicate clearly in writing, because most of this team writes things down.",
    "You are comfortable working across time zones with a distributed team.",
    "You care about the accuracy of what you ship more than the speed of shipping it.",
]

PROSE = """<p>We are looking for a Senior Machine Learning Engineer to join the
Applied AI team. You will work directly with customers to take models from a
notebook into something that runs every day and can be trusted when it does.</p>
<p>This is a hands on engineering role. You will spend most of your time
writing code, reading logs and talking to the people who depend on the systems
you build. The team is small and owns what it ships.</p>"""


def requirement_list(items):
    return "\n".join(f"<li>{line}</li>" for line in items)


def description_block(title):
    return f"""
      <h1>{title}</h1>
      <p>Acme Analytics · San Francisco, CA · Full-time</p>
      {PROSE}
      <h2>What you'll do</h2>
      <ul>{requirement_list(REQUIREMENTS[:8])}</ul>
      <h2>Qualifications</h2>
      <ul>{requirement_list(REQUIREMENTS[8:18])}</ul>
      <h2>Nice to have</h2>
      <ul>{requirement_list(REQUIREMENTS[18:])}</ul>
      <h2>Benefits</h2>
      <p>Health, dental and vision cover from your first day, a learning budget
      and a genuinely flexible remote policy.</p>
      <p>Acme Analytics is an equal opportunity employer. We consider all
      qualified applicants without regard to any protected characteristic.</p>
"""


# --- the furniture ---------------------------------------------------------
ROLES = [
    ("Senior Data Scientist, Growth Platform", "Northwind Data", "New York, NY (Hybrid)"),
    ("Staff Machine Learning Engineer, Ranking", "Contoso Cloud", "Seattle, WA (Remote)"),
    ("Principal Applied Scientist, Forecasting", "Fabrikam Systems", "Austin, TX (On-site)"),
    ("Machine Learning Platform Engineer II", "Globex Corporation", "Boston, MA (Hybrid)"),
    ("Lead Data Engineer, Customer Analytics", "Initech Software", "Chicago, IL (Remote)"),
    ("Senior Research Engineer, Language Models", "Umbrella Labs", "Remote, United States"),
    ("Director of Machine Learning Operations", "Soylent Industries", "San Jose, CA (On-site)"),
    ("Applied AI Engineer, Professional Services", "Vandelay Analytics", "Denver, CO (Remote)"),
    ("Senior Backend Engineer, Data Products", "Wayne Enterprises", "Atlanta, GA (Hybrid)"),
    ("Staff Software Engineer, Model Serving", "Stark Data Group", "Portland, OR (Remote)"),
    ("Machine Learning Engineer, Personalisation", "Cyberdyne Retail", "Miami, FL (On-site)"),
    ("Senior Analytics Engineer, Revenue Team", "Tyrell Commerce", "Phoenix, AZ (Hybrid)"),
]


def role_cards(n, klass="card", whole_card_links=True):
    out = []
    # A fixed id per role. `hash()` is salted per process, and a fixture that
    # changes every time it is generated is not a fixture.
    for i, (title, company, place) in enumerate(ROLES[:n], start=1):
        # The whole card is one anchor, which is how LinkedIn, Ashby and most
        # careers sites build a related-jobs list. It matters: link density is
        # measured in characters, and a card whose title alone is a link reads
        # as prose.
        if whole_card_links:
            out.append(
                f'<li class="{klass}"><a href="/jobs/view/{400000000 + i}">'
                f"<span>{title}</span><span>{company}</span><span>{place}</span>"
                f"<span>Actively recruiting for this role right now</span></a></li>"
            )
        else:
            # The same list, with only the title inside the anchor. This is the
            # case the scorer gets wrong, and it is why this variant exists.
            out.append(
                f'<li class="{klass}"><a href="/jobs/view/{400000000 + i}">'
                f"{title}</a><div>{company}</div><div>{place}</div>"
                f"<div>Actively recruiting for this role right now</div></li>"
            )
    return "\n".join(out)


NAV_LINKS = ["Home", "My Network", "Jobs", "Messaging", "Notifications", "Me", "Work", "Post a job"]
FOOTER_LINKS = [
    "About", "Accessibility", "User Agreement", "Privacy Policy", "Cookie Policy",
    "Copyright Policy", "Brand Policy", "Guest Controls", "Community Guidelines",
    "Careers", "Advertising", "Small Business", "Talent Solutions", "Marketing Solutions",
    "Sales Solutions", "Safety Centre", "Help Centre", "Language",
]
FOOTER_LINES = [
    "Find the right job or internship for you today",
    "Learn the skills that hiring managers are asking for",
    "Browse thousands of open roles across every industry",
    "Salary insights are available for this search",
    "Discover companies that are hiring in your area",
    "See who else in your network already works here",
]

UPSELL = [
    "Get the skills you need to land a job like this one",
    "See how you compare with other applicants for this role",
    "Find out which of your connections work at this company",
    "Try Premium free for one month and stand out to recruiters",
    "Applicants for this job are usually contacted within two weeks",
    "People who viewed this job also applied to forty other roles",
    "Your profile is missing three skills this job asks for",
    "Recruiters are more likely to respond to a complete profile",
]


def upsell_block():
    items = "\n".join(f'<li><a href="/premium">{line}</a></li>' for line in UPSELL)
    return f'<section class="upsell"><h3>Premium</h3><ul>{items}</ul></section>'


def nav(links):
    return "<nav>" + " ".join(f'<a href="/{l}">{l}</a>' for l in links) + "</nav>"


def footer():
    links = " ".join(f'<a href="/{l}">{l}</a>' for l in FOOTER_LINKS)
    lines = "\n".join(f'<li><a href="/x">{l}</a></li>' for l in FOOTER_LINES)
    return f"<footer><ul>{lines}</ul><div>{links}</div>" \
           "<p>Acme Corporation 2026. All rights reserved.</p></footer>"


def page(title, body):
    return (
        f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>\n"
    )


# --- LinkedIn shaped -------------------------------------------------------
# No `.jobs-description__content` anywhere, on purpose: the whole reason this
# page exists is that on the real post the known-site selectors missed and a
# bare `article` caught everything.
linkedin = page(
    "Senior Machine Learning Engineer | Acme Analytics | LinkedIn",
    nav(NAV_LINKS)
    + '<div class="wrap">'
    + '<div class="rail"><h3>People also viewed</h3><ul>'
    + role_cards(12)
    + "</ul></div>"
    + "<main><article>"
    + '<div class="top-card"><p>Acme Analytics</p>'
    + "<form><button>Easy Apply</button></form></div>"
    + '<div class="jd-body">'
    + description_block("Senior Machine Learning Engineer")
    + "</div>"
    + upsell_block()
    + '<section class="similar"><h3>Similar jobs</h3><ul>'
    + role_cards(10)
    + "</ul></section>"
    + "</article></main></div>"
    + footer(),
)

# --- Ashby shaped ----------------------------------------------------------
ashby = page(
    "Senior Machine Learning Engineer @ Acme Analytics",
    "<header><a href=\"/\">Acme Analytics</a> "
    + '<a href="/careers">All openings</a></header>'
    + '<main class="wrap">'
    + '<div class="ashby-job-posting">'
    + description_block("Senior Machine Learning Engineer")
    + "</div>"
    + '<section class="other-openings"><h3>Other openings at Acme</h3><ul>'
    + role_cards(12)
    + "</ul></section>"
    + '<div class="powered">Powered by Ashby. Jobs powered by Ashby are posted '
    + "by the employer and not by us.</div>"
    + "</main>"
    + footer(),
)

# --- A third site nobody coded for ----------------------------------------
# Northwind's own careers site. No board, no known selector, no `article`.
northwind = page(
    "Senior Machine Learning Engineer — Northwind Data careers",
    nav(["Product", "Solutions", "Customers", "Pricing", "Docs", "Company", "Careers", "Contact"])
    + '<div class="wrap">'
    + '<section class="hero"><h2>Work at Northwind</h2>'
    + "<p>We are a hundred and forty people in six countries building the data "
    + "platform that our customers run their businesses on.</p></section>"
    + '<div class="rail"><h3>Open roles in Engineering</h3><ul>'
    + role_cards(12)
    + "</ul></div>"
    + '<div class="posting"><div class="posting-inner">'
    + description_block("Senior Machine Learning Engineer")
    + "</div></div>"
    + '<section class="more"><h3>More ways to join us</h3><ul>'
    + role_cards(8)
    + "</ul></section>"
    + "</div>"
    + footer(),
)

# --- the same LinkedIn page, with only card titles linked --------------------
# Kept deliberately, as the failure. Link density is measured in characters, so
# a card list where the company and the location sit outside the anchor reads
# as prose and the scorer takes the wrapper instead of the description.
def linked_titles_only():
    return page(
        "Senior Machine Learning Engineer | Acme Analytics | LinkedIn",
        nav(NAV_LINKS)
        + '<div class="wrap">'
        + '<div class="rail"><h3>People also viewed</h3><ul>'
        + role_cards(12, whole_card_links=False)
        + "</ul></div>"
        + "<main><article>"
        + '<div class="top-card"><p>Acme Analytics</p>'
        + "<form><button>Easy Apply</button></form></div>"
        + '<div class="jd-body">'
        + description_block("Senior Machine Learning Engineer")
        + "</div>"
        + upsell_block()
        + '<section class="similar"><h3>Similar jobs</h3><ul>'
        + role_cards(10, whole_card_links=False)
        + "</ul></section>"
        + "</article></main></div>"
        + footer(),
    )


for name, html in [
    ("linkedin-shaped.html", linkedin),
    ("ashby-shaped.html", ashby),
    ("northwind-careers.html", northwind),
    ("cards-not-linked.html", linked_titles_only()),
]:
    (OUT / name).write_text(html)
    print("wrote", name, len(html), "chars")

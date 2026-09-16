// The panel. Renders whatever state the worker has for this tab, plus the one
// thing it fetches itself: the stored summary.
//
// No innerHTML anywhere below. Every piece of text on this panel came off a
// web page you did not write, and building DOM nodes by hand is how that stays
// text instead of becoming markup.
//
// THE SIX STATES, and what decides each. design/README.md names them:
//
//   no job post here   the content script did not find one
//   found a job post   found one, the word match has not come back yet
//   quick match only   the word match is in, this post has not been audited
//   the whole answer   POST /summary knew this post
//   no resume saved    GET /resumes has no default
//   Vouch is not running   nothing answered on localhost
//
// The order matters: the server being down outranks everything except "there
// is no job post here", because with no server every other state is a guess.

import { BACKEND, getMode, setMode } from "./config.js";
import { summary } from "./api.js";

const panel = document.getElementById("panel");
const flag = document.getElementById("flag");
const barNote = document.getElementById("bar-note");
const toggle = document.getElementById("fixture-toggle");
const caseSelect = document.getElementById("fixture-case");

// Three answers. Never a fourth. No "likely", no "unclear".
const FIT_WORDS = {
  strong: "Strong fit.",
  worth_applying: "Worth applying.",
  weak: "Weak fit.",
};

// `signal` is a closed set -- decision 0006 section 5. It is the word match's
// own read, so every line below has to stay well short of a verdict: nothing
// has been read or judged at this point. Each says what to do next.
const SIGNAL_WORDS = {
  worth_a_look: "Worth checking properly.",
  maybe: "Could go either way. A proper check would settle it.",
  skip: "Probably not this one. A proper check would be sure.",
};

const NUMBER_WORDS = [
  "no", "one", "two", "three", "four", "five",
  "six", "seven", "eight", "nine", "ten",
];

function count(n, singular, plural) {
  const word = n < NUMBER_WORDS.length ? NUMBER_WORDS[n] : String(n);
  return word + " " + (n === 1 ? singular : plural);
}

// What to call the resume in the header.
//
// The artboard shows a filename -- "maya-okonkwo-2026.pdf" -- and there is no
// filename to show. Decision 0005 specifies `GET /resumes` as the word "list"
// and never says what one item holds, so the running backend answers
// {id, lines, default} and has no `name` at all. This is the same shape of
// hole decision 0006 section 3 closed for the summary's three lists, one field
// further on, and it is the director's to close rather than mine to invent.
//
// Until then: the id, which is derived from the filename and is at least the
// user's own word. Never "undefined" in the one place the panel promises to
// tell you what it checked you against.
function resumeLabel(resume) {
  if (!resume) return "";
  return resume.name || resume.id || "your resume";
}

// --- making nodes ----------------------------------------------------------

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function section(...children) {
  const node = el("div", "sec");
  node.append(...children.filter(Boolean));
  return node;
}

function title(text) {
  return el("div", "sec-title", text);
}

// The answer mark: a left arm, a right arm, and a fill that rises from the
// bottom. The fill level is what survives greyscale and colour blindness, so
// colour is never doing the work alone -- and the aria-label carries the whole
// sentence, because a screen reader gets neither.
const MARK_WORDS = {
  shown: "your resume shows this",
  partly: "your resume shows part of this",
  not: "your resume does not show this",
};

function mark(kind, extra) {
  const node = el("span", "mark " + kind + (extra ? " " + extra : ""));
  node.setAttribute("role", "img");
  node.setAttribute("aria-label", MARK_WORDS[kind]);
  node.append(el("i", "l"), el("i", "r"), el("b"));
  return node;
}

function button(className, label, meta, onClick) {
  const node = el("button", className);
  node.append(el("span", null, label));
  if (meta) node.append(el("span", "meta", meta));
  node.addEventListener("click", onClick);
  return node;
}

// A quoted resume line. Word for word: pre-wrap in the stylesheet keeps the
// resume's own spacing, and nothing here trims, italicises or shortens it.
//
// There is no `quote` for an answer of "does not show this" and there must not
// be: design/README.md is explicit that the block is absent rather than empty.
// That silence is the product.
function quoted(kind, lineNumber, line, where) {
  const box = el("div", "quote " + kind);
  box.append(el("div", "quote-where", "Line " + lineNumber + ", " + where));
  box.append(el("div", "quote-line", line));
  return box;
}

function clear() {
  panel.replaceChildren();
  document.body.classList.remove("is-down");
  barNote.textContent = "";
}

function openPage(fragment) {
  chrome.tabs.create({ url: BACKEND + (fragment || "/") });
}

// The post travels in the URL fragment. A fragment is never sent to the server
// by the browser, so the post text reaches the page without going through a
// request -- which matters, because the whole promise is that nothing leaves
// this machine. Decision 0006 section 4 adopted this and made it the contract.
function openAudit(state) {
  const post = state.post || "";
  openPage(post.length < 12000 ? "/#post=" + encodeURIComponent(post) : "/");
}

// --- the states ------------------------------------------------------------

function renderNoJobPost(state) {
  const box = el("div", "empty");

  const wrap = el("div", "mark-wrap");
  wrap.append(mark("not", "big"));
  box.append(wrap);

  box.append(el("div", "said", "No job post on this page."));
  box.append(
    el("div", "quiet mt-2", "We watch for one. We will tell you without being asked.")
  );

  const foot = el("div", "foot-row");
  foot.append(el("span", "name", resumeLabel(state && state.resume)));
  const link = el("button", "linkish", "Open Vouch");
  link.addEventListener("click", () => openPage("/"));
  foot.append(link);
  box.append(foot);

  panel.append(box);
}

function renderJobHeading(state) {
  return section(
    el("div", "label", "On this page"),
    el("div", "job-title mt-1", state.title || "A job post"),
    state.prescreen
      ? el("div", "note mt-1", count(state.prescreen.total, "thing", "things") + " they ask for")
      : null
  );
}

// Found a job post, and the word match has not come back. The only state the
// panel reaches on its own: spotting a post and the word match are the two
// things allowed to happen without a click.
function renderWorking(state) {
  panel.append(renderJobHeading(state));

  const sweep = el("div", "sweep mt-3");
  sweep.append(el("i"));

  panel.append(
    section(
      el("div", "working", "Checking your resume on this computer…"),
      sweep,
      el("div", "quiet mt-3", "Nothing was sent anywhere. This part is free and takes no time.")
    )
  );
}

function renderQuickMatch(state) {
  const pre = state.prescreen;

  const match = el("div", "match mt-2");
  match.append(el("span", "big", String(pre.matched)));
  match.append(el("span", "of", "of " + pre.total));

  const ticks = el("div", "ticks mt-4");
  for (let i = 0; i < pre.total; i += 1) {
    ticks.append(el("i", i < pre.matched ? "on" : null));
  }

  panel.append(
    section(
      el("div", "quiet", "Quick word match, on this computer"),
      match,
      el("div", "match-says mt-2", "things they ask for look possible"),
      ticks,
      SIGNAL_WORDS[pre.signal] ? el("div", "quiet mt-3", SIGNAL_WORDS[pre.signal]) : null,
      el("div", "quiet mt-2", "This is only a word match. Nothing has been read or judged yet.")
    )
  );

  panel.append(
    section(
      button("btn", "Check my fit properly", "about 1 minute", () => openAudit(state)),
      el(
        "div",
        "quiet mt-3",
        "It reads every line and quotes what it finds. It costs money, so it never starts on its own."
      )
    )
  );
}

// The whole answer. Level one is the word and one sentence; level two is the
// three sections, one line per item. Nothing here says "open the app to see
// this" -- somebody applying to fifteen jobs will not open the app fifteen
// times, so the panel carries all of it and scrolls.
function renderAnswer(data, state) {
  panel.append(
    section(
      el("p", "answer", FIT_WORDS[data.fit] || data.fit),
      el("p", "answer-why", data.fit_reason)
    )
  );
  panel.lastChild.classList.add("lead");

  renderCannotShow(data.blockers || []);
  renderProves(data.strengths || []);
  renderFix(data.undersells || []);

  const foot = el("div", "sec");
  const link = el("button", "linkish", "See the working in the full app →");
  link.addEventListener("click", () => openAudit(state));
  foot.append(link);
  panel.append(foot);
}

function renderCannotShow(blockers) {
  if (blockers.length === 0) {
    panel.append(
      section(
        title("Nothing they need is missing"),
        el("div", "note mt-2", "You can show every one of the things they ask for.")
      )
    );
    return;
  }

  const list = el("div", "stack items mt-3");
  for (const b of blockers) {
    const row = el("div", "item");
    row.append(mark("not"));
    const body = el("div", "body");
    body.append(el("div", "text", b.text));
    // No quote block, ever, on a "does not show this". One plain sentence.
    if (b.reason) body.append(el("div", "note mt-1", b.reason));
    row.append(body);
    list.append(row);
  }

  panel.append(
    section(title("They need " + count(blockers.length, "thing", "things") + " you cannot show"), list)
  );
}

function renderProves(strengths) {
  if (strengths.length === 0) return;

  const list = el("div", "stack quotes mt-3");
  for (const s of strengths) {
    const item = el("div");
    if (s.line) item.append(quoted("shown", s.line_number, s.line, "word for word"));
    else item.append(el("div", "text", s.text));
    if (s.reason) item.append(el("div", "why", s.reason));
    list.append(item);
  }

  panel.append(section(title("This is what proves you fit"), list));
}

function renderFix(undersells) {
  if (undersells.length === 0) return;

  const list = el("div", "stack quotes mt-3");
  for (const u of undersells) {
    const item = el("div");
    if (u.line) item.append(quoted("partly", u.line_number, u.line, "as it stands"));
    else item.append(el("div", "text", u.text));
    if (u.reason) item.append(el("div", "why fix", u.reason));
    list.append(item);
  }

  panel.append(
    section(
      title("Fix these lines in your resume"),
      el(
        "div",
        "note mt-1",
        "You have done these things. Your resume says them so quietly that nobody will notice."
      ),
      list
    )
  );
}

function renderNoResume(state) {
  barNote.textContent = "No resume";

  if (state && state.isJobPost) panel.append(renderJobHeading(state));

  const well = el("div", "well");
  well.append(el("div", "said", "There is nothing to check the job against."));
  well.append(
    el("div", "quiet mt-2", "Save one resume and this panel works on every job board.")
  );

  panel.append(
    section(
      well,
      (() => {
        const b = button("btn mt-3", "Choose a resume", null, () => openPage("/"));
        b.style.justifyContent = "center";
        return b;
      })(),
      el("div", "quiet mt-3", "Saved on this computer only. There is no account to make.")
    )
  );
}

function renderDown(reason, status) {
  document.body.classList.add("is-down");
  barNote.textContent = "Not connected";

  const detail =
    reason === "refused"
      ? "Vouch answered, but with an error" + (status ? " (" + status + ")" : "") + "."
      : "We tried to reach Vouch on this computer and got nothing back.";

  const buttons = el("div", "btn-row mt-4");
  buttons.append(button("btn", "Open Vouch", null, () => openPage("/")));
  buttons.append(button("btn second", "Try again", null, recheck));

  panel.append(
    section(
      title("Vouch is not running on this computer."),
      el(
        "p",
        "answer-why",
        "The panel cannot judge anything without it. Everything happens on your computer, so there is no server to fall back on."
      ),
      el("div", "detail mt-4", detail),
      // Not on the artboard. It is here because starting Vouch is the fix, and
      // a panel that names the problem without naming the fix sends you looking
      // for a README. Mono is allowed: this is text to be copied exactly.
      el("code", "cmd mt-3", "uv run uvicorn audit.server:app --port 8000"),
      buttons,
      el("div", "quiet mt-3", "We can still spot job posts while it is off. We cannot judge them.")
    )
  );
}

// --- wiring ----------------------------------------------------------------

async function render(state) {
  const { mode, fixtureCase } = await getMode();
  flag.hidden = mode !== "fixture";

  clear();

  if (!state || !state.isJobPost) {
    renderNoJobPost(state);
    return;
  }

  if (state.backend && state.backend !== "up") {
    renderDown(state.backend, state.status);
    return;
  }

  if (!state.resume) {
    renderNoResume(state);
    return;
  }

  barNote.textContent = resumeLabel(state.resume);

  const stored = await summary(state.post, state.resume.id, mode, fixtureCase);

  if (!stored.ok) {
    renderDown(stored.reason, stored.status);
    return;
  }

  if (stored.known) {
    renderAnswer(stored.data, state);
    return;
  }

  // Not audited yet. Show what is free and instant, and leave the minute that
  // costs money behind a button. There is no setting that changes that.
  if (state.prescreen) renderQuickMatch(state);
  else renderWorking(state);
}

async function currentTabId() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab ? tab.id : null;
}

async function load() {
  const tabId = await currentTabId();
  if (tabId === null) return renderNoJobPost(null);
  let state = await chrome.runtime.sendMessage({ kind: "get-state", tabId });
  if (!state) {
    // The worker was asleep and the page's last report was dropped. The content
    // script re-reports every second, so one short wait is enough rather than
    // telling you there is no job post on an obvious job post.
    await new Promise((resolve) => setTimeout(resolve, 900));
    state = await chrome.runtime.sendMessage({ kind: "get-state", tabId });
  }
  await render(state);

  // If the word match was still in flight, come back for it once. The panel
  // stays open while this happens, so the "checking" state is real rather than
  // a spinner shown for its own sake.
  if (state && state.isJobPost && state.backend === "up" && state.resume && !state.prescreen) {
    await new Promise((resolve) => setTimeout(resolve, 700));
    const again = await chrome.runtime.sendMessage({ kind: "get-state", tabId });
    if (again && again.prescreen) await render(again);
  }
}

async function recheck() {
  const tabId = await currentTabId();
  if (tabId === null) return;
  clear();
  panel.append(section(el("p", "quiet pad-0", "Looking…")));
  const state = await chrome.runtime.sendMessage({ kind: "recheck", tabId });
  await render(state);
}

async function start() {
  const { mode, fixtureCase } = await getMode();
  toggle.checked = mode === "fixture";
  caseSelect.value = fixtureCase;
  caseSelect.disabled = mode !== "fixture";

  toggle.addEventListener("change", async () => {
    await setMode(toggle.checked ? "fixture" : "live", caseSelect.value);
    caseSelect.disabled = !toggle.checked;
    await recheck();
  });

  caseSelect.addEventListener("change", async () => {
    await setMode(toggle.checked ? "fixture" : "live", caseSelect.value);
    await recheck();
  });

  await load();
}

start();

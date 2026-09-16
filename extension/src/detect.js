// Runs inside every page. Decides one thing: is this a job post, and if so,
// what is its text.
//
// This is a content script, not a module. Content scripts run in an isolated
// world with no `import`, so everything it needs is in this one file and it
// talks to the rest of the extension only by message.
//
// It makes no network call of any kind. It reads the page you are already
// looking at, signed in, in your own browser. Nothing is scraped and no terms
// are broken -- which is the whole argument for an extension over a crawler.

(function () {
  "use strict";

  // Sites where the URL alone settles it. Cheap, and right nearly always.
  const URL_RULES = [
    /linkedin\.com\/jobs\/view\//,
    /linkedin\.com\/jobs\/collections\/.*currentJobId=/,
    /linkedin\.com\/jobs\/search\/.*currentJobId=/,
    /linkedin\.com\/jobs\/search-results\/.*currentJobId=/,
    /boards\.greenhouse\.io\/.+\/jobs\/\d+/,
    /job-boards\.greenhouse\.io\/.+\/jobs\/\d+/,
    /jobs\.lever\.co\/[^/]+\/[0-9a-f-]{8,}/,
    /jobs\.ashbyhq\.com\/[^/]+\/[0-9a-f-]{8,}/,
    // Ashby embedded in a company's own careers page. The job id is the whole
    // rule: an index page never carries one, so this cannot fire on a board.
    // Not tied to a host, because the point of an embed is that the host is
    // the company's own domain.
    /[?&]ashby_jid=[0-9a-f-]{8,}/,
    /\.workable\.com\/j\//,
    /myworkdayjobs\.com\/.+\/job\//,
    /smartrecruiters\.com\/.+\/\d{6,}/,
    /indeed\.com\/viewjob/,
    /wellfound\.com\/(jobs|company\/.+\/jobs)\//,
    /greenhouse\.io\/embed\/job_app/,
  ];

  // Everywhere else, the shape of the page has to earn it. These are the
  // headings a job post has and a blog post about jobs does not.
  const SHAPE_WORDS = [
    "responsibilities",
    "qualifications",
    "what you'll do",
    "what you will do",
    "requirements",
    "who you are",
    "about the role",
    "years of experience",
    "nice to have",
    "benefits",
    "equal opportunity",
    "apply now",
    "full-time",
    "salary",
  ];

  // Known sites, and only known sites. A fast path, nothing more: when one of
  // these matches we skip the scoring below, and when none does the scorer
  // does the whole job. `article` and `main` used to sit at the end of this
  // list and that is precisely what broke it -- on LinkedIn and on Ashby a
  // catch-all matched, swallowed the sidebar and the footer, and the
  // pre-screen counted the navigation as requirements.
  const POST_SELECTORS = [
    ".jobs-description__content",
    ".jobs-box__html-content",
    "#job-details",
    "[data-automation-id='jobPostingDescription']",
    "#content .section-wrapper",
    ".posting-page",
    "#job_description",
    ".job-description",
    "[class*='jobDescription']",
  ];

  // The fast path is a convenience and never a crutch. Turned off, everything
  // below still has to work: that is how this file is measured.
  const USE_KNOWN_SELECTORS = true;

  // A post longer than this is almost certainly the whole page, headers and
  // footers included. The backend tokenises it either way; the cap is here so
  // a 400kB page does not travel through a message port for nothing.
  const MAX_POST_CHARS = 30000;

  // -- The general scorer ---------------------------------------------------
  //
  // Navigation, sidebars and related-job lists are mostly links. A job
  // description is mostly prose. So score every block on two numbers -- how
  // much text it holds, and what fraction of that text sits inside an <a> --
  // and take the winner. This is the core of what Firefox Reader Mode does,
  // minus everything a general reading mode needs and this does not.

  // Never the job post, whatever it scores. Removed before anything is
  // measured, so a nav bar cannot lend its length to the block around it.
  const FURNITURE =
    "nav, header, footer, aside, script, style, form, noscript, template, " +
    "[role='navigation'], [role='banner'], [role='contentinfo'], " +
    "[role='complementary'], [role='search']";

  // The blocks worth scoring. Inline elements hold no structure and the body
  // itself is the thing we are trying to avoid returning.
  const BLOCKS = "article, main, section, div, td";

  // Below this a block is a byline or a button row, not a description.
  const MIN_BLOCK_CHARS = 400;

  // Half the characters inside links is navigation by any reading. Rejected
  // outright rather than scored, so no amount of length can buy it back.
  const MAX_LINK_DENSITY = 0.5;

  // Longer is better, up to a point. Past this, extra length is the rest of
  // the page arriving, so it stops counting.
  const LENGTH_CAP = 12000;

  // A list item this much of which sits inside a link is a card -- a related
  // job, a "people also viewed" -- and the whole card counts as link text.
  // Measured, not guessed: a reconstruction whose cards wrapped the title
  // only, and left the company and the location outside the anchor, read as
  // prose and pushed the pre-screen count from 57 to 83. Counting the card
  // rather than the anchor is the same rule applied one level up.
  const CARD_LINK_SHARE = 0.3;

  function visibleText(node) {
    return (node.innerText || "").replace(/\s+\n/g, "\n").trim();
  }

  // The furniture directly under `node` -- directly meaning not already
  // inside other furniture, so nested nav inside a footer is counted once.
  function furnitureIn(node) {
    const out = [];
    for (const junk of node.querySelectorAll(FURNITURE)) {
      const parent = junk.parentElement;
      if (parent && parent.closest(FURNITURE)) continue;
      out.push(junk);
    }
    return out;
  }

  // Scoring reads `textContent`, not `innerText`, on purpose. `innerText`
  // asks for layout, and this runs on every block of every page once a
  // second; `textContent` is a string walk. The winner alone pays for
  // layout, because only the winner's line breaks matter.
  function linkChars(node) {
    let total = 0;
    const spent = new Set();
    for (const item of node.querySelectorAll("li")) {
      if (item.closest(FURNITURE)) continue;
      // Only the outermost item of a nested list, or its text is counted
      // twice.
      if (item.parentElement && item.parentElement.closest("li")) continue;
      const chars = item.textContent.length;
      if (!chars) continue;
      const anchors = item.querySelectorAll("a");
      let inside = 0;
      for (const a of anchors) inside += a.textContent.length;
      if (inside && inside / chars >= CARD_LINK_SHARE) {
        total += chars;
        for (const a of anchors) spent.add(a);
      }
    }
    for (const a of node.querySelectorAll("a")) {
      if (a.closest(FURNITURE) || spent.has(a)) continue;
      total += a.textContent.length;
    }
    return total;
  }

  function measure(node) {
    let chars = node.textContent.length;
    for (const j of furnitureIn(node)) chars -= j.textContent.length;
    return { chars, density: chars > 0 ? linkChars(node) / chars : 1 };
  }

  // The prose fraction cubed. Squared was not enough: a wrapper holding the
  // description *and* a related-jobs list is longer than the description, and
  // a gentle penalty lets that length win. Cubed, a third of the characters
  // being links costs two thirds of the score, and the description wins.
  function scoreOf({ chars, density }) {
    if (chars < MIN_BLOCK_CHARS) return 0;
    if (density >= MAX_LINK_DENSITY) return 0;
    const prose = 1 - density;
    return Math.min(chars, LENGTH_CAP) * prose * prose * prose;
  }

  // The text of the winner, with its furniture cut back out. Subtracting each
  // piece's own `innerText` from the parent's keeps the line breaks that
  // survive, and line breaks are what the pre-screen counts on.
  function textWithoutFurniture(node) {
    let text = node.innerText || "";
    for (const junk of furnitureIn(node)) {
      const inner = junk.innerText;
      if (!inner) continue;
      const at = text.indexOf(inner);
      if (at === -1) continue;
      text = text.slice(0, at) + "\n" + text.slice(at + inner.length);
    }
    return text.replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function bestBlock() {
    let best = null;
    let bestScore = 0;
    for (const node of document.body.querySelectorAll(BLOCKS)) {
      if (node.closest(FURNITURE)) continue;
      if (node.textContent.length < MIN_BLOCK_CHARS) continue;
      const score = scoreOf(measure(node));
      if (score > bestScore) {
        bestScore = score;
        best = node;
      }
    }
    return best;
  }

  function computePost() {
    if (USE_KNOWN_SELECTORS) {
      for (const selector of POST_SELECTORS) {
        const node = document.querySelector(selector);
        if (node) {
          const text = visibleText(node);
          if (text.length > MIN_BLOCK_CHARS) return text.slice(0, MAX_POST_CHARS);
        }
      }
    }
    const winner = bestBlock();
    if (winner) return textWithoutFurniture(winner).slice(0, MAX_POST_CHARS);
    // Nothing scored. The whole body is a poor answer and it is the honest
    // one: detection still has to decide, and it decides on what it can see.
    return visibleText(document.body).slice(0, MAX_POST_CHARS);
  }

  // Scoring touches every block on the page, and `look()` runs once a second.
  // The page's total text length is a cheap stand-in for "did anything
  // change": on LinkedIn it changes the moment another job is clicked, which
  // is the only time the answer can differ.
  let cached = { key: null, post: "" };

  function extractPost() {
    const key = location.href + "|" + document.body.textContent.length;
    if (key === cached.key) return cached.post;
    const post = computePost();
    cached = { key, post };
    return post;
  }

  function urlSaysJobPost() {
    return URL_RULES.some((rule) => rule.test(location.href));
  }

  function shapeSaysJobPost(text) {
    const lower = text.toLowerCase();
    const hits = SHAPE_WORDS.filter((word) => lower.includes(word)).length;
    // Four signals, not three. Getting it wrong quietly is fine. Getting it
    // wrong loudly -- a badge lighting up on a news article -- is what makes
    // people uninstall an extension, so the bar without a URL match is high.
    return hits >= 4 && text.length > 1200;
  }

  function look() {
    const byUrl = urlSaysJobPost();
    const post = extractPost();
    const byShape = shapeSaysJobPost(post);
    return {
      kind: "page-state",
      isJobPost: byUrl || byShape,
      how: byUrl ? "url" : byShape ? "shape" : "none",
      url: location.href,
      title: document.title,
      post: byUrl || byShape ? post : "",
    };
  }

  let lastSent = "";

  function report() {
    const state = look();
    // The post text changes as a page finishes loading. Only send when the
    // answer actually changed, or the service worker is woken for nothing.
    const stamp = state.url + "|" + state.isJobPost + "|" + state.post.length;
    if (stamp === lastSent) return;
    lastSent = stamp;
    chrome.runtime.sendMessage(state).catch(() => {
      // The worker was asleep and the message was dropped. The panel asks for
      // a fresh look when it opens, so nothing is lost.
    });
  }

  // LinkedIn is a single page app: clicking the next job in the list changes
  // the URL and the whole description without ever loading a document. There
  // is no reliable event for that from an isolated world -- patching
  // history.pushState there does not reach the page's own copy -- so we look
  // every second. One string comparison, and it stops sending when nothing
  // moved.
  report();
  setInterval(report, 1000);

  chrome.runtime.onMessage.addListener((message, sender, reply) => {
    if (message.kind === "look-again") {
      lastSent = "";
      cached = { key: null, post: "" };
      reply(look());
    }
    return true;
  });
})();

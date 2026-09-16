// One place for everything that would otherwise be a magic string.
//
// The only host this extension may ever talk to is the audit server on this
// machine. Decision 0002. `manifest.json` enforces it for real: `host_permissions`
// lists localhost and nothing else, so a fetch anywhere else fails in Chrome
// before it reaches the network.

export const BACKEND = "http://localhost:8000";

// How long we wait on the server before calling it down. The pre-screen is
// BM25 only -- milliseconds -- so anything past two seconds means the server
// is not there, not that it is thinking.
export const TIMEOUT_MS = 2000;

// "live"     talk to the server
// "fixture"  read extension/fixtures/*.json instead
//
// Deliberately NOT an automatic fallback. A panel that silently shows invented
// numbers when the server is down is the worst thing this could do in a live
// demo -- you would read fabricated results out loud believing they were real.
// So the mode is a switch a person flips, and the panel says FIXTURES in the
// header the whole time it is on.
export const DEFAULT_MODE = "live";

// Which fixture set to show. Each one exists to prove a state renders.
//
// Four, not three. `quick-match` was added when decision 0006 gave the panel a
// live summary: "this post has not been audited yet" became a real state with
// its own screen rather than the only thing live mode could ever show.
//
// Two of the six panel states are deliberately not in here. "No job post on
// this page" is decided by the content script, and "Vouch is not running" is
// what live mode does when nothing answers -- making either one a fixture case
// would mean the panel could show them while they were not true.
export const FIXTURE_CASES = {
  "full": { summary: "summary.json", resumes: "resumes.json" },
  "no-blockers": { summary: "summary-clear.json", resumes: "resumes.json" },
  "quick-match": { summary: "summary-unknown.json", resumes: "resumes.json" },
  "no-resume": { summary: "summary.json", resumes: "resumes-empty.json" },
};

export async function getMode() {
  const stored = await chrome.storage.local.get(["mode", "fixtureCase"]);
  return {
    mode: stored.mode || DEFAULT_MODE,
    fixtureCase: stored.fixtureCase || "full",
  };
}

export async function setMode(mode, fixtureCase) {
  await chrome.storage.local.set({ mode, fixtureCase });
}

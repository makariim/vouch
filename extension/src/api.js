// Everything that leaves this extension. Three endpoints and a file read.
//
// No model call happens here and none ever can: there is no key in this
// codebase and no host but localhost is reachable. The one-minute audit is not
// in this file at all -- the extension opens the page for that.

import { BACKEND, TIMEOUT_MS, FIXTURE_CASES } from "./config.js";

// A failed fetch and a 500 are the same thing to the panel: the server is not
// answering. We return a shape rather than throwing, because every caller
// wants to render the failure calmly rather than handle an exception.
async function ask(path, options = {}) {
  const abort = new AbortController();
  const timer = setTimeout(() => abort.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(BACKEND + path, {
      ...options,
      signal: abort.signal,
    });
    if (!response.ok) {
      return { ok: false, reason: "refused", status: response.status };
    }
    return { ok: true, data: await response.json() };
  } catch (error) {
    return { ok: false, reason: "unreachable" };
  } finally {
    clearTimeout(timer);
  }
}

function post(path, body) {
  return ask(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function fixture(name) {
  // A file inside the extension. chrome-extension:// is not the network, so
  // this works with the server down, on a plane, in the room.
  return fetch(chrome.runtime.getURL("fixtures/" + name)).then((r) => r.json());
}

// Decision 0005:
//   POST /prescreen {"post": "...", "resume_id": "default"}
//     -> {"signal": "worth_a_look|maybe|skip", "matched": 14, "total": 21}
//
// `signal` is a closed set, written down in decision 0006 section 5.
export async function prescreen(post_, mode, fixtureCase) {
  if (mode === "fixture") {
    return { ok: true, data: await fixture("prescreen.json") };
  }
  return post("/prescreen", { post: post_, resume_id: "default" });
}

// Decision 0005: GET /resumes. The extension reads this list and never writes
// to it. It does not hold, store or send a resume -- the backend owns that.
export async function resumes(mode, fixtureCase) {
  if (mode === "fixture") {
    const file = FIXTURE_CASES[fixtureCase].resumes;
    return { ok: true, data: await fixture(file) };
  }
  return ask("/resumes");
}

// Decision 0006 section 1, and the reason the panel works at all:
//
//   POST /summary {"post": "...", "resume_id": "default"}
//     ->  the stored summary event, or {"known": false}
//
// Brief 0008 found the hole this closes: `summary` only ever existed inside
// the audit stream, and the panel may not start an audit. So in live mode the
// panel could show a word count and nothing else.
//
// Three answers, and the panel renders a different state for each:
//
//   known      the post has been audited -> show the whole answer
//   not known  it has not -> show the word match and the button
//   no server  -> say so. Never a fixture, never a guess.
//
// THE 404. As of this writing the route does not exist in src/audit/server.py
// -- brief 0012 owns building it. A 404 is therefore "the server is up and
// this post has not been audited", which is the same screen as `known: false`
// and is the honest one: no stored answer is reachable either way. It is
// reported separately from a real `known: false` so the difference stays
// visible rather than being quietly absorbed.
export async function summary(post_, resumeId, mode, fixtureCase) {
  if (mode === "fixture") {
    const file = FIXTURE_CASES[fixtureCase].summary;
    const data = await fixture(file);
    if (data.known === false) return { ok: true, known: false };
    return { ok: true, known: true, data };
  }

  const result = await post("/summary", { post: post_, resume_id: resumeId });

  if (!result.ok) {
    if (result.status === 404) return { ok: true, known: false, missing: true };
    return result;
  }
  if (!result.data || result.data.known === false) {
    return { ok: true, known: false };
  }
  return { ok: true, known: true, data: result.data };
}

export function defaultResume(list) {
  if (!list || !list.resumes || list.resumes.length === 0) return null;
  return list.resumes.find((r) => r.default) || null;
}

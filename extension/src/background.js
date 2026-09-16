// The service worker. Owns the badge, and runs the pre-screen.
//
// An MV3 service worker is not a background page: Chrome stops it after about
// thirty seconds of quiet and starts it again on the next event. So nothing
// may live in a module-level variable -- a Map here would be empty half the
// time. State goes in chrome.storage.session, which survives the worker
// sleeping and is thrown away when the browser closes.

import { getMode } from "./config.js";
import { prescreen, resumes, defaultResume } from "./api.js";

// Two states, and only two. Decision in the brief: no notifications, no popup
// per job post. A dot that appears is the entire interruption this thing is
// allowed to make.
//
// The dot is drawn into the icon rather than set as badge text. That is what
// design/canvas/Extension.dc.html shows -- a 7px rose dot on the corner of the
// mark -- and design/assets/favicon.svg says the same in words: "the extension
// draws a 7px --v-agent dot over the bottom-right corner. That dot is drawn by
// the extension, not by this file." Chrome's own badge is a coloured pill with
// text in it and cannot be either of those, so it is not used at all.
//
// Quiet is not an absence: it is a second drawing, the mark in --v-ink-520.
// Both sets are made by extension/tools/make-icons.py.
const ICON_QUIET = {
  16: "/icons/icon-16.png",
  32: "/icons/icon-32.png",
  48: "/icons/icon-48.png",
  128: "/icons/icon-128.png",
};
const ICON_FOUND = {
  16: "/icons/icon-on-16.png",
  32: "/icons/icon-on-32.png",
  48: "/icons/icon-on-48.png",
  128: "/icons/icon-on-128.png",
};

async function saveTab(tabId, state) {
  await chrome.storage.session.set({ ["tab:" + tabId]: state });
}

async function loadTab(tabId) {
  const key = "tab:" + tabId;
  const stored = await chrome.storage.session.get(key);
  return stored[key] || null;
}

async function setBadge(tabId, on) {
  // Per tab. Two job boards in two tabs must not share one answer.
  await chrome.action.setIcon({ tabId, path: on ? ICON_FOUND : ICON_QUIET });
  await chrome.action.setTitle({
    tabId,
    title: on ? "Vouch — a job post is on this page" : "Vouch",
  });
}

// The pre-screen is BM25 only -- no model call, no cost, milliseconds. That is
// the entire reason it is allowed to run by itself while you scroll a job
// board. The 58-second audit is never run from here. Decision 0005 calls this
// the two speeds, and this function is the fast one.
async function runPrescreen(tabId, state) {
  const { mode, fixtureCase } = await getMode();

  const resumeList = await resumes(mode, fixtureCase);
  const chosen = resumeList.ok ? defaultResume(resumeList.data) : null;

  if (resumeList.ok && !chosen) {
    // No default resume. Nothing to pre-screen against, and we do not ask for
    // a paste -- the page owns resumes.
    await saveTab(tabId, { ...state, backend: "up", resume: null, prescreen: null });
    return;
  }
  if (!resumeList.ok) {
    await saveTab(tabId, {
      ...state,
      backend: resumeList.reason,
      status: resumeList.status,
      resume: null,
      prescreen: null,
    });
    return;
  }

  const result = await prescreen(state.post, mode, fixtureCase);
  await saveTab(tabId, {
    ...state,
    backend: result.ok ? "up" : result.reason,
    status: result.status,
    resume: chosen,
    prescreen: result.ok ? result.data : null,
  });
}

// Ask the page directly. Needed because the worker sleeps: a content script
// that reported while the worker was down had its message dropped, and the
// panel would then say "no job post" on an obvious job post. So when there is
// nothing stored, we go and look rather than believe the absence.
async function freshLook(tabId) {
  try {
    const seen = await chrome.tabs.sendMessage(tabId, { kind: "look-again" });
    if (!seen) return null;
    const state = {
      isJobPost: seen.isJobPost,
      how: seen.how,
      url: seen.url,
      title: seen.title,
      post: seen.post,
      checkedAt: Date.now(),
    };
    await setBadge(tabId, state.isJobPost);
    await saveTab(tabId, state);
    if (state.isJobPost) await runPrescreen(tabId, state);
    return await loadTab(tabId);
  } catch (error) {
    // No content script in this tab -- a chrome:// page, the web store, a PDF.
    return null;
  }
}

chrome.runtime.onMessage.addListener((message, sender, reply) => {
  if (message.kind === "page-state" && sender.tab) {
    const tabId = sender.tab.id;
    (async () => {
      await setBadge(tabId, message.isJobPost);
      const state = {
        isJobPost: message.isJobPost,
        how: message.how,
        url: message.url,
        title: message.title,
        post: message.post,
        checkedAt: Date.now(),
      };
      await saveTab(tabId, state);
      if (message.isJobPost) await runPrescreen(tabId, state);
    })();
    return false;
  }

  if (message.kind === "get-state") {
    (async () => {
      const state = await loadTab(message.tabId);
      reply(state || (await freshLook(message.tabId)));
    })();
    return true; // keeps the port open for the async reply
  }

  if (message.kind === "recheck") {
    // Always goes back to the page. The panel calls this when the mode switch
    // moves or after the server was started, and both mean the stored answer
    // is stale rather than missing.
    (async () => {
      reply(await freshLook(message.tabId));
    })();
    return true;
  }

  return false;
});

chrome.tabs.onRemoved.addListener((tabId) => {
  chrome.storage.session.remove("tab:" + tabId);
});

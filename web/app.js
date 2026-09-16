/* Vouch — the page.
 *
 * Two sources, one renderer. A recording replays from disk with a delay between
 * events; a real run reads the stream. Both push the same event objects through
 * render(), so whatever works in the room works in both.
 *
 * Three levels of reading, and the page is built around them:
 *   one glance   the call, one sentence, three counts
 *   five seconds the few things that decide it
 *   if you ask   the working, folded away, opening by itself only while the
 *                run is going
 *
 * This file renders judgements. It never makes one. The call, the gaps, the
 * lines to fix and the strong lines all arrive in the `summary` event.
 */

'use strict';

// Where a recording might be, depending on who is serving the page: opened from
// the web folder, or served at / by the backend. First one that parses wins.
var FIXTURES = {
  summary: {
    label: 'something to fix',
    paths: ['fixtures/trace-summary.json', 'web/fixtures/trace-summary.json',
            '/fixtures/trace-summary.json']
  },
  clean: {
    label: 'nothing to fix',
    paths: ['fixtures/trace-clean.json', 'web/fixtures/trace-clean.json',
            '/fixtures/trace-clean.json']
  },
  // The first recording, from before decision 0005. No `required`, no
  // `summary`. It is kept so a regression in the old path is visible.
  recorded: {
    label: 'the first recording',
    paths: ['../fixtures/trace-sample.json', 'fixtures/trace-sample.json',
            '/fixtures/trace-sample.json']
  }
};

var RERUN_PATHS = ['fixtures/rerun.json', 'web/fixtures/rerun.json',
                   '/fixtures/rerun.json'];

// Decision 0006 names this endpoint and says it re-emits `summary` when it
// finishes. Before 0006 there was nothing to call and this line was a guess.
var RERUN_ENDPOINT = '/audit/requirement';

var STEP_DELAY = 420;   // ms between recorded events: fast enough to feel live,
                        // slow enough that a change of mind is readable.

// The three answers. Never a fourth.
var ANSWER_WORD = {
  evidenced:        'Your resume shows this',
  partly_evidenced: 'Your resume shows part of this',
  not_evidenced:    'Your resume does not show this'
};

var COUNT_WORD = {
  evidenced:        'your resume shows',
  partly_evidenced: 'shows part of it',
  not_evidenced:    'does not show'
};

var FIT_WORD = {
  strong:         'Strong fit.',
  worth_applying: 'Worth applying.',
  weak:           'Weak fit.'
};

// No digits where a word will do. Line numbers and elapsed seconds stay digits;
// a count of things they asked for reads better spelled out.
var NUMBER_WORD = ['no', 'one', 'two', 'three', 'four', 'five',
                   'six', 'seven', 'eight', 'nine', 'ten'];

function words(n) { return n >= 0 && n < NUMBER_WORD.length ? NUMBER_WORD[n] : String(n); }

var el = {
  post:        document.getElementById('post'),
  resume:      document.getElementById('resume'),
  postFoot:    document.getElementById('post-foot'),
  resumeFoot:  document.getElementById('resume-foot'),
  run:         document.getElementById('run'),
  runNote:     document.getElementById('run-note'),
  fixture:     document.getElementById('fixture'),
  status:      document.getElementById('status'),
  intro:       document.getElementById('intro'),
  banner:      document.getElementById('banner'),
  audit:       document.getElementById('audit'),
  live:        document.getElementById('live'),
  liveTitle:   document.getElementById('live-title'),
  liveMeta:    document.getElementById('live-meta'),
  liveHead:    document.getElementById('live-headline'),
  summary:     document.getElementById('summary'),
  workings:    document.getElementById('workings'),
  listToggle:  document.getElementById('list-toggle'),
  listChev:    document.getElementById('list-chev'),
  listHint:    document.getElementById('list-hint'),
  listMeta:    document.getElementById('list-meta'),
  list:        document.getElementById('list'),
  errorPreview: document.getElementById('error-preview'),

  // brief 0019: the two places a recording says so
  recording:   document.getElementById('recording'),
  auditFlag:   document.getElementById('audit-recording'),

  // brief 0017: the resume as a file
  drop:        document.getElementById('drop'),
  file:        document.getElementById('file'),
  resumeCard:  document.getElementById('resume-card'),
  resumeName:  document.getElementById('resume-name'),
  resumeMeta:  document.getElementById('resume-meta'),
  resumeFixed: document.getElementById('resume-repaired'),
  resumeOpen:  document.getElementById('resume-open'),
  resumeDrop:  document.getElementById('resume-drop'),
  resumeClash: document.getElementById('resume-clash'),
  resumeBlock: document.getElementById('resume-block'),
  uploadWrong: document.getElementById('upload-wrong'),
  resumeView:  document.getElementById('resume-view'),
  resumeTitle: document.getElementById('resume-view-title'),
  resumeBack:  document.getElementById('resume-back'),
  repairs:     document.getElementById('repairs'),
  resumeLines: document.getElementById('resume-lines')
};

var rows = {};        // requirement id -> its DOM node
var body = {};        // requirement id -> the column inside that row
var traces = {};      // requirement id -> the trace block being filled now
var turned = {};      // requirement id -> did this pass change its mind
var req = {};         // requirement id -> {text, required, n}
var order = [];       // requirement ids, in the order they arrived
var verdicts = {};    // requirement id -> the last verdict event for that row
var terms = {};       // requirement id -> every search term used on that row
var counts = null;    // the last counts we were given
var summaryEv = null; // the last summary event we were given

var phase = 'empty';  // empty | ready | running | done | again | error
var running = false;
var cancelled = false;
var againTarget = null;   // set while one requirement is being looked at again
var listOpen = false;
var listTouched = false;  // has a person opened or closed it themselves
var startedAt = 0;
var ticker = null;

/* ---- the stored resume, brief 0017 --------------------------------------
 * `stored` is what POST /resumes gave back for the file on screen. `ranAgainst`
 * is the resume the answers below were actually produced from -- the stored id,
 * or '' for pasted text. They are two different things on purpose: the resume
 * view may only colour a line if the run it is colouring came from the same
 * document. Colouring the file's lines with an answer about pasted text would
 * put two copies of one resume on screen, which is the single thing this brief
 * could break. */
var stored = null;
var ranAgainst = null;
var reading = false;      // an upload is in flight
var viewing = false;      // the resume view is open over the answer
var lastRead = null;      // the last GET /resumes/{id} body, cached by id

// ---------------------------------------------------------------- the frame

function setPhase(next) {
  phase = next;
  // The resume view is a screen, not a panel: while it is open it is the only
  // thing in the column. Everything else keeps its state and comes back.
  el.resumeView.hidden = !viewing;
  el.intro.hidden = viewing || (next !== 'empty' && next !== 'ready');
  el.audit.hidden = viewing || next === 'empty' || next === 'ready' || next === 'error';
  el.banner.hidden = viewing || next !== 'error';
  el.live.hidden = next !== 'running' && next !== 'again';
  syncRun();
  syncList();
  syncHeaderNote();
}

function syncHeaderNote() {
  var total = order.length;
  var done = Object.keys(verdicts).length;
  var note;
  if (phase === 'empty')        note = 'Nothing loaded yet';
  else if (phase === 'ready')   note = 'Ready. Nothing sent anywhere yet';
  else if (phase === 'running') note = 'Working · ' + done + ' of ' + total;
  else if (phase === 'again')   note = 'Looking again at number ' + numberOf(againTarget);
  else if (phase === 'error')   note = 'Stopped at ' + done + ' of ' + total;
  else                          note = 'Finished · ' + done + ' of ' + total;
  el.status.textContent = note;
}

var RUN_STATES = {
  empty:   { label: 'Check my fit', meta: '',                kind: 'off',
             note: 'Add a resume and paste a job post first.' },
  ready:   { label: 'Check my fit', meta: 'about 1 minute',  kind: 'primary',
             note: 'You click this every time. It takes about a minute and it costs money.' },
  running: { label: 'Stop',         meta: '',                kind: 'stopping',
             note: 'Answers already on screen will stay.' },
  done:    { label: 'Check it again', meta: 'about 1 minute', kind: 'secondary',
             note: 'Or look again at one single thing, further down.' },
  again:   { label: 'Check it again', meta: '',              kind: 'off',
             note: 'One thing is being looked at again. The other answers do not change.' },
  error:   { label: 'Check my fit', meta: 'about 1 minute',  kind: 'primary',
             note: 'The answers already on screen survived.' }
};

function syncRun() {
  var s = RUN_STATES[phase] || RUN_STATES.ready;
  el.run.querySelector('.run-label').textContent = s.label;
  el.run.querySelector('.run-meta').textContent = s.meta;
  el.run.className = 'run' + (s.kind === 'primary' ? '' : ' ' + s.kind);
  el.run.disabled = s.kind === 'off';
  el.runNote.textContent = s.note;
}

// Nothing is ready to run until there is something to run it on. In recorded
// mode there always is: the recording is the input.
function syncReady() {
  var filled = el.post.value.trim() && (el.resume.value.trim() || (stored && stored.id));
  if (mode() === 'fixture') filled = true;
  if (phase === 'empty' && filled) setPhase('ready');
  else if (phase === 'ready' && !filled) setPhase('empty');
  else if (phase === 'ready' || phase === 'empty') syncRun();
}

function syncWells() {
  [el.post, el.resume].forEach(function (box) {
    box.classList.toggle('filled', box.value.trim().length > 0);
  });
  var lines = el.resume.value.trim() ? el.resume.value.split('\n').length : 0;
  el.resumeFoot.hidden = lines === 0;
  el.resumeFoot.textContent = lines + (lines === 1 ? ' line' : ' lines') +
                              (stored ? ' pasted' : ' · this is what we quote from');
  if (el.resumeClash) el.resumeClash.hidden = !(stored && lines > 0);
}

// ---------------------------------------------------------------- level three

function syncList() {
  // It opens by itself while the run is going, because that minute is the
  // interesting part. Once a person touches it, their choice wins.
  var auto = phase === 'running' || phase === 'again';
  var open = listTouched ? listOpen : auto;
  listOpen = open;

  el.workings.hidden = order.length === 0;
  el.list.hidden = !open;
  el.listHint.hidden = open;
  el.listChev.textContent = open ? '▾' : '▸';
  el.listToggle.setAttribute('aria-expanded', open ? 'true' : 'false');

  var total = order.length;
  var done = Object.keys(verdicts).length;
  var meta;
  if (phase === 'running') meta = done + ' done · 1 in hand · ' + Math.max(0, total - done - 1) + ' waiting';
  else if (phase === 'again') meta = (total - 1) + ' settled · 1 being looked at again';
  else if (done === 0) meta = 'none checked yet';
  else meta = done + ' of ' + total + ' checked';
  el.listMeta.textContent = meta;
}

el.listToggle.addEventListener('click', function () {
  listTouched = true;
  listOpen = !listOpen;
  syncList();
});

// ---------------------------------------------------------------- the mark

function mark(kind, extra) {
  var box = document.createElement('span');
  box.className = 'mark ' + kind + (extra ? ' ' + extra : '');
  box.setAttribute('aria-hidden', 'true');
  ['arm-l', 'arm-r', 'fill'].forEach(function (part) {
    var piece = document.createElement('i');
    piece.className = part;
    box.appendChild(piece);
  });
  return box;
}

function setMark(row, kind, extra) {
  var next = mark(kind, extra);
  row.replaceChild(next, row.querySelector('.mark'));
}

// ---------------------------------------------------------------- a quote

function quoteBlock(line, lineNumber, kind, caption) {
  // Word for word. No italics, no smart quotes, no trimming: pre-wrap in the
  // stylesheet keeps the resume's own spacing, and nothing here touches it.
  var box = document.createElement('div');
  box.className = 'quote' + (kind ? ' ' + kind : '');

  var where = document.createElement('span');
  where.className = 'where';
  where.textContent = lineNumber === undefined || lineNumber === null
    ? caption
    : 'Line ' + lineNumber + ', ' + caption;
  box.appendChild(where);

  var words_ = document.createElement('p');
  words_.className = 'words';
  words_.textContent = line;
  box.appendChild(words_);
  return box;
}

// ---------------------------------------------------------------- rendering

function reset() {
  rows = {}; body = {}; traces = {}; turned = {};
  req = {}; order = []; verdicts = {}; terms = {};
  counts = null; summaryEv = null; againTarget = null;
  listTouched = false;
  el.list.innerHTML = '';
  el.summary.hidden = true;
  el.summary.innerHTML = '';
  el.summary.classList.remove('behind');
  el.banner.innerHTML = '';
  el.postFoot.hidden = true;
}

function numberOf(id) { return req[id] ? req[id].n : id; }

function renderRequirements(items) {
  // One row per requirement, up front and waiting. They fill in as events
  // arrive, so nothing waits on anything else.
  //
  // This has to survive being sent the list twice. POST /audit/requirement
  // opens with its own `requirements` event naming the one requirement it is
  // re-checking, and an id we have already drawn must land in the row that is
  // already on screen -- not a second copy of it below the other four.
  var fresh = order.length === 0;
  var required = 0;
  items.forEach(function (item, i) {
    if (rows[item.id]) return;                // already drawn. Leave it alone.
    var isRequired = item.required !== false;   // decision 0006: absent means
                                                // required. The safe reading.
    if (isRequired) required += 1;
    req[item.id] = { text: item.text, required: isRequired, n: i + 1 };
    order.push(item.id);

    var row = document.createElement('article');
    row.className = 'req waiting';
    row.appendChild(mark('not_evidenced', 'quiet'));

    var col = document.createElement('div');
    col.className = 'req-body';

    var head = document.createElement('div');
    head.className = 'req-head';

    var text = document.createElement('span');
    text.className = 'req-text';
    text.textContent = item.text;
    head.appendChild(text);

    // A nice-to-have they do not have must not read like a thing they require.
    if (item.required !== undefined) {
      var kind = document.createElement('span');
      kind.className = 'kind';
      kind.textContent = isRequired ? 'Required' : 'Nice to have';
      head.appendChild(kind);
    }

    col.appendChild(head);
    row.appendChild(col);
    rows[item.id] = row;
    body[item.id] = col;
    el.list.appendChild(row);
  });

  // Only the opening list describes the post. A single-requirement re-check
  // must not rewrite it to "1 thing they ask for".
  if (fresh) {
    el.postFoot.hidden = false;
    el.postFoot.textContent = items.length + ' things they ask for · ' +
      required + ' required, ' + (items.length - required) + ' nice to have';
  }

  syncList();
  syncHeaderNote();
}

// ---- the trace, in sentences -------------------------------------------

function newTrace(id) {
  var box = document.createElement('div');
  box.className = 'trace';
  body[id].appendChild(box);
  traces[id] = box;
  turned[id] = false;
  return box;
}

function traceLine(id, text, kind) {
  var box = traces[id] || newTrace(id);
  // Only one line is ever the live one. The one before it settles into history.
  var was = box.querySelector('p.now');
  if (was) was.className = '';
  var p = document.createElement('p');
  if (kind) p.className = kind;
  p.textContent = text;
  box.appendChild(p);
}

// The closed set from decision 0006, turned into plain sentences. The detail
// is the backend's own words and is printed as it arrived.
function sentence(step, detail) {
  var d = detail || '';
  switch (step) {
    case 'search':  return d ? 'It searched your resume for: ' + d : 'It searched your resume.';
    case 'judge':   return d ? 'It is deciding: ' + d : 'It is deciding.';
    case 'verify':  return d ? 'It is checking the line really is in your resume: ' + d
                             : 'It is checking the line really is in your resume.';
    case 'retry':   return d ? 'It threw away its own answer and is searching again: ' + d
                             : 'It threw away its own answer and is searching again.';
    case 'failed':  return d ? 'This one failed: ' + d : 'This one failed.';
    case 'dropped': return d ? 'It dropped this one: ' + d : 'It dropped this one.';
    default:        return d ? step + ': ' + d : step;
  }
}

function renderStep(ev) {
  var id = ev.requirement_id;
  var row = rows[id];
  if (!row) return;                       // a step for a requirement never seen

  row.classList.remove('waiting');
  row.classList.add('working');
  setMark(row, 'working');
  if (!traces[id]) newTrace(id);

  var step = ev.step || 'step';
  traceLine(id, sentence(step, ev.detail), step === 'retry' ? 'turn' : 'now');
  if (step === 'retry') turned[id] = true;

  if (step === 'search' && ev.detail) {
    var seen = terms[id] || (terms[id] = []);
    // A second look that searched for the same thing is not a second look. If
    // it happens the page says so rather than letting it slide past.
    if (seen.indexOf(ev.detail) !== -1) {
      traceLine(id, 'Those are the same words as last time.', 'turn');
    }
    seen.push(ev.detail);
  }

  liveFor(id, step);
  syncHeaderNote();
  syncList();
}

function renderVerdict(ev) {
  var id = ev.requirement_id;
  var row = rows[id];
  if (!row) return;

  var verdict = ev.verdict;
  verdicts[id] = ev;

  // Looking again replaces what was there. Nothing of the old answer survives.
  ['.said', '.quote', '.req-why', 'button.again'].forEach(function (sel) {
    var old = body[id].querySelector(sel);
    if (old) old.remove();
  });

  row.classList.remove('waiting', 'working');
  setMark(row, verdict);

  var said = document.createElement('p');
  said.className = 'said ' + verdict;
  said.textContent = ANSWER_WORD[verdict] || verdict;
  body[id].appendChild(said);

  // Only quote what the event carried, and quote nothing at all when the
  // answer is "does not show this". That silence is the product.
  if (ev.line) {
    body[id].appendChild(quoteBlock(ev.line, ev.line_number, verdict, 'word for word'));
  }

  if (ev.reason) {
    var why = document.createElement('p');
    why.className = 'req-why';
    why.textContent = ev.reason;
    body[id].appendChild(why);
  }

  // A pass that went straight through has nothing worth keeping on screen. A
  // pass where it changed its mind is the most interesting thing on the page,
  // so that one stays — as history, with the rose taken out of it.
  if (traces[id] && !turned[id]) {
    traces[id].remove();
  } else if (traces[id]) {
    row.classList.add('settled');
  }
  traces[id] = null;

  // The trace and the button sit below the reason, in that order.
  var kept = body[id].querySelector('.trace');
  if (kept) body[id].appendChild(kept);

  var again = document.createElement('button');
  again.type = 'button';
  again.className = 'again';
  again.dataset.id = id;
  again.textContent = 'Look again at this one';
  again.addEventListener('click', function () { lookAgain(id); });
  again.disabled = running;
  again.hidden = running;
  body[id].appendChild(again);

  syncHeaderNote();
  syncList();
}

// ---- the live callout ---------------------------------------------------

function liveFor(id, step) {
  if (phase !== 'running' && phase !== 'again') return;
  if (step === 'retry') {
    el.liveTitle.textContent = 'It changed its mind';
    el.liveHead.textContent = 'It threw away its own answer and is searching again.';
  } else {
    el.liveTitle.textContent = phase === 'again' ? 'Looking again' : 'Working';
    el.liveHead.textContent = req[id] ? req[id].text : 'Working.';
  }
  tick();
}

function tick() {
  var seconds = Math.max(0, Math.round((Date.now() - startedAt) / 1000));
  var done = Object.keys(verdicts).length;
  if (phase === 'again') {
    el.liveMeta.textContent = seconds + ' seconds · one of ' + order.length;
  } else {
    el.liveMeta.textContent = seconds + ' seconds · ' + done + ' of ' + order.length + ' done';
  }
  if (phase === 'running') {
    el.run.querySelector('.run-meta').textContent = seconds + ' seconds so far';
  }
}

function startClock() {
  startedAt = Date.now();
  stopClock();
  ticker = setInterval(tick, 1000);
  tick();
}
function stopClock() { if (ticker) { clearInterval(ticker); ticker = null; } }

// ---------------------------------------------------------------- the answer

function answerBlock() {
  // One structure, built once, filled by whichever events turn up. `done`
  // brings the counts; `summary` brings the call and the three sections. An
  // old recording that carries only `done` renders the counts and nothing
  // pretending to be a judgement.
  var block = el.summary.querySelector('.counts');
  if (block) return el.summary;

  var kicker = document.createElement('p');
  kicker.className = 'answer-kicker';
  kicker.textContent = 'Our answer';
  kicker.hidden = true;
  el.summary.appendChild(kicker);

  var call = document.createElement('p');
  call.className = 'call';
  call.hidden = true;
  el.summary.appendChild(call);

  var why = document.createElement('p');
  why.className = 'call-why';
  why.hidden = true;
  el.summary.appendChild(why);

  var row = document.createElement('div');
  row.className = 'counts';
  el.summary.appendChild(row);

  var behind = document.createElement('p');
  behind.className = 'behind-note';
  behind.hidden = true;
  el.summary.appendChild(behind);

  var sections = document.createElement('div');
  sections.className = 'sections';
  el.summary.appendChild(sections);

  el.summary.hidden = false;
  return el.summary;
}

function renderCounts(next) {
  counts = next;
  var block = answerBlock().querySelector('.counts');
  block.innerHTML = '';
  ['evidenced', 'partly_evidenced', 'not_evidenced'].forEach(function (k) {
    var item = document.createElement('div');
    item.className = 'count ' + k;
    item.appendChild(mark(k));

    var n = document.createElement('span');
    n.className = 'n';
    n.textContent = next[k] === undefined ? '–' : next[k];

    var label = document.createElement('span');
    label.className = 'k';
    label.textContent = COUNT_WORD[k];

    item.appendChild(n);
    item.appendChild(label);
    block.appendChild(item);
  });
  el.summary.hidden = false;
}

function tally() {
  // Counting the answers already on screen is arithmetic, not judgement. It is
  // the one thing this page works out for itself, and only after looking again
  // at one requirement, when the `done` event is behind.
  var out = { evidenced: 0, partly_evidenced: 0, not_evidenced: 0 };
  Object.keys(verdicts).forEach(function (id) {
    var v = verdicts[id].verdict;
    if (out[v] !== undefined) out[v] += 1;
  });
  return out;
}

// ---- level two: the few things that decide it --------------------------

function section(heading, lead) {
  var box = document.createElement('section');
  box.className = 'decide';

  var h = document.createElement('h2');
  h.textContent = heading;
  box.appendChild(h);

  var p = document.createElement('p');
  p.className = 'decide-lead';
  p.textContent = lead;
  box.appendChild(p);

  var items = document.createElement('div');
  items.className = 'decide-items';
  box.appendChild(items);
  return box;
}

function nothingHere(box, text) {
  var p = document.createElement('p');
  p.className = 'nothing-here';
  p.textContent = text;
  box.querySelector('.decide-items').appendChild(p);
}

// Decision 0006: all three lists carry the same five fields. The words come
// off the event. Nothing is joined against anything.
function itemText(entry)   { return entry.text || (req[entry.requirement_id] || {}).text || ''; }

function gapSection(list) {
  var n = list.length;
  var heading = n === 0
    ? 'You can show everything they need'
    : 'They need ' + words(n) + (n === 1 ? ' thing' : ' things') + ' you cannot show';
  var box = section(heading, n === 0
    ? 'Every thing they require has a line behind it.'
    : 'These are the ones that will lose you the job.');

  var items = box.querySelector('.decide-items');
  list.forEach(function (entry) {
    var item = document.createElement('div');
    item.className = 'gap-item';
    item.appendChild(mark('not_evidenced'));

    var col = document.createElement('div');
    var what = document.createElement('p');
    what.className = 'what';
    what.style.margin = '0';
    what.textContent = itemText(entry);
    col.appendChild(what);

    if (entry.reason) {
      var why = document.createElement('p');
      why.className = 'why';
      why.textContent = entry.reason;
      col.appendChild(why);
    }
    item.appendChild(col);
    items.appendChild(item);
  });
  return box;
}

function lineSection(list, heading, lead, empty, kind, caption, cls) {
  var box = section(heading, list.length ? lead : empty);
  if (!list.length) return box;

  var items = box.querySelector('.decide-items');
  list.forEach(function (entry) {
    var item = document.createElement('div');
    item.className = 'line-item ' + cls;

    if (entry.line) {
      item.appendChild(quoteBlock(entry.line, entry.line_number, kind, caption));
    } else {
      // The list named a requirement and gave no words for it. Say which
      // requirement, and do not invent a line.
      var bare = document.createElement('p');
      bare.className = 'nothing-here';
      bare.textContent = itemText(entry) ||
        ('Number ' + numberOf(entry.requirement_id) + ', with no line given.');
      item.appendChild(bare);
    }

    if (entry.reason) {
      var why = document.createElement('p');
      why.className = 'why';
      why.textContent = entry.reason;
      item.appendChild(why);
    }
    items.appendChild(item);
  });
  return box;
}

function renderSummary(ev) {
  summaryEv = ev;
  var block = answerBlock();

  var kicker = block.querySelector('.answer-kicker');
  var call = block.querySelector('.call');
  var why = block.querySelector('.call-why');

  kicker.hidden = false;
  call.hidden = false;
  call.textContent = FIT_WORD[ev.fit] || ev.fit || 'No call.';

  if (ev.fit_reason) {
    why.hidden = false;
    why.textContent = ev.fit_reason;
  }

  // Order: the call, then what stops you, then what proves you fit, then the
  // lines to fix. Every heading says what the section does.
  var sections = block.querySelector('.sections');
  sections.innerHTML = '';
  sections.appendChild(gapSection(ev.blockers || []));
  sections.appendChild(lineSection(
    ev.strengths || [],
    'This is what proves you fit',
    'Put these near the top of your letter.',
    'No single line stood out. Open the working below to see what matched.',
    'evidenced', 'word for word', 'proof'));
  sections.appendChild(lineSection(
    ev.undersells || [],
    'Fix these lines in your resume',
    'You have done these things. Your resume says them so quietly that nobody will notice.',
    'Nothing to fix. Where your resume shows something, it says so plainly.',
    'partly_evidenced', 'as it stands', 'fix'));

  block.querySelector('.behind-note').hidden = true;
  el.summary.classList.remove('behind');
  el.summary.hidden = false;
}

function markAnswerBehind(id) {
  // Looking again changes one answer. The call, the gaps and the lines to fix
  // are the backend's judgement of the whole run, and this page will not work
  // them out again — two versions of one judgement drift apart. So it says the
  // answer above is behind, rather than quietly lying.
  if (el.summary.hidden || !summaryEv) return;
  var note = el.summary.querySelector('.behind-note');
  note.hidden = false;
  note.textContent =
    'The counts now include the second look at number ' + numberOf(id) + '. ' +
    'The call and the three sections above are from the first run. We do not ' +
    'work them out again here.';
}

function renderError(message) {
  var done = Object.keys(verdicts).length;
  el.banner.innerHTML = '';

  if (order.length) {
    var where = document.createElement('p');
    where.className = 'wrong-where';
    where.textContent = 'The run stopped · ' + done + ' of ' + order.length + ' done';
    el.banner.appendChild(where);
  }

  var h = document.createElement('h2');
  h.textContent = 'The run stopped before it finished.';
  el.banner.appendChild(h);

  var lead = document.createElement('p');
  lead.className = 'wrong-lead';
  lead.textContent = done
    ? 'The ' + words(done) + ' answers already on screen are finished. They will not ' +
      'change. Nothing was guessed to fill the gap.'
    : 'Nothing was answered, and nothing was guessed to fill the gap.';
  el.banner.appendChild(lead);

  var detail = document.createElement('p');
  detail.className = 'wrong-detail';
  detail.textContent = message || 'It did not say why.';
  el.banner.appendChild(detail);

  var actions = document.createElement('div');
  actions.className = 'wrong-actions';
  var again = document.createElement('button');
  again.type = 'button';
  again.textContent = 'Start again';
  again.addEventListener('click', start);
  actions.appendChild(again);
  el.banner.appendChild(actions);

  stopClock();
  setPhase('error');
  // The answers that survived stay readable underneath.
  el.audit.hidden = viewing || order.length === 0;
  el.live.hidden = true;
}

function render(ev) {
  if (!ev || !ev.type) return;
  switch (ev.type) {
    case 'requirements': renderRequirements(ev.items || []); break;
    case 'step':         renderStep(ev); break;
    case 'verdict':      renderVerdict(ev); break;
    case 'done':         renderCounts(ev.counts || {}); break;
    case 'summary':      renderSummary(ev); break;
    case 'error':        renderError(ev.message); break;
    default:             break;   // an event type we do not know is ignored,
                                  // not guessed at
  }
}

// ---------------------------------------------------------------- recordings

function loadJson(paths, what) {
  var i = 0;
  function next() {
    if (i >= paths.length) {
      return Promise.reject(new Error(
        'Cannot read ' + what + '. Serve the repository root ' +
        '(python3 -m http.server 8000) and open /web/ from there.'));
    }
    var path = paths[i++];
    return fetch(path)
      .then(function (r) { return r.ok ? r.json() : next(); })
      .catch(next);
  }
  return next();
}

function loadFixture(which) {
  var pick = FIXTURES[which] || FIXTURES.summary;
  return loadJson(pick.paths, pick.paths[0]).then(function (data) {
    // Accept a bare array or {"events": [...]}, so a run recorded by the
    // backend drops in without touching this file.
    return Array.isArray(data) ? data : (data && data.events) || [];
  });
}

function sleep(ms) {
  return new Promise(function (resolve) { setTimeout(resolve, ms); });
}

function replay(events, stopAfter) {
  var i = 0;
  function step() {
    if (cancelled) return Promise.resolve();
    if (i >= events.length) return Promise.resolve();
    if (stopAfter !== undefined && i >= stopAfter) return Promise.resolve();
    render(events[i++]);
    return sleep(STEP_DELAY).then(step);
  }
  return step();
}

// ---------------------------------------------------------------- a real run

/* Decision 0004 says POST /audit returns text/event-stream. EventSource cannot
 * POST, so this reads the response body itself and splits SSE frames by hand.
 * It accepts a "data:" prefixed frame or a bare JSON line, because the exact
 * framing is not written down in 0004. */
function parseFrame(frame) {
  var lines = frame.split('\n');
  var payload = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line || line.charAt(0) === ':') continue;          // comment / keepalive
    if (line.indexOf('data:') === 0) payload.push(line.slice(5).trim());
    else if (line.indexOf('event:') === 0) continue;        // type is in the JSON
    else payload.push(line);                                // bare JSON line
  }
  var text = payload.join('');
  if (!text) return null;
  try { return JSON.parse(text); }
  catch (e) { return null; }                                // a half frame, skipped
}

function stream(url, payload) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
    body: JSON.stringify(payload)
  }).then(function (response) {
    if (!response.ok) {
      throw new Error('The backend answered ' + response.status + ' ' +
                      response.statusText + ' for ' + url + '.');
    }
    if (!response.body) throw new Error('This browser cannot read a streamed response.');

    var reader = response.body.getReader();
    var decoder = new TextDecoder();
    var buffer = '';

    function pump() {
      return reader.read().then(function (chunk) {
        if (cancelled) { reader.cancel(); return; }
        if (chunk.done) {
          var last = parseFrame(buffer);
          if (last) render(last);
          return;
        }
        buffer += decoder.decode(chunk.value, { stream: true });

        // Frames are separated by a blank line. Render each one the moment it
        // is whole, so the page never waits on a slow later event.
        var parts = buffer.split(/\n\n|\r\n\r\n/);
        buffer = parts.pop();
        parts.forEach(function (frame) {
          var e = parseFrame(frame);
          if (e) render(e);
        });
        return pump();
      });
    }
    return pump();
  });
}

// --------------------------------------------- looking again at one of them

function againFixture(id) {
  return loadJson(RERUN_PATHS, 'fixtures/rerun.json').then(function (data) {
    var byId = (data && data.by_requirement) || {};
    return byId[String(id)] || (data && data.default) || null;
  });
}

function lookAgain(id) {
  if (running) return;
  var row = rows[id];
  if (!row || !verdicts[id]) return;

  cancelled = false;
  running = true;
  againTarget = id;
  var sawSummary = false;
  var hadSummary = summaryEv;

  // Everything except the one being looked at steps back, and the answer above
  // dims: it is about to be behind.
  order.forEach(function (other) {
    if (String(other) !== String(id)) rows[other].classList.add('aside');
  });
  row.classList.remove('settled');
  el.summary.classList.add('behind');

  listTouched = false;
  setPhase('again');
  startClock();
  buttonsEnabled(false);
  liveFor(id, 'start');

  newTrace(id);

  var work;
  if (mode() === 'live') {
    // Decision 0006 gives this endpoint post, resume and requirement_id, and
    // says it re-emits `summary` when it is done.
    var before = summaryEv;
    // `ranAgainst`, not whatever is in the rail now: the second pass has to
    // read the document the first pass read, or its one new verdict would cite
    // line numbers from a different resume than the rows beside it.
    var again = { post: el.post.value.trim(), requirement_id: id };
    if (ranAgainst) again.resume_id = ranAgainst;
    else again.resume = el.resume.value.trim();
    work = stream(RERUN_ENDPOINT, again)
      .then(function () { sawSummary = summaryEv !== before; });
  } else {
    work = againFixture(id).then(function (pass) {
      if (!pass) throw new Error('No second look recorded for number ' + numberOf(id) + '.');
      var events = (pass.steps || []).map(function (s) {
        return { type: 'step', requirement_id: id, step: s.step, detail: s.detail };
      });
      var v = pass.verdict || {};
      if (v.verdict === 'unchanged') {
        // The second look found nothing better. Re-render the answer the page
        // already holds, with the recording's reason. No answer is invented.
        var was = verdicts[id];
        events.push({
          type: 'verdict', requirement_id: id, verdict: was.verdict,
          line: was.line, line_number: was.line_number,
          reason: v.reason || was.reason
        });
      } else if (v.verdict) {
        events.push({
          type: 'verdict', requirement_id: id, verdict: v.verdict,
          line: v.line, line_number: v.line_number, reason: v.reason
        });
      }
      return replay(events);
    });
  }

  work.then(function () {
    renderCounts(tally());
    if (hadSummary && !sawSummary) markAnswerBehind(id);
  }).catch(function (err) {
    renderError(err.message);
  }).then(function () {
    order.forEach(function (other) { rows[other].classList.remove('aside'); });
    el.summary.classList.remove('behind');
    againTarget = null;
    running = false;
    stopClock();
    if (phase !== 'error') { listTouched = false; setPhase('done'); }
    buttonsEnabled(true);
  });
}

function buttonsEnabled(on) {
  var buttons = el.list.querySelectorAll('button.again');
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].disabled = !on;
    buttons[i].hidden = !on;
  }
}

/* ============================================================================
   THE RESUME AS A FILE                                        brief 0017
   ----------------------------------------------------------------------------
   Nobody has a resume as a .txt. POST /resumes takes the PDF, pypdf pulls the
   text out, and repair puts back what extraction broke. All of that is the
   backend's, and none of it is repeated here.

   THIS FILE DOES NOT TOUCH THE TEXT. It does not trim it, join it, split it or
   clean it. Repair is mechanical and it lives in one place, because the line
   numbers every verdict cites are the numbers of the text repair produced. A
   client that also edited the text would be a second, disagreeing copy.
   ========================================================================= */

// What a refused upload says. The backend's own message decides which row --
// it is matched, never re-diagnosed -- and anything unrecognised is shown
// exactly as it arrived rather than dressed up as something we understood.
var UPLOAD_WRONG = [
  { match: 'has no extractable text',
    what:  'That PDF is a picture of your resume, not text.',
    todo:  'There is nothing in it we can read, so there is nothing we could quote. Paste the text instead.' },
  { match: 'unsupported file type',
    what:  'We can only read a PDF or a plain text file.',
    todo:  'Save your resume as a PDF and drop it here again, or paste the text instead.' },
  { match: 'could not read',
    what:  'We could not open that PDF.',
    todo:  'The file looks damaged. Save it again from the program you wrote it in, or paste the text instead.' },
  { match: 'is not UTF-8 text',
    what:  'We could not read the letters in that file.',
    todo:  'Save it as a PDF and drop that here instead.' },
  { match: 'is empty',
    what:  'There is no text in that file.',
    todo:  'Check you picked the right one, or paste the text instead.' }
];

// The kinds repair reports, in plain English. Every one of them only joins
// lines up or splits them apart; none of them changes a character.
var REPAIR_WORD = {
  'rejoin-wrap':   'A line ran off the page and carried on below. Joined back up.',
  'rejoin-hyphen': 'A word was split across a line break. Put back together.',
  'rejoin-mixed':  'Lines ran off the page and carried on below. Joined back up.',
  'split-row':     'A row of a table came out as one flat line. Split back into its cells.'
};

function showUploadWrong(message) {
  el.uploadWrong.innerHTML = '';
  if (!message) { el.uploadWrong.hidden = true; return; }

  var row = null;
  for (var i = 0; i < UPLOAD_WRONG.length; i++) {
    if (message.indexOf(UPLOAD_WRONG[i].match) !== -1) { row = UPLOAD_WRONG[i]; break; }
  }

  var what = document.createElement('p');
  what.className = 'what';
  what.textContent = row ? row.what : message;
  el.uploadWrong.appendChild(what);

  var todo = document.createElement('p');
  todo.className = 'do';
  todo.textContent = row ? row.todo : 'Paste the text instead.';
  el.uploadWrong.appendChild(todo);

  el.uploadWrong.hidden = false;
}

function syncResume() {
  el.drop.hidden = !!stored;
  el.resumeCard.hidden = !stored;

  if (stored) {
    el.resumeName.textContent = stored.name;
    el.resumeMeta.textContent = stored.lines + (stored.lines === 1 ? ' line' : ' lines') +
                                (stored.isDefault ? ' · your default' : '');
    // The repair count. It is free, and it is the only place a person is told
    // the file arrived damaged at all.
    el.resumeFixed.textContent = stored.repaired
      ? stored.repaired + (stored.repaired === 1 ? ' line' : ' lines') +
        ' came out of the file broken. We put ' +
        (stored.repaired === 1 ? 'it' : 'them') + ' back.'
      : 'Nothing came out broken, so we changed nothing.';
  }

  // Both a file and pasted text is not an error, but only one of them is going
  // to be checked, so say which.
  el.resumeClash.hidden = !(stored && el.resume.value.trim());
}

function setReading(on, name) {
  reading = on;
  el.drop.disabled = on;
  el.drop.classList.toggle('reading', on);
  el.drop.querySelector('.drop-line').textContent =
    on ? 'Reading ' + name : 'Drop a PDF here';
  el.drop.querySelector('.drop-sub').textContent =
    on ? 'It is not leaving this computer.' : 'Or click to choose one. Nothing is uploaded.';
}

function uploadResume(file) {
  if (!file || reading) return;
  showUploadWrong(null);
  setReading(true, file.name);

  var form = new FormData();
  form.append('file', file);

  fetch('/resumes', { method: 'POST', body: form })
    .then(function (response) {
      return response.text().then(function (text) {
        var data = null;
        try { data = JSON.parse(text); } catch (e) { data = null; }
        // IngestError comes back as {"error": ...} with a 400. Anything else
        // is not the resume being wrong, and must not be reported as if it was.
        if (data && data.error) throw new Error(data.error);
        if (!response.ok || !data || !data.id) {
          throw new Error('The backend answered ' + response.status + ' ' +
                          response.statusText + '. Uploading a file needs the ' +
                          'Vouch backend serving this page.');
        }
        return data;
      });
    })
    .then(function (data) {
      stored = {
        id: data.id,
        name: file.name,
        lines: data.lines,
        repaired: data.repaired,
        isDefault: data['default'] === true
      };
      lastRead = null;                 // a different document: forget the old read
      if (viewing) openResumeView();   // the view is open on the old file
    })
    .catch(function (err) {
      showUploadWrong(err.message);
    })
    .then(function () {
      setReading(false);
      syncResume();
      syncReady();
      el.file.value = '';              // so the same file can be picked twice
    });
}

/* Brief 0019: the page forgot the resume on a reload and the backend did not.
 * The file was still stored, still the default, and still what the next run
 * would have been checked against -- but the rail was empty, so the page and
 * the backend disagreed about the single most important input.
 *
 * Two calls, and the second one is not a second source of truth. GET /resumes
 * counts the raw file with LineIndex; POST /resumes counts the repaired text
 * with index_resume, and so does GET /resumes/{id}. Only the detail call can
 * fill this card with the same two numbers an upload puts there, so the card
 * after a reload and the card after an upload cannot say different things
 * about one file. It also warms `lastRead`, which the resume view wanted next.
 *
 * Every failure is silent on purpose. No backend -- the page opened straight
 * from web/ -- nothing stored, or a store that has no default all end the same
 * way: the page looks exactly as it did before this brief.
 */
function restoreResume() {
  fetch('/resumes')
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) {
      var list = (data && data.resumes) || [];
      var pick = null;
      for (var i = 0; i < list.length; i++) {
        if (list[i]['default']) { pick = list[i]; break; }
      }
      // No default is not "use the first one". The brief asks for the default
      // and nothing else, and guessing which resume you meant is the kind of
      // help that gets you audited against last year's CV.
      if (!pick || stored) return null;
      return fetch('/resumes/' + encodeURIComponent(pick.id))
        .then(function (response) { return response.ok ? response.json() : null; })
        .then(function (read) {
          // `stored` again: an upload may have finished while this was in
          // flight, and the file a person just dropped outranks the default.
          if (!read || read.error || stored) return;
          lastRead = read;
          stored = {
            id: read.id,
            name: pick.name,
            lines: read.lines.length,
            repaired: read.repairs.length,
            isDefault: true
          };
          syncResume();
          syncReady();
        });
    })
    .catch(function () {});
}

function forgetResume() {
  stored = null;
  lastRead = null;
  if (viewing) { viewing = false; setPhase(phase); }
  showUploadWrong(null);
  syncResume();
  syncReady();
}

// ---- how we read it -----------------------------------------------------

/* Which displayed line each repair produced.
 *
 * A change's `source_line` counts lines in the text BEFORE repair ran. It is
 * not the number shown in this view and it is never printed as one -- printing
 * it would be exactly the two-sets-of-line-numbers failure this brief is most
 * able to cause.
 *
 * What is safe is the text. `after` holds the line, or the ⏎-separated lines,
 * that repair produced, so a displayed line whose text matches one of them --
 * and which is the only line in the document with that text -- is that line.
 * A text that appears twice identifies nothing, so it is left unmarked. An
 * unmarked repair is still listed in full above; a repair marked on the wrong
 * line would be a lie.
 */
function repairedLines(lines, repairs) {
  var where = {};
  lines.forEach(function (line) {
    if (where[line.text] === undefined) where[line.text] = line.number;
    else where[line.text] = null;
  });

  var fixed = {};
  repairs.forEach(function (change) {
    String(change.after).split('⏎').forEach(function (piece) {
      var at = where[piece.trim()];
      if (at) fixed[at] = true;
    });
  });
  return fixed;
}

/* Which lines the answers on screen quoted, and in what colour.
 *
 * Only when the run those answers came from was run against THIS document. A
 * run on pasted text has its own line numbers, and painting them over the
 * file's lines would put two different resumes on one screen.
 */
function quotedLines() {
  var out = {};
  if (!stored || ranAgainst !== stored.id) return out;
  Object.keys(verdicts).forEach(function (id) {
    var v = verdicts[id];
    if (v.line && v.line_number) out[v.line_number] = v.verdict;
  });
  return out;
}

function repairBlock(repairs) {
  el.repairs.innerHTML = '';
  if (!repairs.length) {
    el.repairs.hidden = true;
    return;
  }

  var open = false;
  var list = document.createElement('div');
  list.className = 'repair-list';
  list.id = 'repair-list';
  list.hidden = true;

  var toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'list-toggle';
  toggle.setAttribute('aria-controls', 'repair-list');

  var chev = document.createElement('span');
  chev.className = 'chev';
  chev.setAttribute('aria-hidden', 'true');

  var title = document.createElement('span');
  title.className = 'list-title';
  title.textContent = 'What we put back';

  var gap = document.createElement('span');
  gap.className = 'top-gap';

  var meta = document.createElement('span');
  meta.className = 'list-meta';
  meta.textContent = repairs.length + (repairs.length === 1 ? ' change' : ' changes');

  [chev, title, gap, meta].forEach(function (part) { toggle.appendChild(part); });

  var hint = document.createElement('p');
  hint.className = 'repair-hint';
  hint.textContent = 'Pulling text out of a PDF breaks lines. These are the ' +
    'ones we put back, and what each one looked like before. Lines were only ' +
    'joined up or split apart. No word was changed. The ⏎ marks where the ' +
    'file had a line break.';

  function sync() {
    list.hidden = !open;
    chev.textContent = open ? '▾' : '▸';
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  toggle.addEventListener('click', function () { open = !open; sync(); });
  sync();

  repairs.forEach(function (change) {
    var item = document.createElement('div');
    item.className = 'repair';

    var kind = document.createElement('p');
    kind.className = 'repair-kind';
    kind.textContent = REPAIR_WORD[change.kind] || change.kind;
    item.appendChild(kind);

    // No line number on either block. See repairedLines() for why.
    item.appendChild(quoteBlock(change.before, null, '', 'out of the PDF'));
    item.appendChild(quoteBlock(change.after, null, '', 'what we read'));
    list.appendChild(item);
  });

  el.repairs.appendChild(toggle);
  el.repairs.appendChild(hint);
  el.repairs.appendChild(list);
  el.repairs.hidden = false;
}

function drawResume(data) {
  var lines = data.lines || [];
  var repairs = data.repairs || [];
  var fixed = repairedLines(lines, repairs);
  var quoted = quotedLines();

  repairBlock(repairs);

  el.resumeLines.innerHTML = '';

  var oldLegend = el.resumeView.querySelector('.resume-legend');
  if (oldLegend) oldLegend.remove();

  if (repairs.length) {
    var legend = document.createElement('p');
    legend.className = 'resume-legend';
    // Not "one ⏎ per change": splitting a flattened table row makes several
    // lines out of one change, so the glyphs outnumber the changes. Saying
    // what the glyph means, rather than implying a count, keeps that honest.
    legend.textContent = '⏎ beside a number means we changed where that line ' +
      'begins or ends. The words on it are the file’s own.';
    el.resumeLines.parentNode.insertBefore(legend, el.resumeLines);
  }

  // GET /resumes/{id} sends the lines that have something on them, keeping
  // their own numbers, so a gap in the numbering is a blank line in the file.
  // The gaps are drawn back as blank rows: the numbers stay exactly where the
  // backend put them, and the resume reads the way it does on paper.
  var expected = 1;
  lines.forEach(function (line) {
    while (expected < line.number) {
      el.resumeLines.appendChild(resumeRow(expected, '', false, null));
      expected += 1;
    }
    el.resumeLines.appendChild(
      resumeRow(line.number, line.text, fixed[line.number], quoted[line.number]));
    expected = line.number + 1;
  });
}

function resumeRow(number, text, wasFixed, verdict) {
  var row = document.createElement('div');
  row.className = 'rline' + (text ? '' : ' blank') +
                  (verdict ? ' quoted ' + verdict : '');

  var n = document.createElement('span');
  n.className = 'n';
  n.textContent = String(number);
  row.appendChild(n);

  var glyph = document.createElement('span');
  glyph.className = 'fixed';
  glyph.textContent = wasFixed ? '⏎' : '';
  if (wasFixed) glyph.title = 'We put this line back together.';
  row.appendChild(glyph);

  var t = document.createElement('span');
  t.className = 't';
  t.textContent = text || ' ';
  row.appendChild(t);
  return row;
}

function openResumeView() {
  if (!stored) return;
  viewing = true;
  setPhase(phase);
  el.resumeTitle.textContent = stored.name;

  if (lastRead && lastRead.id === stored.id) { drawResume(lastRead); return; }

  el.repairs.hidden = true;
  el.resumeLines.innerHTML = '';
  var waiting = document.createElement('p');
  waiting.className = 'nothing-here';
  waiting.textContent = 'Reading it back.';
  el.resumeLines.appendChild(waiting);

  fetch('/resumes/' + encodeURIComponent(stored.id))
    .then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok || data.error) {
          throw new Error(data.error || ('The backend answered ' + response.status + '.'));
        }
        return data;
      });
    })
    .then(function (data) {
      lastRead = data;
      if (viewing) drawResume(data);
    })
    .catch(function (err) {
      el.resumeLines.innerHTML = '';
      var wrong = document.createElement('p');
      wrong.className = 'nothing-here';
      wrong.textContent = 'We could not read it back. ' + err.message;
      el.resumeLines.appendChild(wrong);
    });
}

function closeResumeView() {
  viewing = false;
  setPhase(phase);
}

// ---- wiring -------------------------------------------------------------

el.drop.addEventListener('click', function () { el.file.click(); });
el.file.addEventListener('change', function () { uploadResume(el.file.files[0]); });
el.resumeOpen.addEventListener('click', openResumeView);
el.resumeDrop.addEventListener('click', forgetResume);
el.resumeBack.addEventListener('click', closeResumeView);

// Dropping works on the whole block, in both states: once a file is in, the
// drop zone itself is gone, and there is still an obvious place to drop.
['dragenter', 'dragover'].forEach(function (name) {
  el.resumeBlock.addEventListener(name, function (e) {
    e.preventDefault();
    if (!reading) el.drop.classList.add('over');
  });
});
['dragleave', 'drop'].forEach(function (name) {
  el.resumeBlock.addEventListener(name, function (e) {
    e.preventDefault();
    el.drop.classList.remove('over');
  });
});
el.resumeBlock.addEventListener('drop', function (e) {
  var files = e.dataTransfer && e.dataTransfer.files;
  if (files && files.length) uploadResume(files[0]);
});

// A file dropped anywhere else would otherwise be opened by the browser, which
// navigates away from a finished run.
['dragover', 'drop'].forEach(function (name) {
  window.addEventListener(name, function (e) { e.preventDefault(); });
});

// ---------------------------------------------------------------- driving it

function mode() {
  var picked = document.querySelector('input[name="mode"]:checked');
  return picked ? picked.value : 'live';
}

function whichFixture() { return el.fixture ? el.fixture.value : 'summary'; }

function start() {
  if (running) {
    // The button is Stop while a run is going. What is on screen stays.
    cancelled = true;
    return;
  }
  cancelled = false;
  reset();
  running = true;
  setPhase('running');
  startClock();

  var finish = function () {
    running = false;
    stopClock();
    if (phase !== 'error') { listTouched = false; setPhase('done'); }
    buttonsEnabled(true);
  };

  if (mode() === 'fixture') {
    // A recording quotes the resume it was recorded against, which is not the
    // one in the rail. Nothing it says may colour the resume view.
    ranAgainst = null;
    loadFixture(whichFixture())
      .then(function (events) { return replay(events); })
      .catch(function (err) { renderError(err.message); })
      .then(finish);
    return;
  }

  var post = el.post.value.trim();
  var resume = el.resume.value.trim();
  if (!post || (!resume && !(stored && stored.id))) {
    // The backend checks this too. Saying it here saves a round trip.
    renderError('Add a resume and paste a job post before running this for real.');
    running = false;
    stopClock();
    return;
  }

  // Decision 0005 and brief 0017: the id once a resume is stored, the pasted
  // text otherwise. The backend prefers the id when both arrive, so only one
  // of the two is ever sent and the rail says which it will be.
  var payload = { post: post };
  if (stored && stored.id) payload.resume_id = stored.id;
  else payload.resume = resume;
  ranAgainst = payload.resume_id || '';

  stream('/audit', payload)
    .catch(function (err) { renderError(err.message); })
    .then(finish);
}

// Shows what a broken run looks like without needing a broken backend. It
// replays the opening of a recording, then renders a real error event.
function previewError() {
  if (running) return;
  cancelled = false;
  reset();
  running = true;
  ranAgainst = null;
  setPhase('running');
  startClock();
  loadFixture(whichFixture())
    .then(function (events) { return replay(events, 8); })
    .then(function () {
      render({ type: 'error', message:
        'The connection to the model closed after 41 seconds, part way through.' });
    })
    .catch(function (err) { renderError(err.message); })
    .then(function () { running = false; stopClock(); });
}

// The recording picker does nothing on a real run, so it says so rather than
// sitting there inviting a click that changes nothing.
function syncPicker() {
  var off = mode() === 'live';
  if (el.fixture) el.fixture.disabled = off;
  if (el.errorPreview) el.errorPreview.disabled = off;
  syncRecording();
  syncReady();
}

/* Brief 0019. A recorded answer quotes a resume and a post that are not the
 * ones in the rail, and it has already been read out loud as if it were real.
 *
 * It is tied to the switch, not to what is on screen -- exactly as the
 * extension's FIXTURES flag is. The switch is the statement of intent, and the
 * brief asks that choosing a real run clear the warning outright. The cost is
 * the one case in the other direction: flip to a real run with a finished
 * recording still on screen and the warning goes before the answer does.
 * Running clears it, and the demo script never flips mid-answer. */
function syncRecording() {
  var recorded = mode() === 'fixture';
  if (el.recording) el.recording.hidden = !recorded;
  if (el.auditFlag) el.auditFlag.hidden = !recorded;
}

el.run.addEventListener('click', start);
el.errorPreview.addEventListener('click', previewError);

var radios = document.querySelectorAll('input[name="mode"]');
for (var r = 0; r < radios.length; r++) {
  radios[r].addEventListener('change', syncPicker);
}

[el.post, el.resume].forEach(function (boxEl) {
  boxEl.addEventListener('input', function () { syncWells(); syncReady(); });
});

// ------------------------------------------------- the post arriving by URL

/* The extension opens http://localhost:8000/#post=<encoded>. A fragment is
 * never sent to a server by the browser, which is why decision 0006 chose one:
 * the post reaches this page without a request, and nothing leaves the machine.
 *
 * The fragment is cleared once it has been read, so a refresh does not silently
 * paste it back over something the person has since typed. */
function readPostFromUrl() {
  var hash = location.hash || '';
  var match = hash.match(/(?:^#|&)post=([^&]*)/);
  if (!match) return false;

  var text;
  try { text = decodeURIComponent(match[1].replace(/\+/g, ' ')); }
  catch (e) { return false; }            // a malformed fragment is not a post
  if (!text.trim()) return false;

  el.post.value = text;
  history.replaceState(null, '', location.pathname + location.search);
  syncWells();
  syncReady();
  el.post.focus();
  el.post.setSelectionRange(0, 0);
  el.post.scrollTop = 0;
  return true;
}

// ---------------------------------------------------------------- on load

syncResume();
syncWells();
syncPicker();
setPhase('empty');
syncReady();
readPostFromUrl();
restoreResume();   // brief 0019. Asynchronous, and it only ever adds a card.
window.addEventListener('hashchange', readPostFromUrl);

// Start on load when asked: ?auto=fixture or ?auto=error, and ?fixture=<name>
// to pick which recording. Used to capture the page for the report, and handy
// for opening the demo already running.
(function () {
  var which = (location.search.match(/[?&]fixture=([^&]+)/) || [])[1];
  if (which && FIXTURES[which] && el.fixture) el.fixture.value = which;
  var auto = (location.search.match(/[?&]auto=([^&]+)/) || [])[1];
  if (auto === 'fixture') start();
  else if (auto === 'error') previewError();
})();

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
  errorPreview: document.getElementById('error-preview')
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

// ---------------------------------------------------------------- the frame

function setPhase(next) {
  phase = next;
  el.intro.hidden = next !== 'empty' && next !== 'ready';
  el.audit.hidden = next === 'empty' || next === 'ready' || next === 'error';
  el.banner.hidden = next !== 'error';
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
             note: 'Paste a resume and a job post first.' },
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
  var filled = el.post.value.trim() && el.resume.value.trim();
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
                              ' · this is what we quote from';
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
  el.audit.hidden = order.length === 0;
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
    work = stream(RERUN_ENDPOINT, {
      post: el.post.value.trim(),
      resume: el.resume.value.trim(),
      requirement_id: id
    }).then(function () { sawSummary = summaryEv !== before; });
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

// ---------------------------------------------------------------- driving it

function mode() {
  var picked = document.querySelector('input[name="mode"]:checked');
  return picked ? picked.value : 'fixture';
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
    loadFixture(whichFixture())
      .then(function (events) { return replay(events); })
      .catch(function (err) { renderError(err.message); })
      .then(finish);
    return;
  }

  var post = el.post.value.trim();
  var resume = el.resume.value.trim();
  if (!post || !resume) {
    // The backend checks this too. Saying it here saves a round trip.
    renderError('Paste both a job post and a resume before running this for real.');
    running = false;
    stopClock();
    return;
  }

  stream('/audit', { post: post, resume: resume })
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
  syncReady();
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

syncWells();
syncPicker();
setPhase('empty');
syncReady();
readPostFromUrl();
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

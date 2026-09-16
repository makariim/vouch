---
status: done
date: 2026-09-16
---

# 0019 — Two things that would catch you out on stage

> **You own `web/` and nothing else.**
>
> **Small. Both are about not being embarrassed in front of people, not about
> features.**

## 1. Goal

Two things in the page have already caught the author out once today.

**If we do not do this:** he reads a recorded answer out loud as if it were a
real one, in front of a panel, about a real job.

## 2. Thing one — you cannot tell a recording from a real run

`index.html` line 40:

```html
<label><input type="radio" name="mode" value="fixture" checked><span>A recording</span></label>
```

**Recording mode is the default**, and the only sign of it is a small radio
button in the top corner.

**What happened today.** A real job post was pasted into the box. The answer
beside it came from a recording. It listed *"Willingness to travel up to 25% of
the time"* as a blocker. The real post never mentions travel. Nothing on screen
was loud enough to stop him believing it.

**The extension already solves this.** It shows an amber `FIXTURES` flag across
its header the whole time, and it cannot be missed.

**Do the same here.** While a recording is showing:

- a banner across the top, in the colour the design uses for a warning
- it says plainly that this is a recording and the answer has nothing to do with
  the post in the box
- the answer area itself is marked too, so a screenshot of the answer alone
  still says what it is

It must be impossible to miss from two metres.

**Leave the default alone** unless you have a reason. The banner is the fix; the
default is a separate argument.

## 3. Thing two — reloading loses the resume

Upload a PDF, refresh the page, and the rail is empty — although the backend
still has the file and would still audit against it.

`GET /resumes` exists and returns the stored list with a default. **Ask for it
when the page loads**, and if a default is there, show the card the way an
upload shows it.

If nothing is stored, the page looks exactly as it does now.

**Out of scope:** several resumes, switching the default, deleting one. Anything
outside `web/`. Any backend change — `GET /resumes` already exists.

## 4. Must not happen

Standing ones apply.

- **Do not remove recording mode.** It is the fallback if the model is slow in
  the room, and the demo script depends on it.
- **Do not make recording mode a silent fallback.** It stays a deliberate
  choice, exactly as the extension does it.
- **Do not invent a design value.** `tokens.css` claims full coverage; report a
  gap rather than filling it.
- No CDN, no web font, nothing fetched off this machine.

## 5. Done when

- With a recording showing, **somebody two metres away can tell**, without being
  told where to look.
- A screenshot of just the answer still says it is a recording.
- Switching to a real run clears every trace of the warning.
- Upload a PDF, reload the page, and the resume card is still there.
- With nothing stored, the page is unchanged.
- Every value comes from `tokens.css`.

**What would tell us it failed:** you can still glance at the page and not know
which mode you are in.

## 6. Checked by

`formwork check`.

The gate cannot see a web page. The evidence is looking at it from across a
room, and reloading once after an upload.

## 7. The report must contain

Short.

- what the recording banner looks like, described
- confirmation that a reload keeps the resume, and that an empty store changes
  nothing
- any value `tokens.css` did not have

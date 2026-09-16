---
status: done
date: 2026-09-16
---

# 0017 — Upload a PDF resume

> **You own `web/` and nothing else.** Do not touch `src/`, `tests/`,
> `extension/`, `design/` or `fixtures/`.
>
> **Every endpoint you need already exists and is tested.** No backend work.
> If you think you need a backend change, stop and say so.

## 1. Goal

**Nobody has a resume as a `.txt` file.** People have PDFs.

The backend already takes one: `POST /resumes` accepts a `.pdf`, `pypdf`
extracts the text, and mechanical line repair fixes the damage that extraction
causes — words split across a line break, table rows flattened into one line.
On the real resume it makes **23 changes**.

The page has none of that. It has two paste boxes, and the only way to get a
PDF in is `curl`.

**If we do not do this:** the product asks a job seeker to convert their own
resume to plain text before it will help them, which is not a product.

## 2. Scope

### Upload

- A **drop zone and a file picker** on the page, where the resume goes today.
  `design/canvas/Web.dc.html` draws this; follow it.
- `POST /resumes` with the file as multipart. It returns:

  ```json
  {"id": "...", "lines": 100, "repaired": 23, "default": true}
  ```

- **Show `repaired`.** *"Your PDF lost 23 line breaks. We put them back."*
  That number is the most interesting thing on the screen and it is free.
- The errors the backend already returns, shown calmly, not as a stack trace:
  an unsupported file type, a corrupt file, and **a scanned PDF with no text
  layer** — which is a real thing people will upload.

### Use the stored resume

- `POST /audit` takes **`resume_id`** as well as inline `resume` text. Send the
  id once a resume is stored.
- **Keep pasting as a second way in.** It is the fallback if an upload fails in
  front of people, and the recordings depend on it.

### See how we read it

`GET /resumes/{id}` returns every line with its number, **and a list of what
repair changed** — kind, source line, before, after.

Show it. Numbered lines, and the repairs marked.

**This is the strongest thing in this brief.** A verdict cites "line 77"; this
is where a person checks that line 77 says what the tool claims. It is also the
only place the damage and the fix are both visible.

Mark it droppable: if the clock beats you, ship the upload without it and say so.

**Out of scope:**

- **Any backend change.** Every endpoint exists.
- several resumes, switching the default, deleting one
- anything in `extension/`, `src/`, `design/`
- editing `design/tokens.css` — report a missing value, do not invent one

## 3. Must not happen

Standing ones apply: no writing to version control, no deciding anything, no
changing a check because it failed, NOT ESTABLISHED rather than an estimate.

- **Do not send the resume anywhere but `localhost`.** Decision `0002`.
- **Do not commit a resume**, or any file from `private/`. Do not add fixtures
  built from a real one.
- **Do not repair, clean or reformat anything in JavaScript.** Repair is
  mechanical and it lives in the backend. A client that also edits the text
  breaks the line numbers every verdict depends on.
- **Do not remove the paste box.**
- Do not invent a design value. `tokens.css` claims full coverage.

## 4. Done when

- A real PDF uploads from the page and the number of lines and the number of
  repairs appear.
- **An audit runs against the uploaded resume**, by `resume_id`, and the quoted
  lines are right.
- All three errors show as a calm message: wrong type, corrupt file, scanned PDF
  with no text.
- Pasting still works, and the recordings still run.
- Every value comes from `tokens.css`, and the copy follows the plain-English
  rules in `design/README.md`.

**What would tell us it failed:** a verdict cites a line number that does not
match what the resume view shows on screen. That would mean two different
copies of the resume exist, and it is the one thing this brief could break.

## 5. Checked by

`formwork check`.

**The gate cannot see a web page.** The evidence is uploading a real PDF and
reading section 6.

## 6. The report must contain

The standing list in `formwork/templates/report.md`, plus:

- **how many lines and how many repairs** a real PDF produced
- **two or three of the repairs, before and after**, quoted
- confirmation that a verdict's line number matches the same line in the resume
  view — checked, not assumed
- whether "see how we read it" shipped, or was dropped
- any value `tokens.css` did not have

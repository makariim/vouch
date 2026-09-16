---
status: open
date: 2026-09-16
brief: 0019-page-demo-safety
---

# 0019 — Two things that would catch you out on stage

**A recording now says so across the top of the page and again on the answer
itself, and a reload no longer loses the resume.** Nothing outside `web/` was
touched and no backend change was needed.

## What the recording banner looks like

A bar the full width of the window, directly under the header, in solid
`--v-partly` — the one warning hue tokens.css has, and the same amber the
extension's `FIXTURES` flag uses. Dark text on it. On the left, **A RECORDING**
in 18px caps, letter-spaced. Beside it, at 16px: *This answer was recorded
earlier. It has nothing to do with the post in the box.*

It is **sticky at `--v-header-h`**, so it does not scroll away when you are
three screens down reading the working. The header stays above it; nothing else
does.

**It is the solid colour, not `--v-partly-wash`.** The wash is lightness 0.242
against a 0.180 ground. That is legible at a desk and invisible from two metres,
and two metres is the whole requirement. This is the one place on the page where
a wash was not enough.

**On the answer itself:** a small amber pill, **A RECORDING · NOTHING BELOW CAME
FROM THE POST IN THE BOX**, inside `#audit` and above the working block, so it
sits over the live run and over the finished answer both. It is in the frame of
a screenshot that contains only the answer, which the banner is not.

**Clearing it.** Both are tied to the switch, not to what is on screen — exactly
as the extension's flag is — so picking *A real run* removes both outright.
`syncRecording()` is one function called from `syncPicker()`, which already ran
on every mode change and on load.

**The one case in the other direction, and it is deliberate.** Flip to *A real
run* with a finished recording still on screen and the warning goes before the
answer does. The brief's done-when asks for the switch to clear every trace, so
that is what it does; the alternative would have been a warning that outlives
the mode. Clicking run clears the answer, and the demo script never flips
mid-answer.

## The reload

**Confirmed against a running backend.** Uploading a file whose text has two
broken lines:

| | `name` | lines | repaired |
|---|---|---|---|
| the card after the upload | `cv-0019.txt` | 3 | 2 |
| the card after a reload | `cv-0019.txt` | 3 | 2 |

**With nothing stored, `GET /resumes` returns `{"resumes": []}` and the page is
byte-for-byte what it was.** Same for no default, and same when the page is
opened straight out of `web/` with no backend at all — the fetch rejects, the
catch is empty, and no card appears. Failure is silent on purpose: there is
nothing a person could do about any of it, and the page without a card is a
correct page.

**Two calls, not one, and this is the part worth reading.** `GET /resumes` alone
would have made the card lie. It counts the raw file with `LineIndex`; the
upload card counts the repaired text with `index_resume`. On the file above the
list says **5 lines** where the card says **3**. So the restore asks
`GET /resumes` only for *which* resume is the default, then
`GET /resumes/{id}` for the numbers — the same function the upload card's
numbers come from, so the two cards cannot disagree about one file. It also
warms `lastRead`, so *See how we read it* opens without a second round trip.

**No default is not "use the first one."** Guessing which resume you meant is
the kind of help that audits you against last year's CV.

## What `tokens.css` did not have

**One gap, and it is a naming gap rather than a missing value: there is no "ink
on the warning colour" role.** Section 2 gives `--v-partly` and
`--v-partly-wash` and stops; every ink role in section 1 is for a dark ground,
except `--v-ink-on-light`, whose comment scopes it to a `--v-ink` button.

Nothing was invented. `--v-ink-on-light` is used, because it is the only
dark-on-bright role the design has and `--v-partly` (L 0.815) sits within 0.1
lightness of `--v-ink` (L 0.915), which is what that role was measured against.
**If design wants a `--v-partly-ink`, two declarations in `styles.css` change
and nothing else does.**

This is the second gap the page has reported in the same file — `--page-note`,
from report 0013, is still the other one.

## Left alone, as instructed

- **Recording mode is still the default.** The brief says the banner is the fix
  and the default is a separate argument. It was not touched.
- **Recording mode is still a deliberate choice.** Nothing falls back to it.
- Several resumes, switching the default and deleting one are all still absent.
  One consequence worth knowing before the demo: *Stop using this file* clears
  the card but not the store, so a reload brings the same resume back. That is
  the store being right and the page finally agreeing with it.

## Checked

`formwork check` — **green, 12 checks.** The gate cannot see a page; the banner
is evidence you look at, and the reload was run against a real backend on a real
upload.

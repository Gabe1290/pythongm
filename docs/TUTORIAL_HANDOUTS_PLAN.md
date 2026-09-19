# Student handouts + teacher guides for the in-app tutorials — plan

Written 2026-09-19 on the ask: teachers have students work through the
tutorials, step in when a student is stuck, and add their own course
elements — so each tutorial needs a **student handout** and a **teacher
guide**. Nothing here is started; every scope decision that isn't already
precedent is listed under "Decisions needed".

## Where things stand

| | Tutorials | Handout + guide |
|---|---|---|
| 01 Getting Started | done | **done, EN + FR** (`docs/TUTORIAL_01_{STUDENT_HANDOUT,TEACHER_GUIDE}[_FR].md` + `.odt` + `.pdf`) |
| 02–10 (first game … file-exchange multiplayer) | done | none |
| 11–14 (2.5D series) | done, EN + FR | none |

So **1 of 14** tutorials has classroom material. The machinery already
exists and is the thing to reuse, not rebuild:

- `.md` is the single source of truth; `scripts/generate_tutorial_handouts_odt.py`
  and `_pdf.py` generate the editable `.odt` and the printable `.pdf`
  (with `![alt](img.png)` image support).
- `docs/TUTORIAL_HANDOUT_WORKFLOW.md` is the round-trip procedure for a
  teacher/author hand-editing an `.odt` and folding it back. Follow its
  "commit the draft first, back up before regenerating" rules.
- Tutorial 1's pair is the worked example of tone, length (~1,000 words
  student / ~800 words guide per language) and structure.

## What a teacher actually needs (the design)

The in-app tutorial is a *screen* experience. A handout exists so the
student can work with the tutorial open on one half of the screen and
paper (or a second window) for the rest; a teacher guide exists so someone
who has never used the tool can run the lesson. Neither should just
re-print the tutorial pages.

### Student handout (per tutorial, ~1–2 printed pages per tutorial page-group)

1. **Goal + what you'll have at the end** (one screenshot of the finished result).
2. **Before you start** — what to have open, which earlier tutorial's
   project (if any) is continued, where to save.
3. **Checklist by phase**, with tick-boxes — the tutorial's steps compressed
   to one line each, plus a **"You should see…"** checkpoint after each phase
   so a student can self-verify without calling the teacher.
4. **Stuck? table** — symptom → most likely cause → fix. (The single most
   useful teaching aid; content comes from real failure modes, see sources.)
5. **Vocabulary** — the new terms, in the student's words.
6. **Challenges in three tiers** — *Try this* (5 min), *Push further*,
   *Invent* — so fast students self-differentiate.
7. **Reflection / self-check** — 3 questions ("What does the Collision event
   do?") that double as an exit ticket.
8. **My notes** lines.

### Teacher guide (per tutorial)

1. Objectives, prerequisites, **what students will NOT be able to do yet**
   (Tutorial 1's guide sets this pattern: "the object doesn't move — that's expected").
2. **Timing table** with a shortened variant for a 45-min slot.
3. **Walkthrough with the common mistakes per step**, marked by how often
   they occur (from the truth tests and past bug notes — see sources).
4. **Discussion / questioning prompts** at natural pauses ("Predict what
   happens before you press F5").
5. **Differentiation**: support (pair-programming pairings, partially-built
   starter project) and extension (the challenge tiers, plus an open project brief).
6. **Formative checks + a simple 4-level rubric** for the finished project.
7. **Answer key**: the finished project's key settings, and a pointer to a
   reference project the teacher can open and compare.
8. **Course-element menu**: cross-curricular hooks (maths — angles/coordinates
   for the 2.5D series; art — sprite design; French/other-language — the
   IDE is translated), homework variants, a one-slide summary.
9. **Lab notes**: save location convention, the edition setting (the
   beginner edition hides tutorials 5+; teachers of later lessons must switch
   edition), offline behaviour, what to do on a slow machine.

### Plus one course-level document (once)

`docs/TEACHER_COURSE_OVERVIEW.md`: the sequence (which tutorial follows
which, with the prerequisite graph), suggested pacing for a term / a
short workshop, an assessment map, and the bundled samples that suit each
stage. Without it, teachers face 14 separate guides and no route.

## Sources of truth (so handouts don't teach falsehoods)

- The tutorial HTML pages (`Tutorials/<NN>_*/`, EN) → the step list.
- **Common mistakes/"Stuck?" content** is already known and mostly unwritten
  in one place: `docs/RAYCAST_TUTORIALS_PLAN.md` findings (walls don't block
  without an empty collision event; score/lives belong in Game Start;
  HUD object must be visible; Viewport Height must match the bar), plus the
  landmines in CLAUDE.md (quoted on-screen text, collision fires on *start* of
  overlap, one side of a collision pair fires). For tutorials 02–10, each
  guide starts with a short investigation pass — run the tutorial's
  build-along and record where it goes wrong — before writing.
- **Reference solutions**: `tests/test_raycast_tutorial_lessons.py` already
  rebuilds Lessons 11–14 in code. The same builders can emit a `project.json`
  a teacher can open. For 02–10 the bundled samples are the nearest
  equivalents (`maze_1`, `plateforme_1`, …) and some need a "starter"
  version stripped back to the tutorial's start point.
- Wording, action names and menu paths: French action names from
  `tools/action_ref_i18n.py`; parameter labels stay English in the IDE, so
  French handouts give the English label plus a gloss (the same rule the
  2.5D lessons follow).

## Guard tests (extend the existing pattern)

Modelled on `tests/test_platform_display_checklist.py` and
`test_raycast_tutorial_lessons.py`:

- every handout/guide names a tutorial folder that exists and quotes the
  same page count as `Tutorials/index.json`;
- every referenced sample / tool / action name exists;
- EN and FR of each document have the same section headings and the same
  number of checkboxes (structure parity, not word parity);
- French files contain no stripped-accent words (the repo rule; a small
  regex list of common offenders);
- generated `.pdf`/`.odt` are current with their `.md` (regen + byte
  compare, or a mtime/hash stamp) so an edit can't ship without regeneration.

## Delivery: how teachers get them

Today they sit in `docs/` where a teacher won't look. Options (needs a decision):

1. Keep `.md`/`.odt`/`.pdf` in `docs/handouts/` and link from the wiki
   "For Teachers" page (EN + FR) and the README.
2. Also attach them to each GitHub release as a `teacher-pack.zip`.
3. Add **Help → Teacher Resources…** in the IDE, opening the folder (works
   offline in a school lab; needs the packaged app to include them).

Recommended: 1 + 2 now, 3 as a later small unit.

## Units of work (one commit each, session-sized)

Order is by how likely a class is to use the tutorial, and by how much
verified material already exists.

- [ ] **U0 — Foundations.** Decide the open questions below; write the
      handout + guide *templates* (from Tutorial 1's pair), move existing
      files into `docs/handouts/` (update `TUTORIAL_HANDOUT_WORKFLOW.md`
      paths), add the guard-test scaffold and `TEACHER_COURSE_OVERVIEW.md`.
- [ ] **U1 — Tutorial 02 First Game** (the natural second lesson).
- [ ] **U2 — Tutorial 03 Pong.**
- [ ] **U3 — Tutorial 06 Maze.**
- [ ] **U4 — Tutorial 09 Catch the Coins** (win/lose; teaches conditions).
- [ ] **U5 — Tutorial 07 Platformer.**
- [ ] **U6–U9 — Tutorials 11, 12, 13, 14 (2.5D).** Cheapest: content is
      fresh and the truth tests supply mistakes + reference projects.
      Group 11+12 and 13+14 if the docs are short.
- [ ] **U10 — Tutorials 04 Breakout, 05 Sokoban, 08 Lunar Lander.**
- [ ] **U11 — Tutorial 10 File-exchange multiplayer** (needs two computers
      or two folders — the guide must cover lab setup and shared-drive
      permissions; the most teacher-support-hungry tutorial).
- [ ] **U12 — Delivery:** wiki "For Teachers" pages (EN+FR), release attachment
      script, optional Help menu entry.
- [ ] **U13 — Other languages** (only if wanted; see cost).

Each unit = EN + FR handout + EN + FR guide + regenerated `.odt`/`.pdf` +
tests, committed and pushed on its own so a session-limit stop loses nothing.

## Cost estimate

Tutorial 1's pair is ≈3,650 words across 4 files. From the French-guide
translation arc (13,500 words ≈ 40% of a session), one tutorial's EN+FR
handout+guide ≈ **8–12% of a session**, so the 13 remaining tutorials ≈
**1.5–2 sessions**, plus U0 and U12 (~10% each). Adding a further language
later is roughly the translation cost only (~3% per language per tutorial).
`.pdf` generation needs the existing script's dependencies; LibreOffice is
only needed if converting an `.odt` back.

## Decisions needed

1. **Scope of "course elements".** Handout + guide only, or also
   worksheets/quizzes with answer keys and an assessment rubric file? (The
   plan above folds a short self-check, rubric and answer key *into* each
   guide; separate quiz files are a bigger add.)
2. **Reference solutions.** Ship finished/starter `project.json` folders for
   teachers? Where — a `Tutorials/solutions/` folder bundled in the app, or
   only in the teacher pack download?
3. **Languages.** EN + FR (Tutorial 1 precedent and the 2.5D lessons) — or
   include DE/IT/… where tutorial translations already exist?
4. **Delivery** (options 1/2/3 above).
5. **Order.** Confirm the priority list, especially whether the 2.5D series
   goes first (cheapest) or 02/03/06/09 (most used).

## Not in scope

Translating the in-app tutorial pages themselves; re-recording screenshots
(reuse existing ones; new ones only for the finished-result picture);
slide decks; video.

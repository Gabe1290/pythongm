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

## Delivery: how teachers get them (superseded by the settled decisions below; kept for the reasoning)

Today they sit in `docs/` where a teacher won't look. Options (needs a decision):

1. Keep `.md`/`.odt`/`.pdf` in `docs/handouts/` and link from the wiki
   "For Teachers" page (EN + FR) and the README.
2. Also attach them to each GitHub release as a `teacher-pack.zip`.
3. Add **Help → Teacher Resources…** in the IDE, opening the folder (works
   offline in a school lab; needs the packaged app to include them).

Recommended: 1 + 2 now, 3 as a later small unit.

## Units of work (one commit each, session-sized)

Each tutorial unit = EN + FR handout + guide + worksheet(+key, rubric) +
starter/solution zip + generated `.odt`/`.pdf` + guard tests, committed and
pushed on its own so a session-limit stop loses nothing.

- [x] **U0 — Foundations (DONE 2026-09-19).** Templates (handout, guide, worksheet) written
      from Tutorial 1's pair; move existing files to `docs/handouts/`
      (update `TUTORIAL_HANDOUT_WORKFLOW.md`); guard-test scaffold;
      `scripts/sync_wiki.sh` carries `downloads/`; generator that turns
      `docs/handouts/*.md` into wiki pages + downloads; the wiki
      `Teacher-Resources` landing page with the course overview (sequence,
      prerequisites, pacing, assessment map). Includes Tutorial 1's missing
      worksheet.
- [x] **U1 — Tutorial 02 First Game (DONE 2026-09-19;** found + fixed: alarm 60 = 1 s not 2 s in the tutorial; checkpoint zip opens in the IDE loader**)**
- [x] **U2 — Tutorial 03 Pong (DONE 2026-09-19;** found + fixed: numeric `direction_expr` read as 0 in the runtime; score text was black-on-black and overlapped the wall row (EN+FR tutorial fixed; other 6 languages use an older page layout, still to review); HTML5/Kivy ignore `direction_expr` -> TODO.md**)**
- [x] **U3 — Tutorial 04 Breakout (DONE 2026-09-19;** verified: parent inheritance, death zone, lives, Game Over; the tutorial's "order matters" for Show Highscore/End Game is not true on the desktop player (guide keeps the safe order)**)**
- [x] **U4 — Tutorial 05 Sokoban (DONE 2026-09-20;** found + fixed in EN/FR: targets placed after crates/player are drawn over them (draw order = placement order, no depth UI) so the green feedback was hidden**)**
- [x] **U5 — Tutorial 06 Maze (DONE 2026-09-20;** verified by a scripted full playthrough of the tutorial's own maze; off-grid placement jams 1-tile corridors**)**
- [x] **U6 — Tutorial 07 Platformer (DONE 2026-09-20;** found + fixed in EN/FR: lives set in the controller's Create were refilled by every restart_room, so they could never run out -> Game Start**)**
- [x] **U7 — Tutorial 08 Lunar Lander (DONE 2026-09-20;** found + fixed in EN/FR: the pad's success message re-fired every frame (gravity pushing into the pad) -> Set gravity 0; HUD text was black on the black room -> Set draw color white**)**
- [x] **U8 — Tutorial 09 Catch the Coins (DONE 2026-09-20;** found + fixed in EN/FR: a missed coin fell off-screen but stayed alive, so the win check (count == 0) could never fire -> Outside Room sets y = 0**)**
- [x] **U9 — Tutorial 10 File-exchange multiplayer (DONE 2026-09-20;** the tutorial's game built exactly as written and run on two real GameRunners over a shared folder; found + fixed in EN/FR: Phase 1 board invisible (black on black) -> Set draw color white**)** (lab setup: two
      computers or two folders, shared-drive permissions)
- [x] **U10-U13 — Tutorials 11, 12, 13, 14 (2.5D) (DONE 2026-09-20;** checkpoint zips reuse the lesson truth-test builders: `start` and `finished` projects**).**
- [ ] **U14 — Publish:** run the sync, spot-check the live wiki (links,
      accents, downloads resolve). Publishing is outward-facing — get
      explicit approval before the push.

## Cost estimate

Tutorial 1's pair is ≈3,650 words across 4 files. From the French-guide
translation arc (13,500 words ≈ 40% of a session), one tutorial's EN+FR
handout+guide ≈ **8–12% of a session**, so the 13 remaining tutorials ≈
**1.5–2 sessions**, plus U0 and U12 (~10% each). Adding a further language
later is roughly the translation cost only (~3% per language per tutorial).
`.pdf` generation needs the existing script's dependencies; LibreOffice is
only needed if converting an `.odt` back.

## Decisions (settled 2026-09-19)

1. **Scope: everything.** Per tutorial: student handout, teacher guide,
   **and** a worksheet/quiz with an answer key + a project rubric. All 14
   tutorials (Tutorial 1's pair gets the missing worksheet).
2. **Reference solutions: yes, but NOT bundled in the app.** Finished and
   starter `project.json` folders are teacher resources, distributed
   separately through the Wiki.
3. **Languages: English + French** first (no other language until asked).
4. **Delivery: the Wiki, only.** Each document is published as a wiki page
   (readable and printable from the browser), with downloadable files
   (`.pdf`, `.odt`, solution `.zip`) committed to the wiki repo under
   `downloads/` and linked relatively, exactly like `images/` today.
   `scripts/sync_wiki.sh` currently carries only `*.md` + `images/`, so
   U0 extends it to carry `downloads/` too. No IDE menu entry, no release
   attachment.
5. **Order: all tutorials**, in the order of the units below.

### Delivery layout (wiki repo)

    Teacher-Resources.md / Teacher-Resources_fr.md      landing page + course overview
    Teacher-Tutorial-NN-<slug>.md / _fr.md              teacher guide (one page each)
    Student-Handout-NN-<slug>.md / _fr.md               printable student handout
    Worksheet-NN-<slug>.md / _fr.md                     worksheet/quiz + answer key + rubric
    downloads/                                          .pdf, .odt, solutions/NN_<slug>_{starter,solution}.zip

The **answer key stays out of the student-facing pages** (own section at
the bottom of the Worksheet page, clearly labelled teachers-only; the
`.pdf` student copy is generated without it). Repo source stays in
`docs/handouts/*.md` (single source of truth); `wiki/` pages and the
`downloads/` files are generated from it by a script, never hand-edited.

## Not in scope

Translating the in-app tutorial pages themselves; re-recording screenshots
(reuse existing ones; new ones only for the finished-result picture);
slide decks; video.

### U0 as built

- Sources: `docs/handouts/<NN_slug>/{student,teacher,worksheet}.<en|fr>.md` (+ images, hand-edited `.odt`); `docs/handouts/course_overview.<lang>.md`.
- The **answer key and rubric live in the teacher guide** (not a separate worksheet page), so the student-facing worksheet and its PDF need no filtering.
- `python scripts/build_teacher_wiki.py` writes the wiki pages (`Student-Handout-NN-slug`, `Worksheet-…`, `Teacher-Guide-…`, `Teacher-Resources` landing, all with `_fr`), copies PDFs/ODTs into `wiki/downloads/` and images into `wiki/images/handouts/`. It generates a missing `.odt` (needs `soffice`, on Windows `export PATH="$PATH:/c/Program Files/LibreOffice/program"`) but **never overwrites an existing one** (hand-edit risk).
- `scripts/sync_wiki.sh` now also carries `downloads/`.
- `tests/test_teacher_resources.py` is the guard: complete set per tutorial, EN/FR structure parity, French accents, page-count claims vs the tutorial index, wiki pages current with sources, links resolve. Mutation-checked.
- The sequence/time/prerequisite table in `course_overview.*.md` is **provisional** (times from each tutorial's own "Time Required", prerequisites reasoned from content): confirm each row as its teacher guide is written.
- Known nit in Tutorial 1 FR handout: "Appuye sur" should be "Appuie sur" (hand-edited text; fix on the next round-trip).
- Unit recipe for U1+: (1) run the tutorial's build-along in code/real runner and record where it breaks; (2) write student/worksheet/teacher EN then FR; (3) `build_teacher_wiki.py`; (4) tests; (5) reference solutions zip -> `wiki/downloads/solutions/` (decision for U1: build with the raycast builders' approach).


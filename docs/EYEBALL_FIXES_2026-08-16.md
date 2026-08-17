# Eyeball-check fixes — plan (2026-08-16)

Twelve issues found by playing the exports and samples by hand. This plan
groups them by **root cause** rather than by the order they were reported,
because six of the twelve turn out to be one cause, and fixing them
individually would be wasted work.

Registry discipline as usual: work one item per commit, push after each, tick
the box here. A mid-session usage limit then loses nothing.

---

## The central finding: this project ships three different engines

| What you run | Engine | State |
|---|---|---|
| **Test Game** in the IDE | `runtime/run_game.py` → `GameRunner` (pygame) | Complete. 3327 tests. This is "the engine". |
| **Windows .exe / Linux / macOS / Android** | `export/Kivy/` via `BaseKivyExporter` | A *second, hand-written* engine. Its own docstring says "80% GameMaker 7.0 compatible". |
| **HTML5** | `export/HTML5/templates/engine.js` + Pyodide | A *third* hand-written engine. |

All four desktop/mobile exporters share `BaseKivyExporter` — one engine, four
packagers. So issues **4, 5, 6, 7 and 8 are not five bugs.** They are five
symptoms of "the thing you export is not the thing you tested".

That also explains their shape: tiles missing (7, 8), keyboard wrong (5, 6, 7,
8), collision wrong (4, 5), physics wrong (7, 8), sub-image selection wrong
(8). Those are four whole subsystems, each independently reimplemented.

This is the failure mode already recorded in memory as *"audits miss absent
features — every export target needs an end-to-end play-a-sample test"*. The
repo has ~20 export test files and **not one of them plays a sample**; they
all assert on generated strings and file layout. That is why all of this was
green while being broken.

---

## Group A — desktop exports run a different engine (issues 4, 5, 6, 7, 8)

**Decision required before any code is written.** Two routes:

### A1 (recommended) — freeze the pygame runtime instead

`runtime/run_game.py` is *already* a standalone entry point taking
`(project_json, language)`; the IDE launches it as a subprocess. Freezing that
with PyInstaller makes the exported game **the same program Test Game runs**.

- Closes 4, 5, 6, 7, 8 in one change, plus every export bug not yet found.
- Ends the drift permanently: new engine features reach exports for free.
- Known work: PyInstaller spec bundling `run_game.py` + pygame + project data;
  **plugin/extension discovery is the main risk** — `events/plugin_loader.py`
  finds them by globbing `Path(__file__).parent.parent / "plugins"` and
  `extensions/`, then `spec_from_file_location`. Under a frozen app those must
  ship as *data files* and the root must be `sys._MEIPASS`-aware. Two
  functions, but it must be got right or every plugin action vanishes.
- Other risks: binary size (pygame + CPython); macOS signing/notarisation;
  Android still needs Kivy (pygame does not target it), so `BaseKivyExporter`
  stays for that one target.

### A2 — fix the Kivy runtime's four subsystems

Tiles, keyboard, collision, physics/sub-images, one at a time. Honest cost:
four separate investigations in an engine with no way to execute it in CI, and
the gap reopens every time the pygame engine gains a feature. **Only worth it
if Android parity is the priority**, since Android has no alternative.

- [ ] **A0** — decide A1 vs A2. Nothing else in this group starts first.
- [ ] **A1.1** — spike: freeze `run_game.py` + one sample, confirm it launches
      and plugin actions resolve. Timebox; this de-risks everything after.
- [ ] **A1.2** — `_MEIPASS`-aware plugin/extension roots + ship as data.
- [ ] **A1.3** — rewrite `exe_exporter` on the pygame runtime.
- [ ] **A1.4** — same for `linux_exporter`, `macos_exporter`.
- [ ] **A1.5** — end-to-end test: build an export, launch it headless, assert
      it reaches frame N without crashing. The test that would have caught all
      five issues.

## Group B — HTML5 exports show a black window (issue 1)

A third engine, so this is **not** fixed by Group A. maze_1, maze_4 and
raycast_4 all black means it fails early — before any per-sample difference.

**Cannot be diagnosed from here by reading code, and must not be guessed at.**
The first step is to capture the browser console. Precedent exists: the
2026-08-09 session installed Playwright + headless Chromium ad hoc to run real
Pyodide, and that is the right tool again.

- [x] **B1** — diagnosed (`3b7cf9a`). **Two missing commas** in
      `extensions/raycast_2_5d/export_html5.js`, lines 105 and 317. Those
      files are `Object.assign(GameRoom.prototype, { … })` object literals, so
      a member without a trailing comma is a **syntax error** — the whole of
      `engine.js` then fails to parse. Chromium reported
      `Unexpected identifier 'wallShade'`; every engine global was
      `undefined` and the canvas was a single colour, `0,0,0`.
      **Why every sample was black:** extension JS is injected
      unconditionally, so maze_1 — which contains no raycast content at all —
      was broken by raycast's syntax error.
- [x] **B2** — fixed: two commas. maze_1, maze_4 and raycast_4 verified in
      headless Chromium: no page errors, and 8–13 distinct canvas colours
      instead of 1.
- [x] **B3** — `tests/test_export_html5_extension_syntax.py`. CI has no
      JavaScript parser, so it checks the *structure*: every `Object.assign`
      member is comma-separated, braces balance, each extension's JS actually
      reaches a real export (exercised via **maze_1**, deliberately — a
      project using no extension features, which is how this reached
      everything), and the export is UTF-8 with a declared charset.
      Verified it fails when the original bug is reintroduced.

**False alarm worth recording so nobody re-investigates it:** the diagnostic
appeared to show mojibake (`�`) in the exported HTML. That was the *Windows
console* rendering an em-dash through cp1252, not the export. Checked on the
bytes: source, read, write are all UTF-8, `<meta charset="utf-8">` is present,
and there is no U+FFFD anywhere in the output. Encoding is sound, which
matters because French message text is coming.

Likely suspects to confirm or eliminate in B1, in order of cheapness: a JS
exception during load; asset paths failing under `file://`; Pyodide failing to
fetch. Do not pre-emptively "fix" any of these.

## Group C — samples that do not explain themselves

- [x] **C1 (issue 11)** — done. New `spr_gate`: a stone portcullis, drawn by
      the committed `tools/gen_raycast_4_gate.py` (following
      `gen_block_world_face_colors.py`'s precedent, so the art is reviewable
      as intent and regenerable). Deliberately **grey, not gold** — another
      gold object in a key-hunting level is the mistake being fixed. Repointed
      `obj_goal` in **both** `project.json` and `objects/obj_goal.json`; this
      repo's samples carry object definitions twice and updating one is a
      standing trap. Sprite inventory line updated in all 10 guides.
      `tests/test_raycast_4_gate_sprite.py` (6) includes a check that the
      generator still reproduces the committed PNG, so the two cannot drift.
- [ ] **C2 (issue 12)** — minimap shows walls + player only. That was a
      deliberate call in `docs/RAYCAST_MINIMAP_PLAN.md` ("showing pickups
      trivialises a gem-gated maze") — but raycast_4 is *key*-gated, where
      finding keys is the whole task. Add an **opt-in parameter** to
      `draw_minimap` rather than hardcoding, so raycast_2's reasoning still
      holds for raycast_2. Note this touches 3 targets (desktop/HTML5/Kivy)
      and their parity test.
- [x] **C3 (issue 9)** — done. `H` toggles a 7-line control panel, **shown on
      the first frame** so the keys answer themselves before you have to ask.
      Built from existing standard actions only (`draw_rectangle`, `draw_text`,
      `set_draw_color`, `test_variable`, `start_block`/`end_block`), copying
      raycast_3's proven `map_on` toggle idiom — so no new action, and nothing
      for the HTML5/Kivy engines to learn. Applied to both the embedded and
      side-file copies; `H` row added to the en + fr guides (this sample has
      only those two).

      **Real trap hit and now recorded in CLAUDE.md:** on-screen text must be
      QUOTED in the JSON or `_parse_value` evaluates it — the first render
      showed six lines of `0`, because a string containing `-` or `/` goes to
      the expression evaluator. Existing sample text had only escaped this by
      accident (`Lives:`, `M = map` use non-operators). Guarded by
      `tests/test_sample_visible_text.py`, which scans every sample for
      displayed text that would be evaluated rather than printed.
- [ ] **C4 (issue 10)** — views_1 does not communicate its purpose *in-game*.
      The README is clear ("room 3× wider than the window, collect 18 coins");
      the running game says nothing. Add an opening message and a coin
      counter. Fix the game, not the doc.

## Group D — naming and language (issues 2, 3)

- [ ] **D1 (issue 3)** — "Lancer de rayons" is too long and means nothing to a
      student. **Needs a decision** (see below). Display names only: the
      folders stay `raycast_1..4`, so no project files move. Touches
      `widgets/welcome_tab.py` + the 9 language `.ts` files.
- [ ] **D2 (issue 2)** — raycast_4's in-game messages are English.
      **This contradicts a recorded decision** (CLAUDE.md, 2026-07-20): sample
      *messages* were deliberately left English because they are written with
      ordinary `show_message` actions, so translating them would be
      translating what is meant to be the student's own authored content. Only
      the *guides* were translated. That reasoning is weaker for a bundled
      sample a French child is handed — but it is a real decision with a real
      rationale, so it gets reversed deliberately, not silently. **Needs a
      decision** on scope: raycast_4 only, or all 15 samples? French only, or
      all 9 languages? (All samples × all languages is a large, repetitive
      job — the recorded cost for guides alone was ~40% of a session per
      language.)

## Phase E — the cross-platform verification checklist

The second deliverable: a printable checklist for verifying Linux, Windows and
macOS yourself. Planned coverage:

1. **IDE** — launches; fonts and layout not clipped; language switch; accented
   characters render (é è ê à ç ù î ô).
2. **Every sample** — opens, Test Game runs, controls respond, the sample's
   own goal is reachable.
3. **Every export target** — builds *and* the built artifact plays. Both, as
   separate ticks: "it built" is what the current tests check and is exactly
   how these six issues shipped.
4. **HTML5** — in a real browser, from `file://` and from a served directory.
5. Per-platform gotchas (macOS signing/quarantine, Windows SmartScreen, Linux
   SDL video drivers).

Structured one row per check, with platform columns and a notes field.

- [ ] **E1** — write the checklist.

**Sequencing note:** the checklist is listed last because it verifies the
fixes. But you expect there are more issues, and the checklist is what would
*find* them — so writing E1 **first** is a legitimate reordering, and would
let one pass complete the issue list before any fixing starts.

---

## Priorities as stated (2026-08-17), and what they decide

Stated order:

1. **The desktop edition must be absolutely bug free.** The extension
   framework exists so new features don't force core rewrites.
2. **HTML5 export must work for every sample.** A student can always play an
   HTML version of their game.
3. **Linux, Windows and macOS executables** — school labs run Debian, and
   there is a Mac lab too.
4. **Mobile export**, which uses Kivy, is needed as well.

Mapping the groups onto that:

| Priority | Work | Current state |
|---|---|---|
| 1 · desktop edition | C1–C4, D1, D2 | Works; rough edges |
| 2 · HTML5 | Group B | **Totally broken** — every sample black |
| 3 · Win/Linux/macOS exe | Group A | **Broken** — 5 of the 12 issues |
| 4 · mobile | Kivy repair | Broken in the same four subsystems as (3) |

### A0 resolved: freeze the pygame runtime for desktop (A1); keep Kivy for mobile

Priority 4 settles what looked like the hard part: **Kivy has to be repaired
regardless**, because nothing else targets Android/iOS. So the question was
never "Kivy or pygame" — it is only "which engine do the *desktop* executables
ship?"

Given priorities 1 and 3, A1:

- Priority 3 is delivered by *packaging* an engine that is already proven
  (3327 tests), not by bringing a second engine up to parity. Under A2, the
  Debian and Mac labs wait on four subsystem rewrites in an engine that
  **cannot be executed in CI at all** — so its parity could only ever be
  asserted, never demonstrated. That sits badly with "absolutely bug free".
- It decouples priority 3 from priority 4. Kivy's repair then happens at
  mobile's own priority instead of blocking the school labs.
- `runtime/run_game.py` already takes `(project_json, language)` and sets
  `runner.language`, so the entry point needs no redesign.

**Be clear about what A1 does not do:** the four broken subsystems (tiles,
keyboard, collision, physics/sub-images) are *mobile* bugs too. After A1,
mobile exports remain as broken as they are today. That is accepted, because
mobile is priority 4 — but it is not fixed as a side effect.

### D2 re-scoped: this is engine work, not translation work

Checked before estimating, and the estimate was wrong in both directions.

**There is no mechanism to localise authored strings at all.** The runtime
translates its own UI (window caption, high-score table) but `show_message`
text comes straight out of `project.json` as a literal. So issue 2 cannot be
fixed by typing French — the engine has no place to put it.

**The content, on the other hand, is almost nothing.** Every visible authored
string in all 15 samples:

| Action | Count |
|---|---|
| `show_message` | 11 |
| `draw_text` | 6 |
| `draw_doom_hud` | 1 |
| **Total** | **18** |

So this is ~90% mechanism and ~10% typing, and "all samples" costs barely more
than "raycast_4 only". Scope by language, not by sample.

Recommended mechanism, because it reuses a pattern already proven here: a
per-sample catalogue (`samples/<name>/messages.fr.json`) mapping the English
source string to the translation, resolved through the active language with
**fallback to the literal** — exactly how `SampleDocsDialog.guide_path()`
already handles `README.fr.md`. A missing translation degrades to English
instead of breaking, so languages can land one at a time.

One design note with a sequencing consequence: **exports can resolve the
strings at export time** rather than looking them up at runtime. If so,
neither the HTML5 nor the Kivy engine needs to learn about catalogues at all —
which is a large saving, and means **D2 should be designed before A1** so the
exporter only gets written once.

## Decisions needed before starting

### Decided (2026-08-17)

- **D1 — the family is called "2.5 D".** So "2.5 D — Level 1" … "Level 4".
  Technically honest, short, and identical in all 9 locales so it never needs
  translating. **"Views" is left alone for now** — it has the same jargon
  problem, but renaming it was not asked for; issue 10 is being fixed by making
  the sample explain itself in-game instead.
- **D2 — French only for now.** The mechanism carries an English fallback, so
  any other language can be added later with no rework.
- **E1 — checklist last**, verifying the fixes. Fix the known twelve first.

### Resolved earlier, recorded above

- **A0** — freeze the pygame runtime for desktop; Kivy stays for mobile.
- **D2's shape** — engine mechanism, not translation work.

Nothing is left open. Original wording of the questions kept below for the
record:

1. **D1 — the short name.** Applies to all four raycast samples. "2.5 D" is
   technically honest and needs no translation in any of the 9 locales. "3D"
   is shorter still, instantly meaningful to a 10-year-old, and also needs no
   translation; the cost is that it overstates what the engine does, which the
   guide can explain. Note **"Views" has the same problem** and is arguably
   worse (it is engine jargon, and issue 10 says nobody can tell what that
   sample is for) — worth renaming in the same pass.
2. **D2 — which languages.** French only, or all 9? The content is 18 strings
   either way; the multiplier is purely translation effort.
3. **E1 ordering.** Checklist first (completes the issue list before any
   fixing, and is the instrument for "absolutely bug free") or last (verifies
   the fixes)?

## Order, revised against the stated priorities

1. **E1** — the checklist. Cheap, and it is the instrument for priority 1. You
   expect more issues; this is what finds them before effort is spent.
2. **B1** — HTML5 diagnosis. Priority 2 and *totally* broken, and one headless
   Chromium run tells us whether the fix is a line or a month. That answer
   changes everything after it, so buy it early and cheaply.
3. **B2 / B3** — fix HTML5 + a smoke test that loads a real export.
4. **C1 → C3 → C4 → C2**, then **D1** — priority 1 polish. Cheap, visible,
   makes the samples demoable.
5. **D2** — the message-localisation mechanism. Before A1, so the exporter is
   written once (see the design note above).
6. **A1.1 … A1.5** — desktop executables. Priority 3, and the item most likely
   to span sessions.
7. **Kivy repair** — priority 4, for mobile. Tiles, keyboard, collision,
   physics/sub-images, one subsystem per commit.

The one hard ordering constraint is D2 before A1. Everything else can move.

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

- [ ] **B1** — export maze_1 to HTML5, open under headless Chromium, capture
      console + network errors. **Deliverable is the error, not a fix.**
- [ ] **B2** — fix whatever B1 finds.
- [ ] **B3** — smoke test: export a sample, load it, assert the canvas is not
      uniformly black after N frames. Same shape as A1.5.

Likely suspects to confirm or eliminate in B1, in order of cheapness: a JS
exception during load; asset paths failing under `file://`; Pyodide failing to
fetch. Do not pre-emptively "fix" any of these.

## Group C — samples that do not explain themselves

- [ ] **C1 (issue 11)** — raycast_4: `obj_goal` and `obj_key` both use
      `spr_key`. Confirmed in `samples/raycast_4/project.json`. Draw a
      distinct `spr_gate` (the sample already ships its own art: `spr_face`,
      `spr_key`) and repoint `obj_goal`.
- [ ] **C2 (issue 12)** — minimap shows walls + player only. That was a
      deliberate call in `docs/RAYCAST_MINIMAP_PLAN.md` ("showing pickups
      trivialises a gem-gated maze") — but raycast_4 is *key*-gated, where
      finding keys is the whole task. Add an **opt-in parameter** to
      `draw_minimap` rather than hardcoding, so raycast_2's reasoning still
      holds for raycast_2. Note this touches 3 targets (desktop/HTML5/Kivy)
      and their parity test.
- [ ] **C3 (issue 9)** — block_world_1: add an `H`-toggled help overlay
      listing the controls. Buildable from existing actions (`draw_text` plus
      a toggle variable); `maze_3`, `maze_4`, `raycast_2`, `raycast_3` already
      use `draw_text`. **Worth making the pattern reusable** — every 3D sample
      has the same problem.
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

## Decisions needed before starting

1. **A0 — desktop export engine.** Freeze the pygame runtime (A1, recommended)
   or repair the Kivy runtime (A2)?
2. **D1 — the short name.** "2.5 D" was suggested. It is short and accurate,
   and needs no translation in any language — a real advantage across 9
   locales. Worth checking it does not read as jargon to a 10-year-old either;
   alternatives worth a moment: "3D", "Labyrinthe 3D" / "3D Maze", "Vue 3D".
   Whatever is picked applies to all four raycast samples.
3. **D2 — message translation scope.** Reverse the 2026-07-20 decision for all
   samples, or just the 3D ones a French student is most likely to open?
4. **E1 ordering.** Checklist first (to complete the issue list) or last (to
   verify fixes)?

## Suggested order once decided

`E1` (if going first) → `C1` → `C3` → `C4` → `C2` → `D1` → `B1` → `B2`/`B3` →
`A1.1` … `A1.5` → `D2`.

Rationale: the cheap, self-contained sample fixes first, so there is visible
progress and the samples are worth demoing; then diagnosis-led HTML5; then the
big export rework, which is the one item likely to span sessions. D2 last
because it is bulk translation work that is easy to resume and easy to park.

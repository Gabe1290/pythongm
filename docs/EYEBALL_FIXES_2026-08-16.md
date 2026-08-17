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

- [x] **A0** — decide A1 vs A2. Nothing else in this group starts first.
      *Resolved: A1 (see below).*
- [x] **A1.1** — spike: freeze `run_game.py` + one sample, confirm it launches
      and plugin actions resolve. Timebox; this de-risks everything after.
      **Done 2026-08-17 — the answer is yes, and better than hoped.** A
      throwaway spec froze `runtime/run_game.py`; all four bundled
      plugins/extensions load inside the bundle (Audio Actions, Block World,
      LAN Multiplayer, 2.5D Raycast View), and **every sample the user
      reported broken as a Kivy `.exe` runs on it**: maze_1, maze_4,
      plateforme_2, plateforme_3, block_world_1, views_1, raycast_4 all launch
      and keep running headlessly. Two findings carried into A1.3:
      **Pillow is not optional** (`runtime/game_runner.py` imports PIL at
      module level, so excluding it builds clean then dies with
      ModuleNotFoundError on first run), and `pathex=[repo]` lets PyInstaller
      pull the whole engine in by import analysis — only `plugins/`,
      `extensions/` and `translations/` must be declared as datas.
      Also shook out a real, unrelated user-facing bug: emoji in log messages
      crashed the log handler on a cp1252 Windows console, so an asset-import
      failure printed a logging traceback *instead of* the reason
      (`fbbecfd0`).
- [x] **A1.2** — `_MEIPASS`-aware plugin/extension roots + ship as data.
      **Done 2026-08-17 (`555efd49`).** `plugin_loader.get_app_root()` returns
      `sys._MEIPASS` when frozen; `tests/test_frozen_plugin_discovery.py`
      pins it, because the failure is silent — the glob finds nothing, the
      loader logs "Loaded 0 plugin(s)" and a raycast game quietly draws as a
      flat 2D room.
- [x] **A1.3** — rewrite `exe_exporter` on the pygame runtime.
- [x] **A1.4** — same for `linux_exporter`, `macos_exporter`.
      **Both done 2026-08-17 (`0c5116b6`).** New
      `export/desktop/pygame_desktop_exporter.py` holds the whole pipeline and
      the three platform modules shrink to what is genuinely
      platform-specific — the `.exe` suffix + DPI manifest; the Linux
      executable bit; macOS's onedir+`BUNDLE`, quarantine strip and
      symlink-resolving copy. The three targets drifting apart is how the Kivy
      exporters reached this state, so sharing the build is the point.
      Decisions worth keeping: **the project is copied verbatim** (no
      transformation step in which the export and the tested game can
      diverge), so authored `<param>_translations` are resolved by the runtime
      via `GameRunner.language` rather than baked in — and baking would not
      work here anyway, since `GameRunner` re-merges `objects/*.json` over the
      embedded data and would silently overwrite it. `.trash` is excluded so
      soft-deleted assets are not shipped back to the player. The launcher
      redirects `highscores.json` next to the executable, because in a
      one-file bundle the project folder is a temp directory deleted on exit
      and every score would have been lost silently. The build directory moved
      out of the project folder — it now holds a copy of the project, so
      inside it would recurse into itself.
- [x] **A1.5** — end-to-end test: build an export, launch it headless, assert
      it reaches frame N without crashing. The test that would have caught all
      five issues. **Done 2026-08-17 (`3ad078b8`).** The obstacle was
      measurement: a game runs until the player quits, a headless harness
      cannot press a key, and "the process had not died yet after N seconds"
      cannot tell a running game from one stuck on a black screen before its
      first frame. `tools/smoke_run_samples.py` measures the samples by
      importing `GameRunner` and installing a tick hook, which is impossible
      for a compiled binary. So the engine gained two opt-in env-var hooks —
      `PYGM_MAX_FRAMES` (render N frames, print `PYGM_FRAMES_COMPLETED=N`,
      exit 0) and `PYGM_SCREENSHOT` — that cost a player nothing, and
      `tools/verify_desktop_export.py` builds a real export, launches it, and
      with `--compare` diffs its frame against the engine the IDE runs. That
      turns "the export is the same engine" from an argument into a
      measurement. `tests/test_desktop_export_end_to_end.py` is layered by
      cost, with the real PyInstaller build behind `PYGM_E2E_EXPORT=1`.

### Issues 4–8 closed with evidence (2026-08-17)

All five reported samples were built as real `.exe` files on Windows,
launched, and compared against the IDE's own rendering — `5/5 verified`,
90 frames each, every one exiting 0:

| sample | frames | pixels differing from the IDE |
| --- | --- | --- |
| maze_1 (issue 5) | 90 | 0.00% |
| maze_4 (issue 6) | 90 | 0.00% |
| plateforme_2 (issue 7) | 90 | 0.00% |
| plateforme_3 (issue 8) | 90 | 1.74% |
| raycast_4 (issue 4) | 90 | 0.00% |

plateforme_3's 1.74% is **the sample's own non-determinism, not an export
difference**: two runs of the *source* engine differ from each other by 2.14%,
so the export is closer to the IDE than the IDE is to itself. Checked rather
than assumed, because "close enough" is how a real divergence would hide.

The guarantee is structural, which is the point — the four broken subsystems
(tiles, keyboard, collision, physics/sub-images) are not fixed one by one, they
never existed in this engine. Anything the desktop suite already covers now
covers the export too.

**Still worth the user's own eyes:** nobody has *played* an exported build —
these runs prove it renders the same frames, not that it feels right, and
input in particular is only exercised by the samples' own scripted paths. That
is what the Phase E checklist is for.

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
- [x] **C2 (issue 12)** — done, opt-in as planned, so
      `docs/RAYCAST_MINIMAP_PLAN.md`'s reasoning still holds where it applies:
      four new `draw_minimap` parameters (`mark_object`/`mark_color` and a
      second pair) dot named objects onto the map. raycast_4 marks keys gold
      and monsters red; its player marker moved to **white**, since gold keys
      and a gold player on a key-hunting map is the same confusion C1 fixed in
      the 3D view.

      Mirrored across all three engines with the parity test extended (dot
      size, sorted points, opt-in-ness, and dots drawn *under* the player so a
      pickup can never hide it). Verified on the rendered frame by counting
      pixels: 27 gold = 3 dots = 3 keys, 36 red = 4 dots = 4 monsters, matching
      the room exactly.

      **Kivy y-flip trap, hit and caught:** I first wrote the marker points
      from raw instance positions. Kivy is y-UP while the whole raycast
      pipeline is y-down, so every dot would have been mirrored vertically —
      the standing trap on that target. It must go through
      `scene._raycast_gm_xy()`, as the camera marker already did. The parity
      test now asserts the *result* is used, not merely that the helper is
      named: the first version of that assertion passed against the broken
      code.
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
- [x] **C4 (issue 10)** — done, and **my diagnosis in this plan was wrong.**
      I assumed the sample simply failed to explain itself. The real cause is
      an engine bug: `GameRunner` sized the window to the ROOM
      unconditionally, so views_1 rendered its whole 2400×800 room in one
      window. Views were enabled and correct (an 800×600 port), but the entire
      room was already visible, so the scrolling camera the sample exists to
      demonstrate had nothing to do. "What is this supposed to do?" was the
      right question to ask.

      New `GameRunner._window_size_for()` clamps to the declared window size,
      **per axis and only downwards**, used by all four sizing sites. Blast
      radius was the real risk and is pinned by a test: a blanket "honour the
      setting" would have resized raycast_1–4 (640×480 declared, 480×480
      rooms) and moved raycast_4's tuned DOOM HUD. Measured across all 20
      samples: only views_1 and views_2 change.

      Verified by holding the right-arrow and watching `view_x` go 0 → 304 as
      the player crosses the 240px border — the camera genuinely scrolls now.

      The in-game explanation landed too, since it was worth having anyway:
      an opening message, a `draw_gui` HUD (score + "Collect all 18 coins"),
      and a win message when the last coin goes. **`draw_gui`, not `draw`** —
      it is in screen coordinates and unaffected by the camera, so the HUD
      stays put while the room scrolls underneath.

## Group D — naming and language (issues 2, 3)

- [x] **D1 (issue 3)** — done. The family is **"2.5 D"**: `2.5 D — Level 1`,
      `2.5 D — Niveau 1`, `2.5 D — Уровень 1` … Folders stay `raycast_1..4`,
      so no project files moved.

      Renamed in `widgets/welcome_tab.py`, the 7 `.ts` catalogues that carry
      the names (pt/ja/zh translate no sample names at all — pre-existing, and
      the rename leaves them clearer than before), all 36 guide titles, and the
      27 guides that *instruct* the reader to pick a Welcome-tab entry by name,
      which would otherwise have named something that no longer exists.
      Each language kept **its own** word for "level" by rewriting only the
      name half of the string, rather than my inventing translations.

      **The technique is still raycasting** and prose saying so was left alone
      — only the display name changed. Verified per language with a live
      `QTranslator` after recompiling.

      **Tooling bug fixed en route:** `scripts/compile_translations.py` could
      not find `lrelease` on this Windows box at all, so no translation work
      was compilable here. Its search list assumed a project venv or a Linux
      `~/.local` layout and then shelled out to `which`. It now asks the
      installed `PySide6` where it lives and uses `shutil.which` — relevant
      well beyond this item, given the three-platform goal.
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

~~**There is no mechanism to localise authored strings at all.**~~
**CORRECTION (2026-08-17): partly wrong.** A mechanism exists and predates
this plan:

- `events/action_editor.py` has offered a translation dialog for **any**
  string parameter since it was written, storing `<param>_translations` dicts.
- But the runtime read **only `message_translations`, only for
  `show_message`** — so an author could enter translations for a `draw_text`
  and the engine would silently ignore them. The IDE promised what the engine
  did not deliver.

`localize_param()` now honours the convention for every display string
(`message`, `text`, `caption`), which is **D2a, done**. What was genuinely
missing was never the storage — it was the runtime honouring it, and the
exports.

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

No new catalogue file format is needed after all — the existing
`<param>_translations` convention is the mechanism, and it keeps each
translation next to the string it translates.

**The export half is now the whole problem, and it is confirmed, not
suspected.** Neither export engine reads these dicts: `engine.js`'s
`show_message` uses `params.message` only, and `export/Kivy/` contains no
mention of translations at all. `tests/test_raycast_2_sample.py`'s
`test_goal_messages_are_plain_english` even encodes this as a reason not to
translate samples — *"keeping the sample free of a translation dict means it
behaves identically on every export target"* — and on the facts it was right.

So **resolve translations at EXPORT time** (D2c): the exporter bakes the
chosen language's string into the exported project's plain parameter. Then
neither engine needs translation support, they cannot diverge from the
desktop, and — importantly — this touches neither of the two engines that are
currently broken. Remaining units:

- [x] **D2a** — runtime honours `<param>_translations` for every display
      string. 16 tests; all four mutants caught, including one that needed a
      dict *containing* an `en` key to expose the English short-circuit.
- [x] **D2b** — done. French for all 24 distinct on-screen strings across the
      samples, attached as `<param>_translations` and keyed by the exact
      English source, so an English edit shows up as an unmatched entry rather
      than being silently skipped. Verified end to end: raycast_4's HUD reads
      **VIE / SCORE / CLÉS** on the desktop, and a French HTML5 export carries
      `('VIE', 'CLÉS ')` with no translation dicts left.

      `test_goal_messages_are_plain_english` is replaced by
      `test_goal_messages_are_english_with_a_french_translation`, which keeps
      the half of the old reasoning that still holds — the BASE string stays
      plain English, so a student reads and edits ordinary authored text — and
      records that the export-parity objection was removed by D2c rather than
      overruled.

      **DOOM HUD labels** needed the extension handler routed through
      `localize_param` too; they were read straight from the parameters.

      **Two bugs fixed on the way, both found by running the game rather than
      by reading it:**
      1. `maze_4`'s win message was `"CONGRATULATIONSYou finished all
         levels."` — a missing `#`, GameMaker's line break, so it rendered as
         one run-on word.
      2. My own C4 quoting was wrong in the *other* direction. Only
         `draw_text` runs through `_parse_value`; `show_message`,
         `draw_score`'s caption and the DOOM labels are used verbatim, so the
         defensive quotes I added to views_1's messages were **drawn on
         screen**. `tests/test_sample_visible_text.py` now checks both
         directions — quoting required where a string is evaluated, forbidden
         where it is not — and covers translation values as well, since French
         prose contains hyphens far more often than the English did.
- [x] **D2c** — done. `export/message_localizer.py`'s `resolve_translations()`
      bakes the chosen language into the plain parameter and drops the dict, so
      the exported project contains ordinary one-language strings and neither
      export engine needs to learn about translations at all.

      Hooked at the two funnels: `HTML5Exporter.export()` and
      `BaseKivyExporter._load_project()` — the latter covers exe, Linux, macOS
      and Android together. **Both hooks must sit after the side-file merge**,
      since `objects/*.json` overwrites the embedded objects; a test pins that
      ordering, and my first fixture got it wrong in exactly that way.

      Language comes from the IDE's current language by default
      (`core.language_manager.current_language_code()`), because an author's
      language is their students' language. Made a module-level function rather
      than a method: several tests drive `_current_export_options` unbound on a
      stub, and requiring `self` there put the language lookup into every
      stub's contract for no benefit — that mistake broke 10 tests before it
      was cleaned up.

      **A vacuous test caught here, worth remembering:** the HTML5 assertions
      first searched the exported HTML for the sentinel strings. gameData is
      gzip+base64 compressed into the page, so no project string ever appears
      as text — meaning "no translation dict survives into the export" was
      passing while proving nothing. The tests now inflate the embedded
      gameData and assert on the real shipped JSON. All four hook mutants are
      caught.

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

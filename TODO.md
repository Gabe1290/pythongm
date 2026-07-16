# TODO — Deferred Features

Features that are planned but not yet implemented. Anything listed here used to
either show a "Not Implemented" placeholder dialog or be a stub the user could
click and reach a dead end. To keep the IDE honest, the menu items / buttons
have been removed; the work is tracked here instead.

Add new entries at the top of each section. When you start implementing one,
move it to a feature branch and remove the entry once the feature ships.

**2026-07-15: `docs/DEFERRED_ITEMS_PLAN.md` triages and sequences this
whole registry** (small-and-ready items first, then moderate-effort ones,
then larger multi-session efforts, then explicitly-not-now items) — read
it before picking an item to work on.

---

## IDE features

### ~~Consolidate the two export UIs~~ (DONE 2026-07-12)
- Done: File → Export Project… (Ctrl+E) and Build → Export Game… both
  open the single registry-driven dialog. ExportProjectDialog (and the
  never-referenced BuildProjectDialog) were retired; its distinct
  targets became registry entries (`kivy_project`, `source_zip`), its
  Export Options checkboxes moved into the unified dialog (and now
  reach the desktop/Android runner shells, which had L9's hardcoded
  dict), and its host-OS desktop routing moved to
  `export.registry.desktop_exporter_for_host`. The M13/L8/L9 audit
  tests were migrated to the consolidated path
  (`test_export_dialog_routing/options.py`,
  `test_audit_project_dialogs.py`, `test_desktop_export_host_routing.py`).

### ~~Find / Find and Replace~~ (DONE 2026-07-16, code editor scope)
- Done (deferred-items plan tier 2, item 5): `Edit → Find...` (Ctrl+F) and
  `Edit → Find and Replace...` (Ctrl+H) restored, wired exactly where the
  rc.11 cleanup (`77e9dbf`) removed them. New `dialogs/find_replace_dialog.py`
  (`FindReplaceDialog`) is a non-modal find/replace bar — case-sensitive and
  whole-word toggles, wraparound Find Next/Previous, Replace (only acts on a
  selection that's a live search match, then advances), Replace All (uses the
  standard Qt `while edit.find(text): cursor = edit.textCursor();
  cursor.insertText(replacement)` idiom, which can't loop forever even when
  the replacement text contains the search text, e.g. `cat` → `cats cat`).
  `core/ide_window.py`'s new `_find_target_text_edit`/`_show_find_dialog`
  reuse the existing `_active_editor()` dispatch (same one Undo/Redo/Cut/
  Copy/Paste/Duplicate already use) and reuse a single dialog instance
  across repeated Ctrl+F presses, rebinding its target each time. Regression:
  `tests/test_find_replace.py` (20 tests) — the dialog's search/replace logic
  against a real `QPlainTextEdit`, plus the IDE-level dispatch via the
  established `PyGameMakerIDE.method(stub, ...)` unbound-call pattern.
- **Scoped narrower than the original note, intentionally:** only
  `editors/script_editor.py`'s `QPlainTextEdit` (the sole real code-editing
  widget in the app — verified nothing else uses `QPlainTextEdit`) is wired
  up. "Room editor scripts, event scripts" (the `execute_code` action's
  `QTextEdit` inside `editors/object_editor/gm80_action_dialog.py`, a modal
  per-action dialog, not an editor tab `_active_editor()` can see) and
  project-wide search (asset names, identifiers) are **not** covered —
  genuinely separate follow-up work, not silently dropped scope.

### Asset Manager
- Was: `Tools → Asset Manager...`.
- Scope: bulk operations on assets (rename, move, delete in batch), search and
  filter, usage tracking ("which rooms / objects use this sprite?"), and
  unused-asset cleanup.
- Current workaround: the Asset Tree panel on the left handles single-asset
  operations.
- Notes: removed the menu entry and the `show_asset_manager()` stub in
  `core/ide_window.py`.

### Clean Project
- Was: `Tools → Clean Project`.
- Scope: remove temporary files, delete unused assets, clean build artifacts,
  shrink project size.
- Current workaround: manually delete `.cache/`, `__pycache__/`, `*.pyc`.
- Notes: removed the menu entry and the `clean_project()` stub in
  `core/ide_window.py`.

### ~~Standalone executable build (Build Game / Build and Run)~~ (DONE
2026-07-16, deferred-items plan tier 2, item 7 — closes tier 2)
- Done: `Build → Build Game...` (F7) and `Build → Build and Run` (F8)
  restored, exactly where the rc.11 cleanup (`77e9dbf`) removed them
  (menu entries, actions, and the `has_project` enable/disable wiring).
  Confirmed the plan's prediction — "wiring a menu action + progress UI
  around an existing capability, not new export infrastructure": both
  are thin shells (`build_game`/`build_and_run` → shared `_build_desktop`)
  around the exact same `export.registry.desktop_exporter_for_host` +
  `_run_export_with_progress` machinery the Export Game dialog's Windows/
  macOS/Linux entries already use — same PyInstaller-based exporter
  classes, same progress dialog, same host-OS artifact selection (exe /
  ELF binary / `.app`, since PyInstaller can't cross-compile). `Build and
  Run` additionally launches the freshly-built artifact, via one new
  optional `on_success` callback parameter added to
  `_run_export_with_progress` (called after a successful build,
  regardless of the "open output folder?" answer; `None` for every
  existing caller, so no behaviour change there) — `_launch_built_game`
  locates the artifact by re-deriving its exact filename from the same
  `re.sub(r'[^A-Za-z0-9_]', '_', project_name)` sanitizer each exporter's
  `_create_spec_file` already uses, rather than scanning the output
  directory. Regression: `tests/test_build_game.py` (16 tests) — routing
  (`_build_desktop` picks the right exporter class, threads output dir/
  checkbox options through, no-op on no-project/cancelled-dialog),
  `_launch_built_game`'s per-platform path construction against real
  temp files, and a from-scratch `on_success` integration test that
  exercises the real `_run_export_with_progress` with a fake exporter
  (a real `QThread`-driven version would be non-deterministic in a test,
  so `ExportThread` is swapped for a `QTimer.singleShot(0, ...)`-based
  stand-in that preserves the real "thread starts, then exec() blocks
  until the completion signal arrives" ordering — completing the signal
  before `exec()` starts would hide an unshown dialog and hang the
  subsequent `exec()` forever, a real trap worth documenting for anyone
  else testing this method).
- Kept out of scope, per the original note: Android `.apk` (handled
  separately by `export_android_apk`/the Kivy export path, already a
  dedicated Export Game dialog entry) and iOS.

### ~~Object test runner ("Play Object" button)~~ (DONE 2026-07-15)
- Done (deferred-items plan tier 1): a "▶ Play Object" toolbar button in the
  Object Editor (`editors/object_editor/object_editor_main.py`) emits
  `test_object_requested(name, data)`; `core/ide_window.py`'s
  `PyGameMakerIDE.test_object` builds a throwaway temp project (just the
  object + its sprite, if any, copied alongside it + one small test room)
  and launches it through the *same* subprocess-supervision path Test
  Game uses (`_run_project_json`, factored out of `test_game` so both
  share it rather than duplicating the Popen/stderr-capture/QTimer-polling
  logic) — the real runtime, not a simulation. The temp dir is cleaned up
  in `_drain_game_stderr` (which both the normal-exit and manual-stop
  paths already call), so a Play Object run can't leak a temp directory
  either way. Tests the editor's live in-memory state, not a saved
  project — no save/validate step, matching a "quick preview" workflow.
  Other object types the tested object references (e.g. a collision
  event against `obj_enemy`) won't exist in the throwaway project, so
  those specific events won't fire — an accepted isolation limitation,
  not a bug.
- Regression: `tests/test_play_object.py` (guards, temp-project building,
  sprite copying, missing-sprite-file degradation, cleanup). The
  `test_game`/`_run_project_json` split required updating 3 pre-existing
  tests' lightweight stubs (`test_audit_ide_window_leaks.py`,
  `test_test_game_editor_sync.py`, `test_open_editors_composite_key.py`)
  to also provide the newly-factored-out method — same "give the stub
  every attribute the real method body touches" convention those tests
  already used for `_drain_game_stderr` etc.

### ~~Generic asset-type editor fallback~~ (DONE 2026-07-15)
- Done: `sounds`, `backgrounds`, and `fonts` now have minimal form editors
  (`editors/sound_editor.py`, `editors/background_editor.py`,
  `editors/font_editor.py`), following the `scripts` editor's template —
  a thin `BaseEditor` form, not a re-import surface. Sound adds a Play/Stop
  preview button (`pygame.mixer`); background adds a read-only image
  preview; font adds a live sample label. Wired into
  `on_asset_double_clicked`'s dispatch and `_canonical_category` (the
  singular→plural rename-signal mapping — missing this would silently
  break the open-tab-on-rename path). Round-trip + no-dirty-on-load
  regression tests: `tests/test_asset_type_editors.py`.
- ~~New finding, not fixed: nothing reads a font asset's `font_name`/
  `size`/`bold`/`italic` back~~ **DONE 2026-07-16.** `GameInstance` gained
  `_resolve_draw_font` (looks `self.draw_font` up in
  `project_data['assets']['fonts']`, builds/caches a real
  `pygame.font.Font`/`SysFont` honoring family/size/bold/italic, falls
  back to the old hardcoded 24pt default when unset or missing) and
  `_align_text_pos` (shifts the blit position per `draw_halign`/
  `draw_valign`, which were also being stored and never read).
  `_font_cache` is now keyed by `(family, size, bold, italic)` instead of
  just `size`. `_draw_text`/`_draw_scaled_text` call both. Regression:
  `tests/test_draw_font_rendering.py` (14 tests) — end-to-end cases render
  onto a real `pygame.Surface` and inspect actual pixel bounding boxes
  (`Surface.blit` can't be monkeypatched), confirming alignment shifts and
  that a bigger font asset genuinely produces wider glyphs.
- Formalizing the registration so a future new asset type fails loudly at
  startup (instead of silently at click time) is still open, but lower
  priority now that all current asset types are covered.
- Same applies to the create-asset fallback in
  `widgets/asset_tree/asset_tree_widget.py` — it now logs and returns silently
  when no `create_asset` handler is reachable.

### UI metadata coverage for runtime actions (partial in rc.12)
- The runtime knows ~207 actions (executor `execute_*_action` methods +
  modular handlers in `runtime/action_handlers/`); the UI-side
  `events/action_types.py` registry covers them progressively. After the
  rc.12 bulk-add + the 2026-06-05 "safe bucket" sweep, the *executor*
  handlers split as: covered (or aliased) vs. intentionally deferred.
- **2026-06-05 sweep (for 1.0):** added the "safe & worth it" bucket —
  30 working actions that lacked metadata (draw_text/lives/set_draw_font
  first, then draw primitives rectangle/circle/line/ellipse/arrow/sprite/
  background/variable/health_bar, set_alpha/color/image_index/image_speed,
  start/stop_animation, the test_*/check_* conditionals, stop_sound,
  move_towards_point, open_webpage, show_info, set_room_caption). All
  verified against their runtime handlers' params; edit dialogs round-trip.
- **Still deferred to post-1.0 (do NOT add UI yet):** particle system
  (create_emitter/burst_particles/…), timelines (set_timeline/start_timeline/
  …), save_game/load_game, show_video, execute_script — these need a
  functional check first; and the room-background/scrolling actions
  (set_background*, set_room_speed/persistent) which are incomplete —
  exposing them would re-introduce the rc.11 "stop lying to users"
  anti-pattern.
- **Views/camera — IN PROGRESS (2026-07-15).** No longer fully deferred.
  Plan: `docs/VIEWS_SAMPLES_PLAN.md`. Done: HTML5 8-view camera (`552a9bc`,
  Chromium-verified); `enable_views`/`set_view` **registered** in
  `events/action_types.py` (category "Views"); 3-target parity test
  (`df0a3e9`); the `views_1` sample (`fc37aea`). State by target: **desktop ✅,
  HTML5 ✅ (multi-view: per-view clip+translate), Kivy/Android ✅ (multi-view:
  the room renders into an Fbo and each visible view blits its region into its
  screen port via tex_coords; the OS window is sized to the view, not the room,
  so the camera shows a true scrolling slice).** Non-views Kivy rooms keep the
  original child-widget path untouched. `tests/test_kivy_views.py` covers
  single- and multi-view. The `enable_views`/`set_view` actions are now emitted
  by the Kivy code generator too (via `scene.set_views_enabled`/`apply_set_view`),
  so runtime camera reconfiguration works. **Residual limitation:** the Fbo
  render target is built at room construction, so a room needs `views_enabled`
  in its config for the Kivy camera to render (enabling views purely via a
  runtime action on a non-views room won't retro-fit the Fbo). Both `views_1`
  (single scrolling camera) and `views_2` (split-screen multi-view) samples
  ship. **Phase 1 + 2 complete.**
- Recipe for adding more: see the comments at the bottom of
  `events/action_types.py` and the survey script that lived briefly at
  `.scratch_find_missing_actions.py` (removed after the bulk pass).
- A future cleanup might generalise `get_action_type` to fall back
  through `ActionExecutor.ACTION_ALIASES` so legacy/alternate action
  names resolve to a single ActionType without duplicate entries.

### GMK importer hardening (post-1.0)
- Working plan + checkbox registry: `docs/GMK_IMPORTER_HARDENING_PLAN.md`.
- During rc.12 user-testing the **`treasure.gmk`** and **`maze_4.gmk`**
  samples both exposed importer issues the IDE could only partially
  round-trip — the imported projects loaded but had bad action
  parameters, sprite issues, and half-converted events that produced
  confused state and save errors in the editor surface. Both samples
  were dropped from the bundled set (treasure in commit d3fd71a,
  maze_4 in the commit that adds this entry); they can be
  reintroduced once the importer is hardened.
- **2026-07-16 update:** both `.gmk` sources recovered from git history
  (they were committed once, then untracked when native project folders
  became the shipping format — never actually lost) and re-imported
  fresh. Result: **zero unmapped-action stubs, expected asset counts,
  for both** — a strong sign the importer has closed most of its gaps
  since rc.12 (from general `GM_ACTION_MAP` work over the following
  months, not anything specific to these two samples). Pinned by
  `tests/test_gmk_treasure_maze4_import.py`. **Not yet re-added to the
  bundled set** — a clean unmapped-action result isn't proof of full
  correctness; still needs a visual playtest / test-game smoke run /
  asset-reference check before shipping. See the plan doc for detail.
- The earlier hypothesis that only treasure was affected (because
  it's the only one using project-level scripts) was wrong: maze_4
  has no scripts but still imports with significant gaps. The
  importer issue is broader than first scoped — likely action-
  parameter parsing across a wider feature set than the smaller
  maze_1..3 samples happen to exercise.
- TODO once we have time for it:
  - Regenerate `samples/treasure/` and `samples/maze_4/` from the
    `.gmk` originals (regen path documented in `samples/README.md`).
  - For each, compare against the in-game behaviour of the original
    `.gmk` — e.g. via GameMaker 8.x if available, or by inspecting
    the `.gmk` binary structure with `importers/gmk_parser.py`.
  - Catalog every action whose parameters didn't survive the
    conversion. Likely categories:
      * Action parameter keys renamed (GameMaker had positional
        args; pygm2 expects named) — most-likely root cause
      * Sprite / object references renamed silently when assets had
        case-conflicting or whitespace-bearing names
      * Project-level scripts (`treasure` only) — code that
        references GameMaker built-ins not implemented in the pygm2
        runtime
      * Draw events using `draw_self`, `draw_sprite_ext`, etc.
        without matching UI metadata (the metadata gap is tracked
        separately above)
  - Each finding gets a separate fix in `importers/gmk_*.py` and a
    regression test under `tests/test_importers/`.
  - Consider building a side-by-side diff tool: import a `.gmk`
    twice (once raw, once after each fix) and diff the resulting
    `project.json` trees so regressions in the importer surface as
    review-blocking diffs in CI.
- The maze_1..3 samples shipped clean enough for rc.12 user
  testing — the issue compounds with project complexity
  (room/object count, action variety), so the smaller samples may
  hide the same bugs rather than truly being unaffected. Worth
  re-validating the maze_1..3 imports as part of the eventual
  hardening pass.
- **Concrete findings from rc.12 maze_1 testing pass — RE-VERIFIED
  2026-07-16, both are original-game data, not importer bugs (see
  `docs/GMK_IMPORTER_HARDENING_PLAN.md` for the raw-byte verification
  method):**
  - ~~The importer mistranslated `if_previous_room_exists` into
    `if_next_room_exists`...~~ **Not an importer bug.** Dumped the raw
    parsed `GmkAction` records directly (bypassing the converter): the
    `.gmk` binary itself encodes `id=226` (`if_next_room_exists`) for
    *all three* of `obj_goal`'s events, including the `p`
    (previous-room) keypress — `GM_ACTION_MAP`'s `(1,226)`/`(1,227)`
    entries are correct and the converter faithfully reproduces what's
    actually in the source file. Reads as a copy-paste bug in the
    *original GameMaker 8 game* (collision event's action block reused
    verbatim in both keypress events). The shipped `samples/maze_1/`
    hand patch (`if_previous_room_exists` for the `p` key) is a
    deliberate gameplay fix layered on top of a faithful import, not a
    fidelity restoration — if `maze_1` is ever re-imported from scratch,
    expect the original bug back and re-apply the same hand patch.
  - ~~The importer set `visible: false` on `obj_goal`...~~ **Not an
    importer bug**, same verification method: `obj_wall`/`obj_person`
    both parse as `visible=True` (so the parser's field order isn't
    systematically wrong), but `obj_goal` genuinely parses as
    `visible=False` from the raw byte stream, and has no `draw` event to
    compensate. The original `.gmk` really does mark `obj_goal` invisible
    with no manual draw workaround. Same conclusion: genuine original-game
    bug, faithfully imported; the shipped sample's `visible: true` is a
    deliberate fix layered on top, not fidelity restoration.
  - Bundled maze_1 was patched manually in the IDE after these
    findings; the corrected `samples/maze_1/` is back in git.
- **Concrete findings from rc.12 maze_3 testing pass — RE-VERIFIED
  2026-07-16, all already fixed (fresh `maze_3.gmk` re-import produces
  zero unmapped-action stubs and matches the shipped sample
  byte-for-byte on every action checked; see
  `docs/GMK_IMPORTER_HARDENING_PLAN.md`):**
  - `samples/maze_3/objects/monster_all.json` originally contained
    pairs of `(set_score value=hspeed relative=true)` +
    `(comment "Unmapped GM action: lib=1, id=425, kind=4")` between
    each `set_direction_speed`. The kind=4 comment was the GameMaker
    `exit_event` action — the converter only dispatched on
    `(library_id, action_id)` and missed it. Fixed by adding
    `_GMK_KIND_TO_ACTION` in `importers/gmk_converter.py` so all
    action_kind values 1/2/3/4/5 produce the canonical control-flow
    action regardless of which library/id the GMK file used.
  - ~~The companion `set_score(value=hspeed, relative=true)` lines...~~
    **Also fixed** — a fresh re-import now correctly produces
    `check_empty(x=hspeed, y=vspeed, objects=solid, relative=true)`
    where the old mis-import produced `set_score`, and the shipped
    `samples/maze_3/objects/monster_all.json` already matches that fresh
    import byte-for-byte (the "hand-stripped, deterministic +90° turn"
    workaround described below is stale — the sample was already
    regenerated with the real test-each-candidate-direction logic at
    some point after this note was written, just never updated in this
    doc).
  - `start_moving_direction`'s `directions` parameter accepts a list
    (e.g. `["down", "up"]` for a random-pick monster) but the events
    panel has no multi-select widget for list-typed action params.
    The field falls back to a `QLineEdit`, which serialises a list
    via `str([...])` — so opening + re-saving a list-typed action
    in the editor permanently converts it to the string
    `"['down', 'up']"`. Runtime now tolerates this stringified form
    (`ast.literal_eval` fallback in `execute_start_moving_direction_action`)
    so existing data keeps working, but a proper fix would be a
    `multi_choice` param_type backed by a row of QCheckBox widgets.
    Same gap likely affects other list-typed action params if any
    exist; check for other `isinstance(directions, list)` consumers.
  - ~~The GMK importer mis-maps `action_play_sound`... to `set_sprite`~~
    **Fixed — re-verified 2026-07-16.** A fresh `maze_3.gmk` re-import
    now correctly produces `play_sound` with the right sound name at all
    five originally-affected locations (`controller_main.json`,
    `obj_person.json` ×3, `obj_block.json`, `obj_hole.json`,
    `obj trigger.json`). `GM_ACTION_MAP` already has `(1, 212)` and
    `(1, 551)` mapped to `play_sound`; whichever of those two is the
    actual id in this file, it's covered now.
  - ~~The GMK importer was missing the `(1, 223)` mapping...~~ **Fixed —
    re-verified 2026-07-16.** `GM_ACTION_MAP` has `(1, 223):
    "restart_room"` (`importers/gmk_mappings.py:379`) with the matching
    `["transition"]` param row; a fresh re-import produces no unmapped-id-223
    comment stubs.

---

## Runtime action handlers (stubs that just log and return)

In `runtime/action_handlers/extra_handlers.py`:

- **Splash text / image / video / webpage** (lines 51, 57, 63, 69) — these are
  placeholders. Need real implementations using Pygame surfaces / video
  decoder / `webbrowser` module respectively.
- **Execute file** / **Execute shell command** (lines 84, 90) — intentionally
  restricted for security. If we ever expose them, they need to be sandboxed
  and require explicit user opt-in per project.

Other:

- **Script execution action** — `runtime/action_handlers/control_handlers.py:239` —
  stub only. Decide on the script language (Python? a sandboxed mini-DSL?)
  before implementing.
- **Thymio "play sound"** — `runtime/thymio_action_handlers.py` — placeholder
  that emits a single tone instead of playing the requested sound resource.

## Runtime features called out in code

- ~~**Background auto-scroll on `set_background`**~~ (DONE 2026-07-16,
  deferred-items plan tier 2, item 6) — `execute_set_background_action`
  (`runtime/action_executor.py`) now writes its `hspeed`/`vspeed`
  parameters onto `game_runner.current_room.bg_hspeed`/`bg_vspeed`
  (coerced to float, falling back to 0 on a bad value) alongside the
  existing `tile_horizontal`/`tile_vertical` wiring. `GameRoom` already
  had a fully working `bg_hspeed`/`bg_vspeed`-driven scroll renderer
  (`_render_legacy_background` — accumulates and wraps the scroll offset,
  auto-tiles once either speed is nonzero) serving room-config-authored
  backgrounds and `set_view`; the gap really was just this one action
  never writing to it, confirming the plan's re-scoping note ("smaller
  than it looked"). `foreground` stays acknowledged-but-not-applied — the
  legacy single-background path has no draw-in-front-of-instances
  support at all (only the newer multi-layer `backgrounds` room format
  does, via `_render_bg_layers`), which is unrelated pre-existing scope,
  not part of this fix. Regression: `tests/test_background_scroll.py` (6
  tests) plus an end-to-end case that calls the real
  `GameRoom._render_legacy_background` across several frames and checks
  the scroll offset actually accumulates and wraps.
- ~~**Room transition effects**~~ (DONE 2026-07-15, deferred-items plan
  tier 1) — `goto_room`'s `transition` parameter now supports `'fade'`
  (fade to black, switch, fade back in — `GameRunner.change_room`/
  `_fade_overlay`, `runtime/game_runner.py`). Any other value (including
  the default `'none'`) stays instant, unchanged. **Desktop pygame
  runtime only** — Kivy/HTML5 exports still switch instantly; no bundled
  sample currently exercises `transition` at all (only the `execute_code`
  `self.goto_room_target = ...` pattern and the `next_room`/
  `previous_room`/`restart_room` sentinels, none of which carry a
  transition param), so there's nothing to verify export parity against
  yet — scoped to desktop until a sample or user need shows up. Caught a
  real bug in its own first draft: the fade-in/fade-out alpha ramp was
  inverted (screen went black and stayed black) until
  `tests/test_room_transition_fade.py`'s pixel-sampling test (plus a
  10-frame visual montage) caught it.

## Translations / i18n

### Migrate ja / pt / zh off the legacy translation set (post-1.0)
- The language menu still lists Japanese, Portuguese, and Chinese, but those
  three run on the abandoned `translations/pygamemaker_{ja,pt,zh}.ts` files
  (legacy monolithic format). Their contexts reference source strings that no
  longer exist in the codebase — e.g. the `WelcomeTab` context still lists
  `Quick Actions`, `Create Room (Ctrl+R)`, and `Create amazing 2D games with
  visual scripting`, none of which the current `widgets/welcome_tab.py`
  emits — so essentially the whole IDE renders in English for these locales,
  not just the Welcome tab.
- The six maintained locales (fr/de/es/it/ru/sl/uk) live in the `pygm2_XX*`
  split-file system and were brought fully up to date for the Welcome tab.
- TODO once we have time: regenerate `pygm2_{ja,pt,zh}*.ts` from current
  sources (same `pylupdate6`/split-group layout the other languages use),
  translate, compile to `.qm`, and retire the `pygamemaker_*.{ts,qm}` legacy
  files. Until then ja/pt/zh are effectively English with a flag.

## Project format / persistence

### Manifest-ify objects & sprites in project.json (pre-1.0-final)
- **Do this carefully, with a round-trip test, just before the final
  validation pass before the 1.0 release.** It changes the on-disk save
  format for every project, so it is deliberately scheduled late.
- Today the modular split is half-done. `_prepare_project_data_for_save`
  (`core/project_manager.py`) strips **rooms** (instances) and **playgrounds**
  (walls/robots/colors) out of `project.json`, leaving only a metadata stub +
  `_external_file` pointer — clean single-source-of-truth. **Objects and
  sprites never got that treatment:** they are written *both* as full bodies in
  `project.json` *and* to `objects/*.json` / `sprites/*.json`. That dual storage
  is why editing an asset means editing both files in lockstep or they drift
  (the loader hides the drift because `merge_object_file` lets the modular file
  win). Big `project.json`, unreviewable diffs, and Dropbox/git conflict
  surface are the cost — see the rc.12 plateforme_3 cleanup where obj_power had
  to be removed from both places.
- TODO: extend the rooms/playgrounds pattern to objects and sprites — on save,
  store only a reference/manifest entry in `project.json` (asset name +
  `_external_file`, like rooms do) and keep the body solely in the per-asset
  file. The loader already tolerates string-reference entries (`isinstance(
  object_data, str)` branches in `_load_objects_from_files` /
  `_load_sprites_from_files`), so the read path mostly works already.
- Round-trip test is mandatory: load a representative project → save → reload,
  and assert the in-memory `current_project_data` is byte-for-byte equivalent
  (no events/sprite-frames/params lost), for both a fresh project and a legacy
  embedded-only one. Prove it against pre-refactor HEAD per the audit
  methodology. Also verify `.zip` export/import still round-trips.
- Why it matters long-term: smaller `project.json`, clean per-asset git diffs,
  and far less Dropbox "conflicted copy" / merge risk across the multi-machine
  workflow.

## Export

### Kivy/Android export — remaining parity gaps (draw-queue + mouse LANDED)
- Found while validating the `match3_1` bundled sample (2026-07-03) for
  Android. The two blocking gaps were **fixed the same day** in
  `export/Kivy/kivy_exporter.py` (regression tests:
  `tests/test_kivy_draw_queue_mouse_export.py`, which also runs the exported
  match3_1 game headlessly against stub kivy modules — the first
  execute-the-generated-code export test):
  - ✅ **`draw` events now run.** The exported `GameObject` initializes
    `self._draw_queue` / `mouse_x` / `mouse_y`; the scene loop's step 8
    calls `on_draw` then `_render_draw_queue`, which renders the IDE
    runtime's command schema (rectangle / circle / ellipse / line / text /
    scaled_text, room coords y-down → Kivy y-up) into an InstructionGroup
    on `canvas.after`.
  - ✅ **Left-mouse events now export.** `mouse_left_press`/`_button`/`_down`
    → `on_mouse_left_press`, `mouse_left_release` → `on_mouse_left_release`;
    the scene's `on_touch_down`/`on_touch_up` invert the Android container
    transform (or the desktop DPI window scale), set room-coordinate
    `mouse_x`/`mouse_y`, and dispatch to every instance with the handler
    (IDE-runtime semantics: no hit-test).
  - ✅ The Android virtual D-pad is now generated only when the project has
    keyboard events (`NEEDS_DPAD`), so touch-only games don't get a corner
    overlay that swallows taps.
- **Still open** (deferred, none block `match3_1`):
  - ~~Draw-queue types `background` / `health_bar` are not rendered~~
    **DONE 2026-07-15** (deferred-items plan tier 1): both now render —
    `background` resolves by name via a new `BACKGROUND_PATHS` map
    (backgrounds copy to `assets/images/` alongside sprites but get their
    own map, not merged into `SPRITE_PATHS`, so a same-named sprite and
    background can't collide) with tiling support; `health_bar` is two
    rectangles + a border. All four draw-queue types (`sprite`/`lives`/
    `background`/`health_bar`) are now implemented on Kivy. Regression:
    `tests/test_draw_queue_background_health_bar.py` (includes a headless
    stub-kivy run that actually renders both and checks the resulting
    Rectangle sizes, not just source-level checks).
  - ~~New finding, not fixed: structured `draw_rectangle`/`circle`/
    `ellipse`/`line`/`arrow`/`variable`/`health_bar`/`background`
    *actions* have no codegen case~~ **DONE 2026-07-16.** All 8 action
    types now have a `process_action` branch in
    `export/Kivy/code_generator.py`, each emitting a
    `self._draw_queue.append(dict(type=..., ...))` matching the runtime's
    `execute_draw_*_action` schemas exactly: rectangle/ellipse/circle/line
    are direct param translations; `draw_arrow` precomputes the two tip
    segments at run time via inlined `atan2`/`cos`/`sin` (mirroring
    `execute_draw_arrow_action`'s geometry, since the draw-queue renderer
    only knows how to draw pre-computed line segments, not "arrows");
    `draw_variable` routes its expression through the existing
    `_resolve_instance_names` global-name resolver (`score` →
    `get_score()`, etc.); `draw_health_bar` reads the app's live
    `get_game_app().health`; `draw_background` resolves through a new
    `background_paths` map threaded into `ActionCodeGenerator.__init__`
    and all 4 export call sites, emitting an honest `pass  # ... not
    found in export` comment for an unresolvable name instead of a silent
    no-op. **Surfaced a genuine desktop-runtime bug along the way:**
    `runtime/game_runner.py`'s `_DRAW_HANDLERS` dispatch table had no
    `'arrow'` entry at all, so `draw_arrow` silently drew nothing even on
    the pygame desktop runtime, not just on export — fixed by adding the
    entry plus a new `_draw_arrow` method (shaft + two tip line segments).
    HTML5 got the matching 8 `case` blocks in `engine.js`'s
    `executeAction` switch (reusing `parseNumParam` for numeric params and
    `gmExpressionValue` for `draw_variable`'s expression, matching the
    existing `draw_text`/`draw_score` cases' conventions) plus a new
    `'arrow'` case in `renderDrawCommands` (the draw-queue *renderer*, a
    separate switch from `executeAction`) to actually paint the segments
    on the canvas. Regression: `tests/test_draw_action_codegen.py` (25
    tests) — Kivy side calls `ActionCodeGenerator.process_action` directly
    and `compile()`-checks the emitted source (matching
    `test_kivy_more_actions_export.py`'s established pattern); HTML5 side
    is static regex/substring assertions against `engine.js` source
    (Node isn't a CI dep, matching `test_draw_queue_background_health_bar.py`'s
    pattern); the desktop `_draw_arrow` fix gets both a `_DRAW_HANDLERS`
    lookup test and a real-pixel render test.
  - Right/middle mouse events have no touch equivalent and stay unexported.
  - **`execute_code` env is thinner than the IDE's.** Code is inlined
    verbatim into the generated method (good), but the IDE's exec
    environment (`runtime/action_executor.py` `execute_execute_code_action`)
    also copies locals back onto the instance and binds `game`, `keyboard`,
    `other`; the export does none of that, so bare-name assignments don't
    persist across events and those names raise `NameError`.
  - A real on-device/buildozer end-to-end test still doesn't exist
    (`test_android_export_cleanup.py` mocks the build); the stub-kivy
    execution test above covers logic, not the actual Kivy/GL layer.

### HTML5 export — Python bridge follow-ups (execute_code/mouse LANDED)
- 2026-07-10, while validating "HTML export works" for the classroom: the
  JS engine gained a Pyodide-backed execute_code bridge (IDE exec
  semantics: persistent `self`, locals copy-back, keyboard shim),
  mouse/touch dispatch (IDE no-hit-test semantics, room coords),
  draw-queue canvas rendering, create-before-first-step ordering, the
  object-side-file merge in the exporter (embedded project.json copies go
  stale), and the maze movement actions (`test_alignment`,
  `start_moving_direction`). Verified in headless Chromium for maze_1 and
  match3_1 (`tests/test_html5_python_export.py` pins the codegen; the
  Playwright harness lives in the session notes).
- Still open:
  - Pyodide loads from the jsDelivr CDN — a Python-using game needs
    internet on first open. An "offline bundle" export option (ship
    pyodide files next to the .html) would fix locked-down school
    networks. Pure-action games are unaffected (no Pyodide load at all).
  - The Python env exposes `self`/`math`/`random`/`keyboard` but `game`
    is None — no score/lives bridge yet (match3 tracks its own score).
  - ~~Draw-queue `background`/`health_bar` commands... not implemented~~
    **DONE 2026-07-15** — `case 'background'` (reuses the `game.sprites`
    map backgrounds already share with sprites, per `encode_sprites`) and
    `case 'health_bar'` added to `engine.js`. All four draw-queue types
    now implemented on both HTML5 and Kivy.
  - ~~structured draw_* actions have no codegen on either target~~
    **DONE 2026-07-16** — see the matching Kivy entry above; `engine.js`'s
    `executeAction` switch gained the same 8 `case` blocks and
    `renderDrawCommands` gained an `'arrow'` case.
  - Right/middle mouse events are not implemented.

- **Kivy export — long-tail action coverage** —
  `export/Kivy/code_generator.py:681`. Most actions translate fine; unhandled
  ones fall through to a no-op `pass`. Each one needs to be ported as we hit
  it.

### Export feature-parity matrix (quantified 2026-07-10)
- `tests/test_export_feature_matrix.py` cross-references every action and
  event the bundled samples use against what each export target
  implements — the systematic check the code audits structurally couldn't
  do (audits review code that exists; they can't see integrations that
  don't). Current state, pinned in the test's KNOWN_*_GAPS registries:
  - **Runtime:** complete for all 9 samples (enforced — hard failure).
  - **maze_1 + match3_1:** fully covered on HTML5 AND Kivy (enforced —
    these are the verified classroom demonstrators; gaps may not be
    "registered" for them, only fixed).
  - **HTML5:** maze_2 and plateforme_1 were closed 2026-07-10
    (browser-verified; the pass also replaced the engine's structurally
    wrong branch-scan conditional logic with the runtime's GM80 flat
    skip-next semantics, fixed exit_event to abort the whole event, made
    nested then/else branches actually execute, accepted the legacy
    'object' instance key plateforme rooms use, and fired destroy
    events). plateforme_2 and plateforme_3 followed the same day
    (browser-verified): embedded base64 sounds + play_sound/
    stop_all_sounds, set_sprite, change_instance, sleep (non-blocking
    step suspension), game_start, and runtime-parity no_more_lives
    (fires once on the >0→<=0 crossing, on every listening instance).
    **The HTML5 matrix is CLOSED (2026-07-11):** every action and event
    used by every bundled sample is implemented and browser-verified —
    the final subsystem was sprite-strip animation (frame slicing,
    image_index/image_speed GM semantics, animation_end on wrap,
    frame-sized collision boxes, set_sprite subimage/speed honored),
    proven by maze_3's spawned explosion playing its 16 frames and
    destroying itself via its authored animation_end. 54 browser checks
    green across all 9 samples. Keep the registries empty — a new entry
    means a regression or a new sample outgrowing the engine; fix the
    engine instead. Note: some GMK-imported sample scripts (bare GML
    `vspeed`, `view_xview`) error identically in the IDE runtime —
    sample-data debt, not exporter gaps.
  - **Kivy: CLOSED 2026-07-11** — the parity batch (draw family via the
    draw queue, creation cluster, test_score, set_direction_speed,
    destroy_at_position/jump_to_random base helpers, animation_end on
    wrap, no_more_lives on the set_lives crossing) emptied the Kivy
    registries too. The pass also fixed two pre-existing exporter
    breakers the action survey couldn't see: orphaned else_action
    (GMK mis-import) generated a bare `else:` SyntaxError — the
    plateforme_4/5 Kivy exports never compiled; and maze_3's
    "obj trigger" (space in the name) generated invalid class/module
    identifiers — the maze_3 Kivy export never compiled.
    `tests/test_kivy_parity_batch.py` now compile-gates every module of
    every sample's Kivy export.
- **All four registries are EMPTY — the matrix is fully closed on both
  targets.** The test fails on any NEW gap (a future sample using a
  feature an exporter lacks — the match3_1 lesson) and on stale entries
  after a fix, so the registries can't rot in either direction. What the
  matrix does NOT cover: on-device behavior (a real APK install / a
  phone-browser session) and per-action semantic parity beyond what the
  behavioral tests pin.

---

## Done since the last review (don't re-add)

- **About dialog license info** — surfaced MIT (code) + CC BY 4.0 (docs) in
  the About PyGameMaker dialog with French translation.
- **macOS App-menu Preferences hijack** — explicit `setMenuRole` calls now
  pin Preferences to `PreferencesRole` and prevent `Configure Thymio Blocks...`
  from being auto-promoted to the App menu.
- **Blockly visual ↔ events sync** — automatic, no manual button needed. See
  `SyncCoordinator` in `editors/object_editor/object_editor_main.py`.

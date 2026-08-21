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

### ~~Asset Manager~~ (DONE 2026-08-09, all 4 tiers — see docs/ASSET_MANAGER_PLAN.md)
- Was: `Tools → Asset Manager...`.
- Scope: bulk operations on assets (rename, move, delete in batch), search and
  filter, usage tracking ("which rooms / objects use this sprite?"), and
  unused-asset cleanup.
- **"Move" scoped out**: the app's asset model has no folder hierarchy (each
  category is a flat list), so there's nothing a bulk move would relocate
  between — dropped rather than inventing a folder system to give it meaning.
  Batch rename deferred as its own separately-schedulable feature (a
  different UI shape than delete's uniform "remove all of these").
- Shipped: `utils/asset_usage.py` usage tracking, wired into the delete
  confirmation (Tier 1); `AssetTreeWidget.apply_asset_filter` name-substring
  filter box (Tier 2); `ExtendedSelection` multi-select + one combined
  confirmation for bulk delete (Tier 3); `UnusedAssetsDialog` / Tools → Find
  Unused Assets… (Tier 4). Every delete (single or bulk) is trash-backed
  (see item 10.5 in `docs/DEFERRED_ITEMS_PLAN.md`).

### ~~Clean Project~~ (DONE 2026-08-09, all 3 tiers — see docs/CLEAN_PROJECT_PLAN.md)
- Was: `Tools → Clean Project`.
- Scope: remove temporary files, delete unused assets, clean build artifacts,
  shrink project size. Investigation found rollback-snapshot cleanup already
  happens automatically (`ProjectManager._sweep_orphan_snapshots`, on every
  load) and the `__pycache__`/`.pyc` workaround this entry used to describe
  cleans *this dev repo*, not a saved game project (project code lives as
  strings inside `project.json`, never as importable `.py` files under a
  project directory — doesn't apply to a shipped project at all).
- Shipped: `utils/project_cleanup.py`'s `.tmp`-orphan sweep (Tools → Clean
  Project, permanent removal — never routed through the asset system in the
  first place); `find_orphaned_physical_files`, the inverse of Asset
  Manager's unused-*entry* detection (files on disk with no `project.json`
  entry); `OrphanedFilesDialog` / Tools → Find Orphaned Files…, trashed via
  its own separate `.trash_orphaned_files/` store (not the asset Trash —
  these files have no asset entry for `AssetManager.delete_asset`'s restore
  path to operate on safely).

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
- **2026-08-14 — the functional check, done.** Investigated each of the five
  items this entry named, per its own instruction:
  - **`execute_script` — already DONE, this entry was stale.** It's been
    registered in `events/action_types.py` (line ~1517) all along, with a
    real end-to-end path: the Asset Tree already treats `scripts` as a
    creatable asset type, `editors/script_editor.py`'s `ScriptEditor` edits
    a named script's code, and `execute_execute_script_action` runs it via
    a real `exec()` with `self`/`game`/`argument0-4`/`keyboard` bound —
    functional, and per this repo's session notes, already ported to Kivy
    export too (`execute_script` got the same exec()-based rewrite
    `execute_code` did, 2026-08-09). Nothing to do; corrected here so this
    entry stops claiming otherwise.
  - **`save_game`/`load_game` — DONE 2026-08-14, now registered.** Both
    handlers were already substantially real (real JSON save/restore of
    room/score/lives/health/global vars/instances, matched by
    `object_name` with a real fix for the N-same-object-instances collapse
    bug). One genuine dead path found and fixed: loading a save whose room
    differed from the current room set `instance._load_room_name`/
    `_load_instances`, attributes `runtime/game_runner.py` never read —
    confirmed by grep, so a cross-room load silently did nothing beyond a
    log line. Fixed by routing through the same deferred
    `instance.goto_room_target` flag every other room-changing action
    already uses (`GameRunner.update()`'s existing branch, which calls
    `change_room` synchronously); a new `_pending_load_instances` rides
    alongside it and is restored right after `change_room` returns. Now
    registered in `events/action_types.py` (category "Game", one
    `filename` string param, matching `open_webpage`/`set_room_caption`).
    Desktop-runtime-only for now (same as many already-registered
    actions) — no Kivy/HTML5 export codegen exists yet, and no bundled
    sample uses either action, so this doesn't regress the export
    feature-parity matrix; picking up export codegen is ordinary
    "long-tail action coverage" work, not a blocker for UI registration.
    `tests/test_save_load_game.py` (6 tests) drives a REAL `GameRunner`
    through actual frames (same discipline as
    `test_room_background_scroll_actions.py`'s maze_3 proof) — same-room
    restore, the previously-dead cross-room restore, a nonexistent-room
    save (must not crash), and score/lives/health/global-variable
    round-trip. Suite 2897 → 2903 passed, 0 failed.
  - **Particle system and timelines — confirmed still genuinely
    non-functional, correctly deferred, NOT touched.** Grepped
    `runtime/game_runner.py` for every relevant name
    (`_particle_system`/`particle_types`/`_timeline`/`active_timeline`/
    `timeline_position`, etc.): zero hits. The action handlers
    (`runtime/action_executor.py`, `runtime/action_handlers/
    particle_handlers.py`) build real-looking data structures
    (particle type defs, emitter configs, timeline position/speed) but
    nothing anywhere ever reads them back to spawn/age/draw a particle or
    advance a timeline step — pure write-only state. Exposing UI for
    either would be exactly the "click it, nothing visibly happens"
    dead end rc.11 (`77e9dbf`) removed; both need a real update+render
    pass built first (a genuinely large feature, not a quick fix) before
    this entry's "do NOT add UI yet" instruction can be lifted. Scheduled
    (explicit ask, 2026-08-14): `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 5,
    phased desktop-engine → UI → export-parity, budgeted 3+ sessions and
    deliberately last in that plan's queue.
  - **`show_video` — confirmed still genuinely incomplete, correctly
    deferred, NOT touched.** Its own docstring already says so: "Video
    playback requires additional libraries (moviepy/opencv). This
    implementation logs the request but actual playback may be limited."
    The real implementation just shells out to the OS's default video
    player (`os.startfile`/`open`/`xdg-open`) — opens an external
    application window, not in-game video playback with any pause/resume
    control. Not what a `show_video` action's UI would honestly promise.
    **Re-scoped 2026-08-14**: the shell-out itself is honest and working —
    the actual gap is that it has no `events/action_types.py` entry, so
    it's invisible in the UI despite being functional. Registering it (with
    a description that says plainly "opens in your system's video player,
    not in-engine playback") is a small, real fix, distinct from — and much
    smaller than — building real in-engine decoding. Scheduled:
    `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 2.4 (also folds in
    `splash_show_video`/`splash_show_webpage` as thin wrappers).
- **Room-background/scrolling actions (set_background*, set_room_speed,
  set_room_persistent) — DONE 2026-08-09.** All four registered in
  `events/action_types.py` (category "Room"), each actually finished
  first: `set_room_speed` was already fully functional (just unregistered);
  `set_background_color`'s `show_color` and `set_background`'s `foreground`
  were accepted-and-discarded params, now wired onto new `GameRoom`
  attributes (`show_background_color`, `background_foreground`) with real
  rendering support; `set_room_persistent` set a flag nothing ever read
  (`GameRoom.persistent`) — `GameRunner.change_room` reused
  `self.rooms[room_name]` forever, so every room was accidentally
  persistent regardless of the flag. Fixed with real GameMaker semantics:
  a room now rebuilds fresh from its authored layout on every revisit
  unless explicitly marked `persistent: true` (deliberately NOT applied to
  `restart_game`, which already unconditionally rebuilds every room — a
  full restart stays a hard reset). This surfaced a real regression in
  `maze_3`/`maze_4` (the only samples with real backtracking via
  `previous_room`/`next_room`): their `obj_diamond` collectibles would
  have respawned on backtrack. Fixed by marking every room in both
  samples `persistent: true`. See `docs/DEFERRED_ITEMS_PLAN.md`-style
  planning in the session notes for the full design tradeoffs (an
  `EnterPlanMode` session, including a Plan-agent validation pass that
  traced the actual `change_room` body and audited every sample for
  revisit paths). Coverage: `tests/test_room_background_scroll_actions.py`
  (15 tests, including an end-to-end proof driving a real `GameRunner`
  through the actual `maze_3` sample — collect a diamond, backtrack via
  `previous_room`, return via `next_room`, assert it's still gone).
  **Kivy/HTML5 export codegen for these 4 actions — DONE 2026-08-10**
  (was deliberately deferred, matching the `goto_room` `fade`-transition
  precedent, until picked back up in a follow-on session). Kivy: two
  commits — `set_room_speed`/`set_background_color`/`set_room_persistent`
  first (`Scene.room_speed` replaces the hardcoded 60.0 baseline
  `GameObject._process_movement` scales hspeed/vspeed by; `GameApp`
  gained a `_room_cache` so a persistent room's scene instance is reused
  across a revisit — Kivy previously always rebuilt every room, the
  opposite default from what desktop's fix established), then
  `set_background` on its own (a dedicated `_bg_image_group`
  `InstructionGroup`, independent of the room's baked background,
  supporting dynamic image swap/tiling/scroll/foreground). HTML5: one
  commit for all four (no per-project codegen step there at all — the
  whole project JSON is embedded as `gameData` and `engine.js`'s
  `executeAction` reads params generically at runtime, so the work is
  entirely inside `engine.js`; HTML5 had the OPPOSITE persistent-room bug
  from Kivy, reusing every room forever, fixed with the same
  visited+persistent reuse contract). Both targets' `restart_room` forces
  a fresh rebuild of the current room specifically (needed since its
  target IS the current room, which the normal cache-then-reuse flow
  would otherwise immediately re-cache); HTML5's `restart_game` needed no
  change (`window.location.reload()` already discards everything).
  `set_room_speed` means something different per target — desktop/Kivy
  scale real movement velocity (dt-scaled on Kivy, direct step-rate on
  desktop); HTML5's loop isn't dt-scaled at all, so it scales hspeed/
  vspeed's final per-tick delta by `roomSpeed/60` instead, a documented
  approximation rather than a full step-rate throttle. Coverage:
  `tests/test_kivy_room_actions.py` (26 tests, incl. a real headless
  execution of the generated `main.py`'s `GameApp` for the room-cache
  reuse logic) and `tests/test_html5_room_actions.py` (16 tests,
  structural + a real export round-trip — no Node.js in CI). Full suite
  2451 → 2493 passed, 0 failed across the three commits.
- ~~**Views/camera**~~ **DONE (2026-07-15, residual limitation closed
  2026-08-15).** Plan: `docs/VIEWS_SAMPLES_PLAN.md` (its own status line has
  said "done, Phase 1+2 complete" since 2026-07-15 — this entry's stale "IN
  PROGRESS" header was never updated to match). Done: HTML5 8-view camera
  (`552a9bc`, Chromium-verified); `enable_views`/`set_view` **registered** in
  `events/action_types.py` (category "Views"); 3-target parity test
  (`df0a3e9`); the `views_1` sample (`fc37aea`). State by target: **desktop ✅,
  HTML5 ✅ (multi-view: per-view clip+translate), Kivy/Android ✅ (multi-view:
  the room renders into an Fbo and each visible view blits its region into its
  screen port via tex_coords; the OS window is sized to the view, not the room,
  so the camera shows a true scrolling slice).** Non-views Kivy rooms keep the
  original child-widget path untouched. `tests/test_kivy_views.py` covers
  single- and multi-view. The `enable_views`/`set_view` actions are now emitted
  by the Kivy code generator too (via `scene.set_views_enabled`/`apply_set_view`),
  so runtime camera reconfiguration works. The former residual limitation (the
  Fbo render target was built only at room construction, so enabling views
  purely via a runtime action on a non-views room silently never rendered) is
  now fixed — `_ensure_views_fbo()` lazily builds it from `set_views_enabled`
  too; see `docs/REMAINING_WORK_2026-08-15.md` Section B and
  `tests/test_kivy_views_fbo_retrofit.py`. Both `views_1` (single scrolling
  camera) and `views_2` (split-screen multi-view) samples ship.
- Recipe for adding more: see the comments at the bottom of
  `events/action_types.py` and the survey script that lived briefly at
  `.scratch_find_missing_actions.py` (removed after the bulk pass).
- ~~A future cleanup might generalise `get_action_type` to fall back
  through `ActionExecutor.ACTION_ALIASES` so legacy/alternate action
  names resolve to a single ActionType without duplicate entries.~~
  Scheduled: `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 1.2.

### GMK importer hardening (post-1.0) — ✅ DONE 2026-07-16
- **Closed.** `treasure` and `maze_4` are back in the bundled set after a
  full user playtest: 15 findings, 12 real bugs fixed with regression tests
  (GM "Applies to" targeting never imported, sprite Transparent flag, GM
  Sleep mis-mapped to a conditional, question-chain conditional scoping,
  nokey-before-step event order, destroy_at_position bbox containment,
  execute_script editor UI, HUD relative draws, change_instance motion,
  collision-context targeting, room_order-vs-IDE-reorder), 2 faithful
  imports of the original game's own quirks, 1 self-inflicted regression
  reverted. maze_4 carries one documented `snap_to_grid` wall hand-patch;
  treasure none. See `docs/GMK_IMPORTER_HARDENING_PLAN.md` (registry all
  checked) and `docs/{treasure,maze_4}_testing_pass.md`. Historical notes
  below retained for context.
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
  placeholders, not UI-registered (no `events/action_types.py` entry for any
  of the four, so there's no dead-end UI path today, just an unbuilt
  feature). Real implementations, sequencing, and file/line references:
  `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 2.
- ~~**Execute file** / **Execute shell command**~~ (lines 84, 90) —
  **decision confirmed 2026-08-14: stay disabled.** Asked the user directly
  given the security stakes for this audience (children, per the
  `extension_compat_2_0` plan's own framing); explicit choice was to leave
  both as log-and-return placeholders rather than build a sandboxed opt-in
  model. Neither has an `events/action_types.py` entry, so there is no
  dead-end UI path — this is an internal placeholder only, not a "lying to
  users" case. Don't re-propose implementing these without a fresh explicit
  ask.

Other:

- ~~**Script execution action** — `runtime/action_handlers/control_handlers.py:239` —
  stub only. Decide on the script language (Python? a sandboxed mini-DSL?)
  before implementing.~~ **Investigated 2026-08-14: this is dead code, not
  an undecided feature.** `handle_script`/`handle_code` register under
  action names `"script"`/`"code"` — neither has an `events/action_types.py`
  entry and no sample/importer ever emits either name, so this stub is
  unreachable from any real project; the "decide on a script language"
  framing was stale, since the language question was already answered
  elsewhere. The actually-working, UI-registered, exported feature is the
  **separately-named** `execute_script`/`execute_code` (real `exec()`-based,
  `action_executor.py`), not this. Scheduled for removal:
  `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 1.1.
- **Thymio "play sound"** — `runtime/thymio_action_handlers.py` — placeholder
  that emits a single tone instead of playing the requested sound resource.
  Scheduled: `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 2.3.

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

### ~~`tools/action_ref_i18n.py` missing entries for 4 room actions~~ (DONE 2026-08-12)
Found 2026-08-11 while splitting the reference pages: `set_room_speed`,
`set_background_color`, `set_background`, `set_room_persistent` (added
2026-08-09) had no `action.display`/`action.desc`/`note:*` entries in any
of the 8 non-English tables in `tools/action_ref_i18n.py`, so
`tools/gen_action_reference.py` fell back to English for them on every
translated page. Fixed: added real translations for all 19 strings (4
display names + 4 descriptions + 11 parameter notes) across all 8
languages, reusing already-established app terminology (the real
"Background Color"/"Persistent" strings from `pygm2_<lang>.ts`) where it
existed. Regenerated; 0 untranslated strings reported now.

### ~~Migrate ja / pt / zh off the legacy translation set~~ (DONE 2026-08-09)
- Done: `pygm2_pt.ts`/`pygm2_ja.ts`/`pygm2_zh.ts` were built from scratch
  against the current string catalog (1369 real distinct messages / 61
  contexts each — pt sourced from `pygm2_de.ts`, then ja/zh sourced from
  the corrected `pygm2_pt.ts`, via the committed `scripts/
  gen_translation_ts.py` tool; see `docs/I18N_CLEANUP_2026-08-06.md`
  Section H and `docs/JA_ZH_I18N_PLAN.md`), fully translated, compiled to
  `.qm`, and confirmed reachable in `LanguageManager._discover_languages()`.
  The legacy `translations/pygamemaker_{ja,pt,zh}.ts` files (the ones this
  entry described as abandoned/stale) are all deleted. All three now match
  the six previously-maintained locales' coverage. Two real dead-
  translation bugs were found and fixed along the way (a wrong Qt
  translation *context* name, and `self.tr(f"...")` f-strings that could
  never match a literal `<source>` template) — see `CLAUDE.md`'s
  2026-08-08/09 session notes for detail.
- **Partially addressed 2026-08-10**: an offscreen-QApplication screenshot
  spike (`QWidget.grab()` under `QT_QPA_PLATFORM=offscreen`, no real
  display needed) rendered the Preferences dialog in every one of the 10
  shipped languages and found a real bug this way — see the "extension
  system UI" entry below. Still not a substitute for a full click-through:
  only the Preferences dialog has been screenshotted+visually reviewed,
  not the whole IDE (main window, every other dialog, in-canvas editors).
  Every *string* is still only programmatically verified to resolve via a
  live `QTranslator` (plus the in-app Tutorials curriculum's real-widget-
  driven headless test); nobody has looked at most of the app's actual
  pixels. Not tracked as a scheduled TODO item — pick up opportunistically
  by screenshotting more dialogs the same way, budget permitting.
- ~~**Found 2026-08-11: `pygm2_pt.ts`'s `WelcomeTab` context is missing 26
  of 48 messages**~~ **DONE 2026-08-15** — `docs/DEFERRED_GAPS_2026_PLAN.md`
  Tier 2.1 investigated this and found the "26 of 48" figure was a miscount
  (48 counted vanished/duplicate `<location>` entries too); the real gap
  was 1 missing `WelcomeTab` string (the `"📖  Sample guides"` button) plus
  a whole missing `SampleDocsDialog` context (3 messages) — present in
  pt, ja, **and** zh alike. Both fixed, with real (not copied) translations
  per language, verified via a live `QTranslator`.
  `tests/test_sample_docs_dialog_translations.py`.

## Extensions

### ~~2.0 extension system — compatibility guarantees~~ (DONE 2026-08-09)
- Goal: a project using extensions (Thymio robotics, a future 3D extension)
  must never crash or silently corrupt when opened by an editor that
  doesn't have those extensions installed — audience is children on mixed
  hardware running different app versions.
- Full plan: `docs/extension_compat_2_0/PLAN.md` (+ companion
  `compat_demo.py` / `project_2_0.json` in the same folder).
- Done: format-version guard (`core/project_format.py`, shipped v1.1.2,
  `tests/test_project_format_guard.py`); the confirmed
  `requires_extensions` resave-wipe bug fixed in
  `_prepare_project_data_for_save` (`tests/test_extension_manifest_preservation.py`);
  unrecognized-action tree items render amber with the owning extension
  named when known instead of looking like a normal action, and
  double-clicking one explains why instead of silently doing nothing
  (`events/plugin_loader.extension_for_action`,
  `tests/test_extension_action_ui.py`).
- **Settings UI for toggling an extension on/off — DONE 2026-08-09**
  (separate, later, `EnterPlanMode`-scoped session). New "Extensions" tab
  in `dialogs/preferences_dialog.py`'s `PreferencesDialog` (its existing
  5-tab pattern) calls `events/plugin_loader.set_extension_enabled()` —
  the backend needed zero changes, this was pure UI. Checkbox state is
  buffered and only persisted on Apply/OK (`_apply_extension_settings()`),
  matching every other tab's Cancel-doesn't-persist behavior; no new
  restart mechanism needed (the dialog's existing generic "requires
  restarting the IDE" footer already covers it) and none was built for
  the Kivy/HTML5 exporters either, since they already re-check `enabled`
  live at export time — only the in-IDE action registry needs the
  restart. `_warn_missing_extensions()`'s warning dialog got its "enable
  it" pointer restored now that something real exists to point at.
  `tests/test_preferences_extensions_tab.py` (8 tests).
- **The extension-system UI's translations — DONE 2026-08-10.** This
  whole feature (the Extensions tab above, the unrecognized-action amber
  tree items, the missing/not-installed extension warnings) shipped with
  zero i18n coverage — 15 `self.tr()` strings across 3 contexts, present
  in NONE of the 10 shipped languages. Found via an offscreen screenshot
  spike (see the i18n entry above); fixed for all 10 languages in one
  pass, terminology cross-checked against each language's translated
  `wiki/Extensions_<lang>.md`. `tests/test_extension_ui_translations.py`.
  Surfaced a separate finding, since fixed: de's shipped catalogs carried
  151 never-completed `type="unfinished"` entries (e.g. the Preferences
  dialog's own "General" tab label had never been translated to German) —
  a pre-existing gap in the "organically maintained" languages (as
  opposed to pt/ja/zh, verified 100% complete in the 2026-08-09 i18n arc).
  **DONE 2026-08-10** — scoped and closed across all seven affected
  languages (de/es/fr/it/ru/sl/uk), 1101 entries total, es alone
  contributing 309 (largest, mostly independent gap). One real bug
  found along the way: 4 of de's own translations landed double-escaped
  (passed `lrelease` silently, resolved to literal `&lt;h3&gt;` text at
  runtime), fixed separately. Full writeup, per-language notes, and the
  regression-test registry: `docs/I18N_UNFINISHED_2026-08-10.md`.

### Block World renderer — occlusion culling for the first-person view (DONE 2026-08-21, partial)
- Investigated after a report that movement in the bundled block_world
  samples "feels quite slow." Measured, not assumed: `block_world_1` ran at
  ~8.0 fps and `block_world_2` at ~4.35 fps against their project-configured
  30fps room speed (headless, real `GameRunner.run()` timing) — movement
  itself (`move_and_collide`) is correct; the renderer
  (`extensions/block_world/renderer.py`) can't keep up, so held-key movement
  only advances once per actual rendered frame — far less often than the
  sample authors intended (~3x slower than the designed speed on
  `block_world_1`).
- Root cause (profiled): `render_block_world_view`'s per-column DDA march
  draws a `_draw_wall_strip`/`_draw_horizontal_face_textured` pygame Surface
  op for every occupied cell the ray crosses, including cells entirely
  hidden behind nearer opaque geometry — painter's-algorithm overdraw with
  no occlusion culling at all.
- Fix: `_stack_opaque_spans`/`_merge_covered`/`_is_covered` track cumulative
  screen-row coverage from nearer, already-collected opaque blocks as the
  march proceeds near-to-far; a farther cell whose whole projected span is
  already covered is dropped before it costs a single draw call. Proven
  PIXEL-IDENTICAL against the pre-fix renderer across 72 (seed, camera
  angle) combinations spanning open floor, walls, and gaps (three rounds,
  across two design revisions) — this only removes provably-invisible
  draws, never changes what's on screen. `tests/test_block_world_layers.py`
  `TestCumulativeCoverage` + `TestOcclusionCullingSkipsHiddenCells`.
- **Real, measured trade-off, not a clean win — known and accepted, not a
  bug in the implementation.** `block_world_1` (maze-like, lots of walls)
  improved ~+20% (~8.0 → ~9.6 fps); `block_world_2` (procedurally-generated
  open terrain) got ~-12% WORSE (~4.35 → ~3.85 fps). Walled/maze-style
  worlds get long sightlines that terminate against solid geometry, where
  the coverage bookkeeping pays for itself many times over; open rolling
  terrain rarely has anything that fully occludes, so every column pays the
  bookkeeping cost without triggering enough skips to offset it. Two design
  revisions were tried (whole-stack-only spans, cheaper but weaker; a
  no-genexpr per-block variant) — the trade-off held in both, so it's
  structural to the approach, not an implementation bug to fix further.
  Shipped anyway (explicit user decision, 2026-08-21) since walled/
  structured worlds are the more common authored style for this feature,
  and neither sample is anywhere near its 30fps target regardless.
- **Still open — neither sample reaches its target fps.** The deeper
  bottleneck is per-draw-call Surface-allocation overhead itself
  (`pygame.transform.scale`/`subsurface`/`blit`, ~10,700 calls/frame on
  `block_world_1` even after this fix) — occlusion culling only avoids
  calls that were entirely wasted; it doesn't make a genuinely-visible draw
  any cheaper. A real fix needs either batching per-column draws into fewer
  Surface operations, a lower default `columns`/`render_distance` (a
  visible quality/speed tradeoff, not free), or a different rendering
  approach entirely (e.g. numpy-vectorized column compositing) — a larger,
  riskier effort than this session's scope.
- **Follow-up decision, same day: the block_world extension's further work
  is set aside** (not deleted — `extensions/block_world/`, both samples,
  and all their tests remain and stay green) in favor of a cheaper vertical
  shooter, `samples/sky_strike_1` (see its own README for the design and a
  real spawn-off-screen `outside_room` bug this session's authoring hit).
  `block_world_1`/`block_world_2` were removed from the Welcome tab's
  `SAMPLE_PROJECTS` list (`widgets/welcome_tab.py`); the beginner edition's
  sample whitelist (`config/editions.py`) was unaffected, since both
  already sat outside it via the `_advanced_prefixes` filter
  (`tests/test_edition_sample_filter.py`) — `sky_strike_1` was added to
  that whitelist instead, being simple enough for a beginner. Re-add the
  two Welcome tab tuples to bring block_world back into view if work on it
  resumes later.

## Project format / persistence

### ~~Manifest-ify objects & sprites in project.json~~ (DONE 2026-08-14 objects, DONE 2026-08-15 sprites)
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
- **2026-08-14 investigation (audit-is-a-lead correction — re-verified before
  touching anything, per this doc's own discipline; blast radius is bigger
  than this entry originally described, so scope changed rather than the risk
  being absorbed silently):**
  - **Sprites carry no real "heavy" payload worth stripping.** Sprite pixel
    data lives in a sibling `.png`, never in the JSON; `sprites/<name>.json`
    is already small (~350-450 bytes in `samples/maze_1`, all scalar
    metadata — width/height/origin/frame count/animation params). Manifest-
    ifying sprites would require adding sprite-file loading (currently
    **absent entirely**) to `export/base_exporter.py` (exe/macos/linux),
    `export/android/android_exporter.py`, and `export/ios/ios_exporter.py` —
    real new code in three untestable-here export paths, for near-zero size
    benefit. **Scope narrowed: sprites are staying dual-stored.** The
    actual size/diff/conflict pain the top of this entry describes is
    entirely an **objects** problem (event/action trees, not sprite
    metadata) — `obj_person` in `samples/maze_1` is 1474 bytes serialized
    (2 events) vs. its sprite's 404.
    **Reopened 2026-08-14 (explicit ask):** scheduled as
    `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 6, following the objects
    precedent (this section) exactly, sequenced after the plan's Block World
    texture tier since both touch the same three export-loader files.
  - **Objects: stripping only `events` (not the full body) is the safe cut.**
    Every one of the six known loaders (`core/project_manager.py`,
    `runtime/game_runner.py`, `export/base_exporter.py`,
    `export/HTML5/html5_exporter.py`, `export/android/android_exporter.py`'s
    own hand-rolled merge, `export/ios/ios_exporter.py`'s own hand-rolled
    merge) already correctly restores `events` from `objects/<name>.json` —
    confirmed by reading each one, not assumed. The other object fields
    (`sprite`/`visible`/`solid`/`persistent`/`depth`/`parent`/`mask`/dates)
    can stay embedded as lightweight browsable metadata, mirroring how
    rooms keep `width`/`height`/`background_color` embedded and only
    `instances` moves out.
  - **But two MORE independent readers exist that bypass all six loaders
    entirely, load `project.json` straight off disk, and read `events`
    with no merge step at all — found by grep, not in the six-loader
    survey above, which is exactly why this needed a full sweep before
    coding:**
    1. `export/Aseba/aseba_exporter.py` — `AsebaExporter.export()` is
       handed a raw `project.json` **path** by
       `core/ide_window.py:export_aseba_code` (not the live merged
       `current_project_data`) and never reads `objects/*.json` at all.
       Stripping `events` would silently export **empty** Thymio/Aseba
       robot programs.
    2. `utils/resource_packager.py`'s `ResourcePackager.export_object`
       (Tools → Export Object / single-asset sharing, `.gmobj` packages)
       also reads `project.json` straight off disk with no object-file
       merge — `export_room` right next to it already DOES merge
       `rooms/<name>.json` (proof this exact class of bug is real and
       already had to be fixed once, for rooms, in this same file).
       Stripping `events` would ship `.gmobj` packages with no events —
       silently broken object sharing.
  - **The 7 fallback call sites — all individually cleared (2026-08-14),
    2 were real bugs, fixed:**
    - `widgets/asset_tree/asset_tree_item.py` — only reads a sprite's
      `file_path` (sprites untouched). Safe as-is.
    - `widgets/asset_tree/asset_tree_widget.py` — its `objects` category
      only routes to the already-fixed `ResourcePackager.export_object`/
      `import_object`; its own direct read (`get_room_list`) only touches
      room names. Safe as-is.
    - `editors/base_editor.py` (`load_project_data()`) — its one real
      caller (`object_editor_main.py`, next) only reads `sprites`/
      `settings`. Safe as-is.
    - `editors/object_editor/object_editor_main.py` — `load_project_assets`
      reads only the sprite list + Blockly preset for the sprite combo and
      "Parent" object dropdown (`object_data.keys()`/`.sprite` only, never
      `.events`). Safe as-is.
    - `editors/room_editor/__init__.py` (`load_available_objects`) — the
      object palette only reads `object_data.get('sprite')` for icons.
      Safe as-is.
    - `editors/object_editor/blockly_widget.py` — both hits only touch
      `settings.blockly_preset`, never `assets.objects`. Safe as-is.
    - `editors/playground_editor/__init__.py` (`_refresh_linkable_objects`)
      — **real bug, fixed.** Detected Thymio objects via
      `event_name.startswith('thymio_')` reading straight off the
      unmerged disk copy; an object identifiable as Thymio only by its
      events (no `thymio`-prefixed name, no explicit `is_thymio` flag)
      would have silently vanished from the "linkable objects" list. Now
      reuses `run_playground`'s own `_load_external_objects` merge helper
      (right below it in the same file, which already did this correctly)
      instead of a second, incomplete copy of the same logic.
      `tests/test_playground_linkable_objects_merge.py` (2 tests,
      confirmed to fail without the fix).
  - **A third real bug found beyond the original 9-site list, also fixed:**
    `widgets/asset_tree/asset_operations.py`'s `remove_asset_from_project`
    legacy fallback (no `project_manager` attached to the tree) read
    `assets[asset_category][asset_name]` straight off disk and handed it
    to `trash_asset` — whose own docstring requires "the FULL project.json
    entry... recorded verbatim so restore_asset can hand it straight
    back." **This exact bug already existed for rooms today**, independent
    of this change (rooms have been manifest-ified all along) — extending
    the same treatment to objects just made it apply there too. Fixed by
    merging the `<type>/<name>.json` side file into the snapshot before
    trashing, for both rooms and objects.
    `tests/test_audit_asset_operations_sidefiles.py::
    test_legacy_fallback_delete_merges_side_file_before_trashing`
    (confirmed to fail without the fix — a genuine pre-existing gap, not
    speculative).
  - **Implemented.** `core/project_manager.py`'s `_prepare_project_data_for_save`
    now takes the target `save_path` and, when `<save_path>/objects/`
    exists (mirroring `_save_objects_to_files`'s own gate — by this point
    it has already written every object's full body there this save), sets
    `events: {}` + `_external_file` on each object's project.json entry.
    A project with no `objects/` dir (legacy/embedded-only) is left fully
    embedded, unchanged. Sprites are untouched (see above).
  - **Round-trip test, done** (mandatory per the note below):
    `tests/test_manifest_ify_objects_round_trip.py` (7 tests) — a fresh
    project (save strips `events` to the side file; full load→save→reload
    cycle proves `current_project_data` gets every field back, not just
    `events`; a second save/load cycle is stable/idempotent), a legacy
    embedded-only project (no `objects/` dir — save leaves `events` fully
    embedded, byte-for-byte unchanged from before this feature existed),
    a `.zip` export/import round-trip, and a real bundled sample
    (`samples/maze_1`, copied to a temp dir first — `_save_to_folder`
    itself refuses to write into `samples/`) proving every real object's
    actual events survive a save→reload cycle, not just a synthetic
    fixture's. Full suite 2903 → 2913 passed, 0 failed across this
    session's commits.
- Round-trip test is mandatory: load a representative project → save → reload,
  and assert the in-memory `current_project_data` is byte-for-byte equivalent
  (no events/sprite-frames/params lost), for both a fresh project and a legacy
  embedded-only one. Prove it against pre-refactor HEAD per the audit
  methodology. Also verify `.zip` export/import still round-trips.
- Why it matters long-term: smaller `project.json`, clean per-asset git diffs,
  and far less Dropbox "conflicted copy" / merge risk across the multi-machine
  workflow.
- **2026-08-15 — sprites done too** (`docs/DEFERRED_GAPS_2026_PLAN.md` Tier 6).
  The 2026-08-14 "scope narrowed: sprites are staying dual-stored" call above
  was **reopened by explicit ask**, not overturned on the merits — the actual
  implementation strips the *whole* sprite body (not just one field, since
  sprites have no single risky subfield the way objects have `events`) to a
  `{name, asset_type, _external_file}` stub in `_prepare_project_data_for_save`,
  gated on `sprites/` existing (same pattern as objects). A fresh survey (not
  the stale 2026-08-14 one, which never got past "would need new code, scope
  narrowed") found **6 real gaps**, all fixed with regression tests:
  1. `export/HTML5/html5_exporter.py` had **zero** sprite-file merge at all —
     new `_load_sprite_files` (mirrors `_load_object_files`), called before
     both `encode_sprites` and the `gameData` embed (engine.js reads sprite
     metadata straight from that embed at browser runtime, not just at
     export-encode time — this was the biggest of the six).
  2. `export/base_exporter.py`'s `BaseKivyExporter._load_project` (covers
     exe/linux/macos **and** Android via inheritance — Android overrides the
     room/object loaders but not this one) and `export/ios/ios_exporter.py`'s
     own hand-rolled loader both had zero sprite merge; both got one, using
     `utils/project_file_merge.merge_sprite_file`.
  3. `editors/room_editor/__init__.py::load_available_objects`'s disk fallback
     (detached/floated room editor with no reachable `current_project_data`)
     fed the object palette an unmerged stub — new `_merge_sprite_files_into`
     helper.
  4. `widgets/asset_tree/asset_tree_item.py::load_object_sprite_thumbnail`'s
     own separate disk-fallback (distinct from the sprite-category thumbnail
     path, which was already safe) — merged inline.
  5. `utils/resource_packager.py`'s `export_object`/`export_room` had zero
     sprite merge (object *events* were already merged here from the 2026-08-14
     work; sprites got no equivalent) — a shared `.gmobj`/`.gmroom` package
     would ship (and an importing project would permanently receive) a bare
     stub with no `file_path`/dimensions/frames/origin. New
     `_merge_sprite_files` static helper, called in both export functions.
  6. The trash/rollback gate: `core/asset_manager.py::delete_asset` (preferred
     path) and `widgets/asset_tree/asset_operations.py::remove_asset_from_project`
     (legacy fallback) only recorded a `<type>/<name>.json` side file for
     `("rooms", "objects", "playgrounds")` — `"sprites"` was missing from both,
     so deleting a sprite left `sprites/<name>.json` orphaned on disk instead
     of moving it to `.trash/` (same hazard class as the already-fixed M59).
  Also added `thumbnail`/`image_file` to `utils/project_file_merge.py`'s
  `_SPRITE_FILE_KEYS` whitelist — both appear in real sprite dicts
  (`thumbnail` is read by `core/asset_manager.py`/`utils/asset_trash.py`) but
  were missing from the merge, which would have silently dropped them on the
  very first stub round-trip. Round-trip tests:
  `tests/test_manifest_ify_sprites_round_trip.py` (10 tests, mirrors the
  objects suite exactly — fresh/legacy/zip/real-sample) and
  `tests/test_manifest_ify_sprites_export_paths.py` (10 tests, one per fixed
  gap above). Full suite 3036 passed, 0 failed, 7 skipped (env-dependent).

## Export

### ~~iOS exporter has no app icon~~ (DONE 2026-08-14)
- Done: `iOSExporter.export_settings['icon_path']` (same key `exe_exporter.py`/
  `macos_exporter.py` already use) is resized into every AppIcon.appiconset
  slot via Pillow (`_generate_appiconset_from_image`, flattened onto opaque
  white first — Apple rejects an alpha-carrying app icon), or, with no
  `icon_path` set, `resources/ios/AppIcon.appiconset/` is copied in wholesale
  as PyGameMaker's own default (`_populate_appiconset`) so an export is never
  icon-less. `_install_app_icon` (new Step 7b, after the Xcode project is
  created, before `xcodebuild` archives) locates the appiconset kivy-ios's
  template already ships via `rglob` — robust to the exact folder name/depth
  rather than hardcoding `Assets.xcassets` — falling back to the conventional
  `<app>/Images.xcassets/AppIcon.appiconset` location if the template ships
  none. Deliberately never fails the whole export: a bad/missing `icon_path`
  or an unexpected project layout logs a warning and falls back, since an
  icon-less build (the pre-existing behaviour) is still a successful one.
- No macOS/Xcode/kivy-ios available to run the real IPA build end-to-end
  (matches this module's pre-existing zero test coverage) — verified instead
  with pure filesystem + Pillow tests that don't need either: exact pixel
  dimensions per manifest slot, RGB (no alpha) output, white-flattened
  transparency, graceful fallback on a missing/corrupt source image, and
  `_find_appiconset_dir`/`_install_app_icon` against hand-built fake project
  trees. `tests/test_ios_exporter_icon.py` (11 tests). Suite 2872 → 2883
  passed, 0 failed.

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
  - ~~Right/middle mouse events have no touch equivalent and stay
    unexported~~ **DONE 2026-08-14.** `on_touch_down`/`on_touch_up` now key
    off `touch.button` ('left'/'right'/'middle', set by Kivy's mouse
    motion provider for real mouse input; absent — defaults to 'left' —
    for a genuine touchscreen tap, unchanged Android behavior), dispatching
    to the matching `on_mouse_{button}_press`/`_release` method. New flat
    event keys (`mouse_right_press`/`_button`/`_down`/`_release`, same for
    `middle`) added to `_get_event_method_name`'s map, mirroring
    `_FLAT_MOUSE_KEY_ALIASES`. Verified with a real headless click-dispatch
    run (not just source assertions) via a small synthetic project with an
    object recording which button fired it.
    `tests/test_kivy_html5_right_middle_mouse_export.py`.
  - **`execute_code` env parity — DONE 2026-08-09** (commits `c977f1c`,
    later same day). `game` is bound (a `_ScriptGameProxy` exposing
    score/lives/health as plain read/write values, reusing
    `execute_script`'s existing `_script_game()` helper), errors are
    caught and logged instead of propagating uncaught, `other` is bound
    to the real collision-handler parameter (`None` outside a collision
    event), and — the piece that needed its own design pass — bare
    locals now get copied back onto the instance after the block runs.
    Kivy's codegen switched from inlining the code as literal Python to
    embedding it as a string and running it through a real `exec()` call
    at runtime (Kivy runs on real CPython, so this is available), the
    exact mechanism desktop/HTML5 already use — chosen over an
    export-time AST rewrite of bare assignments, which would need to
    correctly replicate every binding form CPython's real `exec()`
    covers (for-loop targets, `with...as`, tuple unpacking, augmented
    assignment) to get full parity. See `docs/DEFERRED_ITEMS_PLAN.md`
    item 9.
  - **Both adjacent follow-up gaps also DONE, same day.** `keyboard` is
    now bound in Kivy's `execute_code`/`execute_script` namespaces via a
    new `GameObject._check_key(key)` method (`kivy_exporter.py`'s
    `_generate_base_object`): resolves a key name to a Kivy keycode
    (arrows/space/enter/escape/backspace/tab by name, single letters/
    digits via `ord()`) and checks it against `self.scene.keys_pressed`
    (keyed by raw keycode int — different from desktop's per-instance
    set of lowercase name strings, so this is a real adapter, not a
    ported copy). The name→keycode table is single-sourced from
    `code_generator.py`'s `_KIVY_KEY_NAME_TO_CODE` (also now what
    `if_key_pressed`'s condition codegen uses, replacing its own inline
    copy) and embedded into the generated file via a `.format()` value
    substitution, not hand-duplicated. `execute_script` got the identical
    exec()-based rewrite `execute_code` did, plus the `other`/`keyboard`
    bindings it was missing entirely. A real bug surfaced and was fixed
    along the way: the new template comment explaining the `.format()`
    substitution originally *wrote the placeholder name in brace form*,
    and `.format()` replaced that occurrence too, garbling the emitted
    comment — caught by reading the actual generated output, not by any
    test (now documented as a landmine in the comment itself). Coverage:
    `tests/test_kivy_execute_script_export.py` (new, 12 tests, mirrors
    `test_kivy_execute_code_export.py`'s real-execution pattern) plus
    additions to `test_kivy_execute_code_export.py` and
    `test_kivy_execute_code_game_proxy.py` (the latter execs the REAL
    generated `_check_key`/`_KIVY_KEY_NAME_TO_CODE` from an actual
    export, not a re-implemented stub). Full suite 2411 → 2425 passed,
    0 failed.
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
  - ~~Pyodide loads from the jsDelivr CDN — a Python-using game needs
    internet on first open~~ **DONE 2026-08-14, embedded rather than
    "shipped next to the .html"** — the user's explicit requirement was
    that HTML5 export stay a single self-contained file (no sibling
    files), so this embeds Pyodide's core files as base64 directly in the
    .html instead of the originally-sketched "ship files alongside it"
    approach.
    - **Bonus fix found along the way: `pako.min.js` (gzip decompression
      for game_data/sprites_data/sounds_data — needed by EVERY export,
      Python or not) was ALSO CDN-loaded** (`cdnjs.cloudflare.com`),
      meaning even a pure-action game wasn't actually the fully
      self-contained/offline-capable file this doc's own "Pure-action
      games are unaffected" line assumed. Fixed unconditionally (not
      gated behind any option): `resources/vendor/pako.min.js` (MIT+Zlib,
      ~47 KB, license comment preserved) is now vendored and always
      embedded inline (`game_template.html`'s `<script src=...>` →
      `<script>{pako_code}</script>`). Every HTML5 export is now
      genuinely offline-capable by default; Pyodide is the only opt-in
      part, since it's the only piece with a real size cost (~17 MB).
    - **Design, verified against Pyodide's actual source (not
      guessed)**: `loadPyodide()` already supports everything needed
      without protocol-level hacks — `stdLibURL`/`lockFileURL` accept
      `data:` URIs directly (fetch() supports `data:` natively); if
      `_createPyodideModule` already exists globally, `loadPyodide()`
      skips its own `pyodide.asm.js` fetch entirely (its own source
      comment: "If the pyodide.asm.js script has been imported, we can
      skip the dynamic import") — so embedding `pyodide.js`/
      `pyodide.asm.js` as inline `<script>` tags removes those two
      network requests outright. Only `pyodide.asm.wasm` has no direct
      option (computed internally as `indexURL + 'pyodide.asm.wasm'`,
      fetched via plain `fetch()` in browser mode — confirmed by reading
      `compat.ts`'s `browser_getBinaryResponse`, not XHR as a stray
      grep first suggested) — `engine.js`'s `PythonBridge._initEmbedded`
      temporarily overrides `window.fetch` to serve the embedded bytes
      for that one request, restored in a `finally` regardless of
      success/failure.
    - `export/HTML5/pyodide_bundle.py`: downloads (once) and caches
      Pyodide's 5 core files (`pyodide.js`/`pyodide.asm.js`/
      `pyodide.asm.wasm`/`pyodide-lock.json`/`python_stdlib.zip` — NOT
      the full distribution with numpy/pandas/etc.; `PY_BOOTSTRAP` only
      ever imports stdlib json/math/random) under
      `~/.pygamemaker/pyodide_cache/<version>/`, not vendored into git
      (unlike pako's ~47 KB, these are multi-MB third-party binaries).
    - `HTML5Exporter`: new `export_settings={'offline_pyodide': True}` +
      `progress_callback` params (both optional, default off — every
      existing `.export(path, path)` call keeps working unchanged).
      `project_needs_python()` (a Python port of `engine.js`'s
      `PythonBridge.projectNeedsPython`, kept in exact sync) gates
      whether the ~17 MB is worth embedding at all — a pure-action game
      gets the unchanged default output even with the option checked.
      Text files (`pyodide.js`/`pyodide.asm.js`) are gzip-then-base64
      (compress well, matching the existing game_data/sprites_data
      pattern); the three already-compressed binary formats
      (`pyodide.asm.wasm`/`pyodide-lock.json`/`python_stdlib.zip`) are
      plain base64 — the latter two double as the literal payload of a
      `data:...;base64,<this>` URI, so gzipping them would need an
      extra JS-side inflate-then-re-base64 step (chunked, to dodge
      `String.fromCharCode(...)` spread limits on multi-MB arrays) for
      near-zero benefit on data that barely compresses further anyway.
      `last_error_message` (new): `export()`'s outer try/except is
      intentionally broad (catches anything, logs, returns `False`) —
      this preserves pyodide_bundle's specific, actionable failure
      message (e.g. "no internet — uncheck the option or check your
      connection") for the UI instead of it being lost to the console.
    - UI: `core/ide_exporters.py`'s `_ask_offline_pyodide()` — a
      Yes/No prompt shown ONLY when `project_needs_python()` is true (a
      pure-action game isn't asked at all), defaulting to No (so
      Enter/Esc never silently commits +17 MB the user didn't choose).
    - **Verified as thoroughly as possible without a real browser**
      (matches this codebase's established "no Node.js in CI" ceiling —
      except this session, uniquely, had a portable Node available, so
      the bar was raised): `tests/test_html5_offline_pyodide_js_execution.py`
      REALLY EXECUTES the extracted `PythonBridge` class under Node
      (skips cleanly if `node` isn't on PATH — never a hard CI
      dependency) against small fake "pyodide" fixtures, proving script
      injection genuinely runs, the wasm fetch-intercept serves the
      exact embedded bytes, `window.fetch` is restored byte-identical
      afterward (a real bug — `.bind(window)` produced a
      non-identical-but-functionally-equivalent wrapper — caught and
      fixed by this exact test before it ever shipped), the `data:` URIs
      are byte-exact, and the CDN-vs-embedded branch selection is
      correct. A one-off manual check (not committed — same category as
      the ad hoc Playwright verification other sessions have done) then
      round-tripped the REAL downloaded ~13.6 MB Pyodide v0.26.4 files
      through the exact same encode path this exporter uses and
      confirmed byte-for-byte fidelity + valid JS syntax post-decompress
      for all three non-trivial files. **What remains genuinely
      unverified: an actual browser calling the real `loadPyodide()`
      against this embedded bundle end-to-end.** Node.js has its own
      `IN_NODE` environment-detection branch inside pyodide.js itself
      that takes a materially different (fs/require-based) code path
      than a real browser's `fetch()`-based one — confirmed by hitting
      it directly (a `ReferenceError: require is not defined` when the
      real `loadPyodide()` was actually called under Node), which is
      exactly why this doc doesn't claim Node execution as proof of the
      browser path and stops at the boundary where only a real browser
      would tell the difference.
    - `tests/test_pyodide_bundle.py` (11 tests — download/cache logic,
      no real network), `tests/test_html5_offline_pyodide_export.py`
      (17 tests — `project_needs_python`, pako embedding, the full
      export→embed pipeline with mocked downloads, error propagation),
      `tests/test_ide_exporters_offline_pyodide_prompt.py` (5 tests —
      the UI gate). Suite 2953 passed / 7 skipped-without-Node, 0
      failed.
  - ~~The Python env exposes `self`/`math`/`random`/`keyboard` but `game`
    is None — no score/lives bridge~~ **DONE 2026-08-09.** `game` is now
    a fresh `_Game(score, lives, health)` snapshot built each
    `execute_code` call from values synced in from the live JS `game`
    object, diffed back out through the same JSON patch mechanism
    `self.x`/`self.y` already use — no shared crossing-detection refactor
    needed after all (a raw `game.lives = X` from `execute_code` is a
    plain write on every target, matching desktop's real semantics; only
    the `set_lives`/`set_health` ACTIONS trigger `no_more_lives`/
    `no_more_health`). `tests/test_html5_execute_code_game_binding.py`.
    See `docs/DEFERRED_ITEMS_PLAN.md` item 9.
  - **Follow-up limitation on the item above, found 2026-08-21, not yet
    fixed:** the per-call `_Game(score, lives, health)` snapshot means any
    custom attribute set on `game` from `execute_code` (e.g.
    `game.wave_count = 5`) is discarded the instant that call returns —
    it's a fresh object every call, never cached. Desktop diverges here:
    `execute_execute_code_action` binds `game` to the literal live
    `GameRunner` (`self.game_runner`), so a custom attribute set there
    persists for the rest of the game, visible to every later
    `execute_code` call from any instance — real, working desktop idiom
    for ad hoc shared game state. `game.score`/`lives`/`health` themselves
    are unaffected by this gap (they're the intentionally-whitelisted
    fields that already round-trip through the patch mechanism); only
    attributes outside that whitelist vanish silently, with no error or
    warning. Fix would be caching the `_Game` instance at module scope
    (like `_instances` already does for `self` via `_get_inst`) instead of
    reconstructing it fresh in `run_code`/`run_draw`, syncing score/lives/
    health into it before each call rather than replacing it outright.
    Not yet scoped for Kivy (untouched, not investigated this session).
  - ~~Draw-queue `background`/`health_bar` commands... not implemented~~
    **DONE 2026-07-15** — `case 'background'` (reuses the `game.sprites`
    map backgrounds already share with sprites, per `encode_sprites`) and
    `case 'health_bar'` added to `engine.js`. All four draw-queue types
    now implemented on both HTML5 and Kivy.
  - ~~structured draw_* actions have no codegen on either target~~
    **DONE 2026-07-16** — see the matching Kivy entry above; `engine.js`'s
    `executeAction` switch gained the same 8 `case` blocks and
    `renderDrawCommands` gained an `'arrow'` case.
  - ~~Right/middle mouse events are not implemented~~ **DONE 2026-08-14.**
    `setupMouse()`'s `mousedown`/`mouseup` listeners now branch on DOM
    `MouseEvent.button` (0/1/2 = left/middle/right) into three key-alias
    arrays (mirroring the existing left-button one), plus a `contextmenu`
    listener that calls `preventDefault()` so a right-click reaches the
    game instead of opening the browser's menu. Touch input (no `.button`
    concept) is unaffected — still always left, matching Kivy/Android's
    equivalent fallback. See the matching Kivy entry above; both share
    `tests/test_kivy_html5_right_middle_mouse_export.py`.

- **Kivy export — long-tail action coverage** —
  `export/Kivy/code_generator.py`'s `process_action`/`_convert_simple_action`.
  Most actions translate fine; unhandled ones fall through to a no-op
  `pass  # TODO: {action_type}` (with `_UNSUPPORTED_ACTIONS` tracking which).
  Re-surveyed 2026-08-14: ~18-20 of `ACTION_TYPES`'s 107 entries have no
  branch (`bounce`, `open_webpage`, `save_game`, `load_game`,
  `test_question`, `show_info`, `stop_sound`, `check_sound`, `check_room`,
  `fill_color`, `set_alpha`, `move_towards_point`, `draw_scaled_text`,
  `set_image_index`, `set_image_speed`, `set_room_caption`,
  `start_animation`, `stop_animation`, plus a couple more). Being worked in
  small clusters: `docs/DEFERRED_GAPS_2026_PLAN.md` Tier 3.

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

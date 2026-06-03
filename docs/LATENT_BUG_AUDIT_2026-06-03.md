# Latent Bug Audit — 2026-06-03

Multi-agent logic-level bug audit of pygm2 (11 subsystems reviewed → 34
candidate findings → **30 confirmed** by adversarial verification, 4 rejected).
Each finding was verified against the real code (many reproduced empirically);
several severities were corrected *down* during verification.

This file is the working registry so the cleanup can continue across machines.
**When you fix one, flip its checkbox and note the commit.**

- **Highs (7): all FIXED** in commit `67c91e4` (+ `tests/test_audit_regressions.py`,
  17 regression tests). Earlier related fix: `d60f41b` (create_action_dialog
  factory + missing import).
- **Remaining: 14 medium + 9 low** — open, listed below with suggested fixes.

Severity reflects the verifier's corrected rating (real impact), not the
reviewer's initial guess.

---

## ✅ Fixed — High (7) — commit `67c91e4`

- [x] **#1 crash — keypress kills the game on an orphan instance.**
  `runtime/game_runner.py:2318` (+ `_process_held_keys` ~2380).
  `handle_keyboard_press` was the only input handler missing
  `if not instance.object_data: continue`. An instance referencing a
  renamed/deleted object → `None.get()` → AttributeError → game loop dies.
  *Fix:* added the guard before key accumulation in both handlers.

- [x] **#2 save-load — `if_condition` always-false in non-English locales.**
  `events/conditional_editor.py:606`. The condition-type combo stored
  `currentText()` (the translated label, e.g. `nombre_instances`), which no
  runtime branch matches → `return False`. *Fix:* store canonical English as
  combo `userData` (condition_type + key/state/position/mouse sub-fields), read
  `currentData()` / select via `findData()`; `on_condition_type_changed` keys
  off the index.

- [x] **#3 wrong-behavior — Roberta export inverts "decrease variable".**
  `export/Roberta/roberta_exporter.py:421`. `thymio_decrease_variable` reused
  `_build_increase_variable` ("sign in value" never implemented). *Fix:* new
  `_build_decrease_variable` negates the (positive) amount.

- [x] **#4 data-loss — alarm events silently dropped.**
  `editors/object_editor/python_code_parser.py:945`. `generate_full_class`
  special-cased only `keyboard*` for the nested-container shape; `alarm` fell
  through to `def on_alarm(self): pass`. *Fix:* emit `on_alarm_N` per sub-event
  and re-nest under `alarm` on parse.

- [x] **#5 save-load — `keyboard_press`/`keyboard_release` round-trip wrong.**
  `editors/object_editor/python_code_parser.py:347`. `split('_', 1)` turned
  `keyboard_press_space` into base `keyboard` + key `press_space`; lost all
  `keyboard_release` actions. *Fix:* match bases longest-first
  (`keyboard_press`/`keyboard_release`/`keyboard`).

- [x] **#6 wrong-behavior — multi-file asset import imports only the first.**
  `dialogs/import_dialogs.py:131`. `get_selected_files()` returned
  `[self.selected_file]` (just `files[0]`). *Fix:* collect all into
  `self.selected_files`; `exec()`/`get_selected_files()` use the full list.

- [x] **#7 wrong-behavior — room package export collects zero dependencies.**
  `utils/resource_packager.py:411`. Read `instance['object_type']` but
  instances use `object_name`/`object`. *Fix:* read
  `instance.get('object_name') or instance.get('object')`.

---

## ⬜ Open — Medium (14)

- [ ] **#8 wrong-behavior — `if_condition` `key_pressed` always false.**
  `runtime/action_executor.py:4337`. Reads `getattr(game_runner, 'pressed_keys', set())`
  but the attribute is `keys_pressed` — and even that is only mutated on
  *instances* (`instance.keys_pressed`), never on `game_runner`.
  *Fix:* read `instance.keys_pressed` (keys are lowercase pygame names).

- [ ] **#9 wrong-behavior — `destroy_instance target='object'` no-op in collisions.**
  `runtime/action_executor.py:4622`. `handle_collision_action` inlines only
  `self`/`other`; `object` falls through and returns None.
  *Fix:* delegate any non-self/other target to `execute_action`
  (which reaches `execute_destroy_instance_action`).

- [ ] **#10 save-load — `load_game` restores all instances onto the first match.**
  `runtime/action_executor.py:2749`. `_restore_instances` matches by
  `object_name` + `break`, never consuming matched instances; rooms with N
  same-object instances lose per-instance state.
  *Fix:* track consumed instances (set of `id()`), ideally save/restore a
  stable per-instance id. (Note: cross-room load branch stashes
  `_load_instances`/`_load_room_name` that nothing reads — separate gap.)

- [ ] **#11 wrong-behavior — `repeat` dropped inside collision events.**
  `runtime/action_executor.py:4550`. `_execute_collision_action_list_inner`
  lacks the `repeat` flow-control branch the normal loop has (line ~233), so it
  becomes "Unknown action" and the block runs once.
  *Fix:* mirror `_handle_repeat_action` handling into the collision loop.

- [ ] **#12 off-by-one — pixel-perfect collision mask offset wrong.**
  `runtime/game_runner.py:3674` (and ~3726). `_precise_refine` gets bbox-in-world
  coords but masks are full-frame, so the overlap offset is off by
  `(bbox_left2-bbox_left1, bbox_top2-bbox_top1)` — false hits/misses for mixed
  precise sprites (self-cancels only for identical bbox offsets).
  *Fix:* pass frame-origin offset `((inst2.x-org2)-(inst1.x-org1))`, or crop
  masks to bbox.

- [ ] **#13 wrong-behavior — keyboard "button" presses don't set Thymio button state.**
  `runtime/playground_runner.py:275`. `_on_key_pressed` fires the events but
  never calls `sim.set_button(...)` (the mouse path does); state-polling code
  reads 0. `_on_key_released` is a no-op stub.
  *Fix:* map key→button and `set_button(True/False)` on press/release.

- [ ] **#14 state-not-restored — playground Reset leaves stale state.**
  `runtime/playground_runner.py:439`. `_reset` restores only pose/motors; LEDs,
  sound, sensors, timers, proximity counter, and instance variables persist.
  *Fix:* reconstruct each `ThymioSimulator` (like `_create_robots`) or
  explicitly reset led/sound/sensor/timer state and clear dynamic vars.

- [ ] **#15 data-loss — emptying a room then saving resurrects instances.**
  `core/project_manager.py:512`. `_save_rooms_to_files` treats an empty
  in-memory instances list + non-empty file as "data lost" and rewrites the old
  instances; can't tell "never loaded" from "user emptied it".
  *Fix:* track a per-room `instances_loaded` flag; only preserve when never
  loaded this session.

- [ ] **#16 data-loss — GMK import: `repeat` loses its count.**
  `importers/gmk_converter.py:566`. The `action_kind` dispatch (`5:"repeat"`)
  returns `parameters={}` before the ID-based path that knows
  `GM_ACTION_PARAMS[(1,324)]=["times"]`. Runtime default makes it run once.
  *Fix:* remove `5:"repeat"` from `_GMK_KIND_TO_ACTION` (let it fall through),
  or special-case kind 5 to copy `argument_values[0]` into `times`.
  (No bundled sample .gmk currently uses repeat.)

- [ ] **#17 wrong-behavior — GMK room instances use `object` key; rename misses them.**
  `importers/gmk_converter.py:737`. Writes `{"object": name}`; `asset_manager`
  rename only updates `object_name`. After a rename (without re-saving the room
  in the editor, which normalizes the key) the placement points at a missing
  object. *Fix:* emit canonical `object_name`, or make rename check both keys.

- [ ] **#18 wrong-behavior — Kivy export drops `if_object_exists`.**
  `export/Kivy/code_generator.py:650`. No `process_action` branch → falls to a
  bare expression statement; gated actions (e.g. `set_lives`, `restart_room`)
  run unconditionally. *Fix:* add an `if_object_exists` branch that opens an
  `if` block (honor `negate`/count), mirroring `if_condition`. (Also note a
  `negate` vs `not_flag` param-key mismatch vs runtime.)

- [ ] **#19 race — Blockly `_loading` guard cleared synchronously.**
  `editors/object_editor/blockly_widget.py:369`. `load_workspace_xml` sets
  `_loading=False` right after the async `runJavaScript`, so load-time change
  events aren't suppressed → spurious dirty state + sync round-trip.
  *Fix:* reset `_loading` inside the `runJavaScript` callback (like
  `load_events_data`'s `on_load_complete`).

- [ ] **#20 wrong-variable — room paste sets the wrong selection attr.**
  `editors/room_editor/room_canvas.py:473`. Sets `selected_instance` (singular,
  dead attr) instead of `selected_instances`; pasted items aren't selected and
  Delete hits the prior selection. *Fix:* set
  `self.selected_instances = list(pasted_instances)` (mirror
  `duplicate_selected_instances`).

- [ ] **#21 wrong-behavior — Thymio Blockly preset enables `"else"` not `"else_action"`.**
  `config/blockly_config.py:651`. `enable_block` doesn't validate, so the Else
  block never appears in the thymio preset toolbox.
  *Fix:* `enable_block("else_action")`.

---

## ⬜ Open — Low (9)

- [ ] **#22 — `if_object_exists` counts to-be-destroyed instances.**
  `runtime/action_executor.py:1476`. Missing `and not getattr(inst,'to_destroy',False)`
  that `test_instance_count` and the `instance_count` condition both have →
  one-frame lag on "level cleared" gating. *Fix:* add the filter.

- [ ] **#23 — circle-LED color double-scaled.**
  `runtime/thymio_renderer.py:295`. `_render_leds` pre-scales 0-32→0-255, then
  `_draw_led`'s "all ≤32" heuristic rescales again → non-monotonic brightness
  at low intensity. *Fix:* pass raw 0-32 and scale once, or drop the heuristic.

- [ ] **#24 — key auto-repeat re-fires Thymio button events.**
  `runtime/playground_runner.py:65`. `keyPressEvent` has no
  `event.isAutoRepeat()` check → held key fires the button event tens of
  times/sec. *Fix:* ignore auto-repeat in keyPress/keyRelease.

- [ ] **#25 — `reload_plugins` doesn't unregister prior plugin actions/events.**
  `events/plugin_loader.py:186`. Stale entries persist in global
  `ACTION_TYPES`/`EVENT_TYPES`; edited defs ignored (name-skip). **No callers
  today** (dead path). *Fix:* track per-plugin registered names and pop them,
  or rebuild from a pristine baseline.

- [ ] **#26 — missing-file flag undone by imported-migration.**
  `core/asset_manager.py:727`. `_validate_asset_paths` sets `imported=False`
  for a missing file; the next two lines flip it back to True → broken asset
  shown as present, `file_missing` is dead. *Fix:* gate with
  `and not asset_data.get('file_missing', False)`.

- [ ] **#27 — `DEFAULT_COLORS` mutable shared-reference.**
  `editors/playground_editor/__init__.py:258`. `list(DEFAULT_COLORS)` shares the
  element dicts; editing a color when a playground lacked a `colors` key mutates
  the module global process-wide. (Non-default trigger: external/legacy JSON.)
  *Fix:* `copy.deepcopy(DEFAULT_COLORS)` for the fallback and on store/return.

- [ ] **#28 — `cut_instance` reports count 0.**
  `editors/room_editor/__init__.py:716`. Reads `get_selected_count()` *after*
  the cut empties the selection → status shows "Cut 0 instance(s)". *Fix:*
  capture the count before `cut_selected_instances()`.

- [ ] **#29 — Preferences auto-save interval never applied.**
  `dialogs/preferences_dialog.py:377`. Persists `editor.auto_save_interval`
  (minutes) but the timer reads top-level `auto_save_interval` (seconds); never
  bridged. *Fix:* feed the editor value into `set_auto_save` (reconcile units),
  or remove the dead control.

- [ ] **#30 — `OpenProjectDialog.accept_project` refs nonexistent widgets.**
  `dialogs/project_dialogs.py:217`. Reads `project_name_edit`/`description_edit`
  never created in this class → AttributeError on OK. **Dead code** (IDE uses
  `QFileDialog`). *Fix:* rewrite to use `project_path_edit`, or delete the class.

---

## Rejected (4)

Four candidate findings were refuted by the verifier (could not reproduce /
guarded path) and are intentionally not listed. Re-run the audit if you want
the full candidate set.

## How this was produced

Background `Workflow` ("latent-bug-audit"): one reviewer per subsystem →
adversarial verifier per candidate (reads real code, defaults to refute). 45
agents, ~1.84M tokens. Re-running it will re-derive findings from current code —
useful after a batch of fixes to confirm closure and surface anything new.

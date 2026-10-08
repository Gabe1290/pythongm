# Blockly block audit — 2026-10-08

Question asked: *are all the Blockly blocks connected to real code, or are some
just placeholders?* Status: **review complete; U0 and B1 landed.** B2–B9 are
still open, plus two new findings (B10, B11) turned up while fixing B1. The
checkboxes below are the resume state; one unit ≈ one commit with its
regression test.

## How it was checked (re-runnable)

Nothing here comes from reading the JS alone — every claim was observed in the
**real** `editors/object_editor/blockly/blockly_workspace.html`, loaded in a
headless `QWebEngineView` with the auto-generated `custom_*` blocks registered
and the project asset lists pushed exactly as `BlocklyWidget` does.

1. **Every block type (321)**: created in the page; recorded what it saves to
   (`getEventType` / `generateActionCode` / `getInputValue`), whether that saved
   data loads back (`loadEventsData`), and whether save → load → save is stable.
2. **Every saved action name** checked against the runtime's `action_handlers`
   (after `load_all_plugins`, through `LEGACY_RELATIVE_ADD` / `ACTION_ALIASES`),
   and every handler body scanned for stubs.
3. **Every sample object (98 in `samples/*/objects/`)**: real events loaded into
   Blockly and saved straight back, diffed. Re-run with
   `QT_QPA_PLATFORM=offscreen python3 tools/audit_blockly_roundtrip.py`
   (2026-10-08 baseline: **644 differences**; target 0).

Why it matters: `ObjectEditor.on_blockly_events_modified`
(`editors/object_editor/object_editor_main.py`) **replaces the object's events
with Blockly's output** on the first edit in the Blockly tab, and Blockly is
rebuilt from the events whenever the object has no saved workspace XML (samples,
GMK imports, objects made in the action list) and after every edit in the
action-list tab. Every loss below therefore reaches the student's project the
moment they touch a block.

## What is fine

- **Runtime: no placeholders.** All 168 action handlers reached by blocks are
  real code. The flagged short ones are delegations (`set_hspeed` →
  `_set_speed_component`, the room tests → `_dispatch_room_test`).
- `start_block` / `end_block` / `else_action` / `repeat` have no handler by
  name on purpose — the action-list walker implements them.
- All plain parameters of the auto-generated `custom_*` blocks save correctly.
- All 12 game event blocks round-trip; alarms flat vs nested and key-name case
  (`SPACE`/`space`) are both accepted by the runtime (`game_runner.py` alarm
  lookup, `input_handler._find_key_in_event`).

## Findings, by root cause (highest impact first)

- [x] **B1 — Typing 0 gives the default instead, landed `2749147c`.**
  Two independent halves of the same `value || default` anti-pattern, both
  fixed: `getInputValue` (`blockly_generators.js`, SAVE: blocks -> events) now
  uses an `isNaN` check instead of `||`. `setBlockParameters`'s
  `connectNumberBlock`/`connectTextBlock` call sites (`blockly_workspace.html`,
  LOAD: events -> blocks, 42 + 4 sites) had the identical bug one layer
  earlier — found only because a real-page test using a native JSON *number*
  0 for `gravity` still failed after the generator-side fix alone (the 98
  bundled samples all store parameters as *strings*, where `"0"` is truthy
  and never triggered this half; a future numeric-JSON producer would).
  Both now route through a shared `paramOr(value, fallback)` helper that only
  falls back on `undefined`/`null`/`''`. The audit tool's own 98-sample
  baseline only moved on the already-known cases (644 → 633; the
  loader-side fix doesn't show up there since no sample hits it -- see
  above). Verified against the real page via
  `tests/test_blockly_zero_value_roundtrip.py` (6 tests, one shared
  QWebEngineView -- creating more than one per test process segfaults here).
  Surfaced two new, separate bugs while testing (now B10/B11 below) that are
  **not** fixed by this change.
- [ ] **B2 — Conditions lose their condition and nested actions (CRITICAL).**
  - `if_condition`: only the condition types the hand-written block models
    survive; `expression`, `key` and other `condition_type`s are dropped and
    the reload uses the generic `custom_if_condition`, so saving writes
    `parameters: {}` — condition **and then/else actions gone**. 55 nested
    actions lost across block_world_1, multiplayer_lan_1, reseau_1–4,
    sky_strike_1.
  - `test_variable`: reloads as `custom_test_variable`, `then_actions` /
    `else_actions` dropped.
  - `test_expression`, `if_next_room_exists`: nested actions dropped.
  - `if_collision_at`: the loader deliberately replaces it with its **first**
    nested action (`blockly_workspace.html`, "doesn't have a direct block
    equivalent") — condition gone, the action now runs unconditionally, other
    nested actions dropped; with no nested actions the block vanishes.
- [ ] **B3 — Events with no Blockly block are deleted (HIGH).** No block exists
  for `game_start`, `no_more_lives`, `no_more_health`, `outside_room`,
  `end_step`, `animation_end`, `draw_gui`, `player_joined`,
  `network_game_started`, `network_message`, `keyboard_release/anykey`, or a
  key the drop-down lacks (`shift`). They disappear on the first Blockly edit
  (12 samples). `event_other` — listed `"implemented": True` in
  `BLOCK_REGISTRY` and enabled in the **beginner** preset for Breakout's
  game-over — **does not exist as a block at all.**
- [ ] **B4 — Expressions in number slots become numbers (HIGH).** The loader
  puts a non-numeric value into a `math_number`, so `direction+90` → 0,
  `32/6` → 4, `8*other.hspeed` → 0 (`set_direction_speed`,
  `jump_to_position`, `if_collision`, `draw_sprite` x/y, `draw_health_bar`).
  `jump_to_position.relative: true` also becomes `false`. Fix direction: load a
  non-numeric value as a `text` block (which `getInputValue` already returns
  verbatim).
- [ ] **B5 — Parameters the hand-written blocks don't model are dropped (HIGH).**
  "Applies to" `target` / `target_object` (`change_instance`, `jump_to_start`,
  `set_alarm`, `destroy_instance` — the action then hits the wrong instance);
  every authored `*_translations`; `draw_text.color`; `play_sound.loop`;
  `next_room` / `restart_room.transition`; `set_window_caption` fields;
  `draw_lives.sprite/scale`; `if_collision.relative`; `draw_rectangle.filled`;
  `set_draw_font.align`; `draw_health_bar` colours;
  `start_moving_direction.directions` ("stop" → 0). Fix direction: carry
  unmodelled parameters through on the block (e.g. a hidden data field / mutation)
  and merge them back on save.
- [ ] **B6 — Value blocks silently become the default (MEDIUM).** `getInputValue`
  only knows `math_number`, `text`, `value_x/y/score/lives/health`,
  `math_random_int`. In the toolbox but unhandled: `value_hspeed`,
  `value_vspeed`, `value_mouse_x`, `value_mouse_y`, `math_arithmetic`,
  `math_single`, `logic_compare`, `logic_operation`, `logic_negate`,
  `logic_boolean`.
- [ ] **B7 — `move_towards` is a placeholder (MEDIUM).** Block defined,
  `BLOCK_REGISTRY` says implemented, **no generator** — saves nothing. Hidden
  in beginner/intermediate, visible in the full preset.
- [ ] **B8 — Preset names that match no block (LOW).** `event_other` (see B3),
  `instance_change` (action is `change_instance`; enabled in beginner),
  `game_restart` (action is `restart_game`), and the Thymio Events registry
  names lack the `event_` prefix of the real blocks.
- [ ] **B9 — Thymio Blockly blocks are unreachable dead code (LOW).** Defined in
  `blockly_blocks.js`, in no toolbox (Thymio is programmed through its own
  panel); their generators save `{type: …}` rather than `{action: …}`, which
  the runtime's `execute_action` would ignore. Remove or wire up — decide.
- [ ] **B10 — `set_sprite`'s loader never connects SUBIMAGE/SPEED at all
  (found fixing B1).** `setBlockParameters`'s `case 'set_sprite':` only does
  `block.setFieldValue(params.sprite, 'SPRITE')` — no `connectNumberBlock`
  call for either input, unlike every sibling case. Unlike B1 this isn't
  value-specific: **every** authored `subimage`/`speed`, zero or not, is
  lost on load (falls through to `getInputValue`'s final `return
  defaultValue`, i.e. -1/-1) the moment the object's events sync into
  Blockly with no saved workspace XML. Fix: add the two missing
  `connectNumberBlock('SUBIMAGE', paramOr(params.subimage, -1))` /
  `('SPEED', paramOr(params.speed, -1))` calls.
- [ ] **B11 — `move_free` has no `actionToBlockType` entry (found fixing
  B1).** The generator's `case 'move_free':` (free-direction movement, not
  the 4-way `move_direction`/`start_moving_direction` block) emits
  `{action: 'move_free', ...}` on save, but `actionToBlockType` — the
  loader's action-name → block-type lookup — has no `'move_free'` key, so
  an object authoring `move_free` (action list, GMK import, a sample) gets
  **zero** blocks for that action the moment it's loaded into Blockly:
  confirmed empirically, `loadEventsData` on a `move_free` action produces
  an empty `actions` list, not even a fallback block. Same failure shape as
  B3 (an action/event Blockly can't represent gets silently deleted) but
  this one is self-inflicted — the generator and the loader disagree about
  whether this block exists at all. Fix: add
  `'move_free': 'move_free'` to `actionToBlockType`.

## Suggested order

- [x] **U0 — Safety net, landed `394ca579`.** `BlocklyWidget.
  load_events_data` now asks the real page to regenerate code right after
  loading an object's events, diffs it against what was loaded
  (`editors/object_editor/blockly_roundtrip.diff_events` — the same function
  `tools/audit_blockly_roundtrip.py` now imports, so there's one source for
  "what did Blockly lose", not two). Any difference locks the workspace:
  `blockly_workspace.html` gained a `#lockOverlay` + `workspaceLocked` flag
  that the change-listener checks before notifying Python at all (belt and
  braces — the overlay also blocks mouse interaction), and
  `window.blocklyApi.setLocked(bool, message)` drives both. The message names
  what would be lost via `summarize_issues`. Verified against the real page
  (not just unit tests): `setLocked`/`isLocked`/the overlay's `display` all
  toggle correctly headlessly; the audit tool's own baseline is unchanged
  (still 644 differences — U0 only gates edits, it doesn't fix any loader).
  Tests: `tests/test_blockly_round_trip_safety.py` (19). Does **not** cover
  objects that already have a saved `blockly_workspace` XML (that path is
  `load_workspace_xml`, not `load_events_data` — those blocks are already the
  source of truth) — only the "events authored outside Blockly, about to be
  synced in for the first time" case B1 through B9 are about.
- [x] **B1** (landed — see above).
1. B2, B3, B4, B5 — each its own unit; re-run the tool after each.
2. B6, B7, B8, B9.
3. B10, B11 (found while fixing B1, narrower scope than any of the above).

Each fix: regression test (a headless-page test like the harness, or the tool
in CI), full suite green, commit + push, flip the checkbox with the hash.

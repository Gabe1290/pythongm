# Blockly block audit — 2026-10-08

Question asked: *are all the Blockly blocks connected to real code, or are some
just placeholders?* Status: **review complete, no fix started.** The checkboxes
below are the resume state; one unit ≈ one commit with its regression test.

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

- [ ] **B1 — Typing 0 gives the default instead (CRITICAL, affects new blocks).**
  `getInputValue` returns `parseFloat(NUM) || defaultValue`
  (`blockly_generators.js`), so 0 is replaced by the default: *set gravity 0*
  saves **0.5** (gravity turns on), *set sprite subimage 0 / speed 0* saves -1.
  Seen in plateforme_1–3, maze_4, treasure. Fix: `isNaN` check, not `||`.
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

## Suggested order

0. **Safety net first (recommended U0):** at load time, run load → save on the
   object's events and compare; if Blockly can't reproduce them exactly, don't
   let a Blockly edit overwrite the object (read-only Blockly view + a clear
   message naming what isn't supported). Protects every student immediately,
   and stays useful as a guard after B1–B6 shrink the set.
1. B1 (one-line root cause, affects new work).
2. B2, B3, B4, B5 — each its own unit; re-run the tool after each.
3. B6, B7, B8, B9.

Each fix: regression test (a headless-page test like the harness, or the tool
in CI), full suite green, commit + push, flip the checkbox with the hash.

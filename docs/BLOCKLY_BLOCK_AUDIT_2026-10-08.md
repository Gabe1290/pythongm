# Blockly block audit — 2026-10-08

Question asked: *are all the Blockly blocks connected to real code, or are some
just placeholders?* Status: **review complete; U0, B1, B2 (partial), B3
(partial) landed.** B4–B9 are still open, plus three new findings (B10, B11,
B12) turned up while fixing B1/B3, B2 itself only closes 3 of its 4 named
cases (see B2's own notes), and B3 leaves the three LAN-multiplayer events
open (see B3's own notes). The checkboxes below are the resume state; one
unit ≈ one commit with its regression test.

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
   (2026-10-08 baseline: **644 differences**; target 0). *The "644 → 633 → 615"
   chain recorded in U0/B1/B2's own notes below went stale sometime after B2 —
   re-measured directly against pre-refactor HEAD before starting B3 and the
   real number by then was **598**, not 615 (more samples/objects had landed
   in between on another machine; this doc's own baseline wasn't re-verified
   each time). Post-B3: **596** (see B3's own notes for why the headline count
   barely moved despite fixing 37 event-drops — it's not a regression).*

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
  `tests/test_blockly_block_audit_roundtrip.py` (6 tests, one shared
  QWebEngineView -- creating more than one per test process segfaults here).
  Surfaced two new, separate bugs while testing (now B10/B11 below) that are
  **not** fixed by this change.
- [x] **B2 — Conditions lose their condition and nested actions, landed
  `2dd6215d` (partial — see remaining items below).**
  - `if_condition` / `test_variable`: **fixed.** Neither had an
    `actionToBlockType` entry, so they loaded as the generic
    `custom_if_condition` / `custom_test_variable` block — which has no
    DO/ELSE statement input at all (`registerCustomBlocks` only knows
    number/choice/boolean/string fields). Verified empirically this was
    worse than the audit's own description: round-tripping either action
    produced **zero** actions, not `parameters: {}` with the condition
    merely blanked. Added the mapping, a real `setBlockParameters` case for
    each (restoring the condition fields — including `test_variable`'s
    `scope`/`global.`-prefix reconstruction), and a new **ELSE** statement
    input on both blocks (was DO-only) wired through generator + loader.
    **Remaining, not fixed:** `if_condition`'s hand-written block only has
    fields for `condition_type='instance_count'` — loading any other
    `condition_type` (`expression`, `key`, ...) now preserves the nested
    actions, but the condition itself reverts to `instance_count`. A real
    multi-condition-type UI is a separate, larger feature.
  - `if_next_room_exists` / `if_previous_room_exists`: **THEN actions were
    already fine** (re-verified against the real page before touching
    anything — the audit's "nested actions dropped" claim was wrong for
    this half). **ELSE actions were genuinely dropped** (no ELSE statement
    input existed) even though the runtime actually executes them
    (`runtime/action_room.py`'s `_dispatch_room_test`) — not cosmetic.
    Fixed the same way as `if_condition`/`test_variable`.
  - `test_expression`: **not fixed.** No hand-written block exists at all
    (confirmed — zero references anywhere in `blockly_blocks.js` /
    `blockly_generators.js`); falls to the same "zero actions survive"
    failure as `if_condition` did. Needs a new block (expression input +
    DO/ELSE), not a wiring fix.
  - `if_collision_at`: **not fixed, as originally described.** No block
    exists; `createActionBlock` deliberately unwraps it to its first nested
    action, discarding the condition and the rest. Same remedy as
    `test_expression` — a new block, not in this commit's scope.
  - Audit tool's 98-sample baseline: 633 → 615 (`action-lost` 63 → 4, the
    remaining 4 all `test_expression`). Verified against the real page via
    `tests/test_blockly_block_audit_roundtrip.py`'s `TestB2*` classes (one
    shared `QWebEngineView` fixture with B1's tests — **do not add a
    second real-page test file**; see that module's docstring).
- [x] **B3 — Events with no Blockly block are deleted (partial), landed
  `6a54709a`.** Added the missing `event_other` block (a single `EVENT_NAME`
  dropdown; matches `BLOCK_REGISTRY`'s pre-existing but previously-false
  `"implemented": True` claim) and routed `game_start`, `game_end`,
  `room_start`, `room_end`, `begin_step`, `end_step`, `draw_gui`,
  `outside_room`, `intersect_boundary`, `no_more_lives`, `no_more_health`,
  `animation_end` through it (`createEventBlock` LOAD side, `getEventType`
  SAVE side). Separately, `createEventBlock`'s keyboard dispatch checked bare
  `key === 'anykey'/'nokey'` **before** checking whether the event was a
  press/release variant, so `keyboard_release_anykey` collapsed into the
  always-held, no-KEY-field `event_keyboard_anykey` block — fixed by checking
  press/release first, and added `"anykey"`/`"nokey"`/`"shift"` to the KEY
  dropdown's option list (`event_keyboard_press`/`_release` already had the
  field; it just had no matching option, so even correct dispatch ordering
  would have silently reset to the dropdown's first entry).
  **Remaining, not fixed:** `player_joined`, `network_game_started`,
  `network_message` — the LAN multiplayer extension's own events, which need
  per-event blocks following Thymio's convention
  (`PLUGIN_EVENT_BLOCKLY_MAP`), not `event_other` (core-only). A natural
  follow-up unit, same shape as B2's deferred `test_expression`/
  `if_collision_at`.
  Audit tool's 98-sample baseline: 598 → 596 (`event-dropped` 44 → 7, all
  three remaining are the multiplayer events above). The headline total
  barely moved despite fixing 37 event-drops because events that previously
  vanished *entirely* now load far enough to reveal that several of their own
  nested actions have no Blockly representation either — see B12 below; not
  a regression, confirmed via a direct pre/post-fix comparison, not just the
  doc's own prior (and by this point stale) numbers. Verified against the
  real page via `tests/test_blockly_block_audit_roundtrip.py`'s `TestB3*`
  classes (same shared fixture as B1/B2 — do not add a second real-page test
  file).
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
- [ ] **B12 — Several extension actions have no Blockly block at all (found
  fixing B3).** Invisible before B3 because the events containing them
  (`game_start`, `keyboard_press/shift`, ...) were dropped *entirely*; B3
  made them load far enough to reveal the gap underneath. Confirmed via the
  audit tool: `action-lost` went 32 → 36 after B3, all four new entries
  inside previously-dropped events. Affects at least: Block World's
  `move_and_collide`, `set_look_pitch`, `select_hotbar_slot`, `place_block`,
  `break_block`, `load_block_world`, `draw_block_world_hud`; LAN
  multiplayer's `host_game`, `join_game`, `network_spawn`, `set_shared_var`,
  `send_network_message` — but several of these were *already* `action-lost`
  before B3 too (inside events that DID load, e.g. `keyboard_press/h` for
  `host_game`), so this isn't purely a B3 side-effect; the extension-action
  Blockly coverage gap is real and pre-existing, just undercounted. Scope:
  likely needs each extension's own `actionToBlockType`-equivalent wiring
  (mirroring Thymio's pattern), not a one-line fix — hasn't been
  investigated beyond confirming it's real via the audit tool.

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
- [x] **B2** (landed, partial — see above; `test_expression` and
  `if_collision_at` still have no block at all and remain open).
- [x] **B3** (landed, partial — see above; `player_joined`/
  `network_game_started`/`network_message` still have no block and remain
  open).
1. B4, B5 — each its own unit; re-run the tool after each.
2. B6, B7, B8, B9.
3. B10, B11 (found while fixing B1), B12 (found while fixing B3) — narrower
   scope than any of the above.
4. The three deferred LAN-multiplayer events (B3's remainder) — needs
   per-event Blockly blocks, not `event_other`; a reasonable pairing with
   B12 if that turns out to need the same per-extension wiring investigation.

Each fix: regression test (a headless-page test like the harness, or the tool
in CI), full suite green, commit + push, flip the checkbox with the hash.

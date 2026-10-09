# Blockly block audit — 2026-10-08

Question asked: *are all the Blockly blocks connected to real code, or are some
just placeholders?* Status: **review complete; U0, B1, B2 (+ its
condition_type follow-up), B3 (partial), B4, B5 landed.** B6–B9 are still
open, plus four new findings (B10, B11, B12, B13) turned up while fixing
B1/B3/B5. B2 itself now closes 3 of its 4 named cases plus the
condition_type follow-up described under its own bullet (the 4th,
`test_expression`, needs a new block — see below), and B3 leaves the
three LAN-multiplayer events open (see B3's own notes). The checkboxes
below are the resume state; one unit ≈ one commit with its regression
test.

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
   barely moved despite fixing 37 event-drops — it's not a regression).
   Post-B4: **566**. Post-B5: **255** (`param-dropped` 277 → 0). Post-B2's
   condition_type follow-up: **176** (every remaining `if_condition`
   entry gone from the `--details` output).*

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
    **Follow-up, now fixed (landed `7906b7d9`):** `if_condition`'s
    hand-written block originally had fields for
    `condition_type='instance_count'` only — loading any other
    `condition_type` preserved the nested actions but the condition itself
    reverted to `instance_count`. Rebuilt the block with one field-group
    per condition_type (8 total, matching
    `events/conditional_editor.py`'s `ConditionalActionEditor` and
    `runtime/action_executor.py`'s `_evaluate_if_condition` field-by-field),
    shown/hidden via the `CONDITION_TYPE` dropdown's validator — the same
    `setVisible` pattern `set_sprite` already uses elsewhere in the file.
    Verified against the real page via
    `tests/test_blockly_block_audit_roundtrip.py`'s
    `TestB2ConditionTypesBeyondInstanceCount` class, using the shared
    `diff_events` comparator. Audit tool's 98-sample baseline: 255 → 176
    (every `if_condition` entry gone from `--details`). `test_expression`
    and `if_collision_at` (below) are unaffected — this only extends the
    block `if_condition` already had.
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
- [x] **B4 — Expressions in number slots become numbers, landed
  `d20a4706`.** Two of the five originally-named examples (`if_collision`,
  `draw_sprite`) don't exist anywhere in this codebase, and a third
  (`set_direction_speed`) is really `move_direction`'s fixed 4-way DIRECTION
  dropdown — a B5-shaped "the block can't model this" gap, not fixable by
  this fix at all. Corrected here rather than chased. Only `jump_to_position`
  and `draw_health_bar` were real.
  `connectNumberBlock` (LOAD) now falls back to a `text` block (which
  `getInputValue` already returns verbatim on SAVE) for any value that
  isn't a plain number — but that alone did nothing: `Connection.connect()`
  refuses the connection outright when the input is `.setCheck("Number")`
  and `text`'s output is `"String"` (confirmed empirically with a
  throwaway script). Fixed by dropping the type check on
  `move_jump_to`'s/`draw_health_bar`'s X/Y inputs specifically — not swept
  across every `connectNumberBlock` call site.
  Also fixed, same bullet: `jump_to_position.relative` always saved `false`
  — the generator already read a `RELATIVE` field that never existed on
  the block; added the checkbox. And a bug only exposed once X/Y could be a
  string: `draw_health_bar` derives `x2`/`y2` as `x1 + width`/`y1 + 20` with
  a plain JS `+`, which silently did STRING CONCATENATION
  (`"self.x" + 100` → `"self.x100"`) the moment `x1` became non-numeric.
  Fixed with a new `addExpr(a, b)` helper: real arithmetic when both sides
  are genuinely numbers (byte-identical old behaviour), an evaluable
  expression string otherwise.
  **Known, documented remaining limitation, not fixed:** `draw_health_bar`'s
  bar height is a hardcoded `+20`, not a real field — any sample authoring a
  different height (confirmed for real: `raycast_3`'s hud bar is 18px) can
  never round-trip its `y2` exactly, independent of this fix.
  `draw_rectangle` has the identical width/height-derivation shape and would
  hit the identical bug if its own X/Y inputs ever lost their `"Number"`
  check — not done here (unconfirmed by any sample, not a named case), so
  it's unaffected either way.
  Audit tool's 98-sample baseline: 596 → 566 (`param-changed` 263 → 233,
  all from `jump_to_position` — now fully clean across every sample — and
  one pre-existing, unrelated `draw_health_bar.y2` diff explained above).
  Verified against the real page via
  `tests/test_blockly_block_audit_roundtrip.py`'s `TestB4*` classes (same
  shared fixture as B1–B3).
- [x] **B5 — Parameters the hand-written blocks don't model are dropped,
  landed `e7046f0f`.** Fixed with ONE generic mechanism, not twelve
  per-block patches, matching the audit's own prescribed fix direction
  exactly: `createActionBlock` (LOAD) stashes the full, untouched `params`
  dict as `block.pygmExtraParams`; both places that build the final
  `{action, parameters}` result on SAVE — `generateActionCode`'s wrapper
  (every hand-written block) and the dynamic `custom_*` block generator's
  own from-scratch builder (`registerCustomBlocks`'s monkeypatch, used for
  every action with NO hand-written block at all) — merge that stash back
  in underneath whatever their own code explicitly produced.
  The dynamic-block path turned out to be the one that actually mattered
  for most of the named examples: `change_instance`, `set_window_caption`,
  `jump_to_start`, `play_sound.loop`, `test_instance_count.count` and
  others have no hand-written block at all — e.g. `change_instance` sets
  `supports_applies_to=True` (`events/action_types.py`) but has no
  `target`/`target_object` `ActionParameter` in its own list, so the
  generic UI builder never knew `target`/`target_object` existed.
  Confirmed via the audit tool: `param-dropped` across all 98 samples went
  from 277 to **zero** — every named example, plus several the audit
  didn't name (`test_variable`/`set_sprite`/`set_variable`'s own target/
  target_object, `draw_lives.image`/`.relative`, ...).
  **A second, independent bug found investigating this bullet's own
  `start_moving_direction.directions` example:** `"stop"` is a real
  sentinel the runtime zeroes both speeds for, not "move at 0 degrees"
  (right) — `move_direction`'s generator fell through its degrees switch
  for `dir === 'stop'` straight to its default, silently turning every
  authored "stop" into "move right" (confirmed across 12 samples). Fixed
  with an explicit early return. `move_direction`'s SPEED field got the
  same B4 treatment (dropped `"Number"` check) for the identical reason
  (`speed: "32/6"` was becoming the default `4`).
  **Known, NOT addressed:** the remaining `start_moving_direction.directions`
  diffs (`'right' -> 0`, `'up' -> 90`, ...) are a representation
  difference the audit tool's comparator flags, not a behaviour change —
  the runtime accepts both forms identically (same category as B1's own
  note about the samples storing parameters as strings).
  Verified against the real page via
  `tests/test_blockly_block_audit_roundtrip.py`'s `TestB5*` classes
  (same shared fixture as B1–B4, now also registering a dynamic block
  so the custom_* merge path is exercised directly, not just via the
  audit tool).
- [ ] **B6 — Value blocks silently become the default (MEDIUM).** `getInputValue`
  only knows `math_number`, `text`, `value_x/y/score/lives/health`,
  `math_random_int`. In the toolbox but unhandled: `value_hspeed`,
  `value_vspeed`, `value_mouse_x`, `value_mouse_y`, `math_arithmetic`,
  `math_single`, `logic_compare`, `logic_operation`, `logic_negate`,
  `logic_boolean`.

  **Decided with the user 2026-10-09: make them all real, not hide them.**
  Constraint for every unit: the text `getInputValue` saves must evaluate on
  all three engines — desktop (`ActionExecutor._parse_value` /
  `_evaluate_expression` / `_eval_bool_expression`), HTML5
  (`engine.js` `gmExpressionValue` + the action-param evaluator near the
  `gmIrandom` replace), Kivy (`export/Kivy/code_generator.py`
  `_resolve_instance_names` + its function whitelist regex). Check each
  before choosing a spelling; `math_random_int` → `irandom(...)` is the
  precedent. Units, one commit each:
  - [ ] **B6a — value blocks + B15.** `value_score/lives/health` → bare
    `score`/`lives`/`health` (works on all three; `game.score` doesn't on
    desktop); `value_hspeed/vspeed` → `self.hspeed`/`self.vspeed`;
    `value_mouse_x/y` → needs the name resolved on every engine first
    (desktop leaves bare `mouse_x` unresolved); `math_arithmetic` →
    parenthesised `(A op B)` with `+ - * /` and `**` for power.
  - [ ] **B6b — math functions on all three engines.** Add `sqrt`, `ln`,
    `log10`, `exp`, `pow10` (or the spellings chosen) to every engine's
    function set (desktop `_known_functions`, the function-detect regex,
    `safe_namespace`, `_eval_bool_expression`'s namespace; HTML5 evaluator
    scope; Kivy whitelist + generated helpers), then map every
    `math_single` op (ROOT, ABS, NEG, LN, LOG10, EXP, POW10).
  - [ ] **B6c — Logic blocks get a true/false slot: a `test_expression`
    block.** Closes B2's remaining `test_expression` gap at the same time:
    an "if ‹condition›" block with a CONDITION value input (no type check,
    so an authored expression loads as a text block, per B4) and DO/ELSE.
    New `getConditionValue` builds Python-syntax text from
    `logic_compare` (== != < <= > >=), `logic_operation` (and/or),
    `logic_negate` (not), `logic_boolean` (True/False) and any number
    block via `getInputValue` — the syntax `_eval_bool_expression`
    evaluates, HTML5 already converts (`and`/`or`/`not`/`True`/`False`),
    and Kivy emits as Python. Loader: `actionToBlockType` entry + DO/ELSE.
  - [ ] **B6d — re-run the audit tool and the full Blockly suite; check
    a sample exports to HTML5 and Kivy with each new spelling.**
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
- [x] **B10 — `set_sprite` lost its frame and speed, landed (commit
  "fix(blockly): B10", 2026-10-09).** Worse than recorded: the loader gap was
  real, but the block students actually get is `blockly_workspace.html`'s own
  `set_sprite`, which **overrides** `blockly_blocks.js`'s and had only a
  sprite dropdown — no SUBIMAGE/SPEED inputs at all, so a student could not
  set a frame or speed in Blockly, and a saved `<self>` showed as
  "`<self>` (missing)". Added both inputs (no `setCheck("Number")`, so a B4
  expression text block can connect — verified: with the check, an
  expression speed silently became -1), a real "`<self>` (current)" choice
  via a new optional `extraOptions` argument to `createAssetField`, -1
  shadows on both toolbox entries, the two `connectNumberBlock` calls in the
  loader, and fr/pl/de/it/uk labels. Audit tool: 176 → 112. Tests:
  `TestB10SetSpriteFrameAndSpeed` (2 of its 3 fail on the pre-fix page).
- [ ] **B14 — A saved asset name that isn't in the project can't be restored
  by any asset dropdown (found fixing B10).** `createAssetField`'s
  "(missing)" preservation only works for a value set while it was valid;
  `setFieldValue` with a name not in `BLOCKLY_ASSET_LISTS` (deleted/renamed
  sprite, object, sound, room) is rejected by Blockly and the field keeps
  its first option. Pre-existing for every asset field; for `set_sprite` the
  fallback is now `<self>` ("keep current sprite") rather than an empty
  name. U0's lock catches it, but a real fix would load such names as a
  preserved "(missing)" option.
- [ ] **B15 — The score/lives/health value blocks save names the desktop
  engine can't evaluate (found scoping B6, 2026-10-09).** `getInputValue`
  turns `value_score`/`value_lives`/`value_health` into `game.score` /
  `game.lives` / `game.health`, but `ActionExecutor._parse_value` only
  knows the bare names: verified with plain objects (not mocks, which
  "resolve" every attribute), `game.score` stays the literal string
  `"game.score"` and `game.score + 1` evaluates to 0 (`name 'game' is not
  defined`), while `score` → 7 and `score + 1` → 8. Bare `mouse_x` is
  unresolved too. Fix with B6: emit the names every target evaluates
  (check HTML5's `gmExpressionValue` and Kivy's expression translation
  for each before choosing).
- [x] **B11 — `move_free` has no `actionToBlockType` entry, landed (commit
  "fix(blockly): B11", 2026-10-09).** Added the mapping, a loader case
  restoring DIRECTION/SPEED, and dropped the inputs' `setCheck("Number")`
  so an expression direction (a B4 text block) can connect. No sample uses
  `move_free`, so the audit tool can't show it (stays 112); proof is
  `TestB11MoveFreeRoundTrips` (both tests fail on the pre-fix page).
  Original note: the generator's `case 'move_free':` (free-direction movement, not
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
- [ ] **B13 — `start_moving_direction.directions` can be an ARRAY, which
  `move_direction` can't model at all (found fixing B5).** A patrolling
  monster picking a random direction from several (`["left", "right"]`,
  `["up", "down", "left", "right"]`, ...) is real, authored data — confirmed
  across 7 samples (`maze_3`/`4`'s three monster types, `plateforme_3`,
  `raycast_2`/`3`/`4`). `move_direction`'s DIRECTION field is a single-value
  dropdown; every one of these collapses to a single hardcoded direction
  (0/right) on round-trip, silently narrowing a patrol into a straight line.
  Not a quick fix — needs a real UI redesign (a checkbox grid, matching the
  pattern the action-list editor already uses for this exact parameter),
  not a dropdown tweak.

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
- [x] **B4** (landed — see above; the two originally-named non-existent
  actions and the `move_direction`-dropdown case were corrected out of
  scope, not fixed).
- [x] **B5** (landed — see above; `param-dropped` fully closed across all
  98 samples).
1. B6, B7, B8, B9.
2. B10, B11 (found while fixing B1), B12 (found while fixing B3), B13
   (found while fixing B5) — narrower scope than any of the above.
3. The three deferred LAN-multiplayer events (B3's remainder) — needs
   per-event Blockly blocks, not `event_other`; a reasonable pairing with
   B12 if that turns out to need the same per-extension wiring investigation.

Each fix: regression test (a headless-page test like the harness, or the tool
in CI), full suite green, commit + push, flip the checkbox with the hash.

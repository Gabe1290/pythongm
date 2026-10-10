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
- [x] **B6 — Value blocks silently become the default (MEDIUM) — closed 2026-10-10 via B6a–B6d below.** `getInputValue`
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
  - [x] **B6a — value blocks + B15, landed (commit "fix(blockly): B6a",
    2026-10-09).** Spellings in a shared `VALUE_BLOCK_EXPRESSIONS` table:
    `score`/`lives`/`health`, `self.hspeed`/`self.vspeed`,
    `self.mouse_x`/`self.mouse_y` (the last mouse press, the meaning all
    three engines share); `math_arithmetic` → `(A op B)` with `**` for
    power. Engine side: desktop instances now start with
    `mouse_x`/`mouse_y` = 0 (HTML5/Kivy already did); HTML5's
    `parseNumParam` falls back to `gmExpressionValue` (it rejected any bare
    name — verified in a real browser engine: score 7, self.mouse_x 120,
    `(score * (self.x + 2))` 84); Kivy needed nothing. Loader: those exact
    texts (and legacy `game.*`) load as their value blocks, and — found
    while testing — a text block carrying an expression could not connect
    to a Number-only input at all (~120 of them), so `(score * 2)` in
    set_hspeed loaded as nothing; `connectTextBlock` now untypes that one
    block's output. Audit tool 112 → 106. Tests:
    `TestB6aValueAndArithmeticBlocks` + `tests/test_blockly_value_expressions.py`.
  - [x] **B6b — math functions on all three engines, landed (commit
    "feat(blockly): B6b", 2026-10-10).** `sqrt`, `ln`, `log10`, `exp`
    (GameMaker's names; 10^x is `(10 ** (x))`, no function needed).
    Desktop: new `runtime/gm_math.py` (`GM_MATH_FUNCTIONS`, its own module
    because `action_executor` imports `action_flow`), wired into
    `_parse_value`'s function-detect regex, `_known_functions`,
    `safe_namespace` and `_eval_bool_expression`. HTML5: `gmSafeMath` +
    scope entries in `gmExpressionValue` (numbers reach it via B6a's
    `parseNumParam` fallback). Kivy: `GameObject.sqrt/ln/log10/exp`
    methods (the resolver binds names to `self.`, as with `random`) + the
    `_VALUE_IS_EXPRESSION` regex. **Agreed rule: a domain error (sqrt of a
    negative, ln of 0) gives 0 for that call on every engine** — before,
    desktop zeroed the whole expression, HTML5 got NaN and Kivy would have
    raised mid-game. All nine probe expressions give identical results on
    the three engines (HTML5 via the real engine.js headlessly). Generator:
    `MATH_SINGLE_TEMPLATES` for all seven ops. Tests: `TestB6bMathSingle` +
    the MATH cases in `tests/test_blockly_value_expressions.py` (17 of 20
    fail on the old code; abs/negate/power already worked).
  - [x] **B6c — landed (commit "feat(blockly): B6c", 2026-10-10).** As
    planned, plus two things found on the way: (1) **Kivy dropped nested
    branches on `test_expression`** — it only opened a guard over the next
    action, so the block's then/else would have vanished from Kivy exports;
    now emits `if/else` when nested lists are present (flat GM-style still
    guards the next action). HTML5 already ran nested branches. (2)
    `test_expression` moved from `GENERATED_ACTION_NAMES` to
    `BLOCK_REGISTRY`, which **silently removed it from six presets**
    (platformer, grid_rpg, sokoban, testing, code_editor, blockly_editor)
    that enable "every generated action" as a set — the full suite didn't
    catch it, a direct preset check did. New
    `PROMOTED_TO_HAND_WRITTEN_BLOCKS` is added wherever the generated set
    is; pinned by a test. Conditions verified identical on all three
    engines (HTML5 with the real engine.js). Audit tool 106 → 102,
    **action-lost 4 → 0** (all four were `test_expression`). Original plan:
    Closes B2's remaining `test_expression` gap at the same time:
    an "if ‹condition›" block with a CONDITION value input (no type check,
    so an authored expression loads as a text block, per B4) and DO/ELSE.
    New `getConditionValue` builds Python-syntax text from
    `logic_compare` (== != < <= > >=), `logic_operation` (and/or),
    `logic_negate` (not), `logic_boolean` (True/False) and any number
    block via `getInputValue` — the syntax `_eval_bool_expression`
    evaluates, HTML5 already converts (`and`/`or`/`not`/`True`/`False`),
    and Kivy emits as Python. Loader: `actionToBlockType` entry + DO/ELSE.
  - [x] **B6d — landed (commit "test(blockly): B6d", 2026-10-10).**
    A real Kivy export (maze_1 plus a step event using every B6a/B6b/B6c
    spelling) compiles and contains the expected calls
    (`test_kivy_export_with_every_new_spelling_compiles`; fails against the
    pre-B6b Kivy files). HTML5 copies actions verbatim, and its two
    evaluators were checked with the real engine.js in B6a–B6c. Audit tool
    final: 102 differences, action-lost 0. Full suite green.
- [x] **B7 — `move_towards` is a placeholder, landed (commit
  "fix(blockly): B7", 2026-10-10).** The block now saves the engine's
  `move_towards_point` action (x, y, speed — an exact fit), and
  `move_towards_point` loads back into it instead of the generic custom
  block. Seven presets (intermediate, platformer, grid_rpg, sokoban,
  testing, code_editor, blockly_editor) enabled the action but not the block
  name, so `move_towards` joined `PROMOTED_TO_HAND_WRITTEN_BLOCKS` (the
  action stays in `GENERATED_ACTION_NAMES` for the action-list editor).
  Tests: `TestB7MoveTowards` + a preset guard; all 3 fail on the old code.
  Original note: block defined,
  `BLOCK_REGISTRY` says implemented, **no generator** — saves nothing. Hidden
  in beginner/intermediate, visible in the full preset.
- [x] **B8 — Preset names that match no block, landed (commit
  "fix(blockly): B8", 2026-10-10).** Re-checked every `BLOCK_REGISTRY` entry
  against the live page: `event_other` exists since B3. `instance_change`
  was more than a dead name — `ACTION_TO_BLOCKLY_MAP` sends `change_instance`
  to the JS toolbox as `instance_change`, which no JS block has; the only
  block is the generated `custom_change_instance`, matched by the action's
  own name, so **beginner's Blockly tab silently lacked Change Instance**
  while the action-list editor showed it. Fixed generically: new
  `config/toolbox_visibility.toolbox_enabled_blocks` (moved out of
  `BlocklyWidget.apply_configuration`) sends every visible action under its
  own name too — verified in the real toolbox: old list 72 blocks without
  it, new list 73 with it, nothing else added. `game_restart` (a registry
  entry no block or action had, so its config checkbox did nothing) renamed
  to `restart_game`. No other `ACTION_TO_BLOCKLY_MAP` entry points at a
  missing block where a block exists. **Left for B9:** the 14 Thymio event
  registry names (their blocks are unreachable anyway). Tests: four in
  `tests/test_toolbox_visibility.py`. Original note: `event_other` (see B3),
  `instance_change` (action is `change_instance`; enabled in beginner),
  `game_restart` (action is `restart_game`), and the Thymio Events registry
  names lack the `event_` prefix of the real blocks.
- [x] **B9 — landed (commit "fix(blockly): B9", 2026-10-10); the original
  description below was WRONG and the "remove" decision was not applied.**
  On checking before deleting: the 14 Thymio registry names are live —
  `PLUGIN_EVENT_BLOCKLY_MAP` maps each Thymio event to an identical name, so
  they are the switches `get_available_events` uses to offer Thymio events,
  and `ThymioConfigDialog`'s presets (Tools menu) toggle them; and the Thymio
  block definitions are what the loader uses when a Thymio object's events
  are shown in the Blockly tab. Removing either would have broken Thymio.
  The real bug: the 28 Thymio action generators saved `{type: ...}` while
  Thymio's panel, the engine and the Aseba exporter use `{action: ...}`, so
  editing a Thymio object in the Blockly tab silently disabled every Thymio
  action — and U0 missed it because the comparison accepted either key. Fix:
  generators save `action`; `blockly_roundtrip.walk` now reports
  `action-key-changed`, so U0 locks instead. Tests:
  `TestB9ThymioActionsKeepTheActionKey` + a safety-net test. (B8's note
  calling the Thymio registry names dead is corrected by this.) Original:
  Thymio Blockly blocks are unreachable dead code (LOW). Defined in
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
- [x] **B14 — landed with B20 (commit "fix(blockly): B14/B20", 2026-10-10).**
  A saved asset name that isn't in the project can't be restored
  by any asset dropdown (found fixing B10).** `createAssetField`'s
  "(missing)" preservation only works for a value set while it was valid;
  `setFieldValue` with a name not in `BLOCKLY_ASSET_LISTS` (deleted/renamed
  sprite, object, sound, room) is rejected by Blockly and the field keeps
  its first option. Pre-existing for every asset field; for `set_sprite` the
  fallback is now `<self>` ("keep current sprite") rather than an empty
  name. U0's lock catches it, but a real fix would load such names as a
  preserved "(missing)" option.
- [x] **B15 — fixed with B6a (see above).** The score/lives/health value blocks save names the desktop
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
- [x] **B12 — resolved (verified 2026-10-10, no separate fix).** With the
  later loader fixes (B6c, B16, B14/B20) every extension action in the
  samples — Block World's and LAN multiplayer's included — loads as its
  generated `custom_*` block and round-trips: the audit tool's `action-lost`
  count is 0 across all 98 sample objects. Original:
  Several extension actions have no Blockly block at all (found
  fixing B3). Invisible before B3 because the events containing them
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
- [x] **B13 — landed (commit "feat(blockly): B13", 2026-10-10).** As
  decided: `move_direction` is a 3×3 checkbox grid (arrows, centre = stop;
  default →); several ticks save a list (random patrol), a single direction
  saves as before (angle or `stop`), none = `stop`. The loader reads every
  form the runtime accepts (angle, name, list, stringified list); a hidden
  legacy `DIRECTION` field keeps blocks from pre-grid workspace XML pointing
  the right way (tested). `blockly_roundtrip` compares `directions` by the
  set of angles they mean (name = its angle, list order-free), so U0 no
  longer locks those objects. **Audit tool: 0 differences across all 98
  sample objects** (from 644). Tests: `TestB13DirectionGrid` + a normaliser
  test. Original: `start_moving_direction.directions` can be an ARRAY, which
  `move_direction` can't model at all (found fixing B5). A patrolling
  monster picking a random direction from several (`["left", "right"]`,
  `["up", "down", "left", "right"]`, ...) is real, authored data — confirmed
  across 7 samples (`maze_3`/`4`'s three monster types, `plateforme_3`,
  `raycast_2`/`3`/`4`). `move_direction`'s DIRECTION field is a single-value
  dropdown; every one of these collapses to a single hardcoded direction
  (0/right) on round-trip, silently narrowing a patrol into a straight line.
  Not a quick fix — needs a real UI redesign (a checkbox grid, matching the
  pattern the action-list editor already uses for this exact parameter),
  not a dropdown tweak.

### Found 2026-10-10 from the audit tool's remaining 102 differences

**Decided with the user 2026-10-10:** B13 → replace the direction drop-down
with the action-list editor's 3×3 checkbox grid (several ticks = pick one at
random); B17 → `'0'` means **no** on all three engines (matching GameMaker
and the import's intent; check treasure still plays); B9 → remove the dead
Thymio Blockly blocks and their 14 registry names; LAN events → add the three
event blocks, provided by the LAN extension and shown only when it is active.

B12's symptom is gone: extension actions (Block World, LAN) now load as
generated `custom_*` blocks and `action-lost` is 0. What remains, beyond
B13's `directions` and the three LAN events (B3 remainder):

- [x] **B16 — landed (commit "fix(blockly): B16", 2026-10-10).** The
  number-or-expression loader is now one top-level `loadNumberInput` (with
  `loadTextInput`) used by both loaders; audit tool 102 → 76, every
  expression entry gone. Tests: `TestB16GeneratedBlockExpressions`.
  Expressions in auto-generated blocks' number parameters become
  0 (HIGH). The dynamic-block `setBlockParameters` override in
  `blockly_workspace.html` always builds a `math_number` from the value, so
  a non-numeric value parses to 0. B4 fixed this only for hand-written
  blocks (`connectNumberBlock`). Seen: `set_direction_speed` direction
  `facing_angle+180` / `facing_angle` / `direction+90` → 0 (the raycast
  samples' turning), speed `32/6` → 0, `if_collision` x/y `8*other.hspeed`
  → 0, `draw_sprite` x/y `self.x + 3` → 0. Fix: route the dynamic path's
  number params through the same number-or-text logic.
- [x] **B17 — landed (commit "fix(engine): B17", 2026-10-10).** Decided:
  `'0'` means no. One rule, `runtime/gm_math.param_is_true` (False, 0, "0",
  "false", "no", "" are false; missing = the default), used by the
  desktop `change_instance` handler and the Kivy generator (now a literal
  True/False — the raw value was pasted in, so "false" did not even
  compile); HTML5 `gmParamIsTrue`; Blockly's generated-boolean loader.
  treasure: transformed monsters now keep their motion instead of re-running
  `monster`'s create event (new random direction), as the original GameMaker
  game specifies; all 27 samples still smoke-run clean. Audit tool 64 → 60.
  Tests: `tests/test_perform_events_param.py` + `TestB17BooleanTextZero`.
  Original: auto-generated boolean parameters read the text `'0'` as
  true. `change_instance.perform_events: '0'` → `True` (treasure). The
  dynamic loader uses JS truthiness; `'0'`, `'false'`, `''` must be false.
- [x] **B18 — landed (commit "fix(engine): B18", 2026-10-10).** The code
  table already existed in the importer (`gmk_mappings.GM_COMPARISON_OPS`:
  0 equal, 1 less, 2 greater, 3 less_equal, 4 greater_equal, 5 not_equal);
  plateforme_3 predates it. Each engine now normalises the code at its single
  action entry point (desktop `execute_action` via
  `runtime/gm_math.normalize_gm_operation`, Kivy `process_action`, HTML5
  `executeAction` + `evaluateCondition`), and the Blockly loader maps it for
  the OPERATION dropdown. plateforme_3's dead flying monster now caps its
  fall speed at 24 as its comment says. `test_kivy_parity_batch` pinned the
  old always-false behaviour on purpose and was updated (a genuinely unknown
  operation is still false on both). Tests: `tests/test_gm_operation_codes.py`
  + `TestB18NumericOperationCodes`. Original:
  `test_variable` with a numeric GameMaker operation code never
  fires, on the desktop engine itself. plateforme_3's
  `obj_monstre_volant_mort` caps vspeed with `operation: "2"` (kept by the
  GMK import); `ActionExecutor._compare` only knows names/symbols, so it
  always returns False. Blockly then turns `'2'` into `equal`. Fix in the
  importer and/or `_compare` (and the export engines) — **confirm
  GameMaker's code table first** (0 equal, 1 smaller, 2 larger, ... is
  likely but must be checked against the GM8 format / gmk importer).
- [x] **B19 — landed (commit "fix(blockly): B19", 2026-10-10).** New
  `instance_destroy_object` block ("Destroy all instances of ‹object›",
  object drop-down, fr/pl/de/it/uk), generated as `target: object` +
  `target_object`; the loader picks it for target `object`. Registry
  Instance entry; every preset that enables "destroy other" enables it
  (beginner ships maze_4, which needs it) — pinned by a test. Audit tool
  65 → 64. Tests: `TestB19DestroyAllInstancesOfObject`. Original:
  `destroy_instance` with target `object` loads as "destroy
  self". maze_4: the loader picks `instance_destroy` vs
  `instance_destroy_other` from `target` and collapses `object` (+
  `target_object`) into self — the wrong instance is destroyed.
- [x] **B20 — landed with B14 (commit "fix(blockly): B14/B20", 2026-10-10).**
  Generic fix: `Blockly.FieldDropdown.prototype` `doClassValidation_` /
  `getOptions` are wrapped so that, only while saved data loads
  (`loadEventsData` / `loadWorkspaceXml` run under `whileLoadingSaved`), an
  unknown value is kept as an extra choice instead of being rejected;
  outside loading a drop-down still rejects it (tested). Audit tool 75 → 73.
  Tests: `TestB14B20UnknownDropdownValues`. A value missing from a fixed
  drop-down resets to its first option. `place_block.block: 'hotbar_block'` → `'brick'` (block_world_1/2,
  where `hotbar_block` means "the selected hotbar slot"). Same family as
  B14 (asset names); fix both by keeping an unknown saved value as an extra
  option.
- [x] **B21 — landed (commit "fix(blockly): B21", 2026-10-10).** The
  block had no height input: the generator hardcoded y2 = y1 + 20 (the
  translation tables already had a 4-field label with "hauteur"). Added
  HEIGHT (fr/pl/de/it/uk labels); the loader now rebuilds width/height from
  the saved corners via `cornerSpan` — numeric when both are numbers, else
  `(end) - (start)` — instead of `(x2 - x1) || 100`, which also moved an
  absolute right edge whenever x1 was an expression (B4's test pinned that
  lossy result and was corrected). Audit tool 76 → 75. Tests:
  `TestB21HealthBarHeight`. Original: `draw_health_bar` y2 468 → 470
  (raycast_3). The
  hand-written block derives y2 from other fields; one value shifts by 2.
  Investigate before classifying.
- Harmless, no action: `'true'` → `True` on `set_view.visible`,
  `enable_views.enable`, `enable_block_world_view.generate` (the engine
  parses both), and `room_goto_next` → `next_room` (an alias).

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
3. ~~The three deferred LAN-multiplayer events (B3's remainder)~~ **Done
   2026-10-10 (commit "feat(blockly): extension event block"):** one generic
   `event_extension` block covers every extension event without a dedicated
   block (12: LAN + file-exchange multiplayer); Python pushes all names (for
   loading) and the active extensions' events (drop-down) via
   `blocklyApi.setExtensionEvents`; the toolbox shows it only when an active
   extension has events. Audit tool 60 → 53, event-dropped 0. Original:
   The three deferred LAN-multiplayer events (B3's remainder) — needs
   per-event Blockly blocks, not `event_other`; a reasonable pairing with
   B12 if that turns out to need the same per-extension wiring investigation.

Each fix: regression test (a headless-page test like the harness, or the tool
in CI), full suite green, commit + push, flip the checkbox with the hash.

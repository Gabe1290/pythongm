"""Regression tests for docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md that drive the
REAL editors/object_editor/blockly/blockly_workspace.html headlessly, rather
than reimplementing its save/load logic in Python.

**All such tests live in this ONE file, sharing ONE QWebEngineView fixture.**
Creating more than one QWebEngineView per pytest process has been observed to
segfault here -- confirmed the hard way: splitting B1's and B2's real-page
tests into two separate module-scoped-fixture files worked fine individually,
then segfaulted every time pytest selected both in one run (`-k blockly`
alone was enough, no other files needed). If a future finding (B3, B4, ...)
needs its own real-page round trip, add its CASES entries and test class
HERE -- don't start a new file with its own fixture.

## B1 -- Typing 0 gives the default instead

Two independent halves of the same `value || default` anti-pattern:
- blockly_generators.js's getInputValue (SAVE: blocks -> events) -- typing 0
  into a number block saved the block's DEFAULT: "set gravity 0" saved 0.5
  (gravity turned ON when the student meant to turn it off).
- blockly_workspace.html's setBlockParameters, via connectNumberBlock /
  connectTextBlock (LOAD: events -> blocks) -- a project.json storing gravity
  as the JSON NUMBER 0 (not the string "0") loaded the STRENGTH field as 0.5
  before getInputValue's own fix ever got a chance to see a real 0 (the 98
  bundled samples all store parameters as strings, where "0" is truthy, so
  this half never showed up in the audit tool's own sample-based round trip).

(The audit's other named B1 example, "set sprite subimage 0 / speed 0",
turned out to have a second, separate bug layered on top -- the loader never
connects a number block to SUBIMAGE/SPEED for set_sprite at all, so it's
wrong for every value, not just 0; logged as B10 in the audit doc.)

## B2 -- Conditions lose their condition and nested actions

if_condition and test_variable had no entry in the loader's
actionToBlockType, so an authored object loaded them as the generic
custom_if_condition / custom_test_variable block -- which has no DO/ELSE
statement input at all (registerCustomBlocks only knows number/choice/
boolean/string fields). The condition AND every nested then/else action
vanished the moment the object synced into Blockly: round-tripping either
action through the real page produced zero actions, not even a lossy
placeholder. if_next_room_exists / if_previous_room_exists were already
loadable but had no ELSE statement input, so an authored else_actions
(which the runtime genuinely executes -- runtime/action_room.py's
_dispatch_room_test) was silently dropped.

## B2 follow-up -- if_condition's other 7 condition_types

if_condition's hand-written block originally had fields for
condition_type='instance_count' only -- loading any other condition_type
(variable_compare, position_check, collision_check, key_pressed,
mouse_check, random_chance, expression) preserved the nested then/else
actions (B2's fix above) but the condition itself silently reverted to
instance_count, since there was nowhere to put it.

Rebuilt the block with one field-group per condition_type (a
CONDITION_TYPE dropdown whose validator shows/hides the matching group via
setVisible -- the same pattern 'set_sprite' already used elsewhere in this
file), matching events/conditional_editor.py's ConditionalActionEditor
(the traditional action-list editor's equivalent, already supporting all
8 types) and runtime/action_executor.py's _evaluate_if_condition field-
by-field, including the key_pressed condition's canonical key-name set
(deliberately NOT the file's keyboard-EVENT-block ALL_KEYS list, which
uses lshift/rshift/lctrl -- this condition uses the smaller generic
shift/control/alt set both the runtime and the Python editor use).

test_expression and if_collision_at still have no hand-written block at
all and are untouched by this fix (see the audit doc) -- that's a new
block, not a wiring fix, same as B2's own note on those two.

Audit tool's 98-sample baseline: 255 -> 176 (B2 was the last of B1-B5's
if_condition-adjacent fixes; this follow-up's drop is isolated to
if_condition entries, confirmed by their complete absence from the
`--details` output after this fix, where they were present before).
Verified against the real page via
`tests/test_blockly_block_audit_roundtrip.py`'s
`TestB2ConditionTypesBeyondInstanceCount` class (same shared fixture),
using `editors/object_editor/blockly_roundtrip.py`'s own `diff_events`
comparator rather than a hand-rolled equality check, so representational
differences ("10" vs 10) don't false-positive.

## B3 (partial) -- Events with no Blockly block are deleted

Two independent gaps, both in blockly_workspace.html's createEventBlock
(LOAD: events -> blocks):

- Nine events (game_start, game_end, room_start, room_end, begin_step,
  end_step, draw_gui, outside_room, intersect_boundary, no_more_lives,
  no_more_health, animation_end) had NO block at all -- `event_other`
  (config/blockly_config.py's BLOCK_REGISTRY already claimed it existed,
  "implemented": True) was never actually defined. The whole event, and
  everything nested inside it, vanished on the first Blockly edit. Fixed by
  adding the block (a single EVENT_NAME dropdown) and routing all twelve
  through it.
- The keyboard dispatch checked `key === 'anykey'`/`'nokey'` BEFORE checking
  whether the event was a press/release variant, so `keyboard_release_anykey`
  collapsed into the always-held, no-KEY-field `event_keyboard_anykey` block
  -- silently losing the "release" half. Fixed by checking press/release
  first; `event_keyboard_press`/`_release` already have a KEY dropdown, it
  just didn't offer "anykey"/"nokey"/"shift" as values (so even a
  correctly-ordered dispatch would have silently reset to the dropdown's
  first option) -- added all three.

**Not fixed, deliberately deferred (still event-dropped):** `player_joined`,
`network_game_started`, `network_message` -- the LAN multiplayer extension's
own events, which need their own blocks following Thymio's per-event-block
convention (`extensions/thymio/__init__.py`'s `PLUGIN_EVENT_BLOCKLY_MAP`),
not `event_other` (that's for core-only events). Scoped out as its own
follow-up unit, same shape as B2's deferred `test_expression`/
`if_collision_at`.

**New finding surfaced by this fix, not fixed here (logged as B12 in the
audit doc):** events that previously vanished ENTIRELY now load far enough
to reveal that several of their OWN nested actions have no Blockly
representation either (block_world's `move_and_collide`/`place_block`/
`load_block_world`/etc., multiplayer_lan's `host_game`/`network_spawn`/etc.)
-- these were already broken before this fix, just invisible because the
whole containing event was dropped first. Confirmed via the audit tool
itself (`action-lost` 32 -> 36, matching exactly the handful of
now-reachable extension actions; `event-dropped` 44 -> 7).

## B4 -- Expressions in number slots become numbers

Two of the audit's five named examples (`if_collision`, `draw_sprite`) turned
out not to exist anywhere in this codebase at all, and a third
(`set_direction_speed`) is really `start_moving_direction`'s hand-written
`move_direction` block, whose DIRECTION is a fixed 4-way dropdown that can
never represent an arbitrary expression regardless of this fix (a B5-shaped
gap, not B4's). Only `jump_to_position` and `draw_health_bar` are real,
confirmed instances -- corrected in the audit doc rather than chasing the
other three.

The real bug, in `connectNumberBlock` (LOAD: events -> blocks): any
authored value that isn't a plain number (`"direction+90"`, `"self.x"`) got
`String()`-coerced straight into a `math_number` field, which Blockly's
`FieldNumber` can't parse -- it silently keeps the field's own default (0),
discarding the real value entirely.

**The fix needed a second half, found empirically, not just assumed:**
making `connectNumberBlock` fall back to a `text` block for a non-numeric
value does nothing on its own -- `Connection.connect()` refuses the
connection outright when the input is `.setCheck("Number")` and the `text`
block's output is `"String"` (confirmed with a throwaway script connecting
the two blocks directly and checking the return value: `false`, target
`null`). Fixed by dropping the type check on `move_jump_to`'s and
`draw_health_bar`'s X/Y inputs -- intentionally scoped to just these two
(real, confirmed) blocks, not swept across every `connectNumberBlock` call
site in the file.

**A second, independent bug bundled under the same B4 entry:**
`jump_to_position.relative` always saved `false` regardless of what was
authored -- the generator already read `block.getFieldValue('RELATIVE')`,
but `move_jump_to` never had a `RELATIVE` field at all, so the read always
returned `null`. Added the checkbox.

**A third bug, surfaced only once X/Y could carry an expression:**
`draw_health_bar` doesn't store `x2`/`y2` directly -- it derives them as
`x1 + width` / `y1 + 20` with a plain JS `+`. The moment `x1`/`y1` can be a
STRING, that `+` silently does concatenation (`"self.x" + 100` ->
`"self.x100"`, not a usable expression). Fixed with a new `addExpr(a, b)`
helper (`blockly_generators.js`): real arithmetic when both sides are
genuinely numbers (byte-identical to the old behaviour), otherwise an
expression string (`"(self.x) + (100)"`) `ActionExecutor._evaluate_expression`
can evaluate at runtime.

**Known, documented remaining limitation, NOT fixed:** `draw_health_bar`
models bar height as a hardcoded `+20`, not a real field -- a sample
authoring any other height (confirmed for real: `raycast_3`'s hud bar is
18px tall, `y2 - y1 = 18`) will never round-trip its `y2` exactly,
independent of this fix entirely (the block had no way to represent a
custom height before this fix either). `draw_rectangle` has the identical
`x1+width`/`y1+height` derivation and would hit the identical
string-concatenation bug if its own X/Y inputs ever lost their `"Number"`
check -- not done here (not a named B4 case, not confirmed by any sample),
so `draw_rectangle` is unaffected either way; worth checking together if
anyone ever extends expression support to it.

## B5 -- Parameters the hand-written blocks don't model are dropped

A grab-bag of ~12 named examples across a dozen actions, almost all with
the SAME root cause: `translations`, "applies to" `target`/`target_object`,
colours, `play_sound.loop`, `set_window_caption`'s six fields, etc. are
real keys in the authored JSON that the corresponding Blockly block simply
has no field for -- so they vanished the instant an object synced into
Blockly, even though nothing in the UI ever touched them.

Fixed with ONE generic mechanism, not twelve per-block patches, matching
the audit's own prescribed "fix direction" exactly: `createActionBlock`
(LOAD) stashes the full, untouched `params` dict onto the block as
`block.pygmExtraParams`; both places that build the final `{action,
parameters}` result on SAVE -- `generateActionCode`'s wrapper
(`blockly_generators.js`, for every hand-written block) and the dynamic
`custom_*` block generator's own from-scratch parameter builder
(`blockly_workspace.html`'s `registerCustomBlocks` monkeypatch, used for
every action with no hand-written block at all) -- now merge that stash
back in underneath whatever their own code explicitly produced. A field
the block DOES model (and the student may have changed) always wins; a
field it doesn't even know about passes through unchanged.

**The dynamic-block path was the one that actually mattered for most of
the twelve named examples.** `change_instance`, `set_window_caption`,
`jump_to_start`, `play_sound.loop`, `test_instance_count.count`, and
others have NO hand-written Blockly block at all -- they're auto-generated
from their Python `ActionType` definition the moment `registerCustomBlocks`
runs, and that generic builder only ever knew about the action's *declared*
`ActionParameter` list. `change_instance.target`/`target_object` is a
clean example of why: the action sets `supports_applies_to=True`
(`events/action_types.py`) but has no `target`/`target_object`
`ActionParameter` in its own list at all -- "applies to" is handled by a
wholly separate mechanism the generic UI builder never looked at.

Confirmed via the audit tool: `param-dropped` across the 98 bundled
samples went from 277 to **zero** in one commit -- every one of B5's named
examples, plus several more it didn't name (`test_variable`/`set_sprite`/
`set_variable`'s own target/target_object, `draw_lives.image`/`.relative`,
...).

**A second, independent bug found investigating the same bullet's own
`start_moving_direction.directions` example:** `"stop"` is a real sentinel
the runtime zeroes both speeds for, not "move at 0 degrees" (i.e. right).
`move_direction`'s generator fell through its degrees `switch` for `dir ===
'stop'` straight to `default: directionDegrees = 0` -- turning every
authored "stop" into "move right", a genuine behaviour change confirmed
across 12 samples. Fixed with an explicit early return for `'stop'`.
`move_direction`'s SPEED field got the identical B4 treatment (dropped its
`"Number"` check) for the same reason: `speed: "32/6"` was becoming the
default `4`.

**New finding, NOT fixed here (logged as B13 in the audit doc):**
`move_direction`'s DIRECTION field is a single-value dropdown, but
`start_moving_direction.directions` can legitimately be an ARRAY (a
patrolling monster picking a random direction from several). Confirmed
real across 7 samples (`maze_3`/`4`'s three monster types, `plateforme_3`,
`raycast_2`/`3`/`4`) -- every one collapses to a single hardcoded
direction (0/right) on round-trip. Needs a real UI redesign (a checkbox
grid, matching the pattern the action-list editor already uses for the
same parameter), not a quick fix -- scoped out.

**Known, NOT addressed:** the remaining `start_moving_direction.directions`
diffs after this fix (`'right' -> 0`, `'up' -> 90`, ...) are a
representation difference the audit tool's own comparator flags (a JSON
string vs. the equivalent float), not a behaviour change -- the runtime
accepts both forms identically. Not chased; same category as B1's own note
about the bundled samples storing parameters as strings.

## B10 -- set_sprite lost its frame and speed

The set_sprite block students actually get (blockly_workspace.html's
definition, which overrides blockly_blocks.js's) had a sprite dropdown and
nothing else: no frame/speed inputs, so an authored subimage/speed was lost
on every load (saved back as -1/-1, "don't change") and a student could not
set them at all; a saved "<self>" showed as "<self> (missing)". The block
now has SUBIMAGE/SPEED inputs (no Number type check, so a B4 expression
text block can connect), a real "<self> (current)" dropdown choice, and the
loader restores all three.
"""
import json

import pytest

from conftest import skip_without_pyside6
from editors.object_editor.blockly_roundtrip import diff_events

pytestmark = skip_without_pyside6

pytest.importorskip("PySide6.QtWebEngineWidgets")

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
PAGE = REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"

# (label, events) -- each round-tripped through loadEventsData -> generatePythonCode.
# Keep labels unique across B1/B2/future sections; they share one namespace.
CASES = {
    # --- B1 ---
    "gravity_zero_numeric": {"create": {"actions": [
        {"action": "set_gravity", "parameters": {"direction": 270, "gravity": 0}}]}},
    "gravity_zero_string": {"create": {"actions": [
        {"action": "set_gravity", "parameters": {"direction": "270", "gravity": "0"}}]}},
    "gravity_nonzero_control": {"create": {"actions": [
        {"action": "set_gravity", "parameters": {"direction": 270, "gravity": 0.8}}]}},
    "grid_size_zero": {"create": {"actions": [
        {"action": "snap_to_grid", "parameters": {"grid_size": 0}}]}},
    "move_direction_speed_zero": {"create": {"actions": [
        {"action": "start_moving_direction", "parameters": {"directions": 0, "speed": 0}}]}},
    "alpha_zero": {"create": {"actions": [
        {"action": "set_alpha", "parameters": {"alpha": 0}}]}},
    # --- B2 ---
    "if_condition": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "instance_count", "object_name": "obj_coin",
            "operator": "==", "value": "0",
            "then_actions": [{"action": "set_score", "parameters": {"value": "10", "relative": False}}],
            "else_actions": [{"action": "set_lives", "parameters": {"value": "1", "relative": True}}]}}]}},
    "if_condition_no_else": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "instance_count", "object_name": "obj_coin",
            "operator": "==", "value": "0",
            "then_actions": [{"action": "set_score", "parameters": {"value": "10", "relative": False}}],
            "else_actions": []}}]}},
    "test_variable": {"create": {"actions": [
        {"action": "test_variable", "parameters": {
            "variable": "score", "scope": "sel", "operation": "greater", "value": "5",
            "then_actions": [{"action": "set_score", "parameters": {"value": "1", "relative": True}}],
            "else_actions": [{"action": "set_lives", "parameters": {"value": "1", "relative": True}}]}}]}},
    "test_variable_global_scope": {"create": {"actions": [
        {"action": "test_variable", "parameters": {
            "variable": "wave", "scope": "global", "operation": "equal", "value": "3",
            "then_actions": [{"action": "restart_room", "parameters": {}}],
            "else_actions": []}}]}},
    "if_next_room_exists_with_else": {"create": {"actions": [
        {"action": "if_next_room_exists", "parameters": {
            "then_actions": [{"action": "next_room", "parameters": {}}],
            "else_actions": [{"action": "restart_room", "parameters": {}}]}}]}},
    "if_previous_room_exists_with_else": {"create": {"actions": [
        {"action": "if_previous_room_exists", "parameters": {
            "then_actions": [{"action": "previous_room", "parameters": {}}],
            "else_actions": [{"action": "restart_room", "parameters": {}}]}}]}},
    # --- B2 follow-up: if_condition's other 7 condition_types ---
    "if_condition_variable_compare": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "variable_compare", "variable": "hp",
            "operator": "<=", "value": "0",
            "then_actions": [{"action": "destroy_instance", "parameters": {"target": "self"}}],
            "else_actions": [{"action": "set_score", "parameters": {"value": "5", "relative": True}}]}}]}},
    "if_condition_position_check": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "position_check", "check_type": "y position",
            "operator": ">", "value": "600",
            "then_actions": [{"action": "destroy_instance", "parameters": {"target": "self"}}],
            "else_actions": []}}]}},
    "if_condition_collision_check": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "collision_check", "object": "obj_wall",
            "offset_x": "4", "offset_y": "0",
            "then_actions": [{"action": "stop_movement", "parameters": {}}],
            "else_actions": [{"action": "set_score", "parameters": {"value": "1", "relative": True}}]}}]}},
    "if_condition_key_pressed": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "key_pressed", "key": "space",
            "then_actions": [{"action": "start_moving_direction", "parameters": {"directions": 90, "speed": "4"}}],
            "else_actions": []}}]}},
    "if_condition_mouse_check": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "mouse_check", "check": "Left button pressed",
            "then_actions": [{"action": "set_score", "parameters": {"value": "1", "relative": True}}],
            "else_actions": []}}]}},
    "if_condition_random_chance": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "random_chance", "chance": "25",
            "then_actions": [{"action": "set_lives", "parameters": {"value": "1", "relative": True}}],
            "else_actions": [{"action": "set_lives", "parameters": {"value": "-1", "relative": True}}]}}]}},
    "if_condition_expression": {"create": {"actions": [
        {"action": "if_condition", "parameters": {
            "condition_type": "expression", "expression": "self.hp <= 0 and other.alive",
            "then_actions": [{"action": "destroy_instance", "parameters": {"target": "self"}}],
            "else_actions": [{"action": "set_score", "parameters": {"value": "0", "relative": True}}]}}]}},
    # --- B3: the twelve events routed through event_other ---
    "game_start_event": {"game_start": {"actions": [
        {"action": "set_lives", "parameters": {"value": 3, "relative": False}}]}},
    "game_end_event": {"game_end": {"actions": [
        {"action": "restart_room", "parameters": {}}]}},
    "room_start_event": {"room_start": {"actions": [
        {"action": "restart_room", "parameters": {}}]}},
    "room_end_event": {"room_end": {"actions": [
        {"action": "restart_room", "parameters": {}}]}},
    "begin_step_event": {"begin_step": {"actions": [
        {"action": "set_vspeed", "parameters": {"value": 0}}]}},
    "end_step_event": {"end_step": {"actions": [
        {"action": "set_hspeed", "parameters": {"value": 0}}]}},
    "draw_gui_event": {"draw_gui": {"actions": [
        {"action": "draw_score", "parameters": {"x": 10, "y": 10, "caption": "Score:"}}]}},
    "outside_room_event": {"outside_room": {"actions": [
        {"action": "destroy_instance", "parameters": {"target": "self"}}]}},
    "intersect_boundary_event": {"intersect_boundary": {"actions": [
        {"action": "destroy_instance", "parameters": {"target": "self"}}]}},
    "no_more_lives_event": {"no_more_lives": {"actions": [
        {"action": "restart_room", "parameters": {}}]}},
    "no_more_health_event": {"no_more_health": {"actions": [
        {"action": "set_health", "parameters": {"value": 100, "relative": False}}]}},
    "animation_end_event": {"animation_end": {"actions": [
        {"action": "destroy_instance", "parameters": {"target": "self"}}]}},
    # --- B3: keyboard press/release anykey/nokey/shift ---
    "keyboard_press_shift": {"keyboard_press": {"shift": {"actions": [
        {"action": "set_hspeed", "parameters": {"value": 1}}]}}},
    "keyboard_release_anykey": {"keyboard_release": {"anykey": {"actions": [
        {"action": "set_hspeed", "parameters": {"value": 0}}]}}},
    "keyboard_press_anykey": {"keyboard_press": {"anykey": {"actions": [
        {"action": "set_vspeed", "parameters": {"value": 1}}]}}},
    "keyboard_release_nokey": {"keyboard_release": {"nokey": {"actions": [
        {"action": "set_vspeed", "parameters": {"value": 0}}]}}},
    # Regression guard: the always-held variants (no KEY field at all) must
    # still produce the dedicated no-field block, not a KEY='anykey' one --
    # press/release must be checked first, but held-anykey/nokey must still
    # resolve to event_keyboard_anykey/nokey, not event_keyboard_held.
    "keyboard_held_anykey_control": {"keyboard": {"anykey": {"actions": [
        {"action": "set_hspeed", "parameters": {"value": 2}}]}}},
    "keyboard_held_nokey_control": {"keyboard": {"nokey": {"actions": [
        {"action": "set_hspeed", "parameters": {"value": 0}}]}}},
    # --- B4 ---
    "jump_to_position_expression_x": {"create": {"actions": [
        {"action": "jump_to_position", "parameters": {"x": "direction+90", "y": 5, "relative": False}}]}},
    "jump_to_position_relative_true": {"create": {"actions": [
        {"action": "jump_to_position", "parameters": {"x": 5, "y": 10, "relative": True}}]}},
    "jump_to_position_relative_false": {"create": {"actions": [
        {"action": "jump_to_position", "parameters": {"x": 5, "y": 10, "relative": False}}]}},
    "jump_to_position_numeric_control": {"create": {"actions": [
        {"action": "jump_to_position", "parameters": {"x": 100, "y": 200, "relative": False}}]}},
    "draw_health_bar_expression_x1": {"create": {"actions": [
        {"action": "draw_health_bar", "parameters": {"x1": "self.x", "y1": 10, "x2": 110, "y2": 30}}]}},
    "draw_health_bar_numeric_control": {"create": {"actions": [
        {"action": "draw_health_bar", "parameters": {"x1": 10, "y1": 10, "x2": 110, "y2": 30}}]}},
    # --- B5 ---
    "show_message_with_translations": {"create": {"actions": [
        {"action": "show_message", "parameters": {
            "message": "Hello!", "message_translations": {"fr": "Bonjour !"}}}]}},
    "move_direction_stop": {"create": {"actions": [
        {"action": "start_moving_direction", "parameters": {"directions": "stop", "speed": "8"}}]}},
    "move_direction_speed_expression": {"create": {"actions": [
        {"action": "start_moving_direction", "parameters": {"directions": "right", "speed": "32/6"}}]}},
    "move_direction_numeric_control": {"create": {"actions": [
        {"action": "start_moving_direction", "parameters": {"directions": "up", "speed": 4}}]}},
    # Dynamic (custom_*) block: change_instance has supports_applies_to=True
    # (events/action_types.py) but NO target/target_object ActionParameter
    # in its own list -- a real example of the generic-UI-builder gap B5's
    # dynamic-block merge fixes.
    "change_instance_applies_to": {"create": {"actions": [
        {"action": "change_instance", "parameters": {
            "object": "obj_enemy", "perform_events": True,
            "target": "other", "target_object": "obj_trigger"}}]}},
    # B10 -- set_sprite frame/speed/<self>
    "set_sprite_frame_speed": {"create": {"actions": [
        {"action": "set_sprite", "parameters": {"sprite": "spr_b", "subimage": "2", "speed": "0.5"}}]}},
    "set_sprite_self_expression": {"create": {"actions": [
        {"action": "set_sprite", "parameters": {"sprite": "<self>", "subimage": 0, "speed": "image_speed*2"}}]}},
    "set_sprite_defaults": {"create": {"actions": [
        {"action": "set_sprite", "parameters": {"sprite": "spr_a"}}]}},
}

# Minimal real-shaped ActionType definitions for the one dynamic (custom_*)
# block case above -- mirrors events/action_types.py's own change_instance
# entry exactly (object + perform_events only; no target/target_object).
DYNAMIC_BLOCK_DEFS = [
    {"name": "change_instance", "display_name": "Change Instance",
     "description": "Transform into different object type", "category": "Instance",
     "icon": "", "parameters": [
         {"name": "object", "display_name": "Change Into", "param_type": "object", "default_value": ""},
         {"name": "perform_events", "display_name": "Perform Events", "param_type": "boolean", "default_value": True},
     ]},
]


@pytest.fixture(scope="module")
def round_tripped():
    """One QWebEngineView, one JS call, every CASES entry loaded and
    regenerated -- see the module docstring for why this isn't one
    QWebEngineView per test (or per test file)."""
    from PySide6.QtCore import QUrl, QTimer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWebEngineWidgets import QWebEngineView

    app = QApplication.instance() or QApplication([])
    view = QWebEngineView()
    result = {}

    # Asset dropdowns only accept names the project actually has; the IDE
    # pushes them (BlocklyWidget.push_asset_lists), so the fixture does too.
    js = """(function(cases, dynamicDefs){
        registerCustomBlocks(dynamicDefs);
        window.blocklyApi.setAssetLists({objects: [], sprites: ['spr_a', 'spr_b'], sounds: [], rooms: []});
        var out = {};
        for (var k in cases) {
            loadEventsData(cases[k]);
            out[k] = JSON.parse(generatePythonCode());
        }
        return JSON.stringify(out);
    })(%s, %s)""" % (json.dumps(CASES), json.dumps(DYNAMIC_BLOCK_DEFS))

    def loaded(_ok):
        view.page().runJavaScript(js, done)

    def done(r):
        result["after"] = json.loads(r) if r else None
        app.quit()

    view.loadFinished.connect(loaded)
    view.load(QUrl.fromLocalFile(str(PAGE)))
    QTimer.singleShot(20000, app.quit)
    app.exec()
    if result.get("after") is None:
        pytest.fail("Blockly page did not finish (timeout or unparseable result)")
    return result["after"]


def _action(round_tripped, label):
    actions = round_tripped[label]["create"]["actions"]
    assert len(actions) == 1, f"{label}: expected 1 action, got {actions!r}"
    return actions[0]


def _params(round_tripped, label):
    return _action(round_tripped, label)["parameters"]


def _event_actions(round_tripped, label, event_name):
    """The flat ``{event_name: {"actions": [...]}}`` shape the twelve
    event_other-routed events use."""
    events = round_tripped[label]
    assert event_name in events, (
        f"{label}: event {event_name!r} was dropped entirely; got {list(events)!r}")
    return events[event_name]["actions"]


def _nested_key_actions(round_tripped, label, event_name, key):
    """The nested ``{event_name: {key: {"actions": [...]}}}`` shape keyboard
    press/release/held events use."""
    events = round_tripped[label]
    assert event_name in events, (
        f"{label}: event {event_name!r} was dropped entirely; got {list(events)!r}")
    sub = events[event_name]
    assert key in sub, (
        f"{label}: key {key!r} under {event_name!r} was dropped; got {list(sub)!r}")
    return sub[key]["actions"]


class TestB1ZeroValuesSurviveTheRoundTrip:
    def test_gravity_zero_as_a_json_number_is_not_replaced_by_the_default(self, round_tripped):
        gravity = _params(round_tripped, "gravity_zero_numeric")["gravity"]
        assert float(gravity) == 0.0, f"gravity 0 (number) became {gravity!r} (default is 0.5)"

    def test_gravity_zero_as_a_json_string_is_not_replaced_by_the_default(self, round_tripped):
        gravity = _params(round_tripped, "gravity_zero_string")["gravity"]
        assert float(gravity) == 0.0, f"gravity '0' (string) became {gravity!r} (default is 0.5)"

    def test_a_genuinely_nonzero_value_still_round_trips(self, round_tripped):
        """Guard against a fix that breaks the common case while fixing 0."""
        gravity = _params(round_tripped, "gravity_nonzero_control")["gravity"]
        assert float(gravity) == 0.8

    def test_grid_size_zero_is_not_replaced_by_the_default(self, round_tripped):
        grid_size = _params(round_tripped, "grid_size_zero")["grid_size"]
        assert float(grid_size) == 0.0, f"grid_size 0 became {grid_size!r} (default is 32)"

    def test_move_direction_speed_zero_is_not_replaced_by_the_default(self, round_tripped):
        speed = _params(round_tripped, "move_direction_speed_zero")["speed"]
        assert float(speed) == 0.0, f"speed 0 became {speed!r} (default is 4)"

    def test_alpha_zero_fully_transparent_is_not_replaced_by_the_default(self, round_tripped):
        """alpha=0 (fully transparent) is a real, meaningful value, not a
        placeholder -- the default is opaque (1.0)."""
        alpha = _params(round_tripped, "alpha_zero")["alpha"]
        assert float(alpha) == 0.0, f"alpha 0 became {alpha!r} (default is 1.0)"


class TestB2ConditionsPreserveNestedActions:
    def test_if_condition_preserves_condition_then_and_else(self, round_tripped):
        params = _params(round_tripped, "if_condition")
        assert params["object_name"] == "obj_coin"
        assert params["operator"] == "=="
        assert float(params["value"]) == 0.0
        assert params["then_actions"] == [{"action": "set_score", "parameters": {"value": 10, "relative": False}}]
        assert params["else_actions"] == [{"action": "set_lives", "parameters": {"value": 1, "relative": True}}]

    def test_if_condition_with_no_else_leaves_it_empty_not_lost(self, round_tripped):
        params = _params(round_tripped, "if_condition_no_else")
        assert params["else_actions"] == []
        assert len(params["then_actions"]) == 1

    def test_test_variable_preserves_variable_operation_then_and_else(self, round_tripped):
        params = _params(round_tripped, "test_variable")
        assert params["variable"] == "score"
        assert params["scope"] == "sel"
        assert params["operation"] == "greater"
        assert float(params["value"]) == 5.0
        assert params["then_actions"] == [{"action": "set_score", "parameters": {"value": 1, "relative": True}}]
        assert params["else_actions"] == [{"action": "set_lives", "parameters": {"value": 1, "relative": True}}]

    def test_test_variable_global_scope_prefix_round_trips(self, round_tripped):
        """The VARIABLE field reconstructs the 'global.' prefix
        parseScopedVariable strips on save -- a scope mismatch here would
        silently redirect the comparison to the wrong variable."""
        params = _params(round_tripped, "test_variable_global_scope")
        assert params["variable"] == "wave"
        assert params["scope"] == "global"

    def test_if_next_room_exists_preserves_else_actions(self, round_tripped):
        """The runtime genuinely executes else_actions here
        (action_room.py's _dispatch_room_test) -- this isn't cosmetic."""
        params = _params(round_tripped, "if_next_room_exists_with_else")
        assert params["then_actions"] == [{"action": "next_room", "parameters": {}}]
        assert params["else_actions"] == [{"action": "restart_room", "parameters": {}}]

    def test_if_previous_room_exists_preserves_else_actions(self, round_tripped):
        params = _params(round_tripped, "if_previous_room_exists_with_else")
        assert params["then_actions"] == [{"action": "previous_room", "parameters": {}}]
        assert params["else_actions"] == [{"action": "restart_room", "parameters": {}}]


class TestB2ConditionTypesBeyondInstanceCount:
    """if_condition's other 7 condition_types -- see the module docstring's
    'B2 follow-up' section. Each case is checked with diff_events against
    its own CASES entry (not a hand-rolled equality check), so a benign
    representational difference ("10" vs 10) can't false-positive, the
    same discipline the audit tool itself uses."""

    @pytest.mark.parametrize("label", [
        "if_condition_variable_compare",
        "if_condition_position_check",
        "if_condition_collision_check",
        "if_condition_key_pressed",
        "if_condition_mouse_check",
        "if_condition_random_chance",
        "if_condition_expression",
    ])
    def test_condition_type_and_nested_actions_round_trip_clean(self, round_tripped, label):
        before = CASES[label]
        after = round_tripped[label]
        issues = diff_events(before, after)
        assert not issues, f"{label}: {issues}"

    def test_condition_type_field_itself_is_preserved_not_reset_to_instance_count(self, round_tripped):
        """The regression this follow-up fixes: before it, EVERY non-
        instance_count condition_type silently reverted to instance_count
        on load (B2's own documented 'remaining gap')."""
        for label in ["if_condition_variable_compare", "if_condition_position_check",
                      "if_condition_collision_check", "if_condition_key_pressed",
                      "if_condition_mouse_check", "if_condition_random_chance",
                      "if_condition_expression"]:
            expected_type = CASES[label]["create"]["actions"][0]["parameters"]["condition_type"]
            actual_type = _params(round_tripped, label)["condition_type"]
            assert actual_type == expected_type, f"{label}: condition_type reverted to {actual_type!r}"


class TestB3EventsWithNoBlockRoundTrip:
    """The twelve events now routed through the new event_other block."""

    @pytest.mark.parametrize("label,event_name", [
        ("game_start_event", "game_start"),
        ("game_end_event", "game_end"),
        ("room_start_event", "room_start"),
        ("room_end_event", "room_end"),
        ("begin_step_event", "begin_step"),
        ("end_step_event", "end_step"),
        ("draw_gui_event", "draw_gui"),
        ("outside_room_event", "outside_room"),
        ("intersect_boundary_event", "intersect_boundary"),
        ("no_more_lives_event", "no_more_lives"),
        ("no_more_health_event", "no_more_health"),
        ("animation_end_event", "animation_end"),
    ])
    def test_event_survives_the_round_trip(self, round_tripped, label, event_name):
        actions = _event_actions(round_tripped, label, event_name)
        assert len(actions) == 1, f"{label}: expected 1 action, got {actions!r}"


class TestB3KeyboardAnykeyNokeyShift:
    def test_press_shift_is_not_reset_to_the_dropdowns_first_option(self, round_tripped):
        actions = _nested_key_actions(round_tripped, "keyboard_press_shift", "keyboard_press", "shift")
        assert len(actions) == 1

    def test_release_anykey_is_not_collapsed_into_the_held_block(self, round_tripped):
        """The actual B3 bug: keyboard_release_anykey previously matched the
        bare 'anykey' check before the '_release_' check, silently becoming
        the always-held event_keyboard_anykey block (which has no KEY field,
        so it can't distinguish press/release/held at all)."""
        actions = _nested_key_actions(round_tripped, "keyboard_release_anykey", "keyboard_release", "anykey")
        assert len(actions) == 1

    def test_press_anykey_round_trips(self, round_tripped):
        actions = _nested_key_actions(round_tripped, "keyboard_press_anykey", "keyboard_press", "anykey")
        assert len(actions) == 1

    def test_release_nokey_round_trips(self, round_tripped):
        actions = _nested_key_actions(round_tripped, "keyboard_release_nokey", "keyboard_release", "nokey")
        assert len(actions) == 1

    def test_held_anykey_control_still_uses_the_dedicated_no_field_block(self, round_tripped):
        """Regression guard for the dispatch reorder: a bare (always-held)
        anykey/nokey event must keep resolving to event_keyboard_anykey/
        nokey, not get swept into event_keyboard_held by the reorder."""
        actions = _nested_key_actions(round_tripped, "keyboard_held_anykey_control", "keyboard", "anykey")
        assert len(actions) == 1

    def test_held_nokey_control_still_uses_the_dedicated_no_field_block(self, round_tripped):
        actions = _nested_key_actions(round_tripped, "keyboard_held_nokey_control", "keyboard", "nokey")
        assert len(actions) == 1


class TestB4ExpressionsInNumberSlots:
    def test_jump_to_position_x_expression_survives_verbatim(self, round_tripped):
        params = _params(round_tripped, "jump_to_position_expression_x")
        assert params["x"] == "direction+90", f"x became {params['x']!r}, expected the expression verbatim"
        assert float(params["y"]) == 5.0, "a genuinely numeric sibling field must stay numeric"

    def test_jump_to_position_relative_true_round_trips(self, round_tripped):
        """The actual second B4 bug: the generator already read a RELATIVE
        field that never existed on the block, so every save emitted False
        regardless of what was authored."""
        params = _params(round_tripped, "jump_to_position_relative_true")
        assert params["relative"] is True

    def test_jump_to_position_relative_false_round_trips(self, round_tripped):
        params = _params(round_tripped, "jump_to_position_relative_false")
        assert params["relative"] is False

    def test_jump_to_position_plain_numbers_are_not_coerced_to_text(self, round_tripped):
        """Regression guard: the connectNumberBlock fix must not turn an
        ordinary numeric x/y into a text block just because it CAN now hold
        one -- the common case stays a real number."""
        params = _params(round_tripped, "jump_to_position_numeric_control")
        assert params["x"] == 100 and not isinstance(params["x"], str)
        assert params["y"] == 200 and not isinstance(params["y"], str)

    def test_draw_health_bar_x1_expression_survives_and_x2_becomes_a_real_expression(self, round_tripped):
        """The third B4 bug: draw_health_bar derives x2 as x1 + width with a
        plain JS '+' -- once x1 can be a string, that silently did STRING
        CONCATENATION ("self.x" + 100 -> "self.x100", not a usable
        expression) instead of building an evaluable expression string."""
        params = _params(round_tripped, "draw_health_bar_expression_x1")
        assert params["x1"] == "self.x"
        assert params["x2"] == "(self.x) + (100)"
        assert float(params["y1"]) == 10.0
        assert float(params["y2"]) == 30.0

    def test_draw_health_bar_plain_numbers_still_compute_x2_arithmetically(self, round_tripped):
        """Regression guard: when both operands are genuinely numeric, x2/y2
        must stay real numbers (the exact pre-fix behaviour), not an
        expression string like "(10) + (100)"."""
        params = _params(round_tripped, "draw_health_bar_numeric_control")
        assert params["x1"] == 10 and not isinstance(params["x1"], str)
        assert params["x2"] == 110 and not isinstance(params["x2"], str)
        assert params["y2"] == 30 and not isinstance(params["y2"], str)


class TestB5UnmodelledParametersSurviveTheRoundTrip:
    def test_translations_survive_on_a_hand_written_block(self, round_tripped):
        """show_message is hand-written (the 'output_message' block) and
        has no field for message_translations at all -- proves the first
        half of the generic merge (generateActionCode's own wrapper)."""
        params = _params(round_tripped, "show_message_with_translations")
        assert params["message"] == "Hello!"
        assert params["message_translations"] == {"fr": "Bonjour !"}

    def test_applies_to_target_survives_on_a_dynamic_custom_block(self, round_tripped):
        """change_instance has NO hand-written block at all -- it's
        auto-generated by registerCustomBlocks from its ActionType
        definition, which (matching the real events/action_types.py entry)
        declares only object/perform_events, nothing about target/
        target_object. Proves the SECOND half of the generic merge (the
        registerCustomBlocks monkeypatch's own generic parameter builder),
        which is the one that actually mattered for most of B5's named
        examples (change_instance, set_window_caption, jump_to_start, ...)."""
        params = _params(round_tripped, "change_instance_applies_to")
        assert params["object"] == "obj_enemy"
        assert params["perform_events"] is True
        assert params["target"] == "other"
        assert params["target_object"] == "obj_trigger"

    def test_move_direction_stop_is_not_turned_into_move_right(self, round_tripped):
        """The actual B5 bug: 'stop' is a real sentinel the runtime zeroes
        both speeds for -- falling through the degrees switch to its
        default silently turned every authored 'stop' into 'move right'."""
        params = _params(round_tripped, "move_direction_stop")
        assert params["directions"] == "stop"

    def test_move_direction_speed_expression_survives(self, round_tripped):
        params = _params(round_tripped, "move_direction_speed_expression")
        assert params["speed"] == "32/6"

    def test_move_direction_numeric_control_is_unaffected(self, round_tripped):
        """Regression guard: a plain numeric direction/speed must still
        round-trip as numbers, unaffected by the 'stop' special-case or the
        SPEED input's dropped type check."""
        params = _params(round_tripped, "move_direction_numeric_control")
        assert params["directions"] == 90  # 'up'
        assert params["speed"] == 4 and not isinstance(params["speed"], str)


class TestB10SetSpriteFrameAndSpeed:
    def test_frame_and_speed_survive(self, round_tripped):
        params = _params(round_tripped, "set_sprite_frame_speed")
        assert params["sprite"] == "spr_b"
        assert params["subimage"] == 2
        assert params["speed"] == 0.5

    def test_self_and_zero_frame_and_expression_speed_survive(self, round_tripped):
        params = _params(round_tripped, "set_sprite_self_expression")
        assert params["sprite"] == "<self>"
        assert params["subimage"] == 0
        assert params["speed"] == "image_speed*2"

    def test_missing_frame_and_speed_default_to_dont_change(self, round_tripped):
        params = _params(round_tripped, "set_sprite_defaults")
        assert params["subimage"] == -1 and params["speed"] == -1

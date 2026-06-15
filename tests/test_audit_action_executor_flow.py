#!/usr/bin/env python3
"""Regression tests for the 2026-06-11 audit findings in
``runtime/action_executor.py``: M43, M44, M46, M47, L28, L29 (and a guard for
the already-fixed M45).

These exercise pure executor logic; no Qt widgets are needed. The create-instance
findings (M46/M47/L28/L29) use the real ``GameInstance``/``resolve_parent_inheritance``
from ``runtime.game_runner`` (pygame is available on the test box) with a mock
game runner.
"""

import os
import math

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import import_module_directly

_aem = import_module_directly("runtime/action_executor.py")
ActionExecutor = _aem.ActionExecutor
_ExitEvent = _aem._ExitEvent


# --------------------------------------------------------------------------
# Mocks (mirroring tests/test_action_executor.py)
# --------------------------------------------------------------------------
class MockInstance:
    def __init__(self, object_name="test_object"):
        self.object_name = object_name
        self.x = 100.0
        self.y = 100.0
        self.xstart = 100.0
        self.ystart = 100.0
        self.hspeed = 0.0
        self.vspeed = 0.0
        self.speed = 0.0
        self.alarm = [-1] * 12
        self.image_index = 0.0
        self.image_speed = 1.0
        self.to_destroy = False
        self.keys_pressed = set()
        self.object_data = {'events': {}}
        self._cached_width = 32
        self._cached_height = 32
        # marker for tests
        self.log = []


class MockRoom:
    def __init__(self):
        self.name = "test_room"
        self.width = 640
        self.height = 480
        self.instances = []
        self._depth_dirty = False

    def _add_to_grid(self, instance):
        pass

    def invalidate_collision_listened_types(self):
        pass


class MockGameRunner:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.health = 100.0
        self.global_variables = {}
        self.current_room = MockRoom()
        self.project_data = {'assets': {'objects': {}}}
        self.sprites = {}
        self._room_list = ["room1", "room2"]

    def get_room_list(self):
        return self._room_list

    @property
    def _objects_data(self):
        return self.project_data.get('assets', {}).get('objects', {})


# ==========================================================================
# M43 — exit_event must abort the WHOLE event from any nesting level
# ==========================================================================
class TestM43ExitEventNesting:
    def _executor_with_counter(self):
        """Executor with a custom 'mark' action that appends to instance.log."""
        ex = ActionExecutor(game_runner=MockGameRunner())

        def mark(instance, params):
            instance.log.append(params.get("tag"))

        ex.register_custom_action("mark", mark)
        return ex

    def test_exit_inside_if_condition_then_branch_aborts_outer(self):
        ex = self._executor_with_counter()
        inst = MockInstance()
        # if (always true) { mark A; exit_event; mark B } then mark C
        actions = [
            {"action": "if_condition", "parameters": {
                "condition_type": "expression",
                "expression": "1",
                "then_actions": [
                    {"action": "mark", "parameters": {"tag": "A"}},
                    {"action": "exit_event", "parameters": {}},
                    {"action": "mark", "parameters": {"tag": "B"}},
                ],
            }},
            {"action": "mark", "parameters": {"tag": "C"}},
        ]
        ex.execute_action_list(inst, actions)
        # A ran; B (after exit, same branch) and C (the OUTER action) must NOT.
        assert inst.log == ["A"], inst.log

    def test_exit_inside_repeat_block_aborts_all_iterations_and_outer(self):
        ex = self._executor_with_counter()
        inst = MockInstance()
        # repeat 5 { mark X; exit_event } then mark AFTER
        actions = [
            {"action": "repeat", "parameters": {"times": 5}},
            {"action": "start_block"},
            {"action": "mark", "parameters": {"tag": "X"}},
            {"action": "exit_event", "parameters": {}},
            {"action": "end_block"},
            {"action": "mark", "parameters": {"tag": "AFTER"}},
        ]
        ex.execute_action_list(inst, actions)
        # Only the first iteration's X ran; no further iterations, no AFTER.
        assert inst.log == ["X"], inst.log

    def test_exit_inside_generic_conditional_then_branch_aborts_outer(self):
        """test_variable-style conditional with nested then_actions."""
        ex = self._executor_with_counter()
        inst = MockInstance()
        inst.object_data = {'events': {}}
        inst.myvar = 5
        actions = [
            {"action": "test_variable", "parameters": {
                "variable": "myvar", "value": "5", "operator": "==",
                "scope": "self",
                "then_actions": [
                    {"action": "mark", "parameters": {"tag": "A"}},
                    {"action": "exit_event", "parameters": {}},
                ],
            }},
            {"action": "mark", "parameters": {"tag": "OUTER"}},
        ]
        ex.execute_action_list(inst, actions)
        assert "OUTER" not in inst.log, inst.log
        assert "A" in inst.log, inst.log

    def test_exit_event_still_caught_at_top_level(self):
        """A top-level exit_event must not escape execute_action_list."""
        ex = self._executor_with_counter()
        inst = MockInstance()
        actions = [
            {"action": "mark", "parameters": {"tag": "A"}},
            {"action": "exit_event", "parameters": {}},
            {"action": "mark", "parameters": {"tag": "B"}},
        ]
        # Must not raise _ExitEvent
        ex.execute_action_list(inst, actions)
        assert inst.log == ["A"], inst.log


# ==========================================================================
# M44 — Blockly Thymio sub_actions must run; false condition must not skip sibling
# ==========================================================================
class TestM44ThymioSubActions:
    def _executor(self):
        ex = ActionExecutor(game_runner=MockGameRunner())

        def mark(instance, params):
            instance.log.append(params.get("tag"))

        # A condition handler we control directly via a flag.
        def cond_true(instance, params):
            return True

        def cond_false(instance, params):
            return False

        ex.register_custom_action("mark", mark)
        ex.register_custom_action("cond_true", cond_true)
        ex.register_custom_action("cond_false", cond_false)
        return ex

    def test_sub_actions_run_when_condition_true(self):
        ex = self._executor()
        inst = MockInstance()
        actions = [
            {"action": "cond_true", "parameters": {},
             "sub_actions": [{"action": "mark", "parameters": {"tag": "LED"}}]},
        ]
        ex.execute_action_list(inst, actions)
        assert inst.log == ["LED"], inst.log

    def test_sub_actions_in_parameters_also_run(self):
        """The load path can copy sub_actions into parameters."""
        ex = self._executor()
        inst = MockInstance()
        actions = [
            {"action": "cond_true", "parameters": {
                "sub_actions": [{"action": "mark", "parameters": {"tag": "LED"}}]}},
        ]
        ex.execute_action_list(inst, actions)
        assert inst.log == ["LED"], inst.log

    def test_false_condition_with_sub_actions_does_not_skip_sibling(self):
        ex = self._executor()
        inst = MockInstance()
        actions = [
            {"action": "cond_false", "parameters": {},
             "sub_actions": [{"action": "mark", "parameters": {"tag": "INNER"}}]},
            {"action": "mark", "parameters": {"tag": "SIBLING"}},
        ]
        ex.execute_action_list(inst, actions)
        # INNER must NOT run (condition false), but SIBLING (the unrelated next
        # action) MUST run — it must not be GM80-skip_next'd away.
        assert inst.log == ["SIBLING"], inst.log


# ==========================================================================
# M45 — execute_code namespace must bind 'self' (already fixed, guard it)
# ==========================================================================
class TestM45ExecuteCodeSelf:
    def test_self_is_bound_in_execute_code(self):
        ex = ActionExecutor(game_runner=MockGameRunner())
        inst = MockInstance()
        inst.coins = 0
        ex.execute_execute_code_action(inst, {"code": "self.coins = self.coins + 1"})
        assert inst.coins == 1


# ==========================================================================
# Create-instance findings use the real GameInstance + inheritance resolver.
# ==========================================================================
import pygame  # noqa: E402
from runtime.game_runner import GameInstance  # noqa: E402


def _make_runner_with_objects(objects):
    runner = MockGameRunner()
    runner.project_data = {'assets': {'objects': objects}}
    return runner


class TestM46DepthDirty:
    def test_create_random_instance_marks_depth_dirty(self):
        objects = {"obj_bullet": {"events": {}, "sprite": ""}}
        runner = _make_runner_with_objects(objects)
        runner.current_room._depth_dirty = False
        ex = ActionExecutor(game_runner=runner)
        caller = MockInstance("obj_spawner")
        ex.execute_create_random_instance_action(
            caller, {"object1": "obj_bullet", "x": "10", "y": "20"})
        assert len(runner.current_room.instances) == 1
        assert runner.current_room._depth_dirty is True

    def test_create_moving_instance_marks_depth_dirty(self):
        objects = {"obj_bullet": {"events": {}, "sprite": ""}}
        runner = _make_runner_with_objects(objects)
        runner.current_room._depth_dirty = False
        ex = ActionExecutor(game_runner=runner)
        caller = MockInstance("obj_spawner")
        ex.execute_create_moving_instance_action(
            caller, {"object": "obj_bullet", "x": "10", "y": "20",
                     "speed": "4", "direction": "0"})
        assert len(runner.current_room.instances) == 1
        assert runner.current_room._depth_dirty is True


class TestM47CreateMovingInheritance:
    def test_create_moving_inherits_parent_events(self):
        objects = {
            "obj_projectile": {"events": {
                "collision_with_obj_wall": {"actions": [{"action": "destroy_instance"}]}}},
            "obj_fireball": {"parent": "obj_projectile", "sprite": "", "events": {}},
        }
        runner = _make_runner_with_objects(objects)
        ex = ActionExecutor(game_runner=runner)
        caller = MockInstance("obj_spawner")
        ex.execute_create_moving_instance_action(
            caller, {"object": "obj_fireball", "x": "0", "y": "0",
                     "speed": "0", "direction": "0"})
        new_inst = runner.current_room.instances[-1]
        # The spawned child must have inherited the parent's collision event.
        assert "collision_with_obj_wall" in new_inst.object_data.get("events", {})


class TestL28InheritedCreateEvent:
    def test_create_instance_fires_inherited_create_event(self):
        # Parent defines create; child only sets a sprite.
        objects = {
            "obj_base": {"events": {
                "create": {"actions": [{"action": "set_variable", "parameters": {
                    "variable": "spawned", "value": "1", "scope": "self"}}]}}},
            "obj_child": {"parent": "obj_base", "sprite": "", "events": {}},
        }
        runner = _make_runner_with_objects(objects)
        ex = ActionExecutor(game_runner=runner)
        caller = MockInstance("obj_spawner")
        # Not inside an event (_event_depth == 0) -> create event runs immediately.
        ex.execute_create_instance_action(
            caller, {"object": "obj_child", "x": "0", "y": "0"})
        new_inst = runner.current_room.instances[-1]
        assert getattr(new_inst, "spawned", None) == 1


class TestL29CollisionContextCleared:
    def test_collision_context_cleared_before_deferred_create(self):
        """A create event deferred during a collision must not see the colliding
        pair's captured speeds — the context must be cleared first."""
        seen = {}

        objects = {
            "obj_explosion": {"sprite": "", "events": {
                "create": {"actions": [{"action": "record_speeds"}]}}},
        }
        runner = _make_runner_with_objects(objects)
        ex = ActionExecutor(game_runner=runner)

        def record_speeds(instance, params):
            # Snapshot the collision context visible during the deferred create.
            seen["collision_speeds"] = dict(getattr(ex, "_collision_speeds", {}))
            seen["collision_other"] = getattr(ex, "_collision_other", None)

        ex.register_custom_action("record_speeds", record_speeds)

        player = MockInstance("obj_player")
        monster = MockInstance("obj_monster")

        # Collision event on the player that spawns an explosion (its create is
        # deferred because _event_depth > 0 during the collision).
        events = {"collision_with_obj_monster": {"actions": [
            {"action": "create_instance", "parameters": {
                "object": "obj_explosion", "x": "0", "y": "0"}},
        ]}}
        collision_speeds = {"self_hspeed": 4.0, "self_vspeed": 0.0,
                            "other_hspeed": -2.0, "other_vspeed": 0.0}
        ex.execute_collision_event(
            player, "collision_with_obj_monster", events, monster,
            collision_speeds=collision_speeds)

        # The deferred create event ran (record_speeds fired)...
        assert "collision_speeds" in seen
        # ...and saw a CLEARED collision context, not the player/monster speeds.
        assert seen["collision_speeds"] == {}, seen["collision_speeds"]
        assert seen["collision_other"] is None

    def test_collision_context_cleared_after_event(self):
        ex = ActionExecutor(game_runner=_make_runner_with_objects({}))
        player = MockInstance("p")
        monster = MockInstance("m")
        events = {"collision_with_m": {"actions": [
            {"action": "set_hspeed", "parameters": {"hspeed": "1"}}]}}
        ex.execute_collision_event(
            player, "collision_with_m", events, monster,
            collision_speeds={"self_hspeed": 9.0})
        assert ex._collision_speeds == {}
        assert ex._collision_other is None

"""Regression tests for runtime L28/L29/L30/L31."""

import sys
from pathlib import Path

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor

sys.path.insert(0, str(Path(__file__).parent))

pygame_available = __import__("importlib").util.find_spec("pygame") is not None


# --------------------------------------------------------------------------
# L31 — Thymio conditional handlers return False (not None) on non-Thymio
# --------------------------------------------------------------------------

class TestThymioGuard:
    def _executor(self):
        from runtime.thymio_action_handlers import register_thymio_actions
        ex = ActionExecutor(game_runner=None)
        if "thymio_if_proximity" not in ex.action_handlers:
            register_thymio_actions(ex)
        return ex

    def test_conditional_returns_false_without_simulator(self):
        ex = self._executor()
        handler = ex.action_handlers["thymio_if_proximity"]

        class _Inst:
            thymio_simulator = None  # non-Thymio instance

        result = handler(_Inst(), {"sensor_index": 2, "threshold": 2000})
        assert result is False  # not None

    def test_command_no_ops_without_simulator(self):
        ex = self._executor()
        handler = ex.action_handlers["thymio_set_motor_speed"]

        class _Inst:
            thymio_simulator = None

        # Must not raise; returns None (a no-op command).
        assert handler(_Inst(), {"left_speed": 100, "right_speed": 100}) is None


# --------------------------------------------------------------------------
# L28 / L30 need pygame (GameRunner / GameInstance)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not pygame_available, reason="needs pygame")
class TestInheritedCreateEvent:  # L28
    def _setup(self):
        from test_action_executor import MockGameRunner, MockRoom
        runner = MockGameRunner()
        runner.current_room = MockRoom()
        return runner

    def test_create_instance_fires_inherited_create(self):
        runner = self._setup()
        runner.project_data = {"assets": {"objects": {
            "obj_base": {"name": "obj_base",
                         "events": {"create": {"actions": [
                             {"action": "mark", "parameters": {}}]}}},
            "obj_child": {"name": "obj_child", "parent": "obj_base"},
        }}}
        ex = ActionExecutor(game_runner=runner)
        ex.action_handlers["mark"] = lambda inst, p: setattr(inst, "_created", True)
        ex.execute_create_instance_action(_Dummy(ex),
                                          {"object": "obj_child", "x": 0, "y": 0})
        new_inst = runner.current_room.instances[-1]
        assert getattr(new_inst, "_created", False) is True


class _Dummy:
    """Minimal source instance for create_instance (_parse_value needs x/y)."""
    def __init__(self, ex):
        self.x = 0
        self.y = 0
        self.action_executor = ex


@pytest.mark.skipif(not pygame_available, reason="needs pygame")
class TestCollisionContextLeak:  # L29
    def test_deferred_create_does_not_see_collision_speeds(self):
        from test_action_executor import MockGameRunner, MockRoom, MockInstance
        runner = MockGameRunner()
        runner.current_room = MockRoom()
        runner.project_data = {"assets": {"objects": {
            "obj_spawn": {"name": "obj_spawn",
                          "events": {"create": {"actions": [
                              {"action": "rec", "parameters": {}}]}}},
        }}}
        ex = ActionExecutor(game_runner=runner)
        captured = {}

        def _rec(inst, p):
            # Read hspeed the way an authored create expression would.
            captured["hspeed"] = ex._parse_value("hspeed", inst)
        ex.action_handlers["rec"] = _rec

        # The colliding instance's collision handler spawns obj_spawn.
        collider = MockInstance("obj_player")
        events = {"collision_with_obj_wall": {"actions": [
            {"action": "create_instance",
             "parameters": {"object": "obj_spawn", "x": 0, "y": 0}}]}}
        collider.object_data = {"events": events}
        other = MockInstance("obj_wall")

        ex.execute_collision_event(
            collider, "collision_with_obj_wall", events, other,
            collision_speeds={"self_hspeed": 9, "self_vspeed": 0,
                              "other_hspeed": 0, "other_vspeed": 0})

        # The spawned instance's create event must see its OWN hspeed (0),
        # not the colliding pair's captured 9.
        assert captured.get("hspeed") == 0


@pytest.mark.skipif(not pygame_available, reason="needs pygame")
class TestOutsideRoomOrigin:  # L30
    def _runner(self):
        from runtime.game_runner import GameRunner
        runner = GameRunner.__new__(GameRunner)
        return runner

    def test_origin_accounted_for(self):
        from runtime.game_runner import GameRunner

        events_fired = []

        class _Sprite:
            origin_x = 16
            origin_y = 0

        class _Exec:
            def execute_event(self, inst, name, events):
                events_fired.append(name)

        class _Inst:
            object_name = "obj"
            object_data = {"events": {"outside_room": {"actions": []}}}
            _cached_width = 32
            _cached_height = 32
            sprite = _Sprite()
            action_executor = _Exec()
            x = 10   # left edge = x - origin_x = -6; right edge = -6+32 = 26 > 0
            y = 10

        class _Room:
            width = 320
            height = 240
            instances = []

        runner = self._runner()
        room = _Room()
        inst = _Inst()
        room.instances.append(inst)
        runner.current_room = room

        # With origin accounted for, the sprite (left=-6..26) is still partly
        # visible, so outside_room must NOT fire.
        runner.check_outside_room_events()
        assert events_fired == []

        # Move fully off the left: x such that x-16+32 < 0 -> x < -16.
        inst.x = -20
        runner.check_outside_room_events()
        assert events_fired == ["outside_room"]

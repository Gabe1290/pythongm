"""Regression tests for create_random / create_moving instance actions.

M46: both creators appended the instance and called _add_to_grid but never set
the room's _depth_dirty flag, so render() (which draws only the cached
_sorted_instances) left the new instance invisible until an unrelated
destruction/room change dirtied the cache.

M47: create_moving_instance set_object_data on the RAW object data, dropping
parent inheritance — a child object spawned this way lost all inherited events
(collision, outside_room) and properties.
"""

import sys
from pathlib import Path

import pytest

from conftest import import_module_directly

_mod = import_module_directly("runtime/action_executor.py")
ActionExecutor = _mod.ActionExecutor

sys.path.insert(0, str(Path(__file__).parent))
from test_action_executor import MockInstance, MockRoom, MockGameRunner  # noqa: E402

pytestmark = pytest.mark.skipif(
    __import__("importlib").util.find_spec("pygame") is None,
    reason="create actions import GameInstance from runtime.game_runner (pygame)",
)


def _runner_with_objects(objects):
    runner = MockGameRunner()
    runner.project_data = {"assets": {"objects": objects}}
    runner.current_room = MockRoom()
    runner.current_room._depth_dirty = False
    return runner


class TestDepthDirty:  # M46
    def test_create_moving_marks_depth_dirty(self):
        runner = _runner_with_objects({"obj_bullet": {"name": "obj_bullet"}})
        ex = ActionExecutor(game_runner=runner)
        ex.execute_create_moving_instance_action(MockInstance(), {
            "object": "obj_bullet", "x": "0", "y": "0",
            "speed": "4", "direction": "0"})
        assert runner.current_room._depth_dirty is True

    def test_create_random_marks_depth_dirty(self):
        runner = _runner_with_objects({"obj_bonus": {"name": "obj_bonus"}})
        ex = ActionExecutor(game_runner=runner)
        ex.execute_create_random_instance_action(MockInstance(), {
            "object1": "obj_bonus", "x": "0", "y": "0"})
        assert runner.current_room._depth_dirty is True


class TestParentInheritance:  # M47
    def test_create_moving_inherits_parent_events(self):
        objects = {
            "obj_projectile": {
                "name": "obj_projectile",
                "events": {"collision_with_obj_wall": {"actions": []}},
            },
            "obj_arrow": {"name": "obj_arrow", "parent": "obj_projectile"},
        }
        runner = _runner_with_objects(objects)
        ex = ActionExecutor(game_runner=runner)
        ex.execute_create_moving_instance_action(MockInstance(), {
            "object": "obj_arrow", "x": "0", "y": "0",
            "speed": "4", "direction": "0"})
        new_instance = runner.current_room.instances[-1]
        events = new_instance.object_data.get("events", {})
        assert "collision_with_obj_wall" in events

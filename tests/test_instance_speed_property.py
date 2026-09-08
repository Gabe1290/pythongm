"""L5, docs/FULL_AUDIT_2026-09-07.md: `speed` is not derived from
hspeed/vspeed.

GameInstance used to have no `speed` attribute at all except where two
action handlers (create_moving_instance, and the if_can_push
stop_movement branch) and one grid-reset path happened to write a plain
`speed = <value>` alongside hspeed/vspeed. That value went stale the
instant anything else changed velocity -- set_hspeed/set_vspeed never
touched it -- and a bare `self.speed` in an expression on any instance
that never went through one of those three writers (the overwhelming
majority: anything placed in the room editor, or spawned via
create_instance/create_random_instance) always read as 0 regardless of
its real hspeed/vspeed.

Fix: `speed` is now a read-only property computed as
hypot(hspeed, vspeed), exactly mirroring how `direction` already worked
(see the property just above it in runtime/instance.py) -- always live,
never stale, no separate state to keep in sync.
"""
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from runtime.instance import GameInstance  # noqa: E402


def _inst():
    return GameInstance("obj_test", 0.0, 0.0, {}, action_executor=None)


def test_stationary_instance_has_zero_speed():
    inst = _inst()
    assert inst.speed == 0.0


def test_speed_is_the_live_hypot_of_hspeed_and_vspeed():
    inst = _inst()
    inst.hspeed = 3.0
    inst.vspeed = 4.0
    assert inst.speed == 5.0


def test_speed_updates_immediately_when_hspeed_or_vspeed_changes():
    """The exact bug: nothing must be able to leave `speed` stale after a
    direct hspeed/vspeed write (what set_hspeed/set_vspeed do)."""
    inst = _inst()
    inst.hspeed = 3.0
    inst.vspeed = 4.0
    assert inst.speed == 5.0

    inst.hspeed = 0.0
    assert inst.speed == 4.0  # not still 5.0

    inst.vspeed = 0.0
    assert inst.speed == 0.0


def test_speed_has_no_setter():
    """It is derived, like `direction` -- there is nothing to assign."""
    inst = _inst()
    try:
        inst.speed = 10.0
        assert False, "expected AttributeError: speed has no setter"
    except AttributeError:
        pass


def test_create_moving_instance_speed_matches_the_authored_value():
    """The one action that used to also write a separate plain `speed`
    attribute -- the computed property must agree with what was authored,
    for every ordinary GameMaker-style direction."""
    from runtime.action_executor import ActionExecutor

    class _Room:
        def __init__(self):
            self.instances = []
            self._depth_dirty = False

        def _add_to_grid(self, instance):
            pass

        def invalidate_collision_listened_types(self):
            pass

    class _Runner:
        def __init__(self):
            self.current_room = _Room()
            self._objects_data = {"obj_bullet": {"name": "obj_bullet", "events": {}}}
            self.sprites = {}
            self.project_data = {"assets": {"objects": {"obj_bullet": {"name": "obj_bullet", "events": {}}}}}

    class _Instance:
        object_name = "obj_spawner"

    executor = ActionExecutor(game_runner=_Runner())
    for direction in (0, 45, 90, 135, 180, 225, 270, 315):
        executor.execute_create_moving_instance_action(_Instance(), {
            "object": "obj_bullet", "x": 0, "y": 0,
            "speed": 6, "direction": direction,
        })
    for new_inst in executor.game_runner.current_room.instances:
        assert new_inst.speed == pytest.approx(6.0)

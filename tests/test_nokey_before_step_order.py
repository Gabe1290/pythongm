"""GM event order: the <no key> keyboard event runs BEFORE the step event
(maze_4 finding #12, second report — "the conveyors do not work").

maze_4's conveyor markers set motion from obj_person's STEP event, while its
<no key> keyboard event stops motion when nothing is pressed. GM's event order
is keyboard (incl. <no key>) -> step, so the conveyor's step runs LAST and
wins. pygm2 dispatched nokey AFTER the step event, so the stop stomped the
conveyor every frame: the person froze on the marker (velocity set to -8 by
the step, then zeroed by nokey, net zero — reproduced in the full game loop
where the earlier step-only harness had ridden fine).

GameInstance.step now dispatches nokey first, then the step event.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _conveyor_person():
    """An instance whose STEP starts motion (conveyor) and whose <no key>
    event stops it — the maze_4 shape, minus the marker conditionals."""
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameInstance
        from runtime.action_executor import ActionExecutor
        ex = ActionExecutor()
        ex.game_runner = SimpleNamespace(global_variables={})
        inst = GameInstance("obj_person", 32, 384, {}, ex)
        inst.object_data = {"events": {
            "step": {"actions": [
                {"action": "start_moving_direction",
                 "parameters": {"directions": "up", "speed": "8"}},
            ]},
            "keyboard": {"nokey": {"actions": [
                {"action": "start_moving_direction",
                 "parameters": {"directions": "stop", "speed": "8"}},
            ]}},
        }}
        return inst


def test_step_motion_survives_nokey_frame():
    """No keys pressed: nokey stops, then the step (conveyor) re-starts —
    the frame ends MOVING, exactly like GM."""
    person = _conveyor_person()
    person.keys_pressed = set()          # nothing held
    person.step()
    assert person.vspeed == -8.0, (
        "nokey ran after the step event and stomped the conveyor motion")


def test_nokey_still_stops_when_step_sets_no_motion():
    """Without step-driven motion, nokey's stop still lands (ordinary maze
    movement: release the key, stop)."""
    person = _conveyor_person()
    person.object_data["events"]["step"]["actions"] = []   # no conveyor
    person.keys_pressed = set()
    person.hspeed = 4.0                  # was moving right
    person.step()
    assert person.hspeed == 0
    assert person.vspeed == 0


def test_nokey_skipped_while_a_key_is_held():
    person = _conveyor_person()
    person.object_data["events"]["step"]["actions"] = []
    person.keys_pressed = {"right"}
    person.hspeed = 4.0
    person.step()
    assert person.hspeed == 4.0          # nokey did not fire

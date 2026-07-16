"""Question-chain scoping in the action list executors (maze_4 finding).

GM DND semantics: a question guards ONE unit — and when that unit is itself a
question, the unit includes the nested question PLUS ITS guarded unit,
recursively. The executors' skip logic skipped exactly one action instead, so
in a chain

    test_alignment (FALSE)
    if_collision(move_right)
    start_moving_direction(right, 8)

a failed alignment check skipped only the if_collision and ran the movement
UNCONDITIONALLY. maze_4's obj_person step event is four of these chains
back-to-back (up/down/left/right conveyor markers), so every frame the person
was misaligned, all four movements ran and the last one won: forced rightward
motion at the marker speed that arrow keys could never override — the user's
"starts moving right, cannot stop" report, reproduced headlessly before the
fix (h jumped 4 -> 8 one frame after pressing RIGHT, in a room containing
ZERO markers).

Covers both executors (the normal and the collision-event action list).
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _person(x, y):
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameInstance
        return GameInstance("obj_person", x, y, {}, MagicMock())


def _executor(collision_result):
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    ex.game_runner = SimpleNamespace(
        current_room=SimpleNamespace(instances=[]),
        check_collision_at_position=lambda *a, **k: collision_result,
    )
    return ex


def _marker_chain(direction="right"):
    """One maze_4-style conveyor chain: aligned? -> on marker? -> move."""
    return [
        {"action": "test_alignment", "parameters": {"hsnap": "32", "vsnap": "32"}},
        {"action": "if_collision",
         "parameters": {"object": "move_" + direction, "x": "0", "y": "0",
                        "relative": True}},
        {"action": "start_moving_direction",
         "parameters": {"directions": direction, "speed": "8"}},
    ]


def test_failed_question_skips_nested_question_AND_its_unit():
    """Misaligned instance: the whole chain is dead — the movement must NOT run."""
    person = _person(37, 416)               # 37 % 32 != 0 -> test_alignment False
    ex = _executor(collision_result=True)   # even if a marker WERE underfoot
    ex.execute_action_list(person, _marker_chain())
    assert person.hspeed == 0
    assert person.vspeed == 0


def test_four_chains_do_not_leak_into_each_other():
    """The exact maze_4 step event shape: four chains back-to-back. Misaligned
    -> nothing moves (before the fix the LAST chain's movement always won)."""
    person = _person(37, 416)
    ex = _executor(collision_result=False)
    actions = (_marker_chain("up") + _marker_chain("down")
               + _marker_chain("left") + _marker_chain("right"))
    ex.execute_action_list(person, actions)
    assert person.hspeed == 0 and person.vspeed == 0


def test_aligned_but_no_marker_does_not_move():
    person = _person(32, 416)               # aligned
    ex = _executor(collision_result=False)  # no marker underfoot
    ex.execute_action_list(person, _marker_chain())
    assert person.hspeed == 0 and person.vspeed == 0


def test_aligned_on_marker_moves():
    """The chain still fires when BOTH questions pass."""
    person = _person(32, 416)
    ex = _executor(collision_result=True)
    ex.execute_action_list(person, _marker_chain())
    assert person.hspeed == 8.0


def test_collision_list_executor_has_the_same_scoping():
    """The collision-event action list duplicates the loop — same semantics."""
    person = _person(37, 416)
    other = _person(0, 0)          # stands in for the collision partner
    ex = _executor(collision_result=True)
    ex.execute_collision_action_list(person, _marker_chain(), other)
    assert person.hspeed == 0 and person.vspeed == 0


def test_skipped_chain_still_supports_following_else():
    """An else after a skipped question-chain belongs to the OUTER question:
    outer false -> chain skipped -> else branch runs."""
    person = _person(37, 416)
    ex = _executor(collision_result=True)
    actions = _marker_chain() + [
        {"action": "else_action", "parameters": {}},
        {"action": "start_moving_direction",
         "parameters": {"directions": "down", "speed": "2"}},
    ]
    ex.execute_action_list(person, actions)
    assert person.vspeed == 2.0             # else ran
    assert person.hspeed == 0               # chain did not

"""Runtime side of GM's "Applies to" (treasure playtest finding #3).

After the importer began emitting target/target_object (finding #2), the
user's re-test surfaced the runtime gaps behind two symptoms:

- "monsters change color and FREEZE": change_instance zeroed hspeed/vspeed
  unconditionally (a fix from e8f31c9 for a mid-grid-step box). GM8's
  instance_change keeps every variable including motion — treasure's scared
  object has NO events except alarm_0; its movement is purely the velocity
  carried through the change. Motion is now preserved, except for instances
  mid grid-step (the e8f31c9 case), whose leftover cell-to-cell velocity has
  no owner and is still zeroed.
- "only Explorer teleports home on death": jump_to_start and set_alarm ran
  against self only. Both now honor target/target_object via the shared
  _resolve_target_instances helper (self | other | every instance of an
  object), so the death event resets all monsters and the power pill arms
  alarm 0 on every scared monster.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _instance(name, x=0, y=0):
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameInstance
        inst = GameInstance(name, x, y, {}, MagicMock())
        return inst


def _executor_with_room(instances):
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    room = SimpleNamespace(
        instances=list(instances),
        invalidate_collision_listened_types=lambda: None,
    )
    ex.game_runner = SimpleNamespace(
        current_room=room,
        sprites={},
        _objects_data={},
        project_data={"assets": {"objects": {
            "scared": {"name": "scared", "sprite": "", "events": {}},
        }}},
    )
    return ex


# ---------------------------------------------------------------------------
# change_instance motion preservation
# ---------------------------------------------------------------------------

def test_change_instance_preserves_motion():
    """GM8 semantics: the gliding monster keeps its velocity when it becomes
    scared (scared has no events to restart movement — zeroing froze it)."""
    monster = _instance("monster", 100, 100)
    monster.hspeed = 4.0
    monster.vspeed = 0.0
    ex = _executor_with_room([monster])
    ex.execute_change_instance_action(
        monster, {"object": "scared", "perform_events": "0"})
    assert monster.object_name == "scared"
    assert monster.hspeed == 4.0
    assert monster.vspeed == 0.0


def test_change_instance_still_zeroes_mid_grid_step():
    """The e8f31c9 case: an instance mid grid-step had its velocity generated
    by the OLD type's cell-to-cell logic; without it the leftover step
    velocity never terminates, so it is still zeroed."""
    box = _instance("box", 96, 96)
    box.hspeed = 4.0
    box.intended_x = 128        # grid move in progress
    box.intended_y = 96
    ex = _executor_with_room([box])
    ex.execute_change_instance_action(
        box, {"object": "scared", "perform_events": "0"})
    assert box.hspeed == 0
    assert box.vspeed == 0


# ---------------------------------------------------------------------------
# jump_to_start targeting
# ---------------------------------------------------------------------------

def test_jump_to_start_targets_every_instance_of_object():
    """Treasure's death event: every monster teleports back to its spawn."""
    m1 = _instance("monster", 100, 100)
    m2 = _instance("monster", 300, 200)
    hero = _instance("explorer", 50, 50)
    for m in (m1, m2):
        m.x += 64          # they have wandered
        m.y += 32
    ex = _executor_with_room([hero, m1, m2])
    ex.execute_jump_to_start_action(
        hero, {"target": "object", "target_object": "monster"})
    assert (m1.x, m1.y) == (100, 100)
    assert (m2.x, m2.y) == (300, 200)
    assert (hero.x, hero.y) == (50, 50)     # untouched — not the target


def test_jump_to_start_targets_other():
    """Eating a scared monster teleports IT home (target 'other')."""
    hero = _instance("explorer", 50, 50)
    scared = _instance("scared", 200, 200)
    scared.x, scared.y = 260, 230
    hero._collision_other = scared
    ex = _executor_with_room([hero, scared])
    ex.execute_jump_to_start_action(hero, {"target": "other"})
    assert (scared.x, scared.y) == (200, 200)
    assert (hero.x, hero.y) == (50, 50)


def test_jump_to_start_default_is_self():
    hero = _instance("explorer", 50, 50)
    hero.x, hero.y = 400, 300
    ex = _executor_with_room([hero])
    ex.execute_jump_to_start_action(hero, {})
    assert (hero.x, hero.y) == (50, 50)


# ---------------------------------------------------------------------------
# set_alarm targeting
# ---------------------------------------------------------------------------

def test_set_alarm_targets_every_instance_of_object():
    """The power pill arms alarm 0 on every scared monster (they revert to
    normal when it fires)."""
    s1 = _instance("scared", 0, 0)
    s2 = _instance("scared", 10, 10)
    hero = _instance("explorer", 50, 50)
    ex = _executor_with_room([hero, s1, s2])
    ex.execute_set_alarm_action(
        hero, {"steps": "160", "alarm_number": "0",
               "target": "object", "target_object": "scared"})
    assert s1.alarm[0] == 160
    assert s2.alarm[0] == 160
    # the acting instance is NOT armed — it wasn't the target
    assert getattr(hero, 'alarm', [-1] * 12)[0] == -1


def test_set_alarm_default_is_self():
    hero = _instance("explorer", 50, 50)
    ex = _executor_with_room([hero])
    ex.execute_set_alarm_action(hero, {"steps": "30", "alarm_number": "2"})
    assert hero.alarm[2] == 30

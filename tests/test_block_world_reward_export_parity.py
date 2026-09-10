"""Block World mine-to-collect reward parity across desktop and Kivy,
mirroring tests/test_block_world_crafting_export_parity.py's own
two-tier approach for this extension:

- **Desktop <-> Kivy: exact outcome equality.** Both are runnable
  Python, so the identical set_block_reward/break_block calls are fed to
  each and the resulting reward registration + payout are asserted
  equal. Desktop pays out via `game_runner.score += int(points)`; Kivy
  goes through `from main import set_score; set_score(points,
  relative=True)` -- a real, deliberate difference in mechanism (Kivy's
  score lives on the exported GameApp, reached through the same lazy
  `main` import every other score/lives/health action on that target
  uses), so what's compared is the resulting VALUE (the registered
  reward, and the total points paid out for a given break sequence), not
  the call shape.
- **HTML5** already had this action from the start; not re-verified
  here (this file exists specifically for the Kivy gap that was found
  missing, see tests/test_kivy_block_world_reward.py's own docstring).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((1, 1))

from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.block_world.state import block_world_state, set_block  # noqa: E402

from test_kivy_block_world import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _default_cfg, _FakeInst,
    _export_block_world_1,
)

import pytest

CELL = 32


@pytest.fixture(scope="module")
def exported():
    return _export_block_world_1()


def _desktop_world(inventory=False):
    room = GameRoom("reward-parity", {"width": 40 * CELL, "height": 40 * CELL},
                     action_executor=None)
    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = camera._cached_height = CELL
    camera.facing_angle = 0.0
    room.instances.append(camera)
    cfg = block_world_state(room)["camera"]
    cfg.update({"enabled": True, "camera_object": "obj_person", "cell_size": CELL,
                "z_layer": 0, "vz": 0.0, "gravity": 0.0, "inventory": inventory,
                "fov": 66, "render_distance": 20, "columns": 1,
                "wall_textured": False, "eye_height": 0.5})
    return room, camera, cfg


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}
        self.score = 0
        self.show_score_in_caption = False


def _desktop_run(room, camera, action, runner=None, **params):
    if runner is None:
        runner = _Runner(room)
    ex = ActionExecutor(game_runner=runner)
    load_all_plugins(ex)
    camera.action_executor = ex
    ex.action_handlers[action](camera, params)
    return runner


def test_reward_registration_matches_across_desktop_and_kivy(exported):
    room, camera, cfg = _desktop_world()
    _desktop_run(room, camera, "set_block_reward",
                 block_type="diamond_block", points=10)
    desktop_points = cfg["rewards"]["diamond_block"]

    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.block_world_camera = _default_cfg()
        scene._bw_set_block_reward("diamond_block", 10)
        kivy_points = scene.block_world_camera["rewards"]["diamond_block"]

    assert desktop_points == kivy_points == 10


def test_single_break_payout_matches_across_desktop_and_kivy(exported):
    room, camera, cfg = _desktop_world(inventory=False)
    set_block(room, 1, 0, 0, "diamond_block")
    _desktop_run(room, camera, "set_block_reward",
                 block_type="diamond_block", points=10)
    runner = _desktop_run(room, camera, "break_block")
    desktop_payout = runner.score

    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=0.5)
        scene.block_world_camera["camera_instance"] = cam
        scene._bw_set_block(2, 1, 0, "diamond_block")
        scene._bw_set_block_reward("diamond_block", 10)
        scene._bw_break_block(cam, 5)
        kivy_payout = sum(value for value, relative in sys.modules["main"].score_calls)

    assert desktop_payout == kivy_payout == 10


def test_accumulated_payout_across_multiple_breaks_matches(exported):
    room, camera, cfg = _desktop_world(inventory=False)
    set_block(room, 1, 0, 0, "diamond_block")
    set_block(room, 2, 0, 0, "gold_block")
    _desktop_run(room, camera, "set_block_reward",
                 block_type="diamond_block", points=10)
    _desktop_run(room, camera, "set_block_reward",
                 block_type="gold_block", points=100)
    runner = _desktop_run(room, camera, "break_block")
    _desktop_run(room, camera, "break_block", runner=runner)
    desktop_total = runner.score

    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=0.5)
        scene.block_world_camera["camera_instance"] = cam
        scene._bw_set_block(2, 1, 0, "diamond_block")
        scene._bw_set_block(3, 1, 0, "gold_block")
        scene._bw_set_block_reward("diamond_block", 10)
        scene._bw_set_block_reward("gold_block", 100)
        scene._bw_break_block(cam, 5)
        scene._bw_break_block(cam, 5)
        kivy_total = sum(value for value, relative in sys.modules["main"].score_calls)

    assert desktop_total == kivy_total == 110


def test_a_refused_break_pays_out_nothing_on_either_side(exported):
    """Protection wins first: a rewarded AND protected block pays out
    only once actually mined, not on a swing that no-ops -- on both
    engines identically."""
    room, camera, cfg = _desktop_world(inventory=True)
    set_block(room, 1, 0, 0, "diamond_block")
    _desktop_run(room, camera, "set_block_reward",
                 block_type="diamond_block", points=10)
    _desktop_run(room, camera, "set_block_protection",
                 block_type="diamond_block", required_key="gold_block")
    runner = _desktop_run(room, camera, "break_block")
    desktop_payout = runner.score

    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
        scene.instances = [cam]
        scene.block_world_camera = _default_cfg(eye_height=0.5, inventory=True)
        scene.block_world_camera["camera_instance"] = cam
        scene._bw_set_block(2, 1, 0, "diamond_block")
        scene._bw_set_block_reward("diamond_block", 10)
        scene._bw_set_block_protection("diamond_block", "gold_block")
        scene._bw_break_block(cam, 5)
        kivy_payout = sum(value for value, relative in sys.modules["main"].score_calls)

    assert desktop_payout == kivy_payout == 0


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-q"]))

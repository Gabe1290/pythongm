"""Block World crafting parity across desktop and Kivy
(docs/BLOCK_WORLD_CRAFTING_PLAN.md Unit 2), mirroring the two-tier approach
tests/test_block_world_export_parity.py already established for this
extension's DDA renderer:

- **Desktop <-> Kivy: exact state equality.** Both are runnable Python, so
  the identical recipe-registration and craft-attempt calls are fed to each
  and the resulting recipe/inventory state is asserted equal.
- **HTML5: structural equivalence**, covered separately by
  tests/test_html5_block_world_crafting.py (no JS engine here).
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
from extensions.block_world.state import block_world_state  # noqa: E402

from test_kivy_block_world import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _default_cfg, _FakeInst,
    _export_block_world_1,
)

import pytest

CELL = 32


@pytest.fixture(scope="module")
def exported():
    return _export_block_world_1()


def _desktop_world(inventory=True):
    room = GameRoom("crafting-parity", {"width": 40 * CELL, "height": 40 * CELL},
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


def _desktop_run(room, camera, action, **params):
    ex = ActionExecutor(game_runner=type(
        "_R", (), {"current_room": room, "global_variables": {}})())
    load_all_plugins(ex)
    camera.action_executor = ex
    ex.action_handlers[action](camera, params)


# Recipe scenarios exercised identically on both sides: (register kwargs,
# starting inventory, expected recipe inputs list, expected post-craft
# inventory).
SCENARIOS = [
    pytest.param(
        dict(output="brick", output_count=4, input_1="clay", input_1_count=4,
             input_2="", input_2_count=1, input_3="", input_3_count=1),
        {"clay": 4},
        [("clay", 4)],
        {"clay": 0, "brick": 4},
        id="single-input",
    ),
    pytest.param(
        dict(output="obsidian", output_count=1, input_1="stone", input_1_count=2,
             input_2="coal_block", input_2_count=1, input_3="", input_3_count=1),
        {"stone": 2, "coal_block": 1},
        [("stone", 2), ("coal_block", 1)],
        {"stone": 0, "coal_block": 0, "obsidian": 1},
        id="two-input",
    ),
    pytest.param(
        dict(output="obsidian", output_count=2, input_1="stone", input_1_count=1,
             input_2="coal_block", input_2_count=1, input_3="gold_block", input_3_count=1),
        {"stone": 1, "coal_block": 1, "gold_block": 1},
        [("stone", 1), ("coal_block", 1), ("gold_block", 1)],
        {"stone": 0, "coal_block": 0, "gold_block": 0, "obsidian": 2},
        id="three-input",
    ),
    pytest.param(
        dict(output="brick", output_count=1, input_1="clay", input_1_count=1,
             input_2="", input_2_count=1, input_3="sand", input_3_count=1),
        {"clay": 1, "sand": 1},
        [("clay", 1), ("sand", 1)],
        {"clay": 0, "sand": 0, "brick": 1},
        id="blank-slot-2-with-valid-slot-3",
    ),
]


@pytest.mark.parametrize("register_kwargs, starting_inventory, expected_inputs, expected_after_craft", SCENARIOS)
def test_recipe_storage_matches_across_desktop_and_kivy(
        register_kwargs, starting_inventory, expected_inputs, expected_after_craft, exported):
    # Desktop
    room, camera, cfg = _desktop_world(inventory=True)
    _desktop_run(room, camera, "set_crafting_recipe", **register_kwargs)
    desktop_inputs = cfg["recipes"][register_kwargs["output"]]["inputs"]
    desktop_output_count = cfg["recipes"][register_kwargs["output"]]["output_count"]

    # Kivy
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.block_world_camera = _default_cfg(inventory=True)
        scene._bw_set_crafting_recipe(
            register_kwargs["output"], register_kwargs["output_count"],
            register_kwargs["input_1"], register_kwargs["input_1_count"],
            register_kwargs["input_2"], register_kwargs["input_2_count"],
            register_kwargs["input_3"], register_kwargs["input_3_count"])
        kivy_inputs = scene.block_world_camera["recipes"][register_kwargs["output"]]["inputs"]
        kivy_output_count = scene.block_world_camera["recipes"][register_kwargs["output"]]["output_count"]

    assert desktop_inputs == kivy_inputs == expected_inputs
    assert desktop_output_count == kivy_output_count == register_kwargs["output_count"]


@pytest.mark.parametrize("register_kwargs, starting_inventory, expected_inputs, expected_after_craft", SCENARIOS)
def test_craft_consumption_matches_across_desktop_and_kivy(
        register_kwargs, starting_inventory, expected_inputs, expected_after_craft, exported):
    output = register_kwargs["output"]

    # Desktop
    room, camera, cfg = _desktop_world(inventory=True)
    _desktop_run(room, camera, "set_crafting_recipe", **register_kwargs)
    camera.block_inventory = dict(starting_inventory)
    _desktop_run(room, camera, "craft_item", output=output)
    desktop_result = camera.block_inventory

    # Kivy
    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.block_world_camera = _default_cfg(inventory=True)
        scene._bw_set_crafting_recipe(
            register_kwargs["output"], register_kwargs["output_count"],
            register_kwargs["input_1"], register_kwargs["input_1_count"],
            register_kwargs["input_2"], register_kwargs["input_2_count"],
            register_kwargs["input_3"], register_kwargs["input_3_count"])
        kivy_camera = _FakeInst(0, 0, 32, 32)
        kivy_camera.block_inventory = dict(starting_inventory)
        scene._bw_craft_item(kivy_camera, output)
        kivy_result = kivy_camera.block_inventory

    assert desktop_result == kivy_result == expected_after_craft


def test_short_input_consumes_nothing_on_both_sides(exported):
    """All-or-nothing, exercised identically: short by one on the second
    input must leave inventory untouched on both engines."""
    register_kwargs = dict(output="obsidian", output_count=1,
                            input_1="stone", input_1_count=2,
                            input_2="coal_block", input_2_count=1,
                            input_3="", input_3_count=1)
    starting = {"stone": 2, "coal_block": 0}

    room, camera, cfg = _desktop_world(inventory=True)
    _desktop_run(room, camera, "set_crafting_recipe", **register_kwargs)
    camera.block_inventory = dict(starting)
    _desktop_run(room, camera, "craft_item", output="obsidian")
    assert camera.block_inventory == starting

    with _stub_kivy_env(exported):
        cls = _scene_class(exported)
        scene = _blank_scene(cls)
        scene.block_world_camera = _default_cfg(inventory=True)
        scene._bw_set_crafting_recipe(
            "obsidian", 1, "stone", 2, "coal_block", 1, "", 1)
        kivy_camera = _FakeInst(0, 0, 32, 32)
        kivy_camera.block_inventory = dict(starting)
        scene._bw_craft_item(kivy_camera, "obsidian")
        assert kivy_camera.block_inventory == starting


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-q"]))

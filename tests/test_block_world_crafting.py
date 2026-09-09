"""Block World crafting (Tier 8, docs/BLOCK_WORLD_CRAFTING_PLAN.md).

set_crafting_recipe registers {output_block: {output_count, inputs}} on the
room's camera config, one call per output type -- same call-once-per-type
pattern, same camera-config storage, as set_block_protection/
set_block_reward. craft_item then attempts a registered recipe against the
calling instance's block_inventory (Tier 7c), all-or-nothing: every input is
checked before any is consumed.

Outputs are block types, not a separate "item" concept (design decision 1)
-- a crafted result lands in the same block_inventory dict break_block/
place_block already use. Up to three input slots, input_1 required,
input_2/input_3 optional (blank type = unused, design decision 2).

Every project that never calls set_crafting_recipe sees zero change to
anything -- craft_item's cfg.get("recipes", {}).get(output) is never
populated, so there is nothing to attempt -- deliberately backward
compatible, same pattern as every prior Tier.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from runtime.game_runner import GameRoom, GameInstance  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.block_world.state import block_world_state  # noqa: E402

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


def _world(inventory=True):
    room = GameRoom("crafting", {"width": 40 * CELL, "height": 40 * CELL},
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


def _run(room, camera, action, **params):
    ex = ActionExecutor(game_runner=_Runner(room))
    load_all_plugins(ex)
    camera.action_executor = ex
    return ex.action_handlers[action](camera, params)


class TestSetCraftingRecipeRegistersRecipe:
    def test_registers_a_single_input_recipe(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=4, input_1="clay", input_1_count=4)
        assert cfg["recipes"] == {
            "brick": {"output_count": 4, "inputs": [("clay", 4)]}}

    def test_registers_a_two_input_recipe_leaving_slot_3_blank(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="obsidian", output_count=1,
             input_1="stone", input_1_count=4,
             input_2="coal_block", input_2_count=1)
        assert cfg["recipes"]["obsidian"] == {
            "output_count": 1, "inputs": [("stone", 4), ("coal_block", 1)]}

    def test_registers_a_three_input_recipe(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="obsidian", output_count=1,
             input_1="stone", input_1_count=2,
             input_2="coal_block", input_2_count=1,
             input_3="gold_block", input_3_count=1)
        assert cfg["recipes"]["obsidian"]["inputs"] == [
            ("stone", 2), ("coal_block", 1), ("gold_block", 1)]

    def test_blank_slot_2_with_a_valid_slot_3_still_registers_both(self):
        """input_2/input_3 are each independently well-formed-or-skipped --
        a blank slot 2 doesn't block a valid slot 3 from registering too."""
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1,
             input_1="clay", input_1_count=2,
             input_2="", input_2_count=1,
             input_3="sand", input_3_count=1)
        assert cfg["recipes"]["brick"]["inputs"] == [
            ("clay", 2), ("sand", 1)]

    def test_missing_input_1_registers_nothing(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="", input_1_count=1)
        assert cfg.get("recipes", {}) == {}

    def test_unknown_input_1_type_registers_nothing(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1,
             input_1="not_a_real_block", input_1_count=1)
        assert cfg.get("recipes", {}) == {}

    def test_unknown_output_type_registers_nothing(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="not_a_real_block", output_count=1,
             input_1="stone", input_1_count=1)
        assert cfg.get("recipes", {}) == {}

    def test_non_positive_output_count_registers_nothing(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=0,
             input_1="stone", input_1_count=1)
        assert cfg.get("recipes", {}) == {}

    def test_non_positive_input_1_count_registers_nothing(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1,
             input_1="stone", input_1_count=0)
        assert cfg.get("recipes", {}) == {}

    def test_non_positive_optional_slot_count_is_just_skipped(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1,
             input_1="clay", input_1_count=1,
             input_2="stone", input_2_count=0)
        assert cfg["recipes"]["brick"]["inputs"] == [("clay", 1)]

    def test_multiple_calls_accumulate_separate_output_entries(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=4, input_1="clay", input_1_count=4)
        _run(room, camera, "set_crafting_recipe",
             output="wood_plank", output_count=4,
             input_1="wood_log", input_1_count=1)
        assert set(cfg["recipes"]) == {"brick", "wood_plank"}

    def test_re_registering_the_same_output_overwrites(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=4, input_1="clay", input_1_count=4)
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="stone", input_1_count=2)
        assert cfg["recipes"]["brick"] == {
            "output_count": 1, "inputs": [("stone", 2)]}

    def test_without_an_active_view_is_a_noop(self):
        room, camera, cfg = _world()
        cfg["enabled"] = False
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=4, input_1="clay", input_1_count=4)
        assert cfg.get("recipes") is None


class TestCraftItemConsumesAndProduces:
    def test_crafts_successfully_when_inventory_is_sufficient(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="clay", input_1_count=4)
        camera.block_inventory = {"clay": 4}
        _run(room, camera, "craft_item", output="brick")
        assert camera.block_inventory == {"clay": 0, "brick": 1}

    def test_two_input_recipe_consumes_both(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="obsidian", output_count=1,
             input_1="stone", input_1_count=2,
             input_2="coal_block", input_2_count=1)
        camera.block_inventory = {"stone": 2, "coal_block": 1}
        _run(room, camera, "craft_item", output="obsidian")
        assert camera.block_inventory == {
            "stone": 0, "coal_block": 0, "obsidian": 1}

    def test_short_on_one_of_two_inputs_consumes_nothing(self):
        """All-or-nothing: a recipe needing 2 inputs never partially
        consumes one and fails the other."""
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="obsidian", output_count=1,
             input_1="stone", input_1_count=2,
             input_2="coal_block", input_2_count=1)
        camera.block_inventory = {"stone": 2, "coal_block": 0}
        _run(room, camera, "craft_item", output="obsidian")
        assert camera.block_inventory == {"stone": 2, "coal_block": 0}

    def test_exactly_enough_leaves_zero_not_negative(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="clay", input_1_count=4)
        camera.block_inventory = {"clay": 4}
        _run(room, camera, "craft_item", output="brick")
        assert camera.block_inventory["clay"] == 0

    def test_output_accumulates_onto_an_existing_count(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="clay", input_1_count=1)
        camera.block_inventory = {"clay": 2, "brick": 3}
        _run(room, camera, "craft_item", output="brick")
        assert camera.block_inventory == {"clay": 1, "brick": 4}

    def test_no_recipe_registered_is_a_noop(self):
        room, camera, cfg = _world(inventory=True)
        camera.block_inventory = {"clay": 99}
        _run(room, camera, "craft_item", output="brick")
        assert camera.block_inventory == {"clay": 99}

    def test_without_inventory_enabled_is_a_noop(self):
        room, camera, cfg = _world(inventory=False)
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="clay", input_1_count=1)
        _run(room, camera, "craft_item", output="brick")
        assert getattr(camera, "block_inventory", None) is None

    def test_without_an_active_view_is_a_noop(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="brick", output_count=1, input_1="clay", input_1_count=1)
        camera.block_inventory = {"clay": 4}
        cfg["enabled"] = False
        _run(room, camera, "craft_item", output="brick")
        assert camera.block_inventory == {"clay": 4}

    def test_three_input_recipe_consumes_all_three(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "set_crafting_recipe",
             output="obsidian", output_count=2,
             input_1="stone", input_1_count=1,
             input_2="coal_block", input_2_count=1,
             input_3="gold_block", input_3_count=1)
        camera.block_inventory = {"stone": 1, "coal_block": 1, "gold_block": 1}
        _run(room, camera, "craft_item", output="obsidian")
        assert camera.block_inventory == {
            "stone": 0, "coal_block": 0, "gold_block": 0, "obsidian": 2}


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))

"""Kivy export codegen/execution parity for Block World's Tier 8 crafting
(docs/BLOCK_WORLD_CRAFTING_PLAN.md Unit 2): set_crafting_recipe/craft_item.

Reuses tests/test_kivy_block_world.py's own stub-kivy execution harness
(_stub_kivy_env/_scene_class/_blank_scene/_default_cfg/_FakeInst) so the
real generated _bw_set_crafting_recipe/_bw_craft_item methods run against
controlled state -- no Kivy installation or GL context needed, matching
this extension's established test discipline.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402

from test_kivy_block_world import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _default_cfg, _FakeInst,
    _export_block_world_1,
)

import pytest


@pytest.fixture(scope="module")
def exported():
    return _export_block_world_1()


# ---------------------------------------------------------------------------
# Code-generator unit tests
# ---------------------------------------------------------------------------

def test_set_crafting_recipe_codegen_single_input():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_crafting_recipe",
        {"output": "brick", "output_count": "4",
         "input_1": "clay", "input_1_count": "4"}, "create")
    assert code == (
        "self.scene._bw_set_crafting_recipe("
        "'brick', 4, 'clay', 4, '', 1, '', 1)")


def test_set_crafting_recipe_codegen_three_inputs():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_crafting_recipe",
        {"output": "obsidian", "output_count": "2",
         "input_1": "stone", "input_1_count": "1",
         "input_2": "coal_block", "input_2_count": "1",
         "input_3": "gold_block", "input_3_count": "1"}, "create")
    assert code == (
        "self.scene._bw_set_crafting_recipe("
        "'obsidian', 2, 'stone', 1, 'coal_block', 1, 'gold_block', 1)")


def test_craft_item_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("craft_item", {"output": "brick"}, "keyboard_press")
    assert code == "self.scene._bw_craft_item(self, 'brick')"


def test_obj_person_source_and_scene_compile_with_new_methods(exported):
    scene_file = next(f for f in (exported / "scenes").glob("*.py")
                      if "_bw_set_crafting_recipe" in f.read_text(encoding="utf-8"))
    scene = scene_file.read_text(encoding="utf-8")
    for name in ("_bw_crafting_slot", "_bw_set_crafting_recipe", "_bw_craft_item"):
        assert f"def {name}(" in scene
    compile(scene, scene_file.name, "exec")


# ---------------------------------------------------------------------------
# Real execution harness
# ---------------------------------------------------------------------------

class TestSetCraftingRecipeRegistersRecipe:
    def test_registers_a_single_input_recipe(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_crafting_recipe(
                "brick", 4, "clay", 4, "", 1, "", 1)
            assert scene.block_world_camera["recipes"] == {
                "brick": {"output_count": 4, "inputs": [("clay", 4)]}}

    def test_registers_a_three_input_recipe(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_crafting_recipe(
                "obsidian", 1, "stone", 2, "coal_block", 1, "gold_block", 1)
            assert scene.block_world_camera["recipes"]["obsidian"]["inputs"] == [
                ("stone", 2), ("coal_block", 1), ("gold_block", 1)]

    def test_blank_slot_2_with_a_valid_slot_3_still_registers_both(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_crafting_recipe(
                "brick", 1, "clay", 2, "", 1, "sand", 1)
            assert scene.block_world_camera["recipes"]["brick"]["inputs"] == [
                ("clay", 2), ("sand", 1)]

    def test_missing_input_1_registers_nothing(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_crafting_recipe("brick", 1, "", 1, "", 1, "", 1)
            assert scene.block_world_camera.get("recipes", {}) == {}

    def test_unknown_output_type_registers_nothing(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_crafting_recipe(
                "not_a_real_block", 1, "stone", 1, "", 1, "", 1)
            assert scene.block_world_camera.get("recipes", {}) == {}

    def test_without_an_active_view_is_a_noop(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(enabled=False)
            scene._bw_set_crafting_recipe("brick", 1, "clay", 4, "", 1, "", 1)
            assert scene.block_world_camera.get("recipes") is None


class TestCraftItemConsumesAndProduces:
    def test_crafts_successfully_when_inventory_is_sufficient(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(inventory=True)
            scene._bw_set_crafting_recipe("brick", 1, "clay", 4, "", 1, "", 1)
            camera = _FakeInst(0, 0, 32, 32)
            camera.block_inventory = {"clay": 4}
            scene._bw_craft_item(camera, "brick")
            assert camera.block_inventory == {"clay": 0, "brick": 1}

    def test_short_on_one_of_two_inputs_consumes_nothing(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(inventory=True)
            scene._bw_set_crafting_recipe(
                "obsidian", 1, "stone", 2, "coal_block", 1, "", 1)
            camera = _FakeInst(0, 0, 32, 32)
            camera.block_inventory = {"stone": 2, "coal_block": 0}
            scene._bw_craft_item(camera, "obsidian")
            assert camera.block_inventory == {"stone": 2, "coal_block": 0}

    def test_output_accumulates_onto_an_existing_count(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(inventory=True)
            scene._bw_set_crafting_recipe("brick", 1, "clay", 1, "", 1, "", 1)
            camera = _FakeInst(0, 0, 32, 32)
            camera.block_inventory = {"clay": 2, "brick": 3}
            scene._bw_craft_item(camera, "brick")
            assert camera.block_inventory == {"clay": 1, "brick": 4}

    def test_no_recipe_registered_is_a_noop(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(inventory=True)
            camera = _FakeInst(0, 0, 32, 32)
            camera.block_inventory = {"clay": 99}
            scene._bw_craft_item(camera, "brick")
            assert camera.block_inventory == {"clay": 99}

    def test_without_inventory_enabled_is_a_noop(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(inventory=False)
            scene._bw_set_crafting_recipe("brick", 1, "clay", 1, "", 1, "", 1)
            camera = _FakeInst(0, 0, 32, 32)
            scene._bw_craft_item(camera, "brick")
            assert getattr(camera, "block_inventory", None) is None


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-q"]))

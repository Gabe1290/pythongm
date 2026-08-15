"""Kivy export -- Tier 7e Phase 3 (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md):
seed-based procedural terrain generation, ported into the Kivy scene
template. Mirrors tests/test_kivy_block_world.py's structure and reuses
its stub-kivy execution harness (_stub_kivy_env/_scene_class/_blank_scene/
_export_block_world_1) rather than duplicating it.
"""
import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from extensions.block_world.state import terrain_height  # noqa: E402

from test_kivy_block_world import (  # noqa: E402
    _stub_kivy_env, _scene_class, _blank_scene, _export_block_world_1,
    _FakeInst, _default_cfg,
)


@pytest.fixture(scope="module")
def exported():
    return _export_block_world_1()


# ---------------------------------------------------------------------------
# Code-generator unit tests
# ---------------------------------------------------------------------------

class TestEnableBlockWorldViewCodegen:
    def test_generate_off_by_default_sets_seed_none(self):
        gen = ActionCodeGenerator()
        code = gen._convert_simple_action(
            "enable_block_world_view", {"camera_object": "obj_person"}, "create")
        assert "self.scene._bw_seed = None" in code
        ast.parse(code)

    def test_generate_on_sets_the_seed(self):
        gen = ActionCodeGenerator()
        code = gen._convert_simple_action(
            "enable_block_world_view",
            {"camera_object": "obj_person", "generate": "true", "seed": "7"},
            "create")
        assert "self.scene._bw_seed = 7" in code
        ast.parse(code)

    def test_no_camera_object_variant_also_sets_seed(self):
        gen = ActionCodeGenerator()
        code = gen._convert_simple_action(
            "enable_block_world_view", {"generate": "true", "seed": "3"}, "create")
        assert "self.scene._bw_seed = 3" in code
        assert "camera_instance" in code
        ast.parse(code)


class TestLoadBlockWorldCodegen:
    def test_old_list_shape_still_works(self):
        gen = ActionCodeGenerator(extension_data={
            "block_world_files": {"blocks/x.json": [{"x": 1, "y": 2, "z": 3, "type": "stone"}]},
        })
        code = gen._convert_simple_action(
            "load_block_world", {"data_file": "blocks/x.json"}, "game_start")
        assert code == "self.scene._bw_load_block_world([{'x': 1, 'y': 2, 'z': 3, 'type': 'stone'}])"
        ast.parse(code)

    def test_new_seeded_dict_shape(self):
        gen = ActionCodeGenerator(extension_data={
            "block_world_files": {"blocks/seeded.json": {
                "seed": 5, "blocks": [{"x": 2, "y": 2, "z": 0, "type": "gold_block"}]}},
        })
        code = gen._convert_simple_action(
            "load_block_world", {"data_file": "blocks/seeded.json"}, "game_start")
        assert code == ("self.scene._bw_load_block_world("
                        "{'seed': 5, 'blocks': [{'x': 2, 'y': 2, 'z': 0, 'type': 'gold_block'}]})")
        ast.parse(code)


# ---------------------------------------------------------------------------
# Stub-kivy execution: the real generated methods, real geometry
# ---------------------------------------------------------------------------

class TestGenerateChunk:
    def test_fills_a_chunk_matching_desktops_terrain_height(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_seed = 42
            scene._bw_generate_chunk(0, 0)

            x, y = 3, 3
            h = terrain_height(42, x, y)   # same hash formula -- see the
            # module docstring on why Kivy's _bw_hash01 happens to match
            # desktop's, even though it isn't required to.
            assert scene._bw_blocks.get((x, y, h - 1)) == "grass"
            assert scene._bw_blocks.get((x, y, h)) is None

    def test_no_op_without_a_seed(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_generate_chunk(0, 0)
            assert scene._bw_blocks == {}

    def test_does_not_overwrite_a_present_chunk(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_seed = 42
            scene._bw_set_block(0, 0, 0, "gold_block")
            scene._bw_generate_chunk(0, 0)
            assert scene._bw_blocks[(0, 0, 0)] == "gold_block"


class TestEnsureChunksLoaded:
    def test_generates_chunks_within_radius(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_seed = 1
            scene._bw_ensure_chunks_loaded(0, 0, scene.BW_CHUNK_SIZE)
            assert scene._bw_generated.get((0, 0)) is True

    def test_no_op_without_a_seed(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_ensure_chunks_loaded(0, 0, 50)
            assert scene._bw_blocks == {}


class TestLoadBlockWorldDualFormat:
    def test_loads_old_list_shape_with_no_seed(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_load_block_world([{"x": 1, "y": 1, "z": 0, "type": "stone"}])
            assert scene._bw_blocks[(1, 1, 0)] == "stone"
            assert scene._bw_seed is None

    def test_loads_new_seeded_dict_shape(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_load_block_world(
                {"seed": 9, "blocks": [{"x": 2, "y": 2, "z": 0, "type": "gold_block"}]})
            assert scene._bw_blocks[(2, 2, 0)] == "gold_block"
            assert scene._bw_seed == 9
            # The loaded chunk must be marked present -- it must never be
            # silently regenerated over.
            assert scene._bw_generated.get(scene._bw_chunk_key(2, 2)) is True


class TestRenderTriggersGeneration:
    def test_render_block_world_generates_chunks_around_the_camera(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_seed = 5
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(
                camera_object="", eye_height=0.5, render_distance=8)
            scene.block_world_camera["camera_instance"] = cam

            assert scene._bw_blocks == {}
            scene._render_block_world()
            assert scene._bw_blocks != {}

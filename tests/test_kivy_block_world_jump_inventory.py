"""Kivy export codegen/execution parity for Block World's jump/gravity
(Tier 7a), inventory-with-counts (Tier 7c), and per-type protection
(Tier 7b) -- the "Section A" export-parity units of
docs/REMAINING_WORK_2026-08-15.md.

Reuses tests/test_kivy_block_world.py's own stub-kivy execution harness
(_stub_kivy_env/_scene_class/_blank_scene/_default_cfg/_FakeInst) so the
real generated `_bw_apply_gravity`/`_bw_jump`/`_bw_place_block`/
`_bw_break_block`/`_bw_set_block_protection` methods run against controlled
geometry -- no Kivy installation or GL context needed, matching this
extension's established test discipline.
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

def test_enable_block_world_view_bakes_gravity_and_inventory_defaults():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("enable_block_world_view", {}, "create")
    assert "'gravity': 0.0" in code
    assert "'vz': 0.0" in code
    assert "'inventory': False" in code


def test_enable_block_world_view_bakes_gravity_and_inventory_on():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "enable_block_world_view", {"gravity": "0.05", "inventory": "true"}, "create")
    assert "'gravity': 0.05" in code
    assert "'inventory': True" in code


def test_apply_gravity_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("apply_gravity", {}, "step")
    assert code == "self.scene._bw_apply_gravity(self)"


def test_jump_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("jump", {"speed": "0.5"}, "keyboard_press")
    assert code == "self.scene._bw_jump(self, 0.5)"


def test_set_block_protection_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_block_protection",
        {"block_type": "diamond_block", "required_key": "gold_block"}, "create")
    assert code == "self.scene._bw_set_block_protection('diamond_block', 'gold_block')"


def test_draw_block_world_hud_codegen_passes_inventory():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("draw_block_world_hud", {}, "draw")
    assert "getattr(self, 'block_inventory', None)))" in code


# ---------------------------------------------------------------------------
# End-to-end export compiles
# ---------------------------------------------------------------------------

def test_obj_person_source_and_scene_compile_with_new_methods(exported):
    scene_file = next(f for f in (exported / "scenes").glob("*.py")
                      if "_bw_apply_gravity" in f.read_text(encoding="utf-8"))
    scene = scene_file.read_text(encoding="utf-8")
    for name in ("_bw_apply_gravity", "_bw_jump", "_bw_set_block_protection"):
        assert f"def {name}(" in scene
    compile(scene, scene_file.name, "exec")


# ---------------------------------------------------------------------------
# Real execution harness -- jump/gravity
# ---------------------------------------------------------------------------

class TestGravityLegacyUnchanged:
    def test_move_and_collide_without_gravity_still_snaps_down_instantly(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_blocks = {(2, 2, 0): "stone"}  # ground_layer(2,2) == 1
            scene.block_world_camera = _default_cfg(z_layer=1)
            mover = _FakeInst(64, scene.room_height - 64 - 32, 32, 32)
            scene.block_world_camera["camera_instance"] = mover
            scene.instances = [mover]
            # Move east onto an all-air column (ground == 0).
            scene._bw_move_and_collide(mover, dx=32, dy=0, collide=True)
            assert scene.block_world_camera["z_layer"] == 0  # snapped instantly

    def test_apply_gravity_is_a_noop_without_gravity_configured(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(z_layer=5.0, gravity=0.0)
            mover = _FakeInst(0, 0, 32, 32)
            scene.block_world_camera["camera_instance"] = mover
            scene.instances = [mover]
            scene._bw_apply_gravity(mover)
            assert scene.block_world_camera["z_layer"] == 5.0


class TestJumpArc:
    def test_full_arc_rises_then_lands(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(z_layer=0.0, gravity=0.04, vz=0.0)
            mover = _FakeInst(0, 0, 32, 32)
            scene.block_world_camera["camera_instance"] = mover
            scene.instances = [mover]

            scene._bw_jump(mover, 0.35)
            assert scene.block_world_camera["vz"] == 0.35

            heights = []
            for _ in range(200):
                scene._bw_apply_gravity(mover)
                heights.append(scene.block_world_camera["z_layer"])
                if scene.block_world_camera["vz"] == 0.0 and scene.block_world_camera["z_layer"] == 0.0:
                    break

            assert max(heights) > 0.0
            assert scene.block_world_camera["z_layer"] == 0.0
            assert scene.block_world_camera["vz"] == 0.0

    def test_jump_while_airborne_is_refused(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(z_layer=0.0, gravity=0.04, vz=0.0)
            mover = _FakeInst(0, 0, 32, 32)
            scene.block_world_camera["camera_instance"] = mover
            scene.instances = [mover]

            scene._bw_jump(mover, 0.35)
            first_vz = scene.block_world_camera["vz"]
            scene._bw_jump(mover, 0.35)
            assert scene.block_world_camera["vz"] == first_vz


class TestFallingOffALedge:
    def test_walking_off_a_ledge_in_gravity_mode_does_not_snap_down(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene._bw_blocks = {(2, 2, 0): "stone"}  # ground_layer(2,2) == 1
            scene.block_world_camera = _default_cfg(z_layer=1.0, gravity=0.04, vz=0.0)
            mover = _FakeInst(64, scene.room_height - 64 - 32, 32, 32)
            scene.block_world_camera["camera_instance"] = mover
            scene.instances = [mover]

            scene._bw_move_and_collide(mover, dx=32, dy=0, collide=True)
            assert scene.block_world_camera["z_layer"] == 1.0  # not snapped down


# ---------------------------------------------------------------------------
# Real execution harness -- inventory + protection
# ---------------------------------------------------------------------------

class TestInventory:
    def test_break_and_place_round_trip_with_inventory_on(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5, inventory=True)
            scene.block_world_camera["camera_instance"] = cam

            scene._bw_set_block(2, 1, 0, "stone")
            scene._bw_break_block(cam, 5)
            assert scene._bw_get_block(2, 1, 0) is None
            assert cam.block_inventory == {"stone": 1}

            scene._bw_place_block(cam, "stone", 5)
            assert scene._bw_get_block(2, 1, 0) == "stone"
            assert cam.block_inventory == {"stone": 0}

    def test_place_refused_without_stock(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5, inventory=True)
            scene.block_world_camera["camera_instance"] = cam

            scene._bw_place_block(cam, "stone", 5)
            assert scene._bw_get_block(2, 1, 0) is None

    def test_inventory_off_is_unlimited_and_untracked(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5, inventory=False)
            scene.block_world_camera["camera_instance"] = cam

            scene._bw_place_block(cam, "stone", 5)
            assert scene._bw_get_block(2, 1, 0) == "stone"
            assert getattr(cam, "block_inventory", None) is None


class TestProtection:
    def test_breaking_a_protected_block_without_the_key_is_refused(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5, inventory=True)
            scene.block_world_camera["camera_instance"] = cam
            scene._bw_set_block(2, 1, 0, "diamond_block")

            scene._bw_set_block_protection("diamond_block", "gold_block")
            scene._bw_break_block(cam, 5)
            assert scene._bw_get_block(2, 1, 0) == "diamond_block"

    def test_breaking_with_the_key_succeeds_and_does_not_consume_it(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5, inventory=True)
            scene.block_world_camera["camera_instance"] = cam
            scene._bw_set_block(2, 1, 0, "diamond_block")
            cam.block_inventory = {"gold_block": 1}

            scene._bw_set_block_protection("diamond_block", "gold_block")
            scene._bw_break_block(cam, 5)
            assert scene._bw_get_block(2, 1, 0) is None
            assert cam.block_inventory["gold_block"] == 1  # unconsumed

"""Kivy export codegen/execution parity for Block World's Tier 7b
mine-to-collect reward: set_block_reward + break_block's payout.

Found missing during Tier 8 crafting's own Kivy port (2026-09-09, logged
in TODO.md's Block World section rather than fixed there -- a different
action, out of that plan's scope) and picked up here: desktop and HTML5
both had set_block_reward from the start, but neither a
_bw_set_block_reward scene method nor a _cg_set_block_reward codegen
entry ever existed on the Kivy target, so the action fell through to the
generic unsupported-action no-op with nothing to catch it (this file
didn't exist).

Reuses tests/test_kivy_block_world.py's own stub-kivy execution harness
(_stub_kivy_env/_scene_class/_blank_scene/_default_cfg/_FakeInst) --
_stub_kivy_env's "main" module stub now also records set_score(value,
relative) calls on main.score_calls, since the reward payout (like
desktop's real game_runner.score += int(points)) goes through
`from main import set_score`, the same lazy-import pattern every other
score/lives/health action on this export target already uses.
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

def test_set_block_reward_codegen():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_block_reward", {"block_type": "diamond_block", "points": "10"}, "create")
    assert code == "self.scene._bw_set_block_reward('diamond_block', 10)"


def test_obj_person_source_and_scene_compile_with_the_new_method(exported):
    scene_file = next(f for f in (exported / "scenes").glob("*.py")
                      if "_bw_set_block_reward" in f.read_text(encoding="utf-8"))
    scene = scene_file.read_text(encoding="utf-8")
    assert "def _bw_set_block_reward(" in scene
    compile(scene, scene_file.name, "exec")


# ---------------------------------------------------------------------------
# Real execution harness
# ---------------------------------------------------------------------------

class TestSetBlockRewardRegistersReward:
    def test_registers_a_reward_entry(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_block_reward("diamond_block", 10)
            assert scene.block_world_camera["rewards"] == {"diamond_block": 10.0}

    def test_multiple_calls_accumulate_separate_entries(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_block_reward("diamond_block", 10)
            scene._bw_set_block_reward("gold_block", 100)
            assert scene.block_world_camera["rewards"] == {
                "diamond_block": 10.0, "gold_block": 100.0}

    def test_unknown_block_type_is_ignored(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg()
            scene._bw_set_block_reward("not_a_real_block", 10)
            assert scene.block_world_camera.get("rewards", {}) == {}

    def test_without_an_active_view_is_a_noop(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            scene.block_world_camera = _default_cfg(enabled=False)
            scene._bw_set_block_reward("diamond_block", 10)
            assert scene.block_world_camera.get("rewards") is None


class TestBreakBlockPaysOutRewards:
    def test_breaking_a_rewarded_block_calls_set_score(self, exported):
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

            assert scene._bw_get_block(2, 1, 0) is None
            assert sys.modules["main"].score_calls == [(10, True)]

    def test_unrewarded_block_types_award_nothing(self, exported):
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5)
            scene.block_world_camera["camera_instance"] = cam
            scene._bw_set_block(2, 1, 0, "stone")
            scene._bw_set_block_reward("diamond_block", 10)

            scene._bw_break_block(cam, 5)

            assert scene._bw_get_block(2, 1, 0) is None  # still broken, just no payout
            assert sys.modules["main"].score_calls == []

    def test_no_reward_registered_leaves_break_block_unchanged(self, exported):
        """Backward compatibility: a project that never calls
        set_block_reward sees zero behaviour change."""
        with _stub_kivy_env(exported):
            cls = _scene_class(exported)
            scene = _blank_scene(cls)
            cam = _FakeInst(32, scene.room_height - 32 - 32, 32, 32, facing=0.0)
            scene.instances = [cam]
            scene.block_world_camera = _default_cfg(eye_height=0.5)
            scene.block_world_camera["camera_instance"] = cam
            scene._bw_set_block(2, 1, 0, "diamond_block")

            scene._bw_break_block(cam, 5)

            assert scene._bw_get_block(2, 1, 0) is None
            assert sys.modules["main"].score_calls == []

    def test_a_refused_break_pays_out_nothing(self, exported):
        """Protection wins first: a rewarded block that's ALSO protected
        pays out only once actually mined, not on a swing that no-ops."""
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

            assert scene._bw_get_block(2, 1, 0) == "diamond_block"  # still there
            assert sys.modules["main"].score_calls == []

    def test_breaking_multiple_rewarded_blocks_calls_set_score_each_time(self, exported):
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

            assert scene._bw_get_block(2, 1, 0) is None
            assert scene._bw_get_block(3, 1, 0) is None
            assert sys.modules["main"].score_calls == [(10, True), (100, True)]

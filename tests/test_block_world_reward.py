"""Mine-to-collect block rewards: set_block_reward registers
{block_type: points} pairs on the room's camera config; break_block awards
the points AFTER a successful removal (is_breakable + protection already
passed) -- a scored counterpart to set_block_protection's tool/key gate,
same call-once-per-type pattern, same camera-config storage.

Why this exists: the promo game's block-world level originally awarded
"gem" score by walking near a free-standing decorative block (proximity
check in the player's step event), because this engine's move_and_collide
auto-steps the player UP onto anything at most one block taller than the
surrounding floor -- so a lone block placed on the walkable surface is
never a wall you bump into or aim Break Block at, it's just a stair the
player climbs over without noticing. Reported by the user as "cannot
destroy the diamond block with Space", since that's the interaction
GameMaker-taught students actually expect for a visible ore/gem block.
set_block_reward makes that expectation real: embed the reward block in a
wall face (something the player must aim at and mine through, same as any
other terrain block) and breaking it pays out automatically.

Every project that never calls set_block_reward sees zero change to
break_block's behaviour (no entries in cfg["rewards"], so the payout is
never checked) -- backward compatible, same pattern as protection (7b),
gravity (7a), and inventory (7c) before it.
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
from extensions.block_world.state import block_world_state, get_block, set_block  # noqa: E402

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}
        self.score = 0
        self.show_score_in_caption = False


def _world(inventory=True):
    room = GameRoom("reward", {"width": 40 * CELL, "height": 40 * CELL},
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


def _run(room, camera, action, runner=None, **params):
    """runner=None creates a fresh one-shot ActionExecutor/_Runner (matching
    test_block_world_protection.py's pattern); pass an existing runner back
    in to accumulate state (score) across several calls in one test."""
    if runner is None:
        runner = _Runner(room)
    ex = ActionExecutor(game_runner=runner)
    load_all_plugins(ex)
    camera.action_executor = ex
    ex.action_handlers[action](camera, params)
    return runner


class TestSetBlockRewardRegistersPairing:
    def test_registers_a_reward_entry(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        assert cfg["rewards"] == {"diamond_block": 10}

    def test_multiple_calls_accumulate_separate_entries(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        _run(room, camera, "set_block_reward",
             block_type="gold_block", points=100)
        assert cfg["rewards"] == {"diamond_block": 10, "gold_block": 100}

    def test_unknown_block_type_is_ignored(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_reward",
             block_type="not_a_real_block", points=10)
        assert cfg.get("rewards", {}) == {}

    def test_without_an_active_view_is_a_noop(self):
        room, camera, cfg = _world()
        cfg["enabled"] = False
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        assert cfg.get("rewards") is None


class TestBreakBlockPaysOutRewards:
    def test_breaking_a_rewarded_block_awards_score(self):
        room, camera, cfg = _world(inventory=False)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        runner = _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None
        assert runner.score == 10
        assert runner.show_score_in_caption is True

    def test_unrewarded_block_types_award_nothing(self):
        room, camera, cfg = _world(inventory=False)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        runner = _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None  # still broken, just no payout
        assert runner.score == 0

    def test_no_reward_registered_leaves_break_block_unchanged(self):
        """Backward compatibility: a project that never calls
        set_block_reward sees zero behaviour change."""
        room, camera, cfg = _world(inventory=False)
        set_block(room, 1, 0, 0, "diamond_block")
        runner = _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None
        assert runner.score == 0

    def test_a_refused_break_pays_out_nothing(self):
        """Protection wins first: a rewarded block that's ALSO protected
        pays out only once actually mined, not on a swing that no-ops."""
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        runner = _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) == "diamond_block"  # still there
        assert runner.score == 0

    def test_breaking_multiple_rewarded_blocks_accumulates_score(self):
        room, camera, cfg = _world(inventory=False)
        set_block(room, 1, 0, 0, "diamond_block")
        set_block(room, 2, 0, 0, "gold_block")
        _run(room, camera, "set_block_reward",
             block_type="diamond_block", points=10)
        _run(room, camera, "set_block_reward",
             block_type="gold_block", points=100)
        # Same runner reused across both breaks so score accumulates --
        # the ray keeps facing the same direction, so once (1,0,0) is
        # cleared the second break_block call naturally reaches (2,0,0).
        runner = _run(room, camera, "break_block")
        _run(room, camera, "break_block", runner=runner)
        assert get_block(room, 1, 0, 0) is None
        assert get_block(room, 2, 0, 0) is None
        assert runner.score == 110


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))

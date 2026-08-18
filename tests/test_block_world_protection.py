"""Per-type block protection (Tier 7b, docs/DEFERRED_GAPS_2026_PLAN.md,
option 2 -- a required-key/tool gate, chosen by explicit ask over the two
alternatives discussed: un-placeable-on and a per-player permission list).

set_block_protection registers {protected_type: required_key_type} pairs on
the room's camera config; break_block checks the pairing AFTER
state.is_breakable (an absolutely unbreakable block, e.g. obsidian, is
unaffected either way) and requires the calling instance's inventory
(Tier 7c) to hold at least one of the required key -- the key GATES the
break, it is not itself consumed.

Every project that never calls set_block_protection sees zero change to
break_block's behaviour (no entries in cfg["protection"], so the gate is
never checked) -- deliberately backward compatible, same pattern as
gravity (7a) and inventory (7c) before it.
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


def _world(inventory=True):
    room = GameRoom("protection", {"width": 40 * CELL, "height": 40 * CELL},
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


class TestSetBlockProtectionRegistersPairing:
    def test_registers_a_protection_entry(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        assert cfg["protection"] == {"diamond_block": "gold_block"}

    def test_multiple_calls_accumulate_separate_entries(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        _run(room, camera, "set_block_protection",
             block_type="mese_block", required_key="coal_block")
        assert cfg["protection"] == {
            "diamond_block": "gold_block", "mese_block": "coal_block"}

    def test_unknown_block_type_is_ignored(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_protection",
             block_type="not_a_real_block", required_key="gold_block")
        assert cfg.get("protection", {}) == {}

    def test_unknown_required_key_is_ignored(self):
        room, camera, cfg = _world()
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="not_a_real_block")
        assert cfg.get("protection", {}) == {}

    def test_without_an_active_view_is_a_noop(self):
        room, camera, cfg = _world()
        cfg["enabled"] = False
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        assert cfg.get("protection") is None


class TestBreakBlockRespectsProtection:
    def test_breaking_without_the_key_is_refused(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) == "diamond_block"  # still there
        assert getattr(camera, "block_inventory", None) is None  # no pickup

    def test_breaking_with_the_key_in_inventory_succeeds(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        camera.block_inventory = {"gold_block": 1}
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None
        assert camera.block_inventory["diamond_block"] == 1  # picked up

    def test_the_key_is_not_consumed_by_breaking(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        camera.block_inventory = {"gold_block": 1}
        _run(room, camera, "break_block")
        assert camera.block_inventory["gold_block"] == 1  # unchanged -- a tool

    def test_having_a_different_key_type_does_not_satisfy_the_requirement(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        camera.block_inventory = {"coal_block": 99}
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) == "diamond_block"

    def test_unprotected_block_types_are_unaffected(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None  # stone was never protected

    def test_absolutely_unbreakable_still_wins_over_protection(self):
        """is_breakable is checked FIRST -- protection layers on top of it,
        it does not replace it. Even WITH the key, obsidian stays put."""
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "obsidian")
        _run(room, camera, "set_block_protection",
             block_type="obsidian", required_key="gold_block")
        camera.block_inventory = {"gold_block": 99}
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) == "obsidian"

    def test_no_protection_registered_leaves_break_block_unchanged(self):
        """Backward compatibility: a project that never calls
        set_block_protection sees zero behaviour change."""
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None
        assert camera.block_inventory == {"diamond_block": 1}


class TestProtectionWithoutInventoryIsPermanentlyUnbreakable:
    """Documented, intentional consequence -- see set_block_protection's
    own docstring: without Inventory on, the calling instance never has a
    block_inventory to check against, so the requirement can never be met."""

    def test_protected_block_cannot_be_broken_without_inventory_enabled(self):
        room, camera, cfg = _world(inventory=False)
        set_block(room, 1, 0, 0, "diamond_block")
        _run(room, camera, "set_block_protection",
             block_type="diamond_block", required_key="gold_block")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) == "diamond_block"

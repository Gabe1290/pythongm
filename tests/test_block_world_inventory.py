"""Inventory with counts (Tier 7c, docs/DEFERRED_GAPS_2026_PLAN.md):
pickup-on-break, consume-on-place, and slot-count rendering in the hotbar
HUD -- on top of the existing fixed-slot hotbar (state.py's DEFAULT_HOTBAR,
handlers.py's select_hotbar_slot), which stays a simple slot picker.

Opt-in via enable_block_world_view's `inventory` parameter, default False:
every project that predates Tier 7c keeps place_block's original unlimited
creative-mode placing and break_block's original "just removes it" behaviour,
completely unchanged (tested explicitly below). Crafting remains out of
scope -- see state.py's DEFAULT_HOTBAR comment.
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
from extensions.block_world.hud import build_block_world_hud_commands  # noqa: E402

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


def _world(inventory=False):
    room = GameRoom("inventory", {"width": 40 * CELL, "height": 40 * CELL},
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


class TestLegacyBehaviourUnchangedWhenInventoryIsOff:
    def test_break_block_never_creates_an_inventory(self):
        room, camera, cfg = _world(inventory=False)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None  # still broke it
        assert getattr(camera, "block_inventory", None) is None

    def test_place_block_is_still_unlimited(self):
        room, camera, cfg = _world(inventory=False)
        for _ in range(3):
            # Nothing to break/pick up, but placement must not be gated.
            room2, camera2, _cfg2 = _world(inventory=False)
            _run(room2, camera2, "place_block", block="stone")
            assert get_block(room2, 1, 0, 0) == "stone"


class TestPickupOnBreak:
    def test_breaking_adds_one_to_inventory(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) is None
        assert camera.block_inventory == {"stone": 1}

    def test_breaking_multiple_of_the_same_type_accumulates(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "break_block")
        # Camera stays put (nothing left to walk into); place a new stone
        # one cell further and break that too.
        set_block(room, 2, 0, 0, "stone")
        _run(room, camera, "break_block", reach=5)
        assert camera.block_inventory == {"stone": 2}

    def test_unbreakable_block_gives_nothing(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "obsidian")
        _run(room, camera, "break_block")
        assert get_block(room, 1, 0, 0) == "obsidian"  # still there
        assert getattr(camera, "block_inventory", None) is None  # nothing picked up

    def test_different_block_types_track_separately(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "break_block")
        set_block(room, 2, 0, 0, "cobble")
        _run(room, camera, "break_block")
        assert camera.block_inventory == {"stone": 1, "cobble": 1}


class TestConsumeOnPlace:
    def test_placing_without_inventory_is_refused(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "place_block", block="stone")
        assert get_block(room, 1, 0, 0) is None  # nothing placed
        assert getattr(camera, "block_inventory", None) is None

    def test_placing_with_inventory_consumes_one(self):
        room, camera, cfg = _world(inventory=True)
        camera.block_inventory = {"stone": 2}
        _run(room, camera, "place_block", block="stone")
        assert get_block(room, 1, 0, 0) == "stone"
        assert camera.block_inventory == {"stone": 1}

    def test_placing_the_last_one_then_refuses_the_next(self):
        room, camera, cfg = _world(inventory=True)
        camera.block_inventory = {"stone": 1}
        _run(room, camera, "place_block", block="stone")
        assert camera.block_inventory == {"stone": 0}

        room2, camera2, _cfg2 = _world(inventory=True)
        camera2.block_inventory = {"stone": 0}
        _run(room2, camera2, "place_block", block="stone")
        assert get_block(room2, 1, 0, 0) is None  # refused, no stone left
        assert camera2.block_inventory == {"stone": 0}  # not driven negative

    def test_having_a_different_block_type_does_not_satisfy_placement(self):
        room, camera, cfg = _world(inventory=True)
        camera.block_inventory = {"cobble": 5}
        _run(room, camera, "place_block", block="stone")
        assert get_block(room, 1, 0, 0) is None
        assert camera.block_inventory == {"cobble": 5}  # untouched


class TestBreakThenPlaceRoundTrip:
    def test_break_and_place_the_same_block_elsewhere(self):
        room, camera, cfg = _world(inventory=True)
        set_block(room, 1, 0, 0, "stone")
        _run(room, camera, "break_block")
        assert camera.block_inventory == {"stone": 1}

        _run(room, camera, "place_block", block="stone")
        assert get_block(room, 1, 0, 0) == "stone"
        assert camera.block_inventory == {"stone": 0}


class TestHudCountRendering:
    def test_counts_none_draws_no_count_labels(self):
        cmds = build_block_world_hud_commands(
            screen_width=640, screen_height=480, hotbar=["stone", "cobble"],
            selected_index=0, slot_size=40, gap=6, margin_bottom=16,
            back_color="#202020", border_color="#ffffff",
            selected_color="#ffd040", text_color="#ffffff",
            crosshair_size=12, crosshair_color="#ffffff", counts=None)
        # Two rectangles + one label per slot (no count) + 2 crosshair lines.
        text_cmds = [c for c in cmds if c["type"] == "text"]
        assert len(text_cmds) == 2  # just the block-type labels

    def test_counts_dict_adds_one_label_per_slot(self):
        cmds = build_block_world_hud_commands(
            screen_width=640, screen_height=480, hotbar=["stone", "cobble"],
            selected_index=0, slot_size=40, gap=6, margin_bottom=16,
            back_color="#202020", border_color="#ffffff",
            selected_color="#ffd040", text_color="#ffffff",
            crosshair_size=12, crosshair_color="#ffffff",
            counts={"stone": 3, "cobble": 0})
        text_cmds = [c for c in cmds if c["type"] == "text"]
        assert len(text_cmds) == 4  # label + count per slot
        count_texts = {c["text"] for c in text_cmds} - {"ston", "cobb"}
        assert count_texts == {"3", "0"}

    def test_missing_block_type_in_counts_renders_zero(self):
        cmds = build_block_world_hud_commands(
            screen_width=640, screen_height=480, hotbar=["stone"],
            selected_index=0, slot_size=40, gap=6, margin_bottom=16,
            back_color="#202020", border_color="#ffffff",
            selected_color="#ffd040", text_color="#ffffff",
            crosshair_size=12, crosshair_color="#ffffff", counts={})
        text_cmds = [c for c in cmds if c["type"] == "text"]
        assert any(c["text"] == "0" for c in text_cmds)


class TestDrawHudActionPassesCounts:
    def test_no_inventory_yet_draws_without_counts(self):
        room, camera, cfg = _world(inventory=True)
        _run(room, camera, "draw_block_world_hud")
        text_cmds = [c for c in camera._draw_queue if c["type"] == "text"]
        # Only block-type labels, since block_inventory was never touched.
        from extensions.block_world.state import DEFAULT_HOTBAR
        assert len(text_cmds) == len(DEFAULT_HOTBAR)

    def test_with_inventory_draws_counts_too(self):
        room, camera, cfg = _world(inventory=True)
        from extensions.block_world.state import DEFAULT_HOTBAR
        camera.block_inventory = {DEFAULT_HOTBAR[0]: 5}
        _run(room, camera, "draw_block_world_hud")
        text_cmds = [c for c in camera._draw_queue if c["type"] == "text"]
        assert len(text_cmds) == 2 * len(DEFAULT_HOTBAR)
        assert any(c["text"] == "5" for c in text_cmds)

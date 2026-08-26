"""GameRoom's spatial grid was built once in __init__, using every
instance's GameInstance.__init__ default 32x32 placeholder dimensions
(_cached_width/_cached_height) -- the real sprite size isn't known until
GameRoom.set_sprites_for_instances runs afterward, and set_sprite() (which
that method calls) updates the cached dimensions WITHOUT touching the
grid: no _grid_dirty flag, no re-add. Any instance whose real collision
size exceeds 32px in either dimension stayed indexed under its
placeholder-sized cell range forever.

Found via the promo game's side-scroller: a 480x32 ground strip (one
instance spanning the whole room width) was registered as if it were
32x32, i.e. into only the grid cell(s) near its origin. get_nearby_
instances (used by both the pre-emptive movement blocker and the
per-frame collision-event detector) correctly scans every cell a QUERY
box overlaps, but a query far enough from the ground's origin — reached
simply by walking right — never touched the one cell the ground was
mistakenly confined to, so the ground stopped blocking or firing
collision events entirely, and gravity pulled the player straight
through the floor.

Fix: set_sprites_for_instances (runtime/game_runner.py) now calls
self.rebuild_spatial_grid() once more after every instance's real
dimensions are known -- the general fix (every instance re-indexed by its
true collision size), not a special case for wide/tall objects.

Verification: constructs a real GameRoom with a 480x32 "ground" instance
and confirms get_nearby_instances finds it from a query point far from
its origin, both directly and via the real collision-blocker path.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def _fake_sprite(width, height):
    from runtime.game_runner import GameSprite
    s = GameSprite.__new__(GameSprite)
    s.width = width
    s.height = height
    s.origin_x = 0
    s.origin_y = 0
    s.bbox_left = 0
    s.bbox_top = 0
    s.bbox_right = width
    s.bbox_bottom = height
    s.frames = []
    s.surface = None
    s.precise = False
    return s


def _room_with_ground_and_player():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameRoom

    room_data = {
        "width": 480, "height": 480,
        "instances": [
            {"object_name": "obj_ground", "x": 0, "y": 448},
            {"object_name": "obj_player", "x": 90, "y": 400},
        ],
    }
    room = GameRoom("rm_test", room_data)

    objects = {
        "obj_ground": {"name": "obj_ground", "sprite": "spr_ground", "solid": True, "events": {}},
        "obj_player": {"name": "obj_player", "sprite": "spr_player", "solid": False,
                        "events": {"collision_with_obj_ground": {"actions": []}}},
    }
    sprites = {
        "spr_ground": _fake_sprite(480, 32),
        "spr_player": _fake_sprite(40, 48),
    }
    room.set_sprites_for_instances(sprites, objects)
    return room


def test_wide_instance_is_reindexed_after_real_dimensions_are_known():
    room = _room_with_ground_and_player()
    ground = next(i for i in room.instances if i.object_name == "obj_ground")
    assert ground._cached_width == 480  # sanity: real size resolved

    # A query far from the ground's origin (x=0) must still find it, now
    # that the grid was rebuilt with the real 480-wide size.
    nearby = room.get_nearby_instances(400, 448, 40, 48)
    assert ground in nearby


def test_movement_blocker_still_blocks_far_from_the_wide_instances_origin():
    """End-to-end: the actual collision-blocking path a falling player
    goes through, queried from far along a wide solid strip."""
    from runtime.game_runner import GameRunner

    room = _room_with_ground_and_player()
    player = next(i for i in room.instances if i.object_name == "obj_player")

    player._x = 400.0
    player._y = 395.0  # currently clear of the ground (box ends at 443, top at 448)
    player.intended_x = 400.0
    player.intended_y = 415.0  # one frame's fall crosses into [448, 463)

    objects = {
        "obj_ground": {"name": "obj_ground", "sprite": "spr_ground", "solid": True, "events": {}},
        "obj_player": {"name": "obj_player", "sprite": "spr_player", "solid": False,
                        "events": {"collision_with_obj_ground": {"actions": []}}},
    }

    runner = GameRunner.__new__(GameRunner)
    runner.current_room = room
    runner._objects_data = objects

    can_move, blocker = runner.check_movement_collision_with_blocker(player, objects)
    assert can_move is False
    assert blocker is not None and blocker.object_name == "obj_ground"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))

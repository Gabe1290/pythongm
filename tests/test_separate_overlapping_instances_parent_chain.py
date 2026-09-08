"""L4, docs/FULL_AUDIT_2026-09-07.md: separate_overlapping_instances
ignored the parent chain.

CollisionMixin.separate_overlapping_instances only pushes two overlapping
solid instances apart when there is an authored collision event between
them. It found that by testing `other_instance.object_name in
collision_targets` directly -- but collision_targets is keyed by the
LITERAL target name from `collision_with_<target>`, and every other
collision path in runtime/collision.py (the movement blocker in
check_collision_at_position, the event dispatcher itself) resolves that
target through the parent chain via _object_matches_target, so an object
that inherits from the named target also matches. A plain membership
test missed exactly that case: a "collision_with_obj_wall" event and an
obj_wall_brick instance (parent: obj_wall) never separated, even though
the collision event between them fires correctly -- a solid child object
could be walked straight through the wall without ever being pushed back.

Mirrors tests/test_spatial_grid_rebuild_after_sprites.py's real-GameRoom
setup (room_data -> GameRoom -> set_sprites_for_instances), which is what
actually populates _collision_targets/._cached_width/.sprite the way a
real project does -- a hand-built instance would risk missing one of
those and masking the bug for the wrong reason.
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


OBJECTS = {
    "obj_wall": {"name": "obj_wall", "sprite": "spr_block", "solid": True, "events": {}},
    # A child of obj_wall -- no "collision_with_obj_wall_brick" event exists
    # anywhere; the only authored event names the PARENT.
    "obj_wall_brick": {"name": "obj_wall_brick", "parent": "obj_wall",
                        "sprite": "spr_block", "solid": True, "events": {}},
    "obj_player": {"name": "obj_player", "sprite": "spr_block", "solid": False,
                    "events": {"collision_with_obj_wall": {"actions": []}}},
}


def _room_with_player_overlapping_wall_child():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameRoom

    room_data = {
        "width": 200, "height": 200,
        "instances": [
            {"object_name": "obj_wall_brick", "x": 32, "y": 0},
            # Overlaps the brick by 24px on the left edge.
            {"object_name": "obj_player", "x": 8, "y": 0},
        ],
    }
    room = GameRoom("rm_test", room_data)
    sprites = {"spr_block": _fake_sprite(32, 32)}
    room.set_sprites_for_instances(sprites, OBJECTS)
    return room


def _runner_for(room):
    from runtime.game_runner import GameRunner
    runner = GameRunner.__new__(GameRunner)
    runner.current_room = room
    runner._objects_data = OBJECTS
    return runner


def test_solid_child_of_the_collision_target_gets_separated():
    room = _room_with_player_overlapping_wall_child()
    player = next(i for i in room.instances if i.object_name == "obj_player")
    brick = next(i for i in room.instances if i.object_name == "obj_wall_brick")

    player.hspeed = 3.0  # only the mover gets pushed back
    brick.hspeed = 0.0
    brick.vspeed = 0.0

    runner = _runner_for(room)
    runner.separate_overlapping_instances(OBJECTS)

    # Pushed left, flush against the brick's left edge (x=32).
    assert player.x == 0.0

    # No lingering overlap: right edge of the pushed player must sit at or
    # before the brick's left edge.
    assert player.x + player._cached_width <= brick.x


def test_direct_match_still_works_unaffected(monkeypatch=None):
    """Sanity: the fix must not break the ordinary same-name case it
    already handled correctly."""
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameRoom

    room_data = {
        "width": 200, "height": 200,
        "instances": [
            {"object_name": "obj_wall", "x": 32, "y": 0},
            {"object_name": "obj_player", "x": 8, "y": 0},
        ],
    }
    room = GameRoom("rm_test", room_data)
    sprites = {"spr_block": _fake_sprite(32, 32)}
    room.set_sprites_for_instances(sprites, OBJECTS)

    player = next(i for i in room.instances if i.object_name == "obj_player")
    wall = next(i for i in room.instances if i.object_name == "obj_wall")
    player.hspeed = 3.0
    wall.hspeed = 0.0
    wall.vspeed = 0.0

    runner = _runner_for(room)
    runner.separate_overlapping_instances(OBJECTS)

    assert player.x == 0.0

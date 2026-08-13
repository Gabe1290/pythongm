"""Regression tests for Block World Phase 3 -- placing and breaking blocks.

The property worth defending here is AGREEMENT: what `pick_block` selects has
to be the block drawn under the middle of the screen. Picking and rendering
run the same march at the same angle for exactly that reason, so there is a
test below that breaks a block and checks the centre of the rendered frame
actually changed, not merely that the world dict did.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import sys
from pathlib import Path

import pytest

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
from extensions.block_world.state import (  # noqa: E402
    block_world_state, get_block, set_block, column_index,
)
from extensions.block_world.renderer import pick_block, render_block_world_view  # noqa: E402

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room
        self.global_variables = {}


def _world(camera_cell=(0, 0), facing=0.0, enabled=True, **cfg):
    """A room with a camera at a cell centre, block-world view enabled."""
    room = GameRoom("picking", {"width": 40 * CELL, "height": 40 * CELL},
                    action_executor=None)
    camera = GameInstance("obj_person", camera_cell[0] * CELL,
                          camera_cell[1] * CELL, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = camera._cached_height = CELL
    camera.facing_angle = facing
    room.instances.append(camera)
    config = block_world_state(room)["camera"]
    config.update({
        "enabled": enabled, "camera_object": "obj_person", "cell_size": CELL,
        "z_layer": 0, "fov": 66, "render_distance": 20, "columns": 1,
        "wall_textured": False, "wall_color": "#ff0000",
    })
    config.update(cfg)
    return room, camera


def _executor(room):
    ex = ActionExecutor(game_runner=_Runner(room))
    load_all_plugins(ex)
    return ex


def _run(room, action, **params):
    """Dispatch a plugin action as the camera instance would."""
    ex = _executor(room)
    caller = room.instances[0]
    caller.action_executor = ex
    return ex.action_handlers[action](caller, params)


def _pick(room, camera, reach=5):
    """pick_block with the camera resolved exactly as the handler does."""
    cfg = block_world_state(room)["camera"]
    cx, cy = room._sprite_top_left(camera)
    return pick_block(room, cx + camera._cached_width / 2,
                      cy + camera._cached_height / 2,
                      int(cfg["z_layer"]), math.radians(-camera.facing_angle),
                      CELL, reach)


# ---------------------------------------------------------------------------
# pick_block
# ---------------------------------------------------------------------------

class TestPickBlock:
    def test_targets_the_first_block_along_the_ray(self):
        room, camera = _world()
        set_block(room, 3, 0, 0, "stone")
        set_block(room, 5, 0, 0, "brick")  # further -- must be ignored
        target, _placement = _pick(room, camera)
        assert target == (3, 0, 0)

    def test_placement_is_the_cell_just_before_the_target(self):
        room, camera = _world()
        set_block(room, 3, 0, 0, "stone")
        _target, placement = _pick(room, camera)
        assert placement == (2, 0, 0)

    def test_nothing_in_range_places_directly_ahead(self):
        room, camera = _world()
        target, placement = _pick(room, camera)
        assert target is None
        assert placement == (1, 0, 0)

    def test_flush_against_a_block_has_nowhere_to_place(self):
        """The only cell 'before' the target is the one the camera occupies,
        and putting a block there would bury the player."""
        room, camera = _world()
        set_block(room, 1, 0, 0, "stone")
        target, placement = _pick(room, camera)
        assert target == (1, 0, 0)
        assert placement is None

    def test_reach_limits_how_far_you_can_target(self):
        room, camera = _world()
        set_block(room, 6, 0, 0, "stone")
        assert _pick(room, camera, reach=3)[0] is None
        assert _pick(room, camera, reach=8)[0] == (6, 0, 0)

    def test_picks_transparent_blocks_too(self):
        """Glass has to be breakable, so picking must not skip it the way
        the renderer's occlusion test does."""
        room, camera = _world()
        set_block(room, 3, 0, 0, "glass")
        set_block(room, 5, 0, 0, "stone")
        assert _pick(room, camera)[0] == (3, 0, 0)

    def test_only_reaches_the_cameras_own_layer(self):
        """Phase 2b's level camera: the ray runs horizontally at eye height,
        so a block one layer up is not pickable from the ground."""
        room, camera = _world()
        set_block(room, 3, 0, 1, "stone")
        assert _pick(room, camera)[0] is None

        block_world_state(room)["camera"]["z_layer"] = 1
        assert _pick(room, camera)[0] == (3, 0, 1)

    def test_follows_the_facing_angle(self):
        room, camera = _world()
        set_block(room, 0, 3, 0, "stone")  # due south (GM y grows downward)
        assert _pick(room, camera)[0] is None
        camera.facing_angle = 270
        assert _pick(room, camera)[0] == (0, 3, 0)


# ---------------------------------------------------------------------------
# the actions
# ---------------------------------------------------------------------------

class TestPlaceBlock:
    def test_places_against_the_block_you_are_looking_at(self):
        room, _camera = _world()
        set_block(room, 3, 0, 0, "stone")
        _run(room, "place_block", block="brick")
        assert get_block(room, 2, 0, 0) == "brick"

    def test_places_ahead_when_looking_at_nothing(self):
        room, _camera = _world()
        _run(room, "place_block", block="sand")
        assert get_block(room, 1, 0, 0) == "sand"

    def test_defaults_to_stone(self):
        room, _camera = _world()
        _run(room, "place_block")
        assert get_block(room, 1, 0, 0) == "stone"

    def test_an_unknown_block_type_does_nothing(self):
        room, _camera = _world()
        _run(room, "place_block", block="unobtainium")
        assert get_block(room, 1, 0, 0) is None

    def test_never_overwrites_an_existing_block(self):
        room, _camera = _world()
        set_block(room, 1, 0, 0, "stone")   # flush against it
        _run(room, "place_block", block="brick")
        assert get_block(room, 1, 0, 0) == "stone"

    def test_respects_reach(self):
        room, _camera = _world()
        set_block(room, 8, 0, 0, "stone")
        _run(room, "place_block", block="brick", reach=3)
        # Out of reach, so this builds directly ahead instead of against it.
        assert get_block(room, 7, 0, 0) is None
        assert get_block(room, 1, 0, 0) == "brick"

    def test_does_nothing_when_the_view_is_off(self):
        room, _camera = _world(enabled=False)
        _run(room, "place_block", block="brick")
        assert get_block(room, 1, 0, 0) is None

    def test_builds_in_the_direction_the_camera_faces(self):
        """Exercises the HANDLER's own angle conversion. Every other action
        test faces 0, where radians(-a) and radians(a) are the same number,
        so a sign flip in the handler goes unnoticed -- and the pick_block
        tests above can't catch it either, since the helper there has its own
        copy of the conversion."""
        room, _camera = _world(camera_cell=(5, 5), facing=90)  # 90 = north
        _run(room, "place_block", block="brick")
        assert get_block(room, 5, 4, 0) == "brick", "built somewhere other than north"
        assert get_block(room, 5, 6, 0) is None, "built south -- angle sign is inverted"


class TestBreakBlock:
    def test_removes_the_block_in_front(self):
        room, _camera = _world()
        set_block(room, 3, 0, 0, "stone")
        _run(room, "break_block")
        assert get_block(room, 3, 0, 0) is None

    def test_leaves_blocks_behind_the_first_one(self):
        room, _camera = _world()
        set_block(room, 3, 0, 0, "stone")
        set_block(room, 5, 0, 0, "brick")
        _run(room, "break_block")
        assert get_block(room, 5, 0, 0) == "brick"

    def test_nothing_in_range_is_harmless(self):
        room, _camera = _world()
        set_block(room, 9, 0, 0, "stone")
        _run(room, "break_block", reach=4)
        assert get_block(room, 9, 0, 0) == "stone"

    def test_does_nothing_when_the_view_is_off(self):
        room, _camera = _world(enabled=False)
        set_block(room, 3, 0, 0, "stone")
        _run(room, "break_block")
        assert get_block(room, 3, 0, 0) == "stone"

    def test_acts_on_the_cameras_configured_layer(self):
        """Exercises the HANDLER reading z_layer off the camera config.
        Standing on a terrace, you break what is at your eye level, not what
        is at ground level under it."""
        room, _camera = _world(z_layer=1)
        set_block(room, 3, 0, 0, "stone")   # ground, below the eye
        set_block(room, 3, 0, 1, "brick")   # eye level
        _run(room, "break_block")
        assert get_block(room, 3, 0, 1) is None, "did not break at the camera's layer"
        assert get_block(room, 3, 0, 0) == "stone", "broke the wrong layer"


class TestScreenRay:
    """A level camera constrains the forward AXIS to horizontal; it does not
    make every ray horizontal. screen_ray reads out the real 3D ray through
    a pixel, which is what lets picking work in three dimensions with no
    change to the renderer."""

    SW, SH = 800, 600
    FOV = math.radians(66)

    def _ray(self, sx, sy, facing=0.0):
        from extensions.block_world.renderer import screen_ray
        return screen_ray(sx, sy, facing, self.FOV, self.SW, self.SH, CELL)

    def test_the_horizon_is_level(self):
        angle, z_per_px = self._ray(self.SW / 2, self.SH / 2)
        assert angle == pytest.approx(0.0)
        assert z_per_px == pytest.approx(0.0)

    def test_below_the_horizon_descends_and_above_climbs(self):
        assert self._ray(self.SW / 2, self.SH / 2 + 100)[1] < 0
        assert self._ray(self.SW / 2, self.SH / 2 - 100)[1] > 0

    def test_the_centre_column_looks_where_the_camera_faces(self):
        assert self._ray(self.SW / 2, 400, facing=1.2)[0] == pytest.approx(1.2)

    def test_the_vertical_field_of_view_is_bounded_by_the_screen(self):
        """The steepest possible look-down, at the very bottom of the view,
        is about half a cell per cell -- roughly 26 degrees. That IS the
        vertical FOV, and the reason you cannot dig straight down."""
        _angle, z_per_px = self._ray(self.SW / 2, self.SH - 1)
        assert 0.45 < -z_per_px * CELL < 0.55

    def test_it_describes_the_same_ray_as_unproject_to_plane(self):
        """Two ways of asking the same question, so they must agree exactly
        -- otherwise the cursor lands on one cell and the pick acts on
        another."""
        from extensions.block_world.renderer import unproject_to_plane
        for sx, sy in ((400, 400), (200, 500), (700, 350), (150, 380)):
            angle, z_per_px = self._ray(sx, sy, facing=0.4)
            travel = (0 - 0.5) / z_per_px            # ray distance to z = 0
            along = (16 + math.cos(angle) * travel, 16 + math.sin(angle) * travel)
            flat = unproject_to_plane(sx, sy, 0, 16, 16, 0.5, 0.4, self.FOV,
                                      self.SW, self.SH, CELL)
            assert along == pytest.approx(flat)


class TestPickVoxel:
    """3D picking: the general form of pick_block. The face the ray comes
    through decides where a new block goes, and it falls out of tracking the
    previous voxel rather than being special-cased."""

    def _pv(self, room, camera, z_per_px, reach=6, angle=None):
        from extensions.block_world.renderer import pick_voxel
        cfg = block_world_state(room)["camera"]
        cx, cy = room._sprite_top_left(camera)
        if angle is None:
            angle = math.radians(-camera.facing_angle)
        return pick_voxel(room, cx + camera._cached_width / 2,
                          cy + camera._cached_height / 2,
                          int(cfg["z_layer"]) + 0.5, angle, z_per_px,
                          CELL, reach)

    def test_a_level_ray_behaves_like_the_single_layer_walk(self):
        room, camera = _world()
        set_block(room, 3, 0, 0, "stone")
        target, placement = self._pv(room, camera, 0.0)
        assert target == (3, 0, 0)
        assert placement == (2, 0, 0)

    def test_aiming_at_a_top_face_builds_on_top(self):
        """The whole point: point at a block's top and the new one stacks."""
        room, camera = _world(z_layer=1)
        set_block(room, 4, 0, 0, "stone")
        # Shallow descent: crosses z = 1 right as it reaches the block.
        target, placement = self._pv(room, camera, -0.5 / (4 * CELL))
        assert target == (4, 0, 0)
        assert placement == (4, 0, 1), "should have landed on top of it"

    def test_aiming_at_a_side_face_builds_beside(self):
        room, camera = _world(z_layer=1)
        set_block(room, 4, 0, 0, "stone")
        # Steeper: already below the top plane before reaching the block.
        target, placement = self._pv(room, camera, -0.5 / (2 * CELL))
        assert target == (4, 0, 0)
        assert placement[2] == 0 and placement[:2] != (4, 0)

    def test_an_upward_ray_reaches_a_higher_layer(self):
        """Breaking a block above eye level, which the single-layer walk
        could never target."""
        room, camera = _world()
        for z in (0, 1, 2):
            set_block(room, 4, 0, z, "cobble")
        assert self._pv(room, camera, 0.0)[0] == (4, 0, 0)
        assert self._pv(room, camera, 0.5 / (2 * CELL))[0] == (4, 0, 1)

    def test_nothing_in_the_way_hits_nothing(self):
        room, camera = _world()
        assert self._pv(room, camera, -0.01)[0] is None

    def test_it_does_not_tunnel_through_a_block_below(self):
        """A descending ray must stop at the first solid voxel it enters,
        not skip past it because the next column is lower."""
        room, camera = _world(z_layer=2)
        set_block(room, 2, 0, 1, "stone")
        target, _placement = self._pv(room, camera, -1.0 / (2 * CELL))
        assert target == (2, 0, 1)

    def test_an_absurdly_steep_ray_terminates(self):
        """Screen geometry bounds the real slope to about half a cell per
        cell, but nothing stops a caller passing something wilder, and a
        span of layers per column is a loop. z_min/z_max keep it finite."""
        from extensions.block_world.renderer import pick_voxel
        room, camera = _world()
        cx, cy = room._sprite_top_left(camera)
        target, _placement = pick_voxel(
            room, cx + CELL / 2, cy + CELL / 2, 0.5, 0.0, -50.0, CELL, 6,
            z_min=-4, z_max=4)
        assert target is None

    def test_the_clamp_does_not_hide_blocks_inside_the_range(self):
        room, camera = _world()
        set_block(room, 2, 0, -2, "stone")
        from extensions.block_world.renderer import pick_voxel
        cx, cy = room._sprite_top_left(camera)
        target, _placement = pick_voxel(
            room, cx + CELL / 2, cy + CELL / 2, 0.5, 0.0, -1.0 / CELL, CELL, 6,
            z_min=-4, z_max=4)
        assert target == (2, 0, -2)


class TestRefillingHoles:
    """Reported from a playtest: break a block out of a wall and you can
    never put it back.

    A one-cell-thick wall has no cell "before the hit" that IS the hole --
    from either side the ray passes straight through and targets whatever
    stands beyond, so the block always lands past the hole. `pick_block`
    therefore prefers a GAP: an empty cell at the camera's layer with a block
    resting on top of it."""

    # Layout, along the x = 5 column: a wall at y = 5 whose bottom block has
    # been knocked out (only the lintel at z 1-2 remains), and a brick at
    # y = 2 and y = 8 for the ray to reach beyond the hole. Cameras stand at
    # y = 6 (looking north) and y = 4 (looking south) -- both four cells from
    # the brick they face, inside the default reach of five, and neither
    # standing on the other approach's brick.
    NORTH = ((5, 6), 90)
    SOUTH = ((5, 4), 270)

    def _holed_wall(self, approach):
        camera_cell, facing = approach
        room, camera = _world(camera_cell=camera_cell, facing=facing)
        for z in (1, 2):
            set_block(room, 5, 5, z, "cobble")   # lintel over the hole
        set_block(room, 5, 2, 0, "brick")
        set_block(room, 5, 8, 0, "brick")
        return room, camera

    def test_the_hole_is_where_the_block_goes(self):
        room, camera = self._holed_wall(self.NORTH)
        _target, placement = _pick(room, camera)
        assert placement == (5, 5, 0)

    def test_refillable_from_the_other_side_too(self):
        room, camera = self._holed_wall(self.SOUTH)
        _target, placement = _pick(room, camera)
        assert placement == (5, 5, 0)

    def test_place_block_actually_refills_it(self):
        room, _camera = self._holed_wall(self.NORTH)
        _run(room, "place_block", block="cobble")
        assert get_block(room, 5, 5, 0) == "cobble"

    def test_the_target_still_reaches_past_the_hole(self):
        """The crosshair stays on whatever is really behind the gap, and that
        block is still breakable. Only where a NEW block lands changes."""
        room, camera = self._holed_wall(self.NORTH)
        target, _placement = _pick(room, camera)
        assert target == (5, 2, 0)
        _run(room, "break_block")
        assert get_block(room, 5, 2, 0) is None

    def test_an_open_doorway_is_not_a_gap(self):
        """Nothing rests on it, so it is a way through rather than damage,
        and must never be bricked up by accident."""
        room, camera = _world(camera_cell=(5, 6), facing=90)
        set_block(room, 4, 5, 0, "cobble")   # jambs either side, no lintel
        set_block(room, 6, 5, 0, "cobble")
        set_block(room, 5, 2, 0, "brick")    # something beyond, through the door
        target, placement = _pick(room, camera)
        assert target == (5, 2, 0)
        assert placement == (5, 3, 0), "filled in the doorway"

    def test_an_ordinary_wall_still_gets_built_against(self):
        """No gap in the way means the old rule stands."""
        room, camera = _world()
        set_block(room, 3, 0, 0, "stone")
        _target, placement = _pick(room, camera)
        assert placement == (2, 0, 0)

    def test_the_nearest_gap_wins(self):
        room, camera = _world()
        for x in (3, 6):
            set_block(room, x, 0, 1, "cobble")   # two holes, both roofed
        _target, placement = _pick(room, camera, reach=8)
        assert placement == (3, 0, 0)


class TestUnbreakableBlocks:
    """`breakable` is the protection model in full: no modes, no regions,
    one flag consulted in one place. See the edit-mode/play-mode section of
    docs/VOXEL_WORLD_PLAN.md."""

    def test_obsidian_is_the_boundary_material(self):
        from extensions.block_world.state import is_breakable
        assert not is_breakable("obsidian")
        for ordinary in ("stone", "dirt", "glass", "brick", "wool_red"):
            assert is_breakable(ordinary)

    def test_unknown_ids_count_as_breakable(self):
        """A typo must not silently produce indestructible scenery."""
        from extensions.block_world.state import is_breakable
        assert is_breakable("unobtainium")

    def test_break_leaves_an_unbreakable_block_alone(self):
        room, _camera = _world()
        set_block(room, 3, 0, 0, "obsidian")
        _run(room, "break_block")
        assert get_block(room, 3, 0, 0) == "obsidian"

    def test_the_same_swing_removes_an_ordinary_block(self):
        """Control: proves the test above is about the flag, not about the
        break action having quietly stopped working."""
        room, _camera = _world()
        set_block(room, 3, 0, 0, "stone")
        _run(room, "break_block")
        assert get_block(room, 3, 0, 0) is None

    def test_an_unbreakable_block_still_shields_what_is_behind_it(self):
        room, _camera = _world()
        set_block(room, 3, 0, 0, "obsidian")
        set_block(room, 5, 0, 0, "stone")
        _run(room, "break_block")
        _run(room, "break_block")
        assert get_block(room, 3, 0, 0) == "obsidian"
        assert get_block(room, 5, 0, 0) == "stone", "broke through the boundary"

    def test_you_can_still_build_against_one(self):
        """Only breaking is restricted. An unbreakable block is ordinary in
        every other respect -- including being a wall you can build onto."""
        room, _camera = _world()
        set_block(room, 3, 0, 0, "obsidian")
        _run(room, "place_block", block="brick")
        assert get_block(room, 2, 0, 0) == "brick"

    def test_an_unbreakable_type_can_still_be_placed(self):
        """`breakable` is checked in break_block and NOWHERE else. Lining a
        world's edge with the stuff means an author has to be able to put it
        there in the first place."""
        room, _camera = _world()
        _run(room, "place_block", block="obsidian")
        assert get_block(room, 1, 0, 0) == "obsidian"

    def test_it_is_still_targeted(self):
        """The crosshair has to light up on it -- that is the feedback that
        says 'this is here and solid', as opposed to aiming at nothing."""
        room, camera = _world()
        set_block(room, 3, 0, 0, "obsidian")
        target, placement = _pick(room, camera)
        assert target == (3, 0, 0)
        assert placement == (2, 0, 0)


class TestPlacementIsAlwaysAir:
    """place_block writes without re-checking the cell, which is only safe
    because pick_block never returns an occupied one. Pin the invariant."""

    @pytest.mark.parametrize("blocks", [
        [],
        [(3, 0, 0)],
        [(1, 0, 0)],
        [(2, 0, 0), (3, 0, 0)],
        [(1, 0, 0), (2, 0, 0), (3, 0, 0)],
        [(4, 0, 0), (5, 0, 0)],
    ])
    def test_placement_cell_is_empty(self, blocks):
        room, camera = _world()
        for x, y, z in blocks:
            set_block(room, x, y, z, "stone")
        _target, placement = _pick(room, camera)
        if placement is not None:
            assert get_block(room, *placement) is None


# ---------------------------------------------------------------------------
# agreement between picking and rendering
# ---------------------------------------------------------------------------

class TestPickingMatchesWhatIsDrawn:
    def _centre_pixel(self, room):
        screen = pygame.Surface((320, 240))
        render_block_world_view(room, screen)
        return screen.get_at((160, 120))[:3]

    def test_breaking_changes_the_middle_of_the_screen(self):
        """Not just the world dict -- the frame. If picking used a different
        angle or layer from the renderer, this passes on the data and fails
        on the pixels."""
        room, _camera = _world()
        set_block(room, 3, 0, 0, "stone")
        before = self._centre_pixel(room)
        _run(room, "break_block")
        assert self._centre_pixel(room) != before

    def test_placing_changes_the_middle_of_the_screen(self):
        room, _camera = _world()
        before = self._centre_pixel(room)
        _run(room, "place_block", block="stone")
        assert self._centre_pixel(room) != before

    def test_the_wall_revealed_behind_is_the_next_one_along(self):
        """Break the near wall and the far one should be what you now see,
        at its own distance -- i.e. a shorter strip, not the same one."""
        room, _camera = _world()
        set_block(room, 3, 0, 0, "stone")
        set_block(room, 6, 0, 0, "stone")
        screen = pygame.Surface((320, 240))
        render_block_world_view(room, screen)
        floor = tuple(room.parse_color("#3a2f1c"))
        ceiling = tuple(room.parse_color("#87CEEB"))

        def wall_height():
            render_block_world_view(room, screen)
            return sum(1 for y in range(240)
                       if screen.get_at((160, y))[:3] not in (floor, ceiling))

        near = wall_height()
        _run(room, "break_block")
        far = wall_height()
        assert 0 < far < near, "revealed wall should be smaller, not absent"

    def test_a_placed_block_is_visible_immediately(self):
        """set_block has to invalidate the renderer's derived column cache,
        or the world changes and the picture does not."""
        room, _camera = _world()
        column_index(room)  # prime the cache before the world changes
        _run(room, "place_block", block="stone")
        assert (1, 0) in column_index(room)
        screen = pygame.Surface((320, 240))
        render_block_world_view(room, screen)
        assert screen.get_at((160, 120))[:3] != tuple(room.parse_color("#3a2f1c"))


def test_both_actions_are_registered_with_schemas():
    from events.action_types import get_action_type
    load_all_plugins()
    for name in ("place_block", "break_block"):
        schema = get_action_type(name)
        assert schema is not None, "%s missing from ACTION_TYPES" % name
        assert schema.category == "3D View"

    block_param = next(p for p in get_action_type("place_block").parameters
                       if p.name == "block")
    assert block_param.param_type == "choice"
    assert "stone" in block_param.choices and "glass" in block_param.choices

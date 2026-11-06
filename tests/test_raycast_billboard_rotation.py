"""set_billboard_rotation -- Doom/Build-engine "actor rotation" billboards.

A raycast billboard (pickup/monster) used to always draw the same single
camera-facing sprite frame, scaled by distance -- a flat cardboard cutout
with no sense of having real sides. This action gives an instance a sprite
strip of N equally-spaced views of itself; the renderer then picks which
frame to show by the actual angle between the camera and the instance (the
classic Doom monster-rotation trick), so walking a full circle around it
cycles through all N frames exactly once instead of showing the same image
from every angle.

Covers the shared pure function (extensions/raycast_2_5d/renderer.
billboard_rotation_frame -- desktop<->Kivy exact-equality parity lives in
tests/test_raycast_export_parity.py, HTML5 structural parity in
tests/test_html5_raycast.py), the action schema + handler, and a real
pygame-Surface render proving the renderer actually calls it instead of
falling back to the pre-existing image_index-based frame.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()
from runtime.game_runner import GameInstance, GameSprite  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    billboard_rotation_frame, render_raycast_view,
)
from test_raycast_view import _room, _raycast_executor, _dispatch  # noqa: E402

from events.action_types import get_action_type  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()


# ---------------------------------------------------------------------------
# Pure function: billboard_rotation_frame
# ---------------------------------------------------------------------------

class TestBillboardRotationFrame:
    def test_frames_at_most_one_always_returns_zero(self):
        assert billboard_rotation_frame(0, 0, 0.0, 100, 0, 1) == 0
        assert billboard_rotation_frame(0, 0, 90.0, 0, 100, 0) == 0

    def test_front_view_is_frame_zero_regardless_of_facing_angle(self):
        """The camera standing exactly in the direction facing_angle points
        always sees frame 0, by construction -- the documented "front
        view" convention every rotation count must honour."""
        for facing in (0.0, 37.0, 90.0, 180.0, 270.0, 359.0):
            rad = math.radians(-facing)
            cx = 100 + 50 * math.cos(rad)
            cy = 100 + 50 * math.sin(rad)
            assert billboard_rotation_frame(100, 100, facing, cx, cy, 8) == 0

    def test_four_cardinal_views_with_facing_angle_zero(self):
        # Billboard at (100,100) facing GM-east (0); camera due
        # east/south/west/north of it -- a clean cardinal sweep.
        assert billboard_rotation_frame(100, 100, 0.0, 200, 100, 4) == 0  # east
        assert billboard_rotation_frame(100, 100, 0.0, 100, 200, 4) == 1  # south
        assert billboard_rotation_frame(100, 100, 0.0, 0, 100, 4) == 2    # west
        assert billboard_rotation_frame(100, 100, 0.0, 100, 0, 4) == 3    # north

    def test_rotating_facing_angle_shifts_the_mapping(self):
        """Turning the OBJECT (not the camera) by one frame-step's worth of
        angle shifts which frame a fixed camera position sees by exactly
        one frame -- facing_angle and the camera's viewing position are
        independent inputs."""
        cam = (200, 100)  # due east of the billboard at (100, 100)
        assert billboard_rotation_frame(100, 100, 0.0, *cam, 4) == 0
        assert billboard_rotation_frame(100, 100, 90.0, *cam, 4) == 1
        assert billboard_rotation_frame(100, 100, 180.0, *cam, 4) == 2
        assert billboard_rotation_frame(100, 100, 270.0, *cam, 4) == 3

    def test_odd_frame_count(self):
        # 3 frames -> 120 degree steps. Camera due east, facing 0 -> front.
        assert billboard_rotation_frame(0, 0, 0.0, 100, 0, 3) == 0
        # view_rad = atan2(cam_y, cam_x) increasing is a screen-space
        # CLOCKWISE sweep (y grows downward) -- +120 degrees of it is one
        # frame-step for a 3-frame strip.
        rad = math.radians(120.0)
        cx, cy = 100 * math.cos(rad), 100 * math.sin(rad)
        assert billboard_rotation_frame(0, 0, 0.0, cx, cy, 3) == 1

    def test_wraps_cleanly_past_360(self):
        a = billboard_rotation_frame(0, 0, 400.0, 100, 0, 4)   # 400 % 360 = 40
        b = billboard_rotation_frame(0, 0, 40.0, 100, 0, 4)
        assert a == b


# ---------------------------------------------------------------------------
# Action schema + handler
# ---------------------------------------------------------------------------

def test_action_schema_registered():
    action = get_action_type("set_billboard_rotation")
    assert action is not None
    assert action.category == "3D View"
    frames_param = next(p for p in action.parameters if p.name == "frames")
    assert frames_param.default_value == 8


class TestSetBillboardRotationHandler:
    def test_default_frames_is_eight(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_fruit", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_billboard_rotation", inst, {})
        assert inst.billboard_rotation_frames == 8

    def test_explicit_frames(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_fruit", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_billboard_rotation", inst, {"frames": 4})
        assert inst.billboard_rotation_frames == 4

    def test_zero_disables(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_fruit", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_billboard_rotation", inst, {"frames": 0})
        assert inst.billboard_rotation_frames == 0

    def test_negative_clamped_to_zero(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_fruit", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_billboard_rotation", inst, {"frames": -3})
        assert inst.billboard_rotation_frames == 0

    def test_numeric_string_parsed(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_fruit", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_billboard_rotation", inst, {"frames": "6"})
        assert inst.billboard_rotation_frames == 6

    def test_invalid_value_falls_back_to_zero(self):
        ex = _raycast_executor()
        inst = GameInstance("obj_fruit", 0, 0, {}, action_executor=None)
        _dispatch(ex, "set_billboard_rotation", inst, {"frames": "not-a-number"})
        assert inst.billboard_rotation_frames == 0


# ---------------------------------------------------------------------------
# Real render: the renderer actually calls billboard_rotation_frame, not
# just falls back to image_index, and the right frame's pixels land on
# screen -- a real pygame.Surface, pixel-sampled.
# ---------------------------------------------------------------------------

def _rotating_sprited_instance(name, x, y, colors, width=16, height=16):
    """A visible, non-solid instance with a multi-frame sprite strip, one
    solid color per view -- a billboard-rotation candidate."""
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = width
    inst._cached_height = height
    inst.visible = True
    sprite = GameSprite.__new__(GameSprite)
    frames = []
    for color in colors:
        frame = pygame.Surface((width, height))
        frame.fill(color)
        frames.append(frame)
    sprite.frames = frames
    inst.sprite = sprite
    inst.image_index = 0
    return inst


def _centered_top_left(center_x, center_y, width, height):
    return center_x - width / 2.0, center_y - height / 2.0


class TestBillboardRotationRender:
    COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # R G B Y

    def _room_with_camera(self, cam_center, facing_deg, rotation_frames=4):
        room = _room(220, 220)
        bx, by = _centered_top_left(100, 100, 16, 16)
        billboard = _rotating_sprited_instance("obj_fruit", bx, by, self.COLORS)
        billboard.facing_angle = 0.0  # faces GM-east
        if rotation_frames:
            billboard.billboard_rotation_frames = rotation_frames
        room.instances.append(billboard)

        cx, cy = _centered_top_left(cam_center[0], cam_center[1], 16, 16)
        camera = GameInstance("obj_person", cx, cy, {}, action_executor=None)
        camera._cached_width = camera._cached_height = 16
        camera.facing_angle = facing_deg
        room.instances.append(camera)

        raycast_state(room)["camera"] = {
            'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
            'render_distance': 20, 'cell_size': 32, 'columns': 64,
            'floor_color': '#000000', 'ceiling_color': '#000000',
        }
        return room

    def _rendered_colors(self, room):
        screen = pygame.Surface((320, 240))
        render_raycast_view(room, screen)
        w, h = screen.get_size()
        return {screen.get_at((x, h // 2))[:3] for x in range(w)}

    def test_camera_east_sees_front_frame(self):
        room = self._room_with_camera((180, 100), facing_deg=180)
        assert self.COLORS[0] in self._rendered_colors(room)

    def test_camera_south_sees_second_frame(self):
        room = self._room_with_camera((100, 180), facing_deg=90)
        assert self.COLORS[1] in self._rendered_colors(room)

    def test_camera_west_sees_back_frame(self):
        room = self._room_with_camera((20, 100), facing_deg=0)
        assert self.COLORS[2] in self._rendered_colors(room)

    def test_camera_north_sees_fourth_frame(self):
        room = self._room_with_camera((100, 20), facing_deg=270)
        assert self.COLORS[3] in self._rendered_colors(room)

    def test_walking_around_the_object_cycles_through_different_frames(self):
        """The real, user-facing point of this feature: distinct camera
        positions must show visibly different frames, not the same cutout
        from every angle."""
        seen = set()
        for cam_center, facing in (
                ((180, 100), 180), ((100, 180), 90),
                ((20, 100), 0), ((100, 20), 270)):
            room = self._room_with_camera(cam_center, facing_deg=facing)
            seen |= (self._rendered_colors(room) & set(self.COLORS))
        assert len(seen) >= 3, f"too few distinct rotation frames rendered: {seen}"

    def test_rotation_disabled_falls_back_to_image_index(self):
        """billboard_rotation_frames unset (0) -- the pre-existing
        behaviour must be unchanged: the sprite's image_index frame draws
        regardless of viewing angle."""
        room = self._room_with_camera((180, 100), facing_deg=180,
                                      rotation_frames=0)
        billboard = next(i for i in room.instances if i.object_name == "obj_fruit")
        billboard.image_index = 2  # the BLUE frame
        colors = self._rendered_colors(room)
        assert self.COLORS[2] in colors
        assert self.COLORS[0] not in colors

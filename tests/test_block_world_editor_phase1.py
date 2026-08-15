"""Tier 7d Phase 1 (docs/BLOCK_WORLD_EDITOR_PLAN.md): the Block World
editor's camera + raw 3D view embedded in a QWidget, no place/break
editing yet. Per the plan doc's own instruction, this phase needs "a
dedicated proof... every new interaction model must be proven against a
real rendered frame, not assumed to work" before Phase 2 builds on it.

Uses a real offscreen QApplication (not pytest-qt), matching this repo's
established convention for audit/regression tests that must run without
the optional pytest-qt dependency.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((1, 1))

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from runtime.game_runner import GameRoom  # noqa: E402
from extensions.block_world.state import set_block  # noqa: E402
from editors.block_world_editor.session import (  # noqa: E402
    BlockWorldEditSession, EDITOR_CAMERA_OBJECT_NAME, make_empty_room,
)
from editors.block_world_editor.window import BlockWorldEditorWindow  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


CELL = 32


def _room_with_a_wall_in_front():
    """A small room with a solid wall directly ahead of the default spawn
    (room centre, facing angle 0 = +x), close enough to fill the frame,
    so a real render produces more than one flat colour."""
    room = GameRoom("bw_editor_test", {"width": 20 * CELL, "height": 20 * CELL},
                     action_executor=None)
    for y in range(6, 14):
        for z in range(3):
            set_block(room, 12, y, z, "stone")
    return room


class TestBlockWorldEditSession:
    def test_camera_is_planted_in_room_instances(self):
        room = make_empty_room()
        session = BlockWorldEditSession(room)
        assert session.camera in room.instances
        assert session.camera.object_name == EDITOR_CAMERA_OBJECT_NAME

    def test_camera_config_is_wired_for_rendering(self):
        room = make_empty_room()
        session = BlockWorldEditSession(room)
        assert session.camera_config["enabled"] is True
        assert session.camera_config["camera_object"] == EDITOR_CAMERA_OBJECT_NAME

    def test_place_sets_position_and_layer(self):
        room = make_empty_room()
        session = BlockWorldEditSession(room)
        session.place(5, 7, facing_deg=90.0, z_layer=2)
        assert session.camera.x == 5 * session.cell_size
        assert session.camera.y == 7 * session.cell_size
        assert session.camera.facing_angle == 90.0
        assert session.camera_config["z_layer"] == 2

    def test_close_removes_the_editor_camera(self):
        room = make_empty_room()
        session = BlockWorldEditSession(room)
        assert session.camera in room.instances
        session.close()
        assert session.camera not in room.instances
        # A camera never planted (double-close) must not raise.
        session.close()


class TestBlockWorldEditorWindowPhase1:
    def test_constructs_and_renders_a_real_frame(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        try:
            window.timer.stop()   # drive frames manually, not on a wall clock
            window.session.place(6, 10, facing_deg=0.0, z_layer=0)
            window._tick()

            # A real render happened: the surface is not the pygame default
            # all-black fill, and the wall + sky/floor bands both show up as
            # genuinely different colours (proves render_block_world_view
            # actually ran end to end, not just "didn't crash").
            surf = window.canvas.get_surface()
            colors = {surf.get_at((x, y))[:3] for x in (10, 400, 790)
                      for y in (10, 300, 590)}
            assert len(colors) >= 2
        finally:
            window.close()

    def test_wasd_moves_the_camera_forward(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        try:
            window.timer.stop()
            window.session.place(6, 10, facing_deg=0.0, z_layer=0)
            start_x = window.session.camera.x

            window._on_key_pressed(Qt.Key_W)
            for _ in range(10):
                window._tick()

            # facing_angle=0 means +x is forward (GM convention).
            assert window.session.camera.x > start_x
        finally:
            window.close()

    def test_strafe_keys_move_perpendicular_to_facing(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        try:
            window.timer.stop()
            window.session.place(6, 10, facing_deg=0.0, z_layer=0)
            start_x, start_y = window.session.camera.x, window.session.camera.y

            window._on_key_pressed(Qt.Key_D)
            for _ in range(10):
                window._tick()

            # Strafing must not move the camera along its own forward axis.
            assert window.session.camera.x == pytest.approx(start_x, abs=1e-6)
            assert window.session.camera.y != start_y
        finally:
            window.close()

    def test_space_and_shift_step_the_layer_and_floor_at_zero(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        try:
            window.timer.stop()
            assert window.session.camera_config["z_layer"] == 0

            window._on_key_pressed(Qt.Key_Space)
            assert window.session.camera_config["z_layer"] == 1
            window._on_key_pressed(Qt.Key_Space)
            assert window.session.camera_config["z_layer"] == 2

            window._on_key_pressed(Qt.Key_Shift)
            window._on_key_pressed(Qt.Key_Shift)
            window._on_key_pressed(Qt.Key_Shift)   # one more than placed -- must floor at 0
            assert window.session.camera_config["z_layer"] == 0
        finally:
            window.close()

    def test_mouse_drag_turns_and_pitches_the_camera(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        try:
            window.timer.stop()
            window.session.place(6, 10, facing_deg=0.0, z_layer=0)
            start_angle = window.session.camera.facing_angle
            start_pitch = window.session.camera_config["pitch"]

            window._on_mouse_pressed(400, 300, Qt.MiddleButton)
            window._on_mouse_moved(450, 320)   # drag right + down
            window._on_mouse_released(450, 320, Qt.MiddleButton)

            assert window.session.camera.facing_angle != start_angle
            assert window.session.camera_config["pitch"] != start_pitch

            # Releasing the button must stop the drag from tracking further
            # mouse-move events.
            angle_after_release = window.session.camera.facing_angle
            window._on_mouse_moved(500, 200)
            assert window.session.camera.facing_angle == angle_after_release
        finally:
            window.close()

    def test_wheel_adjusts_pitch(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        try:
            window.timer.stop()
            start_pitch = window.session.camera_config["pitch"]
            window._on_mouse_wheel(0, 0, 120)
            assert window.session.camera_config["pitch"] > start_pitch
        finally:
            window.close()

    def test_close_stops_the_timer_and_the_editor_camera(self):
        room = _room_with_a_wall_in_front()
        window = BlockWorldEditorWindow(room)
        session = window.session
        assert session.camera in room.instances
        window.close()
        assert not window.timer.isActive()
        assert session.camera not in room.instances

    def test_defaults_to_an_empty_room_when_none_given(self):
        window = BlockWorldEditorWindow()
        try:
            assert window.session.room is not None
            assert window.session.room.width > 0
        finally:
            window.close()

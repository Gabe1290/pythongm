"""Tier 7d Phase 2 (docs/BLOCK_WORLD_EDITOR_PLAN.md): place/break via
mouse, routed through a QUndoStack. Builds on Phase 1's proven
QWidget/renderer pipeline (tests/test_block_world_editor_phase1.py) --
this file focuses on the editing behaviour itself: picking, the palette,
and undo/redo.
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
from extensions.block_world.state import get_block, set_block  # noqa: E402
from editors.block_world_editor.window import BlockWorldEditorWindow  # noqa: E402
from editors.block_world_editor.undo_commands import (  # noqa: E402
    SetBlockCommand, make_set_block_command,
)

CELL = 32


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _room_with_a_wall_in_front():
    room = GameRoom("bw_editor_test2", {"width": 20 * CELL, "height": 20 * CELL},
                     action_executor=None)
    for y in range(6, 14):
        for z in range(3):
            set_block(room, 12, y, z, "stone")
    return room


def _room_with_an_obsidian_wall():
    room = GameRoom("bw_editor_test2b", {"width": 20 * CELL, "height": 20 * CELL},
                     action_executor=None)
    for y in range(6, 14):
        for z in range(3):
            set_block(room, 12, y, z, "obsidian")
    return room


def _spawned_window(room):
    window = BlockWorldEditorWindow(room)
    window.timer.stop()
    window.session.place(6, 10, facing_deg=0.0, z_layer=0)
    return window


CENTER = (400, 300)   # screen centre -- a level ray at DEFAULT_EYE_HEIGHT
                       # (1.5 cells) intersects LAYER 1 of a wall spanning
                       # z 0..2, not layer 0 -- see eye_z_for's docstring


class TestSetBlockCommand:
    def test_undo_restores_old_type_redo_reapplies_new(self):
        room = GameRoom("bw_cmd_test", {"width": 320, "height": 320}, action_executor=None)
        cmd = SetBlockCommand(room, 1, 2, 0, "stone", None)
        cmd.redo()
        assert get_block(room, 1, 2, 0) == "stone"
        cmd.undo()
        assert get_block(room, 1, 2, 0) is None
        cmd.redo()
        assert get_block(room, 1, 2, 0) == "stone"

    def test_break_command_undo_restores_previous_block(self):
        room = GameRoom("bw_cmd_test2", {"width": 320, "height": 320}, action_executor=None)
        set_block(room, 1, 2, 0, "brick")
        cmd = make_set_block_command(room, 1, 2, 0, new_type=None)
        cmd.redo()
        assert get_block(room, 1, 2, 0) is None
        cmd.undo()
        assert get_block(room, 1, 2, 0) == "brick"


class TestPlaceBlock:
    def test_left_click_places_the_selected_block_via_undo_stack(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window.palette.select("gold_block")
            assert window.undo_stack.count() == 0
            window._on_mouse_pressed(*CENTER, Qt.LeftButton)
            assert window.undo_stack.count() == 1
            assert get_block(window.session.room, 11, 10, 1) == "gold_block"
        finally:
            window.close()

    def test_undo_removes_the_placed_block_redo_reapplies_it(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window.palette.select("wool_blue")
            window._on_mouse_pressed(*CENTER, Qt.LeftButton)
            assert get_block(window.session.room, 11, 10, 1) == "wool_blue"

            window.undo_stack.undo()
            assert get_block(window.session.room, 11, 10, 1) is None

            window.undo_stack.redo()
            assert get_block(window.session.room, 11, 10, 1) == "wool_blue"
        finally:
            window.close()

    def test_no_place_when_no_block_selected(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window.palette._current = None   # simulate nothing selected
            window._on_mouse_pressed(*CENTER, Qt.LeftButton)
            assert window.undo_stack.count() == 0
        finally:
            window.close()


class TestBreakBlock:
    def test_right_click_breaks_the_targeted_block(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            assert get_block(window.session.room, 12, 10, 1) == "stone"
            window._on_mouse_pressed(*CENTER, Qt.RightButton)
            assert get_block(window.session.room, 12, 10, 1) is None
            assert window.undo_stack.count() == 1
        finally:
            window.close()

    def test_undo_restores_the_broken_block(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window._on_mouse_pressed(*CENTER, Qt.RightButton)
            assert get_block(window.session.room, 12, 10, 1) is None
            window.undo_stack.undo()
            assert get_block(window.session.room, 12, 10, 1) == "stone"
        finally:
            window.close()

    def test_obsidian_refuses_to_break(self):
        window = _spawned_window(_room_with_an_obsidian_wall())
        try:
            window._on_mouse_pressed(*CENTER, Qt.RightButton)
            assert get_block(window.session.room, 12, 10, 1) == "obsidian"
            assert window.undo_stack.count() == 0
        finally:
            window.close()


class TestPalette:
    def test_default_selection_is_set_on_construction(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            assert window.palette.current_block() is not None
        finally:
            window.close()

    def test_selecting_a_block_updates_current_and_emits(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            received = []
            window.palette.block_selected.connect(received.append)
            window.palette.select("diamond_block")
            assert window.palette.current_block() == "diamond_block"
            assert received == ["diamond_block"]
        finally:
            window.close()

    def test_unknown_block_type_is_a_no_op(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            before = window.palette.current_block()
            window.palette.select("not_a_real_block")
            assert window.palette.current_block() == before
        finally:
            window.close()


class TestAimOverlayDoesNotCrash:
    def test_tick_with_place_break_wired_still_renders(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window._mouse_pos = CENTER
            window._tick()   # must not raise
            surf = window.canvas.get_surface()
            assert surf.get_size() == (800, 600)
        finally:
            window.close()

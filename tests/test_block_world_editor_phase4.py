"""Tier 7d Phase 4 (docs/BLOCK_WORLD_EDITOR_PLAN.md): the polish pass --
Clear World (undoable, with confirmation) and Delete as a keyboard
alternative to right-click for breaking the aimed block.
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
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from runtime.game_runner import GameRoom  # noqa: E402
from extensions.block_world.state import get_block, set_block, iter_blocks  # noqa: E402
from editors.block_world_editor.window import BlockWorldEditorWindow  # noqa: E402
from editors.block_world_editor.undo_commands import ClearWorldCommand  # noqa: E402

CELL = 32


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _room_with_a_wall_in_front():
    room = GameRoom("bw_editor_test4", {"width": 20 * CELL, "height": 20 * CELL},
                     action_executor=None)
    for y in range(6, 14):
        for z in range(3):
            set_block(room, 12, y, z, "stone")
    return room


def _spawned_window(room):
    window = BlockWorldEditorWindow(room)
    window.timer.stop()
    window.session.place(6, 10, facing_deg=0.0, z_layer=0)
    return window


CENTER = (400, 300)


class TestClearWorldCommand:
    def test_redo_clears_everything_undo_restores_it(self):
        room = _room_with_a_wall_in_front()
        before = sorted(iter_blocks(room))
        assert before   # sanity: the fixture actually has blocks

        cmd = ClearWorldCommand(room)
        cmd.redo()
        assert sorted(iter_blocks(room)) == []

        cmd.undo()
        assert sorted(iter_blocks(room)) == before


class TestClearWorldAction:
    def test_confirmed_clear_empties_the_room_via_undo_stack(self, monkeypatch):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            monkeypatch.setattr(QMessageBox, "question",
                                 staticmethod(lambda *a, **k: QMessageBox.Yes))
            assert list(iter_blocks(window.session.room))
            window.clear_world()
            assert list(iter_blocks(window.session.room)) == []
            assert window.undo_stack.count() == 1
        finally:
            window.close()

    def test_declined_confirmation_leaves_the_world_untouched(self, monkeypatch):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            monkeypatch.setattr(QMessageBox, "question",
                                 staticmethod(lambda *a, **k: QMessageBox.No))
            before = sorted(iter_blocks(window.session.room))
            window.clear_world()
            assert sorted(iter_blocks(window.session.room)) == before
            assert window.undo_stack.count() == 0
        finally:
            window.close()

    def test_clearing_an_empty_world_is_a_no_op_info_message(self, monkeypatch):
        window = _spawned_window(GameRoom("bw_empty", {"width": 640, "height": 640},
                                           action_executor=None))
        try:
            informed = []
            monkeypatch.setattr(
                QMessageBox, "information",
                staticmethod(lambda *a, **k: informed.append(a) or QMessageBox.Ok))
            # question() must not even be reached for an empty world.
            monkeypatch.setattr(
                QMessageBox, "question",
                staticmethod(lambda *a, **k: (_ for _ in ()).throw(
                    AssertionError("should not confirm an already-empty clear"))))
            window.clear_world()
            assert len(informed) == 1
            assert window.undo_stack.count() == 0
        finally:
            window.close()

    def test_undo_after_clear_restores_the_wall(self, monkeypatch):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            monkeypatch.setattr(QMessageBox, "question",
                                 staticmethod(lambda *a, **k: QMessageBox.Yes))
            window.clear_world()
            assert get_block(window.session.room, 12, 10, 1) is None

            window.undo_stack.undo()
            assert get_block(window.session.room, 12, 10, 1) == "stone"
        finally:
            window.close()


class TestDeleteKeyBreaksAimedBlock:
    def test_delete_key_breaks_the_same_block_right_click_would(self):
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window._mouse_pos = CENTER
            assert get_block(window.session.room, 12, 10, 1) == "stone"
            window._on_key_pressed(Qt.Key_Delete)
            assert get_block(window.session.room, 12, 10, 1) is None
            assert window.undo_stack.count() == 1
        finally:
            window.close()

    def test_delete_with_nothing_aimed_at_is_a_no_op(self):
        window = _spawned_window(GameRoom("bw_empty2", {"width": 640, "height": 640},
                                           action_executor=None))
        try:
            window._mouse_pos = CENTER
            window._on_key_pressed(Qt.Key_Delete)   # must not raise
            assert window.undo_stack.count() == 0
        finally:
            window.close()

    def test_delete_still_registers_as_a_held_key(self):
        """Delete doubling as a break-shortcut must not stop it from also
        being tracked in _held_keys like any other key (defensive -- it
        isn't used for movement, but nothing should assume it's special-
        cased out of the held-keys set)."""
        window = _spawned_window(_room_with_a_wall_in_front())
        try:
            window._on_key_pressed(Qt.Key_Delete)
            assert Qt.Key_Delete in window._held_keys
            window._on_key_released(Qt.Key_Delete)
            assert Qt.Key_Delete not in window._held_keys
        finally:
            window.close()

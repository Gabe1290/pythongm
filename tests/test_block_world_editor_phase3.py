"""Tier 7d Phase 3 (docs/BLOCK_WORLD_EDITOR_PLAN.md): save/load to
blocks/<room>.json (io.py) and the Room Editor toolbar entry that opens
the voxel editor for a real project room.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
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

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from runtime.game_runner import GameRoom  # noqa: E402
from extensions.block_world.state import get_block, set_block  # noqa: E402
from editors.block_world_editor.io import (  # noqa: E402
    blocks_path, load_room_blocks, save_room_blocks,
)
from editors.block_world_editor.window import BlockWorldEditorWindow  # noqa: E402
from editors.block_world_editor.undo_commands import make_set_block_command  # noqa: E402

CELL = 32


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _room():
    return GameRoom("bw_editor_test3", {"width": 20 * CELL, "height": 20 * CELL},
                     action_executor=None)


class TestIO:
    def test_round_trip_save_then_load(self, tmp_path):
        room = _room()
        set_block(room, 1, 2, 0, "stone")
        set_block(room, 3, 4, 1, "gold_block")

        save_room_blocks(room, tmp_path, "room0")

        loaded = _room()
        assert get_block(loaded, 1, 2, 0) is None
        assert load_room_blocks(loaded, tmp_path, "room0") is True
        assert get_block(loaded, 1, 2, 0) == "stone"
        assert get_block(loaded, 3, 4, 1) == "gold_block"

    def test_load_nonexistent_returns_false_without_error(self, tmp_path):
        room = _room()
        assert load_room_blocks(room, tmp_path, "no_such_room") is False

    def test_save_creates_the_blocks_directory(self, tmp_path):
        room = _room()
        set_block(room, 0, 0, 0, "brick")
        path = save_room_blocks(room, tmp_path, "room0")
        assert path == blocks_path(tmp_path, "room0")
        assert path.exists()
        assert path.parent.name == "blocks"

    def test_saved_file_is_the_to_block_list_shape(self, tmp_path):
        room = _room()
        set_block(room, 5, 6, 0, "wool_red")
        path = save_room_blocks(room, tmp_path, "room0")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data == [{"x": 5, "y": 6, "z": 0, "type": "wool_red"}]


class TestWindowLoadOnOpen:
    def test_loads_existing_blocks_on_construction(self, tmp_path):
        prep = _room()
        set_block(prep, 2, 2, 0, "diamond_block")
        save_room_blocks(prep, tmp_path, "room0")

        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="room0")
        try:
            window.timer.stop()
            assert get_block(window.session.room, 2, 2, 0) == "diamond_block"
            assert window.undo_stack.isClean()
        finally:
            window.close()

    def test_no_file_opens_empty_without_error(self, tmp_path):
        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="brand_new_room")
        try:
            window.timer.stop()
            assert get_block(window.session.room, 0, 0, 0) is None
        finally:
            window.close()

    def test_corrupt_blocks_file_warns_and_opens_empty(self, tmp_path, monkeypatch):
        path = blocks_path(tmp_path, "room0")
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps([{"x": 0, "y": 0, "z": 0, "type": "not_a_real_block"}]),
                         encoding="utf-8")

        warned = []
        monkeypatch.setattr(QMessageBox, "warning",
                             staticmethod(lambda *a, **k: warned.append(a) or QMessageBox.Ok))

        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="room0")
        try:
            window.timer.stop()
            assert len(warned) == 1
            assert get_block(window.session.room, 0, 0, 0) is None
        finally:
            window.close()


class TestWindowSave:
    def test_save_writes_the_file_and_cleans_the_undo_stack(self, tmp_path):
        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="room0")
        try:
            window.timer.stop()
            cmd = make_set_block_command(window.session.room, 1, 1, 0, new_type="cobble")
            window.undo_stack.push(cmd)
            assert not window.undo_stack.isClean()

            assert window.save() is True
            assert window.undo_stack.isClean()

            data = json.loads(blocks_path(tmp_path, "room0").read_text(encoding="utf-8"))
            assert data == [{"x": 1, "y": 1, "z": 0, "type": "cobble"}]
        finally:
            window.close()

    def test_save_without_project_info_shows_a_message_and_returns_false(self, monkeypatch):
        informed = []
        monkeypatch.setattr(QMessageBox, "information",
                             staticmethod(lambda *a, **k: informed.append(a) or QMessageBox.Ok))
        window = BlockWorldEditorWindow()   # no project_path/room_name
        try:
            window.timer.stop()
            assert window.can_save() is False
            assert window.save() is False
            assert len(informed) == 1
        finally:
            window.close()

    def test_title_gets_dirty_marker_after_edit_and_clears_after_save(self, tmp_path):
        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="room0")
        try:
            window.timer.stop()
            clean_title = window.windowTitle()
            assert "*" not in clean_title

            cmd = make_set_block_command(window.session.room, 1, 1, 0, new_type="cobble")
            window.undo_stack.push(cmd)
            assert window.windowTitle().endswith("*")

            window.save()
            assert "*" not in window.windowTitle()
        finally:
            window.close()


class TestCloseEventPrompt:
    def _dirty_window(self, tmp_path):
        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="room0")
        window.timer.stop()
        cmd = make_set_block_command(window.session.room, 1, 1, 0, new_type="cobble")
        window.undo_stack.push(cmd)
        return window

    def test_save_on_close_writes_the_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(QMessageBox, "question",
                             staticmethod(lambda *a, **k: QMessageBox.Save))
        window = self._dirty_window(tmp_path)
        assert window.close() is True
        assert blocks_path(tmp_path, "room0").exists()

    def test_discard_on_close_does_not_write_the_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(QMessageBox, "question",
                             staticmethod(lambda *a, **k: QMessageBox.Discard))
        window = self._dirty_window(tmp_path)
        assert window.close() is True
        assert not blocks_path(tmp_path, "room0").exists()

    def test_cancel_on_close_keeps_the_window_open(self, tmp_path, monkeypatch):
        monkeypatch.setattr(QMessageBox, "question",
                             staticmethod(lambda *a, **k: QMessageBox.Cancel))
        window = self._dirty_window(tmp_path)
        try:
            assert window.close() is False
        finally:
            # Clean up for real so the test doesn't leak an open window.
            monkeypatch.setattr(QMessageBox, "question",
                                 staticmethod(lambda *a, **k: QMessageBox.Discard))
            window.close()

    def test_clean_window_closes_without_prompting(self, tmp_path, monkeypatch):
        def _fail_if_called(*a, **k):
            raise AssertionError("should not prompt when nothing changed")
        monkeypatch.setattr(QMessageBox, "question", staticmethod(_fail_if_called))
        window = BlockWorldEditorWindow(_room(), project_path=tmp_path, room_name="room0")
        window.timer.stop()
        assert window.close() is True


class TestRoomEditorIntegration:
    def _editor(self, tmp_path):
        from editors.room_editor import RoomEditor
        return RoomEditor(str(tmp_path))

    def test_requires_a_named_room(self, tmp_path, monkeypatch):
        editor = self._editor(tmp_path)
        assert editor.asset_name == ""
        informed = []
        monkeypatch.setattr(QMessageBox, "information",
                             staticmethod(lambda *a, **k: informed.append(a) or QMessageBox.Ok))
        editor.open_block_world_editor()
        assert len(informed) == 1
        assert editor._block_world_window is None

    def test_opens_a_window_for_a_named_room(self, tmp_path):
        editor = self._editor(tmp_path)
        editor.asset_name = "room0"
        editor.open_block_world_editor()
        try:
            assert isinstance(editor._block_world_window, BlockWorldEditorWindow)
            editor._block_world_window.timer.stop()
        finally:
            editor._block_world_window.close()

    def test_reuses_the_same_window_on_a_second_call(self, tmp_path):
        editor = self._editor(tmp_path)
        editor.asset_name = "room0"
        editor.open_block_world_editor()
        editor._block_world_window.timer.stop()
        first = editor._block_world_window

        editor.open_block_world_editor()
        try:
            assert editor._block_world_window is first
        finally:
            editor._block_world_window.close()

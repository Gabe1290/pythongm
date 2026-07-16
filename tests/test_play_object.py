"""Regression tests for the "Play Object" toolbar button (TODO.md's
"Object test runner" item — restores the orphaned test_object method as
a real feature instead of dead code).

Same lightweight-stub pattern as test_game_subprocess_supervision.py:
call PyGameMakerIDE methods unbound on a SimpleNamespace stub rather than
standing up the full Qt IDE window. test_object's actual subprocess
launch is stubbed out (via a fake _run_project_json) so these tests
cover project-building/cleanup logic without spawning a real pygame
process.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _identity_tr(text):
    return text


class TestPlayObjectGuards:
    def test_refuses_when_game_already_running(self):
        ide = _ide_cls()
        running_process = MagicMock()
        running_process.poll.return_value = None  # still running
        stub = SimpleNamespace(
            _game_process=running_process,
            tr=_identity_tr,
        )
        # QMessageBox.information is a modal dialog (blocks for a click);
        # patch it out rather than show it in this headless test — same
        # reasoning as conftest's _auto_dismiss_qmessagebox fixture, which
        # doesn't cover non-qtbot tests like this one.
        with patch('core.ide_window.QMessageBox') as mock_box:
            ide.test_object(stub, "obj_player", {})
            mock_box.information.assert_called_once()
        assert not hasattr(stub, "_game_temp_project_dir")

    def test_refuses_with_no_project_open(self):
        ide = _ide_cls()
        stub = SimpleNamespace(
            _game_process=None,
            current_project_path=None,
            tr=_identity_tr,
        )
        with patch('core.ide_window.QMessageBox') as mock_box:
            ide.test_object(stub, "obj_player", {})
            mock_box.warning.assert_called_once()
        assert not hasattr(stub, "_game_temp_project_dir")


class TestPlayObjectProjectBuilding:
    def _run(self, tmp_path, object_data, project_data=None, sprite_bytes=None):
        """Invoke test_object on a stub, capturing the temp project it
        builds via a fake _run_project_json (records the path instead of
        launching a subprocess)."""
        ide = _ide_cls()

        project_dir = tmp_path / "real_project"
        project_dir.mkdir()
        sprites_dir = project_dir / "sprites"
        sprites_dir.mkdir()
        sprite_file = None
        if sprite_bytes is not None:
            sprite_file = sprites_dir / "spr_player.png"
            sprite_file.write_bytes(sprite_bytes)

        from core.asset_manager import AssetManager
        asset_manager = AssetManager()
        asset_manager.set_project_directory(str(project_dir))

        captured = {}

        def fake_run_project_json(path):
            captured['path'] = Path(path)

        stub = SimpleNamespace(
            _game_process=None,
            current_project_path=project_dir,
            current_project_data=project_data or {},
            asset_manager=asset_manager,
            tr=_identity_tr,
            _run_project_json=fake_run_project_json,
        )

        ide.test_object(stub, "obj_player", object_data)
        return stub, captured.get('path')

    def test_builds_minimal_project_with_one_room_and_one_instance(self, tmp_path):
        stub, temp_dir = self._run(tmp_path, {"sprite": "", "events": {}})
        try:
            assert temp_dir is not None and temp_dir.exists()
            data = json.loads((temp_dir / "project.json").read_text(encoding="utf-8"))
            assert "obj_player" in data["assets"]["objects"]
            assert data["settings"]["startup_room"] in data["assets"]["rooms"]
            room = next(iter(data["assets"]["rooms"].values()))
            assert len(room["instances"]) == 1
            assert room["instances"][0]["object_name"] == "obj_player"
            # Registered for cleanup by test_object (drained later by
            # _drain_game_stderr — see TestTempDirCleanup below).
            assert stub._game_temp_project_dir == temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_inherits_window_size_from_real_project(self, tmp_path):
        project_data = {"settings": {"window_width": 640, "window_height": 480, "room_speed": 60}}
        stub, temp_dir = self._run(tmp_path, {"sprite": ""}, project_data=project_data)
        try:
            data = json.loads((temp_dir / "project.json").read_text(encoding="utf-8"))
            assert data["settings"]["window_width"] == 640
            assert data["settings"]["window_height"] == 480
            assert data["settings"]["room_speed"] == 60
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_copies_the_objects_sprite_file(self, tmp_path):
        png_bytes = b"\x89PNG\r\n\x1a\nfake-but-nonempty"
        project_data = {
            "assets": {"sprites": {
                "spr_player": {"name": "spr_player", "asset_type": "sprite",
                               "file_path": "sprites/spr_player.png"},
            }},
        }
        stub, temp_dir = self._run(
            tmp_path, {"sprite": "spr_player"},
            project_data=project_data, sprite_bytes=png_bytes)
        try:
            data = json.loads((temp_dir / "project.json").read_text(encoding="utf-8"))
            assert "spr_player" in data["assets"]["sprites"]
            copied_rel = data["assets"]["sprites"]["spr_player"]["file_path"]
            copied = temp_dir / copied_rel
            assert copied.exists()
            assert copied.read_bytes() == png_bytes
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_missing_sprite_file_does_not_crash(self, tmp_path):
        """The object references a sprite whose asset entry exists but
        whose backing file doesn't (e.g. deleted-on-disk) — must degrade
        gracefully, not raise."""
        project_data = {
            "assets": {"sprites": {
                "spr_ghost": {"name": "spr_ghost", "asset_type": "sprite",
                              "file_path": "sprites/does_not_exist.png"},
            }},
        }
        stub, temp_dir = self._run(
            tmp_path, {"sprite": "spr_ghost"}, project_data=project_data)
        try:
            assert temp_dir is not None
            data = json.loads((temp_dir / "project.json").read_text(encoding="utf-8"))
            assert "spr_ghost" in data["assets"]["sprites"]
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_object_with_no_sprite(self, tmp_path):
        stub, temp_dir = self._run(tmp_path, {"sprite": ""})
        try:
            data = json.loads((temp_dir / "project.json").read_text(encoding="utf-8"))
            assert data["assets"]["sprites"] == {}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestTempDirCleanup:
    def test_drain_game_stderr_removes_temp_project_dir(self):
        ide = _ide_cls()
        temp_dir = Path(tempfile.mkdtemp(prefix="pygm2_test_object_test_"))
        (temp_dir / "project.json").write_text("{}")
        stub = SimpleNamespace(
            _game_stderr_handle=None,
            _game_stderr_path=None,
            _game_temp_project_dir=temp_dir,
        )

        ide._drain_game_stderr(stub, 0)

        assert not temp_dir.exists()
        assert stub._game_temp_project_dir is None

    def test_drain_game_stderr_is_a_noop_without_a_temp_dir(self):
        """A normal Test Game run (no test_object involved) must not be
        affected — no _game_temp_project_dir attribute at all."""
        ide = _ide_cls()
        stub = SimpleNamespace(_game_stderr_handle=None, _game_stderr_path=None)
        ide._drain_game_stderr(stub, 0)  # must not raise

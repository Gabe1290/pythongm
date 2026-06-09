"""
Regression tests for folder-save backup/rollback.

A folder save writes many files (rooms/*.json, objects/*.json, ...,
project.json) and each is individually atomic, but historically there was no
transaction *across* files: a failure on file N left files 1..N-1 committed
with no way back, corrupting a previously-good project. ProjectManager now
snapshots the save-managed paths before the write and restores them if any
write fails (mirroring what the zip save path already did). These tests lock
that in.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_pm():
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()
        return pm


def _read_room_instances(project_dir: Path, room: str):
    with open(project_dir / "rooms" / f"{room}.json", encoding="utf-8") as f:
        return json.load(f)["instances"]


def _seed_room(pm, instances):
    pm.current_project_data['assets']['rooms'] = {
        'room1': {'name': 'room1', 'asset_type': 'rooms', 'instances': instances}
    }


class TestFolderSaveRollback:

    def test_partial_save_failure_rolls_back_room_files(self, project_manager_dir):
        """If a write fails mid-save, already-written room files revert."""
        pm = _make_pm()
        pm.load_project(project_manager_dir)

        # First, a clean save establishes the on-disk "good" state: room1 with
        # the original instance set.
        original = [{'object': 'obj_a', 'x': 10, 'y': 10}]
        _seed_room(pm, original)
        assert pm.save_project() is True
        assert _read_room_instances(project_manager_dir, 'room1') == original

        # Now mutate the room, then force the *final* step (project.json prep)
        # to blow up — by which point rooms/room1.json has already been
        # rewritten with the new instances on disk.
        mutated = [{'object': 'obj_b', 'x': 99, 'y': 99}]
        _seed_room(pm, mutated)
        with patch.object(pm, '_prepare_project_data_for_save',
                          side_effect=RuntimeError("disk full")):
            assert pm.save_project() is False

        # Rollback restored the room file to the last good state.
        assert _read_room_instances(project_manager_dir, 'room1') == original

    def test_failed_save_leaves_no_backup_dir(self, project_manager_dir):
        """A failed save cleans up its rollback snapshot."""
        pm = _make_pm()
        pm.load_project(project_manager_dir)
        _seed_room(pm, [{'object': 'obj_a', 'x': 1, 'y': 1}])
        pm.save_project()

        with patch.object(pm, '_prepare_project_data_for_save',
                          side_effect=RuntimeError("boom")):
            assert pm.save_project() is False

        leftover = list(project_manager_dir.parent.glob('.*bak-*'))
        assert leftover == [], f"rollback snapshot not cleaned up: {leftover}"

    def test_successful_save_leaves_no_backup_dir(self, project_manager_dir):
        """The happy path discards the snapshot — no leftover temp dirs."""
        pm = _make_pm()
        pm.load_project(project_manager_dir)
        _seed_room(pm, [{'object': 'obj_a', 'x': 1, 'y': 1}])

        assert pm.save_project() is True
        leftover = list(project_manager_dir.parent.glob('.*bak-*'))
        assert leftover == [], f"rollback snapshot not cleaned up: {leftover}"

    def test_project_json_preserved_on_failure(self, project_manager_dir):
        """project.json content is unchanged when a save fails."""
        pm = _make_pm()
        pm.load_project(project_manager_dir)
        _seed_room(pm, [{'object': 'obj_a', 'x': 1, 'y': 1}])
        pm.save_project()

        before = (project_manager_dir / "project.json").read_text(encoding="utf-8")
        pm.current_project_data['description'] = "should not persist"
        with patch.object(pm, '_prepare_project_data_for_save',
                          side_effect=RuntimeError("boom")):
            assert pm.save_project() is False

        after = (project_manager_dir / "project.json").read_text(encoding="utf-8")
        assert before == after


@pytest.fixture
def project_manager_dir(temp_project_dir):
    """Alias to the shared project-dir fixture for readability."""
    return temp_project_dir

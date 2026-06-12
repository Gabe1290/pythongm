"""Regression tests for deleted-instance resurrection in rooms (audit H3).

docs/FULL_AUDIT_2026-06-11.md: the empty-room "preserve existing file
instances" heuristic in _save_rooms_to_files is gated on
_rooms_loaded_this_session, but that set was ONLY populated at project
load. Rooms whose on-disk file first appears mid-session (new projects,
recreated/renamed rooms, legacy projects with no rooms/ dir) never got
registered, so emptying such a room hit the preservation branch and the
deleted instances were written back — and stale rooms/<name>.json orphans
from deleted/renamed rooms injected dead data into any future room with
the same name.

Now registered wherever memory becomes authoritative: create_new_project,
update_asset (room with instances), and after each _save_rooms_to_files
write; AssetManager.delete_asset/rename_asset also remove/carry the
rooms|objects side files.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

INSTANCE = {'object': 'obj_test', 'x': 64, 'y': 64}


def _make_pm():
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=AssetManager())
        pm.auto_save_timer = MagicMock()
        return pm


def _room_file_instances(project_dir: Path, room: str):
    with open(project_dir / "rooms" / f"{room}.json", encoding="utf-8") as f:
        return json.load(f)["instances"]


@pytest.fixture
def new_project(tmp_path):
    pm = _make_pm()
    assert pm.create_new_project("proj", tmp_path) is True
    return pm, tmp_path / "proj"


class TestEmptiedRoomStaysEmpty:

    def test_audit_repro_new_project_empty_after_save(self, new_project):
        """The audit's exact repro: create -> add instance -> save ->
        empty -> save. Pre-fix the second save 'preserved' the instance."""
        pm, project_dir = new_project
        room = pm.current_project_data['assets']['rooms']['room0']

        room['instances'] = [dict(INSTANCE)]
        assert pm.save_project() is True
        assert _room_file_instances(project_dir, 'room0') == [INSTANCE]

        room['instances'] = []
        assert pm.save_project() is True
        assert _room_file_instances(project_dir, 'room0') == []

        # And a fresh load does not bring the deleted instance back
        pm2 = _make_pm()
        assert pm2.load_project(project_dir) is True
        assert pm2.current_project_data['assets']['rooms']['room0']['instances'] == []

    def test_update_asset_with_instances_registers_room(self, new_project):
        """The room editor's save path (update_asset with 'instances')
        makes memory authoritative even if the room wasn't load-registered."""
        pm, project_dir = new_project
        room = pm.current_project_data['assets']['rooms']['room0']
        room['instances'] = [dict(INSTANCE)]
        assert pm.save_project() is True

        # Simulate a session where the room was never load-registered
        pm._rooms_loaded_this_session = set()

        pm.update_asset('rooms', 'room0', {'instances': []})
        room['instances'] = []  # IDE mirrors the editor data into project_data
        assert pm.save_project() is True
        assert _room_file_instances(project_dir, 'room0') == []

    def test_preservation_still_guards_unloaded_rooms(self, new_project):
        """The original bug-#15 protection stays: an empty in-memory list for
        a room that was never materialized this session is 'not loaded',
        not 'user emptied it' — the file's instances survive the save."""
        pm, project_dir = new_project
        room = pm.current_project_data['assets']['rooms']['room0']
        room['instances'] = [dict(INSTANCE)]
        assert pm.save_project() is True

        # New session over the same folder, but the room's instances never
        # reach memory (legacy/no-merge path simulated by clearing both).
        pm._rooms_loaded_this_session = set()
        room['instances'] = []
        assert pm.save_project() is True
        assert _room_file_instances(project_dir, 'room0') == [INSTANCE]


class TestOrphanSideFiles:

    def test_deleting_room_removes_side_file(self, new_project):
        pm, project_dir = new_project
        pm.current_project_data['assets']['rooms']['room0']['instances'] = [dict(INSTANCE)]
        assert pm.save_project() is True
        side = project_dir / "rooms" / "room0.json"
        assert side.exists()

        assert pm.delete_asset('rooms', 'room0') is True
        assert not side.exists()
        assert 'room0' not in pm._rooms_loaded_this_session

    def test_recreated_room_does_not_resurrect_old_instances(self, new_project):
        pm, project_dir = new_project
        rooms = pm.current_project_data['assets']['rooms']
        rooms['room0']['instances'] = [dict(INSTANCE)]
        assert pm.save_project() is True

        assert pm.delete_asset('rooms', 'room0') is True
        del rooms['room0']

        # Recreate a room with the same name, empty
        rooms['room0'] = {'name': 'room0', 'asset_type': 'room',
                          'width': 640, 'height': 480, 'instances': []}
        pm.update_asset('rooms', 'room0', {'instances': []})
        assert pm.save_project() is True
        assert _room_file_instances(project_dir, 'room0') == []

    def test_renaming_room_carries_side_file(self, new_project):
        pm, project_dir = new_project
        pm.current_project_data['assets']['rooms']['room0']['instances'] = [dict(INSTANCE)]
        assert pm.save_project() is True

        am = pm.asset_manager
        assert am.rename_asset('rooms', 'room0', 'level_one') is True
        assert not (project_dir / "rooms" / "room0.json").exists()
        assert (project_dir / "rooms" / "level_one.json").exists()
        assert _room_file_instances(project_dir, 'level_one') == [INSTANCE]

    def test_deleting_object_removes_side_file(self, new_project):
        pm, project_dir = new_project
        (project_dir / "objects").mkdir(exist_ok=True)
        pm.update_asset('objects', 'obj_test', {'events': {}})
        assert pm.save_project() is True
        side = project_dir / "objects" / "obj_test.json"
        assert side.exists()

        assert pm.delete_asset('objects', 'obj_test') is True
        assert not side.exists()

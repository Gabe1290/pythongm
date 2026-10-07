"""
Saving a project whose folder's PARENT is not writable.

Classroom report (2026-10-07): students used "Save Project As" and picked
the USB stick itself, so the project folder was the stick's mount point
(/media/<user>/<STICK>). The save's rollback snapshot was created as a
sibling of the project folder -- inside /media/<user>/, which is root-owned
-- so mkdtemp raised PermissionError and every save of that project was
cancelled. The stick kept only the stale files Save As had copied first.

The snapshot now falls back to the system temp dir. These tests simulate the
read-only parent by making mkdtemp refuse any dir= inside it (portable: a
chmod'd directory doesn't stop root or Windows from writing).
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture
def project_manager_dir(temp_project_dir):
    return temp_project_dir


def _make_pm():
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()
        return pm


def _refuse_parent(parent: Path):
    """A mkdtemp that raises like /media/<user>/ does for a normal user."""
    real_mkdtemp = tempfile.mkdtemp

    def fake_mkdtemp(*args, **kwargs):
        target = kwargs.get('dir')
        if target is not None and Path(target).resolve() == parent.resolve():
            raise PermissionError(13, "Permission denied", str(target))
        return real_mkdtemp(*args, **kwargs)
    return fake_mkdtemp


def _set_room(pm, instances):
    pm.current_project_data['assets']['rooms'] = {
        'room1': {'name': 'room1', 'asset_type': 'rooms', 'instances': instances}
    }


def _room_instances(project_dir: Path):
    with open(project_dir / "rooms" / "room1.json", encoding="utf-8") as f:
        return json.load(f)["instances"]


def test_save_succeeds_when_parent_is_read_only(project_manager_dir):
    pm = _make_pm()
    pm.load_project(project_manager_dir)
    _set_room(pm, [{'object': 'obj_a', 'x': 1, 'y': 1}])
    assert pm.save_project() is True   # on-disk state now exists to snapshot

    edited = [{'object': 'obj_b', 'x': 42, 'y': 7}]
    _set_room(pm, edited)
    with patch('tempfile.mkdtemp', _refuse_parent(project_manager_dir.parent)):
        assert pm.save_project() is True

    assert _room_instances(project_manager_dir) == edited
    # No snapshot may be left next to (or inside) the project.
    leftovers = [p.name for p in project_manager_dir.parent.iterdir()
                 if p.name.startswith(f".{project_manager_dir.name}.bak-")]
    assert leftovers == []


def test_rollback_still_works_with_fallback_snapshot(project_manager_dir):
    """The fallback location must still restore a failed save."""
    pm = _make_pm()
    pm.load_project(project_manager_dir)
    good = [{'object': 'obj_a', 'x': 1, 'y': 1}]
    _set_room(pm, good)
    assert pm.save_project() is True

    _set_room(pm, [{'object': 'obj_b', 'x': 9, 'y': 9}])
    with patch('tempfile.mkdtemp', _refuse_parent(project_manager_dir.parent)), \
         patch.object(pm, '_prepare_project_data_for_save',
                      side_effect=RuntimeError("disk full")):
        assert pm.save_project() is False

    assert _room_instances(project_manager_dir) == good

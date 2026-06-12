"""Regression tests for zip-backed save state across project switches.

Audit H2 (docs/FULL_AUDIT_2026-06-11.md): after opening a project from a
.zip, the _original_zip_path/_temp_extraction_dir/_auto_save_as_zip state
was only ever cleared by close_project() — which has no callers. Switching
to any other project (open folder project, File→New, Save-As) left
save_project() on the zip branch, silently recompressing the OLD zip from
its stale temp extraction on every Ctrl+S / auto-save and returning THAT
as the save result.

Now: load_project()/create_new_project() reset the zip state when a
different project becomes current (a reload of the same temp extraction
keeps it — that's force_project_refresh), save_project_as() resets it on
success, and load_project_from_zip() assigns state only after a
successful load.
"""

import json
import shutil
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


def _make_project(project_dir: Path, name: str):
    """Minimal on-disk project (mirrors the conftest temp_project_dir shape)."""
    project_dir.mkdir(parents=True)
    for subdir in ("sprites", "sounds", "backgrounds", "objects", "rooms",
                   "fonts", "data"):
        (project_dir / subdir).mkdir()
    data = {
        "name": name,
        "version": "1.0.0",
        "room_order": [],
        "assets": {k: {} for k in ("sprites", "sounds", "backgrounds",
                                   "objects", "rooms", "fonts", "data")},
        "game_settings": {"window_width": 800, "window_height": 600},
    }
    with open(project_dir / "project.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return project_dir


@pytest.fixture
def zip_project(tmp_path):
    """A project compressed into a .zip, plus a second folder project."""
    from utils.project_compression import ProjectCompressor

    src = _make_project(tmp_path / "zipped_src", "Zipped Project")
    zip_path = tmp_path / "student.zip"
    assert ProjectCompressor.compress_project(src, zip_path)
    folder = _make_project(tmp_path / "folder_project", "Folder Project")
    return zip_path, folder


class TestZipStateResetOnSwitch:

    def test_open_folder_project_after_zip_clears_zip_state(self, zip_project):
        zip_path, folder = zip_project
        pm = _make_pm()

        assert pm.load_project_from_zip(zip_path) is True
        assert pm.is_project_from_zip() is True
        old_temp = Path(pm._temp_extraction_dir)

        assert pm.load_project(folder) is True

        assert pm.is_project_from_zip() is False
        assert pm._auto_save_as_zip is False
        assert pm._temp_extraction_dir is None
        assert not old_temp.exists()  # stale extraction cleaned up

    def test_save_after_switch_does_not_rewrite_old_zip(self, zip_project):
        zip_path, folder = zip_project
        pm = _make_pm()
        pm.load_project_from_zip(zip_path)
        pm.load_project(folder)

        before = zip_path.read_bytes()
        pm.current_project_data['name'] = 'Folder Project (edited)'
        assert pm.save_project() is True

        assert zip_path.read_bytes() == before  # old zip untouched
        with open(folder / "project.json", encoding="utf-8") as f:
            assert json.load(f)['name'] == 'Folder Project (edited)'

    def test_save_succeeds_after_switch_even_if_old_zip_deleted(self, zip_project):
        """Pre-fix: shutil.copy2 on the missing zip made every save report
        failure even though the folder save succeeded."""
        zip_path, folder = zip_project
        pm = _make_pm()
        pm.load_project_from_zip(zip_path)
        pm.load_project(folder)

        zip_path.unlink()
        assert pm.save_project() is True

    def test_new_project_after_zip_clears_zip_state(self, zip_project, tmp_path):
        zip_path, _ = zip_project
        pm = _make_pm()
        pm.load_project_from_zip(zip_path)

        assert pm.create_new_project("fresh", tmp_path / "newloc") is True
        assert pm.is_project_from_zip() is False
        assert pm._auto_save_as_zip is False

    def test_save_as_from_zip_to_folder_clears_zip_state(self, zip_project, tmp_path):
        zip_path, _ = zip_project
        pm = _make_pm()
        pm.load_project_from_zip(zip_path)

        before = zip_path.read_bytes()
        assert pm.save_project_as(tmp_path / "saved_as") is True

        assert pm.is_project_from_zip() is False
        pm.current_project_data['name'] = 'post save-as edit'
        assert pm.save_project() is True
        assert zip_path.read_bytes() == before  # zip not rewritten post-Save-As


class TestZipStateKeptOnReload:

    def test_reload_of_same_temp_dir_keeps_zip_state(self, zip_project):
        """force_project_refresh reloads the current (temp) path — that must
        NOT drop zip-backed mode or delete the extraction it's loading from."""
        zip_path, _ = zip_project
        pm = _make_pm()
        pm.load_project_from_zip(zip_path)
        temp_dir = Path(pm._temp_extraction_dir)

        assert pm.load_project(temp_dir) is True

        assert pm.is_project_from_zip() is True
        assert pm._auto_save_as_zip is True
        assert temp_dir.exists()

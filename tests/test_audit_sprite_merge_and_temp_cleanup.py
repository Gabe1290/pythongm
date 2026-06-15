"""
Regression tests for two FULL_AUDIT_2026-06-11 findings in
core/project_manager.py:

L6 — the sprite-file merge whitelist omitted 'precise', 'frame_width',
     'frame_height', 'animation_type' and 'speed'. A hand edit to those keys
     in sprites/<name>.json was ignored at load (the stale project.json copy
     won) and then erased from disk on the next save. The merge must now carry
     all five.

L7 — opening a .zip project extracts a full copy to a tempfile.mkdtemp dir.
     Switching/creating/closing a project already rmtrees the previous one, but
     quitting the IDE leaked the currently-open zip's extraction forever. A
     process-exit (atexit) sweep now removes it.

Constructs a real offscreen QApplication (no pytest-qt) so the tests run on
Python 3.11 too. ProjectManager is a QObject, so it needs a QApplication.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# --------------------------------------------------------------------------
# L6 — sprite merge whitelist
# --------------------------------------------------------------------------

def test_sprite_merge_carries_all_divergent_keys(_qapp, tmp_path):
    """A sprites/<name>.json that differs from the project.json copy on the five
    previously-dropped keys must win at load (file takes precedence)."""
    from core.project_manager import ProjectManager

    sprites_dir = tmp_path / "sprites"
    sprites_dir.mkdir()

    # File on disk is the NEWER copy (hand-edited): precise toggled on, speed
    # slowed, animation type changed, frame size set.
    file_data = {
        "name": "spr_monster",
        "asset_type": "sprite",
        "width": 32,
        "height": 32,
        "precise": True,
        "frames": 1,
        "frame_width": 24,
        "frame_height": 48,
        "animation_type": "strip",
        "speed": 4.0,
    }
    with open(sprites_dir / "spr_monster.json", "w", encoding="utf-8") as f:
        json.dump(file_data, f)

    # The embedded project.json copy is STALE on exactly those keys.
    project_data = {
        "assets": {
            "sprites": {
                "spr_monster": {
                    "name": "spr_monster",
                    "asset_type": "sprite",
                    "width": 32,
                    "height": 32,
                    "precise": False,
                    "frames": 1,
                    "frame_width": 32,
                    "frame_height": 32,
                    "animation_type": "single",
                    "speed": 10.0,
                }
            }
        }
    }

    pm = ProjectManager()
    pm._load_sprites_from_files(tmp_path, project_data)

    merged = project_data["assets"]["sprites"]["spr_monster"]
    assert merged["precise"] is True
    assert merged["frame_width"] == 24
    assert merged["frame_height"] == 48
    assert merged["animation_type"] == "strip"
    assert merged["speed"] == 4.0


def test_sprite_save_preserves_file_values_after_load(_qapp, tmp_path):
    """End-to-end: load a divergent sprite file, then save — the file on disk
    must keep the hand-edited values, not revert to the stale project.json ones."""
    from core.project_manager import ProjectManager

    sprites_dir = tmp_path / "sprites"
    sprites_dir.mkdir()

    sprite_file = sprites_dir / "spr_person.json"
    file_data = {
        "name": "spr_person",
        "asset_type": "sprite",
        "width": 32,
        "height": 32,
        "precise": True,
        "speed": 4.0,
        "animation_type": "strip",
        "frame_width": 16,
        "frame_height": 16,
        "frames": 1,
    }
    with open(sprite_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f)

    project_data = {
        "assets": {
            "sprites": {
                "spr_person": {
                    "name": "spr_person",
                    "asset_type": "sprite",
                    "width": 32,
                    "height": 32,
                    "precise": False,
                    "speed": 10.0,
                    "animation_type": "single",
                    "frame_width": 32,
                    "frame_height": 32,
                    "frames": 1,
                }
            }
        }
    }

    pm = ProjectManager()
    pm._load_sprites_from_files(tmp_path, project_data)
    pm.current_project_data = project_data
    pm._save_sprites_to_files(tmp_path)

    with open(sprite_file, "r", encoding="utf-8") as f:
        saved = json.load(f)

    # Before the fix, the load dropped these five keys, so the in-memory dict
    # carried the stale project.json values and the save reverted the file.
    assert saved["precise"] is True
    assert saved["speed"] == 4.0
    assert saved["animation_type"] == "strip"
    assert saved["frame_width"] == 16
    assert saved["frame_height"] == 16


# --------------------------------------------------------------------------
# L7 — temp extraction cleanup
# --------------------------------------------------------------------------

def test_atexit_cleanup_removes_temp_extraction(_qapp, tmp_path):
    """The atexit sweep removes whatever _temp_extraction_dir points at,
    covering the IDE-quit path that never calls close_project."""
    from core.project_manager import ProjectManager

    pm = ProjectManager()
    temp_dir = tmp_path / "pygamemaker_fake"
    temp_dir.mkdir()
    (temp_dir / "project.json").write_text("{}", encoding="utf-8")
    pm._temp_extraction_dir = str(temp_dir)

    pm._cleanup_temp_extraction_atexit()

    assert not temp_dir.exists()


def test_atexit_cleanup_is_noop_when_no_zip_open(_qapp):
    """No temp dir open -> the sweep must not raise."""
    from core.project_manager import ProjectManager

    pm = ProjectManager()
    pm._temp_extraction_dir = None
    # Must not raise.
    pm._cleanup_temp_extraction_atexit()


def test_atexit_cleanup_registered_in_constructor(_qapp):
    """Constructing a ProjectManager registers the exit sweep with atexit so a
    plain process quit cleans the open zip's extraction."""
    import atexit
    from unittest import mock
    from core.project_manager import ProjectManager

    with mock.patch.object(atexit, "register") as reg:
        pm = ProjectManager()

    registered = [c.args[0] for c in reg.call_args_list if c.args]
    assert pm._cleanup_temp_extraction_atexit in registered


def test_switching_project_cleans_previous_temp_extraction(_qapp, tmp_path):
    """Sanity: loading a different project after a zip rmtrees the previous
    extraction (the consequence-(1) leak, already closed by H2's
    _reset_zip_state)."""
    from core.project_manager import ProjectManager

    # Stand in a fake previous zip extraction.
    old_temp = tmp_path / "pygamemaker_old"
    old_temp.mkdir()
    (old_temp / "marker").write_text("x", encoding="utf-8")

    # A real (non-zip) project to switch to.
    proj = tmp_path / "proj"
    proj.mkdir()
    project_json = {
        "name": "proj",
        "version": "1.0",
        "assets": {"sprites": {}, "objects": {}, "rooms": {}},
    }
    with open(proj / "project.json", "w", encoding="utf-8") as f:
        json.dump(project_json, f)

    pm = ProjectManager()
    pm._temp_extraction_dir = str(old_temp)

    ok = pm.load_project(proj)
    assert ok
    assert not old_temp.exists()
    assert pm._temp_extraction_dir is None

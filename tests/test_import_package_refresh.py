"""
Regression test: imported room/object packages appear in the asset tree
immediately, without needing to quit and restart the IDE.

``ResourcePackager.import_room`` / ``import_object`` write the imported asset
(and its dependencies) straight into project.json on disk; they never touch the
in-memory model. The asset tree refresh used by the import handlers
(``force_project_refresh``) rebuilds ``current_project_data["assets"]`` from the
asset manager's cache, which still lacked the import — so the new asset stayed
invisible until a full reload (a restart). The user-visible symptom on the
compiled Linux build: imported rooms only showed up after quitting and
re-opening the project.

The fix folds the newly-written asset keys from disk into both the in-memory
project data and the asset cache (additive only, preserving unsaved edits)
before redrawing. These tests lock that in.

Constructs a real (offscreen) QApplication rather than using pytest-qt, so it
runs anywhere PySide6 is installed.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
import zipfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _make_project(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    data = {
        "name": "T",
        "version": "1.0",
        "settings": {},
        "assets": {
            "rooms": {"room_a": {"name": "room_a", "asset_type": "room",
                                 "width": 640, "height": 480, "instances": []}},
            "objects": {},
            "sprites": {},
            "backgrounds": {},
            "sounds": {},
        },
    }
    (proj / "project.json").write_text(json.dumps(data, indent=2))
    return proj


def _loaded_manager(proj):
    from core.project_manager import ProjectManager
    from core.asset_manager import AssetManager
    pm = ProjectManager(AssetManager())
    assert pm.load_project(proj)
    return pm


def _write_room_package(path, room_name="room_imported"):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("package.json", json.dumps({
            "type": "room",
            "room": {"name": room_name, "asset_type": "room",
                     "width": 800, "height": 600, "instances": []},
            "dependencies": {},
        }))


def test_merge_surfaces_disk_imported_room(_qapp, tmp_path):
    """A room written to project.json by import_room must appear in memory."""
    from utils.resource_packager import ResourcePackager

    proj = _make_project(tmp_path)
    pm = _loaded_manager(proj)

    pkg = tmp_path / "r.gmroom"
    _write_room_package(pkg)
    assert ResourcePackager.import_room(pkg, proj) == "room_imported"

    # Before the merge the in-memory model is unaware of the disk import.
    assert "room_imported" not in pm.current_project_data["assets"]["rooms"]

    added = pm.merge_imported_assets_from_disk()
    assert ("rooms", "room_imported") in added
    assert "room_imported" in pm.current_project_data["assets"]["rooms"]
    assert "room_imported" in pm.asset_manager.assets_cache["rooms"]


def test_merge_pulls_dependencies(_qapp, tmp_path):
    """Dependency objects/sprites bundled in the package are merged too."""
    from utils.resource_packager import ResourcePackager

    proj = _make_project(tmp_path)
    pm = _loaded_manager(proj)

    pkg = tmp_path / "r.gmroom"
    with zipfile.ZipFile(pkg, "w") as z:
        z.writestr("package.json", json.dumps({
            "type": "room",
            "room": {"name": "room_dep", "asset_type": "room",
                     "width": 320, "height": 240, "instances": []},
            "dependencies": {"objects": {"obj_dep": {"name": "obj_dep", "events": {}}}},
        }))
    assert ResourcePackager.import_room(pkg, proj) == "room_dep"

    added = pm.merge_imported_assets_from_disk()
    assert ("rooms", "room_dep") in added
    assert ("objects", "obj_dep") in added
    assert "obj_dep" in pm.current_project_data["assets"]["objects"]


def test_merge_is_additive_and_idempotent(_qapp, tmp_path):
    """Merge never overwrites existing entries, drops nothing, and re-running
    it adds nothing new (so it preserves unsaved in-memory edits)."""
    from utils.resource_packager import ResourcePackager

    proj = _make_project(tmp_path)
    pm = _loaded_manager(proj)

    # An unsaved, in-memory-only edit on an existing room + a memory-only room.
    pm.current_project_data["assets"]["rooms"]["room_a"]["width"] = 999
    pm.asset_manager.assets_cache["rooms"]["room_a"]["width"] = 999
    pm.current_project_data["assets"]["rooms"]["mem_only"] = {"name": "mem_only"}
    pm.asset_manager.assets_cache["rooms"]["mem_only"] = {"name": "mem_only"}

    pkg = tmp_path / "r.gmroom"
    _write_room_package(pkg)
    ResourcePackager.import_room(pkg, proj)

    pm.merge_imported_assets_from_disk()

    rooms = pm.current_project_data["assets"]["rooms"]
    # Existing unsaved edit untouched, memory-only room kept, import added.
    assert rooms["room_a"]["width"] == 999
    assert "mem_only" in rooms
    assert "room_imported" in rooms

    # Second pass is a no-op.
    assert pm.merge_imported_assets_from_disk() == []


def test_merge_no_project_loaded_is_safe(_qapp):
    from core.project_manager import ProjectManager
    from core.asset_manager import AssetManager
    pm = ProjectManager(AssetManager())
    assert pm.merge_imported_assets_from_disk() == []


def test_force_refresh_with_merge_shows_room_in_tree(_qapp, tmp_path):
    """End-to-end: force_project_refresh(merge_from_disk=True) surfaces the
    imported room in the actual AssetTreeWidget."""
    from PySide6.QtWidgets import QWidget
    from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
    from utils.resource_packager import ResourcePackager

    proj = _make_project(tmp_path)
    pm = _loaded_manager(proj)

    # force_project_refresh walks parent() for a `.project_manager` attribute.
    container = QWidget()
    container.project_manager = pm
    tree = AssetTreeWidget(container)
    tree.set_project(str(proj), pm.current_project_data)

    def room_names_in_tree():
        names = []
        for i in range(tree.topLevelItemCount()):
            cat = tree.topLevelItem(i)
            if getattr(cat, "asset_type", None) == "rooms":
                for j in range(cat.childCount()):
                    names.append(cat.child(j).asset_name)
        return names

    assert "room_imported" not in room_names_in_tree()

    pkg = tmp_path / "r.gmroom"
    _write_room_package(pkg)
    ResourcePackager.import_room(pkg, proj)

    tree.force_project_refresh(merge_from_disk=True)
    assert "room_imported" in room_names_in_tree()

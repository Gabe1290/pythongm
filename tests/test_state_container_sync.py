"""
Regression coverage for the two parallel state containers staying in sync:

    ProjectManager.current_project_data['assets']   (the on-save project dict)
    AssetManager.assets_cache                        (the live working copy)

These are independent top-level containers — load_assets_from_project_data
builds a *new* OrderedDict per asset type (asset_manager.py:728), so the two
dicts are NOT the same object. They are kept aligned manually: by the
save_assets_to_project_data sync (asset_manager.py:742) and, for room
reordering, by _reorder_room mirroring the rebuilt OrderedDict into both
(asset_tree_widget.py:967-975).

The historical bug: an earlier _reorder_room re-loaded project.json from disk
(which carries only room metadata + an _external_file pointer, NOT instances)
and assigned those instance-less dicts back into both containers, wiping every
room's in-memory `instances`. The fix rebuilds the order while preserving the
*same* room-data dict references. Nothing locked that in until now.
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _asset_manager():
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
        return AssetManager()


def _project_data_with_rooms():
    """Two rooms, each with a non-empty instances list (the data that the old
    bug wiped)."""
    return {
        "assets": {
            "rooms": OrderedDict([
                ("room_a", {"name": "room_a",
                            "instances": [{"object_name": "obj_a", "x": 0, "y": 0}]}),
                ("room_b", {"name": "room_b",
                            "instances": [{"object_name": "obj_b", "x": 32, "y": 32}]}),
                ("room_c", {"name": "room_c",
                            "instances": [{"object_name": "obj_c", "x": 64, "y": 64}]}),
            ])
        }
    }


class TestManagerSyncInvariants:
    """The save sync must make current_project_data faithfully reflect the live
    assets_cache — same order, same instance data — with no path that can
    silently drop instances."""

    def test_load_builds_independent_top_container_but_shares_inner_refs(self):
        am = _asset_manager()
        project_data = _project_data_with_rooms()
        original_rooms = project_data["assets"]["rooms"]

        am.load_assets_from_project_data(project_data)

        # Top-level container is a fresh OrderedDict (this independence is
        # exactly why the two must be re-synced on save).
        assert am.assets_cache["rooms"] is not original_rooms
        # ...but the inner room dicts are shared references, so instances seen
        # through the cache are the same objects as on the source data.
        assert am.assets_cache["rooms"]["room_a"] is original_rooms["room_a"]

    def test_save_mirrors_order_and_instances_into_project_data(self):
        am = _asset_manager()
        source = _project_data_with_rooms()
        am.load_assets_from_project_data(source)

        # Reorder + edit instances purely through the live cache.
        cache_rooms = am.assets_cache["rooms"]
        am.assets_cache["rooms"] = OrderedDict(
            (k, cache_rooms[k]) for k in ("room_c", "room_a", "room_b"))
        am.assets_cache["rooms"]["room_a"]["instances"].append(
            {"object_name": "obj_extra", "x": 99, "y": 99})

        target = {}
        am.save_assets_to_project_data(target)

        # Order must match the cache exactly...
        assert list(target["assets"]["rooms"].keys()) == ["room_c", "room_a", "room_b"]
        # ...and every room must retain its instances (none silently dropped).
        for name in ("room_a", "room_b", "room_c"):
            assert target["assets"]["rooms"][name]["instances"], \
                f"{name} lost its instances through the save sync"
        # The edit made via the cache is visible in the synced project data.
        assert len(target["assets"]["rooms"]["room_a"]["instances"]) == 2

    def test_save_never_empties_a_populated_room(self):
        """The failure signature of the old bug: a room with instances in the
        cache ending up instance-less in current_project_data."""
        am = _asset_manager()
        am.load_assets_from_project_data(_project_data_with_rooms())
        target = {}
        am.save_assets_to_project_data(target)
        for name, room in target["assets"]["rooms"].items():
            assert room["instances"] != [], f"{name} was emptied by the sync"


class _FakeProjectManager:
    """Captures save calls without touching disk."""
    def __init__(self):
        self.dirtied = False
        self.saved = False

    def mark_dirty(self):
        self.dirtied = True

    def save_project(self):
        self.saved = True


class _FakeIDEWindow:
    def __init__(self, asset_manager, project_data):
        self.asset_manager = asset_manager
        self.current_project_data = project_data
        self.project_manager = _FakeProjectManager()
        self.status = None

    def update_status(self, msg):
        self.status = msg


class _ReorderHost:
    """Duck-typed `self` for AssetTreeWidget._reorder_room: it only ever calls
    self.parent() and self.refresh_from_project(), so we can drive the real
    (regressed-then-fixed) method without constructing a QWidget."""
    def __init__(self, ide_window):
        self._ide = ide_window
        self.refreshed_with = None

    def parent(self):
        return self._ide

    def refresh_from_project(self, project_data):
        self.refreshed_with = project_data


class TestReorderRoomPreservesInstances:
    """_reorder_room is the method that historically wiped instances. Drive the
    real implementation and assert order changes while instances survive in
    BOTH containers."""

    def _setup(self):
        am = _asset_manager()
        project_data = _project_data_with_rooms()
        # Mirror load semantics: cache holds the live OrderedDict; project_data
        # holds the original (independent top container, shared inner refs).
        am.load_assets_from_project_data(project_data)
        # Re-point project_data's rooms at the cache's room objects so the two
        # containers start aligned the way they are right after a real load
        # + save round-trip in the running IDE.
        project_data["assets"]["rooms"] = OrderedDict(am.assets_cache["rooms"])
        ide = _FakeIDEWindow(am, project_data)
        host = _ReorderHost(ide)
        return am, project_data, ide, host

    def _reorder(self, host, room, direction):
        from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
        AssetTreeWidget._reorder_room(host, room, direction)

    def test_move_to_bottom_changes_order_in_both_containers(self):
        am, project_data, ide, host = self._setup()
        self._reorder(host, "room_a", "bottom")

        expected = ["room_b", "room_c", "room_a"]
        assert list(am.assets_cache["rooms"].keys()) == expected
        assert list(project_data["assets"]["rooms"].keys()) == expected

    def test_reorder_preserves_instances_in_both_containers(self):
        am, project_data, ide, host = self._setup()
        self._reorder(host, "room_c", "top")

        for name in ("room_a", "room_b", "room_c"):
            assert am.assets_cache["rooms"][name]["instances"], \
                f"cache: {name} lost instances on reorder"
            assert project_data["assets"]["rooms"][name]["instances"], \
                f"project_data: {name} lost instances on reorder"

    def test_reorder_keeps_same_room_object_references(self):
        """The crux of the fix: rebuild the order without replacing the room
        dicts, so the in-memory instances stay attached."""
        am, project_data, ide, host = self._setup()
        before = am.assets_cache["rooms"]["room_b"]
        self._reorder(host, "room_a", "bottom")
        assert am.assets_cache["rooms"]["room_b"] is before
        # Both containers reference the very same rebuilt OrderedDict.
        assert project_data["assets"]["rooms"] is am.assets_cache["rooms"]

    def test_reorder_persists_via_project_manager(self):
        am, project_data, ide, host = self._setup()
        self._reorder(host, "room_a", "bottom")
        assert ide.project_manager.dirtied
        assert ide.project_manager.saved
        # Tree refreshed from the now-current in-memory project data.
        assert host.refreshed_with is ide.current_project_data

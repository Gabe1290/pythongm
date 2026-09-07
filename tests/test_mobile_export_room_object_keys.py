"""H5, docs/FULL_AUDIT_2026-09-07.md: the Android and iOS exporters used to
hand-copy a short, incomplete list of room/object side-file keys when
merging rooms/<name>.json / objects/<name>.json into project_data --
missing tiles, views, enable_views, backgrounds, persistent (rooms) and
remember_destroyed (objects, iOS only -- Android's list already had it).

Both are now routed through utils/project_file_merge.py's merge_room_file/
merge_object_file (the same kernel export/base_exporter.py and the desktop
exporters use): Android by simply no longer overriding the loaders (so it
inherits BaseKivyExporter's), iOS by calling the kernel functions directly
from its own overrides (it can't inherit BaseKivyExporter -- a QObject
subclass with a substantially different Xcode/kivy-ios build flow).

These tests build a small on-disk project with a room/object side file
carrying every key the pre-fix code silently dropped, run each exporter's
loaders against it, and assert every key survived into project_data.
"""
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

from conftest import skip_without_pyside6


def _write_project(tmp_path):
    """A project with one room and one object, each carrying keys the
    pre-fix hand-copied lists dropped."""
    root = tmp_path / "proj"
    (root / "rooms").mkdir(parents=True)
    (root / "objects").mkdir()

    room_data = {
        "width": 640, "height": 480,
        "background_color": "#000000",
    }
    room_file_data = {
        "instances": [],
        "width": 800, "height": 600,
        "background_color": "#112233",
        "background_image": "bg1",
        "tile_horizontal": True, "tile_vertical": False,
        "tiles": [{"x": 0, "y": 0, "bg": "bg1"}],
        "views_enabled": True, "enable_views": True,
        "views": [{"x": 0, "y": 0, "w": 400, "h": 300}],
        "persistent": True,
        "backgrounds": [{"name": "bg1", "foreground": False}],
        "bg_hspeed": 1.5, "bg_vspeed": -2.0, "bg_stretch": True,
        "creation_code": "self.spawned = True",
    }
    (root / "rooms" / "room_1.json").write_text(
        json.dumps(room_file_data), encoding="utf-8")

    object_data = {"name": "obj_p", "sprite": ""}
    object_file_data = {
        "events": {"create": {"actions": []}},
        "sprite": "spr_p", "visible": True, "solid": True,
        "persistent": True, "depth": 5, "parent": "obj_base",
        "mask": "spr_mask", "imported": True,
        "remember_destroyed": True,
    }
    (root / "objects" / "obj_p.json").write_text(
        json.dumps(object_file_data), encoding="utf-8")

    project_data = {
        "name": "Proj",
        "assets": {
            "rooms": {"room_1": room_data},
            "objects": {"obj_p": object_data},
        },
    }
    (root / "project.json").write_text(json.dumps(project_data), encoding="utf-8")
    return root, project_data


_ROOM_KEYS_THAT_WERE_DROPPED = (
    "tiles", "views", "views_enabled", "enable_views", "backgrounds",
    "persistent", "bg_hspeed", "bg_vspeed", "bg_stretch", "creation_code",
)
_OBJECT_KEYS_THAT_WERE_DROPPED = (
    "sprite", "visible", "solid", "persistent", "depth", "parent",
    "mask", "imported", "remember_destroyed",
)


class TestAndroidRoomObjectKeys:
    def test_room_keys_all_survive_the_side_file_merge(self, tmp_path):
        from export.android.android_exporter import AndroidExporter
        root, project_data = _write_project(tmp_path)
        ex = AndroidExporter()
        ex.project_data = project_data
        ex._load_rooms_from_files(root)

        room = project_data["assets"]["rooms"]["room_1"]
        for key in _ROOM_KEYS_THAT_WERE_DROPPED:
            assert key in room, "room lost key %r" % key
        assert room["tile_horizontal"] is True
        assert room["width"] == 800  # file overrides the embedded stub

    def test_object_keys_all_survive_the_side_file_merge(self, tmp_path):
        from export.android.android_exporter import AndroidExporter
        root, project_data = _write_project(tmp_path)
        ex = AndroidExporter()
        ex.project_data = project_data
        ex._load_objects_from_files(root)

        obj = project_data["assets"]["objects"]["obj_p"]
        for key in _OBJECT_KEYS_THAT_WERE_DROPPED:
            assert key in obj, "object lost key %r" % key
        assert obj["events"]["create"]["actions"] == []


class TestIOSRoomObjectKeys:
    @pytest.fixture(scope="class")
    def qapp(self):
        from PySide6.QtWidgets import QApplication
        return QApplication.instance() or QApplication([])

    def test_room_keys_all_survive_the_side_file_merge(self, qapp, tmp_path):
        from export.ios.ios_exporter import iOSExporter
        root, project_data = _write_project(tmp_path)
        ex = iOSExporter()
        ex.project_data = project_data
        ex._load_rooms_from_files(root)

        room = project_data["assets"]["rooms"]["room_1"]
        for key in _ROOM_KEYS_THAT_WERE_DROPPED:
            assert key in room, "room lost key %r" % key
        assert room["tile_horizontal"] is True
        assert room["width"] == 800

    def test_object_keys_all_survive_the_side_file_merge(self, qapp, tmp_path):
        from export.ios.ios_exporter import iOSExporter
        root, project_data = _write_project(tmp_path)
        ex = iOSExporter()
        ex.project_data = project_data
        ex._load_objects_from_files(root)

        obj = project_data["assets"]["objects"]["obj_p"]
        for key in _OBJECT_KEYS_THAT_WERE_DROPPED:
            assert key in obj, "object lost key %r" % key
        assert obj["events"]["create"]["actions"] == []

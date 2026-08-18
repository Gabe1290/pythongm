"""Per-export-path coverage for Tier 6 (manifest-ify sprites): every path
that previously read `project_data['assets']['sprites'][name]` fields
directly, found by a targeted survey of the whole codebase, gets its own
regression test here so a stub sprite entry ({name, asset_type,
_external_file}) can never silently degrade that path again.

Paths covered (one class each): HTML5Exporter, BaseKivyExporter (covers
exe/linux/macos + Android via inheritance), iOSExporter, ResourcePackager
(export_object/export_room), the room editor's floated/detached disk
fallback, the asset-tree object-sprite-thumbnail disk fallback, and the
sprite trash/rollback side-file gate.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _sprite_stub(name="spr_hero"):
    return {"name": name, "asset_type": "sprite", "_external_file": f"sprites/{name}.json"}


_SPRITE_FILE_BODY = {
    "name": "spr_hero",
    "asset_type": "sprite",
    "file_path": "sprites/spr_hero.png",
    "width": 32,
    "height": 32,
    "origin_x": 16,
    "origin_y": 16,
    "frames": 2,
    "frame_width": 16,
    "frame_height": 32,
    "animation_type": "strip_h",
    "speed": 10.0,
    "thumbnail": "thumbnails/spr_hero_thumb.png",
}


def _make_project_with_stub_sprite(tmp_path, extra_dirs=()):
    proj_dir = tmp_path / "proj"
    (proj_dir / "sprites").mkdir(parents=True)
    for d in extra_dirs:
        (proj_dir / d).mkdir(parents=True, exist_ok=True)
    (proj_dir / "sprites" / "spr_hero.json").write_text(
        json.dumps(_SPRITE_FILE_BODY), encoding="utf-8")
    # A real 32x32 PNG so file-copy steps and the strip_h frame-crop have
    # something real to find/slice (frame_width=16, frame_height=32 below).
    png_bytes = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000020000000200806000000737a7a"
        "f40000002f49444154789cedce310100300c803036ff9e5b197d8201f2a6a6c3"
        "fee51c0000000000000000000000000000a06a0130e3023e36995eb100000000"
        "49454e44ae426082")
    (proj_dir / "sprites" / "spr_hero.png").write_bytes(png_bytes)
    project_data = {
        "name": "StubSpriteGame",
        "version": "1.0.0",
        "room_order": [],
        "assets": {
            "sprites": {"spr_hero": _sprite_stub()},
            "sounds": {}, "backgrounds": {},
            "objects": {}, "rooms": {}, "fonts": {}, "data": {},
        },
    }
    (proj_dir / "project.json").write_text(json.dumps(project_data), encoding="utf-8")
    return proj_dir


class TestHTML5ExporterSpriteMerge:
    def test_load_sprite_files_resolves_the_stub(self, tmp_path):
        from export.HTML5.html5_exporter import HTML5Exporter
        with patch.object(Path, 'read_text', return_value="template"):
            exporter = HTML5Exporter()

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        project_data = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))

        exporter._load_sprite_files(proj_dir, project_data)

        merged = project_data["assets"]["sprites"]["spr_hero"]
        assert merged["file_path"] == "sprites/spr_hero.png"
        assert merged["width"] == 32
        assert merged["frames"] == 2

    def test_encode_sprites_encodes_after_merge(self, tmp_path):
        """The real export() sequencing: merge before encode_sprites."""
        from export.HTML5.html5_exporter import HTML5Exporter
        with patch.object(Path, 'read_text', return_value="template"):
            exporter = HTML5Exporter()

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        project_data = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))

        exporter._load_sprite_files(proj_dir, project_data)
        encoded = exporter.encode_sprites(proj_dir, project_data)

        assert "spr_hero" in encoded
        assert encoded["spr_hero"].startswith("data:image/png;base64,")


class TestBaseKivyExporterSpriteMerge:
    def test_load_project_merges_sprite_file(self, tmp_path):
        from export.base_exporter import BaseKivyExporter

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        exporter = BaseKivyExporter()
        exporter._load_project(str(proj_dir), str(tmp_path / "out"), {})

        merged = exporter.project_data["assets"]["sprites"]["spr_hero"]
        assert merged["file_path"] == "sprites/spr_hero.png"
        assert merged["frame_width"] == 16
        assert merged["thumbnail"] == "thumbnails/spr_hero_thumb.png"

    def test_android_exporter_inherits_sprite_loading(self, tmp_path):
        """AndroidExporter overrides the room/object loaders but not the
        sprite loader -- confirm it still gets the base implementation via
        inheritance rather than silently reading the unmerged stub."""
        from export.android.android_exporter import AndroidExporter

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        exporter = AndroidExporter()
        exporter._load_project(str(proj_dir), str(tmp_path / "out"), {})

        merged = exporter.project_data["assets"]["sprites"]["spr_hero"]
        assert merged["file_path"] == "sprites/spr_hero.png"
        assert merged["width"] == 32


class TestIOSExporterSpriteMerge:
    def test_load_sprites_from_files_merges_stub(self, tmp_path):
        from export.ios.ios_exporter import iOSExporter

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        exporter = iOSExporter()
        exporter.project_data = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        exporter._load_sprites_from_files(proj_dir)

        merged = exporter.project_data["assets"]["sprites"]["spr_hero"]
        assert merged["file_path"] == "sprites/spr_hero.png"
        assert merged["height"] == 32


class TestResourcePackagerSpriteMerge:
    def test_export_object_packages_full_sprite_metadata(self, tmp_path):
        from utils.resource_packager import ResourcePackager

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        (proj_dir / "objects").mkdir()
        project_data = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        project_data["assets"]["objects"]["obj_hero"] = {
            "name": "obj_hero", "asset_type": "object", "sprite": "spr_hero",
            "visible": True, "events": {},
        }
        (proj_dir / "project.json").write_text(json.dumps(project_data), encoding="utf-8")

        out_path = tmp_path / "obj_hero.gmobj"
        assert ResourcePackager.export_object(proj_dir, "obj_hero", out_path) is True

        import zipfile
        with zipfile.ZipFile(out_path, 'r') as zf:
            package_data = json.loads(zf.read('package.json'))
            # The extracted sprite PNG must actually be in the archive --
            # only possible if dependencies carried a real file_path.
            assert 'sprites/spr_hero.png' in zf.namelist()

        sprite_dep = package_data["dependencies"]["sprites"]["spr_hero"]
        assert sprite_dep["file_path"] == "sprites/spr_hero.png"
        assert sprite_dep["width"] == 32

    def test_export_room_packages_full_sprite_metadata_via_object(self, tmp_path):
        from utils.resource_packager import ResourcePackager

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        (proj_dir / "objects").mkdir()
        (proj_dir / "rooms").mkdir()
        project_data = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        project_data["assets"]["objects"]["obj_hero"] = {
            "name": "obj_hero", "asset_type": "object", "sprite": "spr_hero",
            "visible": True, "events": {},
        }
        project_data["assets"]["rooms"]["room_test"] = {
            "name": "room_test", "width": 640, "height": 480,
            "instances": [{"object_name": "obj_hero", "x": 0, "y": 0}],
        }
        (proj_dir / "project.json").write_text(json.dumps(project_data), encoding="utf-8")

        out_path = tmp_path / "room_test.gmroom"
        assert ResourcePackager.export_room(proj_dir, "room_test", out_path) is True

        import zipfile
        with zipfile.ZipFile(out_path, 'r') as zf:
            package_data = json.loads(zf.read('package.json'))

        sprite_dep = package_data["dependencies"]["sprites"]["spr_hero"]
        assert sprite_dep["file_path"] == "sprites/spr_hero.png"


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


class TestAssetTreeItemSpriteThumbnailFallback:
    def test_load_object_sprite_thumbnail_disk_fallback_merges_stub(self, tmp_path, _qapp):
        """No asset_manager attached -- forces the raw project.json disk
        fallback branch, which must now merge the sprite side file too."""
        from PySide6.QtWidgets import QTreeWidget
        from widgets.asset_tree.asset_tree_item import AssetTreeItem

        proj_dir = _make_project_with_stub_sprite(tmp_path)

        tree = QTreeWidget()
        tree.project_path = str(proj_dir)
        item = AssetTreeItem(parent=tree, asset_type="objects", asset_name="obj_hero")

        assert item.load_object_sprite_thumbnail("spr_hero") is True
        # A strip_h sprite with frame_width=16 must be CROPPED, not loaded
        # whole -- only possible if animation_type/frame_width were merged
        # in from the side file (the stub alone carries neither).
        icon = item.icon(0)
        assert not icon.isNull()


class TestRoomEditorDiskFallbackSpriteMerge:
    def test_merge_sprite_files_into_resolves_stub(self, tmp_path):
        from editors.room_editor import RoomEditor

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        editor = RoomEditor.__new__(RoomEditor)
        editor.project_path = proj_dir

        project_data = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        editor._merge_sprite_files_into(project_data)

        merged = project_data["assets"]["sprites"]["spr_hero"]
        assert merged["file_path"] == "sprites/spr_hero.png"
        assert merged["origin_x"] == 16


class TestAssetTrashSpriteSideFile:
    def test_delete_asset_trashes_sprite_side_file(self, tmp_path):
        """core/asset_manager.py's delete_asset must move sprites/<name>.json
        into .trash/ alongside the image, not leave it as an orphan."""
        from core.asset_manager import AssetManager

        proj_dir = _make_project_with_stub_sprite(tmp_path)
        am = AssetManager()
        am.project_directory = proj_dir
        am.assets_cache = {"sprites": {"spr_hero": dict(_SPRITE_FILE_BODY)}, "objects": {}}

        assert am.delete_asset("sprites", "spr_hero") is True

        assert not (proj_dir / "sprites" / "spr_hero.json").exists()
        assert not (proj_dir / "sprites" / "spr_hero.png").exists()

        from utils.asset_trash import list_trash
        entries = list_trash(proj_dir)
        assert len(entries) == 1
        assert entries[0]["files"].get("side_file") == "sprites/spr_hero.json"

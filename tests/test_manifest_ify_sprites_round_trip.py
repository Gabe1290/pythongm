"""Mandatory round-trip proof for docs/DEFERRED_GAPS_2026_PLAN.md Tier 6
("Manifest-ify sprites in project.json"): sprites with a sprites/<name>.json
side file now strip their WHOLE body to a lightweight stub
({name, asset_type, _external_file}) on save -- unlike objects (which only
stripped `events`), sprites have no single risky subfield worth isolating.

Mirrors tests/test_manifest_ify_objects_round_trip.py's structure exactly:
fresh project (sprites/ dir present), legacy embedded-only project (no
sprites/ dir), a .zip export/import round-trip, and a real bundled sample
(maze_1, whose sprites/ dir already exists from _save_sprites_to_files
having always written full sprite bodies there, even before stripping was
wired up).
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_project_manager():
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()
        return pm


_SPRITE_FULL = {
    "name": "spr_hero",
    "asset_type": "sprite",
    "file_path": "sprites/spr_hero.png",
    "width": 32,
    "height": 32,
    "origin_x": 16,
    "origin_y": 16,
    "precise": False,
    "frames": 4,
    "frame_width": 32,
    "frame_height": 32,
    "animation_type": "strip_h",
    "speed": 10.0,
    "imported": True,
    "created": "2026-08-01T00:00:00",
    "modified": "2026-08-01T00:00:00",
    "thumbnail": "thumbnails/spr_hero_thumb.png",
}


def _project_data(name="RoundTripGame"):
    return {
        "name": name,
        "version": "1.0.0",
        "room_order": [],
        "assets": {
            "sprites": {"spr_hero": json.loads(json.dumps(_SPRITE_FULL))},
            "sounds": {}, "backgrounds": {},
            "objects": {}, "rooms": {}, "fonts": {}, "data": {},
        },
    }


class TestFreshProjectRoundTrip:
    """sprites/ dir present -> the whole sprite body strips to a stub."""

    def test_save_strips_sprite_to_stub(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()

        assert pm._save_to_folder(proj_dir) is True

        on_disk = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        sprite_entry = on_disk["assets"]["sprites"]["spr_hero"]
        assert sprite_entry == {
            "name": "spr_hero",
            "asset_type": "sprite",
            "_external_file": "sprites/spr_hero.json",
        }

        side_file = json.loads((proj_dir / "sprites" / "spr_hero.json").read_text(encoding="utf-8"))
        assert side_file["file_path"] == "sprites/spr_hero.png"
        assert side_file["width"] == 32
        assert side_file["frames"] == 4
        assert side_file["thumbnail"] == "thumbnails/spr_hero_thumb.png"

    def test_load_after_save_is_byte_for_byte_equivalent(self, tmp_path):
        """load -> save -> reload; current_project_data must carry the exact
        same sprite data as before the save (not the stub disk form)."""
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        original = _project_data()
        pm.current_project_data = json.loads(json.dumps(original))

        assert pm._save_to_folder(proj_dir) is True

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True

        reloaded = pm2.current_project_data["assets"]["sprites"]["spr_hero"]
        for key, value in _SPRITE_FULL.items():
            assert reloaded[key] == value, f"{key} not restored on reload"
        assert "_external_file" not in reloaded

    def test_two_save_load_cycles_are_stable(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()
        assert pm._save_to_folder(proj_dir) is True

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True
        assert pm2._save_to_folder(proj_dir) is True

        pm3 = _make_project_manager()
        assert pm3.load_project(proj_dir) is True
        reloaded = pm3.current_project_data["assets"]["sprites"]["spr_hero"]
        assert reloaded["file_path"] == "sprites/spr_hero.png"
        assert reloaded["frames"] == 4


class TestLegacyEmbeddedOnlyProjectUnaffected:
    """No sprites/ dir at all -- must keep pre-existing fully-embedded
    behaviour byte for byte."""

    def test_save_does_not_strip_sprite_without_sprites_dir(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        proj_dir.mkdir()  # deliberately no sprites/ subdir
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()

        assert pm._save_to_folder(proj_dir) is True

        on_disk = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        sprite_entry = on_disk["assets"]["sprites"]["spr_hero"]
        for key, value in _SPRITE_FULL.items():
            assert sprite_entry[key] == value
        assert "_external_file" not in sprite_entry
        assert not (proj_dir / "sprites").exists()

    def test_load_after_save_still_round_trips(self, tmp_path):
        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        proj_dir.mkdir()
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()
        assert pm._save_to_folder(proj_dir) is True

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True
        reloaded = pm2.current_project_data["assets"]["sprites"]["spr_hero"]
        assert reloaded["file_path"] == "sprites/spr_hero.png"


class TestZipRoundTrip:
    def test_zip_export_import_preserves_sprite_data(self, tmp_path):
        from utils.project_compression import ProjectCompressor

        pm = _make_project_manager()
        proj_dir = tmp_path / "proj"
        for sub in ("sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"):
            (proj_dir / sub).mkdir(parents=True)
        pm.current_project_path = proj_dir
        pm.current_project_data = _project_data()
        assert pm._save_to_folder(proj_dir) is True

        zip_path = tmp_path / "game.zip"
        assert ProjectCompressor.compress_project(proj_dir, zip_path) is True

        extract_dir = tmp_path / "extracted"
        assert ProjectCompressor.decompress_project(zip_path, extract_dir) is True

        project_file = next(extract_dir.rglob("project.json"))
        extracted_proj_dir = project_file.parent

        pm2 = _make_project_manager()
        assert pm2.load_project(extracted_proj_dir) is True
        reloaded = pm2.current_project_data["assets"]["sprites"]["spr_hero"]
        assert reloaded["file_path"] == "sprites/spr_hero.png"
        assert reloaded["frames"] == 4
        assert reloaded["thumbnail"] == "thumbnails/spr_hero_thumb.png"


class TestRealSampleRoundTrip:
    """maze_1's real sprite data (spr_goal/spr_person/spr_wall), whose
    sprites/ dir already existed pre-Tier-6 (full bodies were always
    written there, just never stripped from project.json until now)."""

    def test_maze_1_sprites_survive_save_reload(self, tmp_path):
        import shutil

        repo_root = Path(__file__).resolve().parent.parent
        src = repo_root / "samples" / "maze_1"
        proj_dir = tmp_path / "maze_1_copy"
        shutil.copytree(src, proj_dir)

        original = json.loads((src / "project.json").read_text(encoding="utf-8"))
        original_sprites = {
            name: data for name, data in original["assets"]["sprites"].items()
            if isinstance(data, dict)
        }
        assert original_sprites, "fixture sample has no embedded sprite data to test against"

        pm = _make_project_manager()
        assert pm.load_project(proj_dir) is True
        assert pm._save_to_folder(proj_dir) is True

        on_disk = json.loads((proj_dir / "project.json").read_text(encoding="utf-8"))
        for name, sprite in original_sprites.items():
            entry = on_disk["assets"]["sprites"][name]
            assert entry == {
                "name": name, "asset_type": "sprite",
                "_external_file": f"sprites/{name}.json",
            }, f"{name} should be a stub"
            side_file = json.loads(
                (proj_dir / "sprites" / f"{name}.json").read_text(encoding="utf-8"))
            assert side_file.get("file_path") == sprite.get("file_path"), (
                f"{name} file_path lost in side file")
            assert side_file.get("width") == sprite.get("width")
            assert side_file.get("height") == sprite.get("height")

        pm2 = _make_project_manager()
        assert pm2.load_project(proj_dir) is True
        for name, sprite in original_sprites.items():
            reloaded = pm2.current_project_data["assets"]["sprites"][name]
            assert reloaded.get("file_path") == sprite.get("file_path"), (
                f"{name} file_path not restored on reload")
            assert reloaded.get("width") == sprite.get("width")
            assert reloaded.get("height") == sprite.get("height")
            assert reloaded.get("frames") == sprite.get("frames")

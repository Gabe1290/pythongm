"""Regression tests for replace_sprite_image (audit M2).

docs/FULL_AUDIT_2026-06-11.md: the method unlinked the existing image and
thumbnail BEFORE copying the new file, so a failed copy (removed media,
permission error, disk full) destroyed the project's only copy of the
sprite art and left file_path dangling. The copy now lands in a validated
temp file first and the old files are retired only after it succeeds.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from conftest import skip_without_pil

pytestmark = skip_without_pil


def _make_png(path: Path, size=(8, 8), color=(255, 0, 0, 255)):
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, color).save(path, "PNG")


@pytest.fixture
def manager_with_sprite(tmp_path):
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
    am = AssetManager()
    am.set_project_directory(tmp_path)

    # Seed an existing sprite with a real image + thumbnail on disk.
    _make_png(tmp_path / "sprites" / "spr_hero.png", size=(16, 16))
    _make_png(tmp_path / "thumbnails" / "spr_hero_thumb.png", size=(4, 4))
    am.assets_cache["sprites"] = {
        "spr_hero": {
            "name": "spr_hero", "asset_type": "sprite",
            "file_path": "sprites/spr_hero.png",
            "thumbnail": "thumbnails/spr_hero_thumb.png",
            "width": 16, "height": 16,
        }
    }
    return am, tmp_path


class TestFailedCopyKeepsOriginal:
    def test_missing_source_does_not_destroy_original(self, manager_with_sprite):
        am, project = manager_with_sprite
        original = project / "sprites" / "spr_hero.png"
        before = original.read_bytes()

        # Source does not exist -> copy must fail, original must survive.
        result = am.replace_sprite_image(project / "nope_missing.png", "spr_hero")

        assert result is None
        assert original.exists()
        assert original.read_bytes() == before
        # file_path still points at the surviving art
        assert am.assets_cache["sprites"]["spr_hero"]["file_path"] == "sprites/spr_hero.png"

    def test_copy_failure_midway_keeps_original(self, manager_with_sprite):
        am, project = manager_with_sprite
        new_src = project / "incoming.png"
        _make_png(new_src, size=(32, 32))
        original = project / "sprites" / "spr_hero.png"
        before = original.read_bytes()

        with patch('core.asset_manager.shutil.copy2', side_effect=OSError("disk full")):
            result = am.replace_sprite_image(new_src, "spr_hero")

        assert result is None
        assert original.exists()
        assert original.read_bytes() == before  # untouched


class TestSuccessfulReplace:
    def test_replace_same_suffix_updates_dimensions(self, manager_with_sprite):
        am, project = manager_with_sprite
        new_src = project / "incoming.png"
        _make_png(new_src, size=(32, 24))

        result = am.replace_sprite_image(new_src, "spr_hero")

        assert result is not None
        assert result["width"] == 32
        assert result["height"] == 24
        assert (project / "sprites" / "spr_hero.png").exists()
        # No stray temp files left in sprites/
        leftovers = [p.name for p in (project / "sprites").iterdir()
                     if p.name != "spr_hero.png"]
        assert leftovers == []

    def test_replace_different_suffix_removes_old_file(self, manager_with_sprite):
        am, project = manager_with_sprite
        new_src = project / "incoming.jpg"
        # JPEG can't hold alpha; use RGB
        from PIL import Image
        Image.new("RGB", (10, 10), (0, 128, 255)).save(new_src, "JPEG")

        result = am.replace_sprite_image(new_src, "spr_hero")

        assert result is not None
        assert result["file_path"] == "sprites/spr_hero.jpg"
        assert (project / "sprites" / "spr_hero.jpg").exists()
        # the old .png is gone (different suffix => different path)
        assert not (project / "sprites" / "spr_hero.png").exists()


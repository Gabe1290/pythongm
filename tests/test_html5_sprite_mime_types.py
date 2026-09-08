"""L10, docs/FULL_AUDIT_2026-09-07.md: HTML5 export mime sniffing knew
only PNG/JPEG.

HTML5Exporter.encode_sprites (and its background twin) embedded every
sprite as a base64 data: URI, but the mime label defaulted to
image/png and special-cased only .jpg/.jpeg (sprites) or nothing at
all (backgrounds). core/asset_manager.py's SUPPORTED_FORMATS accepts
.bmp/.gif/.tga/.webp too, so any of those was embedded with a mime
label that doesn't match its real bytes -- "data:image/png;base64,
<real BMP/WEBP/TGA bytes>" -- and some browsers refuse to decode a
mismatched label rather than sniffing the actual content.

Fix: a shared _image_mime_type() helper (mimetypes.guess_type plus a
small override table for the two extensions Python's own stdlib
doesn't know on every platform -- .webp and .tga, confirmed empirically
absent here) used by both the sprite and background encoding sites.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest


class TestImageMimeTypeHelper:
    @pytest.mark.parametrize("filename,expected", [
        ("spr_player.png", "image/png"),
        ("spr_player.PNG", "image/png"),   # case-insensitive
        ("spr_player.jpg", "image/jpeg"),
        ("spr_player.jpeg", "image/jpeg"),
        ("spr_player.bmp", "image/bmp"),
        ("spr_player.gif", "image/gif"),
        ("spr_player.webp", "image/webp"),
        ("spr_player.tga", "image/x-tga"),
    ])
    def test_known_sprite_extensions_get_the_right_mime_type(self, filename, expected):
        from export.HTML5.html5_exporter import _image_mime_type
        assert _image_mime_type(Path(filename)) == expected

    def test_every_supported_sprite_format_has_a_real_mime_type(self):
        """Cross-check against the actual accepted-import-formats list --
        if a new sprite format is ever added there, this fails until the
        HTML5 exporter's table (or mimetypes itself) also knows it."""
        from export.HTML5.html5_exporter import _image_mime_type
        from core.asset_manager import AssetManager

        for ext in AssetManager.SUPPORTED_FORMATS["sprites"]:
            mime = _image_mime_type(Path(f"x{ext}"))
            assert mime != "application/octet-stream", (
                f"{ext} has no known mime type -- would embed as octet-stream")
            assert mime.startswith("image/"), f"{ext} resolved to non-image mime {mime!r}"


class TestEncodeSpritesEmbedsTheRealMimeType:
    def _project(self, tmp_path, sprite_filename, sprite_bytes=b"fake-image-bytes"):
        sprite_path = tmp_path / sprite_filename
        sprite_path.write_bytes(sprite_bytes)
        project_data = {
            "assets": {
                "sprites": {
                    "spr_test": {"file_path": sprite_filename},
                },
                "backgrounds": {
                    "bg_test": {"file_path": sprite_filename},
                },
            }
        }
        return tmp_path, project_data

    @pytest.mark.parametrize("filename,expected_prefix", [
        ("spr.bmp", "data:image/bmp;base64,"),
        ("spr.webp", "data:image/webp;base64,"),
        ("spr.tga", "data:image/x-tga;base64,"),
        ("spr.gif", "data:image/gif;base64,"),
        ("spr.png", "data:image/png;base64,"),
    ])
    def test_sprite_data_uri_carries_the_correct_mime_prefix(self, tmp_path, filename, expected_prefix):
        from export.HTML5.html5_exporter import HTML5Exporter

        project_path, project_data = self._project(tmp_path, filename)
        exporter = HTML5Exporter()
        encoded = exporter.encode_sprites(project_path, project_data)

        assert encoded["spr_test"].startswith(expected_prefix)

    def test_background_data_uri_carries_the_correct_mime_prefix(self, tmp_path):
        """Backgrounds had no special-casing at all before this fix -- not
        even .gif, unlike sprites."""
        from export.HTML5.html5_exporter import HTML5Exporter

        project_path, project_data = self._project(tmp_path, "bg.webp")
        exporter = HTML5Exporter()
        encoded = exporter.encode_sprites(project_path, project_data)

        assert encoded["bg_test"].startswith("data:image/webp;base64,")

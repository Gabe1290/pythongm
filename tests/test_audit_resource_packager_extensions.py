"""Regression tests for M58 — resource packager hardcoded .png extension.

The packager previously located sprite/background dependency files as
``<type>/<name>.png`` on both export and import, so any asset imported with a
non-PNG suffix (.jpg/.jpeg/.bmp/.gif/.tga/.webp — all in
AssetManager.SUPPORTED_FORMATS) was silently dropped: the export's exists()
check failed and on import the file was never extracted, leaving the imported
object/room referencing a sprite that does not exist in the recipient project.

These tests run pure logic (zip + json on disk), no Qt required, so they pass
on Python 3.11 too.
"""

import json
import zipfile
from pathlib import Path

from utils.resource_packager import ResourcePackager


def _write_project(root: Path, assets: dict):
    (root).mkdir(parents=True, exist_ok=True)
    project = {"assets": assets}
    (root / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return root


def _make_project_with_jpg_sprite(root: Path):
    """A project whose object 'hero' uses sprite 'player' stored as .jpg."""
    sprites_dir = root / "sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)
    # Fake image bytes (content doesn't matter to the packager).
    (sprites_dir / "player.jpg").write_bytes(b"\xff\xd8\xff JPEG-DATA")
    assets = {
        "objects": {
            "hero": {"name": "hero", "sprite": "player"},
        },
        "sprites": {
            "player": {"name": "player", "file_path": "sprites/player.jpg"},
        },
    }
    return _write_project(root, assets)


def test_export_object_includes_non_png_sprite(tmp_path):
    proj = _make_project_with_jpg_sprite(tmp_path / "src")
    out = tmp_path / "hero.gmobj"

    assert ResourcePackager.export_object(proj, "hero", out) is True

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    # The .jpg dependency must be present (not silently dropped).
    assert "sprites/player.jpg" in names
    assert "sprites/player.png" not in names


def test_import_object_extracts_non_png_sprite(tmp_path):
    src = _make_project_with_jpg_sprite(tmp_path / "src")
    out = tmp_path / "hero.gmobj"
    assert ResourcePackager.export_object(src, "hero", out) is True

    # Fresh empty target project.
    dst = _write_project(tmp_path / "dst", {"objects": {}, "sprites": {}})

    name = ResourcePackager.import_object(out, dst)
    assert name == "hero"

    # The .jpg image file landed on disk.
    assert (dst / "sprites" / "player.jpg").exists()

    # The sprite metadata was added to the recipient project (not skipped).
    project_data = json.loads((dst / "project.json").read_text(encoding="utf-8"))
    sprites = project_data["assets"]["sprites"]
    assert "player" in sprites
    assert sprites["player"]["file_path"] == "sprites/player.jpg"


def test_round_trip_room_with_non_png_background_and_sprite(tmp_path):
    src = tmp_path / "src"
    (src / "sprites").mkdir(parents=True)
    (src / "backgrounds").mkdir(parents=True)
    (src / "rooms").mkdir(parents=True)
    (src / "sprites" / "player.bmp").write_bytes(b"BMDATA")
    (src / "backgrounds" / "sky.webp").write_bytes(b"WEBPDATA")
    assets = {
        "objects": {"hero": {"name": "hero", "sprite": "player"}},
        "sprites": {"player": {"name": "player", "file_path": "sprites/player.bmp"}},
        "backgrounds": {"sky": {"name": "sky", "file_path": "backgrounds/sky.webp"}},
        "rooms": {
            "level1": {
                "name": "level1",
                "background_image": "sky",
                "instances": [{"object_name": "hero", "x": 0, "y": 0}],
            }
        },
    }
    _write_project(src, assets)
    out = tmp_path / "level1.gmroom"
    assert ResourcePackager.export_room(src, "level1", out) is True

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert "sprites/player.bmp" in names
    assert "backgrounds/sky.webp" in names

    dst = _write_project(
        tmp_path / "dst",
        {"objects": {}, "sprites": {}, "backgrounds": {}, "rooms": {}},
    )
    room_name = ResourcePackager.import_room(out, dst)
    assert room_name == "level1"
    assert (dst / "sprites" / "player.bmp").exists()
    assert (dst / "backgrounds" / "sky.webp").exists()

    project_data = json.loads((dst / "project.json").read_text(encoding="utf-8"))
    assert "player" in project_data["assets"]["sprites"]
    assert "sky" in project_data["assets"]["backgrounds"]


def test_legacy_png_only_package_still_imports(tmp_path):
    """A package authored by the OLD packager stores sprites/<name>.png and the
    dependency metadata has no file_path. The import must still extract it via
    the legacy fallback."""
    out = tmp_path / "legacy.gmobj"
    package_data = {
        "version": "1.0.0",
        "type": "object",
        "object": {"name": "hero", "sprite": "player"},
        "dependencies": {
            # No file_path on the dependency — legacy data.
            "sprites": {"player": {"name": "player"}},
        },
    }
    with zipfile.ZipFile(out, "w") as zf:
        zf.writestr("package.json", json.dumps(package_data))
        zf.writestr("sprites/player.png", b"PNGDATA")

    dst = _write_project(tmp_path / "dst", {"objects": {}, "sprites": {}})
    name = ResourcePackager.import_object(out, dst)
    assert name == "hero"
    assert (dst / "sprites" / "player.png").exists()
    project_data = json.loads((dst / "project.json").read_text(encoding="utf-8"))
    assert "player" in project_data["assets"]["sprites"]


def test_legacy_png_export_for_asset_without_file_path(tmp_path):
    """Export must fall back to <type>/<name>.png when the asset has no
    file_path (legacy/native projects)."""
    src = tmp_path / "src"
    (src / "sprites").mkdir(parents=True)
    (src / "sprites" / "player.png").write_bytes(b"PNGDATA")
    assets = {
        "objects": {"hero": {"name": "hero", "sprite": "player"}},
        "sprites": {"player": {"name": "player"}},  # no file_path
    }
    _write_project(src, assets)
    out = tmp_path / "hero.gmobj"
    assert ResourcePackager.export_object(src, "hero", out) is True
    with zipfile.ZipFile(out) as zf:
        assert "sprites/player.png" in zf.namelist()


def test_traversal_in_non_png_dependency_is_rejected(tmp_path):
    """The suffix-derivation must not weaken the _safe_join traversal guard.

    OUR _asset_archive_path resolves the dependency's real ``file_path`` (the
    value that carries the non-PNG extension), so that is the path routed
    through _safe_join on extraction. A malicious traversal file_path — even
    with a non-.png suffix — must therefore be blocked: _safe_join raises
    ValueError, import_object swallows it and returns None, and nothing is
    written above the project dir."""
    out = tmp_path / "evil.gmobj"
    evil_path = "../../evil.jpg"
    package_data = {
        "version": "1.0.0",
        "type": "object",
        "object": {"name": "hero", "sprite": "player"},
        "dependencies": {
            # The traversal lives in the file_path our packager actually uses.
            "sprites": {"player": {"name": "player", "file_path": evil_path}},
        },
    }
    with zipfile.ZipFile(out, "w") as zf:
        zf.writestr("package.json", json.dumps(package_data))
        zf.writestr(evil_path, b"PWN")

    dst = _write_project(tmp_path / "dst", {"objects": {}, "sprites": {}})
    # _safe_join raises ValueError on the traversal; import_object swallows it
    # and returns None.
    result = ResourcePackager.import_object(out, dst)
    assert result is None
    # Nothing escaped above the project dir.
    assert not (tmp_path / "evil.jpg").exists()

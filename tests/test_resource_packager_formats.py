"""Regression test for resource_packager non-PNG assets (audit M58).

export/import hardcoded f"{name}.png" for sprite/background files, so a sprite
imported as .jpg/.bmp/etc. was silently dropped from packages (and on import the
recipient got an object referencing a missing sprite). The packager now resolves
the asset's real file_path.
"""

import json
from pathlib import Path

import pytest

from utils.resource_packager import ResourcePackager


def _make_project(root: Path, sprites=None, objects=None):
    root.mkdir(parents=True, exist_ok=True)
    (root / "project.json").write_text(json.dumps({
        "assets": {
            "objects": objects or {},
            "sprites": sprites or {},
            "backgrounds": {},
            "rooms": {},
        }
    }), encoding="utf-8")


def test_object_with_jpg_sprite_round_trips(tmp_path):
    src = tmp_path / "src"
    sprite_meta = {"name": "spr_player", "file_path": "sprites/spr_player.jpg"}
    _make_project(
        src,
        sprites={"spr_player": sprite_meta},
        objects={"obj_player": {"name": "obj_player", "sprite": "spr_player"}},
    )
    (src / "sprites").mkdir()
    (src / "sprites" / "spr_player.jpg").write_bytes(b"\xff\xd8jpeg-bytes")

    pkg = tmp_path / "obj.gmobj"
    assert ResourcePackager.export_object(src, "obj_player", pkg) is True

    dst = tmp_path / "dst"
    _make_project(dst)
    name = ResourcePackager.import_object(pkg, dst)
    assert name == "obj_player"

    # The .jpg must have been packaged and extracted (not silently dropped).
    imported_file = dst / "sprites" / "spr_player.jpg"
    assert imported_file.exists()
    assert imported_file.read_bytes() == b"\xff\xd8jpeg-bytes"

    project = json.loads((dst / "project.json").read_text(encoding="utf-8"))
    assert "spr_player" in project["assets"]["sprites"]


def test_png_fallback_when_no_file_path(tmp_path):
    # Legacy sprite data without file_path still works via the .png fallback.
    src = tmp_path / "src"
    _make_project(
        src,
        sprites={"spr_box": {"name": "spr_box"}},  # no file_path
        objects={"obj_box": {"name": "obj_box", "sprite": "spr_box"}},
    )
    (src / "sprites").mkdir()
    (src / "sprites" / "spr_box.png").write_bytes(b"\x89PNGdata")

    pkg = tmp_path / "box.gmobj"
    assert ResourcePackager.export_object(src, "obj_box", pkg) is True

    dst = tmp_path / "dst"
    _make_project(dst)
    ResourcePackager.import_object(pkg, dst)
    assert (dst / "sprites" / "spr_box.png").exists()

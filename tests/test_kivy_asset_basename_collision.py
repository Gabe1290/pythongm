"""Kivy export: assets sharing a source basename must not clobber (EIO-11).

_export_sprite/_export_background copied each asset to assets/images/<src.name>,
keyed only by the source basename. Two sprites whose source files share a
basename (e.g. imported from different folders, both `tile.png`) overwrote each
other on disk, and their path / frame-metadata map entries collided — one sprite
silently rendered as the other's image. The export now keys the destination on
the project-unique ASSET NAME plus the source extension.
"""
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter, _exported_asset_filename  # noqa: E402


def test_exported_asset_filename_keys_on_name_not_basename():
    # Two different assets, same source basename -> distinct exported names.
    assert _exported_asset_filename("spr_a", "art/a/tile.png") == "spr_a.png"
    assert _exported_asset_filename("spr_b", "art/b/tile.png") == "spr_b.png"
    # Extension is taken from the source file (not hardcoded .png).
    assert _exported_asset_filename("snd_x", "sfx/boom.WAV") == "snd_x.WAV"
    assert _exported_asset_filename("spr_noext", "weird/file") == "spr_noext"


def _project_with_colliding_basenames(src_root: Path):
    """Two sprites + a background whose source files all share basename tile.png,
    each with distinct bytes so a clobber is detectable."""
    for rel, marker in [("a/tile.png", b"AAAA"),
                        ("b/tile.png", b"BBBB"),
                        ("c/tile.png", b"CCCC")]:
        p = src_root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\x89PNG\r\n" + marker)
    return {
        "name": "collide",
        "settings": {"window_width": 320, "window_height": 240},
        "assets": {
            "sprites": {
                "spr_a": {"name": "spr_a", "file_path": "a/tile.png",
                          "width": 16, "height": 16, "frames": 1},
                "spr_b": {"name": "spr_b", "file_path": "b/tile.png",
                          "width": 16, "height": 16, "frames": 1},
            },
            "sounds": {},
            "backgrounds": {
                "bg_c": {"name": "bg_c", "file_path": "c/tile.png",
                         "width": 320, "height": 240},
            },
            "objects": {
                "obj_p": {"name": "obj_p", "sprite": "spr_a", "events": {}},
            },
            "rooms": {
                "rm": {"name": "rm", "width": 320, "height": 240,
                       "background": "bg_c",
                       "instances": [{"object_type": "obj_p", "x": 0, "y": 0}]},
            },
        },
        "room_order": ["rm"],
    }


def test_same_basename_assets_do_not_clobber_on_disk():
    src = Path(tempfile.mkdtemp(prefix="kivy_collide_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_collide_out_")) / "export"
    data = _project_with_colliding_basenames(src)

    assert KivyExporter(data, src, out).export()

    images = out / "game" / "assets" / "images"
    # Each asset copied to its own name-keyed file — no clobber.
    assert (images / "spr_a.png").read_bytes().endswith(b"AAAA")
    assert (images / "spr_b.png").read_bytes().endswith(b"BBBB")
    assert (images / "bg_c.png").read_bytes().endswith(b"CCCC")
    # The old basename-keyed single file must NOT be the only thing present.
    assert not (images / "tile.png").exists()


def test_maps_point_at_distinct_name_keyed_paths():
    src = Path(tempfile.mkdtemp(prefix="kivy_collide_src2_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_collide_out2_")) / "export"
    exp = KivyExporter(_project_with_colliding_basenames(src), src, out)

    assert exp.sprite_path_map["spr_a"] == "assets/images/spr_a.png"
    assert exp.sprite_path_map["spr_b"] == "assets/images/spr_b.png"
    assert exp.background_path_map["bg_c"] == "assets/images/bg_c.png"
    # Distinct meta-map keys (would have been one shared key before).
    assert "assets/images/spr_a.png" in exp.sprite_meta_map
    assert "assets/images/spr_b.png" in exp.sprite_meta_map

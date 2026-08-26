"""HTML5 export never auto-derived a sprite's collision bbox
(bbox_left/top/right/bottom) from its actual opaque pixels — engine.js's
makeSpriteInfo already had the READING side for this (an explicit
author override, all four fields present), but nothing ever WROTE those
fields into the exported gameData, so every sprite's HTML5 collision box
silently fell back to the full frame. Desktop's GameSprite auto-derives
it via a pygame.mask bounding-rect union of frame 0's opaque pixels
(runtime/game_runner.py's _compute_collision_bbox) — a real difference
whenever a sprite has ANY transparent padding.

Found via the promo game's platform level: desktop's penguin sprite
(a 32px-tall frame with 1px of transparent padding top AND bottom)
auto-trims to a 30px collision height and rests flush on the ground;
HTML5's untrimmed 32px box couldn't fit a 32px gap desktop's 30px box
fits comfortably, and rendered the sprite hovering ~1-2px above a flush
landing (the untrimmed box's bottom sits at the true frame edge, below
where the sprite's own opaque pixels actually stop).

Fix: HTML5Exporter._fill_auto_collision_bbox computes the SAME thing via
PIL (the image library this exporter already imports; no pygame
dependency in this file) — frame 0's alpha channel bounding box — and
writes it into the sprite's exported metadata, only when the author
hasn't already set an explicit bbox_* override.
"""
import base64
import gzip
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _make_sprite_png(path, size=(32, 32), opaque_box=(4, 1, 27, 31)):
    """A frame with transparent padding OUTSIDE opaque_box (left, top,
    right, bottom — PIL getbbox convention, right/bottom exclusive)."""
    from PIL import Image
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    left, top, right, bottom = opaque_box
    for x in range(left, right):
        for y in range(top, bottom):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(path)


def _export_and_get_sprite_meta(sprite_png_maker):
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_bbox_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    (proj / "sprites").mkdir(parents=True)
    sprite_png = proj / "sprites" / "spr_test.png"
    sprite_png_maker(sprite_png)

    data = {
        "name": "bbox_html5",
        "settings": {"window_width": 200, "window_height": 200},
        "assets": {
            "sprites": {
                "spr_test": {
                    "name": "spr_test", "frames": 1, "width": 32, "height": 32,
                    "frame_width": 32, "frame_height": 32,
                    "file_path": "sprites/spr_test.png", "origin_x": 0, "origin_y": 0,
                },
            },
            "sounds": {}, "backgrounds": {}, "objects": {},
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200, "instances": []},
            },
        },
        "room_order": ["rm_a"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    import re
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    return embedded["assets"]["sprites"]["spr_test"]


def test_bbox_auto_derived_from_transparent_padding():
    meta = _export_and_get_sprite_meta(
        lambda p: _make_sprite_png(p, opaque_box=(4, 1, 27, 31)))
    assert (meta["bbox_left"], meta["bbox_top"], meta["bbox_right"], meta["bbox_bottom"]) == (4, 1, 27, 31)


def test_fully_opaque_sprite_gets_full_frame_bbox():
    meta = _export_and_get_sprite_meta(
        lambda p: _make_sprite_png(p, opaque_box=(0, 0, 32, 32)))
    assert (meta["bbox_left"], meta["bbox_top"], meta["bbox_right"], meta["bbox_bottom"]) == (0, 0, 32, 32)


def test_explicit_author_override_is_not_overwritten():
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_bbox_override_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    (proj / "sprites").mkdir(parents=True)
    sprite_png = proj / "sprites" / "spr_test.png"
    _make_sprite_png(sprite_png, opaque_box=(4, 1, 27, 31))  # would auto-derive to 4,1,27,31

    data = {
        "name": "bbox_override_html5",
        "settings": {"window_width": 200, "window_height": 200},
        "assets": {
            "sprites": {
                "spr_test": {
                    "name": "spr_test", "frames": 1, "width": 32, "height": 32,
                    "frame_width": 32, "frame_height": 32,
                    "file_path": "sprites/spr_test.png", "origin_x": 0, "origin_y": 0,
                    # explicit override, deliberately different from the real pixels
                    "bbox_left": 0, "bbox_top": 0, "bbox_right": 32, "bbox_bottom": 32,
                },
            },
            "sounds": {}, "backgrounds": {}, "objects": {},
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200, "instances": []},
            },
        },
        "room_order": ["rm_a"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    import re
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    meta = embedded["assets"]["sprites"]["spr_test"]
    assert (meta["bbox_left"], meta["bbox_top"], meta["bbox_right"], meta["bbox_bottom"]) == (0, 0, 32, 32)


def test_matches_desktop_game_sprite_computation_on_a_real_bundled_sample():
    """Cross-engine parity proof: run the exact same PNG through desktop's
    real GameSprite bbox algorithm (pygame.mask) and through the exporter's
    PIL-based one, on a real sprite shipped in this repo's samples, and
    confirm they agree."""
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import glob
    candidates = glob.glob(str(REPO_ROOT / "samples" / "*" / "sprites" / "*.png"))
    if not candidates:
        import pytest
        pytest.skip("no sample sprite PNGs available")
    png_path = Path(candidates[0])

    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameSprite
    desktop_sprite = GameSprite(str(png_path), {"frames": 1})
    desktop_bbox = (desktop_sprite.bbox_left, desktop_sprite.bbox_top,
                     desktop_sprite.bbox_right, desktop_sprite.bbox_bottom)

    from export.HTML5.html5_exporter import HTML5Exporter
    exporter = HTML5Exporter()
    sprite_data = {"frames": 1, "width": desktop_sprite.width, "height": desktop_sprite.height,
                    "frame_width": desktop_sprite.width, "frame_height": desktop_sprite.height,
                    "file_path": png_path.name}
    exporter._fill_auto_collision_bbox(png_path.parent, sprite_data)
    html5_bbox = (sprite_data.get("bbox_left"), sprite_data.get("bbox_top"),
                  sprite_data.get("bbox_right"), sprite_data.get("bbox_bottom"))

    if desktop_bbox == (0, 0, desktop_sprite.width, desktop_sprite.height):
        # Fully opaque sprite -- HTML5's getbbox() may leave the fields
        # unset (None) rather than writing the full frame explicitly;
        # both are equally correct (engine.js's own fallback is the full
        # frame), so only require agreement when there's real padding.
        return
    assert html5_bbox == desktop_bbox


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))

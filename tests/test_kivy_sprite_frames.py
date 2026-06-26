"""Regression tests: the Kivy export must draw a single frame of a multi-frame
sprite strip, not the whole sheet.

User-reported (2026-06-26, screenshot): exported plateforme_3 rendered every
animated object as a horizontal smear of all its frames — penguins, monsters
and bonuses are packed as wide strips (e.g. spr_pingus_ga is a 256x32 PNG of
eight 32x32 frames), but base_object.set_sprite drew the full img.width texture.

The exporter now emits sprite_meta.py (frames / per-frame size / anim speed
keyed by exported path); base_object slices one frame via texture.get_region
and animates it in _advance_animation. The crucial bit is per-frame width: the
sprite's 'width' is the FULL strip width, so it must NOT be used as the frame
width for multi-frame art.
"""

import json
import py_compile
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).parent.parent
SAMPLE = REPO_ROOT / "samples" / "plateforme_3"


def _exporter(project_data, tmp_path):
    from export.Kivy.kivy_exporter import KivyExporter
    return KivyExporter(project_data, tmp_path, tmp_path / "out")


def test_multiframe_uses_per_frame_width_not_strip_width(tmp_path):
    data = {"assets": {"sprites": {
        "spr_walk": {"file_path": "sprites/spr_walk.png",
                     "frames": 8, "frame_width": 32, "frame_height": 32,
                     "width": 256, "height": 32, "speed": 10.0},
    }}}
    meta = _exporter(data, tmp_path).sprite_meta_map["assets/images/spr_walk.png"]
    assert meta["frames"] == 8
    assert meta["frame_width"] == 32   # per-frame, NOT the 256 strip width
    assert meta["frame_height"] == 32
    assert meta["speed"] == 10.0


def test_single_frame_falls_back_to_width(tmp_path):
    data = {"assets": {"sprites": {
        "spr_block": {"file_path": "sprites/spr_block.png",
                      "frames": 1, "width": 32, "height": 32},
    }}}
    meta = _exporter(data, tmp_path).sprite_meta_map["assets/images/spr_block.png"]
    assert meta["frames"] == 1
    assert meta["frame_width"] == 32
    assert meta["frame_height"] == 32


@pytest.mark.skipif(not (SAMPLE / "project.json").exists(),
                    reason="bundled sample not present")
def test_export_emits_sprite_meta_and_base_slices(tmp_path):
    from export.Kivy.kivy_exporter import KivyExporter

    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    out = tmp_path / "export"
    assert KivyExporter(data, SAMPLE, out).export() is True

    meta_py = out / "game" / "sprite_meta.py"
    assert meta_py.exists()
    py_compile.compile(str(meta_py), doraise=True)
    ns = {}
    exec(meta_py.read_text(encoding="utf-8"), ns)
    meta = ns["SPRITE_META"]
    # The known 8-frame penguin strip is recorded with per-frame width 32.
    pingus = meta.get("assets/images/spr_pingus_ga.png")
    assert pingus and pingus["frames"] == 8 and pingus["frame_width"] == 32

    base = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "from sprite_meta import SPRITE_META" in base
    assert "get_region(" in base            # slices one frame
    assert "_advance_animation" in base      # animates it
    py_compile.compile(str(out / "game" / "objects" / "base_object.py"), doraise=True)

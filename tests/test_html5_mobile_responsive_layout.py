"""Reported: HTML5-exported games are unusable on a phone browser -- the
page is fixed-width (a hardcoded `{width}px` on both the canvas and the
HUD bar) and overflows the viewport instead of scaling down, so the title
and HUD get clipped and the player has to pan/zoom to see the game.

Root cause was purely CSS (the input-handling code already converts
clientX/Y through canvas.clientWidth/clientHeight vs canvas.width/height,
so it already tolerates a CSS-scaled canvas -- see setupMouse() in
engine.js): #gameCanvas and #hudBar were pinned to the room's native
pixel size with no responsive scaling, and nothing capped #gameContainer
to the viewport width.

Fix: #gameWrapper caps at the room's native {width}px (so desktop still
renders at exact 1:1 pixel scale, no blur) but never exceeds 100% of its
parent; #gameCanvas and #hudBar both fill #gameWrapper at width:100%, so
they track the same width and shrink together on a narrow viewport.
aspect-ratio keeps the canvas's proportions correct as it scales.
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.HTML5.html5_exporter import HTML5Exporter  # noqa: E402

TEMPLATE = (REPO_ROOT / "export" / "HTML5" / "templates" / "game_template.html").read_text(encoding="utf-8")


def _copy_sample(name="maze_1"):
    src = REPO_ROOT / "samples" / name
    tmp = Path(tempfile.mkdtemp(prefix="mobile_layout_export_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    out = tmp / "out"
    out.mkdir()
    return proj, out


# ---------------------------------------------------------------------------
# Template source-level assertions (the enforced regression guard)
# ---------------------------------------------------------------------------

def test_viewport_meta_tag_present():
    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in TEMPLATE


def test_canvas_scales_with_the_viewport_not_pinned_to_native_pixels():
    m = re.search(r"#gameCanvas\s*\{(.*?)\n        \}", TEMPLATE, re.S)
    assert m
    body = m.group(1)
    assert "width: 100%;" in body
    assert "height: auto;" in body
    assert "aspect-ratio: {width} / {height};" in body
    # image-rendering must survive -- pixel art must stay crisp when scaled.
    assert "image-rendering: pixelated;" in body


def test_hud_bar_tracks_canvas_width_instead_of_a_hardcoded_pixel_value():
    m = re.search(r"#hudBar\s*\{(.*?)\}", TEMPLATE, re.S)
    assert m
    body = m.group(1)
    assert "width: 100%;" in body
    assert "{width}px" not in body


def test_game_wrapper_caps_at_native_size_but_never_exceeds_the_viewport():
    m = re.search(r"#gameWrapper\s*\{(.*?)\n        \}", TEMPLATE, re.S)
    assert m
    body = m.group(1)
    assert "width: 100%;" in body
    assert "max-width: {width}px;" in body


def test_body_and_container_guard_against_horizontal_overflow():
    body_m = re.search(r"\n        body \{(.*?)\}", TEMPLATE, re.S)
    assert body_m
    assert "overflow-x: hidden;" in body_m.group(1)

    container_m = re.search(r"#gameContainer\s*\{(.*?)\}", TEMPLATE, re.S)
    assert container_m
    assert "max-width: 100vw;" in container_m.group(1)


def test_mobile_media_query_present():
    assert "@media (max-width: 480px)" in TEMPLATE


def test_title_does_not_force_horizontal_overflow_on_a_long_game_name():
    m = re.search(r"\.title\s*\{(.*?)\}", TEMPLATE, re.S)
    assert m
    body = m.group(1)
    assert "word-break: break-word;" in body
    assert "max-width: 100%;" in body


# ---------------------------------------------------------------------------
# End-to-end: a real export resolves every placeholder and produces valid,
# self-consistent CSS (the aspect-ratio matches the room's real dimensions).
# ---------------------------------------------------------------------------

def test_real_export_has_no_leftover_placeholders_and_correct_aspect_ratio():
    proj, out = _copy_sample("maze_1")
    assert HTML5Exporter().export(proj, out)
    html = next(out.glob("*.html")).read_text(encoding="utf-8")

    assert "{width}" not in html
    assert "{height}" not in html

    canvas_m = re.search(r'<canvas id="gameCanvas" width="(\d+)" height="(\d+)">', html)
    assert canvas_m
    width, height = canvas_m.group(1), canvas_m.group(2)

    assert f"aspect-ratio: {width} / {height};" in html
    assert f"max-width: {width}px;" in html


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))

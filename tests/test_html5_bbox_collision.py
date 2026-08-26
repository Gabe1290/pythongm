"""HTML5 export — collision geometry now honors sprite bbox_left/top/
right/bottom, matching the desktop runtime.

Bug report: the raycast samples' player sprite (spr_person) defines an 8x8
collision box centered in its 16x16 frame (bbox_left=4, bbox_top=4,
bbox_right=12, bbox_bottom=12) — runtime/game_runner.py's
check_movement_collision_with_blocker uses exactly this narrower box for
collision, but engine.js's boxWidth()/boxHeight()/getBoundingBox() used only
the full spriteInfo.width/height, ignoring bbox_* entirely. The player's
effective collision footprint on HTML5 was therefore twice desktop's for
this sprite (16x16 vs 8x8), giving it far less clearance near walls and
making it much more likely to start a level (or otherwise land) already
overlapping a wall's collision box. _movementBlocker's "already overlapping
at the current position — let it escape" rule (an intentional anti-freeze
safety valve, shared identically with desktop) then stays disengaged for
that pair until the two stop overlapping — which, with the player now
inside solid geometry, meant walking straight through the wall and getting
stuck outside the maze with no way back in. Reported as an HTML5-only
symptom, consistent with desktop already using the narrower box correctly.

Fix: Game.makeSpriteInfo now carries bbox_left/top/right/bottom (falling
back to the full frame when a sprite has no explicit override — the same
default runtime/game_runner.py's Sprite class uses), and every collision
call site (getBoundingBox, _movementBlocker, placeMeetsCollision,
checkCollisionAt, getObjectAt) uses a new bboxLeft()/bboxTop()/
collisionWidth()/collisionHeight() quartet instead of the raw frame box.
boxWidth()/boxHeight() themselves are UNCHANGED (still the full frame) —
they're also used for RENDERING (frame-slicing a sprite strip, billboard
sizing in the raycast renderer), which must stay full-size regardless of
any collision-box override.

Verification tier, per this repo's "no Node in CI" convention (matching
test_html5_solid_movement_blocking.py / test_html5_room_actions.py):
source-level assertions on engine.js here. The actual behavioral proof —
real headless Chromium (Playwright, not a CI dependency) loading a real
raycast_1 HTML5 export and calling the live GameObject's getBoundingBox()/
_movementBlocker() — confirmed: pre-fix, the spawned player's
getBoundingBox() was {x:40,y:424,width:16,height:16}; post-fix it's
{x:44,y:428,width:8,height:8}, byte-for-byte matching desktop's
check_movement_collision_with_blocker math for the same sprite/position.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _method_body(name):
    m = re.search(r"    " + re.escape(name) + r"\([^)]*\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, f"{name} not found"
    return m.group(1)


def test_make_sprite_info_carries_bbox_fields():
    body = _method_body("makeSpriteInfo")
    assert "bbox_left" in body and "bbox_top" in body
    assert "bbox_right" in body and "bbox_bottom" in body
    # All four required together, else falls back to the full frame —
    # matches runtime/game_runner.py's Sprite._resolve_bbox precedent.
    assert "hasBbox" in body
    assert "hasBbox ? parseInt(meta.bbox_right) : fw" in body
    assert "hasBbox ? parseInt(meta.bbox_bottom) : fh" in body


def test_box_width_height_still_return_the_full_frame():
    """boxWidth/boxHeight are also used for RENDERING (frame slicing,
    billboard sizing) — they must NOT shrink to the collision box."""
    w_body = _method_body("boxWidth")
    h_body = _method_body("boxHeight")
    assert "this.spriteInfo.width" in w_body
    assert "this.spriteInfo.height" in h_body
    assert "bbox" not in w_body
    assert "bbox" not in h_body


def test_collision_box_helpers_exist_and_default_to_full_frame():
    left_body = _method_body("bboxLeft")
    top_body = _method_body("bboxTop")
    cw_body = _method_body("collisionWidth")
    ch_body = _method_body("collisionHeight")
    assert "this.spriteInfo.bbox_left || 0" in left_body
    assert "this.spriteInfo.bbox_top || 0" in top_body
    assert "this.spriteInfo.bbox_right - this.bboxLeft()" in cw_body
    assert "return this.boxWidth();" in cw_body  # fallback when unset
    assert "this.spriteInfo.bbox_bottom - this.bboxTop()" in ch_body
    assert "return this.boxHeight();" in ch_body


def test_get_bounding_box_uses_collision_box_not_frame_box():
    body = _method_body("getBoundingBox")
    assert "this.collisionWidth()" in body
    assert "this.collisionHeight()" in body
    assert "this.bboxLeft()" in body
    assert "this.bboxTop()" in body
    assert "this.boxWidth()" not in body
    assert "this.boxHeight()" not in body


def test_movement_blocker_test_rect_uses_collision_box():
    body = _method_body("_movementBlocker")
    assert "this.collisionWidth()" in body
    assert "this.collisionHeight()" in body
    assert "this.bboxLeft()" in body
    assert "this.bboxTop()" in body


def test_place_meets_collision_uses_collision_box():
    body = _method_body("placeMeetsCollision")
    assert "this.collisionWidth()" in body
    assert "this.collisionHeight()" in body
    assert "this.bboxLeft()" in body
    assert "this.bboxTop()" in body


def test_check_collision_at_and_get_object_at_use_collision_box():
    for name in ("checkCollisionAt", "getObjectAt"):
        body = _method_body(name)
        assert "this.collisionWidth()" in body, name
        assert "this.collisionHeight()" in body, name
        assert "this.bboxLeft()" in body, name
        assert "this.bboxTop()" in body, name


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))

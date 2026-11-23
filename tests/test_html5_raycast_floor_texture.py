"""set_floor_texture in the HTML5 export: ground-level floor patches (2026-11-23).

Browser tests run in headless Chromium where Playwright is installed (the dev box; skipped in
CI): an exported room with a patch row ahead of the camera is rendered, in a flat room and in a
room with a step (the column walk), and the floor rows are read back. Structural checks run
everywhere.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_html5_raycast_stairs import _page, needs_browser, JS  # noqa: E402
from test_html5_raycast_ceilings import _column  # noqa: E402

PATCH = (255, 0, 255)
FLOOR = (0, 128, 0)
FLAT = (0, 255, 0)


def test_the_port_registers_the_floor_texture_pieces():
    assert "registerExtensionAction('set_floor_texture'" in JS
    for name in ("function raycastIsFloorPatch(", "buildFloorTextures(cellSize) {",
                 "castFloorCells(ctx, texData, cellTex, flat,",
                 "castStairsFloor(ctx, layouts, sf, floorTex, topTex, facingScreenRad, fovRad, res, groundTex) {"):
        assert name in JS, name
    # A patch is geometry: never a billboard, never a mover.
    body = JS[JS.index("function raycastIsGeometry("):]
    assert "raycastIsFloorPatch(inst)" in body[:body.index("}")]


def _project(tmp_path, floor_texture="spr_floor", step=False):
    import pygame
    proj = tmp_path / "proj"
    (proj / "sprites").mkdir(parents=True)

    def sprite(name, color):
        surf = pygame.Surface((32, 32))
        surf.fill(color)
        pygame.image.save(surf, str(proj / "sprites" / f"{name}.png"))
        return {"name": name, "asset_type": "sprite", "file_path": f"sprites/{name}.png",
                "width": 32, "height": 32, "origin_x": 0, "origin_y": 0, "frames": 1,
                "frame_width": 32, "frame_height": 32, "animation_type": "single", "speed": 10.0}

    sprites = {"spr_block": sprite("spr_block", (128, 128, 128)),
               "spr_rug": sprite("spr_rug", PATCH), "spr_floor": sprite("spr_floor", FLOOR)}

    def obj(name, solid, events, spr="spr_block"):
        return {"name": name, "asset_type": "object", "sprite": spr, "visible": True,
                "solid": solid, "persistent": False, "depth": 0, "events": events}

    cam = {"camera_object": "", "fov": "66", "cell_size": "32", "render_distance": "20",
           "wall_color": "#ff0000", "floor_color": "#00ff00", "ceiling_color": "#0000ff",
           "wall_textured": "false", "floor_texture": floor_texture}
    objects = {
        "obj_wall": obj("obj_wall", True, {}),
        "obj_rug": obj("obj_rug", False, {"create": {"actions": [
            {"action": "set_floor_texture", "parameters": {"texture": "spr_rug"}}]}}, "spr_rug"),
        "obj_step": obj("obj_step", False, {"create": {"actions": [
            {"action": "set_floor_height", "parameters": {"height": "8"}}]}}),
        "obj_person": obj("obj_person", False, {"create": {"actions": [
            {"action": "enable_raycast_view", "parameters": cam}]}}),
    }
    instances = []
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            instances.append({"object_name": "obj_wall", "x": x * 32, "y": y * 32})
    for x in range(4, 9):
        instances.append({"object_name": "obj_rug", "x": x * 32, "y": 7 * 32})
    if step:
        instances.append({"object_name": "obj_step", "x": 2 * 32, "y": 2 * 32})
    instances.append({"object_name": "obj_person", "x": 64, "y": 224})
    project = {
        "name": "floor_patch_e2e", "version": "1.0",
        "settings": {"window_width": 480, "window_height": 480, "room_speed": 30},
        "assets": {"sprites": sprites, "sounds": {}, "backgrounds": {}, "objects": objects,
                   "scripts": {}, "fonts": {}, "data": {},
                   "rooms": {"room0": {"name": "room0", "asset_type": "room", "width": 480,
                                       "height": 480, "background_color": "#000000",
                                       "instances": instances, "tiles": []}}},
    }
    (proj / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return proj


# The camera's rays start at (80, 240), cell (2, 7), facing east. The centre column's floor
# row y looks (360 / (y - 240)) cells ahead: y=330 -> 4 cells (x = 6.5, on the patch row
# x=4..8), y=280 -> 9 cells (x = 11.5, past it).
ON, PAST = 330, 280


@needs_browser
def test_a_patch_replaces_the_floor_texture(tmp_path):
    with _page(_project(tmp_path), tmp_path) as pg:
        col = _column(pg)
    assert col[ON] == PATCH and col[PAST] == FLOOR
    assert PATCH not in col[:240]                       # not drawn as a billboard


@needs_browser
def test_a_patch_without_a_floor_texture(tmp_path):
    with _page(_project(tmp_path, floor_texture=""), tmp_path) as pg:
        col = _column(pg)
    assert col[ON] == PATCH and col[PAST] == FLAT


@needs_browser
def test_a_patch_in_a_room_with_steps(tmp_path):
    with _page(_project(tmp_path, step=True), tmp_path) as pg:
        col = _column(pg)
    assert col[ON] == PATCH and col[PAST] == FLOOR

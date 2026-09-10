#!/usr/bin/env python3
"""Per-tutorial-step screenshots for the wiki's build-along tutorials
(docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md).

Drives a real, offscreen PyGameMakerIDE through a scratch project built to
match a tutorial's own text exactly (object/sprite/event/action names,
room layout), taking one screenshot at each of the tutorial's own "## Step
N" boundaries. Reuses Phase 1's proven headless-capture technique
(QT_QPA_PLATFORM=offscreen + QWidget.grab()) and its privacy fix (blank
Config.recent_projects + a no-op add_recent_project, so the capturing
machine's own project history never leaks into a screenshot) -- see the
plan doc's own "Reusable infrastructure from Phase 1" section.

Each step's project-data mutations are applied directly through the same
AssetManager API the real UI menu actions call (create_asset/import_asset),
rather than synthesizing raw QMouseEvents for every click -- the screenshot
needs to show what the IDE looks like AFTER a step, which only depends on
the resulting project data and which editor is on screen, not on the exact
click sequence that produced it. This was the plan's own flagged open
question ("how mechanically painful is scripting the Room Editor
specifically") and the answer this script gives: placing an instance is
just an entry in the room's instances list, no different in difficulty
from creating an object.

Usage:
    QT_QPA_PLATFORM=offscreen python3 tools/capture_tutorial_screenshots.py breakout

Writes wiki/images/tutorial-breakout-NN-<slug>.png (one per "## Step N"
heading reached) and does NOT touch the wiki markdown itself -- embedding
the images into the tutorial text is a separate, reviewable edit.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

IMAGES_DIR = REPO_ROOT / "wiki" / "images"
WINDOW_SIZE = (1440, 900)


def _make_app():
    from PySide6.QtWidgets import QApplication
    from utils.config import Config

    # Phase 1's privacy fix -- must run BEFORE the IDE window is
    # constructed, or the Welcome tab's "Continue where you left off"
    # panel renders this machine's own real recent-project history into
    # every screenshot.
    Config.set("recent_projects", [])
    Config.add_recent_project = staticmethod(lambda *a, **k: None)

    return QApplication.instance() or QApplication([])


def _make_ide(app):
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    ide.resize(*WINDOW_SIZE)
    ide.show()
    app.processEvents()
    return ide


def _new_scratch_project(ide, name):
    """A brand-new project in a throwaway temp directory -- never the
    bundled samples/ path directly (it triggers the real
    promotion-copy-into-Documents flow, the plan doc's other Phase-1
    landmine)."""
    scratch = Path(tempfile.mkdtemp(prefix="pygm_wiki_shots_"))
    ok = ide.project_manager.create_project(name, str(scratch), "empty", "")
    if not ok:
        raise RuntimeError(f"could not create scratch project {name!r} in {scratch}")
    project_path = ide.project_manager.current_project_path
    project_data = ide.project_manager.current_project_data
    ide.on_project_loaded(project_path, project_data)
    return scratch


def _sync(ide):
    """Mirror AssetManager.assets_cache (what create_asset/import_asset
    actually mutate) into project_manager.current_project_data and
    refresh the visible asset tree from it -- the same sync
    ProjectManager.save_project() already relies on right before writing
    to disk, reused here so a screenshot's asset tree reflects the
    mutation that was just made."""
    ide.asset_manager.save_assets_to_project_data(ide.project_manager.current_project_data)
    ide.asset_tree.refresh_from_project(ide.project_manager.current_project_data)


def _capture(ide, app, filename):
    app.processEvents()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    dest = IMAGES_DIR / filename
    pix = ide.grab()
    if not pix.save(str(dest)):
        raise RuntimeError(f"failed to save screenshot to {dest}")
    print(f"  wrote {dest.relative_to(REPO_ROOT)} ({pix.width()}x{pix.height()})")


def _sprite_png(path, size, shape, color):
    """A simple placeholder sprite image matching what the tutorial asks
    the reader to draw -- a filled rectangle or circle of the given size
    and color, transparent background. Real pixel art isn't the point of
    a step screenshot; showing the right shape/size/origin is."""
    from PIL import Image, ImageDraw
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if shape == "rect":
        draw.rectangle([0, 0, w - 1, h - 1], fill=color)
    elif shape == "circle":
        draw.ellipse([0, 0, w - 1, h - 1], fill=color)
    img.save(path)


# ---------------------------------------------------------------------------
# Breakout (wiki/Tutorial-Breakout.md) -- the proof of concept: shortest of
# the six tutorials (225 lines), picked per the plan's own suggested
# Phase 1 ("read all six's current step counts first -- don't guess").
# ---------------------------------------------------------------------------

def capture_breakout():
    app = _make_app()
    ide = _make_ide(app)
    scratch = _new_scratch_project(ide, "scratch_breakout")
    am = ide.asset_manager
    sprite_dir = scratch / "_capture_sprites"
    sprite_dir.mkdir(exist_ok=True)

    try:
        # -- Step 1: Create the Sprites -----------------------------------
        # Sizes/shapes/colors straight from the tutorial's own text
        # (1.1-1.4); origin defaults to center on import already (see
        # AssetManager._create_asset_data), matching "Click Center" for
        # free.
        sprites = [
            ("spr_paddle", (64, 16), "rect", (90, 170, 250, 255)),
            ("spr_ball", (16, 16), "circle", (240, 200, 80, 255)),
            ("spr_brick", (48, 24), "rect", (200, 90, 90, 255)),
            ("spr_wall", (32, 32), "rect", (120, 120, 130, 255)),
        ]
        for name, size, shape, color in sprites:
            png_path = sprite_dir / f"{name}.png"
            _sprite_png(png_path, size, shape, color)
            asset_data = am.import_asset(png_path, "sprites", name)
            if asset_data is None:
                raise RuntimeError(f"failed to import sprite {name!r}")
        _sync(ide)
        ide.open_sprite_editor("spr_ball", am.get_asset("sprites", "spr_ball"))
        _capture(ide, app, "tutorial-breakout-01-sprites.png")

        # -- Step 2: Create the Paddle Object -------------------------------
        paddle_events = {
            "keyboard": {
                "right": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "5"}},
                ]},
                "left": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "-5"}},
                ]},
            },
            "keyboard_release": {
                "right": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "0"}},
                ]},
                "left": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "0"}},
                ]},
            },
        }
        am.create_asset("obj_paddle", "objects", sprite="spr_paddle",
                        solid=True, visible=True, events=paddle_events)
        _sync(ide)
        ide.open_object_editor("obj_paddle", am.get_asset("objects", "obj_paddle"))
        _capture(ide, app, "tutorial-breakout-02-paddle-object.png")

        # -- Step 3: Create the Ball Object ---------------------------------
        ball_events = {
            "create": {"actions": [
                {"action": "set_hspeed", "parameters": {"speed": "4"}},
                {"action": "set_vspeed", "parameters": {"speed": "-4"}},
            ]},
            "collision_with_obj_paddle": {"actions": [
                {"action": "reverse_vertical", "parameters": {}},
            ]},
            "collision_with_obj_wall": {"actions": [
                {"action": "reverse_horizontal", "parameters": {}},
                {"action": "reverse_vertical", "parameters": {}},
            ]},
        }
        am.create_asset("obj_ball", "objects", sprite="spr_ball",
                        solid=True, visible=True, events=ball_events)
        _sync(ide)
        ide.open_object_editor("obj_ball", am.get_asset("objects", "obj_ball"))
        _capture(ide, app, "tutorial-breakout-03-ball-object.png")

        # -- Step 4: Create the Brick Object --------------------------------
        brick_events = {
            "collision_with_obj_ball": {"actions": [
                {"action": "destroy_instance",
                 "parameters": {"target": "self"}},
            ]},
        }
        am.create_asset("obj_brick", "objects", sprite="spr_brick",
                        solid=True, visible=True, events=brick_events)
        # 4.3: the bounce action goes on obj_ball, not obj_brick (Reverse
        # Vertical always applies to the instance whose event it's in --
        # see the tutorial's own note).
        ball_asset = am.get_asset("objects", "obj_ball")
        ball_asset["events"]["collision_with_obj_brick"] = {"actions": [
            {"action": "reverse_vertical", "parameters": {}},
        ]}
        _sync(ide)
        ide.open_object_editor("obj_brick", am.get_asset("objects", "obj_brick"))
        _capture(ide, app, "tutorial-breakout-04-brick-object.png")

        # -- Step 5: Create the Wall Object ---------------------------------
        am.create_asset("obj_wall", "objects", sprite="spr_wall",
                        solid=True, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_wall", am.get_asset("objects", "obj_wall"))
        _capture(ide, app, "tutorial-breakout-05-wall-object.png")

        # -- Step 6: Create the Game Room ------------------------------------
        CELL = 32
        COLS, ROWS = 12, 9
        room_w, room_h = COLS * CELL, ROWS * CELL   # 384 x 288

        def cell_center(col, row):
            return col * CELL + CELL // 2, row * CELL + CELL // 2

        instances = []

        def place(obj, col, row):
            x, y = cell_center(col, row)
            instances.append({
                "object_name": obj, "x": x, "y": y, "rotation": 0,
                "scale_x": 1.0, "scale_y": 1.0, "visible": True,
            })

        # Walls: top row, left column, right column -- bottom open, per
        # the tutorial's own 6.3 instructions.
        for col in range(COLS):
            place("obj_wall", col, 0)
        for row in range(1, ROWS):
            place("obj_wall", 0, row)
            place("obj_wall", COLS - 1, row)

        # Paddle: bottom center.
        place("obj_paddle", COLS // 2, ROWS - 2)

        # Ball: the open gap between the brick rows (2-4) and the paddle
        # (ROWS-2) -- NOT COLS//2, ROWS//2 (a first version put it dead
        # center, which landed inside the brick rows below and rendered
        # invisible, the brick instance drawn on top of it at the same
        # cell; found by actually looking at the captured screenshot, not
        # assumed correct from the coordinates alone).
        place("obj_ball", COLS // 2, ROWS - 4)

        # Bricks: 3 rows near the top, inside the side walls.
        for brick_row in range(2, 5):
            for col in range(2, COLS - 2):
                place("obj_brick", col, brick_row)

        room_data = am.create_asset(
            "room_game", "rooms",
            width=room_w, height=room_h, background_color="#101018",
            instances=instances)
        _sync(ide)
        ide.open_room_editor("room_game", room_data)
        _capture(ide, app, "tutorial-breakout-06-room.png")

        print("Breakout capture complete.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


SCENARIOS = {
    "breakout": capture_breakout,
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
        print(f"Usage: {sys.argv[0]} <{'|'.join(SCENARIOS)}>")
        return 1
    SCENARIOS[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())

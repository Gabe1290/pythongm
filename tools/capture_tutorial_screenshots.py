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
# Wide enough that the room editor's scroll viewport (roughly window_width
# minus ~970px of side panels) fully contains a 640x480-ish tutorial room --
# a narrower window clips the room's right edge out of a full-window grab.
WINDOW_SIZE = (1680, 980)


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


def _fit_window_to_room(ide, app, room_name):
    """Grow the IDE window until the room editor's scroll viewport fully
    contains the room canvas, so a full-window grab doesn't clip a wide
    room's right/bottom edge. A no-op for rooms that already fit at the
    default WINDOW_SIZE (so the smaller tutorials' shots stay unchanged)."""
    from PySide6.QtWidgets import QScrollArea
    key = ide._editor_key("rooms", room_name)
    editor = ide.open_editors.get(key)
    if editor is None or not hasattr(editor, "room_canvas"):
        return
    canvas = editor.room_canvas
    sa = canvas.parentWidget()
    while sa is not None and not isinstance(sa, QScrollArea):
        sa = sa.parentWidget()
    if sa is None:
        return
    for _ in range(6):
        app.processEvents()
        vw, vh = sa.viewport().width(), sa.viewport().height()
        cw, ch = canvas.width(), canvas.height()
        grow_w = max(0, cw + 8 - vw)
        grow_h = max(0, ch + 8 - vh)
        if grow_w <= 0 and grow_h <= 0:
            return
        ide.resize(ide.width() + grow_w, ide.height() + grow_h)
        ide.show()
    app.processEvents()


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
            # A warm tan rather than a neutral grey: a grey wall row reads as
            # window chrome against the IDE's own grey panels in a full-window
            # screenshot (found by inspecting the Phase 1 room capture).
            ("spr_wall", (32, 32), "rect", (150, 110, 70, 255)),
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


# ---------------------------------------------------------------------------
# Pong (wiki/Tutorial-Pong.md) -- Phase 2, tutorial 1 of the remaining five.
# ---------------------------------------------------------------------------

def capture_pong():
    app = _make_app()
    ide = _make_ide(app)
    scratch = _new_scratch_project(ide, "scratch_pong")
    am = ide.asset_manager
    sprite_dir = scratch / "_capture_sprites"
    sprite_dir.mkdir(exist_ok=True)

    try:
        # -- Step 2: Create the Sprites -------------------------------------
        # Sizes/shapes/colors straight from the tutorial's own text (2.1-2.4).
        sprites = [
            ("spr_ball", (16, 16), "circle", (240, 240, 240, 255)),
            ("spr_paddle_left", (16, 64), "rect", (90, 140, 240, 255)),
            ("spr_paddle_right", (16, 64), "rect", (220, 90, 90, 255)),
            # Warm tan, not neutral grey -- a grey wall blends into the IDE's
            # own grey chrome in a full-window screenshot.
            ("spr_wall", (32, 32), "rect", (150, 110, 70, 255)),
            # The goal is invisible in-game (the tutorial says so); a
            # translucent green here just makes the placement legible in the
            # Room Editor screenshot.
            ("spr_goal", (32, 32), "rect", (80, 180, 140, 110)),
        ]
        for name, size, shape, color in sprites:
            png_path = sprite_dir / f"{name}.png"
            _sprite_png(png_path, size, shape, color)
            asset_data = am.import_asset(png_path, "sprites", name)
            if asset_data is None:
                raise RuntimeError(f"failed to import sprite {name!r}")
        _sync(ide)
        ide.open_sprite_editor("spr_ball", am.get_asset("sprites", "spr_ball"))
        _capture(ide, app, "tutorial-pong-02-sprites.png")

        # -- Step 3: Create the Wall Object ----------------------------------
        am.create_asset("obj_wall", "objects", sprite="spr_wall",
                        solid=True, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_wall", am.get_asset("objects", "obj_wall"))
        _capture(ide, app, "tutorial-pong-03-wall-object.png")

        # -- Step 4: Create the Paddle Objects --------------------------------
        def paddle_events(up_key, down_key):
            return {
                "keyboard": {
                    up_key: {"actions": [
                        {"action": "set_vspeed", "parameters": {"speed": "-8"}},
                    ]},
                    down_key: {"actions": [
                        {"action": "set_vspeed", "parameters": {"speed": "8"}},
                    ]},
                },
                "keyboard_release": {
                    up_key: {"actions": [
                        {"action": "set_vspeed", "parameters": {"speed": "0"}},
                    ]},
                    down_key: {"actions": [
                        {"action": "set_vspeed", "parameters": {"speed": "0"}},
                    ]},
                },
                "collision_with_obj_wall": {"actions": [
                    {"action": "bounce", "parameters": {}},
                ]},
            }

        # 4.1 Left Paddle (Player 1): W / S.
        am.create_asset("obj_paddle_left", "objects", sprite="spr_paddle_left",
                        solid=True, visible=True,
                        events=paddle_events("w", "s"))
        # 4.2 Right Paddle (Player 2): Up / Down arrows.
        am.create_asset("obj_paddle_right", "objects", sprite="spr_paddle_right",
                        solid=True, visible=True,
                        events=paddle_events("up", "down"))
        _sync(ide)
        ide.open_object_editor("obj_paddle_left", am.get_asset("objects", "obj_paddle_left"))
        _capture(ide, app, "tutorial-pong-04-paddle-objects.png")

        # -- Step 5: Create the Ball Object -----------------------------------
        ball_events = {
            "create": {"actions": [
                {"action": "start_moving_direction", "parameters": {
                    "directions": ["down-right"], "direction_expr": "", "speed": 6.0,
                }},
            ]},
            "collision_with_obj_paddle_left": {"actions": [
                {"action": "bounce", "parameters": {}},
            ]},
            "collision_with_obj_paddle_right": {"actions": [
                {"action": "bounce", "parameters": {}},
            ]},
            "collision_with_obj_wall": {"actions": [
                {"action": "bounce", "parameters": {}},
            ]},
        }
        am.create_asset("obj_ball", "objects", sprite="spr_ball",
                        solid=False, visible=True, events=ball_events)
        _sync(ide)
        ide.open_object_editor("obj_ball", am.get_asset("objects", "obj_ball"))
        _capture(ide, app, "tutorial-pong-05-ball-object.png")

        # -- Step 6: Create the Goal Objects ------------------------------------
        am.create_asset("obj_goal_left", "objects", sprite="spr_goal",
                        solid=True, visible=False, events={})
        am.create_asset("obj_goal_right", "objects", sprite="spr_goal",
                        solid=True, visible=False, events={})
        # 6.3: the goal-collision events go on obj_ball -- p2 scores when the
        # ball reaches the LEFT goal, p1 scores on the RIGHT goal.
        ball_asset = am.get_asset("objects", "obj_ball")
        ball_asset["events"]["collision_with_obj_goal_left"] = {"actions": [
            {"action": "jump_to_start", "parameters": {}},
            {"action": "set_variable", "parameters": {
                "variable": "p2score", "value": "1", "scope": "global", "relative": True,
            }},
        ]}
        ball_asset["events"]["collision_with_obj_goal_right"] = {"actions": [
            {"action": "jump_to_start", "parameters": {}},
            {"action": "set_variable", "parameters": {
                "variable": "p1score", "value": "1", "scope": "global", "relative": True,
            }},
        ]}
        _sync(ide)
        # The goal objects themselves have no events -- what this step is
        # really teaching is the scoring logic just added to obj_ball above,
        # so that's what's worth showing here (matching the step's own
        # emphasis, not just the two newly-created empty objects).
        ide.open_object_editor("obj_ball", am.get_asset("objects", "obj_ball"))
        _capture(ide, app, "tutorial-pong-06-goal-objects.png")

        # -- Step 7: Create the Score Display Object ------------------------------
        score_events = {
            "create": {"actions": [
                {"action": "set_variable", "parameters": {
                    "variable": "p1score", "value": "0", "scope": "global", "relative": False,
                }},
                {"action": "set_variable", "parameters": {
                    "variable": "p2score", "value": "0", "scope": "global", "relative": False,
                }},
            ]},
            "draw": {"actions": [
                {"action": "draw_text", "parameters": {
                    "text": "\"Player 1:\"", "x": "10", "y": "10",
                }},
                {"action": "draw_variable", "parameters": {
                    "variable": "global.p1score", "x": "100", "y": "10",
                }},
                {"action": "draw_text", "parameters": {
                    "text": "\"Player 2:\"", "x": "10", "y": "30",
                }},
                {"action": "draw_variable", "parameters": {
                    "variable": "global.p2score", "x": "100", "y": "30",
                }},
            ]},
        }
        am.create_asset("obj_score", "objects", sprite=None,
                        solid=False, visible=True, events=score_events)
        _sync(ide)
        ide.open_object_editor("obj_score", am.get_asset("objects", "obj_score"))
        _capture(ide, app, "tutorial-pong-07-score-object.png")

        # -- Step 8: Design the Room ----------------------------------------------
        CELL = 32
        COLS, ROWS = 20, 15
        room_w, room_h = COLS * CELL, ROWS * CELL   # 640 x 480, per 8.2

        def cell_center(col, row):
            return col * CELL + CELL // 2, row * CELL + CELL // 2

        instances = []

        def place(obj, col, row):
            x, y = cell_center(col, row)
            instances.append({
                "object_name": obj, "x": x, "y": y, "rotation": 0,
                "scale_x": 1.0, "scale_y": 1.0, "visible": True,
            })

        # Walls: top and bottom rows, per the tutorial's own room layout
        # diagram.
        for col in range(COLS):
            place("obj_wall", col, 0)
            place("obj_wall", col, ROWS - 1)

        # Goals: left and right edges, behind where each paddle sits.
        for row in range(1, ROWS - 1):
            place("obj_goal_left", 0, row)
            place("obj_goal_right", COLS - 1, row)

        # Paddles: near the left/right edges, centered vertically -- single
        # instances (the sprite itself is the full 64px-tall paddle, not a
        # per-cell tile like the walls/goals).
        place("obj_paddle_left", 2, ROWS // 2)
        place("obj_paddle_right", COLS - 3, ROWS // 2)

        # Ball: center of the room -- safe here (no bricks/other objects
        # occupy the center cell in this layout, unlike Breakout's).
        place("obj_ball", COLS // 2, ROWS // 2)

        # Score display: position is irrelevant (no sprite -- it draws
        # fixed-position text), placed just inside the top wall, centered.
        place("obj_score", COLS // 2, 1)

        room_data = am.create_asset(
            "room_pong", "rooms",
            width=room_w, height=room_h, background_color="#0a0a12",
            instances=instances)
        _sync(ide)
        ide.open_room_editor("room_pong", room_data)
        _capture(ide, app, "tutorial-pong-08-room.png")

        print("Pong capture complete.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------
# Sokoban (wiki/Tutorial-Sokoban.md) -- Phase 2, tutorial 2 of the remaining
# five. Intermediate preset (grid movement + push mechanic).
# ---------------------------------------------------------------------------

def capture_sokoban():
    app = _make_app()
    ide = _make_ide(app)
    scratch = _new_scratch_project(ide, "scratch_sokoban")
    am = ide.asset_manager
    sprite_dir = scratch / "_capture_sprites"
    sprite_dir.mkdir(exist_ok=True)

    try:
        # -- Step 2: Create the Sprites (all 32x32, per the tutorial) --------
        sprites = [
            ("spr_player", (32, 32), "circle", (100, 150, 240, 255)),
            ("spr_crate", (32, 32), "rect", (170, 120, 70, 255)),
            ("spr_crate_ok", (32, 32), "rect", (90, 190, 110, 255)),
            # "gray or dark colors" per the tutorial -- a dark slate, which
            # also stays distinct from the IDE's own grey chrome.
            ("spr_wall", (32, 32), "rect", (95, 105, 125, 255)),
            ("spr_target", (32, 32), "circle", (240, 200, 60, 255)),
            ("spr_floor", (32, 32), "rect", (55, 55, 65, 255)),
        ]
        for name, size, shape, color in sprites:
            png_path = sprite_dir / f"{name}.png"
            _sprite_png(png_path, size, shape, color)
            if am.import_asset(png_path, "sprites", name) is None:
                raise RuntimeError(f"failed to import sprite {name!r}")
        _sync(ide)
        ide.open_sprite_editor("spr_crate", am.get_asset("sprites", "spr_crate"))
        _capture(ide, app, "tutorial-sokoban-02-sprites.png")

        # -- Step 3: Create the Wall Object --------------------------------
        am.create_asset("obj_wall", "objects", sprite="spr_wall",
                        solid=True, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_wall", am.get_asset("objects", "obj_wall"))
        _capture(ide, app, "tutorial-sokoban-03-wall-object.png")

        # -- Step 4: Create the Target Object ------------------------------
        am.create_asset("obj_target", "objects", sprite="spr_target",
                        solid=False, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_target", am.get_asset("objects", "obj_target"))
        _capture(ide, app, "tutorial-sokoban-04-target-object.png")

        # -- Step 5: Create the Crate Object -------------------------------
        crate_events = {
            "step": {"actions": [
                {"action": "if_collision", "parameters": {
                    "x": "0", "y": "0", "object": "obj_target",
                    "then_actions": [
                        {"action": "set_sprite",
                         "parameters": {"sprite": "spr_crate_ok"}},
                    ],
                    "else_actions": [
                        {"action": "set_sprite",
                         "parameters": {"sprite": "spr_crate"}},
                    ],
                }},
            ]},
        }
        am.create_asset("obj_crate", "objects", sprite="spr_crate",
                        solid=True, visible=True, events=crate_events)
        _sync(ide)
        ide.open_object_editor("obj_crate", am.get_asset("objects", "obj_crate"))
        _capture(ide, app, "tutorial-sokoban-05-crate-object.png")

        # -- Step 6: Create the Player Object ------------------------------
        player_events = {
            "keyboard_press": {
                d: {"actions": [
                    {"action": "move_grid",
                     "parameters": {"direction": d, "grid_size": "32"}},
                ]}
                for d in ("right", "left", "up", "down")
            },
            "collision_with_obj_wall": {"actions": [
                {"action": "stop_movement", "parameters": {}},
            ]},
            "collision_with_obj_crate": {"actions": [
                {"action": "if_can_push", "parameters": {
                    "direction": "facing", "object_type": "obj_crate",
                    "then_action": "push_and_move",
                    "else_action": "stop_movement",
                }},
            ]},
        }
        am.create_asset("obj_player", "objects", sprite="spr_player",
                        solid=False, visible=True, events=player_events)
        _sync(ide)
        ide.open_object_editor("obj_player", am.get_asset("objects", "obj_player"))
        _capture(ide, app, "tutorial-sokoban-06-player-object.png")

        # -- Step 7: Create the Win Condition Checker ----------------------
        create_code = (
            "# Count how many target spots exist in the room\n"
            "self.total_targets = sum(\n"
            "    1 for inst in game.current_room.instances\n"
            "    if inst.object_name == 'obj_target'\n"
            ")\n"
        )
        step_code = (
            "# Count crates currently overlapping a target\n"
            "crates_on_targets = sum(\n"
            "    1 for inst in game.current_room.instances\n"
            "    if inst.object_name == 'obj_crate'\n"
            "    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')\n"
            ")\n"
            "\n"
            "if self.total_targets > 0 and crates_on_targets >= self.total_targets:\n"
            "    self.restart_room_flag = True\n"
        )
        controller_events = {
            "create": {"actions": [
                {"action": "execute_code", "parameters": {"code": create_code}},
            ]},
            "step": {"actions": [
                {"action": "execute_code", "parameters": {"code": step_code}},
            ]},
            "draw": {"actions": [
                {"action": "draw_text", "parameters": {
                    "text": "\"Sokoban - Push all crates to targets!\"",
                    "x": "10", "y": "10",
                }},
            ]},
        }
        am.create_asset("obj_game_controller", "objects", sprite=None,
                        solid=False, visible=True, events=controller_events)
        _sync(ide)
        ide.open_object_editor("obj_game_controller",
                               am.get_asset("objects", "obj_game_controller"))
        _capture(ide, app, "tutorial-sokoban-07-controller-object.png")

        # -- Step 9: Design Your Level ------------------------------------
        # The tutorial's own "Example Level Layout" ASCII, 10 cols x 9 rows,
        # translated cell-for-cell (W/P/C/T). Room is exactly that size so
        # the screenshot matches the diagram.
        CELL = 32
        LAYOUT = [
            "WWWWWWWWWW",
            "W........W",
            "W.P...C..W",
            "W..WW....W",
            "W..WT..C.W",
            "W.....WW.W",
            "W.T......W",
            "W........W",
            "WWWWWWWWWW",
        ]
        COLS, ROWS = len(LAYOUT[0]), len(LAYOUT)
        room_w, room_h = COLS * CELL, ROWS * CELL

        instances = []

        def place(obj, col, row):
            instances.append({
                "object_name": obj,
                "x": col * CELL + CELL // 2, "y": row * CELL + CELL // 2,
                "rotation": 0, "scale_x": 1.0, "scale_y": 1.0, "visible": True,
            })

        char_obj = {"W": "obj_wall", "C": "obj_crate",
                    "T": "obj_target", "P": "obj_player"}
        for row, line in enumerate(LAYOUT):
            for col, ch in enumerate(line):
                if ch in char_obj:
                    place(char_obj[ch], col, row)
        # Controller: anywhere (invisible in-game) -- a clear interior cell
        # well away from the border, so its no-sprite placeholder (drawn a
        # little larger than one cell) doesn't overlap a wall.
        place("obj_game_controller", 3, 5)

        room_data = am.create_asset(
            "room_level1", "rooms",
            width=room_w, height=room_h, background_color="#141414",
            instances=instances)
        _sync(ide)
        ide.open_room_editor("room_level1", room_data)
        _capture(ide, app, "tutorial-sokoban-09-room.png")

        print("Sokoban capture complete.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------
# Maze (wiki/Tutorial-Maze.md) -- Phase 2, tutorial 3 of the remaining five.
# NOTE: its object/sprite names (obj_player/obj_coin/obj_exit ...) do NOT
# match the bundled samples/maze_1 (obj_person/obj_goal/obj_wall), so this
# needs its own scratch project like every other one.
# ---------------------------------------------------------------------------

def capture_maze():
    app = _make_app()
    ide = _make_ide(app)
    scratch = _new_scratch_project(ide, "scratch_maze")
    am = ide.asset_manager
    sprite_dir = scratch / "_capture_sprites"
    sprite_dir.mkdir(exist_ok=True)

    try:
        # -- Step 2: Create the Sprites -----------------------------------
        sprites = [
            ("spr_player", (24, 24), "circle", (90, 200, 250, 255)),
            ("spr_wall", (32, 32), "rect", (95, 105, 125, 255)),
            ("spr_exit", (32, 32), "rect", (90, 200, 110, 255)),
            ("spr_coin", (16, 16), "circle", (245, 205, 70, 255)),
            ("spr_floor", (32, 32), "rect", (60, 60, 70, 255)),
        ]
        for name, size, shape, color in sprites:
            png_path = sprite_dir / f"{name}.png"
            _sprite_png(png_path, size, shape, color)
            if am.import_asset(png_path, "sprites", name) is None:
                raise RuntimeError(f"failed to import sprite {name!r}")
        _sync(ide)
        ide.open_sprite_editor("spr_player", am.get_asset("sprites", "spr_player"))
        _capture(ide, app, "tutorial-maze-02-sprites.png")

        # -- Step 3: Create the Wall Object ------------------------------
        am.create_asset("obj_wall", "objects", sprite="spr_wall",
                        solid=True, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_wall", am.get_asset("objects", "obj_wall"))
        _capture(ide, app, "tutorial-maze-03-wall-object.png")

        # -- Step 4: Create the Exit Object -----------------------------
        exit_events = {
            "collision_with_obj_player": {"actions": [
                {"action": "show_message", "parameters": {"message": "You Win!"}},
                {"action": "next_room", "parameters": {}},
            ]},
        }
        am.create_asset("obj_exit", "objects", sprite="spr_exit",
                        solid=False, visible=True, events=exit_events)
        _sync(ide)
        ide.open_object_editor("obj_exit", am.get_asset("objects", "obj_exit"))
        _capture(ide, app, "tutorial-maze-04-exit-object.png")

        # -- Step 5: Create the Coin Object ---------------------------
        coin_events = {
            "collision_with_obj_player": {"actions": [
                {"action": "set_score",
                 "parameters": {"value": "10", "relative": True}},
                {"action": "destroy_instance", "parameters": {"target": "self"}},
            ]},
        }
        am.create_asset("obj_coin", "objects", sprite="spr_coin",
                        solid=False, visible=True, events=coin_events)
        _sync(ide)
        ide.open_object_editor("obj_coin", am.get_asset("objects", "obj_coin"))
        _capture(ide, app, "tutorial-maze-05-coin-object.png")

        # -- Step 6: Create the Player Object ------------------------
        player_events = {
            "keyboard": {
                "right": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "4"}}]},
                "left": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "-4"}}]},
                "down": {"actions": [
                    {"action": "set_vspeed", "parameters": {"speed": "4"}}]},
                "up": {"actions": [
                    {"action": "set_vspeed", "parameters": {"speed": "-4"}}]},
            },
            "keyboard_no_key": {"actions": [
                {"action": "set_hspeed", "parameters": {"speed": "0"}},
                {"action": "set_vspeed", "parameters": {"speed": "0"}},
            ]},
            "collision_with_obj_wall": {"actions": [
                {"action": "stop_movement", "parameters": {}},
            ]},
        }
        am.create_asset("obj_player", "objects", sprite="spr_player",
                        solid=False, visible=True, events=player_events)
        _sync(ide)
        ide.open_object_editor("obj_player", am.get_asset("objects", "obj_player"))
        _capture(ide, app, "tutorial-maze-06-player-object.png")

        # -- Step 7: Create the Game Controller ---------------------
        coins_left_code = (
            "self.coins_left = sum(\n"
            "    1 for inst in game.current_room.instances\n"
            "    if inst.object_name == 'obj_coin'\n"
            ")\n"
        )
        controller_events = {
            "create": {"actions": [
                {"action": "execute_code", "parameters": {"code": "self.timer = 0.0\n"}},
            ]},
            "step": {"actions": [
                {"action": "execute_code",
                 "parameters": {"code": "self.timer += 1.0 / game.fps\n"}},
            ]},
            "draw": {"actions": [
                {"action": "draw_text", "parameters": {"text": "\"Score:\"", "x": "10", "y": "10"}},
                {"action": "draw_text", "parameters": {"text": "\"Time:\"", "x": "10", "y": "30"}},
                {"action": "draw_text", "parameters": {"text": "\"Coins:\"", "x": "10", "y": "50"}},
                {"action": "execute_code", "parameters": {"code": coins_left_code}},
                {"action": "draw_variable", "parameters": {"variable": "score", "x": "70", "y": "10"}},
                {"action": "draw_variable", "parameters": {"variable": "self.timer", "x": "70", "y": "30"}},
                {"action": "draw_variable", "parameters": {"variable": "self.coins_left", "x": "70", "y": "50"}},
            ]},
        }
        am.create_asset("obj_game_controller", "objects", sprite=None,
                        solid=False, visible=True, events=controller_events)
        _sync(ide)
        ide.open_object_editor("obj_game_controller",
                               am.get_asset("objects", "obj_game_controller"))
        _capture(ide, app, "tutorial-maze-07-controller-object.png")

        # -- Step 8: Design Your Maze --------------------------------
        # The tutorial's own "Example Maze Layout" ASCII, transcribed
        # verbatim (space-separated, 20 tokens x 15 rows).
        CELL = 32
        LAYOUT_RAW = [
            "W W W W W W W W W W W W W W W W W W W W",
            "W P . . . . W . . . . . . . W . . . . W",
            "W . W W W . W . W W W W W . W . W W . W",
            "W . W . . . . . . . . . . . . . . W . W",
            "W . W . W W W W W . W W W W W W . W . W",
            "W . . . W . . . . . . . . C . W . . . W",
            "W W W . W . W W W W W W W . . W W W . W",
            "W C . . . . W . . . . . W . . . . . . W",
            "W . W W W W W . W W W . W W W W W W . W",
            "W . . . . . . . . C . . . . . . . . . W",
            "W . W W W W W W W W W . W W W W W W . W",
            "W . . . . . . . . . . . W . . . . . . W",
            "W W W W W W W W W W W . W . W W W W . W",
            "W . . . . . . . . . . . . . W . C . E W",
            "W W W W W W W W W W W W W W W W W W W W",
        ]
        norm = [line.split() for line in LAYOUT_RAW]
        COLS, ROWS = len(norm[0]), len(norm)

        instances = []

        def place(obj, col, row):
            instances.append({
                "object_name": obj,
                "x": col * CELL + CELL // 2, "y": row * CELL + CELL // 2,
                "rotation": 0, "scale_x": 1.0, "scale_y": 1.0, "visible": True,
            })

        char_obj = {"W": "obj_wall", "C": "obj_coin", "E": "obj_exit", "P": "obj_player"}
        for row, line in enumerate(norm):
            for col, ch in enumerate(line):
                if ch in char_obj:
                    place(char_obj[ch], col, row)
        # Controller: anywhere (invisible) -- a clear interior cell.
        place("obj_game_controller", 3, 11)

        room_data = am.create_asset(
            "room_maze", "rooms",
            width=COLS * CELL, height=ROWS * CELL, background_color="#101014",
            instances=instances)
        _sync(ide)
        ide.open_room_editor("room_maze", room_data)
        _capture(ide, app, "tutorial-maze-08-room.png")

        print("Maze capture complete.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------
# Platformer (wiki/Tutorial-Platformer.md) -- Phase 2, tutorial 4 of five.
# ---------------------------------------------------------------------------

def capture_platformer():
    app = _make_app()
    ide = _make_ide(app)
    scratch = _new_scratch_project(ide, "scratch_platformer")
    am = ide.asset_manager
    sprite_dir = scratch / "_capture_sprites"
    sprite_dir.mkdir(exist_ok=True)

    try:
        # -- Step 2: Create the Sprites ---------------------------------
        sprites = [
            ("spr_player", (32, 48), "rect", (230, 90, 90, 255)),
            ("spr_ground", (32, 32), "rect", (140, 100, 60, 255)),
            ("spr_platform", (64, 16), "rect", (170, 140, 90, 255)),
            ("spr_coin", (16, 16), "circle", (245, 205, 70, 255)),
            # "gray or red" per the tutorial -- grey, to stay distinct from
            # the red player sprite in the room screenshot.
            ("spr_spike", (32, 32), "rect", (190, 190, 200, 255)),
            ("spr_flag", (32, 64), "rect", (90, 200, 110, 255)),
        ]
        for name, size, shape, color in sprites:
            png_path = sprite_dir / f"{name}.png"
            _sprite_png(png_path, size, shape, color)
            if am.import_asset(png_path, "sprites", name) is None:
                raise RuntimeError(f"failed to import sprite {name!r}")
        _sync(ide)
        ide.open_sprite_editor("spr_player", am.get_asset("sprites", "spr_player"))
        _capture(ide, app, "tutorial-platformer-02-sprites.png")

        # -- Step 3: Create the Ground Object -------------------------
        am.create_asset("obj_ground", "objects", sprite="spr_ground",
                        solid=True, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_ground", am.get_asset("objects", "obj_ground"))
        _capture(ide, app, "tutorial-platformer-03-ground-object.png")

        # -- Step 4: Create the Platform Object -----------------------
        am.create_asset("obj_platform", "objects", sprite="spr_platform",
                        solid=True, visible=True, events={})
        _sync(ide)
        ide.open_object_editor("obj_platform", am.get_asset("objects", "obj_platform"))
        _capture(ide, app, "tutorial-platformer-04-platform-object.png")

        # -- Step 5: Create the Player Object -------------------------
        player_events = {
            "create": {"actions": [
                {"action": "set_gravity",
                 "parameters": {"direction": "270", "gravity": "0.5"}},
            ]},
            "keyboard": {
                "left": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "-4"}}]},
                "right": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "4"}}]},
            },
            "keyboard_no_key": {"actions": [
                {"action": "set_hspeed", "parameters": {"speed": "0"}},
            ]},
            "keyboard_press": {
                "up": {"actions": [
                    {"action": "set_vspeed", "parameters": {"speed": "-10"}}]},
            },
            "collision_with_obj_ground": {"actions": [
                {"action": "stop_movement", "parameters": {}},
            ]},
        }
        am.create_asset("obj_player", "objects", sprite="spr_player",
                        solid=False, visible=True, events=player_events)
        _sync(ide)
        ide.open_object_editor("obj_player", am.get_asset("objects", "obj_player"))
        _capture(ide, app, "tutorial-platformer-05-player-object.png")

        # -- Step 6: Create the Coin Object -------------------------
        coin_events = {
            "collision_with_obj_player": {"actions": [
                {"action": "set_score",
                 "parameters": {"value": "10", "relative": True}},
                {"action": "destroy_instance", "parameters": {"target": "self"}},
            ]},
        }
        am.create_asset("obj_coin", "objects", sprite="spr_coin",
                        solid=False, visible=True, events=coin_events)
        _sync(ide)
        ide.open_object_editor("obj_coin", am.get_asset("objects", "obj_coin"))
        _capture(ide, app, "tutorial-platformer-06-coin-object.png")

        # -- Step 7: Create the Spike Object ------------------------
        spike_events = {
            "collision_with_obj_player": {"actions": [
                {"action": "show_message",
                 "parameters": {"message": "Ouch! You hit a spike!"}},
                {"action": "restart_room", "parameters": {}},
            ]},
        }
        am.create_asset("obj_spike", "objects", sprite="spr_spike",
                        solid=False, visible=True, events=spike_events)
        _sync(ide)
        ide.open_object_editor("obj_spike", am.get_asset("objects", "obj_spike"))
        _capture(ide, app, "tutorial-platformer-07-spike-object.png")

        # -- Step 8: Create the Flag Object ------------------------
        flag_events = {
            "collision_with_obj_player": {"actions": [
                {"action": "show_message",
                 "parameters": {"message": "Level Complete!"}},
                {"action": "next_room", "parameters": {}},
            ]},
        }
        am.create_asset("obj_flag", "objects", sprite="spr_flag",
                        solid=False, visible=True, events=flag_events)
        _sync(ide)
        ide.open_object_editor("obj_flag", am.get_asset("objects", "obj_flag"))
        _capture(ide, app, "tutorial-platformer-08-flag-object.png")

        # -- Step 9: Create the Game Controller --------------------
        controller_events = {
            "draw": {"actions": [
                {"action": "draw_text",
                 "parameters": {"text": "\"Score:\"", "x": "10", "y": "10"}},
                {"action": "draw_variable",
                 "parameters": {"variable": "score", "x": "70", "y": "10"}},
            ]},
        }
        am.create_asset("obj_game_controller", "objects", sprite=None,
                        solid=False, visible=True, events=controller_events)
        _sync(ide)
        ide.open_object_editor("obj_game_controller",
                               am.get_asset("objects", "obj_game_controller"))
        _capture(ide, app, "tutorial-platformer-09-controller-object.png")

        # -- Step 10: Design Your Level ---------------------------
        # A grid interpretation of the tutorial's loose "Example Level
        # Layout" art: ground along the bottom with two pits, four floating
        # platforms, coins on/near them, two spikes by a pit, the flag at
        # the far right, the player at the far left.
        CELL = 32
        COLS, ROWS = 25, 15   # 800 x 480, per Step 10's own example size
        instances = []

        def place(obj, col, row):
            instances.append({
                "object_name": obj,
                "x": col * CELL + CELL // 2, "y": row * CELL + CELL // 2,
                "rotation": 0, "scale_x": 1.0, "scale_y": 1.0, "visible": True,
            })

        # Ground along row 14, with pits at cols 8-9 and 16-17.
        pits = {8, 9, 16, 17}
        for col in range(COLS):
            if col not in pits:
                place("obj_ground", col, 14)
        # Floating platforms.
        for col, row in [(5, 11), (10, 9), (15, 10), (20, 8)]:
            place("obj_platform", col, row)
        # Coins on / above the platforms and one over a pit.
        for col, row in [(5, 10), (10, 8), (15, 9), (20, 7), (8, 12)]:
            place("obj_coin", col, row)
        # Spikes on the ground next to the pits.
        for col in (7, 18):
            place("obj_spike", col, 13)
        # Flag at the end; player at the start (both standing on the ground).
        place("obj_flag", 23, 12)
        place("obj_player", 1, 13)
        # Controller: anywhere (invisible) -- up in the open sky, top-left.
        place("obj_game_controller", 2, 2)

        room_data = am.create_asset(
            "room_level1", "rooms",
            width=COLS * CELL, height=ROWS * CELL, background_color="#12141c",
            instances=instances)
        _sync(ide)
        ide.open_room_editor("room_level1", room_data)
        _fit_window_to_room(ide, app, "room_level1")
        _capture(ide, app, "tutorial-platformer-10-room.png")

        print("Platformer capture complete.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


SCENARIOS = {
    "breakout": capture_breakout,
    "pong": capture_pong,
    "sokoban": capture_sokoban,
    "maze": capture_maze,
    "platformer": capture_platformer,
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
        print(f"Usage: {sys.argv[0]} <{'|'.join(SCENARIOS)}>")
        return 1
    SCENARIOS[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())

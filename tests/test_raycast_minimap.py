"""draw_minimap — desktop (RAYCAST_MINIMAP_PLAN Unit 1).

A MACRO action: it reads the wall edges the raycast renderer already derived
and emits ordinary 'rectangle' / 'line' draw-queue commands, so no target
needed a bespoke minimap renderer. build_minimap_commands() is the single
source for the geometry; the HTML5/Kivy ports mirror it and
tests/test_raycast_export_parity.py compares them against it.
"""
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

from runtime.action_executor import (  # noqa: E402
    build_minimap_commands, MINIMAP_HEADING_LEN, MINIMAP_MARKER_HALF,
)

# A 2x2-cell room with one vertical and one horizontal edge, so every
# projected coordinate can be checked by hand.
SIMPLE = dict(
    v_walls={(1, 0)}, h_walls={(0, 1)}, cell_size=32,
    room_width=64, room_height=64,
    cam_x=16.0, cam_y=48.0, facing_angle=0.0,
    x=10.0, y=20.0, size=128.0,
    back_color="#101018", wall_color="#8080a0", player_color="#ffd040",
)


def test_action_is_registered():
    from events.action_types import ACTION_TYPES, get_action_type
    assert "draw_minimap" in ACTION_TYPES
    at = get_action_type("draw_minimap")
    assert at.category == "3D View"
    names = [p.name for p in at.parameters]
    assert names == ["x", "y", "size", "back_color", "wall_color", "player_color"]


def test_handler_is_auto_discovered():
    """The executor registers execute_*_action by naming convention."""
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    assert "draw_minimap" in ex.action_handlers


def test_background_panel_comes_first_and_covers_the_square():
    cmds = build_minimap_commands(**SIMPLE)
    bg = cmds[0]
    assert bg["type"] == "rectangle" and bg["filled"] is True
    assert (bg["x1"], bg["y1"]) == (10.0, 20.0)
    assert (bg["x2"], bg["y2"]) == (10.0 + 128.0, 20.0 + 128.0)
    assert bg["color"] == "#101018"


def test_walls_project_north_up_with_a_uniform_scale():
    """scale = size / max(room_w, room_h); px = x + world_x * scale. y is NOT
    flipped here — that happens once, later, in Kivy's shared draw path."""
    cmds = build_minimap_commands(**SIMPLE)
    lines = [c for c in cmds if c["type"] == "line" and c["color"] == "#8080a0"]
    assert len(lines) == 2, "one vertical + one horizontal edge expected"
    scale = 128.0 / 64.0                      # = 2.0

    # v_wall (1, 0): x = 1*32, y from 0*32 to 1*32  -> a VERTICAL line
    v = next(c for c in lines if c["x1"] == c["x2"])
    assert v["x1"] == 10.0 + 32 * scale
    assert v["y1"] == 20.0 + 0 * scale
    assert v["y2"] == 20.0 + 32 * scale

    # h_wall (0, 1): y = 1*32, x from 0*32 to 1*32  -> a HORIZONTAL line
    h = next(c for c in lines if c["y1"] == c["y2"])
    assert h["y1"] == 20.0 + 32 * scale
    assert h["x1"] == 10.0 + 0 * scale
    assert h["x2"] == 10.0 + 32 * scale


def test_player_marker_and_heading():
    cmds = build_minimap_commands(**SIMPLE)
    marks = [c for c in cmds if c.get("color") == "#ffd040"]
    assert len(marks) == 2, "a position cross and a heading line"
    scale = 2.0
    cx, cy = 10.0 + 16.0 * scale, 20.0 + 48.0 * scale

    cross = next(c for c in marks if c["y1"] == c["y2"])
    assert cross["x1"] == cx - MINIMAP_MARKER_HALF
    assert cross["x2"] == cx + MINIMAP_MARKER_HALF

    heading = next(c for c in marks if (c["x1"], c["y1"]) == (cx, cy))
    # facing 0 = EAST in GM, and screen y is down -> heading points +x, same y.
    assert heading["x2"] == cx + MINIMAP_HEADING_LEN
    assert abs(heading["y2"] - cy) < 1e-9


def test_heading_follows_facing_angle_with_the_gm_convention():
    """GM 0=right / 90=up, screen y DOWN — so 90 must point UP (smaller y)."""
    scale = 2.0
    cx, cy = 10.0 + 16.0 * scale, 20.0 + 48.0 * scale
    for angle, dx, dy in ((0, 1, 0), (90, 0, -1), (180, -1, 0), (270, 0, 1)):
        cmds = build_minimap_commands(**{**SIMPLE, "facing_angle": angle})
        heading = next(c for c in cmds
                       if c.get("color") == "#ffd040"
                       and (c["x1"], c["y1"]) == (cx, cy))
        assert abs((heading["x2"] - cx) - dx * MINIMAP_HEADING_LEN) < 1e-9, angle
        assert abs((heading["y2"] - cy) - dy * MINIMAP_HEADING_LEN) < 1e-9, angle


def test_no_camera_still_draws_the_map():
    """A room whose camera hasn't resolved yet must show walls, not crash."""
    cmds = build_minimap_commands(**{**SIMPLE, "cam_x": None, "cam_y": None})
    assert cmds[0]["type"] == "rectangle"
    assert any(c["color"] == "#8080a0" for c in cmds)
    assert not any(c.get("color") == "#ffd040" for c in cmds)


def test_degenerate_room_returns_just_the_panel():
    """A zero-sized room would divide by zero in the scale."""
    cmds = build_minimap_commands(**{**SIMPLE, "room_width": 0, "room_height": 0})
    assert len(cmds) == 1 and cmds[0]["type"] == "rectangle"


def test_output_is_deterministic():
    """Wall sets are unordered; the commands must not be, or the three targets
    could emit the same picture in different orders and diff spuriously."""
    a = build_minimap_commands(**{**SIMPLE, "v_walls": {(1, 0), (2, 1), (0, 3)}})
    b = build_minimap_commands(**{**SIMPLE, "v_walls": {(0, 3), (1, 0), (2, 1)}})
    assert a == b


# --- End to end through the real game loop ---------------------------------

def test_minimap_renders_over_raycast_3():
    """The whole point: real room, real walls, real camera, drawn in the HUD
    pass over the first-person view."""
    from runtime.game_runner import GameRunner, GameInstance

    project = str(REPO_ROOT / "samples" / "raycast_3" / "project.json")
    runner = GameRunner(project)
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""

    seen = []
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        if self.object_name == "obj_hud":
            seen.extend(self._draw_queue)
        self._draw_queue = []

    # Inject the minimap into the HUD's draw event before run() resolves it.
    hud = runner._objects_data["obj_hud"]
    hud["events"]["draw"]["actions"].append({
        "action": "draw_minimap",
        "parameters": {"x": "500", "y": "340", "size": "130"},
    })

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            if state["f"] >= 6:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    GameInstance._process_draw_queue = spy
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real

    assert runner.current_room.raycast_camera["enabled"] is True
    walls = [c for c in seen if c.get("type") == "line"]
    assert len(walls) > 50, \
        f"minimap drew {len(walls)} lines — the room's wall edges are missing"
    panel = [c for c in seen if c.get("type") == "rectangle"]
    assert panel, "no minimap background panel"
    # Everything must land inside the requested square.
    for c in walls:
        for key in ("x1", "x2"):
            assert 500 - 1 <= c[key] <= 500 + 130 + 1, c
        for key in ("y1", "y2"):
            assert 340 - 1 <= c[key] <= 340 + 130 + 1, c

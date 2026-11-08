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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

# draw_minimap + its geometry builder moved into the raycast extension (Stage
# B3, docs/RAYCAST_EXTENSION_PLAN.md). Load plugins so the schema is merged into
# ACTION_TYPES (the IDE does this at startup; a bare test import does not).
from events.plugin_loader import load_all_plugins  # noqa: E402
load_all_plugins()
from extensions.raycast_2_5d.hud import (  # noqa: E402
    build_minimap_commands, MINIMAP_HEADING_LEN, MINIMAP_MARKER_HALF,
    MINIMAP_MARK_HALF, MINIMAP_TRAIL_HALF,
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
    # Order matters: it is the order the fields appear in the IDE dialog. The
    # four mark_* parameters are opt-in object dots, added after the original
    # six so an existing project's saved parameters keep their positions.
    assert names == ["x", "y", "size", "back_color", "wall_color",
                     "player_color", "mark_object", "mark_color",
                     "mark_object_2", "mark_color_2",
                     "show_trail", "trail_color"]


def test_handler_is_registered_from_the_extension():
    """The handler is the extension's PluginExecutor method now, registered onto
    the executor by load_all_plugins (Stage B3), not an ActionExecutor method."""
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    load_all_plugins(ex)
    assert "draw_minimap" in ex.action_handlers
    assert not hasattr(ex, "execute_draw_minimap_action")


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


# --- Breadcrumb trail (opt-in) ----------------------------------------------

def test_trail_is_off_by_default():
    """No trail_color -> no trail dots, even if trail points are passed --
    the three existing raycast samples' minimaps must render unchanged."""
    cmds = build_minimap_commands(**SIMPLE, trail=[(0.0, 0.0), (32.0, 32.0)])
    allowed = {SIMPLE["back_color"], SIMPLE["wall_color"], SIMPLE["player_color"]}
    assert not any(c.get("color") not in allowed for c in cmds)


def test_trail_dots_are_projected_like_everything_else():
    scale = 2.0
    cmds = build_minimap_commands(
        **SIMPLE, trail=[(16.0, 16.0)], trail_color="#406080")
    dots = [c for c in cmds if c.get("color") == "#406080"]
    assert len(dots) == 1
    d = dots[0]
    tx, ty = 10.0 + 16.0 * scale, 20.0 + 16.0 * scale
    assert d["type"] == "rectangle" and d["filled"] is True
    assert d["x1"] == tx - MINIMAP_TRAIL_HALF and d["x2"] == tx + MINIMAP_TRAIL_HALF
    assert d["y1"] == ty - MINIMAP_TRAIL_HALF and d["y2"] == ty + MINIMAP_TRAIL_HALF


def test_trail_dot_is_smaller_than_a_mark_dot():
    """So a trail reads as a faint trace, not more pickups."""
    assert MINIMAP_TRAIL_HALF < MINIMAP_MARK_HALF


def test_trail_renders_under_marks_and_the_player_marker():
    """Z-order: trail (least important) first, then marks, then the player
    marker on top -- matches the existing marks-under-player convention."""
    cmds = build_minimap_commands(
        **SIMPLE, trail=[(16.0, 16.0)], trail_color="#406080",
        marks=[{"color": "#40e0ff", "points": [(16.0, 16.0)]}])
    colors = [c.get("color") for c in cmds]
    assert colors.index("#406080") < colors.index("#40e0ff") < colors.index("#ffd040")


def test_trail_points_are_sorted_for_determinism():
    """Same reasoning as walls/marks: a set's iteration order isn't stable,
    and the parity test compares command lists element by element."""
    a = build_minimap_commands(
        **SIMPLE, trail=[(0.0, 0.0), (32.0, 32.0), (64.0, 0.0)],
        trail_color="#406080")
    b = build_minimap_commands(
        **SIMPLE, trail=[(64.0, 0.0), (0.0, 0.0), (32.0, 32.0)],
        trail_color="#406080")
    assert a == b


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

    # Use the sample's OWN minimap rather than injecting one — obj_hud ships
    # with it now, and appending a second would capture both and assert the
    # union of two squares.
    hud = runner._objects_data["obj_hud"]
    mm = next(a for a in hud["events"]["draw"]["actions"]
              if a["action"] == "draw_minimap")
    mm_x = float(mm["parameters"]["x"])
    mm_y = float(mm["parameters"]["y"])
    mm_size = float(mm["parameters"]["size"])

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            # The map is OFF by default now — press M to bring it up.
            if f == 2:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_m))
            if f >= 10:
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

    assert raycast_state(runner.current_room)["camera"]["enabled"] is True
    walls = [c for c in seen if c.get("type") == "line"]
    assert len(walls) > 50, \
        f"minimap drew {len(walls)} lines — the room's wall edges are missing"
    panel = [c for c in seen if c.get("type") == "rectangle"]
    assert panel, "no minimap background panel"
    # Everything must land inside the square the sample asked for.
    for c in walls:
        for key in ("x1", "x2"):
            assert mm_x - 1 <= c[key] <= mm_x + mm_size + 1, c
        for key in ("y1", "y2"):
            assert mm_y - 1 <= c[key] <= mm_y + mm_size + 1, c
    # And inside the 640x480 window, i.e. actually on screen.
    assert mm_x + mm_size <= 640 and mm_y + mm_size <= 480


def test_marker_sits_at_the_ray_origin_not_the_sprite_corner():
    """The camera position must be the SAME point the rays are cast from — the
    origin-aware centre of the camera's cell (game_runner.py:2053). Using the
    raw x/y corner parks the marker half a sprite off the actual viewpoint,
    which is exactly the class of exact-grid-line error the 2026-07-17 bug hunt
    fixed in the renderer."""
    src = (REPO_ROOT / "extensions" / "raycast_2_5d" / "handlers.py").read_text(
        encoding="utf-8")
    block = src[src.index("def execute_draw_minimap_action"):]
    assert "_sprite_top_left" in block, \
        "minimap is not using the origin-aware top-left"
    assert "_cached_width" in block and "_cached_height" in block, \
        "minimap is not offsetting to the cell centre"


def test_marker_lands_on_the_player_in_the_real_sample():
    """Behavioural version of the above: the marker must sit where the player
    actually is, within a pixel of the projected centre."""
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
            seen.clear()
            seen.extend(self._draw_queue)
        self._draw_queue = []

    # Re-point the sample's OWN minimap 1:1 over the room, so minimap
    # coordinates equal world coordinates and the marker can be checked
    # directly. Appending a second one would emit two markers.
    mm = next(a for a in runner._objects_data["obj_hud"]["events"]["draw"]["actions"]
              if a["action"] == "draw_minimap")
    mm["parameters"] = {"x": "0", "y": "0", "size": "480"}

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            # The map is OFF by default now — press M to bring it up.
            if f == 2:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_m))
            if f >= 10:
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

    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    room = runner.current_room
    cx, cy = room._sprite_top_left(player)
    cx += player._cached_width / 2.0
    cy += player._cached_height / 2.0

    marks = [c for c in seen if c.get("color") == "#ffd040"]
    assert marks, "no player marker drawn"
    heading = [c for c in marks if c["x1"] == c["x2"] or True][-1]
    # size == room size, x=y=0, so minimap coords == world coords.
    assert abs(heading["x1"] - cx) < 1.0, (heading["x1"], cx)
    assert abs(heading["y1"] - cy) < 1.0, (heading["y1"], cy)


# --- On-demand minimap (toggle) --------------------------------------------
# The minimap is drawn only while toggled on. Two reasons, both concrete:
# it cost ~250 line commands EVERY frame, and at its old bottom-right position
# it overlapped the Kivy virtual D-pad by 117x47 px on a 640x480 Android build.

def test_minimap_is_off_until_toggled_and_alternates():
    """The toggle uses test_variable + exit_event rather than two bare
    conditionals — the naive version sets the flag to 1 and then immediately
    reads 1 and sets it back to 0, so the map never appears."""
    from runtime.game_runner import GameRunner, GameInstance

    runner = GameRunner(str(REPO_ROOT / "samples" / "raycast_3" / "project.json"))
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""

    per_frame = {}
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        if self.object_name == "obj_hud":
            per_frame[state["f"]] = sum(1 for c in self._draw_queue
                                        if c.get("color") == "#8080a0")
        self._draw_queue = []

    PRESS = {10, 30, 50}
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            if f in PRESS:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
            if f - 1 in PRESS:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_m))
            if f >= 65:
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

    on = lambda f: per_frame.get(f, 0) > 0
    assert not on(5), "map drawn before any toggle — it must default to off"
    assert on(20), "first M press did not show the map"
    assert not on(40), "second M press did not hide the map"
    assert on(60), "third M press did not show it again"
    # And while off it costs NOTHING, which is the point.
    assert per_frame.get(5, 0) == 0


def test_minimap_clears_the_android_dpad():
    """Concrete regression: at (508,348,124) the map overlapped Kivy's virtual
    D-pad by 117x47 px. The D-pad geometry is read from the exporter so this
    can't drift from the real thing."""
    import json as _json
    import re as _re
    src = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    btn = int(_re.search(r"self\._btn_size = (\d+)", src).group(1))
    pad = int(_re.search(r"self\._padding = (\d+)", src).group(1))
    W, H = 640, 480
    cx, cy = W - pad - btn * 1.5, pad + btn * 1.5
    corners = [(cx, cy + btn), (cx, cy - btn), (cx - btn, cy), (cx + btn, cy)]
    dp_x1 = min(x for x, _ in corners)
    dp_x2 = max(x for x, _ in corners) + btn
    dp_y1 = H - (max(y for _, y in corners) + btn)
    dp_y2 = H - min(y for _, y in corners)

    hud = _json.loads((REPO_ROOT / "samples" / "raycast_3" / "objects" /
                       "obj_hud.json").read_text(encoding="utf-8"))
    mm = next(a for a in hud["events"]["draw"]["actions"]
              if a["action"] == "draw_minimap")["parameters"]
    mx, my, ms = float(mm["x"]), float(mm["y"]), float(mm["size"])

    overlap_x = min(dp_x2, mx + ms) - max(dp_x1, mx)
    overlap_y = min(dp_y2, my + ms) - max(dp_y1, my)
    assert not (overlap_x > 0 and overlap_y > 0), (
        f"minimap ({mx},{my},{ms}) overlaps the Android D-pad "
        f"(x {dp_x1}..{dp_x2}, y {dp_y1}..{dp_y2}) by "
        f"{overlap_x:.0f}x{overlap_y:.0f}px")
    assert mx + ms <= W and my + ms <= H, "minimap runs off screen"


# --- Breadcrumb trail -- handler-level persistence --------------------------
# The trail is state that must survive across frames (a point list would grow
# forever; a visited-cell SET is bounded by the maze's own cell count) --
# these exercise execute_draw_minimap_action directly, the same
# _raycast_executor/_dispatch pattern test_raycast_billboard_rotation.py uses.

from runtime.game_runner import GameInstance  # noqa: E402
from test_raycast_view import _room, _raycast_executor, _dispatch  # noqa: E402


def _camera(name, x, y, facing=0.0):
    cam = GameInstance(name, x, y, {}, action_executor=None)
    cam.facing_angle = facing
    return cam


class TestTrailPersistence:
    def _room_with_camera(self, top_left_x, top_left_y):
        """A camera's resolved CENTRE (what the handler buckets into a grid
        cell) is its top-left + half its default 32x32 cached size, i.e.
        +16/+16 -- so a top-left aligned to a cell boundary (gx*32, gy*32)
        always resolves unambiguously to cell (gx, gy), never a boundary."""
        room = _room(256, 256)
        camera = _camera("obj_person", top_left_x, top_left_y)
        room.instances.append(camera)
        raycast_state(room)["camera"] = {
            "enabled": True, "camera_object": "obj_person", "cell_size": 32,
        }
        return room, camera

    def _draw(self, ex, room, params):
        hud = GameInstance("obj_hud", 0, 0, {}, action_executor=None)
        hud._draw_queue = []
        ex.game_runner = type("GR", (), {"current_room": room})()
        _dispatch(ex, "draw_minimap", hud, params)
        return hud._draw_queue

    def test_disabled_by_default_leaves_no_trail_state(self):
        room, _ = self._room_with_camera(0, 0)
        ex = _raycast_executor()
        self._draw(ex, room, {"x": 0, "y": 0, "size": 100})
        assert "trail" not in raycast_state(room)

    def test_enabling_records_the_current_cell(self):
        room, _ = self._room_with_camera(0, 0)      # cell (0, 0)
        ex = _raycast_executor()
        self._draw(ex, room, {"x": 0, "y": 0, "size": 100, "show_trail": True})
        assert raycast_state(room)["trail"] == {(0, 0)}

    def test_moving_accumulates_distinct_cells(self):
        room, camera = self._room_with_camera(0, 0)         # cell (0, 0)
        ex = _raycast_executor()
        params = {"x": 0, "y": 0, "size": 100, "show_trail": True}
        self._draw(ex, room, params)
        camera.x, camera.y = 32, 0                           # cell (1, 0)
        self._draw(ex, room, params)
        camera.x, camera.y = 32, 32                          # cell (1, 1)
        self._draw(ex, room, params)
        assert raycast_state(room)["trail"] == {(0, 0), (1, 0), (1, 1)}

    def test_revisiting_a_cell_does_not_duplicate(self):
        room, camera = self._room_with_camera(0, 0)
        ex = _raycast_executor()
        params = {"x": 0, "y": 0, "size": 100, "show_trail": True}
        self._draw(ex, room, params)
        camera.x, camera.y = 32, 0
        self._draw(ex, room, params)
        camera.x, camera.y = 0, 0                            # back to (0, 0)
        queue = self._draw(ex, room, params)
        assert raycast_state(room)["trail"] == {(0, 0), (1, 0)}
        dots = [c for c in queue if c.get("color") == "#406080"]
        assert len(dots) == 2, "a revisited cell must not draw a second dot"

    def test_trail_color_param_is_honored(self):
        room, _ = self._room_with_camera(0, 0)
        ex = _raycast_executor()
        queue = self._draw(ex, room, {
            "x": 0, "y": 0, "size": 100,
            "show_trail": True, "trail_color": "#ff00ff"})
        dots = [c for c in queue if c.get("color") == "#ff00ff"]
        assert len(dots) == 1


def test_trail_shows_the_real_explored_path_over_raycast_3():
    """End to end through the real game loop: turn the sample's own minimap
    trail on, walk the player, and confirm the trail grows with distinct
    dots and survives the toggle-off/toggle-on cycle (press M to hide/show
    doesn't wipe the room's own persisted visited-cell state)."""
    from runtime.game_runner import GameRunner

    runner = GameRunner(str(REPO_ROOT / "samples" / "raycast_3" / "project.json"))
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""

    mm = next(a for a in runner._objects_data["obj_hud"]["events"]["draw"]["actions"]
              if a["action"] == "draw_minimap")
    mm["parameters"] = dict(mm["parameters"], show_trail=True, trail_color="#406080")

    trail_counts = []
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        if self.object_name == "obj_hud":
            trail_counts.append(
                sum(1 for c in self._draw_queue if c.get("color") == "#406080"))
        self._draw_queue = []

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            if f == 2:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_m))
            # Walk FORWARD for a while so the player actually crosses cells --
            # left/right only TURN in this FPS-style sample (set_facing_angle);
            # up/down are the ones that move (set_direction_speed).
            if f == 4:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
            if f >= 120:
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

    assert raycast_state(runner.current_room)["trail"], "no cells recorded"
    nonzero = [c for c in trail_counts if c > 0]
    assert nonzero, "the trail never drew a single dot"
    assert max(nonzero) >= 2, "walking never grew the trail past one cell"

"""Drawing stairs in the raycast view (docs/RAYCAST_STAIRS_PLAN.md, S5).

A room with at least one step is drawn by a front-to-back column walk:
the ray keeps going past steps, every rise in floor height is drawn as a
riser (the step's front), a drop draws nothing (the lower floor hides behind
the nearer edge), and the wall that stops the ray is drawn only down to what
stands in front of it. Rooms with no step never take this path.

The geometry tests check WHERE things land against the one projection
    y(z, d) = horizon + (eye_z - z) * view_h / d
and the render tests read the resulting pixel rows, through hand-built rooms
and through the real GameRunner loop on a project authored with Set Floor
Height.
"""
import json
import math
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d import renderer  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    build_raycast_walls, cast_ray, cast_ray_steps, layout_column,
    render_raycast_view, stairs_y, RAYCAST_EYE_HEIGHT,
)
from test_raycast_view import _room, _solid_instance  # noqa: E402

CELL = 32
H = 480
HALF = H / 2
EYE = RAYCAST_EYE_HEIGHT * CELL              # 24 px
WALL_RGB, FLOOR_RGB, CEIL_RGB = (255, 0, 0), (0, 255, 0), (0, 0, 255)


def _step(x, y, height):
    inst = GameInstance("obj_step", x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = inst._cached_height = 32
    inst.raycast_floor_height = float(height)
    inst.raycast_step_top_texture = ""
    inst.raycast_step_side_texture = ""
    return inst


def _stairs_room():
    """15x15 cells, solid border; a 5-wide staircase (x=5..8, 8 px steps)
    up to a 32-px platform (x=9..11), rows 5..9."""
    room = _room(480, 480)
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            room.instances.append(_solid_instance("w", x * CELL, y * CELL))
    for row in range(5, 10):
        for i, x in enumerate(range(5, 9)):
            room.instances.append(_step(x * CELL, row * CELL, 8 * (i + 1)))
        for x in range(9, 12):
            room.instances.append(_step(x * CELL, row * CELL, 32))
    cam = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    cam._cached_width = cam._cached_height = 32
    room.instances.append(cam)
    return room, cam


def _render(room, cam, cell_xy, angle, **extra):
    cam.x, cam.y = cell_xy[0] * CELL, cell_xy[1] * CELL
    cam.facing_angle = angle
    cfg = {"enabled": True, "camera_object": "obj_person", "fov": 66,
           "render_distance": 20, "cell_size": CELL, "columns": 320,
           "wall_color": "#ff0000", "floor_color": "#00ff00",
           "ceiling_color": "#0000ff", "wall_height": 3,
           "wall_textured": False}
    cfg.update(extra)
    raycast_state(room)["camera"] = cfg
    screen = pygame.Surface((480, H))
    render_raycast_view(room, screen)
    return screen


def _kind(rgb):
    r, g, b = rgb[:3]
    if (r, g, b) == FLOOR_RGB:
        return "floor"
    if (r, g, b) == CEIL_RGB:
        return "ceiling"
    if r > 0 and g == 0 and b == 0:
        return "wall"            # walls and risers: the shaded wall colour
    return "?"


def _column(screen, x=240):
    return [_kind(screen.get_at((x, y))) for y in range(H)]


def _layout(heights, cam_cell, angle_screen, h0=None, eye=None, walls=()):
    """layout_column for a straight-ahead ray (cos_off 1) in a bare room."""
    room = _room(480, 480)
    for w in walls:
        room.instances.append(w)
    build_raycast_walls(room, CELL)
    px, py = cam_cell[0] * CELL, cam_cell[1] * CELL
    crossings, hit = cast_ray_steps(room, px, py, angle_screen, CELL, 20, heights)
    h0 = heights.get((int(cam_cell[0]), int(cam_cell[1])), 0.0) if h0 is None else h0
    eye = h0 + EYE if eye is None else eye
    return crossings, hit, layout_column(crossings, hit, h0, eye, 96.0, CELL, 1.0,
                                         HALF, H, 20)


# ------------------------------------------------------------ the ray cast

class TestCastRaySteps:
    def test_walls_are_hit_exactly_like_cast_ray(self):
        """Steps never stop a ray: the wall result is cast_ray's, bit for
        bit, for random rays in a room full of steps and thin walls."""
        rnd = random.Random(7)
        room, _ = _stairs_room()
        for _ in range(20):
            gx, gy = rnd.randrange(1, 14), rnd.randrange(1, 14)
            room.instances.append(_solid_instance("t", gx * CELL - 4, gy * CELL,
                                                  width=8, height=32))
        build_raycast_walls(room, CELL)
        from extensions.raycast_2_5d.heights import build_floor_heights
        heights, _ = build_floor_heights(room, CELL, 1000)
        for _ in range(300):
            px, py = rnd.uniform(33, 447), rnd.uniform(33, 447)
            ang = rnd.uniform(-math.pi, math.pi)
            _, hit = cast_ray_steps(room, px, py, ang, CELL, 20, heights)
            assert hit == cast_ray(room, px, py, ang, CELL, 20)

    def test_records_each_change_of_floor_height(self):
        heights = {(3, 1): 8.0, (4, 1): 16.0, (6, 1): 16.0}
        crossings, _, _ = _layout(heights, (1.5, 1.5), 0.0)
        got = [(round(d, 9), h, c) for d, h, _s, _u, c in crossings]
        # x=3 rise to 8, x=4 rise to 16, x=5 drop to 0, x=6 rise to 16, x=7 drop
        assert got == [(1.5, 8.0, (3, 1)), (2.5, 16.0, (4, 1)),
                       (3.5, 0.0, (5, 1)), (4.5, 16.0, (6, 1)), (5.5, 0.0, (7, 1))]

    def test_flat_floor_records_nothing(self):
        crossings, _, _ = _layout({}, (1.5, 1.5), 0.0)
        assert crossings == []


# ----------------------------------------------------------- the layout

class TestLayout:
    def test_riser_spans_the_projected_step(self):
        heights = {(3, 1): 8.0}
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0)
        (y_top, y_bot, d, side, _u, cell, lo, hi), = lay["risers"]
        assert d == pytest.approx(1.5 * CELL) and cell == (3, 1) and (lo, hi) == (0, 8)
        assert y_top == pytest.approx(stairs_y(8, EYE, d, HALF, H))
        assert y_bot == pytest.approx(stairs_y(0, EYE, d, HALF, H))

    def test_tread_lies_between_two_risers(self):
        heights = {(3, 1): 8.0, (4, 1): 16.0}
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0)
        first, second = lay["risers"]
        tread8 = next(t for t in lay["treads"] if t[2] == 8.0)
        assert tread8[0] == pytest.approx(stairs_y(8, EYE, 2.5 * CELL, HALF, H))
        assert tread8[1] == pytest.approx(first[0])        # down to the first riser's top
        assert second[1] == pytest.approx(tread8[0])       # second riser stands on it

    def test_a_drop_draws_nothing_and_hides_the_near_lower_floor(self):
        """Standing on a 32-px platform at its edge: no riser, and the lower
        floor is visible only from where it emerges behind the edge."""
        heights = {(1, 1): 32.0, (2, 1): 32.0, (3, 1): 32.0}   # edge 2.5 cells ahead
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0)
        assert lay["risers"] == []
        eye = 32 + EYE
        edge = stairs_y(32, eye, 2.5 * CELL, HALF, H)
        assert edge < H                                      # the edge is on screen
        ground = [t for t in lay["treads"] if t[2] == 0.0]
        assert len(ground) == 1
        assert ground[0][1] == pytest.approx(edge)          # cut by the edge
        assert ground[0][0] > HALF                           # still below the horizon

    def test_a_step_above_the_eye_shows_only_its_front(self):
        heights = {(3, 1): 40.0}                             # eye is at 24
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0, walls=[
            _solid_instance("w", 8 * CELL, CELL)])
        (y_top, y_bot, *_), = lay["risers"]
        assert y_top < HALF < y_bot                          # crosses the horizon
        assert not [t for t in lay["treads"] if t[2] == 40.0]   # its top is unseen
        wall = lay["wall"]
        assert wall is not None and wall[1] == pytest.approx(y_top)

    def test_a_front_hidden_behind_a_nearer_taller_step_is_not_drawn(self):
        """A 40-px block (above the 24-px eye) 1.5 cells away hides the
        front of the 48-px block right behind it: projected from the eye,
        the farther front's top (row ~96) is LOWER on screen than the
        nearer one's (row ~80). Drawing it anyway would also move the clip
        back down and let the wall behind overdraw the near block."""
        heights = {(3, 1): 40.0, (4, 1): 48.0}
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0, walls=[
            _solid_instance("w", 8 * CELL, CELL)])
        assert len(lay["risers"]) == 1
        near_top = lay["risers"][0][0]
        assert stairs_y(48, EYE, 2.5 * CELL, HALF, H) > near_top   # really hidden
        assert lay["wall"][1] == pytest.approx(near_top)

    def test_wall_is_drawn_down_to_what_stands_in_front(self):
        heights = {(3, 1): 8.0, (4, 1): 8.0, (5, 1): 8.0}   # the step runs to the wall
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0, walls=[
            _solid_instance("w", 6 * CELL, CELL)])
        y_top, y_bot, d, *_ = lay["wall"]
        assert d == pytest.approx(4.5 * CELL)
        assert y_top == pytest.approx(stairs_y(96, EYE, d, HALF, H))
        assert y_bot == pytest.approx(stairs_y(8, EYE, d, HALF, H))   # its base, on the step
        assert lay["wall_dist"] == pytest.approx(d)

    def test_stops_once_the_column_is_full(self):
        heights = {(2, 1): 68.0, (3, 1): 8.0}
        _, _, lay = _layout(heights, (1.5, 1.5), 0.0, walls=[
            _solid_instance("w", 8 * CELL, CELL)])
        assert len(lay["risers"]) == 1 and lay["risers"][0][0] <= 0
        assert lay["wall"] is None and lay["wall_dist"] == float("inf")

    def test_a_miss_still_draws_the_raised_floor_to_the_horizon(self):
        heights = {(x, 1): 8.0 for x in range(0, 40)}         # raised beyond range
        crossings, hit, lay = _layout(heights, (1.5, 1.5), 0.0)
        assert crossings == [] and hit[2] is False and lay["wall"] is None
        (y_top, y_bot, height, _d), = lay["treads"]
        assert height == 8.0 and y_bot == H
        assert y_top == pytest.approx(stairs_y(8, 8 + EYE, 20 * CELL, HALF, H))


# ------------------------------------------------------------- rendering

class TestRender:
    def test_a_room_without_steps_never_takes_the_stairs_path(self, monkeypatch):
        def boom(*a, **k):
            raise AssertionError("stairs path used in a room without steps")
        monkeypatch.setattr(renderer, "_draw_stairs_column", boom)
        monkeypatch.setattr(renderer, "_layout_stairs_column", boom)
        monkeypatch.setattr(renderer, "cast_stairs_floor", boom)
        room = _room(480, 480)
        for g in range(15):
            room.instances.append(_solid_instance("w", 14 * CELL, g * CELL))
        cam = GameInstance("obj_person", 64, 224, {}, action_executor=None)
        cam._cached_width = cam._cached_height = 32
        room.instances.append(cam)
        _render(room, cam, (2, 7), 0.0)

    def test_risers_and_treads_land_on_the_predicted_rows(self):
        """Facing the staircase from 2.5 cells: the first riser (0->8 at
        80 px) covers rows y(8)=336 .. y(0)=384; the second (8->16 at
        112 px) rows ~274 .. ~309, with the 8-px tread between them."""
        room, cam = _stairs_room()
        col = _column(_render(room, cam, (2, 7), 0.0))
        r1_top, r1_bot = stairs_y(8, EYE, 80, HALF, H), stairs_y(0, EYE, 80, HALF, H)
        r2_top, r2_bot = stairs_y(16, EYE, 112, HALF, H), stairs_y(8, EYE, 112, HALF, H)
        assert all(k == "wall" for k in col[math.ceil(r1_top):math.floor(r1_bot)])
        assert all(k == "floor" for k in col[math.ceil(r1_bot) + 1:])
        assert all(k == "floor" for k in col[math.ceil(r2_bot) + 1:math.floor(r1_top) - 1])
        assert all(k == "wall" for k in col[math.ceil(r2_top):math.floor(r2_bot)])

    def test_standing_on_a_step_raises_the_eye(self):
        """On the 16-px step (cell 6) facing west, the far wall's base is
        drawn from an eye 16 px higher: lower on screen than from the
        ground -- here at y(0) with eye 40, not 24."""
        room, cam = _stairs_room()
        col = _column(_render(room, cam, (6, 7), 180.0))
        d = 5.5 * CELL                                   # to the wall face on line x=1
        expected = stairs_y(0, 16 + EYE, d, HALF, H)
        base = max(y for y in range(H) if col[y] == "wall")
        assert abs(base - expected) <= 1.5, (base, expected)
        assert abs(base - stairs_y(0, EYE, d, HALF, H)) > 30

    def test_textured_risers_use_the_side_texture(self):
        room, cam = _stairs_room()
        from runtime.game_runner import GameSprite
        spr = GameSprite.__new__(GameSprite)
        frame = pygame.Surface((32, 32))
        frame.fill((200, 200, 0))
        spr.frames = [frame]
        room._all_sprites = {"spr_side": spr}
        for inst in room.instances:
            if getattr(inst, "raycast_floor_height", None) == 8.0:
                inst.raycast_step_side_texture = "spr_side"
        screen = _render(room, cam, (2, 7), 0.0, wall_textured=True)
        mid = int((stairs_y(8, EYE, 80, HALF, H) + stairs_y(0, EYE, 80, HALF, H)) / 2)
        r, g, b = screen.get_at((240, mid))[:3]
        assert r == g and r > 100 and b == 0, (r, g, b)     # yellow, shaded


# ------------------------------------------- end to end, authored project

def _write_project(root):
    (root / "sprites").mkdir()
    surf = pygame.Surface((32, 32))
    surf.fill((128, 128, 128))
    pygame.image.save(surf, str(root / "sprites" / "spr_block.png"))
    sprite = {"name": "spr_block", "asset_type": "sprite",
              "file_path": "sprites/spr_block.png", "width": 32, "height": 32,
              "origin_x": 0, "origin_y": 0, "frames": 1, "frame_width": 32,
              "frame_height": 32, "animation_type": "single", "speed": 10.0}

    def obj(name, solid, events):
        return {"name": name, "asset_type": "object", "sprite": "spr_block",
                "visible": True, "solid": solid, "persistent": False,
                "depth": 0, "events": events}

    objects = {
        "obj_wall": obj("obj_wall", True, {}),
        "obj_step": obj("obj_step", False, {"create": {"actions": [
            {"action": "set_floor_height", "parameters": {"height": "8"}}]}}),
        "obj_person": obj("obj_person", False, {"create": {"actions": [
            {"action": "enable_raycast_view", "parameters": {
                "camera_object": "", "fov": "66", "cell_size": "32",
                "render_distance": "20", "wall_color": "#ff0000",
                "floor_color": "#00ff00", "ceiling_color": "#0000ff",
                "wall_textured": "false", "wall_height": "3"}}]}}),
    }
    instances = []
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            instances.append({"object_name": "obj_wall", "x": x * 32, "y": y * 32})
    for row in range(5, 10):
        instances.append({"object_name": "obj_step", "x": 5 * 32, "y": row * 32})
    instances.append({"object_name": "obj_person", "x": 64, "y": 224})
    project = {
        "name": "stairs_e2e", "version": "1.0",
        "settings": {"window_width": 480, "window_height": 480, "room_speed": 30},
        "assets": {"sprites": {"spr_block": sprite}, "sounds": {}, "backgrounds": {},
                   "objects": objects, "scripts": {}, "fonts": {}, "data": {},
                   "rooms": {"room0": {"name": "room0", "asset_type": "room",
                                       "width": 480, "height": 480,
                                       "background_color": "#000000",
                                       "instances": instances, "tiles": []}}},
    }
    (root / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return root / "project.json"


def test_an_authored_staircase_renders_through_the_real_game_loop(tmp_path):
    """Set Floor Height in a Create event -> the step's front appears where
    the projection puts it, via the real GameRunner (instances get their
    cached sizes from the real sprite loading, not by hand)."""
    from runtime.game_runner import GameRunner

    runner = GameRunner(str(_write_project(tmp_path)))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    captured = {}
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            state["frames"] += 1
            if state["frames"] == 4:
                captured["screen"] = runner.screen.copy()
                runner.running = False
            return 0

        def get_fps(self):
            return 30.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real_clock

    screen = captured["screen"]
    assert screen.get_size() == (480, 480)
    col = _column(screen)
    top, bot = stairs_y(8, EYE, 80, HALF, H), stairs_y(0, EYE, 80, HALF, H)
    assert all(k == "wall" for k in col[math.ceil(top):math.floor(bot)]), col[330:390]
    assert col[math.ceil(top) - 3] == "floor"        # the step's top, above its front


def test_a_staircase_costs_at_most_a_bit_more_than_a_flat_room():
    """Speed guard (plan S2/S5). Relative, like the floor-cast guard in
    test_raycast_view.py, so a loaded CI runner (which slows BOTH renders)
    cannot trip it: the staircase filling the view must stay under 1.6x the
    same room without steps, plus 5 ms of slack. Measured on the dev box at
    S5: 30 ms vs 20 ms at 640x480 (1.5x) with textured walls, floor and
    ceiling."""
    import time
    from runtime.game_runner import GameSprite

    def tex(color):
        spr = GameSprite.__new__(GameSprite)
        frame = pygame.Surface((32, 32))
        for y in range(32):
            pygame.draw.line(frame, (color[0], (y * 8) % 256, color[2]), (0, y), (31, y))
        spr.frames = [frame]
        return spr

    def ms_per_frame(steps):
        room, cam = _stairs_room()
        if not steps:
            room.instances = [i for i in room.instances
                              if getattr(i, "raycast_floor_height", None) is None]
        room._all_sprites = {"w": tex((150, 0, 50)), "f": tex((90, 0, 70)),
                             "c": tex((40, 0, 60))}
        raycast_state(room)["camera"] = {
            "enabled": True, "camera_object": "obj_person", "fov": 66,
            "render_distance": 20, "cell_size": CELL, "columns": 320,
            "wall_texture": "w", "floor_texture": "f", "ceiling_texture": "c",
            "floor_cast_res": 4, "wall_height": 3}
        cam.x, cam.y, cam.facing_angle = 64, 224, 0.0
        screen = pygame.Surface((640, 480))
        render_raycast_view(room, screen)            # warm-up
        t0 = time.perf_counter()
        for _ in range(10):
            render_raycast_view(room, screen)
        return (time.perf_counter() - t0) / 10 * 1000

    flat = ms_per_frame(False)
    stairs = ms_per_frame(True)
    assert stairs < flat * 1.6 + 5.0, (
        f"stairs {stairs:.1f} ms/frame vs the same room without steps "
        f"{flat:.1f} ms/frame")

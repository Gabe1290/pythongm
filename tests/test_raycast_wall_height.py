"""wall_height: taller walls and ceiling for the raycast view (stairs S4).

docs/RAYCAST_STAIRS_PLAN.md: stairs need headroom. At the default wall height
(1.5 cells) the ceiling is only 0.75 cell above the eye, so three 8-px steps
would put the eye at the ceiling. Enable Raycast View gains an optional
`wall_height` (cells, default 1.5). The eye stays RAYCAST_EYE_HEIGHT (0.75
cell) above the floor, so the horizon and the wall BASES do not move; walls
grow upward, the ceiling plane rises with them, and a wall texture REPEATS
every RAYCAST_TEXTURE_HEIGHT (1.5 cells) instead of stretching, so bricks keep
their size.

The default renders byte-identical to the pre-S4 renderer: proven against a
snapshot of the previous HEAD in the commit (desktop: 768 frames; Kivy: 150
frames instruction for instruction). These tests pin the new behaviour by
checking WHERE things land against the projection formulas.
"""
import math
import os
import re
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

from runtime.game_runner import GameInstance, GameSprite  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    render_raycast_view, cast_floor_plane, clamp_wall_height,
    RAYCAST_WALL_HEIGHT, RAYCAST_EYE_HEIGHT, RAYCAST_TEXTURE_HEIGHT,
    RAYCAST_MIN_WALL_HEIGHT, RAYCAST_MAX_WALL_HEIGHT,
)
from test_raycast_view import (  # noqa: E402
    _room, _solid_instance, _raycast_executor, _dispatch,
)
from events.action_types import get_action_type  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()

CELL = 32
W = H = 480
HALF = H / 2
# Camera centred in cell (1, 7) facing east; a full-block wall column at
# gx = 7 puts the wall's west face on grid line 7: 5.5 cells away.
CAM_CELL = (1, 7)
DIST_CELLS = 7 - (CAM_CELL[0] + 0.5)


def _vertical_gradient_sprite():
    """32x32 texture whose ROW r is (r*8, 0, 0): a texel's row is readable."""
    spr = GameSprite.__new__(GameSprite)
    frame = pygame.Surface((32, 32))
    for r in range(32):
        pygame.draw.line(frame, (r * 8, 0, 0), (0, r), (31, r))
    spr.frames = [frame]
    return spr


def _render(**extra):
    room = _room(W, H)
    for gy in range(15):
        room.instances.append(_solid_instance("w", 7 * CELL, gy * CELL))
    cam = GameInstance("obj_person", CAM_CELL[0] * CELL, CAM_CELL[1] * CELL, {},
                       action_executor=None)
    cam._cached_width = cam._cached_height = 32
    cam.facing_angle = 0.0
    room.instances.append(cam)
    room._all_sprites = {"spr_grad": _vertical_gradient_sprite()}
    room._all_sprites.update(extra.pop("_sprites", {}))
    cfg = {'enabled': True, 'camera_object': 'obj_person', 'fov': 66,
           'render_distance': 20, 'cell_size': CELL, 'columns': 320,
           'wall_color': '#ff0000', 'floor_color': '#00ff00',
           'ceiling_color': '#0000ff'}
    cfg.update(extra)
    raycast_state(room)["camera"] = cfg
    screen = pygame.Surface((W, H))
    render_raycast_view(room, screen)
    return screen


def _wall_rows(screen, x=W // 2):
    """First and last row of the centre column that is wall (neither the flat
    ceiling blue nor the flat floor green)."""
    rows = [y for y in range(H)
            if screen.get_at((x, y))[:3] not in ((0, 0, 255), (0, 255, 0))]
    return rows[0], rows[-1]


def _expected_rows(wall_height):
    px = H / DIST_CELLS                    # screen px per world cell at that distance
    top = HALF - (wall_height - RAYCAST_EYE_HEIGHT) * px
    bottom = HALF + RAYCAST_EYE_HEIGHT * px
    return top, bottom


# ---------------------------------------------------------------- geometry

class TestWallGeometry:
    @pytest.mark.parametrize("wall_height", [1.5, 2.25, 3.0])
    def test_wall_rises_from_a_fixed_base(self, wall_height):
        top, bottom = _expected_rows(wall_height)
        y_first, y_last = _wall_rows(_render(wall_height=wall_height))
        assert abs(y_first - top) <= 1.5, (y_first, top)
        assert abs(y_last - bottom) <= 1.5, (y_last, bottom)

    def test_the_base_and_horizon_do_not_move(self):
        _, base_default = _wall_rows(_render())
        _, base_tall = _wall_rows(_render(wall_height=3))
        assert base_default == base_tall

    def test_default_is_today(self):
        assert RAYCAST_WALL_HEIGHT == 1.5
        assert RAYCAST_EYE_HEIGHT == RAYCAST_WALL_HEIGHT / 2
        assert _wall_rows(_render()) == _wall_rows(_render(wall_height=1.5))


class TestTextureRepeats:
    def test_texture_repeats_per_tile_instead_of_stretching(self):
        """With wall_height 3 the wall is two tiles. A row in the lower tile
        and the row exactly one tile above it sample the SAME texel row; a
        stretched texture would sample rows ~16 apart."""
        screen = _render(wall_height=3, wall_texture="spr_grad")
        tile_px = RAYCAST_TEXTURE_HEIGHT * H / DIST_CELLS
        y_low = 230
        y_high = round(y_low - tile_px)
        low = screen.get_at((W // 2, y_low))[0]
        high = screen.get_at((W // 2, y_high))[0]
        assert low > 0 and abs(low - high) <= 8, (low, high)

    def test_texture_is_anchored_at_the_floor(self):
        """The bottom tile of a tall wall looks exactly like a default wall."""
        default = _render(wall_texture="spr_grad")
        tall = _render(wall_height=3, wall_texture="spr_grad")
        _, base = _expected_rows(1.5)
        top, _ = _expected_rows(1.5)
        for y in range(int(top) + 2, int(base) - 1, 7):
            assert default.get_at((W // 2, y)) == tall.get_at((W // 2, y)), y

    def test_a_partial_top_tile_shows_the_texture_s_lower_part(self):
        """wall_height 2.25 = one and a half tiles: just below the wall's top
        the texture shows its MIDDLE row (the top tile is cut in half), i.e.
        what the full bottom tile shows half a tile below its own top -- not
        texture row 0. (Compared within one column, so the distance shading,
        the same for the whole strip, cancels out.)"""
        screen = _render(wall_height=2.25, wall_texture="spr_grad")
        top, _ = _expected_rows(2.25)
        tile_px = RAYCAST_TEXTURE_HEIGHT * H / DIST_CELLS
        y_tile0 = top + 0.5 * tile_px              # top of the bottom tile
        just_below_top = screen.get_at((W // 2, int(math.ceil(top)) + 1))[0]
        bottom_tile_mid = screen.get_at((W // 2, int(math.ceil(y_tile0 + 0.5 * tile_px)) + 1))[0]
        bottom_tile_row0 = screen.get_at((W // 2, int(math.ceil(y_tile0)) + 1))[0]
        assert just_below_top == bottom_tile_mid
        assert just_below_top > bottom_tile_row0 + 50


class TestCeilingFollowsTheWalls:
    @pytest.mark.parametrize("distance", (5.5, 7.5))
    def test_ceiling_meets_the_raised_wall_top(self, distance):
        """Same check as the S1 floor test, for a raised ceiling plane: one
        row above a wall's top, the cast ceiling point is where the wall pass
        puts it (just short of the wall's line)."""
        wall_height = 3.0
        plane = wall_height - RAYCAST_EYE_HEIGHT
        tex = pygame.Surface((64, 1))
        for tx in range(64):
            tex.set_at((tx, 0), (tx * 4, 0, 0))
        screen = pygame.Surface((W, H))
        cast_floor_plane(screen, tex, 3.5, 3.5, 0.0, math.radians(66), 1,
                         ceiling=True, view_h=H, plane_height=plane)
        top_off = plane * H / distance
        j = math.ceil(top_off) + 1
        frac = (screen.get_at((W // 2, H // 2 - 1 - j))[0] // 4) / 64
        expected = 3.5 + distance * top_off / j
        assert abs(frac - (expected - math.floor(expected))) <= 1.5 / 64

    def test_the_renderer_raises_the_ceiling_plane(self):
        """Through the real render: with wall_height 3 the ceiling above the
        walls is the plane cast at (3 - eye) cells, not at the eye height."""
        tex = pygame.Surface((64, 1))
        for tx in range(64):
            tex.set_at((tx, 0), (tx * 4, 0, 0))
        spr = GameSprite.__new__(GameSprite)
        spr.frames = [tex]
        rendered = _render(wall_height=3, ceiling_texture="spr_ceil",
                           _sprites={"spr_ceil": spr})
        cam_c = (CAM_CELL[0] + 0.5, CAM_CELL[1] + 0.5)
        for plane, should_match in ((3 - RAYCAST_EYE_HEIGHT, True),
                                    (RAYCAST_EYE_HEIGHT, False)):
            direct = pygame.Surface((W, H))
            cast_floor_plane(direct, tex, cam_c[0], cam_c[1], 0.0, math.radians(66), 4,
                             ceiling=True, view_h=H, plane_height=plane)
            row = [rendered.get_at((x, 10)) == direct.get_at((x, 10)) for x in range(0, W, 16)]
            assert all(row) is should_match, (plane, row)

    def test_default_plane_height_is_the_eye_height(self):
        tex = pygame.Surface((64, 1))
        for tx in range(64):
            tex.set_at((tx, 0), (tx * 4, 0, 0))
        a, b = pygame.Surface((W, H)), pygame.Surface((W, H))
        cast_floor_plane(a, tex, 3.5, 3.5, 0.3, math.radians(66), 2, view_h=H)
        cast_floor_plane(b, tex, 3.5, 3.5, 0.3, math.radians(66), 2, view_h=H,
                         plane_height=RAYCAST_EYE_HEIGHT)
        assert pygame.image.tobytes(a, "RGB") == pygame.image.tobytes(b, "RGB")


class TestClamp:
    def test_default_garbage_and_range(self):
        assert clamp_wall_height(None) == RAYCAST_WALL_HEIGHT
        assert clamp_wall_height("tall") == RAYCAST_WALL_HEIGHT
        assert clamp_wall_height(float("nan")) == RAYCAST_WALL_HEIGHT
        assert clamp_wall_height("3") == 3.0
        assert clamp_wall_height(0.2) == RAYCAST_MIN_WALL_HEIGHT
        assert clamp_wall_height(500) == RAYCAST_MAX_WALL_HEIGHT
        assert RAYCAST_MIN_WALL_HEIGHT > RAYCAST_EYE_HEIGHT   # ceiling clears the eye

    def test_out_of_range_renders_clamped(self):
        assert _wall_rows(_render(wall_height=0.1)) == _wall_rows(_render(wall_height=1.0))


# ------------------------------------------------------- action + handler

class TestAction:
    def test_parameter_registered(self):
        at = get_action_type("enable_raycast_view")
        p = next(p for p in at.parameters if p.name == "wall_height")
        assert p.param_type == "number" and p.default_value == 1.5
        assert p.required is False

    def test_handler_stores_it(self):
        class _Room:
            pass

        class _Runner:
            current_room = _Room()
            global_variables = {}

        ex = _raycast_executor(game_runner=_Runner())
        cam = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        _dispatch(ex, "enable_raycast_view", cam, {"enable": True, "wall_height": "3"})
        assert raycast_state(_Runner.current_room)["camera"]["wall_height"] == 3.0
        _dispatch(ex, "enable_raycast_view", cam, {"enable": True})
        assert raycast_state(_Runner.current_room)["camera"]["wall_height"] == 1.5


# ------------------------------------------------------------------ HTML5

JS = (REPO_ROOT / "extensions" / "raycast_2_5d" / "export_html5.js").read_text(encoding="utf-8")
KIVY_SRC = (REPO_ROOT / "extensions" / "raycast_2_5d" / "export_kivy.py").read_text(encoding="utf-8")


class TestHtml5:
    """No JS engine in CI: pin the port's structure against the desktop."""

    def test_same_constants(self):
        for name, value in (("RAYCAST_EYE_HEIGHT", RAYCAST_EYE_HEIGHT),
                            ("RAYCAST_TEXTURE_HEIGHT", RAYCAST_TEXTURE_HEIGHT),
                            ("RAYCAST_MIN_WALL_HEIGHT", RAYCAST_MIN_WALL_HEIGHT),
                            ("RAYCAST_MAX_WALL_HEIGHT", RAYCAST_MAX_WALL_HEIGHT)):
            m = re.search(r"const %s = ([0-9.]+);" % name, JS)
            assert m and float(m.group(1)) == value, name

    def test_walls_tile_and_rise(self):
        assert "const wallH = raycastClampWallHeight(cfg.wall_height);" in JS
        assert "const yWallTop = yTile0 - (wallTiles - 1) * tileH;" in JS
        assert "for (let k = 0; k < nTiles; k++) {" in JS
        assert "const segTop = yTile0 - k * tileH;" in JS

    def test_ceiling_plane_and_action(self):
        assert "res, ceiling, viewH, planeHeight) {" in JS
        assert "const posZ = planeHeight * viewH;" in JS
        assert "wallH - RAYCAST_EYE_HEIGHT);" in JS
        assert "wall_height: rNum('wall_height', 1.5)," in JS


# ------------------------------------------------------------------- Kivy

class TestKivy:
    def test_same_constants(self):
        for name, value in (("RAYCAST_EYE_HEIGHT", RAYCAST_EYE_HEIGHT),
                            ("RAYCAST_TEXTURE_HEIGHT", RAYCAST_TEXTURE_HEIGHT),
                            ("RAYCAST_MIN_WALL_HEIGHT", RAYCAST_MIN_WALL_HEIGHT),
                            ("RAYCAST_MAX_WALL_HEIGHT", RAYCAST_MAX_WALL_HEIGHT)):
            m = re.search(r"\n    %s = ([0-9.]+)\n" % name, KIVY_SRC)
            assert m and float(m.group(1)) == value, name

    def test_codegen_carries_wall_height(self):
        from extensions.raycast_2_5d.export_kivy import _cg_enable_raycast_view
        code = _cg_enable_raycast_view(None, {"wall_height": "3"}, "create")
        assert "'wall_height': 3.0" in code
        code = _cg_enable_raycast_view(None, {}, "create")
        assert "'wall_height': 1.5" in code

    def test_tall_wall_is_drawn_as_stacked_tiles(self):
        """wall_height 2.25 (1.5 tiles): every wall column draws a full bottom
        tile (v 0..1) and, directly above it, half a tile (v 0..0.5)."""
        from test_kivy_raycast import (
            _stub_kivy_env, _scene_class, _blank_scene, _FakeInst, _FakeTex,
            _export_raycast_1,
        )
        game = _export_raycast_1()
        with _stub_kivy_env(game):
            scene = _blank_scene(_scene_class(game))
            scene.room_width = scene.room_height = 320
            insts = [_FakeInst(9 * 32, gy * 32, 32, 32, solid=True) for gy in range(10)]
            cam = _FakeInst(32, 4 * 32, 32, 32, solid=False)
            insts.append(cam)
            scene.instances = insts
            scene._raycast_tex_cache = {"spr_wall": _FakeTex(32, 32)}
            scene.raycast_camera = {
                "enabled": True, "cell_size": 32, "fov": 66, "render_distance": 20,
                "columns": 40, "camera_instance": cam, "wall_texture": "spr_wall",
                "wall_height": 2.25}
            scene._render_raycast()
            rects = [c for c in scene._raycast_group.children
                     if getattr(c, "kw", None) and "tex_coords" in c.kw]
        by_x = {}
        for r in rects:
            by_x.setdefault(r.kw["pos"][0], []).append(r.kw)
        # the outermost rays pass beyond the single wall column; the rest hit
        assert len(by_x) >= 36
        for x, (bottom, top) in by_x.items():
            assert abs(bottom["tex_coords"][1]) < 1e-9
            assert abs(bottom["tex_coords"][5] - 1.0) < 1e-9
            assert abs(top["tex_coords"][1]) < 1e-9
            assert abs(top["tex_coords"][5] - 0.5) < 1e-9
            # stacked: the top tile starts where the bottom one ends
            assert abs(top["pos"][1] - (bottom["pos"][1] + bottom["size"][1])) < 1e-9
            assert abs(top["size"][1] - bottom["size"][1] / 2) < 1e-9

"""set_floor_texture in the Kivy (Android/iOS) export: ground-level floor patches (2026-11-23).

Codegen runs everywhere; the stub-kivy harness drives the REAL generated scene code: its patch
map equals heights.build_floor_textures, and its floor buffers (flat room, and the column walk of
a room with steps) equal the desktop casts sample for sample, with textures whose rows differ so a
wrong flip shows.
"""
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling test import

from test_kivy_raycast import _stub_kivy_env, _scene_class, _FakeInst, _export_raycast_1  # noqa: E402
from test_kivy_raycast_stairs import _stairs_scene  # noqa: E402

pygame = pytest.importorskip("pygame")
pygame.init()

KIVY_SRC = (ROOT / "extensions" / "raycast_2_5d" / "export_kivy.py").read_text(encoding="utf-8")
RES = 4
FACING = 0.3
FOV = math.radians(66)


def test_codegen_for_the_action():
    from extensions.raycast_2_5d.export_kivy import _cg_set_floor_texture, ACTION_CODEGEN
    assert ACTION_CODEGEN["set_floor_texture"] is _cg_set_floor_texture
    assert _cg_set_floor_texture(None, {"texture": "spr_rug"}, "create") == \
        "self.raycast_floor_texture = 'spr_rug'"
    assert _cg_set_floor_texture(None, {}, "create") == "self.raycast_floor_texture = ''"


def test_floor_patches_are_not_billboards_or_movers_in_kivy():
    body = KIVY_SRC[KIVY_SRC.index("        billboards = []"):]
    assert "if getattr(inst, 'raycast_floor_texture', None) is not None:" in body[:1800]
    assert "and getattr(i, 'raycast_floor_texture', None) is None]" in KIVY_SRC


@pytest.fixture(scope="module")
def exported():
    return _export_raycast_1()


def _texture(seed):
    """An 8x8 texture whose every texel differs (so a flipped or shifted sample shows)."""
    surf = pygame.Surface((8, 8))
    for y in range(8):
        for x in range(8):
            surf.set_at((x, y), ((seed + x * 30) % 256, (y * 30) % 256, (seed * 7 + x * y) % 256))
    return surf


def _kivy_px(surf):
    return (pygame.image.tobytes(surf, "RGBA", True), surf.get_width(), surf.get_height())


def _buffer_px(buf, sw, i, j):
    di = (j * sw + i) * 4
    return tuple(buf[di:di + 3])


def test_the_patch_map_equals_desktop(exported):
    from runtime.game_runner import GameRoom, GameInstance
    from extensions.raycast_2_5d.heights import build_floor_textures
    patches = [(64, 224, 96, 32, "spr_rug"), (96, 224, 32, 64, "spr_tile"),
               (0, 0, 32, 32, ""), (200, 300, 40, 20, "spr_rug")]
    room = GameRoom("r", {"width": 480, "height": 480}, action_executor=None)
    for x, y, w, h, tex in patches:
        inst = GameInstance("obj_rug", x, y, {}, action_executor=None)
        inst._cached_object_data = {"solid": False}
        inst._cached_width, inst._cached_height = w, h
        inst.raycast_floor_texture = tex
        room.instances.append(inst)
    want = build_floor_textures(room, 32)
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), {})
        scene.instances = []
        for x, y, w, h, tex in patches:
            inst = _FakeInst(x, 480 - y - h, w, h, solid=False)    # Kivy is y-up
            inst.raycast_floor_texture = tex
            scene.instances.append(inst)
        got = scene._raycast_build_floor_textures(32)
    assert got == want and want


def test_the_flat_floor_buffer_equals_desktop(exported):
    from extensions.raycast_2_5d.renderer import _cast_floor_cells
    floor_tex, rug = _texture(10), _texture(120)
    cells = {(4, 7): rug, (5, 7): rug, (5, 8): rug, (6, 6): rug}
    for floor_frame in (floor_tex, None):
        screen = pygame.Surface((480, 480))
        _cast_floor_cells(screen, floor_frame, 2.5, 7.5, FACING, FOV, RES, 480, None,
                          cells, (0, 255, 0))
        with _stub_kivy_env(exported):
            scene, _ = _stairs_scene(_scene_class(exported), {})
            buf, sw, sh = scene._floor_cells_buffer(
                {k: _kivy_px(v) for k, v in cells.items()},
                _kivy_px(floor_frame) if floor_frame is not None else None,
                (0.0, 1.0, 0.0), RES, FACING, FOV, 2.5, 7.5, 480.0)
        assert (sw, sh) == (120, 60)
        seen_rug = 0
        for j in range(sh):
            for i in range(sw):
                want = tuple(screen.get_at((i * RES, 240 + j * RES)))[:3]
                assert _buffer_px(buf, sw, i, j) == want, (floor_frame is None, i, j)
                seen_rug += want[0] >= 120 and want[0] < 120 + 8 * 30
        assert seen_rug


def test_the_stairs_floor_buffer_takes_the_patch_on_ground_cells(exported):
    from extensions.raycast_2_5d.renderer import cast_stairs_floor
    floor_tex, rug, top = _texture(10), _texture(120), _texture(200)
    ground = {(4, 7): rug, (5, 7): rug, (6, 6): rug, (6, 7): rug}
    tops = {(6, 7): top}               # a step over a patched cell keeps its own top
    # Every column: ground up to row 300, then a tread at height 8 (the column walk's spans,
    # near -> far = bottom -> top).
    layouts = [{"treads": [(300.0, 480.0, 0.0, 0.0), (241.0, 300.0, 8.0, 0.0)]} for _ in range(120)]
    sf_py = {"view_h": 480, "cell_size": 32, "eye_z": 24.0, "cam_x": 80.0, "cam_y": 240.0,
             "floor_color": (0, 255, 0), "col_width": 4.0}
    screen = pygame.Surface((480, 480))
    cast_stairs_floor(screen, layouts, sf_py, floor_tex, tops, FACING, FOV, RES,
                      ground_frames=ground)
    with _stub_kivy_env(exported):
        scene, _ = _stairs_scene(_scene_class(exported), {})
        sf = dict(sf_py, w=480.0, floor_color=(0.0, 1.0, 0.0),
                  ground_px={k: _kivy_px(v) for k, v in ground.items()})
        buf, sw, sh = scene._stairs_floor_buffer(
            layouts, sf, _kivy_px(floor_tex), {k: _kivy_px(v) for k, v in tops.items()},
            FACING, FOV, RES)
    seen = set()
    for j in range(sh):
        for i in range(sw):
            want = tuple(screen.get_at((i * RES, 240 + j * RES)))[:3]
            assert _buffer_px(buf, sw, i, j) == want, (i, j)
            seen.add(want[0] // 100)
    assert {0, 1} <= seen            # both the floor texture and the patch were sampled

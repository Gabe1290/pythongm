"""Stage P / K3: the micro:bit board drawn on the Kivy export.

The board is built as draw-queue commands (``export/kivy_draw.py``, shipped as
``microbit_sim/draw.py``). The commands are rasterised with pygame here and
compared, pixel by pixel at the interesting points, with what the desktop
renderer (``renderer.py``) paints for the same simulator state -- so the Kivy
board cannot drift from the pygame one. The generated object's ``_mb_draw`` is
driven under the K1 stub-kivy harness for placement, y-flip, visibility and
options.
"""
import importlib
import sys
from pathlib import Path

import pygame
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_actions import _stub_kivy, _export  # noqa: E402

from extensions.microbit import renderer  # noqa: E402
from extensions.microbit import kivy_draw  # noqa: E402
from extensions.microbit.layout import board_layout, strip_layout  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator  # noqa: E402

SIZE = (900, 500)


def _sim(**state):
    sim = MicrobitSimulator()
    for key, value in state.items():
        getattr(sim, key)(*value) if isinstance(value, tuple) else getattr(sim, key)(value)
    return sim


STATES = {
    "idle": lambda s: None,
    "lit": lambda s: (s.set_pixel(2, 2, 9), s.set_pixel(0, 0, 4), s.set_brightness(120)),
    "button_a": lambda s: s.set_button("a", True),
    "button_b": lambda s: s.set_button("b", True),
    "logo": lambda s: s.set_logo_touched(True),
    "pin1": lambda s: s.set_pin_touched(1, True),
    "tone": lambda s: (s.play_tone(440, 1000), s.update(0.05)),
    "tilt": lambda s: s.set_acceleration(500, -300, -800),
    "shake": lambda s: (s.shake(), s.update(0.05)),
    "sliders": lambda s: (s.set_light_level(200), s.set_temperature(30),
                          s.set_compass_heading(90), s.set_sound_level(10)),
}


def _surface():
    pygame.init()
    surf = pygame.Surface(SIZE)
    surf.fill((250, 0, 250))
    return surf


def _raster(surf, commands):
    """A minimal interpreter of the command types kivy_draw emits (text is
    skipped: it is the exported game's own font)."""
    for c in commands:
        color = tuple(c["color"])
        t = c["type"]
        if t == "rectangle":
            rect = (c["x1"], c["y1"], c["x2"] - c["x1"], c["y2"] - c["y1"])
            pygame.draw.rect(surf, color, rect, 0 if c["filled"] else 1, border_radius=int(c.get("radius", 0)))
        elif t == "polygon":
            pygame.draw.polygon(surf, color, [tuple(pt) for pt in c["points"]])
        elif t == "circle":
            pygame.draw.circle(surf, color, (c["x"], c["y"]), c["radius"], 0 if c["filled"] else 1)
        elif t == "ellipse":
            pygame.draw.ellipse(surf, color, (c["x1"], c["y1"], c["x2"] - c["x1"], c["y2"] - c["y1"]))
        elif t == "line":
            pygame.draw.line(surf, color, (c["x1"], c["y1"]), (c["x2"], c["y2"]))


def _points(layout):
    strip = strip_layout(layout)
    bx, by, bw, bh = layout.body
    pts = {"body": (bx + 4, by + bh // 2)}
    for y in range(5):
        for x in range(5):
            pts["led%d%d" % (x, y)] = layout.led_center(x, y)
    for name, (cx, cy, r) in layout.buttons.items():
        pts["button_" + name] = (cx + int(r * 0.45), cy + int(r * 0.45))
    pts["speaker"] = layout.speaker[:2]
    pts["logo"] = layout.logo[:2]
    for name in ("0", "1", "2"):
        x, y, w, h = layout.pads[name]
        pts["pad" + name] = (x + 4, y + h - 5)
    tx, ty, tw, th = strip.tilt
    pts["tilt_well"] = (tx + 4, ty + th - 5)
    sx, sy, sw, sh = strip.shake
    pts["shake"] = (sx + 3, sy + 3)
    pts["panel_left"] = (strip.panel_left[0] + 3, strip.panel_left[1] + 3)
    pts["panel_right"] = (strip.panel_right[0] + 3, strip.panel_right[1] + 3)
    for name, (kx, ky, kw, kh) in strip.sliders.items():
        pts["track_" + name] = (kx + kw - 3, ky + kh // 2)
        pts["fill_" + name] = (kx + 3, ky + kh // 2)
        pts["track_corner_" + name] = (kx, ky)                       # outside a rounded end
    # the silkscreen wedge: a point well inside it, and one well below it (plain body)
    pts["wedge"] = (bx + int(bw * 0.10), by + int(bh * 0.04))
    pts["wedge_outside"] = (bx + int(bw * 0.02), by + int(bh * 0.50))      # well below the wedge, left of button A: plain body
    # the A tag hangs below button A, the B tag sits above button B: a point inside each
    ax, ay, ar = layout.buttons["a"]
    bxx, byy, br2 = layout.buttons["b"]
    sc = layout.scale
    tw, th = max(6, int(20 * sc)), max(6, int(18 * sc))
    gap = max(2, int(4 * sc))
    pts["tag_a"] = (ax - tw // 2 + tw - 2, ay + ar + gap + th - 2)      # next to its right angle, clear of the letter
    pts["tag_b"] = (bxx - tw // 2 + tw - 4, byy - br2 - gap - th + 1)    # along its top edge, clear of the letter
    # rounded corners: the outer corner pixel of a panel, a pad and the shake button
    pts["panel_corner"] = strip.panel_left[:2]
    pts["pad_corner"] = layout.pads["1"][:2]
    pts["shake_corner"] = strip.shake[:2]
    return pts


@pytest.mark.parametrize("scale", [1.0, 0.6])
@pytest.mark.parametrize("state", sorted(STATES))
def test_the_commands_paint_what_the_pygame_renderer_paints(state, scale):
    sim = MicrobitSimulator()
    STATES[state](sim)
    layout = board_layout(450, 250, scale)
    want, got = _surface(), _surface()
    renderer.draw_board(want, layout, sim)
    renderer.draw_strip(want, strip_layout(layout), sim, layout.scale)
    _raster(got, kivy_draw.board_commands(layout, sim) + kivy_draw.strip_commands(layout, sim))
    bad = {name: (tuple(got.get_at(p)), tuple(want.get_at(p)))
           for name, p in _points(layout).items() if got.get_at(p) != want.get_at(p)}
    assert not bad, bad


def test_a_board_with_its_own_sprite_draws_no_body():
    sim = MicrobitSimulator()
    layout = board_layout(450, 250)
    got = _surface()
    _raster(got, kivy_draw.board_commands(layout, sim, draw_body=False))
    assert tuple(got.get_at(_points(layout)["body"]))[:3] == (250, 0, 250)
    assert not [c for c in kivy_draw.board_commands(layout, sim, draw_body=False)
                if c["type"] == "rectangle" and c["color"] == kivy_draw.BODY_COLOR]


def test_only_command_types_the_exported_renderer_understands_are_emitted():
    layout = board_layout(450, 250)
    sim = MicrobitSimulator()
    types = {c["type"] for c in kivy_draw.board_commands(layout, sim) + kivy_draw.strip_commands(layout, sim)}
    assert types <= {"rectangle", "circle", "ellipse", "line", "scaled_text", "polygon"}
    anchors = {c.get("anchor") for c in kivy_draw.board_commands(layout, sim)
               + kivy_draw.strip_commands(layout, sim) if c["type"] == "scaled_text"}
    assert anchors <= {"topleft", "center", "midbottom", "bottomleft"}


def test_colour_constants_match_renderer_py():
    for name in dir(kivy_draw):
        if name.isupper() and isinstance(getattr(kivy_draw, name), tuple):
            assert getattr(kivy_draw, name) == getattr(renderer, name), name
    assert kivy_draw.SLIDER_TITLES == renderer.SLIDER_TITLES


def test_the_shipped_layout_is_byte_identical_and_state_is_the_stub():
    game = _export({})
    pkg = game / "microbit_sim"
    assert (pkg / "layout.py").read_bytes() == (ROOT / "extensions/microbit/layout.py").read_bytes()
    assert (pkg / "draw.py").read_bytes() == (ROOT / "extensions/microbit/kivy_draw.py").read_bytes()
    assert "option_of" in (pkg / "state.py").read_text(encoding="utf-8")
    assert "import pygame" not in (pkg / "draw.py").read_text(encoding="utf-8")


def test_the_exported_text_renderer_knows_every_anchor():
    text = (ROOT / "export/Kivy/kivy_exporter.py").read_text(encoding="utf-8")
    for anchor in ("center", "midbottom", "bottomleft"):
        assert "anchor == '%s'" % anchor in text, anchor


# -- the generated object (stub kivy) -----------------------------------------

class _Group:
    def __init__(self):
        self.cleared = 0

    def clear(self):
        self.cleared += 1


class _Canvas:
    class after:
        added = []

        @classmethod
        def add(cls, item):
            cls.added.append(item)


def _board(**attrs):
    mod = importlib.import_module("objects.microbit_1")
    base = sys.modules["objects.base_object"]
    base.InstructionGroup = _Group
    inst = mod.Microbit1.__new__(mod.Microbit1)
    inst.object_name = "microbit_1"
    inst.canvas = type("C", (), {"after": type("A", (), {"items": [], "add": lambda s, g: s.items.append(g)})()})()
    inst.visible = True
    inst.has_sprite = False
    inst.x, inst.y, inst.width, inst.height = 100, 150, 32, 32
    for key, value in attrs.items():
        setattr(inst, key, value)
    rendered = []
    inst._dq_render_cmd = lambda group, cmd, room_h: rendered.append((group, cmd, room_h))
    return inst, rendered


def _centre_of(rendered):
    """The board's body rectangle -> its centre."""
    body = next(c for _, c, _ in rendered if c["type"] == "rectangle"
                and c["color"] == kivy_draw.BODY_COLOR and c["filled"])
    return (body["x1"] + body["x2"]) / 2.0, (body["y1"] + body["y2"]) / 2.0


def test_a_spriteless_board_is_centred_on_its_game_maker_point_and_flipped_to_y_down():
    game = _export({})
    with _stub_kivy(game):
        inst, rendered = _board()
        inst._mb_draw(480)
    # Kivy pos (100, 150), 32 high, room 480: GM point (100, 480 - 150 - 32 = 298)
    assert _centre_of(rendered) == pytest.approx((100, 298), abs=1)
    assert all(room_h == 480 for _, _, room_h in rendered)


def test_a_sprited_board_is_centred_on_its_sprite_and_draws_no_body():
    game = _export({})
    with _stub_kivy(game):
        inst, rendered = _board(has_sprite=True, width=64, height=48)
        inst._mb_draw(480)
    assert not [1 for _, c, _ in rendered if c["type"] == "rectangle"
                and c["color"] == kivy_draw.BODY_COLOR]
    led = next(c for _, c, _ in rendered if c["type"] == "rectangle"
               and c["color"] == kivy_draw.LED_WELL)
    layout = board_layout(100 + 32, 480 - 150 - 24)
    cx, cy = layout.led_center(0, 0)
    half = layout.led_size // 2
    assert (led["x1"], led["y1"]) == (cx - half - 1, cy - half - 1)


def test_the_group_is_created_once_attached_to_the_canvas_and_rebuilt_each_frame():
    game = _export({})
    with _stub_kivy(game):
        inst, rendered = _board()
        inst._mb_draw(480)
        inst._mb_draw(480)
    assert len(inst.canvas.after.items) == 1
    assert inst._mb_group.cleared == 2
    assert len({id(g) for g, _, _ in rendered}) == 1


def test_an_invisible_board_draws_nothing_and_clears_what_it_drew():
    game = _export({})
    with _stub_kivy(game):
        inst, rendered = _board()
        inst._mb_draw(480)
        drawn = len(rendered)
        inst.visible = False
        inst._mb_draw(480)
    assert drawn and len(rendered) == drawn
    assert inst._mb_group.cleared == 2


def test_the_strip_follows_microbit_show_sensors_and_scale_follows_microbit_scale():
    game = _export({})
    with _stub_kivy(game):
        inst, with_strip = _board()
        inst._mb_draw(480)
        small, without = _board(microbit_show_sensors=False, microbit_scale=0.5)
        small._mb_draw(480)
    has_panel = lambda cmds: any(c["color"] == kivy_draw.PANEL_COLOR for _, c, _ in cmds)  # noqa: E731
    assert has_panel(with_strip) and not has_panel(without)
    wide = lambda cmds: (lambda b: b["x2"] - b["x1"])(next(  # noqa: E731
        c for _, c, _ in cmds if c["type"] == "rectangle" and c["color"] == kivy_draw.BODY_COLOR and c["filled"]))
    assert wide(without) == pytest.approx(wide(with_strip) / 2, abs=1)


def test_a_non_board_object_draws_nothing():
    game = _export({})
    with _stub_kivy(game):
        inst, rendered = _board(object_name="wall")
        inst._mb_draw(480)
    assert rendered == [] and getattr(inst, "_mb_group", None) is None


def test_the_scene_draws_every_board_each_frame():
    game = _export({})
    with _stub_kivy(game):
        scene_mod = importlib.import_module("scenes.room0")
        scene = scene_mod.Room0.__new__(scene_mod.Room0)
        inst, rendered = _board()
        scene.instances = [inst]
        scene.room_height = 480
        scene._update_extensions(1 / 60)
    assert rendered


def test_the_tilt_dot_sits_where_the_pygame_strip_puts_it():
    from extensions.microbit.layout import tilt_to_pos
    sim = MicrobitSimulator()
    sim.set_acceleration(500, -300, -800)
    layout = board_layout(450, 250)
    want = tilt_to_pos(strip_layout(layout).tilt, 500, -300)
    dots = [c for c in kivy_draw.strip_commands(layout, sim)
            if c["type"] == "circle" and c["color"] == kivy_draw.PAD_DOT]
    assert [(c["x"], c["y"]) for c in dots] == [want]


def test_each_label_is_anchored_where_the_pygame_label_is_placed():
    layout = board_layout(450, 250)
    sim = MicrobitSimulator()
    strip = strip_layout(layout)
    labels = [c for c in kivy_draw.board_commands(layout, sim) + kivy_draw.strip_commands(layout, sim)
              if c["type"] == "scaled_text"]
    texts = {c["text"]: c for c in labels if not (c["text"] in ("A", "B") and c["color"] == kivy_draw.TAG_LABEL)}
    ax, ay, _ = layout.buttons["a"]
    assert (texts["A"]["anchor"], texts["A"]["x"], texts["A"]["y"]) == ("center", ax, ay)
    tags = [c for c in labels if c["color"] == kivy_draw.TAG_LABEL]
    assert sorted(c["text"] for c in tags) == ["A", "B"] and all(c["anchor"] == "center" for c in tags)
    px, py, pw, _ = layout.pads["1"]
    assert (texts["1"]["anchor"], texts["1"]["x"], texts["1"]["y"]) == ("midbottom", px + pw // 2, py - 2)
    sx, sy, sw, sh = strip.shake
    assert (texts["SHAKE"]["anchor"], texts["SHAKE"]["x"], texts["SHAKE"]["y"]) == (
        "center", sx + sw // 2, sy + sh // 2)
    tx, ty, _, _ = strip.tilt
    assert (texts["TILT"]["anchor"], texts["TILT"]["x"], texts["TILT"]["y"]) == ("topleft", tx + 3, ty + 2)
    kx, ky, _, _ = strip.sliders["light"]
    light = next(c for t, c in texts.items() if t.startswith("Light"))
    assert (light["anchor"], light["x"], light["y"]) == ("bottomleft", kx, ky - 1)


# -- the exported draw-queue renderer's new branches (stub kivy; real Kivy: test_kivy_microbit_real_render.py) --

def _area(points):
    n = len(points)
    return abs(sum(points[i][0] * points[(i + 1) % n][1] - points[(i + 1) % n][0] * points[i][1]
                   for i in range(n))) / 2.0


def _tri_area(t):
    return _area(list(t))


def _in_triangle(p, t):
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    a, b, c = t
    signs = (cross(a, b, p), cross(b, c, p), cross(c, a, p))
    return all(s >= 0 for s in signs) or all(s <= 0 for s in signs)


WEDGE = [(0, 0), (42, 0), (30, 12), (22, 5), (12, 20), (5, 10), (0, 36)]       # the silkscreen wedge, scaled
POLYGONS = {
    "triangle": [(0, 0), (10, 0), (0, 10)],
    "square": [(0, 0), (10, 0), (10, 10), (0, 10)],
    "wedge": WEDGE,
    "u": [(10, 10), (30, 10), (30, 50), (50, 50), (50, 10), (70, 10), (70, 70), (10, 70)],
    "arrow": [(0, 3), (6, 3), (6, 0), (10, 5), (6, 10), (6, 7), (0, 7)],
}


@pytest.mark.parametrize("name", sorted(POLYGONS))
@pytest.mark.parametrize("reverse", [False, True])
def test_triangulation_covers_exactly_the_polygon(name, reverse):
    game = _export({})
    pts = list(POLYGONS[name])[::-1] if reverse else list(POLYGONS[name])
    with _stub_kivy(game):
        base = importlib.import_module("objects.base_object")
        tris = base.GameObject._dq_triangulate(pts)
    assert len(tris) == len(pts) - 2
    assert sum(_tri_area(t) for t in tris) == pytest.approx(_area(pts))
    assert all(set(v for v in t) <= set(pts) for t in tris)          # only the polygon's own vertices
    # every triangle's centre lies inside the polygon (no triangle spans a notch)
    for t in tris:
        centre = (sum(p[0] for p in t) / 3.0, sum(p[1] for p in t) / 3.0)
        assert _point_in_polygon(centre, pts), (name, t)


def _point_in_polygon(p, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < (x2 - x1) * (p[1] - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def test_degenerate_polygons_yield_no_triangles():
    game = _export({})
    with _stub_kivy(game):
        tri = importlib.import_module("objects.base_object").GameObject._dq_triangulate
        assert tri([]) == [] and tri([(0, 0)]) == [] and tri([(0, 0), (1, 1)]) == []
        assert tri([(0, 0), (1, 1), (2, 2)]) == []                    # collinear: zero area


class _Rec:
    def __init__(self, name):
        self.name, self.calls = name, []

    def __call__(self, *a, **k):
        self.calls.append((a, k))
        return (self.name, a, k)


def _render(game, cmd, room_h=100):
    """Run one command through the generated _dq_render_cmd with recording stand-ins."""
    base = importlib.import_module("objects.base_object")
    recs = {n: _Rec(n) for n in ("Rectangle", "RoundedRectangle", "Line", "Triangle", "Color")}
    for n, r in recs.items():
        setattr(base, n, r)

    class Group:
        def __init__(self):
            self.added = []

        def add(self, item):
            self.added.append(item)
    group = Group()
    base.GameObject._dq_render_cmd(base.GameObject.__new__(base.GameObject), group, cmd, room_h)
    return recs, group


def test_a_rounded_filled_rectangle_uses_a_rounded_rectangle_with_the_radius():
    game = _export({})
    with _stub_kivy(game):
        recs, _ = _render(game, {"type": "rectangle", "x1": 10, "y1": 20, "x2": 50, "y2": 40, "filled": True,
                                 "color": (1, 2, 3), "radius": 6})
        assert recs["RoundedRectangle"].calls == [((), {"pos": (10, 60), "size": (40, 20), "radius": [6]})]
        assert recs["Rectangle"].calls == []


def test_an_outlined_rounded_rectangle_uses_a_rounded_line():
    game = _export({})
    with _stub_kivy(game):
        recs, _ = _render(game, {"type": "rectangle", "x1": 10, "y1": 20, "x2": 50, "y2": 40, "filled": False,
                                 "color": (1, 2, 3), "radius": 6})
        assert recs["Line"].calls == [((), {"rounded_rectangle": (10, 60, 40, 20, 6), "width": 1})]


def test_a_radius_never_exceeds_half_the_shorter_side():
    game = _export({})
    with _stub_kivy(game):
        recs, _ = _render(game, {"type": "rectangle", "x1": 0, "y1": 0, "x2": 40, "y2": 10, "filled": True,
                                 "color": (1, 2, 3), "radius": 99})
        assert recs["RoundedRectangle"].calls[0][1]["radius"] == [5.0]


def test_a_rectangle_without_a_radius_is_the_plain_one():
    game = _export({})
    with _stub_kivy(game):
        recs, _ = _render(game, {"type": "rectangle", "x1": 10, "y1": 20, "x2": 50, "y2": 40, "filled": True, "color": (1, 2, 3)})
        assert len(recs["Rectangle"].calls) == 1 and recs["RoundedRectangle"].calls == []
        recs, _ = _render(game, {"type": "rectangle", "x1": 10, "y1": 20, "x2": 50, "y2": 40, "filled": False, "color": (1, 2, 3)})
        assert recs["Line"].calls == [((), {"rectangle": (10, 60, 40, 20), "width": 1})]


def test_an_old_kivy_without_rounded_rectangle_falls_back_to_a_square_one():
    game = _export({})
    with _stub_kivy(game):
        base = importlib.import_module("objects.base_object")
        recs, _ = _render(game, {"type": "rectangle", "x1": 10, "y1": 20, "x2": 50, "y2": 40, "filled": True,
                                 "color": (1, 2, 3), "radius": 6})
        base.RoundedRectangle = None
        group = type("G", (), {"added": [], "add": lambda s, i: s.added.append(i)})()
        base.GameObject._dq_render_cmd(base.GameObject.__new__(base.GameObject), group,
                                       {"type": "rectangle", "x1": 10, "y1": 20, "x2": 50, "y2": 40,
                                        "filled": True, "color": (1, 2, 3), "radius": 6}, 100)
        assert recs["Rectangle"].calls, "no square fallback"


def test_a_polygon_becomes_triangles_in_the_flipped_frame():
    game = _export({})
    with _stub_kivy(game):
        recs, _ = _render(game, {"type": "polygon", "points": [[0, 0], [10, 0], [0, 10]], "color": (1, 2, 3)}, room_h=100)
        points = recs["Triangle"].calls[0][1]["points"]
        assert len(recs["Triangle"].calls) == 1 and sorted(zip(points[0::2], points[1::2])) == [(0, 90), (0, 100), (10, 100)]


# -- the decorations, compared whole (not at sample points) with the renderer's own drawing ----------------

@pytest.mark.parametrize("scale", [1.0, 0.6, 1.5])
def test_the_silkscreen_wedge_is_the_renderers_wedge_pixel_for_pixel(scale):
    layout = board_layout(450, 250, scale)
    want, got = _surface(), _surface()
    renderer._corner_decoration(want, layout)
    _raster(got, [c for c in kivy_draw.board_commands(layout, MicrobitSimulator())
                  if c["type"] == "polygon" and c["color"] == kivy_draw.CORNER_GREEN and len(c["points"]) == 7])
    assert pygame.image.tobytes(got, "RGB") == pygame.image.tobytes(want, "RGB")


@pytest.mark.parametrize("scale", [1.0, 0.6, 1.5])
@pytest.mark.parametrize("name", ["a", "b"])
def test_each_ab_tag_is_the_renderers_tag_apart_from_its_letter(scale, name):
    layout = board_layout(450, 250, scale)
    bx, by, br = layout.buttons[name]
    want, got = _surface(), _surface()
    renderer._button_tag(want, name, bx, by, br, layout)
    tag = [c for c in kivy_draw.board_commands(layout, MicrobitSimulator())
           if c["type"] == "polygon" and c["color"] == kivy_draw.CORNER_GREEN and len(c["points"]) == 3]
    # board_commands holds both tags: keep the one whose first point is this button's
    mine = [c for c in tag if (name == "a") == (c["points"][0][1] > c["points"][2][1])]
    assert len(mine) == 1
    _raster(got, mine)
    green = tuple(kivy_draw.CORNER_GREEN)
    w_px = {(x, y) for x in range(SIZE[0]) for y in range(SIZE[1]) if tuple(want.get_at((x, y)))[:3] == green}
    g_px = {(x, y) for x in range(SIZE[0]) for y in range(SIZE[1]) if tuple(got.get_at((x, y)))[:3] == green}
    # the pygame tag has its letter drawn over it: only pixels the letter touched may differ
    differing = w_px ^ g_px
    assert len(g_px) > 20
    assert len(differing) <= 0.45 * len(g_px), (len(differing), len(g_px))
    assert w_px - g_px == set(), "pygame paints green where the command does not"
    xs, ys = [p[0] for p in g_px], [p[1] for p in g_px]
    for (x, y) in differing:
        assert min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)


def test_the_generated_base_object_imports_without_triangle_and_rounded_rectangle():
    """The two names are optional at import time (many test stubs, and a very old Kivy, lack them): a
    polygon is then skipped and a rounded rectangle falls back to a square one, never an ImportError."""
    game = _export({})
    with _stub_kivy(game):
        graphics = sys.modules["kivy.graphics"]
        for name in ("Triangle", "RoundedRectangle"):
            if hasattr(graphics, name):
                delattr(graphics, name)
        base = importlib.import_module("objects.base_object")
        assert base.Triangle is None and base.RoundedRectangle is None
        recs = {n: _Rec(n) for n in ("Rectangle", "Line", "Color")}
        for n, r in recs.items():
            setattr(base, n, r)
        group = type("G", (), {"added": [], "add": lambda s, i: s.added.append(i)})()
        obj = base.GameObject.__new__(base.GameObject)
        obj._dq_render_cmd(group, {"type": "polygon", "points": [[0, 0], [10, 0], [0, 10]], "color": (1, 2, 3)}, 100)
        obj._dq_render_cmd(group, {"type": "rectangle", "x1": 0, "y1": 0, "x2": 20, "y2": 20, "filled": True,
                                   "color": (1, 2, 3), "radius": 4}, 100)
        assert len(recs["Rectangle"].calls) == 1                     # the rounded one fell back to a plain one

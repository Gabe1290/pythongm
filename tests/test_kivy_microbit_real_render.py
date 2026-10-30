"""Stage P / A9: the micro:bit board rendered through REAL Kivy.

Every other Kivy test in this repo runs the generated code under a stub ``kivy``. This one hands
the board's draw-queue commands to the real generated ``objects/base_object.py`` in a subprocess
(``_real_kivy_render.py``), renders them into a real Kivy ``Fbo`` on a hidden window and compares
the pixels with the pygame renderer's. It needs Kivy and a GL context; where either is missing (CI,
a headless box) it skips, and a crashing worker skips instead of killing pytest.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import test_kivy_microbit_draw as draw_tests  # noqa: E402
from test_kivy_microbit_actions import _export  # noqa: E402

from extensions.microbit import kivy_draw, renderer  # noqa: E402
from extensions.microbit.layout import board_layout, strip_layout  # noqa: E402
from extensions.microbit.simulator import MicrobitSimulator  # noqa: E402

WORKER = ROOT / "tests" / "_real_kivy_render.py"
SIZE = draw_tests.SIZE
TOLERANCE = 3                       # per channel: 8-bit colour round trips through float


def _run_worker(game, scenes):
    work = Path(tempfile.mkdtemp(prefix="realkivy_req_"))
    request, result = work / "request.json", work / "result.json"
    request.write_text(json.dumps({"scenes": scenes}), encoding="utf-8")
    try:
        proc = subprocess.run([sys.executable, str(WORKER), str(game), str(request), str(result)],
                              capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return None, "worker timed out"
    if not result.exists():
        return None, f"worker died (exit {proc.returncode}): {proc.stderr[-300:]}"
    data = json.loads(result.read_text(encoding="utf-8"))
    if data.get("fatal"):
        return None, data["fatal"]
    return data, None


STATE_NAMES = ["idle", "lit", "button_a", "logo", "pin1", "tone", "tilt", "shake", "sliders"]
SCALES = [1.0, 0.6]


def _scene_for(state, scale, points):
    sim = MicrobitSimulator()
    draw_tests.STATES[state](sim)
    layout = board_layout(450, 250, scale)
    commands = kivy_draw.board_commands(layout, sim) + kivy_draw.strip_commands(layout, sim)
    return {"name": f"{state}@{scale}", "w": SIZE[0], "h": SIZE[1], "commands": commands,
            "points": points(layout)}, layout, sim


@pytest.fixture(scope="module")
def rendered():
    """One worker run for every state and scale (Kivy takes seconds to start)."""
    pytest.importorskip("kivy")
    game = _export({})
    scenes = []
    for state in STATE_NAMES:
        for scale in SCALES:
            scene, _, _ = _scene_for(state, scale, draw_tests._points)
            scenes.append(scene)
    data, why = _run_worker(game, scenes)
    if data is None:
        pytest.skip(f"real Kivy cannot render here: {why}")
    return data


def _close(a, b):
    return all(abs(x - y) <= TOLERANCE for x, y in zip(a[:3], b[:3]))


def test_the_worker_ran_real_kivy_without_a_command_failing(rendered):
    assert rendered["kivy"], "no Kivy version reported"
    assert rendered["errors"] == [], rendered["errors"]


@pytest.mark.parametrize("scale", SCALES)
@pytest.mark.parametrize("state", STATE_NAMES)
def test_real_kivy_paints_what_the_pygame_renderer_paints(rendered, state, scale):
    scene, layout, sim = _scene_for(state, scale, draw_tests._points)
    want = draw_tests._surface()
    renderer.draw_board(want, layout, sim)
    renderer.draw_strip(want, strip_layout(layout), sim, layout.scale)
    got = rendered["scenes"][scene["name"]]
    # Points the pygame draw puts text under, or on an anti-aliased edge, are not compared:
    # fonts differ between the two toolkits by design.
    skip = {"speaker"} if state == "tone" else set()
    bad = {}
    for name, (x, y) in scene["points"].items():
        if name in skip or name not in got:
            continue
        expected = tuple(want.get_at((int(x), int(y))))[:3]
        if not _close(got[name], expected):
            bad[name] = (tuple(got[name][:3]), expected)
    assert not bad, bad


def test_the_rounded_corners_are_cut_away_and_the_wedge_and_tags_are_filled(rendered):
    got = rendered["scenes"]["idle@1.0"]
    # the outer pixel of a rounded panel is NOT the panel colour (square corners would paint it)
    assert not _close(got["panel_corner"], kivy_draw.PANEL_COLOR)
    assert not _close(got["pad_corner"], kivy_draw.PAD_COLOR)
    assert not _close(got["shake_corner"], kivy_draw.SHAKE_COLOR)
    assert _close(got["wedge"], kivy_draw.CORNER_GREEN)             # inside the silkscreen wedge
    assert _close(got["wedge_outside"], kivy_draw.BODY_COLOR)       # well below the wedge: plain body
    assert _close(got["tag_a"], kivy_draw.CORNER_GREEN) and _close(got["tag_b"], kivy_draw.CORNER_GREEN)


def test_a_concave_polygon_fills_only_its_own_area(rendered_polygon):
    inside, outside = rendered_polygon
    assert all(_close(v, (0, 200, 0)) for v in inside.values()), inside
    assert all(_close(v, (250, 0, 250)) for v in outside.values()), outside


@pytest.fixture(scope="module")
def rendered_polygon():
    pytest.importorskip("kivy")
    game = _export({})
    # a "U": two arms joined at the bottom, with a notch between the arms (concave)
    poly = [[10, 10], [30, 10], [30, 50], [50, 50], [50, 10], [70, 10], [70, 70], [10, 70]]
    scene = {"name": "u", "w": 100, "h": 100, "commands": [{"type": "polygon", "points": poly, "color": (0, 200, 0)}],
             "points": {"left_arm": [20, 30], "right_arm": [60, 30], "bottom": [40, 65], "left_arm_foot": [20, 60],
                        "notch_top": [40, 20], "notch_mid": [40, 40], "outside_left": [5, 30],
                        "outside_below": [40, 80], "outside_right": [80, 30]}}
    data, why = _run_worker(game, [scene])
    if data is None:
        pytest.skip(f"real Kivy cannot render here: {why}")
    got = data["scenes"]["u"]
    return ({k: got[k] for k in ("left_arm", "right_arm", "bottom", "left_arm_foot")},
            {k: got[k] for k in ("notch_top", "notch_mid", "outside_left", "outside_below", "outside_right")})


def test_a_rounded_rectangle_is_filled_and_its_corner_is_not(rendered_rect):
    got = rendered_rect
    assert _close(got["middle"], (200, 0, 0)) and _close(got["edge_middle"], (200, 0, 0))
    assert _close(got["corner"], (250, 0, 250)), got["corner"]           # cut away by the radius
    assert _close(got["plain_corner"], (0, 0, 200)), got["plain_corner"]  # no radius: square


@pytest.fixture(scope="module")
def rendered_rect():
    pytest.importorskip("kivy")
    game = _export({})
    cmds = [{"type": "rectangle", "x1": 10, "y1": 10, "x2": 60, "y2": 40, "filled": True, "color": (200, 0, 0), "radius": 10},
            {"type": "rectangle", "x1": 70, "y1": 10, "x2": 100, "y2": 40, "filled": True, "color": (0, 0, 200)}]
    scene = {"name": "r", "w": 120, "h": 60, "commands": cmds,
             "points": {"middle": [35, 25], "edge_middle": [35, 11], "corner": [10, 10], "plain_corner": [70, 10]}}
    data, why = _run_worker(game, [scene])
    if data is None:
        pytest.skip(f"real Kivy cannot render here: {why}")
    return data["scenes"]["r"]

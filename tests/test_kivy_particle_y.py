"""Kivy export: particle emitters sit at the AUTHOR's y.

Checked 2026-11-20 after the y-space fix for every other action (test_kivy_y_in_actions.py): the particle
simulation is already in the author's space on both targets (y grows downward, direction 90 is up), and
``render_particles`` is the one place that flips to Kivy's y-up, so an emitter at ``y = 200`` really is
200 from the top. Only a ``y`` READ inside an emitter expression (``create_emitter`` at ``y + 200``) was
Kivy's, which the default ``gm=True`` of the value helpers fixed. This pins all of it, differentially against
the desktop's own handlers and ``GameInstance.update_particle_system``.
"""
import ast
import math
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from test_if_condition_parity import kivy_base_methods  # noqa: E402,F401

ROOM_H, IMG_H = 480, 32
START_X, START_Y = 10, 20                         # the caller, in the author's space

PARTICLE_METHODS = ("_cond", "_gm_y", "update_particle_system", "_spawn_particles", "create_particle_system",
                    "create_particle_type", "create_emitter", "destroy_emitter", "burst_particles",
                    "render_particles")


@pytest.fixture(scope="module")
def kivy_particle_class(tmp_path_factory):
    pytest.importorskip("PySide6")
    from export.Kivy.kivy_exporter import KivyExporter
    from test_kivy_parity_batch import _load_project
    out = tmp_path_factory.mktemp("particles") / "export"
    assert KivyExporter(_load_project("maze_1"), ROOT / "samples" / "maze_1", out).export()
    src = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "GameObject")
    lines = ["class _C:"]
    for fn in cls.body:
        if isinstance(fn, ast.FunctionDef) and fn.name in PARTICLE_METHODS:
            seg = ast.get_source_segment(src, fn).splitlines()
            lines += ["    " + seg[0]] + seg[1:]
    return "\n".join(lines) + "\n"


def _desktop(emitter, steps=3, ptype=None):
    from runtime.action_executor import ActionExecutor
    from runtime.instance import GameInstance
    runner = types.SimpleNamespace(global_variables={}, score=0, lives=3, health=100, project_data={},
                                   current_room=types.SimpleNamespace(width=640, height=ROOM_H, instances=[]))
    ex = ActionExecutor(game_runner=runner)
    inst = GameInstance("obj_p", START_X, START_Y, {}, action_executor=ex)
    ex.execute_create_particle_system_action(inst, {})
    ex.execute_create_particle_type_action(inst, ptype or PTYPE)
    ex.execute_create_emitter_action(inst, emitter)
    ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 2})
    for _ in range(steps):
        inst.update_particle_system()
    return sorted((round(p["x"], 6), round(p["y"], 6)) for p in inst._particle_system["particles"])


PTYPE = {"size_min": 1, "size_max": 1, "speed_min": 5, "speed_max": 5, "direction_min": 90, "direction_max": 90,
         "life_min": 10, "life_max": 10, "color": "#FFFFFF"}


def _kivy(emitter, base_methods, steps=3, ptype=None, render=False):
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    for action, params in (("create_particle_system", {}), ("create_particle_type", ptype or PTYPE),
                           ("create_emitter", emitter), ("burst_particles", {"particle_type": 0, "number": 2})):
        gen.process_action({"action_type": action, "parameters": params}, "create")
    src = base_methods + "    def m(self):\n" + gen.get_code() + "\n"
    drawn = []

    class _Rec:
        def __init__(self, *a, **k):
            self.a, self.k = a, k

    class _Group(_Rec):
        def clear(self):
            pass

        def add(self, item):
            drawn.append(item)

    class _Canvas:
        after = types.SimpleNamespace(add=lambda g: None)

    ns = {"math": math, "InstructionGroup": _Group, "Color": type("Color", (_Rec,), {}),
          "Ellipse": type("Ellipse", (_Rec,), {}), "Rectangle": type("Rectangle", (_Rec,), {}),
          "SPRITE_PATHS": {}, "load_image": lambda p: None}
    exec(compile(src, "<generated>", "exec"), ns)
    inst = ns["_C"]()
    inst.scene = types.SimpleNamespace(room_height=ROOM_H)
    inst.image_height, inst.grid_size = IMG_H, 32
    inst.x, inst.y = START_X, ROOM_H - START_Y - IMG_H          # Kivy: y up from the sprite's bottom
    inst._particle_group = None
    inst.canvas = _Canvas()
    inst.m()
    for _ in range(steps):
        inst.update_particle_system()
    particles = sorted((round(p["x"], 6), round(p["y"], 6)) for p in inst._particle_system["particles"])
    if render:
        inst.render_particles()
        return particles, [d for d in drawn if type(d).__name__ == "Ellipse"]
    return particles


EMITTERS = [
    {"x": "100", "y": "200", "width": 0, "height": 0, "shape": "rectangle"},
    {"x": "100", "y": "y + 200", "width": 0, "height": 0, "shape": "rectangle"},     # a READ of y
    {"x": "x * 2", "y": "0", "width": 0, "height": 0, "shape": "line"},
    {"x": "5", "y": "self.y + 1", "width": 0, "height": 0, "shape": "ellipse"},
]


@skip_without_pyside6
@pytest.mark.parametrize("emitter", EMITTERS, ids=lambda e: f"{e['x']},{e['y']}")
def test_particles_end_up_where_the_desktop_puts_them(emitter, kivy_particle_class):
    assert _kivy(emitter, kivy_particle_class) == _desktop(emitter)


@skip_without_pyside6
def test_an_emitter_at_y_200_is_drawn_200_from_the_top(kivy_particle_class):
    """The simulation is in the author's space; render_particles alone flips to Kivy's y-up."""
    emitter = {"x": "100", "y": "200", "width": 0, "height": 0, "shape": "rectangle"}
    particles, ellipses = _kivy(emitter, kivy_particle_class, steps=0, render=True)
    assert particles == [(100.0, 200.0)] * 2
    radius = 1                                                  # size 1
    assert len(ellipses) == 2
    for e in ellipses:
        x, y = e.k["pos"]
        assert (x + radius, y + radius) == (100, ROOM_H - 200)   # screen y = room height - author y
    # a particle moving UP (direction 90) is a SMALLER author y, a larger screen y
    up, _ = _kivy(emitter, kivy_particle_class, steps=3, render=True)
    assert up == [(100.0, 185.0)] * 2


@skip_without_pyside6
def test_a_particle_heading_down_increases_the_authors_y(kivy_particle_class):
    down = dict(PTYPE, direction_min=270, direction_max=270)
    emitter = {"x": "100", "y": "50", "width": 0, "height": 0, "shape": "rectangle"}
    assert _kivy(emitter, kivy_particle_class, ptype=down) == _desktop(emitter, ptype=down)
    assert _kivy(emitter, kivy_particle_class, ptype=down)[0][1] == pytest.approx(65.0)

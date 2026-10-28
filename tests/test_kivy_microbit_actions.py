"""Stage P / K1: the micro:bit actions and conditions on the Kivy export.

A real Kivy export of a micro:bit project ships the simulator package and a
generated object whose handlers call ``_mb_*`` helpers. Kivy cannot run in CI,
so the generated object is imported under a stub ``kivy`` and driven for real;
what it does to its simulator is compared with what the DESKTOP handlers
(``handlers.py``) do to theirs for the same authored parameters, so the two
cannot drift apart.
"""
import importlib
import shutil
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_microbit_export_fallthrough import _project, _action  # noqa: E402


class _Widget:
    def __init__(self, *a, **k):
        pass


@contextmanager
def _stub_kivy(game_dir: Path):
    saved_path, saved_modules = list(sys.path), dict(sys.modules)
    stored = {}

    def mod(name, **attrs):
        m = types.ModuleType(name)
        m.__dict__.update(attrs)
        sys.modules[name] = m

    class _Win:
        width, height = 320, 240

        def bind(self, **kw):
            pass

        def __getattr__(self, name):
            return lambda *a, **k: None

    try:
        mod("kivy")
        mod("kivy.uix")
        mod("kivy.uix.widget", Widget=_Widget)
        mod("kivy.graphics", **{n: object for n in (
            "Rectangle", "Color", "Line", "Ellipse", "InstructionGroup", "PushMatrix",
            "PopMatrix", "Translate", "Fbo", "ClearColor", "ClearBuffers", "Triangle",
            "Scale")})
        mod("kivy.graphics.texture", Texture=object)
        mod("kivy.core")
        mod("kivy.core.window", Window=_Win())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=object)
        mod("kivy.clock", Clock=object)
        mod("main", get_game_app=lambda: None, _ScriptGameProxy=object,
            set_global=lambda k, v: stored.__setitem__(k, v),
            get_global=lambda k: stored.get(k, 0))
        for name in [n for n in sys.modules if n == "utils" or n.startswith(
                ("utils.", "scenes", "objects", "asset_paths", "microbit_sim"))]:
            del sys.modules[name]
        sys.path = [str(game_dir)] + [p for p in sys.path if p != str(ROOT)]
        yield stored
    finally:
        sys.path[:] = saved_path
        for name in [n for n in sys.modules if n not in saved_modules]:
            del sys.modules[name]
        sys.modules.update(saved_modules)


def _export(events):
    from export.Kivy.kivy_exporter import KivyExporter
    out = Path(tempfile.mkdtemp(prefix="mb_k1_")) / "export"
    assert KivyExporter(_project(events), Path(tempfile.mkdtemp()), out).export()
    return out / "game"


def _board(game_dir):
    mod = importlib.import_module("objects.microbit_1")
    cls = mod.Microbit1
    inst = cls.__new__(cls)
    inst.object_name = "microbit_1"
    return inst


def _desktop_board():
    from extensions.microbit.simulator import MicrobitSimulator
    from extensions.microbit.state import attach_simulator

    class Inst:
        pass
    inst = Inst()
    attach_simulator(inst, MicrobitSimulator())
    return inst


def _desktop_run(inst, name, params):
    from events.plugin_loader import load_all_plugins
    from extensions.microbit.handlers import PluginExecutor
    load_all_plugins()
    return getattr(PluginExecutor(), "execute_%s_action" % name)(inst, params)


def _fingerprint(sim):
    """Everything an author can observe: the grid and the reports, over time."""
    from extensions.microbit.state import KEY  # noqa: F401
    trace = []
    for _ in range(40):
        reported = sim.update(0.05)
        trace.append(([[sim.get_pixel(x, y) for x in range(5)] for y in range(5)],
                      [(k, d) for k, d in reported]))
    return trace


ACTION_CASES = [
    ("microbit_show_image", {"image": "HEART", "hold": "200"}),
    ("microbit_show_image", {"image": "SAD", "hold": ""}),
    ("microbit_scroll_text", {"text": "Hi", "delay": "60"}),
    ("microbit_scroll_text", {"text": "AB", "delay": ""}),
    ("microbit_show_number", {"value": "42"}),
    ("microbit_show_number", {"value": "3.5"}),
    ("microbit_set_pixel", {"x": "2", "y": "3", "brightness": "7"}),
    ("microbit_set_pixel", {"x": "9", "y": "9", "brightness": "7"}),
    ("microbit_clear_display", {}),
    ("microbit_set_brightness", {"brightness": "128"}),
    ("microbit_play_tone", {"frequency": "523", "duration": "250"}),
    ("microbit_play_melody", {"melody": "C4:4 D4:4 E4:8", "tempo": "100"}),
    ("microbit_stop_sound", {}),
    ("microbit_radio_set_group", {"group": "5"}),
    ("microbit_radio_send", {"value": "7"}),
]


@pytest.mark.parametrize("name,params", ACTION_CASES)
def test_every_action_does_what_the_desktop_handler_does(name, params):
    full = dict(_action(name)["parameters"])
    full.update(params)
    act = {"action": name, "parameters": full}
    game = _export({"create": {"actions": [act]}})
    with _stub_kivy(game):
        kivy_board = _board(game)
        kivy_board.on_create()
        kivy_sim = kivy_board._mb_sim()
        desk = _desktop_board()
        _desktop_run(desk, name, full)
        desk_sim = desk.extension_state["microbit"]["simulator"]
        assert _fingerprint(kivy_sim) == _fingerprint(desk_sim)
        assert kivy_sim.radio_group == desk_sim.radio_group


def test_a_non_board_object_does_nothing():
    game = _export({"create": {"actions": [_action("microbit_show_number")]}})
    with _stub_kivy(game):
        inst = _board(game)
        inst.object_name = "obj_other"
        inst.on_create()
        assert inst._mb_sim() is None
        assert inst._mb_if_button("a") is False


SENSORS = ["accelerometer x", "accelerometer y", "accelerometer z", "acceleration strength",
           "compass heading", "light level", "temperature", "sound level", "pin 1 analog"]


@pytest.mark.parametrize("sensor", SENSORS)
def test_read_sensor_matches_desktop(sensor):
    from extensions.microbit.handlers import read_sensor
    game = _export({"create": {"actions": [_action("microbit_read_sensor")]}})
    with _stub_kivy(game) as stored:
        inst = _board(game)
        sim = inst._mb_sim()
        sim.set_acceleration(120, -340, 910)
        sim.set_light_level(77)
        sim.set_temperature(31)
        sim.set_compass_heading(200)
        sim.set_sound_level(55)
        inst._mb_read_sensor(sensor, "v")
        assert inst.v == read_sensor(sim, sensor)
        inst._mb_read_sensor(sensor, "g", True)
        assert stored["g"] == read_sensor(sim, sensor)


def test_conditions_match_desktop():
    from events.plugin_loader import load_all_plugins
    from extensions.microbit.handlers import PluginExecutor
    load_all_plugins()
    game = _export({"create": {"actions": []}})
    with _stub_kivy(game):
        k = _board(game)
        ksim = k._mb_sim()
        d = _desktop_board()
        dsim = d.extension_state["microbit"]["simulator"]
        for sim in (ksim, dsim):
            sim.set_button("a", True)
            sim.set_acceleration(500, -200, 800)
            sim.set_pixel(1, 1, 6)
            sim.update(0.05)
        ex = PluginExecutor()
        for button in ("a", "b", "logo"):
            assert k._mb_if_button(button) == ex.execute_microbit_if_button_action(d, {"button": button})
        for gesture in ("shake", "none"):
            assert k._mb_if_gesture(gesture) == ex.execute_microbit_if_gesture_action(d, {"gesture": gesture})
        for axis in "xyz":
            for cmp_ in ("<", "<=", "==", ">=", ">", "!="):
                for value in (-200, 0, 500):
                    want = ex.execute_microbit_if_tilt_action(
                        d, {"axis": axis, "comparison": cmp_, "value": str(value)})
                    assert k._mb_if_tilt(axis, cmp_, value) == want, (axis, cmp_, value)
        for x, y in ((1, 1), (0, 0), (9, 9)):
            want = ex.execute_microbit_if_pixel_action(
                d, {"x": str(x), "y": str(y), "comparison": ">", "value": "3"})
            assert k._mb_if_pixel(x, y, ">", 3) == want


def test_a_condition_guards_the_next_action_in_generated_code():
    cond = _action("microbit_if_button")
    cond["parameters"]["button"] = "a"
    show = _action("microbit_show_number")
    show["parameters"]["value"] = "5"
    game = _export({"create": {"actions": [cond, show]}})
    with _stub_kivy(game):
        board = _board(game)
        board.on_create()                         # A not pressed: guarded action skipped
        assert board._mb_sim().get_pixel(0, 0) == 0
        board._mb_sim().set_button("a", True)
        board._mb_sim().update(0.02)
        board.on_create()
        for _ in range(20):
            board._mb_sim().update(0.05)
        assert any(board._mb_sim().get_pixel(x, y) for x in range(5) for y in range(5))


def test_the_shipped_simulator_is_byte_identical_to_the_source():
    game = _export({"create": {"actions": []}})
    src = ROOT / "extensions" / "microbit"
    for name in ("simulator", "font", "images", "sound", "melodies", "radio"):
        assert (game / "microbit_sim" / f"{name}.py").read_bytes() == (src / f"{name}.py").read_bytes()


def test_support_files_cannot_escape_the_game_folder(monkeypatch, tmp_path):
    from export.Kivy import kivy_exporter
    ext = tmp_path / "evil"
    ext.mkdir()
    (ext / "export_kivy.py").write_text('SUPPORT_FILES = {"../../escaped.py": "export_kivy.py"}\n')
    monkeypatch.setattr("events.plugin_loader.list_available_extensions",
                        lambda: [{"folder": "evil", "enabled": True}])
    monkeypatch.setattr("events.plugin_loader.get_extension_directory", lambda: tmp_path)
    exporter = kivy_exporter.KivyExporter({"assets": {}}, tmp_path, tmp_path / "out")
    (tmp_path / "out" / "game").mkdir(parents=True)
    exporter._write_extension_support_files()
    assert not (tmp_path / "escaped.py").exists()


CONDITION_CASES = [
    ("microbit_if_gesture", {"gesture": "shake"}, lambda s: s.shake(), True),
    ("microbit_if_gesture", {"gesture": "shake"}, lambda s: None, False),
    ("microbit_if_tilt", {"axis": "x", "comparison": ">", "value": "300"},
     lambda s: s.set_acceleration(500, 0, 800), True),
    ("microbit_if_tilt", {"axis": "x", "comparison": ">", "value": "300"},
     lambda s: s.set_acceleration(100, 0, 800), False),
    ("microbit_if_pixel", {"x": "2", "y": "2", "comparison": "==", "value": "9"},
     lambda s: s.set_pixel(2, 2, 9), True),
    ("microbit_if_pixel", {"x": "2", "y": "2", "comparison": "==", "value": "9"},
     lambda s: None, False),
    ("microbit_if_button", {"button": "logo"}, lambda s: s.set_logo_touched(True), True),
    ("microbit_if_button", {"button": "logo"}, lambda s: None, False),
]


@pytest.mark.parametrize("name,params,setup,expect", CONDITION_CASES)
def test_each_generated_condition_guards_in_the_right_direction(name, params, setup, expect):
    cond = _action(name)
    cond["parameters"].update(params)
    mark = {"action": "set_variable", "parameters": {"variable": "hit", "value": "1"}}
    game = _export({"create": {"actions": [cond, mark]}})
    with _stub_kivy(game):
        board = _board(game)
        board.hit = 0
        sim = board._mb_sim()
        setup(sim)
        sim.update(0.02)
        board.on_create()
        assert board.hit == (1 if expect else 0)


@pytest.mark.parametrize("variable,is_global", [("global.reading", True), ("reading", False)])
def test_read_sensor_scope_survives_codegen(variable, is_global):
    act = _action("microbit_read_sensor")
    act["parameters"].update({"sensor": "light level", "variable": variable})
    game = _export({"create": {"actions": [act]}})
    with _stub_kivy(game) as stored:
        board = _board(game)
        board._mb_sim().set_light_level(42)
        board.on_create()
        if is_global:
            assert stored == {"reading": 42} and not hasattr(board, "reading")
        else:
            assert board.reading == 42 and stored == {}

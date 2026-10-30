"""Queue item A7: object-level micro:bit properties work on the Kivy export.

On the desktop ``option_of(instance, name)`` reads an instance variable first and falls back to
the object's own JSON property (``instance.object_data``). An exported Kivy object has no such
dict, so ``export_kivy.py`` lists ``OBJECT_ATTRS`` and the exporter bakes those properties into
the generated object class. The bundled sample sets ``microbit_keyboard`` on the OBJECT, so
before this the sample's keyboard shortcuts silently did nothing on Kivy.
"""
import importlib
import json
import py_compile
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_actions import _stub_kivy  # noqa: E402
from test_microbit_export_fallthrough import _project  # noqa: E402

PROPS = ("microbit_scale", "microbit_show_sensors", "microbit_keyboard")

# (label, object properties) -- what an author can plausibly have typed in the object editor
CASES = [
    ("none set", {}),
    ("keyboard true", {"microbit_keyboard": True}),
    ("keyboard false", {"microbit_keyboard": False}),
    ("keyboard 'true'", {"microbit_keyboard": "true"}),
    ("keyboard 'no'", {"microbit_keyboard": "no"}),
    ("scale 0.5", {"microbit_scale": 0.5}),
    ("scale 2", {"microbit_scale": 2}),
    ("scale text", {"microbit_scale": "1.5"}),
    ("scale junk", {"microbit_scale": "big"}),
    ("scale tiny", {"microbit_scale": 0.01}),
    ("sensors false", {"microbit_show_sensors": False}),
    ("sensors 'false'", {"microbit_show_sensors": "false"}),
    ("sensors 'yes'", {"microbit_show_sensors": "yes"}),
    ("all three", {"microbit_scale": 0.75, "microbit_show_sensors": False, "microbit_keyboard": True}),
]

HOSTILE = "x'" + chr(10) + "import os; os.system(" + chr(34) + "boom" + chr(34) + ")  #"


def _export(cases):
    from export.Kivy.kivy_exporter import KivyExporter
    data = _project({"create": {"actions": []}})
    objects = data["assets"]["objects"]
    base = objects["microbit_1"]
    objects.clear()
    for i, (_, props) in enumerate(cases):
        objects[f"microbit_c{i}"] = dict(base, name=f"microbit_c{i}", **props)
    data["assets"]["rooms"]["room0"]["instances"] = [
        {"object_name": f"microbit_c{i}", "x": 10 + 40 * i, "y": 20} for i in range(len(cases))]
    out = Path(tempfile.mkdtemp(prefix="mb_oattrs_")) / "export"
    assert KivyExporter(data, Path(tempfile.mkdtemp()), out).export()
    return out / "game"


def _desktop_inst(props):
    class Inst:
        object_data = dict(props)
    return Inst()


def _built(game):
    """The instances the REAL generated create_instances() builds, in case order."""
    scene_mod = importlib.import_module("scenes.room0")
    scene = scene_mod.Room0.__new__(scene_mod.Room0)
    scene.instances = []
    scene.add_instance = scene.instances.append
    scene.create_instances()
    return scene.instances


def test_the_extension_declares_the_properties_and_the_loader_reads_them():
    from export.Kivy.code_generator import extension_object_attrs
    assert extension_object_attrs() == list(PROPS)


def test_every_property_the_desktop_reads_is_declared():
    """The properties are exactly the ones the extension's own code asks option_of() for."""
    found = set()
    for name in ("layout.py", "input.py", "state.py"):
        text = (ROOT / "extensions" / "microbit" / name).read_text(encoding="utf-8")
        found |= set(re.findall(r'"(microbit_[a-z_]+)"', text))
    assert found == set(PROPS), found


def test_the_bundled_sample_keyboard_property_reaches_the_exported_object():
    from core.project_manager import merge_object_file
    from export.Kivy.kivy_exporter import KivyExporter
    sample = ROOT / "samples" / "microbit_1"
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        merge_object_file(obj, json.loads((sample / "objects" / f"{name}.json").read_text(encoding="utf-8")))
    data["assets"]["rooms"]["room0"] = json.loads((sample / "rooms" / "room0.json").read_text(encoding="utf-8"))
    out = Path(tempfile.mkdtemp(prefix="mb1_oattrs_")) / "export"
    assert KivyExporter(data, sample, out).export()
    text = (out / "game" / "objects" / "microbit_1.py").read_text(encoding="utf-8")
    assert "self.microbit_keyboard = True" in text
    with _stub_kivy(out / "game"):
        scene_mod = importlib.import_module("scenes.room0")
        scene = scene_mod.Room0.__new__(scene_mod.Room0)
        scene.instances, scene.room_height = [], 480
        scene.add_instance = scene.instances.append
        scene.create_instances()
        board = next(i for i in scene.instances if getattr(i, "object_name", "") == "microbit_1")
        assert board.microbit_keyboard is True
        scene._extension_key_down(97)                  # the A key: the sample's own setting, nothing set by hand
        assert board._mb_sim().buttons["a"]
        scene._extension_key_up(97)
        assert not board._mb_sim().buttons["a"]


@pytest.mark.parametrize("variable", [None, False, True, "off"])
def test_kivy_reads_each_option_exactly_as_the_desktop_does(variable):
    """For every plausible property set, the desktop's option readers and the shipped ones agree,
    with and without an instance variable of the same name (the instance variable wins)."""
    from extensions.microbit import input as desktop_input
    from extensions.microbit import layout as desktop_layout
    game = _export(CASES)
    with _stub_kivy(game):
        kivy_layout = importlib.import_module("microbit_sim.layout")
        kivy_touch = importlib.import_module("microbit_sim.touch")
        for (label, props), inst in zip(CASES, _built(game)):
            twin = _desktop_inst(props)
            if variable is not None:
                for name in PROPS:
                    setattr(inst, name, variable)
                    setattr(twin, name, variable)
            assert kivy_layout.scale_of(inst) == desktop_layout.scale_of(twin), label
            assert kivy_layout.strip_visible(inst) == desktop_layout.strip_visible(twin), label
            kivy_kb = kivy_touch.keyboard_on(getattr(inst, "microbit_keyboard", False))
            assert kivy_kb == desktop_input._keyboard_on(twin), label


def test_a_property_changes_what_the_board_does():
    """Not just attribute plumbing: scale resizes the layout, the strip toggle removes the strip."""
    game = _export([("big", {"microbit_scale": 2}), ("none", {}), ("nostrip", {"microbit_show_sensors": False})])
    with _stub_kivy(game):
        big, plain, nostrip = _built(game)
        for inst in (big, plain, nostrip):
            inst.has_sprite = False
            inst.x, inst.y, inst.width, inst.height = 100, 150, 32, 32
        assert big._mb_layout(480).body[2] == 2 * plain._mb_layout(480).body[2]
        sys.modules["objects.base_object"].InstructionGroup = lambda: type("G", (), {"clear": lambda s: None})()
        strips = []
        for inst in (plain, nostrip):
            cmds = []
            inst.canvas = type("C", (), {"after": type("A", (), {"add": lambda s, g: None})()})()
            inst._dq_render_cmd = lambda group, cmd, room_h, sink=cmds: sink.append(cmd)
            inst._mb_draw(480)
            strips.append(any(c.get("color") == (46, 48, 54) for c in cmds))
        assert strips == [True, False]


def test_only_plain_scalars_become_attributes_and_they_become_literals():
    game = _export([("hostile", {"microbit_scale": HOSTILE}), ("list", {"microbit_scale": [1, 2]}),
                    ("dict", {"microbit_keyboard": {"a": 1}}), ("none", {"microbit_keyboard": None}),
                    ("float", {"microbit_scale": 1.25})])
    for i in range(5):
        py_compile.compile(str(game / "objects" / f"microbit_c{i}.py"), doraise=True)

    def text(i):
        return (game / "objects" / f"microbit_c{i}.py").read_text(encoding="utf-8")

    assert f"self.microbit_scale = {HOSTILE!r}" in text(0)
    assert "os.system" not in text(0).replace(repr(HOSTILE), "")
    for i in (1, 2, 3):
        assert "self.microbit_" not in text(i), i
    assert "self.microbit_scale = 1.25" in text(4)


def test_an_object_without_the_properties_gets_no_attribute_lines():
    text = (_export([("none", {})]) / "objects" / "microbit_c0.py").read_text(encoding="utf-8")
    assert "self.microbit_" not in text

"""Queue item A6: the ``is_microbit`` flag on a room entry works on the Kivy export.

On the desktop an instance is a micro:bit when its object is named ``microbit*`` OR its room
entry says ``is_microbit`` (``extensions/microbit/__init__.py: on_instance_created``). A Kivy
export has no instance-created hook, so ``export_kivy.py`` lists ``INSTANCE_ATTRS`` and the
exporter copies those room-entry keys onto the instance it builds. These tests pin that the
two targets agree about which instances are boards.
"""
import py_compile
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_actions import _stub_kivy  # noqa: E402
from test_microbit_export_fallthrough import _project  # noqa: E402

# (label, object name, extra room-entry keys) -- the matrix both targets are asked about
ENTRIES = [
    ("named", "microbit_1", {}),
    ("named, flag false", "microbit_1", {"is_microbit": False}),
    ("flagged", "player", {"is_microbit": True}),
    ("flag false", "player", {"is_microbit": False}),
    ("plain", "player", {}),
    ("flag as 1", "player", {"is_microbit": 1}),
    ("flag as string", "player", {"is_microbit": "yes"}),
]


def _export(entries):
    from export.Kivy.kivy_exporter import KivyExporter
    data = _project({"create": {"actions": []}})
    data["assets"]["objects"]["player"] = {"name": "player", "asset_type": "object", "sprite": "",
                                           "visible": True, "solid": False, "events": {}}
    data["assets"]["rooms"]["room0"]["instances"] = [
        dict({"object_name": obj, "x": 10 + 40 * i, "y": 20}, **extra)
        for i, (_, obj, extra) in enumerate(entries)]
    out = Path(tempfile.mkdtemp(prefix="mb_flag_")) / "export"
    assert KivyExporter(data, Path(tempfile.mkdtemp()), out).export()
    return out / "game"


def _desktop_is_board(obj, extra):
    from extensions.microbit import on_instance_created
    from extensions.microbit.state import is_microbit

    class Inst:
        object_name = obj
    inst = Inst()
    on_instance_created(inst, dict({"object_name": obj}, **extra), None)
    return is_microbit(inst)


def test_the_extension_declares_the_flag_and_the_exporter_reads_it():
    from export.Kivy.code_generator import extension_instance_attrs
    assert extension_instance_attrs() == ["is_microbit"]


def test_only_flagged_entries_get_an_attribute_line_and_it_is_the_entrys_own_value():
    game = _export(ENTRIES)
    scene = (game / "scenes" / "room0.py").read_text(encoding="utf-8")
    lines = {ln.strip() for ln in scene.splitlines() if ".is_microbit =" in ln}
    assert lines == {"inst_1.is_microbit = False", "inst_2.is_microbit = True",
                     "inst_3.is_microbit = False", "inst_5.is_microbit = 1",
                     "inst_6.is_microbit = 'yes'"}, lines
    assert "inst_0.is_microbit" not in scene and "inst_4.is_microbit" not in scene


def test_kivy_and_desktop_agree_about_which_instances_are_boards():
    """Runs the REAL generated create_instances() (under the stub kivy) and asks each instance
    it built whether it is a board, then asks the desktop hook the same question."""
    game = _export(ENTRIES)
    with _stub_kivy(game):
        import importlib
        scene_mod = importlib.import_module("scenes.room0")
        scene = scene_mod.Room0.__new__(scene_mod.Room0)
        scene.instances = []
        scene.add_instance = scene.instances.append            # the real one needs a canvas
        scene.create_instances()
        assert len(scene.instances) == len(ENTRIES)
        for (label, obj, extra), inst in zip(ENTRIES, scene.instances):
            assert (inst._mb_sim() is not None) == _desktop_is_board(obj, extra), label
        # and the flag really arrives on the instance, with the entry's own value
        assert [getattr(i, "is_microbit", None) for i in scene.instances] == [
            None, False, True, False, None, 1, "yes"]


def test_a_flagged_non_microbit_object_is_a_working_board_on_kivy():
    game = _export([("flagged", "player", {"is_microbit": True})])
    with _stub_kivy(game):
        import importlib
        cls = importlib.import_module("objects.player").Player
        inst = cls.__new__(cls)
        inst.object_name = "player"
        assert inst._mb_sim() is None                  # without the flag it is just an object
        inst.is_microbit = True
        sim = inst._mb_sim()
        assert sim is not None
        inst._mb_show_image("HEART")
        assert any(any(row) for row in sim.display)


def test_values_are_emitted_as_safe_literals_only():
    hostile = "x'\nimport os; os.system('boom')  #"
    game = _export([("hostile", "player", {"is_microbit": hostile}),
                    ("list", "player", {"is_microbit": [1, 2]}),
                    ("dict", "player", {"is_microbit": {"a": 1}}),
                    ("none", "player", {"is_microbit": None})])
    scene_path = game / "scenes" / "room0.py"
    py_compile.compile(str(scene_path), doraise=True)          # no injected statement
    scene = scene_path.read_text(encoding="utf-8")
    assert "os.system" not in scene.replace(repr(hostile), "")
    assert f"inst_0.is_microbit = {hostile!r}" in scene
    for i in (1, 2, 3):                                        # lists, dicts, null: skipped
        assert f"inst_{i}.is_microbit" not in scene


def test_the_loader_only_trusts_plain_identifiers_in_a_declaration():
    from export.Kivy.code_generator import clean_instance_attrs
    assert clean_instance_attrs(("is_microbit", "a_b2")) == ["is_microbit", "a_b2"]
    assert clean_instance_attrs(["x"]) == ["x"]
    assert clean_instance_attrs(("ok", "a b", "x.y", "1abc", "", "a;b", "import os", 5, None, b"x")) == ["ok"]
    assert clean_instance_attrs("is_microbit") == []          # a bare string is not a list of names
    assert clean_instance_attrs(None) == [] and clean_instance_attrs({"a": 1}) == []

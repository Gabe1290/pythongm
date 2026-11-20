"""Kivy export: Begin Step / End Step handlers accept the dt the scene passes.

The generated scene calls ``instance.on_begin_step(dt)`` and
``instance.on_end_step(dt)`` (like ``on_update(dt)``), but the handlers were
generated as ``def on_end_step(self):``. Every call raised TypeError, which the
scene's ``update()`` catches and prints -- so the rest of that frame was
silently abandoned, every frame, for any object with one of these events
(maze_4's monsters and treasure's monster have an End Step). Found by the
raycast stairs real-Kivy test (a monster whose End Step should reverse it
never did).
"""
import ast
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _object_source(events):
    from export.Kivy.kivy_exporter import KivyExporter
    project = {
        "name": "p", "version": "1.0",
        "settings": {"window_width": 64, "window_height": 64, "room_speed": 30},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
                   "fonts": {}, "data": {},
                   "objects": {"obj_a": {"name": "obj_a", "asset_type": "object",
                                         "sprite": "", "visible": True, "solid": False,
                                         "persistent": False, "depth": 0,
                                         "events": events}},
                   "rooms": {"room0": {"name": "room0", "asset_type": "room",
                                       "width": 64, "height": 64,
                                       "instances": [{"object_name": "obj_a", "x": 0, "y": 0}],
                                       "tiles": []}}},
    }
    out = Path(tempfile.mkdtemp(prefix="kivy_steps_")) / "export"
    assert KivyExporter(project, Path(tempfile.mkdtemp()), out).export()
    return (out / "game" / "objects" / "obj_a.py").read_text(encoding="utf-8"), out / "game"


def _arg_names(source, method):
    tree = ast.parse(source)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == method)
    return [a.arg for a in fn.args.args]


def test_begin_and_end_step_handlers_take_dt():
    def act():                     # one dict per event: the exporter annotates them
        return {"actions": [{"action": "set_variable", "parameters": {
            "variable": "seen", "value": "1", "scope": "instance", "relative": False}}]}
    src, game = _object_source({"begin_step": act(), "end_step": act(), "step": act()})
    assert _arg_names(src, "on_begin_step") == ["self", "dt"]
    assert _arg_names(src, "on_end_step") == ["self", "dt"]
    assert _arg_names(src, "on_update") == ["self", "dt"]


def test_the_scene_calls_them_with_dt():
    """The other half of the contract: if a call site ever drops dt, the
    handlers above break the other way round."""
    scene = (ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    assert "instance.on_begin_step(dt)" in scene
    assert "instance.on_end_step(dt)" in scene

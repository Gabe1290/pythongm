"""Surface actions the Kivy export silently drops (F1a).

The Kivy code generator emits `pass # TODO` for any action it (and no enabled
extension) supports, so the exported game silently skips that behaviour. Without
surfacing, the export dialog looks fully successful. These tests pin the
accumulator that feeds the user-facing "N actions were skipped" note, and prove
it fires on a real bundled sample.
"""
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy import code_generator as cg  # noqa: E402


def test_unknown_action_is_recorded_and_reset():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0)
    out = gen._convert_simple_action("totally_made_up_action", {}, "create")
    assert out == "pass  # TODO: totally_made_up_action"
    assert cg.get_unsupported_actions() == ["totally_made_up_action"]
    cg.reset_unsupported_actions()
    assert cg.get_unsupported_actions() == []


def test_supported_action_is_not_recorded():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0)
    gen._convert_simple_action("set_hspeed", {"hspeed": "3"}, "create")
    assert cg.get_unsupported_actions() == []


def _merged(sample_name):
    from utils.project_file_merge import merge_object_file
    sample = REPO_ROOT / "samples" / sample_name
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, obj in data.get("assets", {}).get("objects", {}).items():
        sp = sample / "objects" / f"{name}.json"
        if sp.exists():
            merge_object_file(obj, json.loads(sp.read_text(encoding="utf-8")))
    for name in list(data.get("assets", {}).get("rooms", {})):
        sp = sample / "rooms" / f"{name}.json"
        if sp.exists():
            data["assets"]["rooms"][name] = json.loads(sp.read_text(encoding="utf-8"))
    return data, sample


def test_real_kivy_export_reports_what_it_dropped():
    """A clean sample surfaces nothing; the reset is per-export."""
    from export.Kivy.kivy_exporter import KivyExporter
    data, sample = _merged("maze_1")
    out = Path(tempfile.mkdtemp(prefix="uae_")) / "export"
    KivyExporter(data, sample, out).export()
    assert cg.get_unsupported_actions() == [], \
        "maze_1 exports cleanly; nothing should be reported skipped"


# --- F1b: the tractable handlers are now implemented (shrink the drop list) ---

def test_test_chance_generates_a_probability_guard():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0)
    gen.process_action({"action": "test_chance", "parameters": {"sides": "4"}}, "step")
    code = gen.get_code()
    assert "__import__('random').randint(1, 4) == 1" in code
    assert cg.get_unsupported_actions() == []   # no longer dropped


def test_wrap_around_room_generates_a_method_call_and_the_base_defines_it():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0)
    out = gen._convert_simple_action(
        "wrap_around_room", {"horizontal": "true", "vertical": "false"}, "step")
    assert out == "self.wrap_around_room(True, False)"
    assert cg.get_unsupported_actions() == []
    # the base object must define the method the call targets (the M34 lesson)
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    assert "def wrap_around_room(self, horizontal=True, vertical=True):" in kx


def test_treasure_export_handles_the_previously_dropped_actions():
    """The sample that surfaced this dropped four actions; all four
    (test_chance, wrap_around_room, jump_to_start, execute_script) are now
    implemented — see test_treasure_kivy_export_now_drops_nothing."""
    from export.Kivy.kivy_exporter import KivyExporter
    data, sample = _merged("treasure")
    out = Path(tempfile.mkdtemp(prefix="uae_t_")) / "export"
    KivyExporter(data, sample, out).export()
    dropped = cg.get_unsupported_actions()
    for act in ("test_chance", "wrap_around_room", "jump_to_start", "execute_script"):
        assert act not in dropped, f"{act} still dropped"


# --- Issue 2: jump_to_start + execute_script now implemented on Kivy ---------

def test_jump_to_start_handles_self_other_and_object_targets():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0)
    assert gen._convert_simple_action("jump_to_start", {}, "step") == "self.jump_to_start()"
    assert gen._convert_simple_action(
        "jump_to_start", {"target": "other"}, "collision_with_x") == "other.jump_to_start()"
    obj = gen._convert_simple_action(
        "jump_to_start", {"target": "object", "target_object": "monster"}, "collision_with_x")
    assert "for _o in list(self.scene.instances)" in obj
    assert "getattr(_o, 'object_name', '') == 'monster'" in obj
    assert cg.get_unsupported_actions() == []


def test_base_object_defines_jump_to_start_and_captures_spawn():
    kx = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")
    assert "def jump_to_start(self):" in kx
    assert "self.xstart = float(x)" in kx and "self.ystart = float(y)" in kx
    assert 'self.object_name = "{obj_name}"' in kx   # object template sets its name


def test_execute_script_inlines_the_body_with_bindings_and_a_loud_wrapper():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(
        base_indent=0,
        scripts={"adapt": {"code": "instance.hspeed = 4\ngame.check_collision_at_position(instance, 0, 0, 'solid')"}})
    gen.process_action({"action": "execute_script", "parameters": {"script": "adapt"}}, "step")
    code = gen.get_code()
    assert "instance = self" in code and "game = self._script_game()" in code
    assert "instance.hspeed = 4" in code          # body inlined
    assert "except Exception as _script_err:" in code   # fails loud, not silent
    assert cg.get_unsupported_actions() == []
    compile(code, "obj.py", "exec")


def test_execute_script_missing_script_is_visible_not_silent():
    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0, scripts={})
    gen.process_action({"action": "execute_script", "parameters": {"script": "nope"}}, "step")
    code = gen.get_code()
    assert "not found or empty" in code           # prints at runtime, not a silent no-op
    compile(code, "obj.py", "exec")


def test_treasure_kivy_export_now_drops_nothing():
    """The sample that surfaced the whole thing exports every action now."""
    from export.Kivy.kivy_exporter import KivyExporter
    data, sample = _merged("treasure")
    out = Path(tempfile.mkdtemp(prefix="uae_full_")) / "export"
    KivyExporter(data, sample, out).export()
    assert cg.get_unsupported_actions() == [], \
        f"treasure still drops: {cg.get_unsupported_actions()}"
    # the generated modules with the new codegen must compile
    import py_compile
    for pyf in (out / "game" / "objects").glob("*.py"):
        py_compile.compile(str(pyf), doraise=True)


def test_ide_note_lists_skipped_actions_or_is_empty():
    """The IDE helper turns the tally into a user-facing note (empty when
    nothing was dropped). Called unbound with a tr stub — no Qt needed."""
    from core.ide_window import PyGameMakerIDE
    stub = SimpleNamespace(tr=lambda s: s)

    cg.reset_unsupported_actions()
    assert PyGameMakerIDE._unsupported_actions_note(stub) == ""

    cg.reset_unsupported_actions()
    gen = cg.ActionCodeGenerator(base_indent=0)
    gen._convert_simple_action("execute_script", {}, "create")
    note = PyGameMakerIDE._unsupported_actions_note(stub)
    assert "execute_script" in note and "skipped" in note
    cg.reset_unsupported_actions()

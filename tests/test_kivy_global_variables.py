"""`global.<name>` must actually work on a Kivy export, not merely compile.

Desktop keeps author-defined globals on `GameRunner.global_variables` and
HTML5 on `game.globalVariables`. Kivy had no store at all, which produced three
different failures for one documented feature (Set Variable's own description
says "instance or global variable"):

  * `set_variable` on `global.X` generated `self.global.coins = 5` — `global`
    is a reserved word, so that is a SyntaxError, and per the Phase 7.3 note it
    takes the whole generated module's import down with it;
  * a condition on `global.X` was silently substituted with a literal `0`;
  * `draw_text` on `global.X` drew the seventeen characters "global.team_score".

`GameApp.globals` plus main.py's `get_global`/`set_global` fixes all three. The
tests that matter here are the round-trip ones: generated code that WRITES a
global, and generated code that READS it, have to agree at runtime — asserting
on the emitted strings alone would pass just as happily if the two halves named
different stores.
"""
import ast
import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import (  # noqa: E402
    ActionCodeGenerator, _resolve_instance_names, _variable_read_code)


def emit(action, params, event="step"):
    return ActionCodeGenerator()._convert_simple_action(action, params, event)


@pytest.fixture
def fake_main():
    """Stand in for the generated main.py, with the same accessor contract its
    template defines. Generated code reaches it through
    `__import__('main')`, so installing it in sys.modules is enough to run the
    real emitted lines with no Kivy present at all."""
    store = {}
    module = types.ModuleType("main")
    module.get_global = lambda name, default=0: store.get(name, default)

    def _set(name, value):
        store[name] = value
        return value

    module.set_global = _set
    saved = sys.modules.get("main")
    sys.modules["main"] = module
    try:
        yield store
    finally:
        if saved is None:
            del sys.modules["main"]
        else:
            sys.modules["main"] = saved


class TestRoundTrip:
    """Write with one generated line, read with another."""

    def test_a_global_written_by_set_variable_is_read_back(self, fake_main):
        exec(emit("set_variable", {"variable": "global.coins", "value": "7"}), {})
        assert fake_main["coins"] == 7
        assert eval(_resolve_instance_names("global.coins"), {}) == 7

    def test_relative_adds_to_the_stored_value(self, fake_main):
        exec(emit("set_variable", {"variable": "global.coins", "value": "4"}), {})
        exec(emit("set_variable", {"variable": "global.coins", "value": "3",
                                   "relative": True}), {})
        assert fake_main["coins"] == 7

    def test_a_value_expression_may_itself_read_a_global(self, fake_main):
        exec(emit("set_variable", {"variable": "global.total", "value": "10"}), {})
        exec(emit("set_variable", {"variable": "global.total",
                                   "value": "global.total + 5"}), {})
        assert fake_main["total"] == 15

    def test_an_instance_variable_can_be_set_from_a_global(self, fake_main):
        exec(emit("set_variable", {"variable": "global.base", "value": "9"}), {})

        class Inst:
            pass

        inst = Inst()
        exec(emit("set_variable", {"variable": "coins", "value": "global.base"}),
             {}, {"self": inst})
        assert inst.coins == 9

    def test_a_condition_sees_the_written_value(self, fake_main):
        exec(emit("set_variable", {"variable": "global.hp", "value": "3"}), {})
        assert eval(_resolve_instance_names("global.hp > 0"), {}) is True
        exec(emit("set_variable", {"variable": "global.hp", "value": "0"}), {})
        assert eval(_resolve_instance_names("global.hp > 0"), {}) is False

    def test_an_unset_global_reads_zero_like_desktop_and_html5(self, fake_main):
        assert eval(_resolve_instance_names("global.never_set"), {}) == 0

    def test_a_string_global_survives(self, fake_main):
        exec(emit("set_variable", {"variable": "global.msg", "value": "bonjour"}), {})
        assert fake_main["msg"] == "bonjour"


class TestDrawText:
    def test_a_bare_global_draws_its_value(self, fake_main):
        exec(emit("set_variable", {"variable": "global.team_score", "value": "42"}), {})

        class Inst:
            _draw_queue = []
            draw_color = None

        inst = Inst()
        exec(emit("draw_text", {"text": "global.team_score", "x": 5, "y": 6}),
             {}, {"self": inst})
        assert inst._draw_queue[-1]["text"] == "42"

    def test_ordinary_text_is_untouched(self, fake_main):
        class Inst:
            _draw_queue = []
            draw_color = None

        inst = Inst()
        exec(emit("draw_text", {"text": "Score:", "x": 0, "y": 0}), {},
             {"self": inst})
        assert inst._draw_queue[-1]["text"] == "Score:"

    def test_anything_beyond_a_bare_reference_stays_literal(self, fake_main):
        """Deliberately the same narrow `^global\\.(\\w+)$` shape HTML5 uses, so
        no existing sample's rendered text changes."""
        class Inst:
            _draw_queue = []
            draw_color = None

        inst = Inst()
        exec(emit("draw_text", {"text": "global.a + global.b", "x": 0, "y": 0}),
             {}, {"self": inst})
        assert inst._draw_queue[-1]["text"] == "global.a + global.b"


class TestGeneratedCodeShape:
    @pytest.mark.parametrize("params", [
        {"variable": "global.coins", "value": "5"},
        {"variable": "global.coins", "value": "5", "relative": True},
        {"variable": "global.total", "value": "global.total + 1"},
        {"variable": "coins", "value": "global.base"},
        {"variable": "coins", "value": "5"},
        {"variable": "x", "value": "10", "relative": True},
    ])
    def test_set_variable_always_emits_parseable_python(self, params):
        ast.parse(emit("set_variable", params))

    def test_the_reserved_word_never_reaches_the_generated_file(self):
        """The original bug: `self.global.coins = 5` is a SyntaxError, and it
        took the whole module's import with it."""
        for params in ({"variable": "global.coins", "value": "5"},
                       {"variable": "global.coins", "value": "1",
                        "relative": True}):
            assert "self.global" not in emit("set_variable", params)

    def test_reads_need_no_import_line_of_their_own(self):
        """They are substituted into arbitrary expressions, including an `if`
        condition, where a statement cannot go."""
        resolved = _resolve_instance_names("global.hp > 0")
        assert ";" not in resolved
        ast.parse(resolved, mode="eval")


class TestExportedRuntime:
    """The other half of the contract lives in the main.py template."""

    @pytest.fixture(scope="class")
    def main_source(self):
        from PIL import Image
        from export.Kivy.kivy_exporter import KivyExporter

        data = {
            "name": "globals_probe",
            "settings": {"window_width": 320, "window_height": 240},
            "assets": {
                "objects": {
                    "obj_ctrl": {
                        "name": "obj_ctrl", "sprite": "", "visible": True,
                        "events": {"create": {"actions": [
                            {"action": "set_variable",
                             "parameters": {"variable": "global.coins",
                                            "value": "5"}},
                        ]}, "draw": {"actions": [
                            {"action": "draw_text",
                             "parameters": {"text": "global.coins",
                                            "x": 4, "y": 4}},
                        ]}},
                    },
                },
                "rooms": {
                    "rm": {"name": "rm", "width": 320, "height": 240,
                           "background_color": "#101010",
                           "instances": [{"object": "obj_ctrl", "x": 0, "y": 0}]},
                },
            },
            "room_order": ["rm"],
        }
        src = Path(tempfile.mkdtemp(prefix="kivy_globals_src_"))
        (src / "sprites").mkdir(parents=True)
        Image.new("RGBA", (8, 8), (1, 2, 3, 255)).save(src / "sprites" / "unused.png")
        out = Path(tempfile.mkdtemp(prefix="kivy_globals_out_")) / "export"
        assert KivyExporter(data, src, out).export()
        return (out / "game" / "main.py").read_text(encoding="utf-8")

    def test_main_defines_the_accessors_generated_code_calls(self, main_source):
        assert "def get_global(" in main_source
        assert "def set_global(" in main_source

    def test_the_store_exists_on_the_app(self, main_source):
        assert "self.globals = {}" in main_source

    def test_globals_survive_an_android_activity_restart(self, main_source):
        """Room switches on Android restart the Activity for a clean GL
        context, so state that is not in the save file is silently lost.
        score/lives/health are already saved; globals must be too, or a game
        keeps its score across a room change and forgets everything else."""
        assert "'globals':" in main_source
        assert "_saved.get('globals')" in main_source

    def test_the_generated_module_compiles(self, main_source):
        ast.parse(main_source)


class TestVariableNameScopes:
    """A `set_variable`/`test_variable` NAME may carry a scope prefix -- the
    action's own parameter description offers "self.var, global.var, or bare
    names". The generator used to prepend `self.` to whatever it was handed,
    so a prefixed name wrote to, or read from, the wrong place -- silently, in
    two of the three cases."""

    def test_a_self_prefixed_name_does_not_double_prefix(self):
        assert emit("set_variable", {"variable": "self.coins", "value": "5"}) \
            == "self.coins = 5"

    def test_a_self_prefixed_name_reads_the_same_attribute_it_writes(self):
        write = emit("set_variable", {"variable": "self.coins", "value": "5"})
        read = _variable_read_code("self.coins")
        assert "self.self" not in write and "self.self" not in read
        assert "'coins'" in read

    def test_a_global_name_is_read_from_the_store_not_the_instance(self):
        """`getattr(self, 'global.coins', 0)` is not an error -- it just
        always answers 0, so a condition on a global was quietly dead."""
        read = _variable_read_code("global.coins")
        assert "getattr" not in read
        assert "get_global('coins')" in read

    def test_other_is_only_read_inside_a_collision(self):
        assert "other" in _variable_read_code("other.hp", "collision_obj_x")
        # Outside one `other` is None everywhere in this generator, so reading
        # through it would raise; 0 is the runtime's own unresolved answer.
        assert _variable_read_code("other.hp", "step") == "0"

    def test_writing_to_other_outside_a_collision_is_dropped_not_crashed(self):
        code = emit("set_variable", {"variable": "other.hp", "value": "1"}, "step")
        assert code.startswith("pass")
        ast.parse(code)

    def test_writing_to_other_inside_a_collision_targets_other(self):
        code = emit("set_variable", {"variable": "other.hp", "value": "1"},
                    "collision_obj_x")
        assert code == "other.hp = 1"

    def test_vspeed_keeps_its_gamemaker_space_sign(self):
        """Kivy's Y axis is inverted and set_vspeed flips the sign on export."""
        assert _variable_read_code("vspeed") == "-(self.vspeed)"


class TestVariableValues:
    """A custom variable's VALUE was always emitted as a literal, so an
    expression became the text of itself: `coins + 1` assigned the string
    "coins + 1" and the most ordinary counter a student writes never
    incremented, on this target only."""

    def _run(self, value, start=None):
        class Inst:
            pass
        inst = Inst()
        if start is not None:
            inst.coins = start
        exec(emit("set_variable", {"variable": "coins", "value": value}),
             {}, {"self": inst})
        return inst.coins

    def test_the_counter_increments(self):
        assert self._run("coins + 1", start=4) == 5

    def test_arithmetic_is_evaluated(self):
        assert self._run("3 * 4") == 12

    def test_a_bare_word_is_still_text(self):
        """Not every value is an expression, and a bare word was already
        treated as text by both this exporter and desktop."""
        assert self._run("hello") == "hello"

    def test_quoted_text_keeps_its_content_and_loses_its_quotes(self):
        """Quoting is desktop's escape hatch for text containing an operator
        ("W A S D - Move"); the quotes are part of the escape, not the value,
        and desktop strips them. This used to keep them."""
        assert self._run('"W A S D - Move"') == "W A S D - Move"

    def test_operator_looking_prose_stays_text_rather_than_becoming_junk(self):
        """Desktop evaluates this and lands on 0 -- the landmine CLAUDE.md
        documents. Unparseable here means we keep what the author typed."""
        assert self._run("Level 1 - Start") == "Level 1 - Start"

    def test_a_gml_function_resolves_to_the_object_helper(self):
        code = emit("set_variable", {"variable": "coins", "value": "irandom(10)"})
        assert "self.irandom(10)" in code   # GameObject provides it

    def test_an_empty_value_is_empty_text_not_uncompilable(self):
        assert self._run("") == ""

    def test_test_variable_reads_a_global_from_the_store(self, fake_main):
        """The NAME side of the same action. `getattr(self, 'global.coins', 0)`
        raises nothing -- it just answers 0 forever, so the condition was
        quietly dead. A mutation reverting only this half slipped past the
        value-side test below, which is why it has its own."""
        gen = ActionCodeGenerator()
        gen.process_action(
            {"action": "test_variable",
             "parameters": {"variable": "global.coins", "value": "5",
                            "operation": "greater"}},
            "step")
        code = gen.get_code()
        assert "get_global('coins')" in code
        assert "getattr(self, 'global.coins'" not in code

    def test_test_variable_does_not_double_prefix_a_self_name(self, fake_main):
        gen = ActionCodeGenerator()
        gen.process_action(
            {"action": "test_variable",
             "parameters": {"variable": "self.hp", "value": "0"}},
            "step")
        assert "self.hp" not in gen.get_code()      # it is a getattr, not an attr
        assert "'hp'" in gen.get_code()
        assert "'self.hp'" not in gen.get_code()

    def test_test_variable_compares_against_an_evaluated_value(self, fake_main):
        gen = ActionCodeGenerator()
        gen.process_action(
            {"action": "test_variable",
             "parameters": {"variable": "hp", "value": "global.threshold"}},
            "step")
        code = gen.get_code()
        assert "get_global('threshold')" in code
        assert "'global.threshold'" not in code

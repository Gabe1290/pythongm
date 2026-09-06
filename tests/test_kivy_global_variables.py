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
    ActionCodeGenerator, _resolve_instance_names)


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

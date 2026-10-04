"""GameMaker's random()/irandom()/choose() inside a free expression, on the
HTML5 and Kivy export targets.

Logged as a known, scoped-out residual when direction_expr export parity
was fixed (TODO.md): HTML5's general-purpose expression evaluator
(gmExpressionValue) lacked these three GameMaker functions, for every
action that takes a free expression (direction_expr, a custom variable's
value, an if_condition expression, ...), not just start_moving_direction.
Desktop's own _evaluate_expression has supported them all along via its
gm_random/gm_irandom/gm_choose substitution.

Checked Kivy for the same gap before assuming it existed there too --
it doesn't. _resolve_instance_names's default path rewrites any bare
`random`/`irandom`/`choose` call to `self.random`/`self.irandom`/
`self.choose` (they're deliberately absent from _EXPR_LEAVE_BARE, same as
any other GameMaker builtin meant to resolve onto the object), and
GameObject (base_object.py) already ships real `random`/`irandom`/`choose`
methods matching GameMaker's exact semantics -- confirmed present before
any of this fix's changes (`git show <prior commit>:export/Kivy/
kivy_exporter.py`). So only HTML5 needed a change:
- HTML5: added directly to gmExpressionValue's scope object (a plain JS
  object used as a `new Function(...)` argument list -- no renaming needed,
  no AST involved).
- Kivy: untouched. TestKivyRealExecution below locks in that its
  pre-existing, non-prefixed random/irandom/choose methods keep working,
  so a future change to _resolve_instance_names or base_object.py can't
  silently regress this without a test failing.

Since these are genuinely random, the tests assert the documented VALUE
RANGE/behaviour (random(n) in [0, n), irandom(n) an int in [0, n]
inclusive, choose picks one of its arguments), not an exact value.
"""
import re
import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import import_module_directly  # noqa: E402

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockInstance:
    pass


class TestDesktopReference:
    """The baseline both export targets are matching."""

    def test_random_is_a_float_below_n(self):
        executor = ActionExecutor()
        for _ in range(20):
            v = executor._evaluate_expression("random(10)", MockInstance())
            assert isinstance(v, float)
            assert 0 <= v < 10

    def test_irandom_is_an_int_up_to_and_including_n(self):
        executor = ActionExecutor()
        seen = set()
        for _ in range(200):
            v = executor._evaluate_expression("irandom(3)", MockInstance())
            assert isinstance(v, int)
            assert 0 <= v <= 3
            seen.add(v)
        assert seen == {0, 1, 2, 3}, "expected every value 0..3 to come up over 200 draws"

    def test_choose_picks_one_argument(self):
        executor = ActionExecutor()
        seen = set()
        for _ in range(200):
            v = executor._evaluate_expression("choose(0, 90, 180, 270)", MockInstance())
            assert v in (0, 90, 180, 270)
            seen.add(v)
        assert seen == {0, 90, 180, 270}


# ---------------------------------------------------------------------------
# Kivy
# ---------------------------------------------------------------------------

from export.Kivy.code_generator import (  # noqa: E402
    ActionCodeGenerator, _resolve_instance_names,
)
from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402


class TestKivyRename:
    """_resolve_instance_names's ordinary default path already resolves a
    bare random/irandom/choose call onto self -- no renaming involved, no
    change needed here."""

    @pytest.mark.parametrize("src,expected_call", [
        ("random(360)", "self.random(360)"),
        ("irandom(3)", "self.irandom(3)"),
        ("choose(0, 90, 180, 270)", "self.choose(0, 90, 180, 270)"),
    ])
    def test_resolved_onto_self(self, src, expected_call):
        assert _resolve_instance_names(src) == expected_call

    def test_bare_names_inside_choose_still_resolve_normally(self):
        assert _resolve_instance_names("choose(facing, 0)") == "self.choose(self.facing, 0)"

    def test_does_not_misfire_on_unrelated_identifiers(self):
        """A word merely CONTAINING "random" (e.g. a hypothetical
        "randomize" custom variable) must resolve as its own bare name,
        not get mistaken for a call to `random`."""
        assert _resolve_instance_names("randomize + 1") == "self.randomize + 1"


class TestKivyCodegen:
    """start_moving_direction's direction_expr, exercising these functions
    through the actual call site -- already correct, no change needed."""

    def _gen(self, direction_expr):
        g = ActionCodeGenerator(base_indent=2)
        g.process_action(
            {"action_type": "start_moving_direction",
             "parameters": {"directions": [], "direction_expr": direction_expr, "speed": 4}},
            "create")
        return g.get_code()

    def test_choose_compiles(self):
        out = self._gen("choose(0, 90, 180, 270)")
        assert "self.direction = (self.choose(0, 90, 180, 270))" in out
        compile("class _C:\n    def m(self):\n" + out, "<gen>", "exec")

    def test_random_compiles(self):
        out = self._gen("random(360)")
        assert "self.direction = (self.random(360))" in out
        compile("class _C:\n    def m(self):\n" + out, "<gen>", "exec")

    def test_irandom_arithmetic_compiles(self):
        out = self._gen("irandom(3) * 90")
        assert "self.direction = (self.irandom(3) * 90)" in out
        compile("class _C:\n    def m(self):\n" + out, "<gen>", "exec")


# -- Stubs for the real-export harness below, matching
# test_kivy_vertical_convention.py's own established pattern exactly (so a
# real GameObject class, built from the actual exported base_object.py
# source, is available without a real Kivy install). --

class _Stub:
    def __init__(self, *a, **k):
        self.args, self.kw = a, k


class _Group(_Stub):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.children = []

    def add(self, c):
        self.children.append(c)

    def remove(self, c):
        if c in self.children:
            self.children.remove(c)

    def clear(self):
        self.children = []


class _Widget:
    def __init__(self, **kwargs):
        pass

    def add_widget(self, *a, **k):
        pass


def _merged(sample: Path) -> dict:
    import json
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    assets = data.get("assets", {})
    for kind in ("rooms", "objects"):
        for name, entry in assets.get(kind, {}).items():
            side = sample / kind / ("%s.json" % name)
            if side.exists():
                entry.update(json.loads(side.read_text(encoding="utf-8")))
    return data


@pytest.fixture(scope="module")
def game_object():
    """The REAL GameObject class, compiled from a real exported
    base_object.py -- proves random/irandom/choose exist, are correctly
    indented inside the whole generated template, and behave correctly,
    not just that the source text looks right."""
    sample = REPO_ROOT / "samples" / "plateforme_2"
    out = Path(tempfile.mkdtemp(prefix="kivy_gmrand_"))
    assert KivyExporter(_merged(sample), sample, out).export()

    source = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    compile(source, "base_object.py", "exec")

    module = types.ModuleType("generated_base_object_gmrand")
    module.__dict__.update({
        "Widget": _Widget, "Rectangle": _Stub, "Color": _Stub, "Line": _Stub,
        "Ellipse": _Stub, "InstructionGroup": _Group, "PushMatrix": _Stub,
        "PopMatrix": _Stub, "Label": object,
        "Window": types.SimpleNamespace(size=(800, 600)),
        "load_image": lambda *a, **k: None,
        "SPRITE_PATHS": {}, "SOUND_PATHS": {}, "BACKGROUND_PATHS": {},
        "get_game_app": lambda: None, "_ScriptGameProxy": object,
        "math": __import__("math"), "random": __import__("random"),
    })
    stripped = "\n".join(line for line in source.splitlines()
                         if not line.startswith(("from ", "import ")))
    exec(stripped, module.__dict__)  # noqa: S102 - our own generated code
    return next(v for v in module.__dict__.values()
                if isinstance(v, type) and v.__name__ == "GameObject")


def _blank_instance(cls):
    """A real instance with just enough state for random/irandom/choose
    and a direction/speed assignment to work -- the direction/speed
    PROPERTY setters (base_object.py) read these underscored attributes,
    matching test_kivy_vertical_convention.py's own _instance() helper."""
    made = type("ObjThing", (cls,), {})
    instance = made.__new__(made)
    instance.__dict__.update({
        "_hspeed": 0.0, "_vspeed": 0.0, "_speed": 0.0, "_direction": 0.0,
        "_gravity": 0.0, "_gravity_direction": 270.0, "_friction": 0.0,
    })
    return instance


class TestKivyRealExecution:
    """Locks in that Kivy's PRE-EXISTING random/irandom/choose methods
    (base_object.py) actually behave per GameMaker's documented semantics
    at runtime, not just that the generated source text looks right --
    nothing here needed a code change, but nothing was testing the real
    VALUE RANGE before either."""

    def test_random_is_a_float_below_n(self, game_object):
        instance = _blank_instance(game_object)
        for _ in range(20):
            v = instance.random(10)
            assert isinstance(v, float)
            assert 0 <= v < 10

    def test_irandom_is_an_int_up_to_and_including_n(self, game_object):
        instance = _blank_instance(game_object)
        seen = set()
        for _ in range(200):
            v = instance.irandom(3)
            assert isinstance(v, int)
            assert 0 <= v <= 3
            seen.add(v)
        assert seen == {0, 1, 2, 3}

    def test_choose_picks_one_argument(self, game_object):
        instance = _blank_instance(game_object)
        seen = set()
        for _ in range(200):
            v = instance.choose(0, 90, 180, 270)
            assert v in (0, 90, 180, 270)
            seen.add(v)
        assert seen == {0, 90, 180, 270}

    def test_direction_expr_choose_sets_a_valid_direction(self, game_object):
        """End to end: the real generated start_moving_direction statement,
        executed against a real instance of the real exported class."""
        instance = _blank_instance(game_object)
        g = ActionCodeGenerator(base_indent=2)
        g.process_action(
            {"action_type": "start_moving_direction",
             "parameters": {"directions": [], "direction_expr": "choose(0, 90, 180, 270)", "speed": 4}},
            "create")
        code = g.get_code()
        exec(compile("def _run(self):\n" + "\n".join(
            "    " + line for line in code.splitlines()), "<gen>", "exec"), {}, (ns := {}))
        ns["_run"](instance)
        assert instance.direction in (0, 90, 180, 270)
        assert instance.speed == 4


# ---------------------------------------------------------------------------
# HTML5 (export/HTML5/templates/engine.js is shared across every export --
# no per-project codegen step exists for this target, so reading the
# template directly is equivalent to reading an exported game's copy).
# ---------------------------------------------------------------------------

ENGINE_JS = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
# Keeps the function's own opening "(" (split on the marker BEFORE it, not
# after) so a paren-balance check is self-consistent instead of off by the
# one closing paren that matches it -- same boundary pitfall as the
# direction_expr test's _CASE slice.
_GM_EXPRESSION_VALUE = ENGINE_JS.split("function gmExpressionValue", 1)[1].split(
    "\nfunction ", 1)[0]


class TestHTML5Structure:

    def test_random_irandom_choose_are_in_scope(self):
        for name in ("random:", "irandom:", "choose:"):
            assert name in _GM_EXPRESSION_VALUE

    def test_random_is_math_random_times_n(self):
        assert "random: (n) => Math.random() * n" in _GM_EXPRESSION_VALUE

    def test_choose_picks_from_args(self):
        assert "choose: (...args) => args[Math.floor(Math.random() * args.length)]" in _GM_EXPRESSION_VALUE

    def test_braces_and_parens_balance_in_the_function(self):
        assert _GM_EXPRESSION_VALUE.count("{") == _GM_EXPRESSION_VALUE.count("}")
        assert _GM_EXPRESSION_VALUE.count("(") == _GM_EXPRESSION_VALUE.count(")")

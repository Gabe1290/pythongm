"""`start_moving_direction`'s `direction_expr` parameter, ignored on HTML5
and Kivy (TODO.md, found 2026-09-19).

The desktop runtime's execute_start_moving_direction_action already honours
`direction_expr` (a free expression evaluated as degrees — a plain number,
a direction name, or a self/other/global-aware expression — which OVERRIDES
`directions` entirely when non-empty). Neither export target read the
parameter at all, so a ball authored with "Direction Expression = 45"
(Tutorial 3's own style) moved on desktop but sat still after export.

Covers, for both targets: a plain-number degrees value (the actual bug
report), a direction name, "stop", and a self/other-referencing expression
— plus a parity check tying Kivy's resulting `direction` value to desktop's
own resulting angle for the same inputs, and a regression guard that an
absent/empty direction_expr still falls back to the existing `directions`
behaviour unchanged.

choose()/random()/irandom() in a direction_expr are NOT covered here —
confirmed to be a pre-existing, broader gap in both targets' expression
evaluators (gmExpressionValue on HTML5, _num_code/_resolve_instance_names
on Kivy), shared by every OTHER action that takes a free expression, not
specific to this one. Out of scope for this fix; see the code comments at
each new branch.
"""
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import import_module_directly  # noqa: E402

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockInstance:
    """Minimal stand-in, matching test_action_executor.py's own MockInstance
    but trimmed to only what execute_start_moving_direction_action reads."""

    def __init__(self):
        self.hspeed = 0.0
        self.vspeed = 0.0


def _desktop_angle(direction_expr, speed=4.0):
    """Run the real desktop handler and recover the resulting angle in
    degrees (0=right, 90=up), the same convention direction_expr/directions
    both use. Returns None for a "stop" result (hspeed/vspeed both 0, which
    has no angle)."""
    executor = ActionExecutor()
    instance = MockInstance()
    executor.execute_start_moving_direction_action(
        instance, {"directions": [], "direction_expr": direction_expr, "speed": speed})
    if abs(instance.hspeed) < 1e-9 and abs(instance.vspeed) < 1e-9:
        return None
    # Desktop: hspeed = cos(a)*speed, vspeed = -sin(a)*speed (screen y down).
    return math.degrees(math.atan2(-instance.vspeed, instance.hspeed)) % 360


class TestDesktopReference:
    """Sanity on the already-correct desktop behaviour this fix brings the
    two export targets up to -- the baseline every other test compares
    against."""

    def test_plain_number_is_degrees(self):
        assert _desktop_angle("45") == pytest.approx(45.0)
        assert _desktop_angle("180") == pytest.approx(180.0)

    def test_direction_name_resolves(self):
        assert _desktop_angle("up") == pytest.approx(90.0)

    def test_stop_zeroes_speed(self):
        assert _desktop_angle("stop") is None

    def test_expression_resolves(self):
        # "90 + 90" has no scoped (self./other.) reference, so a plain
        # ActionExecutor/MockInstance pair is enough to exercise the
        # arithmetic-expression branch of _evaluate_expression.
        executor = ActionExecutor()
        instance = MockInstance()
        executor.execute_start_moving_direction_action(
            instance, {"directions": [], "direction_expr": "90 + 90", "speed": 4})
        # 180 degrees = left: hspeed = cos(180)*4 = -4, vspeed = -sin(180)*4 = 0.
        assert instance.hspeed == pytest.approx(-4.0)
        assert instance.vspeed == pytest.approx(0.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Kivy
# ---------------------------------------------------------------------------

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


def _kivy_gen(params):
    g = ActionCodeGenerator(base_indent=2)
    g.process_action({"action_type": "start_moving_direction", "parameters": params}, "create")
    return g.get_code()


def _kivy_valid(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    compile(wrapper, "<gen>", "exec")  # raises SyntaxError if malformed


def _kivy_exec(code, **self_attrs):
    """Actually run the generated statement against a small fake `self`,
    not just assert on its source text."""
    class _Self:
        pass
    obj = _Self()
    for k, v in self_attrs.items():
        setattr(obj, k, v)
    exec(compile("def _run(self):\n" + "\n".join(
        "    " + line for line in code.splitlines()), "<gen>", "exec"), {}, (ns := {}))
    ns["_run"](obj)
    return obj


class TestKivyCodegen:

    def test_plain_number_sets_direction_and_speed(self):
        out = _kivy_gen({"directions": [], "direction_expr": "45", "speed": 6})
        assert "self.direction = 45" in out
        assert "self.speed = 6" in out
        _kivy_valid(out)

    def test_direction_name_resolves_via_dir_map(self):
        out = _kivy_gen({"directions": [], "direction_expr": "up", "speed": 5})
        assert "self.direction = 90" in out
        assert "self.speed = 5" in out
        _kivy_valid(out)

    def test_stop_zeroes_speed(self):
        out = _kivy_gen({"directions": [], "direction_expr": "stop", "speed": 5})
        assert out.strip() == "self.speed = 0"
        _kivy_valid(out)

    def test_expression_resolves_bare_names_to_self(self):
        out = _kivy_gen({"directions": [], "direction_expr": "facing + 90", "speed": 3})
        assert "self.direction = (self.facing + 90)" in out
        assert "self.speed = 3" in out
        _kivy_valid(out)
        obj = _kivy_exec(out, facing=90)
        assert obj.direction == 180
        assert obj.speed == 3

    def test_empty_direction_expr_falls_back_to_directions(self):
        """Regression guard: existing samples with no direction_expr at all
        must be completely unaffected by this change."""
        out = _kivy_gen({"directions": ["up"], "direction_expr": "", "speed": 6})
        assert "self.direction = 90" in out
        assert "self.speed = 6" in out
        _kivy_valid(out)

    def test_missing_direction_expr_key_falls_back_to_directions(self):
        """Same guard, but for move_fixed/older data with no direction_expr
        key present at all (not even an empty string)."""
        out = _kivy_gen({"directions": ["right"], "speed": 4})
        assert "self.direction = 0" in out
        assert "self.speed = 4" in out
        _kivy_valid(out)


class TestKivyDesktopParity:
    """Ties Kivy's resulting `direction` value to desktop's own resulting
    angle for the same direction_expr -- the actual cross-engine behaviour
    that matters, not just each side's own internal consistency."""

    @pytest.mark.parametrize("expr", ["45", "180", "270", "up", "down-left"])
    def test_same_angle_on_both_targets(self, expr):
        desktop_angle = _desktop_angle(expr)
        out = _kivy_gen({"directions": [], "direction_expr": expr, "speed": 4})
        obj = _kivy_exec(out, facing=0)
        assert obj.direction % 360 == pytest.approx(desktop_angle)

    def test_stop_matches_on_both_targets(self):
        assert _desktop_angle("stop") is None
        out = _kivy_gen({"directions": [], "direction_expr": "stop", "speed": 4})
        assert "self.speed = 0" in out


# ---------------------------------------------------------------------------
# HTML5 (export/HTML5/templates/engine.js is shared across every export --
# no per-project codegen step exists for this target, so reading the
# template directly is equivalent to reading an exported game's copy).
# ---------------------------------------------------------------------------

ENGINE_JS = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
# Keeps the case block's own opening "{" (split on the marker BEFORE it,
# not after) so a brace-balance check over _CASE is self-consistent instead
# of off by the one closing brace that matches it.
_CASE = ENGINE_JS.split("case 'start_moving_direction': ", 1)[1].split(
    "case 'set_variable':", 1)[0]


class TestHTML5EngineStructure:

    def test_direction_expr_is_read(self):
        assert "params.direction_expr" in _CASE

    def test_direction_expr_checked_before_directions_fallback(self):
        """The override must be checked (and `break`) BEFORE the existing
        `directions`-list logic runs, not after -- otherwise a project
        using BOTH fields (or just a stray default) would silently prefer
        the wrong one."""
        expr_pos = _CASE.index("dirExpr")
        directions_pos = _CASE.index("let dirs = params.directions")
        assert expr_pos < directions_pos

    def test_stop_and_none_short_circuit(self):
        branch = _CASE.split("dirExpr", 1)[1]
        assert "lower === 'stop' || lower === 'none'" in branch

    def test_known_direction_name_resolves_via_angles_map(self):
        branch = _CASE.split("dirExpr", 1)[1]
        assert "lower in angles" in branch

    def test_plain_number_and_expression_fallback_present(self):
        branch = _CASE.split("dirExpr", 1)[1]
        assert "parseFloat(trimmed)" in branch
        assert "gmExpressionValue(trimmed, this, game)" in branch

    def test_braces_balance_in_the_touched_case(self):
        assert _CASE.count("{") == _CASE.count("}")

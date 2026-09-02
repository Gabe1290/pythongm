"""Regression test: `global.<name>` inside an exported Kivy condition must
not crash the export.

Found while investigating docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 7.3 (a Kivy
export of a multiplayer sample "should still run single-player") --
reseau_3's obj_ctrl authors `if global.network_connected != 1: ...` (the
Réseau extension mirrors identity/shared state into `global.*`, matching
desktop and HTML5). `global` is a reserved Python keyword, so
`global.network_connected != 1` is not even syntactically valid Python --
ast.parse() raises SyntaxError on it, which _resolve_instance_names
already caught and (before this fix) returned the ORIGINAL text unchanged.
That text then reached the generated .py file verbatim:

    if global.network_connected != 1:
       ^^^^^^
    SyntaxError: invalid syntax

so the WHOLE exported module failed to even import -- not scoped to
multiplayer specifically; ANY project authoring a `global.X` condition
hit this on a Kivy export.

Kivy has no global-variable storage at all (unlike desktop's
game_runner.global_variables / HTML5's game.globalVariables), so there is
no real value to route a `global.X` read to. The fix turns the reference
into a literal 0 instead of leaving it unparseable: correctly-scoped
(matches this file's existing "degrade gracefully, never crash the
export" convention for everything else it can't represent) and actually
semantically right for every multiplayer identity/status global
specifically (is_host, network_connected, player_id, ...) -- they are
genuinely always 0/false on a target that never networks at all.
"""
import ast
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import _resolve_instance_names, _strip_global_refs  # noqa: E402


def _equiv(a, b):
    return ast.dump(ast.parse(a, mode="eval")) == ast.dump(ast.parse(b, mode="eval"))


class TestStripGlobalRefs:
    def test_single_reference_becomes_zero(self):
        assert _strip_global_refs("global.is_host == 1") == "0 == 1"

    def test_multiple_references(self):
        out = _strip_global_refs("global.a + global.b")
        assert out == "0 + 0"

    def test_no_global_reference_is_unchanged(self):
        assert _strip_global_refs("self.x + 4") == "self.x + 4"

    def test_non_string_passthrough(self):
        assert _strip_global_refs(5) == 5
        assert _strip_global_refs(None) is None

    def test_does_not_false_positive_on_substring(self):
        """An identifier that merely CONTAINS "global" (no following dot)
        must not be mangled -- the regex requires a literal '.' right
        after the word "global"."""
        assert _strip_global_refs("self.globalscore == 1") == "self.globalscore == 1"


class TestResolveInstanceNamesWithGlobals:
    def test_previously_raised_syntax_error_now_resolves(self):
        """Before the fix, ast.parse("global.is_host == 1") raised
        SyntaxError, which _resolve_instance_names swallowed and returned
        the ORIGINAL unparseable text -- the exact bug that broke the
        export. Now it must return real, parseable Python."""
        resolved = _resolve_instance_names("global.is_host == 1")
        ast.parse(resolved, mode="eval")   # must not raise
        assert "global" not in resolved
        assert _equiv(resolved, "0 == 1")

    def test_network_connected_condition_from_reseau_3(self):
        """The literal expression reseau_3's obj_ctrl authors."""
        resolved = _resolve_instance_names("global.network_connected != 1")
        ast.parse(resolved, mode="eval")
        assert _equiv(resolved, "0 != 1")

    def test_mixed_with_self_and_bare_names(self):
        resolved = _resolve_instance_names("global.is_host == 1 and hp > 0")
        ast.parse(resolved, mode="eval")
        assert _equiv(resolved, "0 == 1 and self.hp > 0")

    def test_ordinary_expression_unaffected(self):
        """No 'global.' present -- must behave exactly as before."""
        resolved = _resolve_instance_names("vspeed > 0 and y < other.y+8")
        assert _equiv(resolved, "-(self.vspeed) > 0 and self.y < other.y + 8")


# ---------------------------------------------------------------------------
# Real export + compile, for every sample that actually authors global.X in
# a condition (the Réseau samples -- see CLAUDE.md's "if is_host(): ..."
# authoring pattern, which desktop/HTML5 both support via global.*).
# ---------------------------------------------------------------------------

def _kivy_export_and_compile(sample_name):
    from export.Kivy.kivy_exporter import KivyExporter
    from core.project_manager import merge_object_file
    import py_compile

    sample = REPO_ROOT / "samples" / sample_name
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = sample / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = sample / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))

    out = Path(tempfile.mkdtemp(prefix=f"{sample_name}_kivy_global_")) / "export"
    assert KivyExporter(data, sample, out).export(), f"{sample_name} failed to export"

    py_files = list(out.rglob("*.py"))
    assert py_files, "no generated .py files found"
    for p in py_files:
        py_compile.compile(str(p), doraise=True)   # raises on any SyntaxError
    return out


@pytest.mark.parametrize("sample_name", ["reseau_1", "reseau_2", "reseau_3"])
def test_reseau_samples_export_and_compile_cleanly(sample_name):
    _kivy_export_and_compile(sample_name)


def test_reseau_3_generated_code_has_no_bare_global_dot_in_a_condition():
    """The literal substitution must have actually landed in the shipped
    file's condition/expression code, not just in a unit-tested helper
    function. Scoped to `if `-guard lines specifically -- draw_text's own
    `text='global.team_score'` is a separate, legitimate case (a literal
    string VALUE reseau_3 authors on purpose, not an expression this fix
    touches; Kivy's draw_text doesn't resolve global.* the way desktop/
    HTML5 do, a pre-existing, narrower display-only gap outside this
    fix's scope)."""
    out = _kivy_export_and_compile("reseau_3")
    for p in out.rglob("*.py"):
        for line in p.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("if ") or " if " in stripped:
                assert "global." not in line, f"{p.name}: {line!r}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

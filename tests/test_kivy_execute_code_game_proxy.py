"""Kivy execute_code `game` binding — DEFERRED_ITEMS_PLAN.md Tier 3 item 9 /
extension_compat_2_0/PLAN.md's implementation-update follow-up.

Before this fix, an execute_code block on Kivy had no `game` name bound at
all (NameError on any `game.*` reference) and no error wrapping (an
exception propagated up uncaught instead of failing loudly like
execute_script already does). Desktop's execute_code binds the real
GameRunner as `game`; Kivy has no equivalent single object, so `game` is a
minimal proxy (`_ScriptGameProxy`, reusing the same `_script_game()` helper
execute_script already had) exposing score/lives/health as plain
read/write values — matching desktop's actual semantics exactly (raw
attribute writes there do NOT trigger caption updates or
no_more_lives/no_more_health crossing checks either; those only fire from
the set_lives/set_health ACTIONS specifically).

"Locals copied back onto the instance" parity (the other half of item 9)
was deliberately NOT attempted in this pass — Kivy inlined execute_code as
literal Python source in a real generated method, unlike desktop's dynamic
exec()/locals-dict approach. It was resolved in a later pass: Kivy's codegen
now runs the user's code through a real exec() call at runtime too (Kivy
runs on real CPython, so this is available), giving byte-for-byte identical
semantics to desktop rather than an export-time AST rewrite. See
tests/test_kivy_execute_code_export.py for that behavior's coverage — this
file's own tests below still hold: they cover the `game` proxy binding,
which the exec() switch didn't change.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402
from utils.project_file_merge import merge_object_file  # noqa: E402


# ---------------------------------------------------------------------------
# Codegen: execute_code binds game/instance and wraps errors
# ---------------------------------------------------------------------------

def _gen(action_type, params, event_type="step", **kwargs):
    g = ActionCodeGenerator(base_indent=2, **kwargs)
    g.process_action({"action_type": action_type, "parameters": params}, event_type)
    return g.get_code()


def _valid(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    compile(wrapper, "<gen>", "exec")
    return True


def test_execute_code_binds_game_and_instance():
    out = _gen("execute_code", {"code": "self.x += game.score"})
    assert "game = self._script_game()" in out
    assert "instance = self" in out
    assert _valid(out)


def test_execute_code_wraps_errors_like_execute_script():
    out = _gen("execute_code", {"code": "self.x = 1"})
    assert "try:" in out
    assert "except Exception as _code_err:" in out
    assert "[execute_code]" in out
    assert _valid(out)


def test_execute_code_preserves_nested_code_text():
    code = "if self.x > 0:\n    self.x -= 1\nelse:\n    self.x = 0"
    out = _gen("execute_code", {"code": code})
    assert _valid(out)
    # The user's code is now embedded as a repr()'d string literal (exec()'d
    # at runtime, not inlined as literal source — see the module docstring),
    # so it no longer appears as indented Python in the generated source;
    # confirm the text still round-trips through repr() intact.
    assert "if self.x > 0:" in out
    assert "self.x -= 1" in out


def test_empty_execute_code_still_valid_and_no_game_binding_needed():
    out = _gen("execute_code", {"code": ""})
    assert "pass" in out
    assert _valid(out)


# ---------------------------------------------------------------------------
# Real export: the _ScriptGameProxy class exists, is well-formed, and the
# whole generated file still compiles (the strongest available check for a
# .format()-template edit in this file without a full Kivy install).
# ---------------------------------------------------------------------------

SAMPLE = REPO_ROOT / "samples" / "match3_1"


def _sample_project_data():
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = SAMPLE / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    return data


@pytest.fixture(scope="module")
def exported_game_dir():
    out = Path(tempfile.mkdtemp(prefix="kivy_execcode_export_")) / "export"
    assert KivyExporter(_sample_project_data(), SAMPLE, out).export()
    return out / "game"


@pytest.fixture(scope="module")
def exported_main(exported_game_dir):
    return (exported_game_dir / "main.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def exported_base_object(exported_game_dir):
    return (exported_game_dir / "objects" / "base_object.py").read_text(encoding="utf-8")


def test_script_game_proxy_class_present(exported_main):
    assert "class _ScriptGameProxy:" in exported_main
    assert "def score(self):" in exported_main
    assert "def lives(self):" in exported_main
    assert "def health(self):" in exported_main
    assert "@score.setter" in exported_main
    assert "@lives.setter" in exported_main
    assert "@health.setter" in exported_main


def test_script_game_imports_and_returns_the_proxy(exported_base_object):
    # _ScriptGameProxy is defined in main.py but _script_game() is a
    # base_object.py method — it must import the name (this repo's
    # established "from main import <name>" lazy-import pattern for
    # cross-file references in this exporter) rather than reference it as
    # a bare name, or every execute_code/execute_script call raises
    # NameError at runtime. Caught a real instance of exactly this bug
    # during development (the first draft omitted the import).
    assert "from main import _ScriptGameProxy" in exported_base_object
    assert "return _ScriptGameProxy()" in exported_base_object


def test_generated_main_still_compiles(exported_main):
    # The strongest available regression guard for a .format()-template
    # edit: an un-doubled brace or bad indent would break this.
    compile(exported_main, "main.py", "exec")


def test_generated_base_object_still_compiles(exported_base_object):
    compile(exported_base_object, "base_object.py", "exec")


def test_proxy_matches_desktop_no_side_effect_semantics(exported_main):
    # Regression against over-engineering: the setters must be plain
    # attribute writes onto _game_app, with NO caption-update or
    # no_more_lives/no_more_health crossing logic — matching desktop's
    # actual raw-attribute behavior (see module docstring). Extract the
    # class body and confirm it's short/simple rather than calling the
    # heavier set_score()/set_lives()/set_health() module functions (which
    # DO have that side-effect logic, correct for the set_* ACTIONS but
    # wrong here).
    start = exported_main.index("class _ScriptGameProxy:")
    end = exported_main.index("# Whether any object listens to keyboard events.", start)
    # Skip past the docstring — it explains what the class deliberately
    # does NOT do (and says "no_more_lives" while doing so), so only the
    # code after it should be asserted against, not the prose.
    body_start = exported_main.index('"""', exported_main.index('"""', start) + 3) + 3
    proxy_body = exported_main[body_start:end]
    assert "set_score(" not in proxy_body
    assert "set_lives(" not in proxy_body
    assert "set_health(" not in proxy_body
    assert "no_more_lives" not in proxy_body
    assert "no_more_health" not in proxy_body
    assert "_old_lives" not in proxy_body
    assert "_old_health" not in proxy_body

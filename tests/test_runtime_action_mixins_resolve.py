"""Every name a runtime/action_*.py mixin uses must actually be importable,
and every action those mixins define must reach the composed executor.

The File-4 split (docs/POST_1_0_REFACTOR.md) moved 130-odd
`execute_*_action` methods verbatim out of `runtime/action_executor.py` into
sibling mixin modules. Two failure modes are specific to that kind of move and
neither shows up at import time:

1. **A dropped import.** A method that referenced a module-level name in
   action_executor.py (`math`, `logger`, `_hex_to_rgb`, `_ExitEvent`, ...)
   raises NameError only when that branch actually runs -- and action handlers
   are full of branches guarded by `try/except Exception`, so it degrades
   silently rather than crashing. This is the same hazard
   `tests/test_ide_mixins_resolve.py` was built for during File 2, so this
   reuses its scanner rather than re-deriving it.

2. **A mixin left out of the bases.** Adding `runtime/action_x.py` and
   forgetting `class ActionExecutor(..., XMixin)` loses every action in it
   with no error at all: the module imports fine, the class builds fine, and
   the actions simply are not there. The auto-registration scan walks
   `dir(self)`, so it cannot notice something that never joined the class.
"""
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_ide_mixins_resolve import _unresolved  # noqa: E402

RUNTIME = REPO_ROOT / "runtime"
MIXIN_MODULES = sorted(RUNTIME.glob("action_*.py"))


def test_there_are_mixin_modules_to_check():
    """Guards the globs below from silently checking nothing if the files are
    ever renamed."""
    names = {p.name for p in MIXIN_MODULES}
    assert len(names) >= 10, names
    for expected in ("action_drawing.py", "action_movement.py",
                     "action_flow.py", "action_misc.py"):
        assert expected in names


def test_every_runtime_action_mixin_name_resolves():
    problems = {}
    for py in MIXIN_MODULES:
        unresolved = _unresolved(py)
        if unresolved:
            problems[py.name] = unresolved
    assert not problems, "unresolved names (missing imports?):\n" + "\n".join(
        "  %s: %s" % (mod, ", ".join("%s()->%s" % (fn, sorted(names))
                                     for fn, names in fns.items()))
        for mod, fns in problems.items())


def _actions_defined_in(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = set()
    for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        for fn in cls.body:
            if isinstance(fn, ast.FunctionDef) and fn.name.startswith("execute_"):
                found.add(fn.name)
    return found


def test_every_mixin_action_reaches_the_composed_executor():
    """The "forgot to add it to the bases" case. A mixin module that is never
    inherited loses all of its actions silently."""
    from runtime.action_executor import ActionExecutor

    missing = {}
    for py in MIXIN_MODULES:
        absent = sorted(name for name in _actions_defined_in(py)
                        if not hasattr(ActionExecutor, name))
        if absent:
            missing[py.name] = absent
    assert not missing, (
        "these mixin modules define actions the executor does not expose -- "
        "is the mixin missing from `class ActionExecutor(...)`?\n%s" % missing)


def test_the_mixins_actually_contribute_most_of_the_actions():
    """Stops the split being quietly undone. If someone copies methods back
    onto the base, this notices the balance shifting."""
    from runtime.action_executor import ActionExecutor

    from_mixins = set()
    for py in MIXIN_MODULES:
        from_mixins |= _actions_defined_in(py)

    on_class = {n for n in dir(ActionExecutor)
                if n.startswith("execute_") and n.endswith("_action")}
    contributed = {n for n in from_mixins if n.endswith("_action")}

    assert len(contributed) > 100, len(contributed)
    assert contributed <= on_class
    # The base keeps dispatch, not actions.
    left_on_base = on_class - contributed
    assert not left_on_base, (
        "actions still defined on the base rather than a mixin: %s"
        % sorted(left_on_base))


def test_registered_handlers_include_actions_from_every_mixin():
    """End to end: auto-registration walks dir(self), so this proves the
    mixin-contributed methods really are registered and dispatchable."""
    from runtime.action_executor import ActionExecutor

    executor = ActionExecutor()
    registered = executor.action_handlers

    for sample in ("draw_text", "set_hspeed", "set_score", "goto_room",
                   "create_instance", "burst_particles", "if_condition",
                   "set_sprite", "save_game", "show_message", "set_variable"):
        assert sample in registered, (
            "%s is not registered; its mixin may not be composed in" % sample)

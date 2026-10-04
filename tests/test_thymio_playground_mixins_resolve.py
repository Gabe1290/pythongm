"""Every name a extensions/thymio/editor/_*.py mixin uses must actually be
importable.

The Thymio-extraction follow-up (docs/PROJECT_STATUS.md: "splitting
widgets/thymio_playground.py into smaller modules") moves
ThymioPlaygroundWindow methods verbatim into mixin modules, mirroring
core/ide_window.py's own File 2 split (tests/test_ide_mixins_resolve.py).
A method that referenced a module-level name in playground_window.py
(pygame, EditMode, COLOR_BACKGROUND, ...) breaks *silently* if the new
module forgets to import it -- often inside a try/except that swallows the
NameError, same failure mode test_ide_mixins_resolve.py's own docstring
describes for the ide_window.py split.

This test AST-scans each new mixin: every Name loaded anywhere (including
deep inside nested if/try/with) must resolve to a module global, a
builtin, or a binding local to its function (parameter / assignment /
for-target / comprehension / `except ... as` / nested def name). Anything
left over is a missing import.

Scoped to an explicit file list, not a `_*.py` glob -- unlike
core/ide/, extensions/thymio/editor/ already held unrelated pre-existing
files that happen to start with an underscore (``__init__.py``) before
this split; globbing would scan code this change never touched.
"""
import ast
import builtins
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PKG = REPO_ROOT / "extensions" / "thymio" / "editor"
MIXIN_FILES = [
    "_constants.py", "_camera.py", "_simulation.py", "_status.py",
    "_input.py", "_resize.py", "_undo.py",
]
# `__builtins__` is present in every module's globals but is not an
# attribute of the builtins module itself, so dir(builtins) misses it.
_BUILTINS = set(dir(builtins)) | {"__file__", "__name__", "__doc__",
                                  "__class__", "__builtins__"}


def _module_globals(tree):
    g = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                g.add(a.asname or a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                g.add((a.asname or a.name).split(".")[0])
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            g.add(n.name)
        if isinstance(n, ast.Assign):
            for t in n.targets:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name):
                        g.add(x.id)
    return g


def _function_bindings(fn):
    b = {"self", "cls"}
    a = fn.args
    for arg in a.args + a.kwonlyargs + getattr(a, "posonlyargs", []):
        b.add(arg.arg)
    if a.vararg:
        b.add(a.vararg.arg)
    if a.kwarg:
        b.add(a.kwarg.arg)
    for n in ast.walk(fn):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for al in n.names:
                b.add((al.asname or al.name).split(".")[0])
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name):
                        b.add(x.id)
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
            tgt = n.target
            for x in ast.walk(tgt):
                if isinstance(x, ast.Name):
                    b.add(x.id)
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension)):
            for x in ast.walk(n.target):
                if isinstance(x, ast.Name):
                    b.add(x.id)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            b.add(n.name)
        elif isinstance(n, ast.withitem) and n.optional_vars:
            for x in ast.walk(n.optional_vars):
                if isinstance(x, ast.Name):
                    b.add(x.id)
        elif isinstance(n, ast.ClassDef):
            b.add(n.name)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            b.add(getattr(n, "name", ""))
            aa = n.args
            for arg in aa.args + aa.kwonlyargs + getattr(aa, "posonlyargs", []):
                b.add(arg.arg)
            if aa.vararg:
                b.add(aa.vararg.arg)
            if aa.kwarg:
                b.add(aa.kwarg.arg)
        elif isinstance(n, ast.Global):
            b.update(n.names)
    return b


def _unresolved(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    g = _module_globals(tree)
    bad = {}
    for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        for fn in [n for n in cls.body
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            local = _function_bindings(fn)
            for n in ast.walk(fn):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    if n.id not in g and n.id not in _BUILTINS and n.id not in local:
                        bad.setdefault(fn.name, set()).add(n.id)
    return bad


def test_every_mixin_name_resolves():
    problems = {}
    for name in MIXIN_FILES:
        py = PKG / name
        u = _unresolved(py)
        if u:
            problems[py.name] = u
    assert not problems, "unresolved names (missing imports?):\n" + "\n".join(
        f"  {mod}: " + ", ".join(f"{fn}()->{sorted(names)}" for fn, names in fns.items())
        for mod, fns in problems.items()
    )


def test_playground_window_composes_every_mixin():
    """Belt-and-braces: the skeleton actually inherits from all six mixins,
    not just imports them (an import with no base-class wiring would still
    satisfy the resolver test above while silently losing every method)."""
    from extensions.thymio.playground_window import ThymioPlaygroundWindow
    from extensions.thymio.editor._camera import CameraMixin
    from extensions.thymio.editor._simulation import SimulationMixin
    from extensions.thymio.editor._status import StatusMixin
    from extensions.thymio.editor._input import InputMixin
    from extensions.thymio.editor._resize import ResizeMixin
    from extensions.thymio.editor._undo import UndoMixin

    for mixin in (CameraMixin, SimulationMixin, StatusMixin, InputMixin,
                  ResizeMixin, UndoMixin):
        assert issubclass(ThymioPlaygroundWindow, mixin), mixin.__name__

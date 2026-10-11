"""Regression test for main.py's LIBGL_ALWAYS_SOFTWARE fallback.

Real classroom crash, 2026-10-11, the sequel to the Blockly-tab fixes in
5908b2ae/0dc7aeac: after those landed, the same user's compiled Linux build
crashed a second way -- this time clicking "Test Game" -- with Mesa failing
to find the DRI_Mesa extension, EGL failing to init its GBM device, and a
fatal X BadAccess on glXMakeCurrent. Test Game runs pygame's SDL window
in-process with Qt for a packaged build (core/ide/_test_game.py's
is_packaged branch -- there's no separate interpreter to subprocess into),
so SDL's own GLX probing contends with Qt's already-active EGL/GBM session
over the same hardware DRM device. Forcing Mesa to its software rasterizer
for the whole process (LIBGL_ALWAYS_SOFTWARE=1) means neither side ever
touches the DRM/GBM device, so there's nothing left to contend over.

main.py has heavy module-level side effects (Qt imports, a Python-version
gate that can sys.exit), so this extracts just the small, self-contained
if-block that sets the env var via AST and execs it in isolation -- same
technique tests/test_pyinstaller_libstdcxx_exclusion.py uses for the .spec
file's filter function, for the same reason (the surrounding file can't be
safely imported/exec'd wholesale in a test).
"""
import ast
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

MAIN_PATH = Path(__file__).parent.parent / "main.py"


def _find_libgl_if_node():
    source = MAIN_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MAIN_PATH))
    for node in tree.body:
        if isinstance(node, ast.If) and "LIBGL_ALWAYS_SOFTWARE" in ast.dump(node):
            return node
    raise AssertionError("No top-level `if` block in main.py sets LIBGL_ALWAYS_SOFTWARE")


def _run_block(platform, pre_existing_env=None):
    """Exec the extracted if-block against fake sys/os stand-ins so the
    real process's actual os.environ and sys.platform are never touched."""
    node = _find_libgl_if_node()
    fake_environ = dict(pre_existing_env or {})
    fake_sys = SimpleNamespace(platform=platform)
    fake_os = SimpleNamespace(environ=fake_environ)
    namespace = {"sys": fake_sys, "os": fake_os}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(MAIN_PATH), "exec"), namespace)
    return fake_environ


def test_block_exists():
    assert _find_libgl_if_node() is not None


@pytest.mark.parametrize("platform", ["linux", "linux2", "freebsd12"])
def test_sets_the_env_var_on_non_windows_non_macos(platform):
    env = _run_block(platform)
    assert env.get("LIBGL_ALWAYS_SOFTWARE") == "1"


@pytest.mark.parametrize("platform", ["win32", "darwin"])
def test_does_not_set_the_env_var_on_windows_or_macos(platform):
    env = _run_block(platform)
    assert "LIBGL_ALWAYS_SOFTWARE" not in env


def test_does_not_override_an_explicit_user_setting():
    """setdefault, not a plain assignment -- a user who deliberately wants
    real hardware GL (e.g. to debug a graphics issue) isn't overridden."""
    env = _run_block("linux", pre_existing_env={"LIBGL_ALWAYS_SOFTWARE": "0"})
    assert env["LIBGL_ALWAYS_SOFTWARE"] == "0"


def test_block_precedes_any_qt_or_pygame_import():
    """Mutation guard: the block must run before Qt is ever imported, or
    Mesa may have already made its driver decision. Confirms the textual
    position in main.py -- before the first `from PySide6` import and
    before setup_qtwebengine_paths() is called."""
    source = MAIN_PATH.read_text(encoding="utf-8")
    libgl_idx = source.index("LIBGL_ALWAYS_SOFTWARE")
    first_pyside_import_idx = source.index("from PySide6")
    call_idx = source.index("setup_qtwebengine_paths()\n")
    assert libgl_idx < first_pyside_import_idx
    assert libgl_idx < call_idx

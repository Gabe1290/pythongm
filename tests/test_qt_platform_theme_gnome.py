"""Regression test for main.py's GNOME Qt-platform-theme default.

Real crash, 2026-11-14, Ubuntu 26.04 (GNOME): the IDE aborted at startup with
"GLib-GIO-ERROR: Settings schema 'org.gnome.settings-daemon.plugins.xsettings'
does not contain a key named 'antialiasing'" -- "core dumped" before the window
appeared. Qt's GTK3 platform theme reads that key, newer GNOME removed it, and
GLib aborts the process on a missing key. QT_QPA_PLATFORMTHEME=xdgdesktopportal
crashed identically (it delegates to GTK3 on GNOME); 'generic' worked.

Same AST-extract-and-exec technique as tests/test_libgl_always_software.py:
main.py has heavy module-level side effects and can't be imported in a test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

MAIN_PATH = Path(__file__).parent.parent / "main.py"


def _find_theme_if_node():
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8"), filename=str(MAIN_PATH))
    for node in tree.body:
        if isinstance(node, ast.If) and "QT_QPA_PLATFORMTHEME" in ast.dump(node):
            return node
    raise AssertionError("No top-level `if` block in main.py sets QT_QPA_PLATFORMTHEME")


def _run_block(platform, env=None):
    """Exec the extracted block against fake sys/os so the real process's
    environment is never touched."""
    fake_environ = dict(env or {})
    namespace = {
        "sys": SimpleNamespace(platform=platform),
        "os": SimpleNamespace(environ=fake_environ),
    }
    module = ast.Module(body=[_find_theme_if_node()], type_ignores=[])
    exec(compile(module, str(MAIN_PATH), "exec"), namespace)
    return fake_environ


@pytest.mark.parametrize("desktop", ["ubuntu:GNOME", "GNOME", "gnome", "GNOME-Classic:GNOME"])
def test_defaults_to_generic_on_gnome(desktop):
    env = _run_block("linux", {"XDG_CURRENT_DESKTOP": desktop})
    assert env["QT_QPA_PLATFORMTHEME"] == "generic"


@pytest.mark.parametrize("desktop", ["KDE", "XFCE", "X-Cinnamon", "", "GNOMEISH"])
def test_leaves_other_desktops_alone(desktop):
    env = _run_block("linux", {"XDG_CURRENT_DESKTOP": desktop})
    assert "QT_QPA_PLATFORMTHEME" not in env


def test_leaves_unset_desktop_alone():
    assert "QT_QPA_PLATFORMTHEME" not in _run_block("linux", {})


def test_does_not_override_an_explicit_user_setting():
    env = _run_block("linux", {"XDG_CURRENT_DESKTOP": "ubuntu:GNOME",
                               "QT_QPA_PLATFORMTHEME": "gtk3"})
    assert env["QT_QPA_PLATFORMTHEME"] == "gtk3"


def test_empty_setting_counts_as_unset():
    """Qt treats an empty value as unset and would pick GTK3 again."""
    env = _run_block("linux", {"XDG_CURRENT_DESKTOP": "ubuntu:GNOME",
                               "QT_QPA_PLATFORMTHEME": ""})
    assert env["QT_QPA_PLATFORMTHEME"] == "generic"


@pytest.mark.parametrize("platform", ["win32", "darwin"])
def test_not_applied_on_windows_or_macos(platform):
    env = _run_block(platform, {"XDG_CURRENT_DESKTOP": "GNOME"})
    assert "QT_QPA_PLATFORMTHEME" not in env


def test_block_precedes_any_qt_import():
    """The platform theme is chosen when QApplication is built; the env var
    must be set before Qt is imported at all."""
    source = MAIN_PATH.read_text(encoding="utf-8")
    theme_idx = source.index("os.environ['QT_QPA_PLATFORMTHEME']")
    assert theme_idx < source.index("from PySide6")
    assert theme_idx < source.index("setup_qtwebengine_paths()\n")

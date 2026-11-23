"""Regression tests: a language change refills the main toolbar, never replaces it.

Real crash (classroom 2026-11-18, reproduced on the dev box 2026-11-23): the
IDE segfaulted right after its window appeared, on EVERY launch, for any
non-English language once a maximised window layout had been saved
(window_geometry_b64 + window_state_b64 in config.json). Startup sends a
LanguageChange to every widget; the main window's changeEvent deleted the
"MainToolbar" and built a new one. After restoreState() of a maximised
window, Qt's QMainWindowLayout still points at the original toolbar until
the resize finishes, so the maximise walked a dangling pointer
(gdb: QSizeGrip::eventFilter -> QLayout::activate -> call to 0x0).

The offscreen platform has no window manager and cannot maximise, so it
does not reproduce the crash itself. The CI test pins the invariant that
removes it (same toolbar object, refilled, never duplicated); the real-screen
test replays the exact crash and runs only where an X display exists.
"""

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def ide():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from core.ide_window import PyGameMakerIDE
    window = PyGameMakerIDE()
    yield window
    window.close()
    window.deleteLater()


def _toolbars(window):
    from PySide6.QtWidgets import QToolBar
    return [t for t in window.findChildren(QToolBar)
            if t.objectName() == "MainToolbar"]


def _send_language_change(window):
    from PySide6.QtCore import QCoreApplication, QEvent
    QCoreApplication.sendEvent(window, QEvent(QEvent.Type.LanguageChange))
    QCoreApplication.processEvents()  # run any deleteLater


def test_language_change_keeps_the_same_toolbar_object(ide):
    import shiboken6
    before = _toolbars(ide)
    assert len(before) == 1
    toolbar = before[0]
    actions_before = [a.objectName() or a.text() for a in toolbar.actions()]
    assert actions_before

    _send_language_change(ide)
    _send_language_change(ide)

    after = _toolbars(ide)
    assert len(after) == 1, "a language change must not add a second toolbar"
    assert shiboken6.isValid(toolbar), "the original toolbar was deleted"
    assert after[0] is toolbar, "the toolbar was replaced instead of refilled"
    assert [a.objectName() or a.text() for a in toolbar.actions()] == actions_before


def test_language_change_does_not_delete_or_remove_the_toolbar():
    """Source guard: the changeEvent path must not removeToolBar/deleteLater."""
    import ast
    src = (REPO / "core" / "ide_window.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "changeEvent")
    calls = {getattr(n.func, "attr", "") for n in ast.walk(fn) if isinstance(n, ast.Call)}
    assert "removeToolBar" not in calls
    assert "deleteLater" not in calls


# --- real screen: replay the crash ------------------------------------------

def _x_display_usable():
    if sys.platform != "linux" or not os.environ.get("DISPLAY"):
        return False
    try:
        out = subprocess.run(
            [sys.executable, "-c",
             "from PySide6.QtWidgets import QApplication; QApplication([]); print('ok')"],
            env=dict(os.environ, QT_QPA_PLATFORM="xcb"),
            capture_output=True, text=True, timeout=30)
        return "ok" in out.stdout
    except Exception:
        return False


DRIVER = textwrap.dedent("""
    import os, runpy, sys
    sys.path.insert(0, os.getcwd())
    sys.argv = [sys.argv[0]]
    mod = runpy.run_path("main.py", run_name="pygm_main")
    from PySide6.QtCore import QTimer
    cls = mod["PyGameMakerIDE"]
    orig = cls.show
    def show(self):
        orig(self)
        QTimer.singleShot(5000, lambda: (print("SURVIVED", flush=True), os._exit(0)))
    cls.show = show
    mod["main"]()
""")

# The exact layout saved on the machine that crashed: a maximised 1920x1032
# window with the main toolbar and the tutorial dock (Qt saveGeometry /
# saveState, base64 as config.json stores them).
CRASHING_GEOMETRY = ("AdnQywADAAAAAAAAAAAAAAAAB38AAAQHAAACVwAAACUAAAY+AAAC4AAAAAACAAAA"
                     "B4AAAAAAAAAAJQAAB38AAAQH")
CRASHING_STATE = ("AAAA/wAAAAD9AAAAAQAAAAEAAAFoAAACV/wCAAAAAfsAAAAYAFQAdQB0AG8AcgBpAGEA"
                  "bABEAG8AYwBrAQAAAEYAAAJXAAAAAAAAAAAAAAeAAAADfgAAAAQAAAAEAAAACAAAAAj8"
                  "AAAAAQAAAAIAAAABAAAAFgBNAGEAaQBuAFQAbwBvAGwAYgBhAHIBAAAAAP////8AAAAA"
                  "AAAAAA==")


@pytest.mark.skipif(not _x_display_usable(), reason="needs a real X display")
@pytest.mark.parametrize("language", ["fr", "pt"])
def test_maximised_saved_layout_in_another_language_does_not_crash(tmp_path, language):
    """Segfaulted (rc 139) before the fix, every time, on the dev box."""
    home = tmp_path / "home"
    (home / ".pygamemaker").mkdir(parents=True)
    (home / ".pygamemaker" / "config.json").write_text(json.dumps({
        "language": language,
        "window_geometry_b64": CRASHING_GEOMETRY,
        "window_state_b64": CRASHING_STATE,
    }), encoding="utf-8")
    env = dict(os.environ, HOME=str(home), QT_QPA_PLATFORM="xcb",
               PYGM_ALLOW_MULTIPLE_INSTANCES="1",
               XDG_CONFIG_HOME=str(home / ".config"),
               XDG_DATA_HOME=str(home / ".local" / "share"),
               XDG_CACHE_HOME=str(home / ".cache"))
    proc = subprocess.run([sys.executable, "-c", DRIVER], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=90)
    assert "SURVIVED" in proc.stdout, (proc.returncode, proc.stdout[-2000:], proc.stderr[-2000:])

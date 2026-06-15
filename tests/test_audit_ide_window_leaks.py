"""
Regression tests for core/ide_window.py audit findings L3 and L4.

L3 — test_game must not leak the stderr-capture temp file / open fd when
subprocess.Popen raises (e.g. interpreter or run_game.py missing on a
misconfigured install). The except handler previously showed a dialog but
never closed _game_stderr_handle nor unlinked _game_stderr_path, so each
failed F5 orphaned a /tmp/pygm2_game_*.log.

L4 — show_thymio_playground must reuse a live window and set WA_DeleteOnClose
rather than constructing a new ThymioPlaygroundWindow (retaining pygame
surfaces + a 60 FPS simulator) on every open and overwriting the only
reference.

Both tests drive the real PyGameMakerIDE methods against lightweight stubs so
they do not need a fully constructed IDE; they construct a real offscreen
QApplication rather than using pytest-qt, so they run on Python 3.11 too.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_test_game_cleans_stderr_capture_on_popen_failure(_qapp, tmp_path, monkeypatch):
    """L3: a Popen failure must close the handle and unlink the temp log."""
    import subprocess
    from PySide6.QtWidgets import QMessageBox
    from core import ide_window
    from core.ide_window import PyGameMakerIDE

    # A real project dir with project.json so test_game reaches the Popen call.
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "project.json").write_text("{}", encoding="utf-8")

    # Make is_packaged() detection fall through to the subprocess path: keep
    # sys.executable existing and __file__ outside /tmp (it already is).
    monkeypatch.setattr(subprocess, "Popen",
                         lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("boom")))
    # Don't pop a modal dialog in the headless except handler.
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: None))

    class Stub:
        current_project_path = project_dir
        game_runner = type("GR", (), {"test_game": lambda self, *a, **k: True})()

        # Use the real cleanup routine — that is the fix under test.
        _drain_game_stderr = PyGameMakerIDE._drain_game_stderr

        def _iter_open_editors(self):
            return iter(())

        def save_project(self):
            pass

        def _show_validation_warnings(self):
            pass

        def update_status(self, *a, **k):
            pass

        def tr(self, s, *a, **k):
            return s

    import tempfile
    tmpdir = Path(tempfile.gettempdir())
    before = set(tmpdir.glob("pygm2_game_*.log"))

    stub = Stub()
    stub._game_process = None
    stub._game_stderr_handle = None
    stub._game_stderr_path = None

    # Run the real method bound to the stub.
    PyGameMakerIDE.test_game(stub)

    # The handle/path attrs are reset and no NEW temp log survives the failure.
    assert stub._game_stderr_handle is None
    assert stub._game_stderr_path is None
    after = set(tmpdir.glob("pygm2_game_*.log"))
    leaked = after - before
    assert leaked == set(), f"leaked stderr temp file(s) on Popen failure: {leaked}"


def test_show_thymio_playground_reuses_window_and_deletes_on_close(_qapp, monkeypatch):
    """L4: second open reuses the first live window; WA_DeleteOnClose is set."""
    from PySide6.QtCore import Qt
    from core.ide_window import PyGameMakerIDE
    import widgets.thymio_playground as tp

    created = []

    class FakePlayground:
        def __init__(self, parent):
            self.parent = parent
            self._attrs = set()
            self.shown = 0
            self.raised = 0
            created.append(self)

        def setAttribute(self, attr):
            self._attrs.add(attr)

        def show(self):
            self.shown += 1

        def showNormal(self):
            self.shown += 1

        def raise_(self):
            self.raised += 1

        def activateWindow(self):
            pass

    monkeypatch.setattr(tp, "ThymioPlaygroundWindow", FakePlayground)

    # isValid is imported inside the method from shiboken6; make our fake count
    # as a live object.
    import shiboken6
    monkeypatch.setattr(shiboken6, "isValid", lambda obj: obj in created)

    class Stub:
        def tr(self, s, *a, **k):
            return s

    stub = Stub()

    PyGameMakerIDE.show_thymio_playground(stub)
    assert len(created) == 1, "first open should construct one window"
    first = created[0]
    assert Qt.WA_DeleteOnClose in first._attrs, "WA_DeleteOnClose not set"

    # Second open with the window still live must NOT construct a new one.
    PyGameMakerIDE.show_thymio_playground(stub)
    assert len(created) == 1, "second open leaked a new window instead of reusing"
    assert first.raised >= 1, "existing window not raised on reopen"

    # After the window is closed (no longer valid), a new open creates one.
    monkeypatch.setattr(shiboken6, "isValid", lambda obj: False)
    PyGameMakerIDE.show_thymio_playground(stub)
    assert len(created) == 2, "a fresh window should be created once the old one is gone"

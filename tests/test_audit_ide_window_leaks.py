"""
Regression test for core/ide_window.py audit finding L3.

L3 — test_game must not leak the stderr-capture temp file / open fd when
subprocess.Popen raises (e.g. interpreter or run_game.py missing on a
misconfigured install). The except handler previously showed a dialog but
never closed _game_stderr_handle nor unlinked _game_stderr_path, so each
failed F5 orphaned a /tmp/pygm2_game_*.log.

Drives the real PyGameMakerIDE.test_game against a lightweight stub so it
does not need a fully constructed IDE; constructs a real offscreen
QApplication rather than using pytest-qt, so it runs on Python 3.11 too.

(L4 — show_thymio_playground reusing a live window — moved to
tests/test_thymio_extension.py's Stage G section once that method moved to
extensions/thymio/tools_menu.py, docs/THYMIO_EXTENSION_PLAN.md.)
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
        # test_game delegates the actual launch to _run_project_json
        # (factored out so test_object/"Play Object" can reuse it) — the
        # stub needs the real implementation too, not just the methods it
        # directly calls itself.
        _run_project_json = PyGameMakerIDE._run_project_json

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

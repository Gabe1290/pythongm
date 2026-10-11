"""Regression test for genuine process isolation on Test Game / Debug Game,
even for a packaged (frozen) build.

Real classroom crash, confirmed recurring on v1.5.1-1.5.3 despite the
LIBGL_ALWAYS_SOFTWARE fix: clicking Test Game in the compiled Linux build
died with "X Error of failed request: BadAccess ... X_GLXMakeCurrent".
core/ide/_test_game.py's packaged branch used to run the game IN-PROCESS
(self.game_runner.test_game(...)), sharing this process's X11/GLX/EGL state
with Qt -- the actual conflict, which forcing Mesa to software rendering
didn't fix, because it isn't about which Mesa driver loads, it's Qt and SDL
sharing one process's connection to the graphics subsystem at all.

The fix: a packaged build's sys.executable is a real, directly re-runnable
path to the SAME compiled onefile binary (confirmed by PyInstaller's own
documented support for this), so _run_project_json now ALWAYS launches a
subprocess -- for a packaged build, by relaunching itself with a
"--pygm-run-game" sentinel main.py checks for before any Qt import.
debug_game() (a second, independent in-process caller with the exact same
bug, not even gated behind the packaged/dev check) now delegates to
_run_project_json too, instead of its own separate game_runner.test_game(...)
call.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


class _Stub:
    """Minimal stand-in for PyGameMakerIDE, matching
    test_audit_ide_window_leaks.py's established pattern."""
    current_project_path = None
    game_runner = None  # intentionally never touched by the fixed code

    from core.ide_window import PyGameMakerIDE as _IDE
    _drain_game_stderr = _IDE._drain_game_stderr
    _run_project_json = _IDE._run_project_json
    debug_game = _IDE.debug_game
    _minimize_for_test_game = _IDE._minimize_for_test_game
    _restore_after_test_game = _IDE._restore_after_test_game
    bring_to_front = _IDE.bring_to_front
    del _IDE

    def __init__(self):
        self._pre_test_game_maximized = False
        self._game_process = None

    def _iter_open_editors(self):
        return iter(())

    def save_project(self):
        pass

    class project_manager:
        @staticmethod
        def is_dirty():
            return False

    def _show_validation_warnings(self):
        pass

    def update_status(self, *a, **k):
        pass

    def tr(self, s, *a, **k):
        return s

    def isMinimized(self):
        return False

    def showMinimized(self):
        pass

    def showNormal(self):
        pass

    def showMaximized(self):
        pass

    def windowState(self):
        from PySide6.QtCore import Qt
        return Qt.WindowState.WindowNoState

    def raise_(self):
        pass

    def activateWindow(self):
        pass


def _project_dir(tmp_path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "project.json").write_text("{}", encoding="utf-8")
    return project_dir


def test_packaged_build_relaunches_itself_with_sentinel(_qapp, tmp_path, monkeypatch):
    """The core of the fix: when frozen, the subprocess argv must be
    [sys.executable, '--pygm-run-game', project_json, language] -- NOT a
    call into self.game_runner.test_game (the removed in-process path)."""
    captured = {}

    def fake_popen(argv, **kwargs):
        captured['argv'] = argv
        raise FileNotFoundError("stubbed, never actually launched")

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    try:
        from PySide6.QtWidgets import QMessageBox
        monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: None))

        stub = _Stub()
        stub.current_project_path = _project_dir(tmp_path)
        stub._run_project_json(stub.current_project_path)

        assert 'argv' in captured, "Popen was never called"
        argv = captured['argv']
        assert argv[0] == sys.executable
        assert argv[1] == "--pygm-run-game"
        assert argv[2] == str(stub.current_project_path / "project.json")
    finally:
        monkeypatch.delattr(sys, "frozen", raising=False)


def test_non_packaged_build_launches_run_game_script(_qapp, tmp_path, monkeypatch):
    """Dev/source runs keep their existing shape: a real Python interpreter
    running runtime/run_game.py as a script -- unaffected by this fix."""
    captured = {}

    def fake_popen(argv, **kwargs):
        captured['argv'] = argv
        raise FileNotFoundError("stubbed, never actually launched")

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: None))

    stub = _Stub()
    stub.current_project_path = _project_dir(tmp_path)
    stub._run_project_json(stub.current_project_path)

    argv = captured['argv']
    assert argv[0] == sys.executable
    assert argv[1].endswith(str(Path("runtime") / "run_game.py"))
    assert argv[2] == str(stub.current_project_path / "project.json")


def test_debug_game_delegates_to_run_project_json_not_game_runner(_qapp, tmp_path, monkeypatch):
    """debug_game() used to call self.game_runner.test_game(...) directly,
    in-process, unconditionally -- the same bug as test_game's old packaged
    branch, but with no packaged/dev gate at all. It must now go through
    the same (now subprocess-only) _run_project_json path."""
    captured = {}

    def fake_popen(argv, **kwargs):
        captured['argv'] = argv
        raise FileNotFoundError("stubbed, never actually launched")

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: None))
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))

    stub = _Stub()
    stub.current_project_path = _project_dir(tmp_path)
    stub.debug_game()

    assert 'argv' in captured, "debug_game never reached the subprocess launch path"
    # stub.game_runner stays None throughout -- if debug_game still called
    # game_runner.test_game(...), this would raise AttributeError on None
    # before Popen was ever reached.
    assert stub.game_runner is None


def test_debug_game_checks_game_process_not_game_runner(_qapp, tmp_path, monkeypatch):
    """The 'already running' guard must check self._game_process (the
    subprocess handle _run_project_json manages), not
    self.game_runner.is_game_running() (the removed in-process object)."""
    from PySide6.QtWidgets import QMessageBox
    informed = []
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: informed.append(a)))

    stub = _Stub()
    stub.current_project_path = _project_dir(tmp_path)

    class _FakeRunningProcess:
        def poll(self):
            return None  # still running

    stub._game_process = _FakeRunningProcess()
    stub.debug_game()

    assert informed, "debug_game should have shown the 'already running' dialog"


def test_main_py_dispatches_pygm_run_game_before_any_qt_import():
    """Confirms the real end-to-end dispatch, not just the argv the IDE
    builds: running main.py with --pygm-run-game as a genuine subprocess
    must reach runtime.run_game and never touch Qt (no
    'QtWebEngine paths configured' / 'Qt patch loaded' banner lines main.py
    only prints on the normal IDE-launch path)."""
    project = REPO_ROOT / "samples" / "views_1" / "project.json"
    assert project.exists()

    env = dict(os.environ)
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PYGM_MAX_FRAMES"] = "3"

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "main.py"), "--pygm-run-game", str(project), "en"],
        cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PYGM_FRAMES_COMPLETED=3" in result.stdout
    assert "QtWebEngine paths configured" not in result.stdout
    assert "Qt patch loaded" not in result.stdout

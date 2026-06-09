"""
Regression tests for Test-Game subprocess supervision in PyGameMakerIDE.

Two narrow gaps are covered:
  1. A crashing game's stderr is captured to a temp file and surfaced on a
     non-zero exit (it used to vanish to a discarded stderr), and the temp
     file is always cleaned up.
  2. Stopping the game (e.g. on IDE close) terminates the child and drains its
     stderr capture — closeEvent now calls stop_game() so the subprocess isn't
     orphaned.

These call the methods unbound on a lightweight stub to avoid standing up the
full Qt IDE window (heavy; the widget suite skips it on 3.11 anyway). The
project logger lives under the "pygm" tree with propagate=False, so we patch
the module logger rather than relying on caplog.
"""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _capture(content: str):
    """An open stderr capture (handle + temp file) like run_game() sets up."""
    fd, path = tempfile.mkstemp(prefix='pygm2_test_', suffix='.log')
    handle = os.fdopen(fd, 'w')
    handle.write(content)
    handle.flush()
    return handle, path


class TestDrainGameStderr:

    def test_nonzero_exit_logs_captured_stderr(self):
        ide = _ide_cls()
        handle, path = _capture("Traceback (most recent call last):\nBoom")
        stub = SimpleNamespace(_game_stderr_handle=handle, _game_stderr_path=path)

        with patch('core.ide_window.logger') as log:
            ide._drain_game_stderr(stub, 3)

        msg = "\n".join(str(c.args[0]) for c in log.error.call_args_list)
        assert "Boom" in msg
        assert "exit 3" in msg
        assert not os.path.exists(path)        # temp file cleaned up
        assert stub._game_stderr_handle is None  # capture state cleared
        assert stub._game_stderr_path is None

    def test_clean_exit_does_not_log_but_still_cleans_up(self):
        ide = _ide_cls()
        handle, path = _capture("some incidental stderr noise")
        stub = SimpleNamespace(_game_stderr_handle=handle, _game_stderr_path=path)

        with patch('core.ide_window.logger') as log:
            ide._drain_game_stderr(stub, 0)

        log.error.assert_not_called()
        assert not os.path.exists(path)

    def test_no_capture_active_is_safe(self):
        ide = _ide_cls()
        stub = SimpleNamespace()  # no capture attrs at all
        ide._drain_game_stderr(stub, 1)  # must not raise
        assert stub._game_stderr_handle is None
        assert stub._game_stderr_path is None

    def test_idempotent(self):
        ide = _ide_cls()
        handle, path = _capture("x")
        stub = SimpleNamespace(_game_stderr_handle=handle, _game_stderr_path=path)
        ide._drain_game_stderr(stub, 1)
        ide._drain_game_stderr(stub, 1)  # second call: no crash, no resurrection
        assert not os.path.exists(path)


class _FakeProcess:
    def __init__(self, exit_code=0, hang=False):
        self.exit_code = exit_code
        self.hang = hang
        self.terminated = False
        self.killed = False

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        if self.hang:
            import subprocess
            raise subprocess.TimeoutExpired(cmd="game", timeout=timeout)
        return self.exit_code

    def kill(self):
        self.killed = True


def _stop_stub(ide, proc):
    handle, path = _capture("late crash output")
    stub = SimpleNamespace(
        _game_process=proc,
        _check_game_timer=None,
        _game_stderr_handle=handle,
        _game_stderr_path=path,
        update_status=lambda *a, **k: None,
        tr=lambda s: s,
    )
    # Bind the real drain method so stop_game's self._drain_game_stderr resolves.
    stub._drain_game_stderr = ide._drain_game_stderr.__get__(stub)
    return stub, path


class TestStopGame:

    def test_terminates_and_drains(self):
        ide = _ide_cls()
        proc = _FakeProcess(exit_code=0)
        stub, path = _stop_stub(ide, proc)

        ide.stop_game(stub)

        assert proc.terminated
        assert stub._game_process is None
        assert not os.path.exists(path)  # stderr capture cleaned up

    def test_kills_a_hung_child(self):
        ide = _ide_cls()
        proc = _FakeProcess(hang=True)
        stub, path = _stop_stub(ide, proc)

        ide.stop_game(stub)

        assert proc.terminated and proc.killed
        assert not os.path.exists(path)

    def test_safe_with_no_running_game(self):
        ide = _ide_cls()
        stub = SimpleNamespace(update_status=lambda *a, **k: None, tr=lambda s: s)
        stub._drain_game_stderr = ide._drain_game_stderr.__get__(stub)
        ide.stop_game(stub)  # no process / timer / capture — must not raise

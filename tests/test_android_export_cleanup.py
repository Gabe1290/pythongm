"""Regression tests for Android export L23 (cleanup on failure) and L24
(cancel returns sentinel, no bogus failure emit), plus the silent-build
cancel/timeout follow-up (a stalled buildozer that produces no stdout must
still honor Cancel and the wall-clock ceiling — the read loop is fed by a
daemon thread so it can't block on a silent pipe)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_build_dir_cleaned_on_failure(_qapp, tmp_path, monkeypatch):
    import export.android.android_exporter as mod
    ex = mod.AndroidExporter()

    build_dir = tmp_path / "pygm_android_xyz"
    build_dir.mkdir()
    (build_dir / "junk.txt").write_text("x", encoding="utf-8")

    # Bypass platform / dependency / project gates.
    monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)
    monkeypatch.setattr(ex, "_check_buildozer", lambda: True)
    monkeypatch.setattr(ex, "_check_kivy", lambda: True)
    monkeypatch.setattr(ex, "_check_cython", lambda: True)
    monkeypatch.setattr(ex, "_check_java", lambda: True)
    monkeypatch.setattr(ex, "_check_build_tools", lambda: [])
    monkeypatch.setattr(ex, "_create_build_directory", lambda: build_dir)
    # Fail at the first build step.
    monkeypatch.setattr(ex, "_generate_kivy_game", lambda b: False)

    result = ex.export_project("proj", str(tmp_path / "out"), {})
    assert result is False
    # The build dir must have been cleaned up despite the failure (L23).
    assert not build_dir.exists()


def test_cancel_emits_once(_qapp, tmp_path, monkeypatch):
    """A cancelled build returns None so export_project skips the bogus
    'Buildozer build failed: False' second emit (L24)."""
    import export.android.android_exporter as mod
    ex = mod.AndroidExporter()

    build_dir = tmp_path / "pygm_android_c"
    build_dir.mkdir()

    monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)
    monkeypatch.setattr(ex, "_check_buildozer", lambda: True)
    monkeypatch.setattr(ex, "_check_kivy", lambda: True)
    monkeypatch.setattr(ex, "_check_cython", lambda: True)
    monkeypatch.setattr(ex, "_check_java", lambda: True)
    monkeypatch.setattr(ex, "_check_build_tools", lambda: [])
    monkeypatch.setattr(ex, "_create_build_directory", lambda: build_dir)
    monkeypatch.setattr(ex, "_generate_kivy_game", lambda b: True)
    monkeypatch.setattr(ex, "_generate_buildozer_spec", lambda b: True)
    # Simulate _run_buildozer cancellation returning the None sentinel.
    monkeypatch.setattr(ex, "_run_buildozer", lambda b: None)

    emits = []
    ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

    result = ex.export_project("proj", str(tmp_path / "out"), {})
    assert result is False
    # No 'Buildozer build failed' emit for the cancel sentinel.
    assert not any("Buildozer build failed" in msg for _, msg in emits)


def _silent_process_class():
    """A fake Popen whose stdout never yields a line (simulates a buildozer
    that is silent for a long stretch) and only reaches EOF once killed."""
    import threading

    class _BlockingStdout:
        def __init__(self):
            self._stop = threading.Event()

        def __iter__(self):
            return self

        def __next__(self):
            self._stop.wait()      # block (no lines) until the process is killed
            raise StopIteration

    class _FakeSilentProcess:
        def __init__(self, *args, **kwargs):
            self.stdout = _BlockingStdout()
            self.returncode = None
            self.killed = False

        def kill(self):
            self.killed = True
            self.returncode = -9
            self.stdout._stop.set()

        def wait(self, timeout=None):
            if self.returncode is None:
                self.returncode = 0
            return self.returncode

    return _FakeSilentProcess


def test_cancel_during_silent_build_is_noticed(_qapp, tmp_path, monkeypatch):
    """Cancel pressed while buildozer is silent must return the None sentinel
    promptly and kill the process — not hang on a blocking stdout read."""
    import export.android.android_exporter as mod
    import threading
    import time

    ex = mod.AndroidExporter()
    ex._use_wsl = False

    Fake = _silent_process_class()
    created = {}

    def _popen(*a, **k):
        created["p"] = Fake(*a, **k)
        return created["p"]

    monkeypatch.setattr(mod.subprocess, "Popen", _popen)

    # Cancel arrives mid-silence (no stdout lines are ever produced).
    def _cancel_soon():
        time.sleep(0.15)
        ex.cancel_requested = True

    threading.Thread(target=_cancel_soon, daemon=True).start()

    start = time.monotonic()
    result = ex._run_buildozer(tmp_path)
    elapsed = time.monotonic() - start

    assert result is None                  # cancel sentinel (L24)
    assert created["p"].killed is True     # the process was killed
    assert elapsed < 5                     # returned promptly; did not block on the silent pipe


def test_timeout_fires_during_silent_build(_qapp, tmp_path, monkeypatch):
    """The wall-clock ceiling must fire even when buildozer emits no output."""
    import export.android.android_exporter as mod
    import time

    ex = mod.AndroidExporter()
    ex._use_wsl = False

    Fake = _silent_process_class()
    created = {}

    def _popen(*a, **k):
        created["p"] = Fake(*a, **k)
        return created["p"]

    monkeypatch.setattr(mod.subprocess, "Popen", _popen)
    # Shrink the ceiling so the deadline trips quickly.
    monkeypatch.setattr(mod, "BUILDOZER_TIMEOUT_NATIVE", 0.3)

    start = time.monotonic()
    result = ex._run_buildozer(tmp_path)
    elapsed = time.monotonic() - start

    assert isinstance(result, str)
    assert "timed out" in result.lower()   # timeout message returned, not a hang
    assert created["p"].killed is True      # the handler killed the process
    assert elapsed < 5


# --- KA-M2/M3: cancel/timeout must kill the whole build tree --------------

def test_native_terminate_signals_process_group(_qapp, monkeypatch):
    """KA-M3: native cancel/timeout must killpg the buildozer group, not
    just the parent (which orphaned gradle/gcc/p4a)."""
    import os as _os
    import export.android.android_exporter as mod
    ex = mod.AndroidExporter()
    ex._use_wsl = False

    calls = {}

    class FakeProc:
        pid = 4321
        def kill(self):
            calls["parent_kill"] = True

    # os.getpgid/killpg are POSIX-only; inject them so the POSIX branch is
    # exercised even when the test host is Windows (raising=False creates
    # the attrs). The native path never runs on Windows in production.
    monkeypatch.setattr(_os, "getpgid", lambda pid: pid, raising=False)
    monkeypatch.setattr(_os, "killpg",
                        lambda pgid, sig: calls.setdefault("killpg", (pgid, sig)),
                        raising=False)

    ex._terminate_build(FakeProc())
    # Signalled the whole GROUP (pgid == pid here) with a real signal,
    # and therefore did NOT need the lone-parent fallback.
    assert calls.get("killpg") is not None
    assert calls["killpg"][0] == 4321 and calls["killpg"][1]
    assert "parent_kill" not in calls


def test_wsl_terminate_kills_wsl_and_cleans_linux_tree(_qapp, monkeypatch):
    """KA-M2: WSL cancel/timeout kills wsl.exe AND best-effort pkills the
    Linux-side build (killing wsl.exe alone leaves it running)."""
    import export.android.android_exporter as mod
    ex = mod.AndroidExporter()
    ex._use_wsl = True

    calls = {"killed": False, "runs": []}

    class FakeProc:
        pid = 99
        def kill(self):
            calls["killed"] = True

    monkeypatch.setattr(mod.subprocess, "run",
                        lambda *a, **k: calls["runs"].append(a[0]))
    ex._terminate_build(FakeProc())
    assert calls["killed"] is True
    assert any("pkill" in " ".join(cmd) for cmd in calls["runs"]), calls["runs"]


def test_native_buildozer_starts_new_session():
    """KA-M3: the native buildozer Popen must be a process-group leader so
    the group can be killed."""
    src = (Path(__file__).parent.parent / "export" / "android"
           / "android_exporter.py").read_text(encoding="utf-8")
    assert "start_new_session=True" in src

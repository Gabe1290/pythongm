"""Regression tests for the Android exporter audit findings L23 and L24.

L23 — the temporary buildozer build directory (``tempfile.mkdtemp``) leaked
on every failed/cancelled export because cleanup ran only on the full-success
path.  Cleanup now runs in a ``finally`` so it happens on every exit path
(unless ``include_debug`` keeps the tree on purpose).

L24 — cancelling a build double-emitted ``export_complete`` (the second a
bogus "Buildozer build failed: False") and the cancel/timeout checks were dead
during a silent build because stdout was read with a blocking
``for line in process.stdout``.  ``_run_buildozer`` now returns a dedicated
``_CANCELLED`` sentinel (so the caller emits exactly one completion signal) and
polls a reader-thread queue with a deadline so cancel/timeout work even when
buildozer produces no output.

These run on Python 3.11 (offscreen QApplication, no pytest-qt).
"""

import os
import time
import threading
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    return app


def _make_exporter(_qapp):
    from export.android.android_exporter import AndroidExporter
    exp = AndroidExporter()
    return exp


# ---------------------------------------------------------------------------
# L24 — cancel returns a sentinel, single completion emit, working poll loop
# ---------------------------------------------------------------------------

class _FakeStdout:
    """A stdout whose readline blocks (like a silent build) until released."""

    def __init__(self):
        self._released = threading.Event()

    def readline(self):
        # Block until the test lets the build "finish" — mimics a quiet
        # gradle/buildozer phase that produces no output.
        self._released.wait()
        return ''  # EOF

    def release(self):
        self._released.set()


class _FakeProcess:
    def __init__(self, stdout):
        self.stdout = stdout
        self.returncode = 0
        self.killed = False

    def kill(self):
        self.killed = True
        # Releasing stdout lets the reader thread reach EOF and exit cleanly.
        self.stdout.release()

    def wait(self, timeout=None):
        self.stdout.release()
        return self.returncode


def test_cancel_returns_sentinel_not_emit(_qapp, monkeypatch):
    """A cancel during the (silent) build returns _CANCELLED and does NOT
    emit export_complete from inside _run_buildozer."""
    exp = _make_exporter(_qapp)
    exp._use_wsl = False

    emits = []
    exp.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

    stdout = _FakeStdout()
    fake_proc = _FakeProcess(stdout)
    import export.android.android_exporter as mod
    monkeypatch.setattr(mod.subprocess, "Popen", lambda *a, **k: fake_proc)

    # Request cancellation before the call; the poll loop must notice it even
    # though stdout never produces a line (the old blocking read could not).
    exp.cancel_requested = True

    result = exp._run_buildozer(Path("/tmp/does-not-matter"))

    assert result is exp._CANCELLED
    assert fake_proc.killed is True
    # The cancel branch must NOT have emitted anything itself.
    assert emits == []


def test_cancel_during_silent_build_is_noticed(_qapp, monkeypatch):
    """If cancel is requested AFTER the build starts and stdout is silent,
    the loop still notices within ~0.5s (it no longer blocks on readline)."""
    exp = _make_exporter(_qapp)
    exp._use_wsl = False

    stdout = _FakeStdout()
    fake_proc = _FakeProcess(stdout)
    import export.android.android_exporter as mod
    monkeypatch.setattr(mod.subprocess, "Popen", lambda *a, **k: fake_proc)

    def _request_cancel_soon():
        time.sleep(0.2)
        exp.cancel_requested = True

    t = threading.Thread(target=_request_cancel_soon, daemon=True)
    t.start()

    start = time.monotonic()
    result = exp._run_buildozer(Path("/tmp/does-not-matter"))
    elapsed = time.monotonic() - start

    assert result is exp._CANCELLED
    # The poll wakes at least every 0.5s, so cancellation is honoured quickly
    # despite zero build output — generously bounded to avoid CI flakiness.
    assert elapsed < 5.0
    t.join(timeout=1)


def test_timeout_fires_during_silent_build(_qapp, monkeypatch):
    """A silent build that exceeds the deadline raises TimeoutExpired and
    returns the timeout message — the blocking-read version could never reach
    process.wait(timeout=) while stdout stayed open."""
    exp = _make_exporter(_qapp)
    exp._use_wsl = False

    stdout = _FakeStdout()
    fake_proc = _FakeProcess(stdout)
    import export.android.android_exporter as mod
    monkeypatch.setattr(mod.subprocess, "Popen", lambda *a, **k: fake_proc)

    # Make monotonic jump far past the deadline so the loop's deadline check
    # trips on the first iteration without waiting 20 minutes.
    import time as _real_time
    base = _real_time.monotonic()
    calls = {"n": 0}

    def _fast_monotonic():
        calls["n"] += 1
        # First call sets the deadline; later calls are way past it.
        return base if calls["n"] <= 1 else base + 10_000_000

    # _time is imported inside the method as `import time as _time`, so it
    # resolves to the real time module — patch that.
    monkeypatch.setattr(_real_time, "monotonic", _fast_monotonic)

    result = exp._run_buildozer(Path("/tmp/does-not-matter"))

    assert isinstance(result, str)
    assert "timed out" in result.lower()
    assert fake_proc.killed is True


def test_export_project_emits_single_completion_on_cancel(_qapp, monkeypatch):
    """End-to-end: a cancelled build yields exactly one export_complete with
    the cancel message — never the bogus 'Buildozer build failed: False'."""
    exp = _make_exporter(_qapp)

    emits = []
    exp.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

    # Stub the steps so we reach _run_buildozer without doing real work.
    monkeypatch.setattr(exp, "_load_project", lambda *a, **k: None)
    monkeypatch.setattr(exp, "_create_build_directory",
                        lambda: Path("/tmp/pygm_fake_build"))
    monkeypatch.setattr(exp, "_generate_kivy_game", lambda bd: True)
    monkeypatch.setattr(exp, "_generate_buildozer_spec", lambda bd: True)
    monkeypatch.setattr(exp, "_cleanup", lambda bd: None)
    monkeypatch.setattr(exp, "_run_buildozer", lambda bd: exp._CANCELLED)
    # Avoid the Windows/WSL platform branch.
    import export.android.android_exporter as mod
    monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(exp, "_check_buildozer", lambda: True)
    monkeypatch.setattr(exp, "_check_kivy", lambda: True)
    monkeypatch.setattr(exp, "_check_cython", lambda: True)
    monkeypatch.setattr(exp, "_check_java", lambda: True)
    monkeypatch.setattr(exp, "_check_build_tools", lambda: [])

    ok = exp.export_project("proj.pgm", "/tmp/out", {})

    assert ok is False
    assert len(emits) == 1, "cancel must emit exactly one completion signal"
    success, message = emits[0]
    assert success is False
    assert "cancel" in message.lower()
    assert "False" not in message  # no bogus "build failed: False"


# ---------------------------------------------------------------------------
# L23 — temp build directory is cleaned up on failure / cancel, kept on debug
# ---------------------------------------------------------------------------

def _run_export_with_outcome(_qapp, monkeypatch, *, kivy_ok=True,
                              spec_ok=True, buildozer_result=True,
                              copy_ok=True, include_debug=False,
                              build_dir=None):
    exp = _make_exporter(_qapp)
    monkeypatch.setattr(exp, "_load_project", lambda *a, **k: None)
    monkeypatch.setattr(exp, "_create_build_directory", lambda: build_dir)
    monkeypatch.setattr(exp, "_generate_kivy_game", lambda bd: kivy_ok)
    monkeypatch.setattr(exp, "_generate_buildozer_spec", lambda bd: spec_ok)
    monkeypatch.setattr(exp, "_run_buildozer", lambda bd: buildozer_result)
    monkeypatch.setattr(exp, "_copy_to_output", lambda bd: copy_ok)

    cleaned = {"called_with": None}

    def _fake_cleanup(bd):
        cleaned["called_with"] = bd

    monkeypatch.setattr(exp, "_cleanup", _fake_cleanup)

    import export.android.android_exporter as mod
    monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(exp, "_check_buildozer", lambda: True)
    monkeypatch.setattr(exp, "_check_kivy", lambda: True)
    monkeypatch.setattr(exp, "_check_cython", lambda: True)
    monkeypatch.setattr(exp, "_check_java", lambda: True)
    monkeypatch.setattr(exp, "_check_build_tools", lambda: [])

    ok = exp.export_project("proj.pgm", "/tmp/out", {"include_debug": include_debug})
    return ok, cleaned["called_with"]


def test_cleanup_on_buildozer_failure(_qapp, monkeypatch):
    bd = Path("/tmp/pygm_fake_build")
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, buildozer_result="boom: build failed", build_dir=bd)
    assert ok is False
    assert cleaned_with == bd, "build dir must be cleaned up on buildozer failure"


def test_cleanup_on_kivy_generation_failure(_qapp, monkeypatch):
    bd = Path("/tmp/pygm_fake_build")
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, kivy_ok=False, build_dir=bd)
    assert ok is False
    assert cleaned_with == bd


def test_cleanup_on_no_apk_found(_qapp, monkeypatch):
    bd = Path("/tmp/pygm_fake_build")
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, copy_ok=False, build_dir=bd)
    assert ok is False
    assert cleaned_with == bd


def test_cleanup_on_cancel(_qapp, monkeypatch):
    bd = Path("/tmp/pygm_fake_build")
    from export.android.android_exporter import AndroidExporter
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, buildozer_result=AndroidExporter._CANCELLED,
        build_dir=bd)
    assert ok is False
    assert cleaned_with == bd


def test_cleanup_on_unexpected_exception(_qapp, monkeypatch):
    bd = Path("/tmp/pygm_fake_build")

    def _raise(_bd):
        raise RuntimeError("kaboom mid-build")

    exp = _make_exporter(_qapp)
    monkeypatch.setattr(exp, "_load_project", lambda *a, **k: None)
    monkeypatch.setattr(exp, "_create_build_directory", lambda: bd)
    monkeypatch.setattr(exp, "_generate_kivy_game", _raise)

    cleaned = {"called_with": None}
    monkeypatch.setattr(exp, "_cleanup",
                        lambda b: cleaned.__setitem__("called_with", b))

    import export.android.android_exporter as mod
    monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(exp, "_check_buildozer", lambda: True)
    monkeypatch.setattr(exp, "_check_kivy", lambda: True)
    monkeypatch.setattr(exp, "_check_cython", lambda: True)
    monkeypatch.setattr(exp, "_check_java", lambda: True)
    monkeypatch.setattr(exp, "_check_build_tools", lambda: [])

    ok = exp.export_project("proj.pgm", "/tmp/out", {})
    assert ok is False
    assert cleaned["called_with"] == bd, "exception path must still clean up"


def test_cleanup_on_success(_qapp, monkeypatch):
    bd = Path("/tmp/pygm_fake_build")
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, build_dir=bd)
    assert ok is True
    assert cleaned_with == bd


def test_no_cleanup_in_debug_mode(_qapp, monkeypatch):
    """Debug mode intentionally keeps the build tree for inspection."""
    bd = Path("/tmp/pygm_fake_build")
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, include_debug=True, build_dir=bd)
    assert ok is True
    assert cleaned_with is None, "debug mode must keep the build tree"


def test_no_cleanup_in_debug_mode_on_failure(_qapp, monkeypatch):
    """Debug mode keeps the tree even when the build fails (for diagnosis)."""
    bd = Path("/tmp/pygm_fake_build")
    ok, cleaned_with = _run_export_with_outcome(
        _qapp, monkeypatch, buildozer_result="boom", include_debug=True,
        build_dir=bd)
    assert ok is False
    assert cleaned_with is None

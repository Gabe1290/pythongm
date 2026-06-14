"""Regression tests for Android export L23 (cleanup on failure) and L24
(cancel returns sentinel, no bogus failure emit)."""

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

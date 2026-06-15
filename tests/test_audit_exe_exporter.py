"""Regression tests for export/exe/exe_exporter.py audit findings.

M38 — project names containing an apostrophe/quote must not break the
       generated PyInstaller spec (French names like "L'aventure").
M39 — EXE export must NOT report success and delete the only built copy when
       copying to the output folder fails.

Constructs a real (offscreen) QApplication rather than using pytest-qt so the
tests run on Python 3.11 too. ExeExporter is a QObject (it declares Qt
Signals), so a QApplication must exist before instances are created.
"""

import ast
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    return app


def _make_exporter(qapp):
    from export.exe.exe_exporter import ExeExporter
    return ExeExporter()


# ---------------------------------------------------------------------------
# M38 — name sanitization
# ---------------------------------------------------------------------------

def test_sanitize_strips_apostrophe(qapp):
    from export.exe.exe_exporter import ExeExporter
    # The classic French case: "L'aventure".
    assert "'" not in ExeExporter._sanitize_exe_name("L'aventure")
    assert '"' not in ExeExporter._sanitize_exe_name('Say "hi"')


def test_sanitize_no_path_separators(qapp):
    from export.exe.exe_exporter import ExeExporter
    out = ExeExporter._sanitize_exe_name("a/b\\c")
    assert "/" not in out and "\\" not in out


def test_sanitize_empty_falls_back(qapp):
    from export.exe.exe_exporter import ExeExporter
    assert ExeExporter._sanitize_exe_name("") == "Game"
    assert ExeExporter._sanitize_exe_name("''") == "Game"
    assert ExeExporter._sanitize_exe_name("...") == "Game"


def test_sanitize_keeps_normal_names(qapp):
    from export.exe.exe_exporter import ExeExporter
    assert ExeExporter._sanitize_exe_name("MyGame") == "MyGame"
    assert ExeExporter._sanitize_exe_name("My Game") == "My_Game"


def test_spec_with_apostrophe_name_is_valid_python(qapp, tmp_path):
    """The whole point of M38: a project named L'aventure must produce a spec
    that parses as Python (PyInstaller execs it). Build a real spec file and
    parse it with ast."""
    exporter = _make_exporter(qapp)
    exporter.project_data = {"name": "L'aventure"}
    exporter.export_settings = {}

    build_dir = tmp_path / "build_temp_exe"
    game_dir = build_dir / "game"
    game_dir.mkdir(parents=True)
    (game_dir / "main.py").write_text("print('hi')\n", encoding="utf-8")

    launcher = build_dir / "game_launcher.py"
    launcher.write_text("# launcher\n", encoding="utf-8")

    spec_file = exporter._create_spec_file(build_dir, launcher)
    spec_src = spec_file.read_text(encoding="utf-8")

    # Must not contain the broken literal name='L'aventure.exe'
    assert "name='L'aventure.exe'" not in spec_src
    # Must parse as valid Python (this is what PyInstaller's exec would do).
    ast.parse(spec_src)


# ---------------------------------------------------------------------------
# M39 — copy-failure must not be reported as success / must not delete build
# ---------------------------------------------------------------------------

def test_copy_to_output_returns_false_on_permission_error(qapp, tmp_path, monkeypatch):
    exporter = _make_exporter(qapp)
    exporter.output_path = tmp_path / "out"

    build_dir = tmp_path / "build_temp_exe"
    dist_dir = build_dir / "dist"
    dist_dir.mkdir(parents=True)
    (dist_dir / "game.exe").write_bytes(b"MZ")

    import shutil as _shutil

    def boom(*a, **k):
        raise PermissionError("locked by antivirus")

    monkeypatch.setattr(_shutil, "copy2", boom)
    # avoid real 1s sleeps in the retry loop
    import time as _time
    monkeypatch.setattr(_time, "sleep", lambda *_a, **_k: None)

    assert exporter._copy_to_output(build_dir) is False


def test_copy_to_output_returns_true_on_success(qapp, tmp_path):
    exporter = _make_exporter(qapp)
    exporter.output_path = tmp_path / "out"

    build_dir = tmp_path / "build_temp_exe"
    dist_dir = build_dir / "dist"
    dist_dir.mkdir(parents=True)
    (dist_dir / "game.exe").write_bytes(b"MZ")

    assert exporter._copy_to_output(build_dir) is True
    assert (exporter.output_path / "game.exe").exists()


def test_export_reports_failure_and_keeps_build_on_copy_failure(qapp, tmp_path, monkeypatch):
    """End-to-end of M39: when the copy fails, export_project must emit
    export_complete(False, ...) and must NOT run _cleanup (which would delete
    the only surviving copy under dist/)."""
    import platform as _platform
    monkeypatch.setattr(_platform, "system", lambda: "Windows")

    exporter = _make_exporter(qapp)

    build_dir = tmp_path / "build_temp_exe"
    dist_dir = build_dir / "dist"
    dist_dir.mkdir(parents=True)
    (dist_dir / "game.exe").write_bytes(b"MZ")

    # Stub out all the heavy real steps.
    monkeypatch.setattr(exporter, "_load_project", lambda *a, **k: None)
    monkeypatch.setattr(exporter, "_require_kivy_dependencies", lambda *a, **k: True)
    monkeypatch.setattr(exporter, "_create_build_directory", lambda: build_dir)
    monkeypatch.setattr(exporter, "_generate_kivy_game", lambda *a, **k: True)
    monkeypatch.setattr(exporter, "_create_launcher_script", lambda *a, **k: build_dir / "l.py")
    monkeypatch.setattr(exporter, "_create_spec_file", lambda *a, **k: build_dir / "game.spec")
    monkeypatch.setattr(exporter, "_run_pyinstaller", lambda *a, **k: True)
    exporter.output_path = tmp_path / "out"

    # Force the copy to fail.
    monkeypatch.setattr(exporter, "_copy_to_output", lambda *a, **k: False)

    cleanup_called = []
    monkeypatch.setattr(exporter, "_cleanup", lambda *a, **k: cleanup_called.append(True))

    results = []
    exporter.export_complete.connect(lambda ok, msg: results.append((ok, msg)))

    ret = exporter.export_project("proj", str(exporter.output_path), {})

    assert ret is False
    assert results, "export_complete must be emitted"
    ok, msg = results[-1]
    assert ok is False
    # cleanup must be skipped so the dist build survives
    assert not cleanup_called
    assert dist_dir.exists() and (dist_dir / "game.exe").exists()
    # the message should point the user at the surviving build
    assert "dist" in msg

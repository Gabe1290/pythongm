"""
Regression tests for audit findings in dialogs/project_dialogs.py.

L9 — ExportProjectDialog._export_executable() used to build a hardcoded
{'include_assets': True, 'include_debug': False, 'optimize': True} dict,
ignoring the user's Export Options checkboxes (Include Assets / Optimize for
Release / Include Debug Info). ExeExporter genuinely consumes include_debug
(PyInstaller console=/debug=) and optimize (upx=), so the checkboxes had zero
effect. This locks in that the user's checkbox states reach ExeExporter.

L8 — NewProjectDialog collects a Description, but its sole consumer in
core/ide_window.py drops it. The dialog side is correct (get_project_info()
returns the description); the missing write lives in another source file, so
that finding is deferred cross-file. We still assert the dialog exposes the
description so the cross-file fix has something to consume.

Constructs a real offscreen QApplication (no pytest-qt) so it runs on 3.11.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_new_project_dialog_exposes_description(_qapp):
    """L8 (dialog side): the description the user types is returned by
    get_project_info(); the drop happens in the consumer (ide_window)."""
    from dialogs.project_dialogs import NewProjectDialog

    dialog = NewProjectDialog()
    dialog.project_name_edit.setText("MyGame")
    dialog.project_path_edit.setText("/tmp/somewhere")
    dialog.description_edit.setPlainText("A platformer about a frog.")

    dialog.accept_project()

    info = dialog.get_project_info()
    assert info["description"] == "A platformer about a frog."


def test_export_executable_honors_checkbox_options(_qapp, tmp_path, monkeypatch):
    """L9: the user's Export Options checkboxes must reach ExeExporter
    instead of being overridden by a hardcoded dict."""
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtWidgets import QMessageBox
    import dialogs.project_dialogs as pd

    # A real project.json so the early-exists guard passes.
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "project.json").write_text("{}", encoding="utf-8")

    captured = {}

    class FakeExeExporter(QObject):
        progress_update = Signal(int, str)
        export_complete = Signal(bool, str)

        def export_project(self, project_path, output_path, settings):
            captured["settings"] = dict(settings)
            # Mimic a successful export so no failure dialog pops.
            self.export_complete.emit(True, "ok")
            return True

    # _export_executable does `from export.exe import ExeExporter`, so patch
    # the attribute on that module.
    import export.exe as exe_pkg
    monkeypatch.setattr(exe_pkg, "ExeExporter", FakeExeExporter, raising=False)

    # Don't block on the post-export info/warn message boxes.
    monkeypatch.setattr(
        QMessageBox, "information",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.No),
    )
    monkeypatch.setattr(
        QMessageBox, "warning",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok),
    )
    monkeypatch.setattr(
        QMessageBox, "critical",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok),
    )

    class FakeIDE:
        current_project_path = str(project_dir)

    dialog = pd.ExportProjectDialog()
    dialog.parent_ide = FakeIDE()
    dialog.output_path_edit.setText(str(tmp_path / "out"))

    # User wants a debug build, no UPX optimization, and no asset bundling.
    dialog.include_debug_check.setChecked(True)
    dialog.optimize_check.setChecked(False)
    dialog.include_assets_check.setChecked(False)

    # Populate self.export_settings the way accept_export would, then export.
    dialog._export_executable()

    assert captured.get("settings") is not None, "ExeExporter.export_project not called"
    assert captured["settings"]["include_debug"] is True
    assert captured["settings"]["optimize"] is False
    assert captured["settings"]["include_assets"] is False


def test_export_executable_default_checkbox_states(_qapp, tmp_path, monkeypatch):
    """The default checkbox states (debug off, optimize on, assets on) still
    flow through unchanged — guards against an inverted-logic regression."""
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtWidgets import QMessageBox
    import dialogs.project_dialogs as pd

    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "project.json").write_text("{}", encoding="utf-8")

    captured = {}

    class FakeExeExporter(QObject):
        progress_update = Signal(int, str)
        export_complete = Signal(bool, str)

        def export_project(self, project_path, output_path, settings):
            captured["settings"] = dict(settings)
            self.export_complete.emit(True, "ok")
            return True

    import export.exe as exe_pkg
    monkeypatch.setattr(exe_pkg, "ExeExporter", FakeExeExporter, raising=False)
    monkeypatch.setattr(
        QMessageBox, "information",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.No),
    )
    monkeypatch.setattr(
        QMessageBox, "warning",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok),
    )
    monkeypatch.setattr(
        QMessageBox, "critical",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok),
    )

    class FakeIDE:
        current_project_path = str(project_dir)

    dialog = pd.ExportProjectDialog()
    dialog.parent_ide = FakeIDE()
    dialog.output_path_edit.setText(str(tmp_path / "out"))

    dialog._export_executable()

    assert captured.get("settings") is not None
    assert captured["settings"]["include_debug"] is False
    assert captured["settings"]["optimize"] is True
    assert captured["settings"]["include_assets"] is True

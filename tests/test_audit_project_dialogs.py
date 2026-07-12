"""
Regression tests for audit findings L8/L9 (post export-UI consolidation).

L9 -- Export Options checkboxes must reach the exporter instead of being
overridden by a hardcoded dict. Originally pinned against
ExportProjectDialog._export_executable; that dialog was retired
2026-07-12 (the two overlapping export UIs were consolidated into the
registry-driven Build -> Export Game dialog), so the same guarantee is
now pinned against the unified path: the dialog stashes _export_options,
and export_windows_exe builds ExeExporter's settings from
_current_export_options().

L8 -- NewProjectDialog collects a Description; the dialog side must keep
exposing it via get_project_info() for the cross-file consumer fix.

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


def _run_windows_export_with_options(options):
    """Drive the real export_windows_exe shell with a stub IDE carrying
    ``options`` in _export_options; return the settings the exporter
    would receive."""
    from core.ide_window import PyGameMakerIDE

    captured = {}

    class StubIDE:
        _export_options = options

        def tr(self, text):
            return text

        def _require_open_project(self):
            return True

        def _ask_export_dir(self, suffix):
            return "/tmp/out"

        def _current_export_options(self):
            return PyGameMakerIDE._current_export_options(self)

        def _run_export_with_progress(self, **kwargs):
            captured.update(kwargs["export_settings"])

    PyGameMakerIDE.export_windows_exe(StubIDE())
    return captured


def test_export_executable_honors_checkbox_options(_qapp):
    """L9: the user's Export Options choices must reach ExeExporter."""
    settings = _run_windows_export_with_options(
        {"include_assets": False, "optimize": False, "include_debug": True})
    assert settings["include_debug"] is True
    assert settings["optimize"] is False
    assert settings["include_assets"] is False
    assert settings["output_path"] == "/tmp/out"


def test_export_executable_default_checkbox_states(_qapp):
    """The defaults (debug off, optimize on, assets on) still flow through
    unchanged when no dialog stashed options -- guards inverted logic."""
    settings = _run_windows_export_with_options(None)
    assert settings["include_debug"] is False
    assert settings["optimize"] is True
    assert settings["include_assets"] is True

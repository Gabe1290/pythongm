"""Regression tests: Export Options must be honored (audit L9 lineage)
and NewProjectDialog carries the description (audit L8, dialog side).

L9 originally lived in ExportProjectDialog._collect_export_settings; that
dialog was retired 2026-07-12 when the export UIs were consolidated. The
seam is now PyGameMakerIDE._current_export_options(): the unified export
dialog stashes the checkbox states in _export_options before dispatching,
and every desktop/Android runner shell builds its exporter settings from
it (the shells used to hardcode the dict -- the exact L9 anti-pattern,
which the consolidation also fixed in this second path).
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_new_project_dialog_carries_description(_qapp):  # L8 (dialog contract)
    from dialogs.project_dialogs import NewProjectDialog
    dlg = NewProjectDialog()
    dlg.description_edit.setPlainText("My great game")
    dlg.project_data = {
        "name": "Game1", "description": dlg.description_edit.toPlainText()}
    assert dlg.get_project_info()["description"] == "My great game"


def test_current_export_options_returns_dialog_choices():
    """When the unified dialog stashed choices, the runners see them."""
    from core.ide_window import PyGameMakerIDE

    class Stub:
        _export_options = {
            "include_assets": False, "optimize": False, "include_debug": True}

    options = PyGameMakerIDE._current_export_options(Stub())
    assert options == {
        "include_assets": False, "optimize": False, "include_debug": True}


def test_current_export_options_defaults_without_dialog():
    """Runners invoked directly (no dialog) keep the historical defaults."""
    from core.ide_window import PyGameMakerIDE

    class Stub:
        _export_options = None

    options = PyGameMakerIDE._current_export_options(Stub())
    assert options == {
        "include_assets": True, "optimize": True, "include_debug": False}


def test_runner_shells_use_the_options_not_hardcoded_dicts():
    """No runner shell may regress to a hardcoded options dict (the
    pre-consolidation state of export_windows_exe/linux/macos/android)."""
    src = (REPO_ROOT / "core" / "ide_window.py").read_text(encoding="utf-8")
    assert src.count("**self._current_export_options()") >= 4
    hardcoded = "'include_assets': True,\n                'optimize': True,"
    assert hardcoded not in src

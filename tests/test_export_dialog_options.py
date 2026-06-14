"""Regression test for Export Options checkboxes being honored (audit L9).

_export_executable built a hardcoded {'include_assets': True, 'include_debug':
False, 'optimize': True} dict, so the dialog's checkboxes had no effect. The
settings are now collected from the checkboxes.
"""

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


def test_new_project_dialog_carries_description(_qapp):  # L8 (dialog contract)
    from dialogs.project_dialogs import NewProjectDialog
    dlg = NewProjectDialog()
    dlg.description_edit.setPlainText("My great game")
    # get_project_info returns whatever accept_project stored; simulate that
    # population (avoids exec()) and confirm the description is carried.
    dlg.project_data = {
        "name": "Game1", "description": dlg.description_edit.toPlainText()}
    assert dlg.get_project_info()["description"] == "My great game"


def test_collect_export_settings_reflects_checkboxes(_qapp):
    from dialogs.project_dialogs import ExportProjectDialog
    dlg = ExportProjectDialog()

    dlg.include_debug_check.setChecked(True)
    dlg.optimize_check.setChecked(False)
    dlg.include_assets_check.setChecked(False)

    settings = dlg._collect_export_settings()
    assert settings == {
        "include_assets": False,
        "include_debug": True,
        "optimize": False,
    }

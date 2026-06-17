"""Regression test for empty tutorial index placeholder (audit L1).

When the edition filter yields zero tutorials from an index.json (e.g. a
tutorial-gating edition under a localized index missing its gated tutorial),
both tutorial widgets returned immediately after the index loop, so the
'No tutorials available' placeholder (only on the folder-scan fallback) never
showed — a wordless blank list. The placeholder now also covers the index path.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
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


def _tutorials_dir(tmp_path, tutorials):
    (tmp_path / "index.json").write_text(
        json.dumps({"tutorials": tutorials}), encoding="utf-8")
    return tmp_path


def test_panel_shows_placeholder_for_empty_index(_qapp, tmp_path):
    from widgets.tutorial_panel import TutorialPanel
    panel = TutorialPanel()
    panel.tutorials_path = _tutorials_dir(tmp_path, [])  # filters to empty
    panel.load_tutorial_list()
    items = [panel.tutorial_list.item(i).text()
             for i in range(panel.tutorial_list.count())]
    assert items == ["No tutorials available"]


def test_dialog_shows_placeholder_for_empty_index(_qapp, tmp_path):
    from widgets.tutorial_dialog import TutorialDialog
    dlg = TutorialDialog()
    dlg.tutorials_path = _tutorials_dir(tmp_path, [])
    dlg.load_tutorial_list()
    items = [dlg.tutorial_list.item(i).text()
             for i in range(dlg.tutorial_list.count())]
    assert items == ["No tutorials available"]

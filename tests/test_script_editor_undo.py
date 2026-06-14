"""Regression test for script editor undo/redo (audit L14).

ScriptEditor inherited BaseEditor's undo_stack-based undo/redo, which it never
pushed to, so the toolbar Undo/Redo buttons and the IDE Edit > Undo were dead
while the QPlainTextEdit's own document undo worked via Ctrl+Z. undo()/redo()
now delegate to the document and the toolbar actions reflect its availability.
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


def _editor():
    from editors.script_editor import ScriptEditor
    return ScriptEditor()


def test_undo_action_enables_on_edit(_qapp):
    ed = _editor()
    assert ed.undo_action.isEnabled() is False
    ed.code_edit.insertPlainText("hello")
    assert ed.undo_action.isEnabled() is True


def test_editor_undo_reverts_text(_qapp):
    ed = _editor()
    ed.code_edit.insertPlainText("abc")
    assert ed.code_edit.toPlainText() == "abc"
    ed.undo()  # the path IDE Edit > Undo uses
    assert ed.code_edit.toPlainText() == ""


def test_editor_redo_restores_text(_qapp):
    ed = _editor()
    ed.code_edit.insertPlainText("xyz")
    ed.undo()
    ed.redo()
    assert ed.code_edit.toPlainText() == "xyz"

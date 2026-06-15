#!/usr/bin/env python3
"""Regression test for audit L14 — ScriptEditor Undo/Redo toolbar buttons and
IDE Edit-menu undo()/redo() must drive the QPlainTextEdit document undo, not
the never-populated BaseEditor.undo_stack.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication

from editors.script_editor import ScriptEditor


def _app():
    return QApplication.instance() or QApplication([])


def _make_editor():
    _app()
    ed = ScriptEditor()
    ed.load_data({"code": "print('a')\n", "language": "python"})
    return ed


def test_undo_redo_actions_start_disabled_on_clean_load():
    ed = _make_editor()
    # Freshly loaded, nothing typed yet -> nothing undoable/redoable.
    assert ed.undo_action.isEnabled() is False
    assert ed.redo_action.isEnabled() is False


def test_typing_enables_undo_action():
    ed = _make_editor()
    ed.code_edit.insertPlainText("# more\n")
    # The document now has an undoable edit -> toolbar Undo lights up.
    assert ed.undo_action.isEnabled() is True


def test_ide_menu_undo_reverts_the_edit():
    """ide_window Edit > Undo delegates to editor.undo(); it must actually
    revert the QPlainTextEdit content."""
    ed = _make_editor()
    before = ed.code_edit.toPlainText()
    ed.code_edit.insertPlainText("XYZ")
    assert ed.code_edit.toPlainText() != before

    ed.undo()  # the path the IDE Edit menu calls
    assert ed.code_edit.toPlainText() == before


def test_ide_menu_redo_reapplies_the_edit():
    ed = _make_editor()
    before = ed.code_edit.toPlainText()
    ed.code_edit.insertPlainText("XYZ")
    after = ed.code_edit.toPlainText()

    ed.undo()
    assert ed.code_edit.toPlainText() == before
    ed.redo()
    assert ed.code_edit.toPlainText() == after


def test_toolbar_undo_action_triggers_document_undo():
    """The toolbar action must be wired to the document undo, not to the dead
    BaseEditor.undo_stack (which is never populated by ScriptEditor)."""
    ed = _make_editor()
    before = ed.code_edit.toPlainText()
    ed.code_edit.insertPlainText("ZZZ")
    assert ed.code_edit.toPlainText() != before

    ed.undo_action.trigger()
    assert ed.code_edit.toPlainText() == before


def test_redo_available_drives_redo_action():
    ed = _make_editor()
    ed.code_edit.insertPlainText("ZZZ")
    ed.undo()
    # After an undo there should be something to redo -> button enabled.
    assert ed.redo_action.isEnabled() is True
    ed.redo_action.trigger()
    assert ed.redo_action.isEnabled() is False

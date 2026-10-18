"""TODO.md's Find/Replace follow-up: "Room editor scripts, event scripts
(the execute_code action's QTextEdit inside gm80_action_dialog.py, a modal
per-action dialog, not an editor tab _active_editor() can see) ... are not
covered."

Investigation found the TODO's own lead was partly stale: the dialog a
regular (non-Thymio) object's execute_code/execute_script action actually
opens is events.action_editor.ActionConfigDialog (via
events/conditional_editor.py's create_action_dialog), not
GM80ActionDialog -- that one is Thymio-extension-only. Both are real,
separate modal QDialog subclasses with a bare QTextEdit for "code" (and,
for ActionConfigDialog, "text") parameters, and both have the identical
problem: being modal (exec()/setModal(True)), the main IDE window's
Edit > Find... QAction (Qt.WindowShortcut context) never fires while
either is open, no matter how core/ide/_edit_actions.py's
_active_editor()/_find_target_text_edit() is extended -- a dialog-owned
QShortcut is the only way to reach it. Fixed for both.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# ---------------------------------------------------------------------------
# events.action_editor.ActionConfigDialog -- the real, non-Thymio path
# ---------------------------------------------------------------------------

def _action_type_with_code_param():
    from events.action_types import ActionType, ActionParameter
    return ActionType(
        name="execute_code",
        display_name="Execute Code",
        description="Run Python code",
        category="Control",
        parameters=[
            ActionParameter(name="code", display_name="Code", param_type="code",
                             default_value="pass"),
        ],
    )


def _action_type_with_no_code_param():
    from events.action_types import ActionType, ActionParameter
    return ActionType(
        name="set_score",
        display_name="Set Score",
        description="Set the score",
        category="Score",
        parameters=[
            ActionParameter(name="value", display_name="Value", param_type="number",
                             default_value=0),
        ],
    )


class TestActionConfigDialogFindReplace:
    def test_code_param_produces_a_findable_text_edit(self, _qapp):
        from events.action_editor import ActionConfigDialog
        dialog = ActionConfigDialog(_action_type_with_code_param())
        try:
            target = dialog._find_target_text_edit()
            assert target is not None
            assert target is dialog.param_widgets["code"]
        finally:
            dialog.deleteLater()

    def test_no_code_or_text_param_means_no_target(self, _qapp):
        from events.action_editor import ActionConfigDialog
        dialog = ActionConfigDialog(_action_type_with_no_code_param())
        try:
            assert dialog._find_target_text_edit() is None
        finally:
            dialog.deleteLater()

    def test_ctrl_f_shortcut_opens_find_dialog_bound_to_the_code_edit(self, _qapp):
        from events.action_editor import ActionConfigDialog
        dialog = ActionConfigDialog(_action_type_with_code_param())
        try:
            mock_find_dialog = MagicMock()
            with patch('dialogs.find_replace_dialog.FindReplaceDialog',
                       return_value=mock_find_dialog):
                dialog._show_find_dialog(show_replace=False)
            assert dialog._find_dialog is mock_find_dialog
            mock_find_dialog.set_target.assert_called_once_with(dialog.param_widgets["code"])
            mock_find_dialog.set_replace_visible.assert_called_once_with(False)
            mock_find_dialog.show.assert_called_once()
        finally:
            dialog.deleteLater()

    def test_ctrl_h_shows_replace_fields(self, _qapp):
        from events.action_editor import ActionConfigDialog
        dialog = ActionConfigDialog(_action_type_with_code_param())
        try:
            mock_find_dialog = MagicMock()
            with patch('dialogs.find_replace_dialog.FindReplaceDialog',
                       return_value=mock_find_dialog):
                dialog._show_find_dialog(show_replace=True)
            mock_find_dialog.set_replace_visible.assert_called_once_with(True)
        finally:
            dialog.deleteLater()

    def test_no_target_is_a_quiet_noop_not_a_crash(self, _qapp):
        from events.action_editor import ActionConfigDialog
        dialog = ActionConfigDialog(_action_type_with_no_code_param())
        try:
            dialog._show_find_dialog(show_replace=False)  # must not raise
            assert getattr(dialog, '_find_dialog', None) is None
        finally:
            dialog.deleteLater()

    def test_second_call_reuses_the_same_find_dialog_instance(self, _qapp):
        from events.action_editor import ActionConfigDialog
        dialog = ActionConfigDialog(_action_type_with_code_param())
        try:
            mock_find_dialog = MagicMock()
            with patch('dialogs.find_replace_dialog.FindReplaceDialog',
                       return_value=mock_find_dialog):
                dialog._show_find_dialog(show_replace=False)
                dialog._show_find_dialog(show_replace=True)
            assert dialog._find_dialog is mock_find_dialog
        finally:
            dialog.deleteLater()

    def test_focused_text_edit_is_preferred_over_the_first_one(self, _qapp):
        """A dialog with more than one multi-line param (e.g. a "code"
        param plus a "text" comment param) must target whichever one the
        user actually has focus in, not always the first."""
        from events.action_types import ActionType, ActionParameter
        from events.action_editor import ActionConfigDialog
        action_type = ActionType(
            name="execute_code", display_name="Execute Code",
            description="", category="Control",
            parameters=[
                ActionParameter(name="code", display_name="Code", param_type="code",
                                 default_value=""),
                ActionParameter(name="note", display_name="Note", param_type="text",
                                 default_value=""),
            ],
        )
        dialog = ActionConfigDialog(action_type)
        try:
            # setFocus() only actually transfers QApplication.focusWidget()
            # once the widget's window is shown/active and the event loop
            # has processed the focus change -- an offscreen platform
            # still honors that, just not synchronously for a never-shown
            # dialog with no pumped events.
            from PySide6.QtWidgets import QApplication
            dialog.show()
            QApplication.processEvents()
            note_edit = dialog.param_widgets["note"]
            note_edit.setFocus()
            QApplication.processEvents()
            assert dialog._find_target_text_edit() is note_edit
        finally:
            dialog.deleteLater()


# ---------------------------------------------------------------------------
# editors.object_editor.gm80_action_dialog.GM80ActionDialog -- Thymio
# ---------------------------------------------------------------------------

def _gm80_action_def_with_code_param():
    from actions import ActionDefinition, ActionParameter
    return ActionDefinition(
        name="execute_code", display_name="Execute Code",
        category="Control", tab="control", description="Run code",
        parameters=[
            ActionParameter(name="code", type="code", display_name="Code",
                             description="", default="pass"),
        ],
    )


def _gm80_action_def_with_no_code_param():
    from actions import ActionDefinition, ActionParameter
    return ActionDefinition(
        name="set_score", display_name="Set Score",
        category="Score", tab="score", description="Set the score",
        parameters=[
            ActionParameter(name="value", type="int", display_name="Value",
                             description="", default=0),
        ],
    )


class TestGM80ActionDialogFindReplace:
    def test_code_param_produces_a_findable_text_edit(self, _qapp):
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog
        dialog = GM80ActionDialog(_gm80_action_def_with_code_param())
        try:
            target = dialog._find_target_text_edit()
            assert target is not None
            assert target is dialog.param_widgets["code"]
        finally:
            dialog.deleteLater()

    def test_no_code_param_means_no_target(self, _qapp):
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog
        dialog = GM80ActionDialog(_gm80_action_def_with_no_code_param())
        try:
            assert dialog._find_target_text_edit() is None
        finally:
            dialog.deleteLater()

    def test_ctrl_f_shortcut_opens_find_dialog_bound_to_the_code_edit(self, _qapp):
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog
        dialog = GM80ActionDialog(_gm80_action_def_with_code_param())
        try:
            mock_find_dialog = MagicMock()
            with patch('dialogs.find_replace_dialog.FindReplaceDialog',
                       return_value=mock_find_dialog):
                dialog._show_find_dialog(show_replace=False)
            mock_find_dialog.set_target.assert_called_once_with(dialog.param_widgets["code"])
            mock_find_dialog.show.assert_called_once()
        finally:
            dialog.deleteLater()

    def test_no_target_is_a_quiet_noop_not_a_crash(self, _qapp):
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog
        dialog = GM80ActionDialog(_gm80_action_def_with_no_code_param())
        try:
            dialog._show_find_dialog(show_replace=False)  # must not raise
            assert getattr(dialog, '_find_dialog', None) is None
        finally:
            dialog.deleteLater()

    def test_shortcuts_are_actually_registered_on_the_dialog(self, _qapp):
        """Not just that the methods work when called directly -- that a
        real Ctrl+F/Ctrl+H QShortcut exists on the dialog at all."""
        from PySide6.QtGui import QShortcut
        from editors.object_editor.gm80_action_dialog import GM80ActionDialog
        dialog = GM80ActionDialog(_gm80_action_def_with_code_param())
        try:
            shortcuts = dialog.findChildren(QShortcut)
            keys = {s.key().toString() for s in shortcuts}
            assert "Ctrl+F" in keys
            assert "Ctrl+H" in keys
        finally:
            dialog.deleteLater()

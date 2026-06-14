"""Regression tests for action editor L18 (check_empty dropdown) and L19
(unknown actions misalign rows)."""

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


class TestCheckEmptyDropdown:  # L18
    def test_objects_choice_excludes_project_objects(self, _qapp):
        from PySide6.QtWidgets import QWidget, QComboBox
        from events.action_editor import ActionConfigDialog
        from events.action_types import ACTION_TYPES

        parent = QWidget()
        parent.current_project_data = {
            "assets": {"objects": {"obj_wall": {}, "obj_coin": {}}}
        }
        dlg = ActionConfigDialog(ACTION_TYPES["check_empty"], {}, parent)
        dlg._keep = parent
        widget = dlg.param_widgets["objects"]
        assert isinstance(widget, QComboBox)
        items = [widget.itemText(i) for i in range(widget.count())]
        assert items == ["solid", "all"]
        assert "obj_wall" not in items


class TestUnknownActionRows:  # L19
    def test_unknown_action_is_rendered(self, _qapp):
        from events.action_editor import MultiActionEditor
        actions = [
            {"action": "check_keys_and_move", "parameters": {}},  # unknown type
            {"action": "set_hspeed", "parameters": {"value": 4}},
        ]
        editor = MultiActionEditor(actions)
        # Every action gets a row, so indexes stay aligned with the data.
        assert editor.action_tree.topLevelItemCount() == 2

    def test_remove_targets_correct_action(self, _qapp):
        from events.action_editor import MultiActionEditor
        actions = [
            {"action": "check_keys_and_move", "parameters": {}},  # unknown, row 0
            {"action": "set_hspeed", "parameters": {"value": 4}},  # row 1
        ]
        editor = MultiActionEditor(actions)
        # Select row 0 (the unknown action) and remove it.
        editor.action_tree.setCurrentItem(editor.action_tree.topLevelItem(0))
        editor.remove_action()
        assert len(editor.action_list) == 1
        assert editor.action_list[0]["action"] == "set_hspeed"

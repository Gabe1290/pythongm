"""ObjectEventsPanel's handling of actions from a disabled/not-installed
extension — DEFERRED_ITEMS_PLAN.md Tier 3 item 13 / extension_compat_2_0
PLAN.md Task 3.

Before this fix an unrecognized action rendered as plain "❓ <raw id>" text
in the normal action font color, and double-clicking it to edit silently
did nothing (a debug-only log line). Now it renders visibly inert (amber,
distinct from both a normal action and a comment's gray-italic), names the
owning extension when its manifest is on disk (list_available_extensions()
sees a disabled extension's manifest fine — only a genuinely absent one, or
a plain unknown action name, has no owner to report), and double-clicking
explains why instead of doing nothing.

get_action_type and extension_for_action are mocked rather than relying on
real global ACTION_TYPES/extension state, since load_all_plugins() may or
may not have already run earlier in the same pytest session (shared
process-global state — see CLAUDE.md's "plugin loader" landmines).
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
from unittest.mock import patch

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


def _make_panel(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    return ObjectEventsPanel()


def _amber_matches(color):
    return (color.red(), color.green(), color.blue()) == (180, 120, 20)


class TestUnknownActionRendering:
    def test_known_extension_owner_is_named_and_amber(self, _qapp):
        panel = _make_panel(_qapp)
        panel.current_events_data = {
            "step": {"actions": [{"action": "set_camera_3d", "parameters": {}}]}
        }
        fake_owner = {"folder": "threed", "name": "3D", "enabled": True,
                      "provides_actions": ["set_camera_3d"]}
        with patch("editors.object_editor.events._action_lookup.get_action_type",
                   return_value=None), \
             patch("events.plugin_loader.extension_for_action",
                   return_value=fake_owner):
            panel.refresh_events_display()

        step_item = panel.events_tree.topLevelItem(0)
        action_item = step_item.child(0)
        text = action_item.text(0)
        assert "❓" in text
        assert "set_camera_3d" in text
        assert "3D" in text
        assert _amber_matches(action_item.foreground(0).color())

    def test_unknown_owner_shows_raw_id_only(self, _qapp):
        panel = _make_panel(_qapp)
        panel.current_events_data = {
            "step": {"actions": [{"action": "totally_made_up_action", "parameters": {}}]}
        }
        with patch("editors.object_editor.events._action_lookup.get_action_type",
                   return_value=None), \
             patch("events.plugin_loader.extension_for_action",
                   return_value=None):
            panel.refresh_events_display()

        step_item = panel.events_tree.topLevelItem(0)
        action_item = step_item.child(0)
        text = action_item.text(0)
        assert "❓ totally_made_up_action" in text
        assert "needs" not in text
        assert _amber_matches(action_item.foreground(0).color())

    def test_recognized_action_is_unaffected(self, _qapp):
        panel = _make_panel(_qapp)
        panel.current_events_data = {
            "step": {"actions": [{"action": "set_score", "parameters": {"value": "1"}}]}
        }
        panel.refresh_events_display()

        step_item = panel.events_tree.topLevelItem(0)
        action_item = step_item.child(0)
        assert "❓" not in action_item.text(0)


class TestEditUnknownAction:
    def _action_item_for(self, panel, action_name):
        panel.current_events_data = {
            "step": {"actions": [{"action": action_name, "parameters": {}}]}
        }
        panel.refresh_events_display()
        return panel.events_tree.topLevelItem(0).child(0)

    def test_known_owner_shows_specific_message(self, _qapp):
        panel = _make_panel(_qapp)
        fake_owner = {"folder": "threed", "name": "3D", "enabled": False,
                      "provides_actions": ["set_camera_3d"]}
        with patch("editors.object_editor.events._action_lookup.get_action_type",
                   return_value=None), \
             patch("editors.object_editor.events._action_crud.get_action_type",
                   return_value=None), \
             patch("events.plugin_loader.extension_for_action",
                   return_value=fake_owner):
            action_item = self._action_item_for(panel, "set_camera_3d")
            with patch("editors.object_editor.events._action_crud.QMessageBox") as mock_box:
                panel.edit_action(action_item)

        assert mock_box.information.called
        title = mock_box.information.call_args[0][1]
        message = mock_box.information.call_args[0][2]
        assert "Extension Action" in title
        assert "3D" in message
        assert "disabled" in message

    def test_unknown_owner_shows_generic_message(self, _qapp):
        panel = _make_panel(_qapp)
        with patch("editors.object_editor.events._action_lookup.get_action_type",
                   return_value=None), \
             patch("editors.object_editor.events._action_crud.get_action_type",
                   return_value=None), \
             patch("events.plugin_loader.extension_for_action",
                   return_value=None):
            action_item = self._action_item_for(panel, "totally_made_up_action")
            with patch("editors.object_editor.events._action_crud.QMessageBox") as mock_box:
                panel.edit_action(action_item)

        assert mock_box.information.called
        message = mock_box.information.call_args[0][2]
        assert "totally_made_up_action" in message
        assert "isn't installed" in message

    def test_edit_does_not_crash_and_no_dialog_created_for_known_action(self, _qapp):
        # Sanity: a recognized action still opens its real editor dialog
        # path (not asserting the dialog itself here, just that we didn't
        # accidentally route it through the new unknown-action branch).
        panel = _make_panel(_qapp)
        action_item = self._action_item_for(panel, "set_score")
        with patch("editors.object_editor.events._action_crud.QMessageBox") as mock_box, \
             patch("editors.object_editor.events._action_crud.create_action_dialog") as mock_dialog:
            mock_dialog.return_value.exec.return_value = 0  # QDialog.Rejected
            panel.edit_action(action_item)
        assert not mock_box.information.called

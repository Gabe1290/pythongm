"""dialogs/preferences_dialog.PreferencesDialog's Extensions tab —
DEFERRED_ITEMS_PLAN.md item 13's settings UI. events.plugin_loader's
list_available_extensions/set_extension_enabled are patched throughout so
these tests never touch the real extensions/ folder or the real
~/.pygamemaker/config.json (see the module docstring on that concern).

apply_settings() itself also writes font/appearance/editor/project/advanced
Config, applies a theme, and can trigger a blockly-preset file write — none
of that is safely mockable in one shot without a lot of unrelated
scaffolding, so these tests exercise the extension-specific piece via
PreferencesDialog._apply_extension_settings() (the method apply_settings()
delegates to for exactly this reason — see its own docstring) rather than
the full apply_settings().
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


_RAYCAST = {
    "folder": "raycast_2_5d", "name": "2.5D Raycast View", "version": "1.0.0",
    "description": "Doom/Wolfenstein-style first-person room renderer.",
    "enabled": True,
    "provides_actions": ["enable_raycast_view", "set_facing_angle"],
}
_DEMO_DISABLED = {
    "folder": "demo_ext", "name": "Demo Extension", "version": "0.1.0",
    "description": "A test fixture extension.",
    "enabled": False,
    "provides_actions": ["demo_action"],
}


def _make_dialog(_qapp, extensions):
    with patch("events.plugin_loader.list_available_extensions", return_value=extensions):
        from dialogs.preferences_dialog import PreferencesDialog
        return PreferencesDialog()


class TestExtensionsTabListing:
    def test_no_extensions_shows_no_checkboxes(self, _qapp):
        dialog = _make_dialog(_qapp, [])
        assert dialog.extension_checkboxes == {}

    def test_one_extension_creates_a_checkbox_with_its_name(self, _qapp):
        dialog = _make_dialog(_qapp, [_RAYCAST])
        assert "raycast_2_5d" in dialog.extension_checkboxes
        assert dialog.extension_checkboxes["raycast_2_5d"].text() == "2.5D Raycast View"

    def test_checkbox_checked_state_reflects_enabled_field(self, _qapp):
        dialog = _make_dialog(_qapp, [_RAYCAST, _DEMO_DISABLED])
        assert dialog.extension_checkboxes["raycast_2_5d"].isChecked() is True
        assert dialog.extension_checkboxes["demo_ext"].isChecked() is False

    def test_provides_actions_surfaced_as_tooltip_not_inline(self, _qapp):
        dialog = _make_dialog(_qapp, [_RAYCAST])
        tooltip = dialog.extension_checkboxes["raycast_2_5d"].toolTip()
        assert "enable_raycast_view" in tooltip
        assert "set_facing_angle" in tooltip


class TestApplyExtensionSettings:
    """PreferencesDialog._apply_extension_settings — the method
    apply_settings() delegates to (see its docstring for why it's tested
    directly rather than through the full apply_settings())."""

    def test_writes_every_checkbox_current_state(self, _qapp):
        dialog = _make_dialog(_qapp, [_RAYCAST, _DEMO_DISABLED])
        dialog.extension_checkboxes["raycast_2_5d"].setChecked(False)
        dialog.extension_checkboxes["demo_ext"].setChecked(True)

        with patch("events.plugin_loader.set_extension_enabled") as mock_set:
            dialog._apply_extension_settings()

        mock_set.assert_any_call("raycast_2_5d", False)
        mock_set.assert_any_call("demo_ext", True)
        assert mock_set.call_count == 2

    def test_no_extensions_is_a_safe_noop(self, _qapp):
        dialog = _make_dialog(_qapp, [])
        with patch("events.plugin_loader.set_extension_enabled") as mock_set:
            dialog._apply_extension_settings()
        mock_set.assert_not_called()

    def test_cancel_never_calls_apply_extension_settings(self, _qapp):
        """Cancel = self.reject(), which must never write anything —
        matching every other tab's buffer-until-apply behavior."""
        dialog = _make_dialog(_qapp, [_RAYCAST])
        dialog.extension_checkboxes["raycast_2_5d"].setChecked(False)

        with patch.object(dialog, "_apply_extension_settings") as mock_apply:
            dialog.reject()

        mock_apply.assert_not_called()

    def test_apply_settings_delegates_to_apply_extension_settings(self, _qapp):
        """Wiring check: apply_settings() (the real Apply/OK path) must
        call _apply_extension_settings(). Everything else apply_settings()
        touches (Config writes, theme application, a possible blockly-
        preset file write) is neutralized so this stays a safe, isolated
        check of just the wiring, not an endorsement of calling the real
        apply_settings() freely in tests."""
        dialog = _make_dialog(_qapp, [_RAYCAST])

        with patch("dialogs.preferences_dialog.Config"), \
             patch("dialogs.preferences_dialog.QMessageBox"), \
             patch("utils.theme_manager.ThemeManager.apply_theme"), \
             patch.object(dialog, "_apply_extension_settings") as mock_apply, \
             patch.object(dialog, "_apply_edition_blockly_preset"):
            dialog.apply_settings()

        mock_apply.assert_called_once()

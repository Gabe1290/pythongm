"""Regression tests for ThymioConfigDialog preset_name (audit M14).

docs/FULL_AUDIT_2026-06-11.md: unlike its twin BlocklyConfigDialog,
ThymioConfigDialog never set config.preset_name when customizing — neither
the _apply_thymio_* presets / select_none nor the base _on_revert_to_custom
hook touched it. So after customizing Thymio blocks and saving, the config
persisted under the stale default preset_name 'full', and load_config's
'full' migration re-added every disabled block (and a project's
blockly_preset got the stale name, reverting the restriction immediately).

The dialog now marks the config 'custom' on every block-changing path.
Tested by driving the real methods on an instance built with __new__ (no
Qt UI needed) and a real BlocklyConfig.
"""

import pytest

from config.blockly_config import BlocklyConfig


def _dialog_with_config():
    from dialogs.thymio_config_dialog import ThymioConfigDialog
    dlg = ThymioConfigDialog.__new__(ThymioConfigDialog)
    dlg.config = BlocklyConfig(preset_name="full")
    # select_none calls load_config_to_ui; stub it (no UI in this test).
    dlg.load_config_to_ui = lambda: None
    return dlg


class TestMarksCustom:
    def test_apply_basic_marks_custom(self):
        dlg = _dialog_with_config()
        dlg._apply_thymio_basic()
        assert dlg.config.preset_name == "custom"

    def test_apply_sensors_marks_custom(self):
        dlg = _dialog_with_config()
        dlg._apply_thymio_sensors()
        assert dlg.config.preset_name == "custom"

    def test_apply_full_marks_custom(self):
        dlg = _dialog_with_config()
        dlg._apply_thymio_full()
        assert dlg.config.preset_name == "custom"

    def test_select_none_marks_custom(self):
        dlg = _dialog_with_config()
        dlg.select_none()
        assert dlg.config.preset_name == "custom"

    def test_manual_toggle_hook_marks_custom(self):
        dlg = _dialog_with_config()
        # The base dialog calls _on_revert_to_custom when the user toggles a
        # checkbox; pre-fix it was the inherited no-op.
        dlg._on_revert_to_custom()
        assert dlg.config.preset_name == "custom"

    def test_basic_actually_restricts_and_keeps_custom(self):
        """A restriction (disable a category) survives because the config is
        now 'custom', not 'full' (which the load migration would re-expand)."""
        dlg = _dialog_with_config()
        dlg._apply_thymio_basic()
        # Buttons+motors enabled, others disabled — and marked custom so the
        # 'full' re-add migration won't fire on next load.
        assert dlg.config.preset_name == "custom"
        assert "Thymio Events" in dlg.config.enabled_categories
        assert "Thymio Sensors" not in dlg.config.enabled_categories

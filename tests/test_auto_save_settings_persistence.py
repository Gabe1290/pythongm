"""Regression tests for Auto-Save settings persistence (audit M6).

docs/FULL_AUDIT_2026-06-11.md: the Auto-Save Settings dialog wrote
top-level Config keys ('auto_save_enabled', 'auto_save_interval' in
seconds) that IDE startup never reads — the timer is wired from
Config.get_editor_config() ('editor.auto_save_*', interval in MINUTES) and
the top-level enabled flag drove only the menu checkbox. So the dialog's
choice evaporated on restart and the checkbox desynchronized from the
real timer.

Now the dialog (and the menu toggle) persist to the editor config that
startup reads, and the checkbox init reads from the same store.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture
def isolated_config():
    from utils.config import Config
    saved = Config._config_data
    Config._config_data = {}
    with patch.object(Config, 'save'):  # don't touch the real config file
        yield Config
    Config._config_data = saved


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _stub():
    return SimpleNamespace(
        project_manager=MagicMock(auto_save_interval=30000),
        auto_save_action=MagicMock(),
        update_status=lambda *a: None,
        tr=lambda s: s,
    )


class _FakeDialog:
    """Stand-in for AutoSaveSettingsDialog with a preset result."""
    result = (False, 120)  # (enabled, interval_seconds)

    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        return True

    def get_settings(self):
        return self.result


class TestDialogPersistsToEditorConfig:
    def test_dialog_writes_editor_config_in_minutes(self, isolated_config):
        _FakeDialog.result = (False, 120)  # 2 minutes
        stub = _stub()
        with patch('dialogs.auto_save_dialog.AutoSaveSettingsDialog', _FakeDialog):
            _ide_cls().show_auto_save_settings(stub)

        editor = isolated_config.get_editor_config()
        assert editor['auto_save_enabled'] is False
        assert editor['auto_save_interval'] == 2  # minutes, the unit startup reads

    def test_sub_minute_interval_clamps_to_one(self, isolated_config):
        _FakeDialog.result = (True, 15)  # 15 seconds
        stub = _stub()
        with patch('dialogs.auto_save_dialog.AutoSaveSettingsDialog', _FakeDialog):
            _ide_cls().show_auto_save_settings(stub)

        assert isolated_config.get_editor_config()['auto_save_interval'] == 1

    def test_session_uses_exact_seconds(self, isolated_config):
        _FakeDialog.result = (True, 45)
        stub = _stub()
        with patch('dialogs.auto_save_dialog.AutoSaveSettingsDialog', _FakeDialog):
            _ide_cls().show_auto_save_settings(stub)
        # set_auto_save is called with the exact 45s (in ms), not the rounded
        # persisted minutes.
        stub.project_manager.set_auto_save.assert_called_once_with(True, 45000)


class TestTogglePersists:
    def test_menu_toggle_persists_enabled_flag(self, isolated_config):
        stub = _stub()
        stub.auto_save_action.isChecked.return_value = False
        with patch('core.ide_window.QMessageBox'):  # toggle shows an info box
            _ide_cls().toggle_auto_save(stub)
        assert isolated_config.get_editor_config()['auto_save_enabled'] is False


class TestRoundTrip:
    def test_dialog_choice_is_what_startup_would_read(self, isolated_config):
        """End-to-end: persist via dialog, then read exactly the way the
        startup timer-wiring does."""
        _FakeDialog.result = (False, 600)  # disabled, 10 min
        stub = _stub()
        with patch('dialogs.auto_save_dialog.AutoSaveSettingsDialog', _FakeDialog):
            _ide_cls().show_auto_save_settings(stub)

        editor_cfg = isolated_config.get_editor_config()
        startup_enabled = editor_cfg.get('auto_save_enabled', True)
        startup_interval_ms = editor_cfg.get('auto_save_interval', 5) * 60 * 1000
        assert startup_enabled is False
        assert startup_interval_ms == 10 * 60 * 1000

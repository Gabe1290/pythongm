"""Preferences -> Advanced -> "Allow several IDE instances at the same time".

The single-instance guard (core/single_instance.py) was env-var-only
(PYGM_ALLOW_MULTIPLE_INSTANCES=1), which a teacher or student launching from a
desktop shortcut cannot set. The same opt-out now lives in the Advanced tab as
``advanced.allow_multiple_instances`` (default off -- the guard stays on).

Hand-rolled offscreen QApplication (no qapp fixture), per the repo's
audit-regression convention, so this runs without pytest-qt.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV = "PYGM_ALLOW_MULTIPLE_INSTANCES"


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


def _advanced(allow):
    from utils.config import Config
    base = Config.get_advanced_config()
    base["allow_multiple_instances"] = allow
    return base


class TestConfigDefault:
    def test_default_is_off(self):
        from utils.config import Config
        with patch.object(Config, "_config_data", {}):
            assert Config.get_advanced_config()["allow_multiple_instances"] is False

    def test_set_then_get_roundtrip(self):
        from utils.config import Config
        with patch.object(Config, "_config_data", {}), \
                patch.object(Config, "save"):
            Config.set_advanced_config(allow_multiple_instances=True)
            assert Config.get_advanced_config()["allow_multiple_instances"] is True


class TestMultipleInstancesAllowed:
    def test_guard_stays_on_by_default(self, monkeypatch):
        from core.single_instance import multiple_instances_allowed
        monkeypatch.delenv(ENV, raising=False)
        with patch("utils.config.Config.get_advanced_config",
                   return_value=_advanced(False)):
            assert multiple_instances_allowed() is False

    def test_config_setting_opts_out(self, monkeypatch):
        from core.single_instance import multiple_instances_allowed
        monkeypatch.delenv(ENV, raising=False)
        with patch("utils.config.Config.get_advanced_config",
                   return_value=_advanced(True)):
            assert multiple_instances_allowed() is True

    def test_env_var_still_opts_out(self, monkeypatch):
        from core.single_instance import multiple_instances_allowed
        monkeypatch.setenv(ENV, "1")
        with patch("utils.config.Config.get_advanced_config",
                   return_value=_advanced(False)):
            assert multiple_instances_allowed() is True

    @pytest.mark.parametrize("value", ["0", "true", "yes", ""])
    def test_env_var_only_exact_one_counts(self, monkeypatch, value):
        from core.single_instance import multiple_instances_allowed
        monkeypatch.setenv(ENV, value)
        with patch("utils.config.Config.get_advanced_config",
                   return_value=_advanced(False)):
            assert multiple_instances_allowed() is False

    def test_main_uses_the_helper_not_the_raw_env_var(self):
        src = (REPO_ROOT / "main.py").read_text(encoding="utf-8")
        assert "multiple_instances_allowed()" in src
        assert "os.environ.get('PYGM_ALLOW_MULTIPLE_INSTANCES')" not in src


class TestPreferencesCheckbox:
    def test_checkbox_reflects_stored_value(self, _qapp):
        from dialogs.preferences_dialog import PreferencesDialog
        with patch("utils.config.Config.get_advanced_config",
                   return_value=_advanced(True)):
            dialog = PreferencesDialog()
        assert dialog.allow_multiple_instances.isChecked() is True

    def test_checkbox_defaults_unchecked(self, _qapp):
        from dialogs.preferences_dialog import PreferencesDialog
        with patch("utils.config.Config.get_advanced_config",
                   return_value=_advanced(False)):
            dialog = PreferencesDialog()
        assert dialog.allow_multiple_instances.isChecked() is False

    def test_apply_writes_the_checkbox_state(self, _qapp):
        from dialogs.preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog()
        dialog.allow_multiple_instances.setChecked(True)
        with patch("utils.config.Config.set_advanced_config") as mock_set, \
                patch("utils.config.Config.set"), \
                patch("utils.config.Config.set_font_config"), \
                patch("utils.config.Config.set_appearance_config"), \
                patch("utils.config.Config.set_editor_config"), \
                patch("utils.config.Config.set_project_config"), \
                patch("PySide6.QtWidgets.QMessageBox.information"), \
                patch.object(PreferencesDialog, "_apply_extension_settings"), \
                patch.object(PreferencesDialog, "accept"):
            try:
                dialog.apply_settings()
            except Exception:
                pass  # unrelated apply steps (theme etc.); the write is what we assert
        assert mock_set.called
        assert mock_set.call_args.kwargs["allow_multiple_instances"] is True


# ---------------------------------------------------------------- translations
_SPLIT = {"de", "it", "ru", "sl", "uk"}
_LANGS = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk", "ja", "zh"]
_SOURCES = [
    "Multiple IDE windows",
    "Allow several IDE instances at the same time",
    "By default only one PyGameMaker IDE runs at a time, because two "
    "instances saving into the same project folder corrupt it. "
    "Enable this only if you open different projects in each "
    "instance. Takes effect the next time the IDE starts.",
]


def _qm(lang):
    name = f"pygm2_{lang}_core.qm" if lang in _SPLIT else f"pygm2_{lang}.qm"
    return REPO_ROOT / "translations" / name


def test_sources_match_the_dialog_code():
    """The .ts <source> must equal what preferences_dialog.py actually passes
    to tr() -- Qt concatenates adjacent literals, so a drift here silently
    kills the translation."""
    code = (REPO_ROOT / "dialogs" / "preferences_dialog.py").read_text(encoding="utf-8")
    for source in _SOURCES[:2]:
        assert f'self.tr("{source}")' in code or f'self.tr(\n            "{source}")' in code
    flat = re.sub(r'"\s*\n\s*"', "", code)
    assert _SOURCES[2] in flat


def test_runtime_translate_resolves_in_every_language():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    for lang in _LANGS:
        translator = QTranslator()
        assert translator.load(str(_qm(lang))), f"{_qm(lang).name} failed to load"
        app.installTranslator(translator)
        try:
            for source in _SOURCES:
                resolved = QCoreApplication.translate("PreferencesDialog", source)
                assert resolved and resolved != source, (
                    f"{lang}: {source[:40]!r} did not resolve")
        finally:
            app.removeTranslator(translator)

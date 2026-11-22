"""The Thymio events panel, pickers and action configure dialog show translated names
(docs/THYMIO_PANEL_I18N_PLAN.md U3), while projects keep storing what they stored before.

Choice parameters are saved as their English label ("0 - Startup") and the Thymio exporter and
simulator read the number from it (U0), so the combo shows the translation but saves the label.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture
def lang(monkeypatch):
    """Thymio enabled, its tables registered, the IDE switched to a language; English afterwards."""
    from PySide6.QtWidgets import QApplication
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))
    plugin_loader.load_all_plugins()
    QApplication.instance() or QApplication([])
    from core.language_manager import get_language_manager
    manager = get_language_manager()

    def switch(code):
        manager.set_language(code)
    yield switch
    manager.set_language("en")


def _dialog(action, params=None):
    from editors.object_editor.gm80_action_dialog import GM80ActionDialog
    from extensions.thymio.actions import THYMIO_ACTIONS
    return GM80ActionDialog(THYMIO_ACTIONS[action], params)


def _labels(dialog):
    from PySide6.QtWidgets import QLabel
    return [w.text() for w in dialog.findChildren(QLabel)]


def test_the_configure_dialog_is_translated(lang):
    lang("fr")
    d = _dialog("thymio_set_motor_speed")
    try:
        assert "Régler la vitesse des moteurs" in d.windowTitle()
        labels = _labels(d)
        assert any("Vitesse du moteur gauche" in t for t in labels), labels
        assert any("Régler séparément la vitesse" in t for t in labels), labels
    finally:
        d.deleteLater()


def test_a_choice_shows_the_translation_but_saves_the_english_label(lang):
    lang("ja")
    d = _dialog("thymio_play_system_sound", {"sound_id": "3 - Central"})
    try:
        combo = d.param_widgets["sound_id"]
        assert [combo.itemText(i) for i in range(2)] == ["0 - 起動", "1 - 終了"]
        assert combo.currentData() == "3 - Central" and combo.currentText() == "3 - 中央"
        assert d.get_parameter_values()["sound_id"] == "3 - Central"
    finally:
        d.deleteLater()


def test_a_saved_project_reopens_and_saves_back_unchanged(lang):
    """Every Thymio action with a choice, opened in French with each option saved: the same value comes back."""
    from extensions.thymio.actions import THYMIO_ACTIONS
    lang("fr")
    checked = 0
    for name, action in THYMIO_ACTIONS.items():
        for param in action.parameters:
            if param.type != "choice" or not param.options:
                continue
            for option in param.options:
                d = _dialog(name, {param.name: str(option)})
                try:
                    assert d.get_parameter_values()[param.name] == str(option), (name, param.name, option)
                    checked += 1
                finally:
                    d.deleteLater()
    assert checked > 30


def test_the_pickers_are_translated(lang):
    from extensions.thymio.dialogs.thymio_action_selector import ThymioActionSelector
    from extensions.thymio.dialogs.thymio_event_selector import ThymioEventSelector
    lang("fr")
    events, actions = ThymioEventSelector(), ThymioActionSelector()
    try:
        event_texts = [events.event_list.item(i).text() for i in range(events.event_list.count())]
        action_texts = [actions.action_list.item(i).text() for i in range(actions.action_list.count())]
        assert any("Bouton central" in t for t in event_texts), event_texts[:3]
        assert any("Avancer" in t and "paramètre(s)" in t for t in action_texts), action_texts[:3]
        assert not any("Button Center" in t or "Move Forward" in t for t in event_texts + action_texts)
    finally:
        events.deleteLater()
        actions.deleteLater()


def test_english_is_unchanged(lang):
    lang("en")
    d = _dialog("thymio_play_system_sound", {"sound_id": "3 - Central"})
    try:
        combo = d.param_widgets["sound_id"]
        assert combo.currentText() == "3 - Central"
        assert any("Play System Sound" in t for t in _labels(d)) or "Play System Sound" in d.windowTitle()
    finally:
        d.deleteLater()


def test_the_thymio_tab_tree_is_translated(lang):
    from extensions.thymio.object_editor_panel import ThymioEventsPanel
    from PySide6.QtWidgets import QTreeWidget
    lang("de")
    panel = ThymioEventsPanel()
    try:
        panel.load_events_data({"thymio_button_center": {"actions": [
            {"action": "thymio_stop_motors", "parameters": {}}]}})
        tree = panel.findChildren(QTreeWidget)[0]
        top = tree.topLevelItem(0)
        assert "Mittlere Taste" in top.text(0), top.text(0)
        assert "Motoren anhalten" in top.child(0).text(0), top.child(0).text(0)
        assert top.toolTip(0).startswith("Wird ausgeführt, wenn die Taste mittlere")
    finally:
        panel.deleteLater()

"""The Standard events panel and the action dialog show the core names from config/ui_names, and a
project still saves exactly what it saved before (docs/CORE_NAMES_I18N_PLAN.md U3).

Choice parameters used to be saved as the combo's shown text, so the combo now shows the
translation with the English value as item data; every choice of every action is opened and saved
here in French and must come back unchanged. A real offscreen QApplication, no pytest-qt.
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
    """Every extension on, the IDE switched to a language; English afterwards."""
    from PySide6.QtWidgets import QApplication
    from events import plugin_loader
    monkeypatch.setattr(plugin_loader, "is_extension_enabled", lambda folder, default=True: True)
    plugin_loader.load_all_plugins()
    QApplication.instance() or QApplication([])
    from core.language_manager import get_language_manager
    manager = get_language_manager()
    yield manager.set_language
    manager.set_language("en")
    from core.ui_names import clear_ui_translations
    clear_ui_translations()
    monkeypatch.undo()
    plugin_loader.load_all_plugins()


def _dialog(action, params=None):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type
    return ActionConfigDialog(get_action_type(action), params or {})


def _choice_params():
    from events.action_types import ACTION_TYPES
    for name, action in ACTION_TYPES.items():
        if name == "if_condition":          # its own editor, already stores canonical values
            continue
        for param in action.parameters:
            if param.choices and param.param_type != "multi_choice" and param.name not in ("then_action", "else_action"):
                yield name, param


def test_the_dialog_shows_the_french_name(lang):
    lang("fr")
    d = _dialog("set_hspeed")
    try:
        assert "Définir la vitesse horizontale" in d.windowTitle()
    finally:
        d.deleteLater()


def test_the_panel_tree_shows_the_french_name(lang):
    from editors.object_editor.events import ObjectEventsPanel
    lang("fr")
    panel = ObjectEventsPanel()
    try:
        panel.current_events_data = {"create": {"actions": [{"action": "set_hspeed", "parameters": {"speed": 4}}]}}
        panel.refresh_events_display()
        top = panel.events_tree.topLevelItem(0)
        texts = [top.child(i).text(0) for i in range(top.childCount())]
        assert any("Définir la vitesse horizontale" in t for t in texts), texts
    finally:
        panel.deleteLater()


def test_every_choice_saves_back_unchanged_in_french(lang):
    lang("fr")
    checked = 0
    for name, param in _choice_params():
        for option in param.choices:
            d = _dialog(name, {param.name: option})
            try:
                assert d.get_parameter_values()[param.name] == str(option), (name, param.name, option)
                checked += 1
            finally:
                d.deleteLater()
    assert checked > 100


def test_a_translated_choice_is_shown_translated_and_saved_in_english(lang):
    from core.ui_names import register_ui_translations
    lang("fr")
    register_ui_translations({"core.choice": {"right": {"fr": "droite"}}})
    d = _dialog("move_grid", {"direction": "right"})
    try:
        combo = d.param_widgets["direction"]
        assert combo.currentText() == "droite" and combo.currentData() == "right"
        assert d.get_parameter_values()["direction"] == "right"
    finally:
        d.deleteLater()


def test_a_typed_object_name_is_still_saved_as_typed(lang):
    lang("fr")
    d = _dialog("if_collision_at", {"object_type": "any"})
    try:
        combo = d.param_widgets["object_type"]
        combo.setEditText("obj_lava")
        assert d.get_parameter_values()["object_type"] == "obj_lava"
    finally:
        d.deleteLater()


def test_english_is_unchanged(lang):
    lang("en")
    d = _dialog("move_grid", {"direction": "left"})
    try:
        combo = d.param_widgets["direction"]
        assert combo.currentText() == "left"
        assert "Move Grid" in d.windowTitle()
    finally:
        d.deleteLater()

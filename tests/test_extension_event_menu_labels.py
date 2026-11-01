"""The Blockly "extension event" drop-down speaks the IDE language (micro:bit follow-up M2).

``event_extension``'s choices were the English ``EventType.display_name``. Extensions now add
``"events": {event: {lang: label}}`` to PLUGIN_GENERATED_BLOCK_TRANSLATIONS; the menu resolves
through it and falls back to English. The event *value* (what is saved and compared) never changes.
"""
import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import blockly_generated_block_i18n as I18N  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402

FOLDERS = ["microbit", "multiplayer_lan", "multiplayer_files"]


def _events(folder):
    module = importlib.import_module(f"extensions.{folder}")
    return module.PLUGIN_EVENTS if hasattr(module, "PLUGIN_EVENTS") else {}


@pytest.fixture(autouse=True)
def _plugins():
    load_all_plugins()
    for folder in FOLDERS:           # an extension this box disables is still translated
        I18N.register_generated_block_translations(
            importlib.import_module(f"extensions.{folder}").PLUGIN_GENERATED_BLOCK_TRANSLATIONS)


@pytest.mark.parametrize("folder", FOLDERS)
def test_every_event_of_the_extension_has_a_french_label_that_differs_from_english(folder):
    events = _events(folder)
    assert events
    for name, event in events.items():
        label = I18N.get_translated_event_display_name(name, "fr", event.display_name)
        assert label and label != event.display_name, name


def test_the_translated_set_is_exactly_the_events_it_provides():
    for folder in FOLDERS:
        module = importlib.import_module(f"extensions.{folder}")
        declared = set(module.PLUGIN_GENERATED_BLOCK_TRANSLATIONS["events"])
        assert declared == set(_events(folder)), folder


def test_french_keeps_its_accents():
    labels = {n: I18N.EVENT_TRANSLATIONS[n]["fr"] for f in FOLDERS for n in _events(f)}
    assert labels["microbit_gesture_screen_up"] == "Écran vers le haut"
    assert labels["network_started"] == "Réseau prêt"
    assert labels["file_session_started"] == "Session par fichiers démarrée"
    assert not any("e" in l and l.startswith("Ecran") for l in labels.values())


def test_english_unknown_language_and_unknown_event_fall_back():
    assert I18N.get_translated_event_display_name("microbit_button_a", "en", "Button A Pressed") == "Button A Pressed"
    assert I18N.get_translated_event_display_name("microbit_button_a", "xx", "Button A Pressed") == "Button A Pressed"
    assert I18N.get_translated_event_display_name("no_such_event", "fr", "Fallback") == "Fallback"


def test_registering_events_never_overwrites_and_is_optional():
    I18N.register_generated_block_translations({"events": {"microbit_button_a": {"fr": "HIJACK", "xx": "xx label"}}})
    try:
        assert I18N.get_translated_event_display_name("microbit_button_a", "fr", "x") == "Bouton A pressé"
        assert I18N.get_translated_event_display_name("microbit_button_a", "xx", "x") == "xx label"
    finally:
        I18N.EVENT_TRANSLATIONS["microbit_button_a"].pop("xx", None)
    I18N.register_generated_block_translations({"actions": {}})        # no "events" key: harmless


def test_the_menu_uses_the_language_but_the_saved_value_is_unchanged():
    from config.toolbox_visibility import extension_event_menu
    project = {"settings": {"active_extensions": ["microbit"]}}
    english = {value: label for label, value in extension_event_menu(project)}
    french = {value: label for label, value in extension_event_menu(project, "fr")}
    assert set(english) == set(french) and len(french) == 24
    assert english["microbit_button_a"] == "Button A Pressed"
    assert french["microbit_button_a"] == "Bouton A pressé"
    assert extension_event_menu(project, "xx") == extension_event_menu(project)          # fallback = English
    assert extension_event_menu(project) == extension_event_menu(project, "en")


def test_the_widget_passes_the_ide_language():
    source = (Path(__file__).resolve().parent.parent / "editors/object_editor/blockly_widget.py").read_text(encoding="utf-8")
    assert "extension_event_menu(self._find_project_data(), language)" in source

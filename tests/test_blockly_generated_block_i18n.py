"""Regression tests for TODO.md's "Blockly: generated/custom blocks never
localize" (found 2026-10-16): every action with no hand-written Blockly
block (config.blockly_config.GENERATED_ACTION_NAMES, ~79 actions) rendered
its block face -- label, parameter field labels, tooltip -- in raw English
on the live Blockly workspace CANVAS regardless of IDE language, because
editors/object_editor/blockly_widget.py's _register_custom_blocks() sent
ActionType text straight to blockly_workspace.html's registerCustomBlocks()
with zero language awareness.

This is a SEPARATE surface/table from config.blockly_translations (which
covers the "Configure Action Blocks" dialog) -- see
tests/test_blockly_config_dialog_control_game_views_i18n.py for that one.

Scoping decision: French only this pass (the action-level text was free --
already translated in config.blockly_translations.BLOCK_TRANSLATIONS or
tools/action_ref_i18n.py's ACTIONS_FR; only the 119 distinct parameter
field labels needed fresh translation). Other languages logged as a
follow-up in TODO.md.
"""
import json

import pytest

from conftest import dispose_qt_widget
from config.blockly_config import GENERATED_ACTION_NAMES
from events.action_types import ACTION_TYPES
from config.blockly_generated_block_i18n import (
    ACTION_TRANSLATIONS,
    PARAM_LABEL_TRANSLATIONS,
    get_translated_action_display_name,
    get_translated_action_description,
    get_translated_param_label,
)


def test_every_generated_action_has_a_french_translation():
    missing = [n for n in sorted(GENERATED_ACTION_NAMES) if n not in ACTION_TRANSLATIONS]
    assert missing == []


def test_every_generated_actions_parameter_labels_have_a_french_translation():
    missing = set()
    for name in GENERATED_ACTION_NAMES:
        for p in (ACTION_TYPES[name].parameters or []):
            if p.display_name not in PARAM_LABEL_TRANSLATIONS["fr"]:
                missing.add(p.display_name)
    assert missing == set()


def test_lookup_functions_fall_back_to_english():
    assert get_translated_action_display_name("bounce", "en", "Bounce") == "Bounce"
    assert get_translated_action_description("bounce", "en", "Bounce off") == "Bounce off"
    assert get_translated_param_label("Speed", "en") == "Speed"
    # An untranslated language (not yet added) falls back too, same as 'en'.
    assert get_translated_action_display_name("bounce", "de", "Bounce") == "Bounce"
    assert get_translated_param_label("Speed", "de") == "Speed"
    # An unknown label (typo, or a label this table never covered) is
    # returned unchanged rather than raising.
    assert get_translated_param_label("Something Unmapped", "fr") == "Something Unmapped"


def test_lookup_functions_translate_french():
    assert get_translated_action_display_name("bounce", "fr", "Bounce") == "Rebondir"
    assert get_translated_param_label("Speed", "fr") == "Vitesse"
    assert get_translated_param_label("Object", "fr") == "Objet"


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


def _captured_action_defs(widget):
    """_register_custom_blocks() builds a JS snippet embedding the JSON
    payload as an escaped string literal (not a direct function-call
    argument the way apply_configuration's reconfigureToolbox(...) is) --
    unwrap it the same way it was escaped, in reverse."""
    captured = {}

    def _capture(js, *_args, **_kwargs):
        start = js.index("JSON.parse('") + len("JSON.parse('")
        end = js.index("')", start)
        escaped = js[start:end]
        raw = escaped.replace("\\n", "\n").replace("\\'", "'").replace("\\\\", "\\")
        captured["defs"] = json.loads(raw)

    widget.web_view.page().runJavaScript = _capture
    widget._register_custom_blocks()
    return {d["name"]: d for d in captured["defs"]}


def test_register_custom_blocks_sends_french_text_when_french_is_active(_qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.language_manager import get_language_manager
    from editors.object_editor.blockly_widget import BlocklyWidget
    from PySide6.QtWidgets import QMainWindow

    class _IDE(QMainWindow):
        current_project_data = None

    manager = get_language_manager()
    previous_language = manager.get_current_language()
    manager.set_language("fr")
    ide = _IDE()
    widget = BlocklyWidget(ide)
    try:
        defs = _captured_action_defs(widget)
        bounce = defs["bounce"]
        assert bounce["display_name"] == "Rebondir"
        assert bounce["description"] == "Rebondir sur les objets solides"

        set_direction_speed = defs["set_direction_speed"]
        param_labels = {p["name"]: p["display_name"] for p in set_direction_speed["parameters"]}
        # direction/speed params use the translated "Direction"/"Vitesse" labels.
        assert "Direction" in param_labels.values() or "Vitesse" in param_labels.values()
    finally:
        dispose_qt_widget(widget)
        manager.set_language(previous_language)


def test_register_custom_blocks_keeps_english_when_english_is_active(_qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.language_manager import get_language_manager
    from editors.object_editor.blockly_widget import BlocklyWidget
    from PySide6.QtWidgets import QMainWindow

    class _IDE(QMainWindow):
        current_project_data = None

    manager = get_language_manager()
    previous_language = manager.get_current_language()
    manager.set_language("en")
    ide = _IDE()
    widget = BlocklyWidget(ide)
    try:
        defs = _captured_action_defs(widget)
        bounce = defs["bounce"]
        assert bounce["display_name"] == ACTION_TYPES["bounce"].display_name
        assert bounce["description"] == ACTION_TYPES["bounce"].description
    finally:
        dispose_qt_widget(widget)
        manager.set_language(previous_language)


def test_register_custom_blocks_untranslated_language_falls_back_to_english(_qapp):
    """A language with no entry in this table yet (e.g. German, logged as
    a follow-up in TODO.md) must render the same raw English it did before
    this fix -- never a KeyError, never a blank label."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.language_manager import get_language_manager
    from editors.object_editor.blockly_widget import BlocklyWidget
    from PySide6.QtWidgets import QMainWindow

    class _IDE(QMainWindow):
        current_project_data = None

    manager = get_language_manager()
    previous_language = manager.get_current_language()
    manager.set_language("de")
    ide = _IDE()
    widget = BlocklyWidget(ide)
    try:
        defs = _captured_action_defs(widget)
        bounce = defs["bounce"]
        assert bounce["display_name"] == ACTION_TYPES["bounce"].display_name
    finally:
        dispose_qt_widget(widget)
        manager.set_language(previous_language)


def test_hand_written_blocks_are_unaffected_by_this_change(_qapp):
    """Actions with a REAL hand-written block (set_variable, if_condition,
    ... -- promoted out of GENERATED_ACTION_NAMES, already have working
    per-language text via BLOCK_MESSAGES on the JS side) are still sent
    through unfiltered (Python sends the full ACTION_TYPES, same as
    before this fix -- JS is what skips creating a block for them), just
    with their own text untouched since they have no entry in
    ACTION_TRANSLATIONS."""
    assert "set_variable" not in GENERATED_ACTION_NAMES  # hand-written, not this fix's concern

    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from core.language_manager import get_language_manager
    from editors.object_editor.blockly_widget import BlocklyWidget
    from PySide6.QtWidgets import QMainWindow

    class _IDE(QMainWindow):
        current_project_data = None

    manager = get_language_manager()
    previous_language = manager.get_current_language()
    manager.set_language("fr")
    ide = _IDE()
    widget = BlocklyWidget(ide)
    try:
        defs = _captured_action_defs(widget)
        assert "set_variable" in defs
        assert defs["set_variable"]["display_name"] == ACTION_TYPES["set_variable"].display_name
    finally:
        dispose_qt_widget(widget)
        manager.set_language(previous_language)

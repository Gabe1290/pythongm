"""Regression tests for the Configure Action Blocks dialog i18n gap reported
2026-10-18: "the Configure Action Blocks dialog still shows some labels (like
'Control', 'Set Variable') in English even in a non-English IDE".

Root cause, wider than the two literal examples named: `config/
blockly_translations.py`'s CATEGORY_TRANSLATIONS had no "Control"/"Game"/
"Views" entry in ANY of the 7 languages (de/es/fr/it/ru/sl/uk) -- not a
missing-block gap, the whole category label fell back to English -- and
BLOCK_TRANSLATIONS had no entry for any of the 9 Control blocks, 9 Game
blocks, or 2 Views blocks either, so every block inside those 3 categories
showed its raw English name/description regardless of active language too.

This fix closes those 3 categories completely (label + every child block,
all 7 languages). A separate, milder gap remains -- 32 blocks scattered
inside categories that already HAD a translated label (Events/Movement/
Drawing/Score-Lives-Health/Instance/Room) -- logged in TODO.md as a
follow-up, not fixed here (see that entry for the exact list and why it's a
smaller, less jarring gap than this one was).
"""
import pytest

from config.blockly_config import BLOCK_REGISTRY
from config.blockly_translations import (
    BLOCK_TRANSLATIONS,
    CATEGORY_TRANSLATIONS,
    get_translated_block_description,
    get_translated_block_name,
    get_translated_category,
)

LANGS = ["de", "es", "fr", "it", "ru", "sl", "uk"]
NEW_CATEGORIES = ["Control", "Game", "Views"]
NEW_BLOCKS = {
    "Control": ["if_condition", "set_variable", "test_variable", "test_expression",
                "check_empty", "exit_event", "else_action", "start_block", "end_block"],
    "Game": ["restart_game", "load_game", "save_game", "open_webpage",
             "set_window_caption", "show_info", "show_video",
             "splash_show_image", "splash_show_text"],
    "Views": ["enable_views", "set_view"],
}


@pytest.mark.parametrize("category", NEW_CATEGORIES)
def test_category_translated_in_every_language(category):
    for lang in LANGS:
        assert category in CATEGORY_TRANSLATIONS[lang], (category, lang)
        translated = CATEGORY_TRANSLATIONS[lang][category]
        assert translated, (category, lang)


def test_category_translations_match_block_registry_exactly():
    """Every block registered under Control/Game/Views now has a real
    translation entry -- this would fail if BLOCK_REGISTRY ever gains a new
    block in one of these 3 categories without a matching translation."""
    for category, expected_types in NEW_BLOCKS.items():
        registry_types = {b["type"] for b in BLOCK_REGISTRY[category]}
        assert registry_types == set(expected_types), category


@pytest.mark.parametrize("category,block_types", NEW_BLOCKS.items())
def test_every_new_block_has_name_and_description_in_every_language(category, block_types):
    for block_type in block_types:
        assert block_type in BLOCK_TRANSLATIONS, block_type
        entry = BLOCK_TRANSLATIONS[block_type]
        assert set(entry.keys()) == {"name", "description"}, block_type
        for field in ("name", "description"):
            for lang in LANGS:
                value = entry[field].get(lang)
                assert value, (block_type, field, lang)


def test_get_translated_category_resolves_for_a_sample_of_languages():
    assert get_translated_category("Control", "de") == "Steuerung"
    assert get_translated_category("Control", "fr") == "Contrôle"
    assert get_translated_category("Game", "ru") == "Игра"
    assert get_translated_category("Views", "uk") == "Перегляди"


def test_get_translated_block_name_and_description_resolve():
    assert get_translated_block_name("set_variable", "fr") == "Définir Variable"
    assert get_translated_block_description("set_variable", "fr")
    assert get_translated_block_name("restart_game", "de") == "Spiel neu starten"
    assert get_translated_block_name("enable_views", "it") == "Attiva Viste"


def test_english_still_falls_back_to_the_literal_registry_text():
    """language="en" must keep returning the raw English strings -- the
    lookup functions' own documented fallback, unaffected by this fix."""
    assert get_translated_category("Control", "en") == "Control"
    assert get_translated_block_name("set_variable", "en") is None
    assert get_translated_block_description("set_variable", "en") is None


def test_configure_action_blocks_dialog_shows_translated_labels_in_french(qapp_for_dialog):
    """Drives the real dialog (dialogs/_block_config_dialog_base.py via
    BlocklyConfigDialog) with French active and asserts the Control/Game/
    Views top-level tree items -- and a sample of their children -- render
    translated text, not the raw English BLOCK_REGISTRY strings."""
    from core.language_manager import get_language_manager
    from dialogs.blockly_config_dialog import BlocklyConfigDialog

    manager = get_language_manager()
    previous_language = manager.get_current_language()
    manager.set_language("fr")
    try:
        dlg = BlocklyConfigDialog()
        try:
            top_level_texts = {
                dlg.tree.topLevelItem(i).text(0)
                for i in range(dlg.tree.topLevelItemCount())
            }
            assert "Contrôle" in top_level_texts
            assert "Jeu" in top_level_texts
            assert "Vues" in top_level_texts
            assert "Control" not in top_level_texts
            assert "Game" not in top_level_texts
            assert "Views" not in top_level_texts

            def _child_texts(category_label):
                for i in range(dlg.tree.topLevelItemCount()):
                    item = dlg.tree.topLevelItem(i)
                    if item.text(0) == category_label:
                        return {item.child(j).text(0) for j in range(item.childCount())}
                raise AssertionError(f"{category_label} not found in tree")

            control_children = _child_texts("Contrôle")
            assert "Définir Variable" in control_children
            assert "Set Variable" not in control_children

            game_children = _child_texts("Jeu")
            assert "Redémarrer le Jeu" in game_children
            assert "Restart Game" not in game_children

            views_children = _child_texts("Vues")
            assert "Activer les Vues" in views_children
        finally:
            dlg.deleteLater()
    finally:
        manager.set_language(previous_language)


@pytest.fixture
def qapp_for_dialog():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])

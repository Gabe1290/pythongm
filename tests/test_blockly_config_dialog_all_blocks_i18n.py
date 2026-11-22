"""Every block in the Configure Blocks dialog is translated (2026-11-21).

The dialog names each category and block through config/blockly_translations.py.
After the Control/Game/Views fix (test_blockly_config_dialog_control_game_views_i18n.py)
32 blocks inside already-translated categories still showed English names and
descriptions (Other Events, Move Free, Draw Line, Test Score, End Game...).
They are translated now; this guard keeps EVERY registered block translated in
the seven languages these tables cover, so a new block cannot slip in English.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.blockly_config import BLOCK_REGISTRY  # noqa: E402
from config.blockly_translations import BLOCK_TRANSLATIONS, CATEGORY_TRANSLATIONS  # noqa: E402

LANGS = ("de", "es", "fr", "it", "ru", "sl", "uk", "pl", "pt")
ALL_BLOCKS = [b for blocks in BLOCK_REGISTRY.values() for b in blocks]


@pytest.mark.parametrize("lang", LANGS)
def test_every_block_has_a_name_and_description(lang):
    missing = [b["type"] for b in ALL_BLOCKS
               if not (BLOCK_TRANSLATIONS.get(b["type"], {}).get("name", {}).get(lang)
                       and BLOCK_TRANSLATIONS[b["type"]].get("description", {}).get(lang))]
    assert not missing, (lang, missing)


@pytest.mark.parametrize("lang", LANGS)
def test_every_category_is_translated(lang):
    assert set(BLOCK_REGISTRY) <= set(CATEGORY_TRANSLATIONS[lang]), set(BLOCK_REGISTRY) - set(CATEGORY_TRANSLATIONS[lang])


# Block names that really are the same word as the English (checked by hand).
SAME_WORD = {("fr", "event_collision"), ("fr", "value_score"),
             ("it", "value_mouse_x"), ("it", "value_mouse_y")}


@pytest.mark.parametrize("lang", LANGS)
def test_no_block_name_is_left_in_english(lang):
    same = [b["type"] for b in ALL_BLOCKS
            if BLOCK_TRANSLATIONS[b["type"]]["name"][lang] == b["name"]
            and (lang, b["type"]) not in SAME_WORD]
    assert not same, (lang, same)


def test_french_accents_in_the_new_entries():
    fr = {t: BLOCK_TRANSLATIONS[t]["name"]["fr"] for t in ("event_other", "room_goto_previous", "set_direction")}
    assert fr == {"event_other": "Autres événements", "room_goto_previous": "Salle précédente",
                  "set_direction": "Définir la direction"}


def test_the_dialog_shows_the_translations():
    """Through the real dialog: build it in German and read the tree."""
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager
    from dialogs.blockly_config_dialog import BlocklyConfigDialog

    QApplication.instance() or QApplication([])
    get_language_manager().set_language("de")
    try:
        dialog = BlocklyConfigDialog()
        texts = set()
        for i in range(dialog.tree.topLevelItemCount()):
            top = dialog.tree.topLevelItem(i)
            texts.add(top.text(0))
            for j in range(top.childCount()):
                texts.add(top.child(j).text(0))
                texts.add(top.child(j).text(1))
        for expected in ("Weitere Ereignisse", "Linie zeichnen", "Punktzahl prüfen", "Spiel beenden"):
            assert any(expected in t for t in texts), expected
        assert not any(t in ("Other Events", "Draw Line", "Test Score", "End Game") for t in texts)
        dialog.deleteLater()
    finally:
        get_language_manager().set_language("en")


@pytest.mark.parametrize("lang", __import__("config.blockly_translations", fromlist=["x"]).MODULE_LANGUAGES)
def test_the_dialog_is_translated_in_the_module_languages(lang):
    """pl/pt/ja/zh live in config/blockly_block_i18n_<lang>.py; build the real
    dialog in that language and check every category and block it shows."""
    import importlib
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager
    from dialogs.blockly_config_dialog import BlocklyConfigDialog

    mod = importlib.import_module(f"config.blockly_block_i18n_{lang}")
    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    try:
        dialog = BlocklyConfigDialog()
        tops = [dialog.tree.topLevelItem(i) for i in range(dialog.tree.topLevelItemCount())]
        shown = {top.text(0) for top in tops} | {top.child(j).text(0) for top in tops for j in range(top.childCount())}
        for text in mod.CATEGORIES.values():
            assert any(text in t for t in shown), (lang, text)
        for name, _desc in list(mod.BLOCKS.values())[:20]:
            assert any(name in t for t in shown), (lang, name)
        assert not any(t.strip() in ("Movement", "Drawing", "Instance") for t in shown), lang
        dialog.deleteLater()
    finally:
        get_language_manager().set_language("en")

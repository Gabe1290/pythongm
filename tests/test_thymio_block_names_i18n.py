"""Thymio block and event names in the Configure dialog, every language (2026-11-22).

docs/THYMIO_BLOCKS_I18N_2026-11-22.md U1: ThymioConfigDialog showed its 42
entries (28 blocks + 14 events) in English in every language. The extension now
supplies PLUGIN_BLOCK_TRANSLATIONS, which the plugin loader merges into
config.blockly_translations. (The Thymio events panel and action list keep their
English names; the French activity sheets rely on them.)
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.thymio.block_translations import LANGS, PLUGIN_BLOCK_TRANSLATIONS  # noqa: E402
from extensions.thymio.blockly_categories import PLUGIN_BLOCK_CATEGORIES  # noqa: E402

ENTRIES = {b["type"]: b for blocks in PLUGIN_BLOCK_CATEGORIES.values() for b in blocks}
# Names that really are the same word as the English (checked by hand).
SAME_WORD = {("de", "thymio_timer_0"), ("de", "thymio_timer_1"), ("it", "thymio_timer_0"), ("it", "thymio_timer_1")}


def test_every_entry_has_a_name_and_description_in_every_language():
    assert set(PLUGIN_BLOCK_TRANSLATIONS) == set(ENTRIES)
    for block, entry in PLUGIN_BLOCK_TRANSLATIONS.items():
        for field in ("name", "description"):
            assert set(entry[field]) == set(LANGS), (block, field)
            assert all(text.strip() for text in entry[field].values()), (block, field)


def test_no_name_is_left_in_english():
    same = [(lang, block) for block, entry in PLUGIN_BLOCK_TRANSLATIONS.items() for lang, text in entry["name"].items()
            if text == ENTRIES[block]["name"] and (lang, block) not in SAME_WORD]
    assert not same, same


def test_french_keeps_its_accents():
    fr = {b: e["name"]["fr"] for b, e in PLUGIN_BLOCK_TRANSLATIONS.items()}
    assert fr["thymio_leds_off"] == "Éteindre les LED"
    assert fr["thymio_tap"] == "Tapotement détecté"


@pytest.fixture
def _thymio_enabled(monkeypatch):
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


@pytest.mark.parametrize("lang, block, expected", [
    ("fr", "thymio_move_forward", "Avancer"), ("de", "thymio_stop_motors", "Motoren anhalten"),
    ("ja", "thymio_leds_off", "LED を消す"), ("zh", "thymio_button_center", "中间按钮"),
    ("pl", "thymio_play_tone", "Zagraj ton")])
def test_the_loaded_extension_registers_them(_thymio_enabled, lang, block, expected):
    from events.plugin_loader import load_all_plugins
    from config.blockly_translations import get_translated_block_name
    load_all_plugins()
    assert get_translated_block_name(block, lang) == expected


def test_the_thymio_configure_dialog_shows_them(_thymio_enabled):
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from extensions.thymio.dialogs.thymio_config_dialog import ThymioConfigDialog
    QApplication.instance() or QApplication([])
    get_language_manager().set_language("fr")
    try:
        d = ThymioConfigDialog()
        shown = set()
        for i in range(d.tree.topLevelItemCount()):
            top = d.tree.topLevelItem(i)
            shown |= {top.child(j).text(0) for j in range(top.childCount())}
        for expected in ("Avancer", "Éteindre les LED", "Bouton central", "Si le sol est sombre"):
            assert any(expected in text for text in shown), expected
        assert not any(text.strip() in ("Move Forward", "Turn Off LEDs", "Center Button") for text in shown)
        d.deleteLater()
    finally:
        get_language_manager().set_language("en")

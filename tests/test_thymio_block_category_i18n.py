"""Thymio's Configure dialog category names exist in all eleven languages (2026-11-22).

The Thymio extension supplies its toolbox category names through
PLUGIN_BLOCK_CATEGORY_TRANSLATIONS; pl, pt, ja and zh were missing, so in those
languages the eight "Thymio ..." categories showed in English. The block names
themselves stay English on purpose: the Thymio Blockly blocks and actions are
English in the IDE (TODO.md, Thymio entry).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.thymio.blockly_categories import (  # noqa: E402
    PLUGIN_BLOCK_CATEGORIES, PLUGIN_BLOCK_CATEGORY_TRANSLATIONS)

LANGS = ("de", "es", "fr", "it", "ja", "pl", "pt", "ru", "sl", "uk", "zh")


@pytest.mark.parametrize("lang", LANGS)
def test_every_thymio_category_is_translated(lang):
    table = PLUGIN_BLOCK_CATEGORY_TRANSLATIONS[lang]
    assert set(table) == set(PLUGIN_BLOCK_CATEGORIES), lang
    assert all("Thymio" in text and text not in PLUGIN_BLOCK_CATEGORIES for text in table.values()
               if text != "Thymio LEDs"), table


@pytest.fixture
def _thymio_enabled(monkeypatch):
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


@pytest.mark.parametrize("lang, expected", [("ja", "Thymio モーター"), ("pl", "Silniki Thymio"),
                                            ("pt", "Motores do Thymio"), ("zh", "Thymio 电机")])
def test_the_loaded_extension_registers_them(_thymio_enabled, lang, expected):
    from events.plugin_loader import load_all_plugins
    from config.blockly_translations import get_translated_category
    load_all_plugins()
    assert get_translated_category("Thymio Motors", lang) == expected

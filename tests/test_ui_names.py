"""core/ui_names.py: translated names for data (docs/THYMIO_PANEL_I18N_PLAN.md U1)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import ui_names  # noqa: E402


@pytest.fixture
def table():
    saved = {k: {e: dict(v) for e, v in t.items()} for k, t in ui_names._TABLES.items()}
    ui_names.clear_ui_translations()
    ui_names.register_ui_translations({"action": {"Stop Motors": {"fr": "Arrêter les moteurs", "de": "Motoren anhalten"}}})
    yield
    ui_names.clear_ui_translations()
    ui_names._TABLES.update(saved)


def test_a_known_name_is_translated(table):
    assert ui_names.ui_name("action", "Stop Motors", "fr") == "Arrêter les moteurs"


def test_english_and_unknown_fall_back_to_the_english(table):
    assert ui_names.ui_name("action", "Stop Motors", "en") == "Stop Motors"
    assert ui_names.ui_name("action", "Stop Motors", "ja") == "Stop Motors"          # no Japanese entry
    assert ui_names.ui_name("action", "Fly Away", "fr") == "Fly Away"                 # unknown name
    assert ui_names.ui_name("event", "Stop Motors", "fr") == "Stop Motors"            # kinds are separate


def test_non_text_passes_through(table):
    assert ui_names.ui_name("choice", None, "fr") is None
    assert ui_names.ui_name("choice", 3, "fr") == 3


def test_a_later_registration_adds_languages(table):
    ui_names.register_ui_translations({"action": {"Stop Motors": {"ja": "モーターを止める"}}})
    assert ui_names.ui_name("action", "Stop Motors", "ja") == "モーターを止める"
    assert ui_names.ui_name("action", "Stop Motors", "fr") == "Arrêter les moteurs"


def test_the_plugin_loader_registers_an_extensions_table(table, monkeypatch):
    from types import SimpleNamespace
    from events.plugin_loader import PluginLoader
    module = SimpleNamespace(PLUGIN_UI_TRANSLATIONS={"event": {"Button Center": {"fr": "Bouton central"}}})
    PluginLoader._load_block_categories(SimpleNamespace(), module)
    assert ui_names.ui_name("event", "Button Center", "fr") == "Bouton central"

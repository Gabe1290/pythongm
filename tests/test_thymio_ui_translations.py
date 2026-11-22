"""Thymio names for the events panel, action list and configure dialog, in every language
(docs/THYMIO_PANEL_I18N_PLAN.md U2)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.thymio.actions import THYMIO_ACTIONS  # noqa: E402
from extensions.thymio.block_translations import LANGS, PLUGIN_BLOCK_TRANSLATIONS  # noqa: E402
from extensions.thymio.dialogs.thymio_action_selector import THYMIO_ACTION_CATEGORIES  # noqa: E402
from extensions.thymio.events import THYMIO_EVENT_CATEGORIES, THYMIO_EVENT_TYPES  # noqa: E402
from extensions.thymio.ui_translations import PLUGIN_UI_TRANSLATIONS as U  # noqa: E402

PARAMS = [p for a in THYMIO_ACTIONS.values() for p in a.parameters]
NEEDED = {
    "action": {a.display_name for a in THYMIO_ACTIONS.values()},
    "event": {e.display_name for e in THYMIO_EVENT_TYPES.values()},
    "action_description": {a.description for a in THYMIO_ACTIONS.values()},
    "event_description": {e.description for e in THYMIO_EVENT_TYPES.values()},
    "param": {p.display_name for p in PARAMS},
    "param_description": {p.description for p in PARAMS},
    "choice": {str(o) for p in PARAMS for o in (p.options or []) if any(c.isalpha() for c in str(o))},
    "category": {c["name"] for c in list(THYMIO_EVENT_CATEGORIES.values()) + list(THYMIO_ACTION_CATEGORIES.values())},
}


@pytest.mark.parametrize("kind", sorted(NEEDED))
def test_every_string_has_all_eleven_languages(kind):
    missing = sorted(NEEDED[kind] - set(U[kind]))
    incomplete = sorted(e for e in NEEDED[kind] & set(U[kind])
                        if set(U[kind][e]) != set(LANGS) or not all(t.strip() for t in U[kind][e].values()))
    assert not missing and not incomplete, (kind, missing[:5], incomplete[:5])


def test_names_match_the_configure_dialog():
    """The dialog, the Blockly blocks and the panel name each action and event the same way."""
    for registry, kind in ((THYMIO_ACTIONS, "action"), (THYMIO_EVENT_TYPES, "event")):
        for key, item in registry.items():
            assert U[kind][item.display_name] == PLUGIN_BLOCK_TRANSLATIONS[key]["name"], key


def test_choice_labels_keep_their_number():
    """The number before ' - ' is what the exporter and simulator read; every translation keeps it."""
    for english, per_lang in U["choice"].items():
        if " - " in english:
            number = english.split(" - ")[0]
            assert all(t.startswith(number + " - ") for t in per_lang.values()), english


def test_french_keeps_its_accents():
    assert U["action_description"]["Turn off all LEDs (top, bottom, and circle)"]["fr"] == \
        "Éteindre toutes les LED (dessus, dessous et cercle)"
    assert U["choice"]["0 - Startup"]["fr"] == "0 - Démarrage"
    assert U["param"]["Store in Variable"]["fr"] == "Ranger dans la variable"

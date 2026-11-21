"""The raycast stairs' configure-dialog text reads in every shipped language
(docs/RAYCAST_STAIRS_PLAN.md, S13).

ActionConfigDialog passes each parameter label and the action's description
through tr(), so the new labels (Height, Top/Side Texture, Wall Height, Max
Step) and Set Floor Height's description are translated in its context.
Resolved through the real LanguageManager, as the running app does.
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

SHIPPED = ("de", "es", "fr", "it", "ja", "pt", "ru", "sl", "uk", "zh")


def _sources():
    from events.plugin_loader import load_all_plugins
    from events.action_types import get_action_type
    load_all_plugins()
    floor = get_action_type("set_floor_height")
    view = get_action_type("enable_raycast_view")
    labels = [p.display_name for p in floor.parameters]
    labels += [p.display_name for p in view.parameters if p.name in ("wall_height", "max_step")]
    return labels + [floor.description]


def test_the_strings_are_the_ones_the_dialog_shows():
    assert _sources()[:5] == ["Height", "Top Texture", "Side Texture", "Wall Height", "Max Step"]


@pytest.fixture(autouse=True)
def _back_to_english():
    yield
    try:
        from PySide6.QtWidgets import QApplication
        from core.language_manager import get_language_manager
        if QApplication.instance() is not None:
            get_language_manager().set_language("en")
    except Exception:
        pass


@pytest.mark.parametrize("lang", SHIPPED)
def test_every_stairs_string_resolves(lang):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager

    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    unresolved = [s[:40] for s in _sources()
                  if QCoreApplication.translate("ActionConfigDialog", s) == s]
    assert not unresolved, (lang, unresolved)


def test_french_keeps_its_accents():
    text = (ROOT / "translations" / "pygm2_fr.ts").read_text(encoding="utf-8")
    for word in ("Texture du côté", "surélevé", "À utiliser", "l'événement"):
        assert word in text, word


def test_the_action_reference_translates_every_raycast_action():
    """Follow-up F1: the generated wiki reference falls back to English for
    any action missing from tools/action_ref_i18n.py -- set_billboard_rotation
    did, from when it joined the reference (S13) until F1."""
    import json
    sys.path.insert(0, str(ROOT / "tools"))
    import action_ref_i18n as ref
    names = json.loads((ROOT / "extensions" / "raycast_2_5d" / "extension.json")
                       .read_text(encoding="utf-8"))["provides_actions"]
    for code in ("FR", "DE", "UK", "RU", "IT", "ES", "PT", "SL"):
        table = getattr(ref, "ACTIONS_" + code)
        missing = [n for n in names if not (table.get(n) or {}).get("desc")]
        assert not missing, (code, missing)

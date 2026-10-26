"""micro:bit in the Blockly editor (docs/MICROBIT_EXTENSION_PLAN.md, Stage S10).

The extension needs no hand-written blocks: each action is auto-generated into
a "micro:bit" toolbox category, extension events ride the generic
``event_extension`` block, and per-project visibility is core's
``active_extensions`` mechanism. What S10 adds is French text for the
generated blocks, through a generic registration seam. These tests pin that
seam, the French resolution (accents included), the visibility behaviour and
that the generated blocks will be well formed.
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

from events.plugin_loader import load_all_plugins
from events.action_types import ACTION_TYPES
from events.event_types import EVENT_TYPES
from config import blockly_generated_block_i18n as I18N

ACTIONS = [
    "microbit_show_image", "microbit_scroll_text", "microbit_show_number",
    "microbit_set_pixel", "microbit_clear_display", "microbit_set_brightness",
    "microbit_play_tone", "microbit_play_melody", "microbit_stop_sound",
    "microbit_radio_set_group", "microbit_radio_send", "microbit_read_sensor",
    "microbit_if_button", "microbit_if_gesture", "microbit_if_tilt",
    "microbit_if_pixel",
]


@pytest.fixture(autouse=True)
def _plugins():
    load_all_plugins()


# --- the generic seam ---------------------------------------------------------------------

def test_registering_adds_new_entries_and_never_overwrites_existing_ones():
    before_bounce = I18N.ACTION_TRANSLATIONS["bounce"]["fr"]["display_name"]
    before_color = I18N.PARAM_LABEL_TRANSLATIONS["fr"]["Color"]
    I18N.register_generated_block_translations({
        "actions": {
            "bounce": {"fr": {"display_name": "HIJACK", "description": "x"}},
            "zz_test_action": {"fr": {"display_name": "Essai", "description": "Un essai"}},
        },
        "params": {"fr": {"Color": "HIJACK", "ZZ Test Label": "Étiquette d'essai"},
                   "xx": {"ZZ Test Label": "xx label"}},
    })
    try:
        assert I18N.ACTION_TRANSLATIONS["bounce"]["fr"]["display_name"] == before_bounce
        assert I18N.PARAM_LABEL_TRANSLATIONS["fr"]["Color"] == before_color
        assert I18N.get_translated_action_display_name("zz_test_action", "fr", "Test") == "Essai"
        assert I18N.get_translated_param_label("ZZ Test Label", "fr") == "Étiquette d'essai"
        assert I18N.get_translated_param_label("ZZ Test Label", "xx") == "xx label"
        assert I18N.get_translated_action_display_name("zz_test_action", "de", "Test") == "Test"
    finally:
        I18N.ACTION_TRANSLATIONS.pop("zz_test_action", None)
        I18N.PARAM_LABEL_TRANSLATIONS["fr"].pop("ZZ Test Label", None)
        I18N.PARAM_LABEL_TRANSLATIONS.pop("xx", None)


def test_registering_nothing_is_harmless():
    I18N.register_generated_block_translations(None)
    I18N.register_generated_block_translations({})
    I18N.register_generated_block_translations({"actions": None, "params": None})


def test_core_names_nothing_micro_bit():
    for rel in ("config/blockly_generated_block_i18n.py", "config/blockly_config.py",
                "config/toolbox_visibility.py", "events/plugin_loader.py"):
        src = (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
        assert "microbit" not in src and "micro:bit" not in src, rel


# --- French ------------------------------------------------------------------------------------

def test_every_action_has_a_french_label_and_tooltip_that_differ_from_english():
    for name in ACTIONS:
        schema = ACTION_TYPES[name]
        label = I18N.get_translated_action_display_name(name, "fr", schema.display_name)
        tip = I18N.get_translated_action_description(name, "fr", schema.description)
        assert label and label != schema.display_name, name
        assert tip and tip != schema.description, name


def test_every_parameter_label_resolves_in_french():
    labels = {p.display_name for name in ACTIONS for p in ACTION_TYPES[name].parameters}
    assert labels
    for label in labels:
        assert label in I18N.PARAM_LABEL_TRANSLATIONS["fr"], label
    assert I18N.get_translated_param_label("Duration (ms)", "fr") == "Durée (ms)"


def test_other_languages_and_english_fall_back_to_the_schema_text():
    schema = ACTION_TYPES["microbit_play_tone"]
    for lang in ("en", "de", "ja", "xx"):
        assert I18N.get_translated_action_display_name(
            "microbit_play_tone", lang, schema.display_name) == schema.display_name
        assert I18N.get_translated_action_description(
            "microbit_play_tone", lang, schema.description) == schema.description
    assert I18N.get_translated_param_label("Melody", "de") == "Melody"


# Words that must carry an accent in French; the bare form is the stripped-
# diacritics bug CLAUDE.md warns about.
_STRIPPED = ["Evenement", "evenement", "Melodie", "melodie", "Luminosite", "luminosite",
             "Duree", "duree", "Delai", "delai", "Frequence", "frequence", "Regler",
             "Arreter", "Eteindre", "ecran", "Ecran", "defile", "defiler", "Defiler",
             "Recu", "recu", "Selection", "caractere", "accentuee", "Emettre",
             "Verifier", "a une", "a la ", "a 4"]


def test_french_text_carries_its_accents():
    from extensions.microbit.translations import PLUGIN_GENERATED_BLOCK_TRANSLATIONS as T
    texts = [t for languages in T["actions"].values() for t in languages["fr"].values()]
    texts += list(T["params"]["fr"].values())
    joined = "\n".join(texts)
    for bad in _STRIPPED:
        assert bad not in joined, bad
    # and the accented spellings really are there
    for good in ("Afficher une image", "Faire défiler", "Éteindre", "mélodie",
                 "Régler", "Arrêter", "événement", "Durée", "Fréquence", "Luminosité"):
        assert good in joined, good


def test_french_keeps_literal_identifiers_the_student_types():
    from extensions.microbit.translations import PLUGIN_GENERATED_BLOCK_TRANSLATIONS as T
    play = T["actions"]["microbit_play_melody"]["fr"]["description"]
    for token in ("DADADADUM", "C4:4 E G C5:8 R:4"):
        assert token in play
    send = T["actions"]["microbit_radio_send"]["fr"]["description"]
    assert "radio_number" in send and "radio_string" in send
    reading = T["actions"]["microbit_read_sensor"]["fr"]["description"]
    assert "global." in reading


# --- visibility in the toolbox / pickers -------------------------------------------------------------

def _project(active=None, using=None):
    data = {"name": "p", "settings": {}, "assets": {"objects": {}}}
    if active is not None:
        data["settings"]["active_extensions"] = active
    if using:
        data["assets"]["objects"]["microbit_1"] = {"events": {
            "create": {"actions": [{"action": using, "parameters": {}}]}}}
    return data


def test_actions_show_only_in_projects_that_activate_or_use_the_extension():
    from config.toolbox_visibility import visible_actions
    assert not set(ACTIONS) & visible_actions(None, _project())
    assert not set(ACTIONS) & visible_actions(None, None)
    assert set(ACTIONS) <= visible_actions(None, _project(active=["microbit"]))
    used = visible_actions(None, _project(using="microbit_show_image"))
    assert set(ACTIONS) <= used          # using one action unlocks the whole set


def test_a_globally_disabled_extension_stays_hidden_even_if_active(monkeypatch):
    import events.plugin_loader as pl
    from config.toolbox_visibility import visible_actions
    monkeypatch.setattr(pl, "is_extension_enabled", lambda folder, *a, **k: folder != "microbit")
    assert not set(ACTIONS) & visible_actions(None, _project(active=["microbit"]))


def test_active_extension_overrides_a_restrictive_preset():
    from config.blockly_config import PRESETS
    from config.toolbox_visibility import visible_actions
    beginner = PRESETS["beginner"]
    assert not set(ACTIONS) & visible_actions(beginner, _project())
    assert set(ACTIONS) <= visible_actions(beginner, _project(active=["microbit"]))


def test_events_appear_in_the_extension_event_menu_only_when_active():
    from config.toolbox_visibility import extension_event_menu
    micro_events = {n for n in EVENT_TYPES if n.startswith("microbit_")}
    assert len(micro_events) == 24
    assert not micro_events & {n for _, n in extension_event_menu(_project())}
    menu = extension_event_menu(_project(active=["microbit"]))
    assert micro_events <= {n for _, n in menu}
    labels = dict((n, label) for label, n in menu)
    assert labels["microbit_button_a"] == "Button A Pressed"


def test_manifest_declares_exactly_the_events_it_provides():
    import json
    manifest = json.loads((REPO_ROOT / "extensions" / "microbit"
                           / "extension.json").read_text(encoding="utf-8"))
    assert sorted(manifest["provides_events"]) == sorted(
        n for n in EVENT_TYPES if n.startswith("microbit_"))
    from events.plugin_loader import extension_for_event
    assert extension_for_event("microbit_radio_received")["folder"] == "microbit"
    assert extension_for_event("step") is None


def test_extension_event_names_are_known_to_the_loader():
    from config.toolbox_visibility import extension_event_names
    assert {n for n in EVENT_TYPES if n.startswith("microbit_")} <= set(extension_event_names())


# --- the generated blocks will be well formed ------------------------------------------------------------

_JS_PARAM_TYPES = {"choice", "number", "float", "boolean", "string"}


def test_every_action_is_in_the_one_micro_bit_category_with_a_label_and_icon():
    for name in ACTIONS:
        schema = ACTION_TYPES[name]
        assert schema.category == "micro:bit", name
        assert schema.display_name and schema.description and schema.icon, name


def test_every_parameter_is_a_type_the_block_generator_handles():
    for name in ACTIONS:
        for p in ACTION_TYPES[name].parameters:
            assert p.param_type in _JS_PARAM_TYPES, (name, p.name, p.param_type)
            if p.param_type == "choice":
                assert p.choices and p.default_value in p.choices, (name, p.name)


def test_defaults_are_safe_to_drop_into_the_toolbox_xml():
    # registerCustomBlocks writes <field name="..">DEFAULT</field> unescaped.
    for name in ACTIONS:
        for p in ACTION_TYPES[name].parameters:
            text = str(p.default_value)
            assert "<" not in text and "&" not in text, (name, p.name, text)


def test_parameter_names_are_unique_per_action_once_upper_cased():
    # block field names are the upper-cased parameter names
    for name in ACTIONS:
        fields = [p.name.upper() for p in ACTION_TYPES[name].parameters]
        assert len(fields) == len(set(fields)), name


def test_conditions_have_no_branches_so_they_guard_the_next_block():
    # Generated blocks are plain statement blocks (no DO slot): a condition
    # guards what follows it, GameMaker-style, like core's check_empty.
    for name in ("microbit_if_button", "microbit_if_gesture",
                 "microbit_if_tilt", "microbit_if_pixel"):
        names = {p.name for p in ACTION_TYPES[name].parameters}
        assert not names & {"then_actions", "else_actions", "sub_actions"}


def test_block_ids_for_the_category_dont_need_escaping():
    # toolbox categories are keyed by the schema's category string
    assert re.fullmatch(r"[A-Za-z:' -]+", ACTION_TYPES["microbit_show_image"].category)

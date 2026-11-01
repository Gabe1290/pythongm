"""Every language the micro:bit extension translates covers the same ground (follow-up M3).

One module per language beside ``translations.py``; add the language code to LANGUAGES below
when a new one lands and these checks apply to it unchanged.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import blockly_generated_block_i18n as I18N  # noqa: E402
from events.action_types import ACTION_TYPES  # noqa: E402
from events.event_types import EVENT_TYPES  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.microbit.translations import PLUGIN_GENERATED_BLOCK_TRANSLATIONS as T  # noqa: E402

LANGUAGES = ["fr", "de", "es", "it"]
# words that are the same in the language on purpose (cognates / units / names)
SAME = {"de": {"X (0-4)", "Y (0-4)", "Tempo (bpm)", "Text", "Variable", "Sensor"},
        "es": {"X (0-4)", "Y (0-4)", "Tempo (bpm)", "Sensor", "Variable"},
        "it": {"X (0-4)", "Y (0-4)", "Tempo (bpm)"},
        "fr": {"Image", "Message", "Variable", "X (0-4)", "Y (0-4)", "Tempo (bpm)"}}


@pytest.fixture(autouse=True)
def _plugins():
    load_all_plugins()
    I18N.register_generated_block_translations(T)


def _micro_actions():
    return {n: a for n, a in ACTION_TYPES.items() if n.startswith("microbit_")}


@pytest.mark.parametrize("lang", LANGUAGES)
def test_every_action_has_a_label_and_tooltip_in_the_language(lang):
    actions = _micro_actions()
    assert len(actions) == 16
    for name, schema in actions.items():
        label = I18N.get_translated_action_display_name(name, lang, schema.display_name)
        tip = I18N.get_translated_action_description(name, lang, schema.description)
        assert label != schema.display_name and tip != schema.description, (lang, name)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_every_parameter_label_resolves_in_the_language(lang):
    labels = {p.display_name for a in _micro_actions().values() for p in a.parameters}
    for label in labels:
        got = I18N.get_translated_param_label(label, lang)
        assert got != label or label in SAME[lang], (lang, label)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_every_event_has_a_label_in_the_language(lang):
    events = [n for n in EVENT_TYPES if n.startswith("microbit_")]
    assert len(events) == 24
    for name in events:
        assert I18N.get_translated_event_display_name(name, lang, EVENT_TYPES[name].display_name) \
            != EVENT_TYPES[name].display_name, (lang, name)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_identifiers_a_student_types_survive_translation(lang):
    """ALL_CAPS names (HEART, DADADADUM), snake_case variables and ``global.`` are typed
    into fields verbatim; a translation must keep every one the (reference) French tooltip
    names -- French abbreviates the long melody list with an ellipsis, as the others do."""
    token = re.compile(r"\b(?:[A-Z][A-Z_0-9]{3,}|[a-z]+_[a-z_]+|global\.)")
    for name, schema in _micro_actions().items():
        reference = I18N.get_translated_action_description(name, "fr", schema.description)
        want = set(token.findall(reference))
        assert want <= set(token.findall(schema.description)), name      # nothing invented
        got = I18N.get_translated_action_description(name, lang, schema.description)
        for t in want:
            assert t in got, (lang, name, t)


# characters each language's text must contain somewhere (proof the accents / script were not lost)
SCRIPT = {"fr": "éèêàçùî", "de": "äöüß", "es": "áéíóñ¿", "it": "àèéìòù", "pt": "çãõáéê",
          "ru": "абвгдежз", "uk": "абвгдежіїє", "sl": "čšž", "ja": "あいうえおアイウエオ", "zh": "的是不了"}


@pytest.mark.parametrize("lang", LANGUAGES)
def test_the_text_carries_the_languages_accents_or_script(lang):
    texts = [t for a in T["actions"].values() for t in a[lang].values()]
    texts += list(T["params"][lang].values()) + [e[lang] for e in T["events"].values()]
    joined = " ".join(texts)
    assert any(ch in joined for ch in SCRIPT[lang]), lang
    if lang in ("ru", "uk", "ja", "zh"):                      # a non-Latin language is mostly non-ASCII
        assert sum(ch.isascii() for ch in joined) < len(joined) * 0.6, lang


def test_german_uses_real_umlauts_not_transliteration():
    texts = [t for a in T["actions"].values() for t in a["de"].values()]
    texts += list(T["params"]["de"].values()) + [e["de"] for e in T["events"].values() if "de" in e]
    joined = " ".join(texts)
    assert all(ch in joined for ch in "äöüß")
    # ae/oe/ue inside a word is how umlauts get transliterated; the only real words here that
    # contain those letter pairs are listed (au+e in Dauer, Frequ+enz).
    legit = {"dauer", "anzeigedauer", "frequenz"}
    suspicious = {w for w in re.findall(r"\w*(?:ae|oe|ue)\w*", joined, re.I) if w.lower() not in legit}
    assert not suspicious, suspicious
    assert "Stoss" not in joined and "Gross" not in joined


def test_registering_a_second_language_leaves_french_alone():
    assert I18N.get_translated_action_display_name("microbit_show_image", "fr", "x") == "Afficher une image"
    assert I18N.get_translated_event_display_name("microbit_button_a", "fr", "x") == "Bouton A pressé"
    assert I18N.get_translated_action_display_name("microbit_show_image", "de", "x") == "Bild anzeigen"
    assert I18N.get_translated_action_display_name("microbit_show_image", "ko", "x") == "x"


def test_the_languages_cover_the_same_keys():
    assert set(T["actions"]) == {n for n in ACTION_TYPES if n.startswith("microbit_")}
    for action in T["actions"].values():
        assert set(action) == set(LANGUAGES)
    fr, de = set(T["params"]["fr"]), set(T["params"]["de"])
    assert fr == de
    for event in T["events"].values():
        assert set(event) == set(LANGUAGES)


def test_the_multiplayer_extensions_have_german_event_labels_too():
    import importlib
    for folder in ("multiplayer_lan", "multiplayer_files"):
        events = importlib.import_module(f"extensions.{folder}").PLUGIN_GENERATED_BLOCK_TRANSLATIONS["events"]
        assert events and all(set(LANGUAGES) <= set(v) for v in events.values()), folder

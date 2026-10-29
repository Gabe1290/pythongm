"""The micro:bit wiki page exists in all nine languages and stays in step.

Catches a language falling behind (a missing heading, table row or step), a
code identifier that was translated by accident, a broken internal link,
mojibake, accents stripped from a language that needs them, and a page nobody
links to (Home and Extensions must point at it).
"""
import re
from pathlib import Path

import pytest

WIKI = Path(__file__).resolve().parent.parent / "wiki"
LANGS = ["fr", "de", "es", "it", "pt", "ru", "sl", "uk"]
# Accented Latin letters / Cyrillic letters (em dashes and arrows do not count:
# a page that lost its accents would still have those).
LETTERS = re.compile("[À-ÖØ-öø-ſЀ-ӿ]")   # without × and ÷
MIN_ACCENTED_LETTERS = {"fr": 100, "de": 40, "es": 60, "it": 30, "pt": 80, "ru": 1000, "sl": 20, "uk": 1000}


def _page(lang=None):
    name = "Microbit.md" if lang is None else f"Microbit_{lang}.md"
    return (WIKI / name).read_text(encoding="utf-8")


def _shape(text):
    return {
        "headings": len(re.findall(r"^#{1,3} ", text, re.M)),
        "table_rows": len(re.findall(r"^\|", text, re.M)),
        "numbered": len(re.findall(r"^\d\. ", text, re.M)),
        "bullets": len(re.findall(r"^- ", text, re.M)),
        "rules": text.count("\n---\n"),
    }


def _identifiers(text):
    """Backticked tokens that are code, not prose: snake_case names, UPPERCASE
    names, and dotted/colon forms such as ``global.``."""
    found = set(re.findall(r"`([^`]+)`", text))
    return {c for c in found
            if re.fullmatch(r"[A-Za-z0-9_.:+/ -]+", c) and ("_" in c or c.isupper() or c.endswith("."))}


EN = _page()


@pytest.mark.parametrize("lang", LANGS)
def test_the_page_has_the_same_shape_as_the_english_one(lang):
    assert _shape(_page(lang)) == _shape(EN)


@pytest.mark.parametrize("lang", LANGS)
def test_every_code_identifier_is_kept_verbatim(lang):
    missing = sorted(_identifiers(EN) - _identifiers(_page(lang)))
    assert not missing, missing


@pytest.mark.parametrize("lang", LANGS)
def test_internal_links_resolve(lang):
    text = _page(lang)
    links = re.findall(r"\]\(([^)#\s]+)\)", text)
    assert links
    for target in links:
        assert (WIKI / f"{target}.md").exists(), target
        assert target.endswith(f"_{lang}") or lang == "en", f"{target} is not the {lang} page"


@pytest.mark.parametrize("lang", LANGS)
def test_no_mojibake_and_real_non_ascii_text(lang):
    text = _page(lang)
    assert "�" not in text
    # UTF-8 read as Latin-1: a lead byte (Ã Â for Latin, Ð Ñ for Cyrillic) + a continuation byte
    assert not re.search("[ÃÂÐÑ][\u0080-¿]", text)
    assert "\r" not in text, "wiki pages are stored with LF endings"
    assert len(LETTERS.findall(text)) >= MIN_ACCENTED_LETTERS[lang]


@pytest.mark.parametrize("lang", LANGS)
def test_the_sample_name_matches_the_ide_translation(lang):
    ts = {"fr": "pygm2_fr.ts"}.get(lang)
    translations = WIKI.parent / "translations"
    candidates = [translations / ts] if ts else sorted(translations.glob(f"pygm2_{lang}*.ts"))
    source = "micro:bit — Dice and Moods"
    name = None
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        m = re.search(re.escape(f"<source>{source}</source>") + r"\s*<translation>([^<]+)</translation>", text)
        if m:
            name = m.group(1).split("—", 1)[1].strip()
            break
    assert name, f"no IDE translation of the sample name for {lang}"
    assert name in _page(lang) or name.lower() in _page(lang).lower()


@pytest.mark.parametrize("lang", LANGS)
def test_home_and_extensions_link_to_the_page(lang):
    for page in ("Home", "Extensions"):
        text = (WIKI / f"{page}_{lang}.md").read_text(encoding="utf-8")
        assert f"(Microbit_{lang})" in text, f"{page}_{lang}.md does not link to Microbit_{lang}"


@pytest.mark.parametrize("lang", [None] + LANGS)
def test_extensions_says_it_works_in_all_three_exports(lang):
    name = "Extensions.md" if lang is None else f"Extensions_{lang}.md"
    text = (WIKI / name).read_text(encoding="utf-8")
    assert "HTML5" in text.split("micro:bit", 1)[1][:1500]


def test_the_english_and_french_pages_describe_the_kivy_simulator():
    assert "does not have a simulator yet" not in EN
    assert "n'a pas encore" not in _page("fr").split("Kivy", 1)[1][:200]


# -- the MicroPython export section ---------------------------------------------------------

ALL = [None] + LANGS

# (source string in the IDE, how a page may show it: the menu entry has its `&`
# mnemonic and trailing dots removed in running text)
_IDE_STRINGS = [
    "Export &micro:bit (MicroPython) code...",
    "V2 (2020 or later)",
    "V1 (original, 2016-2020)",
    "Both (one .hex for V1 and V2 boards)",
    "Copy to micro:bit?",
    "Build a ready-to-flash .hex?",
]


def _ide_translation(lang, source):
    """What the IDE shows for ``source`` in ``lang`` (English: the source)."""
    if lang is None:
        return source
    import html
    for path in sorted((WIKI.parent / "translations").glob(f"pygm2_{lang}*.ts")):
        text = path.read_text(encoding="utf-8")
        m = re.search(re.escape("<source>" + html.escape(source, quote=False) + "</source>")
                      + r"\s*(?:<[^>]*>\s*)*<translation[^>]*>([^<]*)</translation>", text)
        if m and m.group(1).strip():
            return html.unescape(m.group(1))
    raise AssertionError(f"no {lang} translation of {source!r}")


@pytest.mark.parametrize("lang", ALL)
def test_the_page_shows_the_ide_wording_for_the_export_dialogs(lang):
    text = " ".join(_page(lang).split())          # the page is hard-wrapped
    for source in _IDE_STRINGS:
        shown = _ide_translation(lang, source).replace("&", "")
        if shown.endswith("..."):
            shown = shown[:-3]
        assert shown in text, f"{lang}: {shown!r}"


@pytest.mark.parametrize("lang", ALL)
def test_the_size_limits_are_the_real_ones(lang):
    from extensions.microbit.export import hex_build
    v1, v2 = hex_build.v1_max_script_size(), hex_build.v2_max_script_size()
    assert (v1, v2) == (8187, 20150)
    text = _page(lang)
    assert re.search(r"8\D?187\b", text) and re.search(r"20\D?150\b", text)


@pytest.mark.parametrize("lang", ALL)
def test_the_section_names_what_a_v1_board_cannot_do(lang):
    """The three V2-only features the exporter reports (micropython_exporter.py)."""
    import inspect
    from extensions.microbit.export import micropython_exporter
    source = inspect.getsource(micropython_exporter)
    for name in ("microbit_logo_touched", "microbit_loud_sound/microbit_quiet_sound", "(sound level)"):
        assert name in source, name                 # the claim still matches the exporter
    text = _page(lang)
    for event in ("Logo Touched", "Loud Sound", "Quiet Sound", "Display Finished", "Sound Finished"):
        assert event in text, event
    assert "main.py" in text and ".hex" in text and "MICROBIT" in text

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

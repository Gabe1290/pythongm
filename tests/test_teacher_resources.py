"""Guards for the teacher resources (docs/handouts -> wiki), see
docs/TUTORIAL_HANDOUTS_PLAN.md.

Structure, EN/FR parity, French accents, page counts matching the tutorial
index, and that the generated wiki pages/links are current with the sources.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HANDOUTS = REPO / "docs" / "handouts"
WIKI = REPO / "wiki"
TUTORIALS = REPO / "Tutorials"
KINDS = ("student", "worksheet", "answer_key", "teacher")
LANGS = ("en", "fr")

DIRS = sorted(p for p in HANDOUTS.glob("[0-9][0-9]_*") if p.is_dir())

_spec = importlib.util.spec_from_file_location("build_teacher_wiki", REPO / "scripts" / "build_teacher_wiki.py")
btw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(btw)


def _read(p):
    return p.read_text(encoding="utf-8")


def test_there_is_at_least_one_handout_dir():
    assert DIRS


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
def test_dir_matches_a_real_tutorial_and_is_complete(d):
    assert (TUTORIALS / d.name).is_dir(), f"no Tutorials/{d.name}"
    for kind in KINDS:
        for lang in LANGS:
            assert (d / f"{kind}.{lang}.md").is_file(), f"{d.name}: missing {kind}.{lang}.md"


def _shape(md):
    return {
        "h2": sum(1 for ln in md.splitlines() if ln.startswith("## ")),
        "h3": sum(1 for ln in md.splitlines() if ln.startswith("### ")),
        "checkboxes": len(re.findall(r"^- \[ \] ", md, re.M)),
        "table_rows": sum(1 for ln in md.splitlines() if ln.startswith("|")),
        "images": len(re.findall(r"^!\[", md, re.M)),
        "notes": len(re.findall(r"^\[\[notes:", md, re.M)),
        "numbered": len(re.findall(r"^\d+\. ", md, re.M)),
    }


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("kind", KINDS)
def test_english_and_french_have_the_same_structure(d, kind):
    en, fr = _shape(_read(d / f"{kind}.en.md")), _shape(_read(d / f"{kind}.fr.md"))
    assert en == fr, f"{d.name}/{kind}: EN {en} != FR {fr}"


# Words that appear in French text only WITH an accent; the stripped form is the bug.
STRIPPED = ["eleve", "eleves", "ecran", "creer", "deja", "reponse", "reponses", "premiere",
            "evenement", "evenements", "debutant", "etape", "etapes", "selectionne",
            "necessaire", "resultat", "probleme", "problemes", "systeme", "meme", "apres",
            "generique", "activite", "modele", "modeles", "controle", "verifie", "verifier"]


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("kind", KINDS)
def test_french_keeps_its_accents(d, kind):
    text = re.sub(r"`[^`]*`", "", _read(d / f"{kind}.fr.md")).lower()
    text = re.sub(r"\]\([^)]*\)", "]", text)
    found = [w for w in STRIPPED if re.search(rf"(?<![\w/])({w})(?![\w])", text)]
    assert not found, f"{d.name}/{kind}.fr.md has accent-stripped words: {found}"


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("lang", LANGS)
def test_page_count_claim_matches_the_tutorial_index(d, lang):
    base = TUTORIALS / "fr" if lang == "fr" else TUTORIALS
    entry = next(t for t in json.loads(_read(base / "index.json"))["tutorials"] if t["folder"] == d.name)
    m = re.search(r"(\d+) pages?\b", _read(d / f"teacher.{lang}.md"))
    if m:
        assert int(m.group(1)) == len(entry["pages"])


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("lang", LANGS)
def test_wiki_page_is_current_with_its_source(d, kind, lang):
    page = WIKI / f"{btw.stem(kind, d.name, lang)}.md"
    assert page.is_file(), f"{page.name} missing; run scripts/build_teacher_wiki.py"
    expected = btw.convert(_read(d / f"{kind}.{lang}.md"), lang, f"images/handouts/{d.name}")
    _, rest = expected.split("\n", 1)
    assert _read(page).endswith("---\n" + rest), f"{page.name} is stale; run scripts/build_teacher_wiki.py"


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("lang", LANGS)
def test_wiki_page_links_resolve(d, kind, lang):
    text = _read(WIKI / f"{btw.stem(kind, d.name, lang)}.md")
    for rel in re.findall(r"\]\(((?:downloads|images)/[^)]+)\)", text):
        assert (WIKI / rel).is_file(), f"broken link {rel}"


@pytest.mark.parametrize("lang", LANGS)
def test_landing_page_lists_every_tutorial(lang):
    landing = _read(WIKI / (btw.HOME[lang][2] + ".md"))
    for d in DIRS:
        for kind in KINDS:
            assert btw.stem(kind, d.name, lang) in landing

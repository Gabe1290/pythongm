"""Guards for scripts/extract_worksheet_answer_keys.py -- the standalone,
printable "Answer Key" page sliced out of each teacher guide's own
"Worksheet Answer Key" section (single source of truth stays the teacher
guide; see docs/TUTORIAL_HANDOUTS_PLAN.md and tests/test_teacher_resources.py).
"""
import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HANDOUTS = REPO / "docs" / "handouts"
LANGS = ("en", "fr")
DIRS = sorted(p for p in HANDOUTS.glob("[0-9][0-9]_*") if p.is_dir())


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ewak = _load("extract_worksheet_answer_keys", "scripts/extract_worksheet_answer_keys.py")


def _read(p):
    return p.read_text(encoding="utf-8")


def test_extract_section_stops_before_the_next_heading():
    md = "# Title\n\n## Worksheet Answer Key\n\nline one\nline two\n\n## Rubric: X\n\nmore\n"
    section = ewak.extract_section(md, "en")
    assert section == "## Worksheet Answer Key\n\nline one\nline two\n"
    assert "Rubric" not in section


def test_extract_section_returns_none_without_the_heading():
    assert ewak.extract_section("# Title\n\n## Something Else\n\nbody\n", "en") is None


@pytest.mark.parametrize("title,lang,expected", [
    ("PyGameMaker — Tutorial 1: First Steps — Worksheet", "en",
     "PyGameMaker — Tutorial 1: First Steps — Answer Key"),
    ("PyGameMaker — Tutoriel 1 : Premiers pas — Feuille d'exercices", "fr",
     "PyGameMaker — Tutoriel 1 : Premiers pas — Corrigé"),
])
def test_answer_key_title_swaps_only_the_suffix(title, lang, expected):
    assert ewak.answer_key_title(title, lang) == expected


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
def test_every_tutorial_has_an_answer_key_in_both_languages(d):
    for lang in LANGS:
        assert (d / f"answer_key.{lang}.md").is_file(), f"{d.name}: missing answer_key.{lang}.md"


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("lang", LANGS)
def test_answer_key_is_current_with_its_teacher_guide(d, lang):
    expected = ewak.build_answer_key_md(d, lang)
    assert expected is not None
    assert _read(d / f"answer_key.{lang}.md") == expected, \
        f"{d.name}/answer_key.{lang}.md is stale; run scripts/extract_worksheet_answer_keys.py"


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("lang", LANGS)
def test_answer_key_is_marked_teachers_only_and_generated(d, lang):
    text = _read(d / f"answer_key.{lang}.md")
    assert re.search(r"^<!--.*GENERATED.*-->$", text, re.M), "missing the generated-file marker"
    notice = "For teachers only" if lang == "en" else "enseignant"
    assert notice in text


@pytest.mark.parametrize("d", DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize("lang", LANGS)
def test_answer_key_never_hand_edited_out_of_sync_with_worksheet_numbering(d, lang):
    # The Answer Key's own body (after the title/notice) must be an exact
    # copy of the teacher guide's section -- no drift between what a teacher
    # prints standalone and what the full teacher guide says.
    teacher_md = _read(d / f"teacher.{lang}.md")
    section = ewak.extract_section(teacher_md, lang)
    assert section is not None
    assert _read(d / f"answer_key.{lang}.md").endswith(section)


def test_build_answer_key_md_returns_none_for_a_dir_with_no_teacher_guide(tmp_path):
    assert ewak.build_answer_key_md(tmp_path, "en") is None


# --- regression: a full-line HTML comment (used for the "generated" marker)
# must render invisibly everywhere the same .md source feeds -- GitHub's own
# wiki markdown already hides it; the printable PDF/ODT renderers did not. ---

_SAMPLE_MD = (
    "# Title\n\n"
    "<!-- GENERATED marker, must never be printed -->\n\n"
    "> INFO: visible notice\n\n"
    "## Worksheet Answer Key\n\n"
    "**Part A:** 1-B.\n"
)


def test_odt_renderer_drops_html_comment_lines():
    odt_gen = _load("generate_tutorial_handouts_odt", "scripts/generate_tutorial_handouts_odt.py")
    html = odt_gen.md_to_html(_SAMPLE_MD)
    assert "GENERATED marker" not in html
    assert "visible notice" in html and "Part A" in html


def test_pdf_renderer_drops_html_comment_lines(tmp_path):
    pytest.importorskip("fpdf")
    pdf_gen = _load("generate_tutorial_handouts_pdf", "scripts/generate_tutorial_handouts_pdf.py")
    src = tmp_path / "sample.md"
    src.write_text(_SAMPLE_MD, encoding="utf-8")
    out = tmp_path / "sample.pdf"
    pdf_gen.render(str(src), str(out))
    fitz = pytest.importorskip("pymupdf")
    doc = fitz.open(str(out))
    text = "".join(page.get_text() for page in doc)
    assert "GENERATED marker" not in text
    assert "visible notice" in text and "Part A" in text

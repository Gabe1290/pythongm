"""The English and French Junior teacher guides stay in step (queue item A5).

The French guide gets the new parts first (docs/junior/teacher.fr.md); the English one is its
translation. These checks catch the English copy falling behind again, as it did between
2026-10-16 and 2026-10-29: a lesson plan that still described a 5-part handout, a missing bonus
paragraph, a missing troubleshooting row -- and the printable .pdf/.odt and the wiki copies left
behind the .md.
"""
import hashlib
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JUNIOR = ROOT / "docs" / "junior"
WIKI = ROOT / "wiki"
EN = (JUNIOR / "teacher.en.md").read_text(encoding="utf-8")
FR = (JUNIOR / "teacher.fr.md").read_text(encoding="utf-8")
STUDENT_EN = (JUNIOR / "student.en.md").read_text(encoding="utf-8")


def _count(pattern, text):
    return len(re.findall(pattern, text, re.M))


def test_same_sections_tables_and_steps():
    assert _count(r"^## ", EN) == _count(r"^## ", FR) == 7
    assert _count(r"^\|", EN) == _count(r"^\|", FR)
    assert _count(r"^\d\. ", EN) == _count(r"^\d\. ", FR)


def test_the_only_extra_french_bullet_is_the_sidebar_note_that_has_no_english_meaning():
    """FR explains that the asset-tree categories stay English in a French IDE; an English IDE
    shows the same words anyway, so the English guide has nothing to say."""
    assert _count(r"^- ", FR) == _count(r"^- ", EN) + 1
    assert "Catégories de la barre latérale" in FR


def test_the_lesson_plan_has_the_same_time_slots_in_both():
    slots = lambda t: re.findall(r"^\| (\d+-\d+) \|", t, re.M)       # noqa: E731
    assert slots(EN) == slots(FR) == ["0-10", "10-25", "25-45", "45-55", "55-60"]


def test_the_lesson_plan_matches_the_english_student_handout():
    """The plan names Parts of the student handout; they must be the handout's real parts."""
    parts = re.findall(r"^## Part (\d+): (.+)$", STUDENT_EN, re.M)
    assert [n for n, _ in parts] == ["1", "2", "3", "4", "5", "6", "7"]
    titles = dict(parts)
    assert "Start a Project" in titles["1"] and "Draw a Sprite" in titles["3"]
    assert "Share" in titles["6"] and "BONUS" in titles["7"]
    plan = EN.split("## Suggested Lesson Plan")[1].split("## Common Problems")[0]
    assert "Parts 1 to 3: start a project, then draw a sprite" in plan
    assert "Parts 4 and 5" in plan and "Part 6: export as HTML5" in plan
    assert "do Parts 1 to 5" in plan
    assert "Part 7 (bonus, optional)" in plan


def test_the_bonus_troubleshooting_row_names_the_objects_the_handout_uses():
    assert "obj_hero" in STUDENT_EN and "obj_fruit" in STUDENT_EN
    assert "Score does not go up (Part 7)" in EN
    assert "**obj_hero**" in EN and "obj_fruit" in EN


def test_no_french_left_in_the_english_guide():
    assert not re.search(r"[àâçéèêëîïôûùüœ]", EN), "accented letters in the English guide"
    for word in ("Partie", "élève", "Fiche", "Ressources", "Salle"):
        assert word not in EN, word


def test_the_printable_odt_carries_the_current_text():
    content = zipfile.ZipFile(JUNIOR / "teacher.en.odt").read("content.xml").decode("utf-8")
    for phrase in ("Parts 1 to 3: start a project", "Part 7 (bonus, optional)", "Score does not go up (Part 7)"):
        assert phrase in content, f"teacher.en.odt is stale: {phrase!r}"


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_the_wiki_downloads_are_the_current_files():
    for ext in ("pdf", "odt"):
        assert _digest(WIKI / "downloads" / f"Junior-Teacher-Guide.{ext}") == _digest(JUNIOR / f"teacher.en.{ext}"), ext
        assert _digest(WIKI / "downloads" / f"Junior-Teacher-Guide_fr.{ext}") == _digest(JUNIOR / f"teacher.fr.{ext}"), ext


def test_the_wiki_page_has_the_current_text():
    page = (WIKI / "Junior-Teacher-Guide.md").read_text(encoding="utf-8")
    assert "Part 7 (bonus, optional)" in page and "Score does not go up (Part 7)" in page

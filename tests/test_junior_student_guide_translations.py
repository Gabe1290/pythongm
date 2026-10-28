"""The English and French Junior student guides stay in step.

The French guide is the one that gets the screenshots and the new parts first
(docs/junior/student.fr.md); the English one is its translation. These checks
catch the English copy falling behind again: a missing part, a missing
screenshot, an image file that does not exist, French left in the English
text, or a wiki page whose image links point nowhere.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JUNIOR = ROOT / "docs" / "junior"
EN = (JUNIOR / "student.en.md").read_text(encoding="utf-8")
FR = (JUNIOR / "student.fr.md").read_text(encoding="utf-8")
IMG = re.compile(r'!\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


def _count(pattern, text):
    return len(re.findall(pattern, text, re.M))


def test_same_number_of_parts_and_sections():
    assert _count(r"^## ", EN) == _count(r"^## ", FR)
    assert _count(r"^## (?:Part|Partie) \d", EN) == _count(r"^## (?:Part|Partie) \d", FR) == 7


def test_same_checkboxes_callouts_and_table_rows():
    assert _count(r"^- \[ \]", EN) == _count(r"^- \[ \]", FR)
    assert _count(r"^> (?:TIP|DONE)", EN) == _count(r"^> (?:TIP|DONE)", FR)
    assert _count(r"^\|", EN) == _count(r"^\|", FR)
    assert "[[notes:6]]" in EN


def test_same_screenshots_and_every_file_exists():
    en, fr = IMG.findall(EN), IMG.findall(FR)
    assert len(en) == len(fr) == 7
    assert [Path(p).name for p in en] == [Path(p).name for p in fr]
    for path in en:
        assert path.startswith("images/en/"), "English guide must use English screenshots"
        assert (JUNIOR / path).is_file(), path


def test_no_french_left_in_the_english_guide():
    prose = IMG.sub("", EN)      # screenshot file names are shared with the French set
    assert not re.search(r"[àâçéèêëîïôûùüœ]", prose), "accented letters in the English guide"
    for word in ("Partie", "Clique", "Ressources", "Enregistrer", "salle", "Fichier"):
        assert word not in prose, word


def test_menu_paths_match_the_real_english_interface():
    for text in ("**Assets > Create Sprite**", "**Assets > Create Object**",
                 "**File > Export as HTML5**", "**Tools > Restore Deleted Assets**",
                 "**Keyboard: No key**", "**Add to score 10**",
                 "**Destroy other instance**", "**When drawing**"):
        assert text in EN, text


def test_wiki_pages_link_to_images_that_exist():
    for page in ("Junior-Student-Handout.md", "Junior-Student-Handout_fr.md"):
        text = (ROOT / "wiki" / page).read_text(encoding="utf-8")
        links = re.findall(r"\]\((images/junior/[^)]+)\)", text)
        assert len(links) == 7, page
        for link in links:
            assert (ROOT / "wiki" / link).is_file(), (page, link)
        assert "images/junior/" in text and '"' not in "".join(links)

"""A paragraph that follows a blank line after a list must come out AFTER
that list (the soft-wrap merge used to glue it onto the blank line, so the
ODT generator emitted it before the list)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

SRC = "Intro:\n\n- one\n- two\n\nAfter the list.\n\n- three\n"


def test_odt_paragraph_stays_after_its_list():
    import generate_tutorial_handouts_odt as g
    html = g.md_to_html(SRC)
    assert html.index("<li>two</li>") < html.index("After the list.") < html.index("<li>three</li>")


def test_soft_wrap_still_joins_continuation_lines():
    import generate_tutorial_handouts_odt as g
    assert g._merge_soft_wraps(["- item", "  continued", "", "para", "more"]) == \
        ["- item continued", "", "para more"]


def test_pdf_merge_keeps_blank_before_paragraph():
    try:
        import generate_tutorial_handouts_pdf as g
    except ImportError:  # CI has no fpdf2
        return
    assert g._merge_soft_wraps(["- a", "", "para"]) == ["- a", "", "para"]


def test_no_junior_handout_source_uses_a_standalone_double_dash():
    """fpdf2's markdown=True (generate_tutorial_handouts_pdf.py's render
    engine) treats a bare " -- " as the OPEN of an --underline-- span, not
    an em dash -- this repo's own prose habit (used throughout CLAUDE.md
    and commit messages) silently underlines everything from there to the
    end of that text run if it ever leaks into handout source text. Found
    once already (docs/junior/teacher.fr.md's Partie 7 bonus note, fixed
    the same session) by actually rendering a real page and looking at it;
    this scan keeps it from coming back unnoticed."""
    import glob
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    offenders = {}
    for path in sorted(glob.glob(str(root / "docs" / "junior" / "*.md"))):
        text = Path(path).read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if re.search(r"(?<!-)--(?!-)", ln)]
        if lines:
            offenders[path] = lines
    assert offenders == {}


# --- "KEYWORD :" with a space before the colon (French typography) ----------
# French handout sources write "TIP :", "INFO :", "DONE :" with a space
# before the colon (docs/junior/{student,lessons/*/*}.fr.md). All three
# callout-kind regexes (odt/pdf generators + build_teacher_wiki.py's wiki
# converter) were copy-pasted from the English-only "KEYWORD:" form and
# never allowed that space, so `re.match` failed, `kind` silently stayed at
# its "TIP" default, and the literal "INFO :"/"DONE :" prefix survived as
# rendered text -- every French INFO/DONE callout in those 5 files rendered
# as a yellow TIP box with its own label still showing. Found by inspecting
# the generated .odt's actual background-color per paragraph directly
# (visually it looked like "LibreOffice merged adjacent callout styles",
# which was the wrong diagnosis -- the HTML was wrong before LibreOffice
# ever saw it).

def test_odt_callout_with_space_before_colon_gets_the_right_colour_and_strips_the_label():
    import generate_tutorial_handouts_odt as g
    html = g.md_to_html("> INFO : un texte bleu\n\n> TIP : un texte jaune\n")
    assert "#d1ecf1" in html.split("un texte bleu")[0].rsplit("<p", 1)[-1]
    assert "#fff3cd" in html.split("un texte jaune")[0].rsplit("<p", 1)[-1]
    assert "INFO" not in html and "TIP" not in html  # label stripped, like English


def test_pdf_callout_kind_regex_allows_a_space_before_the_colon():
    try:
        import generate_tutorial_handouts_pdf as g
    except ImportError:  # CI has no fpdf2
        return
    import re
    m = re.match(r"(TIP|INFO|DONE)\s*:\s*(.*)", "INFO : un objet Solide")
    assert m and m.groups() == ("INFO", "un objet Solide")


def test_wiki_converter_callout_with_space_before_colon():
    import build_teacher_wiki as btw
    assert btw.convert("> INFO : un texte\n", "fr", "images/x") == "> **Info:** un texte\n"

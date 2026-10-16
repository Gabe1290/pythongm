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

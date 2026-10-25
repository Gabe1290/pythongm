"""Every handout .odt this repo generates (docs/junior/, docs/handouts/)
came out with its document language set to whatever this machine's
LibreOffice install defaults to (typically en/US), regardless of the
handout's real language -- so a teacher opening a French handout got the
English spell-checker flagging every French word. A plain
<html lang="fr"> attribute on the generated HTML is silently ignored by
LibreOffice's HTML-import filter (confirmed empirically: converting a
minimal lang="fr" HTML file still produced fo:language="en" in the output
.odt, every time). Fixed by post-processing the produced .odt package
directly: rewrite the Western-text fo:language/fo:country pair in
styles.xml to match the language the source filename's "<name>.<lang>.md"
suffix carries.
"""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_doc_language_reads_the_filename_suffix():
    import generate_tutorial_handouts_odt as g

    assert g._doc_language("docs/junior/student.fr.md") == "fr"
    assert g._doc_language("docs/handouts/05_sokoban/teacher.en.md") == "en"
    assert g._doc_language("/abs/path/worksheet.de.md") == "de"


def test_doc_language_is_none_without_a_language_suffix():
    import generate_tutorial_handouts_odt as g

    assert g._doc_language("docs/junior/student.md") is None
    assert g._doc_language("README.md") is None


def _fake_odt(path, styles_xml, extra_files=None):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/vnd.oasis.opendocument.text",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("styles.xml", styles_xml)
        z.writestr("content.xml", "<office:document-content/>")
        for name, data in (extra_files or {}).items():
            z.writestr(name, data)


def test_set_document_language_rewrites_western_text_language(tmp_path):
    import generate_tutorial_handouts_odt as g

    odt_path = tmp_path / "doc.odt"
    styles = (
        '<office:document-styles>'
        '<style:default-style style:family="paragraph">'
        '<style:text-properties fo:language="en" fo:country="US" '
        'style:language-asian="zh" style:country-asian="CN"/>'
        '</style:default-style>'
        '<style:default-style style:family="text">'
        '<style:text-properties fo:language="en" fo:country="US"/>'
        '</style:default-style>'
        '</office:document-styles>'
    )
    _fake_odt(odt_path, styles)

    g._set_document_language(str(odt_path), "fr")

    with zipfile.ZipFile(odt_path) as z:
        names = z.namelist()
        new_styles = z.read("styles.xml").decode("utf-8")
        content = z.read("content.xml").decode("utf-8")
        mimetype_info = z.getinfo("mimetype")

    assert new_styles.count('fo:language="fr" fo:country="FR"') == 2
    assert 'fo:language="en"' not in new_styles
    # style:language-asian/-complex (CJK/RTL font fallback, not spelling)
    # must be left alone.
    assert 'style:language-asian="zh"' in new_styles
    # Untouched entries survive the rewrite unchanged.
    assert content == "<office:document-content/>"
    # mimetype must stay first and stored (uncompressed) for a valid ODF
    # package.
    assert names[0] == "mimetype"
    assert mimetype_info.compress_type == zipfile.ZIP_STORED


def test_set_document_language_uses_the_lang_country_table():
    import generate_tutorial_handouts_odt as g

    assert g._LANG_COUNTRY["fr"] == "FR"
    assert g._LANG_COUNTRY["en"] == "US"
    # An unlisted language falls back to upper-casing the code itself --
    # wrong for a few real countries, but only the language half actually
    # selects which spell-check dictionary runs.
    assert g._doc_language("x.xx.md") == "xx"


def test_set_document_language_is_a_noop_without_a_language_match(tmp_path):
    """No fo:language attribute in styles.xml (an unexpected LibreOffice
    output) must not raise -- silently leaves the .odt as LibreOffice
    produced it rather than failing the whole render."""
    import generate_tutorial_handouts_odt as g

    odt_path = tmp_path / "doc.odt"
    _fake_odt(odt_path, "<office:document-styles/>")
    before = odt_path.read_bytes()

    g._set_document_language(str(odt_path), "fr")

    assert odt_path.read_bytes() == before

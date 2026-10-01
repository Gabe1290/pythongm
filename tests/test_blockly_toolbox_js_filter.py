"""Structural guard for the Unit-3 JS fix (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md):
`generateToolboxXml`'s "append dynamically registered custom categories"
loop used to add every block with NO preset check at all -- the actual bug
the whole plan fixes. No JS engine in CI, so this is regex/structure only,
the same tier `tests/test_export_html5_extension_syntax.py` already
established for this repo's hand-written JS. The *behavioural* proof (the
resolved payload actually hides/shows the right blocks) is
tests/test_blockly_preset_generated_actions.py and the apply_configuration
tests in tests/test_thymio_extension.py (Stage G5b.1) -- this file only
guards that the JS itself stays syntactically sound and keeps the fix.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

JS_PATH = REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"


def _source():
    return JS_PATH.read_text(encoding="utf-8")


def _generate_toolbox_xml_body():
    src = _source()
    start = src.index("function generateToolboxXml(config) {")
    end = src.index("function extractBlockType(blockXml) {")
    return src[start:end]


def test_file_exists():
    assert JS_PATH.exists()


def test_script_braces_and_parens_balance():
    """Same brace-balance tier test_export_html5_extension_syntax.py uses,
    applied to the <script> block containing generateToolboxXml (the whole
    HTML file also has markup braces/parens in attributes that don't nest
    the same way, so scope to the script content)."""
    src = _source()
    script_start = src.index("function generateToolboxXml")
    script_end = src.index("return Blockly.utils.xml.textToDom(xml);\n        }") + len(
        "return Blockly.utils.xml.textToDom(xml);\n        }")
    blob = src[script_start:script_end]
    stripped = re.sub(r"//[^\n]*", "", blob)
    stripped = re.sub(r"'(\\.|[^'\\])*'", "''", stripped)
    stripped = re.sub(r'"(\\.|[^"\\])*"', '""', stripped)
    stripped = re.sub(r"`(\\.|[^`\\])*`", "``", stripped)
    for open_c, close_c in (("{", "}"), ("(", ")")):
        assert stripped.count(open_c) == stripped.count(close_c), (
            f"unbalanced {open_c}{close_c} ({stripped.count(open_c)} vs "
            f"{stripped.count(close_c)}) in generateToolboxXml")


def test_unmerged_custom_categories_are_now_filtered():
    body = _generate_toolbox_xml_body()
    # The old bug: the unmerged loop pushed every block from
    # `custom.blocks` straight through with no enabledBlocks check at all.
    assert "custom.blocks.join('')" not in body, (
        "unmerged custom categories are appended unfiltered again -- this "
        "is the exact bug docs/BLOCKLY_TOOLBOX_GATING_PLAN.md fixes")

    # The fix: a per-block filter mirroring the merged path's own check
    # (enabledBlocks.has(blockType) || enabledBlocks.has(baseName)).
    unmerged_loop = body[body.index("mergedCustomCats[customName]) continue;"):]
    assert "filteredBlocks" in unmerged_loop
    assert re.search(
        r"enabledBlocks\.has\(blockType\)\s*\|\|\s*enabledBlocks\.has\(baseName\)",
        unmerged_loop), "unmerged loop doesn't filter per block like the merged path does"
    assert "filteredBlocks.join('')" in unmerged_loop


def test_merged_path_filter_is_unchanged():
    """Didn't touch the already-correct merged-category filter while fixing
    the unmerged one."""
    body = _generate_toolbox_xml_body()
    merged_section = body[:body.index("mergedCustomCats[categoryName] = true;")]
    assert re.search(
        r"enabledBlocks\.has\(customBlockType\)\s*\|\|\s*enabledBlocks\.has\(baseName\)",
        merged_section)

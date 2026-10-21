"""Student-defined custom blocks ("My Blocks") -- docs/
BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 2.

Design: a custom block (Blockly's native procedures_defnoreturn/
procedures_callnoreturn -- the vendored library already ships the whole
feature, confirmed present in lib/blocks_compressed.js/
blockly_compressed.js) is pure authoring sugar, expanded into its
definition's own action list AT GENERATION TIME
(editors/object_editor/blockly/blockly_generators.js). The saved project
data only ever contains ordinary actions -- no new action type, no
runtime/HTML5/Kivy engine changes.

v1 scope (deliberately narrower than Scratch's own procedures, see the
plan doc): a call is only expanded when it's a TOP-LEVEL action directly
inside an event or another custom block's own body -- nesting a call
inside an if_condition/test_variable then/else branch, or inside another
custom block (recursion), is explicitly NOT supported and surfaces as a
visible sentinel action rather than silently vanishing or infinite-
looping. Reporter-style (value-returning) custom blocks are deferred
too.

No Node.js in CI (this repo's established convention for this editor's
JS), so this is a structural/source check, not an execution test --
cross-referenced against the exact vendored Blockly API this was written
against (confirmed by grepping lib/blocks_compressed.js directly, not
assumed from memory): block.getFieldValue('NAME'), block.getVars() ->
this.arguments_, block.getInputTargetBlock('STACK'), ARG0/ARG1/... value
inputs on the call block, and variables_get's field_variable 'VAR'
resolved via workspace.getVariableById(id).getName().

**Genuinely unverified, flagged rather than silently claimed solid**:
whether dragging a parameter reporter into a socket inside a real
Blockly mutator dialog actually produces the variables_get block this
code assumes, in THIS exact vendored Blockly build, end to end in a real
browser. This needs a human (or a real browser session) to drag blocks
and confirm -- see the plan doc's own follow-up note.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATORS_JS = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                  "blockly_generators.js")
WORKSPACE_HTML = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                   "blockly_workspace.html")
I18N_JS = (REPO_ROOT / "editors" / "object_editor" / "blockly" / "blockly_i18n.js")
BLOCKS_COMPRESSED = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                      "lib" / "blocks_compressed.js")


def _gen_source():
    return GENERATORS_JS.read_text(encoding="utf-8")


def _ws_source():
    return WORKSPACE_HTML.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The vendored Blockly API this feature is built against -- pinned so a
# future Blockly upgrade that changes these names is caught immediately
# instead of silently breaking a feature with no Node.js test to catch it.
# ---------------------------------------------------------------------------

def test_vendored_blockly_still_ships_procedures_blocks():
    src = BLOCKS_COMPRESSED.read_text(encoding="utf-8")
    for block_type in ("procedures_defnoreturn", "procedures_callnoreturn"):
        assert f'"{block_type}"' in src


def test_vendored_blockly_still_uses_the_assumed_api_shape():
    src = BLOCKS_COMPRESSED.read_text(encoding="utf-8")
    assert '"STACK"' in src
    assert 'getFieldValue("NAME")' in src
    assert 'getVars:function(){returnthis.arguments_}' in src.replace(" ", "")
    assert '"ARG"+' in src.replace(" ", "")


def test_vendored_blockly_ships_translated_procedures_strings():
    """Confirmed in an earlier session: lib/msg/fr.js already has 32
    PROCEDURES_* strings -- zero fresh translation work needed for the
    definition/call block UI itself, across all 11 shipped languages."""
    for lang in ("fr", "de", "it", "pl", "uk", "es", "pt", "ru", "sl", "ja", "zh-hans"):
        msg_file = REPO_ROOT / "editors" / "object_editor" / "blockly" / "lib" / "msg" / f"{lang}.js"
        assert msg_file.exists(), lang
        assert "PROCEDURES_" in msg_file.read_text(encoding="utf-8"), lang


# ---------------------------------------------------------------------------
# Toolbox registration
# ---------------------------------------------------------------------------

def test_my_blocks_category_uses_custom_procedure():
    body = _ws_source()
    assert 'custom="PROCEDURE"' in body
    assert "TOOLBOX_GROUP_COLORS['My Blocks']" in body


def test_my_blocks_category_excluded_for_junior():
    src = _ws_source()
    start = src.index("function generateToolboxXml(config) {")
    end = src.index("function extractBlockType(blockXml) {")
    body = src[start:end]
    section = body[body.index('"My Blocks" -- docs/'):]
    assert "isJunior" in section
    assert "junior" in section.lower()
    assert re.search(r"if \(!isJunior\)\s*\{", section)


def test_my_blocks_not_gated_by_enabled_categories():
    """Unlike every BLOCK_REGISTRY-driven group, 'My Blocks' doesn't check
    enabledCategories/showAll at all -- it's always shown (barring
    junior), matching Scratch's own "the My Blocks drawer with its Make a
    Block button is always there" behaviour."""
    src = _ws_source()
    start = src.index("function generateToolboxXml(config) {")
    end = src.index("function extractBlockType(blockXml) {")
    body = src[start:end]
    section = body[body.index('"My Blocks" -- docs/'):]
    assert "enabledCategories" not in section


def test_workspace_registers_the_procedure_flyout_callback():
    body = _ws_source()
    assert "registerToolboxCategoryCallback(" in body
    assert "Blockly.Procedures.flyoutCategory" in body


def test_toolbox_group_colors_and_i18n_cover_my_blocks():
    assert "'My Blocks': '#FF6680'" in _ws_source()
    i18n = I18N_JS.read_text(encoding="utf-8")
    for lang in ("fr", "pl", "de", "it", "uk"):
        start = i18n.index("const CATEGORY_MESSAGES")
        end = i18n.index("\n};", start)
        block = i18n[start:end]
        lang_start = block.index(f"'{lang}': {{")
        lang_end = block.index("}", lang_start)
        assert "'My Blocks':" in block[lang_start:lang_end], lang


# ---------------------------------------------------------------------------
# Codegen: indexing, expansion, substitution
# ---------------------------------------------------------------------------

def test_definitions_are_indexed_by_name_from_top_blocks():
    src = _gen_source()
    start = src.index("function indexCustomBlockDefs(workspace) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "block.type === 'procedures_defnoreturn'" in body
    assert "block.getFieldValue('NAME')" in body
    assert "block.getVars()" in body
    assert "block.getInputTargetBlock('STACK')" in body


def test_definitions_never_produce_their_own_event():
    """procedures_defnoreturn has no case in getEventType's switch, so the
    default (return null) already skips it at the true top level -- no
    special-case needed there, confirmed present as a negative check."""
    src = _gen_source()
    start = src.index("function getEventType(block) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "procedures_defnoreturn" not in body


def test_generate_block_code_uses_the_expand_aware_walker():
    src = _gen_source()
    start = src.index("function generateBlockCode(eventBlock, customBlockDefs) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "walkTopLevelActionChain(" in body


def test_pygamemaker_code_builds_the_index_once_up_front():
    src = _gen_source()
    start = src.index("function generatePyGameMakerCode(workspace) {")
    end = src.index("\nfunction getEventType", start)
    body = src[start:end]
    assert "indexCustomBlockDefs(workspace)" in body
    assert "generateBlockCode(block, customBlockDefs)" in body


def test_walk_top_level_action_chain_expands_calls_inline():
    src = _gen_source()
    start = src.index("function walkTopLevelActionChain(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "block.type === 'procedures_callnoreturn'" in body
    assert "expandCustomBlockCall(" in body
    # Every other block still goes through the ordinary single-action path.
    assert "generateActionCode(block)" in body


def test_expand_custom_block_call_substitutes_positional_args():
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "getInputValue(callBlock, 'ARG' + i, '')" in body
    assert "substituteCustomBlockArgs(" in body


def test_expand_custom_block_call_refuses_to_nest():
    """The v1 scope decision that avoids needing cycle detection
    entirely: a call found while already inside another definition's
    body is never expanded, regardless of whether its own target exists."""
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "insideDefinition" in body
    assert "__pygm_custom_block_nesting_unsupported__" in body
    assert "__pygm_undefined_custom_block__" in body


def test_undefined_call_target_is_surfaced_not_dropped():
    src = _gen_source()
    assert "__pygm_undefined_custom_block__" in src


def test_substitute_args_is_a_deep_substring_replace():
    src = _gen_source()
    start = src.index("function substituteCustomBlockArgs(value, argValues) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "typeof value === 'string'" in body
    assert "Array.isArray(value)" in body
    assert "{{PYGM_ARG:' + name + '}}" in body
    # Substring (not exact-match) replace -- a parameter can be embedded
    # inside a larger expression string (e.g. inside a math_arithmetic
    # result), not just stand alone.
    assert "result.split(placeholder).join(" in body


def test_get_input_value_resolves_variables_get_through_the_workspace():
    src = _gen_source()
    start = src.index("function getInputValue(block, inputName, defaultValue) {")
    end = src.index("return defaultValue;\n}", start) + len("return defaultValue;\n}")
    body = src[start:end]
    assert "input.type === 'variables_get'" in body
    assert "input.getFieldValue('VAR')" in body
    assert "input.workspace.getVariableById(varId)" in body
    assert "varModel.getName()" in body
    assert "{{PYGM_ARG:' + varName + '}}" in body


def test_procedures_blocks_have_a_fallback_case_for_unsupported_positions():
    """generateActionCodeInner's own switch (reached only when these
    appear somewhere walkTopLevelActionChain doesn't cover, e.g. an
    if_condition branch) must not silently return null for either block
    type -- a dropped custom-block call would be invisible to the author."""
    src = _gen_source()
    start = src.index("function generateActionCodeInner(block) {")
    end = src.index("\n}", src.index("default:\n            return null;", start))
    body = src[start:end]
    assert "case 'procedures_callnoreturn':" in body
    assert "__pygm_custom_block_nesting_unsupported__" in body
    assert "case 'procedures_defnoreturn':" in body
    assert "__pygm_custom_block_definition_misplaced__" in body


def test_sentinel_action_names_are_not_real_registered_actions():
    """The sentinel names must never collide with a real ActionType, or
    they'd silently execute as something else instead of rendering as
    the intended visible 'unrecognized action' indicator."""
    from events.action_types import ACTION_TYPES
    sentinels = [
        "__pygm_undefined_custom_block__",
        "__pygm_custom_block_nesting_unsupported__",
        "__pygm_custom_block_definition_misplaced__",
    ]
    for name in sentinels:
        assert name not in ACTION_TYPES


@pytest.mark.parametrize("js_file", [GENERATORS_JS, WORKSPACE_HTML])
def test_braces_and_parens_balance(js_file):
    src = js_file.read_text(encoding="utf-8")
    assert src.count("{") == src.count("}")
    assert src.count("(") == src.count(")")

"""Student-defined custom blocks ("My Blocks") -- docs/
BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 2.

Design: a custom block (Blockly's native procedures_defnoreturn/
procedures_callnoreturn/procedures_defreturn/procedures_callreturn --
the vendored library already ships the whole feature, confirmed present
in lib/blocks_compressed.js/blockly_compressed.js) is pure authoring
sugar, expanded into its definition's own action list (no-return) or
return expression (reporter) AT GENERATION TIME
(editors/object_editor/blockly/blockly_generators.js). The saved project
data only ever contains ordinary actions/expression strings -- no new
action type, no runtime/HTML5/Kivy engine changes.

Nesting is fully supported (2026-10-22 follow-up, see the plan doc's
"Follow-up: nesting + reporters" section): a call inside an
if_condition/test_variable/thymio_if_* branch, or inside another custom
block's own body, expands exactly like a top-level one --
walkActionChain (renamed from walkTopLevelActionChain, since it's no
longer just for the top level) is the only place a chain of sibling
statement blocks is ever walked, and a `callStack` of in-progress
custom-block names catches any cycle (direct self-recursion or a longer
A -> B -> A chain) instead of recursing forever at generation time, with
a depth cap (MAX_CUSTOM_BLOCK_EXPANSION_DEPTH) as a separate guard
against pathologically deep but acyclic nesting.

Reporter-style (value-returning) custom blocks -- procedures_defreturn/
procedures_callreturn -- are also done, resolved on the expression side
(getInputValue/evaluateValueBlock) rather than the action side. A pure
reporter (empty STACK, just a RETURN/"VALUE" expression) resolves to an
expression string with its own parameters substituted. A reporter whose
STACK has statements is a real, inherent limitation of this action-based
architecture (no way to "run these actions, then use this value" from a
single expression socket) -- not resolved, and surfaced as a visible
placeholder rather than silently dropped.

No Node.js in CI (this repo's established convention for this editor's
JS), so this is a structural/source check, not an execution test --
cross-referenced against the exact vendored Blockly API this was written
against (confirmed by grepping lib/blocks_compressed.js directly, not
assumed from memory): block.getFieldValue('NAME'), block.getVars() ->
this.arguments_, block.getInputTargetBlock('STACK')/('VALUE' for a
reporter's return expression -- NOT 'RETURN'), ARG0/ARG1/... value
inputs on the call block, procedures_callreturn's setOutput(true) (no
statement connectors), and variables_get's field_variable 'VAR' resolved
via workspace.getVariableById(id).getName().

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
    for block_type in ("procedures_defnoreturn", "procedures_callnoreturn",
                       "procedures_defreturn", "procedures_callreturn"):
        assert f'"{block_type}"' in src


def test_vendored_blockly_still_uses_the_assumed_api_shape():
    src = BLOCKS_COMPRESSED.read_text(encoding="utf-8")
    assert '"STACK"' in src
    assert 'getFieldValue("NAME")' in src
    assert 'getVars:function(){returnthis.arguments_}' in src.replace(" ", "")
    assert '"ARG"+' in src.replace(" ", "")


def test_vendored_defreturn_return_socket_is_named_value_not_return():
    """Confirmed directly against the vendored source before writing any
    code against it: procedures_defreturn's return-value input is named
    "VALUE" (under the PROCEDURES_DEFRETURN_RETURN label), not "RETURN"."""
    src = BLOCKS_COMPRESSED.read_text(encoding="utf-8")
    assert 'appendValueInput("VALUE")' in src.replace(" ", "")
    assert "PROCEDURES_DEFRETURN_RETURN" in src


def test_vendored_callreturn_is_output_type_with_no_statement_connectors():
    """procedures_callreturn is setOutput(true) -- it can never be dragged
    into a statement slot, so no action-list handling is needed for it on
    the codegen side (it can only ever reach a value socket)."""
    src = BLOCKS_COMPRESSED.read_text(encoding="utf-8")
    assert 'setOutput(!0)' in src.replace(" ", "")


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
    assert "block.type === 'procedures_defnoreturn' || block.type === 'procedures_defreturn'" in body
    assert "block.getFieldValue('NAME')" in body
    assert "block.getVars()" in body
    assert "block.getInputTargetBlock('STACK')" in body


def test_reporter_definitions_are_indexed_with_their_return_block():
    src = _gen_source()
    start = src.index("function indexCustomBlockDefs(workspace) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "isReporter" in body
    assert "block.getInputTargetBlock('VALUE')" in body
    assert "returnBlock" in body


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
    assert "walkActionChain(" in body


def test_pygamemaker_code_builds_the_index_once_up_front():
    src = _gen_source()
    start = src.index("function generatePyGameMakerCode(workspace) {")
    end = src.index("\nfunction getEventType", start)
    body = src[start:end]
    assert "indexCustomBlockDefs(workspace)" in body
    assert "generateBlockCode(block, customBlockDefs)" in body


def test_walk_action_chain_expands_calls_inline():
    src = _gen_source()
    start = src.index("function walkActionChain(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "block.type === 'procedures_callnoreturn'" in body
    assert "expandCustomBlockCall(" in body
    # Every other block still goes through the ordinary single-action path.
    assert "generateActionCode(block, customBlockDefs, callStack)" in body


def test_walk_action_chain_is_the_only_statement_chain_walker():
    """Every nested DO/ELSE/sub_actions site routes through walkActionChain
    now (the 2026-10-22 nesting follow-up) instead of a hand-rolled while
    loop -- confirms the old per-site duplication is actually gone, not
    just that walkActionChain itself works."""
    src = _gen_source()
    start = src.index("function generateActionCodeInner(")
    end = src.index("\n        default:\n            return null;", start)
    body = src[start:end]
    assert body.count("walkActionChain(block.getInputTargetBlock(") >= 12
    # The old per-branch while-loop pattern must not remain anywhere.
    assert "getNextBlock();\n            }" not in body


def test_expand_custom_block_call_substitutes_positional_args():
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "getInputValue(callBlock, 'ARG' + i, '')" in body
    assert "substituteCustomBlockArgs(" in body


def test_expand_custom_block_call_detects_cycles_via_the_call_stack():
    """Nesting is now fully supported (2026-10-22), so what guards
    against infinite generation-time recursion is explicit cycle
    detection via callStack, not a blanket nesting refusal."""
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "callStack.indexOf(name) !== -1" in body
    assert "__pygm_custom_block_cycle_detected__" in body
    assert "callStack.concat([name])" in body
    assert "__pygm_undefined_custom_block__" in body


def test_expand_custom_block_call_caps_expansion_depth():
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "callStack.length >= MAX_CUSTOM_BLOCK_EXPANSION_DEPTH" in body
    assert "__pygm_custom_block_too_deeply_nested__" in body


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


def test_get_input_value_delegates_to_evaluate_value_block():
    """getInputValue is now a thin (block, inputName) -> resolved-target
    wrapper so evaluateValueBlock can also be called directly on a
    definition's own RETURN block (evaluateCustomBlockReporterCall), not
    just via a parent's named input."""
    src = _gen_source()
    start = src.index("function getInputValue(block, inputName, defaultValue) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "evaluateValueBlock(block.getInputTargetBlock(inputName), defaultValue)" in body


def test_evaluate_value_block_resolves_variables_get_through_the_workspace():
    src = _gen_source()
    start = src.index("function evaluateValueBlock(input, defaultValue) {")
    end = src.index("return defaultValue;\n}", start) + len("return defaultValue;\n}")
    body = src[start:end]
    assert "input.type === 'variables_get'" in body
    assert "input.getFieldValue('VAR')" in body
    assert "input.workspace.getVariableById(varId)" in body
    assert "varModel.getName()" in body
    assert "{{PYGM_ARG:' + varName + '}}" in body


def test_evaluate_value_block_resolves_reporter_calls():
    src = _gen_source()
    start = src.index("function evaluateValueBlock(input, defaultValue) {")
    end = src.index("return defaultValue;\n}", start) + len("return defaultValue;\n}")
    body = src[start:end]
    assert "input.type === 'procedures_callreturn'" in body
    assert "evaluateCustomBlockReporterCall(input, defaultValue)" in body


def test_reporter_call_resolution_covers_undefined_cycle_depth_and_side_effects():
    src = _gen_source()
    start = src.index("function evaluateCustomBlockReporterCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "!def || !def.isReporter" in body
    assert "{{PYGM_UNDEFINED_REPORTER:" in body
    assert "CURRENT_REPORTER_CALL_STACK.indexOf(name) !== -1" in body
    assert "{{PYGM_REPORTER_CYCLE:" in body
    assert "CURRENT_REPORTER_CALL_STACK.length >= MAX_CUSTOM_BLOCK_EXPANSION_DEPTH" in body
    assert "{{PYGM_REPORTER_TOO_DEEP:" in body
    assert "def.bodyBlock" in body
    assert "{{PYGM_REPORTER_SIDE_EFFECTS:" in body
    assert "evaluateValueBlock(def.returnBlock, defaultValue)" in body
    assert "substituteCustomBlockArgs(exprValue, argValues)" in body


def test_reporter_call_stack_is_pushed_and_popped_around_evaluation():
    """Confirms the reporter cycle-detection stack is actually maintained
    (push before recursing into the definition's own RETURN expression,
    pop after) rather than just declared and never touched."""
    src = _gen_source()
    start = src.index("function evaluateCustomBlockReporterCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "CURRENT_REPORTER_CALL_STACK.push(name)" in body
    assert "CURRENT_REPORTER_CALL_STACK.pop()" in body


def test_generation_run_resets_the_reporter_module_state():
    src = _gen_source()
    start = src.index("function generatePyGameMakerCode(workspace) {")
    end = src.index("\nfunction getEventType", start)
    body = src[start:end]
    assert "CURRENT_CUSTOM_BLOCK_DEFS = customBlockDefs" in body
    assert "CURRENT_REPORTER_CALL_STACK = []" in body


def test_procedures_blocks_have_a_fallback_case_for_unsupported_positions():
    """generateActionCodeInner's own switch (reached only when a call
    somehow bypasses walkActionChain -- a code-path bug, not a normal
    authoring scenario, since nesting is now fully supported there) must
    not silently return null for any of the four procedures_* block
    types -- a dropped custom-block call/definition would be invisible
    to the author."""
    src = _gen_source()
    start = src.index("function generateActionCodeInner(")
    end = src.index("\n}", src.index("default:\n            return null;", start))
    body = src[start:end]
    assert "case 'procedures_callnoreturn':" in body
    assert "case 'procedures_callreturn':" in body
    assert "__pygm_custom_block_call_not_expanded__" in body
    assert "case 'procedures_defnoreturn':" in body
    assert "case 'procedures_defreturn':" in body
    assert "__pygm_custom_block_definition_misplaced__" in body


def test_sentinel_action_names_are_not_real_registered_actions():
    """The sentinel names must never collide with a real ActionType, or
    they'd silently execute as something else instead of rendering as
    the intended visible 'unrecognized action' indicator. (The
    expression-side PYGM_UNDEFINED_REPORTER/PYGM_REPORTER_* placeholders
    are never action names -- they're embedded in a parameter's own
    expression string -- so they don't need this check.)"""
    from events.action_types import ACTION_TYPES
    sentinels = [
        "__pygm_undefined_custom_block__",
        "__pygm_custom_block_call_not_expanded__",
        "__pygm_custom_block_definition_misplaced__",
        "__pygm_custom_block_cycle_detected__",
        "__pygm_custom_block_too_deeply_nested__",
    ]
    for name in sentinels:
        assert name not in ACTION_TYPES


@pytest.mark.parametrize("js_file", [GENERATORS_JS, WORKSPACE_HTML])
def test_braces_and_parens_balance(js_file):
    src = js_file.read_text(encoding="utf-8")
    assert src.count("{") == src.count("}")
    assert src.count("(") == src.count(")")

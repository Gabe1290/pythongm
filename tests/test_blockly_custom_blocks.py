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
BLOCKLY_COMPRESSED = (REPO_ROOT / "editors" / "object_editor" / "blockly" /
                       "lib" / "blockly_compressed.js")


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


def test_definitions_are_indexed_with_their_private_flag():
    """2026-10-22 item 7: 'for THIS object only' is read straight off
    the definition block, not stored anywhere else."""
    src = _gen_source()
    start = src.index("function indexCustomBlockDefs(workspace) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "isPrivate: isCustomBlockPrivate(block)" in body


def test_is_and_toggle_custom_block_private_use_block_data():
    """block.data is a plain string every Blockly Block already has and
    that already round-trips through workspace XML save/load for free
    (confirmed against the vendored blockToDom/domToBlock: both handle a
    <data> child element) -- no new persistence mechanism needed, and no
    mutator-field change to the vendored procedures_defnoreturn/defreturn
    block definitions themselves."""
    src = _gen_source()
    start = src.index("function isCustomBlockPrivate(block) {")
    end = src.index("\n}", start)
    is_private_body = src[start:end]
    assert "block.data === 'private'" in is_private_body

    start = src.index("function toggleCustomBlockPrivate(block) {")
    end = src.index("\n}", start)
    toggle_body = src[start:end]
    assert "block.data = wasPrivate ? null : 'private'" in toggle_body
    # A plain property write fires no Blockly event on its own -- the
    # toggle must fire one explicitly or nothing marks the workspace
    # dirty / re-runs generation. BlockChange/fire/isEnabled confirmed as
    # real Blockly.Events module members (not assumed).
    assert "Blockly.Events.isEnabled()" in toggle_body
    assert "new Blockly.Events.BlockChange(" in toggle_body
    assert "Blockly.Events.fire(" in toggle_body


def test_export_json_skips_private_definitions():
    """A private definition must never reach update_custom_blocks_registry
    at all -- skipped at export time, not filtered out on the Python
    side."""
    src = _gen_source()
    start = src.index("function generateCustomBlocksExportJson(workspace) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "if (def.isPrivate) {\n            continue;\n        }" in body


def test_context_menu_registers_the_private_toggle():
    """Exact field shape (id/scopeType/weight/preconditionFn/displayText/
    callback) confirmed against a real built-in Blockly registration
    (blockDelete) in the vendored source, not guessed -- and reuses the
    SAME Blockly.ContextMenuRegistry API the pre-existing junior-edition
    right-click removals just above it already rely on."""
    body = _ws_source()
    start = body.index("id: 'pygmToggleCustomBlockPrivate'")
    end = body.index("});", start)
    section = body[start:end]
    assert "scopeType: Blockly.ContextMenuRegistry.ScopeType.BLOCK" in section
    assert "procedures_defnoreturn" in section and "procedures_defreturn" in section
    assert "isCustomBlockPrivate(scope.block)" in section
    assert "toggleCustomBlockPrivate(scope.block)" in section


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
    """indexCustomBlockDefs itself is called from inside
    prepareCustomBlockDefsForGeneration now (the 2026-10-22 project-wide-
    sharing follow-up), not directly from generatePyGameMakerCode -- it
    also merges in every shared definition from another object, which
    generatePyGameMakerCode needs just as much as a local-only index."""
    src = _gen_source()
    start = src.index("function generatePyGameMakerCode(workspace) {")
    end = src.index("\nfunction getEventType", start)
    body = src[start:end]
    assert "prepareCustomBlockDefsForGeneration(workspace).merged" in body
    assert "generateBlockCode(block, customBlockDefs)" in body


def test_walk_action_chain_expands_calls_inline():
    src = _gen_source()
    start = src.index("function walkActionChain(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "block.type === 'procedures_callnoreturn'" in body
    assert "expandCustomBlockCall(" in body
    # Every other block still goes through the ordinary single-action path.
    assert "generateActionCode(block, customBlockDefs, callStack, hoisted)" in body


def test_walk_action_chain_hoists_actions_for_both_branches():
    """Reporter side-effect hoisting (2026-10-22, item 4): both the
    procedures_callnoreturn branch and the ordinary-action branch set up
    their own fresh hoist sink and splice its contents in BEFORE the
    statement's own result."""
    src = _gen_source()
    start = src.index("function walkActionChain(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "CURRENT_HOIST_SINK = hoistedForCall" in body
    assert "actions.concat(hoistedForCall).concat(expanded)" in body
    assert "actions = actions.concat(hoisted);" in body


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
    assert "CURRENT_EXPANSION_STACK.indexOf(name) !== -1" in body
    assert "{{PYGM_REPORTER_CYCLE:" in body
    assert "CURRENT_EXPANSION_STACK.length >= MAX_CUSTOM_BLOCK_EXPANSION_DEPTH" in body
    assert "{{PYGM_REPORTER_TOO_DEEP:" in body
    assert "def.bodyBlock" in body
    assert "{{PYGM_REPORTER_SIDE_EFFECTS:" in body
    assert "evaluateValueBlock(def.returnBlock, defaultValue)" in body
    assert "substituteCustomBlockArgs(exprValue, argValues)" in body


def test_reporter_with_side_effects_is_hoisted_not_refused():
    """The 2026-10-22 follow-up (item 4): a side-effecting reporter body
    is walked/reused and pushed onto CURRENT_HOIST_SINK, substituted with
    this call's own argument values -- "run the actions, then use the
    value" -- rather than unconditionally returning the SIDE_EFFECTS
    placeholder. That placeholder now only fires when there's no hoist
    sink available at all (hasSideEffectingBody && !CURRENT_HOIST_SINK)."""
    src = _gen_source()
    start = src.index("function evaluateCustomBlockReporterCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "hasSideEffectingBody && !CURRENT_HOIST_SINK" in body
    assert "CURRENT_HOIST_SINK.push(hoistedActions[h])" in body
    assert "walkActionChain(def.bodyBlock, CURRENT_CUSTOM_BLOCK_DEFS," in body
    assert "CURRENT_EXPANSION_STACK.slice()" in body


def test_reporter_call_stack_is_pushed_and_popped_around_evaluation():
    """Confirms the reporter cycle-detection stack is actually maintained
    (push before recursing into the definition's own RETURN expression,
    pop after) rather than just declared and never touched."""
    src = _gen_source()
    start = src.index("function evaluateCustomBlockReporterCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "CURRENT_EXPANSION_STACK.push(name)" in body
    assert "CURRENT_EXPANSION_STACK.pop()" in body


def test_generation_run_resets_the_reporter_module_state():
    """The reset moved into prepareCustomBlockDefsForGeneration (the
    2026-10-22 project-wide-sharing follow-up), called by BOTH
    generatePyGameMakerCode and generateCustomBlocksExportJson, so
    neither can prepare customBlockDefs differently from the other."""
    src = _gen_source()
    start = src.index("function prepareCustomBlockDefsForGeneration(workspace) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "CURRENT_CUSTOM_BLOCK_DEFS = merged" in body
    assert "CURRENT_EXPANSION_STACK = []" in body
    assert "CURRENT_HOIST_SINK = null" in body


def test_pygamemaker_code_and_export_share_the_same_preparation_function():
    src = _gen_source()
    gen_start = src.index("function generatePyGameMakerCode(workspace) {")
    gen_end = src.index("\nfunction getEventType", gen_start)
    assert "prepareCustomBlockDefsForGeneration(workspace)" in src[gen_start:gen_end]

    export_start = src.index("function generateCustomBlocksExportJson(workspace) {")
    export_end = src.index("\n}", export_start)
    export_body = src[export_start:export_end]
    assert "prepareCustomBlockDefsForGeneration(workspace)" in export_body


# ---------------------------------------------------------------------------
# Project-wide custom block sharing (2026-10-22 follow-up) -- each object's
# Blockly workspace lives on its own separate page with its own isolated
# JS state (confirmed via blockly_widget.py/object_editor_main.py: the
# workspace XML is saved/loaded per object, nothing merges another
# object's blocks in), so without the mechanism below a custom block
# defined in object A is invisible when editing object B -- contradicting
# this feature's own original "Scope: project-level... shared by every
# object" decision. See docs/BLOCKLY_SCRATCH_PARITY_PLAN.md's "Follow-up:
# nesting + reporters" / sharing section for the full design.
# ---------------------------------------------------------------------------

def test_merge_shared_custom_block_defs_lets_local_win_on_collision():
    src = _gen_source()
    start = src.index("function mergeSharedCustomBlockDefs(localDefs) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "SHARED_CUSTOM_BLOCKS" in body
    assert "bodyBlock: null" in body
    assert "returnBlock: null" in body
    assert "bodyActionsTemplate: entry.body_actions" in body
    assert "returnExprTemplate" in body
    # Local defs are assigned into `merged` AFTER the shared ones, in the
    # same object -- an object-literal/plain-assignment loop ordering
    # that lets a later key win, which is exactly how "local wins" is
    # implemented here (no explicit `if` needed).
    local_loop = body.index("for (var localName in localDefs)")
    shared_loop = body.index("for (var sharedName in SHARED_CUSTOM_BLOCKS)")
    assert shared_loop < local_loop


def test_expand_custom_block_call_uses_the_template_for_a_shared_def():
    """A shared (cross-object) def has bodyBlock===null -- confirms
    expandCustomBlockCall branches to bodyActionsTemplate instead of
    trying to walk a nonexistent block."""
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "def.bodyBlock\n            ? walkActionChain" in body or "def.bodyBlock ? walkActionChain" in body
    assert "def.bodyActionsTemplate || []" in body


def test_expand_custom_block_call_mirrors_its_name_into_the_expansion_stack():
    """2026-10-22 item 4: expandCustomBlockCall pushes/pops the SAME
    CURRENT_EXPANSION_STACK a side-effecting reporter checks, so a cycle
    crossing both mechanisms (A calls reporter R which calls A again) is
    caught -- not just a same-mechanism A->A or R->R cycle."""
    src = _gen_source()
    start = src.index("function expandCustomBlockCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "CURRENT_EXPANSION_STACK.push(name)" in body
    assert "CURRENT_EXPANSION_STACK.pop()" in body


def test_reporter_call_resolves_shared_templates_too():
    src = _gen_source()
    start = src.index("function evaluateCustomBlockReporterCall(")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "hasSideEffectingBody" in body
    assert "def.bodyActionsTemplate && def.bodyActionsTemplate.length" in body
    assert "hasReturnExpr" in body
    assert "def.returnExprTemplate !== null" in body
    assert "exprValue = def.bodyBlock" in body
    assert "def.returnExprTemplate" in body


def test_set_shared_custom_blocks_parses_and_tolerates_bad_json():
    src = _gen_source()
    start = src.index("function setSharedCustomBlocks(json) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "JSON.parse(json)" in body
    assert "catch (e)" in body
    assert "SHARED_CUSTOM_BLOCKS = {}" in body


def test_export_json_only_exports_local_defs_not_shared_pass_throughs():
    """Confirms generateCustomBlocksExportJson iterates prepared.local
    (indexCustomBlockDefs' own return value), not prepared.merged -- a
    shared/external def must never be echoed back out as if this
    workspace owned it."""
    src = _gen_source()
    start = src.index("function generateCustomBlocksExportJson(workspace) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "for (var name in prepared.local)" in body
    assert "walkActionChain(def.bodyBlock, prepared.merged, [name])" in body


def test_build_shared_custom_block_flyout_items_matches_xml_flyout_category_shape():
    """XML shape confirmed directly against the vendored source's
    xmlFlyoutCategory function (the one actually driving the "PROCEDURE"
    category, since Blockly.Procedures.flyoutCategory turned out not to
    be real public dotted API -- see the workspace.html comment this
    mirrors): <block type="procedures_call(no)return" gap="16">
    <mutation name="..."><arg name="..."/></mutation></block>."""
    src = _gen_source()
    start = src.index("function buildSharedCustomBlockFlyoutItems(ws) {")
    end = src.index("\nfunction escapeCustomBlockXmlAttr", start)
    body = src[start:end]
    assert '<block type="' in body
    assert "gap=\"16\"" in body or 'gap="16"' in body
    assert '<mutation name="' in body
    assert '<arg name="' in body
    assert "procedures_callreturn" in body and "procedures_callnoreturn" in body
    assert "Blockly.utils.xml.textToDom(" in body


def test_build_shared_custom_block_flyout_items_skips_locally_defined_names():
    src = _gen_source()
    start = src.index("function buildSharedCustomBlockFlyoutItems(ws) {")
    end = src.index("\nfunction escapeCustomBlockXmlAttr", start)
    body = src[start:end]
    assert "if (localNames[name]) continue;" in body


def test_escape_custom_block_xml_attr_handles_the_dangerous_characters():
    src = _gen_source()
    start = src.index("function escapeCustomBlockXmlAttr(s) {")
    end = src.index("\n}", start)
    body = src[start:end]
    for needle in ("&amp;", "&quot;", "&lt;", "&gt;"):
        assert needle in body


def test_toolbox_wraps_whatever_is_already_registered_not_the_unreal_public_api():
    """The pre-existing guard (`if (Blockly.Procedures && typeof
    Blockly.Procedures.flyoutCategory === 'function')`) assumed a public
    dotted API that doesn't actually exist in this vendored build -- the
    only occurrence of that exact string anywhere in blocks_compressed.js
    is inside a deprecation-warning MESSAGE, not real code (confirmed by
    grep). The fix reads back whatever workspace.getToolboxCategoryCallback
    already has registered for "PROCEDURE" (self-registered by the
    vendored core at workspace construction, confirmed separately) and
    wraps THAT, with the old check kept only as a defensive fallback."""
    body = _ws_source()
    assert "workspace.getToolboxCategoryCallback(procedureCategoryName)" in body
    assert "workspace.registerToolboxCategoryCallback(procedureCategoryName, function(ws) {" in body
    assert "buildSharedCustomBlockFlyoutItems(ws)" in body


def test_vendored_flyoutcategory_string_is_only_ever_a_warning_message():
    """Pins the finding that justified the fix above -- if a future
    Blockly upgrade ever makes Blockly.Procedures.flyoutCategory real
    public API, this test (not a runtime surprise) is what should catch
    the vendored-source assumption going stale. The literal string lives
    in blockly_compressed.js (the core engine), not blocks_compressed.js
    (the block definitions) -- confirmed by grep before writing this."""
    src = BLOCKLY_COMPRESSED.read_text(encoding="utf-8")
    idx = src.find("Blockly.Procedures.flyoutCategory")
    assert idx != -1, "expected the string to still exist at least once"
    assert "deprecat" in src[max(0, idx - 200):idx].lower()


def test_blockly_api_exposes_the_new_sharing_entry_points():
    body = _ws_source()
    assert "setSharedCustomBlocks: setSharedCustomBlocks" in body
    assert "getCustomBlocksExport: function() { return generateCustomBlocksExportJson(workspace); }" in body


# ---------------------------------------------------------------------------
# Live cross-object name-collision prevention (2026-10-22 follow-up, item 6)
# ---------------------------------------------------------------------------

def test_change_listener_checks_definition_create_and_name_change():
    """Both ways a definition's name can end up colliding: a fresh
    "Make a Block" (BLOCK_CREATE) and editing an existing one's NAME
    field (BLOCK_CHANGE, element 'field', name 'NAME') -- both guarded by
    the SAME ignoreChanges/workspaceLocked check already protecting
    onBlocksChanged, so a programmatic workspace load never triggers
    this."""
    src = _ws_source()
    start = src.index("workspace.addChangeListener(function(event) {")
    end = src.index("\n        });", start)
    body = src[start:end]
    assert "if (ignoreChanges || workspaceLocked) return;" in body
    assert "disambiguateCustomBlockNameAgainstShared(event.blockId)" in body
    assert "event.type === Blockly.Events.BLOCK_CREATE" in body
    assert "event.element === 'field' && event.name === 'NAME'" in body


def test_block_create_event_type_is_read_from_its_own_json():
    src = _ws_source()
    start = src.index("function _blockTypeOfCreateEvent(event) {")
    end = src.index("\n        }", start)
    body = src[start:end]
    assert "event.json && event.json.type" in body
    assert "workspace.getBlockById(event.blockId)" in body


def test_disambiguate_renames_and_warns_on_a_real_collision():
    src = _gen_source()
    start = src.index("function disambiguateCustomBlockNameAgainstShared(blockId) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "procedures_defnoreturn" in body and "procedures_defreturn" in body
    assert "SHARED_CUSTOM_BLOCKS[name]" in body
    # Loops to the next free "<name>_<n>" suffix, mirroring Blockly's own
    # local findLegalName behaviour, extended to the shared registry.
    assert "while (SHARED_CUSTOM_BLOCKS[candidate])" in body
    assert "block.setFieldValue(candidate, 'NAME')" in body
    assert "block.setWarningText(" in body
    assert "existing.source_object" in body


def test_disambiguate_is_a_noop_for_a_block_with_no_collision():
    src = _gen_source()
    start = src.index("function disambiguateCustomBlockNameAgainstShared(blockId) {")
    end = src.index("\n}", start)
    body = src[start:end]
    assert "if (!existing) {\n        return;\n    }" in body


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

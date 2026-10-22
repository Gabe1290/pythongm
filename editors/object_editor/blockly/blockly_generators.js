/**
 * PyGameMaker Blockly Code Generators
 * Converts blocks to PyGameMaker event/action format
 */

// ============================================================================
// CODE GENERATION FUNCTIONS
// ============================================================================

function generatePythonCode() {
    return generatePyGameMakerCode(workspace);
}

// Custom Python code generator for PyGameMaker
function generatePyGameMakerCode(workspace) {
    var events = {};
    var topBlocks = workspace.getTopBlocks(true);
    // docs/BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 2 ("My Blocks"): indexed
    // once per generation run, before any event is walked, so a call
    // appearing anywhere can resolve its definition regardless of block
    // order on the canvas. procedures_defnoreturn/defreturn blocks are
    // themselves skipped by getEventType's default case below (no case
    // names them), so a definition never produces its own spurious event.
    // prepareCustomBlockDefsForGeneration merges in every project-wide
    // SHARED definition (another object's own custom blocks, pushed into
    // this page via setSharedCustomBlocks) alongside this workspace's own
    // local ones, and seeds the module-level reporter-resolution state
    // (CURRENT_CUSTOM_BLOCK_DEFS/CURRENT_EXPANSION_STACK/CURRENT_HOIST_SINK)
    // that getInputValue/evaluateValueBlock read from, since they aren't
    // threaded customBlockDefs as a parameter (see the big comment above
    // evaluateCustomBlockReporterCall).
    var customBlockDefs = prepareCustomBlockDefsForGeneration(workspace).merged;

    for (var i = 0; i < topBlocks.length; i++) {
        var block = topBlocks[i];
        var eventType = getEventType(block);
        if (eventType) {
            var code = generateBlockCode(block, customBlockDefs);

            // Handle keyboard and alarm events with nested format
            // Output: {"keyboard": {"right": {"actions": [...]}}} or {"alarm": {"alarm_0": {"actions": [...]}}}
            if (eventType.subtype && (eventType.event === 'keyboard' || eventType.event === 'keyboard_press' || eventType.event === 'keyboard_release' || eventType.event === 'alarm')) {
                if (!events[eventType.event]) {
                    events[eventType.event] = {};
                }
                // Create nested structure: keyboard -> key -> actions
                events[eventType.event][eventType.subtype] = {actions: code.actions || []};
            } else {
                // Regular event (create, step, draw, etc.)
                if (!events[eventType.event]) {
                    events[eventType.event] = {actions: []};
                }
                events[eventType.event].actions = events[eventType.event].actions.concat(code.actions || []);
            }
        }
    }

    return JSON.stringify(events, null, 2);
}

function getEventType(block) {
    switch (block.type) {
        case 'event_create': return {event: 'create'};
        case 'event_step': return {event: 'step'};
        case 'event_draw': return {event: 'draw'};
        case 'event_destroy': return {event: 'destroy'};
        case 'event_alarm': return {event: 'alarm', subtype: 'alarm_' + block.getFieldValue('ALARM_NUM')};
        case 'event_keyboard_nokey': return {event: 'keyboard', subtype: 'nokey'};
        case 'event_keyboard_anykey': return {event: 'keyboard', subtype: 'anykey'};
        case 'event_keyboard_held': return {event: 'keyboard', subtype: block.getFieldValue('KEY')};
        case 'event_keyboard_press': return {event: 'keyboard_press', subtype: block.getFieldValue('KEY')};
        case 'event_keyboard_release': return {event: 'keyboard_release', subtype: block.getFieldValue('KEY')};
        case 'event_mouse': return {event: 'mouse_' + block.getFieldValue('BUTTON')};
        case 'event_collision': return {event: 'collision_with_' + block.getFieldValue('OBJECT')};
        // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B3: the EVENT_NAME dropdown
        // value IS the real event name -- no lookup table to keep in sync.
        case 'event_other': return {event: block.getFieldValue('EVENT_NAME')};
        case 'event_extension':
            var extEvent = block.getFieldValue('EVENT_NAME');
            return extEvent ? {event: extEvent} : null;
        // Thymio events
        case 'event_thymio_button_forward': return {event: 'thymio_button_forward'};
        case 'event_thymio_button_backward': return {event: 'thymio_button_backward'};
        case 'event_thymio_button_left': return {event: 'thymio_button_left'};
        case 'event_thymio_button_right': return {event: 'thymio_button_right'};
        case 'event_thymio_button_center': return {event: 'thymio_button_center'};
        case 'event_thymio_any_button': return {event: 'thymio_any_button'};
        case 'event_thymio_proximity_update': return {event: 'thymio_proximity_update'};
        case 'event_thymio_ground_update': return {event: 'thymio_ground_update'};
        case 'event_thymio_timer_0': return {event: 'thymio_timer_0'};
        case 'event_thymio_timer_1': return {event: 'thymio_timer_1'};
        case 'event_thymio_tap': return {event: 'thymio_tap'};
        case 'event_thymio_sound_detected': return {event: 'thymio_sound_detected'};
        case 'event_thymio_sound_finished': return {event: 'thymio_sound_finished'};
        case 'event_thymio_message_received': return {event: 'thymio_message_received'};
        default: return null;
    }
}

function generateBlockCode(eventBlock, customBlockDefs) {
    var doBlock = eventBlock.getInputTargetBlock('DO');
    return {actions: walkActionChain(doBlock, customBlockDefs || {}, [])};
}

// ============================================================================
// CUSTOM BLOCKS ("My Blocks") -- docs/BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 2
// ============================================================================
//
// A student-defined block (Blockly's native procedures_defnoreturn/
// procedures_callnoreturn/procedures_defreturn/procedures_callreturn --
// the vendored library already ships the whole feature, definition UI
// included, see lib/blocks_compressed.js) is pure authoring sugar: a
// call is expanded into its definition's own action list (no-return) or
// return expression (reporter) AT GENERATION TIME, right here, with each
// declared parameter substituted by its call-site value. The *saved*
// project data therefore only ever contains ordinary, already-understood
// actions and expression strings -- no new action type, no runtime
// changes, no HTML5/Kivy codegen changes needed.
//
// Nesting is fully supported: walkActionChain is used for every action
// chain in this file, not just an event's own top-level DO stack -- an
// if_condition/test_variable/thymio_if_* branch, and a custom block's own
// STACK body, all walk through it, so a call anywhere expands correctly
// to zero-or-many actions instead of being refused. `callStack` is the
// list of custom-block names currently being expanded on the path from
// the nearest top-level chain down to here; expandCustomBlockCall pushes
// onto it before walking a definition's own body and pops after, so a
// call that would re-enter a name already on the stack (direct
// self-recursion, or a longer A -> B -> A cycle) is caught and refused
// with a visible sentinel INSTEAD of generation recursing forever --
// this is the cycle detection the nesting restriction used to make
// unnecessary by construction. MAX_CUSTOM_BLOCK_EXPANSION_DEPTH is a
// defense-in-depth cap independent of that: a long chain of distinct,
// non-cyclic custom blocks calling each other could still expand into a
// pathologically large action list, so depth is capped even though no
// cycle is present.
//
// Reporter-style (value-returning) custom blocks -- procedures_defreturn/
// procedures_callreturn -- are resolved on the EXPRESSION side instead
// (getInputValue/evaluateValueBlock below), since a reporter call can
// appear inside any value socket, not just a statement chain. A pure
// reporter (its own STACK is empty -- just a RETURN value) expands to an
// expression string with its own parameters substituted, exactly like a
// no-return call's action parameters.
//
// A reporter whose STACK has statements (side effects before computing
// the return value) IS resolved too (2026-10-22 follow-up): its body is
// walked/reused the same way a no-return call's body is, and the
// resulting (argument-substituted) actions are HOISTED -- spliced into
// the enclosing action list immediately before whatever action is
// actually consuming the reporter's return value (walkActionChain sets
// up a fresh hoist sink, CURRENT_HOIST_SINK, for every single statement
// it walks). This is genuinely "run these actions, then use this value"
// from inside what started as one expression socket, not a workaround --
// made possible by walkActionChain already being the universal chain
// walker everywhere (the nesting follow-up above), so there's always
// somewhere to splice hoisted actions in, however deeply nested the
// reporter call is. The one case that's still NOT resolved, narrowed
// from "every side-effecting reporter call" to just this one: a
// reporter's own RETURN expression, evaluated once at EXPORT time to
// build another definition's reusable TEMPLATE (generateCustomBlocks
// ExportJson), has no action list to hoist into at all -- surfaced as
// the same visible, non-crashing placeholder string as before, just for
// a much narrower case.
//
// Reporter calls get their OWN cycle-detection stack, CURRENT_EXPANSION_
// STACK (module-level -- getInputValue's ~60 existing call sites across
// this file take only (block, inputName, defaultValue), and threading an
// extra parameter through every one of them for this would be a much
// larger, riskier change than the contained action-side threading
// above) -- but, since reporter hoisting now actually walks a
// side-effecting body (which can itself call a no-return custom block,
// or another reporter), this stack is SHARED with the action side too:
// expandCustomBlockCall mirrors its own callStack pushes into it, so a
// cycle that crosses BOTH mechanisms (A calls reporter R calls A again,
// or R calls no-return block A which calls R again) is caught exactly
// like a same-mechanism cycle, not just R->R or A->A. A custom-block
// NAME uniquely identifies either kind of definition (indexCustomBlockDefs
// keys both into the same dict), so one shared stack is the correct,
// not merely convenient, way to track this.

// Defense-in-depth against a pathologically deep (but acyclic) chain of
// custom blocks calling custom blocks -- cycles themselves are already
// fully prevented by callStack/CURRENT_EXPANSION_STACK below.
var MAX_CUSTOM_BLOCK_EXPANSION_DEPTH = 50;

// ----------------------------------------------------------------------
// PROJECT-WIDE CUSTOM BLOCK SHARING (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md,
// 2026-10-22 follow-up)
// ----------------------------------------------------------------------
//
// Each object's Blockly workspace lives on its own separate page with its
// own isolated JS state (confirmed against editors/object_editor/
// blockly_widget.py / object_editor_main.py: workspace XML is saved and
// loaded per object, and nothing ever merges another object's blocks into
// this one) -- so without this, a custom block defined in object A is
// completely invisible when editing object B, contradicting this
// feature's own original design decision ("Scope: project-level...
// shared by every object"). SHARED_CUSTOM_BLOCKS holds the project-wide
// registry Python maintains (core/project_manager.py's
// update_custom_blocks_registry, called whenever an object is saved) in
// current_project_data['custom_blocks'], pushed into this page via
// setSharedCustomBlocks at load time (blockly_widget.py's
// push_shared_custom_blocks) -- so even an object whose own editor has
// never been opened this session still has its blocks available,
// because the registry is read from the already-loaded project data, not
// from any other object's live workspace.
//
// Each registry entry is a fully pre-resolved TEMPLATE: its own nested
// calls already expanded (via generateCustomBlocksExportJson, run inside
// the SOURCE object's own workspace the last time IT generated code),
// with only that definition's own {{PYGM_ARG:<name>}} placeholders left
// unsubstituted so a future call site -- in this object or any other --
// can still supply its own argument values. This is why a shared
// definition never needs the calling page's own Blockly blocks to
// resolve: expandCustomBlockCall/evaluateCustomBlockReporterCall treat a
// null bodyBlock/returnBlock (the merged-in shape below) as a signal to
// use bodyActionsTemplate/returnExprTemplate directly instead of walking
// real blocks.
//
// Each object's export is computed independently from whatever snapshot
// of OTHER objects' templates was pushed into its page. A block changed
// in object A is pushed into every OTHER currently open object editor's
// workspace immediately on save (core/ide/_editor_lifecycle.py's
// _broadcast_shared_custom_blocks, 2026-10-22 follow-up item 5) -- not
// instantly while A's OWN edit is still in progress mid-keystroke, since
// the export only happens at save, but there is no more "reopen the tab
// to see it" gap for a tab that was already open. A genuine cross-object
// cycle (A's block calls B's which calls back into A's) is consequently
// still never a crash risk regardless of how promptly the push happens:
// nothing recomputes recursively across OBJECTS at generation time,
// since each side only ever consumes an already-resolved template, never
// a live block -- at worst a call sees a one-generation-stale template,
// never an infinite loop. A same-object cycle (including one that now
// crosses between a reporter and a no-return call, since reporter
// side-effect hoisting started walking real bodies -- see the big
// comment above MAX_CUSTOM_BLOCK_EXPANSION_DEPTH) is still actively
// caught by callStack/CURRENT_EXPANSION_STACK; this paragraph only
// concerns the cross-OBJECT case those can't see.
var SHARED_CUSTOM_BLOCKS = {};

// Called from blocklyApi.setSharedCustomBlocks (blockly_widget.py's
// push_shared_custom_blocks). Safe to call repeatedly; the project-wide
// registry is always replaced wholesale, never merged incrementally.
function setSharedCustomBlocks(json) {
    try {
        SHARED_CUSTOM_BLOCKS = JSON.parse(json) || {};
    } catch (e) {
        SHARED_CUSTOM_BLOCKS = {};
    }
    return Object.keys(SHARED_CUSTOM_BLOCKS).length;
}

// Merges this workspace's own local definitions (indexCustomBlockDefs'
// own return value -- unchanged, still local-only) with every
// project-wide shared definition from SHARED_CUSTOM_BLOCKS, in the shape
// expandCustomBlockCall/evaluateCustomBlockReporterCall already expect. A
// LOCAL definition always wins on a name collision -- this is now
// mostly theoretical rather than a real sharp edge, since
// disambiguateCustomBlockNameAgainstShared (2026-10-22 follow-up, item
// 6) actively renames a NEW local definition the moment its name would
// collide with a shared one (Blockly's own duplicate-name prevention --
// findLegalName -- is workspace-local only, so that live check is what
// extends it project-wide); the remaining cases this merge rule quietly
// covers are a collision that already existed before that check shipped,
// or one introduced by hand-editing project.json outside the IDE.
function mergeSharedCustomBlockDefs(localDefs) {
    var merged = {};
    for (var sharedName in SHARED_CUSTOM_BLOCKS) {
        var entry = SHARED_CUSTOM_BLOCKS[sharedName];
        if (!entry) continue;
        merged[sharedName] = {
            argNames: entry.arg_names || [],
            bodyBlock: null,
            returnBlock: null,
            isReporter: !!entry.is_reporter,
            bodyActionsTemplate: entry.body_actions || [],
            returnExprTemplate: (entry.return_expr !== undefined) ? entry.return_expr : null
        };
    }
    for (var localName in localDefs) {
        merged[localName] = localDefs[localName];
    }
    return merged;
}

// Indexes local defs, merges in shared ones, and (re)seeds the
// module-level reporter-resolution state in one place, so
// generatePyGameMakerCode and generateCustomBlocksExportJson can never
// prepare customBlockDefs differently from each other.
function prepareCustomBlockDefsForGeneration(workspace) {
    var localDefs = indexCustomBlockDefs(workspace);
    var merged = mergeSharedCustomBlockDefs(localDefs);
    CURRENT_CUSTOM_BLOCK_DEFS = merged;
    CURRENT_EXPANSION_STACK = [];
    CURRENT_HOIST_SINK = null;
    return {local: localDefs, merged: merged};
}

// The project-wide-sharing counterpart to generatePyGameMakerCode: for
// every LOCAL definition on this workspace only (never a merged-in
// shared one -- re-exporting a pass-through copy of another object's
// own block would be redundant and could only ever go stale sooner),
// pre-resolve it ONCE into a template using the exact same walkActionChain/
// evaluateValueBlock machinery a real call site uses, so its own nested
// calls are already expanded -- just with this definition's OWN
// {{PYGM_ARG:<name>}} placeholders left unsubstituted for a future call
// site to fill in. Returns a JSON string; blocklyApi.getCustomBlocksExport
// (mirroring getXml's own cached-pull pattern in blockly_widget.py) is
// how Python retrieves it.
function generateCustomBlocksExportJson(workspace) {
    var prepared = prepareCustomBlockDefsForGeneration(workspace);
    var exported = {};
    for (var name in prepared.local) {
        var def = prepared.local[name];
        // "For THIS object only" (item 7): a private definition is never
        // published project-wide -- skipped here, not filtered out on
        // the Python side, so it never even reaches
        // update_custom_blocks_registry. Calls to it from elsewhere IN
        // THIS SAME object's own workspace are completely unaffected
        // (prepared.local/prepared.merged still include it; only the
        // EXPORT is skipped).
        if (def.isPrivate) {
            continue;
        }
        // return_expr is a standalone, reusable TEMPLATE -- not part of
        // any real action list a side-effecting nested reporter call
        // could hoist into -- so CURRENT_HOIST_SINK is explicitly nulled
        // around this one call (not left at whatever a PRIOR
        // walkActionChain call happened to set it to) so
        // evaluateCustomBlockReporterCall's own "no sink available"
        // fallback behaves deterministically here.
        var previousSink = CURRENT_HOIST_SINK;
        CURRENT_HOIST_SINK = null;
        var returnExpr;
        try {
            returnExpr = (def.isReporter && def.returnBlock)
                ? evaluateValueBlock(def.returnBlock, '')
                : null;
        } finally {
            CURRENT_HOIST_SINK = previousSink;
        }
        exported[name] = {
            arg_names: def.argNames,
            is_reporter: def.isReporter,
            body_actions: walkActionChain(def.bodyBlock, prepared.merged, [name]),
            return_expr: returnExpr
        };
    }
    return JSON.stringify(exported);
}

// The "My Blocks" flyout's own counterpart to the codegen merge above:
// Blockly.Procedures.allProcedures only ever sees THIS workspace's own
// local blocks, so without this, a shared definition from another
// object could be CALLED (via the codegen merge above) but never
// actually DRAGGED IN in the first place -- making it entirely
// unreachable in practice, since a procedures_callnoreturn/callreturn
// block can only be authored by dragging one from this flyout (Blockly
// has no other way to create one). Returns an array of <block> XML
// Elements in the exact shape Blockly's own internalFlyoutCategory
// produces for a local definition -- confirmed against the vendored
// source's xmlFlyoutCategory function: <block type="procedures_call(no)
// return" gap="16"><mutation name="..."><arg name="..."/>...</mutation>
// </block> -- parsed via the same Blockly.utils.xml.textToDom this file's
// own workspace loader already uses elsewhere, so a dragged-in shared
// call block is indistinguishable from a local one to the rest of
// Blockly's own call-site-sync machinery (mutationToDom/domToMutation).
// Skips any shared name that collides with a LOCAL definition (which
// already gets its own real flyout entry from the wrapped original
// callback; showing it twice would be confusing, and
// mergeSharedCustomBlockDefs already means local wins at the codegen
// level too, so the two must agree).
function buildSharedCustomBlockFlyoutItems(ws) {
    var names = Object.keys(SHARED_CUSTOM_BLOCKS || {});
    if (names.length === 0) return [];

    var localNames = {};
    try {
        if (window.Blockly && Blockly.Procedures && typeof Blockly.Procedures.allProcedures === 'function') {
            var procs = Blockly.Procedures.allProcedures(ws);
            procs[0].concat(procs[1]).forEach(function(p) { localNames[p[0]] = true; });
        } else {
            // allProcedures isn't reliably exposed as public dotted API in
            // this vendored build (the same reason the pre-existing
            // Blockly.Procedures.flyoutCategory guard below is defensive,
            // not assumed) -- fall back to indexCustomBlockDefs, which
            // this file already trusts for the same "what's defined
            // locally" answer.
            localNames = indexCustomBlockDefs(ws);
        }
    } catch (e) { /* on any failure, show every shared block rather than hide all of them */ }

    var xmlParts = [];
    for (var i = 0; i < names.length; i++) {
        var name = names[i];
        if (localNames[name]) continue;
        var entry = SHARED_CUSTOM_BLOCKS[name];
        if (!entry) continue;
        var blockType = entry.is_reporter ? 'procedures_callreturn' : 'procedures_callnoreturn';
        var argsXml = (entry.arg_names || []).map(function(argName) {
            return '<arg name="' + escapeCustomBlockXmlAttr(argName) + '"></arg>';
        }).join('');
        xmlParts.push(
            '<block type="' + blockType + '" gap="16">' +
            '<mutation name="' + escapeCustomBlockXmlAttr(name) + '">' + argsXml + '</mutation>' +
            '</block>'
        );
    }
    if (xmlParts.length === 0) return [];
    try {
        var dom = Blockly.utils.xml.textToDom('<xml>' + xmlParts.join('') + '</xml>');
        return Array.prototype.slice.call(dom.childNodes);
    } catch (e) {
        return [];
    }
}

function escapeCustomBlockXmlAttr(s) {
    return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;')
                     .replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Real, LIVE prevention for cross-object custom-block name collisions
// (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md's 2026-10-22 follow-up, item 6 --
// previously "last-write-wins, not prevented"). Called from blockly_
// workspace.html's own change listener whenever a procedures_defnoreturn/
// defreturn block is created, or its NAME field edited -- both already
// guarded there by the same ignoreChanges/workspaceLocked check that
// suppresses this during a programmatic workspace LOAD, so reopening a
// project never silently renames something already saved; this only
// ever fires for a genuine live edit.
//
// If the current name already belongs to a project-wide SHARED
// definition (SHARED_CUSTOM_BLOCKS, sourced from a DIFFERENT object --
// this object's own prior save of the SAME name is impossible to collide
// with itself here, since mergeSharedCustomBlockDefs always lets the
// LOCAL block win at generation time regardless of what the registry
// echoes back), renames it to the next available "<name>_<n>" suffix --
// mirroring Blockly's own local findLegalName behaviour (workspace-local
// only), just extended to the project-wide registry -- and leaves a
// visible warning balloon (block.setWarningText, the same mechanism
// procedures_ifreturn's own PROCEDURES_IFRETURN_WARNING already uses)
// explaining why, since silently renaming something a student just
// typed with no feedback would be exactly the kind of "stop lying to
// users" silence this codebase avoids elsewhere.
function disambiguateCustomBlockNameAgainstShared(blockId) {
    var block = workspace.getBlockById(blockId);
    if (!block) return;
    if (block.type !== 'procedures_defnoreturn' && block.type !== 'procedures_defreturn') return;

    var name = block.getFieldValue('NAME');
    var existing = SHARED_CUSTOM_BLOCKS[name];
    if (!existing) {
        return;
    }

    var candidate = name;
    var n = 2;
    while (SHARED_CUSTOM_BLOCKS[candidate]) {
        candidate = name + '_' + n;
        n++;
    }
    block.setFieldValue(candidate, 'NAME');
    block.setWarningText(
        'Renamed to "' + candidate + '" because "' + name + '" is already ' +
        'used by a custom block in another object (' +
        (existing.source_object || '?') + ').');
}

// Every procedures_defnoreturn/procedures_defreturn block on the
// workspace, keyed by name -> {argNames: [...], bodyBlock: <first body
// block, or null if empty>, returnBlock: <the RETURN value's block, or
// null>, isReporter: bool, isPrivate: bool}. Built once per generation
// run (see generatePyGameMakerCode).
function indexCustomBlockDefs(workspace) {
    var defs = {};
    var topBlocks = workspace.getTopBlocks(true);
    for (var i = 0; i < topBlocks.length; i++) {
        var block = topBlocks[i];
        if (block.type === 'procedures_defnoreturn' || block.type === 'procedures_defreturn') {
            var name = block.getFieldValue('NAME');
            // getVars() is the standard accessor (shared by both def
            // types) for the parameter name list (confirmed against the
            // vendored source: `getVars: function() { return
            // this.arguments_; }`).
            var argNames = (typeof block.getVars === 'function') ? block.getVars() : [];
            var isReporter = block.type === 'procedures_defreturn';
            defs[name] = {
                argNames: argNames,
                bodyBlock: block.getInputTargetBlock('STACK'),
                // The return value socket's input name is "VALUE", NOT
                // "RETURN" -- confirmed directly against the vendored
                // source (procedures_defreturn's init swaps in
                // `this.appendValueInput("VALUE")` under the
                // PROCEDURES_DEFRETURN_RETURN label); defnoreturn has no
                // such input at all.
                returnBlock: isReporter ? block.getInputTargetBlock('VALUE') : null,
                isReporter: isReporter,
                // "For THIS object only" (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md's
                // 2026-10-22 follow-up, item 7 -- Scratch's OTHER custom-
                // block scoping option, project-wide sharing being the
                // first). isCustomBlockPrivate reads block.data, a plain
                // string field every Blockly Block already has and that
                // already round-trips through workspace XML save/load
                // for free (confirmed against the vendored source:
                // blockToDom/domToBlock both serialize a <data> child
                // element) -- no new persistence mechanism needed. This
                // flag only affects generateCustomBlocksExportJson
                // (whether to publish this definition project-wide); it
                // never affects local generation, so calls to a private
                // block from elsewhere IN THE SAME object's own workspace
                // are completely unaffected.
                isPrivate: isCustomBlockPrivate(block)
            };
        }
    }
    return defs;
}

// Toggled via the "Keep this block private to this object" / "Share
// this block with other objects" right-click entry blockly_workspace.html
// registers for procedures_defnoreturn/defreturn blocks
// (pygmToggleCustomBlockPrivate). A plain string on block.data rather
// than a dedicated mutator field (Blockly's own "Make a Block" dialog
// has no such checkbox -- that's a scratch-blocks-only fork feature,
// confirmed absent from this vendored plain-Blockly build) -- the
// lowest-risk way to add persistent per-block state without touching
// the vendored procedures_defnoreturn/defreturn block definitions
// themselves (which already manage their OWN mutation-based XML
// serialization; a second, independent field needs no coordination
// with that).
function isCustomBlockPrivate(block) {
    return !!(block && block.data === 'private');
}

function toggleCustomBlockPrivate(block) {
    if (!block) return;
    var wasPrivate = isCustomBlockPrivate(block);
    block.data = wasPrivate ? null : 'private';
    // A plain property write fires no Blockly event by itself (unlike
    // setFieldValue/setCommentText) -- without firing one explicitly,
    // nothing would mark the workspace dirty or re-run generation, so
    // the toggle would silently have no effect until some UNRELATED
    // edit happened to trigger it. Blockly.Events.BlockChange/fire/
    // isEnabled are confirmed real members of the Blockly.Events module
    // object (grep of the vendored source, not assumed -- unlike
    // Blockly.Procedures.flyoutCategory, which turned out NOT to be).
    if (typeof Blockly !== 'undefined' && Blockly.Events && Blockly.Events.isEnabled()) {
        Blockly.Events.fire(new Blockly.Events.BlockChange(
            block, 'data', null, wasPrivate ? 'private' : null, block.data));
    }
}

// Walks an action chain (an event's own DO stack, a custom block's own
// STACK body, or any nested statement input such as if_condition's
// DO/ELSE) into an actions array, expanding any procedures_callnoreturn
// call found anywhere in the chain. This is the ONLY function that ever
// walks a chain of sibling statement blocks in this file -- every nested
// DO/ELSE/sub_actions case in generateActionCodeInner calls this instead
// of looping by hand, so a call nested at any depth is expanded exactly
// like a top-level one.
//
// Also the place HOISTED actions actually land (docs/
// BLOCKLY_SCRATCH_PARITY_PLAN.md's 2026-10-22 follow-up, item 4): a
// side-effecting reporter used inside an action's own parameter value,
// or inside a custom-block call's own argument expression, pushes its
// body's actions into a hoist sink (CURRENT_HOIST_SINK) that this
// function sets up for EACH statement individually and splices in
// immediately before that statement's own result -- "run these actions,
// then use the value" from inside what started as a single expression
// socket, the thing this architecture was previously said to have no
// way to do.
function walkActionChain(startBlock, customBlockDefs, callStack) {
    var actions = [];
    var block = startBlock;
    while (block) {
        if (block.type === 'procedures_callnoreturn') {
            var hoistedForCall = [];
            var previousSinkForCall = CURRENT_HOIST_SINK;
            CURRENT_HOIST_SINK = hoistedForCall;
            var expanded;
            try {
                expanded = expandCustomBlockCall(block, customBlockDefs, callStack);
            } finally {
                CURRENT_HOIST_SINK = previousSinkForCall;
            }
            actions = actions.concat(hoistedForCall).concat(expanded);
        } else {
            var hoisted = [];
            var action = generateActionCode(block, customBlockDefs, callStack, hoisted);
            actions = actions.concat(hoisted);
            if (action) {
                actions.push(action);
            }
        }
        block = block.getNextBlock();
    }
    return actions;
}

function expandCustomBlockCall(callBlock, customBlockDefs, callStack) {
    var name = callBlock.getFieldValue('NAME');
    var def = customBlockDefs[name];

    if (!def) {
        // A call whose definition was deleted/renamed (or never existed,
        // e.g. a corrupted save) -- surfaced as a real, visible
        // unrecognized action (the same amber-highlighted convention
        // events/plugin_loader.extension_for_action already uses for an
        // unknown extension action) rather than silently vanishing.
        return [{action: '__pygm_undefined_custom_block__', parameters: {name: name}}];
    }
    if (callStack.indexOf(name) !== -1) {
        // Direct self-recursion (A calls A) or a longer cycle (A -> B ->
        // A) -- callStack holds every name currently being expanded on
        // the path down to here, so re-entering one is unambiguous proof
        // of a cycle regardless of how long the chain is. Refused with a
        // visible sentinel rather than recursing forever at generation
        // time.
        return [{action: '__pygm_custom_block_cycle_detected__',
                 parameters: {name: name, call_stack: callStack.concat([name]).join(' -> ')}}];
    }
    if (callStack.length >= MAX_CUSTOM_BLOCK_EXPANSION_DEPTH) {
        return [{action: '__pygm_custom_block_too_deeply_nested__', parameters: {name: name}}];
    }

    var argValues = {};
    for (var i = 0; i < def.argNames.length; i++) {
        argValues[def.argNames[i]] = getInputValue(callBlock, 'ARG' + i, '');
    }

    // Mirrored into CURRENT_EXPANSION_STACK (the one tracker shared with
    // the reporter side -- see evaluateCustomBlockReporterCall) so a
    // side-effecting REPORTER encountered while walking this no-return
    // block's own body can correctly detect a cycle back through THIS
    // name too, not just through another reporter -- a real risk only
    // since reporter side-effect hoisting (item 4) started actually
    // walking a reporter's own body instead of refusing it outright.
    var newCallStack = callStack.concat([name]);
    CURRENT_EXPANSION_STACK.push(name);
    var bodyActions;
    try {
        // A local definition has a real bodyBlock to walk; a project-wide
        // SHARED one (mergeSharedCustomBlockDefs) carries null bodyBlock/
        // returnBlock and a pre-resolved bodyActionsTemplate instead --
        // its own nested calls were already expanded when the SOURCE
        // object last exported it (generateCustomBlocksExportJson), so
        // there's nothing further to walk here.
        bodyActions = def.bodyBlock
            ? walkActionChain(def.bodyBlock, customBlockDefs, newCallStack)
            : (def.bodyActionsTemplate || []);
    } finally {
        CURRENT_EXPANSION_STACK.pop();
    }
    return bodyActions.map(function(action) {
        return substituteCustomBlockArgs(action, argValues);
    });
}

// Deep-substitutes every `{{PYGM_ARG:<name>}}` placeholder (see
// getInputValue's 'variables_get' case) inside a generated action's
// parameters with its call-site value. A placeholder can appear
// mid-string (a parameter dropped into a math_arithmetic expression, for
// instance, builds a larger expression string around it), so this is a
// substring replace, not an exact-match swap.
function substituteCustomBlockArgs(value, argValues) {
    if (typeof value === 'string') {
        var result = value;
        for (var name in argValues) {
            var placeholder = '{{PYGM_ARG:' + name + '}}';
            if (result.indexOf(placeholder) !== -1) {
                result = result.split(placeholder).join(String(argValues[name]));
            }
        }
        return result;
    } else if (Array.isArray(value)) {
        return value.map(function(v) { return substituteCustomBlockArgs(v, argValues); });
    } else if (value && typeof value === 'object') {
        var out = {};
        for (var k in value) {
            out[k] = substituteCustomBlockArgs(value[k], argValues);
        }
        return out;
    }
    return value;
}

// Reporter (procedures_defreturn/procedures_callreturn) resolution --
// module-level rather than threaded through getInputValue's ~60 existing
// call sites (see the big comment block above). Set once per generation
// (or export) run by prepareCustomBlockDefsForGeneration, which both
// generatePyGameMakerCode and generateCustomBlocksExportJson call.
//
// CURRENT_EXPANSION_STACK (renamed from CURRENT_REPORTER_CALL_STACK,
// 2026-10-22, item 4) is now shared with the no-return/action side too
// (expandCustomBlockCall mirrors its own pushes into it): a custom-block
// NAME uniquely identifies either a no-return or a reporter definition
// (indexCustomBlockDefs keys both into the SAME dict), so one shared
// "currently expanding" tracker correctly catches every cycle shape --
// R->R, A->A, A->R->A, R->A->R -- not just reporter-to-reporter. That
// cross-mechanism case became real the moment reporter side-effect
// hoisting below started actually walking a reporter's own body instead
// of refusing it outright; before that, a side-effecting reporter's body
// was never touched, so no cycle through it was reachable either.
//
// CURRENT_HOIST_SINK is the array walkActionChain hands to whichever
// single action/call is currently being generated -- evaluateCustomBlock
// ReporterCall pushes a side-effecting reporter's own (argument-
// substituted) body actions onto it instead of refusing them, "running
// the actions, then using the value" from inside what started as one
// expression socket. null when there is no such action-list context to
// hoist into (building another definition's own return-expression
// TEMPLATE at export time) -- the one genuinely remaining case this
// can't resolve, narrowed from "every side-effecting reporter call" to
// just that one.
var CURRENT_CUSTOM_BLOCK_DEFS = {};
var CURRENT_EXPANSION_STACK = [];
var CURRENT_HOIST_SINK = null;

// A procedures_callreturn block dropped into a value socket --
// getInputValue/evaluateValueBlock's own case delegates here. Returns an
// expression string (or defaultValue / a visible placeholder), never an
// action -- a reporter can never appear anywhere but a value socket
// (Blockly's own connection typing: procedures_callreturn is
// setOutput(true), no previous/nextStatement, confirmed against the
// vendored source), so there is no statement-side counterpart to this
// function the way expandCustomBlockCall has one. Side-effecting bodies
// are hoisted into CURRENT_HOIST_SINK as a side effect of this call,
// not returned as part of the expression string.
function evaluateCustomBlockReporterCall(callBlock, defaultValue) {
    var name = callBlock.getFieldValue('NAME');
    var def = CURRENT_CUSTOM_BLOCK_DEFS[name];

    if (!def || !def.isReporter) {
        // Deleted/renamed, or the name now belongs to a no-return block
        // (a callreturn block desynced from its definition) -- visible,
        // non-crashing placeholder, same spirit as
        // __pygm_undefined_custom_block__ on the action side.
        return '{{PYGM_UNDEFINED_REPORTER:' + name + '}}';
    }
    if (CURRENT_EXPANSION_STACK.indexOf(name) !== -1) {
        return '{{PYGM_REPORTER_CYCLE:' + name + '}}';
    }
    if (CURRENT_EXPANSION_STACK.length >= MAX_CUSTOM_BLOCK_EXPANSION_DEPTH) {
        return '{{PYGM_REPORTER_TOO_DEEP:' + name + '}}';
    }
    // A local definition carries a real bodyBlock/returnBlock pair; a
    // project-wide SHARED one (mergeSharedCustomBlockDefs) carries null
    // for both and a pre-resolved returnExprTemplate instead -- "has
    // side-effecting statements" / "has a return expression" are
    // answered from whichever shape this def actually is.
    var hasSideEffectingBody = def.bodyBlock
        ? true
        : !!(def.bodyActionsTemplate && def.bodyActionsTemplate.length);
    if (hasSideEffectingBody && !CURRENT_HOIST_SINK) {
        // No action-list context available to hoist into (e.g. this
        // call is reached while building ANOTHER definition's own
        // return-expression template at export time, not while
        // generating a real action) -- the one case this genuinely
        // can't resolve, narrowed from every side-effecting reporter
        // call to just this one. Flagged rather than silently dropping
        // the side effects or silently treating the call as 0.
        return '{{PYGM_REPORTER_SIDE_EFFECTS:' + name + '}}';
    }
    var hasReturnExpr = def.bodyBlock
        ? !!def.returnBlock
        : (def.returnExprTemplate !== null && def.returnExprTemplate !== undefined);

    var argValues = {};
    for (var i = 0; i < def.argNames.length; i++) {
        argValues[def.argNames[i]] = getInputValue(callBlock, 'ARG' + i, '');
    }

    CURRENT_EXPANSION_STACK.push(name);
    var exprValue;
    try {
        if (hasSideEffectingBody) {
            // Walk (local) or reuse (shared template) the side-effecting
            // body, substitute THIS call's own argument values into it,
            // and push the result onto the active hoist sink -- these
            // actions will run immediately before whatever action is
            // consuming this reporter's return value.
            var rawBodyActions = def.bodyBlock
                ? walkActionChain(def.bodyBlock, CURRENT_CUSTOM_BLOCK_DEFS,
                                   CURRENT_EXPANSION_STACK.slice())
                : (def.bodyActionsTemplate || []);
            var hoistedActions = rawBodyActions.map(function(a) {
                return substituteCustomBlockArgs(a, argValues);
            });
            for (var h = 0; h < hoistedActions.length; h++) {
                CURRENT_HOIST_SINK.push(hoistedActions[h]);
            }
        }
        if (!hasReturnExpr) {
            // An empty RETURN socket -- Blockly's own procedures_ifreturn
            // warning mechanism already flags this on the definition
            // block itself (PROCEDURES_IFRETURN_WARNING); nothing more
            // useful to produce on the call side than the caller's own
            // default.
            exprValue = defaultValue;
        } else {
            exprValue = def.bodyBlock
                ? evaluateValueBlock(def.returnBlock, defaultValue)
                : def.returnExprTemplate;
        }
    } finally {
        CURRENT_EXPANSION_STACK.pop();
    }

    return substituteCustomBlockArgs(exprValue, argValues);
}

// docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B4: draw_health_bar models x2/y2 as
// x1+width/y1+20 rather than storing them directly, computed with a plain JS
// `+`. That silently did STRING CONCATENATION the moment x1/y1 became an
// authored expression instead of always being a number (e.g. "self.x" + 100
// -> "self.x100", not a usable expression) -- a direct consequence of this
// same fix making a non-numeric X/Y possible at all. Real arithmetic when
// both sides are genuinely numbers (preserves the exact prior behavior);
// otherwise builds an expression string ActionExecutor._evaluate_expression
// can evaluate at runtime.
function addExpr(a, b) {
    if (typeof a === 'number' && typeof b === 'number') return a + b;
    return '(' + a + ') + (' + b + ')';
}

// parseScopedVariable: split a 'scope.name' user-typed variable expression
// into the (scope, name) pair the runtime's set_variable / test_variable
// actions expect. Accepted prefixes: 'self.' (or 'sel.'), 'global.', 'other.'.
// A bare name defaults to instance scope ("sel"), the runtime default.
function parseScopedVariable(raw) {
    var name = (raw || '').trim();
    var scope = 'sel';
    var dotIdx = name.indexOf('.');
    if (dotIdx > 0) {
        var prefix = name.substring(0, dotIdx).toLowerCase();
        var rest = name.substring(dotIdx + 1);
        if (prefix === 'self' || prefix === 'sel') { scope = 'sel'; name = rest; }
        else if (prefix === 'global') { scope = 'global'; name = rest; }
        else if (prefix === 'other')  { scope = 'other';  name = rest; }
    }
    return {name: name, scope: scope};
}

// hoistedOut: an array (walkActionChain's own, freshly created per
// statement) that any side-effecting reporter used inside THIS block's
// own parameter values pushes its hoisted body actions into (docs/
// BLOCKLY_SCRATCH_PARITY_PLAN.md's 2026-10-22 follow-up, item 4) --
// exposed to the deeply-nested getInputValue/evaluateCustomBlockReporter
// Call call chain via the module-level CURRENT_HOIST_SINK mirror (not
// threaded as a parameter through those ~60 call sites, same reasoning
// as CURRENT_CUSTOM_BLOCK_DEFS/CURRENT_EXPANSION_STACK above), saved and
// restored here so a NESTED generateActionCode call (e.g. for an
// if_condition's own DO/ELSE statements, triggered while THIS call's own
// generateActionCodeInner is still running) can't leak its own sink into
// this one's later field evaluations.
function generateActionCode(block, customBlockDefs, callStack, hoistedOut) {
    var previousSink = CURRENT_HOIST_SINK;
    CURRENT_HOIST_SINK = hoistedOut || [];
    var result;
    try {
        result = generateActionCodeInner(block, customBlockDefs, callStack);
        // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B5: merge back whatever the
        // LOAD side (createActionBlock, blockly_workspace.html) saw but this
        // block's own case below never mentions -- translations, an "applies
        // to" target, a colour, anything the hand-written block simply has no
        // field for. Keys the case DID explicitly set always win (the merge
        // order below puts them on top), since those reflect the block's real
        // current state, not the stale original.
        if (result && result.parameters && block.pygmExtraParams) {
            var merged = {};
            for (var k in block.pygmExtraParams) merged[k] = block.pygmExtraParams[k];
            for (var k2 in result.parameters) merged[k2] = result.parameters[k2];
            result.parameters = merged;
        }
    } finally {
        CURRENT_HOIST_SINK = previousSink;
    }
    return result;
}

function generateActionCodeInner(block, customBlockDefs, callStack) {
    switch (block.type) {
        case 'move_set_hspeed':
            return {action: 'set_hspeed', parameters: {value: getInputValue(block, 'SPEED', 0)}};
        case 'move_set_vspeed':
            return {action: 'set_vspeed', parameters: {value: getInputValue(block, 'SPEED', 0)}};
        case 'move_stop':
            return {action: 'stop_movement', parameters: {}};
        case 'move_direction':
            // Audit B13: a 3x3 grid -- several ticks = the runtime picks one
            // at random each time (a patrol). A single direction saves as
            // before (an angle, or "stop" -- B5: stop is a real sentinel, not
            // "move right"); nothing ticked is "stop" too (the runtime treats
            // an empty list the same way).
            var speed = getInputValue(block, 'SPEED', 4);
            var picked = MOVE_DIRECTION_FIELDS.filter(function(f) {
                return block.getFieldValue(f[0]) === 'TRUE';
            }).map(function(f) { return f[1]; });
            var directions;
            if (picked.length === 0 || (picked.length === 1 && picked[0] === 'stop')) {
                directions = 'stop';
            } else if (picked.length === 1) {
                directions = DIRECTION_DEGREES[picked[0]];
            } else {
                directions = picked;
            }
            var directionExpr = block.getFieldValue('DIRECTION_EXPR') || '';
            return {action: 'start_moving_direction', parameters: {directions: directions, direction_expr: directionExpr, speed: speed}};
        case 'move_towards':
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B7: the block existed with
            // no generator, so it saved nothing at all.
            return {action: 'move_towards_point', parameters: {
                x: getInputValue(block, 'X', 0),
                y: getInputValue(block, 'Y', 0),
                speed: getInputValue(block, 'SPEED', 4)
            }};
        case 'move_free':
            return {action: 'move_free', parameters: {
                direction: getInputValue(block, 'DIRECTION', 0),
                speed: getInputValue(block, 'SPEED', 4)
            }};
        case 'set_speed':
            return {action: 'set_speed', parameters: {speed: getInputValue(block, 'SPEED', 0)}};
        case 'set_direction':
            return {action: 'set_direction', parameters: {direction: getInputValue(block, 'DIRECTION', 0)}};
        case 'move_snap_to_grid':
            return {action: 'snap_to_grid', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'grid_move':
            return {action: 'move_grid', parameters: {direction: block.getFieldValue('DIRECTION') || 'right', grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'move_jump_to':
            var relative = block.getFieldValue('RELATIVE') === 'TRUE';
            return {action: 'jump_to_position', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0), relative: relative}};
        case 'grid_stop_if_no_keys':
            return {action: 'stop_if_no_keys', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'grid_check_keys_and_move':
            return {action: 'check_keys_and_move', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32), speed: getInputValue(block, 'SPEED', 4)}};
        case 'grid_if_on_grid':
            // This is a wrapper action - collect inner actions (via
            // walkActionChain so a custom-block call nested here expands
            // instead of being refused -- see the big comment above
            // walkActionChain/expandCustomBlockCall).
            var innerActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'if_on_grid', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32), then_actions: innerActions}};
        case 'score_set':
            return {action: 'set_score', parameters: {value: getInputValue(block, 'VALUE', 0), relative: false}};
        case 'score_add':
            return {action: 'set_score', parameters: {value: getInputValue(block, 'VALUE', 0), relative: true}};
        case 'lives_set':
            return {action: 'set_lives', parameters: {value: getInputValue(block, 'VALUE', 0), relative: false}};
        case 'lives_add':
            return {action: 'set_lives', parameters: {value: getInputValue(block, 'VALUE', 0), relative: true}};
        case 'health_set':
            return {action: 'set_health', parameters: {value: getInputValue(block, 'VALUE', 0), relative: false}};
        case 'health_add':
            return {action: 'set_health', parameters: {value: getInputValue(block, 'VALUE', 0), relative: true}};
        case 'draw_score':
            return {action: 'draw_score', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0), caption: "Score: "}};
        case 'draw_lives':
            return {action: 'draw_lives', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0)}};
        case 'draw_health_bar':
            var hbX = getInputValue(block, 'X', 0);
            var hbY = getInputValue(block, 'Y', 0);
            return {action: 'draw_health_bar', parameters: {
                x1: hbX, y1: hbY,
                x2: addExpr(hbX, getInputValue(block, 'WIDTH', 100)),
                y2: addExpr(hbY, getInputValue(block, 'HEIGHT', 20))}};
        case 'instance_destroy':
            return {action: 'destroy_instance', parameters: {target: 'self'}};
        case 'instance_destroy_other':
            return {action: 'destroy_instance', parameters: {target: 'other'}};
        case 'instance_destroy_object':
            return {action: 'destroy_instance', parameters: {
                target: 'object', target_object: block.getFieldValue('OBJECT')}};
        case 'instance_create':
            // Bug fix: this case was missing entirely, so every "Create
            // instance of X at x: ... y: ..." block silently produced no
            // action at all (generateBlockCode's switch fell through to
            // default: return null) -- e.g. Tutorial 2's star spawner
            // alarm event re-armed itself every frame but never actually
            // created a star. OBJECT is a plain typed FieldTextInput, not
            // a dropdown (see the block definition in blockly_blocks.js).
            return {action: 'create_instance', parameters: {
                object: block.getFieldValue('OBJECT'),
                x: getInputValue(block, 'X', 0),
                y: getInputValue(block, 'Y', 0)
            }};
        case 'exit_event':
            return {action: 'exit_event', parameters: {}};
        case 'if_condition':
            // Collect nested actions from the DO/ELSE slots (common to every
            // condition_type), then the fields for whichever type is
            // selected -- see blockly_blocks.js for the 8 types and why.
            // walkActionChain (not a raw while-loop) so a custom-block call
            // nested in either branch expands correctly.
            var ifCondActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            var ifCondElseActions = walkActionChain(block.getInputTargetBlock('ELSE'), customBlockDefs, callStack);
            var ifCondType = block.getFieldValue('CONDITION_TYPE');
            var ifCondParams = {
                condition_type: ifCondType,
                then_actions: ifCondActions,
                else_actions: ifCondElseActions
            };
            if (ifCondType === 'variable_compare') {
                ifCondParams.variable = block.getFieldValue('VAR_NAME');
                ifCondParams.operator = block.getFieldValue('VAR_OPERATOR');
                ifCondParams.value = block.getFieldValue('VAR_VALUE');
            } else if (ifCondType === 'position_check') {
                ifCondParams.check_type = block.getFieldValue('POS_CHECK_TYPE');
                ifCondParams.operator = block.getFieldValue('POS_OPERATOR');
                ifCondParams.value = block.getFieldValue('POS_VALUE');
            } else if (ifCondType === 'collision_check') {
                ifCondParams.object = block.getFieldValue('COLLISION_OBJECT');
                ifCondParams.offset_x = block.getFieldValue('COLLISION_OFFSET_X');
                ifCondParams.offset_y = block.getFieldValue('COLLISION_OFFSET_Y');
            } else if (ifCondType === 'key_pressed') {
                ifCondParams.key = block.getFieldValue('KEY_CHECK');
            } else if (ifCondType === 'mouse_check') {
                ifCondParams.check = block.getFieldValue('MOUSE_CHECK_FIELD');
            } else if (ifCondType === 'random_chance') {
                ifCondParams.chance = block.getFieldValue('CHANCE');
            } else if (ifCondType === 'expression') {
                ifCondParams.expression = block.getFieldValue('EXPRESSION');
            } else {
                // instance_count (and any unrecognized future type)
                ifCondParams.object_name = block.getFieldValue('OBJECT_NAME');
                ifCondParams.operator = block.getFieldValue('OPERATOR');
                ifCondParams.value = block.getFieldValue('VALUE');
            }
            return {action: 'if_condition', parameters: ifCondParams};
        case 'set_variable':
            // Split a leading 'self.' / 'global.' / 'other.' prefix into the
            // separate `scope` parameter the runtime expects. A bare name
            // defaults to instance scope ("sel"), matching the executor's default.
            var sv = parseScopedVariable(block.getFieldValue('VARIABLE'));
            return {action: 'set_variable', parameters: {
                variable: sv.name,
                scope: sv.scope,
                value: getInputValue(block, 'VALUE', 0),
                relative: false
            }};
        case 'test_variable':
            // Same nested-action pattern as if_condition: collect DO/ELSE
            // slot statements (via walkActionChain, so a nested custom-block
            // call expands) and let the runtime branch.
            var tvActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            var tvElseActions = walkActionChain(block.getInputTargetBlock('ELSE'), customBlockDefs, callStack);
            var tv = parseScopedVariable(block.getFieldValue('VARIABLE'));
            return {action: 'test_variable', parameters: {
                variable: tv.name,
                scope: tv.scope,
                operation: block.getFieldValue('OPERATION'),
                value: getInputValue(block, 'VALUE', 0),
                then_actions: tvActions,
                else_actions: tvElseActions
            }};
        case 'test_expression':
            return {action: 'test_expression', parameters: {
                expression: getConditionValue(block, 'CONDITION'),
                then_actions: collectStatementActions(block, 'DO', customBlockDefs, callStack),
                else_actions: collectStatementActions(block, 'ELSE', customBlockDefs, callStack)
            }};
        case 'room_goto_next':
            return {action: 'next_room', parameters: {}};
        case 'room_goto_previous':
            return {action: 'previous_room', parameters: {}};
        case 'room_restart':
            return {action: 'restart_room', parameters: {}};
        case 'room_goto':
            // Parameter key MUST be "room", not "room_name" -- matches
            // events/action_types.py's goto_room ActionType schema (the
            // canonical parameter name every other caller uses) and the
            // LOADER case right below for this same block type
            // (createActionBlock: `if (params.room) block.setFieldValue(...)`
            // -- it already read "room", not "room_name"). The runtime
            // handler (execute_goto_room_action, runtime/action_room.py)
            // also reads parameters.get("room", ""), so a "room_name" key
            // was never read by anything: this made every Blockly-authored
            // "Go to room" block a silent, permanent no-op regardless of
            // which room was selected (real classroom report, 2026-10-12:
            // "the go to different room action does not work").
            return {action: 'goto_room', parameters: {room: block.getFieldValue('ROOM')}};
        case 'room_if_next_exists':
            var nextExistsActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            var nextExistsElseActions = walkActionChain(block.getInputTargetBlock('ELSE'), customBlockDefs, callStack);
            return {action: 'if_next_room_exists', parameters: {
                then_actions: nextExistsActions, else_actions: nextExistsElseActions
            }};
        case 'room_if_previous_exists':
            var prevExistsActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            var prevExistsElseActions = walkActionChain(block.getInputTargetBlock('ELSE'), customBlockDefs, callStack);
            return {action: 'if_previous_room_exists', parameters: {
                then_actions: prevExistsActions, else_actions: prevExistsElseActions
            }};
        case 'sound_play':
            return {action: 'play_sound', parameters: {sound: block.getFieldValue('SOUND')}};
        case 'music_play':
            return {action: 'play_music', parameters: {music: block.getFieldValue('MUSIC')}};
        case 'music_stop':
            return {action: 'stop_music', parameters: {}};
        case 'output_message':
            return {action: 'show_message', parameters: {message: getInputValue(block, 'MESSAGE', '')}};
        case 'set_alarm':
            return {action: 'set_alarm', parameters: {alarm_number: parseInt(block.getFieldValue('ALARM_NUM')), steps: getInputValue(block, 'STEPS', 30)}};
        case 'draw_text':
            return {action: 'draw_text', parameters: {text: getInputValue(block, 'TEXT', ''), x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0)}};
        case 'draw_rectangle':
            return {action: 'draw_rectangle', parameters: {x1: getInputValue(block, 'X', 0), y1: getInputValue(block, 'Y', 0), x2: getInputValue(block, 'X', 0) + getInputValue(block, 'WIDTH', 100), y2: getInputValue(block, 'Y', 0) + getInputValue(block, 'HEIGHT', 100), color: getInputValue(block, 'COLOR', 'white')}};
        case 'draw_circle':
            return {action: 'draw_circle', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0), radius: getInputValue(block, 'RADIUS', 50), color: getInputValue(block, 'COLOR', 'white')}};
        case 'set_sprite':
            var spriteMode = block.getFieldValue('SPRITE_MODE');
            var spriteName = (spriteMode === '<self>') ? '<self>' : block.getFieldValue('SPRITE');
            return {action: 'set_sprite', parameters: {
                sprite: spriteName,
                subimage: getInputValue(block, 'SUBIMAGE', -1),
                speed: getInputValue(block, 'SPEED', -1)
            }};
        case 'set_alpha':
            return {action: 'set_alpha', parameters: {alpha: getInputValue(block, 'ALPHA', 1.0)}};
        case 'set_gravity':
            return {action: 'set_gravity', parameters: {direction: getInputValue(block, 'DIRECTION', 270), gravity: getInputValue(block, 'STRENGTH', 0.5)}};
        case 'set_friction':
            return {action: 'set_friction', parameters: {friction: getInputValue(block, 'FRICTION', 0)}};
        case 'reverse_horizontal':
            return {action: 'reverse_horizontal', parameters: {}};
        case 'reverse_vertical':
            return {action: 'reverse_vertical', parameters: {}};
        case 'wrap_around_room':
            return {action: 'wrap_around_room', parameters: {
                horizontal: block.getFieldValue('HORIZONTAL') === 'TRUE',
                vertical: block.getFieldValue('VERTICAL') === 'TRUE'
            }};
        case 'if_can_push':
            return {action: 'if_can_push', parameters: {
                direction: block.getFieldValue('DIRECTION') || 'facing',
                object_type: block.getFieldValue('OBJECT_TYPE') || 'box',
                then_action: block.getFieldValue('THEN_ACTION') || 'push_and_move',
                else_action: block.getFieldValue('ELSE_ACTION') || 'stop_movement'
            }};
        case 'execute_code':
            return {action: 'execute_code', parameters: {code: block.getFieldValue('CODE') || ''}};

        // ============================================================================
        // THYMIO MOTOR ACTIONS
        // ============================================================================
        case 'thymio_set_motor_speed':
            return {action: 'thymio_set_motor_speed', parameters: {
                left_speed: getInputValue(block, 'LEFT_SPEED', 0),
                right_speed: getInputValue(block, 'RIGHT_SPEED', 0)
            }};
        case 'thymio_move_forward':
            return {action: 'thymio_move_forward', parameters: {speed: getInputValue(block, 'SPEED', 200)}};
        case 'thymio_move_backward':
            return {action: 'thymio_move_backward', parameters: {speed: getInputValue(block, 'SPEED', 200)}};
        case 'thymio_turn_left':
            return {action: 'thymio_turn_left', parameters: {speed: getInputValue(block, 'SPEED', 300)}};
        case 'thymio_turn_right':
            return {action: 'thymio_turn_right', parameters: {speed: getInputValue(block, 'SPEED', 300)}};
        case 'thymio_stop_motors':
            return {action: 'thymio_stop_motors', parameters: {}};

        // ============================================================================
        // THYMIO LED ACTIONS
        // ============================================================================
        case 'thymio_set_led_top':
            return {action: 'thymio_set_led_top', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_bottom_left':
            return {action: 'thymio_set_led_bottom_left', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_bottom_right':
            return {action: 'thymio_set_led_bottom_right', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_circle':
            return {action: 'thymio_set_led_circle', parameters: {
                led_index: parseInt(block.getFieldValue('LED_INDEX')),
                intensity: getInputValue(block, 'INTENSITY', 32)
            }};
        case 'thymio_set_led_circle_all':
            return {action: 'thymio_set_led_circle_all', parameters: {
                led0: getInputValue(block, 'LED0', 0),
                led1: getInputValue(block, 'LED1', 0),
                led2: getInputValue(block, 'LED2', 0),
                led3: getInputValue(block, 'LED3', 0),
                led4: getInputValue(block, 'LED4', 0),
                led5: getInputValue(block, 'LED5', 0),
                led6: getInputValue(block, 'LED6', 0),
                led7: getInputValue(block, 'LED7', 0)
            }};
        case 'thymio_leds_off':
            return {action: 'thymio_leds_off', parameters: {}};

        // ============================================================================
        // THYMIO SOUND ACTIONS
        // ============================================================================
        case 'thymio_play_tone':
            return {action: 'thymio_play_tone', parameters: {
                frequency: getInputValue(block, 'FREQUENCY', 440),
                duration: getInputValue(block, 'DURATION', 60)
            }};
        case 'thymio_play_system_sound':
            return {action: 'thymio_play_system_sound', parameters: {
                sound_id: parseInt(block.getFieldValue('SOUND_ID'))
            }};
        case 'thymio_stop_sound':
            return {action: 'thymio_stop_sound', parameters: {}};

        // ============================================================================
        // THYMIO SENSOR READING ACTIONS
        // ============================================================================
        case 'thymio_read_proximity':
            return {action: 'thymio_read_proximity', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                variable: block.getFieldValue('VARIABLE')
            }};
        case 'thymio_read_ground':
            return {action: 'thymio_read_ground', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                variable: block.getFieldValue('VARIABLE')
            }};
        case 'thymio_read_button':
            return {action: 'thymio_read_button', parameters: {
                button: block.getFieldValue('BUTTON'),
                variable: block.getFieldValue('VARIABLE')
            }};

        // ============================================================================
        // THYMIO CONDITION ACTIONS (with sub_actions)
        // ============================================================================
        case 'thymio_if_proximity':
            var proxSubActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'thymio_if_proximity', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                comparison: block.getFieldValue('COMPARISON'),
                threshold: getInputValue(block, 'THRESHOLD', 2000)
            }, sub_actions: proxSubActions};

        case 'thymio_if_ground_dark':
            var groundDarkSubActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'thymio_if_ground_dark', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                threshold: getInputValue(block, 'THRESHOLD', 300)
            }, sub_actions: groundDarkSubActions};

        case 'thymio_if_ground_light':
            var groundLightSubActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'thymio_if_ground_light', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                threshold: getInputValue(block, 'THRESHOLD', 300)
            }, sub_actions: groundLightSubActions};

        case 'thymio_if_button_pressed':
            var btnPressSubActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'thymio_if_button_pressed', parameters: {
                button: block.getFieldValue('BUTTON')
            }, sub_actions: btnPressSubActions};

        case 'thymio_if_button_released':
            var btnRelSubActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'thymio_if_button_released', parameters: {
                button: block.getFieldValue('BUTTON')
            }, sub_actions: btnRelSubActions};

        case 'thymio_if_variable':
            var varSubActions = walkActionChain(block.getInputTargetBlock('DO'), customBlockDefs, callStack);
            return {action: 'thymio_if_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                comparison: block.getFieldValue('COMPARISON'),
                value: getInputValue(block, 'VALUE', 0)
            }, sub_actions: varSubActions};

        // ============================================================================
        // THYMIO TIMING ACTIONS
        // ============================================================================
        case 'thymio_set_timer_period':
            return {action: 'thymio_set_timer_period', parameters: {
                timer_id: parseInt(block.getFieldValue('TIMER_ID')),
                period: getInputValue(block, 'PERIOD', 1000)
            }};

        // ============================================================================
        // THYMIO VARIABLE ACTIONS
        // ============================================================================
        case 'thymio_set_variable':
            return {action: 'thymio_set_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                value: getInputValue(block, 'VALUE', 0)
            }};
        case 'thymio_increase_variable':
            return {action: 'thymio_increase_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                amount: getInputValue(block, 'AMOUNT', 1)
            }};
        case 'thymio_decrease_variable':
            return {action: 'thymio_decrease_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                amount: getInputValue(block, 'AMOUNT', 1)
            }};

        // ============================================================================
        // CUSTOM BLOCKS ("My Blocks") -- docs/BLOCKLY_SCRATCH_PARITY_PLAN.md
        // Feature 2. A procedures_callnoreturn is normally intercepted by
        // walkActionChain BEFORE generateActionCode is ever called on it --
        // every statement-chain position in this file (an event's own DO
        // stack, a custom block's own STACK body, and every nested DO/ELSE/
        // sub_actions branch) walks through that function now, so a call
        // anywhere is always properly expanded. This case is reached only
        // if some future statement-chain site is added without routing
        // through walkActionChain -- a code-path bug, not a normal
        // authoring scenario -- so it's a defensive fallback, not live
        // behaviour: surfaced visibly rather than silently producing
        // nothing if it somehow happens.
        case 'procedures_callnoreturn':
            return {action: '__pygm_custom_block_call_not_expanded__',
                    parameters: {name: block.getFieldValue('NAME')}};
        // A reporter call (procedures_callreturn) is output-type (Blockly's
        // own connection checking: setOutput(true), no previous/
        // nextStatement -- confirmed against the vendored source) and so
        // can never be dragged into a statement slot in the first place;
        // reached only if that invariant is ever violated.
        case 'procedures_callreturn':
            return {action: '__pygm_custom_block_call_not_expanded__',
                    parameters: {name: block.getFieldValue('NAME')}};
        // A definition hat dragged somewhere it can't act as a top-level
        // workspace block (e.g. plugged into a statement input) -- not a
        // real authoring path Blockly's own connection-checking should
        // ever allow, but surfaced rather than silently producing nothing
        // if it somehow happens. Covers both the no-return and reporter
        // definition hats.
        case 'procedures_defnoreturn':
        case 'procedures_defreturn':
            return {action: '__pygm_custom_block_definition_misplaced__',
                    parameters: {name: block.getFieldValue('NAME')}};

        default:
            return null;
    }
}

// Value blocks -> expression text (see getInputValue). Shared with the
// loader (blockly_workspace.html's connectNumberBlock), which turns these
// exact texts back into the same blocks.
var VALUE_BLOCK_EXPRESSIONS = {
    'value_x': 'self.x',
    'value_y': 'self.y',
    'value_hspeed': 'self.hspeed',
    'value_vspeed': 'self.vspeed',
    'value_mouse_x': 'self.mouse_x',
    'value_mouse_y': 'self.mouse_y',
    'value_score': 'score',
    'value_lives': 'lives',
    'value_health': 'health'
};

// Blockly's math_arithmetic OP field -> operator text. "**" (power) is
// valid on all three engines (Python eval on desktop/Kivy, JS on HTML5).
var MATH_ARITHMETIC_OPS = {
    'ADD': '+', 'MINUS': '-', 'MULTIPLY': '*', 'DIVIDE': '/', 'POWER': '**'
};

// The actions stacked in a statement input (DO / ELSE) -- a thin
// (block, inputName)-ergonomic wrapper around walkActionChain, which
// every other nested DO/ELSE/sub_actions site in this file calls
// directly on an already-resolved start block instead.
function collectStatementActions(block, inputName, customBlockDefs, callStack) {
    return walkActionChain(block.getInputTargetBlock(inputName), customBlockDefs, callStack);
}

// Blockly logic block -> Python-syntax condition text (audit B6c). Desktop's
// _eval_bool_expression evaluates it, HTML5's gmExpressionValue converts
// and/or/not/True/False, and Kivy emits it as Python. A number/value block
// is used as-is (non-zero = true), a text block verbatim (an authored
// expression), an empty slot is False.
var LOGIC_COMPARE_OPS = {'EQ': '==', 'NEQ': '!=', 'LT': '<', 'LTE': '<=', 'GT': '>', 'GTE': '>='};

function getConditionValue(block, inputName) {
    var input = block.getInputTargetBlock(inputName);
    if (!input) return 'False';
    switch (input.type) {
        case 'logic_boolean':
            return input.getFieldValue('BOOL') === 'TRUE' ? 'True' : 'False';
        case 'logic_negate':
            return '(not ' + getConditionValue(input, 'BOOL') + ')';
        case 'logic_operation':
            var join = input.getFieldValue('OP') === 'OR' ? ' or ' : ' and ';
            return '(' + getConditionValue(input, 'A') + join + getConditionValue(input, 'B') + ')';
        case 'logic_compare':
            var op = LOGIC_COMPARE_OPS[input.getFieldValue('OP')] || '==';
            return '(' + getConditionOperand(input, 'A') + ' ' + op + ' ' + getConditionOperand(input, 'B') + ')';
        case 'text':
            var text = input.getFieldValue('TEXT');
            return (text === null || text === undefined || text.trim() === '') ? 'False' : text;
        default:
            return String(getInputValue(block, inputName, 0));
    }
}

// A comparison side: a nested logic block compares as its truth value,
// anything else as the number/value expression getInputValue gives.
function getConditionOperand(block, inputName) {
    var input = block.getInputTargetBlock(inputName);
    if (input && /^logic_/.test(input.type)) return getConditionValue(block, inputName);
    return String(getInputValue(block, inputName, 0));
}

// move_direction's 3x3 grid (audit B13): checkbox field -> direction name,
// in GameMaker's grid order (centre = stop), plus each name's angle.
var MOVE_DIRECTION_FIELDS = [
    ['DIR_UL', 'up-left'], ['DIR_U', 'up'], ['DIR_UR', 'up-right'],
    ['DIR_L', 'left'], ['DIR_STOP', 'stop'], ['DIR_R', 'right'],
    ['DIR_DL', 'down-left'], ['DIR_D', 'down'], ['DIR_DR', 'down-right']
];
var DIRECTION_DEGREES = {
    'right': 0, 'up-right': 45, 'up': 90, 'up-left': 135, 'left': 180,
    'down-left': 225, 'down': 270, 'down-right': 315
};

// Blockly's math_single OP field -> expression template ("%" = argument).
var MATH_SINGLE_TEMPLATES = {
    'ROOT': 'sqrt(%)', 'ABS': 'abs(%)', 'NEG': '(-(%))',
    'LN': 'ln(%)', 'LOG10': 'log10(%)', 'EXP': 'exp(%)', 'POW10': '(10 ** (%))'
};

// getInputValue resolves a named value socket on `block`; evaluateValueBlock
// does the actual work given the already-resolved target block directly --
// factored apart so evaluateCustomBlockReporterCall can evaluate a
// reporter definition's own RETURN block (captured once at index time,
// not reached via any parent's named input) through the exact same logic.
function getInputValue(block, inputName, defaultValue) {
    return evaluateValueBlock(block.getInputTargetBlock(inputName), defaultValue);
}

function evaluateValueBlock(input, defaultValue) {
    if (input) {
        if (input.type === 'math_number') {
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B1: `|| defaultValue`
            // treats 0 (and NaN/empty) alike, so typing 0 saved the block's
            // DEFAULT instead -- "set gravity 0" silently saved 0.5 (gravity
            // turned ON), "set sprite subimage 0" saved -1. Only fall back
            // to defaultValue when the field genuinely isn't a number.
            var num = parseFloat(input.getFieldValue('NUM'));
            return isNaN(num) ? defaultValue : num;
        } else if (input.type === 'text') {
            // Same pattern as above, applied to the empty string -- no
            // currently-registered caller passes a non-'' default for a
            // text field, so this has no observable effect yet, but it's
            // the identical bug shape and a future caller would hit it.
            var text = input.getFieldValue('TEXT');
            return (text === null || text === undefined) ? defaultValue : text;
        } else if (input.type === 'variables_get') {
            // A custom block's own parameter reporter, dropped into a
            // value socket inside the definition's body (docs/
            // BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 2) -- the ONLY way a
            // variables_get block can appear anywhere in this app, since
            // nothing else registers Blockly's generic variable blocks.
            // Resolved to a placeholder substituteCustomBlockArgs replaces
            // with the real call-site value when the enclosing definition
            // is expanded; a reporter encountered OUTSIDE any expansion
            // (variables_get's field value is a variable ID per the
            // vendored source's own getVariableById(id).getName() pattern,
            // not the name directly) still degrades to a visible,
            // non-crashing placeholder string rather than silently
            // vanishing if the ID never resolves.
            var varId = input.getFieldValue('VAR');
            var varName = varId;
            try {
                if (input.workspace && typeof input.workspace.getVariableById === 'function') {
                    var varModel = input.workspace.getVariableById(varId);
                    if (varModel) {
                        if (typeof varModel.getName === 'function') {
                            varName = varModel.getName();
                        } else if (varModel.name) {
                            varName = varModel.name;
                        }
                    }
                }
            } catch (e) { /* fall back to the raw field value */ }
            return '{{PYGM_ARG:' + varName + '}}';
        } else if (input.type === 'procedures_callreturn') {
            // A reporter-style custom block call dropped into a value
            // socket (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md Feature 2,
            // deferred item 4) -- see evaluateCustomBlockReporterCall's
            // own comment for what this does and does not support.
            return evaluateCustomBlockReporterCall(input, defaultValue);
        } else if (VALUE_BLOCK_EXPRESSIONS[input.type]) {
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B6a/B15: spellings every
            // engine evaluates (desktop _parse_value, HTML5 gmExpressionValue
            // via parseNumParam, Kivy _num_code). "game.score" -- the old
            // spelling -- only ever worked nowhere on desktop.
            return VALUE_BLOCK_EXPRESSIONS[input.type];
        } else if (input.type === 'math_arithmetic') {
            var op = MATH_ARITHMETIC_OPS[input.getFieldValue('OP')] || '+';
            return '(' + getInputValue(input, 'A', 0) + ' ' + op + ' ' + getInputValue(input, 'B', 0) + ')';
        } else if (input.type === 'math_single') {
            // B6b: every op maps to a function all three engines provide
            // (runtime/gm_math.py, engine.js gmSafeMath, Kivy GameObject).
            var arg = getInputValue(input, 'NUM', 0);
            var tmpl = MATH_SINGLE_TEMPLATES[input.getFieldValue('OP')] || 'abs(%)';
            return tmpl.replace('%', arg);
        } else if (input.type === 'math_random_int') {
            // Blockly's standard Math category block ("random integer from
            // %1 to %2", FROM/TO value inputs) -- used by Tutorial 2's star
            // spawner to pick a random x. The three runtime engines (desktop
            // Python, HTML5, Kivy) only implement single-argument irandom(n)
            // (0..n inclusive), not a two-argument range function, so this
            // is synthesized from it rather than emitting a call to a
            // two-argument range function no target implements:
            // irandom(b-a)+a covers [a, b] inclusive, matching
            // math_random_int's own semantics exactly.
            var rangeFrom = getInputValue(input, 'FROM', 0);
            var rangeTo = getInputValue(input, 'TO', 0);
            return 'irandom((' + rangeTo + ') - (' + rangeFrom + ')) + (' + rangeFrom + ')';
        }
    }
    return defaultValue;
}

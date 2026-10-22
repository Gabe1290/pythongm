# Blockly Scratch-parity plan: fewer categories + student-defined blocks

Status: Written 2026-10-18. **Both features shipped 2026-10-21** (see
their own sections below for what landed, what was deliberately scoped
narrower, and what's deferred). The plan's whole code-level scope is
done; what's left is the "needs human eyes" verification flagged in
Feature 2's own section, and the explicitly-deferred follow-ups each
section lists.

Two separate features, sequenced so the second lands into the shape the
first produces:

1. ✅ Reduce the Blockly toolbox's category count toward Scratch's model — DONE.
2. ✅ Let a student define their own reusable block ("My Blocks") — DONE, narrower v1 scope (see below).

Both are scoped for the existing desktop IDE editor (`editors/
object_editor/blockly_widget.py` + `blockly_workspace.html`). Neither
touches the runtime or either export target (HTML5/Kivy) — see each
feature's own "why no engine changes" note below; that's a load-bearing
design choice, not an oversight.

---

## Open decision — resolved 2026-10-21

"Reduce the number of categories to one like for Scratch" was confirmed
to mean Scratch's small category *count* (the screenshot's ~9), not a
literal single category — the proposed mapping was accepted as written,
with one change: `Score/Lives/Health` merges into `Variables` rather
than staying its own category.

---

## Feature 1: fewer, Scratch-sized categories — ✅ DONE 2026-10-21

**Confirmed by the user:** "reduce to one like for Scratch" meant
Scratch's small category *count*, the proposed mapping is accepted as
written, and `Score/Lives/Health` merges into `Variables` (not kept as
its own 10th category, resolving the one open question this plan left).

Shipped exactly the "presentation-only grouping layer" design below:
- `config/blockly_config.py`'s `TOOLBOX_CATEGORY_GROUPS` +
  `display_category()` — the canonical mapping. Every other
  category-keyed mechanism (presets' `enabled_categories`,
  `action_types.py`'s `category=`, `register_block_categories`)
  confirmed unchanged.
- `blockly_workspace.html`'s hand-mirrored JS copy
  (`TOOLBOX_CATEGORY_GROUPS`/`toolboxGroupOf()`), consulted by
  `generateToolboxXml()` — the function now pools each fine-grained
  category's already-filtered blocks into a `groupBuckets` accumulator
  via `pushToGroup()` instead of emitting a `<category>` tag
  immediately, then emits one tag per group at the end, in a fixed
  `TOOLBOX_GROUP_ORDER` (Motion/Looks/Sound/Events/Control/Sensing/
  Operators/Variables, Scratch's own order) so the toolbox reads the
  same way every time. The always-on Math/Logic/Text categories pool
  into `Operators` the same way. A category absent from the mapping
  (an extension's own, e.g. Thymio's 8) falls through to its own
  standalone group unchanged, appended after the fixed 8.
- A 9-color palette (`TOOLBOX_GROUP_COLORS`) loosely following Scratch's
  own category colors; a dynamically-generated block's own body color
  (`registerCustomBlocks`) now prefers its group's color too, for visual
  consistency between a block and the drawer it lives in.
- `editors/object_editor/blockly/blockly_i18n.js`'s `CATEGORY_MESSAGES`
  rekeyed from the 11 old fine-grained names to the 8 new group names,
  for all 5 languages that table covers (fr/pl/de/it/uk) — including a
  `Control` entry that table never had before (a pre-existing gap,
  fixed in passing since the table was already being touched). Reused
  this session's own earlier `config/blockly_translations.py` wording
  for `Control` where the two tables now overlap (Contrôle/Steuerung/
  Controllo/Керування) for cross-table consistency.
- `tests/test_blockly_toolbox_category_groups.py` (28 tests): the
  Python mapping's exact shape, the Score/Lives/Health→Variables pin,
  unmapped-category fallback behaviour, a Python/JS drift guard (the
  two hand-written copies must stay identical), structural checks on
  the new `generateToolboxXml` grouping logic (no Node.js in CI, same
  tier `tests/test_blockly_toolbox_js_filter.py` already established
  for this exact function), and per-language translation coverage for
  all 8 groups. 6 pre-existing tests (across `test_blockly_toolbox_js_
  filter.py`, `test_blockly_category_mismatch_fix.py`,
  `test_blockly_i18n_pl.py`, `test_blockly_i18n_uk.py`) updated for the
  new category shape rather than left asserting the old one. Full
  suite: 6354 passed, 0 failed.

**Follow-up done 2026-10-21 (same day, on explicit ask):** the 73 CORE
(non-Thymio) hand-written block definitions in `blockly_blocks.js` were
recolored to match their new group's toolbox color — each block's
`this.setColour("#HEX")` call is a literal, independent string (no
shared constant to edit once), so this was a scripted, per-block-scoped
edit (find each `Blockly.Blocks['name'] = {...}` span, replace only
that span's own color), not a blind global find-and-replace: 2 of the
12 old per-category colors (`#FF6B6B`, `#9B59B6`) happen to coincide
with colors genuinely still used by untouched Thymio blocks, which a
naive whole-file replace would have corrupted. Thymio's own ~42 blocks
(a separate category set, out of scope per this plan) were verified
unchanged. `tests/test_blockly_block_body_colors.py` (22 tests) pins
every core block's color against its group, confirms Thymio's colors
are untouched (including the two colliding values), and confirms no
core block still carries a stale pre-recolor color. Full suite: 6376
passed, 0 failed.

---

### Current state (verified by reading the code, not assumed)

pygm2's toolbox has far more categories than Scratch's 9: `Events`,
`Control`, `Movement`, `Timing`, `Drawing`, `Score/Lives/Health`,
`Instance`, `Room`, `Values`, `Sound`, `Game`, `Particles`, `Views` (13),
plus the always-on built-in `Math`/`Logic`/`Text`, plus up to 8 more from
the Thymio extension when it's active.

**Category identity is declared independently in 5 places**, confirmed
by reading each:
1. `config/blockly_config.py`'s `BLOCK_REGISTRY` — a `{category:
   [block, ...]}` dict, category names are bare strings used as dict
   keys everywhere (no enum/ID layer).
2. Every `BlocklyConfig` preset (`get_beginner`, `get_junior`,
   `get_intermediate`, ~10 total) ends with its own literal
   `enabled_categories = {...}` set.
3. `blockly_workspace.html`'s `generateToolboxXml()` has its own
   parallel hardcoded `categories` dict (color + toolbox XML) that a
   dedicated drift test (`tests/test_toolbox_visibility.py`-style)
   already keeps in sync with #1.
4. The same file's `registerCustomBlocks()` has a *third* `categoryColors`
   map, for the ~80 actions with no hand-written block.
5. `events/action_types.py`'s per-action `category=` string — a fourth
   source of truth a 2026-10-15 "category mismatch" cleanup already had
   to reconcile against the first three (see `TODO.md`'s closed Blockly-
   category entries for that history).

**Consequence for this plan:** collapsing the category *set* is not a
one-line change, but it is mechanical — renaming/regrouping existing
strings, not an architectural rewrite. The real risk is touching 5 places
instead of 1 and missing one (exactly the bug class the 2026-10-15
cleanup fixed).

**No existing precedent for actually shrinking the category set.** The
`junior` edition tier (`docs/KID_UI_SIMPLIFICATION_PLAN.md` Phase 3,
`BlocklyConfig.JUNIOR_BLOCKS`) only narrows *which blocks* show inside
the existing categories — it does not touch `enabled_categories` at all,
so junior's toolbox has the same 13+ categories, just visually sparse.
This plan is the first attempt at merging the categories themselves.

### Recommended approach: a presentation-only grouping layer, not a rename

Rather than renaming `BLOCK_REGISTRY` keys everywhere (which would force
touching all 10 presets' `enabled_categories` literals, the drift test,
and `action_types.py`'s per-action strings), add **one new mapping**
that only the toolbox-rendering code consults:

```python
# config/blockly_config.py
TOOLBOX_CATEGORY_GROUPS: dict[str, list[str]] = {
    "Motion":    ["Movement", "Views"],
    "Looks":     ["Drawing", "Particles"],
    "Sound":     ["Sound"],
    "Events":    ["Events"],
    "Control":   ["Control", "Timing", "Room", "Game"],
    "Sensing":   ["Instance"],
    "Operators": ["Values"],            # + the built-in Math/Logic/Text
    "Variables": ["Score/Lives/Health"],# + set_variable/test_variable
    "My Blocks": [],                    # Feature 2 populates this
}
```

Everything internal (presets, `enabled_categories`, `enabled_blocks`,
`action_types.py`'s `category=`, the existing drift test) keeps working
**exactly as today** — a preset still enables/disables at the original
fine-grained category level. Only `generateToolboxXml()` changes: instead
of one toolbox `<category>` per `BLOCK_REGISTRY` key, it emits one per
`TOOLBOX_CATEGORY_GROUPS` key, pooling every enabled block from that
group's source categories into one flyout.

This is lower-risk and reversible (tune the grouping without touching
preset logic) and it's the right layering: "what's enabled" (fine-
grained, unchanged) stays separate from "how it's drawn" (coarse,
new) — the same separation a UI redesign should have from the feature
gating underneath it.

A new test (`tests/test_toolbox_category_groups.py`-shaped) should
assert every `BLOCK_REGISTRY` key appears in exactly one
`TOOLBOX_CATEGORY_GROUPS` list (no orphaned category silently vanishes
from the toolbox when this ships) — the same shape of guard the existing
drift test already uses for the BLOCK_REGISTRY/toolbox-XML sync.

### Proposed mapping (needs sign-off, not just engineering judgment)

The table above is a first proposal, reasoned from what each category
actually contains, not a given:
- **Motion** ← Movement + Views (camera settings are motion-adjacent;
  could also stay separate — see open questions).
- **Looks** ← Drawing + Particles (anything visual/cosmetic).
- **Control** ← Control + Timing + Room + Game. This is the biggest
  merge — alarms/timers, room navigation, and game-lifecycle actions
  (restart/save/load) are all "control flow" in a loose sense, but it's
  also the category most likely to feel overstuffed. Worth revisiting
  once it's actually rendered and clicked through.
- **Sensing** ← Instance (collision checks, instance counts — the
  closest existing match to Scratch's "touching", "distance to" blocks).
- **Operators** ← Values + the built-in Math/Logic/Text categories
  (already conceptually "operators" in Scratch's sense).
- **Variables** ← Score/Lives/Health + `set_variable`/`test_variable`
  (currently hand-written blocks filed under Control). **Open
  question:** Score/Lives/Health is used by nearly every beginner
  tutorial; burying it inside a generic "Variables" bucket may hide it
  from exactly the students who need it most often. Keeping it as its
  own 10th category instead of merging it is a real, defensible
  alternative — flag for the sign-off conversation, don't just merge it
  silently.
- **My Blocks** ← empty until Feature 2 fills it.

This lands at exactly 9 categories, matching the screenshot's count. Not
a requirement — just confirms the mapping is Scratch-sized, not
arbitrarily shrunk.

### Work breakdown

1. Pin the mapping (the open questions above need a decision) as the
   `TOOLBOX_CATEGORY_GROUPS` dict.
2. `generateToolboxXml()`: group by the new mapping instead of iterating
   `BLOCK_REGISTRY` keys directly; recolor (9 new colors, not 13 — reuse
   Scratch's own category colors as a starting palette, since they're a
   reasonable, tested-on-kids default).
3. `registerCustomBlocks()`'s `categoryColors`/`customCategories`
   dispatch (for the ~80 auto-generated-block actions) needs the same
   grouping applied, so a generated block's `def.category` string
   resolves through the mapping too — otherwise generated blocks would
   still fragment into the old 13 categories even after hand-written
   ones consolidate.
4. New completeness test (every `BLOCK_REGISTRY` category covered
   exactly once).
5. Visual QA: screenshot the toolbox for `beginner`/`intermediate`/
   `junior` presets (the offscreen-`QWidget.grab()` technique already
   used elsewhere in this repo for headless visual spot-checks — see
   CLAUDE.md's 2026-08-10 session note) and actually look at whether 9
   categories read sensibly, before calling this done.
6. Update `docs/KID_UI_SIMPLIFICATION_PLAN.md`/`TODO.md` to record the
   new grouping as the current toolbox shape (so a future session
   doesn't rediscover the 13-category layout as if it still existed).

### If "reduce to one category" was literally meant

Then skip the mapping/grouping table above and instead: every enabled
block (from every source: `BLOCK_REGISTRY`, generated actions, built-in
Math/Logic/Text, and Feature 2's My Blocks) goes into a single flyout,
alphabetized or lightly grouped by a visual separator Blockly's toolbox
XML already supports (`<sep>`) rather than real categories. Simpler to
build (no mapping decisions) but likely to be a worse browsing
experience the moment the block count climbs past what the junior
preset ships (already ~40 blocks) — a single long flyout is harder to
scan than Scratch's own multi-category model, which is presumably why
Scratch itself doesn't do this. Not recommended unless genuinely
intended.

---

## Feature 2: student-defined custom blocks ("My Blocks") — ✅ DONE 2026-10-21

Shipped the Blockly-side-only design below, exactly as recommended, with
one scope narrowing found necessary during implementation (see "v1 scope
note" further down).

- **Toolbox**: `blockly_workspace.html` adds `<category name="My Blocks"
  ... custom="PROCEDURE"></category>` to the generated toolbox XML —
  Blockly's own built-in `flyoutCategory` populates it dynamically
  (every `procedures_defnoreturn` on the workspace, plus its own "Make a
  Block" button), confirmed present in the vendored
  `lib/blocks_compressed.js`/`blockly_compressed.js`, no bespoke UI
  built. An explicit `workspace.registerToolboxCategoryCallback(...)`
  call was added as a defensive safety net alongside the auto-
  registration the vendored core appears to already perform on every
  workspace (confirmed by reading the minified source: a
  `this.registerToolboxCategoryCallback(CATEGORY_NAME..., 
  internalFlyoutCategory...)` call reached from workspace construction)
  — cheap and harmless either way, since the call just overwrites a
  name's callback. Excluded from the `junior` tier by product decision
  (reusing the same `?junior=1` check this file already uses elsewhere),
  per the plan's own leaning.
- **Codegen** (`blockly_generators.js`): a call is expanded into its
  definition's own action list at generation time — `indexCustomBlockDefs`
  builds a `{name: {argNames, bodyBlock}}` index once per generation run;
  `walkTopLevelActionChain` (replacing `generateBlockCode`'s old inline
  loop) expands any `procedures_callnoreturn` it meets directly, with
  each declared parameter substituted via `getInputValue`'s new
  `variables_get` case (a parameter reporter dropped into a value
  socket resolves to a `{{PYGM_ARG:<name>}}` placeholder,
  `substituteCustomBlockArgs` deep-substring-replaces it with the real
  call-site value afterward). The saved project data only ever contains
  ordinary actions — confirmed no runtime, HTML5, or Kivy changes were
  needed, the whole point of this design.
- **API grounded in the real vendored source, not just memory**: every
  method/field name this relies on
  (`getFieldValue('NAME')`/`getVars()`→`this.arguments_`/
  `getInputTargetBlock('STACK')`/`ARG0,ARG1,...`/`variables_get`'s
  `field_variable` + `workspace.getVariableById(id).getName()`) was
  confirmed by grepping `lib/blocks_compressed.js`/
  `blockly_compressed.js` directly before writing any code, not assumed.
- **v1 scope note — narrower than the plan originally sketched, decided
  during implementation, not silently cut**: a custom-block call is only
  expanded when it's a TOP-LEVEL action directly inside an event or
  another custom block's own body. Nesting a call inside an
  if_condition/test_variable then/else branch, or inside ANOTHER custom
  block (recursion/cycles), is explicitly **not** expanded — both
  surface as a clear, visible sentinel action
  (`__pygm_custom_block_nesting_unsupported__` /
  `__pygm_undefined_custom_block__`, reusing the existing amber
  "unrecognized action" convention) rather than being silently dropped.
  This was chosen specifically because ~15 other call sites across the
  generator (if_condition/test_variable branches, several Thymio
  conditionals) all share the same long-standing "one block walked ->
  exactly one action pushed" contract; teaching all of them to handle a
  call expanding to zero-or-many actions would have been a much larger,
  riskier change touching a lot of already-battle-tested code, for a
  nesting capability Scratch's own UI doesn't make especially obvious
  either. A useful side effect: restricting calls to the top level means
  **no cycle detection/depth cap was needed at all** — a cycle is
  structurally impossible when calls can't nest.
- **Translations**: the Blockly-native definition/call block UI is
  already translated for free (all 11 shipped languages, confirmed by
  grepping `lib/msg/<lang>.js`). "My Blocks" itself (the category label)
  added to `CATEGORY_MESSAGES` for the 5 languages that table covers
  (fr/pl/de/it/uk) — `Mes Blocs`/`Meine Blöcke`/`I Miei Blocchi`/
  `Moje Bloki`/`Мої Блоки`.
- **Tests**: `tests/test_blockly_custom_blocks.py` (22 tests) — the
  vendored-API pin (so a future Blockly upgrade that renames something
  this relies on is caught instead of silently breaking), toolbox
  registration/junior-exclusion/i18n, and the full codegen chain
  (indexing, expansion, substitution, the nesting/undefined sentinels,
  the sentinel names confirmed to not collide with any real
  `ActionType`). No Node.js in CI, same structural tier this repo
  already established for this editor's JS. 3 pre-existing tests
  (`test_blockly_i18n_pl.py`, `test_blockly_i18n_uk.py` ×2,
  `test_blockly_toolbox_category_groups.py`) updated for the 9th
  category. Full suite: 6398 passed, 0 failed.
- **Deferred items 4 and 5 — ✅ DONE 2026-10-22.** Both resolved in the
  same session, see "Follow-up: nesting + reporters" below for the full
  design. Still deferred, logged not forgotten: per-object (vs.
  project-wide) custom blocks; a bundled sample/tutorial teaching "make
  your own block" (this repo's own established convention for a new
  teaching feature — a real scope of its own).
- **Needs human eyes, genuinely unverified — the most important caveat
  on this feature**: no Node.js/browser available in this environment,
  so none of this was ever actually executed. The core mechanism (drag
  a parameter reporter into a socket inside Blockly's own mutator
  dialog, confirm it really produces a `variables_get` block resolving
  the way this code assumes, confirm a dragged "My Blocks" call
  actually expands correctly into a running game) has not been watched
  working in a real IDE session. This is squarely in the same category
  as this project's other standing "needs a human/real browser" items
  (`docs/PROJECT_STATUS.md`'s manual-QA backlog) — flagged rather than
  claimed solid.

#### Follow-up: nesting + reporters — ✅ DONE 2026-10-22

Both items 4 and 5 from the "treated at a later date" retrospective
list, resolved in the same `blockly_generators.js`:

- **Nesting (item 5).** The v1 "never expand inside another chain"
  restriction is gone. `walkTopLevelActionChain` was renamed
  `walkActionChain` and is now the ONLY place any chain of sibling
  statement blocks is ever walked in this file — every nested DO/ELSE/
  sub_actions site that used to hand-roll its own `while` loop calling
  `generateActionCode` directly (`if_condition`, `test_variable`,
  `test_expression`, `grid_if_on_grid`, `room_if_next_exists`,
  `room_if_previous_exists`, and all six `thymio_if_*` blocks — 12 sites)
  now calls `walkActionChain` instead, so a custom-block call nested at
  any depth — inside a conditional branch, inside another custom block's
  own body, or both — expands exactly like a top-level one.
  `generateActionCode`/`generateActionCodeInner` had `customBlockDefs`
  and `callStack` threaded through as explicit parameters to make this
  work (the bounded ~15-site surface the original plan anticipated).
  Cycle detection replaces the old "can't happen by construction"
  argument: `callStack` is the list of custom-block names currently
  being expanded on the path down to the current call;
  `expandCustomBlockCall` refuses (with a visible
  `__pygm_custom_block_cycle_detected__` sentinel, not infinite
  generation-time recursion) a call that would re-enter a name already
  on the stack, which catches direct self-recursion and any longer
  `A -> B -> A` cycle alike. A separate `MAX_CUSTOM_BLOCK_EXPANSION_DEPTH`
  (50) cap guards the orthogonal case a name-based check can't:
  pathologically deep but acyclic nesting (`__pygm_custom_block_too_
  deeply_nested__`). The old nesting-refusal sentinel
  (`__pygm_custom_block_nesting_unsupported__`) no longer describes real
  behaviour, since nesting is supported; it was renamed to
  `__pygm_custom_block_call_not_expanded__` and now exists only as a
  defensive fallback in `generateActionCodeInner`'s own switch, reached
  only if some future statement-chain site is added without routing
  through `walkActionChain` — a code-path bug, not a live authoring
  scenario.
- **Reporters (item 4).** `procedures_defreturn`/`procedures_callreturn`
  are resolved on the EXPRESSION side (`getInputValue`, refactored to
  delegate to a new `evaluateValueBlock(inputBlock, defaultValue)` so the
  same logic can evaluate a definition's own `VALUE` input directly, not
  just a named socket on a parent block) rather than the action side,
  since a reporter call can appear in any value socket, not just a
  statement chain. Confirmed against the vendored source before writing
  any code: `procedures_defreturn`'s return-value input is named
  `"VALUE"`, not `"RETURN"` (`this.appendValueInput("VALUE")` under the
  `PROCEDURES_DEFRETURN_RETURN` label); `procedures_callreturn` is
  `setOutput(true)` with no statement connectors, confirmed via
  `grep`, so it can never be dragged into a statement slot in the first
  place and needs no action-list handling. `indexCustomBlockDefs` now
  indexes both def types, capturing `returnBlock`/`isReporter` alongside
  the existing `argNames`/`bodyBlock`. A **pure** reporter (empty
  `STACK`, just a `RETURN` value) resolves to an expression string with
  its own `ARG0..` parameters substituted — reusing the exact same
  `{{PYGM_ARG:<name>}}` placeholder + `substituteCustomBlockArgs`
  mechanism the no-return side already established, since a reporter's
  `RETURN` expression references its own parameters via the identical
  `variables_get` block. A reporter whose `STACK` has statements is
  **not** resolved — not a scoping choice but an inherent limit of this
  action-based architecture (there's no way to "run these actions, then
  use this value" from inside a single expression socket) — surfaced as
  a visible `{{PYGM_REPORTER_SIDE_EFFECTS:<name>}}` placeholder rather
  than silently dropping the side effects or treating the call as 0.
  Undefined/cyclic/too-deep reporter calls get their own analogous
  placeholders (`{{PYGM_UNDEFINED_REPORTER:...}}`,
  `{{PYGM_REPORTER_CYCLE:...}}`, `{{PYGM_REPORTER_TOO_DEEP:...}}`).
  Reporter cycle detection uses its own module-level
  `CURRENT_REPORTER_CALL_STACK` (set once per generation run alongside
  the existing `customBlockDefs` index) rather than a threaded
  parameter: `getInputValue` has roughly 60 existing call sites across
  this file taking only `(block, inputName, defaultValue)`, and
  threading a new parameter through every one of them would have been a
  much larger, riskier change than the contained action-side threading
  above — and the two call stacks can never cross anyway, since a
  no-return custom block and a reporter are different block types that
  can't substitute for each other.
- **Tests**: `tests/test_blockly_custom_blocks.py` extended (reporter
  indexing/resolution, nested-call expansion through a conditional
  branch, nested custom-block-calling-custom-block, cycle detection,
  the depth cap, the renamed/new sentinel set re-checked against
  `ACTION_TYPES` for collisions). Same "no Node.js in CI" structural
  tier as the rest of this feature — **still genuinely unverified in a
  real browser**, same caveat as the rest of Feature 2.

#### Follow-up: project-wide sharing (item 6) — ✅ DONE 2026-10-22

A retrospective note from the session that built Feature 2 described
"per-object custom blocks" as deferred because the shipped feature was
already "project-wide/shared." **That description was never actually
true, and this follow-up is what makes it true.** Verified by reading
`editors/object_editor/blockly_widget.py`/`object_editor_main.py` before
writing any code: each object's Blockly workspace is its own separate
page with its own isolated JS state — the workspace XML is saved into
and loaded from THAT object's own `object_data['blockly_workspace']`
field, and nothing anywhere merged another object's blocks in. So a
custom block defined in object A was, in fact, 100% invisible when
editing object B — the opposite of "shared" — contradicting this
feature's own original design decision ("Scope: project-level... shared
by every object"). Confirmed with the user before building a feature
this size on a corrected premise (see the session's own clarifying
question): build the real thing, not just fix the doc.

- **Persistence — a plain top-level project key, no new save/load
  plumbing needed.** `current_project_data['custom_blocks']` (NOT under
  `assets` — it's derived metadata about objects' Blockly workspaces, not
  an asset type of its own) rides through `save_project`/`load_project`
  for free: `load_project` does a wholesale `self.current_project_data =
  project_data` with no key allowlist, and `_prepare_project_data_for_save`
  only ever mutates specific `assets` subtrees, never filters other
  top-level keys. `ProjectManager.update_custom_blocks_registry(
  source_object, exported_defs)` (`core/project_manager.py`) is the only
  write path: replaces every existing entry previously sourced from
  `source_object` (so a renamed/deleted definition doesn't linger) and
  leaves every other object's entries untouched.
- **No live cross-tab broadcast — a deliberate, documented
  simplification, not an oversight.** The registry updates only when an
  object is SAVED (`core/ide/_editor_lifecycle.py`'s
  `on_editor_save_requested`, which pops a transient
  `object_data['_custom_blocks_export']` key — attached by
  `object_editor_main.py`'s `get_data()` — and folds it in before the
  object's own record continues through the ordinary save), not live on
  every keystroke. So a block changed in object A becomes visible to
  object B once B's editor is next opened (or reopened), not instantly
  while both are open simultaneously. Reads never depend on any other
  object's editor being open at all, which is the thing that makes this
  tractable: `current_project_data['custom_blocks']` is already fully
  populated from disk the moment a project loads, long before any
  individual object's editor is lazily constructed.
- **Each registry entry is a pre-resolved TEMPLATE, computed once by the
  SOURCE object's own workspace.** `generateCustomBlocksExportJson`
  (`blockly_generators.js`) re-walks each of a workspace's own LOCAL
  definitions through the exact same `walkActionChain`/`evaluateValueBlock`
  machinery a real call site uses, so the definition's own nested calls
  are already expanded — only that definition's OWN
  `{{PYGM_ARG:<name>}}` placeholders are left unsubstituted, for a future
  call site (in this object or any other) to fill in. This is why a
  shared definition never needs the CALLING page's own Blockly blocks to
  resolve: `expandCustomBlockCall`/`evaluateCustomBlockReporterCall` treat
  a null `bodyBlock`/`returnBlock` (the shape `mergeSharedCustomBlockDefs`
  builds for an entry from `SHARED_CUSTOM_BLOCKS`) as a signal to use
  `bodyActionsTemplate`/`returnExprTemplate` directly instead of walking
  real blocks that don't exist on this page.
  - **Consequence, by design: a genuine cross-object cycle (A's block
    calls B's which calls back into A's) is never a crash risk.** Nothing
    recomputes recursively across objects at generation time — each side
    only ever consumes an already-resolved template from a PRIOR save, so
    at worst a call sees a one-generation-stale template, never an
    infinite loop. A same-object cycle is still actively caught by
    `callStack`/`CURRENT_REPORTER_CALL_STACK` exactly as the nesting
    follow-up above built; this only concerns the cross-object case those
    can't see in the first place.
  - **Known sharp edge: a genuine cross-object name collision is
    last-write-wins, not prevented.** Blockly's own duplicate-name guard
    (`findLegalName`) is workspace-local only — nothing stops two objects
    naming a block the same. `mergeSharedCustomBlockDefs` always lets a
    LOCAL definition win over a shared one when generating THAT object's
    own code, but across two objects that never locally define the same
    name, whichever one saved to the registry most recently wins for
    everyone else calling it. Documented, not silently surprising;
    acceptable for a kid-focused IDE where names are meant to be
    project-unique identifiers anyway.
- **The toolbox flyout extension — without this, the whole mechanism
  would be unreachable in practice.** A `procedures_callnoreturn`/
  `callreturn` block can only ever be authored by dragging one out of the
  "My Blocks" flyout; `Blockly.Procedures.allProcedures` (which drives
  that flyout) only ever sees a workspace's own local blocks. So
  `buildSharedCustomBlockFlyoutItems` (`blockly_generators.js`) appends
  flyout entries for every project-wide shared definition not already
  locally defined, in the exact XML shape confirmed against the vendored
  source's `xmlFlyoutCategory` function (`<block type="procedures_call
  (no)return" gap="16"><mutation name="..."><arg name="..."/></mutation>
  </block>`), parsed via `Blockly.utils.xml.textToDom` (already used
  elsewhere in this app's own loader, so not a new dependency on an
  unverified API).
  - **A real finding, not an assumption carried over from the original
    Feature 2 session: `Blockly.Procedures.flyoutCategory` is NOT real
    public dotted API in this vendored build.** The only occurrence of
    that exact string anywhere in `blockly_compressed.js` is inside a
    deprecation-warning MESSAGE, not actual code (confirmed by `grep`
    before writing anything that depended on it) — meaning the ORIGINAL
    Feature 2 session's defensive `if (Blockly.Procedures && typeof
    Blockly.Procedures.flyoutCategory === 'function')` guard almost
    certainly never actually ran, relying entirely on the vendored core's
    own self-registration (confirmed separately: `this.
    registerToolboxCategoryCallback(CATEGORY_NAME..., 
    internalFlyoutCategory...)`, called from workspace construction).
    Fixed properly this time: `workspace.getToolboxCategoryCallback`/
    `registerToolboxCategoryCallback` ARE real, unmangled `WorkspaceSvg`
    prototype methods (confirmed directly), so the new code reads back
    whatever is ALREADY registered for `"PROCEDURE"` and wraps THAT,
    keeping the old (likely-dead) check only as a defensive fallback in
    case a future Blockly build ever makes `flyoutCategory` real public
    API.
- **Tests**: `tests/test_blockly_custom_blocks.py` extended further
  (merge/template shape, the flyout XML shape and name-collision
  skipping, the `Blockly.Procedures.flyoutCategory`-is-only-a-warning-
  string finding pinned so a future Blockly upgrade that makes it real
  gets caught instead of silently reintroducing the same dead-code risk).
  New `tests/test_custom_blocks_sharing.py` (29 tests) covers the Python
  side: the registry's merge/collision/dirty semantics including a REAL
  save+load round trip proving `custom_blocks` survives on disk, every
  new `BlocklyWidget` push/pull method (mirroring
  `tests/test_blockly_workspace_xml.py`'s own cached-value pattern for
  `get_workspace_xml`), and `on_editor_save_requested`'s wiring (unbound-
  method-on-a-stub, mirroring `tests/test_room_editor_sprite_metadata_
  refresh.py`'s established pattern for this exact method) including that
  a raising registry update never blocks the object's own save. Full
  suite: 6472 passed, 0 failed (the raycast smoke-test failures seen
  mid-session were pre-existing timing flakiness, confirmed unrelated by
  re-running them in isolation — no raycast/runtime code was touched).
- **Needs human eyes, genuinely unverified — same standing caveat as the
  rest of Feature 2**: nobody has watched two real object editors open
  side by side, defined a block in one, reopened the other, and dragged
  the shared call in from the flyout. The JS mechanics (merge shape,
  flyout XML, the toolbox-callback read-and-wrap) are all grounded in the
  vendored source rather than assumed, but none of it has executed in an
  actual browser.

---

### Current state

**No existing support at all.** Grepped the whole Blockly integration
(`blockly_workspace.html`, `blockly_widget.py`) for `procedures_def*`/
`procedures_call*`/`Blockly.Procedures` — zero hits anywhere in this
app's own code.

**But the vendored Blockly library already ships the whole feature,
fully translated, just never wired in** — this is the single most
important finding for scoping this feature cheaply:
- `editors/object_editor/blockly/lib/blocks_compressed.js` and
  `blockly_compressed.js` already contain Blockly's standard
  `procedures_defnoreturn`/`procedures_callnoreturn`/
  `procedures_defreturn`/`procedures_callreturn` block definitions, the
  "Make a Block" mutator dialog (add/remove/rename typed parameters,
  live-updating every call site), and local-variable scoping inside the
  definition — all of Scratch's "My Blocks" UX, because Scratch's
  underlying model (a fork called scratch-blocks) descends from the
  same Blockly procedures concept.
- Every one of this app's 11 shipped UI languages already has these
  strings translated, for free, as part of Blockly's own vendored
  per-language message catalog (`lib/msg/<lang>.js` — confirmed 32
  `PROCEDURES_*` strings present in `msg/fr.js`, and the same catalog
  already gets loaded per-language by the existing
  `blockly_message_file()`/`_set_blockly_language()` machinery). Zero
  translation work needed for the block UI itself.

This means the expensive part of "build a Scratch-style custom block
system" — the definition/parameter UI, the call-site auto-sync, the
i18n — **already exists and already ships in this app's own vendored
files.** The actual work is wiring it in and teaching *this app's*
code generator what a block definition/call means.

### Why this can be Blockly-side only — no runtime or export changes

Trace of how a block currently becomes game behavior (confirmed by
reading `blockly_workspace.html`/`blockly_widget.py`): a workspace
change fires `generatePyGameMakerCode()`, which walks each event's
action-block chain and emits **JSON** (`{"create": {"actions": [...]}, ...}`)
— not source code. That JSON is what gets saved into the object's data
and is what the desktop runtime, HTML5's `engine.js`, and Kivy's codegen
each independently read and execute.

**Recommended design: expand a custom-block call into its definition's
action JSON at generation time**, inside `blockly_generators.js`, the
same place `execute_script` already resolves. Concretely:
- `procedures_defnoreturn` is not an event hat — skip it at the
  top-level walk, but index it by name so calls can find it.
- When `procedures_callnoreturn` appears inside an event's action
  chain, look up the matching definition and **inline its body's action
  list directly into the caller**, substituting each declared
  parameter's value into any `argN`-style reference inside the
  definition — reusing the exact substitution convention
  `execute_script`'s `arg0..argN` params already establish, so it's a
  familiar pattern, not a new one.
- The *saved* project data therefore contains only ordinary,
  already-understood actions. **No new action type, no runtime
  changes, no HTML5/Kivy codegen changes, no 3-engine parity work** —
  the single biggest cost class in this codebase for any new
  primitive (see CLAUDE.md's repeated notes on raycast/room-action
  work needing three independently-maintained implementations). A
  custom block is pure authoring sugar, expanded before anything
  downstream ever sees it.
- Editing a definition and re-syncing *any* event naturally picks up
  the change, because the Blockly workspace XML (not the generated
  JSON) is the real source of truth and regenerates on every change —
  this falls out of the existing architecture for free, doesn't need
  to be specially built.

The alternative — a real runtime "call a named action-list, with a call
stack" concept, implemented identically in the desktop Python runtime,
`engine.js`, and Kivy's codegen — is explicitly **not recommended** for
v1: it's the expensive path, and it buys recursion/true subroutine
semantics a beginner's game essentially never needs. Worth reconsidering
only if a real teaching need for recursion shows up later.

### Design

- **Scope: command blocks only for v1** (run a sequence of actions, the
  Scratch default). Reporter-style custom blocks that *return a value*
  for use inside an expression field (`procedures_defreturn`/
  `callreturn`) are explicitly deferred — they'd touch the expression-
  evaluation side (`_parse_value`), a materially different and larger
  piece of work, not just the action-list side.
- **Scope: project-level, not per-object.** Scratch allows both ("for
  all sprites" vs. "for this sprite only"); starting project-wide
  (shared by every object) is simpler and avoids per-object duplication
  for v1. Revisit if students actually want object-local blocks.
  ~~Note: v1's actual implementation never built the cross-object
  sharing this decision called for — each object's workspace ended up
  fully isolated by accident of its own save/load architecture, the
  opposite of "shared."~~ **Corrected 2026-10-22** — see "Follow-up:
  project-wide sharing (item 6)" above; real cross-object sharing is now
  built, matching this original decision for real.
- **Toolbox integration**: a new "My Blocks" category (the empty slot
  Feature 1's `TOOLBOX_CATEGORY_GROUPS` already reserves), populated via
  Blockly's own built-in `Blockly.Procedures.flyoutCategory` — which
  already renders the real "Make a Block" button Scratch's own UI is
  modeled on, so no bespoke dialog needs to be built for v1.
- **Guardrails for a kid audience, not optional polish:**
  - Recursive/cyclic calls (a block that calls itself, directly or via
    a cycle of calls) must be detected and refused at expansion time —
    naive inlining would infinite-loop the generator. Cap expansion
    depth defensively regardless of cycle detection.
  - A call block referencing a deleted/renamed definition needs a clear
    "this block no longer exists" indicator, reusing the existing amber
    "unrecognized action" convention this app already has for
    extension actions (`events/plugin_loader.extension_for_action`) —
    not a silent no-op.
- **Round-trip safety**: needs the same proof every other Blockly
  feature in this app gets (`tests/test_blockly_round_trip_safety.py`'s
  established pattern) — save, reload, confirm the definition and every
  call site reconstruct identically. Blockly's own XML serialization for
  procedures is standard/battle-tested, but this app's save/load path
  around it is not, and needs its own verification.
- **Open product question, not an engineering one: does the `junior`
  tier get this at all?** Abstraction/parameterization is a
  meaningfully harder concept than sequencing pre-made actions, which
  is the whole premise of the current junior-tier design
  (`docs/KID_UI_SIMPLIFICATION_PLAN.md`). Leaning toward excluding "My
  Blocks" from `junior`'s preset by default and introducing it starting
  at the `beginner` tier, but this is a teaching-judgment call, not
  something to decide unilaterally while implementing.

### Work breakdown

1. Register `procedures_defnoreturn`/`procedures_callnoreturn` in the
   toolbox under "My Blocks," using Blockly's native flyout category —
   confirm it renders and the definition/call blocks drag in correctly
   before writing any codegen.
2. `blockly_generators.js`: index definitions by name, implement
   call-site inlining with `argN` parameter substitution, cycle
   detection with a clear error, depth cap.
3. Toolbox gating: decide which `BlocklyConfig` presets enable "My
   Blocks" (likely a new entry alongside `enabled_categories`, or a
   simple boolean flag given it's a single category with no internal
   block list to gate).
4. Round-trip test coverage (save/reload a project containing a
   definition + 2+ call sites with different argument values).
5. Stale/missing-definition handling (amber indicator, matching the
   existing extension-action convention).
6. A bundled sample or Junior-tutorial-adjacent lesson demonstrating
   "make your own block" end to end — this repo's established
   convention is to pair every new teaching feature with a sample/
   tutorial, not ship it as an untaught capability.
7. ~~(Explicitly deferred, not v1) reporter-style value-returning custom
   blocks.~~ **DONE 2026-10-22** — see "Follow-up: nesting + reporters"
   above.

---

## Suggested sequencing

Do Feature 1 first — it produces the `TOOLBOX_CATEGORY_GROUPS`
mechanism and the empty "My Blocks" slot that Feature 2 then fills,
rather than wiring "My Blocks" into the old 13-category toolbox and
touching it again during consolidation. Each feature is independently
shippable and testable; within each, follow this repo's established
one-cluster-per-commit discipline (see CLAUDE.md's "Standing
preferences" section) rather than landing either as one large commit.

## Explicitly out of scope for this plan

- Any change to `events/action_types.py`'s per-action `category=`
  strings beyond what Feature 1's grouping layer needs — those stay the
  fine-grained source of truth.
- Export/runtime engine changes of any kind (both features are
  authoring-time/IDE-only by design — see each feature's own "why no
  engine changes" reasoning above).
- ~~Reporter-style (value-returning) custom blocks.~~ **DONE 2026-10-22**
  — see "Follow-up: nesting + reporters" above (with the one real
  architectural limit it couldn't remove: a reporter whose own body has
  side-effecting statements, not just a return value).
- ~~Per-object custom blocks.~~ **Project-wide sharing DONE 2026-10-22**
  — see "Follow-up: project-wide sharing (item 6)" above. The narrower
  "for THIS object only" restriction mode (Scratch's other option)
  remains genuinely out of scope, not revisited.
- Redesigning the Thymio extension's own category set (8 categories,
  merged in separately via `register_block_categories`) — out of scope
  unless explicitly asked; it's a different audience/context than the
  core toolbox.

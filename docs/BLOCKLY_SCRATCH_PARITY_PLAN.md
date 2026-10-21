# Blockly Scratch-parity plan: fewer categories + student-defined blocks

Status: Written 2026-10-18. **Feature 1 shipped 2026-10-21** (see its own
section below). Feature 2 (My Blocks) not started.

Two separate features, sequenced so the second lands into the shape the
first produces:

1. ✅ Reduce the Blockly toolbox's category count toward Scratch's model — DONE.
2. Let a student define their own reusable block ("My Blocks") — not started.

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

**Deliberately not done in this pass, flagged rather than silently
skipped:** the ~115 hand-written block definitions in
`blockly_blocks.js` each set their OWN body color via a literal
`this.setColour("#HEX")` call, independent of the toolbox category
dict — confirmed these **already don't match** the toolbox's own
per-category colors even before this change (e.g. `event_create`'s
body is `#FFD500` while the old "Events" toolbox category itself was
`#CC8800`), so this is a pre-existing cosmetic inconsistency, not one
this change introduces or worsens. Recoloring all 115 to match their
new group is a real, mechanical, separately-schedulable follow-up
(no shared color constant to edit once — every call site is a literal
hex string) if full Scratch-style "every block in a category is that
category's color" fidelity is wanted later.

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

## Feature 2: student-defined custom blocks ("My Blocks")

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
7. (Explicitly deferred, not v1) reporter-style value-returning custom
   blocks.

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
- Reporter-style (value-returning) custom blocks.
- Per-object custom blocks.
- Redesigning the Thymio extension's own category set (8 categories,
  merged in separately via `register_block_categories`) — out of scope
  unless explicitly asked; it's a different audience/context than the
  core toolbox.

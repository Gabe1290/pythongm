# Plan: the two Blockly toolbox issues logged in TODO.md on 2026-10-16

Two independent, unrelated follow-ups, both found (not fixed) while
closing out `docs/BLOCKLY_CATEGORY_MISMATCH_2026-10-15.md`. Each is sized
to be its own session/commit sequence; they don't depend on each other
and can be done in either order.

## Issue A — "Particles" and "Views" are stray toolbox categories (DONE 2026-10-16)

Same bug class as "Game" (part 2 of the category-mismatch fix), same
fix shape, and simpler: both are already clean, single-purpose groups
with no mixed-category untangling needed (unlike Game's 20-action,
11-vs-9 split). Implemented exactly as planned below, plus one pleasant
surprise: `config/blockly_translations.py`'s `CATEGORY_TRANSLATIONS`
already had real "Particles" entries in all 7 languages (leftover from
before this category was ever wired up), so it renders translated in the
config dialog immediately — "Views" has no translation anywhere and
falls back to English, a deliberate choice matching "Game"/"Text" rather
than a gap. `config_version` bumped to `4`. Preset audit found 7 of 10
presets at risk (`get_intermediate`, `get_platformer`, `get_grid_rpg`,
`get_sokoban`, `get_testing`, `get_code_editor`, `get_blockly_editor`),
all fixed by adding the two categories to their `enabled_categories`
literal. 18 new tests in `tests/test_blockly_category_mismatch_fix.py`
(51 → 69) + 1 broadened + 2 new in
`tests/test_blockly_preset_generated_actions.py`. Full suite green.

### Root cause (already confirmed, no further investigation needed)

`events/action_types.py` has `category="Particles"` on 8 actions and
`category="Views"` on 2, neither of which is a real hardcoded key in
`editors/object_editor/blockly/blockly_workspace.html`'s `categories` JS
dict — so `registerCustomBlocks()` dumps each into its own grey,
uncolored, category-gating-exempt dynamic box.

| Category | Actions |
|---|---|
| Particles (8) | `create_particle_system`, `destroy_particle_system`, `clear_particles`, `create_particle_type`, `create_emitter`, `destroy_emitter`, `burst_particles`, `stream_particles` |
| Views (2) | `enable_views`, `set_view` |

None of these 10 are hardcoded/mapped (verified against `actionToBlockType`
— all 10 genuinely leak); none overlap with any other category's actions.

### Proposed fix (mirrors the Game fix exactly, see that commit for the
worked example — `a2f5db9d`)

1. `blockly_workspace.html`: add `'Particles': {color: <TBD>, blocks: []}`
   and `'Views': {color: <TBD>, blocks: []}` to the dynamic `categories`
   dict (pure merge targets, like Game's `blocks: []` — all 10 actions stay
   dynamically generated, nothing to hardcode). Add both to
   `categoryColors` too (used for each generated block's own face colour,
   independent of the category box colour). Proposed, non-clashing colours
   against the current palette (Events #CC8800, Movement #5C81A6, Control
   #FFAB19, Drawing #9B59B6, Score/Lives/Health #5CA65C, Instance #A65C81,
   Room #A6745C, Values/Math #5C68A6, Sound/Audio #9966FF, Timing #FF6B6B,
   Game #607D8B, Text #4FA8A8): Particles `#E67E22` (warm orange, fits a
   burst/spark visual theme), Views `#34568B` (deep blue, fits "camera").
   Adjust on sight if either reads badly next to a neighbour in the
   flyout.
2. No `action_types.py` changes needed — these 10 actions already carry
   the right category string; they just need a real category to land in.
3. `config/blockly_config.py` `BLOCK_REGISTRY`: add new `"Particles"` and
   `"Views"` keys (currently absent entirely, so the config dialog can't
   show/hide any of these 10 blocks today) with the 8 + 2 entries above
   (display names/descriptions already pulled from `ACTION_TYPES`, ready
   to paste).
4. **Preset audit (do this BEFORE flipping the toolbox switch, same
   lesson as the Game regression)**: for each of the 10 `BlocklyConfig`
   presets, check whether `{particles ∪ views actions} & enabled_blocks`
   is non-empty while `"Particles"`/`"Views"` is absent from
   `enabled_categories` — any such preset needs the category added, same
   as `get_platformer`/`get_grid_rpg`/`get_sokoban`/`get_testing` needed
   `"Game"` added. Script for this already exists in spirit
   (`tests/test_blockly_category_mismatch_fix.py`'s
   `test_no_preset_shows_game_blocks_without_enabling_the_game_category`
   parametrized test) — write the Particles/Views equivalent first, let
   it fail, read off exactly which presets need the fix, same workflow
   as last time.
5. Same `load_config()` migration pattern: bump `config_version` to `4`
   (building on the `3` part 2 introduced), add `"Particles"`/`"Views"`
   to `enabled_categories` for a saved config that already has any of
   these 10 actions in `enabled_blocks` — mirrors the version-2→3
   migration in `config/blockly_config.py` almost line for line.
6. Translations: check whether `"Particles"`/`"Views"` need entries in
   `config/blockly_translations.py` (7 languages) and/or
   `blockly_i18n.js`'s `CATEGORY_MESSAGES` (5 languages, confirmed a
   *different* table from the Python one, per part 1's "missed it the
   first time" lesson) — same judgment call part 2 made for "Game"/"Text"
   (both left untranslated, falling back to English, as a deliberate,
   documented scope decision, not an oversight). Decide once, apply
   consistently to both new categories.
7. Regression tests, same shape as
   `tests/test_blockly_category_mismatch_fix.py`'s Game-specific block
   (real-toolbox category-key dump including "Particles"/"Views", `BLOCK_
   REGISTRY` content, the `enabled_categories` audit per preset, the new
   migration, a live `BlocklyConfigDialog` dump showing both new
   categories).

### Estimated size

Smaller than the Game fix (no 11-vs-9 split, no action_types.py changes,
no orphaned-block side-quest like `execute_code` was). One commit is
plausible; split into two (Particles, then Views) only if the preset
audit turns up enough per-category fixes to want separate review.

## Issue B — preset `enabled_categories` can silently lag `enabled_blocks`

Different bug class from Issue A: `"Control"` and `"Timing"` ARE real,
correctly-named, already-hardcoded toolbox categories — this was never a
stray-category naming mismatch. `get_platformer` enables Control-category
generated actions (`test_chance`, `if_collision`, `if_collision_at`,
`if_object_exists`, `start_block`, `end_block`, `comment`, `check_empty`,
`test_question`, `execute_script`, `else_action`, `repeat`) and
Timing-category ones (`sleep`, `pause_timeline`, `set_timeline`,
`set_timeline_position`, `set_timeline_speed`, `start_timeline`,
`stop_timeline`) via the blanket `GENERATED_ACTION_NAMES |
PROMOTED_TO_HAND_WRITTEN_BLOCKS` union, but its `enabled_categories` set
has never listed `"Control"` or `"Timing"` — so these 19 blocks have been
silently invisible in the platformer preset's live toolbox since it was
written. Found by accident (narrowing a regression test for Issue
A's predecessor); never audited on purpose.

### Step 1 — audit every preset × every category (not just this one
instance)

Before fixing `get_platformer` specifically, run the general form of the
check across all 10 presets and every real toolbox category (not scoped
down to Game/Drawing the way `tests/test_blockly_preset_generated_actions.py
::test_everything_presets_also_enable_the_categories_their_generated_actions_need`
deliberately is today — see that test's own docstring for why it was
narrowed). This is a short script, not a big investigation:

```python
from config.blockly_config import BlocklyConfig, PRESETS
from events.action_types import ACTION_TYPES
# mapped = parse actionToBlockType from blockly_workspace.html (see
# tests/test_blockly_category_mismatch_fix.py's _action_to_block_type_map
# for the exact extraction regex) -- exclude these, same false-positive
# reason as every check this session already hit twice.
for name, cfg in PRESETS.items():
    for action_name in cfg.enabled_blocks:
        if action_name in mapped:
            continue
        action = ACTION_TYPES.get(action_name)
        if action and action.category not in cfg.enabled_categories:
            print(name, action.category, action_name)
```

Catalogue every `(preset, category)` pair this prints — `get_platformer`
× Control/Timing is confirmed already; there may be more (no other preset
has been checked this way yet, including the ones this session's Game
fix already touched — worth re-running after Issue A ships too, since
new categories change the mapped/leak picture again).

### Step 2 — decide the fix per gap found

For each `(preset, category)` pair: if the action only reached
`enabled_blocks` via the blanket `GENERATED_ACTION_NAMES |
PROMOTED_TO_HAND_WRITTEN_BLOCKS` union (true for every case found so
far), the preset's author never deliberately excluded these blocks —
the union's whole stated purpose is "show every generated/promoted
action" — so the category belongs in `enabled_categories`, same
reasoning and same fix as Issue A/the Game regression. If a future
catalogue entry turns out to be explicitly, individually enabled via its
own `config.enable_block(...)` call (not just the blanket union), that's
a genuinely different signal worth a second look before assuming the
same answer — hasn't happened in any case found so far, but check before
batch-applying the fix.

### Step 3 — fix + regression test

Add the missing categories to each preset's `enabled_categories` literal.
One general-purpose regression test (the audit script above, turned into
an assertion with zero exclusions — once every real gap is fixed, it
should find nothing left to report) replaces needing a bespoke test per
preset.

### Estimated size

Audit-then-fix, same shape as the Score/Grid/Output/Game work already
done this week. Could be one commit if the audit only confirms
`get_platformer`; more if it finds siblings. Low risk — purely additive
(`enabled_categories.add(...)`), never removes visibility from anything.

## Sequencing

No dependency between A and B. Suggested order: A first (same bug class
as the just-shipped Game fix, pattern is fresh, lowest-risk), then B's
audit (cheap to run, might turn up more now that A will have changed the
"mapped" picture again), then B's fixes. Both end with a full-suite gate
before pushing, same discipline as every unit this week.

# Blockly toolbox / "Configure Action Blocks..." category mismatch

**Status: fixed 2026-10-15/16** (see "Resolution" at the bottom). The
investigation below is kept verbatim as the record of how the root cause
was found. Picks up the user's
request: "The 'Configure Action Blocks...' sub menu should display a window
that corresponds to the actual blockly editor Blocks... there is a
'Score/Lives/Health' and a 'Score' categories. The 'Grid' category should be
merged with the Movement category. ... 'Output' should be merged with
'Drawing'."

## Root cause (confirmed, ground-truthed against live code)

Three independent sources of "categories," which don't agree:

1. **`config/blockly_config.py`'s `BLOCK_REGISTRY`** — feeds the "Tools >
   Configure &Action Blocks..." menu item
   (`core/ide/_menu_builder.py:240`) → `configure_blockly()`
   (`core/ide/_dialogs.py:37`) → `BlocklyConfigDialog`
   (`dialogs/blockly_config_dialog.py`, window title "Configure Events &
   Actions"). 12 categories: Events, Control, Movement, Timing, Drawing,
   Score/Lives/Health, Instance, Room, Values, Sound, Output, Game.
   **Verified live** via a headless `BlocklyConfigDialog` instantiation — no
   separate "Score" or "Grid" category exists *here*.

2. **The real Blockly toolbox's hardcoded `categories` JS dict**
   (`editors/object_editor/blockly/blockly_workspace.html`, `generateToolboxXml()`,
   ~line 3057): Events, Movement, Timing, Drawing, Score/Lives/Health,
   Instance, Control, Room, Values, Output (10 keys) + Math + Logic always
   appended. No Sound (auto-generated into "Audio"), no Game.

3. **`registerCustomBlocks(actionDefs)`** (same file, ~line 3300) — called
   from `editors/object_editor/blockly_widget.py:_register_custom_blocks()`
   with **every** entry in `events/action_types.py`'s `ACTION_TYPES` at
   editor load. For any action name **not** already in the hardcoded
   `actionToBlockType` map (~line 2034), it auto-generates a block and files
   it under `def.category` **verbatim** — creating a **brand-new toolbox
   category** if that exact string isn't already a key in `categories`
   (source #2). It only merges into an existing category if the string
   matches one of #2's keys exactly.

**This is where the duplicates actually come from.** In
`events/action_types.py`, several actions carry a `category` that doesn't
match any key in source #2, and aren't in `actionToBlockType`, so they leak
into their own stray dynamic category:

| Action | `category=` in action_types.py | In `actionToBlockType`? | Result |
|---|---|---|---|
| `test_health`, `show_highscore`, `test_score`, `test_lives`, `clear_highscore` | `"Score"` | No | **stray "Score" category**, duplicate of hardcoded "Score/Lives/Health" |
| `test_alignment` | `"Grid"` | No | **stray "Grid" category**, duplicate/sibling of "Movement" (which already holds `move_grid`/`stop_if_no_keys`/`if_on_grid`/`snap_to_grid` via `actionToBlockType` mappings) |
| `restart_game` | `"Game"` | No | stray "Game" category (grey, uncolored — `categoryColors` in `registerCustomBlocks` has no "Game" entry), containing only this one action. Not raised by the user but same root cause. |
| `game_end` | `"Room"` | No | **correctly merges** into the existing "Room" category (string matches exactly) — not a bug. |
| `set_score`, `set_lives`, `set_health`, `draw_score`, `draw_lives`, `draw_health_bar`, `snap_to_grid`, `stop_if_no_keys`, `if_on_grid` | `"Score"`/`"Grid"` | **Yes** | Already mapped to a hardcoded block (`score_set` etc.) — `registerCustomBlocks` skips them (`if (actionToBlockType[actionName]) continue;`), so they never reach the stray category. |

The **Output vs Drawing** split is different in kind: it's not a dynamic
leak, it's a **real, static, intentional split** present identically in all
three sources (BLOCK_REGISTRY, the toolbox `categories` dict, and the dialog's
own `BLOCKLY_CATEGORY_COLORS`) — `output_message`/`execute_code` vs
`draw_text`/`draw_rectangle`/`draw_circle`/`set_sprite`/`set_alpha`. The user's
ask to merge these is a straightforward category consolidation, not a bug fix.

## BLOCK_REGISTRY is itself wrong relative to the real toolbox

Checked which of the leaking/stray action names even appear in
`BLOCK_REGISTRY` at all (so the config dialog can toggle them):
`test_health`, `test_score`, `test_lives`, `test_alignment` — **absent
entirely** (not in BLOCK_REGISTRY under any category, so the config dialog
can't show/hide them even though they're real, visible toolbox blocks).
`show_highscore`, `clear_highscore`, `restart_game`, `game_end` **are** in
BLOCK_REGISTRY, filed under "Game" — but in the real toolbox they actually
land in "Score" (stray), "Score" (stray), "Game" (stray, alone), "Room"
(merged) respectively. So BLOCK_REGISTRY's "Game" grouping doesn't correspond
to where these blocks actually end up — this is exactly the "categories do
not correspond" complaint, independent of the three explicit merge requests.

## Proposed fix (not yet implemented)

1. **`events/action_types.py`**: change `category=` on the leaking actions
   so they match an *existing* real toolbox category string exactly:
   - `test_health`, `show_highscore`, `test_score`, `test_lives`,
     `clear_highscore`: `"Score"` → `"Score/Lives/Health"`.
   - `test_alignment`: `"Grid"` → `"Movement"`.
   - `output_message`'s action (likely `show_message`) and `execute_code`:
     merge "Output" → "Drawing" at the source too, if they carry an explicit
     category field (need to check — `show_message` is mapped via
     `actionToBlockType['show_message'] = 'output_message'` already, so it
     won't leak either way; the merge for Output/Drawing is really about the
     **hardcoded** categories, not a leak).
   - Leave `restart_game` (`"Game"`) as a separate, smaller follow-up — not
     in the user's explicit list; needs its own decision (fold into "Room"?
     into "Score/Lives/Health" alongside the highscore actions? keep as-is
     but give it a real color?).

2. **`registerCustomBlocks`'s `categoryColors` map** (blockly_workspace.html
   ~line 3310): add `'Score/Lives/Health': '#5CA65C'` (currently only has
   stray `'Score'`/`'Scoring'` keys — check if anything else still relies on
   those before removing them) so merged dynamic blocks get the right color
   instead of falling back to grey/wrong.

3. **Static "Output"/"Drawing" merge** — needs changes in lockstep across:
   - `config/blockly_config.py` `BLOCK_REGISTRY["Drawing"]` (absorb
     `output_message`, `execute_code`; delete the `"Output"` key).
   - `dialogs/blockly_config_dialog.py` `BLOCKLY_CATEGORY_COLORS` (drop
     `"Output"` entry).
   - `editors/object_editor/blockly/blockly_workspace.html`'s `categories`
     JS dict (~line 3187 `'Output': {...}`) — merge its block list into the
     `'Drawing'` entry (~line 3063) and delete the `'Output'` key.
   - `config/blockly_translations.py` — check for an `"Output"` category
     translation entry and fold/remove it; confirm `"Drawing"` already has
     full per-language coverage.
   - The static embedded `<category name="Output" ...>` XML near line 524 of
     blockly_workspace.html too, if that block is still live (unclear whether
     it's dead code superseded by `generateToolboxXml` — **needs checking
     before deleting**, per this repo's "verify before claiming dead code"
     discipline).

4. **BLOCK_REGISTRY "Game" category reconciliation** — move `show_highscore`
   /`clear_highscore` into "Score/Lives/Health" (to match where they'll now
   really land after step 1), and decide what to do with `game_end`
   (really lands in "Room") and `restart_game` (stray "Game", alone) so the
   config dialog's categories genuinely correspond to the real toolbox. This
   is the part of the user's *first* sentence ("should correspond to the
   actual blockly editor Blocks") that goes beyond the three named merges.

5. Add `test_health`/`test_score`/`test_lives`/`test_alignment` to
   BLOCK_REGISTRY (currently entirely absent — real, visible toolbox blocks
   the config dialog can't toggle today) under their new homes
   ("Score/Lives/Health" and "Movement" respectively).

6. Regression test: headless `BlocklyConfigDialog` category dump (the
   technique already used this session) + a headless `QWebEngineView` real
   toolbox dump (dump category names from `generateToolboxXml({})` /
   `workspace.getToolbox()`) asserting the two sources' category sets match,
   and that "Score"/"Grid"/"Output" no longer appear as independent
   categories.

## Verification commands used this session (reusable)

```bash
# Dump the config dialog's real category/block tree:
QT_QPA_PLATFORM=offscreen venv/bin/python3 -c "
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])
from dialogs.blockly_config_dialog import BlocklyConfigDialog
dlg = BlocklyConfigDialog()
tree = dlg.tree
for i in range(tree.topLevelItemCount()):
    cat = tree.topLevelItem(i)
    print('CATEGORY:', cat.text(0))
"

# Find every ActionType's name + category pairing:
python3 -c "
import re
text = open('events/action_types.py').read()
pattern = re.compile(r'\"([a-zA-Z0-9_]+)\":\s*ActionType\(', re.M)
matches = list(pattern.finditer(text))
for idx, m in enumerate(matches):
    start = m.end()
    end = matches[idx+1].start() if idx+1 < len(matches) else len(text)
    catm = re.search(r'category=\"([^\"]+)\"', text[start:end])
    print(m.group(1), '->', catm.group(1) if catm else None)
"
```

## Status (superseded by Resolution below)

Pure investigation, zero files edited. Next session: implement steps 1-6
above, one commit per logical cluster (matching this repo's audit-commit
discipline), with a regression test for each, full suite green before
pushing.

## Resolution (2026-10-15/16)

All six proposed-fix steps implemented, `restart_game`/`game_end`
deliberately left exactly as proposed (separate, undecided follow-up, not
in the user's explicit ask).

- **Step 1** (`events/action_types.py`): `test_health`, `show_highscore`,
  `test_score`, `test_lives`, `clear_highscore` → `category=
  "Score/Lives/Health"`; `test_alignment` → `category="Movement"`.
- **Step 2** (`blockly_workspace.html` `categoryColors`): added
  `'Score/Lives/Health': '#5CA65C'`.
- **Step 3** (Output → Drawing, across all four files): done. Also found
  and fixed a genuinely separate bug while merging: `execute_code` had NO
  `<block type="execute_code">` entry anywhere in the real (post-load)
  toolbox — only in the static pre-load XML every real page load replaces
  — so it was undraggable. Fixed by adding it alongside `output_message`
  under the merged "Drawing" category (both the generated `categories`
  dict and the static initial toolbox), and moving it from
  `GENERATED_ACTION_NAMES` to `PROMOTED_TO_HAND_WRITTEN_BLOCKS` (now a
  real hardcoded block, same mechanism `test_expression`/`move_towards`
  already use). The generic `text`/`text_join` value blocks turned out to
  have the identical orphan problem but were deliberately NOT fixed —
  logged in `TODO.md` instead, since where they belong is its own design
  question, not a mechanical consequence of this fix.
- **Step 4**: `show_highscore`/`clear_highscore` moved from BLOCK_REGISTRY
  `"Game"` to `"Score/Lives/Health"`. `game_end`/`restart_game` left in
  `"Game"` as proposed — explicitly deferred, not part of the user's ask.
- **Step 5**: `test_health`/`test_score`/`test_lives` added to
  BLOCK_REGISTRY under `"Score/Lives/Health"`; `test_alignment` added
  under `"Movement"` — all four were previously entirely absent from
  BLOCK_REGISTRY despite being real, visible toolbox blocks.
- **Step 6**: `tests/test_blockly_category_mismatch_fix.py` (21 tests) —
  real-toolbox category-key dump (static source parse, no Node needed),
  static-vs-generated toolbox consistency, the `execute_code` orphan fix,
  `BLOCK_REGISTRY` content checks, a live headless `BlocklyConfigDialog`
  category dump, every `BlocklyConfig` preset's `enabled_categories`, and
  the translation/color-map cleanups.
- Also fixed in passing: the six `BlocklyConfig` presets (`get_beginner`,
  `get_grid_rpg`, `get_sokoban`, `get_testing`, `get_code_editor`,
  `get_blockly_editor`) that referenced `"Output"` in `enabled_categories`
  — three already had `"Drawing"` too (just dropped the redundant
  `"Output"`), three only had `"Output"` (swapped to `"Drawing"`; verified
  behaviour-preserving since block-level visibility is governed separately
  by `enabled_blocks`, not the category list, and none of those three
  individually enabled any other Drawing block like `draw_text`).
  `config/blockly_translations.py`'s `"Output"` entries removed from all 7
  languages; `dialogs/blockly_config_dialog.py`'s `BLOCKLY_CATEGORY_COLORS`
  `"Output"` entry removed.
- Full suite green throughout; targeted blockly/toolbox/extension/thymio
  subset (473 tests) and the new regression file verified on every step.

## Resolution, part 2 (2026-10-16): the "Game" category + text/text_join

Picked up the two things part 1 deliberately left untouched. Presented as
two decisions with options; user picked the recommended one for each:
**B** (proper fix: split by what the actions actually are, give "Game" a
real color) for the Game category, and **A** (own small always-on
category, same as Math/Logic) for `text`/`text_join`.

**The "Game" category was bigger than part 1 assumed.** Re-auditing
`actionToBlockType` against every `ActionType.category == "Game"` found
not 1 but **20** actions carrying that category, of which **19 genuinely
leak** (not hardcoded-mapped) into one grey, uncolored, category-gating-
exempt dynamic box: **11 are really Drawing actions**
(`draw_arrow`, `draw_background`, `draw_ellipse`, `draw_line`,
`draw_scaled_text`, `draw_sprite`, `draw_variable`, `fill_color`,
`set_color`, `set_draw_color`, `set_draw_font`) and **9 are genuine
game-lifecycle actions** (`restart_game`, `load_game`, `save_game`,
`open_webpage`, `set_window_caption`, `show_info`, `show_video`,
`splash_show_image`, `splash_show_text`). `game_end` already correctly
lands in "Room" and was never part of the mess.

- The 11 drawing-ish actions: `category=` changed `"Game"` -> `"Drawing"`
  in `events/action_types.py`, merging in via the same mechanism as part
  1's Score/Grid fixes.
- The 9 lifecycle actions: left at `category="Game"`; `"Game"` itself
  promoted from a stray dynamic fallback to a real, colored (`#607D8B`)
  category in `blockly_workspace.html` (both the generated `categories`
  dict and `categoryColors`).
- `BLOCK_REGISTRY` (`config/blockly_config.py`) updated to match: the 11
  drawing-ish actions added under `"Drawing"`; the 8 remaining lifecycle
  actions (`restart_game` was already listed) added under `"Game"`;
  `game_end` moved from `"Game"` to `"Room"` (where it always really
  landed) -- the loose end part 1's "Resolution" explicitly deferred.

**Regression found and fixed before it shipped: promoting "Game" to a
real category silently hid its blocks in 4 presets.** The OLD stray-
category rendering path (`blockly_workspace.html`'s second toolbox-
building loop) filtered purely by `enabledBlocks` -- no `enabledCategories`
check at all, since a stray category was never something a preset could
even name to toggle. Making "Game" real moves it into the FIRST loop,
which gates the whole category box on `enabledCategories.has('Game')`
first. Auditing all 10 `BlocklyConfig` presets found `get_platformer`,
`get_grid_rpg`, `get_sokoban` and `get_testing` all had the 9 lifecycle
actions in `enabled_blocks` (via the blanket `GENERATED_ACTION_NAMES |
PROMOTED_TO_HAND_WRITTEN_BLOCKS` union) but no `"Game"` in
`enabled_categories` -- would have silently lost Restart Game and friends.
`get_platformer` also lacked `"Drawing"` entirely. Fixed by adding the
missing categories to each preset's `enabled_categories` literal (verified
none of the four explicitly enable any of Drawing's OTHER, unrelated
hardcoded blocks like `draw_text`/`output_message`, so this doesn't newly
expose anything beyond what was intended).

**Same regression risk existed for users' saved custom Blockly configs on
disk**, which `load_config()`'s migration never addressed (only
`enabled_blocks`, never `enabled_categories`). Since `"Game"` never
existed as a real, toggleable category before this fix, NO saved config
could ever have had it enabled. Fixed with a new `config_version < 3`
migration (the existing `< 2` one stays for the original
`GENERATED_ACTION_NAMES` gap): adds `"Game"` to `enabled_categories`
whenever any of the 9 lifecycle actions is already in `enabled_blocks`.
`BlocklyConfig.config_version`'s dataclass default bumped `2` -> `3` so
freshly-constructed configs (already current) skip it.

**`text`/`text_join`**: added as an always-on "Text" category
(`#4FA8A8`), inserted right after "Math"/"Logic" in both the generated
toolbox and the static pre-load one -- exact same unconditional-append
precedent, not gated by any preset's `enabled_categories` (matching
Math/Logic, which also have no `BLOCK_REGISTRY` entry).

**Three more findings surfaced while writing the regression tests for
this part, deliberately NOT fixed here** (reported to the user, logged in
`TODO.md`):
- `"Particles"` (8 actions) and `"Views"` (2 actions) are a separate,
  not-yet-decided instance of the *exact same* stray-category bug --
  clean, single-purpose groups, no mixed-category untangling needed,
  structurally the simplest of the three found so far.
- `get_platformer` has silently hidden its Control- and Timing-category
  generated blocks (12 + 7 actions) since the preset was written --
  unrelated to the stray-category bug class (Control/Timing are real,
  correctly-named categories), just `enabled_categories` never listing
  them despite `enabled_blocks` including their actions. Found while
  scoping the new regression test tightly enough to not fail on this
  unrelated, pre-existing gap.

New tests: `tests/test_blockly_category_mismatch_fix.py` grew to 51 (from
21); `tests/test_blockly_preset_generated_actions.py` gained 4 (the
category/migration regression guards, deliberately scoped to only
Game/Drawing -- see its own docstring for why a broader version was
tried and reverted). `editors/object_editor/blockly/blockly_i18n.js`'s
separate `CATEGORY_MESSAGES` table (5 languages, a different i18n system
than part 1's `config/blockly_translations.py`) also had a dangling
`"Output"` entry part 1 missed -- removed, with
`test_blockly_i18n_{pl,uk}.py`'s pinned counts updated. Full suite:
**6179 passed, 0 failed, 13 skipped.**

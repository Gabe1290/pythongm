# Blockly toolbox / "Configure Action Blocks..." category mismatch

Investigation only — **no code changes made yet**. Picks up the user's
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

## Status

Pure investigation, zero files edited. Next session: implement steps 1-6
above, one commit per logical cluster (matching this repo's audit-commit
discipline), with a regression test for each, full suite green before
pushing.

# Block World — Crafting

A small voxel world built on the **Block World** extension
(`extensions/block_world/`), demonstrating its Tier 8 crafting actions
(`docs/BLOCK_WORLD_CRAFTING_PLAN.md`): `Set Crafting Recipe` and
`Craft Item`.

**The goal:** mine clay from the vein in the east wall, craft it into
bricks, and carry at least 4 bricks to the gold beacon back toward the
middle of the room. Walking there with enough bricks in your inventory is
all it takes to win — no block-placement puzzle, no precision aiming.
Reaching the beacon without enough bricks does nothing; keep mining and
crafting. The vein is 4 blocks wide, so you'll need to step sideways
(`W`/`S`) along the wall to reach each one — one `Space` press only ever
breaks whichever single block you're directly facing.

## Controls

|  | |
|---|---|
| `W` `A` `S` `D` | Move (north/south/west/east — map-direction, not look-direction) |
| Left / Right arrow | Turn to look left/right |
| Up / Down arrow | Look up/down |
| `Space` | Break the block you're aiming at (mine clay from the wall vein) |
| `C` | Craft: turns 4 clay in your inventory into 4 bricks, if you have enough |
| `H` | Show or hide the controls (shown when you start) |

**Movement is map-direction, not look-direction** — same convention as
`block_world_1`/`block_world_2`: pressing `D` always walks east, whichever
way the camera happens to be facing.

## What it demonstrates

- **`Set Crafting Recipe`**, called once in `create` right after
  `Enable Block World View`: 4 `clay` → 4 `brick`, a single-input recipe
  (the plan's own simplest worked example).
- **`Craft Item`**, bound to a key (`C`): attempts the registered recipe
  against the player's own inventory (`Enable Block World View`'s
  **Inventory** parameter is on, the same Tier 7c mechanism `Break Block`/
  `Place Block` already use) — all-or-nothing, so pressing `C` with fewer
  than 4 clay does nothing rather than partially consuming what you have.
- **The built-in inventory HUD** (`Draw Block World HUD`) — no custom
  crafting UI needed; your crafted brick count shows up on the hotbar
  strip like any other block type, since crafting outputs are ordinary
  block types, not a separate "item" concept.
- **A world loaded from data**: `blocks/room0.json` (built by the
  committed `tools/gen_block_world_3_room.py` generator) is loaded by a
  `load_block_world` action in the player's `game_start` event, same
  pattern as `block_world_1`.

## Why the goal doesn't require placing anything

`block_world_1`'s own README explains why an earlier design asking the
player to *build* a bridge/staircase to reach a goal was rejected — it
needed a fiddly combination of look-angle and distance to place blocks
reliably. This sample sidesteps that risk entirely: the win condition is
just "have you crafted enough, and are you standing near the right spot"
— both checked by reading the player's own inventory and position, no
placement precision involved anywhere.

## Why the clay is embedded in the wall, not a free-standing mound

A real playtest against a running `GameRunner` (not just reading the
code) found two things the first two versions of this world got wrong,
both worth knowing if you're building your own Block World level:

1. A free-standing clay patch sitting on the open floor, exactly one
   layer tall, was never actually mined during normal play — the engine
   treats any one-layer obstruction as a **climbable step**
   (`state.DEFAULT_MAX_STEP_UP`), so walking toward it just auto-stepped
   the player up onto it instead of blocking them the way a real obstacle
   would. Once standing on top, the level-aim ray sailed clean over it.
2. Stacking the patch two layers high fixed that (correctly unclimbable),
   but then only the *bottom* layer was ever minable at level pitch — a
   body's resting height above a floor block is one layer *above* the
   floor, so a level-pitch ray from the ground targets the layer *above*
   where you might expect, not the very first one.

Embedding the vein in the wall's own middle layer (with the layers above
and below it left as ordinary wall) sidesteps both problems in one move:
the wall stays fully unclimbable (so you're never routed onto or over
it), and its clay sits at exactly the height a level-pitch aim from the
floor reaches — the same "approach a wall, aim level, `Space`"
interaction `block_world_1`'s own perimeter wall already exercises, no
new interaction to get right.

## Engine status

Crafting is fully ported to all three of Block World's targets — desktop
(pygame), HTML5, and Kivy (Android/desktop app export) — with a
cross-engine parity test (`tests/test_block_world_crafting_export_parity.py`)
pinning identical behaviour between desktop and Kivy.

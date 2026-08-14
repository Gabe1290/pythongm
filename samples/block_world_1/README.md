# Block World — Level 1

A small voxel world built on the **Block World** extension
(`extensions/block_world/`) — the same "inspired by, not copied from"
territory Luanti/Minetest occupy, built from scratch with a CC0 texture set
(see `extensions/block_world/ASSETS.md`), not a clone of any existing game.

**The goal:** climb the staircase to the golden beacon block at the top of
the terrace. That's it — walking there is enough to win. You can also dig
and build anywhere in the world along the way; nothing about winning
requires it.

## Controls

|  | |
|---|---|
| `W` `A` `S` `D` | Move (north/south/west/east — see note below) |
| Left / Right arrow | Turn to look left/right |
| Up / Down arrow | Look up/down |
| `Space` | Break the block you're aiming at |
| `Shift` | Place a block from your hotbar |
| `Q` / `E` | Cycle your hotbar selection |

**Movement is map-direction, not look-direction.** Pressing `D` always
walks east, whichever way you're currently facing — turning the camera
(the arrow keys) only changes what you *see*, not which way `WASD` moves
you. This is a deliberate simplification: aiming a movement key at
wherever the camera happens to be facing needs trigonometry this engine's
simple action-parameter expressions don't support yet, and "look around
freely, walk on the map's compass" is a perfectly normal control scheme
for a lot of real games — not a corner cut to get this sample out the
door.

## What it demonstrates

- **Stacking blocks and stepping up onto them** — the whole reason the
  in-game camera is a two-block-tall body (`eye_height`): from the ground,
  you can see the top of a block right beside you and build straight up.
  The staircase you climb to reach the beacon is pre-built, but you're
  free to build your own next to it.
- **Breaking and placing**, bound to real keys, with your current
  selection tracked by a hotbar (`Q`/`E` to cycle it).
- **A world loaded from data**, not hand-placed: `blocks/room0.json`
  (built by the committed `tools/gen_block_world_1_room.py` generator) is
  loaded into the room by a `load_block_world` action in the player's
  `game_start` event.

## Why the goal doesn't require placing a specific block

An earlier design for this sample had you *build* a bridge across a pit to
reach the goal. It turned out to need looking sharply downward at exactly
the right distance to place blocks at foot level — a real, working
mechanic (`Up`/`Down` to look, then `Shift` to place), but one that made
the sample's own completion depend on a fiddly combination of angle and
distance most players would find frustrating on a first try. Climbing a
pre-built staircase by walking is guaranteed to work and still shows off
the engine's stacking/stepping mechanics — building your own additions is
there to explore, not required to finish.

## Engine status

This sample runs on Block World's desktop (pygame) engine —
Phases 0 through 5 of `docs/VOXEL_WORLD_PLAN.md`. HTML5 and Kivy export
support (Phase 6) is tracked separately in that same plan doc.

# Maze — Level 4

The largest maze sample: **21 rooms** of grid-maze puzzles with **conveyor
tiles**, three kinds of **monster**, **bombs/explosions** that blow through
walls, a **power-ring** that scares the monsters, and collectibles
(diamonds, rings, hearts). A native pygm2 project imported from `maze_4.gmk`
(GameMaker 8.x), authored/saved in pygm2's own JSON format.

**Where this fits:** the fourth `maze_*` level and the most mechanically rich —
it layers conveyor movement, multiple enemy types, a scare/eat power-up loop,
and a destructible-wall bomb onto the basic grid movement of `maze_1..3`. It
was dropped in rc.12 for GMK-import bugs and **re-added after the importer
hardening** (2026-07-16); see
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
and [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Sound & music:** 10 sound effects are bundled. One legacy GM8-era track
(`sound_background`) is in a format pygame can't load and is skipped at runtime
(same as maze_2/maze_3); gameplay is unaffected.

## How to play

- **Arrow keys** move the player one grid cell at a time; walls block movement.
- **Conveyor tiles** (up/down/left/right arrows on the floor) carry the player
  automatically in their direction while standing on them.
- **Monsters** come in three kinds (`monster_all` roams freely; `monster_ud`
  patrols vertically; `monster_lr` horizontally) — touching one costs a life
  and restarts the room.
- Grab a **ring** and every monster turns **afraid** (sprite changes, they
  freeze) for ~10 seconds — touch one then to eat it for points; they revert
  when the timer runs out.
- **Bombs** explode into a blast that **destroys the surrounding walls** —
  used to open otherwise-sealed sections.
- Collect **diamonds/rings/hearts**; reach the **goal** to advance. The HUD
  (score + lives) is drawn along the bottom by `controller_main`.

## A note on the hand-patch (honest documentation)

pygm2's movement *slides to contact* with a wall, whereas GameMaker 8 *reverts*
a blocked move to the pre-move position — the GM behavior kept the player
grid-aligned for free. Without it, pressing into a flush wall left the player a
few pixels off the 32-grid, and the grid-gated movement/conveyor checks then
wedged it. So `obj_person` carries a deliberate **gameplay hand-patch**:
`snap_to_grid(32)` on its `wall_corner`/`wall_horizontal`/`wall_vertical`
collision events. This mirrors the same patch shipped in `maze_1` and is a fix,
not a fidelity change — a fresh import from the `.gmk` will not include it (see
below).

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Manifest — window/room settings, embedded assets, and room order |
| `rooms/*.json` | 21 rooms; play order `room_start` then descending runs (`room14`, `room13`, …) — the original game's own order, faithfully imported |
| `objects/*.json` | 24 object definitions (source of truth; merged over the embedded copies at load) |
| `sprites/` | 24 sprite PNGs + `.json` metadata |
| `sounds/` | 10 sound effects |
| `backgrounds/` | 2 backgrounds |
| `CREDITS.txt` | Asset licensing notice |

## Objects (24)

Player/HUD: `obj_person`, `controller_main` (draws score+lives), `controller_start`.
Walls: `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Enemies: `monster_all`, `monster_ud`, `monster_lr`.
Power-ups / items: `ring` (scare), `bomb` + `explosion` (destroy walls),
`obj_diamond`, `heart`, `bonus`, `obj_door`, `obj_goal`, `trigger`, `hole`.
Conveyor tiles: `move_up`, `move_down`, `move_left`, `move_right`.

## Assets

24 sprites, 10 sounds, 2 backgrounds, 1 font — all imported from `maze_4.gmk`.
See `CREDITS.txt` and
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) for provenance.

## Things to tweak

- **Conveyor / player speed** — conveyors move at speed `8`; keyboard grid
  moves at `4` (per-action params on `obj_person`).
- **Scare duration** — the ring's `set_alarm` is `300` steps on `monster_all`.
- **Room order** — rooms play in `project.json`'s room-dict key order; reorder
  them in the IDE (drag in the resource tree) and Test Game follows.

## Export status

Covered by the headless smoke-test suite (`tools/smoke_run_samples.py`, which
lists `maze_4`) and the import regression suite
(`tests/test_gmk_treasure_maze4_import.py`). Verified in a manual playtest
during the 2026-07 importer hardening (see the testing-pass doc). Exposed in
the Welcome tab as **"Maze — Level 4"**.

## Regenerating from the `.gmk` original

The sibling `../maze_4.gmk` is the GameMaker 8.x source:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

A fresh import is faithful to the original game, **minus** the `snap_to_grid`
wall hand-patch described above — re-apply it (add `snap_to_grid` grid_size 32
to `obj_person`'s three wall-collision events) after regenerating.

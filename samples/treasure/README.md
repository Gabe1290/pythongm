# Treasure

A Pac-Man-style maze chase: the **explorer** roams a walled maze collecting
**treasure points**, chased by **monsters** that pick a fresh direction at each
crossing. Grab a **power pill** (`pil`) and the tables turn — every monster
becomes **scared** and can be eaten for bonus points until the effect wears
off. This is a native pygm2 project imported from `treasure.gmk` (GameMaker
8.x); the project itself is authored/saved in pygm2's own JSON format.

**Where this fits:** `treasure` sits alongside the `maze_*` family — built from
GameObjects + built-in actions and the visual event editor — but adds a
**project-level script** (`adapt_direction`, the monster's crossing AI) and a
GM-style **"chase / power-up / flee"** state loop across its objects. It was
one of the two samples dropped in rc.12 for GMK-import bugs and **re-added
after the importer hardening** (2026-07-16); see
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
and [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Sound & music:** 6 sound effects are bundled (pickup, power-pill, eat-monster,
death, …). One legacy GM8-era track (`music`) is in a format pygame can't
load and is skipped at runtime — same as the other maze samples' background
music; gameplay is unaffected.

## How to play

- **Arrow keys** move the explorer through the maze; walls block movement.
- Collect every **treasure point** to clear the level (4 rooms total).
- **Monsters** chase you; touching one normally costs a life.
- Grab a **power pill** and monsters turn **scared** (they change sprite) for a
  few seconds — touch a scared monster to **eat it** (+points; it teleports
  back to its start as a normal monster). The effect reverts on a timer.

## The monster AI (`adapt_direction` script)

Each monster calls the project script `adapt_direction` from its step/collision
events. It's real pygm2 Python — at a possible crossing it randomly considers
turning, checking `game.check_collision_at_position(...)` for a wall before
committing, so monsters wander the maze instead of running in straight lines.
Open the **Scripts** asset to read it; the `execute_script` action in the
monster's events shows where it's called.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Manifest — window/room settings, embedded assets, the `adapt_direction` script, and room order |
| `rooms/room0..3.json` | The four maze levels (instances per room) |
| `objects/*.json` | The 7 object definitions (source of truth; merged over the embedded copies at load) |
| `sprites/` | 10 sprite PNGs + `.json` metadata |
| `sounds/` | 6 sound effects |
| `backgrounds/` | 1 background |
| `CREDITS.txt` | Asset licensing notice |

## Objects

| Object | Role |
|---|---|
| `explorer` | Player character; collects treasure, eats scared monsters, dies to normal ones |
| `monster` | Chaser; wanders via `adapt_direction`; turns into `scared` on a power pill |
| `scared` | A monster in its fleeing state; edible; reverts to `monster` on a timer |
| `pil` | Power pill — scares every monster when collected |
| `point` | Treasure to collect |
| `bonus` | Extra pickup |
| `wall` | Static solid maze wall |

## Assets

10 sprites, 6 sounds, 1 background — all imported from `treasure.gmk`. See
`CREDITS.txt` and [`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md)
for provenance.

## Things to tweak

- **Scare duration** — the power-pill alarm is `160` steps on `explorer`'s
  `collision_with_pil` event; raise it for a longer flee phase.
- **Monster turn chance** — the `random.random() * 3 < 1` tests in the
  `adapt_direction` script set how often monsters turn at a crossing.
- **Score values** — treasure and eat-monster points are `set_score`
  (relative) actions on the respective collision events.

## Export status

Covered by the headless smoke-test suite (`tools/smoke_run_samples.py`, which
lists `treasure`) and the import regression suite
(`tests/test_gmk_treasure_maze4_import.py` + `tests/test_gmk_applies_to.py`).
Verified in a manual playtest during the 2026-07 importer hardening (see the
testing-pass doc). Exposed in the Welcome tab as **"Treasure"**.

## Regenerating from the `.gmk` original

The sibling `../treasure.gmk` is the GameMaker 8.x source. To regenerate:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

A fresh import is faithful to the original game as of the 2026-07 importer
hardening (no hand-patches applied to this sample).

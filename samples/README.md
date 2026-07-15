# Bundled samples

These are the projects surfaced by the IDE's **Welcome tab → Try a sample
game** dropdown, plus an Aseba playground used by the testing checklists.

## Layout

Each game sample is a **native pygm2 project folder** (`project.json` +
asset subdirectories). Clicking a sample in the IDE copies the folder
into the user's `~/Documents/PyGameMaker Projects/` area (or a numbered
variant if a project of the same name is already there) and opens the
copy — the bundled folders themselves are never modified.

| Folder           | Origin                              | Notes                                            |
| ---------------- | ----------------------------------- | ------------------------------------------------ |
| `maze_1/`        | imported from a GameMaker 8.x .gmk  | 2 rooms, 3 objects, 3 sprites                    |
| `maze_2/`        | imported from a GameMaker 8.x .gmk  | 3 rooms, 9 objects, 7 sprites, 4 sounds          |
| `maze_3/`        | imported from a GameMaker 8.x .gmk  | 6 rooms, 17 objects, 16 sprites, 8 sounds        |
| `plateforme_1/`  | imported from a GameMaker 8.x .gmk  | platformer · art from Pingus, GPLv3+ †           |
| `plateforme_2/`  | imported from a GameMaker 8.x .gmk  | platformer · art from Pingus, GPLv3+ †           |
| `plateforme_3/`  | imported from a GameMaker 8.x .gmk  | platformer · art from Pingus, GPLv3+ †           |
| `match3_1/`      | authored natively in pygm2          | match-3 puzzle · 1 room, 1 object, pure `execute_code` · see its `README.md` ‡ |
| `match3_2/`      | authored natively in pygm2          | match-3 puzzle · sprites, sound, swap animation, pure `execute_code` · see its `README.md` ‡ |
| `match3_3/`      | authored natively in pygm2          | match-3 puzzle · move limit, 3 levels, special tiles, pure `execute_code` · see its `README.md` ‡ |
| `maze.playground`| Aseba playground (for Thymio tests) | XML file, used by `File → Open Playground`       |

## Progression: how each family is *built*, not just how it plays

The three sample families are a rough progression in **authoring technique**,
each one adding something the previous family didn't use. Every sample's own
`README.md` states its specific facts (object/sprite/tile/sound counts,
whether any bundled sound is actually wired up); this section is the
one-time explanation of the pattern across all of them.

1. **`maze_*`** — the basic building blocks: GameObjects (each with a
   sprite) composed from built-in actions and wired together via the
   visual event editor (create/step/collision/keyboard events). `maze_2`
   and `maze_3` add a static **background image** per room (a single image
   layer, e.g. `background_main`) behind the objects. No sample in this
   family uses the room-level tile system.
2. **`plateforme_*`** — everything `maze_*` uses, plus (in `plateforme_2`
   and `plateforme_3` — not the minimal `plateforme_1`) a **tiled
   background**: the room's `tiles` array places individual background
   tile chunks (125-127 of them) under the object instances, layered with
   its own background image (`fond_degrade`, a gradient) — a decorative
   layer distinct from, and in addition to, the solid brick *objects* that
   still handle collision. This is the room-authoring step maze doesn't
   use at all.
3. **`match3_*`** — a different paradigm, not an incremental addition: no
   built-in actions, no per-tile objects, no room-level tiles. The whole
   game in each is a handful of `execute_code` (raw Python) events on a
   single controller object — grid state, collision, rendering (via the
   runtime's draw-queue) and, from `match3_2` on, sound (via the
   cross-platform sound-queue primitive) are all driven directly from
   code rather than composed from built-in actions across many objects.

‡ `match3_1/`, `match3_2/`, and `match3_3/` are authored directly in the
native format (no `.gmk` origin, so the "Regenerating" section below does
not apply to them) — the whole game in each is a handful of `execute_code`
events on a single controller object, no built-in actions at all, which is
a different authoring style from every other sample here (all of which
compose built-in actions across many objects). match3_2 adds sprite tiles,
sound effects, and a swap animation over match3_1; match3_3 adds a move
limit, three rooms as rising-target levels, and special tiles. Each
sample's gameplay, code architecture, and export status are documented in
its own `README.md` — Android/Kivy export is supported since 2026-07-03
(the draw-queue + touch support in the Kivy exporter was added for
match3_1). Tile sprites and sound effects are CC0 (see each sample's
`CREDITS.txt`).

† The `plateforme_*` image assets are taken from [Pingus](https://pingus.seul.org/)
and are licensed **GPL-3.0-or-later**, *not* the project's MIT license. Each
folder carries a `CREDITS.txt`; the full terms, scope, and artist credits are in
[`docs/ASSET_LICENSES.md`](../docs/ASSET_LICENSES.md), and the license text is at
[`licenses/GPL-3.0.txt`](../licenses/GPL-3.0.txt). In `maze_1/`, the
author-created `spr_person.png` and `spr_wall.png` are dedicated to the public
domain under **CC0-1.0** (see `maze_1/CREDITS.txt` and
[`licenses/CC0-1.0.txt`](../licenses/CC0-1.0.txt)); the remaining maze-sample
art provenance is still to be documented.

`plateforme_4/` and `plateforme_5/` (platformers using the same Pingus art
as `plateforme_1..3/`) were removed from the bundled set for the same
reason: real leftover import debt (e.g. a `test_score` action still
carrying a raw, un-translated GML operation code instead of a named
comparison) that hadn't been cleaned up. Their `.gmk` sources
(`samples/plateforme_4.gmk`, `samples/plateforme_5.gmk`) are still
tracked, so they can be regenerated and re-added once that cleanup is
done — see "Regenerating from `.gmk` originals" below.

Two further samples (`treasure/` and `maze_4/`) shipped briefly in
rc.12 but were dropped after user testing surfaced enough GMK-import
edge cases (bad action parameters, sprite issues, half-converted
events) that the IDE could only partially round-trip them. Both can
be reintroduced by running the regeneration steps below against the
original `.gmk` source once the importer is hardened against those
cases — see `TODO.md` ("GMK importer hardening") for the
investigation recipe.

## Regenerating from `.gmk` originals

The folders above were produced by running `importers/gmk_importer.py`
against a set of GameMaker 8.x source files (`maze_1.gmk` etc.). Most of
the `.gmk` sources **are** committed alongside this README
(`samples/maze_3.gmk` and `samples/plateforme_1..5.gmk`) — the global
`*.gmk` ignore rule has a `!samples/*.gmk` exception so they stay tracked
and the import is auditable. The `maze_1.gmk` / `maze_2.gmk` sources are
not currently committed. If the conversion ever needs to be redone:

1. Place any missing `.gmk` files next to this README. Files under
   `samples/` are exempt from the global `*.gmk` ignore, so they will be
   tracked once committed.
2. Run something like:

   ```bash
   python -c "
   from importers.gmk_importer import import_gmk_detailed
   import_gmk_detailed('samples/maze_1.gmk', 'samples/maze_1')
   "
   ```

3. Commit the regenerated `samples/<name>/` folder.

## Why ship them as native projects rather than `.gmk`?

The Welcome tab used to run the GMK importer at click time and ask the
user where to save the result. Two problems:

- The import step took several seconds and depended on the importer
  staying bug-free.
- The "choose destination" dialog up front felt like friction for a
  "just let me try the sample" interaction.

Pre-converting once and shipping the native projects fixes both — and
makes diffs reviewable in git, which `.gmk` (binary) is not.

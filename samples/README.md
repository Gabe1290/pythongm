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
| `plateforme_4/`  | imported from a GameMaker 8.x .gmk  | platformer · art from Pingus, GPLv3+ †           |
| `plateforme_5/`  | imported from a GameMaker 8.x .gmk  | platformer · art from Pingus, GPLv3+ †           |
| `match3_1/`      | authored natively in pygm2          | match-3 puzzle · 1 room, 1 object, pure `execute_code` · see its `README.md` ‡ |
| `maze.playground`| Aseba playground (for Thymio tests) | XML file, used by `File → Open Playground`       |

‡ `match3_1/` is the first sample authored directly in the native format
(no `.gmk` origin, so the "Regenerating" section below does not apply to
it). Its gameplay, code architecture, planned advanced versions, and
export status (including the current Android/Kivy limitations) are
documented in [`match3_1/README.md`](match3_1/README.md) — Android/Kivy
export is supported since 2026-07-03 (the draw-queue + touch support in
the Kivy exporter was added for this sample); its four tile sprites are
CC0 (see `match3_1/CREDITS.txt`).

† The `plateforme_*` image assets are taken from [Pingus](https://pingus.seul.org/)
and are licensed **GPL-3.0-or-later**, *not* the project's MIT license. Each
folder carries a `CREDITS.txt`; the full terms, scope, and artist credits are in
[`docs/ASSET_LICENSES.md`](../docs/ASSET_LICENSES.md), and the license text is at
[`licenses/GPL-3.0.txt`](../licenses/GPL-3.0.txt). In `maze_1/`, the
author-created `spr_person.png` and `spr_wall.png` are dedicated to the public
domain under **CC0-1.0** (see `maze_1/CREDITS.txt` and
[`licenses/CC0-1.0.txt`](../licenses/CC0-1.0.txt)); the remaining maze-sample
art provenance is still to be documented.

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

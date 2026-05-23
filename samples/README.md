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
| `maze_4/`        | imported from a GameMaker 8.x .gmk  | 21 rooms, 24 objects, 24 sprites, 10 sounds      |
| `treasure/`      | imported from a GameMaker 8.x .gmk  | 4 rooms, 7 objects, 10 sprites, 6 sounds         |
| `maze.playground`| Aseba playground (for Thymio tests) | XML file, used by `File → Open Playground`       |

## Regenerating from `.gmk` originals

The folders above were produced by running `importers/gmk_importer.py`
against a set of GameMaker 8.x source files (`maze_1.gmk` etc.). The
`.gmk` originals are *not* shipped here — they're regeneration sources,
not runtime artifacts. If the conversion ever needs to be redone:

1. Place the `.gmk` files next to this README (the global `*.gmk`
   gitignore rule keeps them out of commits even if you don't move them).
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

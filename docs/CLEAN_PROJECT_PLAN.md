# Plan: Clean Project (`TODO.md` / `docs/DEFERRED_ITEMS_PLAN.md` item 11)

Status: **Tiers 1 (`.tmp` orphan sweep) and 2 (orphaned physical file
detection) DONE, both 2026-08-09.** Only **Tier 3** (deletion UI for the
files Tier 2 finds) remains open — Tier 1's own deletion is already UI'd
(Tools → Clean Project) and unused-*entry* deletion already shipped as
Asset Manager Tier 4, so what's left is specifically surfacing Tier 2's
findings with a delete button. `TODO.md`'s own note says to
scope this *after* Asset Manager, since it overlaps that item's unused-asset
detection — Asset Manager Tier 1 (`utils/asset_usage.py`, done the same
session) unblocked this scoping pass. The "Why nothing shipped this pass"
section below was written assuming the shared undo-semantics question was
still open; it was settled the same day (see
`docs/ASSET_MANAGER_PLAN.md`'s "The bulk-delete-undo question — SETTLED"
section: a soft-delete Trash, `utils/asset_trash.py`, not a
`QUndoCommand`-based undo/redo). **Deleting anything through
`AssetManager.delete_asset` is now trash-backed and restorable**, so the
specific blocking reason below no longer applies — this item's own
sub-scope (the `.tmp` sweep, the orphaned-physical-file scan, and their
deletion UI) is simply not built yet, not blocked.

## What "Clean Project" actually means (from `TODO.md`)

> remove temporary files, delete unused assets, clean build artifacts,
> shrink project size

Four sub-scopes again, and investigation found the real situation is
different from what the one-line TODO summary suggests for at least two of
them.

## Investigation: what actually accumulates in a project directory

- **Rollback snapshots (`.<name>.bak-*`) — already handled, not a gap.**
  `core/project_manager.py`'s `_sweep_orphan_snapshots` runs automatically
  on every `load_project()` call and removes rollback directories orphaned
  by a prior crashed/killed save. "Clean Project" doesn't need to rebuild
  this.
- **`.tmp` sibling files from `_atomic_write_json`** — written before
  `os.replace` swaps them into place; a hard crash mid-write (power loss,
  `kill -9`) could theoretically orphan one. Genuinely rare in practice
  (the same class of landmine `CLAUDE.md` notes for the *IDE's own* repo
  during editing, not typically for a running game project), but a real,
  small, safe thing to sweep — these are unambiguously safe to delete (a
  `.tmp` file is never the authoritative copy of anything).
- **`__pycache__`/`*.pyc` — likely doesn't apply to a PyGameMaker project
  at all.** The TODO's workaround line ("manually delete `.cache/`,
  `__pycache__/`, `*.pyc`") describes cleaning *this development repo*,
  not a saved game project — a PyGameMaker project's Python code
  (`execute_code`/`execute_script` bodies) lives as strings inside
  `project.json`/`objects/*.json`, never as importable `.py` files under
  the project directory, so nothing in a normal project should ever
  produce a `__pycache__` there. Worth confirming this assumption doesn't
  break for some export-related workflow before writing this off entirely,
  but the original TODO line looks like it may have conflated "clean this
  dev repo" with "clean a user's saved project."
- **Unused assets — detection exists (Asset Manager Tier 1), and
  deletion is now safe to route through.** `utils.asset_usage.
  find_unused_assets` reports every asset *entry* (in `project.json`)
  with zero references. Actually removing them means routing through the
  existing single-asset delete path per item — `AssetManager.
  delete_asset`, which is trash-backed as of the same session (see
  status note above), so this is now just a UI-building task (a dialog
  listing unused assets with checkboxes, calling delete per selected
  item), not a design question.
- **"Shrink project size" — probably means orphaned PHYSICAL files, a
  different thing from `find_unused_assets`.** A sprite/sound/background
  can be deleted from `project.json` (via the asset tree, or by hand-
  editing the file) while its actual `.png`/`.wav` file is left behind in
  `sprites/`/`sounds/`/`backgrounds/` — `find_unused_assets` doesn't see
  these at all, since it only iterates entries that exist in
  `project.json`. Detecting this needs the inverse walk: list every file
  on disk under each asset subfolder, cross-reference against every
  `file_path` value actually present in `project.json` (plus per-frame
  thumbnail files, which follow their own naming convention), and report
  what's left. Not built yet — a legitimately separate detection pass
  from Tier 1's, not a duplicate of it.
- **Build artifacts** — exports write to a location the user explicitly
  chooses via a file dialog (`_ask_export_dir`-style prompts throughout
  `core/ide_window.py`), not to a fixed subfolder inside the project
  directory by default. There may be nothing *inside the project
  directory itself* to clean here at all; this needs a closer look at
  whether any export path defaults to writing under the project root
  before assuming there's real scope here.

## Proposed tiers

1. **`.tmp` orphan sweep — DONE (2026-08-09).** `utils/project_cleanup.py`:
   `find_orphan_tmp_files`/`sweep_orphan_tmp_files` list/remove `*.tmp`
   files under the project directory older than `DEFAULT_MIN_AGE_SECONDS`
   (60s — avoids racing an in-flight save; a real atomic write's `.tmp`
   sibling lives only milliseconds). Pure filesystem logic, no Qt
   dependency, so it's usable standalone or from a future automatic sweep.
   Permanent removal, not Trash — these files were never routed through
   the asset system, so item 10.5's soft-delete mechanism doesn't apply;
   a `.tmp` file is never the authoritative copy of anything (contrast
   with `utils/asset_trash.py`'s module docstring). Wired up exactly as
   this section originally proposed: `core/ide_window.py`'s
   `clean_project` (Tools → Clean Project) does *only* this for now — a
   simple "removed N file(s)" or "nothing to clean" report — rather than
   waiting for Tiers 2-3. Coverage: `tests/test_project_cleanup.py` (10
   tests, pure filesystem, no Qt) + `tests/test_clean_project_dispatch.py`
   (4 tests, the repo's unbound-call-on-a-stub dispatch pattern). Full
   suite 2353 → 2367 passed, 0 failed.
2. **Orphaned physical asset files (detection) — DONE (2026-08-09).**
   `utils/project_cleanup.find_orphaned_physical_files(project_dir,
   project_data)`: the inverse walk described above, grouped by category
   (sprites/sounds/backgrounds/fonts/thumbnails). Cross-references every
   on-disk file with a known asset extension against every `file_path`/
   `thumbnail` value actually present in `project_data['assets']`, so it
   catches both "entry deleted, file left behind" and "file dropped in by
   hand, no entry ever created." Deliberately restricted to known
   extensions per category (not a bare directory listing) so a README or
   other file a user intentionally placed there isn't reported as debris.
   Local copy of the extension table rather than importing
   `core.asset_manager.AssetManager.SUPPORTED_FORMATS`, to keep this
   module's "pure filesystem logic, no Qt" property genuinely true (that
   class pulls in PySide6/pygame/PIL). Read-only — no deletion wired up
   yet, that's Tier 3. Coverage: 10 more tests added to
   `tests/test_project_cleanup.py` (18 total in that file). Full suite
   2367 → 2375 passed, 0 failed.
3. **Deletion UI for orphaned physical files** — the undo-semantics
   question that used to gate this is resolved (Trash, shared with
   `docs/ASSET_MANAGER_PLAN.md` Tier 4); route through
   `AssetManager.delete_asset`-style trashing per file (note: these files
   have no *asset* entry to delete, just a physical file — trashing them
   needs a small variant, not a literal `delete_asset` call, since that
   method operates on a named project.json entry). Not started; only
   remaining open item in this plan.

## Why nothing shipped this pass

This session's actual work went into settling the shared blocker (see the
status note at the top) — the Trash mechanism itself, plus retrofitting
both real delete paths and single-asset delete's confirmation dialog to
use it — rather than into this item's own remaining sub-scope (the
`.tmp` sweep, the orphaned-file scan, their UI). That was a deliberate
choice: the blocker was shared with Asset Manager Tier 3/4, so resolving
it once there unblocks both, and doing so first meant this item's actual
build-out (now unblocked) could start clean in its own session rather
than being squeezed in alongside the design work. Tiers 1-3 above remain
open work for whenever this is picked up.

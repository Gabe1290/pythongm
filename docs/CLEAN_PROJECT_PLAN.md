# Plan: Clean Project (`TODO.md` / `docs/DEFERRED_ITEMS_PLAN.md` item 11)

Status: **scoped 2026-08-09, not implemented.** `TODO.md`'s own note says to
scope this *after* Asset Manager, since it overlaps that item's unused-asset
detection — Asset Manager Tier 1 (`utils/asset_usage.py`, done the same
session) unblocks this. This doc is the scoping pass; nothing here has code
yet, deliberately — see "Why nothing shipped this pass" at the end.

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
- **Unused assets — detection now exists (Asset Manager Tier 1), deletion
  does not.** `utils.asset_usage.find_unused_assets` reports every asset
  *entry* (in `project.json`) with zero references. Actually removing
  them means routing through the existing single-asset delete path per
  item, which **has no undo** — see "Why nothing shipped this pass" below.
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

## Proposed tiers, once this is picked up for real implementation

1. **`.tmp` orphan sweep** — smallest, safest, no design questions. A
   function that lists `*.tmp` under the project directory older than
   some threshold (avoid racing an in-flight save) and removes them, with
   a simple "found N, removed N" report. Good candidate for a "Tools →
   Clean Project" menu entry that does *only* this to start, rather than
   waiting for every other tier.
2. **Orphaned physical asset files (detection only)** — the "shrink
   project size" inverse-walk described above. Read-only, matching Tier
   1's own risk profile (`find_asset_usages`/`find_unused_assets` never
   delete anything either) — report findings, don't act on them yet.
3. **Deletion UI for both unused project.json entries and orphaned
   physical files** — gated on deciding undo semantics for bulk/
   destructive asset operations, which is shared with
   `docs/ASSET_MANAGER_PLAN.md` Tier 3. Decide that once, for both
   features, not twice.

## Why nothing shipped this pass

Every sub-scope that's actually safe to build **read-only** (the `.tmp`
sweep's *detection* half, the orphaned-physical-file scan) is small and
could ship quickly. But the highest-value pieces of "Clean Project" as
originally scoped — actually deleting unused assets, actually removing
orphaned files — are destructive operations against a user's real,
possibly-unsaved-elsewhere game project, and this repo doesn't yet have
an answer to "what happens if that goes wrong" (no undo on the existing
single-asset delete either). Shipping a *detection-only* tier alone,
without ever wiring it to a delete action, would leave the feature
looking half-finished — a report with no button to act on it. Better to
resolve the undo-semantics question once (see Tier 3 above) and build
detection + deletion together as a coherent unit, than to ship a stub now
and a real feature later. Flagging this explicitly rather than silently
deferring it, per this repo's own "stop lying to users" / no half-
finished-implementations standing preference.

# Plan: Asset Manager (`TODO.md` / `docs/DEFERRED_ITEMS_PLAN.md` item 10)

Status: **Tier 1 (usage tracking) done, 2026-08-09.** Written the same session
it's first worked, per this repo's "no small starting subset documented;
needs its own scoping pass" note — the scoping and the first tier's
implementation happened together rather than as two sessions, since the
investigation needed to scope it accurately also produced the design for
the first tier.

## What "Asset Manager" actually means (from `TODO.md`)

> bulk operations on assets (rename, move, delete in batch), search and
> filter, usage tracking ("which rooms / objects use this sprite?"), and
> unused-asset cleanup.

Four genuinely different features bundled under one menu item. They don't
need to ship together, and several depend on a shared piece — knowing what
references what — that didn't exist at all before this session.

## Investigation: what already existed

- `widgets/asset_tree/asset_operations.py`'s `delete_asset` deletes a
  single asset **with no usage check at all** — the confirmation dialog
  says "This will permanently remove the asset and its file," nothing
  about what would break. The **only** reference-clearing that exists is
  sprite→object (`obj_data["sprite"]` cleared when the referenced sprite is
  deleted, including the `objects/<name>.json` side file, audit L32). Sound,
  background, and object-referencing-object deletions leave dangling
  references silently.
- `events/action_types.py`'s `ActionParameter.param_type` already carries
  typed values (`sprite`, `object`, `sound`, `room`, among others,
  documented in the dataclass docstring) for parameters that reference
  another asset by name. This makes a systematic usage scanner possible —
  walk every action, look up its `ActionType` for typed params, and check
  the actual parameter value against the query name — rather than a
  hand-maintained, inevitably-incomplete list of "which actions reference
  which asset type."
- **No `param_type` exists for `background`.** Background references (room
  `background_image`, room tiles' `background_name`, `draw_background`'s
  `background` param) need to be special-cased explicitly; there's no
  generic hook for them the way sprite/object/sound/room have.
- Room instances reference an object via `object_name` (not `object`).
  Rooms have a top-level `background_image` plus a `tiles[]` list each with
  its own `background_name`. Objects have `sprite` and `parent` fields
  outside the `events` structure entirely.
- Collision events store their target as a sibling key (`target_object`) on
  the event dict, not inside any action's parameters — a different shape
  from every other reference, needing its own walk.
- `events/plugin_loader.py`'s `collect_project_action_names` already walks
  every object's events (including nested `then_actions`/`else_actions`/
  `sub_actions`) recursively to collect action *names* for the extension-
  dependency system (see `docs/extension_compat_2_0/PLAN.md`). The same
  walk, extended to also inspect each action's *parameter values* against
  its `ActionType`'s typed params, is the natural foundation for usage
  tracking — reusing a walk this codebase already trusts rather than
  writing a second, possibly-divergent one.

## Tier 1 — usage tracking (DONE)

`utils/asset_usage.py`:
- `find_asset_usages(project_data, asset_type, asset_name)` — every place a
  named asset is referenced, as structured `AssetUsage` records (kind,
  object/room name, and for actions the event name + action index so a
  caller could jump to it). Covers: typed action parameters (sprite/
  object/sound/room, walked recursively through then/else/sub-actions,
  reusing `collect_project_action_names`'s traversal shape), collision
  event `target_object`, room instance `object_name`, object `sprite`/
  `parent` fields, room `background_image` and tile `background_name`,
  and `draw_background`'s `background` param (special-cased — no
  `param_type` exists for backgrounds).
- `find_unused_assets(project_data)` — every asset with zero usages,
  grouped by category. The shared detection engine both "unused-asset
  cleanup" (this item) and the future Clean Project item need — built
  once here so Clean Project doesn't rebuild it (per
  `docs/DEFERRED_ITEMS_PLAN.md` item 11's own note about the overlap).
- **Wired into the existing delete-asset confirmation** —
  `AssetOperations.delete_asset` now shows what would be affected ("used
  by 3 objects, 1 room") before deleting, instead of a generic "this will
  permanently remove it" with no impact information. This alone is real,
  immediately-visible value from Tier 1 without needing any new UI
  surface — the existing single-asset delete just got safer.
- **Known limitation, inherent to static analysis:** a reference inside
  `execute_code`/`execute_script` (an asset name as a plain Python string
  literal, e.g. `self.game_runner.sounds['explosion'].play()`) cannot be
  found this way — only structured action parameters are visible. Not
  solvable without parsing arbitrary user Python, which is out of scope
  for a "usage tracking" feature. Documented in the module docstring so a
  future caller doesn't assume 100% recall.

## Tier 2 — search & filter (not started)

Filtering the existing Asset Tree panel by name substring / asset type.
Smaller than it sounds — the tree already has all assets loaded; this is
a filter-as-you-type box above it, hiding non-matching items. No new data
model needed. Good next small unit whenever picked up.

## The bulk-delete-undo question — SETTLED (2026-08-09)

Both Tier 3 (bulk delete) and Clean Project's deletion UI
(`docs/CLEAN_PROJECT_PLAN.md`) were blocked on the same open question:
what happens when a delete was a mistake? **Decision: not a
`QUndoCommand`-based undo/redo.** The existing `QUndoStack` usage in this
codebase (`editors/room_undo_commands.py`,
`editors/playground_editor/playground_undo_commands.py`, the sprite
editor) is scoped to live, in-memory canvas edits with no file I/O — an
undo stack for that is naturally cleared on project switch or app
restart, exactly when "I didn't mean to delete that" tends to get
noticed. Asset deletion also touches far more than one in-memory object:
a `project.json` entry, a physical file, a thumbnail, a side file, and
cross-references cleared in *other* assets.

**Implemented instead: a soft-delete Trash**, `utils/asset_trash.py`.
Deleting an asset moves its files into `<project>/.trash/` and records a
manifest entry (the full `asset_data`, which files moved where, and any
cross-references that were cleared) instead of unlinking anything. A new
"Tools → Restore Deleted Assets..." dialog (`TrashDialog`,
`widgets/asset_tree/asset_dialogs.py`) lists trash entries with Restore /
Delete Permanently / Empty Trash. Both real delete paths —
`core/asset_manager.py`'s `AssetManager.delete_asset` (the live-app path)
and `widgets/asset_tree/asset_operations.py`'s legacy fallback — route
through it, so single-asset delete is safer today, not just future bulk
features. `utils/project_compression.py`'s zip export excludes `.trash/`
(an unfiltered `rglob('*')` walk would otherwise have bundled deleted
assets into every export/backup).

This resolves the shared blocker for both remaining tiers below — bulk
delete and Clean Project's cleanup UI can now call
`AssetManager.delete_asset` per item (or a thin `bulk_delete` wrapper
around it) and get the same trash safety net for free, with no new
undo design needed.

## Tier 3 — bulk rename/move/delete (not started; delete's undo question resolved)

The most UI-heavy piece: multi-select in the asset tree and a batch
operation dialog. The undo/redo design question is now moot — deletes
already land in Trash regardless of whether they're triggered one at a
time or as a batch. What's left is purely the multi-select UI and
looping the existing (now trash-backed) single-asset operations.

## Tier 4 — unused-asset cleanup, deletion side (not started; unblocked)

Tier 1's `find_unused_assets` already does the *detection*, and deletion
now has a safety net (this session's Trash mechanism, above). What's left
is purely UI: a dialog listing unused assets with checkboxes, "select all
truly-zero-usage items," and routing selected ones through
`AssetManager.delete_asset` (trash-backed) per item. Small once Tier 1
exists — held for a future session so `docs/CLEAN_PROJECT_PLAN.md` (item
11) can build its own "delete unused files/build artifacts" scope on top
of both the detection engine and the trash mechanism, rather than
duplicating either.

## Verification

- `tests/test_asset_usage.py` — unit tests against hand-built project
  dicts for every reference kind listed above, plus a real-sample smoke
  test (`samples/plateforme_3`) confirming realistic counts.
- `tests/test_asset_delete_usage_warning.py` — confirms the delete
  confirmation dialog text includes usage counts when references exist,
  and stays as before (no spurious warning) when an asset truly has zero
  usages.
- `tests/test_asset_trash.py` (12 tests) — the pure `utils/asset_trash.py`
  mechanism: move/list/restore/empty, missing files, name-collision
  refusal on restore, manifest persistence across a reload.
- `tests/test_asset_manager.py`'s `TestAssetManagerDelete`/
  `TestAssetManagerTrashWrappers` — `AssetManager.delete_asset` is a real
  soft delete (restorable, records cleared references), and the
  `list_trash`/`restore_from_trash`/`empty_trash` wrapper methods.
- `tests/test_audit_asset_operations_sidefiles.py`'s
  `test_legacy_fallback_delete_is_also_a_soft_delete` — the second delete
  path (no `project_manager` attached) is trash-backed too, not just the
  live-app one.
- `tests/test_project_compression_trash_exclusion.py` — `.trash/` never
  ends up inside a zip export.
- `tests/test_trash_dialog.py` (12 tests) — `TrashDialog`'s listing,
  restore (including the collision-refusal path), permanent delete, empty
  all, and the cleared-references detail text; plus
  `PyGameMakerIDE.show_trash_dialog`'s dispatch (no-project message vs.
  opening the dialog).

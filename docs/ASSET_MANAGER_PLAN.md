# Plan: Asset Manager (`TODO.md` / `docs/DEFERRED_ITEMS_PLAN.md` item 10)

Status: **All four tiers DONE, all 2026-08-09.** `docs/ASSET_MANAGER_PLAN.md`
is now fully closed. Written the same session it's first worked, per this
repo's "no small starting subset documented; needs its own scoping pass"
note — the scoping and the first tier's implementation happened together
rather than as two sessions, since the investigation needed to scope it
accurately also produced the design for the first tier.

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

## Tier 2 — search & filter (DONE, 2026-08-09)

Filtering the existing Asset Tree panel by name substring. Smaller than it
sounds, as predicted — the tree already had all assets loaded; this is a
filter-as-you-type box above it, hiding non-matching items, no new data
model. `AssetTreeWidget.apply_asset_filter(text)` toggles Qt item
visibility only (selection/drag-drop/everything else keeps working
unchanged): matches case-insensitively against each leaf's raw
`asset_name` (not the displayed text, which carries an emoji/status
prefix); a category auto-hides once every child is filtered out and
reappears once one matches; separators hide while a filter is active.
`core/ide_window.py`'s `create_main_widget` now wraps `self.asset_tree` in
a small container (`asset_panel`) with a `QLineEdit` (`asset_filter_box`,
clear-button-enabled) above it, connected via `textChanged` — `self.asset_tree`
itself is unchanged and still the direct object every existing call site
references; only the splitter's index-0 child became the wrapper instead
of the tree directly, so the two width constraints moved onto the wrapper.
`refresh_from_project` (called on project load, drag-reorder, asset
add/delete) re-applies whatever filter was active instead of it silently
resetting on a tree rebuild — the one non-obvious bit, caught by writing
that regression case first. Asset **type** filtering (mentioned in the
original TODO wording) was intentionally left out of this cut: substring
matching against category-grouped names already gets most of the value
covering it would need a second control (a type dropdown) for a much
smaller marginal benefit, since the tree is already grouped by category.
Coverage: `tests/test_asset_tree_filter.py` (7 tests, hand-rolled offscreen
`QApplication` — no pytest-qt needed, matching this repo's audit-test
convention). Full suite 2333 → 2340 passed, 0 failed.

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

## Tier 3 — bulk multi-select delete (DONE, 2026-08-09)

**Scope correction made before implementing: "move" doesn't apply.** The
original `TODO.md` wording ("rename, move, delete in batch") assumes
assets can live in subfolders a bulk operation would relocate them
between. This app's asset model has no such hierarchy — each category
(sprites/sounds/…) is a flat list; "moving" an asset only ever means
reordering within a category, which drag-and-drop already does one at a
time. There's nothing a *bulk* "move" would do here, so it's dropped from
scope rather than inventing a folder system to give it meaning. Batch
rename (e.g. a shared prefix/suffix or find-replace across several
selected assets) is a real, separately-schedulable feature — deferred,
not because it's out of scope but because it's genuinely a different
piece of UI than what shipped here (a rename dialog per unique new name
vs. delete's uniform "remove all of these").

**What shipped: multi-select + bulk delete**, the two clearly-defined,
already-safe (Trash-backed) parts of the four. `AssetTreeWidget` now uses
`ExtendedSelection` (was `SingleSelection`) so Ctrl/Shift-click multi-select
works; right-clicking with 2+ non-category items selected shows a reduced
context menu with just "Delete N Selected" instead of the full single-item
menu. `bulk_delete_selected` shows **one combined confirmation** for the
whole batch (not the per-item dialog N times — `docs/ASSET_MANAGER_PLAN.md`
had actually suggested "looping the existing single-asset operations,"
which would mean N separate "are you sure?" popups; built the better UX
instead, consistent with `UnusedAssetsDialog`'s own single-confirmation
precedent from Tier 4), then routes each item through the *same*
trash-backed deletion a single delete uses.

`widgets/asset_tree/asset_operations.py`'s `delete_asset` was split into
`delete_asset` (confirmation + usage-note dialog) and a new
`delete_asset_confirmed` (the actual deletion, assuming confirmation
already happened) so bulk delete can call the latter directly per item.
**A real regression caught by the existing suite, not by new tests**:
the original code closed any editor open on the asset *before* showing
the confirmation dialog — a pinned, if slightly odd, existing behavior
(cancelling the delete still closed the editor; a stale composite-key
call bug this exact behavior was tests against —
`tests/test_rename_thumbnail_recovery.py`'s
`test_delete_open_asset_closes_editor_with_composite_key`). The first cut
of this split moved that step into `delete_asset_confirmed` (i.e. after
confirmation), silently changing the behavior the pinned test enforced.
Fixed by factoring it into an idempotent `_close_open_editor_if_any`
helper called from BOTH `delete_asset` (before confirmation, preserving
the quirk) and `delete_asset_confirmed` (so bulk delete, which skips
`delete_asset` entirely, still closes editors for items it deletes).
Coverage: `tests/test_asset_tree_bulk_delete.py` (9 tests: selection mode,
no-selection/single-selection/multi-confirmed/multi-declined, category
items excluded from a batch even though the raw Qt API can select them
despite lacking `ItemIsSelectable`, `delete_asset_confirmed`'s own
dialog-free + editor-closing behavior). Full suite 2398 → 2407 passed,
0 failed (2406 immediately after the split, until the editor-close
regression above was caught and fixed, landing at 2407).

## Tier 4 — unused-asset cleanup, deletion side (DONE, 2026-08-09)

`widgets/asset_tree/asset_dialogs.UnusedAssetsDialog`: lists
`find_unused_assets`' output grouped by category, each leaf a checkbox,
Select All / Select None, and "Move Selected to Trash" routing through
`AssetManager.delete_asset` per item (trash-backed, same safety net as
every other delete). `refresh_list` re-syncs the live asset-manager cache
into `project_data` and re-scans after every delete, so a delete that
clears a reference (e.g. removing an unused object that held the only
remaining reference to a sprite) can reveal a newly-unused asset on the
very next listing without closing/reopening the dialog.

**One real design fix made along the way, not just UI-building**:
`utils/asset_usage.py`'s own module docstring already flags that rooms
have no usage-tracking path at all — a room nobody explicitly navigates
to by name (a single-room game, or a linear sequence's first room)
legitimately shows zero `AssetUsage` records, and the docstring explicitly
warns callers not to present that as "unused." The dialog honors this:
the rooms category is labeled "Rooms — not explicitly navigated to (N)"
rather than "Rooms (N)", and **Select All deliberately skips rooms** (a
one-click sweep could otherwise trash a game's starting room) while
individual room checkboxes stay manually selectable for a deliberate
choice. `core/ide_window.py`'s `show_unused_assets_dialog` wires it up
(Tools → Find Unused Assets…), following the exact `show_trash_dialog`
dispatch pattern (no-project guard, `on_deleted` callback updates the
asset tree, save + status message only if anything was actually deleted).
Coverage: `tests/test_unused_assets_dialog.py` (13 tests, hand-rolled
offscreen `QApplication` against a real `AssetManager`/temp project dir,
matching `tests/test_trash_dialog.py`'s convention) — including the
rooms-excluded-from-Select-All behavior and the cascading-newly-unused
scenario. Full suite 2340 → 2353 passed, 0 failed.

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

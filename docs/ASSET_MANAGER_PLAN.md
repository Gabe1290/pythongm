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

## Tier 3 — bulk rename/move/delete (not started, needs its own design pass)

The most UI-heavy piece: multi-select in the asset tree, a batch operation
dialog, and — critically — **undo/redo integration**, since a batch delete
across dozens of assets with no undo would be a real data-loss risk this
repo's single-asset delete doesn't currently have either (it's also
not undoable; check whether that's an accepted gap or worth fixing
alongside bulk delete before building the bulk version on the same
unsafe foundation). Do not start this without deciding that first.

## Tier 4 — unused-asset cleanup, deletion side (not started)

Tier 1's `find_unused_assets` already does the *detection*. What's left is
purely UI: a dialog listing unused assets with checkboxes, "select all
truly-zero-usage items," and routing selected ones through the existing
(single-asset, still not undoable) delete path. Small once Tier 1 exists —
this is intentionally the cheapest remaining tier, held for a future
session so `docs/DEFERRED_ITEMS_PLAN.md` item 11 (Clean Project) can build
its own "delete unused files/build artifacts" scope on top of the same
detection engine rather than duplicating it.

## Verification

- `tests/test_asset_usage.py` — unit tests against hand-built project
  dicts for every reference kind listed above, plus a real-sample smoke
  test (`samples/plateforme_3`) confirming realistic counts.
- `tests/test_asset_delete_usage_warning.py` — confirms the delete
  confirmation dialog text includes usage counts when references exist,
  and stays as before (no spurious warning) when an asset truly has zero
  usages.

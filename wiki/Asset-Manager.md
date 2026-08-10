# Asset Manager

> [English](Asset-Manager)

---

> [Back to Home](Home)

Beyond the resource tree's day-to-day create/rename/delete, PyGameMaker
tracks **where each asset is actually used**, keeps deleted assets
recoverable instead of gone forever, and can find both unused assets and
stray files cluttering the project folder. These live under the **Tools**
menu.

---

## Filtering the Asset Tree

Type into the filter box above the resource tree to narrow it to matching
names as you type. Matching is case-insensitive against the raw asset
name; a category (Sprites, Objects, ...) hides once every child inside it
is filtered out, and reappears as soon as one matches again.

---

## Usage Tracking

Every asset delete now checks where that asset is actually referenced —
other objects, rooms, actions — before you confirm. If `spr_player` is
used by 3 objects, the delete confirmation says so instead of a generic
warning, so you find out *before* deleting something that would break
other parts of the project, not after.

**Known limitation:** this only sees references PyGameMaker's own data
structures can see — action parameters, collision targets, room
instances, sprite/parent fields. An asset name used only inside a raw
Python string in the [[Code-Editor|Code Editor]] or Execute Code action
(e.g. `game.sounds['explosion'].play()`) isn't visible to this analysis.

---

## Restoring Deleted Assets (Trash)

**Tools > Restore Deleted Assets...**

Deleting an asset doesn't erase it immediately — its files move into a
project-local Trash and PyGameMaker keeps a record of what was deleted,
where its files went, and any cross-references that were cleared (for
example, an object's sprite field getting blanked because the sprite it
pointed to was deleted). This dialog lists everything currently in the
Trash with three actions:

| Action | Effect |
|--------|--------|
| **Restore** | Brings the asset back exactly as it was. Refuses to overwrite if a new asset with the same name now exists — restore isn't destructive either. |
| **Delete Permanently** | Removes a single trash entry for good |
| **Empty Trash** | Removes everything currently in the Trash |

Cross-references that were cleared on delete are **not** automatically
relinked on restore — you'll see what changed, so you can decide whether
to reconnect it rather than have PyGameMaker guess.

Trashed files are excluded from project exports (zip/HTML5/etc.) — a
deleted asset never quietly reappears in a shipped game.

---

## Finding Unused Assets

**Tools > Find Unused Assets...**

Scans the whole project via the same usage-tracking analysis above and
lists every asset with zero references, grouped by category, each with a
checkbox. Select the ones you actually want gone (or **Select All**) and
**Move Selected to Trash** — same Trash safety net as any other delete.

**Rooms are handled carefully.** A room nobody explicitly navigates to by
name — a single-room game, or a game's very first room — legitimately
shows as "unused" under a pure reference count, but deleting it would
break the game. Rooms are labeled *"Rooms — not explicitly navigated to"*
rather than flatly "unused," and **Select All skips rooms** on purpose;
you can still check one individually if you're sure.

---

## Finding Orphaned Files

**Tools > Find Orphaned Files...**

The inverse problem: files sitting in the project folder (`sprites/`,
`sounds/`, `backgrounds/`, `fonts/`, `thumbnails/`) that have **no**
matching entry in the project at all — left behind by an interrupted
operation, or dropped in by hand outside the IDE. Lists them by category
with the same checkbox / Select All / **Move Selected to Trash** pattern
as unused assets, and includes its own mini Trash panel (Restore / Delete
Permanently / Empty) right in the same dialog — orphaned files use a
separate trash store from regular asset deletes, since they were never a
real project.json entry to begin with.

---

## Clean Project

**Tools > Clean Project**

A one-click sweep for leftover `.tmp` files — the temporary siblings
PyGameMaker's atomic save process creates and normally removes itself.
Only files older than about a minute are touched, so an in-flight save
is never at risk of being swept mid-write. Reports how many files were
removed, or that there was nothing to clean. Unlike the dialogs above,
these files are never routed through the asset system or Trash — a
`.tmp` file is never the authoritative copy of anything, so it's deleted
outright.

---

## Next Steps

- [[Room-Editor]] / [[Object-Editor]] - Where most asset references come from
- [[FAQ]] - Common questions, including data-safety ones

# Plan: in-IDE visual Block World editor (Tier 7d)

Status: **not started.** Written 2026-08-15 per
`docs/REMAINING_WORK_2026-08-15.md` Section F. Called out there as "the
largest item in the whole queue" — larger than the entire particle/timeline
system. This doc exists so a future session can start from a concrete plan
instead of a blank page.

## What exists today, and what doesn't

Block World worlds are authored two ways right now, both outside the IDE:

1. A committed **generator script** (`tools/gen_raycast_3_maze.py`-style,
   or `extensions/block_world`'s own sample data) that writes a
   `blocks/<room>.json` file in the `to_block_list` shape
   (`[{"x":, "y":, "z":, "type":}, ...]`, `extensions/block_world/state.py`).
2. Hand-editing that JSON file directly.

`load_block_world` (an action, `extensions/block_world/handlers.py`) reads
that file at runtime into `room.extension_state["block_world"]["blocks"]`
(`extensions/block_world/state.py::load_block_list`). There is **no
`editors/` scaffolding for Block World at all** — no menu entry, no
QWidget, nothing. This plan is about closing that gap: paint/place/remove
blocks visually inside the IDE, the same way the Room Editor already lets
you place object instances and paint tiles, and save the result back to a
`blocks/<room>.json` file the existing `load_block_world` action already
knows how to load.

## Proven building blocks this plan reuses (not starting from zero)

Two real technical risks are already de-risked by working precedent
elsewhere in this codebase:

1. **Rendering a first-person voxel view inside a Qt widget.**
   `extensions/block_world/renderer.py`'s `render_block_world_view(room,
   screen)` already renders a real pygame `Surface` — it's the same
   function the room-renderer hook calls in a running game, and the exact
   entry point `tools/preview_block_world.py` (a standalone pygame-window
   dev tool) already calls to eyeball the renderer. Getting that pygame
   surface onto a Qt canvas is **already a solved problem** in this
   codebase: `widgets/thymio_playground.py` does exactly this today
   (`pygame.image.tostring(surface, 'RGB')` → `QImage(data, w, h, w*3,
   QImage.Format_RGB888)` → paint). The Block World editor's canvas widget
   should follow that same pattern, not invent a new one.
2. **Undo/redo for placing and removing blocks.** The 2026-08-13 design
   note already on record (see `docs/DEFERRED_GAPS_2026_PLAN.md`'s Tier 7d
   entry) correctly leans toward `QUndoStack`/`QUndoCommand`, matching
   `editors/room_undo_commands.py`'s existing shape
   (`AddInstanceCommand`/`RemoveInstanceCommand`: constructor snapshots
   what's needed to reverse the action, `undo()`/`redo()` mutate the live
   canvas state and call `QTimer.singleShot(0, canvas.update)` to repaint
   safely off the direct call stack). `PlaceBlockCommand`/
   `RemoveBlockCommand` should follow that file's exact shape: constructor
   captures `(x, y, z, new_type, old_type)`, `undo` restores `old_type`
   (`None` = was air, so undo calls `remove_block`), `redo` re-applies
   `new_type`.

Neither of these needs a design spike — both have a real, working,
readable example already in the tree to copy the shape of.

## What's genuinely new (the actual size of this task)

- **A camera/movement model for a 2D mouse+keyboard user to navigate 3D
  voxel space and pick a target cell**, inside a QWidget that isn't a game
  loop. `extensions/block_world/handlers.py`'s `_pick` (screen-centre-ray
  picking) and `renderer.py`'s `pick_voxel`/`screen_ray` already do the
  ray math the picking needs — but they assume a `GameInstance`-shaped
  camera object with `x`/`y`/`facing_angle` driven by the actual game loop
  (`move_and_collide`, `set_look_pitch`, mouse-look). The editor needs its
  own lightweight stand-in "camera" object (position + yaw + pitch as
  plain floats, no `GameInstance` at all) that the SAME picking functions
  can operate on, updated by editor-specific input handling (WASD to fly,
  mouse-drag to look, no gravity/collision at all — this is a build mode,
  not play mode, matching `tools/preview_block_world.py`'s own "press C to
  fly through walls" precedent for a debug camera).
- **A hotbar/block-type picker UI panel** — visually this can closely
  mirror `editors/room_editor/tile_palette.py`'s existing tile-picker
  layout (a scrollable grid of clickable swatches, one per `BLOCK_TYPES`
  entry, showing each block's texture), swapping "which tile" for "which
  block type." `tile_palette.py` (436 lines) is the right file to read in
  full before starting this piece — it's the closest existing analogue to
  copy the interaction shape from, not a novel design.
- **Left-click-place / right-click-break mouse handling** translated from
  screen pixel → world ray → target voxel, reusing `_pick`'s math directly
  (it already returns `(target, placement)` cell coordinates — the editor
  calls the same function the `place_block`/`break_block` actions call at
  runtime, just from a mouse event instead of an action).
- **Save/load wiring**: reading a room's existing `blocks/<room>.json` (if
  any) into the editor on open, and writing `to_block_list(room)`'s output
  back out on save. Where this file lives in the asset tree, and whether
  it needs a new "Blocks" asset category (mirroring how sprites/sounds/
  rooms are each their own category) or just lives as a per-room sibling
  file the way room instance data already does — **needs a decision before
  implementation, not a guess**: the two behave differently for delete/
  rename/asset-tree-listing purposes, and this repo has a whole audit
  history (`docs/DEFERRED_GAPS_2026_PLAN.md` Tier 6, the sprite
  manifest-ification work) of exactly this kind of "which asset-management
  code paths does a new file type need to plug into" question turning out
  to have more call sites than expected. Recommendation: treat a room's
  block data as a per-room sibling file (like room instances already are,
  `rooms/<name>.json`) rather than inventing a whole new top-level asset
  category — a Block World room's blocks are conceptually part of that
  room, not a separate reusable asset multiple rooms would share.
- **Menu/toolbar entry** — how a user gets INTO this editor at all. The
  natural trigger is a per-room toggle (open the Room Editor for a room
  that has `enable_block_world_view` wired up, then a "3D Block Edit"
  button/tab switches the SAME room's editing surface into the voxel
  painter) rather than a wholly separate top-level editor type — keeps the
  mental model "one editor per room," matching how the Room Editor's tile
  palette is a mode *within* the room editor, not a separate window.

## Explicit non-decisions already made (don't re-litigate these)

- **No edit-mode/play-mode engine toggle.** The 2026-08-13 note already
  reasoned this through: whether a player can break blocks in the shipped
  game is entirely a function of whether the author bound `break_block` to
  an input event, exactly like every other action in this engine. The
  in-IDE editor is a separate, editor-only surface (like the Room Editor
  itself is), not a runtime mode switch.
- **Not a general-purpose 3D modeling tool.** Placing/removing unit cubes
  from the existing `BLOCK_TYPES` registry only — no custom meshes, no
  rotation, no non-cubic shapes. Matches the engine's own voxel model
  exactly; scope creep here would be building a different, much bigger
  product.

## Suggested phase breakdown

1. **Camera + raw 3D view embedded in a QWidget, no editing yet.** Prove
   the `pygame.image.tostring` → `QImage` pipeline against the real
   `render_block_world_view`, with WASD+mouse-look navigation and zero
   place/break logic. This is the phase with the most genuine technical
   risk (Qt event loop timing vs. a per-frame pygame render — needs a
   `QTimer` tick, not a blocking pygame loop, so check how
   `widgets/thymio_playground.py` drives ITS repaint timing and follow the
   same approach) and should be proven completely on its own before adding
   editing.
2. **Place/break via mouse, undo/redo wired.** `PlaceBlockCommand`/
   `RemoveBlockCommand`, hotbar panel, left/right-click handling.
3. **Save/load to `blocks/<room>.json`**, plus whatever asset-tree/menu
   wiring the sibling-file decision above implies.
4. **Polish pass**: status bar (current block type, coordinates), a
   "clear world" action, keyboard shortcuts matching the Room Editor's own
   conventions where they naturally apply.

Each phase is its own commit+push, full-suite-green gate. Phase 1 in
particular should get a dedicated proof (matching this repo's
audit-discipline: "every consolidation must be proven," extended here to
"every new interaction model must be proven against a real rendered frame,
not assumed to work") before phase 2 starts building on top of it.

# Block World — a voxel block-building extension (in progress)

**Working name only.** Never call this "Minecraft" anywhere in code, UI
strings, or docs — see the naming section of `docs/VOXEL_WORLD_PLAN.md`. This
is "inspired by," the same territory Luanti/Minetest itself occupies, not a
clone wearing someone else's name.

**Status: Phase 2b done; Phase 3 under way (picking + place/break landed
2026-08-13).** A room with the view enabled renders as a textured
first-person world whose blocks **stack** — walls several blocks high, you
can stand on things and see over what's below you, blocks show their top
faces — and you can now build and dig at your own layer. Still no hotbar
action, no collision and no gravity — see "What's not here yet" below.

## What exists so far

| File | What's in it |
|---|---|
| `extension.json` | The manifest. |
| `__init__.py` | The entry point — declares `PLUGIN_ACTIONS`, `PluginExecutor` and `PLUGIN_ROOM_RENDERERS`, and `render_room` claims a room only when its camera config says `enabled`. |
| `state.py` | The per-room world data model: a sparse `(x, y, z) -> block type id` store plus a camera config, both under `room.extension_state["block_world"]`, and the `BLOCK_TYPES` registry mapping block type ids to face textures. Also the derived `column_index` / `stack_top` heightmap queries the renderer reads. |
| `renderer.py` | The renderer: `march_ray` (the one cell-occupancy DDA, yielding each cell's entry and exit distance), `cast_ray` (first-hit wrapper over it), and `render_block_world_view` (camera-plane projection, stacked textured wall columns, texture-mapped top/bottom faces). |
| `actions.py` / `handlers.py` | Three actions: `enable_block_world_view` (camera/config plumbing, mirroring `enable_raycast_view`), plus `place_block` and `break_block`, which act on whatever the camera's centre ray reaches. |
| `textures/source_hand_painted_expanded/` | The CC0-licensed block textures (Phase 0), 32 files. |
| `ASSETS.md` | The licensing audit — read this before adding or swapping any texture. |

## Looking at it

`tools/preview_block_world.py` renders a hand-built showcase world through
the real `render_block_world_view`, so what it shows is what the engine
draws:

```
py -3.12 tools/preview_block_world.py              # walk around (needs a display)
py -3.12 tools/preview_block_world.py --shots out  # 14 fixed frames as PNGs (headless)
```

The pixel-sampling tests prove a strip got drawn; this is how you judge
whether the textures actually read well — which is the whole point of
staging 2a first. Its movement, footing and collision are the script's own,
not engine features (the engine gets none until Phase 4), though the
step-up rule it uses is built on the real `stack_top` heightmap query.

## Building and digging (Phase 3)

`place_block` and `break_block` both act on whatever the camera's centre ray
reaches, via `renderer.pick_block` — the *same* march the renderer runs, at
the same angle the centre column is drawn from, so you break exactly what
sits under the crosshair. A second raycast for picking would be a second
thing to keep in step.

What the level camera implies, and it is not a bug: the ray runs horizontally
at eye height, so **only your own layer is reachable**. You build outwards at
your feet and climb what you build; digging down or placing onto ground below
you needs Phase 2c's free look. Standing flush against a wall there is
genuinely nowhere to build at your layer, and the action does nothing.

A placement cell returned by `pick_block` is **always air** — the march only
advances past cells it has read as empty. `place_block` relies on that and
deliberately does not re-check.

**A gap beats a surface.** If the ray passes through a hole — an empty cell
at your layer with a block resting on top of it — the new block goes *there*,
rather than against whatever the crosshair finds beyond. Without that rule a
hole knocked in a one-block-thick wall can never be refilled from either
side, because no cell "before the hit" is ever the hole itself. Breaking is
unaffected: the crosshair still reaches past the hole. An open doorway has
nothing resting on it, so it is never bricked up by accident.

**`obsidian` cannot be broken.** It is the designated boundary material:
line a world's edges with it and a player cannot dig out. `break_block`
consults `state.is_breakable` (default True, so a type says nothing unless it
wants to be indestructible) and **nothing else does** — an unbreakable block
is still aimed at, still occludes, still gets built against, and can still be
placed. Swinging at one does nothing. That one flag is the whole protection
model; the engine has no edit/play modes, and the plan doc explains why.

## The data model (`state.py`)

Mirrors `extensions/raycast_2_5d/state.py`'s pattern exactly: nothing
voxel-specific touches core's `GameRoom`. A room's blocks live under
`room.extension_state["block_world"]`, reached through:

- `block_world_state(room)` — get-or-create, for code that owns/mutates the
  world.
- `peek_blocks(room)` — non-creating read, for a future room-renderer hook
  that runs on every room and must not stamp state onto rooms that were
  never a block world.
- `get_block` / `set_block` / `remove_block` / `iter_blocks` / `bounds` —
  the working API. Air is the absence of a key, not a stored block — the
  same "sparse, not dense" reasoning the plan doc gives.
- `column_index(room)` / `stack_top(room, x, y)` — the DERIVED heightmap
  view: every non-empty column as `{(x, y): [(z, type), ...]}`, lowest
  first, cached until a mutator invalidates it. The renderer needs a whole
  stack per cell it steps into, and probing the `"x,y,z"` string keys layer
  by layer would cost tens of thousands of string formats a frame. Anything
  that edits `state["blocks"]` without going through the mutators above
  MUST call `_invalidate_columns`, or the renderer keeps drawing the old
  world.
- `to_block_list` / `load_block_list` — round-trip to a flat list of
  `{"x", "y", "z", "type"}` dicts, matching the shape convention room JSON
  already uses for tile layers. Nothing here reads or writes room JSON
  directly yet; `extension_state` is transient runtime state, exactly like
  raycast's camera config — an actual load path (a generator script, a
  `create`-event action reading a bundled world file) is Phase 3+.

## What's not here yet

- Free vertical camera look (Phase 2c, deliberately deferred). Pitch is
  fixed level, so you cannot look down into a pit at your feet or up at the
  top of a tower you are standing against — run the preview's `pit`
  viewpoint to see exactly what that costs.
- A fast renderer. A frame marches ~19 cells and draws ~38 wall strips per
  column for a handful of visible surfaces, because painting far→near
  rasterises everything hidden too; deck-heavy views run ~18 fps at 800x600
  with 320 columns. `columns` and `top_cast_res` are the knobs.
- Transparency as a designed feature. Alpha textures (glass, water, ice,
  leaves) do composite over whatever stands behind them, and `BLOCK_TYPES`'
  `transparent` flag is read in exactly one place — it stops a see-through
  block from being treated as an occluder, so the march never skips what is
  behind one. But that much falls out of painting far→near; there is no
  blending model, no per-block opacity, and a transparent block still costs
  a full textured strip. `solid` is still unread until Phase 4 gives it
  collision to gate.
- Protected *regions*. Protection is per block TYPE only (`breakable`); a
  bounding box the actions refuse to touch is the follow-up if that turns
  out too coarse.
- A hotbar action, and a committed world generator (rest of Phase 3).
- Collision, gravity, a HUD (Phase 4).
- A sample game (Phase 5).
- HTML5 / Kivy export parity (Phase 6).

See `docs/VOXEL_WORLD_PLAN.md` for the full staging.

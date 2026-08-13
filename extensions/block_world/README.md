# Block World — a voxel block-building extension (in progress)

**Working name only.** Never call this "Minecraft" anywhere in code, UI
strings, or docs — see the naming section of `docs/VOXEL_WORLD_PLAN.md`. This
is "inspired by," the same territory Luanti/Minetest itself occupies, not a
clone wearing someone else's name.

**Status: Phase 2a of `docs/VOXEL_WORLD_PLAN.md` done; Phase 2b next.** A room
with the view enabled renders as a flat, single-layer textured first-person
world. There is still no way to place or break a block, no collision, and no
gravity — see "What's not here yet" below.

## What exists so far

| File | What's in it |
|---|---|
| `extension.json` | The manifest. |
| `__init__.py` | The entry point — declares `PLUGIN_ACTIONS`, `PluginExecutor` and `PLUGIN_ROOM_RENDERERS`, and `render_room` claims a room only when its camera config says `enabled`. |
| `state.py` | The per-room world data model: a sparse `(x, y, z) -> block type id` store plus a camera config, both under `room.extension_state["block_world"]`, and the `BLOCK_TYPES` registry mapping block type ids to face textures. |
| `renderer.py` | Phase 2a's renderer: `cast_ray` (cell-occupancy DDA) and `render_block_world_view` (camera-plane projection, textured wall columns, flat floor/ceiling). |
| `actions.py` / `handlers.py` | One action, `enable_block_world_view` — camera/config plumbing, mirroring `enable_raycast_view`. |
| `textures/source_hand_painted_expanded/` | The CC0-licensed block textures (Phase 0), 32 files. |
| `ASSETS.md` | The licensing audit — read this before adding or swapping any texture. |

## Looking at it

`tools/preview_block_world.py` renders a hand-built showcase world through
the real `render_block_world_view`, so what it shows is what the engine
draws:

```
py -3.12 tools/preview_block_world.py              # walk around (needs a display)
py -3.12 tools/preview_block_world.py --shots out  # 9 fixed frames as PNGs (headless)
```

The pixel-sampling tests prove a strip got drawn; this is how you judge
whether the textures actually read well — which is the whole point of
staging 2a first. Its movement and collision are the script's own, not
engine features.

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
- `to_block_list` / `load_block_list` — round-trip to a flat list of
  `{"x", "y", "z", "type"}` dicts, matching the shape convention room JSON
  already uses for tile layers. Nothing here reads or writes room JSON
  directly yet; `extension_state` is transient runtime state, exactly like
  raycast's camera config — an actual load path (a generator script, a
  `create`-event action reading a bundled world file) is Phase 3+.

## What's not here yet

- Stacked blocks / multiple visible z-layers (Phase 2b); free vertical look
  (Phase 2c).
- `place_block` / `break_block` actions, a hotbar (Phase 3).
- Collision, gravity, a HUD (Phase 4).
- A sample game (Phase 5).
- HTML5 / Kivy export parity (Phase 6).

See `docs/VOXEL_WORLD_PLAN.md` for the full staging.

# Block World — a voxel block-building extension (in progress)

**Working name only.** Never call this "Minecraft" anywhere in code, UI
strings, or docs — see the naming section of `docs/VOXEL_WORLD_PLAN.md`. This
is "inspired by," the same territory Luanti/Minetest itself occupies, not a
clone wearing someone else's name.

**Status: Phase 1 of `docs/VOXEL_WORLD_PLAN.md`.** This extension currently
has a data model and a texture set. It has **no room renderer and no
actions yet** — loading it changes nothing about a running game. Follow the
plan doc for what's next.

## What exists so far

| File | What's in it |
|---|---|
| `extension.json` | The manifest. `provides_actions: []` — genuinely none yet. |
| `__init__.py` | The entry point. No `PLUGIN_ACTIONS` / `PLUGIN_ROOM_RENDERERS` declared (both are optional to `events/plugin_loader.py`, checked via `hasattr`) — declaring empty placeholders for features that don't exist yet would just be dead code. |
| `state.py` | The per-room world data model: a sparse `(x, y, z) -> block type id` store under `room.extension_state["block_world"]`, plus the `BLOCK_TYPES` registry mapping block type ids to face textures. |
| `textures/source_hand_painted_expanded/` | The CC0-licensed block textures (Phase 0), 32 files. |
| `ASSETS.md` | The licensing audit — read this before adding or swapping any texture. |

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

- A room renderer (Phase 2) — nothing draws a block world.
- `place_block` / `break_block` actions, a hotbar (Phase 3).
- Collision, gravity, a HUD (Phase 4).
- A sample game (Phase 5).
- HTML5 / Kivy export parity (Phase 6).

See `docs/VOXEL_WORLD_PLAN.md` for the full staging.

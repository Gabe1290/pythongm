# Raycast — Level 1

A Doom/Wolfenstein-style first-person view of **the exact same maze layout
as `maze_1`** — same rooms, same walls, same goal. Where `maze_1` shows the
maze top-down, this sample renders it as a raycast projection: cast one ray
per screen column, measure the distance to the nearest wall, draw a
vertical strip whose height falls off with distance. See
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) in the repo
root for the full engineering plan this sample is Phase 1/4 of.

**This is 2.5D, not 3D** — gameplay logic is completely unchanged from
`maze_1` (the same 2D `x`/`y` position, the same solid-wall collision); only
the *picture* is faked into looking three-dimensional. There's no vertical
look (no pitch), corridors must be grid-aligned, and there's no true
room-over-room. That's a deliberate, honest limitation, not a missing
feature — see the plan doc's "why raycasting" pedagogy note.

**v1 status — flat colors only, desktop (pygame) only.** Walls are a flat
color per grid-cell face orientation (a free lighting cue, no real lighting
model), floor/ceiling are flat fills, no textures, no sky/horizon yet, no
sprites for `obj_goal` in the first-person view. Kivy/HTML5 export parity is
not implemented — this sample currently only runs correctly through
`Build → Test Game` / desktop export.

## How to play

- **Up / Down** move forward / backward in whichever direction you're
  facing (continuous movement, not grid-snapped — walls still block you via
  the engine's normal solid-instance collision, unchanged from `maze_1`).
- **Left / Right** turn in place (rotates `facing_angle`, independent of
  movement — you can turn while standing still).
- **Objective:** find the goal. Touching it advances to the next room if one
  exists (same `obj_goal` logic as `maze_1`, byte-identical file).

## What's new here, engine-wise

- `GameInstance.facing_angle` — persistent look direction (GM angle
  convention: 0=right, 90=up, 180=left, 270=down), set via the new
  `set_facing_angle` action. Unlike the existing `direction` property
  (derived from `hspeed`/`vspeed`, always 0 when stationary), this survives
  standing still — required for "turn on the spot" FPS controls.
- `enable_raycast_view` — switches the current room to the raycast camera
  (bound to the calling instance, here `obj_person`'s `create` event) or
  back to normal top-down rendering.
- The wall map is **derived from this room's existing solid `obj_wall`
  instances** (bucketed into a grid by `x // cell_size`), not a separate
  authoring format — this is why `raycast_1`'s rooms are literal copies of
  `maze_1`'s: any grid-based maze already works with zero new content.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest |
| `rooms/room0.json`, `rooms/room1.json` | Identical maze layouts to `maze_1` |
| `objects/obj_person.json` | Player/camera — `create` enables the raycast view, `keyboard` events drive turning + forward/back |
| `objects/obj_goal.json` | Goal object — byte-identical to `maze_1`'s |
| `objects/obj_wall.json` | Wall object — byte-identical to `maze_1`'s (still just a normal 2D solid `GameObject`) |
| `sprites/` | Same three sprites as `maze_1` (unused for rendering while raycast mode is active, still needed for the room editor / a future top-down fallback) |

## Things to tweak

- Turn rate is `3`°/frame (`room_speed: 30` → 90°/sec) and move speed is `3`
  px/frame, both hardcoded in `obj_person`'s `keyboard` events.
- FOV `66`°, `render_distance` `20` cells, `cell_size` `32` — all
  `enable_raycast_view` parameters on `obj_person`'s `create` event.
- Wall/floor/ceiling colors are also `enable_raycast_view` parameters —
  easy first thing to experiment with before textures land.

## Export status

Desktop (pygame) only — see the plan doc's phased status. Not yet in the
IDE's Welcome tab sample list; open the project folder directly for now.

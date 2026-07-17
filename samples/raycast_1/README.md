# Raycast — Level 1

A Doom/Wolfenstein-style first-person view of **the same maze layout as
`maze_1`** — same rooms, same goal, same solvable paths. Where `maze_1`
shows the maze top-down with full-cell wall blocks, this sample renders
it as a raycast projection with **thin edge-walls** (8px partitions
sitting on cell boundaries, not 32px blocks filling a cell) — genuinely
Wolfenstein-proportioned corridors, not just a first-person camera bolted
onto the old blocky layout. `rooms/room0.json` and `room1.json` were
regenerated from `maze_1`'s original layout via a topology-preserving
conversion (same connectivity/solvability, different wall geometry), not
hand-redesigned. See
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) in the repo
root for the full engineering plan, including the "Complete rethink"
section on why full-cell walls didn't work for real turning clearance.

**This is 2.5D, not 3D** — gameplay logic is completely unchanged from
`maze_1` (the same 2D `x`/`y` position, the same solid-wall collision); only
the *picture* is faked into looking three-dimensional. There's no vertical
look (no pitch), corridors must be grid-aligned, and there's no true
room-over-room. That's a deliberate, honest limitation, not a missing
feature — see the plan doc's "why raycasting" pedagogy note.

**v1 status — flat colors only, desktop (pygame) only.** Walls are a flat
color per wall-face orientation (a free lighting cue, no real lighting
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
- The wall map is **derived from this room's existing solid instances**,
  not a separate authoring format — but as of the thin-wall rework, it's
  derived as real edges (`GameRoom._build_raycast_walls`), not coarse
  per-cell occupancy: a solid instance's sprite aspect ratio decides
  whether it's a horizontal or vertical wall segment (roughly square
  falls back to blocking a whole cell, for backward compatibility with
  non-thin-wall content). This is what makes `obj_wall_h`/`obj_wall_v`'s
  8px thickness actually matter for both rendering and turning
  clearance, not just visually — see the plan doc's "Complete rethink"
  section.

## Project structure

| File | Purpose |
|---|---|
| `project.json` | Project manifest |
| `rooms/room0.json`, `rooms/room1.json` | Same maze *topology* as `maze_1`, regenerated with thin edge-walls (see the plan doc's conversion algorithm) |
| `objects/obj_person.json` | Player/camera — `create` enables the raycast view, `keyboard` events drive turning + forward/back, registers `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Goal object — byte-identical to `maze_1`'s |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Thin wall segments (32×8 and 8×32) — replace `maze_1`'s single full-block `obj_wall` |
| `sprites/` | `spr_person`, `spr_goal` (from `maze_1`) plus this sample's own `spr_wall_h`/`spr_wall_v` (thin, solid-color placeholders — never rendered in first-person mode, only their dimensions matter for collision/raycasting) |

## Things to tweak

- Turn rate is `3`°/frame (`room_speed: 30` → 90°/sec) and move speed is `3`
  px/frame, both hardcoded in `obj_person`'s `keyboard` events.
- FOV `66`°, `render_distance` `20` cells, `cell_size` `32` — all
  `enable_raycast_view` parameters on `obj_person`'s `create` event.
- Wall/floor/ceiling colors are also `enable_raycast_view` parameters —
  easy first thing to experiment with before textures land.
- Wall thickness is `8`px, hardcoded in the conversion that generated
  `rooms/*.json` (not a runtime parameter) — regenerate the rooms to
  change it.
- `spr_person`'s collision bbox is `(8,8)-(24,24)` (16×16, 8px margin per
  side), set in `sprites/spr_person.json` (this sample's own copy,
  independent of `maze_1`'s) — kept from the earlier bbox-only fix even
  though the thin walls now give much more headroom on their own; a
  smaller player still feels more appropriate for a corridor shooter than
  the sprite's full 32×32 canvas.

## Export status

Desktop (pygame) only — see the plan doc's phased status. Not yet in the
IDE's Welcome tab sample list; open the project folder directly for now.

# Plan: raycast minimap (`draw_minimap`)

Status: **DONE (2026-07-20)** — all four units landed; see the checklist.
Originally: **PLAN (2026-07-20).** Session E of `docs/RAYCAST_HUD_PLAN.md`, which
scheduled the minimap behind its own design pass because it is a *world-space
projection* problem, not the screen-space compositing problem Sessions A–D
solved. It depends on the HUD pass landing first (`341f5c4` / `d11550b` /
`fd2402f`) — the minimap draws in that same final screen-space pass.

## The key finding, which changes the shape of the work

The HUD plan assumed each target would need a new minimap *renderer*. It
doesn't. Checked against the code first:

- All three targets already cache the **same derived wall-edge sets** —
  `v_walls` / `h_walls`, keyed `(line_x, row)` and `(col, line_y)` — built by
  `_build_raycast_walls` (desktop `game_runner.py:1837`, Kivy
  `kivy_exporter.py:1700`, HTML5 `engine.js:2817`).
- All three already render `rectangle` and `line` draw-queue commands (desktop
  `_DRAW_HANDLERS`, HTML5 `engine.js:387`/`419`, Kivy `_dq_render_cmd`
  `:3599`/`:3633`).
- A drawing instance can reach its room via
  `action_executor.game_runner.current_room` (and the equivalent on each
  export), so the **action** can read the wall set at queue time.

So `draw_minimap` is a **macro action**: it reads the wall edges, projects them
to screen space, and pushes ordinary `rectangle` + `line` commands. **No
renderer changes on any target.** Only the action is implemented three times,
and the parity surface is pure geometry — numerically comparable in a test,
exactly like `_cast_ray` in `test_raycast_export_parity.py`.

## Design decisions

- **North-up, not rotating.** A rotating minimap is harder to read (the reason
  many games offer a toggle), and rotation means the same wall projects to
  different screen pixels on each target — a far wider parity surface for no
  teaching value. Facing is shown by the player marker instead: a short line
  from the player dot in the `facing_angle` direction.
- **Full map, not fog-of-war.** Fog needs per-cell visited state, persisted per
  room and kept in sync across three targets — real state, not just drawing.
  A fully-revealed map is a legitimate design (it's a map you carry), and it
  keeps v1 stateless. **Scoped out, not forgotten.**
- **Walls only, plus the player.** Not gems/monsters: showing every pickup and
  enemy trivialises the maze, and `raycast_3`'s gem-gated exit is meant to make
  you explore. A `show_items` parameter is a plausible v2; deliberately absent
  in v1 so the default isn't a spoiler.
- **Whole map scaled into `size`,** rather than a radar window around the
  player. Simpler, and for the 15×15 sample mazes an 8px cell is legible. A
  `range` parameter (draw only cells within N of the player) is the natural
  extension if a much larger room ever needs it.

### Projection

Room→minimap is a uniform scale plus offset, north-up:

    scale = size / (grid_cells * cell_size)      # square maps; room is square
    px = x + (world_x * scale)
    py = y + (world_y * scale)

`x`, `y` are the minimap's top-left in **screen space** (the HUD pass draws with
no view offset). y is *not* flipped here — Kivy's flip happens once, later, in
the shared draw-queue path that already handles every other HUD command.

### Emitted commands

1. one `rectangle` — the background panel;
2. one `line` per wall edge — a v-wall at `(line_x, row)` spans
   `(line_x*cs, row*cs)` → `(line_x*cs, (row+1)*cs)`; an h-wall at
   `(col, line_y)` spans `(col*cs, line_y*cs)` → `((col+1)*cs, line_y*cs)`;
3. two `line`s for the player — a short cross at the camera position, plus a
   heading line of `facing_len` px along `-facing_angle` (the same convention
   the renderers use: GM 0=right/90=up mapped to y-down screen).

### Parameters

`x`, `y`, `size`, `back_color`, `wall_color`, `player_color`. Registered in
`events/action_types.py` under the existing **"3D View"** category next to
`enable_raycast_view` / `set_facing_angle`.

## Cost note

A 15×15 maze is ~250 wall edges, so a full map emits ~250 line commands per
frame. Fine on desktop and HTML5; on Kivy it rebuilds that many `Line`
instructions into the HUD `InstructionGroup` each frame. Worth measuring on the
sample before assuming, and the `range` parameter above is the escape hatch if
it bites.

## Units (one commit each)

- [x] **Unit 0 — this plan.** `0ff7edb`.
- [x] **Unit 1 — desktop `draw_minimap`.** `a1784fc`, plus `cadc341` fixing two
  bugs the first pass shipped: the camera never resolved (the code looked for
  `_find_raycast_camera`, which is **Kivy-only**; desktop uses
  `_find_first_instance`), and the marker used the sprite corner rather than
  the ray origin. Both were invisible to a test that only checked that walls
  were drawn — the lesson being to assert *where* a marker lands.
- [x] **Unit 2 — HTML5.** `case 'draw_minimap'` in engine.js.
- [x] **Unit 3 — Kivy.** The generator emits a CALL to
  `GameObject._draw_minimap` (generated into `base_object.py`) because the
  minimap needs loops and Kivy codegen emits single-line expressions — the M34
  two-halves pattern. Verified the emitted call's arity matches the definition
  and both files compile.
- [x] **Unit 4 — parity + sample.** Parity tests cover the shared constants,
  the facing-angle negation, the wall-set sort, the ray-origin marker, and an
  exact numeric comparison of the projected geometry. `raycast_3`'s `obj_hud`
  draws it bottom-right; EN + FR guides updated.

**Cost note resolved:** the ~250 lines/frame estimate held and caused no
trouble on desktop; the Kivy per-frame `InstructionGroup` rebuild is still
untested on real hardware, so the `range` escape hatch stays worth remembering.

## Out of scope

- Fog of war (see above).
- Rotating/heading-up orientation.
- Showing items or enemies.
- Non-square rooms are handled by the scale formula but untested; the sample
  mazes are square.

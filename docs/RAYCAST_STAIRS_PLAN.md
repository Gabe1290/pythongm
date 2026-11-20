# 2.5D raycast: climbable stairs (floor heights) — plan

Written 2026-11-20 on request ("when designing 2.5D games, I want to add the
possibility of climbing up stairs like in Doom — write the plan, do not
implement"). **Not started.** This file is the resume state: work the units
in order, one commit + push per unit, tick the checkbox with the hash.

## Goal

A student builds a staircase in the room editor (a row of step objects, each a
little higher than the last), runs the game, and walks up it in the
first-person view: the view rises step by step, the steps are drawn as real
risers and treads, a step that is too high blocks you like a wall, and you can
walk off a ledge and drop down. It works on desktop, HTML5 and Kivy exports,
and every existing raycast game (`raycast_1`–`4`, tutorials 11–14) renders
**pixel-identical** when it uses no steps.

## What exists today (verified against the code, 2026-11-20)

All of it lives in the folder extension `extensions/raycast_2_5d/`:

- **Walls** are derived every frame from **solid** instances
  (`renderer.build_raycast_walls`): thin edges on grid lines (`v_walls`,
  `h_walls`), keyed by cell, with the sprite per edge for texturing.
- **One hit per column.** `cast_ray` is a DDA that stops at the first wall
  edge; the renderer draws one wall strip per column. There is no notion of
  height anywhere: floor at 0, eye fixed, ceiling fixed.
- **Projection.** Wall strip height is
  `view_h * cell_size * RAYCAST_WALL_HEIGHT / corrected` with
  `RAYCAST_WALL_HEIGHT = 1.5`, centred on the horizon `view_h / 2`. So walls
  span world height `0 .. 1.5 cell` and the **eye is at 0.75 cell**.
- **Floor/ceiling cast** (`cast_floor_plane`): row-major, low-res
  (`floor_cast_res`, default 4), `pos_z = 0.5 * view_h`, i.e. an **eye height
  of 0.5 cell**. See finding F1 below.
- **Billboards**: every visible, sprited, **non-solid** instance, centred on
  the horizon, occluded per column against `col_wall_dist`.
- **Movement and blocking are core's**: the player moves with
  `set_direction_speed`; solid instances block it in `runtime/collision.py`
  (`check_movement_collision_with_blocker`, `_slide_axis_to_contact`). The
  extension has no movement code.
- **Hooks available without touching core** (`runtime/extension_hooks.py`):
  `register_frame_update(func, phase)` with phases `before_step`,
  `after_collision`, `after_update`; the room renderer; instance-created
  hooks. HTML5 has `registerFrameUpdate`; Kivy has `_update_extensions(dt)`
  and the `_ext_<hook>__<extension>` method convention.
- **Three hand-written renderers**: desktop `renderer.py`, HTML5
  `export_html5.js`, Kivy `export_kivy.py` (`SCENE_CODE`, a %-formatted
  string). The numeric core is pinned by `tests/test_raycast_export_parity.py`
  (desktop vs Kivy `_cast_ray` exact; HTML5 structural).
- Precedent for "an action that tags an instance for the renderer":
  `set_billboard_rotation` sets `instance.billboard_rotation_frames`, which all
  three renderers read.

### Finding F1 — floor and walls disagree on eye height (pre-existing)

Since `f0bfd4ec` (walls 1.5× taller) the wall pass puts the eye at 0.75 cell
but the floor cast still uses 0.5 cell. Arithmetic: a wall at `d` cells has
its base at `p = 0.75 * view_h / d` below the horizon; the floor cast maps that
row to `0.5 * view_h / p = 0.67 d`. So the floor texture under a wall's base
is sampled at two-thirds of the wall's distance: the floor appears to slide
relative to the wall bases as you walk, and its tiles do not line up with the
grid the walls stand on. Same formula on all three targets. Nobody has
reported it, but stairs make it impossible to ignore: a tread is a piece of
floor that has to meet its riser exactly. See decision D1.

## Design

### Authoring: step objects with a floor height

A step is an ordinary **non-solid** object with a cell-sized sprite, placed on
the grid in the room editor like a wall. Its Create event runs a new action:

```
Set Floor Height   height = 8   top_texture = spr_step_top   side_texture = spr_step_side
```

- `height` is in room pixels (same unit as x/y and `cell_size`). A staircase is
  four objects (heights 8, 16, 24, 32) sharing a parent, or one object per
  level — exactly how students already make wall objects.
- The handler stores `instance.raycast_floor_height` (+ the two texture
  names), like `set_billboard_rotation` does. Non-solid on purpose: solid
  would make core block it and `build_raycast_walls` turn it into a wall.
- An instance raises **every grid cell its sprite box covers** (a 64×32 sprite
  raises two cells). Overlap: the highest wins. Cells with no step are at 0.
- The height map is rebuilt every frame from the live instances
  (`build_floor_heights(room, cell_size)`, new module `heights.py`), for the
  same reason walls are: a step created or destroyed at runtime (a lift, a
  bridge appearing) shows up immediately. One builder is shared by the
  renderer and the movement rule, so what you see is what you can climb.
- Step instances are **excluded from the billboard pass** (otherwise each step
  would also be drawn as a flat cutout).

No new asset type, no new room-editor layer, no heightmap file. Rejected
alternative: a per-room height map painted on a tile layer — needs editor
work, and a step that is an object can move, be destroyed, or carry events.

### Vertical model

| World height | Meaning | Default |
|---|---|---|
| `floor(cell)` | height of the floor under a cell | 0, or a step's height |
| `eye_z` | camera eye = smoothed floor under the camera + `EYE_HEIGHT` | `EYE_HEIGHT = 0.75 cell` |
| `ceiling` | top of every wall and the ceiling plane | `wall_height × cell`, `wall_height = 1.5` |

`RAYCAST_WALL_HEIGHT` is split into two named constants: the eye height (0.75
cell, fixed) and the wall/ceiling height (new optional `wall_height` parameter
on **Enable Raycast View**, default 1.5). With the default both reproduce
today's numbers exactly. A stair game needs more headroom (at 1.5 the ceiling
is only 0.75 cell above the eye, so three 8-px steps put your eye at the
ceiling); the sample uses `wall_height = 3`.

Constraint, validated with a warning in the log and clamped: a floor height may
not exceed `ceiling − EYE_HEIGHT − 4 px`.

One projection formula for everything (walls, risers, treads, billboards,
floor cast): a world height `Z` at corrected distance `d` lands at
`y = horizon + (eye_z − Z) × view_h / d`. With `eye_z = 0.75 cell` and
`Z = 0` this is exactly today's wall base, which is the pixel-identity check.

### Rendering: from one hit per column to a front-to-back column walk

The fast path stays: **if the room has no floor-height instances and
`wall_height` is the default, the existing code runs unchanged.** Every
existing game is pixel-identical by construction, and the proof is a diff of
rendered frames, not an argument.

The stairs path replaces "first hit" with the classic portal-style column walk
(Doom/Build), done per column, front to back, with one clip value:

1. Cast the DDA as today, but **record every grid line crossed** — its corrected
   distance and the floor height of the cell entered — until a wall edge or the
   render distance. (A wall still ends the ray; steps never do.)
2. Keep `clip_bottom`, starting at the bottom of the view. For each crossing
   at distance `d`, from the camera's cell outward:
   - **tread** of the cell being left: the span from `y(h_cur, d)` down to
     `clip_bottom`; record it for the floor cast, then
     `clip_bottom = min(clip_bottom, y(h_cur, d))`;
   - if the next cell is **higher**, draw its **riser** from `y(h_next, d)` to
     `y(h_cur, d)`, clipped, then lower `clip_bottom` to its top;
   - if the next cell is **lower** (a ledge), nothing is drawn: its tread is
     automatically hidden behind the nearer edge by `clip_bottom`.
   - Stop early once `clip_bottom` reaches the top of the view.
3. At the wall: draw the wall from `y(ceiling, d)` down to `clip_bottom` (its
   base is hidden behind nearer steps for free).
4. A tread above eye level faces away from the viewer and produces an empty
   span automatically; risers above the horizon simply cover the ceiling.

Per-column work grows from one hit to at most `2 × render_distance` crossings
(cheap integer steps); the cost that matters is the floor (step 5).

5. **Floor cast becomes column-major.** Today's row-major cast assumes one
   floor plane. With heights, each low-res floor pixel belongs to a recorded
   tread span of known height `h`, so its distance is
   `d = (eye_z − h) × view_h / (y − horizon)` and the texel is
   `camera + d × ray_dir`. Same number of texel lookups as today (only floor
   pixels are cast), different `h` per span. Measured in S2: casting the
   whole floor this way beats keeping today's row-major ground cast and
   re-casting only the treads (that casts tread pixels twice). Treads use the step's
   `top_texture` (falls back to the floor texture, then to a flat colour);
   risers use `side_texture` (falls back to the wall texture, then flat), with
   the same `wall_shade` side/fog model as walls. The ceiling cast keeps its
   plane at `ceiling`, so it only needs `eye_z` instead of a constant.

6. **Billboards** stand on the floor of their own cell: their vertical centre
   moves by `(eye_z − (floor(cell) + EYE_HEIGHT)) × view_h / d` — zero when
   both are on the ground, so unchanged today. Occlusion: each column keeps
   its list of `(distance, clip_bottom)` steps from the walk, and a billboard at
   distance `D` draws only the rows above the clip reached before `D` (plus the
   existing wall-distance test). A monster half hidden behind the top step of a
   staircase is clipped correctly.

### Movement: climbing, blocking, dropping

All of it in the extension, through frame hooks, with **no core change**:

- `before_step`: remember each mover's `(x, y)`.
- `after_collision` (after core has moved and resolved solid walls): for each
  instance that moved, look up the floor height of the cell under its sprite
  centre. If it is more than `max_step` above the floor it stood on, undo the
  move **per axis** (try keeping x only, then y only, then neither), so the
  player slides along the edge of a ledge exactly as along a wall.
- Who obeys it (D4): the camera, plus every non-solid, non-step instance that
  moved this frame (monsters, projectiles). Pickups don't move, so they are
  unaffected.
- `max_step`: new optional parameter on **Enable Raycast View**, default 12 px
  (stairs of 8 px climb, a 16 px block does not).
- **Eye smoothing**: the camera's `eye_z` eases toward its target instead of
  snapping — up at a fixed climb speed (≈2 px/frame, like Doom's view-height
  easing), down with gravity when stepping off a ledge. Stored per room in
  `raycast_state(room)["eye_z"]`, reset on room entry. Gameplay position is
  still 2D; only the view rises and falls.
- Readable from events (D5): `raycast_floor_z` on the camera instance, so an
  author can test "am I on the platform?" with an ordinary `test_variable`.

### Exports

Same design, same numbers, hand-ported as for every earlier raycast feature:

- **HTML5** (`export_html5.js`): `set_floor_height` via
  `registerExtensionAction`; the stairs render path on `GameRoom.prototype`;
  movement through `registerFrameUpdate` (verify where it runs relative to
  movement before relying on it — it was added for multiplayer interpolation).
- **Kivy** (`export_kivy.py`): codegen for the action, the stairs path in
  `SCENE_CODE` (still in GM y-down space; only the final draw flips, as the
  existing renderer does), the movement rule in an `_ext_update__raycast_2_5d`
  scene hook. `SCENE_CODE` is %-formatted: double every `%`.
- **Parity**: extend `tests/test_raycast_export_parity.py` with a "column walk"
  contract — given the same walls + height map, desktop and Kivy return the
  same list of crossings, spans and riser extents (exact), plus `y(Z, d)` and
  the eye-easing step. HTML5 stays structural (no JS engine in CI), with a
  Playwright frame comparison on the dev box (skips in CI), as micro:bit
  Stage P did.

## Decisions

Recommended choice first. The plan assumes these unless the owner says
otherwise.

- **D1 — Fix F1 (floor eye height) for existing games too?** *Recommended:
  yes, as its own unit (S1), on all three targets, with before/after
  screenshots of `raycast_1`–`4` for the owner to look at.* It is a real
  rendering inconsistency, and leaving it means the stairs path and the flat
  path would draw the same floor differently. It does change how the floor of
  every existing raycast game looks (tiles at their true size, locked to the
  wall bases), so it needs a yes. If no: the stairs path uses the correct eye
  height and the flat path keeps today's floor; S1 is skipped.
- **D2 — Height authored per object via an action**, not a tile height map
  (reasons above).
- **D3 — Constant ceiling, configurable via `wall_height`.** No per-area
  ceilings in this plan.
- **D4 — Step rule applies to the camera and to all moving non-solid
  instances.** Alternative: camera only, plus an opt-in action for monsters —
  more to teach, and monsters would otherwise glide up a wall-high platform.
- **D5 — Expose the floor height as `raycast_floor_z`** on the camera.

## Non-goals (could be later plans)

Looking up/down (pitch), jumping and crouching (jumping is a natural next step:
it is `eye_z` with a vertical speed), slopes/ramps (build them from small
steps), rooms over rooms, per-area ceiling heights, lifts/doors with
animated heights (a step instance can already be moved or destroyed),
step-aware collision for solid walls, the top-down 2D view drawing heights.

## Units (one commit + push each; full raycast test files + smoke after each)

- [x] **S0 — This plan.** `d936e1ae`
- [x] **S1 — F1 fix (only if D1 = yes).** `ee271f2d` (D1 = yes, owner 2026-11-20). `pos_z` follows the wall pass's eye
  height on desktop, HTML5, Kivy. Parity test pins the shared formula; a test
  asserts the floor texel sampled at a wall's base row is at the wall's own
  distance (assert *where*, not that something drew). Before/after PNGs of
  `raycast_1`–`4` via `PYGM_SCREENSHOT` for the owner.
- [x] **S2 — Timing spike (throwaway, not committed code; result recorded here).**
  Done 2026-11-20 on the Linux box (Python 3.12, pygame 2.6.1). **Gate
  passed; design confirmed: the stairs path casts the WHOLE floor
  column-major (variant A), the ceiling stays row-major.**
  - Prototype: a copy of `render_raycast_view` with the crossing-recording
    DDA, the column walk, textured risers (same crop/scale/shade trick as
    walls), textured walls clipped to `clip_bottom`, a column-major low-res
    floor cast over the recorded spans, and the ceiling as today's row-major
    cast with `pos_z` from `eye_z`. Room: 15×15 cells, 5-wide staircase of
    8-px steps to a 32-px platform, a 64-px block, `wall_height` 3, 320
    columns, `floor_cast_res` 4, raycast_4's real textures. Screenshots from
    three poses (facing the stairs, at their foot, on the platform looking
    down) were checked by eye: steps, treads lined up with the grid, the
    lower floor seen from the platform, the too-high block -- all correct.
  - Two floor designs measured (ms/frame, two runs agreed within 0.5 ms):

    | 640×480 | today's renderer | B: row-major base floor + re-cast treads | **A: whole floor column-major** |
    |---|---|---|---|
    | staircase filling the view | 17.8 | 27.0–27.4 | **22.1–22.6** |
    | on the platform looking down | 17.8 | 23.0 | **18.2–18.4** |
    | full turn in the stairs room | 17.8 | 21.4–21.6 | **18.5–18.8** |

    (480×480: today 14.4; A 19.2–19.7 / 15.3 / 15.3–15.6.) B casts every
    tread pixel twice (as ground, then as tread), so it is strictly worse; A
    casts each floor pixel exactly once at its own height. A's worst case is
    +27 % over today, a full turn +5 %; the existing guard
    (`textured < flat × 6 + 15 ms`) is nowhere near. 22.6 ms leaves ~10 ms of
    a 30-fps frame for game logic on this machine; `floor_cast_res` 8 and
    fewer `columns` remain the escape hatches on slow school PCs.
  - Profile (stairs ahead): the two plane casts are about half the frame;
    the column walk (recording ~10–20 crossings per column) about 10 %;
    risers (one scale+blit each, like a wall strip) are cheap. Lesson for
    S5/S6: write the per-pixel loops the way `cast_floor_plane` does (plain
    `if` clamps, local aliases) -- a `min()` per pixel cost the first spike
    run ~4 ms.
  - Also seen: in the walk, a miss column (no wall within render distance)
    needs a final span from the last crossing to the horizon, or its floor
    is left unpainted. Keep that in S5/S6.
  - Regression guard to add in S6 (relative, CI-noise-proof like the existing
    one): the stairs frame stays under 1.6× today's renderer on the same
    room (measured 1.27×).
- [x] **S3 — `Set Floor Height` + the height map.** `f0b05af9` (2026-11-20).
  Schema in `actions.py` (category "3D View", icon 🪜, params `height` default
  8, `top_texture`, `side_texture`), handler (records
  `raycast_floor_height` / `raycast_step_top_texture` /
  `raycast_step_side_texture`; garbage, NaN or inf height -> 0),
  `extension.json` `provides_actions`, new `heights.py`
  (`is_step`, `max_floor_height`, `build_floor_heights`: sprite-box cell
  coverage, origin-aware, a box ending on a grid line stays in its cells,
  highest wins with its textures, clamped to `0..max` with ONE warning per
  instance, solid instances never steps; stored as `floor_heights` /
  `floor_textures` in the raycast state), billboard exclusion (desktop).
  `tests/test_raycast_floor_heights.py` (20 tests, five mutations all caught).
  **Scope moved here from S13:** the action's display name is translated in
  all ten languages in this commit (both Qt contexts, `.qm` recompiled) --
  `tests/test_extension_action_i18n.py` requires it (count 47 -> 48), and
  the repo's rule is "translated the same commit". Parameter labels and
  descriptions are still S13. Nothing calls `build_floor_heights` yet (S5
  does); HTML5/Kivy still draw a step as a billboard until S10/S11.
- [x] **S4 — `wall_height` + eye-height constant split.** `00d811a2` (2026-11-20).
  New optional `wall_height` on Enable Raycast View (cells, default 1.5,
  clamped to 1–10 where it is used: `renderer.clamp_wall_height`, HTML5
  `raycastClampWallHeight`, Kivy `_clamp_wall_height`; the handler and both
  export config builders store the number as given). Named constants on all
  three targets: `RAYCAST_EYE_HEIGHT` 0.75, `RAYCAST_TEXTURE_HEIGHT` 1.5,
  min/max wall height; `RAYCAST_WALL_HEIGHT` 1.5 stays as the default.
  Walls grow UPWARD from a fixed base (eye, horizon and wall bases never
  move); **the wall texture repeats every 1.5 cells, anchored at the floor,
  instead of stretching** (decided here: bricks keep their size, as in Doom;
  the default wall is exactly one tile). The ceiling cast takes the plane's
  height from the eye (`plane_height` / `planeHeight`, default the eye
  height; the ceiling passes `wall_height − eye`). Desktop's per-tile blit
  moved verbatim into `blit_wall_tile`.
  **Proof the default is unchanged**, against a snapshot of the previous
  HEAD: desktop 768 frames byte-identical (8 settings incl. letterbox, sky,
  textured/flat, 97 columns; 2 window sizes; random poses incl. exactly on
  grid lines); Kivy 150 frames instruction-for-instruction identical through
  the stub harness (and the same harness does see `wall_height` 3 as a
  change); the four raycast samples' frame-90 screenshots identical. HTML5
  could not be executed here (no Playwright on this box): the edit mirrors
  desktop line for line and its source is pinned structurally.
  `tests/test_raycast_wall_height.py` (22 tests: wall top/base rows against
  the projection formula, texture repeat vs stretch, floor anchoring, half
  tile, ceiling meeting the raised wall top both directly and through the
  real render, clamping, schema, handler, HTML5 structure, Kivy stacked tile
  rectangles); six mutations all caught. Six existing SOURCE-TEXT checks
  (`test_html5_raycast.py` ×4, `test_raycast_export_parity.py`, and S1's
  HTML5 check) pinned the old expressions (`full_h = … RAYCAST_WALL_HEIGHT`,
  the one-call `drawImage`, `posZ = 0.5 * RAYCAST_WALL_HEIGHT * viewH`);
  each was repointed at the equivalent new expression, keeping the property
  it protects (unclamped height, cropped texture, view-height scaling).
- [x] **S5 — Desktop stairs path.** `b1c41d69` (2026-11-20). In
  `renderer.py`: `build_floor_heights` runs every frame; a room with no
  step keeps the old single-hit code untouched (still byte-identical to
  pre-S4 HEAD over the 768-frame proof). With steps, each column takes
  `_draw_stairs_column`: `cast_ray_steps` (cast_ray plus the crossings where
  the floor height changes; its wall result equals `cast_ray`'s bit for bit,
  pinned over 300 random rays), `layout_column` (pure geometry, the parity
  target for S10/S11: treads at every height incl. 0, risers, the clipped
  wall, per-crossing occluders for S7), then drawing. The eye is the floor
  under the camera's centre + `RAYCAST_EYE_HEIGHT` (snaps; S8 eases it);
  the ground floor/ceiling casts take their plane heights from it.
  **Change from the plan: risers are already TEXTURED here** (step side
  texture, else wall texture, else flat wall colour) -- a riser is just the
  slice of a wall between two heights, so `draw_wall_rows` draws walls and
  risers alike, tiles anchored at height 0. Only raised TREADS are still flat
  (floor colour); S6 casts them.
  **Speed:** first cut 35 ms vs 20 ms for the same room without steps
  (640×480, textured, staircase filling the view) -- over the plan's 1.6×.
  A per-frame cache of scaled+shaded strips (a riser facing the camera has
  the same distance in every column) plus cheaper clamps brought it to
  **30 ms (1.5×)**; a full turn 25.5 vs 21 ms. Both changes were proven not to
  move a pixel (150 stairs frames hashed before/after, and cache on vs off).
  Guard added: stairs < 1.6× flat + 5 ms. Lesson: reordering a float
  expression (`* (view_h / d)` vs `* view_h / d`, `a // b` vs
  `floor(a / b)`) DID change pixels -- keep the original expressions.
  `tests/test_raycast_stairs_render.py` (17 tests: ray/crossings, exact
  riser/tread/wall rows, ledge hiding the near lower floor, a step above the
  eye, a riser hidden behind a taller nearer one, early stop, miss to the
  horizon, rendered rows, the raised eye, side texture, a room without steps
  never entering the path, an authored project through the real GameRunner,
  the speed guard). Mutations: 8 of 9 caught; the survivor (draw risers on
  drops too) is equivalent -- a drop's front is always below the clip.
- [x] **S6 — Textured treads.** `825a9dfb` (2026-11-20). The stairs path
  is now three passes: lay out every column (`_layout_stairs_column`), cast
  the whole floor column-major (`cast_stairs_floor`: each low-res pixel at
  its own tread's height, texture = the cell's step top texture, else the
  floor texture, else the flat floor colour; the row-major ground cast is
  skipped in stairs rooms), then draw risers and walls at full resolution on
  top (`_draw_stairs_column`) so their edges stay crisp. A low-res block that
  straddles a tread edge takes the nearest tread at or below its sample row;
  the riser/wall drawn over it covers the overhang, so no block is ever
  unpainted (a mutation pre-filling the buffer magenta could not make the
  no-gap test fail). No floor texture and no step top texture -> no cast at
  all (flat treads as in S5). Rooms without steps still byte-identical over
  the 768-frame proof. Speed (640×480, textured, staircase filling the view):
  30.5 vs 20.5 ms (1.5×, unchanged from S5); full turn 27.7 vs 22.4 ms.
  `tests/test_raycast_stairs_floor.py` (18 tests: the ground just below a
  riser and the tread just above it both sampled at the riser's line, the
  raised eye from the platform, per-cell top textures, top texture alone,
  no gaps at res 1 and 4 over six poses, flat rooms skip the cast); 6 of 7
  mutations caught, the survivor is the magenta pre-fill above.
- [ ] **S7 — Billboards on steps.** Lift by their cell's floor; per-column clip
  profile occlusion. Tests: a pickup on a platform is drawn higher by the
  predicted amount; a billboard behind a riser loses exactly its lower rows.
- [ ] **S8 — Climbing.** Frame hooks (`before_step` snapshot, `after_collision`
  per-axis undo), `max_step` parameter, eye easing up/gravity down,
  `raycast_floor_z`, reset on room entry/restart. Tests through the real loop:
  walk up a staircase of 8 px steps; blocked by a 16 px block; slide along a
  ledge; drop off and land; a monster patrolling into a high block turns back
  (its own collision/stop logic, not stuck in place); `restart_room` resets
  the eye.
- [ ] **S9 — Minimap shows raised cells** (shade by height; ordinary
  rectangle commands, so `draw_minimap` stays a macro action on every target).
- [ ] **S10 — HTML5 port** (render path, action, movement). Structural tests +
  real export string checks + brace-balance guard (no `//` pairs or brackets
  inside string literals — `test_export_html5_extension_syntax.py`); a
  dev-box Playwright frame comparison against desktop.
- [ ] **S11 — Kivy port** (codegen, `SCENE_CODE`, movement hook). Parity test
  (exact column walk), stub harness, generated-file compile, a real-Kivy
  render under `tests/_real_kivy_render.py`, and the all-extensions-on
  coexistence test.
- [ ] **S12 — Sample `raycast_5` ("Stairs" / « Les escaliers »).** A small
  level built to show the feature: a staircase up to a gallery with the goal
  on it, a block too high to climb, a ledge to drop from, a monster on the
  lower floor, `wall_height = 3`. Generator committed under `tools/` (like
  `gen_raycast_3_maze.py`) with a test pinning the room JSON. `README.md` +
  `README.fr.md` (accents checked), Welcome-tab entry + its translation in
  every shipped `.ts`, smoke list, `test_edition_sample_filter` if needed,
  a sample test that climbs to the goal through the real loop.
- [ ] **S13 — Docs and translations.** Extension `README.md`; the new
  parameter strings (action display names are done with their unit, as S3
  did) in all ten languages' `.ts` (split files for
  de/it/ru/sl/uk, monolithic for the rest — re-derive per context, don't
  assume); `wiki/3D-View.md` + `_fr` (other languages fall back, as before);
  regenerate the action reference with `tools/gen_action_reference.py`
  (force all extensions on for that process on this machine) and add the
  localized strings to `tools/action_ref_i18n.py`; CHANGELOG.

Optional, only on request: a tutorial lesson 15 following
`docs/RAYCAST_TUTORIALS_PLAN.md`'s format, and the teacher-resource handouts.

## Risks and landmines to carry in

- **Exact-grid-line coincidence** (the 2026-07-17 raycast bug): a camera or
  step sprite at an exact cell edge sits on a grid line. Sample the floor
  under a sprite **centre**, never raw `x/y`, in both the renderer and the
  movement rule.
- **Performance in pure Python** is the real risk, hence S2 before S6.
- **The loader imports the extension under a synthetic package name**: a spy
  on the renderer or a frame hook must patch the loaded module
  (`_loaded_renderer()` in `tests/test_raycast_viewport.py`).
- **Schemas exist only after `load_all_plugins()`**: tests that query
  `get_action_type("set_floor_height")` must load plugins first.
- **Kivy `SCENE_CODE`** is %-formatted (double `%`); Kivy is y-up (flip only at
  draw time).
- **Assert where things land, not that something drew** (the minimap lesson):
  every geometry test checks a computed screen row or distance.
- **Needs human eyes at the end**, as every raycast arc has: how climbing
  *feels* (easing speed, step height), and the HTML5/Android renders of
  `raycast_5`. List it in `docs/RELEASE_QA_CHECKLIST.md`.

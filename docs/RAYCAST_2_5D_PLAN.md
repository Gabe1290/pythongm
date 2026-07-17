# Plan: Doom/Wolfenstein-style raycast 2.5D rendering mode

Status: **Phase 0 + Phase 1 DONE (2026-07-16, desktop/pygame only).**
Written in response to a direct ask: "how hard would a 3D extension be,
and if hard, scope out a fake 2.5D instead," then given an explicit
go-ahead to start ("start work based on maze_1 with flat color walls to
start, then... flat textures... then an outside horizon like in DOOM").
Phases 2 onward (HTML5/Kivy parity, textures, sky/horizon, sprites) are
still ahead — see the phase list below for current per-phase status. Not
linked from `docs/DEFERRED_ITEMS_PLAN.md` — this is a new feature, not an
item from the existing deferred-features registry.

## Phase 0 + Phase 1 — what actually landed

- **Phase 0 spike, validated**: pure-Python DDA raycasting against
  maze_1's real 15×15 grid measured ~1.6ms/frame at 320 columns (≈636fps
  ceiling) — the performance risk flagged in the original scope-out did
  not materialize; no numpy/Cython needed. Correctness verified visually
  via rendered PNG frames (a corridor view with correctly-converging side
  walls and floor/ceiling perspective triangles).
- **`GameInstance.facing_angle`** (`runtime/game_runner.py`): new
  persistent float, GM angle convention (0=right/90=up/180=left/270=down,
  matching `set_direction_speed`/the `direction` property), independent
  of `hspeed`/`vspeed` — needed because the existing `direction` property
  is read-only and derived from velocity (0 when stationary), exactly the
  gap flagged during the original scope-out.
- **`set_facing_angle` action** (`runtime/action_executor.py`):
  absolute/relative, same shape as every other `set_*` action.
- **`GameRoom.raycast_camera`** + **`enable_raycast_view` action**: wall
  map is *derived* from the room's existing solid instances — no new
  authoring format, so every existing grid-based maze sample is
  raycastable for free. Cached per room, invalidated on a `cell_size`
  change. *(Originally a coarse per-cell occupancy grid via
  `_build_raycast_grid`/`_raycast_is_wall` — superseded 2026-07-16 by
  edge-based `_build_raycast_walls`, see "Complete rethink" below; kept
  here as the historical record of what shipped first.)*
- **`GameRoom._cast_ray`/`_render_raycast_view`**: DDA core + flat-color
  wall/floor/ceiling rendering, side-based shading (x-face vs y-face) as
  a free depth cue. Hooked into `_render_room` as an early-return —
  raycast mode fully replaces the normal top-down render for that room
  (not an overlay); game *logic* is completely unaffected, only this
  method's picture changes.
- **`samples/raycast_1/`**: a new sample, walls/rooms literally copied
  from `maze_1` (same grid, same layout — the "reuse existing content"
  bet paid off exactly as scoped), `obj_person` rewritten for FPS-style
  controls (continuous turn via `set_facing_angle`, forward/back via
  `set_direction_speed(direction="facing_angle[+180]", ...)` — both
  resolve `facing_angle` as a bare expression variable through the
  existing generic `hasattr(instance, name)` expression resolver, no
  new expression-evaluation code needed). Wall collision is the
  **existing** solid-instance movement-blocking system, completely
  unchanged — confirms the core "2.5D" premise: gameplay stayed 2D, only
  the picture changed.
- Manually smoke-tested through the real `GameRunner` loop (headless,
  injected key events, mirroring `tools/smoke_run_samples.py`'s
  pattern) and visually verified via rendered PNG frames: turning,
  forward movement, and automatic wall-blocking all behaved correctly.
- Regression tests: `tests/test_raycast_view.py` (26 tests) —
  `set_facing_angle`/`enable_raycast_view` action behavior, wall-grid
  derivation, **deterministic DDA geometry tests with closed-form
  expected distances** (not "doesn't crash" — the same discipline that
  caught the inverted fade-alpha bug earlier this session), a real-Surface
  pixel-sampled render test, a performance regression guard, and an
  end-to-end smoke run of the real sample through the real `GameRunner`
  loop. Full suite 1829 → 1855 passed, 0 failed.

**Known v1 gaps, by design** (not bugs, scoped out deliberately):
Kivy/HTML5 parity (Phases 2-3, not started — `raycast_1` currently only
runs on desktop); no textures (flat colors only, Phase 5 per the original
phase list, now reordered — see below); no sky/horizon; no billboard
sprites for `obj_goal` in the first-person view; no HUD compositing while
raycast mode is active (documented in code comments in `_render_room`).

## Playtesting fixes (2026-07-16, after Phase 1 shipped)

Two rounds of real playtesting on `raycast_1` surfaced three real bugs,
all fixed:

- **Ceiling read as an indoor/dark tone.** `enable_raycast_view`'s
  `ceiling_color` default was `#1e1e28` (dark navy); changed to `#87CEEB`
  (sky blue, matching this codebase's own existing `GameRoom.background_color`
  default) in both the action's default and `_render_raycast_view`'s own
  internal fallback (a second, separate hardcoded default that also
  needed fixing).
- **Side-wall shading barely visible.** The x-face/y-face shading factor
  was `c * 3 // 4` (only 25% darker); changed to `c // 2` (50% darker) —
  a much clearer depth cue.
- **Player could walk through walls, or get stuck unable to turn a
  corner.** Two related but distinct root causes:
  1. This engine's movement-blocking check is gated behind
     `get_collision_listened_types()` as a perf optimization — it only
     runs when at least one side has a *registered*
     `collision_with_<object>` event, even though the geometric block
     itself doesn't depend on that event's actions. `raycast_1`'s
     `obj_person` dropped its `collision_with_obj_wall` handler when
     rewritten for continuous movement (wrongly assuming the block was
     unconditional). Fixed by restoring the handler with empty actions,
     just to register it.
  2. Even with blocking restored, `spr_person`'s collision bbox was
     ~32×31 — essentially the full 32px grid cell. Every corridor and
     gap in a `maze_1`-derived layout is exactly one cell (32px) wide,
     so a full-cell player needs *exact*, zero-tolerance alignment to
     pass through a perpendicular gap — unachievable with continuous
     (non-grid-snapped) movement, which will always have some drift.
     Fixed by giving `raycast_1`'s own copy of `spr_person` (not
     `maze_1`'s shared asset — kept fully independent to avoid any risk
     to that sample) an explicit, smaller collision bbox: `(8,8)-(24,24)`,
     an effective 16×16 box with 8px of clearance per side. Harmless
     here since the sprite never renders in first-person mode anyway —
     this is purely a movement-feel parameter now, decoupled from visual
     size.
- Regression tests added: `test_side_shading_is_half_brightness` (direct
  pixel check) and `test_player_can_turn_a_corner_in_the_maze` (places
  the player 5px off-center from a known 1-cell gap and confirms it still
  passes through — verified during development that this specific
  scenario reproduces the bug against the pre-fix bbox and is fixed by
  the post-fix one, not just "passes regardless"). An earlier draft of
  the corner-turning test walked a perfectly cardinal-aligned path that
  never drifted at all and passed even without the fix — worth noting as
  a reminder that a scripted-input smoke test can *look* like it
  exercises a bug class without actually discriminating pass/fail on it;
  the fix was to explicitly verify the test fails against the pre-fix
  code, not just that it passes against the post-fix code.
- Suite 1855 → 1858 passed, 0 failed.

## Complete rethink: thin edge-walls, not full-cell blocks (2026-07-16)

Even after the bbox fix above, a third playtesting round found the
player *still* getting stuck unable to turn corners. The user's own
diagnosis was right: patching bbox sizes was chasing a symptom. The
actual root cause was architectural, and specific to `raycast_1`'s
maze data — **every corridor and every wall in a `maze_1`-derived
layout is exactly one 32px grid cell**, because walls there are
full-cell solid blocks, not thin partitions. A corridor bounded by
full-cell walls on both sides is *exactly* 32px wide — no amount of
shrinking the player recovers real turning clearance once you're also
subtracting a full 32px wall block's footprint from each neighboring
cell at a corner. Genuine clearance requires the walls themselves to be
thin, matching how real Wolfenstein/Doom-style engines actually
represent a map: walls are thin segments on cell *edges*, not blocks
occupying whole cells.

That, in turn, exposed a second, deeper mismatch: **collision and
raycasting disagreed about what "wall" meant.** Collision
(`check_movement_collision_with_blocker`) already used real per-instance
AABB geometry — thin wall objects would have collided correctly with
zero engine changes. But `_build_raycast_grid` (the original raycasting
wall-map builder) worked on **coarse per-cell occupancy**: any solid
instance touching a cell made the *whole* cell opaque for ray-marching,
regardless of the instance's actual size. Making wall sprites thin
would have changed nothing visually — the raycaster would still have
drawn a full 32px block wherever a thin sliver touched a cell, while
collision quietly let the player through most of that same cell. Fixing
only the maze content, or only bbox sizes, could never have closed this
gap on its own.

**The fix, chosen after presenting the user two options (widen
corridors within the existing block-wall model vs. this) and getting
an explicit go-ahead for the real one:**

1. **`GameRoom._build_raycast_walls`** (replaces `_build_raycast_grid`)
   derives thin wall **edges**, not cell occupancy, from solid
   instances — keyed as `v_walls: {(line_x, row)}` / `h_walls: {(col,
   line_y)}`, absolute grid-line indices, not cells. A solid instance's
   sprite aspect ratio decides its role: wider-than-tall → a horizontal
   edge segment; taller-than-wide → vertical; roughly square (e.g. an
   old-style full-cell block) falls back to blocking all 4 edges of its
   cell, so non-thin-wall content still works unchanged (verified via
   `TestBuildRaycastWalls::test_square_solid_instance_blocks_all_four_edges_of_its_cell`).
2. **`GameRoom._cast_ray`** now checks, at each DDA step, whether the
   *specific grid line just crossed* carries a registered edge —
   instead of whether the cell just entered is occupied. This is the
   textbook Wolfenstein-style DDA (the algorithm already naturally knows
   which line it just crossed via the existing `side_x < side_y`
   step-selection; the only change is what's looked up at that line).
   Rays now march freely through any number of open cells and stop only
   at an actual wall's real position — confirmed with
   `test_thin_horizontal_wall_only_blocks_its_own_row`: a wall registered
   for row 0 does not block a ray one row over.
3. **No changes needed to collision at all** — it already did real
   geometry. This is exactly the payoff of the "2.5D: only the picture
   is faked" design: fixing the *rendering* model didn't require
   touching *gameplay* code.
4. **Removed the implicit "out of room bounds = wall" rule.** With real
   edges, an unenclosed map is a content bug (the maze needs its own
   boundary wall segments), not something the raycaster should paper
   over — an open ray now just marches to `render_distance` and stops
   cleanly, no crash, no infinite loop (`test_no_walls_at_all_reaches_max_cells`).
5. **`samples/raycast_1/` regenerated**: new thin sprites `spr_wall_h`
   (32×8) / `spr_wall_v` (8×32) and objects `obj_wall_h` / `obj_wall_v`
   replace the old `spr_wall`/`obj_wall` full-block pair (deleted, along
   with their now-dead side files). `rooms/room0.json` and `room1.json`
   were regenerated from the *original* block-wall layout via a
   topology-preserving conversion (not hand-redesigned): for every open
   cell, place a thin edge wherever a neighboring cell (or the room
   edge) is solid in the *original* data, leaving no edge where both
   neighbors were open. This preserves the exact original maze
   connectivity/solvability while giving every corridor its full 32px
   width — confirmed the conversion correctly reconstructs a column that
   was a single long open shaft in the source data (not a "1-cell gap",
   as an earlier, wrong assumption about the maze's shape had it) purely
   from re-deriving edges, with no hand-authored corrections. `obj_person`
   gained `collision_with_obj_wall_h`/`_v` registrations (same
   empty-actions-just-to-register pattern as the earlier fix, now against
   both new wall object names).
6. Verified with a multi-corner walkthrough (not just one gap): starting
   at the spawn point, walk east, turn north into a shaft, walk the full
   height of the maze (12 rows), turn west, walk further — all with
   realistic key timing, no stuck states, reaching deep into the maze
   each time.
7. Regression tests reworked: `TestBuildRaycastWalls` (was
   `TestBuildRaycastGrid`) covers the aspect-ratio-based edge derivation
   and the square-instance backward-compat fallback;
   `TestRaycastIsWall` (a method that no longer exists) removed;
   `TestCastRay` gained thin-wall-specific cases and dropped the
   out-of-bounds test (behaviour removed by design, see point 4);
   `test_player_can_turn_a_corner_in_the_maze` rewritten around a real
   multi-frame walk-turn-walk sequence against the new content (its
   predecessor's hardcoded pixel coordinates were tied to the old
   block-wall geometry and stopped being meaningful once the walls moved).
   Suite 1858 → 1857 passed, 0 failed (net -1 test count from
   consolidating the old corner test into the new one, not a coverage
   loss — see the diff for what each test now covers).

**Takeaway for later phases**: this is now the correct foundation for
Phase 5 (textures) — a texture needs to know exactly which wall segment
and which face was hit, which edge-based walls give directly (the
segment *is* the addressable unit), where the old coarse-grid model
would have needed guessing which of possibly several instances touching
a cell was actually hit.

## What this is, precisely

Not real 3D. A **raycast projection**: the room stays a normal 2D grid
of GameObjects; a camera has a 2D position `(x, y)` plus a facing angle;
for each screen column, cast a ray from the camera through the grid
until it hits a solid cell, then draw a vertical strip whose height is
inversely proportional to the hit distance. This is exactly how
Wolfenstein 3D (1992) and the id Tech 1 engine underneath the original
Doom worked, and it's popular for exactly the reason it fits this
project: **no GPU, no 3D math library, no z-buffer beyond one float per
screen column** — it's O(screen-width) per frame, cheap enough for pure
Python/JS.

Gameplay logic — collision, movement, events — **stays entirely 2D**,
unchanged. Only the picture on screen is faked into looking 3D. That's
the whole "2.5D" idea, and it's why this is tractable where true 3D
isn't (see the prior chat answer this doc follows from): it needs zero
new rendering backends (no OpenGL/WebGL on any of the three export
targets — confirmed HTML5 uses plain `getContext('2d')` and Kivy's
exporter has no OpenGL/3D usage at all today), because a raycast "wall
strip" is just a filled/textured rectangle — a primitive all three
targets already draw.

## Why this is the right scope, pedagogically

The user's framing was explicit: this needs to be "sufficient to waken
student interest" before they move to a dedicated 3D tool. Raycasting is
historically *the* teaching engine for exactly that transition — it's
simple enough to explain the whole pipeline in one classroom session
(cast a ray, measure distance, draw a strip), produces an immediately
recognizable "I'm inside my own maze" result using content students
already built (the existing `maze_*` samples are solid-walls-on-a-grid —
literally a raycast map already), and its limitations are pedagogically
honest hooks into "real" 3D: no vertical look (no pitch), corridors must
be grid-aligned, no true room-over-room, no arbitrary camera roll. A
student who asks "why can't I look up?" has just asked the question that
motivates learning a real 3D engine.

## Architecture fit — what already exists to build on

- **Walls are already grid-solid `GameObject`s.** Every `maze_*` sample
  places solid wall instances on a grid; `runtime/game_runner.py` already
  has `solid`-flag collision and a grid-size/snap-to-grid concept
  (`_get_step_grid_size`/`snap_to_grid`, used by `move_grid`-style
  actions). A raycast wall map can be **derived from existing room
  content** — bucket each solid instance into a grid cell by
  `(x // cell_size, y // cell_size)` — rather than inventing a new
  authoring format. This is the single biggest scope-reducer: no new
  room-editor UI is required for a first version.
- **Viewports already exist.** `enable_views`/`set_view` (added for
  `views_1`/`views_2`) already give a named screen rectangle
  (`port_x/y/w/h`) clipped via `screen.set_clip` on desktop, and
  equivalent per-target clipping on HTML5/Kivy. A raycast camera can
  reuse a view's port rectangle as its render target instead of
  inventing a new viewport concept.
- **The draw-queue pattern is the right integration seam.** Every
  structured draw action (`draw_rectangle`, `draw_health_bar`, ...) is a
  `{'type': ..., ...}` dict interpreted by `_DRAW_HANDLERS` on desktop,
  `_dq_render_cmd` on Kivy, `renderDrawCommands` on HTML5. A
  `raycast_view` draw command (computed once per frame, containing the
  per-column strip data) fits this seam exactly — the actual DDA-cast
  loop runs once in the action's execute step (or once per frame in a
  dedicated render hook, TBD in Phase 1), and each target's renderer just
  draws the resulting strips, which is only ever rectangles or scaled
  1px-wide sprite slices — primitives that already exist everywhere.
- **`direction` does NOT already fit as camera facing — this needs new
  state.** Checked `GameInstance.direction`: it's a **read-only property
  derived from `hspeed`/`vspeed` via `atan2`**, returning `0` when
  stationary (GameMaker parity, added so `direction+90`-style expressions
  resolve in collision handlers). It cannot represent "player is
  standing still but looking left" — an FPS-style camera needs a
  **persistent stored facing angle**, independent of velocity. This is a
  real new piece of instance state (e.g. `instance.facing_angle` or a
  camera-config field), not something to reuse from the existing
  movement system.

## Phased plan

**Reprioritized 2026-07-16** per explicit direction after Phase 1 shipped:
next up is flat *textures* for walls/floor/ceiling, then an outside
sky/horizon (both "DOOM-style" — the original Phase 5/stretch content),
**ahead of** HTML5/Kivy parity and billboard sprites. The phase numbers
below are kept as originally scoped (so this doc's history stays legible)
but the work order is: **0 → 1 → 5 (textures) → new sky/horizon phase →
2/3 (HTML5/Kivy) → 4 (sample) → 6 (sprites)** — note Phase 4's sample
already exists (`raycast_1`, built alongside Phase 1 since deriving the
map from `maze_1`'s content made it nearly free), so what's left of
Phase 4 is folding textures/sky into it as they land, not building a
sample from scratch.

### Phase 0 — feasibility spike (throwaway script, not a feature commit)
**DONE 2026-07-16.**

The one real technical unknown is **pure-Python raycasting performance**.
Wolfenstein-era raycasting was cheap on 1992 hardware because it's
integer/fixed-point DDA in C; this runtime is pure Python (no numpy
dependency currently). Before designing anything further:

- Write a standalone script: a small hardcoded grid map, a DDA raycast
  loop over N screen columns (test at 160, 320, 640), render flat-colored
  strips to a real `pygame.Surface`, and **time it** — target ≥30fps
  headroom (i.e. well under ~33ms/frame) leaves room for the rest of the
  game loop (physics, collision, other rendering) to run in the same
  frame budget.
- Render a few frames to PNG and eyeball them (same "montage + Read
  tool" validation this session already used for the room-fade work) to
  confirm the projection math (fisheye correction via `cos(Δangle)`,
  wall-height = `screen_height / corrected_distance`) actually looks
  right before it's load-bearing for anything else.
- **Decision gate:** if 320-column raycasting is too slow in pure Python
  at a reasonable map size, the fallback is capping render-column count
  (render at e.g. 160 columns and let the blit upscale — an authentic
  period technique, actual Wolfenstein used chunky low-res columns too)
  rather than reaching for numpy/Cython — keep the dependency footprint
  matching the rest of this codebase.

### Phase 1 — desktop runtime core (flat-color walls, no textures/sprites yet)
**DONE 2026-07-16** — see "what actually landed" above.

- New persistent instance state: a facing angle (separate from
  `direction`, per the finding above) plus FOV, render distance/fog
  falloff — likely a small config dict on the room or a dedicated
  "raycast camera" concept, analogous to how `views` config lives on
  `GameRoom`.
- New action, naming to match the `enable_views`/`set_view` precedent —
  e.g. `enable_raycast_view` / `set_raycast_camera` — parameters: which
  view/port to render into, FOV, render distance, wall-color-by-object
  mapping (or texture, once Phase 5 lands), floor/ceiling color.
- Wall-map derivation: build the grid-occupancy map from solid instances
  in the current room once (on room load / camera enable), not every
  frame — this is static room geometry, cache it like the existing
  tile/background caches already do.
- Core DDA cast: one ray per screen column across the camera's FOV,
  march the grid, record hit distance + which wall's mapped color; write
  results into a `raycast_view` draw-queue command (columns × (distance,
  color/texture-id)).
- New `_draw_raycast_view` handler in `_DRAW_HANDLERS` — draws each
  column as a `pygame.draw.rect`/surface fill at the projected height,
  vertically centered, plus flat floor/ceiling fill.
- Player controls: standing/strafing stays on the existing 2D
  hspeed/vspeed + `solid` collision system unchanged (no new movement
  code); only rotation (turning the facing angle) and the "forward is
  wherever I'm facing" hspeed/vspeed computation are new, and both are
  small — likely authorable via existing actions/expressions plus a
  couple of lines of `execute_code`, matching how `match3_*` samples
  already do custom logic without new engine primitives.

(HTML5/Kivy parity moved below — see "Phase 2"/"Phase 3" after Phase 5b,
reflecting the 2026-07-16 reprioritization.)

### Phase 4 — sample game
**Landed alongside Phase 1, ahead of schedule** — `samples/raycast_1/`
already exists (built 2026-07-16), because deriving the wall map from
`maze_1`'s existing content made a from-scratch sample essentially free
once Phase 1's core existed, exactly as this doc originally bet. What's
left of this phase is folding in textures/sky/sprites as those phases
land, not building a sample from scratch.

### Phase 5 — textured walls, floor, and ceiling (NEXT, reprioritized ahead of HTML5/Kivy)

- **Walls**: sample a 1px-wide vertical strip from the wall's sprite at
  the ray's hit position instead of a flat color. The hit position's
  fractional offset within its cell (`side_x`/`side_y`'s fractional part
  at the moment of the hit, already computed by `_cast_ray` — needs
  exposing, not recomputing) gives the horizontal texture-U coordinate;
  `pygame.transform.scale` a 1px-wide subsurface of the wall sprite to
  the strip height. Which sprite to sample needs resolving per solid
  instance hit (currently `_raycast_grid` only stores `True`/`False` —
  will need to store the hit instance's sprite reference too, not just
  occupancy).
- **Floor/ceiling**: classic "floor casting" — for each screen row below
  the horizon, compute the world-space distance for that row (a function
  of row-to-center-of-screen offset, not column), then for each column
  derive the world (x, y) at that distance along that column's ray
  direction, and sample the floor/ceiling texture at that world position
  modulo the texture's tile size. This is a per-pixel-row operation
  (screen_height/2 rows × screen_width columns), meaningfully more work
  than the per-column wall pass — worth a dedicated Phase 0-style timing
  check before committing to full-resolution floor casting; a cheaper
  fallback is a fixed low-res floor grid (checkerboard-style, sampled
  coarsely) if per-pixel floor casting is too slow in pure Python.

### Phase 5b — outside sky/horizon (NEXT, DOOM-style)

- The "outside" look: replace the flat ceiling fill with a horizontal
  strip of sky texture (or a gradient, as a cheaper first cut) whose
  horizontal offset scrolls with `facing_angle` (so turning pans the
  sky, giving a sense of a full 360° horizon even though only a FOV-wide
  slice renders per frame) but does **not** scale/recede with distance —
  classic Doom sky rendering treats the sky as infinitely far away, which
  conveniently means it's the *cheapest* texture in the whole pipeline
  (no per-column distance math, just a horizontal pan-and-tile). Likely
  implementation: a `sky_texture`/`sky_color` param on
  `enable_raycast_view`, applied to the ceiling fill above the horizon
  line only where no wall strip is drawn (open sight-lines, e.g. looking
  over a low wall or out of the maze bounds if a sample ever has open
  areas — `raycast_1`'s current maze is fully enclosed, so this may need
  a second sample, or `raycast_1`'s map opened up at an edge, to actually
  be visible in play).

### Phase 2 — HTML5 parity

- Port the same DDA loop into `engine.js` (a `renderRaycastView`
  function alongside `renderDrawCommands`), draw with `ctx.fillRect` per
  column — natural fit for Canvas2D, no rendering-model change needed.
- New `case 'enable_raycast_view'` (or whatever the action is named) in
  `executeAction`'s switch, mirroring every other action-parity addition
  this session.

### Phase 3 — Kivy parity

- Port the same loop into `export/Kivy/code_generator.py`'s codegen,
  emitting a loop of `Rectangle` graphics instructions per column into
  the object's canvas — mirrors the existing Fbo-based view/camera
  codegen from `views_1`/`views_2`, no OpenGL/3D API needed.

### Phase 6 — billboard sprites (stretch, likely last)

- Render non-wall solid objects (monsters, pickups) as camera-facing
  sprites, scaled by distance, sorted back-to-front (or tested per-column
  against the wall distance array for correct occlusion behind walls).
  This is the piece with the most edge cases (partial occlusion, sprites
  behind the camera, sprites outside the FOV) — sequence it last and
  treat it as genuinely optional for a first ship.

## Testing strategy (matching this session's established discipline)

- **Deterministic geometry tests**: a tiny hardcoded map (e.g. a 3×3
  grid with one wall) + a known camera position/angle has a *closed-form*
  expected wall-strip height and screen position per column — assert
  against that, not against "doesn't crash." (The room-transition-fade
  bug earlier this session was only caught by exactly this kind of
  pixel-level assertion; a "doesn't crash" test alone would have missed
  it.)
- **Performance regression test**: assert a render call for a
  representative map completes under a threshold — this is the one area
  with a real risk of silently regressing into unplayable framerates.
- **Static source-parity checks** for the HTML5/Kivy codegen, following
  `test_kivy_more_actions_export.py` / `test_draw_queue_background_health_bar.py`'s
  established pattern (compile-check generated Python, regex/substring
  assertions against `engine.js` source).
- **Visual sanity via PNG montage + Read tool** during development, same
  as the fade-transition and font-rendering work — cheap and has already
  caught a real, otherwise-invisible bug once this session.

## Rough effort shape

Relative to work already landed this session: Phase 0 is small (a spike,
not a shippable commit). Phase 1 is the biggest single chunk — comparable
in size to the GMK importer hardening pass (new persistent state, a new
action, a new render subsystem, tests) — because it's where the actual
algorithm and integration decisions get made; Phases 2-3 are each smaller
since they're porting an already-proven algorithm, not designing one.
Phase 4 (the sample) is small once Phase 1-3 exist. Phases 5-6 are each
their own medium-sized follow-up, genuinely optional for a first ship.
Total for a flat-color, wall-only, three-target MVP with a sample and
tests: several focused sessions, not one — but a small fraction of what
true `d3d_*`-parity 3D would cost (no OpenGL/WebGL stack to build and
maintain on any target).

## Before committing to this

This doc is a scope-out, not a green light. Per this repo's own
"stability over features" stance and the rc.11 "stop lying to users"
precedent (half-shipped features get torn out, not left half-working),
Phase 1 should ship complete (flat walls, working controls, a sample) on
**all three** export targets before merging to `main`, or it should be
built and reviewed on a feature branch until it is — landing a
desktop-only raycast mode with Kivy/HTML5 silently no-op'ing would
repeat the exact anti-pattern this project has been actively cleaning up
all session (e.g. `TODO.md`'s "UI metadata coverage" notes on what NOT
to expose half-built). This is also the one place in this doc that
should override the repo's usual "commit straight to `main`, no feature
branches" habit — that habit assumes small, always-shippable increments;
a multi-phase new rendering subsystem across three targets does not fit
that shape until Phase 1-3 are done together.

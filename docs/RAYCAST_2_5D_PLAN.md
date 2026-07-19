# Plan: Doom/Wolfenstein-style raycast 2.5D rendering mode

Status: **Desktop/pygame feature COMPLETE (2026-07-18).** Phases 0, 1, 4
(sample), 5 (textured walls + panning sky + cast floor) and a first cut of 6
(billboard sprites) are all done on desktop. **NEXT: Phases 2 & 3 — HTML5 +
Kivy export parity** (detailed plan added 2026-07-18, see that section);
`raycast_1` is desktop-only until then. Historical per-phase notes below.

Original status line: **Phase 0 + Phase 1 DONE (2026-07-16, desktop/pygame only).**
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

## Miss-column render artifact ("I walked outside the map") (2026-07-17)

User report, with screenshot: "From starting position I go backward
(down arrow) and end up outside" — sky-colored ceiling, a wall filling
part of the screen, and a thin horizontal band of alternating dark-red/
black vertical stripes right at the horizon line.

Extensive position/collision testing (direct scripted play through the
real SDL event pipeline via `pygame.event.post` + `GameRunner.run()`,
20,000+ frames of randomized stress-testing across both rooms, a
rigorous rebuild of the expected wall topology straight from `maze_1`'s
original block-wall source data diffed against `raycast_1`'s converted
edges) found **zero** cases of the player's logical `x`/`y` ever leaving
the enclosed maze, and confirmed the converted wall data is a bit-exact
match to the source topology. The player was never actually outside.

The real bug was in rendering, not collision: `_cast_ray` returned
`(dist_cells * cell_size, side)` unconditionally, including on a miss
(the DDA loop exhausts `max_cells` without crossing a registered wall
edge — a real, valid case for any column facing an opening wider than
`render_distance`). `_render_raycast_view`'s per-column loop then drew a
wall strip for *every* column regardless, using `dist == max_cells` (a
thin sliver right at the horizon, since projected height is inversely
proportional to distance) and whatever `side` the last *non-hit* DDA
step happened to leave set — which flips between 0 and 1 semi-randomly
column to column depending on ray angle, producing the reported
alternating-stripe pattern. Fixed by having `_cast_ray` return a third
`hit: bool` and having the render loop `continue` (leave the already-
filled ceiling/floor colors showing) on a miss instead of drawing a
strip. Regression: `test_miss_column_shows_no_wall_sliver_at_horizon` in
`tests/test_raycast_view.py` — verified failing pre-fix (leaks
`wall_color` at the horizon) and passing post-fix, per this session's
established discipline. Suite 1857 → 1858 passed, 0 failed.

**Follow-up, same session**: after that fix landed, the user sent a
second screenshot from the same "Down from spawn" scenario — no more
stripes, but still a wall filling ~40% of the screen with sky/floor
visible for the rest, and still reported as "ended up outside." This
was a second, deeper bug in the same area: `_render_raycast_view` used
`camera.x`/`camera.y` **raw** as the ray origin — a GameInstance's x/y
is its sprite's top-left corner, not its center. Every instance in a
grid maze (walls and the player alike) sits at exact multiples of
`cell_size`, so a player at rest against a wall — extremely common in a
corridor maze — has a raw position landing exactly on a wall-bearing
grid line. DDA rays cast from precisely on that line hit it (or graze
past it) almost immediately, inconsistently by ray angle: reproduced by
holding Down from room0's spawn (blocks correctly at `(29, 416)`,
`facing_angle` unchanged at 0/east since only movement was blocked, not
facing) and directly inspecting `_cast_ray`'s returned distances across
the FOV — roughly half the rays (the half angled toward the coincident
grid line) measured **~3px**, the other half ~130px (the real corridor).
The player's logical position was never wrong (re-confirmed) and the
wall topology was still bit-exact (re-confirmed by rebuilding it fresh
from `maze_1`'s source data and diffing — zero missing/extra edges in
either room) — this was purely which point in space the camera rays
originate from. Fixed by adding half the camera instance's cached
sprite width/height to its x/y before casting, so the ray origin is the
occupied cell's center, matching how a real body would stand in it.
Regression: `test_camera_origin_is_centered_not_the_sprite_corner`,
grounded in the real sample (not a hand-built minimal case — the
coincidence proved surprisingly hard to reproduce synthetically without
going through the actual `GameRunner.run()` startup, since object_data/
sprite-dimension caching on instances isn't resolved until then; an
earlier draft of this test silently produced an empty or wrongly-shaped
wall set and passed for the wrong reason). The test intercepts the real
`_cast_ray` call `_render_raycast_view` makes (rather than
re-implementing the centering formula inline, and rather than
pixel-sampling the rendered output — strip height caps at full screen
height once distance ≤ `cell_size`, so both the ~3px pre-fix and
~29-35px post-fix near-wall readings render pixel-identically and can't
be told apart that way) and asserts the origin passed is the sprite-
centered point, not the raw corner. Verified failing pre-fix (origin
`(29.0, 416.0)`, expected `(45.0, 432.0)`) and passing post-fix. Suite
1858 → 1859 passed, 0 failed.

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

### Phase 5 — textured walls, floor, and ceiling

**Floor/ceiling: DONE 2026-07-18.** The mandated timing spike settled it:
full-resolution per-pixel floor casting measured **~64ms/frame** at the sample's
480×480 in pure Python (unusable), while a **low-res cast + `transform.scale`
upscale** is ~5ms at 4× downsample (3× ≈ 7.6ms, 2× ≈ 17ms) — so the
plan's documented fallback is what shipped. `_cast_floor_plane` renders the
ground plane into a `(w//res) × (region_h//res)` surface (Lodev camera-plane
method: two FOV-edge ray directions interpolated across columns for straight
floor lines; sampled in CELL units so the texture tiles once per grid cell and
`rowDistance_cells = 0.5h/(y-horizon)` makes it meet the wall bases seamlessly),
then upscales. `floor_texture` casts the floor; `ceiling_texture` casts the
ceiling **only when no `sky_texture` claimed it** (mirrored via `flip`);
`floor_cast_res` (default 4) trades sharpness for speed. `raycast_1` ships a
generated 32×32 stone `spr_floor` — the corridor now has brick walls, a cloudy
panning sky, and a paved receding floor (verified by rendered-PNG eyeball).
Regression: `tests/test_raycast_view.py::TestFloorCasting` (6: floor replaces
the flat fill, flat fallback, ceiling_texture casts without sky, sky wins over
ceiling_texture, res configurable+safe, and a full walls+sky+floor
under-budget perf guard). **Phase 5 is complete** — remaining raycast work is
Phases 2/3 (HTML5/Kivy export parity) and 6 (sprite facing, already a first cut).

**Walls: DONE 2026-07-18.** `_cast_ray` now also returns the texture-U (the
fractional hit position along the wall face, computed from the DDA hit — the
standard `posY + perpDist*rayDirY` fractional part, flipped per face so the
texture isn't mirrored) and the hit wall's sprite (stored in parallel
`_raycast_{v,h}_wall_sprites` dicts built alongside the edge sets). The render
loop samples a 1px vertical subsurface strip and `pygame.transform.scale`s it
to the projected strip height, with the same half-brightness y-face shading as
the flat path (via `BLEND_RGB_MULT`). Resolution order per wall column: an
explicit `wall_texture` sprite name on the camera config (the usual choice —
the derived thin edge-wall collision sprites aren't real wall art), else the
per-instance wall sprite, else flat colour; `wall_textured: false` forces flat.
`raycast_1` ships a generated 64×64 tileable brick `spr_wall_texture` and looks
like a proper Wolfenstein corridor now (verified by rendered-PNG eyeball).
Regression: `tests/test_raycast_view.py::TestTexturedWalls` (6 tests: textured
render, flat override, y-face shading, tex_u + sprite on hit, miss returns no
texture, spriteless fallback). **Floor/ceiling casting is still ahead** (the
per-pixel-row part flagged for a timing check) — next.

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

### Phase 5b — outside sky/horizon (DOOM-style)

**DONE 2026-07-18.** The flat ceiling fill is replaced (when a `sky_texture`
sprite name is set on the camera config) by a panorama scaled to the ceiling
region and panned horizontally by `facing_angle`: `pano_w = w * 360 / fov`
(so the FOV-wide screen shows exactly `fov/360` of the panorama), `pan =
(facing_angle % 360)/360 * pano_w`, blitted at `-pan` plus a wrap copy — a full
360° turn pans the sky exactly once and it never recedes with distance
(cheapest texture in the pipeline: one scale + up to two blits, no per-column
math). Drawn over the flat ceiling fill and under the walls, so wall strips
occlude it for free; the sky shows in the ceiling region (always visible above
walls in `raycast_1`'s enclosed maze — no open-edge map needed after all).
`raycast_1` ships a generated 256×64 tileable `spr_sky` (blue gradient +
sun + wrap-safe clouds) and the `sky_texture` param. Regression:
`tests/test_raycast_view.py::TestSky` (4: sky replaces the flat ceiling, pans
with facing_angle, floor stays flat, absent sky_texture keeps the flat fill).
**Floor casting is the remaining Phase 5 piece** (the per-pixel timing-check
one).

Original notes:

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

### Phases 2 & 3 — HTML5 + Kivy export parity (NEXT — detailed plan, 2026-07-18)

`raycast_1` is **desktop-only** today. Bringing it to the two export targets
means re-implementing the desktop raycast renderer in each (there is no shared
code between the runtime and the exporters — the exported games are
standalone), so this is a **three-copies-of-the-renderer** situation, exactly
like the `views` feature (desktop `game_runner.update_views`, `engine.js`
`updateViews`, Kivy generated `update_views`). Same mitigations apply:
port faithfully, and add a **3-target parity test** (model it on
`tests/test_views_export_parity.py`) so the copies can't drift.

**Ground truth to port** (all in `runtime/game_runner.py` / `action_executor.py`):
`_build_raycast_walls` (edge derivation + parallel sprite dicts), `_cast_ray`
(DDA returning dist/side/hit/tex_u/sprite), `_render_raycast_view` (flat fills →
sky pan → floor cast → per-column wall strips → billboard sprites with
per-column occlusion), `_cast_floor_plane` (low-res floor cast), and the
`facing_angle` instance state + `set_facing_angle` / `enable_raycast_view`
actions.

#### Shared prerequisite — action registration + facing-angle parity (do first)

Neither `set_facing_angle` nor `enable_raycast_view` is registered in
`events/action_types.py` yet (they're runtime-only, like `enable_views` was
before I registered it), and neither exporter knows `facing_angle`. One small
unit, mirroring the `enable_views`/`set_view` registration
(`a7a963a`-style):
1. Register both actions in `events/action_types.py` (category e.g. "3D View"),
   with the full parameter set (`fov`, `render_distance`, `cell_size`,
   `columns`, `wall_color`/`floor_color`/`ceiling_color`,
   `wall_texture`/`sky_texture`/`floor_texture`/`ceiling_texture`,
   `wall_textured`, `floor_cast_res`, `camera_object`; and `angle` + `relative`
   for `set_facing_angle`). This unblocks both exporters' action dispatch and
   lets the action round-trip through save/load.
2. Regression test like `tests/test_views_action_registration.py`.

#### Phase 2 — HTML5 (`engine.js`)

Anchors (as of this writing): `GameRoom.render(ctx)` at ~line 2866 (the raycast
branch goes here as an early return, exactly like the desktop `_render_room`
early-return); `executeAction` switch at ~line 1316 (new `case
'enable_raycast_view'` / `'set_facing_angle'`, next to `case 'enable_views'` at
~2021); `parseNumParam` (~305) / `gmExpressionValue` (~340) for expressions;
sprites are ready-to-draw `Image` objects via `game.sprites[name]`.

- **facing_angle**: add it as a `GameInstance` property (default 0), a
  `set_facing_angle` action case, and expose `facing_angle` in the
  `gmExpressionValue` scope so `set_direction_speed(direction="facing_angle")`
  — the exact expression `raycast_1`'s controls use — resolves (it already
  exposes `direction`, `hspeed`, etc.; add this name).
- **Renderer** — a `renderRaycastView(ctx)` method on `GameRoom`, called from
  `render()` when `this.raycastCamera?.enabled`:
  - Wall map: port `_build_raycast_walls` to build `vWalls`/`hWalls` (Set of
    `"lx,cell"` keys) + parallel sprite-name maps, once, cached on the room
    (invalidate on cell_size change), from the solid instances.
  - DDA: port `_cast_ray` verbatim (integer/float math is identical in JS).
  - Walls: `ctx.drawImage(img, texX, 0, 1, texH, x0, y0, stripW, stripH)` — the
    9-arg form samples a 1px source column and scales it to the strip, the
    Canvas2D equivalent of pygame's subsurface+scale. Half-brightness y-face
    via a `ctx.globalAlpha`/overlay or a pre-dimmed offscreen (simplest: draw
    then `fillRect` a 50%-black over side==1 strips).
  - Sky: `pano_w = w*360/fov`, `ctx.drawImage` the sky scaled to
    `(pano_w, h/2)` at `-pan` + wrap copy (direct port).
  - Floor: the per-pixel cast is even less viable in JS; port the **low-res
    approach** — render the floor into a small offscreen canvas via
    `ImageData`/`putImageData` at `(w/res, (h/2)/res)`, then `drawImage` it
    scaled up (Canvas smoothing off for the chunky look). Time it in a Phase-0
    style spike first, same as desktop.
  - Billboards: port the non-solid-sprite pass + `colWallDist` per-column
    occlusion (`drawImage` per unoccluded column slice).
- **Action**: `case 'enable_raycast_view'` builds `this.currentRoom.raycastCamera`
  from params (mirror the desktop handler's defaults).
- **Tests**: source-level assertions in a new `tests/test_html5_raycast.py`
  (the renderer/actions exist, the wall/sky/floor/DDA formulas are present),
  plus a real-Chromium Playwright check during development (Playwright isn't a
  CI dep — same pattern as `test_html5_views`).

#### Phase 3 — Kivy (generated scene)

Anchors: the FBO/views machinery in `export/Kivy/kivy_exporter.py`
(`_render_views` ~1543, `_update_impl` ~1741, `InstructionGroup` on the scene
canvas ~1494) is the model. Textures load via `load_image(...).texture`
(`CoreImage`); per-column draws are `Rectangle(texture=…, tex_coords=…)` in an
`InstructionGroup` — the same primitives the view blits already use.

- **facing_angle / actions**: `set_facing_angle` + `enable_raycast_view` codegen
  in `export/Kivy/code_generator.py` (like the `enable_views`/`set_view` codegen
  added in `c6c034b`), writing a `raycast_camera` dict + a `_facing_angle`
  attribute onto the generated object/scene.
- **Renderer**: a generated `_render_raycast()` scene method drawing into a
  dedicated `InstructionGroup` each frame (branch `_update_impl` so a
  raycast-enabled room renders the first-person view instead of the top-down
  child-widget instances). Port `_build_raycast_walls` + `_cast_ray` as scene
  methods. Walls: one `Rectangle(texture=wall_tex.texture, tex_coords=(u,0, u,0,
  u,1, u,1), pos=(x0,y0), size=(stripW, stripH))` per column (a 1px-wide U
  slice — the FBO views code already does exactly this kind of tex_coords
  slice). Sky: one panned `Rectangle`. Floor: low-res — render into a small
  `Fbo` (or a `Texture.create` + `blit_buffer`) and draw it scaled; **spike the
  timing** (Python-in-Kivy is the same speed class as the desktop spike, so 4×
  downsample should land ~5ms). **Watch the y-axis**: Kivy is y-up (the whole
  reason the views port needed a flip) — the raycast screen math is y-down, so
  either flip the final draw or build the column rects in Kivy coords.
- **Tests**: stub-Kivy headless render (extend the existing
  `tests/test_kivy_views.py` stub set — `Fbo`/`Rectangle`/`InstructionGroup`
  are already stubbed) asserting the per-column rect count/geometry; source
  assertions on the generated scene.

#### The 3-target parity test (last unit of this phase)

`tests/test_raycast_export_parity.py`, modeled on `test_views_export_parity.py`:
feed one synthetic room (a couple of solid walls + a camera at a known
position/`facing_angle`) through all three `_cast_ray` implementations and
assert they return the **same hit distance + side** for a fixed set of ray
angles. `_cast_ray` is coordinate-system-independent (pure grid DDA), so this
is a clean cross-target invariant — the raycast analogue of the views parity
test's `view_x` check. (Desktop runs the real method; Kivy via the stub scene;
HTML5 via source-formula assertion since node isn't a CI dep, or a tiny node
harness if one is available.)

#### Suggested commit-sized unit sequence (session-limit discipline)

1. Register `set_facing_angle` + `enable_raycast_view` in `action_types.py`
   (+ test). Small. — **DONE 2026-07-18** (category "3D View", full param sets
   with sprite-picker texture params + colour params; `tests/
   test_raycast_action_registration.py`, 6 tests). No feature-matrix/handler
   coverage regressions.
2. HTML5 facing_angle + walls (+ source test). Medium. — **DONE 2026-07-18.**
   `engine.js`: `facing_angle` on GameInstance + `set_facing_angle` case +
   `parseNumParam` facing_angle expansion (so `set_direction_speed(direction=
   "facing_angle")` resolves); `enable_raycast_view` case building
   `room.raycastCamera`; `buildRaycastWalls`/`castRay`/`renderRaycastView`
   (walls: `ctx.drawImage(tex, texX,0,1,th, x0,y0,stripW,stripH)` slice + flat
   fallback + y-face shade) ported faithfully from the desktop; `render()`
   early-return. `tests/test_html5_raycast.py` (7, source-level + real
   raycast_1 export round-trip). No JS engine/Playwright in CI, so behavioural
   proof is a browser run (as with views); added lines brace-balanced.
3. HTML5 sky + floor (spike first) + billboards (+ source/Playwright). Medium.
   — **sky + billboards DONE 2026-07-18** (`engine.js` renderRaycastView: sky
   panorama pan+wrap over the ceiling; per-column `colWallDist`; billboard pass
   — non-solid sprited instances, farthest-first, per-column occlusion via
   `ctx.drawImage` source-column slices; `tests/test_html5_raycast.py` +2, added
   lines brace-balanced).
   — **3b HTML5 floor casting DONE 2026-07-19.** The browser timing spike
   (`spikes/floor_cast_html5.html`) came back green: Brave + Edge both measured
   **res=2 at ~0.3–0.4 ms median** (target <8 ms), so the cast is affordable
   with huge headroom. `engine.js` gained `_textureData` (offscreen-canvas
   `getImageData` per sprite, cached; returns null on a cross-origin taint so
   the flat fill stands) and `castFloorPlane` — a faithful port of
   `_cast_floor_plane` (camera-plane rays, `rowd = 0.5h/(y−horizon)`, per-cell
   tiling, low-res `ImageData` fill + `drawImage` upscale; `ceiling` flips
   vertically). Called between the sky and wall passes; honors
   `cfg.floor_cast_res` (default 4, desktop parity) and casts the ceiling only
   when no sky claimed it. `tests/test_html5_raycast.py` +4 (source structure +
   floor-precedes-walls order + real raycast_1 export ships `spr_floor`); added
   lines brace-balanced (whole-file bracket mismatch is pre-existing at HEAD).
   Suite 1912→1916.
4. Kivy facing_angle + walls (+ stub test). Medium.
   — **4a movement/action parity DONE 2026-07-19** (`kivy_exporter.py`:
   `facing_angle` on the base object, `raycast_camera=None` on the scene;
   `code_generator.py`: `set_direction_speed` [raycast_1's FPS controls, the
   Kivy generator dropped it before], `set_facing_angle` [abs/relative],
   `enable_raycast_view` [builds the scene `raycast_camera` cfg; no named camera
   ⇒ `camera_instance=self`]. `tests/test_kivy_raycast.py`, 8 — codegen unit
   asserts + real raycast_1 export compile check. Suite 1895→1903.)
   — **4b the wall RENDERER DONE 2026-07-19** (`kivy_exporter.py` scene:
   `_build_raycast_walls` / `_cast_ray` / `_render_raycast` ported faithfully
   from the desktop `game_runner` copies; textured + flat-colour wall strips
   drawn into an opaque overlay `InstructionGroup` on `canvas.after`, hooked
   into `_update_impl` step 7d + an initial frame in `__init__`. **y-flip
   handled by computing the whole DDA in GM y-down space** — each Kivy
   instance's y-up `x/y` is converted back to a GM top-left via
   `room_height - y - image_height`, so wall-key derivation / camera centering /
   tex_u / facing_angle all match the desktop verbatim; only the final draw
   flips, and wall strips are vertically symmetric so just the ceiling/floor
   fills swap halves. Textured strips slice a 1-px column via
   `texture.get_region(tex_x, 0, 1, h)` — the same frame-slice trick the sprite
   animator uses, so orientation is right without hand-set `tex_coords`. Wall
   textures resolve sprite-name→texture through `SPRITE_PATHS`/`load_image`
   (cached). `tests/test_kivy_raycast.py` +4 headless tests vs stub-kivy:
   `_cast_ray` hits a wall ahead at the exact 16-px distance; `_render_raycast`
   draws the ceiling/floor fills in the right (y-up) halves + wall strips facing
   a wall, none facing away, and clears the overlay when disabled. Suite
   1903→1907.)
5. Kivy sky + floor (spike) + billboards (+ stub test). Medium.
   — **5a sky + billboards DONE 2026-07-19** (`kivy_exporter.py`
   `_render_raycast`: a panning sky panorama over the ceiling — `pano_w =
   w*360/fov`, panned by `facing_angle`, wrap rect, drawn UNDER the walls in
   the top (y-up) half so wall strips occlude it; a `col_wall_dist` array filled
   during the wall pass; a billboard pass — every visible non-solid sprited
   instance drawn camera-facing, farthest-first, with real per-ray-column
   occlusion via textured `get_region` slices, plus `_billboard_texture`
   [current animation frame]. `tests/test_kivy_raycast.py` +2 headless: sky
   panorama sized `w*360/fov` in the ceiling half; a goal billboard drawn when
   visible and fully suppressed when a solid wall sits between it and the
   camera. Suite 1907→1909.)
   — **5b Kivy floor casting DONE 2026-07-19.** The GL timing spike
   (`spikes/floor_cast_kivy.py`) on the Windows box (AMD 840M) came back:
   naive Python cast + real `blit_buffer` upload measured **res=4 at ~5.1 ms
   median** (res=1 86 ms, res=2 20 ms, res=8 1.2 ms) — so res=4 naive fits the
   <8 ms target, matching the desktop default; numpy wasn't needed (and isn't
   installed on that box). `kivy_exporter.py` gained `_raycast_texture_pixels`
   (cached `texture.pixels`), `_floor_buffer` (the pure naive cast → RGBA bytes,
   **flipping the source row since Kivy `.pixels` are bottom-up**), and
   `_render_floor_plane` (builds a low-res `Texture`, `blit_buffer`, draws a
   Rectangle GPU-upscaled to the region). **y-up handled with tex_coords**: the
   floor is the bottom half and the cast's horizon row (row 0) must sit at the
   TOP of that region, so the floor uses `tex_coords=(0,1,1,1,1,0,0,0)` and the
   ceiling mirrors it. `Texture` is imported LOCALLY inside `_render_floor_plane`
   (a top-level import broke every other test's stub-kivy env, which doesn't
   stub `kivy.graphics.texture`). `tests/test_kivy_raycast.py` +2: `_floor_buffer`
   returns a 120×60 opaque sampled buffer for a 480×480 display at res=4;
   `_render_raycast` adds the v-flipped floor Rectangle at the bottom half
   (stub `Texture`). Suite 1916→1918.
6. 3-target `_cast_ray` parity test. Small.
   — **DONE 2026-07-19** (`tests/test_raycast_export_parity.py`, 3 tests).
   Desktop `GameRoom._cast_ray` and the Kivy generated scene `_cast_ray` are fed
   IDENTICAL derived wall edges and asserted to return the same
   (distance, side, hit, tex_u) across a 5-origin × 52-angle matrix (260 rays) —
   **exact** numeric equality (< 1e-9), since the ports were transcribed
   line-for-line. HTML5's `castRay` can't be executed here (no JS engine), so it
   gets structural parity: its body must carry the same load-bearing DDA
   statements (`Math.abs(1/dx)`, `sideX < sideY`, `_vWalls.has`/`_hWalls.has`,
   `Math.floor(wallCoord)`, `hit: true`/`hit: false`). A third test pins the
   shared facing-angle convention (`-facing_angle` → screen radians) across all
   three sources. Suite 1909→1912.

Then fold the result into `raycast_1`'s README (drop the "desktop-only" caveat)
and, optionally, add `raycast_1` to `tools/smoke_run_samples.py`.
— **BOTH DONE 2026-07-19.** README parity update `4021c95`; `raycast_1` added to
the smoke runner (`[OK]` at 120 frames — the injected RIGHT/LEFT/UP keys drive
the turn/move controls, so the first-person renderer incl. the floor cast runs
headlessly; 14/14 samples clean). **The whole raycast 2.5D plan is now closed
across all three targets.**

#### Risks / open questions

- **Floor casting perf on each target** is the main unknown — JS `ImageData`
  per-pixel and Kivy `blit_buffer` are both untested here; the low-res spike is
  mandatory before committing either (a documented fallback is a *flat* floor
  on export if a target can't hit budget, with textured floor desktop-only).
- **Drift** across three renderer copies — the parity test covers the DDA
  core, but sky/floor/billboard rendering isn't cross-checked by it; keep the
  ports close to the desktop source and reference it in comments.
- **Kivy y-flip** is the fiddly bit (same class of bug as the views port).

### Phase 6 — billboard sprites (stretch, likely last)
**DONE (scoped down), 2026-07-17** — landed early, out of phase order,
in direct response to a user report that `obj_goal` was invisible in
`raycast_1`'s first-person view.

- `_render_raycast_view` now renders every visible, **non-solid**
  sprited instance (walls are solid and already drawn as strips —
  excluded explicitly, both to avoid double-drawing and because a solid
  instance with a sprite would otherwise render as both a wall strip and
  a billboard) as a camera-facing sprite: angle-to-instance vs. facing
  angle picks the screen column, fisheye-corrected distance picks the
  scale (same formula as wall strips, generalized to the sprite's own
  width/height instead of assuming a full cell), vertically centered on
  the horizon like a wall strip.
- **Real per-column occlusion**, not the single-ray approximation
  originally scoped: the wall pass already computes a corrected distance
  per screen column (`col_wall_dist`); the billboard pass reuses that
  array directly, clipping the sprite's own scaled surface one pixel-
  column at a time against it. A goal fully behind a wall is fully
  hidden; one peeking around a corner shows only the unoccluded slice.
- Multiple billboards sort farthest-first (painter's algorithm) so
  nearer ones draw over farther ones where they overlap.
- The camera's own instance is excluded by identity (it's non-solid too
  — `obj_person` would otherwise billboard itself).
- **Not done** (deliberately out of scope for this cut, matching the
  plan's original "genuinely optional" framing for anything beyond the
  core): sprite rotation to face a fixed direction regardless of camera
  angle (these always face the camera, which is the standard/expected
  Wolfenstein convention anyway), partial alpha blending, and sprites
  that are their own camera target (a billboard can't currently *be*
  `camera_object`, which was never a sensible configuration).
- Regression: `TestBillboardSprites` in `tests/test_raycast_view.py` (5
  tests — renders when visible, occluded behind a wall, solid instances
  never billboarded, the camera never billboards itself, nearer sprite
  wins overlap) — verified the two "must render" cases fail without the
  feature and pass with it. Suite 1859 → 1864 passed, 0 failed.

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

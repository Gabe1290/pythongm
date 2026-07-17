# Plan: Doom/Wolfenstein-style raycast 2.5D rendering mode

Status: **scoped, not started.** Written 2026-07-16 in response to a
direct ask: "how hard would a 3D extension be, and if hard, scope out a
fake 2.5D instead." This doc is that scope-out. Not linked from
`docs/DEFERRED_ITEMS_PLAN.md` — this is a new feature pitch, not an item
from the existing deferred-features registry, and shouldn't be started
without an explicit go-ahead (see "Before committing to this" at the
bottom).

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

### Phase 0 — feasibility spike (throwaway script, not a feature commit)

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

### Phase 4 — sample game

- A new bundled sample (`raycast_1`, matching the `views_1`/`views_2`
  naming precedent) — most efficient path is reusing `maze_1`'s existing
  wall layout (it's already a grid of solid objects) rendered in
  first-person instead of top-down. This is the actual "aha" deliverable
  for students and should ship as soon as Phase 1-3 are solid, even
  before textures/sprites — a flat-colored maze you can walk through in
  first-person is already the pedagogical payload.

### Phase 5 — textured walls (stretch, after the flat-color MVP ships)

- Sample a 1px-wide vertical strip from the wall's sprite at the ray's
  hit position instead of a flat color. Desktop:
  `pygame.transform.scale` a 1px subsurface. HTML5: `ctx.drawImage` with
  a 1px source rect. Kivy: a textured `Rectangle` with `tex_coords`. Each
  is a small, target-specific addition on top of the Phase 1-3
  machinery, not a new rendering approach.

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

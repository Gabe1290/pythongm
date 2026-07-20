# Plan: in-view HUD compositing + the `raycast_3` sample

Status: **Sessions A–B DONE (2026-07-20); C–D (the `raycast_3` sample) and E
(minimap) open.** The engine feature is complete and shipped on all three
targets — see the unit checklist below. Supersedes the 2026-07-19
version, which scoped this as engine-only work ending in a `raycast_2` tweak.
The HUD is now the **headline feature of a third raycast sample**, so the plan
covers engine work (3 targets) *and* `raycast_3`, sequenced in session-size
bites.

Surfaced by `raycast_2` (see `RAYCAST_2_SAMPLE_PLAN.md` Unit 2 and the open item
in `RAYCAST_2_5D_PLAN.md`).

## Problem

When raycast mode is active, HUD draw actions (`draw_score`, `draw_lives`,
`draw_text`, `draw_health_bar`, and the draw primitives) **don't render**. Each
target draws the first-person view and then stops before the per-instance draw
pass that composites the HUD. Verified against current code 2026-07-20:

| Target | Site | What happens |
|---|---|---|
| Desktop | `runtime/game_runner.py:1670-1672` | `if self.raycast_camera.get('enabled'): self._render_raycast_view(screen); return` — the `_sorted_instances` loop (`:1689`) that calls `instance.render()` never runs, so the draw event at `:851-860` never fires |
| HTML5 | `engine.js:3293` | `this.renderRaycastView(ctx); return;` — skips the sprite + draw-queue pass |
| Kivy | `kivy_exporter.py:1935` | `_raycast_group` is an **opaque** `InstructionGroup` on the **scene's** `canvas.after`, which paints over every child `GameObject` widget's canvas — including each object's own `_dq_group` (`:3481`) |

Consequence: scored/lives-based raycast games (like `raycast_2`) show score and
lives only in the **desktop window caption** — invisible in the HTML5 (browser
tab) and Kivy (fullscreen) exports. A real limitation, not cosmetic.

## Engine-risk assessment — LOW, and smaller than the old plan assumed

Checked before writing this revision: **every HUD draw action already has full
codegen and a renderer on all three targets.** Nothing new has to be authored
per-action.

| Action | Desktop | HTML5 | Kivy |
|---|---|---|---|
| `draw_score` | `_process_draw_queue` `'text'` | `engine.js:2218` | `code_generator.py:1012` → `_dq_render_cmd` |
| `draw_lives` | `_draw_lives` (`:865`) | `engine.js:2240` / `:480` | `code_generator.py:1030` → `:3612` |
| `draw_health_bar` | `_draw_health_bar` | `engine.js:2328` / `:528` | `code_generator.py:1118` → `:3674` |

So this is a **compositing-order change only**. That is the whole engine story,
and it's why the sample below can lean on the HUD heavily without new actions.

## Design

**Composite the HUD as a final pass over the finished first-person frame, in
SCREEN space** — no camera offset, top-left origin. A HUD `draw_score` at
`(8, 8)` lands 8 px from the window's top-left, exactly as in a normal game with
no active view.

Which draw actions: the same per-instance `draw` events that already run in
normal mode — an authored HUD controller's `draw` event (`set_draw_font` +
`set_draw_color` + `draw_score`/`draw_lives`/`draw_text`/`draw_health_bar`, the
`maze_3` `controller_main` pattern, verified still shaped that way). No new
action types; this changes only *when* the existing draw pass runs.

**Scope-out (document, don't fix):** draws that are intrinsically top-down
(`draw_self`, `draw_sprite` at world coords, `draw_background`) have no
meaningful place over a first-person view. They may draw at raw screen coords or
be skipped. A HUD is text/score/lives/bars — screen-space by nature. Do **not**
try to project world-space draws into the 3D view.

### Per-target approach

- **Desktop.** Factor `game_runner.py:851-860` (clear queue → `execute_event`
  `"draw"` → `_process_draw_queue`) out of `GameInstance.render` into a small
  `run_draw_event(screen)`. Call it from both `render()` and a new
  `_render_draw_events(screen)` that `_render_room` invokes after
  `_render_raycast_view` instead of the bare `return`. Screen-space, offset
  `(0,0)`.
- **HTML5.** In `render(ctx)`, replace the early `return` at `:3293` with the
  same draw-queue pass the normal path already uses, run after
  `renderRaycastView(ctx)`. Screen-space.
- **Kivy — the hard one.** Two traps, both confirmed in code:
  1. **Z-order across widgets.** `_dq_group` lives on each *GameObject widget's*
     `canvas.after`; `_raycast_group` lives on the *scene's* `canvas.after`,
     which paints after all children. Adding another group to a child widget
     will **not** get above the overlay. The HUD needs a dedicated
     `_raycast_hud_group` on the **scene's** `canvas.after`, added *after*
     `_raycast_group`.
  2. **Wrong y-flip.** `_render_draw_queue` (`:3470`) converts y-down room
     coords using `room_height`. A screen-space HUD must flip against the
     **window height** instead. Reusing `_render_draw_queue` unchanged will put
     the HUD at the wrong height on any room whose height ≠ window height —
     which is every scrolling raycast room. Needs its own screen-space path.
  - Plus the standing landmine: the scene class is a `.format()` template, so
    every literal `{`/`}` in added code must be doubled.

### Testing

- **Desktop:** render a frame of a room whose HUD controller does
  `draw_score`/`draw_text` over an enabled raycast camera; assert HUD-region
  pixels change (or intercept the draw-queue commands). Must go through the real
  `run()` startup — per the 2026-07-17 bug hunt, instances don't get
  `_cached_object_data` / sprite-derived sizes until `set_sprites_for_instances`
  runs, so a hand-built room passes for the wrong reason.
- **HTML5:** source-level structural assertion (draw pass invoked after the
  raycast render, not skipped) — no JS engine in CI — plus a dev browser run.
- **Kivy:** the existing stub-kivy harness (`tests/test_kivy_raycast.py`
  pattern: `cls.__new__` + controlled geometry). **Assert the y-flip uses window
  height, not room height** — use a room whose height differs from the window so
  the two can't be confused.
- **Parity:** extend `tests/test_raycast_export_parity.py` — HUD pass fires on
  all three.

## The `raycast_3` sample

**Concept — "the status bar is the game."** Where `raycast_1` teaches the
first-person view and `raycast_2` adds things happening *in* the view (gems,
a patrolling monster, a gated exit), `raycast_3` is the first raycast sample
whose **state is legible while you play**: a DOOM-style status bar composited
over the 3D view.

Mechanics, chosen so each one makes a HUD element necessary:

1. **Health instead of instant death** — monsters damage you (`set_health`
   relative) rather than costing a life outright; `draw_health_bar` is how you
   know you're in trouble. This is the single biggest gameplay difference from
   `raycast_2`.
2. **Health pickups** — medkit billboards restore health, giving the bar a
   reason to move both ways.
3. **Score + lives** — `draw_score` / `draw_lives`, carried over from
   `raycast_2`, now visible on every target rather than caption-only.
4. **A key/objective counter** — `draw_text` bound to a counter variable, so the
   gated exit's requirement is readable instead of guessed.

Delta taught vs `raycast_2`: health as a resource, HUD authoring, and reading
game state without leaving the first-person view.

**Engine risk — this claim was WRONG, corrected 2026-07-20 during Unit 6.**
The original text read "none beyond the HUD compositing itself: health actions
and all four HUD draw actions are already 3-target-complete". The *draw* actions
were; the health **logic** was not. The check that produced the table above
looked only at draw actions, so it missed that health was display-only on the
exports:

| | desktop | HTML5 | Kivy |
|---|---|---|---|
| `set_health`, `draw_health_bar` | y | y | y |
| `test_health` | y | y | **no** |
| `test_lives` | y | y | **no** |
| `no_more_health` | y | **no** | **no** |
| `no_more_lives` | y | y | y |

So the bar would have moved on all three targets while every conditional
branching on it silently vanished — a "you died" handler that never fires. That
is precisely the failure this sample exists to prevent, and the class of gap
CLAUDE.md's *"audits miss absent features"* note warns about: a static read sees
the actions present and concludes it works. Closed in Unit 5b before Unit 6
built on it; `tests/test_health_lives_export_parity.py` pins all six.

**Lesson for the remaining units:** when a sample introduces a mechanic, check
the *conditionals and events* it needs on every target, not just the actions
that draw it.

**Assets:** reuse `raycast_2`'s wall/sky/floor textures, `obj_person`,
`obj_wall_h`/`_v`, monster and gem sprites. New: a medkit billboard sprite, a
key sprite, and a font for the status bar (or reuse `maze_3`'s `score_font`).

## Session-size bites

Cost basis: the measured French-guide run (15 guides ≈ 40% of a session) and the
`raycast_2` build (6 units ≈ 1.5 sessions). Percentages are of one session;
each **unit is one commit**, pushed before the next starts, so a mid-session
limit loses nothing and the next session resumes from clean `main`.

### Session A — engine, the two easy targets — **DONE**

- [x] **Unit 0 — this plan.** `a869f7a`, minimap scheduled `f90d586`.
- [x] **Unit 1 — desktop HUD pass.** `341f5c4`. `run_draw_event` split out of
  `GameInstance.render`; `_render_draw_events` after `_render_raycast_view`.
- [x] **Unit 2 — HTML5 HUD pass.** `d11550b`. `runDrawEvent(ctx)` split out of
  `onDraw`, run after `renderRaycastView`.

### Session B — engine, Kivy + parity — **DONE**

- [x] **Unit 3 — Kivy HUD pass.** `fd2402f`. Both traps were real: the HUD group
  had to be scene-level (a child widget's group can never rise above the
  scene's opaque overlay), and the y-flip had to use `display_height`, not
  `room_height`.
- [x] **Unit 4 — parity + retire the caveat.** Parity tests pin that none of the
  three regresses to a bare early-return; `raycast_2` ships `obj_hud`; the
  caption-only caveat is gone from its EN + FR guides.

**Unscheduled work that came out of Session A** (`380abd2`): two PRE-EXISTING
export bugs, both divergences from the desktop runtime rather than raycast
issues — **draw depth order** (engine.js sorted ascending, inverting sprite
z-order; the Kivy exporter ignored `depth` entirely) and **draw-event
visibility** (both targets ran an invisible instance's draw event, which
GameMaker does not). Four samples rendered wrong on those targets: `maze_3`,
`maze_4`, `plateforme_3`, `treasure`. Worth a browser/Android playtest of
`plateforme_3` (five distinct depths) before the next release — the tests prove
the ordering logic but can't prove it *looks* right.

**Consequence for authoring, now load-bearing:** a HUD controller must be
`visible: true`. `raycast_2`'s `obj_cam0`/`obj_cam1` are invisible, which is
exactly why `obj_hud` is a separate object rather than a draw event bolted onto
the camera controller.

*Engine feature is complete and shipped at the end of Session B.* `raycast_3`
can then slip without leaving anything half-done — a deliberate cut line.

### Session C — `raycast_3`, the game (~50%)

- **Unit 5 — maze + objects.** Generate the maze via `raycast_2`'s
  recursive-backtracker + edge-wall conversion; place walls, player, camera
  controller, gems, monsters. Smoke-run desktop. (~30%)
- **Unit 6 — health loop + HUD controller.** Monster damage, medkit pickups,
  the status-bar controller (`draw_health_bar` + `draw_score` + `draw_lives` +
  key counter). **Landmine from `raycast_2`:** score/lives/health init belongs in
  **`game_start`**, not `create` — `create` re-runs on `restart_room`.
  `enable_raycast_view` must stay in `create`. (~20%)

### Session D — second room + ship it (~50%)

- **Unit 7 — room 2 + gated exit.** Second themed room via a per-room camera
  controller with `camera_object='obj_person'`; key-gated exit
  (`test_instance_count`, param key is **`number`**, not `count`). (~20%)
- **Unit 8 — ship.** Welcome-tab entry + `pygm2_fr.ts` translation
  ("Lancer de rayons — Niveau 3"), smoke runner, 3-target playtest, README.md +
  README.fr.md. (~30%)

### Session E — minimap (planned 2026-07-20, needs its own plan doc first)

A minimap is **not** a HUD-compositing problem: it needs world-space→view
projection, which Sessions A–D explicitly scope out. It rides on the HUD pass
landing first (it's drawn in the same screen-space final pass), so it is
correctly sequenced after D — but it needs its own design pass before any code,
covering at minimum: what it projects (wall edges from `_build_raycast_walls`?
instance positions?), whether it rotates with `facing_angle` or stays
north-up, fog-of-war vs. fully revealed, and how it renders on all three
targets given none of them has a world→minimap primitive today.

**First action of Session E is writing `docs/RAYCAST_MINIMAP_PLAN.md`**, not
writing code. Estimated 1–2 sessions once scoped; do not start it before
Session B ships the HUD pass it depends on.

**Total ≈ 2 sessions of engine work, 2 of sample work, plus the minimap.**
Sessions A–B, C–D and E are independently shippable.

## Questions settled before Session C (2026-07-20)

- **Status-bar layout — CORNER OVERLAYS** (decided; DOOM bottom bar rejected).
  The raycast renderer always fills the window (`w, h = screen.get_size()`) and
  hardcodes the horizon at `h / 2`; `enable_raycast_view` has no viewport
  parameter. So a bottom bar could only be done two ways, both bad:
  *(a)* paint an opaque bar over the finished frame — zero engine change, but
  the horizon stays at true screen centre while the visible centre moves up,
  giving a permanent slight-upward-tilt feel (DOOM avoided this by shrinking
  the 3D viewport, not covering it), and it floor-casts pixels it then hides;
  *(b)* letterbox the view properly — needs a viewport height threaded through
  horizon, wall-strip heights, floor casting, billboard scaling and sky panning
  in all three hand-written renderers, i.e. an engine unit the size of Sessions
  A–B for a cosmetic change.
  Corner overlays cost nothing (it is exactly what `raycast_2`'s `obj_hud`
  already does) and keep the full first-person view, which in a raycast game
  *is* the game. **Layout rule:** score and health go in OPPOSITE corners, not
  stacked, so a wide health bar can't collide with a growing score string.
  A DOOM-style bar remains a legitimate standalone feature later — a
  `viewport_height` parameter on `enable_raycast_view` — and would pair
  naturally with the Session E minimap, which also wants screen real estate.
- **Health damage model — per-touch, with a short invulnerability alarm.**
  Simpler than damage-over-time and matches `raycast_2`'s collision idiom;
  the alarm stops a single overlap draining the whole bar in a few frames.

## Out of scope

- No new draw actions or HUD authoring UI — reuse existing actions and the
  `maze_3` controller pattern.
- No world-space→view projection of top-down draws (see Scope-out above).
- No changes to the DDA / billboard / floor-cast passes — compositing order
  only.
- No minimap **in Sessions A–D**. It is not a HUD-compositing problem (it needs
  world-space projection, explicitly scoped out above). Now scheduled as
  **Session E**, gated on its own plan doc — see the Session E entry.

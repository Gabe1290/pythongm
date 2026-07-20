# Plan: in-view HUD compositing + the `raycast_3` sample

Status: **PLAN (revised 2026-07-20). Not started.** Supersedes the 2026-07-19
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

**Engine risk: none beyond the HUD compositing itself.** Health actions and all
four HUD draw actions are already 3-target-complete (table above); everything
else reuses `raycast_2`'s proven mechanics.

**Assets:** reuse `raycast_2`'s wall/sky/floor textures, `obj_person`,
`obj_wall_h`/`_v`, monster and gem sprites. New: a medkit billboard sprite, a
key sprite, and a font for the status bar (or reuse `maze_3`'s `score_font`).

## Session-size bites

Cost basis: the measured French-guide run (15 guides ≈ 40% of a session) and the
`raycast_2` build (6 units ≈ 1.5 sessions). Percentages are of one session;
each **unit is one commit**, pushed before the next starts, so a mid-session
limit loses nothing and the next session resumes from clean `main`.

### Session A — engine, the two easy targets (~50%)

- **Unit 0 — this plan.** Commit first. (~5%)
- **Unit 1 — desktop HUD pass.** Extract `run_draw_event`, add
  `_render_draw_events`, call after `_render_raycast_view`; regression test
  through real `run()`. (~20%)
- **Unit 2 — HTML5 HUD pass.** Draw-queue pass after `renderRaycastView`;
  structural test. Verify brace/paren balance against HEAD after the edit, as in
  the earlier engine.js work. (~20%)

### Session B — engine, Kivy + parity (~45%)

- **Unit 3 — Kivy HUD pass.** Screen-space `_raycast_hud_group` on the scene's
  `canvas.after` above `_raycast_group`; window-height y-flip; stub-kivy test
  that pins the flip. Budget generously — this is the unit with both traps.
  (~30%)
- **Unit 4 — parity + retire the caveat.** Parity test that all three composite
  the HUD; add a HUD controller to `raycast_2`; drop the "caption-only" caveat
  from `raycast_1`/`raycast_2` guides (EN **and** FR). (~15%)

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

**Total ≈ 2 sessions of engine work, 2 of sample work.** Sessions A–B and C–D
are independently shippable.

## Open questions to settle before Session C

- **Status-bar layout** — DOOM-style bottom bar vs. corner overlays. Affects
  room height budget (a bottom bar eats vertical view space) and the sample's
  look. Worth a mock before committing.
- **Health damage model** — per-touch fixed damage vs. damage-over-time while
  overlapping. Per-touch is simpler and matches `raycast_2`'s collision idiom;
  damage-over-time reads better with a health bar. Recommend per-touch with a
  short invulnerability alarm.

## Out of scope

- No new draw actions or HUD authoring UI — reuse existing actions and the
  `maze_3` controller pattern.
- No world-space→view projection of top-down draws (see Scope-out above).
- No changes to the DDA / billboard / floor-cast passes — compositing order
  only.
- No minimap. It's the obvious next ask and it is **not** a HUD-compositing
  problem (it needs world-space projection, explicitly scoped out); it belongs
  in its own plan if wanted.

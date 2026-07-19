# Plan: in-view HUD compositing for raycast mode

Status: **PLAN (2026-07-19). Not started.** Surfaced by `raycast_2` (see
`RAYCAST_2_SAMPLE_PLAN.md` Unit 2 and the open-item in `RAYCAST_2_5D_PLAN.md`).
This is a **3-target engine feature**, not sample work.

## Problem

When raycast mode is active, HUD draw actions (`draw_score`, `draw_lives`,
`draw_text`, `draw_health_bar`, and the draw primitives) **don't render**. Each
target's renderer draws the first-person view and then stops before the normal
per-instance draw-event pass that composites the HUD:

- **Desktop** (`runtime/game_runner.py`): `_render_room` does
  `self._render_raycast_view(screen); return` (~line 1670), so the loop that
  calls `instance.render()` → draw event → `_process_draw_queue` never runs.
- **HTML5** (`engine.js`): `render(ctx)` does
  `if (this.raycastCamera && this.raycastCamera.enabled) { this.renderRaycastView(ctx); return; }`
  (~line 3213), skipping the sprite+draw-queue pass (normally at ~line 751).
- **Kivy** (`kivy_exporter.py`): the raycast view is an **opaque**
  `InstructionGroup` on `canvas.after` (~line 1915); the per-instance draw queue
  (`_render_draw_queue`, room-space y-down) is drawn elsewhere and is covered by
  (or ordered before) that opaque overlay.

Consequence: scored/lives-based raycast games (like `raycast_2`) show score/lives
only in the **desktop window caption** — invisible on the HTML5 (browser tab) and
Kivy (fullscreen) exports. Real limitation, not cosmetic.

## Design

**Composite the HUD as a final pass, on top of the finished first-person frame,
in SCREEN space** (no camera offset, top-left origin). A HUD `draw_text`/
`draw_score` at (8, 8) should land 8 px from the top-left of the window, exactly
as it does in a normal (non-raycast) game with no active view.

Which draw actions: the same per-instance `draw` events that already run in
normal mode — an authored HUD controller's `draw` event (`set_draw_font` +
`set_draw_color` + `draw_score`/`draw_lives`/`draw_text`, the maze_3
`controller_main` pattern). No new action types; this only changes *when/whether*
the existing draw pass runs under raycast.

Scope-out (leave as-is / documented): draw commands that are intrinsically
top-down (`draw_self`, `draw_sprite` at world coords, `draw_background`) have no
meaningful place over a first-person view — they may draw at their raw screen
coords or be skipped; a HUD is text/score/lives/bars, which is screen-space by
nature. Don't try to project world-space draws into the 3D view.

## Per-target approach

- **Desktop.** In `_render_room`, after `_render_raycast_view(screen)`, run the
  draw-event pass instead of bare `return`: for each instance with a `draw`
  event, `instance._draw_queue = []; execute_event(instance, "draw", events);
  instance._process_draw_queue(screen)` — screen-space (offset (0,0)). This is
  the exact code the normal `instance.render()` path already uses; factor it into
  a small `_render_draw_events(screen)` helper and call it from both paths.
- **HTML5.** In `render(ctx)`, before the raycast early-`return`, run the same
  draw-queue pass the normal path uses (the block near line 751 that executes the
  `draw` event and renders its queue) for each instance, on top of
  `renderRaycastView`. Keep it screen-space.
- **Kivy.** The raycast overlay is opaque on `canvas.after`; the HUD must be a
  **later** instruction group on `canvas.after` (added after `_raycast_group`) so
  it draws on top, fed by the per-instance draw queue in **screen space** (not
  the room-space y-down `_render_draw_queue`). Likely a dedicated
  `_raycast_hud_group` rebuilt each frame from the HUD instances' draw commands.
  Mind the `.format()`-template brace-doubling landmine.

## Testing

- **Desktop:** render one frame of a room whose HUD controller does
  `draw_score`/`draw_text` over an enabled raycast camera; assert non-background
  pixels appear in the HUD region (or intercept the draw-queue commands), through
  the real `run()` startup (the `set_sprites_for_instances` caveat from the
  2026-07-17 bug hunt).
- **HTML5 / Kivy:** structural assertions (the draw pass is invoked after the
  raycast render, not skipped) plus the existing stub-kivy harness for Kivy;
  no JS engine in CI, so HTML5 is source-level + a dev browser run.
- **Parity:** extend `tests/test_raycast_export_parity.py` — the HUD pass fires
  on all three (the DDA parity is already locked there).

## Unit sequence (one commit each — session-limit discipline)

- **Unit 0 — this plan.** Commit first.
- **Unit 1 — desktop HUD pass.** `_render_draw_events` helper + call it after
  `_render_raycast_view`; test.
- **Unit 2 — HTML5 HUD pass.** Draw-queue pass after `renderRaycastView`; test.
- **Unit 3 — Kivy HUD pass.** Screen-space `_raycast_hud_group` on `canvas.after`
  above the overlay; test.
- **Unit 4 — parity + wire the sample.** Parity test that all three composite the
  HUD; add a HUD controller (`draw_score` + `draw_lives`) to `raycast_2` (and
  optionally `raycast_1`), verify on all three targets, update those READMEs to
  drop the "caption-only" caveat.

## Out of scope

- No new draw actions or HUD authoring UI — reuse the existing draw actions and
  the maze_3 controller pattern.
- No world-space→view projection of top-down draws (see Scope-out above).
- No engine changes to the DDA / billboard / floor-cast passes — this is a
  compositing-order change only.

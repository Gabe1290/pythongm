# 2.5D raycast: per-cell ceilings and a seamless room-to-room teleport — plan

Written 2026-11-23. Follows `docs/RAYCAST_STAIRS_PLAN.md` (S0–S13, F1–F3, all done),
whose design, proofs and landmines this plan builds on. Resume state: the checkboxes
under **Units**.

## Goal

Two ideas borrowed from how Doom-era games disguised the "one floor per cell" limit
(the 2.5D view cannot put a floor above a floor; see the 2026-11-23 discussion):

1. **Per-cell ceiling height.** A cell can have a ceiling lower than the room's.
   Authors can build low tunnels, alcoves, doorway lintels, and passages *beside* a
   platform that read as going under it.
2. **Seamless room-to-room teleport.** An action that moves the player to another room
   at the *matching* position, facing and eye height, with no fade and no visible
   jump. Two rooms built to match around a junction then feel like one place: "under
   the platform" can be a second room.

Both live in the `raycast_2_5d` extension, need **no core change**, and run on all
three targets (desktop, HTML5, Kivy), as the stairs did.

## What exists today (verified against the code, 2026-11-23)

- **Heights**: `heights.py` `build_floor_heights(room, cell_size, max_height)` derives
  `(gx, gy) → height` from instances that ran **Set Floor Height**; rebuilt every frame;
  out-of-range heights are clamped once with a warning (`_clamped`). The ceiling is
  ONE height for the room: `wall_height × cell` (Enable Raycast View, default 1.5,
  clamped 1–10); `max_floor_height = (wall_height − 0.75) × cell − 4`.
- **Renderer**: with no step in the room the old single-hit path runs unchanged; with
  steps, `cast_ray_steps` records every grid crossing and `layout_column` walks them
  front to back with **one** clip value that rises from the bottom of the view
  (treads, risers, wall, billboard occluders). The **ceiling** is either a flat fill or
  the row-major `cast_floor_plane(ceiling=True)` at the single plane
  `wall_h − eye` — no per-cell variation anywhere.
- **Climbing**: `climbing.py`, extension frame hooks: per-axis undo of a move that
  climbs more than `max_step`; eye easing stored in `raycast_state(room)["eye_z"]`,
  **reset on room entry**; `raycast_floor_z` / `raycast_step_blocked` on movers.
- **Room change (desktop)**: `goto_room` only sets `instance.goto_room_target`; the
  loop calls `GameRunner.change_room`, which carries persistent instances, fires
  `run_room_change_hooks(old_room, new_room)`, then runs the new instances' **Create**
  events and **Room Start**, and the next frame is drawn. The camera's own Create event
  (`enable_raycast_view`, `set_facing_angle`) therefore runs on every entry.
- **Exports**: HTML5 `Game.changeRoom(name, forceRebuild, transition)` and
  `registerFrameUpdate(fn, phase)`; Kivy `GameApp._switch_to_room(index, …)` and the
  `_ext_update__<ext>` scene hook (after-collision only).
- **Speed headroom is already thin**: `tools/perf_levels/base_heights` costs 21–30 ms
  per frame on the dev box (34–48 fps); a second clip and a column-major ceiling cast
  add work. Hence a timing spike before committing to the design (C2).

## Design

### Part C — per-cell ceilings

**Authoring.** A new action **Set Ceiling Height** (category 3D View), used like Set
Floor Height in a non-solid object's Create event: `height` (room px, absolute, the
same unit as floor heights), optional `texture` (blank = the camera's ceiling texture,
then the flat colour). An object may run both actions, so one object can be a "low
tunnel cell" with a raised floor *and* a low ceiling. `heights.py` gains
`build_ceiling_heights` beside `build_floor_heights` (same covered-cells rule, same
once-per-instance warning), giving `(gx, gy) → ceiling` for lowered cells only; an
absent cell uses the room ceiling.

Constraints, clamped with a warning: `floor(cell) + EYE_HEIGHT + 4 ≤ ceiling(cell) ≤
room ceiling`. (A ceiling that low forbids standing there; a cell meant to be closed
should be a wall.)

**Rendering: a two-clip column walk.** Only rooms that contain a ceiling marker take
the new path; rooms with steps but no ceiling marker keep today's stairs path, and
rooms with neither keep the single-hit path — both byte-for-byte, proven by the same
old-vs-new frame diff the stairs plan used (768 frames). The walk keeps `clip_bottom`
(as today) and adds `clip_top`, starting at the top of the view:

1. Cell being left: its **ceiling span** from `clip_top` down to
   `y(ceiling_cur, d)` (record it for the ceiling cast), then
   `clip_top = max(clip_top, y(ceiling_cur, d))`. Its tread as today.
2. If the next cell's ceiling is **lower**, draw its **lintel** (Doom's "upper
   texture") from `y(ceiling_cur, d)` down to `y(ceiling_next, d)`, clipped, then lower
   `clip_top` to its bottom. If the next floor is higher, its riser as today.
3. Stop once `clip_top ≥ clip_bottom` (the column is full).
4. At the wall: from `max(y(ceiling_cur, d), clip_top)` down to `clip_bottom`.
5. **Ceiling cast becomes column-major**, mirroring S6's floor: each low-res ceiling
   pixel belongs to a recorded span of known height `c`, so
   `d = (c − eye_z) × view_h / (horizon − y)`. Per-cell `texture`, else the camera's.
6. **Billboards**: occluders record `(d, clip_top, clip_bottom)`; a sprite behind a
   lintel loses its top rows exactly as one behind a step loses its bottom rows.
7. **Sky**: a sky texture keeps drawing where the room ceiling is open; a lowered cell's
   ceiling span is cast over it (a tunnel under an open sky looks right).

**Movement.** `climbing.py` gains a **headroom** rule beside the step rule: a move into
a cell where `ceiling − floor < EYE_HEIGHT + HEADROOM` (HEADROOM 4 px) is undone per
axis, exactly like a too-high step, so the player slides along the opening. The eye
never rises above `ceiling − 4`. New readable variable `raycast_ceiling_z`.

### Part T — seamless teleport

**Authoring.** A new action **Go to Room Seamlessly** (category 3D View), parameters:
`room` (target room) and `marker` (an object). The author places one instance of the
marker object in *each* room, at the "same" spot of the shared geometry. On the
action, the camera's offset from the marker in the current room becomes its offset
from the marker in the target room. Markers, rather than raw dx/dy numbers, because
students can line two rooms up by eye in the room editor, and the junction survives
either room being edited.

**Carried across**: camera `x`, `y` (via the marker offset), `facing_angle`, `speed`
and `direction` (no stop at the junction), and the eased `eye_z` (no bob). Nothing else
— other instances belong to their own rooms.

**When it is applied — the key point.** The action records a pending arrival and
requests an ordinary instant room change (`goto_room`, `transition='none'`). The new
room's Create / Room Start events run as usual (the camera re-arms its raycast view and
sets its authored facing angle). The arrival is applied in the **first `before_step`
frame hook of the new room** — after those events, before any frame is drawn — so the
transferred angle wins and no frame shows the camera at its authored start.
`climbing.py` must not reset `eye_z` on that entry (it reads the pending arrival).
Same mechanism on the exports: HTML5 via `changeRoom` + a `before_step` frame update;
Kivy via `_switch_to_room` + the first `_ext_update__raycast` of the new scene (Kivy
has no before-step hook — the arrival is applied before that scene's first render,
which unit T1 must prove there, not assume).

**Failure modes, all logged, none fatal**: marker missing in either room → plain room
change at the target's authored start; target room missing → nothing happens (same as
`goto_room`); no raycast camera → the action still changes room.

## Decisions (owner, before C1)

**Decided 2026-11-23: the recommended choice on all five** — a separate Set Ceiling
Height action (D1), absolute heights (D2), marker objects (D3), "Go to Room
Seamlessly" / « Aller dans une salle sans transition » (D4), a new sample `raycast_6`
(D5).

- **D1 — Authoring.** A separate **Set Ceiling Height** action (recommended) vs a
  `ceiling` parameter on Set Floor Height. Separate keeps both actions small and lets
  an object be a ceiling-only marker.
- **D2 — Units.** Absolute height above ground (recommended, like floors and like Doom)
  vs clearance above the cell's floor.
- **D3 — Teleport anchor.** Marker objects (recommended) vs numeric offsets.
- **D4 — Name.** "Go to Room Seamlessly" / « Aller dans une salle sans transition »
  (proposal).
- **D5 — Demo.** A new sample `raycast_6` (both features: a low tunnel beside a
  platform leading to a second room "under" it), or extend the
  `tools/perf_levels/base_heights` test level only.

## Non-goals (could be later plans)

Floors above floors in one room (several layers per cell); sloped floors or ceilings;
moving ceilings (crushers, doors that lower); teleporting other instances with the
player; fade or other visible transitions for the new action.

## Units (one commit + push each; raycast test files + smoke after each)

- [x] **C0 — This plan.** (2026-11-23)
- [x] **C1 — Set Ceiling Height + the ceiling map.** (2026-11-23) Action schema/handler in the
  extension, `build_ceiling_heights`, clamping + warning, unit tests. No rendering yet.
  `heights.py`: `is_ceiling`, `is_geometry` (step or ceiling marker), and
  `build_ceiling_heights(room, cell, room_ceiling, floor_heights, eye)` — lowest marker
  wins per cell, clamped per cell to `[floor + eye + 4, room ceiling]`, one warning per
  instance, stored in `raycast_state(room)["ceiling_heights"/"ceiling_textures"]`. The
  renderer's billboard pass and `climbing._is_mover` now skip ceiling markers as well as
  steps (`is_geometry`). Parameter labels reuse "Height" / "Ceiling Texture" (already in
  every language); the action name and description are in all eleven `config/ui_names`
  tables, the two parameter descriptions in the eight that have that section. Extension
  action count 48 → 49. `tests/test_raycast_ceiling_heights.py` (18). **Known gap until
  C7/C8:** the HTML5 and Kivy exports do not know the action, so a marker there is drawn
  as an ordinary sprite.
- [x] **C2 — Timing spike (throwaway; result recorded here).** (2026-11-23) Two-clip walk +
  column-major ceiling cast on `base_heights` with tunnels added: if a ceiling room
  costs more than ~1.3× the same room without ceilings on the dev box, decide
  (here, with the owner) between a lower ceiling-cast resolution and dropping the
  per-cell ceiling texture before writing C3.
  **Result: 1.16× — under the limit, design unchanged.** Real engine, headless, the
  hand-test's scripted walk (up the staircase, turn round), 311 frames, two runs per
  mode. A (today): 26.3–26.5 ms work/frame, of which the column-major floor cast
  6.4–6.5 ms. B (the row-major ceiling cast replaced by a prototype column-major one
  — a mirror of `cast_stairs_floor`'s per-pixel loop with a per-cell texture lookup —
  plus a second pass over each column's spans for `clip_top`): 30.4–30.9 ms, of which
  the ceiling cast 8.0–8.1 ms and the extra walk pass 0.2 ms. So the cost is the
  ceiling's per-pixel cast (≈ 8 ms in place of the row-major plane's ≈ 4 ms); the
  two-clip walk itself is negligible. The prototype cast the whole upper half, so the
  real C4 (ceiling spans only, as the floor does treads) should cost no more. If C4
  needs speed later, the lever is the same as the floor's: `floor_cast_res`.
- [x] **C3 — Desktop two-clip walk.** (2026-11-23) `layout_column` gains `clip_top`, ceiling spans
  and lintels; identity proof for stair-only and plain rooms (768-frame diff).
  As built: `layout_column` is untouched; a separate `layout_column_ceilings` (two
  clips: ceiling spans, lintels where the next ceiling is lower, the wall rising to the
  ceiling of the cell in front of it, `occluders_top` for C5) runs only when the room
  has lowered ceilings. `cast_ray_steps(..., ceilings=None)` also records ceiling
  changes when given a map (sixth item, None = room ceiling). `render_raycast_view`
  builds the ceiling map each frame; a room with markers takes the column walk even
  without steps. Lowered spans are drawn in the flat `ceiling_color` (C4 casts them),
  lintels with the wall texture and shading. **Identity proof:** real engine, scripted
  walk, every frame hashed, new vs previous renderer — `raycast_1` and `raycast_5`
  identical on all 321 frames; `stairs_speed` and `base_heights` identical on all 321
  below the yellow readout (its timings differ between any two runs, new vs new
  included): 1,284 frames. `tests/test_raycast_ceilings_render.py` (9).
- [x] **C4 — Column-major ceiling cast + per-cell texture; sky interplay.** (2026-11-23) `cast_ceiling_spans` (mirror of `cast_stairs_floor`): only the LOWERED spans of each column are cast, at their own height, into a transparent low-res surface that is upscaled over the screen before the lintels, risers and walls are drawn at full resolution. Texture per pixel: the cell's own ceiling texture, else the camera's, else the flat ceiling colour. The room-ceiling spans are not touched, so the room's own flat / sky / row-major pass stands and a sky stays visible where the ceiling is open; a lowered cell roofs over it (camera texture if set, else flat). The cast runs only when the camera or a marker names a ceiling texture; otherwise the spans stay the crisp flat fills of C3, and a room without lowered ceilings never reaches the new code (byte-identical by construction). `tests/test_raycast_ceilings_cast.py` (8; 5 fail without the change). Cost not re-measured: it casts only the lowered spans, which C2 already costed at the whole upper half (1.16x).
- [x] **C5 — Billboards clipped by lintels.** (2026-11-23) The billboard pass reads each column's `occluders_top` (`_clip_top_before`, mirror of `_clip_before`) and draws a sprite only below the top clip the walk had reached before the sprite's distance, shifting the source rows with it; columns without ceilings (`occluders_top` absent) take exactly the old path. `tests/test_raycast_ceilings_billboards.py` (5; the two behaviour tests fail with the clip disabled).
- [x] **C6 — Headroom in `climbing.py`; `raycast_ceiling_z`.** (2026-11-23) Every mover reads `raycast_ceiling_z` (the lowered ceiling over it, else the room's); the camera's eased view height never rises above the ceiling over it (CEILING_MARGIN below): off a ledge into a low tunnel the eye drops to the roof at once, then eases down. **Plan change, found while building it:** the movement refusal the plan describes (undo a move into a cell where ceiling - floor < eye + 4) can never fire, because C1's `build_ceiling_heights` already clamps every cell's ceiling to at least floor + eye + 4 -- so every cell can be stood in. It was not built; only the view needed the limit. `tests/test_raycast_ceilings_climbing.py` (7, one through the real `GameRunner` loop; the two eye tests fail with the limit disabled).
- [x] **C7 — HTML5 port** (`export_html5.js`). (2026-11-23) Everything C1-C6 did, same names and arithmetic: the `set_ceiling_height` action, `buildCeilingHeights`, `castRaySteps` with a ceilings map (sixth crossing item), `raycastLayoutColumnCeilings`, `castCeilingSpans` (transparent low-res canvas, cell texture / camera texture / flat), the flat ceiling fill and lintels in `drawStairsColumn`, the billboard top clip (`raycastClipTopBefore`), `raycast_ceiling_z` and the eye limit in the climbing hooks; ceiling markers are neither movers nor billboards. `tests/test_html5_raycast_ceilings.py` (7): layout and ray walk equal the Python originals to 1e-12 on 300 random inputs each, and an exported tunnel project in headless Chromium renders its lintel, flat and textured ceiling on the predicted rows, hides a billboard's top, and drops the view under the roof while walking (the two behaviour tests fail with those two rules disabled). Not compared: a whole-frame desktop-vs-browser diff, and no frame-identity run for rooms without ceilings (the new code is reached only when the room has a marker).
- [x] **C8 — Kivy port** (`export_kivy.py` `SCENE_CODE`), stub harness + real Kivy. (2026-11-23) Same pieces as C7 in the scene: `_raycast_build_ceiling_heights`, `_cast_ray_steps` with a ceilings map, `_layout_column_ceilings` and `_clip_top_before` (verbatim copies), `_stairs_ceiling_buffer` / `_stairs_ceiling` (RGBA buffer, transparent outside lowered spans, nearest filtering so no dark fringe), flat spans and lintels in `_draw_stairs_column`, the billboard top clip in Kivy's y-up terms, `raycast_ceiling_z` and the eye limit in `_ext_update__raycast_2_5d`, the `set_ceiling_height` codegen; markers are neither movers nor billboards. `tests/test_kivy_raycast_ceilings.py` (12): the walk, layout and clip equal the desktop functions on 300 random inputs; the stub harness checks the map clamp, the projected rows, the cast buffer, a lintel hiding a billboard and the climbing hook (two behaviour tests fail with the eye limit / top clip disabled); and under real Kivy an exported tunnel is drawn on the predicted rows, flat and textured. Not run on a device. **All of part C (C1-C8) is done on all three targets.**
- [x] **T1 — Go to Room Seamlessly, desktop.** (2026-11-23) Action `go_to_room_seamlessly` (`room`, `marker`) in 3D View; `teleport.py` records a pending arrival on the game runner (offset from the marker, facing, hspeed/vspeed, eased `eye_floor`/`eye_vz`) and requests an instant room change; the arrival is applied in the new room by `teleport.after_collision`, registered BEFORE climbing's. **Plan correction, found by testing:** the plan applied it in the first `before_step` of the new room, but on desktop the room change happens inside `update()` and the frame is drawn in the SAME iteration, before the next `before_step` -- applied there, one frame is drawn at the authored start (the test fails 4 ways with that phase). `after_collision` runs after the room change and before the draw, so no wrong frame is ever drawn. The HTML5 and Kivy ports (T2) must re-check their own order. Failure modes (all logged, none fatal): target room missing -> nothing; camera missing, a marker missing in either room, or same room -> a plain room change at the new room's authored start. Name and description in all eleven `config/ui_names` tables, the two parameter descriptions in the eight that have that section (no native-speaker read); extension action count 49 -> 50. `tests/test_raycast_seamless_teleport.py` (11, through the real `GameRunner` loop, camera recorded at every draw call).
- [x] **T2 — HTML5 + Kivy ports of T1**, each proving "no frame at the authored start". (2026-11-23) **HTML5** (`export_html5.js`): the engine changes room in the middle of a logic step and runs the NEW room's Create events at the start of ITS first step (a keyboard-triggered action runs before the room's own step, so that path has no gap; a step/collision/alarm-triggered one does). The arrival is applied by a frame update in the `after_collision` phase, registered before climbing's, only once the new room has consumed `_pendingRoomStart` (= its Create / Room Start ran); until then the room renderer shows a snapshot of the frame from before the change (the canvas resize would blank it otherwise). `tests/test_html5_raycast_teleport.py` (4, Chromium, action fired from a Step event): every frame the canvas shows is the old room's or the new room's raycast view (ceiling pixel read per animation frame), every raycast draw of the new room has the camera at the arrival position; both rules fail when disabled. **Kivy** (`export_kivy.py`): no hook is needed -- `GameApp._do_room_switch` builds the new scene and the scene CONSTRUCTOR runs the Create events and then renders the first overlay frame, so the arrival is applied at the head of `_ext_overlay__raycast_2_5d` (scene method `_raycast_apply_arrival`), with the offset kept in the author's y-down space so rooms of different heights agree; `_raycast_go_seamless` is the action's target (codegen `self.scene._raycast_go_seamless(room, marker)`). `tests/test_kivy_raycast_teleport.py` (11, incl. real Kivy: the real generated scenes of a two-room export, the new scene constructed as the game does and its camera read before any update). Known edge, not changed: a PERSISTENT room reused from the cache is not rebuilt, so its overlay shows its last frame until its first update.
- [ ] **D5 demo** — sample or test level, guides EN + FR, Welcome tab if a sample.
- [ ] **Docs and translations** — wiki 3D-View pages (nine languages), regenerated
  action reference, the two actions' dialog text in all ten shipped languages,
  `TODO.md`, the `CLAUDE.md` session note.

## Risks and landmines to carry in

- **Speed.** The stairs path already runs below 60 fps in `base_heights` on the dev
  box; C2 exists so the design is costed before it is built.
- **Pixel identity.** Keep the original float expressions when refactoring
  (`* (view_h / d)` vs `* view_h / d` changed pixels in the stairs work); the identity
  diff catches it.
- **Kivy**: `SCENE_CODE` is %-formatted (double any `%`); scene hooks are
  `_ext_<hook>__raycast`, never overrides; test with all extensions enabled.
- **HTML5**: the extension-syntax test counts brackets without string awareness.
- **Translations**: new dialog text needs all ten languages and must be filed under the
  contexts that actually run it (`scripts/i18n_catchup.py`).
- **Teleport timing differs by target** (desktop and HTML5 have a before-step hook,
  Kivy does not); each port proves its own "no wrong frame".
- **This machine's config disables some extensions** — force them on in tests, never
  edit the user's config.

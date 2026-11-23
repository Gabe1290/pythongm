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
- [ ] **C1 — Set Ceiling Height + the ceiling map.** Action schema/handler in the
  extension, `build_ceiling_heights`, clamping + warning, unit tests. No rendering yet.
- [ ] **C2 — Timing spike (throwaway; result recorded here).** Two-clip walk +
  column-major ceiling cast on `base_heights` with tunnels added: if a ceiling room
  costs more than ~1.3× the same room without ceilings on the dev box, decide
  (here, with the owner) between a lower ceiling-cast resolution and dropping the
  per-cell ceiling texture before writing C3.
- [ ] **C3 — Desktop two-clip walk.** `layout_column` gains `clip_top`, ceiling spans
  and lintels; identity proof for stair-only and plain rooms (768-frame diff).
- [ ] **C4 — Column-major ceiling cast + per-cell texture; sky interplay.**
- [ ] **C5 — Billboards clipped by lintels.**
- [ ] **C6 — Headroom in `climbing.py`; `raycast_ceiling_z`.** Through the real
  `GameRunner` loop (the stairs plan's harness), not a hand-built room.
- [ ] **C7 — HTML5 port** (`export_html5.js`), Chromium parity to 1e-12 as in S10.
- [ ] **C8 — Kivy port** (`export_kivy.py` `SCENE_CODE`), stub harness + real Kivy.
- [ ] **T1 — Go to Room Seamlessly, desktop.** Action, pending arrival, `before_step`
  apply, `eye_z` kept. Tests through the real loop: no frame drawn at the authored
  start, facing and speed carried, the camera's Create event does not win, all three
  failure modes.
- [ ] **T2 — HTML5 + Kivy ports of T1**, each proving "no frame at the authored start".
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

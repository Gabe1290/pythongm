# Plan: closing the "documented deferred engine gaps" + explicit-ask items

Registry + resume state for the queue described in `CLAUDE.md`'s 2026-08-14
"list any and all work that still needs to be done" audit. Work one unit at a
time, one commit per unit, full suite green + push after each (this repo's
standing session-limit discipline — see `CLAUDE.md`'s "Standing preferences &
landmines"). Flip checkboxes as units land.

## Corrections made before scheduling anything (audit-is-a-lead discipline)

Two of the original 9 "documented deferred engine gaps" turned out not to be
real work:

- [x] **Raycast HTML5/Kivy floor rendering was already DONE**, not deferred —
  the "blocked on a per-target GL/browser timing spike" note in `CLAUDE.md`
  was written mid-session on 2026-07-19, hours before units 3b/5b actually
  landed that same day (`031cc1e1` HTML5, `796daea9` Kivy). Corrected in
  `CLAUDE.md` and `docs/VOXEL_WORLD_PLAN.md` (2026-08-14). No code change.
- [x] **execute_file / execute_shell: decision confirmed — stay disabled.**
  Asked the user directly given the security stakes for children's software;
  explicit choice was to leave both as log-and-return placeholders rather
  than build a sandboxed opt-in model. Neither has a UI registration, so
  there was never a dead-end-UI problem, just an internal placeholder.
  Corrected in `TODO.md` (2026-08-14). No code change.

## Tier 1 — small, safe cleanups

- [ ] **1.1 Remove the dead "script"/"code" action stub.**
  `runtime/action_handlers/control_handlers.py`'s `handle_script` (L217-239)
  and `handle_code` (L186-215), registered as `"script"`/`"code"` in
  `CONTROL_HANDLERS` (L259-260). Confirmed unreachable: neither name has an
  `ActionType` entry in `events/action_types.py`, and no sample/importer
  emits them — a dead path distinct from the real, working
  `execute_script`/`execute_code` actions. Delete both functions + registry
  entries. Test: assert `"script"`/`"code"` absent from `CONTROL_HANDLERS`
  and `get_action_type` still returns `None` for both (no behavior change).

- [ ] **1.2 Unify `get_action_type` alias resolution with `ActionExecutor.ACTION_ALIASES`.**
  Two independently-maintained alias tables exist today: `events/action_types.py`'s
  `ACTION_TYPE_ALIASES` (L2516, consulted by `get_action_type`, L2572-2579)
  and `runtime/action_executor.py`'s `ACTION_ALIASES` (L467-485, 10 entries,
  consulted only at dispatch, L518-520). Make `get_action_type` fall back
  through `ActionExecutor.ACTION_ALIASES` too via a lazy/local import (avoid
  a circular import — `action_executor.py` already imports from
  `action_types.py`). Test: a name only in runtime's `ACTION_ALIASES` (e.g.
  `"display_message"`) now resolves via `get_action_type`.

## Tier 2 — small, single-target honesty fixes

- [ ] **2.3 Thymio "play sound".** Investigate first: is real Thymio
  hardware tone-only, or can the simulator legitimately play a sampled
  sound? If hardware is tone-only (current docstring already asserts this),
  narrow the fix to making sure UI/docs never imply sample playback is
  coming — a documentation-honesty fix, not a feature gap. Only build real
  sample mixing in `thymio_simulator` if research shows the hardware
  genuinely supports it.

- [ ] **2.4 Register `show_video`; fold `splash_show_video`/`splash_show_webpage` into it.**
  `execute_show_video_action` (`action_executor.py:2837`) already works (OS
  default-player shell-out, honest docstring) but has no `ActionType` entry
  — invisible in the UI despite being functional. Register it with a
  description that says plainly "opens in your system's video player, not
  in-engine playback." No new dependency (moviepy/opencv) — flag as a
  possible future ask if ever wanted. `splash_show_webpage` registers as a
  thin wrapper over `handle_open_url`/`webbrowser.open`; `splash_show_video`
  becomes an alias to the newly-registered `show_video` handler.

- [ ] **2.5 Register real `splash_show_text` / `splash_show_image`.** Reuse
  the runtime's existing blocking modal-message machinery
  (`_show_or_queue_message`, used by `show_info`/`show_message`) for text;
  a full-screen sprite blit + wait-for-input loop (existing
  `draw_sprite`/`draw_background` primitives) for image. Register both in
  `events/action_types.py`.

## Tier 3 — Kivy long-tail action coverage (several small commits)

- [ ] **3.x** ~18-20 actions in `ACTION_TYPES` have no branch in
  `export/Kivy/code_generator.py`'s `process_action`/`_convert_simple_action`:
  `bounce`, `open_webpage`, `save_game`, `load_game`, `test_question`,
  `show_info`, `stop_sound`, `check_sound`, `check_room`, `fill_color`,
  `set_alpha`, `move_towards_point`, `draw_scaled_text`, `set_image_index`,
  `set_image_speed`, `set_room_caption`, `start_animation`,
  `stop_animation`, plus whatever Tier 2 newly registers. Work in clusters
  of 3-5 related actions per commit, mirroring the desktop runtime handler;
  compile-gated regression test per commit
  (`tests/test_kivy_more_actions_export.py` pattern). Lowest-risk, most
  mechanical tier — good first thing to ship after Tier 1.

## Tier 4 — Block World real texture mapping (large, ~1-2 sessions)

Desktop already textures all faces by default (`wall_textured=True`,
`top_cast_res=4`, `extensions/block_world/renderer.py`'s `_draw_wall_strip`
sub-texel crop + `_draw_horizontal_face_textured` per-pixel cast). HTML5
(`export_html5.js`) and Kivy (`export_kivy.py`) flat-fill **all three** face
orientations from precomputed `BLOCK_FACE_COLORS` — a real, visible fidelity
gap on `block_world_1` today.

- [ ] **4a. Side (wall) faces.** Reuse the already-proven raycast wall
  texturing pattern: HTML5 `ctx.drawImage` sub-rect slicing
  (`export_html5.js`'s raycast wall renderer, ~L228), Kivy
  `texture.get_region()` (`export_kivy.py`'s raycast renderer, ~L501/585).
  Highest visual impact, lowest risk.
- [ ] **4b. Top/bottom (horizontal) faces.** Port the `top_cast_res`
  downsampled per-pixel cast — same *category* as raycast's floor casting,
  different geometry (block quads vs. a single ground plane); template, not
  a literal port.
- [ ] Parity test per half against desktop (mirroring
  `tests/test_block_world_export_parity.py`) + compile/brace-balance gate.

## Tier 5 — Particle system + timelines (large, greenfield, ~3+ sessions, last of Tiers 1-6)

100% write-only today: `action_executor.py`'s particle/emitter/timeline
`execute_*_action` methods populate `instance._particle_system`/
`instance.timeline_*`, but `game_runner.py` never reads any of it — nothing
spawns/ages/moves/draws/advances. Zero `ActionType` entries (no dead-end UI
today, just unbuilt).

- [ ] **5.1 Phase 1 (desktop engine).** Per-frame update step in
  `game_runner.py`: age/move/cull particles, spawn from armed emitters, new
  `_render_particles` draw step. Timelines: advance `timeline_position` by
  `timeline_speed` when running, firing whatever's scheduled — investigate
  the actual "moments" storage shape the write-side handlers already
  produce before designing the read side. Verify with a real `GameRunner`
  driven through frames, not a hand-rolled harness.
- [ ] **5.2 Phase 2 (UI).** Register in `events/action_types.py` (2026-06-05
  "safe bucket" precedent). Check whether the existing `multi_choice`
  pattern suffices for a timeline "moments" editor before inventing a new
  `param_type`.
- [ ] **5.3 Phase 3 (export parity).** HTML5/Kivy, deferred until Phase 1-2
  are proven and at least one sample uses them (match3_1 lesson: don't chase
  parity for a feature nothing uses yet).

## Tier 6 — Manifest-ify sprites in `project.json` (medium, ~1 session)

Follow the objects precedent (`core/project_manager.py::_prepare_project_data_for_save`,
L947-970) exactly. Sequence **after** Tier 4 — both touch the same three
export-loader files; keep as separate clean passes.

- [ ] Strip the **whole** sprite body on save (unlike objects, which
  stripped just `events` — sprites have no single risky subfield to
  isolate; small pure metadata, no pixel data).
- [ ] No new loader code needed for core/runtime —
  `core/project_manager.py::_load_sprites_from_files` and
  `runtime/game_runner.py::_load_sprites_from_files` already have working
  `merge_sprite_file` logic, currently a no-op since nothing strips yet.
- [ ] Add sprite-file loading to the three export paths that have **zero**
  today: `export/base_exporter.py`, `export/android/android_exporter.py`,
  `export/ios/ios_exporter.py` — mirror the existing merge pattern.
- [ ] Route `export/HTML5/html5_exporter.py::encode_sprites` and
  `export/Kivy/kivy_exporter.py::_export_sprite` through a sprite-file merge
  (currently read embedded data directly).
- [ ] Mandatory round-trip test mirroring
  `tests/test_manifest_ify_objects_round_trip.py`: fresh project
  (byte-identical reload), legacy embedded-only project (unchanged), `.zip`
  export/import round-trip, one real bundled sample. One test per
  newly-sprite-aware export path.

## Tier 7 — Block World big features (large, multi-part)

- [ ] **7a. Jump mechanic (~1 session).** Vertical velocity (`vz`) in
  `execute_move_and_collide_action` (`extensions/block_world/handlers.py`,
  currently pure horizontal + "footing is always `ground_layer`", no
  gravity anywhere), jump action/key, gravity accumulation, real landing
  detection. Comparable to Unit 5's original size in `docs/VOXEL_WORLD_PLAN.md`.
- [ ] **7b. Per-type block protection beyond `breakable` (small, needs a
  definition first).** `state.py`'s `is_breakable` (L160-174) is already a
  single boolean per block type — a second flag is the same shape.
  **Underspecified: confirm with the user what "protection" means**
  (unbreakable only? un-placeable-on? requires a specific hotbar item?)
  before implementing.
- [ ] **7c. Inventory with counts (medium; crafting split out).** Today's
  hotbar (`state.py`'s `DEFAULT_HOTBAR`, `handlers.py`'s
  `select_hotbar_slot`) is a fixed list, no counts/stacking (documented as
  deliberately out of scope creative-mode selection). Add real counts
  (pickup-on-break, consume-on-place, persisted in room state, real
  slot-count rendering in the hotbar HUD macro action). **Crafting has zero
  existing scaffold** (no recipes, no UI) — needs its own dedicated
  planning pass, not bundled here.
- [ ] **7d. In-IDE visual world editor — needs its own future planning
  session, do not start from this doc.** No `editors/` scaffolding exists;
  building one is a new editor pane on the scale of
  `editors/room_editor/`/`editors/playground_editor/`. Largest item in the
  whole queue — larger than Tier 5. Do last, once 7a-7c settle the
  interaction model it needs to expose.
- [ ] **7e. Procedural/infinite terrain — needs its own future planning
  session, do not start from this doc.** World storage today is a single
  in-memory sparse dict per room, no chunking/streaming. "Infinite" terrain
  needs a fundamentally different storage model and reworking every
  renderer's "iterate all blocks" assumption on all three export targets —
  comparable in size to a second `VOXEL_WORLD_PLAN.md`.

## Verification (every tier)

One unit = one commit, full suite (`QT_QPA_PLATFORM=offscreen python3 -m
pytest tests/ -q`) green before moving on, push after each commit. Flip the
checkbox above as each unit lands. Engine-loop changes (Tier 5, 7a) get a
real `GameRunner`-driven test. Export-parity changes (Tier 3, 4, 5.3, 6) get
a compile/structural gate and, where numerically comparable, a parity test
against the desktop implementation (matching `_cast_ray`/`march_ray`
precedent).

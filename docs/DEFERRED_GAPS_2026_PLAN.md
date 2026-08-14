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

- [x] **1.1 Remove the dead "script"/"code" action stub.** Done `3b099735`.
  `runtime/action_handlers/control_handlers.py`'s `handle_script` (L217-239)
  and `handle_code` (L186-215), registered as `"script"`/`"code"` in
  `CONTROL_HANDLERS` (L259-260). Confirmed unreachable: neither name has an
  `ActionType` entry in `events/action_types.py`, and no sample/importer
  emits them — a dead path distinct from the real, working
  `execute_script`/`execute_code` actions. Delete both functions + registry
  entries. Test: assert `"script"`/`"code"` absent from `CONTROL_HANDLERS`
  and `get_action_type` still returns `None` for both (no behavior change).

- [x] **1.2 Unify `get_action_type` alias resolution with `ActionExecutor.ACTION_ALIASES`.** Done `e08c09d1`.
  Two independently-maintained alias tables exist today: `events/action_types.py`'s
  `ACTION_TYPE_ALIASES` (L2516, consulted by `get_action_type`, L2572-2579)
  and `runtime/action_executor.py`'s `ACTION_ALIASES` (L467-485, 10 entries,
  consulted only at dispatch, L518-520). Make `get_action_type` fall back
  through `ActionExecutor.ACTION_ALIASES` too via a lazy/local import (avoid
  a circular import — `action_executor.py` already imports from
  `action_types.py`). Test: a name only in runtime's `ACTION_ALIASES` (e.g.
  `"display_message"`) now resolves via `get_action_type`.

## Tier 2 — small, single-target honesty fixes

- [x] **2.1 `pygm2_pt.ts`'s `WelcomeTab` context is missing 26 of 48
  messages.** Done (2026-08-15). Re-verified before fixing (audit-is-a-lead):
  the "26 of 48" figure was a miscount — 48 counted every `<message>` element
  in fr's `WelcomeTab` context including 8 historical `vanished` ones and
  duplicate `<location>`s; the real active-message diff against fr found only
  **one** truly missing string, `"📖  Sample guides"`. But chasing that one
  string surfaced the actual bug: `SampleDocsDialog` (the guide-viewer dialog
  that button opens) was missing as a **whole context** — 3 real active
  messages (`"Sample guides"` window title, `"_No bundled samples were found
  in this build._"`, `"_No documentation is bundled for **{0}**._"`) — from
  pt, ja, **and** zh alike (confirmed ja/zh inherited the same gap, per the
  investigation note above). The other 3 "missing" contexts a full context-
  name diff also turned up (`AboutDialog`, `EventActionWidget`,
  `GM80EventsPanel`) are correctly absent — all have zero active messages in
  fr too (dead/renamed classes), so pt/ja/zh's "only what's currently used"
  build already handled them right. Fixed: added the 1 `WelcomeTab` message +
  the 3-message `SampleDocsDialog` context to all three `.ts` files, real
  translations (not copies) for each language, verified via a live
  `QTranslator` resolving all 4 strings in all 3 languages and differing from
  the English source. `tests/test_sample_docs_dialog_translations.py`
  (6 tests). Full suite: 2966 passed, 7 skipped, 0 failed.
- [x] **2.3 Thymio "play sound".** Done (2026-08-15). Investigated first:
  real Thymio hardware genuinely has no sampled-audio capability (only
  `sound.freq`/`sound.system` tone primitives) — but the gap turned out
  narrower than assumed, since it doesn't apply to the whole feature.
  `export/Aseba/aseba_exporter.py`'s `_translate_play_system_sound` already
  emits the real `sound.system(id)` Aseba call, so an exported/uploaded
  program plays the robot's own authentic melody for that sound — no
  approximation on real hardware at all. Only the in-app SIMULATOR preview
  (`runtime/thymio_action_handlers.py`) approximates each system sound as a
  single tone, which could mislead a student testing in the simulator into
  thinking that's what the real robot sounds like. Fixed by disclosing the
  simulator/hardware difference in `thymio_play_system_sound`'s user-facing
  description (`actions/thymio_actions.py`, shown directly in the action
  config dialog) rather than building anything — there's nothing to build,
  since hardware has no sampled playback to add. `thymio_play_tone`'s
  description needed no change (already accurate for both targets — real
  arbitrary-frequency tones work identically in both). Never had any
  translations to begin with (0 languages), so no i18n regression from the
  wording change. `tests/test_thymio_sound_honesty.py` (3 tests). Full
  suite: 2969 passed, 7 skipped, 0 failed.

- [x] **2.4 Register `show_video`; fold `splash_show_video`/`splash_show_webpage` into it.**
  Done (2026-08-15). `execute_show_video_action` (`action_executor.py:2837`)
  already worked (OS default-player shell-out) but had no `ActionType` entry
  — invisible in the UI. Registered with a description that says plainly it
  opens as a separate window in the system video player, not in-engine
  playback. `splash_show_video`/`splash_show_webpage` were both 100% dead
  code — no `ActionType` ever existed for either name, so nothing could have
  authored them through the UI — folded into `show_video`/`open_webpage` via
  `ActionExecutor.ACTION_ALIASES` (alias resolution rewrites the action name
  before handler lookup, so this is a real fold, not just a UI label); their
  now-unreachable placeholder handlers deleted from
  `runtime/action_handlers/extra_handlers.py`. `splash_show_text`/
  `splash_show_image` deliberately left alone — Tier 2.5's own real
  implementations, not a fold. `tests/test_show_video_action.py` (8 tests,
  including an end-to-end dispatch test proving the alias actually reaches
  the real handler, not just `get_action_type`). Full suite: 2977 passed,
  7 skipped, 0 failed.

- [x] **2.5 Register real `splash_show_text` / `splash_show_image`.**
  Done (2026-08-15). `splash_show_text` reuses `_show_or_queue_message`
  directly (the same blocking modal `show_message`/`show_info` already use).
  `splash_show_image` resolves its sprite through `runner.sprites` (the same
  registry `draw_sprite` reads from) and blits it full-screen via a new
  `GameRunner.show_splash_image` — a genuinely new blocking loop, not a
  `draw_sprite`/`draw_background` reuse (those only *queue* a draw-event
  command, they don't block; `show_splash_image` mirrors
  `show_message_dialog`'s own pygame-event loop, speed-pause/restore, and
  `KEYUP`/M54 silent-release handling instead), scaled to fit the screen
  preserving aspect ratio, letterboxed in black. Both registered in
  `events/action_types.py`. Auto-discovery means both executor methods take
  priority over the old placeholder handlers, which are now unreachable —
  deleted from `runtime/action_handlers/extra_handlers.py`. One real bug
  caught by the tests, not assumed: an early draft's fake-runner test
  fixtures were missing `global_variables`, which `_parse_value`'s bare-name
  fallback reads unconditionally — `execute_action`'s generic
  `except AttributeError` swallowed it silently, making a broken fixture
  look like a passing "no-op" test for the wrong reason; fixed by completing
  the fixtures and calling the handler directly where the test's whole point
  is proving no exception occurs. `tests/test_splash_show_actions.py`
  (6 tests). Full suite: 2983 passed, 7 skipped, 0 failed. **Tier 2 is now
  fully closed.**

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

- [x] **4a. Side (wall) faces.** Done (2026-08-14). Both targets draw real
  per-pixel wall textures (HTML5 `ctx.drawImage` sub-rect slicing off a
  `data:` URI `Image()`; Kivy `texture.get_region()` + `tex_coords`),
  falling back to `BLOCK_FACE_COLORS` only when a texture hasn't loaded or
  `wall_textured` is off. New infra both needed: `march_ray`/`_bw_march_ray`
  gained `tex_u` back (dropped in the original flat-color port);
  `extensions/block_world/export_data.py`'s `collect_export_data` now also
  returns `block_textures` (all 32 PNGs, base64) via the same generic
  `_collect_extension_data` hook Unit 8/9 built for `load_block_world`'s
  world data — HTML5 embeds them straight into `gameData`, Kivy decodes
  them back to real files under `assets/images/block_world/` via a new
  `KivyExporter._materialize_extension_textures`. The Kivy port needed a
  genuinely new derivation, not a literal raycast port: raycast's wall pass
  computes entirely in Kivy's native y-up space, so its `v0`/`v1` mapping
  falls out directly, but block_world's renderer computes in GM y-down
  space and flips only at the final draw — so real texturing needed the
  flip to apply to the *texture v-coordinate* too, not just the rectangle
  position. Verified with dedicated boundary-case tests (an unclipped
  full-height strip maps exactly v=[0,1]; a strip clipped from below by
  half its height maps `v_bottom=0.5`), not just visual inspection, since
  no Kivy/browser execution is available here. Two real bugs found and
  fixed along the way (both would have silently dropped `load_block_world`
  data too, not just textures): `export_data.py`'s new texture-collecting
  code used `Path(__file__)` and a relative `from .state import`, neither
  of which resolve inside the bare-namespace `exec()` both exporters use to
  load an extension's `export_data.py` — fixed by seeding `__file__` into
  the exec namespace (mirrors a real import) and switching to an absolute
  import. `tests/test_kivy_block_world.py`, `tests/test_html5_block_world.py`.
  Full suite: 2960 passed, 7 skipped, 0 failed. Smoke run 18/18.
- [ ] **4b. Top/bottom (horizontal) faces.** Port the `top_cast_res`
  downsampled per-pixel cast — same *category* as raycast's floor casting,
  different geometry (block quads vs. a single ground plane); template, not
  a literal port.
- [x] Parity test for 4a against desktop, mirroring
  `tests/test_block_world_export_parity.py` (structural, since real texture
  drawing can't be numerically diffed without a JS/Kivy execution
  environment) + compile/brace-balance gate. 4b's parity test is still
  open, pending 4b itself.

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

## Tracked elsewhere — not part of this queue, but genuinely open

Full picture of outstanding work also includes two items big enough to carry
their own plan docs rather than a line item here:

- **`docs/POST_1_0_REFACTOR.md` — splitting the four giant files.** Status:
  not started. Filed during the 1.0 stability push specifically so it would
  survive being set aside; nothing in this queue touches it, and nothing in
  this queue should be blocked on it either.
- **`docs/WIKI_COMPLETENESS_PLAN_2026-08-11.md` — per-tutorial-step
  screenshots.** The one deferred item from an otherwise-closed plan
  (Phases 0-3 and 5 done, Phase 4 explicitly decided against). Scoped down
  and logged there, not forgotten; pick up only on an explicit ask.

Both are correctly OUTSIDE this doc's own scope (a small-first, one-commit-
per-unit queue) — they're multi-session efforts in their own right, the same
reason Tier 7d/7e above say "needs its own future planning session, do not
start from this doc."

## Verification (every tier)

One unit = one commit, full suite (`QT_QPA_PLATFORM=offscreen python3 -m
pytest tests/ -q`) green before moving on, push after each commit. Flip the
checkbox above as each unit lands. Engine-loop changes (Tier 5, 7a) get a
real `GameRunner`-driven test. Export-parity changes (Tier 3, 4, 5.3, 6) get
a compile/structural gate and, where numerically comparable, a parity test
against the desktop implementation (matching `_cast_ray`/`march_ray`
precedent).

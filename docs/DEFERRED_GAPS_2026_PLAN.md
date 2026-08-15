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

- [x] **3.x** Done (2026-08-15), all 23 in one commit rather than several
  small ones — re-verified the list first (audit-is-a-lead: a naive grep
  first over-matched to 33 "missing" names before checking the real
  `code_generator.py` source, several of which were already handled via
  `in (...)` tuple branches the naive pattern missed), confirmed 23 genuinely
  absent anywhere in `export/Kivy/`, then found most share NEW shared
  infrastructure this unit had to build once regardless (a `PROJECT_META`
  constant baked at export time, a new `game/savegame.py` module mirroring
  `highscore.py`'s verbatim-string generation, `image_alpha`/`image_blend`
  wired into `_redraw_frame`'s `Color()` call so `set_alpha`/`set_color`
  have a REAL visible effect instead of an inert instance attribute, a new
  `'fill'` draw-queue command case, `stop_sound`/`is_sound_playing`/
  `open_webpage`/`show_video_file`/`show_splash_image` helpers in `main.py`)
  — splitting into artificial clusters would have meant re-touching the
  same shared code repeatedly. `bounce`, `open_webpage`, `save_game`,
  `load_game`, `test_question`, `show_info`, `stop_sound`, `check_sound`,
  `check_room`, `fill_color`, `set_alpha`, `set_color`, `move_towards_point`,
  `move_free`, `draw_scaled_text`, `set_image_index`, `set_image_speed`,
  `set_room_caption`, `start_animation`, `stop_animation`,
  `splash_show_text`, `splash_show_image`, `show_video` (the last two Tier
  2's own new registrations) all now generate real code, none fall through
  to the `pass # TODO` default. Three deliberate, documented scope
  reductions rather than silent gaps: **`bounce`** ports only
  `execute_bounce_action`'s own no-collision-info fallback branch (Kivy's
  collision model has no `h_blocked`/`v_blocked` equivalent to reverse a
  specific axis against); **`save_game`/`load_game`** persist score/lives/
  health/current-room only, not full instance positions/custom variables
  (would need rebuilding a room's instance list from saved data — a much
  larger change to the room-switching path); **`test_question`** always
  proceeds (`if True`), since Kivy's popups are callback-driven with no
  blocking-call equivalent to `desktop`'s `QMessageBox.exec()` to build a
  real Yes/No gate on — matches the desktop handler's own documented
  Qt-unavailable fallback rather than guessing False or dropping the
  action. `show_video`'s video file isn't copied into the export bundle
  (no video-asset pipeline exists) — same category of honest, narrower
  scope. One real bug caught by a real export + compile check, not
  assumed: `process_action`'s multi-line-code handling calls
  `line.strip()` on every line before re-indenting at a single shared
  level, so an early draft's nested `if:`/`else:` blocks for
  `move_towards_point`/`bounce` silently lost their indentation and
  produced a real `IndentationError` on compile — fixed by rewriting both
  as flat ternary expressions instead of nested blocks.
  `tests/test_kivy_tier3_actions_export.py` (27 tests, including one full
  `KivyExporter().export()` + multi-file compile run, not just isolated
  codegen strings). Full suite: 3010 passed, 7 skipped, 0 failed.
  **Tier 3 is now fully closed.**

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
- [x] **4b. Top/bottom (horizontal) faces.** Done (2026-08-15). Ported the
  `top_cast_res` downsampled per-pixel cast for both targets — genuinely a
  template, not a literal port of either the wall pass (4a) or raycast's
  floor caster, since a block face is a bounded quad sampled from a screen
  COLUMN, not an infinite plane sampled by ROW. `enable_block_world_view`
  now actually stores `top_cast_res` in the camera config on both targets
  (previously accepted but silently dropped since neither target had a
  per-pixel path to control the resolution of).
  - **HTML5**: `bwTextureData` builds a cached `ImageData` per texture
    (mirrors raycast's own `_textureData`); `bwDrawHorizontalFaceTextured`
    samples `ceil(span/res)` texels via the same inverse-projection formula
    as desktop's `_texel`, into a small offscreen canvas via `putImageData`,
    then `drawImage`-scales it to fill the face — same trick as the wall
    pass and raycast's floor caster.
  - **Kivy**: deliberately AVOIDS `Texture.create()`/`blit_buffer()` (whose
    row-order convention relative to `tex_coords` needed its own separate
    reasoning on top of `get_region`'s) — instead each sampled texel is its
    own `get_region(tx, th-1-ty, 1, 1)` single-pixel region (a 1x1 region
    has no orientation to get wrong), drawn as its own small `Rectangle`
    segment. Reuses the `th-1-ty` bottom-left-origin flip
    `_bw_fill_span_textured` (Tier 4a) already established for reading
    Kivy texture pixels. A real, deliberate perf-for-simplicity tradeoff:
    more draw calls than a single scaled blit, accepted for a first
    correctness-focused pass.
  - **Real numeric parity, not just structural**: fed the SAME inputs to
    desktop's actual `_draw_horizontal_face_textured` (via a fake
    pygame-Surface-like object recording every `get_at()` call) and the
    Kivy port (via a fake texture recording `get_region()` calls), and
    proved the two sample the IDENTICAL grid cell at every one of 10 rows
    (`tx` matches exactly; `ty` matches through the documented `th-1-ty`
    flip) — the strongest available proof short of watching real pixels.
    `tests/test_block_world_export_parity.py`
    (`test_desktop_and_kivy_horizontal_face_texel_grid_matches`).
  - One real test-authoring bug caught before it shipped (same class as
    the grid-alignment trap documented elsewhere in this repo): an early
    draft's point-blank camera-to-block distance combined with a tall
    `eye_height` pushed the ENTIRE projected face span off-screen (`y0v >
    y1v` after clamping), making the test pass for the wrong reason (0
    draws either way) until checking the real render output showed the
    face genuinely wasn't drawing — fixed by using a realistic multi-cell
    camera-to-block distance, matching how the actual sample plays.
  - `tests/test_kivy_block_world.py`, `tests/test_html5_block_world.py`,
    `tests/test_block_world_export_parity.py`. Full suite: 3019 passed,
    7 skipped, 0 failed. Smoke run 18/18; real end-to-end export of
    `block_world_1` verified on both targets. **Tier 4 (both 4a and 4b) is
    now fully closed** — Block World renders real per-pixel textures on
    all three faces, on all three targets.

## Tier 5 — Particle system + timelines (large, greenfield, ~3+ sessions, last of Tiers 1-6)

100% write-only today: `action_executor.py`'s particle/emitter/timeline
`execute_*_action` methods populate `instance._particle_system`/
`instance.timeline_*`, but `game_runner.py` never reads any of it — nothing
spawns/ages/moves/draws/advances. Zero `ActionType` entries (no dead-end UI
today, just unbuilt).

- [x] **5.1 Phase 1 (desktop engine) — DONE 2026-08-15.** Per-frame update
  in `runtime/game_runner.py`: `GameInstance.update_particle_system()`
  (spawns from streaming emitters via a new shared `ActionExecutor.
  _spawn_particles` helper factored out of `execute_burst_particles_action`
  so burst/stream sample position/size/speed/direction/life identically;
  ages/moves/culls every live particle — movement mirrors
  `set_direction_speed`'s convention, 0°=right/90°=up/y grows downward) and
  `GameInstance.update_timeline()`, both called from the main loop's
  per-instance step (`game_runner.py`, right after delayed actions, before
  the step event — new "2c. PARTICLES & TIMELINE"). New
  `GameInstance.render_particles()`: sprite-typed particles blit a scaled
  copy of the sprite's first frame (looked up by name via
  `action_executor.game_runner.sprites`, same pattern `_draw_sprite` uses);
  colorless particles draw as an alpha-blended filled circle. Called from
  `render()` **before** the `if not self.visible: return` guard, so an
  invisible "particle controller" instance (a common real pattern) still
  draws its particles — confirmed this would otherwise be a real gap by
  writing the test first. Known, documented simplification: a particle
  system's own `depth` field is unused; particles draw immediately
  alongside their owning instance's position in the existing depth-sorted
  instance list, not independently re-sorted against every other instance
  in the room (there's no room-global particle layer here, only
  per-instance ones).
  **Timeline "moments" finding (audit-is-a-lead correction to this plan's
  own text): no moments/storage shape exists to investigate.** Read every
  write-side timeline handler — `timeline_index` is set to an opaque
  string never looked up anywhere; there is no Timeline resource, no
  project.json asset category, no action that attaches an action list to a
  position. The plan's premise that such a structure already existed
  write-side was wrong. Resolution: `timeline_position`/`timeline_speed`/
  `timeline_running` becoming real, per-frame-advancing, `getattr`-able
  instance state (mirrored by `test_variable`'s `scope='sel'` reading via
  plain `getattr(instance, variable, 0)`) is by itself a complete, honest
  reading of "firing whatever's scheduled" — an author reacts to a
  specific position with an ordinary `test_variable` conditional in their
  own step event, exactly how alarms are authored as ordinary object
  events rather than through a dedicated resource. Inventing a new
  Timeline resource/asset type + editor UI would be genuine new scope
  belonging to 5.2 (UI), not 5.1 (engine), and no existing action supports
  authoring one — deliberately not done here.
  Tests: `tests/test_particle_timeline_engine.py` (18 tests) — real
  `GameInstance`/`ActionExecutor` pair (not a hand-rolled harness) driven
  across simulated frames: burst age/cull, directional movement (both
  axes), size_increase floor, streaming spawn-per-frame, stream binds to
  the emitter it was armed on (not `_last_emitter_id` at spawn time),
  color + sprite rendering (real pixel assertions on a real
  `pygame.Surface`), the invisible-controller case, timeline
  advance/pause/speed-scaling/stop-resets, and a combined integration test
  driving `update_particle_system`/`update_timeline`/`step()` together.
  Suite 3036 → 3054 passed, 0 failed.
- [x] **5.2 Phase 2 (UI) — DONE 2026-08-15.** All 14 actions registered in
  `events/action_types.py`, new "Particles" category (8: create/destroy
  particle system, clear_particles, create_particle_type, create/destroy
  emitter, burst/stream particles) + 6 more in the existing "Timing"
  category (set_timeline, set_timeline_position, set_timeline_speed,
  start/pause/stop_timeline) — matches the 2026-06-05 "safe bucket"
  precedent's own pattern (one `ActionType` per runtime handler, params
  mirroring exactly what `parameters.get(...)` reads). No `multi_choice`/
  new `param_type` needed — per 5.1's finding there is no moments concept
  to build an editor for; `set_timeline`'s `timeline` param stayed a plain
  `string` (bookkeeping label, not a resource picker — there's no Timeline
  resource to pick from). Confirmed the new "Particles" category needs no
  extra registration beyond `ACTION_TYPES` itself — actions with no
  `ACTION_TO_BLOCKLY_MAP` entry take the same "include if unmapped" path
  already established for basic Audio actions (see `CLAUDE.md`), so they
  surface in the events-panel action picker without touching
  `config/blockly_config.py`'s `BLOCK_REGISTRY`; Blockly-specific block
  generation was deliberately left unwired, mirroring that same precedent.
  Tests: `tests/test_particle_timeline_action_registration.py` (22 tests
  — every action resolves in its category, full param sets match the
  runtime reads, the sprite/shape/relative/string param-type choices are
  pinned, every registered name has a real `execute_*_action` handler).
  Suite 3054 → 3076 passed, 0 failed. Not done (deliberately, separate
  follow-up): regenerating the localized wiki Full-Action-Reference pages
  (`tools/gen_action_reference.py`) to include these 14 — real but
  unrelated documentation work, same class as any other action addition.
- [ ] **5.3 Phase 3 (export parity).** HTML5/Kivy, deferred until Phase 1-2
  are proven and at least one sample uses them (match3_1 lesson: don't chase
  parity for a feature nothing uses yet).

## Tier 6 — Manifest-ify sprites in `project.json` (medium, ~1 session) — CLOSED 2026-08-15

- [x] Strip the **whole** sprite body on save (unlike objects, which
  stripped just `events` — sprites have no single risky subfield to
  isolate; small pure metadata, no pixel data).
- [x] No new loader code needed for core/runtime —
  `core/project_manager.py::_load_sprites_from_files` and
  `runtime/game_runner.py::_load_sprites_from_files` already have working
  `merge_sprite_file` logic, now actually exercised now that saves strip.
- [x] Add sprite-file loading to the three export paths that had **zero**:
  `export/base_exporter.py` (covers exe/linux/macos + Android via
  inheritance), `export/ios/ios_exporter.py` — mirror the existing merge
  pattern.
- [x] Route `export/HTML5/html5_exporter.py::encode_sprites` through a
  sprite-file merge (new `_load_sprite_files`, called before both
  `encode_sprites` and the `gameData` embed — engine.js reads sprite
  metadata straight from that embed at browser runtime too, not just the
  export-time PNG encoding). `export/Kivy/kivy_exporter.py::_export_sprite`
  needed **no** change — `KivyExporter` only ever receives `project_data`
  already merged by its caller (`base_exporter.py`/`ios_exporter.py`), never
  reloads `project.json` itself.
- [x] Mandatory round-trip test mirroring
  `tests/test_manifest_ify_objects_round_trip.py`:
  `tests/test_manifest_ify_sprites_round_trip.py` (10 tests — fresh project
  byte-identical reload, legacy embedded-only project unchanged, `.zip`
  export/import round-trip, real bundled sample `maze_1`).
- [x] **A full sprite-read-site survey (not scoped by the plan text above,
  done before implementing per this repo's audit-is-a-lead discipline) found
  6 real gaps beyond the three export paths named above**, each fixed with
  its own regression test in `tests/test_manifest_ify_sprites_export_paths.py`
  (10 tests): the HTML5 exporter had **zero** sprite merge (bigger than just
  `encode_sprites` — the whole unmerged `project_data` is embedded as
  `gameData`); `editors/room_editor/__init__.py`'s detached/floated-editor
  disk fallback; `widgets/asset_tree/asset_tree_item.py`'s object-sprite-
  thumbnail disk fallback (a *second*, separate fallback from the
  already-safe sprite-category thumbnail path); `utils/resource_packager.py`'s
  `export_object`/`export_room` (object *events* were already merged there
  from the 2026-08-14 objects work; sprites had no equivalent, so a shared
  `.gmobj`/`.gmroom` package would ship a stub with no `file_path`); and the
  trash/rollback gate in both `core/asset_manager.py::delete_asset` and
  `widgets/asset_tree/asset_operations.py`'s legacy fallback (`"sprites"` was
  missing from the `("rooms", "objects", "playgrounds")` side-file gate,
  same orphan hazard M59 already fixed for the other three types). Also
  added `thumbnail`/`image_file` to `utils/project_file_merge.py`'s
  `_SPRITE_FILE_KEYS` — both are real, read fields that were missing from
  the merge whitelist and would have silently vanished on the first
  stub round-trip. Full writeup: `TODO.md`'s "Manifest-ify objects &
  sprites" entry, 2026-08-15 addendum. Suite 3036 passed, 0 failed.

## Tier 7 — Block World big features (large, multi-part)

- [x] **7a. Jump mechanic — DONE 2026-08-15.** Desktop-engine only, matching
  the plan's own Verification section (7a is grouped with Tier 5 as a
  `GameRunner`-driven-test tier, not an export-parity one) — HTML5/Kivy
  codegen is a separate, later unit, deliberately not done here.
  Opt-in and fully backward-compatible: `enable_block_world_view` gained a
  `gravity` parameter (cells/step², default **0**), and `move_and_collide`'s
  original instant-footing behaviour (snap to ground in both directions, no
  falling — "a drop is just a step down") is **completely unchanged** for
  every project that leaves it at 0, i.e. every project that predates this
  tier. `gravity > 0` switches on real physics via two new actions:
  `apply_gravity` (bind in the **Step** event — fires every frame regardless
  of input, unlike `move_and_collide`'s usual keyboard-held binding, so
  falling continues even while no movement key is held) integrates
  `vz`/`z_layer` each step and lands cleanly (`vz` zeroed, `z_layer` clamped
  to the exact block top) once height reaches the ground below; `jump`
  (bind to a key press) gives upward velocity, but only while grounded — no
  double-jump/flying by mashing the key. `z_layer` changed from an
  always-`int()` field to a float (`renderer.py`'s `eye_z_for` no longer
  truncates) — safe because the multi-layer renderer already projects every
  block relative to continuous `eye_z`, so a fractional camera height
  mid-jump/fall renders as a smooth rise/fall with **zero other renderer
  changes needed**; world-grid raycasting is unaffected since that keys off
  x/y columns only, never `z_layer`. One more real bug found and fixed
  along the way: `move_and_collide`'s step-up gate compared the target cell
  against the ground *below* the mover, which is only correct while
  grounded — an airborne body (already above the ground) needs the gate
  compared against its own actual height instead, or a jump could be
  wrongly refused/allowed near a tall obstacle depending on what's on the
  ground far beneath it (covered by a dedicated test for both the airborne
  and grounded cases). Constants (`DEFAULT_GRAVITY=0.04`,
  `DEFAULT_JUMP_SPEED=0.35`, `TERMINAL_FALL_SPEED=-0.9` — a discrete-step
  fall-speed cap so landing detection can't tunnel through a one-layer-thick
  floor) live in `handlers.py`, freely overridden per project via the new
  action parameters. `tests/test_block_world_gravity_jump.py` (12 tests,
  real `GameRoom`/`GameInstance`/`ActionExecutor` harness matching this
  extension's own established test pattern): legacy behaviour provably
  unchanged at `gravity=0`, a full jump arc that rises then lands back
  exactly on flat ground, refused double-jump, terminal-velocity capping,
  falling off a ledge in gravity mode (no instant snap, real multi-step
  descent), step-up still instant in gravity mode, and both
  airborne/grounded cases of the step-up-gate fix. Also fixed
  `extension.json`'s `provides_actions` list (missing the 2 new action
  names — caught by an existing manifest-parity test, not assumed).
  Suite 3054 → 3088 passed, 0 failed. Not done (deliberately, per scope):
  HTML5/Kivy export codegen for `apply_gravity`/`jump`/the `gravity` param,
  and updating `block_world_1` (or a new sample) to actually demo jumping —
  same "wait for a real sample" discipline as Tier 5.3.
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

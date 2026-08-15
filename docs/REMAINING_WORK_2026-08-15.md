# Plan: everything remaining for pygm2

Written 2026-08-15, right after `docs/DEFERRED_GAPS_2026_PLAN.md`'s queue
(Tiers 1–7c) closed. That doc is done; this one is the next resume point —
a full survey of every other planning doc in `docs/` plus `TODO.md`, so a
future session has one place to start instead of re-deriving "what's left"
from scratch. Verified against current doc state, not assumed — see the
per-section sourcing below.

Sized loosely as **small** (a session or less), **medium** (1–3 sessions),
**large** (its own multi-session plan doc), or **manual QA** (not code —
needs a human/real device, can't be closed by an agent).

---

## A. Blocked on "a sample uses it first" (small–medium each)

Same deliberate pattern already used for Tier 5.3 and Tier 7a/7b/7c's export
halves: land the desktop engine + UI first, defer HTML5/Kivy codegen until a
real sample exercises the feature, so parity work isn't spent on dead
scope.

- [x] **Block World jump/gravity + inventory + protection HTML5+Kivy
  codegen — DONE 2026-08-15.** All three of Tier 7a/7b/7c's deferred export
  halves landed in one pass (they share the same `move_and_collide`/
  `place_block`/`break_block`/`enable_block_world_view` call sites on both
  targets, so splitting them into three separate passes would have meant
  re-touching the same functions three times). `apply_gravity`/`jump`/
  `set_block_protection` registered on both targets; `move_and_collide`/
  `place_block`/`break_block` made gravity/inventory/protection-aware,
  matching desktop's exact backward-compatible gating (0/off defaults =
  zero behaviour change). `eye_z_for`'s HTML5 (`bwEyeZFor`) and Kivy
  (`_bw_eye_z_for`) copies both dropped their `Math.trunc()`/`int()`
  truncation to match desktop's float `z_layer`, needed for a smooth
  jump arc — the existing multi-layer renderers on both targets already
  project every block relative to continuous eye height, so (as on
  desktop) this needed zero other renderer changes. HUD builders on both
  targets gained an optional `counts` param.
  Tests: `tests/test_kivy_block_world_jump_inventory.py` (17 tests) drives
  the real generated `_bw_apply_gravity`/`_bw_jump`/`_bw_place_block`/
  `_bw_break_block`/`_bw_set_block_protection` methods through the
  established stub-Kivy execution harness — a real jump arc, refused
  double-jump, falling off a ledge without an instant snap, break/place
  inventory round-trips, and protection gating, all executed, not just
  string-matched. `tests/test_html5_block_world_jump_inventory.py`
  (9 tests): structural checks (no JS engine available) plus one **exact
  numeric parity** test that reimplements the JS gravity formula in Python
  and drives it step-for-step against the real desktop
  `execute_apply_gravity_action`/`execute_jump_action` handlers, asserting
  identical `z_layer`/`vz` at every step of a full jump arc (mirrors
  `test_raycast_export_parity.py`'s established two-tier HTML5 approach).
  Suite 3117 → 3143 passed, 0 failed.
- [x] **Particle system + timeline HTML5/Kivy codegen (Tier 5.3) — DONE
  2026-08-15. Section A is now fully closed.** All 14 actions registered on
  both targets. **HTML5**: `case` branches added directly to `executeAction`
  (these are core actions, not an extension, so no `registerExtensionAction`
  involved); a new module-level `spawnParticles()` helper (mirrors
  `ActionExecutor._spawn_particles`) shared by `burst_particles` and the
  per-frame streaming-emitter spawn in the new `GameObject.
  updateParticleSystem()`; `updateTimeline()` advances position; `render
  Particles()` draws sprite- or color-circle particles via Canvas2D, called
  from `onDraw` **before** the visibility-gated `render()` (invisible
  particle-controller parity, same as desktop). Both update methods run
  every frame from the room step loop's new "3d. Particles & timeline"
  phase, unconditional on step-event authoring. **Kivy**: same 14 actions
  as real `GameObject` methods (`create_particle_system`, `burst_particles`,
  `set_timeline`, etc. — multi-field/dict logic emits a single method call
  from codegen, mirroring the established `_draw_minimap` precedent, not
  inline expressions); `render_particles()` uses its own
  `InstructionGroup` on `self.canvas.after` (**not** `self.canvas`, which
  `_redraw_frame` clears every sprite-animation frame — the same reason
  `_dq_group` already lives in `.after`). Every method lives inside the
  `.format()`-templated `BASE_OBJECT_CODE` string, so every literal
  `{`/`}` (dict/set literals) is doubled throughout.
  Tests: `tests/test_kivy_particle_timeline_export.py` (20 tests) imports
  the REAL generated `objects/base_object.py` under the established
  stub-kivy harness (mirrors `test_kivy_parity_batch.py`'s
  `test_base_object_helpers_behave`) and drives real spawn/age/cull,
  streaming, and timeline advance/pause/stop — not a reimplementation.
  `tests/test_html5_particle_timeline_export.py` (10 tests): structural
  checks plus an exact numeric parity test reimplementing the deterministic
  half of the JS aging formula (fixed speed/direction, no RNG spread) and
  driving it step-for-step against the real desktop
  `update_particle_system`, matching Block World's own two-tier HTML5
  approach. Suite 3143 → 3173 passed, 0 failed.

## B. Small, narrow, unscheduled fixes

- [x] **Kivy camera FBO is build-time-only — DONE 2026-08-15.** Extracted
  the constructor's Fbo/`_view_group` construction block into a new
  `_ensure_views_fbo()` method (a no-op once `self._fbo` already exists);
  `set_views_enabled(True)` now calls it when the room started without
  views, then runs `update_views()`/`_render_views()` for an immediately
  correct frame — previously `self._fbo` stayed permanently `None` and the
  camera silently never rendered. Known, documented limitation left as-is
  (matches the item's own "no known blocked use case yet"): retrofitting
  doesn't clean up the room's original non-views rendering path (the
  `canvas.before` background + child-widget instances added at
  construction for a non-views room), so a room that starts non-views and
  is later switched to views risks both paths drawing at once — full
  correctness there would mean tearing down the non-views path too, out of
  scope for what was asked (fixing the FBO allocation gap specifically).
  `tests/test_kivy_views_fbo_retrofit.py` (5 tests, reusing
  `test_kivy_views.py`'s own stub-kivy harness via sibling import): a
  non-views room starts with `_fbo is None`, `set_views_enabled(True)`
  builds a real Fbo/view_group and actually renders without crashing,
  repeated enable/disable toggles reuse the same Fbo (no leak), and the
  legacy construction-time path (room already `views_enabled` at export)
  is unchanged byte-for-byte. Suite 3173 → 3178 passed, 0 failed.
- [x] **`TODO.md` doc-hygiene — DONE 2026-08-15.** Views/camera section
  header changed from "IN PROGRESS" to a struck-through "DONE," with its
  "Residual limitation" paragraph updated to point at the FBO fix above
  instead of describing a now-closed gap. The pt `WelcomeTab` entry struck
  through and marked done, with a short pointer to `DEFERRED_GAPS_2026_PLAN.md`
  Tier 2.1 (which actually fixed it 2026-08-15) instead of the stale
  "not yet fixed" wording.
- [x] **`docs/EXPORT_SYSTEM_STATUS.md` reconciliation — DONE 2026-08-15,
  turned out to need almost nothing.** Re-reading the file found its
  existing 2026-07-19 banner already does the "wishlist, not backlog"
  framing this plan called for — it explicitly says to treat the body's
  checkboxes as historical and already buckets the open items into
  deferred-features / manual-QA / docs. Only real gap: nothing pointed a
  reader at the freshest version of that same list. Added one banner line
  cross-referencing this doc's own Section D (wishlist) and Section C
  (manual QA) as where to check first.

## C. Manual QA — not code work, needs a human or real device

Real, standing gaps this session (or any agent session) structurally cannot
close:

- **Kivy/Android on-device test.** The stub-kivy execution harness covers
  logic, not the real Kivy/GL layer or a real APK build+install+run.
- **HTML5 embedded-Pyodide real-browser verification.** Everything
  verifiable without a browser is verified (Node structural checks, byte-
  fidelity round-trips, one ad hoc Playwright/Chromium spike during the
  HTML5 `execute_code` work) — a real browser calling the real
  `loadPyodide()` end-to-end has never been watched.
- **Raycast samples' shape changes, never watched rendering.** Standing
  caveat repeated across several 2026-07-2x session notes: nobody has
  watched `raycast_3`'s corner-overlay HUD, `raycast_4`'s letterboxed
  viewport + DOOM status bar, or `plateforme_3` after its depth-order export
  fix actually render in a browser or on Android. Structure/codegen/parity
  numbers are all verified; pixels are not.
- **pt/ja/zh visual spot-check beyond the Preferences dialog.** The
  offscreen-`QApplication` + `QWidget.grab()` screenshot technique
  (established 2026-08-10) has only been pointed at one dialog. Extending it
  to the main window and a few more dialogs per language is cheap per
  screenshot but open-ended in aggregate — pick a handful of the busiest
  dialogs (Room Editor, Object Editor, Export dialog) rather than trying to
  cover everything.
- **Published GitHub wiki spot-check.** Nobody has viewed the live pages on
  github.com since the 2026-07-29 accuracy/translation sweep — worth
  confirming accents render (not mojibake), language-switcher banners
  resolve, and accented-header ToC anchors land correctly.
- **Device/browser matrix from `EXPORT_SYSTEM_STATUS.md`**: antivirus false-
  positive scan on the Windows `.exe`, mobile-browser/touch testing for the
  HTML5 export. Same category as the two bullets above — real, but needs
  hardware/services this environment doesn't have.

## D. Open-ended export wishlist — aspirational, not scheduled

From `docs/EXPORT_SYSTEM_STATUS.md`'s reconciliation banner. No plan doc, no
tier, no sizing anywhere — listed here so it's not lost, not because it's
imminent:

HTML5: external-asset loading (today everything embeds inline), a PWA
manifest, service workers for offline play. Desktop `.exe`: code signing,
version-info embedding, an auto-updater, crash reporting, analytics. Kivy/
mobile: debug vs. release export presets, in-app purchases, mobile ads, push
notifications, cloud saves. Further out still: Steam/itch.io/console export
targets. None of this should be picked up without an explicit ask — it's
the kind of scope a school-focused educational IDE may never need.

## E. Translation completeness gap (real, unbounded until swept)

Noted but not chased during the 2026-08-10 Extensions-tab i18n fix: the six
"older maintained" languages (de/es/fr/it/ru/sl/uk minus fr, which ships
monolithic) were never verified at 100% completeness the way pt/ja/zh were
built to be. Confirmed concretely for German alone: `pygm2_de_core.ts` +
`_editors.ts` carry **151** `type="unfinished"` empty-translation entries
between just those two split files, with likely similar-scale gaps in the
other five languages, uncounted. Real user-facing gap (untranslated strings
silently fall back to English), but the size is unknown until someone runs
the same completeness count `scripts/gen_translation_ts.py`'s pt/ja/zh work
established against each of the six. Natural next step: run the count
first (cheap), then decide whether to schedule filling them as a tier.

## F. Large — each needs its own future planning session, not this doc

Explicitly named as too large for a "small unit, one commit" queue like
`DEFERRED_GAPS_2026_PLAN.md`. Do not start any of these from a resume-state
doc; each deserves its own `docs/<NAME>_PLAN.md` the way `VOXEL_WORLD_PLAN.md`
and `RAYCAST_2_5D_PLAN.md` got one.

- **`docs/POST_1_0_REFACTOR.md` — splitting the four giant files.** Not
  started. `runtime/action_executor.py` (5,593 lines), `runtime/game_runner.py`
  (4,680), `core/ide_window.py` (4,153), `editors/object_editor/
  object_events_panel.py` (1,880). The doc already has a full proposed
  split-target module list per file, a deliberate difficulty-ascending
  order (events panel → ide_window → game_runner → action_executor, each
  behind a stabilization pause), an explicit proof methodology (offscreen-Qt
  harness diffing observable state against pre-refactor HEAD, one cluster
  per commit — this repo's standing audit discipline), and abort criteria.
  Its own estimate: **~3 months of focused work** including stabilization
  windows. Five smaller "companion cleanups" (consolidate the 3-copy
  `ACTION_ALIASES` table, delete the dead `CollisionMixin`, prune audit-era
  debug comments, demote noisy `logger.info` calls, cross-check
  `docs/CODE_AUDIT.md` §4) are listed as worth doing alongside it, not
  requiring the full refactor to start.
- **Block World Tier 7d — in-IDE visual world editor.** No `editors/`
  scaffolding exists for it at all; called out in
  `docs/DEFERRED_GAPS_2026_PLAN.md` as "the largest item in the whole
  queue — larger than Tier 5 [particles/timelines, itself sized 3+
  sessions]." `VOXEL_WORLD_PLAN.md`'s own Phase 3 notes add: paint blocks in
  3D inside the Room Editor, mirroring the Room Editor's existing tile
  painter; a 2026-08-13 design note already leans toward `QUndoStack`/
  `QUndoCommand` (matching `editors/room_undo_commands.py`) over any global
  engine-level edit/play-mode toggle, since whether a player can break
  blocks is already just "whether the author bound `break_block` to an
  input" — no separate mode concept needed.
- **Block World Tier 7e — procedural/infinite terrain.** World storage today
  is a single in-memory sparse dict per room, no chunking/streaming.
  `VOXEL_WORLD_PLAN.md` deliberately scoped this OUT up front (Phase 1):
  "infinite chunk streaming is a much bigger engineering problem (chunk
  loading/unloading, seed-based generation, LOD) with limited teaching
  payoff" for bounded, author-sized worlds. Sized as "comparable to a second
  `VOXEL_WORLD_PLAN.md`."
- **Wiki per-tutorial-step screenshots** (`docs/WIKI_COMPLETENESS_PLAN_2026-08-11.md`'s
  one open item). Needs up to 5 more scratch sample projects (one matching
  each of the 6 build-along tutorials' own taught object names — Phase 1's
  existing screenshots all come from one `plateforme_3` copy whose French
  names don't match the tutorials' English-named samples, so they can't be
  reused) plus per-step capture through each. Sized as "comparable to all of
  Phase 1 combined, for lower-traffic pages" — deliberately deferred in
  favor of finishing translation instead.
- **Full crafting system.** Explicitly split out of Tier 7c's inventory-with-
  counts work: no recipes, no UI, zero scaffold exists. Needs its own
  dedicated planning pass if wanted.
- **LAN multiplayer.** A 2026-05-02 git stash holds unfinished work, blocked
  on missing `runtime/network/` source files (only stale `.pyc` remain).
  Decided 2026-08-08 to rebuild as a folder extension (matching the
  raycast/block-world pattern) rather than touch core — the stash itself is
  not recoverable as a starting point, this would be a fresh build. See the
  `multiplayer-network-stash` memory entry for the full decision record.

---

## Suggested order, if picking this up fresh

1. **Section E's count-first step** (run the completeness sweep across the
   six older languages) — cheap, and determines whether a real translation
   gap needs scheduling at all.
2. **Section B** — the two/three small fixes, an easy single session.
3. **Section A** — build the combined jump+inventory+protection Block World
   sample, which unlocks motivating all three export-parity units at once
   rather than three separate low-context passes.
4. **Section C** — opportunistic, whenever there's real device/browser
   access available; not blocking anything else.
5. **Section F** — pick ONE, write it its own dedicated plan doc first
   (mirroring `VOXEL_WORLD_PLAN.md`'s shape), then work it the same
   one-commit-per-unit way this repo already does everything else. Don't
   start code before that doc exists — these are all large enough that
   skipping the planning step is how a "small first step" quietly turns
   into an unreviewable multi-thousand-line change.

Section D is intentionally last/optional — pick up only on explicit ask.

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
- [~] **pt/ja/zh visual spot-check beyond the Preferences dialog — extended
  2026-08-15, still open-ended.** `NewProjectDialog` screenshotted (the same
  offscreen-`QApplication` + `QWidget.grab()` technique) across pt/ja/zh:
  all three render cleanly, no mojibake, no truncation, no leftover English
  in any of the app's own strings. One real but out-of-scope-here finding:
  the dialog's OK/Cancel button box falls back to **Qt's own base
  translations** (`qtbase_<lang>.qm`), not this app's `.ts` catalog — ja's
  Qt install had one bundled (`キャンセル`), pt/zh's didn't (`Cancel` stayed
  English). This is a Qt-framework-string gap, not an app-string one, so it
  sits outside everything this repo's whole i18n effort has targeted so
  far; would need bundling additional Qt locale data (a packaging
  decision) to close, not a code fix. Two dialogs now checked (Preferences,
  New Project) across the three newest languages; the main window and the
  rest of the busiest dialogs (Room Editor, Object Editor, Export dialog)
  remain unchecked — still genuinely open-ended, pick up opportunistically.
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

**Reviewed 2026-08-15, deliberately not implemented.** Several of these
(in-app purchases, mobile ads, push notifications, analytics, crash
reporting) are product/business/data-practice decisions for software used
by children, not well-defined engineering tasks — there's no spec here for
what gets monetized, what data gets collected, or what consent flow would
be needed, and guessing at any of that would be the wrong kind of
"proceeding without asking." A blanket instruction to work through a
numbered list of sections is not the same as an explicit ask for any one
specific item on this particular list; each of these needs its own
deliberate go-ahead naming the item, not a pass-through. The purely
technical, lower-stakes items here (code signing, version-info embedding,
PWA manifest, export presets) are more plausibly pickup-able later, but
still have zero sizing/design done — genuinely start from scratch, not a
resume point.

## E. Translation completeness gap — [x] ALREADY CLOSED, re-verified 2026-08-15

**This section's own premise was stale.** It was written from a CLAUDE.md
note dated 2026-08-10 describing an unclosed gap (151 empty
`type="unfinished"` entries in German alone, likely similar elsewhere,
"unbounded until someone runs the count"). Running that count first, per
this section's own prescribed next step, immediately surfaced
`docs/I18N_UNFINISHED_2026-08-10.md` — a full plan doc, already marked
**"CLOSED — all 7/7 done: fr, de, it, ru, sl, uk, es,"** from later the
same day the gap was found. 1101 real empty entries across all seven
languages (not just the six this section named — es was included too) were
filled with real, non-machine-copied translations and verified via a live
`QTranslator` per language (`tests/test_i18n_unfinished_{de,es,fr,it,ru,sl,uk}.py`,
84 tests total, all passing).

**Re-confirmed independently 2026-08-15** (not just trusting the doc's own
claim): grepped every shipped `.ts` file for `de/es/fr/it/ru/sl/uk` for both
`<translation type="unfinished"></translation>` (empty, closing-tag form)
and `<translation type="unfinished"/>` (empty, self-closing form) —
**zero hits across all 7 languages.** The 92 remaining non-empty
`type="unfinished"` entries found in a few `_editors`/`_dialogs` files (and
`es`/`fr`) all carry real translated text; compiled a fresh `.qm` from one
with `lrelease` and confirmed via a live `QTranslator` that Qt's
"unfinished" flag has zero effect on compilation or runtime resolution —
it's a Linguist review-workflow marker, not an untranslated-string marker,
so these are not a gap at all. `CLAUDE.md`'s original note corrected in
place to point at the closure instead of describing a gap that no longer
exists.

## F. Large — each needs its own future planning session, not this doc

Explicitly named as too large for a "small unit, one commit" queue like
`DEFERRED_GAPS_2026_PLAN.md`. **Every item below now has its own dedicated
plan doc (written/refreshed 2026-08-15)** — do not start implementation
from THIS doc; open the linked plan first and work from it.

- [x] **`docs/POST_1_0_REFACTOR.md` — splitting the four giant files.**
  Already had a full plan (split-target module list per file, a
  difficulty-ascending order, an offscreen-Qt proof methodology, abort
  criteria, ~3-months-of-focused-work estimate) — **refreshed 2026-08-15**:
  line counts updated (all four files have grown further; current sizes
  2,111 / 5,295 / 5,854 / 6,421), and two stale claims corrected in place —
  `runtime/collision_system.py` (the dead `CollisionMixin` the plan
  described deleting) was already deleted 2026-06-09, and a *new*
  companion-cleanup finding was added: `runtime/action_handlers/
  particle_handlers.py` is now confirmed fully dead code, shadowed by
  `ActionExecutor`'s own `execute_*_action` methods.
- [x] **Block World Tier 7d — in-IDE visual world editor.**
  **UPDATE (2026-08-15, same day): fully implemented, all four phases.**
  `docs/BLOCK_WORLD_EDITOR_PLAN.md`. `editors/block_world_editor/`: a
  QWidget fly-camera view (reusing `widgets/thymio_playground.py`'s
  pygame-in-Qt plumbing verbatim), left-click place / right-click break
  routed through a `QUndoStack` (`editors/room_undo_commands.py`'s exact
  shape), save/load to a per-room `blocks/<room>.json` sibling file, a
  "🧱 Block Edit" Room Editor toolbar entry, and a Clear World action.
  Found and fixed a real PySide6/shiboken segfault along the way (a
  `destroyed`-signal connection creating a teardown-order hazard) — see
  the plan doc's own status header for the full record.
- [x] **Block World Tier 7e — procedural/infinite terrain.**
  **UPDATE (2026-08-15, same day): fully implemented, all four phases.**
  `docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`. Chunked storage
  (`CHUNK_SIZE=16`, a two-level per-chunk + merged column-index cache),
  a hand-rolled deterministic value-noise heightmap (no cross-target
  determinism requirement, per the plan's own recommendation), seed-based
  generation on all three targets (desktop `state.py`, `export_html5.js`,
  `export_kivy.py` — the latter two skip the chunked-storage/eviction
  rework as a documented scope cut, since an exported game has no
  long-lived IDE session to bound memory for), and the
  `samples/block_world_2` sample demonstrating real boundary-free
  exploration with zero pre-authored world data.
- [x] **Wiki per-tutorial-step screenshots.** New plan:
  `docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md`. Confirmed (not assumed) that
  **all six** tutorials need from-scratch scratch projects, not just
  Platformer — checked `Tutorial-Maze.md`'s object names directly against
  the bundled `maze_1` sample and found they don't match either, the same
  problem already found for Platformer. Reuses Phase 1's proven headless-
  capture technique and its one hard-won landmine (the Welcome tab's
  recent-projects privacy leak); the genuinely new work is scripting the
  IDE through each tutorial's full authoring sequence programmatically.
  Recommends proving the approach on one (shortest) tutorial completely
  before committing to it for the other five.
- [x] **Full crafting system.** Explicitly split out of Tier 7c's
  inventory-with-counts work: no recipes, no UI, zero scaffold exists.
  Still genuinely needs its own dedicated planning pass — not written yet;
  smaller and less urgent than the other four, deliberately last.
- [x] **LAN multiplayer.** New plan: `docs/MULTIPLAYER_LAN_PLAN.md`. The
  2026-05-02 git stash (`stash@{0}`) is confirmed still present and its
  exact diff read in full — a real, working vertical slice, reusable as a
  functional spec even though it can't be reapplied directly (`runtime/
  network/`'s source is unrecoverable, and it bakes networking straight
  into `GameRunner` rather than as a folder extension). **Real
  prerequisite surfaced**: `runtime/extension_hooks.py` has no per-frame
  "run every frame regardless of authored actions" hook today — only a
  room-renderer hook — and multiplayer's broadcast/apply-inbound needs
  exactly that, so Phase 0 of this plan is building that hook generically
  (useful to future extensions too) before any networking code. Also flags
  a real design tension the stash's own CLI-flag approach only partly
  solves: every other extension is configured by design-time actions, but
  "who hosts, who joins" is inherently a per-launch player choice — laid
  out three ways to reconcile it with a recommendation.
  **UPDATE (2026-08-15, same day): fully implemented, all four phases.**
  This checkbox originally meant only "the plan is written" — it now also
  means the plan was executed end to end the same session: the generic
  frame-update hook (Phase 0), the `extensions/multiplayer_lan/` folder
  extension with a TCP/JSON-lines wire protocol (Phase 1), the
  `set_network_mode` action plus `run_game.py --net-host`/`--net-client`
  CLI flags (Phase 2), and the `multiplayer_lan_1` sample (Phase 3). See
  `docs/MULTIPLAYER_LAN_PLAN.md`'s own per-phase DONE notes for the full
  record. Only the manual two-window visual playtest remains (needs a
  real display, out of scope for automation).

---

## Status as of 2026-08-15 (second pass) — where to actually start next

Sections A, B, and E are fully closed (worked the same day this doc was
written). Section D stays intentionally last/optional — pick up only on
explicit, per-item ask, never a pass-through of a broader instruction.
Section C's automatable pieces are done; what's left there is genuinely
manual and opportunistic.

**Section F now has a dedicated, ready-to-work-from plan for four of its
five items** (`docs/POST_1_0_REFACTOR.md`, `docs/BLOCK_WORLD_EDITOR_PLAN.md`,
`docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`,
`docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md`, `docs/MULTIPLAYER_LAN_PLAN.md`) —
the "write the plan first" step this doc used to tell a future session to
do is done. The full crafting system is the one Section F item still
without a plan doc (smaller and lower-priority than the other four; write
one when it's actually next in line, not speculatively).

**Recommended next step given all of this**: pick ONE plan from Section F
based on what's actually wanted next (they're independent of each other
except where a plan says otherwise — Block World's two plans have an
explicit sequencing note between them), open its doc, and start working
its phase breakdown the same one-commit-per-unit way every other tier in
this repo's history has been worked. Each of the five plans already names
its own first concrete phase — start there, not by re-deriving scope from
scratch.

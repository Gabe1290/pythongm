# Project status — where things actually stand

**Read this first.** Written 2026-09-02, after a full audit of every
planning/audit/status document that had accumulated in `docs/` since
early 2026 (~50 files). Each doc's own status claim was verified against
its body and against current code, not just trusted — several were
stale. The ~55 confirmed-closed docs that audit found were **deleted**
the same day (not archived) — their content is fully captured either
here, in `TODO.md`, in `CHANGELOG.md`, or in `CLAUDE.md`'s session-note
history, so keeping them around was pure clutter. Full history (every
file, byte-for-byte, at the commit that removed it) is still in `git
log` if anyone ever needs the original text.

**One accepted trade-off from the deletion:** ~140 comments across the
live codebase (`extensions/`, `export/`, `runtime/`, several test
docstrings) point at specific deleted docs for design rationale — e.g.
`extensions/raycast_2_5d/__init__.py` used to say "see
`docs/RAYCAST_EXTENSION_PLAN.md`." Those comments now name a file that
no longer exists on disk (still recoverable via `git log -- docs/
<name>.md`). Rewriting all ~140 was judged out of scope for a docs
cleanup — the comments' own surrounding prose still explains the *why*
inline in the vast majority of cases; only the "go read more" pointer is
stale. Fix a given one in passing if you're already editing that file,
not as a standalone sweep.

---

## Currently open work

This is the complete list. Everything else that used to be tracked in
`docs/` is done and has been deleted.

1. **Multiplayer LAN — Phases 7–8.** `docs/MULTIPLAYER_LAN_V2_PLAN.md`
   is the one plan doc with real, checked-out-but-unchecked work: Phase 7
   (HTML5 export parity for multiplayer — a hand-rolled WebSocket
   listener on the desktop host, the browser client, a Kivy no-op
   placeholder, wiki pages) and Phase 8 items 8.2–8.7 (`reseau_2`/`_3`/
   `_4` samples, `tools/smoke_run_multiplayer.py` + CI wiring, graceful
   host-loss handling, closing the doc). Plus a standing manual-QA list
   (two real machines on a school LAN, a real firewall prompt, HTML5
   export joining from a Chromebook) that needs real hardware, not code.
   This is the most concrete, ready-to-pick-up item in the whole
   backlog — the doc names its own next phase. **Kept** (not deleted —
   this is live work).

2. **`docs/POST_1_0_REFACTOR.md` — splitting the four largest files.**
   Zero progress (confirmed: no DONE/checkbox markers anywhere in the
   doc, and the four target files have only grown since it was written).
   Estimated ~3 months of focused work. Real, large, genuinely
   untouched — needs a dedicated session (or several) when there's an
   explicit appetite for it; not a quick pickup. **Kept.**

3. **`docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md`.** Confirmed "not started"
   in its own header, and nothing since mentions it being picked up.
   Scoped and ready to work from, but explicitly flagged (in the
   now-deleted `DEFERRED_GAPS_2026_PLAN.md`'s own closing section) as
   "pick up only on an explicit ask" — low value relative to its effort,
   not neglected. **Kept.**

4. **Full crafting system for Block World.** No plan doc exists yet.
   Explicitly split out of the inventory work as its own future item,
   smaller and lower-priority than the other three — write a plan when
   it's actually next in line, not speculatively.

5. **`TODO.md`'s own two small leftovers** (already tracked there, not
   duplicated here): the Block World renderer's remaining fps gap
   (deliberately parked in favor of `sky_strike_1`, not neglected — see
   TODO.md's "Block World renderer" section), and a low-priority
   asset-type-registration formalization note with no current asset type
   actually affected by its absence.

### Standing manual-QA backlog (not code work — needs a human/real device)

Consolidated from what used to be repeated caveats scattered across a
dozen now-deleted docs:

- Kivy/Android on-device test (real APK install/run — the stub-kivy
  harness covers logic, not the real GL layer).
- HTML5 embedded-Pyodide real-browser verification (`loadPyodide()`
  end-to-end in an actual browser).
- Raycast samples (`raycast_3`/`raycast_4`) and `plateforme_3`'s
  depth-order fix, never watched actually rendering in a browser or on
  Android.
- pt/ja/zh visual spot-check beyond the Preferences + New Project
  dialogs (main window, Room/Object Editor, Export dialog unchecked).
  One known Qt-framework-string gap already found (OK/Cancel button box
  falls back to `qtbase_<lang>.qm`, not this app's catalog) — a
  packaging decision, not a code fix.
- Published GitHub wiki spot-check (accents, language-switcher banners,
  ToC anchors) — not viewed live since the 2026-07-29 sweep.
- `docs/PLATFORM_DISPLAY_CHECKLIST.md` — the standing, currently-blank
  Linux/macOS/Windows manual pass. Use this checklist when picking up
  any of the above rather than inventing a new one.
- Antivirus false-positive scan on the Windows `.exe`; real mobile-
  browser/touch testing for HTML5 exports.

---

## What was deleted, and why it's safe

57 files removed 2026-09-02 (all confirmed closed against their own body
+ current code before deletion). Grouped by area — this is the
permanent record of what used to be tracked, in case anyone goes looking
for "wasn't there a doc about X":

- **Meta surveys**: the previous two "everything remaining" registries
  (`DEFERRED_ITEMS_PLAN.md` — all 13 items done; `DEFERRED_GAPS_2026_PLAN.md`
  — all 7 tiers done; `REMAINING_WORK_2026-08-15.md` — the prior version
  of this doc, all its named plans done or superseded by the entries
  above).
- **Code audits** (three successive generations — `CODE_AUDIT.md`,
  `LATENT_BUG_AUDIT_2026-06-03.md`, `FULL_AUDIT_2026-06-11.md` — plus
  `EXPORT_AUDIT_2026-07.md` and `EYEBALL_FIXES_2026-08-16.md`): every
  confirmed finding fixed and tested; `CLAUDE.md`'s "Audit-cleanup
  history" section keeps the methodology notes worth reusing.
  `FULL_AUDIT_2026-06-11.md` was the definitive 111/111-closed pass.
- **Export system**: `EXPORT_SYSTEM_STATUS.md`, `EXPORT_POLISH_PLAN.md`
  (done except a deliberately-skipped auto-updater),
  `GMK_IMPORTER_HARDENING_PLAN.md` (`treasure`/`maze_4` both back in the
  bundled samples), `web_port_plan.md` (2026-04-30, speculative
  "browser-native IDE port" sketch, never started — its core premise,
  closing the `engine.js`/desktop parity gap, is now moot per
  `tests/test_export_feature_matrix.py`).
- **Extensions**: `VOXEL_WORLD_PLAN.md` (the origin plan for what
  shipped as Block World), `BLOCK_WORLD_EDITOR_PLAN.md`,
  `BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`, the whole raycast/2.5D arc
  (`RAYCAST_2_5D_PLAN.md`, `RAYCAST_2_SAMPLE_PLAN.md`,
  `RAYCAST_HUD_PLAN.md`, `RAYCAST_DOOM_HUD_PLAN.md`,
  `RAYCAST_MINIMAP_PLAN.md`, `RAYCAST_EXTENSION_PLAN.md`),
  `extension_compat_2_0/PLAN.md` (+ its `compat_demo.py`/
  `project_2_0.json` fixtures — format guard shipped as v1.1.2),
  `MULTIPLAYER_LAN_PLAN.md` (the v1 spectator-only plan; v2 above is
  the live doc).
- **Asset/project management**: `ASSET_MANAGER_PLAN.md`,
  `CLEAN_PROJECT_PLAN.md` — both done, all tiers, including the shared
  Trash mechanism.
- **i18n / translations**: `I18N_CLEANUP_2026-08-06.md`,
  `I18N_UNFINISHED_2026-08-10.md`, `JA_ZH_I18N_PLAN.md`,
  `I18N_SAMPLE_GUIDES_2026-07-15.md`,
  `TRANSLATION_CATALOG_CORRUPTION_2026-08-08.md`,
  `TUTORIALS_I18N_PLAN.md`, `AI_SLOP_CLEANUP_2026-08-06.md`,
  `WIKI_COMPLETENESS_PLAN_2026-08-11.md` — all closed (pt/ja/zh at
  1369/1369 strings, 1101 previously-empty translations filled across
  de/es/fr/it/ru/sl/uk, the wiki screenshot/split/accuracy pass done).
- **Views/camera**: `VIEWS_SAMPLES_PLAN.md` — done, all 3 export
  targets.
- **Early implementation-completion reports** (2026-01-11 to
  2026-01-14, predate this repo's "plan doc + TODO.md registry"
  convention entirely — one-off "✅ COMPLETED" reports superseded as a
  *reference* by the generated wiki action pages,
  `tools/gen_action_reference.py`): `ALARM_SYSTEM_IMPLEMENTATION.md`,
  `CONTROL_FLOW_ACTIONS_IMPLEMENTATION.md`,
  `DRAWING_ACTIONS_IMPLEMENTATION.md`,
  `DRAW_LINE_SPRITE_IMPLEMENTATION.md`, `KIVY_EXPORTER_COMPLETION.md`,
  `MOVEMENT_ACTIONS_IMPLEMENTATION.md`,
  `ROOM_CONFIGURATION_IMPLEMENTATION.md`,
  `ROOM_LIFECYCLE_IMPLEMENTATION.md`, `THYMIO_ACTIONS.md`,
  `THYMIO_COMPLETE.md`, `THYMIO_EVENTS.md`,
  `THYMIO_GAMERUNNER_INTEGRATION.md`, `THYMIO_IMPLEMENTATION_STATUS.md`,
  `THYMIO_PHASE_2_COMPLETE.md`, `THYMIO_PHASE_4_COMPLETE.md`,
  `THYMIO_SIMULATOR.md`.
- **GMK-import playtest records** (historical, tied to the closed
  importer-hardening pass): `maze_1_testing_pass.md`,
  `maze_2_testing_pass.md`, `maze_3_testing_pass.md`,
  `maze_4_testing_pass.md`, `treasure_testing_pass.md`.

---

## Not part of this cleanup — living reference material, not plans

Left untouched; these aren't trackers, they're current documentation:
`README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CLAUDE.md` (the session
log — historical narrative; its own stale doc-path mentions inside past
session notes weren't rewritten, same reasoning as the code-comment
trade-off above), `docs/BUILDING.md`, `docs/ANDROID_EXPORT.md`,
`docs/EXPORT_TESTING_GUIDE.md`, `docs/ASSET_LICENSES.md`,
`docs/test_checklist.md` (+`.fr.md`), `docs/TESTING_CHECKLIST.md`,
`docs/TESTING_PRESET_CHECKLIST.md`, `docs/blockly_editor_test_checklist.md`,
`docs/PLATFORM_DISPLAY_CHECKLIST.md`, the `docs/USER_MANUAL*.md` /
`docs/FLYER*.md` language sets, and `docs/session-notes/*.md` +
`docs/SESSION_NOTES.md` (the append-only session log).

`TODO.md` stays the registry for small, feature-level deferred items —
this doc is for the handful of larger initiatives and for knowing, at a
glance, what's live vs. done.

## Discipline for future doc-writing

A plan doc's top-of-file Status line is a claim, not ground truth —
three were found stale during this audit (saying "not started" on work
that had actually shipped) before being deleted. When a plan doc is
truly finished: fold anything worth keeping into `TODO.md`,
`CHANGELOG.md`, or a `CLAUDE.md` session note, then delete the plan doc
rather than letting it sit as unverified "maybe still relevant" clutter.
Only keep a doc alive past its own completion if it's genuinely living
reference material (see the section above), not a snapshot of one
session's work.

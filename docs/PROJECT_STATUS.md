# Project status — where things actually stand

**Read this first.** `docs/` has accumulated ~50 planning/audit/status
documents since early 2026. This doc is the map: what's genuinely still
open, and where everything else lives. Written 2026-09-02 after a full
audit of every doc in `docs/` (each doc's own status line was verified
against current code, not just trusted at face value — several were
stale, corrected in place; see "Corrections made" below).

**Why the docs weren't moved or deleted:** the closed plan docs are
referenced by design-rationale comments in ~140 places across the live
codebase (`extensions/`, `export/`, `runtime/`, and many test docstrings
— e.g. `extensions/raycast_2_5d/__init__.py` points readers at
`docs/RAYCAST_EXTENSION_PLAN.md` for context). Relocating those files
would turn every one of those comments into a dangling reference for no
real benefit — the fix here is a map, not a move.

---

## Currently open work

This is the complete list. Everything else in `docs/` is closed.

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
   backlog — the doc names its own next phase.

2. **`docs/POST_1_0_REFACTOR.md` — splitting the four largest files.**
   Zero progress (confirmed: no DONE/checkbox markers anywhere in the
   doc, and the four target files have only grown since it was written).
   Estimated ~3 months of focused work. Real, large, genuinely
   untouched — needs a dedicated session (or several) when there's an
   explicit appetite for it; not a quick pickup.

3. **`docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md`.** Confirmed "not started"
   in its own header, and nothing in `CLAUDE.md`/`TODO.md` mentions it
   being picked up since. Scoped and ready to work from, but explicitly
   flagged (in `docs/DEFERRED_GAPS_2026_PLAN.md`'s own closing section)
   as "pick up only on an explicit ask" — low value relative to its
   effort, not neglected.

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

Scattered across a dozen docs as repeated caveats; consolidated here so
it's one list instead of a dozen:

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

## Index — everything else, and why it's closed

Every doc below has its own status line confirming closure (verified,
not assumed, before being listed here). Grouped by area; each is a
historical record, not a live task list.

**Meta / superseded surveys** — read `docs/PROJECT_STATUS.md` (this
doc) instead:
- `docs/REMAINING_WORK_2026-08-15.md` — the previous version of this
  doc. All its Section F plans now have their own dedicated docs
  (listed above or below); Sections A/B/E fully closed.
- `docs/DEFERRED_ITEMS_PLAN.md` — all 13 items done (its own top-of-file
  "planned, not started" banner was stale — corrected in place).
- `docs/DEFERRED_GAPS_2026_PLAN.md` — all 7 tiers `[x]`.

**Code audits** (three generations; each superseded the last —
`docs/FULL_AUDIT_2026-06-11.md` is the most complete and final one):
- `docs/CODE_AUDIT.md` (2026-05, pre-1.0, §0–§3 closed).
- `docs/LATENT_BUG_AUDIT_2026-06-03.md` (30 findings, superseded by the
  next one below per its own note in `CLAUDE.md`).
- `docs/FULL_AUDIT_2026-06-11.md` (111/111 findings closed — the
  definitive one).
- `docs/EXPORT_AUDIT_2026-07.md` — scoped `engine.js` audit, all
  confirmed findings closed.
- `docs/EYEBALL_FIXES_2026-08-16.md` — 19/19 hand-played issues closed.

**Export system:**
- `docs/EXPORT_SYSTEM_STATUS.md` — reconciled banner already frames its
  own checkboxes as historical.
- `docs/EXPORT_POLISH_PLAN.md` — done except the auto-updater
  (deliberately skipped, no driving scenario).
- `docs/GMK_IMPORTER_HARDENING_PLAN.md` — done (own header said "planned,
  not started"; stale, corrected in place — the body confirms `treasure`/
  `maze_4` are both back in the bundled set).
- `docs/web_port_plan.md` — old (2026-04-30), speculative "port to a
  browser-native IDE" sketch, never started. Its core premise (closing
  the `engine.js`/desktop runtime parity gap) is now substantially moot
  — `tests/test_export_feature_matrix.py` shows that gap closed for
  every bundled sample. Left as-is: a real web-IDE port is a different,
  much bigger question than parity, and nothing here should be read as
  scheduled.

**Extensions (Block World, Raycast, Multiplayer v1):**
- `docs/VOXEL_WORLD_PLAN.md` — the origin plan for what shipped as
  Block World; superseded by the two plans below.
- `docs/BLOCK_WORLD_EDITOR_PLAN.md`, `docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`
  — both fully done, all phases.
- `docs/RAYCAST_2_5D_PLAN.md`, `docs/RAYCAST_2_SAMPLE_PLAN.md` (own
  header said "not started"; stale — `raycast_2` shipped the next
  session, corrected in place), `docs/RAYCAST_HUD_PLAN.md`,
  `docs/RAYCAST_DOOM_HUD_PLAN.md`, `docs/RAYCAST_MINIMAP_PLAN.md`,
  `docs/RAYCAST_EXTENSION_PLAN.md` — all done; the whole raycast/2.5D
  arc is closed and extension-owned.
- `docs/extension_compat_2_0/PLAN.md` — done (format guard shipped as
  v1.1.2, both surfaced bugs fixed).
- `docs/MULTIPLAYER_LAN_PLAN.md` — the v1 (spectator-only) plan,
  superseded by `docs/MULTIPLAYER_LAN_V2_PLAN.md` (the live doc, see
  "Currently open work" above).

**Asset/project management:**
- `docs/ASSET_MANAGER_PLAN.md`, `docs/CLEAN_PROJECT_PLAN.md` — both done,
  all tiers, including the shared Trash mechanism.

**i18n / translations** (all closed):
- `docs/I18N_CLEANUP_2026-08-06.md`, `docs/I18N_UNFINISHED_2026-08-10.md`,
  `docs/JA_ZH_I18N_PLAN.md`, `docs/I18N_SAMPLE_GUIDES_2026-07-15.md`,
  `docs/TRANSLATION_CATALOG_CORRUPTION_2026-08-08.md`,
  `docs/TUTORIALS_I18N_PLAN.md` (its own "final pass ... not yet done"
  caveat was closed afterward by `tests/test_tutorial_panel_i18n_verification.py`
  — the doc predates that fix and was never updated; treat it as closed),
  `docs/AI_SLOP_CLEANUP_2026-08-06.md` (content-accuracy sweep; its own
  closing note recommends a fresh audit rather than resuming this one if
  ever reopened).
- `docs/WIKI_COMPLETENESS_PLAN_2026-08-11.md` — closed; its one deferred
  item is `docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md` above.

**Views/camera:**
- `docs/VIEWS_SAMPLES_PLAN.md` — done, all 3 targets.

**Early implementation-completion reports** (2026-01-11 to 2026-01-14,
predate this repo's whole "plan doc + TODO.md registry" convention —
each is a standalone "✅ COMPLETED" report for one shipped feature, kept
for historical context, superseded as a *reference* by the generated
wiki action pages, `tools/gen_action_reference.py`):
`docs/ALARM_SYSTEM_IMPLEMENTATION.md`,
`docs/CONTROL_FLOW_ACTIONS_IMPLEMENTATION.md`,
`docs/DRAWING_ACTIONS_IMPLEMENTATION.md`,
`docs/DRAW_LINE_SPRITE_IMPLEMENTATION.md`,
`docs/KIVY_EXPORTER_COMPLETION.md`,
`docs/MOVEMENT_ACTIONS_IMPLEMENTATION.md`,
`docs/ROOM_CONFIGURATION_IMPLEMENTATION.md`,
`docs/ROOM_LIFECYCLE_IMPLEMENTATION.md`,
`docs/THYMIO_ACTIONS.md`, `docs/THYMIO_COMPLETE.md`,
`docs/THYMIO_EVENTS.md`, `docs/THYMIO_GAMERUNNER_INTEGRATION.md`,
`docs/THYMIO_IMPLEMENTATION_STATUS.md`, `docs/THYMIO_PHASE_2_COMPLETE.md`,
`docs/THYMIO_PHASE_4_COMPLETE.md`, `docs/THYMIO_SIMULATOR.md`.

**GMK-import playtest records** (historical, tied to the now-closed
importer hardening pass — `treasure` and `maze_4` are both back in the
bundled set):
`docs/maze_1_testing_pass.md`, `docs/maze_2_testing_pass.md`,
`docs/maze_3_testing_pass.md`, `docs/maze_4_testing_pass.md`,
`docs/treasure_testing_pass.md`.

---

## Not part of this audit — living reference material, not plans

Left untouched; these aren't trackers, they're current documentation:
`README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CLAUDE.md` (the session
log — historical narrative, referenced-path staleness there is expected
and not worth a rewrite), `docs/BUILDING.md`, `docs/ANDROID_EXPORT.md`,
`docs/EXPORT_TESTING_GUIDE.md`, `docs/ASSET_LICENSES.md`,
`docs/test_checklist.md` (+`.fr.md`), `docs/TESTING_CHECKLIST.md`,
`docs/TESTING_PRESET_CHECKLIST.md`, `docs/blockly_editor_test_checklist.md`,
`docs/PLATFORM_DISPLAY_CHECKLIST.md`, the `docs/USER_MANUAL*.md` /
`docs/FLYER*.md` language sets, and `docs/session-notes/*.md` +
`docs/SESSION_NOTES.md` (the append-only session log).

`TODO.md` stays the registry for small, feature-level deferred items —
this doc is for the handful of larger initiatives and for knowing, at a
glance, what in `docs/` is live vs. closed.

## Corrections made while writing this doc

A few docs' own status headers were stale relative to their body/reality
and were corrected in place (not moved):
- `docs/DEFERRED_ITEMS_PLAN.md`: "planned, not started" → all 13 items
  are actually done.
- `docs/GMK_IMPORTER_HARDENING_PLAN.md`: same stale "planned, not
  started" banner despite the body (and `TODO.md`) showing it done.
- `docs/RAYCAST_2_SAMPLE_PLAN.md`: "PLAN. Not started." despite
  `raycast_2` having shipped the very next session.

Keep this discipline going forward: a doc's top-of-file Status line is a
claim, not ground truth — verify against the body and against current
code before trusting it, same as everywhere else in this repo.

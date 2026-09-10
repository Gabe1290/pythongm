# Project status — where things actually stand

**Read this first.** Written 2026-09-02 and revised 2026-09-06 (items 1
and 2 had both gone stale within days — see their own notes), after a full
audit of every
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

1. **Multiplayer LAN — code COMPLETE, blocked on hardware.**
   *(Updated 2026-09-06. This entry said "Phases 7–8 open"; both landed on
   2026-09-02/03, right after this document was written.)*
   `docs/MULTIPLAYER_LAN_V2_PLAN.md` has eight unticked boxes and six of them
   are the standing manual-QA list below — two real machines on a school LAN,
   the discovery beacon, a Windows firewall prompt, `reseau_2` with 4+ clients,
   an HTML5 export joining from a Chromebook, a Kivy export still running
   single-player. Of the other two, **6.3 (runner caption) is a stale box** —
   verified wired in `extensions/multiplayer_lan/handlers.py` — and **8.4 is a
   name collision**: it wants a *draw-together* `reseau_4`, while the
   `samples/reseau_4` that exists is "Salle partagée (Test Game)", a
   Test-Game-launchable rebuild of `reseau_1`. It is marked optional.
   **Nothing here is code work anyone can do without two machines.**

2. **`docs/POST_1_0_REFACTOR.md` — DONE, all four files split.**
   *(Updated 2026-09-06. This entry said "Zero progress ... estimated ~3 months
   of focused work", which was true when written and wrong within days.)*
   File 1 `object_events_panel.py` → `editors/object_editor/events/`;
   File 2 `core/ide_window.py` 5,316 → **955** LoC across 9 mixins in
   `core/ide/`; File 3 `runtime/game_runner.py` 6,063 → **2,540** across
   `sprite`/`room`/`instance`/`input_handler`/`collision`; File 4
   `runtime/action_executor.py` 6,520 → **1,427** across ten
   `runtime/action_*.py` mixins, in twelve one-cluster-per-commit steps each
   proven bytecode-identical against pre-refactor HEAD.
   **The companion cleanup is closed too** (2026-09-06): the decision it was
   blocked on was made — legacy action names are not worth carrying, there
   being too few legacy projects — so `runtime/action_handlers/` and Phase 2
   of `_register_action_handlers` are gone, with the live handlers folded into
   the mixins. **This plan now has no open work at all.**

3. **`docs/WIKI_TUTORIAL_SCREENSHOTS_PLAN.md` — Phase 1 done (2026-09-11),
   picked up on an explicit ask.** Breakout (shortest of the six
   tutorials, 225 lines) now has 6 real screenshots
   (`wiki/images/tutorial-breakout-*.png`) embedded at each of its
   `## Step N` headings, produced by a new committed, re-runnable tool
   (`tools/capture_tutorial_screenshots.py`) that drives a real offscreen
   `PyGameMakerIDE` through a scratch project matching the tutorial's own
   text. **The plan's own flagged open question is answered**: scripting
   the Room Editor turned out no harder than any other editor — an
   instance placement is just an entry in the room's `instances` list,
   the same "set the data, open the widget" mechanism that already
   worked for sprites and objects — so no per-tutorial risk exists for
   the remaining five. One real placement bug found by actually looking
   at the captured screenshot (a ball placed dead-center landed inside a
   brick's cell and rendered invisible) — fixed, see the plan doc's own
   "What Phase 1 actually found" section. **Remaining, explicit-ask-only
   per this plan's own "pick up only on an explicit ask" framing**:
   Pong/Sokoban/Maze/Platformer/LunarLander (Phase 2) and all 48
   translated-variant pages (Phase 3, `Tutorial-Breakout_fr.md` included).

4. **Full crafting system for Block World — DONE, all 4 units closed
   the same day it was written (2026-09-09).** *(This entry's own
   previous "planned, not started" wording was written earlier the same
   day the plan was drafted and never revisited once the units actually
   landed a few hours later — stale in exactly the way this doc's own
   "Discipline for future doc-writing" section warns about; caught and
   fixed 2026-09-11 rather than trusted at face value.)*
   `docs/BLOCK_WORLD_CRAFTING_PLAN.md` says "Closed 2026-09-09 — all 4
   units done, same day" and the code backs it up:
   `set_crafting_recipe`/`craft_item` (`extensions/block_world/actions.py`
   + `handlers.py`) ship on desktop + HTML5 + Kivy, translated into all
   10 UI languages + 8 wiki languages, documented in the extension's own
   README, and covered by 46 tests including a cross-engine parity suite.
   Outputs stay block types (no new "item" asset type); no crafting-table
   gating, no dedicated crafting HUD (all explicit, written cuts — see
   the plan's own "Explicitly out of scope"). The one thing found along
   the way and logged rather than chased at the time — Kivy had no
   `set_block_reward` port at all (Tier 7b, pre-existing, unrelated to
   crafting) — is **also closed now (2026-09-11)**: `_bw_set_block_reward`
   + `_cg_set_block_reward` added to `extensions/block_world/export_kivy.py`,
   mirroring `set_block_protection`'s exact shape, with 15 new tests
   (`tests/test_kivy_block_world_reward.py` +
   `tests/test_block_world_reward_export_parity.py`, mutation-tested).
   **This item has no open threads left at all.**

5. **`docs/BLOCK_WORLD_PERF_PLAN.md` — the Block World fps gap. CLOSED
   2026-09-09; Phase 1 shipped, re-measured, stopping there per the plan's
   own recommendation.** *(Superseding this item's 2026-09-06 "now scoped"
   framing, which had gone stale the same way items 1/2 above once did —
   Phase 1 landed the next day, 2026-09-07, and this entry was never
   updated.)* Distance fog + `render_distance` 10 (all three targets — see
   the plan doc's 1.1–1.4) is live in code today: `fog_amount`/`fog_mix` in
   `extensions/block_world/renderer.py`, ported to `export_html5.js` and
   `export_kivy.py`, both samples' cameras at `render_distance: 10`.
   **Fresh measurement 2026-09-09** (`tools/measure_block_world_fps.py`,
   interleaved, 30fps target): `block_world_1` static 37.9 (met), walking
   16.2 (1.8x under — an enclosed maze, never render-distance-bound, so fog
   doesn't touch it); `block_world_2` static 26.5 / walking 27.3 (both only
   ~1.1x under, down from ~2x pre-fog). Asked the user whether to chase the
   remaining ~10% on `block_world_2` (Phase 2, estimated ~+5%, likely not
   enough on its own) or investigate `block_world_1` walking (a different,
   unscoped near-wall-pixel-cost regime) — **decision: stop here.** Neither
   sample is in the Welcome tab (see `TODO.md`'s Block World section), Phase
   1 already delivered on its own stated goal, and the plan doc itself says
   not to start Phase 2/3 without a clear need. Re-open only on a fresh,
   explicit ask.

6. **`TODO.md`'s own small leftover — DONE 2026-09-09, before this note was
   last touched.** *(This entry described the item as still open; TODO.md
   itself already marked it `~~DONE~~` — caught 2026-09-11 while working
   through this same list on an explicit ask, the same stale-doc pattern
   as item 4 above.)* `ASSET_TYPE_REGISTRY`
   (`widgets/asset_tree/asset_utils.py`) is the single source for all 8
   asset types; `PyGameMakerIDE.__init__` calls
   `AssetsMixin._verify_asset_editor_registry()` at startup, which raises
   if a registered `editor_method` doesn't exist on the class — a new
   asset type now fails loudly at startup instead of silently at first
   double-click. Commit `61b16a0e`. **No open work here.**

7. **`docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md` — 1990s-style file-exchange
   multiplayer. Track E Phases 1–2–4 of 5 done; Track T done and
   reconciled against the landed API (2026-09-10). Only Phase 5
   (real-hardware QA) remains, and it needs a human + a second machine,
   not agent time.** A new, additional extension
   (`extensions/multiplayer_files/`) alongside — not a replacement for —
   the socket-based `multiplayer_lan`: turn-based games played over a
   shared folder instead of a live connection, for a school LAN whose
   firewall blocks the direct connections sockets need.
   Host-authoritative rounds; `host_game_files`/`join_game_files`/
   `leave_game_files`/`set_shared_var_files`/`get_shared_var_files`/
   `end_turn`/`send_network_message_files`, the six file-session
   lifecycle events, and a built-in connect screen
   (`host_game_files(show_lobby=true)` waiting room,
   `join_game_files(folder="auto")` a typed/validated shared-folder path
   instead of hand-editing the action) — all shipped with real translated
   action names in all 10 languages (`tests/test_extension_action_i18n.py`);
   `samples/fichier_1` ("File Exchange — Tic-Tac-Toe") is the finished
   bundled sample, `h`/`j` hosts/joins straight from Test Game, `j` now
   using the connect screen. Split across two independent tracks for
   parallel work on two machines (see the plan doc's own "Splitting the
   work across two machines" section). **Track T (Teaching:
   `wiki/FileExchange.md` + Tutorial 10) was written in parallel against
   the plan's original action surface, then reconciled against the real
   landed API once both tracks synced** (action/event renames,
   `global.round_number` starting at 1 not 0, an unset shared variable
   reading as `0` not `""`, the non-active-player-must-call-End-Turn
   requirement, and — the one finding big enough to force a rewrite —
   `set_shared_var_files`'s `name` param being always literal, never a
   computed expression, which meant Tutorial 10's original
   nine-`obj_cell`-instances design wasn't buildable at all; rearchitected
   around a single `obj_game` object matching `fichier_1`'s own proven
   layout). All three deliverables (extension, sample, Tutorial) are now
   consistent with each other and fully done modulo Phase 5.

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

# Plan: working through TODO.md's deferred items

Status: **DONE — all 13 items across Tiers 0-3 closed** (corrected
2026-09-02; this line previously said "planned, not started," stale
against the doc's own body and against `TODO.md`). Written 2026-07-15,
right after the views/camera plan (`docs/VIEWS_SAMPLES_PLAN.md`) shipped,
specifically so it can be picked up cold on a different machine. This doc
triaged and sequenced `TODO.md`'s registry; see `docs/PROJECT_STATUS.md`
for the current overall picture.

## Before touching anything: re-verify, don't trust

While drafting this plan, two `TODO.md` claims turned out to be stale —
the Kivy and HTML5 exporters were both claimed to skip `sprite`/`lives`
draw-queue commands, but both actually implement them now (landed
earlier the same day, with the match3_2 sound-queue work and the views
work). Corrected in `TODO.md` directly. **This is exactly the "audit is
a lead, not ground truth" discipline `CLAUDE.md` already documents for
the code-audit work — apply it here too.** Before starting any item
below, grep for the specific claim against current code first; don't
assume the registry is accurate just because it's the most detailed
document available. A chunk of this registry predates several sessions'
worth of shipped work and hasn't been swept since.

## Tier 1 — small, contained, ready to start (no design questions)

Good candidates for a "one task = one commit, verify, push" queue, same
discipline as the match3_2/3 and views sessions:

1. ~~**Generic asset-type editor fallback**~~ **DONE 2026-07-15** —
   `editors/sound_editor.py` / `background_editor.py` / `font_editor.py`,
   following the `scripts` editor's template. Found along the way: the
   font asset's fields aren't consumed by `draw_text` rendering yet
   (new TODO.md entry) — **also DONE 2026-07-16**, see below.
2. ~~**Kivy/HTML5 draw-queue `background`/`health_bar` types**~~ **DONE
   2026-07-15** — `BACKGROUND_PATHS` map + both `_dq_render_cmd` branches
   on Kivy, both `case`s in `engine.js`. Found along the way: structured
   `draw_rectangle`/`circle`/`ellipse`/`line`/`arrow`/`variable`/
   `health_bar`/`background` *actions* (not `execute_code` draw-queue
   dicts) have no codegen on either export target at all — **also DONE
   2026-07-16**, see below.
3. ~~**Object test runner ("Play Object" button)**~~ **DONE 2026-07-15** —
   runs the object in a throwaway temp project through the same
   `_run_project_json` path Test Game now shares (factored out of
   `test_game`). Turned out less "small" than it looked: the refactor
   changed `test_game`'s observable call shape, which broke 3
   pre-existing tests' lightweight `PyGameMakerIDE` stubs (they needed
   the newly-factored-out method added, same convention those stubs
   already used elsewhere) — worth remembering for the remaining tier-1/2
   items: touching a method other tests stub out has a wider blast radius
   than the diff alone suggests.
4. ~~**Room transition effects**~~ **DONE 2026-07-15** — `goto_room`'s
   `transition='fade'` fades to black, switches, fades back in
   (`GameRunner._fade_overlay`). Scoped to desktop only (no sample
   exercises the parameter at all yet, so there was nothing to verify
   Kivy/HTML5 parity against — see the TODO.md entry). Worth noting: the
   first draft's alpha ramp was inverted (screen went black and stayed
   black); a pixel-sampling test plus a 10-frame visual montage caught it
   before it shipped — a "doesn't crash" test alone would have missed it.
   **Tier 1 is now fully closed.**

## Tier 2 — moderate effort, clear scope, one design decision each

5. ~~**Find / Find and Replace**~~ **DONE 2026-07-16** — code-editor-only,
   as recommended below. `dialogs/find_replace_dialog.py` +
   `core/ide_window.py`'s `find`/`find_replace`/`_show_find_dialog`/
   `_find_target_text_edit`. Project-wide search (asset names,
   identifiers) and the `execute_code` action dialog's separate `QTextEdit`
   remain open as a follow-up — see `TODO.md`'s entry.
6. ~~**Background auto-scroll on `set_background`**~~ **DONE 2026-07-16** —
   confirmed smaller than it looked, per the re-scoping note: `GameRoom`
   already had a working `bg_hspeed`/`bg_vspeed`-driven scroll renderer;
   `execute_set_background_action` just never wrote its `hspeed`/`vspeed`
   parameters into it. One small wiring fix — see `TODO.md`'s entry.
7. ~~**Standalone executable build**~~ (Build Game / Build and Run, F7/F8)
   **DONE 2026-07-16 — Tier 2 is now fully closed.** Confirmed the
   prediction exactly: thin shells around the existing
   `export.registry.desktop_exporter_for_host` + `_run_export_with_progress`
   machinery, no new export infrastructure. See `TODO.md`'s entry.

## Tier 3 — larger, needs its own finder→verify→fix pass

8. **GMK importer hardening** — ✅ **DONE 2026-07-16.** `treasure` and
   `maze_4` re-added to the bundled set after a full user playtest closed
   12 real importer/runtime bugs (registry all checked in the plan doc).
   Detailed working plan + checkbox registry:
   `docs/GMK_IMPORTER_HARDENING_PLAN.md` (written 2026-07-16, includes an
   unblocking discovery — `treasure.gmk`/`maze_4.gmk` are recoverable
   from git history despite not being in the working tree — and flags
   that several of the findings cataloged below look already fixed on a
   spot check, so re-verification is Step 0, not fixing from memory).
   The biggest-value item here: reintroduces
   two dropped samples (`treasure`, `maze_4`) and has unusually good
   groundwork already (specific root-cause hypotheses cataloged in
   `TODO.md`'s "GMK importer hardening" section: `if_previous_room_exists`
   swapped with `if_next_room_exists`, `visible: false` defaulting wrong,
   `action_play_sound` mis-mapped to `set_sprite`, missing
   `(1, 223)` → `restart_room` mapping — several sibling bugs in
   maze_1/maze_3 were already found and hand-fixed this way). Treat as
   its own multi-session project: regenerate both samples from their
   `.gmk` sources, catalog every parameter that didn't survive
   conversion, fix each in `importers/gmk_mappings.py` /
   `gmk_converter.py` with a dedicated regression test under
   `tests/test_importers/`, following the exact recipe `TODO.md` already
   lays out. Don't start this inside a single session that's also doing
   other Tier 1/2 items — it has its own investigation phase.
9. **`execute_code` environment parity (Kivy + HTML5 `game` binding, and
   Kivy locals-copied-back)** — ✅ **FULLY DONE, all sub-items.** Kivy's
   score/lives/health half shipped
   2026-08-09 (commit `c977f1c`) — `game`/`instance` bound via the same
   `_script_game()` proxy `execute_script` already used, extended with
   `score`/`lives`/`health` as plain read/write values. HTML5's matching
   `game: None` gap **also closed the same day** (commit `2ecc6f0`) — a
   fresh `_Game(score, lives, health)` snapshot built each `run_code`
   call from values synced in from the live JS `game` object, diffed
   back out through the same JSON patch mechanism `self.x`/`self.y`
   already use. **Both fixes share the identical design decision**,
   confirmed correct by re-checking desktop's real behavior: a raw
   `game.lives = X` from `execute_code` is a PLAIN write on every
   target — no caption update, no `no_more_lives`/`no_more_health`
   crossing check. Those only fire from the `set_lives`/`set_health`
   ACTIONS specifically. This turned out to make the HTML5 fix *simpler*
   than the original plan assumed — no shared-refactor of the crossing-
   detection logic was needed after all, since the correct design never
   triggers it from `execute_code` in the first place. Verified two
   ways: `tests/test_html5_execute_code_game_binding.py`'s primary
   coverage exec()'s the real `PY_BOOTSTRAP` Python source directly
   (deterministic, no network, no JS engine — the established pattern
   `test_sound_queue_primitive.py` already uses for this exact string),
   plus a one-time ad hoc real-browser check (`playwright` + a real
   headless Chromium against the actual Pyodide CDN, not a project
   dependency, not committed) that caught a real cosmetic bug (an
   unescaped-backtick `SyntaxWarning` in the new docstring) the
   regression tests alone wouldn't have.

   **"Locals copied back onto the instance" (the Kivy half) — DONE
   (2026-08-09).** User given the choice between an exec()-at-runtime
   switch (full parity, same mechanism desktop/HTML5 already use, loses
   compile-time syntax checking of user code — which desktop/HTML5 don't
   have either) and an export-time AST rewrite of bare assignments into
   `self.x = x` (keeps literal inlining, correctness-fragile against
   every binding form CPython's real `exec()` covers — for-loop targets,
   `with...as`, tuple unpacking, augmented assignment); **chose exec()**.
   `export/Kivy/code_generator.py`'s `execute_code` branch now embeds the
   user's code as a `repr()`'d string literal and execs it at runtime
   against `{self, instance, other, game, math, random, __builtins__}`,
   then `setattr`s every leftover local onto the instance — byte-for-byte
   the same mechanism as `runtime/action_executor.py`'s
   `execute_execute_code_action` and HTML5's `PY_BOOTSTRAP` `run_code`.
   `other` is bound to the real `other` parameter only inside a collision
   handler (`None` elsewhere), matching desktop's
   `_collision_other`-or-`None` semantics. `math`/`random` are now
   *always* available (matching desktop's unconditional binding),
   replacing the old conditional-import text-heuristic. Verified almost
   entirely by REAL EXECUTION (compile + exec the generated method
   against a stub class), not string matching — the only way to actually
   prove the locals-copied-back mechanism works, since text matching
   can't tell you whether `exec()` ran correctly:
   `tests/test_kivy_execute_code_export.py` (11 tests, rewritten —
   3 of the old tests tested the since-removed literal-inline/
   conditional-import behavior and were replaced, not just patched).
   Full suite 2407 → 2411 passed, 0 failed.
   **Both adjacent follow-up gaps (found here, deliberately left open at
   the time) are now ALSO DONE, same day.** `keyboard` binding via a new
   `GameObject._check_key` adapter method (single-sourced key-name table
   with `if_key_pressed`'s codegen), and `execute_script` got the
   identical exec()-based rewrite `execute_code` did, plus the `other`/
   `keyboard` bindings it never had at all. See `TODO.md`'s matching
   entry for full detail, including a real `.format()`-template comment
   bug this surfaced and fixed. `tests/test_kivy_execute_script_export.py`
   (new). Full suite 2411 → 2425 passed, 0 failed.
10. **Asset Manager** (`Tools → Asset Manager...`) — ✅ **DONE
    (2026-08-09), all 4 tiers.** Bulk rename/move/delete, usage tracking
    ("which rooms/objects use this sprite?"), unused-asset cleanup.
    **Scoped 2026-08-09**:
    `docs/ASSET_MANAGER_PLAN.md` breaks it into 4 tiers. **Tier 1 (usage
    tracking) DONE** (commit `07a0d8a`) — `utils/asset_usage.py`, wired
    into the existing single-asset delete confirmation. **The Tier 3
    "bulk-delete-undo" design question is also DONE, same day** (commit
    range starting `feat: soft-delete Trash` — see item 10.5 below): a
    soft-delete Trash, not a QUndoCommand undo/redo. **Tier 2 (search &
    filter) DONE (2026-08-09)** — `AssetTreeWidget.apply_asset_filter`, a
    name-substring filter box above the Asset Tree panel. **Tier 4
    (unused-asset cleanup UI) DONE (2026-08-09)** —
    `UnusedAssetsDialog`/`Tools → Find Unused Assets…`; see the plan doc
    for the rooms-labeling fix this surfaced. **Tier 3 (bulk multi-select
    delete) DONE (2026-08-09)** — `docs/ASSET_MANAGER_PLAN.md` scoped
    "move" out entirely first (the app's flat per-category asset model has
    no folder hierarchy for a bulk move to relocate anything within); what
    shipped is `ExtendedSelection` + a reduced right-click menu + one
    combined confirmation for the whole batch, routed through the same
    trash-backed per-item delete. **`docs/ASSET_MANAGER_PLAN.md` is now
    fully closed.**
10.5. **The bulk-delete-undo design question — SETTLED (2026-08-09).**
    Explicitly its own numbered item because it was the shared blocker
    for both item 10 Tier 3 and item 11. Decision: **not**
    `QUndoCommand`-based undo/redo (the existing `QUndoStack` usage in
    this codebase is scoped to live in-memory canvas edits with no file
    I/O, cleared on project switch/app restart — the wrong tool for
    "restore a deleted file"). Built instead: `utils/asset_trash.py`, a
    soft-delete Trash — deleting an asset moves its files to
    `<project>/.trash/` and records a manifest entry instead of
    unlinking anything, with a new "Tools → Restore Deleted Assets..."
    dialog (`TrashDialog`) to restore or permanently empty. Both real
    delete paths (`AssetManager.delete_asset`, the live-app path, and
    `asset_operations.py`'s legacy fallback) route through it, so
    single-asset delete is safer today too, not just future bulk
    features. Zip export excludes `.trash/` (the compression walk had no
    exclusions at all before this). 46 new tests across
    `test_asset_trash.py`, `test_trash_dialog.py`, and additions to
    `test_asset_manager.py`/`test_audit_asset_operations_sidefiles.py`/
    `test_project_compression_trash_exclusion.py`.
11. **Clean Project** — ✅ **DONE (2026-08-09), all 3 tiers.**
    `docs/CLEAN_PROJECT_PLAN.md` is fully closed. Two findings shrank the
    real scope: rollback-snapshot cleanup already happens automatically
    (`_sweep_orphan_snapshots`, every load), and the `__pycache__`/`.pyc`
    workaround describes cleaning this dev repo, not a saved game project
    (which never has importable `.py` files under it). `utils/
    project_cleanup.py`: Tier 1 (`.tmp` orphan sweep, permanent removal,
    Tools → Clean Project), Tier 2 (orphaned-physical-file detection,
    the inverse of Asset Manager's unused-*entry* detection), Tier 3
    (`OrphanedFilesDialog`, Tools → Find Orphaned Files…, trashed via a
    **second, deliberately separate** trash store —
    `.trash_orphaned_files/`, not `.trash/` — since these files have no
    project.json entry for `AssetManager.delete_asset`/its restore path
    to operate on; see the plan doc for the concrete bug that sharing the
    store would have caused).
13. **2.0 extension system — the feature work.** ✅ **DONE (2026-08-09,
    commit `4c50485`)** for everything with a concrete, provable fix.
    Tasks 2-4 of `docs/extension_compat_2_0/PLAN.md` turned out much
    smaller than drafted — investigating before coding found
    `events/plugin_loader.py` already implemented most of "Task 2" and
    "Task 3". Landed: (a) the `_prepare_project_data_for_save` fidelity
    bug fixed (an extension dependency this editor can't verify is stale
    is now preserved, not wiped) with 5 regression tests
    (`tests/test_extension_manifest_preservation.py`); (b) unrecognized
    action tree items now render amber with the owning extension named
    when its manifest is on disk (new `plugin_loader.extension_for_action`),
    and double-clicking one explains why instead of silently doing
    nothing, with 6 regression tests (`tests/test_extension_action_ui.py`);
    (c) dropped a misleading "enable the extensions in your config" hint
    — investigation found no config UI for toggling extensions exists
    anywhere in the app yet. Full suite 2245 → 2256, 0 failed.

    **The deferred settings UI — DONE (2026-08-09, separate session, planned
    via `EnterPlanMode` before coding).** A new "Extensions" tab in
    `dialogs/preferences_dialog.py`'s `PreferencesDialog` (its existing
    5-tab structure), listing every `events.plugin_loader.
    list_available_extensions()` entry as a checkbox (name, version +
    description caption, `provides_actions` in a tooltip rather than
    inline to stay uncluttered as more extensions land), with an
    empty-state placeholder when none are found. **The backend needed zero
    changes** — `list_available_extensions`/`is_extension_enabled`/
    `set_extension_enabled` already existed complete; this was pure UI.
    Checkbox state is buffered and only written (via a new
    `_apply_extension_settings()`, split out for testability) inside
    `apply_settings()` — never live-on-toggle — matching every other tab's
    Cancel-must-not-persist semantics. No new restart mechanism: the
    dialog's existing generic footer ("Note: Some settings require
    restarting the IDE...") already covers it; no app-relaunch/hot-reload
    infrastructure exists anywhere in this codebase and building one was
    explicitly scoped OUT (extension loading has real side effects —
    process-global `ACTION_TYPES` registration, room-renderer hooks, a
    synthetic-package-name import — cleanly unregistering all of that is a
    materially bigger task). One real nuance surfaced during design
    validation and folded into the tab's caption text: toggling here
    changes **IDE** behavior after a restart, but the Kivy/HTML5 **exporters**
    already re-check `enabled` live at export time (`export/HTML5/
    html5_exporter.py`, `export/Kivy/kivy_exporter.py`, `export/Kivy/
    code_generator.py` each call `list_available_extensions()` fresh per
    export) — without calling this out, a user could be confused why an
    export dropped code before restarting. Also restored the accurate
    pointer text ("You can enable an extension via Preferences →
    Extensions.") to `_warn_missing_extensions()`'s warning dialog, closing
    the loop the misleading-hint removal above left open. Deliberately
    NOT built (noted as future follow-ups only, not started): an "Enable
    Now" button wired directly into that warning dialog (a second entry
    point, needs its own scoping), and a live "Restart Now" relaunch
    button. Coverage: `tests/test_preferences_extensions_tab.py` (8 tests
    — listing, checked-state, tooltip, `_apply_extension_settings`
    writing the right calls, Cancel never persisting, and a wiring check
    that `apply_settings()` delegates to it — with `events.plugin_loader`
    and `Config` mocked throughout so no test touches the real
    `extensions/` folder or `~/.pygamemaker/config.json`). Full suite
    2425 → 2433 passed, 0 failed.

## Tier 0 — do before anything else in this doc (protects future downloads) — ✅ DONE

12. **Ship a project-format-version guard.** ✅ **DONE, shipped as v1.1.2
    (2026-08-09)** — not 1.0.1 as originally drafted; the plan's "1.0"
    assumption was stale (this repo was already on 1.1.1 when this item
    was written). Task 1 of `docs/extension_compat_2_0/PLAN.md`:
    `core/project_format.py`'s `check_project_format()`, called from
    `ProjectManager.load_project()` immediately after parsing, refuses
    (doesn't crash, doesn't resave-and-corrupt) a project newer than this
    build supports, with a specific `QMessageBox` at the UI layer.
    `tests/test_project_format_guard.py` (13 tests) includes a
    byte-for-byte on-disk-unchanged assertion after a refused load. The
    remaining three tasks in that plan (now much smaller than drafted —
    see item 13) are real feature work, correctly bucketed with Tier 3.

## Explicitly not now (already scheduled or deliberately deferred)

- **Manifest-ify objects & sprites in `project.json`** — its own note
  says to do this "carefully... just before the final validation pass
  before the 1.0 release." Don't move it earlier; it changes the on-disk
  save format for every project.
- **Particle system / timelines / save_game / load_game / show_video /
  execute_script UI metadata** — `TODO.md` explicitly says "do NOT add UI
  yet" pending a functional check of the underlying handlers.
- **Splash text/image/video/webpage placeholders, Execute file/shell
  command** — no urgency signal, and the file/shell ones are
  intentionally security-restricted; don't expose without a real
  sandboxing story.
- **Thymio "play sound" placeholder** — niche (Thymio-specific), low
  general priority relative to everything else here.
- **Kivy long-tail action coverage, on-device Android/buildozer
  end-to-end test** — real but each is either open-ended ("port actions
  as we hit them") or needs infrastructure this repo doesn't have in a
  headless CI sense (a real phone, a real buildozer build). Pick up
  opportunistically, not as a scheduled item.
  **Right/middle mouse export is DONE (2026-08-14)** — see `TODO.md`'s
  Kivy/Android and HTML5 export sections.

## Suggested starting point when resuming

**Tier 1 is fully closed (2026-07-15, items 1-4).** Two follow-up items
it surfaced along the way are now **also DONE (2026-07-16)**: font assets
are consumed by `draw_text`/`draw_scaled_text` rendering
(`GameInstance._resolve_draw_font`/`_align_text_pos`,
`tests/test_draw_font_rendering.py`), and structured `draw_*` actions
(rectangle/circle/ellipse/line/arrow/variable/health_bar/background) now
have codegen on both Kivy (`export/Kivy/code_generator.py`) and HTML5
(`export/HTML5/templates/engine.js`'s `executeAction` + a new `'arrow'`
case in `renderDrawCommands`), plus a genuine desktop `_DRAW_HANDLERS`
gap for `'arrow'` that surfaced along the way — see `TODO.md`'s matching
entries for detail; `tests/test_draw_action_codegen.py` covers all three.

**Tier 2 is now fully closed (2026-07-16, items 5-7).** Find/Replace
(code-editor scope, `dialogs/find_replace_dialog.py`), the
`set_background` `hspeed`/`vspeed` scroll wiring (one-line-per-axis fix in
`execute_set_background_action`, confirmed smaller than it looked), and
Build Game/Build and Run (F7/F8 — thin shells around the existing
`export.registry.desktop_exporter_for_host`/`_run_export_with_progress`
machinery, confirmed no new export infrastructure needed as predicted).

**2026-07-16, 72% session usage, next session in ~1h25 — stopped here on
purpose** rather than start Tier 3 mid-budget. `docs/GMK_IMPORTER_HARDENING_PLAN.md`
is the resume state for item 8: it starts with Step 0 (re-verify every
cataloged finding — several already look fixed on a spot check) before
any regeneration/fixing, and has the `treasure.gmk`/`maze_4.gmk`
git-history recovery command ready to run. Kivy `execute_code`
environment parity (item 9) needs a design decision first (build a
`game` proxy vs. document the gap) before any code. Asset Manager / Clean
Project (items 10-11) have no small starting subset documented yet —
scope Asset Manager first since Clean Project's unused-asset detection
overlaps it. Re-verify each item's `TODO.md` claim against current code
before starting it, per the discipline above.

**Item 8 (GMK importer hardening) is now DONE** (2026-07-16, same day as
the note above — `treasure`/`maze_4` reintroduced, 12 real bugs closed,
registry in `docs/GMK_IMPORTER_HARDENING_PLAN.md` fully checked). ja/pt/zh
translation migration, listed above as "explicitly not now," is **also
now DONE** (2026-08-09 — see `TODO.md`'s matching entry and
`docs/I18N_CLEANUP_2026-08-06.md`).

**2026-08-09 — new Tier 0 item added.** A mobile design session produced
a ready-to-implement plan for 2.0 extension-system compatibility
(`docs/extension_compat_2_0/PLAN.md`) with its Task 1 — a project-format-
version guard that must ship as **1.0.1** before any real 2.0 file exists
— now item 12, sequenced *ahead* of everything else in this doc precisely
because it's the one item here with a real "must happen before X" ordering
constraint relative to work outside this repo entirely (future downloads
of the already-released 1.0 build). The rest of that plan (2.0 read/write,
placeholder rendering, install-offer UX) is item 13, bucketed with Tier 3
since it's real feature work with open design questions, not urgent
infrastructure. **Suggested next session, in order: item 12 first (small,
self-contained, unblocks a release), then resume wherever Tier 3 was left
— item 9 (Kivy `execute_code` parity, needs a design decision) or item 10
(Asset Manager, needs its own scoping pass) are the two with no other
open dependency.**

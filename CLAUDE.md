# CLAUDE.md

Working notes for Claude / agent sessions on pygm2. Lives in-repo so the
context follows across machines.

## Running tests

From the repo root:

- **Linux/macOS:** `python3 -m pytest tests/ -q` (Python 3.11+, PySide6 6.9.2).
- **Windows:** `py -3.12 -m pytest tests/ -q`. Do **not** use bare `python3` —
  it resolves to `pythoncore-3.14`, which is outside the supported 3.10–3.13
  range (commit `faa8f00`) and lacks pygame on this box, producing ~34 errors
  / 7 failures that aren't real regressions. The `venv/` directory at repo
  root is a Linux artifact synced via Dropbox and is unusable from Windows.

- **Baseline:** the pass count grows as tests are added and the skip count is
  env-dependent, so treat **any non-zero _failure_ count as a real
  regression** rather than chasing an exact pass number. Recent green
  snapshots: **532 passed, 21 skipped, 0 failed** on this Linux box
  (Python 3.11.2 + pygame 2.6.1, 2026-06-03); **670 passed, 0 skipped** on
  Python 3.12 + pygame 2.6.1 + PySide6 6.10.1 (2026-06-07, the Windows box —
  tests have grown since). The old "536 passed" / "486 passed" figures are
  stale snapshots.
- **`pytest-qt` is required to RUN the widget tests, and CI runs them.** Without
  it (the default on the Linux box) ~41 tests that use the `qapp` fixture
  **error** (not skip) and are effectively *not run locally* — so a regression
  in a GUI path passes locally and only fails in CI. Install it
  (`pip install pytest-qt`) and run `QT_QPA_PLATFORM=offscreen python3 -m pytest
  tests/ -q` to reproduce CI exactly. CI-equivalent green snapshot: **1162
  passed, 0 failed, 0 skipped** (2026-06-15, Linux 3.11 + pytest-qt). Audit
  regression tests deliberately use a hand-rolled offscreen QApplication
  (no `qapp` fixture) so they run even without pytest-qt.
- `pyflakes` is **not** installed; substitute `py_compile` + import sanity for
  static checks.
- For headless / offscreen Qt: `QT_QPA_PLATFORM=offscreen` (`conftest.py`
  already sets `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` for pygame).
- Skip `-x`; tests are independent and the full count is the signal.

## Audit-cleanup history (§1–§3 closed)

`docs/CODE_AUDIT.md` tracks a pre-1.0 audit/dedup effort across §0–§4.
**§1–§3 are all closed** as of 2026-05-19 (see the `Single-source X` commit
series — dfee042, 19ca7a1, 43cae83, ee853d8, b408b1f, 39f6f38, 36b4a14).

Methodology for any future audit work (§4, follow-ups, or new audits):

- The audit is **a lead, not ground truth.** Re-verify every duplication
  claim with an AST/byte check before extracting. Multiple §3 items were
  materially wrong (overstated copy counts, divergent code labeled
  "identical", inert `pass` stubs labeled "duplicate"). When the audit
  overstates, correct `docs/CODE_AUDIT.md` rather than forcing a
  behaviour-changing "consolidation."
- Every consolidation must be **behaviour-preserving and proven against
  pre-refactor HEAD** via a throwaway offscreen-Qt harness (snapshot HEAD
  with `git show HEAD:path`, exercise old vs. new across an exhaustive /
  representative input matrix, diff observable state). Document the proof in
  the commit body.
- Translation safety for base-class / mixin extraction: PySide6 `self.tr()`
  takes its context from the **concrete runtime class**, so moving `tr()`
  into a shared base / mixin is runtime-safe; keep divergent strings
  lexically in subclass hooks. (Repo uses `lrelease` only — no `lupdate`.)
- Work in audit order, one cluster per commit on `main`.

## TODO.md is the deferred-features registry

Anything that was a "Not Implemented" placeholder or click-then-dead-end
stub was removed in rc.11 and tracked in `TODO.md` instead. **Don't propose
adding "Not Implemented" dialogs back** — that's the exact pattern rc.11
cleaned up (commit 77e9dbf: *"stop lying to users"*). Items still listed
in `TODO.md` include room scrolling (`runtime/action_executor.py:3781`),
room transitions (`runtime/action_executor.py:5111`), and Thymio
sampled-audio playback (`runtime/thymio_action_handlers.py`).
Pixel-perfect collision was implemented in Phase 2a (2026-05-22) and is
no longer in `TODO.md` as a stub — what remains is the IDE-UI follow-up
for toggling `precise` on a native sprite asset.

## Standing preferences & landmines (ported from machine-local agent memory, 2026-07-13)

These lived only in the Linux box's local agent memory and were ported here
before that machine was reformatted. They apply on every machine.

- **French text must always carry proper accents** (é, è, ê, à, ç, ù, î, ô…).
  This is educational software for French-speaking students and teachers;
  missing accents are unacceptable. Double-check any generated or translated
  French — UI strings, docs, flyers.
- **Commit and push directly to `main` — no feature branches.** The user works
  across several computers that all converge on `main` (GitHub is the sync);
  a feature branch fragments that single line of history. Group changes into
  logical commits and push.
- **Size every task to the account's session limit — no multi-agent
  workflows.** The account's usage limit is small; fan-out (not total work)
  exhausts it. Empirically (2026-07 export audit) multi-agent `Workflow`s
  (15–28 parallel agents) hit the limit and blocked the account **three
  times**, always mid-run; single `Agent` finders and main-thread work
  stayed fine. So: **one task ≈ one commit** (a fix + its regression test +
  verification); **don't launch multi-agent `Workflow`s** — if parallel
  investigation is needed, run ONE `Agent` at a time and **verify findings by
  reading code on the main thread**, not with verifier subagents; for a big
  job (audit/migration) write the plan/registry to a file and **commit it
  first**, then work a queue of finder→verify→fix units one at a time,
  **committing and pushing after each** so a mid-session limit loses nothing
  and the next session resumes from clean `main`. Checkbox registries (e.g.
  `docs/EXPORT_AUDIT_2026-07.md`) are the resume state.
- **Audio actions are plugin-owned.** `play_sound`/`stop_sound`/`play_music`/
  `stop_music`/`set_volume` live in `plugins/audio_actions.py` (category
  "Audio"), NOT in the static `ACTION_TYPES` dict in `events/action_types.py`;
  `events/plugin_loader.py` merges them at app runtime, so
  `get_action_type('play_sound')` returning `None` in CLI/test imports is
  expected, not a bug. **Landmine:** `plugin_loader._load_actions` skips any
  plugin action whose name already exists in `ACTION_TYPES`, so adding a
  static duplicate silently shadows the plugin version (real regression
  `f85e1ec`, fixed in `1ae8fbd`). To add/modify an audio action, edit the
  plugin; don't add it to `BLOCKLY_TO_ACTION_MAP`/`actionToBlockType` or the
  hardcoded Blockly "Sound" toolbox category (basic audio is intentionally
  ungated and auto-generates its Blockly blocks into an always-visible
  "Audio" category; the legacy `sound_play`/`music_play`/`music_stop` block
  defs exist only to load old saved workspaces).
- **Export dependency strategy (decided 2026-06-26): keep pip-based deps.**
  Native desktop/mobile export needs kivy + pyinstaller + pillow in the same
  Python that runs the IDE. A second "everything bundled" download was
  discussed and **deferred** (PyInstaller can't run inside a frozen app, so
  it would mean shipping a portable Python env — hundreds of MB, ~double
  release work, macOS signing pain). Don't re-propose it unless asked. The
  supported low-friction paths: `pip install --user <pkg>` (no admin) or the
  zero-install HTML5 export; `export/base_exporter.py`
  `_missing_dependency_message` already surfaces both.

## Recent agent-session notes

**2026-05-22 — Copilot rate-limit handoff.** A Copilot session at
`~/.copilot/session-state/4ce8797d-a274-4586-b049-1361fcf18a53/` produced a
plan claiming "Phase 1 ✅ COMPLETE" (README badge updated,
`FeatureStatusDialog` created, 10+ exception handlers narrowed, JSON schema
validation added). **Most of that was hallucinated** — no commits landed,
the worktree was an empty root-owned stub, `FeatureStatusDialog` never
existed, the README badge was still `rc.6`, and the exception handlers were
untouched. `_validate_project_data` in `core/project_manager.py` already
existed since 2025-10-26.

The Phase-1 items genuinely worth doing were folded into the post-rc.11
polish commits (README badge fix, `set_hspeed`/`set_vspeed` consolidation,
honest Thymio docstring).

**2026-05-22 — Phase 2 reversal.** The user approved Phase-2 work
(viewport scrolling + pixel-perfect collision) for inclusion in 1.0, with
the rc.11 release window slipping accordingly. Phase 2a (pixel-perfect
collision) has landed: static-only, opt-in per sprite via
`sprite_data['precise']`, GMK importer captures the source flag, AABB
fallback for rotated/scaled instances. Phase 2b–2c (views/camera system)
is next on the queue. The general "stability over features" principle
still applies to *other* work in the repo — this is a scoped exception
limited to the two named features.

**2026-06-03 — Latent-bug audit.** A multi-agent audit confirmed 30
logic-level bugs; the registry (with file:line, suggested fixes, and
checkboxes) lives in `docs/LATENT_BUG_AUDIT_2026-06-03.md`. The **7 highs
are fixed** (commits `d60f41b`, `67c91e4`) with regression coverage in
`tests/test_audit_regressions.py`. **14 medium + 9 low remain open** —
pick up from that doc and flip checkboxes as you fix. Re-running the
"latent-bug-audit" workflow re-derives findings from current code.

**2026-06-07 — IDE bug-fix batch (sprites, room restart, instance ids).**
A run of user-reported fixes, each pushed to `main` with regression tests:
- `84bafd5` "Stay destroyed" opt-in object flag (`remember_destroyed`): a
  destroyed instance won't respawn on a room *restart* (or re-entry); cleared
  on a full game restart; child-only inheritance like `persistent`. Engine
  keeps the set in `GameRunner._destroyed_memory` keyed by
  `(object_name, xstart, ystart)`. `tests/test_remember_destroyed.py`.
- `5f09b1d` the `game_start` event is now actually fired (it had *no* trigger
  anywhere, so authored startup setup — score/lives/window caption — never
  ran; lives only appeared after the first death because `set_lives`
  auto-enables the caption). Also: collision processing now stops once a
  handler queues a room change/restart, so one death can't deduct a life per
  overlapping monster. `tests/test_event_lifecycle_fixes.py`.
- `e950e4c` object editor shows imported-but-unsaved sprites — prefers the
  IDE's live in-memory project data over the on-disk `project.json` read, plus
  a push model for floated editors. (Imports copy the file + update memory but
  don't rewrite `project.json` until save.)
- `c9ca13a` sprite editor: moving a *selection* no longer blanks the sprite —
  `SelectTool.on_release` now commits the floating layer (it cleared the
  source region but only re-stamped on the next click, so the frame sync baked
  a transparent hole); `save()` also flattens any floating selection.
- `aee596f` the red "(not imported)" badge self-heals on save via
  `AssetManager.revalidate_asset_import_state` (it's set only at load when the
  image file is absent, and a guard kept it stuck). `file_missing`/`imported`
  are display-only — runtime/export ignore them.
- `5b14c13` + `76209af` + `5e61605` room editor stops baking `id(self)`
  memory-address `instance_id`s into room JSON (dead metadata — read nowhere;
  the runtime grid keys off the live `id(instance)`). Swept **all** samples
  clean (1147 ephemeral ids removed across maze_1/2/3 + plateforme_2). User
  has since re-saved maze_1 (`01587c9`) and maze_2 (`1567565`) with new sprite
  art; maze_3 still pending.

**2026-07-15 — Platformer stomp-test fixed.** The `plateforme_3` follow-up
noted above (`obj_pingus`'s `collision_with_obj_monstre`/`_volant` fragile
stomp test) is applied: `vspeed > 0 and y < other.y+8` →
`vspeed > 0 and y - vspeed < other.y+8` (checks the pre-move position, so a
fast fall no longer overshoots the 8px window and costs an unearned life) in
both `samples/plateforme_3/objects/obj_pingus.json` and the embedded copy in
`samples/plateforme_3/project.json`. The sample's own README documented this
as a "Things to tweak" teaching point; it's been reworded to describe the fix
rather than pose it as an open exercise.

**2026-06-09 — Audit follow-through (dead code + save rollback).** Acted on a
re-audit by verifying each claim against code first (several were overstated).
Two landed:
- Removed the dead `runtime/collision_system.py` module entirely
  (`CollisionMixin` plus the unused `get_bounding_box`/`boxes_overlap`) — it
  was only referenced by `runtime/__init__.py`; `GameRunner` never inherited
  it and has its own same-named collision methods. Cleaned the `__init__.py`
  import/`__all__`/docstring and the ARCHITECTURE.md §6 + tree references.
- Gave the **folder** save the cross-file backup/rollback the **zip** save
  already had. `_save_to_folder` now snapshots the save-managed paths
  (`rooms/`, `objects/`, `sprites/`, `playgrounds/`, `project.json`) via
  `_snapshot_for_rollback` before the multi-file write and restores them on
  any exception via `_restore_from_snapshot` (discarded on success). Per-file
  atomicity (`_atomic_write_json`) was already there; this adds the
  *across-file* transaction so a failure on file N can't leave files 1..N-1
  committed. Regression coverage: `tests/test_save_rollback.py` (4 tests).
  Baseline 647→651 passed, 0 failed.

Then closed the two narrow Test-Game subprocess gaps (the audit's "spawn and
forget" was overstated — there was already a 100ms `QTimer` poll +
terminate/kill on stop):
- `run_game` now captures the child's stderr to a temp **file** (not
  `subprocess.PIPE`, which can deadlock the child when the unread buffer
  fills — the hazard the old "don't capture output" comment dodged). New
  `_drain_game_stderr` logs the captured traceback on a non-zero exit (a
  crashing game no longer fails silently) and always deletes the temp file;
  called from both `_check_game_process` (normal exit) and `stop_game`.
- `closeEvent` now calls `stop_game()` (past the cancel paths, so a cancelled
  close leaves the game running) — previously closing the IDE mid-run orphaned
  the subprocess. Regression coverage: `tests/test_game_subprocess_supervision.py`
  (7 tests). Suite 651→658 passed, 0 failed.

Audit claims deliberately **not** acted on: the "7-file action" and
"manual sync is fragile" items are real but low-churn / already pinned by
`tests/test_state_container_sync.py`, and reworking them conflicts with the
stability-over-features stance.

**2026-06-09 — Archive path-traversal (Zip Slip) hardening.** An audit flagged
`ProjectCompressor.decompress_project`'s `zipf.extractall` as HIGH-severity Zip
Slip with an "overwrite /etc/passwd" PoC. **Severity was overstated** — modern
CPython's `extractall` already strips `..` components (verified on 3.11: a
`../../../tmp/x` member lands at `out/tmp/x`, not `/tmp/x`), so the PoC doesn't
work on any supported Python (3.10–3.13). Added the explicit per-member
`is_relative_to(base)` guard anyway as defense-in-depth + to fail loudly
instead of silently flattening. The **real** (and exploitable) traversal the
audit missed: `utils/resource_packager.py` `import_object`/`import_room` build
destinations from untrusted `package.json` asset names and write via
`zipf.open` (which, unlike `extractall`, does NOT sanitize) — a sprite/bg named
`../../../x` escaped the project dir. Fixed with a shared
`ResourcePackager._safe_join` guard at all three write sites. Note the guard
correctly *allows* in-bounds normalization (`sprites/../player.png` →
`base/player.png`); only paths that climb above base are rejected. Coverage:
`tests/test_zip_slip.py` (10 tests). Suite 658→668 passed, 0 failed.

**2026-06-09 — Project-loading path-traversal: audit finding rejected, real
analog fixed.** An audit flagged `load_project` as MEDIUM path traversal and
proposed whitelisting project roots (`VALID_PROJECT_ROOTS = [~/PyGameMaker
Projects, cwd]`). **Rejected as a false positive** — every path reaching
`load_project` is user-chosen (`QFileDialog` defaulting to `~`), from the
user's own recent list, or app-generated (samples/exports); there's no
untrusted channel and the process runs as the user, so there's no sandbox to
escape. The whitelist would break the intended "open a project from anywhere"
feature for zero security gain. (The audit also mis-cited `utils/__init__.py`'s
`load_project`, a static helper with no non-test callers; the live loader is
`core/project_manager.py`.) The **real** analog, same class as the
resource_packager bug: asset *names* (dict keys from a project.json) are used
directly as filenames — `rooms_dir / f"{name}.json"` etc. — on both load (read)
and save (write), so a malicious *shared* project with a key like `../../../x`
could traverse. Added `_safe_asset_path` (module-level in `project_manager.py`)
and routed all 10 sites through it (4 load, 4 save, 2 migrate); unsafe names are
skipped with a warning, legitimate identifiers pass untouched. Coverage:
`tests/test_asset_name_traversal.py` (9 tests, incl. a load test that plants a
file at the traversal target and confirms no leak). Suite 668→677 passed, 0
failed.

**2026-06-09 — "Unbounded sprite cache": audit finding rejected, one real cache
gap fixed.** An audit called `RoomCanvas.sprite_cache`/`origin_cache`
"unlimited growth → OOM" and proposed `@lru_cache(maxsize=100)`. **Rejected.**
Both caches are keyed by asset *name*, so they're bounded by the project's asset
count (a plateau, not unbounded-over-time), sprites are capped ≤64px, and both
are already cleared on project change in `set_project_info`. The proposed
`@lru_cache` on an *instance method* would be actively harmful — it keys on
`self`, pinning the whole widget in memory (a real leak), needs `self`
hashable, can't clear per-project, and a cap of 100 below typical project sizes
forces sprite re-decode every repaint. The **one genuine gap**:
`tile_pixmap_cache` (keyed by `(background_name, tile_x, tile_y, w, h)`) is
project-scoped like its two siblings but was the only one never cleared, so it
accumulated stale tile crops across project switches. Fixed by clearing it (and
the pre-composited `_tile_layer_cache`) in `set_project_info` alongside the
others. Coverage: `tests/test_room_canvas_cache_clear.py` (constructs a real
offscreen QApplication, no pytest-qt needed, so it runs on 3.11 too). Suite
677→678 passed, 0 failed.

**2026-06-15 — Audit fixes landed in bulk: 107/111 closed.** Drove the
open findings down via a parallel worktree fix-workflow (one agent per
file, re-verify + behaviour-preserving fix + offscreen-QApplication
regression test). H12 was already fixed (stale checkbox; shared `3d60e14`
with H10) — corrected. 75 open → 69 fixed + 3 already-fixed + 0 refuted +
5 deferred-cross-file. Landed from worktree diffs after a full-suite gate
that caught two cross-fix regressions (eyedropper M25 vs canvas-no-op L16,
reconciled with a new `SpriteCanvas.gesture_finished` signal; Kivy M34
call-site over-reach, reverted to absolute coords). Suite **1076 passed,
0 failed** (41 pre-existing pytest-qt `qapp` errors on 3.11). 11
per-subsystem commits `b6b27da`..`4d76181`. The 4 deferred-cross-file items
(M31, M34, L5, L8) were then ALL closed in the same session with their
coordinated second-file edits + tests. **The full 2026-06-11 audit is now
111/111 closed** (suite 1091 passed, 0 failed). Untracked tracked-for-later
remainder (not a registry item): M30 belt-and-braces runtime alias/'state'
field in action_executor.py. (The other one, L4 WA_DeleteOnClose on
PlaygroundRunnerWindow, was already fixed by commit `f389035` — both
PlaygroundRunnerWindow and ThymioPlaygroundWindow set Qt.WA_DeleteOnClose;
verified 2026-07-15, this note corrected.)

**2026-06-11 — Full-codebase audit (18 finders, adversarially verified):
111 confirmed findings.** Unlike the earlier single-batch audits, every
finding here survived adversarial verification against the actual code
(and highs got 2 extra refutation votes), with the known-rejected list
baked into the finder prompts. Registry with checkboxes:
`docs/FULL_AUDIT_2026-06-11.md` — 15 high / 61 medium / 35 low. Work in
audit order; re-verify each claim before fixing (leads, not ground truth)
and land each fix with a regression test. This supersedes the "14 medium
+ 9 low remain open" note above — the 2026-06-03 registry is fully closed
(all 30 checkboxes flipped).

**2026-06-12 — All 15 highs from the 2026-06-11 audit fixed.** One
session on the Windows box, one commit per finding (H13+H14 and H6+H7
share commits — same root cause), each with a dedicated regression test
file and the registry checkbox flipped with the commit hash. Suite went
724 → 808 passed, 0 failed. Highlights: the Kivy export generator now
implements the runtime's GM skip-next conditional scoping and handles
test_instance_count/test_variable (H6/H7), and the Mobile (Kivy) dialog
path works at all (H9); mouse events fire from the flat keys writers
actually emit (H11); zip-backed save state resets on project switch (H2);
emptied rooms stay empty via `_rooms_loaded_this_session` registration at
all authoritative-memory points plus orphan side-file cleanup on
delete/rename (H3); asset delete and sprite-animation config operate on
the live model and `force_project_refresh` no longer reloads from disk
(H13/H14); the code editor fills paired-attribute identity values (H4)
and preserves Thymio if/else verbatim instead of dropping the else (H5).
**61 medium / 35 low remain open** — pick up from the registry, top of
the Medium section. Box-specific gotcha: commit messages containing
double quotes must go through `git commit -F <file>` here (PowerShell 5.1
mangles inline quoting).

**2026-06-13 — First 20 mediums (M1–M20) from the 2026-06-11 audit fixed.**
One Windows-box session, one commit per finding (M3/M4/M5 share a commit —
same rename path; M9/M10 share one — duplicate findings; M17 was already
resolved by H11), each with a regression test and the registry checkbox
flipped (`77974b2`..`5c9418b`). Suite 808 → 890 passed, 0 failed.
Highlights: Thymio choice params recover their index from the saved
label so sensors/sounds aren't all 0 (M1); replace_sprite_image copies +
validates before deleting the old art (M2); asset rename keeps room order
and updates references inside then/else branches and 8-layer backgrounds
(M3/M4/M5); Auto-Save settings persist to the editor config startup reads
(M6); zip projects reopen from Recent (M7); Test Game and project-switch/
close now sync detached + modified editors (M8/M12); the export progress
dialog can't be Esc-dismissed into a GUI-thread freeze (M9/M10);
re-opening a dirty asset focuses its editor instead of duplicating it
(M11); export targets route by stable id not translated text (M13);
ThymioConfigDialog marks the config custom so restrictions stick (M14);
editor Ctrl+S/F5 no longer collide with the IDE menu (M15); Blockly
workspace XML is cached so the layout saves (M16); plain assignments
aren't misclassified as Thymio variables and the handler preserves value
types (M18); conditionals always render a body — no bodiless if/for (M19);
execute_code binds `self` and a `keyboard.check()` shim (M20).
Reminder: do NOT round-trip docs/FULL_AUDIT through PowerShell
Get-Content/Set-Content (it mangles the em-dashes to mojibake) — edit the
registry only with the Edit tool.

**2026-06-14 — Mediums M21–M40 from the 2026-06-11 audit fixed.** One
Windows-box session, commits grouped by shared file/root-cause (`17dcec2`
M21+M22 playground ports/redo; `ac49bfd` M23+M24 room Clear/Shift-All undo
+ already_added redo; `67d39e0` M25+M26 eyedropper drag + frame undo;
`e2f7482` M27 set_sprite `<self>`; `7b008ee` M28 room nav sentinels in
goto/check_room; `547d024` M29 test_health operators; `e9f4897` M30+M31
key_pressed arrow names + mouse_check; `c3650ca` M32+M33 aseba .aesl XML
envelope + stray `end`; `097c7b1` M34 Kivy check_collision_at;
`98ba8b2` M35+M36+M37 Kivy keyboard_release / grid heuristic / dup-method
merge; `7891d7c` M38+M39 desktop export name-sanitize + copy-failure
reporting; `2002957` M40 GMK image-dimension clamp). Each finding has a
dedicated regression test file and the registry checkbox flipped. Suite
890 → 958 passed, 0 failed. Notes worth carrying forward: the M30 fix
changed the key_pressed canonical values to lowercase runtime names and
dropped the misleading Held/Released states (updated
`tests/test_audit_regressions.py` accordingly); the M34 fix changed the
Kivy collision codegen to offset-from-self (updated `tests/test_exporters.py`).
The Kivy GameObject/Scene templates are `.format()` strings — literal `{`/`}`
must be doubled; the base-object template ends with `code.format(grid_size=…)`.

**2026-06-14 — Mediums M41–M61 fixed; the entire Medium section (M1–M61) is
now closed.** One Windows-box session, commits grouped by file/root-cause:
`c3ea583` M41+M42 (gmk zlib-bomb cap, Roberta LED red/green/blue keys);
`900050f` M43 (exit_event propagates through nested lists via
`_execute_action_list_inner` — also fixed a discovered if_condition
then/else **double-run**); `ad0eb54` M44+M45 (Blockly `sub_actions` honored in
the generic conditional dispatch; `other` bound in execute_code/script — M45's
`self` was already done in `82f9b04`); `f267939` M46+M47 (create_random/moving
set `_depth_dirty`; create_moving resolves parent inheritance); `6d090e4`
M48+M49 (room_speed→fps; per-frame loops iterate `list()` snapshots);
`2eff238` M50 (push_back_instance works in bbox-world coords); `a469669`
M51+M52+M53 (restart_room carries persistent instances; restart_game rebuilds
every visited room; **create event guarded once-per-instance via
`_create_fired` inside `execute_event`** — this is the single chokepoint, don't
re-add per-call guards); `aa8ae31` M54 (modal dialogs clear held keys on KEYUP
via `_release_held_key_silent`); `aa15976` M55+M56 (Thymio ground sensors
sample forward; differential-drive rotation sign flipped for the y-down frame);
`51a9884` M57 (`compile_translations.should_compile` skips split .ts without a
split set); `7276a09` M58 (resource_packager honors real file extensions via
`_asset_archive_path`); `96264ed` M59 (playground side-file cleanup on
delete/rename — rooms/objects already done by H3); `6667fc6` M60+M61
(force_project_refresh already fixed by H13/H14 + guard test; properties-panel
object edits write through to the live model when no editor is open). Suite
958 → 1015 passed, 0 failed. Re-verification caught three findings already
resolved by prior work (M45, M60, and M59-for-rooms) — confirming the
audit-is-a-lead discipline. **All 61 mediums closed.**
Box gotcha: the Edit tool's atomic write leaves `*.tmp.<pid>.<hash>` artifacts
on the Dropbox folder that `git add -A` will grab — committed two by accident
this session, then added `*.tmp.*` to `.gitignore`; prefer targeted `git add`.

**2026-06-15 — Lows L1–L35 fixed; the entire 2026-06-11 audit is now closed.**
One session, commits grouped by area: `413e39f` L25/L26/L27 (keymap numpad/
punctuation, BMP dim cap, Roberta RGB guard); `723c748` L20/L21/L22 (kivy ASCII
package name, show_message repr, bg filename); `26c8c71` L10 (code-parser string
escaping); `c141572` L15/L16/L17 (sprite floor-pixel, no-op gesture, pause
playback); `b9f3505` L12/L13 (room scaled hit-test, duplicate clipboard);
`b637c4d` L18/L19 (check_empty dropdown, render unknown actions); `8358738`
L28/L29/L30/L31 (inherited create lookup, collision-context clear, outside_room
origin, thymio sim-None guard); `c17f8c1` L8/L9 (new-project description,
export-option checkboxes); `986ed06` L23/L24 (android cleanup-on-failure, cancel
sentinel); `e053d2b` L14 (script editor undo→document); `7125c7a` L11 (playground
props refresh on undo); `0f4824b` L32 (sprite-delete ref cleanup — guard test;
resolved by live delete path + M60); `9b563fe` L6 (single-sourced sprite-file
merge whitelist); `f389035` L2/L3/L4/L7 (import save-flush, test_game stderr
leak, playground-window WA_DeleteOnClose, zip temp cleanup on quit); `8b20517`
L33/L34/L35 (theme foreground, atomic project.json save, tutorial setOpenLinks);
`2a74aa4` L1 (tutorial empty-index placeholder); `03453c2` L5 (open_editors
keyed by composite "<category>:<name>"). Re-verification found several already
resolved by earlier high/medium work (L32, L7-project-switch, L29-adjacent). The
L5 fix touched core editor lifecycle (open/close/float/reattach/rename/delete);
editors now carry `_open_editor_key` and `_canonical_category` normalizes the
singular/plural asset-type vocabulary that differs between the rename and delete
signals. Suite 1015 → 1080 passed, 0 failed. **All 111 audit findings (15 high /
61 medium / 35 low) are closed.**

**2026-06-09 — Runtime-core audit (Batch A): most rejected, room-dimension
bounds added.** A 9-finding audit of `game_runner.py` / `action_executor.py` /
`constants.py`. Verified each against code first (the established
audit-is-a-lead methodology); only finding #6 survived. **Do not re-raise the
rejected items** — this is the 5th audit in this class:
- **`eval()` "HIGH" (action_executor.py:2014) — rejected.** Already double-gated:
  `{"__builtins__": {}}` *and* a regex whitelist
  `^[\d\s\+\-\*\/\%\(\)\.\,a-zA-Z_]+$`. The audit's PoC
  `__import__('os').system('rm -rf ~')` contains `'` and `~`, fails the regex,
  and returns 0 — it cannot run. Swapping in an AST evaluator would also break
  the intentionally-supported `random()`/`irandom()`/`choose()` calls. (A second
  eval at :4219 is the GML-expression path, also `__builtins__`-stripped.)
- **`exec()` "HIGH" (action_executor.py:2882, :2966) — rejected.** This is the
  deliberate `execute_code`/`execute_script` power-user feature; GMK imports
  route script calls through it. Clamping `__builtins__` to a safe subset would
  break legitimate imported scripts. Threat model ("malicious *shared* project")
  is the same one rejected for `load_project` above — projects are user-authored
  / samples / self-exported; no untrusted channel, runs as the user.
- **#3 "infinite slide loop" (game_runner.py:3142) — rejected.** `while moved +
  1.0 <= remaining` increments `moved` unconditionally each pass; it terminates
  in `ceil(|speed|)` steps. Not infinite. Its only real edge (a pathological
  speed) is data, not a loop bug.
- **#4 "unbounded caches" — rejected**, same reasoning as the 2026-06-09 sprite-
  cache rejection above (room/project-scoped, bounded by asset/room count).
- **#5 "dialog speed-restore leak" (game_runner.py:4585) — already correct.** The
  restore loop already iterates live instances under `if id(instance) in
  saved_speeds`, exactly the audit's proposed fix.
- **#7 rate-limiting / #8 div-by-zero — non-issues** (audit itself marks #8 ✅).
- **#9 "split the 6.5k/8k-line files" — declined** per stability-over-features.
- **#6 room-dimension validation — ACTED.** A `GameRoom` surface is allocated at
  `width x height`, so a corrupt/hostile project.json setting 0, negative,
  non-numeric, or absurd dimensions would crash pygame or exhaust memory at room
  build. Added module-level `_sane_room_dimension` + `ROOM_MIN_DIMENSION` (64) /
  `ROOM_MAX_DIMENSION` (16384) in `game_runner.py`; `GameRoom.__init__` routes
  `width`/`height` through it (coerce to int, fall back to default on
  `TypeError`/`ValueError`/`OverflowError` incl. NaN/inf, then clamp). Coverage:
  `tests/test_room_dimension_bounds.py` (12 tests). Suite 678→690 passed, 0
  failed.

**2026-07-17 — Raycast (`raycast_1`) bug hunt: two real rendering bugs
found and fixed, plus billboard sprites shipped.** Follow-on to the
2026-07-16 "complete rethink" (thin edge-walls) session-notes entry —
after that rearchitecture landed, the user reported (with screenshots,
running via IDE Test Game) "press Down from spawn, end up outside the
map." Both bugs were purely in `_render_raycast_view`/`_cast_ray`
(`runtime/game_runner.py`) — the player's logical position and the wall
topology were re-verified correct at every step; nothing here touched
collision.
- **Bug 1 (`5284cb7`): miss-column phantom wall sliver.** `_cast_ray`
  returned a distance/side pair even when the DDA loop reached
  `render_distance` without hitting a registered wall edge (a legitimate
  case — any column facing an opening wider than render distance). The
  render loop drew a wall strip anyway (`dist==max_cells`, a thin sliver
  right at the horizon since strip height is inversely proportional to
  distance), shaded by whatever `side` the last *non-hit* DDA step
  happened to leave set — flips per column, producing the reported
  alternating dark-red/black stripe band. Fixed: `_cast_ray` now returns
  a third `hit: bool`; the render loop skips the strip on a miss.
- **Bug 2 (`8772e53`): camera ray origin was the sprite's top-left
  corner, not its center.** Every instance in a grid maze — walls and
  the player alike — sits at exact multiples of `cell_size`, so a player
  at rest against a wall (constant in a corridor maze) has a raw `(x,
  y)` landing exactly on a wall-bearing grid line. DDA rays cast from
  precisely on that line hit it almost immediately and inconsistently by
  angle, reading as "a wall fills my screen" when the real corridor
  ahead was wide open. Fixed by offsetting the ray origin to the
  occupied cell's center (`+ half the camera's cached sprite
  width/height`). **General lesson, worth remembering for any future
  raycast/grid-geometry work**: this class of exact-grid-line coincidence
  is a real, recurring hazard in this DDA implementation — anything that
  casts a ray from a position/computes geometry using raw instance `x/y`
  in a grid-aligned map is at risk of it, not just the camera. The
  billboard occlusion check below reuses `_cast_ray` and inherits the
  same theoretical exposure (accepted as-is; realistic float positions
  essentially never land exactly on a grid corner in practice).
- Both bugs were hard to reproduce in a hand-built minimal test — a
  `GameRunner`'s rooms are loaded straight from JSON and **instances
  don't get `_cached_object_data`/sprite-derived `_cached_width/height`
  resolved until `set_sprites_for_instances` runs** (normally inside
  `run()`'s real startup); a partially-initialized room silently
  produces an empty or wrongly-shaped wall set and makes a naive test
  pass for the wrong reason. Both regression tests ended up going
  through the real `GameRunner.run()` loop (matching the existing
  `TestRaycast1SampleSmoke` harness pattern: `pygame.event.post` +
  `_FakeClock` + a tick-hook), not a hand-initialized room. Also:
  pixel-sampling the rendered output can't distinguish some pre/post-fix
  states, because wall-strip height caps at full screen height for any
  distance <= `cell_size` — a ~3px pre-fix reading and a ~30px post-fix
  reading render pixel-identically. Where that mattered, the test
  intercepts the real `_cast_ray` call args instead of sampling pixels
  or reimplementing the fix's own math inline.
- **Feature (`2c14c67`): billboard sprites.** Once the two bugs were
  fixed, the user noted `obj_goal` was invisible in the first-person
  view — expected, since `_render_raycast_view` only ever drew *solid*
  instances as wall strips; non-solid sprited instances (goals, pickups,
  monsters) had no representation at all. Added a scoped-down first cut
  of the plan doc's Phase 6 (originally sequenced last/optional): every
  visible, non-solid, sprited instance now draws as a camera-facing
  billboard, scaled by the same fisheye-corrected-distance formula wall
  strips use, with **real per-column occlusion** (reuses `col_wall_dist`,
  the corrected distances the wall pass already computes that frame —
  not a single approximating ray) and farthest-first painter's-algorithm
  sorting for overlaps. `docs/RAYCAST_2_5D_PLAN.md`'s Phase 6 section and
  `samples/raycast_1/README.md` both updated; not done (deliberately):
  sprite rotation/facing, alpha blending.
- Suite 1858 → 1859 → 1864 passed, 0 failed across the three commits.
  Full root-cause detail and the exact reproduction numbers are in
  `docs/RAYCAST_2_5D_PLAN.md`'s "Miss-column render artifact" and
  "Follow-up" sections. **Next up on this feature** (per the plan doc,
  still open): flat textures for walls/floor/ceiling, then an outdoor
  sky/horizon, then HTML5/Kivy export parity — this session's fixes and
  the billboard cut were both reactive (user-reported), not scheduled
  roadmap work, so the phase order in the plan doc is otherwise
  unchanged.

**2026-07-19 — Raycast HTML5 + Kivy export parity: the first-person view
now renders on all three targets.** Executed the `docs/RAYCAST_2_5D_PLAN.md`
Phase 2/3 unit sequence, one commit+push per unit (session-limit
discipline). The three renderers share NO code (three hand-written copies:
desktop `runtime/game_runner.py`, HTML5 `export/HTML5/templates/engine.js`,
Kivy `export/Kivy/kivy_exporter.py`), so a parity test locks the DDA core.
- Unit 1 `d74ca33`: registered `set_facing_angle` + `enable_raycast_view`
  actions (`events/action_types.py`, category "3D View").
- Unit 2 `fed4894` + 3a `2180662`: HTML5 walls, then sky + billboards in
  engine.js (`test_html5_raycast.py`).
- Unit 4a `e4fa670`: Kivy movement/action parity — `facing_angle` on the base
  object, `raycast_camera` on the scene; codegen for `set_direction_speed`
  (the Kivy generator dropped it, so the FPS player never moved),
  `set_facing_angle`, `enable_raycast_view`.
- Unit 4b `9c37cfd`: Kivy wall renderer (`_build_raycast_walls`/`_cast_ray`/
  `_render_raycast` ported into the scene, opaque `InstructionGroup` overlay
  on `canvas.after`). **Key y-flip decision: run the ENTIRE DDA in GM y-down
  space** — convert each Kivy y-up instance back via
  `room_height - y - image_height` — so wall-keys/tex_u/facing_angle match
  desktop verbatim; only the final draw flips, and wall strips are vertically
  symmetric so just the ceiling/floor fills swap halves. Textured strips reuse
  the sprite animator's `texture.get_region(tex_x,0,1,h)` column-slice (no
  hand-set `tex_coords`).
- Unit 5a `4a9493a`: Kivy sky panorama + billboards (per-ray-column occlusion
  via a `col_wall_dist` array).
- Unit 6 `b0d8da0`: `tests/test_raycast_export_parity.py` — desktop
  `GameRoom._cast_ray` vs the Kivy scene `_cast_ray`, fed identical wall edges,
  **exact** (<1e-9) over a 260-ray matrix; HTML5 gets structural parity (no JS
  engine in CI); + a facing-angle-convention pin across all three sources.
- README `293206d`: dropped the "desktop-only" caveat.
- Suite 1864 → **1912 passed, 0 failed**. New tests: `test_kivy_raycast.py`
  (14, incl. a stub-kivy headless harness that drives the real generated
  renderer via `cls.__new__` + controlled geometry), `test_raycast_export_parity.py` (3).
- **DEFERRED, both blocked on the same thing — a per-target GL/browser timing
  spike for the low-res per-pixel floor cast, which can't be measured
  headlessly:** unit 3b (HTML5 floor, JS `ImageData`) and 5b (Kivy floor,
  `blit_buffer`). Until then HTML5/Kivy fall back to the flat `floor_color`
  fill (walls, sky, billboards are all real there). Everything else in the plan
  doc is closed; those two are the only open raycast items.
- Landmine confirmed: the Kivy scene class is a `.format()` template
  (`kivy_exporter.py` ~line 1430-1990) — every literal `{`/`}` in added code
  must be doubled. Commit messages with double-quotes/parens must go through
  `git commit -F <file>` (PowerShell 5.1 here-strings mangle them).

**2026-07-19 — Audit cleanup, GMK fixes, and the `raycast_2` sample.** One long
Windows-box session, one commit per unit, all pushed.
- **Audit registries all closed.** `EXPORT_AUDIT_2026-07.md` and
  `GMK_IMPORTER_HARDENING_PLAN.md` are now fully closed; `EXPORT_SYSTEM_STATUS.md`
  was reconciled (a stale Jan-2026 snapshot — corrected line counts, non-existent
  modules, bucketed its checkboxes into done/feature/QA/docs). Real fixes landed:
  `multi_choice` param widget for list-valued action params (`32396d5`,
  `start_moving_direction` directions now a 3×3 checkbox picker);
  draw-action UI metadata `relative`/`image` alias (`5e209b7`); GM Set-Font
  `align`→`halign` in the importer + runtime fallback (`6cafe7b`); PyInstaller
  `.spec` path escaping across exe/linux/macos (`c4dd07b` — apostrophe/`\U`
  crashes; the regression test caught a macos icon bug the finder missed); Kivy
  asset same-basename clobber → name-keyed export filenames (`c496ef8`).
- **`raycast_2` sample — COMPLETE (Units 1–6, plan `docs/RAYCAST_2_SAMPLE_PLAN.md`).**
  A two-level Doom-style game built with **zero engine changes** (all authoring
  on the finished raycast engine): hand-built recursive-backtracker mazes run
  through raycast_1's edge-wall formulas; collectible gems + score; a patrolling
  billboard monster + lives; a `test_instance_count` gem-gated exit; a second
  crystal-cavern room via **per-room camera controllers** (`enable_raycast_view`
  with an explicit `camera_object='obj_person'` — moved off `obj_person` so each
  room's controller can carry its own texture theme). Shipped: Welcome-tab entry
  + translations ("Lancer de rayons — Niveau 2"), smoke runner, 3-target
  playtest. Commits `848f774`(1) `15ed197`(2) `d2fd437`(3) `790945e`(4)
  `e80fbdf`(5) `b957891`(6). Suite ended **1961 passed, 0 failed**.
  - **Sample-authoring landmine (cost a real bug):** `create` **re-runs on
    `restart_room`**, so score/lives init belongs in **`game_start`** (fires
    once, survives a room restart) — `set_lives` in `create` reset lives to full
    on every death. `enable_raycast_view` must stay in `create` (the camera
    re-arms per room entry; `restart_room` builds a fresh room with
    `raycast_camera=None`).
  - **`test_instance_count` param key is `number`, not `count`** — the desktop
    runtime reads `number` (maze_3's `count` works only by the 0-default
    coincidence); all three targets read `number`.
- **Open engine follow-up (NOT started):** in-view HUD compositing —
  `draw_score`/`draw_lives` over the raycast view (3 targets). Right now
  `_render_room` early-returns after `_render_raycast_view`, so raycast games
  show score/lives only in the desktop window caption (invisible on HTML5/Kivy
  exports). Plan: `docs/RAYCAST_HUD_PLAN.md`; tracked in `RAYCAST_2_5D_PLAN.md`.

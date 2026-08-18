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
- **On-screen text in a project must be QUOTED or it gets evaluated.**
  `ActionExecutor._parse_value` routes any string containing `* + - / %` to the
  expression evaluator, so a `draw_text` reading `W A S D - Move` renders as
  `0`. Wrapping it in double quotes inside the JSON (`"\"W A S D - Move\""`)
  makes `_parse_value` return it verbatim — that check is explicitly
  `not value_str.startswith('"')`. Existing sample text only ever escaped this
  by accident (`Lives:` and `M = map` use `:` and `=`, which are not
  operators); block_world_1's help overlay was the first sample text to
  contain a dash and the first to break. Guarded now by
  `tests/test_sample_visible_text.py`, which fails on any displayed string
  `_parse_value` would evaluate.

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
111/111 closed** (suite 1091 passed, 0 failed). Two untracked (not registry
items) remainders were noted here and both are now resolved: **L4**
(`WA_DeleteOnClose` on `PlaygroundRunnerWindow`) was already fixed by commit
`f389035` — both `PlaygroundRunnerWindow` and `ThymioPlaygroundWindow` set
`Qt.WA_DeleteOnClose`; verified 2026-07-15. **M30** (belt-and-braces runtime
alias/`'state'` field in `action_executor.py`) turned out to be
`events/conditional_editor.py`'s `key_pressed` condition widget: a "Is:"
dropdown (`self.key_state`) that offered exactly one always-selected choice
("Pressed (held down)") and saved a `"state"` parameter the runtime's
`key_pressed` handler (`action_executor.py`) never read — real dead weight,
not a bug, since there was only ever one selectable value. Removed the
dropdown and the `"state"` field entirely (2026-07-21); `key` is now the only
`key_pressed` parameter. `tests/test_audit_regressions.py`'s
`test_key_pressed_subfields_are_canonical` updated to assert `"state" not in
out` instead of `out["state"] == "pressed"`.

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
- ~~**DEFERRED, both blocked on the same thing — a per-target GL/browser
  timing spike for the low-res per-pixel floor cast, which can't be measured
  headlessly:** unit 3b (HTML5 floor, JS `ImageData`) and 5b (Kivy floor,
  `blit_buffer`). Until then HTML5/Kivy fall back to the flat `floor_color`
  fill (walls, sky, billboards are all real there). Everything else in the
  plan doc is closed; those two are the only open raycast items.~~ **DONE,
  same day (2026-07-19).** The throwaway timing spike (`70f0d0de`) cleared
  the concern; unit 3b landed in `031cc1e1` (HTML5, `castFloorPlane()` /
  `ImageData`) and unit 5b in `796daea9` (Kivy, `_floor_buffer()` /
  `blit_buffer`), both same-day follow-ons to this note, which was written
  mid-session before they landed and never updated afterward — a stale-doc
  gap, not a real regression. `4021c95d` dropped `raycast_1`'s README
  "floor is desktop-only" caveat once both landed. Confirmed still current as
  of 2026-08-14: both are tested (`tests/test_html5_raycast.py`,
  `tests/test_kivy_raycast.py`, `tests/test_raycast_view.py::TestFloorCasting`)
  and exercised by every bundled raycast sample (`floor_texture` is set on
  every camera object in `raycast_1`–`4`) — the flat `floor_color` fill that
  remains in both exporters is only the fallback for a camera with no
  `floor_texture` configured, not the default path. The raycast 2.5D arc has
  no open items.
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

**2026-07-20 — Sample guides: French translations complete (15/15).** The
decision behind this: sample *messages* stay **English** — they're written with
ordinary `show_message` actions, so students author them in their own language;
auto-translating them would be translating the student's own content. What gets
translated is the **guides**, and the raycast samples' guides explain the
messages. Infra (`b1ef0c2`): `SampleDocsDialog.guide_path()` resolves
`README.<lang>.md` next to `README.md` with an **English fallback**, so a
missing translation degrades gracefully — translations can land per-sample,
per-language, with no partial-rollout risk. `_guide_language()` must go through
the `get_language_manager()` **singleton** (it's an instance method — calling it
on the class silently pins every guide to English; pinned by a test).
- Commits: `b1ef0c2` (infra + raycast_2), `5b08ef9` (maze_1–4), plateforme_1,
  `70812f9` (plateforme_2, treasure, views_1), `4b373a0` (views_2,
  plateforme_3), `7cbb9dc` (raycast_1), `f056d3d` (match3_1/2), `792496e`
  (match3_3 + test fix). Suite **1971 passed, 0 failed**.
- **Landmine this exposed:** any test asserting English prose from a sample
  guide is language-dependent once a `README.fr.md` exists — on a
  French-configured box `guide_path()` correctly returns the French file and the
  test fails for the wrong reason. `test_renders_selected_readme` hit exactly
  this; fixed by monkeypatching `_guide_language` to `'en'`. Do the same for any
  new guide-rendering test.
- Convention used throughout: **technical identifiers stay in English**
  (object/file/action/attribute names, JSON keys, test paths, embedded Python)
  so the guide keeps matching what the IDE and repo actually show; only prose,
  table headers and diagram labels are translated. Welcome-tab display names
  match the existing `pygm2_fr.ts` strings.
- **Cost measured** (the user's stated reason for doing French first): one
  language ≈ **40% of a session** for all 15 guides (~13,500 English words).
  Budget accordingly before starting another; the English fallback means the
  other 6 IDE languages are safe to leave untranslated indefinitely, and
  translating only the languages students actually use is a legitimate choice.

**2026-07-20 — In-view HUD (3 targets) + the `raycast_3` sample.** Plan:
`docs/RAYCAST_HUD_PLAN.md`, Sessions A–D all closed; only **Session E (minimap)**
is open, and it's gated on writing `docs/RAYCAST_MINIMAP_PLAN.md` first (it needs
world-space projection, which the HUD work explicitly scoped out).
- **Engine — HUD compositing.** Every target drew the first-person view then
  returned before the per-instance draw pass, so raycast games showed score/lives
  only in the desktop window caption. Desktop `341f5c4` (`run_draw_event` split
  out of `GameInstance.render`; `_render_draw_events` after
  `_render_raycast_view`), HTML5 `d11550b`, Kivy `fd2402f`, parity + sample
  `7018e3a`. **Kivy had two traps, both real:** the HUD group must be
  *scene-level* on `canvas.after` (a child widget's group can never rise above
  the scene's opaque `_raycast_group`), and it must flip y against
  **`display_height`**, not `room_height` as `_render_draw_queue` does.
- **`380abd2` — two PRE-EXISTING export bugs found en route, both divergences
  from the desktop runtime.** (1) **Draw depth order**: engine.js sorted
  *ascending* (inverting sprite z-order) and the Kivy exporter **ignored `depth`
  entirely** — the word appeared nowhere in `export/Kivy/`. Four samples rendered
  wrong on those targets: `maze_3`, `maze_4`, `plateforme_3` (player depth −100
  drew *behind* the exit at 100), `treasure`. Kivy needed depth plumbed end to
  end; note widget order *is* z-order there and Kivy draws children in REVERSE,
  so the child path keeps `children` ascending while the Fbo path inserts
  descending. (2) **Draw-event visibility**: both targets ran an invisible
  instance's draw event; GameMaker doesn't. Fixing this made
  **`obj_hud` needing `visible: true` load-bearing** — a HUD on an invisible
  camera controller silently draws nothing.
- **`84707a4` — health was DISPLAY-ONLY on the exports.** `set_health` /
  `draw_health_bar` exported fine, but `test_health` and `test_lives` had no Kivy
  codegen and `no_more_health` existed on *neither* export target, so any
  conditional on health silently vanished and a "you died" handler never fired.
  The plan's "engine risk: none" claim was wrong because it only checked *draw*
  actions. **Lesson, now in the plan: when a sample introduces a mechanic, verify
  the conditionals and events it needs on every target, not just the actions that
  draw it.**
- **`raycast_3`** (`59cd8e6` `4dbe128` `f2c9967` `0587963`): two-level FPS where
  monsters cost **health** (−25, with a 45-step `alarm_0` invulnerability window)
  rather than a life; medkits +40; `no_more_health` → −1 life + refill + restart;
  HUD = score top-left / lives top-right / health bar bottom-left (**opposite
  corners** so a wide bar can't collide with a growing score). Room1 is the
  harder half (5 monsters, 2 medkits) with the ice theme via `obj_cam1`.
  **Its maze generator is committed** (`tools/gen_raycast_3_maze.py`) — unlike
  `raycast_2`'s throwaway script, so these rooms can be regenerated; a test pins
  room JSON against the generator. Seeds are *chosen*: `check_start()` asserts
  the spawn cell opens east (the player spawns facing east — a walled start means
  beginning nose-to-wall, which passed every structural test) and that all 225
  cells are reachable.
- **Runtime facts worth keeping:** collision events fire when instances **START**
  overlapping (`_active_collisions`), so a continuous overlap deals exactly one
  hit — pinning a player on a monster can never produce a second, which looked
  like a bug and wasn't. Alarms/collisions dispatch via `execute_action_list` /
  `execute_collision_event`, **not** `execute_event`, so a spy on the latter sees
  neither.
- **HUD layout decided (`f21dc80`): corner overlays, NOT a DOOM bottom bar.** The
  renderer always fills the window and hardcodes the horizon at `h/2`;
  `enable_raycast_view` has no viewport param. A bar either leaves the horizon at
  true screen centre while the visible centre moves up (permanent upward-tilt
  feel) or needs a viewport height threaded through every pass of three
  hand-written renderers. A `viewport_height` param remains a legitimate later
  feature, pairing naturally with the minimap.
- Suite **1971 → 2028 passed, 0 failed**; smoke **16/16**.
- **Open, needs human eyes:** nobody has *watched* `raycast_3` render in a
  browser or on Android, nor `plateforme_3` after the depth fix. Structure and
  codegen are verified; the visual playtest isn't.

**2026-07-20 — Minimap (`draw_minimap`), Session E.** Plan
`docs/RAYCAST_MINIMAP_PLAN.md`, **all 4 units closed**; the raycast HUD/minimap
arc is complete. Commits `0ff7edb` (plan) `a1784fc`+`cadc341` (desktop)
`71bbb99` (HTML5 + Kivy + parity + sample).
- **The design finding that shrank the work:** the HUD plan assumed each target
  needed a new minimap *renderer*. It didn't. All three already cache the same
  derived wall-edge sets and already render `rectangle`/`line` draw commands, and
  the action can reach the room at queue time. So `draw_minimap` is a **MACRO
  action** — it emits ordinary primitives, **no renderer changes anywhere**, and
  the parity surface is pure geometry (numerically comparable like `_cast_ray`).
  `build_minimap_commands()` in `runtime/action_executor.py` is THE single source
  the other two mirror.
- Design: **north-up** (rotation would widen the parity surface for no teaching
  value), **no fog of war** (needs per-room persisted state on 3 targets — scoped
  out, not forgotten), **walls + player only** (showing pickups trivialises a
  gem-gated maze), whole-map scale rather than a radar window.
- **Kivy needed the M34 two-halves pattern:** codegen emits single-line
  expressions, but a minimap needs loops — so the generator emits a CALL to
  `GameObject._draw_minimap`, generated into `base_object.py`. Verified the
  emitted call's arity matches the def (6/6) and both files compile.
- **Two bugs I shipped in Unit 1 and caught in `cadc341`** — both invisible to a
  test that only checked *that* walls were drawn: (1) **`_find_raycast_camera` is
  KIVY-ONLY**; desktop resolves the camera via `_find_first_instance`, so
  `getattr` returned None and no player marker was ever drawn; (2) the marker
  used the camera's raw x/y (sprite corner) instead of the **origin-aware cell
  centre the rays are cast from** (`game_runner.py:2053`), parking it half a
  sprite off. **Lesson: assert WHERE a marker lands, not that something drew.**
  Same shape as the room1-HUD test earlier the same day.
- Wall sets are unordered → all three targets **sort** before emitting, or a
  command-level parity diff flaps.
- Landmine for future sample tests: `raycast_3`'s `obj_hud` now ships a
  `draw_minimap`, so a test that *appends* another captures TWO minimaps and
  asserts the union of two squares. Re-point the existing action instead.
- Suite **2028 → 2046 passed, 0 failed**; smoke **16/16**.
- **Still needs human eyes** (unchanged): nobody has *watched* `raycast_3` render
  in a browser or on Android, nor `plateforme_3` after the depth fix. Also
  untested on real hardware: Kivy rebuilding ~250 `Line` instructions per frame
  for the minimap — the plan's `range` parameter is the escape hatch if it bites.

**2026-07-21 — DOOM status bar (viewport_height + draw_doom_hud) + `raycast_4`.**
Plan `docs/RAYCAST_DOOM_HUD_PLAN.md`, **all 6 units closed**. Reopened/reversed
the corner-overlay decision `RAYCAST_HUD_PLAN.md` made for raycast_3 — a
DOOM-style bottom bar for a NEW sample, raycast_1–3 untouched.
- **`viewport_height` letterbox** on `enable_raycast_view` (default 0 = full
  height, backward-compat asserted): shrinks the 3D view into the top band and
  reserves a black band below for the bar. Desktop `1d207db`, HTML5 `dc90cc1`,
  Kivy `896a228`. **Kivy is y-UP so the reserved band is at the BOTTOM
  (`[0, h-view_h)`), horizon at `h - view_h/2`, walls clamp their bottom to
  `view_bottom` not 0** — the mirror image of desktop/HTML5; `_floor_buffer`/
  `_render_floor_plane` each take their own `view_h`.
- **`draw_doom_hud`** `25e94e9`: a MACRO action like draw_minimap —
  `build_doom_hud_commands()` emits rectangle/line/text/sprite/lives only, no
  new draw-queue type. Health bar + number, health-reactive **face** portrait,
  score, lives, objective counter. Face frame = `doom_face_frame()` even-bucket
  map (0=healthiest), pinned identical across targets. Kivy codegen emits a
  BOUNDED inline `dict(...)` append block (not the minimap's call-out — no loop).
- **Unit 4a `e3280e1`:** the `sprite` draw-queue command ignored `subimage` on
  HTML5 + Kivy (drew the whole spritesheet); fixed to crop the frame — needed
  for the face icon, generically useful. A test compiles the generated Kivy
  base_object.py to catch the `{{}}` brace-doubling.
- **`raycast_4` `62f04bf`** (+ ship `527d7bd`): single-room FPS built AROUND the
  bar. **obj_person is BOTH the camera AND the HUD drawer** so the key counter
  is its own instance var (`keys`) — draw_doom_hud's objective expression then
  resolves to `self.keys` identically on all 3 targets, sidestepping
  global/cross-instance expression resolution. New art: 4-frame face strip
  (spr_face), gold key (spr_key). Maze DELEGATES to gen_raycast_3_maze.
- **Two real bugs Unit 6 surfaced, both fixed with tests:** (1) the export
  config-BUILDERS (Kivy codegen + HTML5 `case 'enable_raycast_view'`) never SET
  `viewport_height` in the camera dict, though Units 2/3 made the RENDERERS read
  it — so exports ignored the letterbox entirely. (2) **The runtime fires only
  ONE side of a collision pair's handlers** — obj_person.collision_with_obj_key
  fired but obj_key.collision_with_obj_person didn't, so a key counted but never
  destroyed/scored. Fix: put all pickup logic (count + score + destroy other) on
  the ONE reliably-firing handler; the collectible is passive.
- Suite **2052 → 2090 passed, 0 failed**; smoke **17/17**.
- **Open, needs human eyes:** nobody has WATCHED a shrunk viewport or the bar
  render on any target. raycast_4 is the first raycast sample whose *view shape*
  changes — most worth eyeballing in a browser + on Android. (Same standing
  caveat as raycast_3/plateforme_3, still unaddressed.)

**2026-07-23 — Raycast moved into an EXTENSION (RAYCAST_EXTENSION_PLAN Stage B
complete).** The 2.5D raycast feature is now a self-contained folder extension
(`extensions/raycast_2_5d/`) instead of being woven through core — the plan's
worked teaching example of extending the IDE. Five commits, each behaviour-
preserving with proof and a full-suite + smoke gate:
- **B2 (`b30b15f`) — the renderer.** `_render_raycast_view` + `_cast_ray` +
  `_build_raycast_walls` + `_cast_floor_plane` + `_wall_shade` + the RAYCAST_*
  constants (~547 lines of GameRoom methods) → `renderer.py`. Mechanical extract
  (`self` → an explicit `room` param, class consts → module consts), proven
  pixel-for-pixel vs pre-move HEAD before deleting the core copy. `GameRoom.
  _render_room`'s built-in raycast branch is GONE; raycast rooms draw through the
  Stage-B1 `extension_hooks` seam. New guard: `tests/test_raycast_extension.py`.
- **B3 (`8ca55c9`, `74e418b`, `fa9219f`) — the actions + builders.** All four
  "3D View" actions (set_facing_angle, enable_raycast_view, draw_minimap,
  draw_doom_hud): **schemas** → `actions.py` (`PLUGIN_ACTIONS`), **handlers** →
  `handlers.py` (`PluginExecutor`), HUD **builders** (build_minimap_commands,
  build_doom_hud_commands, doom_face_frame + MINIMAP consts) → `hud.py`. Core's
  static `ACTION_TYPES` now has NO 3D-View entry and `action_executor.py` no
  raycast handler/builder — only pointer comments.
- **B4 — `facing_angle` stays in core** (a general instance property; the
  expression parser references it by name). The action that writes it moved; the
  attribute didn't.
- **Landmines worth carrying forward** (also in the plan doc):
  1. A plugin handler runs on a `PluginExecutor`, not the `ActionExecutor`, so it
     reaches the engine via `instance.action_executor.game_runner` /
     `._parse_value` (the audio_actions pattern). Tests that used to call
     `executor.execute_*_action` directly now `load_all_plugins(ex)` and dispatch
     through `ex.action_handlers[...]`.
  2. Moved action **schemas** only appear in `ACTION_TYPES` AFTER
     `load_all_plugins()` runs (the loader merges `PLUGIN_ACTIONS`). A bare test
     import that queries `get_action_type("enable_raycast_view")` returns None
     unless it loads plugins first — same class as the long-standing
     `'play_sound' in ACTION_TYPES` gotcha.
  3. `load_all_plugins` re-registers room renderers on EVERY call (idempotent) —
     the hook registry is process-global state a test can clear.
  4. The loader imports a folder extension under a SYNTHETIC package name
     (`pygm_extension_<folder>`), so its submodules are DIFFERENT objects from
     `extensions.raycast_2_5d.*` imported the normal way. Harmless (no module-
     level mutable state), but a render-path spy must patch the LOADED copy — see
     `_loaded_renderer()` in `tests/test_raycast_viewport.py`.
- **B3b (done, same day) — the STATE moved too.** All per-room raycast state
  (the `camera` config + the derived wall-edge caches) now lives under
  `room.extension_state["raycast"]`, reached via `extensions/raycast_2_5d/
  state.py`'s `raycast_state(room)` (get-or-create) / `peek_camera(room)` (non-
  creating — the render hook runs on EVERY room and must not stamp raycast state
  onto non-raycast ones). `GameRoom.__init__` dropped all six raycast attributes;
  core carries **nothing** raycast-specific. The Kivy/HTML5 ports keep their own
  `self._raycast_*` scene attrs (unaffected — only desktop storage changed), so
  the parity test feeds each side its own way. Test sweep was broad (~50 sites:
  `room.raycast_camera` → `raycast_state(room)["camera"]`, `room._raycast_v_walls`
  → `["v_walls"]`, etc.); done with word-boundary regex so `scene._raycast_*` and
  `current_room` receivers weren't mangled.
- **Still open — just Stage C (optional):** move the HTML5/Kivy export renderers
  into the extension (build-system plumbing, low teaching value); the exports
  work as-is because they key off action names, not this code.
- Suite **2090 → 2147 passed, 0 failed** across the six commits; smoke **17/17**
  (all four raycast samples verified rendering *through the loaded extension*).

**2026-07-23 — Raycast EXTENSION Stage C: the EXPORT engines are now
extension-agnostic too (plan COMPLETE).** The HTML5 (`engine.js`) and Kivy
(`kivy_exporter.py` + `code_generator.py`) engines had NO extension mechanism —
so Stage C first BUILT a generic one on each, then moved the raycast port onto
it. Nine commits, each behaviour-preserving with a full-suite + smoke gate. End
state: `engine.js`, `kivy_exporter.py`, `code_generator.py` name **no** raycast
code; the ports live in `extensions/raycast_2_5d/export_html5.js` +
`export_kivy.py`, injected at export time.
- **HTML5 (`d66fdea` C1a, `4633bda` C1b, `994bb21` C1c).** engine.js gained a
  room-renderer registry (`renderExtensionRoom`, called first in `GameRoom.
  render`), an action registry (`registerExtensionAction`, consulted in
  `executeAction`'s `default`), and a `// __PYGM_EXTENSION_JS__` marker the
  `HTML5Exporter` fills from each enabled extension's `export_html5.js`. Then the
  RAYCAST_* consts + 5 render methods moved out as `Object.assign(GameRoom.
  prototype, {…})` (method sigs verbatim so parity regexes match), and the 4
  action `case`s became `registerExtensionAction(…)`. **Found + fixed a
  pre-existing browser bug:** `draw_doom_hud` read a bare `ctx` undefined in
  `executeAction` → now `game.canvas`.
- **Kivy (`1b47bb8` C2a, `d1ff9da` C2b, `4d518ed` C2c-1, `6a03c54` C2c-2).**
  Harder: each room is its OWN scene class in a `.format()` template. Added
  post-`.format()` injection markers (`__PYGM_EXTENSION_SCENE_CODE__`,
  `__PYGM_EXTENSION_BASE_CODE__`) so injected Python keeps single `{ }` (no
  brace-doubling), plus an `ACTION_CODEGEN` codegen hook in `code_generator`'s
  DEFAULT branch. Moved: the 565-line renderer → `export_kivy.py` `SCENE_CODE`
  (braces un-doubled `{{`→`{`), the `_draw_minimap` base method → `BASE_OBJECT_CODE`,
  the 4 action codegens → `ACTION_CODEGEN`. `__init__` state + dispatch became
  generic hooks (`_init_extensions` / `_render_extension_overlay`, template no-op
  defaults the injected `SCENE_CODE` overrides — LAST def wins, verified by method
  resolution).
- **Landmines worth carrying forward:**
  1. **No `node` in CI** for JS, and Kivy can't execute at all — so JS surgery
     was verified by **brace-balance counting** + real-export string checks, and
     Kivy by the **stub harness** (`test_kivy_raycast.py` execs the generated
     `_cast_ray`/`_render_raycast`) + generated-file compile. Un-doubling braces
     is only safe after proving the block has ZERO `.format()` fields (a script
     checks: strip `{{`/`}}`, assert no lone `{name}` remains).
  2. **Behaviour-identical codegen** was proven by capturing each action's
     generated string BEFORE the move and asserting byte-equality after through
     the hook — the strongest check available without executing Kivy.
  3. Tests read the **shipped** source (engine.js + export_html5.js as combined
     `ENGINE`; kivy_exporter + export_kivy as `KIVY`/`KG`), with the CORE files
     kept separable for the structural "which file owns this seam" assertions.
  4. `tests/test_export_raycast_ownership.py` is the completeness guard — it trips
     if raycast code ever re-inlines into an export engine.
- **C3 (`test_export_raycast_ownership.py` + README/plan/CLAUDE docs).** Suite
  **2147 → 2160 passed, 0 failed** across the nine commits; smoke **17/17**.
  `docs/RAYCAST_EXTENSION_PLAN.md` records the full staging; the whole A→B→C arc
  is the plan's worked teaching example — a folder that adds a new way to draw a
  room AND export it to web + Android.
- **Still needs human eyes** (unchanged standing caveat): nobody has WATCHED the
  exported raycast games render in a real browser or on Android after this move.
  Structure, codegen, parity numbers and generated-file compiles are all verified;
  the visual playtest of an actual export isn't.

**2026-07-29 — Full wiki accuracy + translation review across all 9 languages,
published to the live GitHub wiki.** A sweep of `wiki/` (en, fr, de, uk, ru, it,
es, pt, sl) for accuracy AND correct diacritics, ~52 `docs(wiki)` commits, all on
`main`, then published. 216 `wiki/*.md` pages total.
- **The localized action reference is GENERATED, not hand-maintained — don't edit
  `wiki/Full-Action-Reference*.md` by hand.** `tools/gen_action_reference.py`
  reads the live `ACTION_TYPES` (after `load_all_plugins()`, so it includes plugin
  + extension actions — 109 actions / 207 param notes) and merges per-language
  tables from `tools/action_ref_i18n.py` (`LANGS` dict: 8 translated langs keyed
  `fr/de/uk/ru/it/es/pt/sl`; `en` is pass-through). Run:
  `PYTHONUTF8=1 py -3.12 tools/gen_action_reference.py fr de uk ru it es pt sl`
  (bare = `en`; `PYTHONUTF8=1` is REQUIRED on the Windows console for emoji/Cyrillic
  or it dies on cp1252). Emits English fallback for any missing string + a
  missing-string report, and explicit `<a id="…">` anchors before each category
  header so `#3d-view`-style deep links survive translated headings. To fix a
  localized action string, edit the `ACTIONS_XX`/`NOTES_XX` table in
  `action_ref_i18n.py` and regenerate — never touch the output.
  **`.ts` files are useless for this** — all action strings are `type="vanished"`
  (repo runs `lrelease` only, never `lupdate`).
- **Diacritic-stripping bug fixed across every accented language.** Older
  translated pages had been saved with accents stripped (é→e, č→c, ã→a…) —
  unacceptable for this French/Latin/Slovenian educational content. Restored fr/de
  earlier, then it/es/pt/sl this pass. Strategy: hand-rewrite where a verb/word
  is ambiguous without the accent (Italian `e`/`é`, Portuguese), word-boundary
  regex for unambiguous cases (Spanish, Slovenian) — **always protect code
  identifiers** (`collision`, `--version`) via a placeholder swap before running a
  broad accent regex (a `-sión` rule once mangled `--version`→`--versión` inside a
  code block). Keep accented section headers in sync with ToC anchors: **GitHub's
  auto-slug KEEPS accented chars** (`## Časovni Dogodki` → `#časovni-dogodki`), so
  DON'T add an ASCII `<a id>` for an accented header — let the auto-slug match an
  accented ToC link.
- **New/updated pages:** added `3D-View` + `Extensions` pages (all langs); Home
  accuracy (109 actions not "40+", macOS export, 2.5D/3D + Extensions rows, honest
  preset counts, fixed broken internal links); Event-Reference +3 events
  (keyboard_no_key, draw_gui, animation_end); Intermediate-Preset
  `move_towards`→`move_towards_point`; export guides rewritten for accuracy (real
  menu paths, macOS `.app`, `.zip` project export; dropped fabricated
  py2app/AppImage/WebGL/Windows-cross-compile claims).
- **Publishing mechanics — `scripts/sync_wiki.sh {check|pull|push}`.** The live
  wiki is a SEPARATE repo (`Gabe1290/pythongm.wiki.git`, branch **`master`**).
  `push` clones it, `cp wiki/*.md` in, commits (inheriting `user.name/email` from
  the main repo), pushes. **It is additive/overwrite ONLY — copies `*.md`, never
  deletes or renames.** So a page renamed/obsoleted in `wiki/` leaves its stale
  copy live; reconcile those by hand. It also won't carry non-`.md` files (see the
  `.gitattributes` note below). Publishing is outward-facing — get explicit
  approval first.
- **Line-ending landmine (cost a long detour — READ THIS before touching wiki
  line endings).** `sync_wiki.sh check` does a byte-level `diff -rq`, so on a
  Windows box it perpetually reported "DRIFT" that was **pure CRLF-vs-LF, content
  byte-identical**. Fix: added `*.md text eol=lf` to `.gitattributes` in the main
  repo (`09a6ceb`) AND pushed a matching `.gitattributes` into the live wiki repo
  (its blobs were already LF; without the attribute a Windows checkout renders
  CRLF and always "drifts"). Both stores keep LF blobs; the attribute just fixes
  Windows checkout rendering. **The measurement gotcha that wasted the time: in the
  Bash tool, `grep -c $'\r'` is BROKEN** (the tool strips CR from the command
  string, so `$'\r'` collapses to an empty pattern that matches every line →
  false "95 CR" on LF files), and **Windows `py` can't read git-bash `/tmp/…`
  paths** (a Python byte-compare silently `os.path.exists`-skipped every cloned
  file and reported "0 differences" — comparing nothing). Trustworthy CR checks:
  git-bash-native `cmp` / `wc -c` / `diff <(tr -d '\r' a) <(tr -d '\r' b)`, or a
  Python one-liner reading the file with a **Windows** path.
- **Session-notes consolidation (`6b14f7f`).** The two uncommitted session-note
  transcripts were consecutive halves of the raycast-extension arc (884fd424 ended
  at Stage B2's "Want me to continue?"; 6753ac1a opened with "Continue with B2");
  merged 6753ac1a into `2026-07-03-884fd424.md` under a divider, deleted the
  standalone file, and added a `<!-- curated -->` marker so the auto-extractor
  won't overwrite the merge.
- **Still needs human eyes:** nobody has viewed the published pages rendered on
  github.com — worth spot-checking that accents render (not mojibake), the
  language-switcher banners resolve (no 404s), and accented-header ToC anchors +
  the `Full-Action-Reference#3d-view` deep links land correctly.

**2026-08-08 — pt Tutorials curriculum complete; Section H (pt/ja/zh UI
translation) underway; found + fixed a real dead-translation-context bug.**
Continuation of the `docs/I18N_CLEANUP_2026-08-06.md` queue across several
`/loop`-style "proceed" turns.
- **`Tutorials/pt/` built from scratch, all 9 lessons (Section L, Section 2).**
  Same workflow as the six other languages' `09_catch_the_coins` additions:
  read the CURRENT English lesson from the top-level `Tutorials/index.json` +
  actual files (several lessons' real page counts differed from what stale
  registry guesses assumed — e.g. `06_maze`/`07_platformer`/`08_lunar_lander`
  are 4 pages each, not 7/8/8), translate prose, keep Blockly block-LABEL
  mockups in English (pt has zero `BLOCK_MESSAGES`/`KEY_NAMES` coverage in
  `blockly_i18n.js`), translate quoted in-game block-TEXT content (e.g.
  "Você Venceu!"), keep asset paths pointing at the English folder. Verified
  folder-for-folder, page-count-for-page-count parity against
  `Tutorials/index.json` by script (zero mismatches) before the final commit.
  Final in-IDE verification (open the Tutorial panel with pt selected) is
  still gated on Section H, since pt isn't in the language menu yet.
- **Section H (pt UI translation) started — 438/1371 active messages done
  (51 of 65 contexts) as of this note, all pushed one context-batch per
  commit.** Source-string list decision: `pygm2_de.ts` (**monolithic**, 1371
  active messages / 65 contexts), NOT the split `pygm2_de_*.ts` set — the
  split set turned out to be a *narrower* subset of the same maintained
  content (1007 active messages), not a staler one (spot-checked: the
  raycast_2/3/4 `WelcomeTab` entries exist in both, added the same day per
  git log). `pygm2_pt.ts` is built **monolithic** to dodge
  `compile_translations.py`'s split-set bootstrap gate (`should_compile` only
  compiles `pygm2_<lang>_<group>.ts` once `pygm2_<lang>_core.qm` already
  exists — a chicken-and-egg problem for a brand-new split language). A
  session-local generator script reads a named context's active (has
  `<location>`, i.e. not `type="vanished"`) messages out of `pygm2_de.ts` and
  emits the same `<context>` block into `pygm2_pt.ts` with supplied
  Portuguese translations — mechanical XML generation to avoid hand-format
  errors across hundreds of entries. Per-batch verification that held for
  every commit: XML well-formedness, `scripts/compile_translations.py`
  compiles cleanly, a live `QTranslator` resolves sampled strings (incl.
  leading/trailing-space and `{0}`-placeholder cases — the same
  leading-space landmine as the `TRANSLATION_CATALOG_CORRUPTION_2026-08-08`
  fix), full suite green. Registry (`docs/I18N_CLEANUP_2026-08-06.md`,
  Section H) has a full per-context checklist with commit hashes — that's
  the resume state, not this note.
- **Real bug found and fixed: the "self.ide" translation context never
  applied at runtime, in EVERY shipped language.** While translating pt,
  noticed a context literally named `self.ide` in `pygm2_de.ts`. Root cause:
  `self.ide.tr(...)` calls in `core/ide_exporters.py` (`self.ide` is a
  `PyGameMakerIDE` instance, set via `self.ide = ide_window` in
  `core/ide_window.py`) resolve their Qt translation CONTEXT from the
  runtime class name (`"PyGameMakerIDE"`), not the `"self.ide"` call-site
  text — confirmed empirically with a live `QTranslator` + a `QMainWindow`
  subclass literally named `PyGameMakerIDE`: `self.tr("No Project")` fell
  back to English even with a `"self.ide"`-context translation loaded, and
  `QCoreApplication.translate("self.ide", ...)` was simply never consulted
  by the real call path. Of 24 such messages per language, 6 happened to
  already work (duplicated, correctly, under the real `PyGameMakerIDE`
  context via `ide_window.py`'s own `self.tr()` calls) — **the other 18
  were genuinely broken**, real human-translated text sitting in every
  language's `.ts` that could never reach the running app. Fixed for all 7
  already-shipped languages (commit `cfdb541`): moved the 18 into the real
  `PyGameMakerIDE` context of whichever file is actually shipped —
  `pygm2_<lang>_core.ts` for de/it/ru/sl/uk (split-shipping; `PyGameMakerIDE`
  already lives in `_core` for those), `pygm2_<lang>.ts` in place for es/fr
  (monolithic-shipping) — reusing each language's own already-correct
  translation text and real `core/ide_exporters.py` locations, then deleted
  the now-redundant `self.ide` context from the fixed file. Did **not**
  create a `self.ide` context for pt (would've been dead on arrival) —
  those 18 strings will fold into pt's own `PyGameMakerIDE` batch (287
  messages, not yet started) when that context is tackled. Regression
  coverage: `tests/test_self_ide_context_fix.py` (4 tests, hand-rolled
  offscreen `QApplication` per this repo's audit-test convention — no
  `qapp` fixture needed). Suite 2200→2204 passed, 0 failed.
- **Session-limit discipline held throughout:** every translation batch
  (typically 1-10 contexts / 10-80 strings) is its own commit+push, followed
  by a small separate registry-checkbox commit+push — so a mid-session
  usage-limit stop loses nothing and the next session resumes straight from
  `docs/I18N_CLEANUP_2026-08-06.md`'s checkboxes.
- **Second dead-translation bug found the same way, same session,
  different root cause: `self.tr(f"...")` f-strings.** While
  translating `ThymioPlaygroundWindow` (commit `19797f9`), found 7
  messages in `widgets/thymio_playground.py` written as
  `self.tr(f"Zoom: {int(self.zoom_level * 100)}%")` — an f-string is
  fully interpolated BEFORE reaching `tr()`, so Qt's `translate()` only
  ever saw the already-substituted runtime string (e.g. `"Zoom: 150%"`),
  never the literal template text every language's `.ts` had a real,
  complete human translation for. Same FAILURE MODE as `self.ide`
  (translated text that can never reach the running app), different
  CAUSE (broken source code, not a wrong context name) — worth
  remembering as its own pattern to grep for (`self\.tr\(f"` or
  `self\.tr\(f'`) if auditing other files for this class of bug; a
  repo-wide sweep for the same pattern was **not** done this session,
  scoped to just this one file. One extra wrinkle made this worse than
  `self.ide` for 5 of the 7 shipped languages: the split
  `pygm2_<lang>_misc.ts` files ACTUALLY SHIPPED for de/it/ru/sl/uk had
  these entries marked `type="vanished"` with no `<location>` —
  `lrelease` drops `type="vanished"` from the compiled `.qm` outright,
  so they were dead a SECOND, independent way there (confirmed
  empirically: a translation that clearly differs from its source
  still resolved to the untranslated English pre-fix). Fixed: converted
  all 8 call sites to `self.tr("Zoom: {0}%").format(...)` placeholder
  style, wrapped the two interpolated English state words
  (`"on"/"off"/"paused"/"running"`, never previously localized
  anywhere) in their own `self.tr()` calls, and re-filed every
  already-shipped language's real translation under the corrected
  source text (un-vanishing + adding real `<location>` tags where
  needed) rather than discarding good translation work. `pygm2_de.ts`
  (monolithic — this repo's documented Section H source-string
  reference) was synced to match. Regression:
  `tests/test_thymio_playground_fstring_tr_fix.py` (3 tests). Suite
  2204→2207 passed, 0 failed. pt's own `ThymioPlaygroundWindow`
  translation (75 messages, using the now-fixed source) landed in the
  same commit — 1061/1375 active pt messages done (63 of 65 contexts).
- **pt UI translation (Section H) finished the same session.** Closed
  the remaining `PyGameMakerIDE` context (287 messages — the main
  window menu bar/toolbar/status bar, by far the largest single
  context) in 5 batches, translated incrementally via a new
  `add_partial_context()` generator helper (appends into the same
  `<context>` block across runs — the ordinary `add_contexts()` helper
  required the whole context up front, unworkable at this size).
  Content: File/Edit/Assets/Build/Tools/Help menus + mnemonic
  accelerators, auto-save toggles, object/room/GameMaker-.gmk/Open-
  Roberta-XML import flows, project create/save/load, Test/Debug Game,
  the full Export Game dialog (every platform's availability string),
  the About dialog (features/tech-stack/license HTML blocks, verified
  the markup and the GitHub link/LICENSE code identifiers survive
  translation intact), Aseba (Thymio) export, and the 5 Thymio editor
  guard dialogs. Finished by folding `self.ide`'s 18 real-but-orphaned
  `ide_exporters.py` strings into the now-complete `PyGameMakerIDE`
  context (commit `c461528`) — the fix from the `self.ide` finding
  above. **Result: pygm2_pt.ts translates all 1369 real distinct UI
  strings in the current codebase (61 real contexts; 65 in the
  reference catalog minus 3 zero-active minus the dead `self.ide`
  context name itself).** Deleted the now-superseded
  `translations/pygamemaker_pt.ts` stub (289 entries, zero real
  translations, confirmed unreferenced). `pt` confirmed in
  `LanguageManager._discover_languages()`; every batch this session
  additionally spot-checked its own strings via a live `QTranslator`.
  **Not done: a human has not opened the running IDE with pt selected
  and eyeballed it** — every string is programmatically verified to
  resolve, but nobody has looked at the actual rendered UI. ja and zh
  are unstarted, same-shaped tiers — `docs/I18N_CLEANUP_2026-08-06.md`
  Section H is the resume state, with pt's full commit history as the
  worked example to follow (source-string-list decision, generator-
  script pattern, per-batch verification discipline, and the two real
  bugs — `self.ide` and the `self.tr(f"...")` f-strings — that were
  found and fixed along the way rather than silently replicated).

**2026-08-09 — ja UI translation (Section H) also finished, following
the plan exactly as written.** Picked up `docs/JA_ZH_I18N_PLAN.md` in a
fresh session and worked the full 61-context/1369-message ja tier to
completion across ~20 commits, using the committed `scripts/
gen_translation_ts.py` tool with `pygm2_pt.ts` as the source-string
reference (per the plan's own reasoning — pt is the corrected, de-
duplicated end state after the `self.ide` and f-string bug fixes, so
starting from it means ja never had to re-discover either bug).
**Result: `pygm2_ja.ts` translates all 1369 real distinct UI strings —
61 contexts, EXACTLY matching pt's final shape** (same context count,
same message count), which is itself a useful cross-check that the
reference-file approach generalizes correctly to a second language.
- **One new landmine, unique to ja, worth carrying into zh:** Qt/
  Windows menu mnemonics (`&File`) don't have a natural "letter
  position" once translated into a language with no Latin alphabet.
  Followed the standard Japanese Qt/Windows localization convention
  instead of embedding `&` in the translated word: keep the ORIGINAL
  English mnemonic letter in parentheses at the end of the translated
  label — `"&File"` → `"ファイル(&F)"`, `"&Edit"` → `"編集(&E)"`. This
  only came up in the large `PyGameMakerIDE` menu-bar context; none of
  the other 60 contexts have real menu mnemonics. zh likely needs the
  same convention (it's standard for CJK-localized Qt/Windows apps
  generally, not ja-specific) — check before assuming otherwise.
- The snake_case `ConditionalActionEditor` combo-box values
  (`instance_count` etc.) were translated to natural short Japanese
  labels (インスタンス数, 変数比較, ...) rather than literal snake_case
  — underscore-joining isn't idiomatic in Japanese UI text, unlike the
  Romance languages which mostly kept the joined-word style. Judgment
  call, not a hard rule; zh may want its own natural phrasing too
  rather than copying ja's exact choices.
- Every other pt-established landmine (leading/trailing-space sources,
  literal tab characters in the 5 Sprite Editor shortcut strings,
  `&quot;`/`&apos;`-escaped quotes, Qt `%1` placeholders, HTML markup
  preservation in the About dialog) reproduced identically — the
  `TranslationBuilder` tool and per-batch verification discipline
  (XML validity, `lrelease` compile, live `QTranslator` resolution,
  full suite green) caught all of them the same way pt's build did,
  with zero new process gaps.
- Deleted the now-superseded `translations/pygamemaker_ja.ts` stub (289
  entries, all `type="unfinished"`) once `pygm2_ja.ts` was complete —
  same treatment as `pygamemaker_pt.ts` earlier. `ja` (日本語 🇯🇵)
  confirmed in `LanguageManager._discover_languages()`. Full suite held
  at 2207 passed / 0 failed throughout (no application code changed
  this arc — pure translation-file + one doc/tooling commit at the
  start).
- **Two of three Section H languages (pt, ja) are now fully done.**
  Only zh remains — same plan doc, same tool, same `pygm2_pt.ts`
  reference, budget it the same as ja (NOT as cheap as pt, since
  Chinese doesn't get Romance-language pattern-matching either — the
  plan doc's original effort-expectation note already said this).
  `docs/I18N_CLEANUP_2026-08-06.md` Section H is the resume state.

**2026-08-09 — zh UI translation (Section H) finished; all three
languages (pt/ja/zh) now complete — Section H is CLOSED.** Same session
as the ja completion above (continued across several "proceed" check-ins
at rising usage percentages), worked the full 61-context/1369-message zh
tier to completion across ~11 commits using `scripts/
gen_translation_ts.py` with `pygm2_pt.ts` as source. **Result:
`pygm2_zh.ts` translates all 1369 real distinct UI strings — 61
contexts, EXACTLY matching pt's and ja's final shape** — a third
independent confirmation the reference-file approach generalizes.
- Followed ja's predicted CJK menu-mnemonic convention for the large
  `PyGameMakerIDE` context — original English letter kept in parentheses
  at the end (`"&File"` → `"文件(&F)"`), not embedded in the translated
  word.
- **New landmine, not hit by pt or ja, worth carrying into any future
  language:** `TranslationBuilder.add_contexts`/`add_partial_context`
  XML-escapes the translation VALUE for you (`xml.sax.saxutils.escape`,
  per the module's own docstring) — a translated value must use real
  unescaped characters (`>`, `<`, `&`), never the SOURCE's already-
  escaped `&gt;`/`&amp;&amp;`/`&lt;` form copied over by habit. Doing so
  double-escapes the output (`&amp;gt;`), which is syntactically valid
  XML and passes both `xml.dom.minidom` validation and `lrelease`
  compilation silently — the resulting `.qm` just displays literal
  `&gt;` text to the user instead of resolving to `>`. Caught once (in
  `ConditionalActionEditor`'s GML-expression-example string) only by a
  live `QTranslator` spot-check comparing actual output against the
  expected real character; fixed same session (commit `fb731c4`). Only
  the SOURCE dict *keys* need the escaped form (matched verbatim against
  existing `<source>` text) — this rule applies to translation *values*
  only.
- Every pt/ja-established landmine (entity-escaped `&apos;`/`&quot;`
  sources, `{0}`-style placeholders, literal tab characters, exact emoji
  codepoint matching via `\U000XXXXX` escapes verified against the
  source file before use, HTML markup preservation in the About/License
  dialog text) reproduced correctly with zero new process gaps beyond
  the one above.
- Deleted the now-superseded `translations/pygamemaker_zh.ts` stub (289
  entries, all `type="unfinished"`) — same treatment as the pt/ja stubs.
  `zh` (中文 🇨🇳) confirmed in `LanguageManager._discover_languages()`.
  Full suite held at 2207 passed / 0 failed throughout (one isolated
  flaky/timing-sensitive re-run of
  `test_raycast_view.py::TestFloorCasting::test_full_textured_pipeline_under_budget`,
  confirmed pre-existing and unrelated — passed clean in isolation).
- **Section H (`docs/I18N_CLEANUP_2026-08-06.md`) is now fully closed** —
  pt/ja/zh are all 1369/1369 (61/61 contexts). Only Section L (in-app
  Tutorials curriculum, its own deferred plan doc) remains open in that
  registry. **Not done for any of the three languages: a human opening
  the running IDE with pt/ja/zh selected and eyeballing the rendered
  UI** — every string is programmatically verified to resolve via a
  live `QTranslator`, but nobody has looked at the actual widgets.

**2026-08-09 — Section L (in-app Tutorials) closed; the entire
`docs/I18N_CLEANUP_2026-08-06.md` registry is now COMPLETE.** New
session, picked up the one remaining checkbox: the plan called for
opening the Tutorial panel in a running IDE with pt (and, by extension,
the six lesson-9 languages) selected and confirming every lesson
renders — impossible in this headless environment. Closed it
programmatically instead: `tests/test_tutorial_panel_i18n_verification.py`
(commit `33e4a0e`) drives the real `TutorialPanel` widget through the
exact code path a click-through exercises — `set_tutorials_path` →
`load_tutorial_list` → `open_tutorial_by_data` → `load_current_page` for
every page of every lesson — across every language with a
`Tutorials/<lang>/` folder (de/es/fr/it/pt/ru/sl/uk), asserting the
widget never falls into one of its own error/placeholder branches
("Tutorial not found", "No content", "Error loading page") and that
every page renders substantial content (>100 chars), plus a bonus test
confirming ja/zh (no dedicated folder yet — outside this plan's
original scope) fall back cleanly to the English root. Same judgment
call as Section H's live-`QTranslator` proxy for a GUI check: the
strongest automatable evidence available, not a literal substitute for
eyeballing pixels, and treated as closing the item.
- **Real discovery, not a bug:** the app's actual `DEFAULT_EDITION`
  ("beginner", `config/editions.py`) only surfaces tutorials 1-4 — a
  first draft of this test asserted the tutorial list always has all 9
  lessons and failed for every non-fr/de/it language that doesn't get a
  base-index-fallback rescue, because the beginner edition's
  `tutorial_folders` whitelist genuinely hides 5-9. Fixed by having the
  test fixture force `Config.set("edition", "development")`
  (`tutorial_folders=None`, i.e. show all) — this is a verification
  scoping fix, not an app fix; the beginner-edition gating is intended
  behavior (`filter_tutorials_for_edition`'s own docstring/tests already
  cover it).
- 25 new tests, all passing; full suite 2207 → 2232, 0 failed.
- **Registry status: Sections G/H/I/J/K/L are all now checked off —
  `docs/I18N_CLEANUP_2026-08-06.md` is fully complete.** Anything found
  after this point (a real GUI pass surfacing an actual rendering bug,
  a new language, ja/zh eventually getting their own
  `Tutorials/<lang>/` folders) is new work, not a resumption of this
  queue.

**2026-08-09 — Extension-compat design brief integrated from mobile;
1.1.2 released; `docs/DEFERRED_ITEMS_PLAN.md` Tier 3 fully worked
through.** New session, separate arc from the i18n work above. Four
phases:
1. **Integrated a mobile design session's brief for a 2.0 extension
   manifest system** (Thymio/future-3D compatibility guarantees) into
   `docs/extension_compat_2_0/PLAN.md`, fixing the mobile export's
   mojibake throughout (including French comment text that hit the
   exact double-encoding bug this doc's own "accents matter" rule
   warns about) and re-verifying its prototype's three claimed
   properties against the real bundled `samples/plateforme_3/
   project.json` rather than just trusting the phone session's own
   copy. Logged as a dated `docs/SESSION_NOTES.md` entry. Also cleaned
   a stale `TODO.md` entry ("migrate ja/pt/zh off the legacy
   translation set") that had already been fixed by the i18n arc above.
2. **Tier 0 (`docs/DEFERRED_ITEMS_PLAN.md`): a project-file format-
   version guard, shipped as v1.1.2** — `core/project_format.py`'s
   `check_project_format()`, called from `ProjectManager.load_project()`
   immediately after parsing, refuses (never crashes, never silently
   resaves over) a project newer than this build understands, with a
   specific `_show_load_failure_message` dialog rather than a generic
   one. `tests/test_project_format_guard.py` (13 tests) includes a
   byte-for-byte on-disk-unchanged assertion after a refused load.
3. **Tier 3, all four items closed** (done or scoped):
   - **Item 13 (2.0 extension system feature work) — done, much smaller
     than drafted.** Investigating before coding (this repo's standing
     discipline) found `events/plugin_loader.py` already implemented
     most of it — `requires_extensions`, auto-derived and saved every
     save, plus disabled/not-installed detection already wired to a
     warning dialog. Found and fixed a real, confirmed bug in the
     existing system: `ProjectManager._prepare_project_data_for_save`
     recomputed `requires_extensions` from scratch every save via
     `required_extensions_for_project()`, which can only name an
     extension whose manifest is present **on disk** — so an editor
     without a given extension installed silently wiped the dependency
     record on resave, even though the actual unrecognized actions
     survived untouched. Fixed by unioning the recomputation with any
     existing entry the current editor can't verify is stale. Also
     gave unrecognized action tree items a real visual state (amber,
     the owning extension named via new `plugin_loader.
     extension_for_action()`) and a real double-click message instead
     of a silent no-op (`editors/object_editor/object_events_panel.py`).
     Dropped a misleading "enable the extensions in your config" hint —
     investigation found no such config UI exists anywhere in the app
     (`set_extension_enabled()` is defined but never called from any UI
     code).
   - **Item 9 (Kivy `execute_code` environment parity) — score/lives/
     health half done, "locals copied back" half deliberately deferred
     as its own follow-up.** `execute_code` previously had no `game`
     name bound at all (`NameError` on any `game.*` reference) and no
     error wrapping. Fixed by reusing `execute_script`'s existing
     `_script_game()` helper for `execute_code` too, extended with a
     real `_ScriptGameProxy` class matching desktop's actual semantics
     exactly (a raw `game.lives = X` on desktop does **not** trigger a
     caption update or `no_more_lives` crossing check either — only the
     `set_lives`/`set_health` ACTIONS do that; the proxy intentionally
     doesn't add behavior desktop doesn't have). Caught a real bug via
     this repo's own stub-Kivy execution tests, not just codegen-string/
     compile checks: `_script_game()` referenced `_ScriptGameProxy`
     without importing it from `main` (where the class actually lives,
     per this exporter's established `from main import <name>` lazy-
     import pattern for `base_object.py` → `main.py` references) — would
     have been a `NameError` on every `execute_code`/`execute_script`
     call at runtime. Fixing it required updating 6 pre-existing test
     files' stub `main` modules (`test_kivy_draw_queue_mouse_export.py`,
     `test_kivy_match3_2_sound_sprite_export.py`,
     `test_draw_queue_background_health_bar.py`, `test_kivy_raycast.py`,
     `test_kivy_views.py`, `test_views_export_parity.py`) to also stub
     `_ScriptGameProxy`, since `execute_code` now unconditionally needs
     it. HTML5's matching `game: None` gap was investigated (its
     architecture — real Pyodide `exec()`, locals already copied back —
     is much closer to desktop's, likely a smaller fix) but left
     untouched: fixing it needs a JS refactor of `set_score`/
     `set_lives`/`set_health`'s crossing-detection logic to be shared
     between the action-codegen switch and a new patch-application path,
     and this repo has no way to execute JS in CI to verify a refactor
     like that.
   - **Item 10 (Asset Manager) — Tier 1 (usage tracking) done, Tiers
     2-4 scoped.** `docs/ASSET_MANAGER_PLAN.md` breaks the TODO's four
     bundled features into tiers after investigating what already
     existed (single-asset delete had **zero** usage-impact warning —
     the only auto-cleared reference was sprite→object). New
     `utils/asset_usage.py`'s `find_asset_usages`/`find_unused_assets`
     systematically walk every typed action parameter (using
     `ActionParameter.param_type` metadata rather than a hand-
     maintained action list), collision targets, room instances/
     backgrounds/tiles, and object sprite/parent fields; wired into the
     existing delete confirmation so deleting something still
     referenced elsewhere is no longer a silent surprise. **Caught a
     real correctness bug during development, not just at review:**
     `play_sound` and other plugin actions (`plugins/audio_actions.py`)
     are invisible to `get_action_type()` until `load_all_plugins()`
     runs — the exact landmine this doc already documents elsewhere —
     so without calling it internally, a project's actively-used sounds
     showed up as "unused." Fixed by calling `load_all_plugins()`
     inside the module rather than pushing that requirement onto every
     caller; verified against real sample data
     (`samples/plateforme_3`), not just a hand-built test case.
   - **Item 11 (Clean Project) — scoped, not implemented.**
     `docs/CLEAN_PROJECT_PLAN.md`. Investigation shrank the real scope:
     rollback-snapshot cleanup already happens automatically
     (`_sweep_orphan_snapshots`, every load), and the `__pycache__`/
     `.pyc` workaround in `TODO.md` describes cleaning this dev repo,
     not a saved game project (which never has importable `.py` files
     under it — project code lives as strings inside `project.json`).
     Real remaining scope (a `.tmp`-orphan sweep, an orphaned-physical-
     asset-file scan distinct from Tier 1's unused-*entry* detection,
     and deletion UI for both) was deliberately **not** implemented,
     including the safe read-only detection halves — the valuable parts
     are destructive operations against a user's real project files
     with no undo story yet, a question shared with Asset Manager
     Tier 3 worth resolving once rather than piecemeal.
4. **Cut the actual `v1.1.2` release** (tag + GitHub Release, not just
   the version-bump commit) once explicitly asked to — this is
   deliberately treated as a separate, more consequential step from
   committing/pushing code, per this doc's own risk-tiering; the
   CHANGELOG's `[1.1.2]` entry was completed to cover everything that
   actually shipped under that version (Tier 0 + item 13 + item 9, not
   just the first thing written when the entry was drafted) before
   tagging, so the release notes are accurate.
- Every unit of work this session was its own commit, pushed
  immediately (10 feature/fix + doc commits total) — full suite held
  at 2207 → 2286 passed, 0 failed throughout. `docs/DEFERRED_ITEMS_PLAN.md`
  Tier 3 is now fully worked through: every item is either done or has
  a written, ready-to-resume scoping doc. The two genuinely open
  threads for a future session are the Asset Manager Tier 3 / Clean
  Project bulk-delete-undo design question (shared between both plans)
  and HTML5's `execute_code` `game` binding.

**2026-08-09 — The bulk-delete-undo design question settled: a
soft-delete Trash, not `QUndoCommand` undo/redo.** New session, picked
up the one explicitly-flagged open thread from the note above. Real
investigation before deciding (this repo's standing discipline):
checked what undo infrastructure already exists — `editors/
room_undo_commands.py`, `editors/playground_editor/
playground_undo_commands.py`, the sprite editor — and found it's all
real Qt `QUndoStack`/`QUndoCommand`, but scoped entirely to live,
in-memory canvas edits with zero file I/O (moving a room instance,
say). That's architecturally the wrong tool for "undo a file deletion":
an in-memory undo stack is cleared on project switch or app restart,
exactly when "I didn't mean to delete that" tends to get noticed, and
asset deletion touches a `project.json` entry, a physical file, a
thumbnail, a side file, and cross-references cleared in *other*
assets — not one live object.
- **Decision: soft-delete Trash instead.** `utils/asset_trash.py`
  (pure file/manifest logic, no Qt) moves a deleted asset's files into
  `<project>/.trash/` and records a manifest entry rather than
  unlinking anything — `trash_asset`/`list_trash`/`restore_asset`/
  `empty_trash`. Restore refuses to overwrite on a name collision
  (a same-named asset created after the delete) rather than silently
  clobbering it, leaving the trash entry intact for a retry.
- **Found the REAL live-app delete path is `core/asset_manager.py`'s
  `AssetManager.delete_asset`, not the file I'd initially assumed.**
  `widgets/asset_tree/asset_operations.py`'s `remove_asset_from_project`
  has two paths: a "preferred" one that delegates to
  `project_manager.delete_asset()` → `asset_manager.delete_asset()`
  whenever a `project_manager` is attached (true in the real running
  IDE, always), and a "legacy fallback" (direct file round-trip) used
  only when it isn't. Wired the trash mechanism into **both** rather
  than just the one that looked more prominent in the file I happened
  to read first — the legacy fallback is real, exercised by
  `tests/test_audit_asset_operations_sidefiles.py`'s M59/L32 regression
  tests, and leaving it silently non-trash-backed would've been an
  inconsistent half-fix.
- **`AssetManager` gained `list_trash`/`restore_from_trash`/
  `empty_trash` wrapper methods.** `restore_from_trash` looks up
  asset_type/asset_name from the manifest *before* calling
  `utils.asset_trash.restore_asset` (which deletes the manifest entry on
  success) — otherwise that information would be unrecoverable
  afterward. Re-inserts into `assets_cache` and emits the existing
  `asset_imported` signal (confirmed safe to reuse — its only real
  listener, `ProjectManager.on_asset_changed`, just calls
  `mark_dirty()`) rather than inventing a new `asset_restored` signal.
  Deliberately did **not** add a parallel manual sync into
  `current_project_data` the way `ProjectManager.import_asset` does
  (a "CRITICAL FIX" comment there manually mirrors the cache into
  `current_project_data['assets']`) — traced through `save_project()`
  and confirmed it already calls `asset_manager.
  save_assets_to_project_data(current_project_data)` right before
  writing to disk, which is the same mechanism `delete_asset` already
  relies on (it doesn't touch `current_project_data` either). Matching
  the existing, simpler, already-correct pattern beat copying a second
  one that looked more thorough but was actually redundant.
- **Found and fixed a real, unrelated bug while checking whether trash
  could leak anywhere:** `utils/project_compression.py`'s
  `compress_project` walks the whole project directory
  (`project_path.rglob('*')`) with **zero exclusions** — before this
  fix, every soft-deleted asset would have been bundled straight back
  into every zip export/backup, defeating the entire point of deleting
  it. One `.trash` check fixes it; the save-rollback snapshot mechanism
  (`_snapshot_for_rollback`) was checked too but turned out to already
  be safe by construction (it copies an explicit allowlist of named
  paths, not an unfiltered walk).
- New "Tools → Restore Deleted Assets..." menu entry
  (`show_trash_dialog` in `core/ide_window.py`) opens `TrashDialog`
  (`widgets/asset_tree/asset_dialogs.py`): list, restore, delete
  permanently, empty trash, and a detail line naming any cross-
  references a delete cleared (e.g. an object's blanked `sprite`
  field) — informational only, never auto-relinked on restore, since
  guessing whether a reference should come back is exactly the kind of
  silent behavior this repo's "stop lying to users" preference warns
  against.
- `docs/ASSET_MANAGER_PLAN.md` and `docs/CLEAN_PROJECT_PLAN.md` updated:
  the shared blocker is resolved, so both plans' remaining tiers (Asset
  Manager's bulk multi-select UI and unused-asset cleanup dialog; Clean
  Project's `.tmp` sweep, orphaned-file scan, and their deletion UI) are
  now pure UI-building work with no open design questions — any of them
  is a reasonable next session's starting point.
- 46 new tests across `utils/asset_trash.py`'s mechanism,
  `AssetManager` integration, the legacy fallback path, the zip-export
  exclusion, and `TrashDialog`/`show_trash_dialog`. Full suite
  2286 → 2321, 0 failed.

**2026-08-09 — HTML5 `execute_code` `game` binding: item 9's last open
half, closed.** Same session, explicitly asked for after the summary
above flagged it as the one remaining thread. Re-derived the design from
the Kivy fix rather than the original (stale) plan: the plan's own note
said fixing this needed "factoring `set_score`/`set_lives`/
`set_health`'s crossing-detection logic into something both the action-
codegen switch and a new Python-patch-application path can call" — but
re-checking the Kivy fix's own decided semantics (a raw `game.lives = X`
from `execute_code` never triggers `no_more_lives` on any target, only
the `set_lives` ACTION does) made that refactor unnecessary. The fix is
just: build a fresh `_Game(score, lives, health)` snapshot each
`run_code` call from values synced in from the live JS `game` object,
diff any change back out through the exact same JSON patch mechanism
`self.x`/`self.y` already use. Smaller than planned, not bigger.
- **Verification method worth remembering.** The committed regression
  test uses an established pattern this session almost missed:
  `tests/test_sound_queue_primitive.py`'s `py_bootstrap_ns` fixture
  already `exec()`s `PY_BOOTSTRAP` (real embedded Python inside the JS
  template literal) directly in a Python namespace and calls `run_code`/
  `run_draw` for real — deterministic, no network, no JS engine, and
  *stronger* than the source-structure regex assertions this session
  first reached for out of habit (matching `test_draw_action_codegen.py`'s
  "Node isn't a CI dependency" HTML5 pattern). Wrote the structural
  checks first, found the exec-based fixture pattern by grepping for
  other tests touching `PY_BOOTSTRAP`, and rewrote around it — the
  lesson being: check for an existing execution-based harness before
  defaulting to string matching, even when the "no JS engine" constraint
  is real.
- **Additionally, installed `playwright` + downloaded a real headless
  Chromium ad hoc** (pip install + `playwright install chromium` both
  worked in this environment — network access and no `--with-deps`
  needed) to run `PY_BOOTSTRAP` against real Pyodide loaded from the
  actual CDN in an actual browser, the strongest possible proof for the
  hand-written half of this fix. Not a project dependency, not
  committed — this was a one-time development-time check, consistent
  with the repo's stance that Node/browser execution isn't a CI
  dependency for `engine.js`. It found one real (if purely cosmetic) bug
  the regression tests alone wouldn't have: the new `_Game` docstring
  used escaped backticks (`` \`game\` ``) copying the style of a
  pre-existing `#`-comment nearby, but inside a real Python docstring
  that produces a `SyntaxWarning: invalid escape sequence` — comments
  don't care about backslash escapes, string literals do. Fixed by
  dropping the backtick formatting in the docstring; worth remembering
  as a landmine for any future edit inside `PY_BOOTSTRAP`'s Python
  source specifically (not a concern anywhere else in `engine.js`,
  which is plain JS).
- `tests/test_html5_execute_code_game_binding.py` (12 tests). Full suite
  2321 → 2333, 0 failed. `docs/DEFERRED_ITEMS_PLAN.md` item 9 is now
  fully closed on both export targets — the only remaining gap noted
  there is Kivy's separately-deferred "locals copied back onto the
  instance" (HTML5 never had it, since Pyodide's real `exec()` already
  does that part).

**2026-08-10 — Kivy + HTML5 export codegen for the 4 room actions
(picked back up after being flagged as deliberately deferred).** The
2026-08-09 desktop-runtime session (`set_room_speed`/
`set_background_color`/`set_background`'s `foreground`/
`set_room_persistent`) explicitly left export codegen for both targets
unbuilt, since no sample used the actions yet. Closed in three commits,
one full-suite gate each.
- **Kivy.** `set_room_speed` couldn't just mirror desktop: Kivy's
  movement is already dt-scaled for frame-rate independence
  (`GameObject._process_movement` multiplies by a hardcoded `dt * 60.0`),
  the opposite architecture from desktop's raw per-step model. Replaced
  the `60.0` literal with a new `Scene.room_speed` (default 60,
  runtime-mutable), so changing it scales real-world velocity the same
  way changing desktop's FPS clock does. `set_room_persistent` needed
  actual new infrastructure, not just wiring: Kivy's `GameApp.
  _do_room_switch` always constructed a fresh scene on every switch
  (`room_class()`), so it already behaved like "always non-persistent" —
  the opposite starting point from desktop's old bug. Added a
  `_room_cache` (keyed by room index) populated on exit for a persistent
  room and consulted on revisit; `restart_room` needed a new
  `force_rebuild` param threaded through `_switch_to_room`/
  `_do_room_switch` (and the popup-deferred `_pending_room_switch`, now a
  tuple) since its target IS the current room index, so the normal
  cache-on-exit step would otherwise immediately re-cache-and-reuse the
  very instance being discarded; `restart_game` became a real `GameApp`
  method that clears the whole cache first. `set_background` (its own,
  larger commit) draws through a dedicated `_bg_image_group`
  `InstructionGroup` added once at construction rather than touching the
  existing baked `_draw_bg_image` codegen at all — repositionable
  (behind/foreground, via a *captured* Fbo insert index for a views room,
  not a hardcoded one, since a baked background adds its own instructions
  first) and rebuildable (image swap/tiling/scroll) at runtime; a room's
  baked background (if any) keeps rendering underneath, occluded by the
  dynamic one in the common opaque/stretched case. Verification landmine
  worth repeating: actually importing and executing the real generated
  `main.py`'s `GameApp` (not just asserting on its source) needed
  extending the stub-kivy-env with `kivy.app`/`kivy.config`/`kivy.clock`/
  `kivy.uix.*` stubs, `monkeypatch.chdir(tmp_path)` (its `_log()`
  unconditionally writes a crash log into the CWD on import — a stray
  `pygm_crash.log` landed in the repo root on the first run, caught before
  committing), and NOT pre-stubbing a fake `main` module the way
  `test_kivy_views.py` does for scene-only tests (it would permanently
  shadow the real one). `tests/test_kivy_room_actions.py` (26 tests).
  Suite 2451 → 2467 → 2477 passed, 0 failed.
- **HTML5.** Structurally nothing like Kivy: `html5_exporter.py` dumps
  the whole project straight into `gameData` as JSON with zero
  transformation, and `engine.js`'s `executeAction` is a single shared
  runtime interpreter reading `action.parameters` generically — so there
  is no separate per-action codegen step at all, the entire change lives
  in `engine.js`. Two real surprises versus Kivy: (1) HTML5's game loop
  is **not** dt-scaled at all (`this.x += this._hspeed`, no delta time),
  so `set_room_speed` scales hspeed/vspeed's *final* per-tick position
  delta by `roomSpeed/60` rather than the game loop's call rate (left
  untouched — `requestAnimationFrame`-driven, uncapped — to avoid risking
  a shared-loop change across every exported game); gravity/friction
  accumulation is deliberately left unscaled, a documented approximation
  rather than a full step-rate throttle. (2) HTML5 had the **opposite**
  persistent-room bug from Kivy: `changeRoom` reused `this.rooms
  [roomName]` forever (a dict built once at startup), so every room was
  already accidentally persistent — the same bug shape desktop had before
  its own fix, just on a different target. Fixed by extracting the
  per-room construction loop out of `loadGame` into a reusable `Game.
  buildRoom(roomName)`, and teaching `changeRoom` a `forceRebuild` param
  plus a `_visitedRooms` Set so a non-persistent room rebuilds fresh on
  revisit; `restart_room` passes `forceRebuild=true` for the same reason
  as Kivy's `force_rebuild`. `restart_game` needed **no** change at all —
  it's already `window.location.reload()`, a full page reload that
  trivially discards everything, more thorough than an explicit cache
  clear. All four actions' boolean params route through the same
  defensive true/false-*as-string* coercion `enable_views` already
  established (`v === false || v === 'false' || v === 0`), not a bare
  `!!params.x` — the string `"false"` straight from project JSON is
  truthy under `!!`, a real bug class this file already had the fix
  pattern for. Verified via this repo's established "no Node.js in CI"
  tier (source-structure regex assertions on `engine.js`, matched against
  `test_html5_views.py`'s precedent) plus a real `HTML5Exporter` export
  whose embedded `gameData` round-trips a project exercising all four
  actions; brace/paren balance of the whole file checked before and after
  (only the diff's own brackets — 14/14 — changed). `tests/
  test_html5_room_actions.py` (16 tests, all passing on the first run).
  Suite 2477 → 2493 passed, 0 failed.
- `TODO.md`'s room-background/scrolling entry updated to record both
  targets done; no sample was changed to exercise these actions (matching
  the desktop session's own note that none currently do).

**2026-08-10 — DEFERRED_ITEMS_PLAN.md/TODO.md re-verified fully drained;
picked up the "needs human eyes" thread instead, found and fixed a real
untranslated-UI bug.** Re-checked every tier/section in both docs against
current code before doing anything (the established audit-is-a-lead
discipline) — confirmed all of Tiers 0-3 and every numbered item (1-13,
10.5) are genuinely DONE, and the remaining TODO.md sections (Kivy
long-tail action coverage, right/middle mouse, the Pyodide offline
bundle, manifest-ifying objects/sprites) are explicitly filed as
"pick up opportunistically" / "just before 1.0 final," not ready items.
Rather than invent scope on the closed backlog, picked up the other
standing open thread: the "nobody has looked at the actual rendered UI"
caveat attached to every completed i18n arc.
- **New technique, worth reusing:** an offscreen `QApplication`
  (`QT_QPA_PLATFORM=offscreen`) can still `QWidget.grab()` a real,
  fully-laid-out widget into a `QPixmap` and save it as a PNG — no real
  display needed. Combined with `get_language_manager().set_language(x)`
  (installs the real compiled `.qm` into the running `QApplication`
  before constructing the widget, so `self.tr()` resolves for real) and
  Claude's own multimodal image reading, this is a genuine visual
  spot-check in a headless dev box — categorically stronger than the
  string-resolution tests this repo's i18n work has relied on until now,
  even though it's still not literally "a human looked at it." Ran it
  against `PreferencesDialog` (Tools → Preferences) for all 10 shipped
  languages, switching every tab.
- **Found a real bug on the very first screenshot.** pt/ja/zh's
  Preferences dialog rendered every tab correctly EXCEPT "Extensions"
  (the settings-UI tab from the item-13 follow-up work above), which was
  100% English — tab label, description text, section header, all of it.
  Traced the root cause: that whole feature arc (the tab, plus
  `ObjectEventsPanel`'s unrecognized-action amber tree items and
  `PyGameMakerIDE`'s missing/not-installed extension warning dialogs)
  added 15 `self.tr()`-wrapped strings across those 3 contexts, but the
  session that added them never touched a translation catalog at all —
  confirmed by grep: zero of the 15 sources existed in ANY of the 10
  shipped languages' `.ts` files, not just pt/ja/zh. A gap that predates
  and is independent of the 2026-08-09 pt/ja/zh completion arc; it would
  have hit de/es/fr/it/ru/sl/uk identically.
- **Fixed for all 10 languages in one commit**, not just the 3 that
  happened to be screenshotted. Wrote a one-off script (not committed,
  same category as `scripts/gen_translation_ts.py`'s own session-local
  predecessor before it got generalized) that appends new `<message>`
  entries directly — `TranslationBuilder`/`gen_translation_ts.py` couldn't
  be reused as-is here since it always pulls source text FROM an existing
  reference `.ts`'s `<context>` block, and none of the 10 files had these
  strings yet for it to pull from. Routed each context to the correct
  shipped file per this repo's split-vs-monolithic rule
  (`PreferencesDialog`/`PyGameMakerIDE` → `_core` for de/it/ru/sl/uk,
  `ObjectEventsPanel` → `_editors`; one monolithic file for es/fr/pt/ja/zh)
  — got this from re-deriving it via `grep -c "<name>X</name>"` across
  each split file rather than assuming. Terminology (the noun
  "extension," the enable/disable verb pair) was cross-checked against
  each language's own translated `wiki/Extensions_<lang>.md` page instead
  of invented fresh, so it matches vocabulary a reader may already have
  seen from the wiki. Compiled clean; re-ran the same screenshot spike
  post-fix and visually confirmed pt/ja/zh (full re-check) plus
  de/es/fr/it/ru/sl/uk (Extensions tab only) all render correctly now —
  no mojibake, no truncation, no leftover English. `tests/
  test_extension_ui_translations.py` (3 tests: every source present with
  a real translation in every shipped file; a live `QTranslator`
  resolving all 15 strings in all 10 languages — the actual runtime bug).
  One test-writing landmine: French's "Extensions" is a genuine cognate
  (confirmed against `wiki/Extensions_fr.md`'s own page title, "# Extensions")
  — a naive "translation must differ from the English source" assertion
  false-positived on it; carved out as an explicit, documented exception
  alongside "v{0}" (a legitimately-universal version-prefix string).
- **Found, but explicitly did NOT chase, a much bigger related gap.**
  While spot-checking why German's "General" tab label rendered in
  English, found `pygm2_de_core.ts`/`_editors.ts` alone carry 151
  `<translation type="unfinished"></translation>` entries (78 + 38, plus
  smaller counts in `_blockly`/`_actions`/`_misc`/`_dialogs`) — real
  strings that have simply never been translated, sitting quietly in an
  "already maintained" language's catalog. This is categorically
  different from the pt/ja/zh work (which built each catalog complete
  from a clean reference and got verified 1369/1369) — the six older
  "maintained" languages (de/es/fr/it/ru/sl/uk minus fr, which is
  monolithic) were never swept for 100% completeness the same way, so
  they likely carry similar-scale gaps too, just not counted. Logged in
  `TODO.md`'s Extensions section rather than fixed here — real scope, but
  unbounded until someone runs the same count across the other six
  languages and decides whether/how to prioritize filling them, which is
  a different, larger unit of work than "translate these 15 known
  strings."
- Suite 2493 → 2496 passed, 0 failed. Screenshot spike scripts were
  throwaway (scratchpad, not committed), matching this repo's established
  treatment of Playwright/ad hoc verification tooling.
- **Closed the same day, later in this session: `docs/I18N_UNFINISHED_2026-08-10.md`.**
  The "unbounded until someone runs the count" gap above was counted and
  fully fixed for all 7 languages (de/es/fr/it/ru/sl/uk), not just German —
  1101 real empty-`unfinished` entries across all seven, verified zero
  remain via `tests/test_i18n_unfinished_{de,es,fr,it,ru,sl,uk}.py` (every
  source has a real non-empty translation, resolves via a live
  `QTranslator`). **Re-confirmed still true 2026-08-15**
  (`docs/REMAINING_WORK_2026-08-15.md` Section E): zero empty
  `<translation type="unfinished">` entries anywhere in the 7 files as of
  that date. Don't re-flag this as an open gap without re-running the
  count first — the number above is fully historical.

**2026-08-17 — Desktop export now freezes the REAL pygame engine (was Kivy).
The single most important thing to know about `export/` going forward.**
Closes `docs/EYEBALL_FIXES_2026-08-16.md` Group A (issues 4–8) and Phase E.
The exe/linux/macos exporters used to bundle the **Kivy code generator** — a
second engine, self-described "80% GameMaker 7.0 compatible" — so an exported
`.exe` was never the game the author had just tested with Test Game. One manual
pass over the built files found five bugs at once (no tiles, a keyboard that
jammed at the first wall, no wall collision, a player drifting upward,
sub-images stuck on frame 0), with a green suite behind every one of them.
- **Architecture now:** `export/desktop/pygame_desktop_exporter.py` holds the
  whole pipeline; `export/{exe,linux,macos}/*.py` are thin subclasses carrying
  only what is genuinely platform-specific (`.exe` suffix + DPI manifest; the
  Linux executable bit; macOS onedir+`BUNDLE`, quarantine strip,
  symlink-resolving copy). **Kivy remains for Android/iOS only** — its four
  known gaps are unfixed there, which is the next priority.
- **The project is copied VERBATIM into the bundle.** Not regenerated. That is
  the invariant the whole rework rests on, so don't add a transformation step.
  Consequence worth remembering: authored `<param>_translations` are resolved
  at runtime via `GameRunner.language`, NOT baked in as HTML5/Kivy must —
  and baking here would silently fail anyway, because `GameRunner` re-merges
  `objects/*.json` over the embedded data.
- **Landmines, all of them cost real time this session:**
  1. `plugin_loader` must resolve `plugins/`/`extensions/` at `sys._MEIPASS`
     when frozen (`get_app_root()`, `555efd49`). Failure is **silent** — the
     glob finds nothing, "Loaded 0 plugin(s)", and a 2.5D game draws as a flat
     2D room.
  2. **Pillow is NOT optional**: `runtime/game_runner.py` imports PIL at module
     level, so excluding it builds cleanly then dies with `ModuleNotFoundError`
     on first launch. pygame is required; **Kivy is not** — don't reuse
     `_require_kivy_dependencies` here.
  3. The build directory must live OUTSIDE the project folder (it now holds a
     copy of the project, so inside it recurses into itself).
  4. `.trash` is excluded from the copy — shipping soft-deleted assets would
     undo the author's deletion.
  5. One-file bundles unpack to a temp dir deleted on exit, so the launcher
     redirects `highscores.json` next to the executable or every score is lost
     silently.
  6. Killing a one-file PyInstaller process is awkward — the bootloader spawns
     a child that keeps the pipes open, so `subprocess.run`'s post-timeout
     `communicate()` hangs forever. Use the frame budget below instead of a
     kill.
- **New engine hooks for verifying an export (both opt-in, env-var gated, zero
  cost to a player):** `PYGM_MAX_FRAMES=N` renders N frames, prints
  `PYGM_FRAMES_COMPLETED=N` and exits 0; `PYGM_SCREENSHOT=<path>` saves that
  final frame. They exist because a compiled binary **cannot** be measured the
  way `tools/smoke_run_samples.py` measures the samples (it imports
  `GameRunner` and installs a tick hook), and "still running after N seconds"
  cannot distinguish a running game from one stuck on a black screen before its
  first frame.
- **`tools/verify_desktop_export.py`** builds a real export for the host,
  launches it, and with `--compare` diffs its rendered frame against the engine
  the IDE runs. **Result: 5/5 samples verified on Windows, four
  pixel-identical.** plateforme_3's 1.74% is its own non-determinism — two
  source-engine runs differ by 2.14%, checked rather than assumed.
  `PYGM_E2E_EXPORT=1` enables the real-build test in
  `tests/test_desktop_export_end_to_end.py`.
- **Also fixed en route (unrelated, user-facing):** emoji in log messages
  crashed the log handler on a cp1252 Windows console, so an asset-import
  failure printed a logging traceback *instead of* the reason. New
  `core/logger.ConsoleSafeHandler` sanitizes in `format()` — `emit()` catches
  its own exceptions, so a subclass cannot intercept there. Text the console
  CAN encode passes through untouched, so French accents survive exactly.
- **Deliverable for the user:** `docs/PLATFORM_DISPLAY_CHECKLIST.md` — the
  eyes-only cross-platform pass, deliberately NOT an extension of
  `docs/test_checklist.md` (the exhaustive 1.0.0 feature list). It opens with
  the automated commands so no human time goes on what a script can check, and
  it records mobile/Kivy as known-broken so that isn't re-reported as new.
  `tests/test_platform_display_checklist.py` pins every concrete claim it makes
  (named tools exist, samples exist, views_1 really is 800×600 over 2400×800,
  the overlay really has 7 lines, 11 languages) — writing those tests caught two
  wrong claims in the first draft.
- **Testing lesson worth carrying:** a first draft asserted
  `"runner.language = LANGUAGE" in source`, which a mutation that **commented
  the line out** still satisfied — the text was right there in the comment.
  Launcher assertions now parse the AST. Mutation-test string-presence
  assertions; they are the easiest kind to write blind.
- Suite 3483 → **3558 passed, 0 failed**. All 19 items in
  `docs/EYEBALL_FIXES_2026-08-16.md` are closed. **Still needs human eyes:**
  nobody has *played* an exported build — the runs prove it renders the same
  frames, not that it feels right to hold a key down on.

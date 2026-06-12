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
  tests have grown since). The widget tests that skip on 3.11 run on 3.12,
  which explains the skip-count gap. The old "536 passed" / "486 passed"
  figures are stale snapshots.
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

Open follow-up (left to the user — game-feel): the platformer samples' player
`collision_with_obj_monstre` uses a fragile stomp test `vspeed > 0 and
y < other.y+8`; fast falls overshoot the 8px window and take a life. Suggested
`vspeed > 0 and y - vspeed < other.y+8` (uses the pre-move position). Sample
data only; not applied.

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

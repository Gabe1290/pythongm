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
  will re-save maze_2/maze_3 with new sprites later.

Open follow-up (left to the user — game-feel): the platformer samples' player
`collision_with_obj_monstre` uses a fragile stomp test `vspeed > 0 and
y < other.y+8`; fast falls overshoot the 8px window and take a life. Suggested
`vspeed > 0 and y - vspeed < other.y+8` (uses the pre-move position). Sample
data only; not applied.

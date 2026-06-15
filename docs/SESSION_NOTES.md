# Session Notes

A **portable, git-tracked** log of significant explanations, decisions, and
cross-machine context from Claude / agent sessions.

## Why this file exists

The automatic, complete trace of everything an agent says lives in per-machine
session transcripts:

```
~/.claude/projects/<encoded-absolute-path>/<session-uuid>.jsonl
```

Those transcripts are **not portable**:

- They live under `~/.claude` on one specific machine. Nothing syncs them —
  not GitHub (which only tracks this repo), not Dropbox.
- They are keyed by the **absolute path** the project was opened from. Even on
  the same machine, opening `~/projects/pygm2` vs `~/Dropbox/pygm2` produces
  two separate, non-overlapping histories — and agent *memory* under those
  paths doesn't carry over either.

`CLAUDE.md` already solves this for standing instructions by living in-repo.
**This file does the same for session-by-session explanations and decisions.**
Because it rides GitHub (the canonical cross-machine sync), it follows you to
every computer.

## Conventions

- **Newest entry at the top.** One dated `## YYYY-MM-DD` heading per
  significant session (skip trivial ones).
- Capture the *why* and any cross-machine-relevant state (branch, stash,
  uncommitted work, machine-specific gotchas) — not a blow-by-blow of every
  command.
- Keep deep dives in their dedicated docs (`docs/CODE_AUDIT.md`,
  `docs/LATENT_BUG_AUDIT_2026-06-03.md`, etc.) and just link them here.

## How to keep it synced across machines

GitHub is the cross-machine sync (the repo was migrated off Dropbox for exactly
this reason — see the entry below). So:

1. **Start of session, on any machine:** `git pull`.
2. During/after the session, the agent appends an entry here.
3. **End of session:** commit + push so the next machine sees it.

The raw transcripts on the *other* machines stay local to those machines and
are not retrievable from here. If you ever want one mined into notes, copy that
machine's `.jsonl` into the repo (or just run the agent there and have it
append below).

---

## 2026-06-13 — First 20 audit mediums (M1–M20) fixed (Windows box)

Continued through the medium list of `docs/FULL_AUDIT_2026-06-11.md`:
re-verified each claim, fixed, landed a regression test, flipped the
checkbox with the commit hash. Commits `77974b2`..`5c9418b` (one per
finding; M3/M4/M5 and M9/M10 grouped; M17 was already resolved by H11).
Suite **808 → 890 passed, 0 failed**.

Cross-machine notes:
- **M21–M61 medium + all 35 low remain open** — next session starts at M21.
- **Process gotcha (cost me a recovery):** never edit
  `docs/FULL_AUDIT_2026-06-11.md` (or any UTF-8 doc with em-dashes) via
  PowerShell `(Get-Content -Raw) ... | Set-Content -Encoding utf8` — the
  round-trip read the UTF-8 em-dashes as cp1252 and rewrote them as
  mojibake (`â€"`). Recovered with `git checkout HEAD -- <file>` then
  re-applied the flips with the Edit tool. Use the Edit tool for the
  registry, always.
- Commit messages with double quotes still need `git commit -F <file>`
  on this box (PowerShell 5.1 mangles inline quoting) — used a temp file
  under `.git/` for each.

## 2026-06-12 — All 15 audit highs fixed (Windows box)

Worked through the full high-severity list of `docs/FULL_AUDIT_2026-06-11.md`
in one session: re-verified each claim against code, fixed, landed with a
dedicated regression test file, flipped the registry checkbox with the
commit hash. Commits `120124c`..`94a7ba0` (one per finding; H13+H14 and
H6+H7 share commits because they share a root cause). Test suite went
**724 → 808 passed, 0 failed**.

Cross-machine notes:

- **61 medium / 35 low remain open** — next session starts at the top of
  the registry's Medium section.
- Two audit fixes were verified against the *shipped samples*
  (plateforme_2 physics, maze_3 door) — if those samples get re-saved
  with new art, the sample-driven tests skip gracefully but re-check the
  paths after big sample changes.
- This Windows box still uses the Dropbox repo copy
  (`c:\Users\gthul\Dropbox\pygm2`) — `~/projects/pygm2` does not exist
  here; the "retired Dropbox copy" note below applies to the Linux box
  only. Worth migrating this box at some point for consistency.
- PowerShell 5.1 gotcha: `git commit -m` mangles messages containing
  double quotes — write the message to a file and `git commit -F` it.

## 2026-06-15 — Audit fixes landed in bulk: 107/111 closed (4 deferred)

Drove the open audit findings down hard. Start state was a misleading "77
open": the H12 data-loss high was actually already fixed (commit `3d60e14`,
shared with H10) but its checkbox was never flipped — corrected first. M21
(playground robot ports all 33333) fixed by hand with a test.

The remaining 75 were fixed via a **parallel worktree fix-workflow**: one
agent per file (40 files), each in an isolated git worktree, re-verifying its
findings against current code, fixing behaviour-preservingly, and adding a
3.11-compatible offscreen-QApplication regression test. Returned 69 fixed,
3 already-fixed (stale checkboxes), 0 refuted, 5 deferred-cross-file.

I landed by pulling each worktree's real diff (4 agents had inlined a
placeholder for their new test file instead of the content — the worktrees
still held the real files), confirming no two agents touched the same source
file, applying all 40, and running the **full suite**. That gate caught two
real regressions an agent's isolated test run missed:

- **Eyedropper (M25) vs. canvas no-op (L16) conflict.** M25 routed its
  deferred tool-switch-back-to-pencil through `canvas_modified`; the L16 fix
  stopped emitting `canvas_modified` for no-op gestures (picker clicks) — so
  the switch never applied. Reconciled by adding a dedicated
  `SpriteCanvas.gesture_finished` signal (fires on every release) for the
  switch, keeping `canvas_modified` change-only. Both findings' tests pass.
- **Kivy collision (M34) over-reach.** The agent changed the
  `check_collision_at` call site from absolute coords to `self.x + (offset)`,
  contradicting the `check_empty` sibling and the existing `test_exporters.py`
  contract. Reverted the call-site to absolute; M34's real defect (the method
  is undefined in the generated runtime) is deferred to `kivy_exporter.py`.

Final suite: **1076 passed, 0 failed, 30 skipped, 41 errors** — the 41 errors
are all the pre-existing pytest-qt `qapp`-fixture absence on this 3.11 box (6
widget-test files, untouched by this work); they run on the 3.12 Windows box.

Landed as 11 per-subsystem commits (`b6b27da`..`4d76181`) plus the H12/M21
fixes. Registry `docs/FULL_AUDIT_2026-06-11.md`: **107/111 fixed**.

**4 still OPEN — each needs a coordinated edit in a second file** (an agent was
scoped to one file and correctly refused to touch another that a parallel
agent might be editing):
- **M31** (`events/conditional_editor.py` ✓ editor side correct) — runtime
  `if_condition` `mouse_check` arm in `runtime/action_executor.py` (~:4490) is a
  `return False` stub; needs a real read of `pygame.mouse.get_pressed()` /
  tracked mouse pos for the saved 'check' value.
- **M34** (`export/Kivy/code_generator.py` ✓ call site correct) — must DEFINE
  `check_collision_at(self, x, y, object_name)` (absolute coords) on the
  generated GameObject base in `export/Kivy/kivy_exporter.py` + the
  `game_object.py.template`.
- **L5** (`core/ide_window.py`) — `open_editors`/`detached_editor_windows`
  keyed by bare asset name; a same-named room+object collide. Needs composite
  (category, name) keys coordinated with `widgets/asset_tree/asset_operations.py`
  (`close_editor_by_name`).
- **L8** (`dialogs/project_dialogs.py` ✓ exposes description) — `new_project()`
  in `core/ide_window.py` (~:1308) must write `project_info['description']`
  into the created project (`create_project` takes no description today).

Minor remainders noted by agents (primary finding fixed): **L4** also wants
`WA_DeleteOnClose` on `PlaygroundRunnerWindow`; **M30** has a belt-and-braces
runtime alias / 'state' field aspect in `action_executor.py`.

## 2026-06-11 — Full-codebase audit completed (111 confirmed findings)

The 18-finder adversarially-verified audit of the whole source tree finally
completed after spanning three sessions and **two machine crashes**. Each
crash was recovered by harvesting completed agents' results from the workflow
journals under `~/.claude/projects/.../subagents/workflows/` and hand-building
a continuation script that re-ran only the dead agents (dedup logic replicated
exactly so verification verdict ids stayed aligned).

**Result: 119 raw → 114 deduped → 111 confirmed (15 high / 61 medium /
35 low), 3 refuted.** All 15 highs survived 2 extra refutation votes each.
Registry with file:line, failure scenarios, suggested fixes, and checkboxes:
`docs/FULL_AUDIT_2026-06-11.md`. Highlights among the highs: Kivy export
generates syntactically invalid code (`i`/`eli`), mouse events never fire at
runtime (writer/reader key mismatch), room-file merge permanently destroys
tiles/backgrounds on save, GMK import has a real path-traversal, asset
deletion reloads stale disk state discarding unsaved work.

Per the established methodology these are **leads, not ground truth** — each
fix should re-verify the claim and land with a regression test.

## 2026-06-06 — Decision: replace ALL sample sprites with clearly-licensed art

**Decided:** every sample sprite will be replaced with images that have clear,
documented copyright/licensing. The proper LICENSE/attribution text will be
written **after** the swap is complete, to match what actually ships — not before.

This **supersedes** the earlier "open decision" about whether to swap the Pingus
art (entry below): it's now decided — swap first, then license.

Scope & implications:

- Applies to **both** the platform art (currently Pingus, GPL-3.0-or-later) **and**
  the still-undocumented maze art. So the maze-provenance TODO is mooted by the
  swap — no need to trace the old maze art if it's being replaced anyway.
- Once the Pingus art is gone, the **GPLv3+ copyleft concern** for exported
  platform games disappears.
- `docs/ASSET_LICENSES.md` will need a **rewrite** once new art lands; its current
  Pingus entry + `samples/plateforme_*/CREDITS.txt` + `licenses/GPL-3.0.txt` stay
  accurate only until the swap, then come out.
- **Not a candidate:** the gmshaders.com yellow teddy bear (© Xor, no license
  stated → all-rights-reserved; also not currently in the repo).

## 2026-06-06 — Asset licensing: platform samples (Pingus) done; maze art still TODO

Documented the copyright status of bundled image assets (commit `b4c188b`):

- **Platform samples** (`samples/plateforme_1..5/`, 76 PNGs) — the art comes
  from **Pingus** (https://pingus.seul.org/, https://github.com/Pingus/), which
  licenses code *and* artwork under **GPL-3.0-or-later** (verified against
  upstream `LICENSE.txt`/`AUTHORS`). These files are **GPLv3+, not MIT.** Added
  `docs/ASSET_LICENSES.md` (registry), a `CREDITS.txt` in each plateforme folder,
  `licenses/GPL-3.0.txt`, and fixed `samples/README.md`.
- **Copyleft caveat noted in the doc:** a game *exported* from a platform sample
  contains GPL art and inherits GPL obligations. If that's unwanted for
  classroom redistribution, the fix is swapping in permissive/original art — an
  open decision, not yet acted on.

**Open follow-ups (pick up from `docs/ASSET_LICENSES.md`):**

- **Maze samples** (`samples/maze_1..3/`) — art provenance still undocumented.
  These were also `.gmk` imports; origin/license TBD. ← do this next.
- `resources/flags/*.png` (8) and `Tutorials/**/*.png` — provenance unrecorded
  (stubbed in the registry).
- Optional: add a one-line pointer from root `LICENSE` to `docs/ASSET_LICENSES.md`.

## 2026-06-06 — Set up portable session notes

- Established this file as the portable record of agent explanations, after
  confirming that the automatic transcripts (`~/.claude/projects/.../*.jsonl`)
  are local-only and path-keyed, so they don't follow the user across machines.
- Confirmed no `~/.claude` transcripts are synced into Dropbox; **GitHub is the
  only cross-machine channel**, so portable notes must be committed to the repo.

### Cross-machine layout & state (ported from a machine-local memory note, 2026-06-03)

This was captured during the repo's migration off Dropbox and previously lived
only in this machine's local agent memory — recording it here so it survives.

- **Canonical repo (program source):** `~/projects/pygm2` on each machine.
  GitHub is the sync. `git pull` at the start of every session; edit / test /
  commit here.
- **Retired repo:** `~/Dropbox/pygm2` — kept as a safe fallback, do **not**
  edit. Its `.git` rode Dropbox sync, which is the hazard the move fixed. Can be
  removed once every machine is migrated and any unique work is captured.
- **Working game projects:** `~/Dropbox/PyGameMaker Projects/` (e.g.
  `plateforme_3`) stay in Dropbox; only the *repo* moved. Distinct from the
  in-repo `samples/` copies.
- **Work that may live ONLY on one machine (not pushed):** a
  `WIP: multiplayer over network` stash and a `tutorial-dock-and-test-pdfs`
  branch (`93ca148`) were noted as local-only on the primary machine. Other
  machines won't get them via clone — push them if they're needed elsewhere.
  (The earlier "If Condition" editor fix from that note has since landed as
  commit `d60f41b`.)

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

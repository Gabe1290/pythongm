# Plan: GMK importer hardening (deferred-items plan Tier 3, item 8)

Status: **planned, not started.** Written 2026-07-16 at 72% session usage
with ~1h25 until the next session window, specifically so Tier 3 can be
picked up cold next session per `CLAUDE.md`'s "write the plan/registry to
a file and commit it first" guidance for big jobs. Tier 1 and Tier 2 of
`docs/DEFERRED_ITEMS_PLAN.md` are fully closed (see that file); this is
the detail doc for Tier 3's highest-value item.

## Goal

Reintroduce `treasure` and `maze_4` to the bundled samples by hardening
`importers/gmk_*.py` against the parameter/mapping bugs that made both
imports produce broken action data (see `TODO.md`'s "GMK importer
hardening" section for the original narrative — this doc supersedes it
as the working plan but does not replace it as the historical record).

## Unblocking discovery: the missing `.gmk` sources are recoverable

`samples/treasure.gmk` and `samples/maze_4.gmk` are **not in the current
working tree** (`samples/README.md` only lists `maze_3.gmk` and
`plateforme_1..5.gmk` as tracked) — at first glance this looks like a
blocker, since you can't regenerate a sample without its source.

**They are not lost.** Commit `a8f78d0` ("ship the Welcome-tab sample
games via a tracked samples/ directory") added `maze_1.gmk`, `maze_2.gmk`,
`maze_4.gmk`, and `treasure.gmk` alongside `maze_3.gmk`; a later commit
`f8a0eb7` ("ship as native pygm2 project folders") deleted the four
non-`maze_3` `.gmk` binaries from the tree once native project folders
became the shipping format, but **git history still has them**. Verified
recoverable this session:

```bash
git show f8a0eb7^:samples/treasure.gmk > samples/treasure.gmk
git show f8a0eb7^:samples/maze_4.gmk    > samples/maze_4.gmk
git show f8a0eb7^:samples/maze_1.gmk    > samples/maze_1.gmk   # if maze_1 re-verification needs it
git show f8a0eb7^:samples/maze_2.gmk    > samples/maze_2.gmk   # ditto maze_2
```

(Extracted and byte-verified both files during planning — 504284 bytes
for treasure.gmk, 286245 for maze_4.gmk, matching the sizes recorded in
`a8f78d0`'s diffstat.) Do this once, near the start of the work, and
commit the recovered `.gmk` files (they're exempted from the `*.gmk`
gitignore rule under `samples/`, same as `maze_3.gmk`).

## Step 0 (do this FIRST, before any fix): re-verify every cataloged
finding — several look already fixed

`TODO.md`'s "GMK importer hardening" section catalogs specific findings
from the rc.12 maze_1/maze_3 testing passes. Per `CLAUDE.md`'s "audit is
a lead, not ground truth" discipline (already burned this session on two
stale `TODO.md` claims about Kivy/HTML5 draw-queue support), **do not
assume these are still live bugs.** A spot check during planning found
several already fixed in current `importers/gmk_mappings.py` /
`gmk_converter.py`:

- `(1, 223): "restart_room"` — present (`gmk_mappings.py:379`). The
  "missing `(1, 223)` mapping" finding may be stale.
- `(1, 226): "if_next_room_exists"`, `(1, 227): "if_previous_room_exists"`
  — present and **correctly** (non-swapped) at `gmk_mappings.py:382-383`.
  The "importer mistranslated if_previous_room_exists into
  if_next_room_exists" finding may be stale — or may only affect a
  *different* code path (the finding was about a specific obj_goal event
  in maze_1, not necessarily this table).
- `(1, 212): "play_sound"` and `(1, 551): "play_sound"` — both present
  (`gmk_mappings.py:298,305`). The "action_play_sound mis-mapped to
  set_sprite" finding may be stale, UNLESS the actual mis-firing
  `(library_id, action_id)` pair from the maze_3 samples is a *third*,
  still-unmapped id distinct from these two (the finding's own text
  admits it never pinned down the exact id — "probably in the (1, 6XX)
  range" — so this needs the fresh maze_3 re-import to actually confirm
  which id was firing, not just a grep).
- `_GMK_KIND_TO_ACTION` (the action_kind 1-5 exit_event/repeat/block
  fallback) — present at `gmk_converter.py:583-589`, matches the maze_3
  finding's own "Fixed by adding..." note (this one was already correctly
  marked done, not stale).

**What this means for scoping:** don't start by "fixing" the cataloged
findings one by one from memory — re-import `maze_3.gmk` fresh (source
already tracked, no recovery needed) and diff the result against
`samples/maze_3/` as it stands today. Whatever's *still* different is the
real, current gap list. Only after that should `treasure.gmk`/`maze_4.gmk`
be recovered and imported for the first time, since they're testing new
ground (maze_3 already shipped and was hand-patched, so a maze_3 re-diff
is the cheap, low-risk way to calibrate "is the importer actually better
now" before spending time on two samples that have never successfully
imported).

## Recipe (from `samples/README.md`, "Regenerating from `.gmk`
originals")

```bash
python3 -c "
from importers.gmk_importer import import_gmk_detailed
import_gmk_detailed('samples/maze_3.gmk', '/tmp/maze_3_reimport')
"
# diff /tmp/maze_3_reimport against samples/maze_3/ — every remaining
# difference from the hand-patched, shipped version is either (a) a
# genuine importer gap the hand-patch worked around, or (b) art/content
# the hand-patch changed for unrelated reasons (check git log on the
# specific file before assuming (a)).
```

Then, once the recovered `.gmk` files are committed:

```bash
python3 -c "
from importers.gmk_importer import import_gmk_detailed
import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')
import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')
"
```

Catalog every action whose parameters look wrong (per `TODO.md`'s
category hints: renamed positional-vs-named params, silently-renamed
sprite/object references on case/whitespace conflicts, project-level
script calls to unimplemented GM built-ins for `treasure` specifically,
draw events without matching UI metadata).

## Working discipline (per `CLAUDE.md`, unchanged from Tier 1/2)

- **One task ≈ one commit.** Each fix in `importers/gmk_mappings.py` /
  `gmk_converter.py` gets its own dedicated regression test under
  `tests/test_importers/` (new directory — doesn't exist yet) and its own
  commit, following the exact `finder → verify → fix` unit shape used all
  last session.
- **Commit and push after each unit** so a mid-session limit doesn't lose
  partial work — this doc is the resume state; check off items below (or
  add newly-discovered ones) as they land, mirroring
  `docs/EXPORT_AUDIT_2026-07.md`'s checkbox-registry style.
- **No feature branches** — commit straight to `main`.
- **No multi-agent `Workflow`s** for this — if parallel investigation is
  useful, run one `Agent` at a time and verify findings by reading code on
  the main thread, not with verifier subagents (this class of fan-out has
  hit the account's session limit before).
- Regression tests belong under `tests/test_importers/` (new — this is
  the first work item that needs it) so future importer regressions have
  an obvious home; follow the naming convention of existing regression
  suites (`test_audit_*.py`, `test_gmk_*.py` if any already exist —
  check before inventing a new prefix).

## Registry (fill in as Step 0's re-verification proceeds)

- [ ] Recover `samples/treasure.gmk` and `samples/maze_4.gmk` from git
      history (`git show f8a0eb7^:samples/<name>.gmk > samples/<name>.gmk`)
      and commit them alongside this plan, or in the first work commit.
- [ ] Re-import `maze_3.gmk` fresh; diff against shipped `samples/maze_3/`;
      record every genuine remaining gap here as a new checkbox item
      (expect most of the historical findings below to already be
      resolved — confirm each rather than trusting the note).
- [ ] Re-import `treasure.gmk` for the first time since it was dropped;
      catalog every broken action/parameter as a checkbox item.
- [ ] Re-import `maze_4.gmk` for the first time since it was dropped;
      catalog every broken action/parameter as a checkbox item.
- [ ] (Historical, needs re-verification per Step 0) `if_previous_room_exists`
      / `if_next_room_exists` swap in some maze_1 event — confirm still
      reproduces; if the `GM_ACTION_MAP` table is already correct, find
      the actual remaining root cause (a different lookup path?) before
      closing.
- [ ] (Historical, needs re-verification) `obj_goal` importing with
      `visible: false` when the GM source marks it visible.
- [ ] (Historical, needs re-verification) `action_play_sound` mis-mapped
      to `set_sprite` — pin the exact `(library_id, action_id)` from a
      fresh maze_3 re-import rather than assuming it's `(1,212)`/`(1,551)`
      (both already correctly mapped).
- [ ] (Historical, needs re-verification) list-typed action params
      (`start_moving_direction`'s `directions`) round-tripping through the
      events panel as a stringified `"['down', 'up']"` — this is an
      events-panel widget gap, not strictly an importer gap; confirm
      whether it's still worth a `multi_choice` param_type or whether the
      `ast.literal_eval` runtime fallback is judged sufficient long-term.
- [ ] Project-level script calls in `treasure` referencing GM built-ins
      not implemented in the pygm2 runtime — catalog which built-ins are
      missing once `treasure.gmk` re-imports.
- [ ] Draw events (`draw_self`, `draw_sprite_ext`, etc.) without matching
      UI metadata — cross-reference against the "UI metadata coverage for
      runtime actions" section of `TODO.md` before assuming this is an
      importer bug rather than a metadata-registry gap.
- [ ] Once fixes land: re-add `treasure` and `maze_4` to the bundled
      Welcome-tab sample list (reverses commits `d3fd71a` and `be6e0a9`);
      update `samples/README.md`'s dropped-samples note.

## When this doc is done

Mark the corresponding item in `docs/DEFERRED_ITEMS_PLAN.md` (Tier 3,
item 8) and `TODO.md`'s "GMK importer hardening" section done, following
the same strikethrough + "DONE `<date>`" style used for every other
closed item this cycle.

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

## Registry

- [x] Recover `samples/treasure.gmk` and `samples/maze_4.gmk` (plus
      `maze_1.gmk`/`maze_2.gmk`, needed for the re-verification below)
      from git history and commit them — **DONE 2026-07-16**, commit
      `c6682d9`. Byte-verified identical to the historical committed
      versions (sha1 match against `f8a0eb7^`).
- [x] Re-import `maze_3.gmk` fresh; diff against shipped `samples/maze_3/`
      — **DONE 2026-07-16.** Result: **clean.** No "Unmapped GM action"
      comments anywhere; `monster_all.json`'s `collision_with_wall_corner`
      event (the specific spot the maze_3 finding below was about)
      matches the shipped, hand-verified sample byte-for-byte (modulo
      `created`/`modified` timestamps) — `check_empty`/`exit_event` are
      both correctly emitted, not the `set_score(hspeed)`/comment-stub
      pattern the old finding described. All 5 `play_sound` sites
      (`controller_main.json`, `obj_person.json` ×3,
      `obj_block.json`, `obj_hole.json`, `obj trigger.json`) import as
      `play_sound` with the right sound name, not `set_sprite`.
      **Both maze_3 findings below are stale — already fixed**, most
      likely by general `GM_ACTION_MAP`/`_GMK_KIND_TO_ACTION` work done
      since the note was written, not anything from this session.
- [x] Re-import `treasure.gmk` for the first time since it was dropped —
      **DONE 2026-07-16.** Result: **clean.** Zero unmapped-action
      comments across all 7 objects; expected asset counts (7 objects, 4
      rooms, 10 sprites, 6 sounds, 1 script) match; the one project-level
      script (`adapt_direction`, called from `monster`'s `step` and
      `collision_with_wall` events) round-trips as real, working pygm2
      Python (`instance.hspeed`, `game.check_collision_at_position`,
      `random.random()` — not raw GML pseudo-code, not dropped). Pinned
      by `tests/test_gmk_treasure_maze4_import.py::TestTreasureImport`
      (4 tests).
- [x] Re-import `maze_4.gmk` for the first time since it was dropped —
      **DONE 2026-07-16.** Result: **clean.** Zero unmapped-action
      comments across all 24 objects; expected asset counts (24 objects,
      21 rooms, 24 sprites, 10 sounds) match. Pinned by
      `tests/test_gmk_treasure_maze4_import.py::TestMaze4Import`
      (3 tests).
- [x] `if_previous_room_exists` / `if_next_room_exists` "swap" in maze_1's
      `obj_goal` — **RE-VERIFIED, NOT AN IMPORTER BUG.** Dumped the raw
      parsed `GmkAction` records (`GmkParser().parse(...)`, inspecting
      `library_id`/`action_id`/`action_kind` directly, bypassing the
      converter) for all three of `obj_goal`'s events
      (`collision_with_obj_person`, `keyboard_press/p`,
      `keyboard_press/n`). **All three raw GMK records use
      `id=226` (`if_next_room_exists`)** — including the `p`
      (previous-room) keypress event. The `.gmk` binary itself encodes
      `if_next_room_exists` for the "previous room" key, not
      `if_previous_room_exists`; `GM_ACTION_MAP`'s `(1,226)`/`(1,227)`
      entries are correct and the converter faithfully reproduces the
      source data. This reads as a genuine bug/oversight in the
      **original GameMaker 8 game** (the developer likely copy-pasted the
      collision event's action block into both keypress events without
      swapping "next" for "previous"), not an importer defect. The hand
      patch in shipped `samples/maze_1/` (using
      `if_previous_room_exists` for the `p` key) is a deliberate
      **gameplay fix**, not a fidelity restoration — worth being explicit
      about that distinction if `maze_1` is ever re-imported from scratch
      (the fresh import will reproduce the original bug; that's correct
      importer behaviour, re-apply the same hand patch afterward).
- [x] `obj_goal` importing with `visible: false` — **RE-VERIFIED, NOT AN
      IMPORTER BUG.** Same raw-parse technique: `obj_wall` and
      `obj_person` both parse as `visible=True` (so the parser's
      `sprite_id, solid, visible, depth, persistent, parent_id, mask_id`
      field order — matching GM8's actual on-disk object-chunk layout —
      is not systematically off), but `obj_goal` genuinely parses as
      `visible=False` directly from the raw byte stream, and `obj_goal`
      has no `draw` event to compensate (GameMaker draws invisible
      instances only if their object has an explicit draw event that
      manually calls `draw_self`/`draw_sprite`). The original `.gmk`
      really does mark `obj_goal` invisible with no manual draw
      workaround — matching the described symptom exactly ("goal sprite
      never renders... only walking into the invisible goal trigger
      advances the room"). Same conclusion as the room-nav item: a
      genuine original-game bug, faithfully imported; the shipped
      sample's `visible: true` hand patch is a deliberate fix, not
      fidelity restoration.
- [ ] `action_play_sound` mis-mapped to `set_sprite` — **closed by the
      maze_3 re-verification above** (all 5 sites now import correctly as
      `play_sound`). No further action.
- [ ] List-typed action params (`start_moving_direction`'s `directions`)
      round-tripping through the events panel as a stringified
      `"['down', 'up']"` — **not re-investigated this pass** (confirmed
      out of scope for the importer specifically: it's an events-panel
      widget gap, not a GMK-conversion gap — the importer itself emits a
      real list). Still open if someone wants to build a `multi_choice`
      param_type; the `ast.literal_eval` runtime fallback means it isn't
      urgent.
- [x] Asset-reference integrity check for `treasure`/`maze_4` — **DONE
      2026-07-16.** Every `object.sprite`, room-instance `object_name`,
      and room/layer `background_image` reference resolves to a real
      asset name in both samples (zero dangling references across all
      175+ room instances checked); every sprite/sound/background's
      `file_path` also resolves to a real file on disk. This is the
      "silently-renamed sprite/object references on case/whitespace
      conflicts" category `TODO.md` flagged as a plausible failure mode —
      checked directly rather than inferred from the unmapped-action
      result, since a reference can be well-formed but still point at
      nothing. Pinned by
      `tests/test_gmk_treasure_maze4_import.py::test_no_dangling_asset_references`
      (both samples).
- [x] Remaining full re-validation of `treasure`/`maze_4` — **DONE
      2026-07-16 (on the Windows box).** Two new layers, both **clean**:
      **(a) room-content fidelity vs the raw `.gmk` parse** — per-room
      instance/tile counts AND the multiset of instance positions in the
      import match `GmkParser`'s raw records exactly (treasure: 708
      instances / 4 rooms; maze_4: 2909 instances / 21 rooms; 0 tiles in
      both sources, 0 in both imports), with every instance inside (or
      ≤64px off) its room bounds; **(b) headless smoke run** — both fresh
      imports run 120/180 frames through the real `GameRunner` (SDL dummy,
      injected input) with no loop crash; maze_4 advanced through rooms on
      injected input (room transitions work). Pinned by
      `test_room_content_fidelity_vs_raw_parse` +
      `test_fresh_import_smoke_runs_headlessly` (both samples, in
      `tests/test_gmk_treasure_maze4_import.py`; random seeded, GameRunner
      `cleanup()` no-opped so pygame survives for the rest of the suite).
      Two benign findings: each game has one sound in a format pygame
      can't load ("music" / "sound_background", "Unrecognized audio
      format" — same pre-existing class as shipped maze_2/maze_3, a GM8
      MIDI-era asset, not an importer bug); and the importer's
      nokey/anykey "cannot dispatch" warnings are FALSE POSITIVES — the
      runtime dispatches both (maze_3's controller relies on anykey);
      `RUNTIME_SUPPORTED_KEY_NAMES` just omits the two pseudo-keys (fix
      queued as its own small commit). No visual playtest was possible in
      this headless session — flagged for a quick human confirmation when
      re-adding, but all automatable gates are green.
- [ ] Draw events (`draw_self`, `draw_sprite_ext`, etc.) without matching
      UI metadata in `treasure`/`maze_4` — not checked this pass; cross
      reference against the "UI metadata coverage for runtime actions"
      section of `TODO.md` before assuming any gap found is an importer
      bug rather than a metadata-registry gap.
- [x] Re-add `treasure` and `maze_4` to the bundled set — **DONE
      2026-07-16, verdict RE-ADD** (user played both through and approved).
      The playtest ran 15 findings; **12 were real bugs, all fixed** with
      regression tests, 2 were faithful imports of the original game's own
      data, and 1 was a regression I introduced and reverted. The fixes
      (each its own commit): execute_script editor UI (`8d11101`), GM
      "Applies to" never imported — parser + converter (`fbed924`),
      change_instance motion / jump_to_start+set_alarm targeting / GM Sleep
      mis-map (`d328466`), target-"other" collision context (`c1c6123`),
      question-chain conditional scoping (`06d1051`), room_order vs IDE
      reorder regression revert (`3d12a12`), HUD relative draws + draw_lives
      image alias (`f1dcc86`), sprite Transparent flag (`32e066d`),
      destroy_at_position bbox containment (`b8be6a9`), nokey-before-step
      order (`6df509b`), and set_variable/set_sprite/test_variable targeting
      for the scare mechanic (`7783584`). Fresh imports landed in
      `samples/{treasure,maze_4}/` (`429a633`); maze_4 carries the documented
      `snap_to_grid` wall hand-patch (maze_1 precedent), treasure none.
      Registered in `widgets/welcome_tab.py` + `tools/smoke_run_samples.py`
      (13/13 smoke OK) + name translations, with READMEs/CREDITS and the
      `samples/README.md` note rewritten. Both remaining unchecked items
      below (draw-event UI metadata) are folded into the playtest result —
      no unmapped/undrawn actions surfaced.

## Correction to the working-discipline note above

Regression tests for this work landed as flat
`tests/test_gmk_treasure_maze4_import.py`, **not** under a new
`tests/test_importers/` directory as originally suggested — the existing
suite already has an established flat `test_gmk_*.py` / `test_audit_gmk_*.py`
naming convention (`test_gmk_zlib_bomb.py`, `test_gmk_image_bounds.py`,
etc.) with zero subdirectories anywhere in `tests/`, so a new nested
directory would be the odd one out. Follow that convention for any
further importer regression tests from this plan.

## When this doc is done

Mark the corresponding item in `docs/DEFERRED_ITEMS_PLAN.md` (Tier 3,
item 8) and `TODO.md`'s "GMK importer hardening" section done, following
the same strikethrough + "DONE `<date>`" style used for every other
closed item this cycle.

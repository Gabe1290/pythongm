# Maze_4 (2026-07 re-import) playtest checklist

Gate for re-adding `maze_4` to the bundled Welcome-tab samples
(`docs/GMK_IMPORTER_HARDENING_PLAN.md`, final registry item). Every
**automatable** check is green (zero unmapped actions, zero dangling
references, all 21 rooms' 2909 instances byte-match the raw `.gmk`
parse positions, 120-frame headless smoke run clean — commits
`f90934a`, `f311bbd`, `770e067`); this pass is the remaining **human
visual/gameplay** confirmation.

**Where the build is:** `<Documents>/PyGameMaker Projects/maze_4_reimport_2026-07/`
(File → Open Project → select that folder's `project.json`).
⚠️ Your Documents folder still contains an old `maze_4` — that's the
**broken rc.12 import**. Only test `maze_4_reimport_2026-07`.

Scope: **21 rooms, 24 objects, 24 sprites, 10 sounds, 1 font**. The
biggest maze — a full playthrough is long; the structured pass below
covers the first rooms thoroughly and spot-checks the rest (~25–30 min).

Legend: `[x]` pass · `[!]` works with caveat (note it) · `[-]` not testable.

## Known findings — do NOT log these as new bugs

- `sound_background` is in a format pygame cannot load ("Unrecognized
  audio format" — GM8 MIDI-era asset, same as shipped maze_2/maze_3).
- Original-game quirks are possible (maze_1 shipped two); note anything
  odd but don't assume importer fault — we raw-parse the `.gmk` to
  attribute it first.

## 1. Console hygiene on open

- [ ] No `Unknown action type` warnings
- [ ] No "will never fire" keyboard warnings (`df993c8` regression check)
- [ ] No tracebacks during the (larger) project load

## 2. Editor spot-checks (the drop reason was "bad action parameters")

- [ ] Open 4–5 objects across the roster (player, a monster, a pickup, a
      controller): action parameters look sane — no empty required
      fields, no stringified `['...']` lists, no obviously swapped values
- [ ] Room editor: open room0 + 2–3 mid/late rooms — layout looks like a
      playable maze (visual confirmation of the automated position match)
- [ ] The font asset imported (project has 1 GM8 font) — check any text
      the game draws renders legibly rather than falling back broken

## 3. Test Game — structured playthrough

- [ ] Game launches from Test Game without a crash
- [ ] Menu/intro rooms advance (these use `anykey` — the events the old
      importer warning wrongly called dead)
- [ ] Rooms 1–4: movement, walls solid, monsters/hazards behave,
      pickups/score work
- [ ] Sounds play (except `sound_background` — see known findings)
- [ ] Spot-check 2–3 later rooms via room navigation (N/P debug keys if
      wired, or play through): no blank rooms, no missing sprites
- [ ] Lives/death/restart flow behaves

## 4. Verdict

- [ ] **RE-ADD**: gameplay correct (or only original-game quirks needing
      a deliberate maze_1-style hand-patch — list in Notes)
- [ ] **HOLD**: importer-caused defects found — list in Notes; each
      becomes a finder→verify→fix unit in the hardening plan

## Notes

- **Finding #12 (room24 conveyor markers): VERIFIED WORKING — could not
  reproduce a failure.** Drove all four marker types (move_up/down/left/right)
  headlessly in room24 on current code: each sets the right velocity when the
  person is on it, and a multi-frame ride carried the person smoothly up a
  move_up column (y 384 → 192, staying aligned). The mechanic depends on the
  question-chain scoping fix (#5, commit 06d1051) — before that, markers fired
  unconditionally; after it, they fire correctly. **If you saw this on an
  older build/before pulling #5, re-test now.** If it still fails, note the
  exact spot: which marker, whether the person actually reaches it, and whether
  it's grid-aligned when it arrives (a marker only fires when the person is on
  the 32/8 grid — arriving off-grid from a prior slide would gate it).
- **Finding #13 (room16 explosions don't destroy walls): FIXED (runtime).**
  `destroy_at_position` matched only instances within 1px of their ORIGIN, but
  the explosion clears a 3x3 area by firing at points 16px INSIDE the
  surrounding walls (inside their bboxes, not at their origins), so no walls
  opened and the level was inescapable. Now uses GM's `position_destroy`
  semantics — destroy every instance whose BOUNDING BOX contains the point
  (radius==0); radius>0 still does the Euclidean sweep. Verified: an explosion
  on a wall grid clears the surrounding wall block. Regression:
  `tests/test_destroy_at_position_bbox.py`. **This is a repo runtime fix — it
  takes effect as soon as you re-run `python main.py`; no re-import needed.**

- **Finding #11 (2026-07-16, FIXED — REGRESSION I introduced in f1dcc86):**
  reordering rooms in the IDE had no effect at Test Game — the original
  imported order still played. Root cause: finding #7's fix baked a
  `room_order` key into project.json, but pygm2's room order IS the rooms-dict
  key order (the IDE reorders by moving keys and never writes `room_order`),
  while the runtime's `find_starting_room`/`get_room_list` PREFER `room_order`
  when present. So the frozen key shadowed every in-IDE reorder. Reverted the
  emission (dict order is the single source of truth; the importer already
  builds the dict in play order). **The user's build had its `room_order`
  stripped in place** — their saved reorder (room_start → room8 → …) now
  drives play order. **RELOAD the project in the IDE** (close + reopen) before
  the next Test Game so the in-memory copy drops the stale key too; after that,
  reorder/save/test all honor dict order. Regression:
  `tests/test_draw_relative_and_room_order.py` (asserts the dict is in play
  order AND that no `room_order` key is emitted).

- **Finding #5 (2026-07-16, FIXED same day — runtime, severe):** "obj_person
  starts moving right, cannot stop." Root cause was question-CHAIN scoping in
  both action-list executors: a false question skipped exactly one action, but
  when the skipped action was itself a question (obj_person's step event is
  four `test_alignment → if_collision(move_*) → start_moving_direction`
  conveyor chains), the nested question's guarded movement ran
  UNCONDITIONALLY — every misaligned frame executed all four movements and
  the last (right, speed 8) won, overriding the arrow keys. Reproduced
  headlessly (h jumped 4→8 one frame after pressing RIGHT in a room with ZERO
  markers), fixed (a skipped question now takes its guarded unit down with
  it, recursively), verified headlessly (steady speed-4 movement, aligned
  wall stop at x=256). Regression: `tests/test_question_chain_scoping.py`.
  **Test build refreshed — re-open it.**
- **Finding #6 (2026-07-16, RESOLVED for testing via hand-patch):** pressing a
  movement key TOWARD a flush wall slid the person ~3px into it (pygm2
  slides-to-contact where GM8 reverts to the pre-move position; tight GM
  bboxes give the slack), knocking it off the 32-grid so `test_alignment`
  gated all movement — permanently stuck. Verified headlessly (UP at
  (256,416) → y=413, dead controls). **Fix applied = the maze_1 precedent**
  (a fresh maze_1 import confirms its shipped `snap_to_grid` wall patch was
  hand-added in rc.12 for this same engine deviation): obj_person's
  `collision_with_wall_corner` gets `snap_to_grid(32)` appended, and new
  stop+snap events added for `wall_horizontal`/`wall_vertical` (the person can
  press into those too; the original needed no events there because GM's
  revert kept it aligned for free). Verified headlessly: wall press now stays
  at (256,416), aligned, controls alive. **This hand-patch lives in the test
  build and MUST be re-applied to `samples/maze_4/` at re-add time** (script:
  the session scratchpad's patch_maze4.py logic — stop+snap on all three wall
  types). Engine-level revert-on-block stays rejected for now (the platformer
  samples rely on slide-to-contact landing).
- **Finding #7 (2026-07-16, RESOLVED — half original-game quirk, half fixed):**
  the level order really IS `room_start, room14, room13, ..., room7,
  room20..15, room26..21` — that's the .gmk's own room execution order
  (calibrated: maze_1/maze_3/treasure all parse in their known-correct
  ascending order, so the parser is right and this is the author's ordering,
  faithfully imported — same class as maze_1's original-game quirks). The
  genuine gap: the importer never wrote an explicit `room_order` into
  project.json (the rooms dict was ordered correctly but key-order reliance
  is fragile) — now emitted. Regression:
  `tests/test_draw_relative_and_room_order.py`.
- **Finding #8 (2026-07-16, FIXED — runtime, two bugs):** score/lives not
  displayed. (a) `draw_score`/`draw_text`/`draw_lives` ignored GM's
  `relative` flag, drawing the HUD at absolute (300,4)/(8,4)/(70,4) — buried
  in the top wall row — instead of controller-relative (0,480)+offset = the
  bottom strip; (b) `draw_lives` read only a `sprite` parameter while GM/the
  importer call it `image`, so the lives images resolved to "" and drew
  nothing. Both fixed; verified headlessly (queue now shows "Score: 0" at
  (300,484), "Lives:" at (8,484), sprite_lives at (70,484)). Regression:
  `tests/test_draw_relative_and_room_order.py`. **Test build refreshed —
  re-open it.**
- **Finding #9 (2026-07-16, FIXED — importer/parser):** the hole sprite was
  invisible. `sprite_hole.png` decoded to a 100% transparent image (0/1024
  opaque pixels): the pre-v800 sprite reader read GM's per-sprite Transparent
  flag into a discarded local and hardcoded the BMP key-color pass ON for
  every sprite — a solid black hole with transparency OFF in GM got its own
  color keyed out entirely. The parser now honors the real flag; verified no
  sprite in maze_4/treasure/maze_1/maze_3 decodes blank, and sprites WITH
  transparency still key their background. Regression in
  `tests/test_gmk_treasure_maze4_import.py`. **Test build refreshed.**
- **Finding #10 (2026-07-16, NOT A BUG — faithful import, verified working):**
  the hole's collision destroying SELF before OTHER is the `.gmk`'s own action
  order (raw records: `action_kill_object` applies_to −1 then −2 — the
  original author wrote it that way). Verified the runtime destroys BOTH in
  that order (the event continues after a self-destroy and `other` resolves
  from the executor's collision context) — push a block into a hole and both
  vanish. Pinned in `tests/test_gmk_treasure_maze4_import.py`. If gameplay
  shows the block SURVIVING the hole, re-log with what you saw — that would
  be a different bug, not the action order.

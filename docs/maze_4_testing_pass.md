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
- **Finding #6 (OPEN — next up):** pressing a movement key TOWARD a flush
  wall slides the person ~3px into it (pixel-mask slop; pygm2 slides-to-
  contact where GM8 reverts to the pre-move position), leaving it off the
  32-grid so `test_alignment` gates all further movement — permanently stuck.
  Verified headlessly (UP at (256,416) against the wall above → y=413, then
  dead). Candidate fixes: engine revert-on-block semantics (risky for the
  platformer samples) vs a maze_1-style hand-patch (snap_to_grid in the wall
  collision) at re-add time. Under investigation.
- **Finding #7 (OPEN):** the importer emits NO `room_order`, and the rooms
  dict order is scrambled — the first playable room is room14, not the
  original first level, and next_room walks 13, 12, ... backwards. The raw
  .gmk chunk order starts `room_start, room7, room8...` (creation order); the
  true PLAY order lives in the GM resource tree, which the parser currently
  skips. Needs resource-tree parsing + room_order emission.
- **Finding #8 (OPEN):** score/lives not displayed. `controller_main`'s draw
  event (`set_draw_font score_font` + `draw_score`/`draw_text`/`draw_lives`
  with `relative: true`, controller placed at (0,480) = bottom strip) — not
  yet diagnosed (relative-draw support? font? draw event not firing?).

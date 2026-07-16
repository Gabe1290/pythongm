# Treasure (2026-07 re-import) playtest checklist

Gate for re-adding `treasure` to the bundled Welcome-tab samples
(`docs/GMK_IMPORTER_HARDENING_PLAN.md`, final registry item). Every
**automatable** check is already green (zero unmapped actions, zero
dangling asset references, room content byte-matches the raw `.gmk`
parse, 120-frame headless smoke run clean — commits `f90934a`,
`f311bbd`, `770e067`); this pass is the remaining **human visual/gameplay**
confirmation the plan calls for.

**Where the build is:** `<Documents>/PyGameMaker Projects/treasure_reimport_2026-07/`
(File → Open Project → select that folder's `project.json`).
⚠️ Your Documents folder still contains `treasure`, `treasure_2..4` —
those are the **old, broken rc.12 imports**. Only test
`treasure_reimport_2026-07`.

Scope: **4 rooms, 7 objects, 10 sprites, 6 sounds, 1 project script**
(`adapt_direction`, used by the monster). Should take ~15 minutes.

Legend: `[x]` pass · `[!]` works with caveat (note it) · `[-]` not testable.

## Known findings — do NOT log these as new bugs

- The sound named `music` is in a format pygame cannot load
  ("Unrecognized audio format" in the console — GM8 MIDI-era asset).
  Same class as the shipped maze_2/maze_3 `sound_background`. Expected.
- If something looks odd, remember the maze_1 lesson: it may be a bug in
  the **original GM8 game**, faithfully imported (maze_1's invisible goal
  and next/previous-room swap both were). Note it either way — we'll
  raw-parse the `.gmk` to attribute it before "fixing" the importer.

## 1. Console hygiene on open

- [ ] No `Unknown action type` warnings
- [ ] No "will never fire" keyboard warnings (fixed in `df993c8` —
      if any appear, that's a regression)
- [ ] No tracebacks during project load

## 2. Editor spot-checks (the old failure mode was bad action params)

- [ ] Open the monster object: its `step` / `collision_with_wall` events
      call the `adapt_direction` script — the code shown should be real
      Python (`instance.hspeed`, `game.check_collision_at_position`,
      `random.random()`), not GML pseudo-code or an empty stub
- [ ] Open 2–3 other objects: action parameters look sane (no empty
      required fields, no `['...']` stringified lists, no swapped values)
- [ ] Room editor: open each of the 4 rooms — walls/instances placed
      sensibly (automated check says positions match the .gmk exactly;
      this is the visual confirmation)

## 3. Test Game — full playthrough

- [ ] Game launches from Test Game without a crash
- [ ] Player moves correctly (keys as the original game intended)
- [ ] Monster moves and changes direction on wall hits
      (the `adapt_direction` script actually driving behavior)
- [ ] Collecting treasure works (score/pickup effects)
- [ ] Sounds play (except `music` — see known findings)
- [ ] Room advancement works through all 4 rooms
- [ ] Win/lose flow behaves (lives, restart, end)

## 4. Verdict

- [ ] **RE-ADD**: gameplay is correct (or only original-game quirks that
      need the same kind of deliberate hand-patch as maze_1 — list them
      in Notes)
- [ ] **HOLD**: importer-caused defects found — list in Notes; each one
      becomes a finder→verify→fix unit in the hardening plan

## Notes

(findings here)

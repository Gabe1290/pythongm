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

- [x] No `Unknown action type` warnings
- [x] No "will never fire" keyboard warnings (fixed in `df993c8` —
      if any appear, that's a regression)
- [x] No tracebacks during project load

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

- **Finding #1 (2026-07-16, FIXED same day):** opening the monster object
  logged `Unknown action type: execute_script` (×4 — the two script-call
  actions, step + collision_with_wall) and double-clicking either action
  refused to open the editor dialog. Root cause: the runtime executes
  `execute_script` fine (the smoke run's monster moved), but the action had
  no `events/action_types.py` entry, so the events panel had no UI metadata
  for it. Fixed by registering it (script + arg0..arg4, matching the runtime
  handler) with a new `script` param type — an editable dropdown of the
  project's script assets. Regression:
  `tests/test_execute_script_action_registration.py`. **Re-test section 2's
  first checkbox after pulling** — the action should now open a dialog with
  "adapt_direction" selected. (To view the script's *code*, open the script
  asset itself; the action dialog shows which script is called + arguments.)
- **Finding #2 (2026-07-16, FIXED same day — importer, two-layer):** Explorer's
  `collision_with_pil` destroyed **Self** instead of **Other** (eating a pill
  killed the player). Root cause: GM's "Applies to" selector was never
  imported — the parser read the wrong int into `applies_to` (a 0/1
  "has-selector" flag) and threw the real value away, and the converter never
  emitted a target. Fixed: the parser now reads the true WHO field
  (-1 self / -2 other / ≥0 object), and the converter emits
  `target`/`target_object` for `destroy_instance` / `change_instance` /
  `destroy_at_position`. The power-pill event is now faithful: destroy the
  pill, reset already-scared monsters, scare all monsters. Regression:
  `tests/test_gmk_applies_to.py`. **Test build refreshed — re-open it.**
- **Known remaining (next unit, do NOT re-log):** actions the runtime can't
  retarget yet now import with a **console warning** instead of silent
  self-targeting: treasure's `set_alarm` (applies to scared — so scared
  monsters may not revert to normal after the timer) and `jump_to_start`
  (applies to other/monster/scared — eaten monsters won't teleport home, and
  monsters won't reset when you die). Runtime target support for those is the
  queued follow-up; expect those specific behaviors to be off in this pass.
- **adapt_direction script round-trip: CONFIRMED GOOD** (user pasted the
  imported code — real Python: `instance.hspeed`,
  `game.check_collision_at_position`, `random.random()`).

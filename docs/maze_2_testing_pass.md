# Maze_2 careful-pass checklist

Middle-tier bundled sample: **3 rooms, 9 objects, 7 sprites, 4 sounds,
1 font**. First of the bundled samples to exercise the sound asset
type — useful for catching audio-loading regressions that maze_1
can't surface. Should complete in 20-30 minutes.

Origin: imported from `maze_2.gmk` via `importers.gmk_importer`
(see [`samples/README.md`](../samples/README.md)).
Opens via Welcome tab → **Choose a sample ▾ → Maze — Level 2**, which
copies into `<Documents>/PyGameMaker Projects/maze_2/` (numbered suffix
on repeat clicks) and opens the copy — the bundled `samples/maze_2/`
is structurally protected from edits (commit `63b47d7`).

Note the importer caveat: the rc.12 GMK importer has known issues
that took down `treasure` and `maze_4`. The maze_2 sample shipped
clean enough for testing but the issue likely scales with project
complexity, so something more sophisticated than maze_1 (9 vs 3
objects) is where more subtle import gaps may first show up. **Log
anything off in the Notes section below — see
[`TODO.md`](../TODO.md) "GMK importer hardening".**

If you've already done [`maze_1_testing_pass.md`](maze_1_testing_pass.md),
you can fast-skim the sections that are structurally identical
(console hygiene, save behaviour, recent-list refresh) and focus on
the maze_2-specific bits: sound assets, the larger object/event
surface, and a more interesting gameplay loop.

---

## How to use this document

Same conventions as `maze_1_testing_pass.md` — `[x]` pass, `[!]`
caveat, `[-]` not applicable. Free-form notes at the bottom.

---

## 1. Console hygiene during the open

Launch `python main.py`, click "Choose a sample" → "Maze — Level 2",
let the project finish opening, then **glance at the PowerShell output**
before doing anything else.

- [ ] No `Qt Warning: QObject::connect(...)` lines
- [ ] No duplicate `pygm.X` log lines
- [ ] No `Unknown action type: X` warnings — if any surface, copy
      the exact action name; the fix template lives at the bottom
      of `events/action_types.py`
- [ ] No `No editor registered for asset type 'X'` warnings —
      maze_2 has at least one font, and fonts don't currently have
      an editor (TODO.md notes this); a single warning for "fonts"
      after double-clicking a font is **expected** and not a
      regression
- [ ] No tracebacks, no `PermissionError`, no `FileNotFoundError`

## 2. Save behaviour (samples/ protection)

- [ ] Make a small edit, press **Ctrl+S**. Save completes silently
- [ ] After save, `git status` shows `samples/maze_2/` unchanged
- [ ] Window title shows `maze_2 — PyGameMaker IDE` with live `*`
      dirty marker

## 3. Sprite fix-up pass

7 sprites — walk through each, looking for the importer-related
issues called out in the maze_1 doc (palette, transparency, origin,
frame ordering).

- [ ] Expand **Sprites** in the asset tree (7 entries)
- [ ] For each sprite: double-click → sprite editor opens →
      visually confirm image / transparency / origin / frames
- [ ] Per-sprite findings logged below as needed

## 4. Sound assets (new for maze_2)

maze_2 is the first bundled sample with sounds. The sounds asset
type doesn't have a dedicated editor yet (TODO.md), but the
runtime loads and plays them. Quick check that they're present
and load cleanly.

- [ ] Expand **Sounds** in the asset tree (4 entries expected)
- [ ] Each sound shows a sensible name (no `???` / blank /
      garbled — that'd be an importer name-handling bug)
- [ ] When you double-click a sound, the IDE logs "No editor
      registered for asset type 'sounds'" (expected — silent
      drop is correct)
- [ ] At runtime (see Section 6), the sounds actually play when
      triggered (collision, goal, etc. depending on what maze_2
      does)

## 5. Asset references (importer fidelity)

9 objects is enough to surface subtle reference issues.

- [ ] Expand **Objects** in the asset tree (9 entries)
- [ ] For each, the Properties panel shows:
      - A `Sprite` field that resolves to a real sprite
      - Any `Parent` reference resolves to a real parent object
- [ ] Double-click 2-3 of the objects with the longest event lists
      (likely the player and any enemy). The Events panel shows
      events with proper parameter widgets — no `Unknown action
      type:` rows; no parameter values that look like raw GameMaker
      ID numbers (importer should have translated them to asset
      names)

## 6. Editor surface

- [ ] Room editor: double-click each of the 3 rooms. Each renders
      cleanly; the Asset Information / Properties / Preview panel
      populates correctly
- [ ] Instances render where they should on the canvas
- [ ] Sprite editor (one or two sprites): Precise Collision
      checkbox visible below origin spinboxes

## 7. Gameplay pass

- [ ] **Test Game** (F5) launches the game window without error
- [ ] First room renders, player visible, sprites loaded
- [ ] Player responds to input
- [ ] Wall / boundary collision behaves as expected
- [ ] Sounds play at the right moments (this is the new bit vs
      maze_1 — listen for collision sounds, goal sounds, etc.)
- [ ] Room transitions advance through all 3 rooms in order
- [ ] Whatever maze_2's win condition is, it triggers cleanly
- [ ] Closing the game window returns to the IDE without
      traceback

## 8. Welcome tab inline list refresh

- [ ] After working in maze_2, close the project / restart the IDE.
      Welcome tab's recent-list shows `maze_2` at the top
- [ ] Recent-list does NOT contain `samples/maze_2`

---

## Notes

(Free-form observations.)

### Importer-related findings to feed into TODO.md "GMK importer hardening"

(Anything that looks like a bad import — wrong sprite, missing event,
action with a nonsensical parameter, sound that never plays even
though the action fires. Each one is a data point for the post-1.0
hardening pass.)


---

## After the pass

If everything ticked clean: move on to
[`maze_3_testing_pass.md`](maze_3_testing_pass.md) (the largest of the
three bundled samples, 6 rooms / 17 objects).

If anything tripped: log it, push the doc, ping me.

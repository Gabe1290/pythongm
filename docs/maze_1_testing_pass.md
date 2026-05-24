# Maze_1 careful-pass checklist

The smallest bundled sample: **2 rooms, 3 objects, 3 sprites, no
sounds**. Useful as a fast first sanity-check that the IDE → runtime
loop works end-to-end before tackling the larger maze_2 / maze_3
passes. Should complete in 10-15 minutes if everything passes.

Origin: imported from `maze_1.gmk` via `importers.gmk_importer`
(see [`samples/README.md`](../samples/README.md)).
Opens via Welcome tab → **Choose a sample ▾ → Maze — Level 1**, which
copies into `<Documents>/PyGameMaker Projects/maze_1/` (numbered suffix
on repeat clicks) and opens the copy — the bundled `samples/maze_1/`
is structurally protected from edits (commit `63b47d7`).

Note the importer caveat: the rc.12 GMK importer has known issues
that took down `treasure` and `maze_4`. The maze_1..3 samples shipped
clean enough for testing but the issue likely scales with project
complexity (room/object count, action variety) so small samples may
*hide* the same bugs rather than truly being unaffected — see
[`TODO.md`](../TODO.md) "GMK importer hardening" for the post-1.0
investigation plan. **If you see anything off in maze_1 that smells
like a bad import, log it under the Notes section below — it'll
inform the importer fix even if it doesn't block rc.12.**

---

## How to use this document

- Work through one section at a time; tick each `[ ]` as you confirm it.
- Console output should be captured from the same PowerShell session
  that launched `python main.py`. Paste the **whole** block, not just
  the line that looked wrong, so context isn't lost.
- For each finding, drop a one-line note next to the checkbox using
  the same legend as `docs/test_checklist.md` (`[x]` pass, `[!]` works
  with caveat, `[-]` not applicable on my OS / not testable).
- Anything that doesn't fit a checkbox goes in the **Notes** section
  at the bottom.

---

## 1. Console hygiene during the open

Launch `python main.py`, click "Choose a sample" → "Maze — Level 1",
let the project finish opening, then **glance at the PowerShell output**
before doing anything else.

- [ ] No `Qt Warning: QObject::connect(...)` lines (regression for
      commit `afb9c75`)
- [ ] No duplicate `pygm.X` log lines (regression for commit `afb9c75`)
- [ ] No `Unknown action type: X` warnings
- [ ] No `No editor registered for asset type 'X'` warnings (rc.12
      covers rooms / objects / sprites / playgrounds / scripts)
- [ ] No tracebacks, no `PermissionError`, no `FileNotFoundError`

## 2. Save behaviour (samples/ protection)

- [ ] Make a small edit (e.g. rename an object, move an instance),
      press **Ctrl+S**. Save completes silently — no PermissionError,
      no "Refusing to save into bundled samples/" log line
- [ ] After save, run `git status` in a separate shell —
      `samples/maze_1/` shows **no changes**
- [ ] Window title shows `maze_1 — PyGameMaker IDE` (with `*` while
      dirty, dropped after save)

## 3. Sprite fix-up pass

maze_1 has only 3 sprites — fastest of the three samples to walk
through. Importer-related sprite issues to look for:
the wrong colour palette (GameMaker stores sprites in a different
format the converter may have flattened), missing transparency, wrong
origin point (everything's offset by 16px instead of centred), or
animation frames in the wrong order.

- [ ] Expand **Sprites** in the asset tree (3 entries expected)
- [ ] For each sprite: double-click → sprite editor opens →
      visually confirm:
      - The image is intact (no obvious corruption / wrong colours)
      - Transparency / alpha is preserved (no black background where
        there should be transparency)
      - The origin point is sensible (centred, or at the natural
        anchor — usually 0,0 or w/2,h/2)
      - Frame count is correct (1 frame for a static wall, multiple
        for an animation)
- [ ] If you fix any sprite during this pass: edit happens against
      the working copy in `<Documents>/PyGameMaker Projects/maze_1/`,
      not against `samples/maze_1/`. Decide whether the fix is
      worth back-porting to the bundled sample (separate commit, do
      it manually after closing the IDE)

## 4. Asset references (importer fidelity)

maze_1 is small enough to inspect every object individually.

- [ ] Expand **Objects** in the asset tree (3 entries: typically
      something like `obj_player`, `obj_wall`, `obj_goal`)
- [ ] Click each in turn; for each, the Properties panel on the
      right shows:
      - A `Sprite` field that resolves to a real sprite asset
        (no blank value, no "not found")
      - Any `Parent` field resolves to a real parent (likely blank
        for maze_1)
- [ ] Double-click one of the objects with events (player movement,
      goal collision). The Events panel on the left shows events
      with proper parameter widgets — no `Unknown action type:`
      rows in the tree

## 5. Editor surface

- [ ] Room editor: double-click both rooms. Each room opens, asset
      tree on left + room canvas in centre + Properties / Preview
      panel on the right populate correctly (no empty-state
      placeholder lingering after project load — regression for
      commit `00911b3`)
- [ ] Instances render where they should on the canvas (player at
      start position, walls forming a maze boundary, goal
      somewhere reachable)

## 6. Gameplay pass

The real test — actually play maze_1 end-to-end.

- [ ] Toolbar **Test Game** (or **F5**) launches the game window
      without error
- [ ] First room renders (player visible, walls visible, goal
      visible) — if you only see a blank or solid-colour window,
      that's an importer sprite-load failure
- [ ] Player responds to input (likely arrow keys) — walks around
      the maze
- [ ] Wall collision works — player cannot walk through walls
- [ ] Reaching the goal triggers the room transition (advances
      to room 2 or shows a "you won" state — depends on what
      maze_1 was originally programmed to do)
- [ ] Room 2 plays similarly — if maze_1 has a "win" or "loop"
      ending, that behaves correctly
- [ ] Closing the game window returns control to the IDE cleanly,
      no traceback

## 7. Welcome tab inline list refresh

- [ ] After working in maze_1 for a few minutes, close the project
      (or restart the IDE) and return to the Welcome tab. The right
      column's **Continue where you left off** list shows `maze_1`
      (or `maze_1_2` / `_3` depending on which copy you opened)
      at the top, with a recent-time annotation ("just now" / "X
      minutes ago")
- [ ] The recent-projects list does **not** contain
      `samples/maze_1` (raw bundled path). The cleanup in commit
      `63b47d7` filters those out

---

## Notes

(Add free-form observations here as you go — anything that doesn't
fit a checkbox above. Pinned things you'd want a follow-up commit to
address.)

### Importer-related findings to feed into TODO.md "GMK importer hardening"

(If you spot anything in maze_1 that looks like a bad import — wrong
sprite, missing event, action with a nonsensical parameter — log
the specifics here. Each one is a data point for the post-1.0
hardening pass.)


---

## After the pass

If everything ticked clean: move on to
[`maze_2_testing_pass.md`](maze_2_testing_pass.md) (next step up in
complexity).

If anything tripped: paste the console output and a one-line note
here about which step it was; I'll triage and patch what's in scope
for rc.12, and file the rest under post-1.0 importer hardening.

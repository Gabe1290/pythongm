# Maze_3 careful-pass checklist

The largest of the rc.12 bundled samples: **6 rooms, 17 objects,
16 sprites, 8 sounds, 1 font**. Big enough to exercise the action /
event / asset surface meaningfully, but small enough to fit in a
single careful sitting (~45 minutes if everything passes; more with
findings).

Origin: imported from `maze_3.gmk` via `importers.gmk_importer`
(see [`samples/README.md`](../samples/README.md)).
Opens via Welcome tab → **Choose a sample ▾ → Maze — Level 3**, which
copies into `<Documents>/PyGameMaker Projects/maze_3/` (numbered suffix
on repeat clicks) and opens the copy — the bundled `samples/maze_3/`
is structurally protected from edits (commit `63b47d7`).

Note the importer caveat: the rc.12 GMK importer has known issues
that took down `treasure` and `maze_4`. maze_3 is the most complex
of the three remaining bundled samples — if the importer issue scales
with complexity (the working hypothesis per
[`TODO.md`](../TODO.md) "GMK importer hardening"), this is the most
likely place to find new instances. **Be especially thorough about
logging anything off here — findings inform the post-1.0 importer
work, even when they don't block rc.12.**

If you've worked through `maze_1` and `maze_2` already, the
boilerplate sections (console hygiene, save behaviour, recent-list
refresh) can be fast-skimmed; the maze_3-specific value is in the
larger object / event surface, the 6-room navigation loop, and a
gameplay pass that touches more of the runtime than the smaller
samples.

---

## How to use this document

Same conventions as `maze_1_testing_pass.md` — `[x]` pass, `[!]`
caveat, `[-]` not applicable. Free-form notes at the bottom.

---

## 1. Console hygiene during the open

Launch `python main.py`, click "Choose a sample" → "Maze — Level 3",
let the project finish opening, then **glance at the PowerShell output**
before doing anything else.

- [ ] No `Qt Warning: QObject::connect(...)` lines
- [ ] No duplicate `pygm.X` log lines
- [ ] No `Unknown action type: X` warnings — if any surface in
      maze_3 specifically (and weren't seen in maze_1/2), they're
      the most useful data point about the importer's parameter-
      handling regression
- [ ] No tracebacks, no `PermissionError`, no `FileNotFoundError`

## 2. Save behaviour (samples/ protection)

- [ ] Make a small edit, press **Ctrl+S**. Save completes silently
- [ ] After save, `git status` shows `samples/maze_3/` unchanged
- [ ] Window title shows `maze_3 — PyGameMaker IDE` with live `*`
      dirty marker

## 3. Sprite fix-up pass

16 sprites — the largest sprite set of the bundled samples. Worth
spending the most time here looking for importer-related issues
(palette, transparency, origin, frame ordering).

- [ ] Expand **Sprites** in the asset tree (16 entries)
- [ ] Walk through each sprite — open in editor → visual check
- [ ] If you fix multiple sprites: each edit goes to the working
      copy under `<Documents>/PyGameMaker Projects/maze_3/`,
      never back into `samples/maze_3/`. Verify with `git status`
      after a few edits
- [ ] Per-sprite findings logged below as needed

## 4. Sound assets

- [ ] Expand **Sounds** in the asset tree (8 entries)
- [ ] Each sound has a sensible name, not a placeholder
- [ ] At runtime (Section 7), sounds play at the right moments

## 5. Asset references (importer fidelity)

17 objects is a meaningful sample size for finding the kind of
import-rename / parameter-misalignment issues `treasure` showed.

- [ ] Expand **Objects** in the asset tree (17 entries)
- [ ] For each: the Properties panel `Sprite` field resolves;
      `Parent` (if set) resolves
- [ ] Pick 3-5 of the objects most likely to have rich event
      lists (player, monster/enemy, item pickup, level transition).
      For each:
      - Events panel opens cleanly, all expected event rows visible
      - Action parameters look sensible — strings where strings
        belong, numbers where numbers belong, sprite/object pickers
        showing resolved names rather than raw IDs
      - No `Unknown action type:` rows
- [ ] If maze_3 has any object that subclasses / parents another:
      open the parent first, then the child — confirm the child's
      events panel shows inherited events alongside its own

## 6. Editor surface

- [ ] Room editor: double-click each of the 6 rooms. Each renders
      cleanly; right-panel populates correctly; no editor errors
      in the console
- [ ] Reorder rooms via drag-and-drop in the asset tree, save,
      reopen — order persists (regression check for the room-order
      preservation in `set_project`)
- [ ] Sprite editor: precise-collision checkbox visible on a few
      sprites

## 7. Gameplay pass

The biggest game in the bundle. Worth playing all the way through
at least once if you have the time.

- [ ] **Test Game** (F5) launches the game window without error
- [ ] First room renders correctly
- [ ] Player controls work
- [ ] Wall / boundary collision behaves as expected
- [ ] Sounds play at the right moments (collision, item pickup,
      enemy hit, etc.)
- [ ] Score / lives / health (if maze_3 uses them) update as you
      play and display in the window caption
- [ ] Room transitions advance through all 6 rooms in the
      expected order
- [ ] Whatever maze_3's win condition is, it triggers cleanly
- [ ] If maze_3 has a death / restart loop (enemies that catch
      you), restart_game brings you back to the start cleanly
- [ ] Closing the game window returns to the IDE without
      traceback

## 8. Cross-platform Desktop / Documents defaults

Specifically Windows-with-OneDrive territory — the rc.12 X3 fix
(`53ec9ae`) routed the file-dialog defaults through `QStandardPaths`
so OneDrive-redirected Desktop is respected.

- [ ] **File → Export → Export Game** (or any export target):
      destination QFileDialog opens at your **real** OneDrive-
      redirected Desktop, not at a stale `C:\Users\gthul\Desktop\`
      that may not exist
- [ ] **File → Save Project As**: defaults to
      `~/Documents/PyGameMaker Projects/`

## 9. Welcome tab inline list refresh

- [ ] After working in maze_3, close / restart. Welcome tab's
      recent-list shows `maze_3` at the top
- [ ] Recent-list does NOT contain `samples/maze_3`

---

## Notes

(Free-form observations.)

### Importer-related findings to feed into TODO.md "GMK importer hardening"

(Specific examples of imports that didn't survive cleanly. Each one
is a data point for the post-1.0 hardening pass — even cosmetic
sprite differences are worth recording, because they may hint at a
broader importer category. Useful format for each finding:

  - **What's wrong:** "obj_monster's collision event has a
    `set_sprite` action with `sprite: <self>` but the original
    GameMaker project used `sprite_monster_attack`"
  - **Suspected cause:** "importer fell back to `<self>` sentinel
    when it couldn't resolve the original sprite reference"
  - **How visible:** "monster doesn't change appearance when
    attacking — gameplay still works"
)


---

## After the pass

If everything ticked clean: rc.12 testing is effectively complete.
The bundled samples that ship in 1.0 are validated, the importer's
known gaps are scoped to post-1.0 work, and we have concrete
findings to feed back into TODO.md.

If anything tripped: log it; we triage rc.12-blockers vs deferrable.

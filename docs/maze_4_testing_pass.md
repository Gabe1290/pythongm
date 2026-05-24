# Maze_4 careful-pass checklist

A focused testing pass for the most complex bundled sample. `maze_4` is
the largest project the IDE ships (21 rooms, 24 objects, 24 sprites,
10 sounds) — so it exercises the widest surface of the runtime + editor
in a single sitting. If a regression is hiding anywhere in the recent
audit / visual / samples work, this is the most likely place to flush
it out before we move past rc.12.

Origin: imported from `maze_4.gmk` via `importers.gmk_importer`
(see [`samples/README.md`](../samples/README.md)).
Opens via Welcome tab → **Choose a sample ▾ → Maze — Level 4**, which
copies into `<Documents>/PyGameMaker Projects/maze_4/` (numbered suffix
on repeat clicks) and opens the copy — the bundled
`samples/maze_4/` is structurally protected from edits (commit `63b47d7`).

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

Launch `python main.py`, click "Choose a sample" → "Maze — Level 4",
let the project finish opening, then **glance at the PowerShell output**
before doing anything else.

- [ ] No `Qt Warning: QObject::connect(...)` lines (regression for
      commit `afb9c75`)
- [ ] No duplicate `pygm.X` log lines (regression for commit `afb9c75`
      — every record should appear once with the `pygm.X - LEVEL:`
      formatter, never twice)
- [ ] No `Unknown action type: X` warnings
  - If you see one, copy the exact action name. The fix template is
    documented at the bottom of `events/action_types.py`; rc.12 bulk-add
    (commit `2ab1bd2`) covered every action *the samples used at survey
    time*, but new ones may surface if maze_4 has events the survey
    missed.
- [ ] No `No editor registered for asset type 'X'` warnings
  - Rooms / Objects / Sprites / Playgrounds / Scripts all have editors
    in rc.12. Sounds, Backgrounds, Fonts intentionally don't yet (see
    `TODO.md`). A warning for any other type is unexpected.
- [ ] No tracebacks, no `PermissionError`, no `FileNotFoundError`

## 2. Save behaviour (samples/ protection)

- [ ] Make a small edit (rename an object, move an instance), press
      **Ctrl+S**. Save completes silently — no PermissionError, no
      "Refusing to save into bundled samples/" log line
- [ ] After save, run `git status` in a separate shell — `samples/maze_4/`
      shows **no changes**. The save went to `<Documents>/PyGameMaker
      Projects/maze_4/`, not the bundled folder
- [ ] Window title shows `maze_4 — PyGameMaker IDE` (with `*` while
      dirty, dropped after save) — regression check for commits
      `00911b3` and `afb9c75`
- [ ] Title bar updates **live** as you edit (the trailing `*` appears
      the moment you make a change, not just after save/load)

## 3. Room navigation (21 rooms)

maze_4 is the only sample with enough rooms to genuinely test the
multi-room runtime paths. The runtime "next room" / "previous room"
logic is the same code for 4 rooms as for 21, but if there's a
boundary case (off-by-one at start/end of the room list, room order
preserved through save/load) it's most likely to show here.

- [ ] Run the game (toolbar **Test Game** / **F5**). Game window opens
      without error
- [ ] Navigate through rooms using whatever in-game key maze_4 binds
      (likely arrow keys + enter). At each room transition, no console
      warnings appear
- [ ] `goto_room` actions go to the intended room (i.e. each level
      ends at the next level, not at room 1 or some unrelated room)
- [ ] `restart_game` (likely bound to a key or a death event) returns
      to room 0, not to whatever room you started from
- [ ] In the IDE, expand **Rooms** in the asset tree → confirm the
      tree shows 21 entries in the order the game uses them (room0,
      room1, ... ). Reorder via drag-and-drop, save, reopen — the
      new order persists

## 4. Asset references (importer fidelity)

If the GMK importer mis-renamed an asset, the symptom is an object
whose `sprite:` field shows blank or a "not found" warning at runtime.
This is the failure mode that took down `treasure` — worth a careful
check on all 24 objects.

- [ ] Expand **Objects** in the asset tree (all 24 entries should be
      listed). Click each in turn; for each, the Properties panel on
      the right shows:
      - A non-empty `Sprite` field that resolves to a real sprite asset
      - Any `Parent` field resolves to a real parent object (no "not
        found")
- [ ] At runtime, no `Sprite '<name>' not found` warnings in the
      console during play — that's the smoking gun for an asset
      reference the importer left dangling
- [ ] For one or two objects with rich event lists (likely the player
      or an enemy), double-click → confirm the event tree on the left
      shows events with parameter widgets, not just `Unknown action
      type:` rows

## 5. Editor surface (24 objects × N events)

Sanity-check that the audit's editor work holds up under more data
than the test suite covers.

- [ ] Object editor: pick an object with a long event list. The
      Events panel scrolls cleanly, no `RuntimeError` in console on
      open / close (regression for the `QTreeWidget` teardown fix
      that's been in place since pre-rc.12 — see commit log)
- [ ] Room editor: open the largest room (probably one of the later
      levels). Asset Information / Properties / Preview panel on the
      right populates (no empty-state placeholder lingering after
      project load — regression for commit `00911b3`)
- [ ] Sprite editor: double-click any sprite. Editor opens, **Precise
      Collision** checkbox is visible below the origin spinboxes
      (regression for `editors/sprite_editor`)
- [ ] Script editor (rc.12 new, commit `4dcca25`): if maze_4 has any
      script assets, they double-click into a tab with monospace
      code. (maze_4 may not have any — that's fine, mark as `[-]`.)

## 6. Cross-platform Desktop / Documents defaults

Specifically Windows-with-OneDrive territory — the rc.12 X3 fix
(`53ec9ae`) routed the export and project-save defaults through
`QStandardPaths` so OneDrive-redirected Desktop is respected. maze_4
exercises the file-dialog defaults more than the smaller samples
because you'll probably export it at least once.

- [ ] **File → Export → Export Game** (or any export target): the
      destination QFileDialog opens at your **real** Desktop
      (OneDrive-redirected), not a stale `C:\Users\gthul\Desktop\`
      that may not exist
- [ ] **File → Save Project As**: defaults to `~Documents/PyGameMaker
      Projects/` (also OneDrive-redirected)

## 7. Welcome tab inline list refresh

- [ ] After working in maze_4 for a few minutes, close the project
      (or restart the IDE) and return to the Welcome tab. The right
      column's **Continue where you left off** list shows `maze_4`
      (or `maze_4_2`, `maze_4_3` depending on which copy you opened)
      at the top, with a recent-time annotation ("just now" / "X
      minutes ago")
- [ ] The recent-projects list does **not** contain `samples/maze_4`
      (raw bundled path). The cleanup in commit `63b47d7` filters
      those out

---

## Notes

(Add free-form observations here as you go — anything that doesn't
fit a checkbox above. Pinned things you'd want a follow-up commit to
address.)


---

## After the pass

If everything ticked clean: bump version (or mark `1.0.0-rc.12` as the
final pre-release), and we're closer to 1.0.

If anything tripped: paste the console output and a one-line note here
about which step it was; I'll triage and patch.

# Release QA Checklist — PyGameMaker IDE

**The single, self-contained checklist for signing off a release.** It
replaces the older split set (`test_checklist.md`,
`PLATFORM_DISPLAY_CHECKLIST.md`, `TESTING_CHECKLIST.md`,
`TESTING_PRESET_CHECKLIST.md`, `blockly_editor_test_checklist.md` — all
removed) and folds in the "still needs human eyes" caveats that had
accumulated across the session notes and `docs/PROJECT_STATUS.md`.

Release being validated: `________`   (current shipped: 1.3.1)

> **Box convention** — `L [ ]` Linux · `M [ ]` macOS · `W [ ]` Windows.
> Tick each box on each OS you verified it on. Items with a single box
> are platform-agnostic (run once) or platform-specific (only that box
> exists).

### Why so much of this is manual

The automated suite is large and green — and every visual/UX bug in the
last "eyeball pass" shipped *with a green suite*. Five of them had one
cause: the exported build was a different engine than the IDE runs, so
nothing the tests covered applied to it. That is fixed (desktop exports
freeze the real pygame engine now), but the lesson stands:

1. **Building is not playing.** The tests prove an export renders the
   same pixels as the IDE. They do not prove it feels right to hold a
   key down on.
2. **A machine cannot tell you the layout looks wrong.** Every automated
   check runs offscreen at a fixed size.

So Section 1 does the mechanical half, and the rest spends your attention
on what only a human at a real screen (and, for §10–§11 and §15, a
second machine or a real device) can confirm.

Last full automated green run on record: **Linux 2026-08-19,
`verify_desktop_export.py --all --compare` → 20/20 verified, every sample
0.00% different from the IDE's own rendering.**

---

## How to use this

1. **Section 1 first, on every OS.** It runs the mechanical half for you
   and stops you before you waste time on something a script already
   caught.
2. **Sections 2–12** are the desktop IDE + runtime regression pass. Do
   them on all three OSes for a full release; a patch release touching
   one subsystem can be scoped to that section + Section 1.
3. **Sections 13–16** are the export targets. Each needs its own platform
   (PyInstaller can't cross-compile; Kivy/Android needs a device).
4. **Sections 17–22** are localization, help/docs, the live wiki, the
   packaged IDE, error recovery and per-platform gotchas.
5. **Section 23** is the 2026-06-11 audit-fix regression spot-check.
6. **Release sign-off** (at the end) is the per-OS matrix — fill it in
   last.

Anything you find: one line — **platform, screen/sample, expected, saw.**
A screenshot beats prose for layout. Group findings by root cause before
filing bugs.

---

## 1. Automated pre-flight (do this first, on each OS)

From the repo root.

**On Windows, use `py -3.12` in place of `python3` for every command
below.** Bare `python3` there hits the **Microsoft Store** stub ("Python
was not found"); if that stub is disabled it resolves to an unsupported
3.14, which is worse because it runs and then fails oddly. So each
command has both forms:

```
# Linux / macOS                          :: Windows
python3 -m pytest tests/ -q              py -3.12 -m pytest tests/ -q
python3 tools/smoke_run_samples.py       py -3.12 tools/smoke_run_samples.py
python3 tools/verify_desktop_export.py   py -3.12 tools/verify_desktop_export.py
```

- [ ] L · [ ] W · [ ] m — **Full test suite, CI-equivalent.** Install
  `pytest-qt` first (without it ~41 `qapp`-fixture tests *error* rather
  than skip and a GUI regression passes locally):
  `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q` — **0 failures**
  (skip count is environment-dependent; treat any non-zero *failure* as a
  real regression). Green snapshot: ~4810 passed.
- [ ] L · [ ] W · [ ] m — `python3 tools/smoke_run_samples.py` — every
  bundled sample boots and runs its loop ~180 frames under SDL dummy
  drivers, no `LOOP-CRASH`.
- [ ] L · [ ] W · [ ] m — `python3 tools/smoke_room_lifecycle.py` — room
  restart / change / restart_game and create-once hold on real sample
  data.
- [ ] L · [ ] W · [ ] m — `python3 tools/smoke_run_multiplayer.py` — a
  real two-process host+client over `127.0.0.1` on `reseau_1` reports
  `PYGM_NET_STATUS=` OK for both.
- [ ] L · [ ] M · [ ] W — `python3 tools/verify_desktop_export.py --all
  --compare` — builds a real export **for this platform**, launches each
  sample, and diffs its rendered frame against the IDE's. Exit 0. Last
  full green: Linux 2026-08-19, **20/20 verified, 0.00% different**.
  (Non-zero exit = stop and read the output.)
- [ ] Run once (any OS) — `python3 -m pytest
  tests/test_platform_display_checklist.py
  tests/test_ide_bundle_spec.py -q` — pins the concrete claims the
  eyes-only checklist and the PyInstaller spec make.
- [ ] Optional, per OS — `python3 tools/build_qa_bundle.py` — builds
  every export artifact a human needs (per-platform `.exe`/binary/`.app`,
  HTML5, Pyodide-bundled HTML5, mobile project) into one folder with a
  README, so Sections 13–15 are just double-clicking. Needs network at
  build time for the Pyodide bundle.

---

## 2. IDE application shell

- L [ ] M [ ] W [ ] Launches with **no console error**; Welcome tab shown
  by default with no project.
- L [ ] M [ ] W [ ] Window opens at a sensible size; nothing off-screen;
  title reads `PyGameMaker IDE` with no project.
- L [ ] M [ ] W [ ] Menu bar, toolbar, status bar, asset-tree panel and
  properties panel all visible without resizing; splitters draggable.
- L [ ] M [ ] W [ ] **No clipped / truncated text** in menus, buttons,
  tab labels, status bar (watch translated strings longer than English).
- L [ ] M [ ] W [ ] Toolbar icons render (not blank squares / ✕
  placeholders); hover → tooltip with description + shortcut
  (e.g. "Save Project (Ctrl+S)", "Test Game (F5)").
- L [ ] M [ ] W [ ] Save / Test / Debug / Export / Import Sprite / Import
  Sound icons **grey out with no project**, enable once one is loaded;
  New / Open stay enabled in both states.
- L [ ] M [ ] W [ ] Tools menu: "Validate Project" and "Migrate to
  Modular Structure" grey out with no project; Preferences / Configure
  Action Blocks / Language stay enabled; all enable once a project loads.
- L [ ] M [ ] W [ ] Asset-tree empty-state hint visible with no project
  ("No project loaded. Use File → New / Open Project to begin."),
  disappears once a project loads, dims correctly in **both themes**.
- L [ ] M [ ] W [ ] Right panel with no project: the Asset Information /
  Properties / Preview group boxes are hidden, replaced by one centred
  italic message; they reappear on project load.
- L [ ] M [ ] W [ ] **Dark and light theme** both fully legible — no
  dark-on-dark text anywhere, including imported assets.
- L [ ] M [ ] W [ ] **High-DPI**: text sharp, not a blurry upscale
  (Windows relies on the DPI manifest; macOS deliberately does not claim
  Retina, so a slightly soft game window is expected there).
- L [ ] M [ ] W [ ] Dialog button bars follow the host convention
  (OK-then-Cancel on Win/Linux, Cancel-then-OK on macOS) — check the
  Sprite Strip Import dialog and the Blockly Block Config dialog (Select
  All / Select None stay left).

---

## 3. Project lifecycle

- L [ ] M [ ] W [ ] New Project (File → New Project) — dialog defaults to
  the **localised Documents folder**; description persists into Project
  Settings later.
- L [ ] M [ ] W [ ] Open Project, Save (Ctrl+S), Save As (new name),
  Close Project.
- L [ ] M [ ] W [ ] Recent projects list works; clicking a row opens that
  project; "Clear recent projects" link hides itself when the list is
  empty.
- L [ ] M [ ] W [ ] Open a `.zip` project; edit; save; quit — **no temp
  extraction left behind** in TEMP.
- L [ ] M [ ] W [ ] Reopen a `.zip` project from the Recent list.
- L [ ] M [ ] W [ ] Import a normal `.gmk` (File → Import GMK) works; a
  hostile/corrupt one (huge declared image / zlib sizes) is **rejected
  with a warning**, not an OOM hang.
- L [ ] M [ ] W [ ] **Project-format guard**: opening a project whose
  `format_version` is newer than this build shows a specific "made with a
  newer version" dialog and **does not silently resave over it** (the
  file on disk is byte-unchanged after the refused load).
- L [ ] M [ ] W [ ] Window title: `<ProjectName> — PyGameMaker IDE`;
  trailing ` *` appears in real time on the first unsaved edit and
  disappears on save.
- L [ ] M [ ] W [ ] Invalid / unreadable project file shows an error
  message, no crash; missing asset references handled gracefully.

### Tools → Restore Deleted Assets (soft-delete Trash)

- L [ ] M [ ] W [ ] Deleting an asset that's still referenced elsewhere
  shows a usage-impact warning listing what the delete would clear.
- L [ ] M [ ] W [ ] Tools → Restore Deleted Assets… lists trashed assets;
  Restore brings one back (refusing to overwrite a same-named asset
  created since); Empty Trash / Delete Permanently work.
- L [ ] M [ ] W [ ] A zip export / backup taken after a soft-delete does
  **not** re-bundle the trashed asset.

---

## 4. Asset tree & editors

### Sprites / sounds / backgrounds / fonts

- L [ ] M [ ] W [ ] Create / import (PNG, JPG, GIF for sprites; WAV, MP3,
  OGG for sounds) / edit properties / rename / duplicate / delete for
  each asset type.
- L [ ] M [ ] W [ ] Sprite import auto-centres the origin; "Click Center"
  and manual X/Y both work; **Center-Bottom** preset selectable.
- L [ ] M [ ] W [ ] Sound preview playback.
- L [ ] M [ ] W [ ] Imported-but-unsaved sprite is visible in the object
  editor's sprite dropdown; the red "(not imported)" badge self-heals on
  save.
- L [ ] M [ ] W [ ] Deleting / renaming a room, object or playground
  removes/moves its `<type>/<name>.json` side file — **no resurrection**
  when the name is reused.

### Sprite editor

- L [ ] M [ ] W [ ] Pencil / line / rectangle / ellipse / fill / select
  tools draw; colour palette + custom colour.
- L [ ] M [ ] W [ ] Frame add / duplicate / **delete** are all undoable;
  drawing during playback doesn't lose strokes; a marquee selection
  doesn't dirty the sprite; margin clicks don't paint edge pixels; the
  eyedropper drag doesn't paint.
- L [ ] M [ ] W [ ] Moving a *selection* doesn't blank the sprite;
  `save()` flattens a floating selection.
- L [ ] M [ ] W [ ] "Precise Collision" checkbox toggles the per-sprite
  flag; survives save → reopen; GMK import carries it through.

### Room editor

- L [ ] M [ ] W [ ] Grid display toggle, grid snap toggle, zoom in/out,
  pan/scroll.
- L [ ] M [ ] W [ ] Instance place / click-select / multi-select
  (Ctrl+click and drag-box) / move / delete (Delete key) / copy-paste.
- L [ ] M [ ] W [ ] Scaled instances are clickable over their whole
  footprint; Ctrl+D doesn't clobber the copy clipboard.
- L [ ] M [ ] W [ ] Clear All and Shift All are **undoable**;
  paste / duplicate / paint **redo** works.
- L [ ] M [ ] W [ ] Room background: select, stretch, tiling, scroll
  speed; multi-layer backgrounds; a background renamed elsewhere updates
  its reference here.
- L [ ] M [ ] W [ ] Room size, room speed, first-room order.
- L [ ] M [ ] W [ ] Tile Palette: paint / erase tiles; tiles persist and
  export.

### Object editor

- L [ ] M [ ] W [ ] Assign sprite; toggle Visible / Solid / Persistent /
  Stay-destroyed; set depth; set parent.
- L [ ] M [ ] W [ ] Object properties edited in the **right panel with no
  editor open** write through to the model and mark dirty; a drag-reorder
  isn't discarded by a later asset delete.
- L [ ] M [ ] W [ ] Events panel: add every event type; add actions;
  reorder (Move Up/Down); remove; nested then/else blocks; an
  unknown / Blockly-only action still shows as a row so Remove/Move hit
  the right action.
- L [ ] M [ ] W [ ] Editing a `set_sprite` action keeps `<self>` (doesn't
  silently re-point to the first sprite).
- L [ ] M [ ] W [ ] An **unrecognised extension action** (extension not
  installed) renders amber, names its owning extension, and its
  double-click shows a real message — not a silent no-op.
- L [ ] M [ ] W [ ] A room and an object that share a name can both be
  open; deleting one doesn't close the other.

### Blockly editor

- L [ ] M [ ] W [ ] Opens for an object/event; every toolbox category
  visible and colour-distinct; categories expand/collapse.
- L [ ] M [ ] W [ ] Blocks drag from the toolbox; snap together;
  disconnect; delete (Delete key or drag-to-trash); duplicate (Ctrl+D);
  copy/paste (Ctrl+C / Ctrl+V).
- L [ ] M [ ] W [ ] Undo (Ctrl+Z) / Redo (Ctrl+Y); multiple undo steps.
- L [ ] M [ ] W [ ] Block params: dropdowns, number inputs, text inputs;
  the object / sprite / sound / room selection dropdowns **populate** from
  the project.
- L [ ] M [ ] W [ ] Workspace: zoom in/out, pan/scroll; the layout
  **saves** and reloads with the project.
- L [ ] M [ ] W [ ] Generated code runs in a real Test Game.
- L [ ] M [ ] W [ ] Presets (Full / Beginner / Intermediate / Platformer /
  Grid RPG / Sokoban / Implemented-Only): switching one updates the
  toolbox; disabled blocks aren't shown; the choice persists. Tools →
  Configure Action Blocks changes what's offered; Select All / Select
  None on the left; Save commits, Cancel discards.

### Code editor

- L [ ] M [ ] W [ ] Python code editor opens; syntax highlighting; toolbar
  Undo/Redo and Edit → Undo work (not just Ctrl+Z); saves; executes
  in-game; `execute_code` binds `self`, `other`, `game`, `keyboard`,
  `math`.

---

## 5. Events & actions — runtime pass

The largest section. Build test projects (or reuse the bundled samples)
and verify **every event fires** and **every action does what it should**
in a real Test Game run. A good coverage plan is one small project per
game genre, each adding the events/actions the previous didn't need:

1. **Sokoban** — grid movement, push, `if_collision`, blocks, `next_room`
2. **Labyrinth / rogue-like** — `keyboard_press`, alarms, `destroy`,
   chase AI, health/lives, sound
3. **Platformer** — `keyboard_release`, `begin/end_step`, gravity,
   friction, `move_to_contact`, `bounce`, `set_sprite`
4. **Scrolling shooter** — `outside_room`, `animation_end`,
   `no_more_lives/health`, `create_moving_instance`, `wrap_around_room`
5. **Racing** — `intersect_boundary`, `room_start/end`, `set_room_speed`,
   views/camera, high-score table
6. **Zelda-like** — `draw`, `game_start/end`, mouse events, user events,
   `test_question`, `test_expression`, `goto_room`, `set_room_persistent`

### 5.1 Events — each one fires and its actions run

- L [ ] M [ ] W [ ] **Create** — runs when an instance is created (room
  start *and* dynamically via `create_instance`); variable init works;
  fires **once per instance**.
- L [ ] M [ ] W [ ] **Destroy** — runs when an instance is destroyed.
- L [ ] M [ ] W [ ] **Step / Begin Step / End Step** — every frame, in
  that order relative to movement.
- L [ ] M [ ] W [ ] **Alarm 0–11** — settable; fires at the right step
  count; can be reset.
- L [ ] M [ ] W [ ] **Keyboard (held)** — fires continuously while held;
  arrow keys, WASD, Space, Enter, numpad, punctuation.
- L [ ] M [ ] W [ ] **Key Press** — once on key-down; every letter/number
  key.
- L [ ] M [ ] W [ ] **Key Release** — once on key-up.
- L [ ] M [ ] W [ ] **No Key** — fires when nothing is held (order: runs
  before Step).
- L [ ] M [ ] W [ ] **Any Key**.
- L [ ] M [ ] W [ ] **Mouse** — left/right/middle press, release, held;
  mouse enter / leave an instance; global (anywhere on screen) variants.
- L [ ] M [ ] W [ ] **Collision with <object>** — fires on the first step
  the footprints overlap (a continuous overlap = one hit); solid vs
  non-solid; multiple collision events on one object.
- L [ ] M [ ] W [ ] **Outside Room** — fires when the sprite is fully
  off-screen, **including for a nonzero-origin sprite**.
- L [ ] M [ ] W [ ] **Intersect Boundary**.
- L [ ] M [ ] W [ ] **Game Start** — fires once, survives a room restart
  (authored score/lives/caption setup runs).
- L [ ] M [ ] W [ ] **Game End**, **Room Start**, **Room End**,
  **Animation End**, **No More Lives**, **No More Health**.
- L [ ] M [ ] W [ ] **User-defined events** (called via Call Parent /
  trigger).
- L [ ] M [ ] W [ ] **Draw** — overrides default sprite drawing; **Draw
  GUI** for a HUD over a scrolling view; Draw Begin / Draw End.

### 5.2 Actions — each one does what it should

- L [ ] M [ ] W [ ] **Movement** — Move Fixed (8 dirs + stop), Move Free,
  Move Towards Point, Set Speed / Direction, Set H/V Speed, Reverse
  H/V, Set Gravity, Set Friction, Jump to Position / Start / Random,
  Snap to Grid, Wrap Screen, Move to Contact, Bounce, Move Grid.
- L [ ] M [ ] W [ ] **Instance** — Create, Create with Motion, Create
  Random, Change Instance, Destroy Instance (self / other), Destroy at
  Position. Spawned instances are **visible next frame** and inherit
  parent events/collisions; a spawner in Step does **not** hang the
  frame; a collision-spawned instance's Create event reads **its own**
  speed, not the colliding pair's.
- L [ ] M [ ] W [ ] **Control flow** — If Variable / Instance Count /
  Dice / Question / Expression / Mouse Button / Aligned-with-Grid; Start
  Block / End Block; Else; Exit Event; Repeat; Call Parent Event.
  `set_sprite` keeps `<self>`. `if_condition` runs its then-branch
  **once**, not twice.
- L [ ] M [ ] W [ ] **Room** — Next / Previous / Restart Room, Go to Room,
  If Next/Previous Room Exists, Set Room Speed, Set Room Caption, Set
  Room Persistent, Set Background Color, Set Background.
- L [ ] M [ ] W [ ] **Variable** — Set Variable (self / other / global,
  relative), If Variable, Draw Variable.
- L [ ] M [ ] W [ ] **Score / Lives / Health** — Set / If / Draw for each;
  Draw Health Bar; `test_health` `<=0` / `>=N` death checks trigger;
  `no_more_health` / `no_more_lives` fire on the 0 crossing.
- L [ ] M [ ] W [ ] **Drawing** — Draw Sprite / Background / Text / Text
  Transformed / Rectangle / Ellipse / Line / Arrow; Set Color (honours a
  `color` param on `draw_text`); Set Font; Set Full Screen; the minimap
  and DOOM-HUD macro actions.
- L [ ] M [ ] W [ ] **Sound** — Play Sound / Stop Sound / If Sound
  Playing / Set Volume / Set Pan; Play Music / Stop Music.
- L [ ] M [ ] W [ ] **Timing** — Set Alarm, Sleep, Set Timeline.
- L [ ] M [ ] W [ ] **Info / Game** — Display Message, Show Info, Show
  Video, Restart Game, End Game, Save Game, Load Game, Show/Clear
  Highscore.
- L [ ] M [ ] W [ ] **Execute Code / Execute Script** — real Python;
  `self`, `other`, `game`, `keyboard`, `math` all bound; a raw
  `self.<var>` runs with no silent `NameError`; `self.restart_room_flag`
  / `self.next_room_flag` trigger the matching navigation.

### 5.3 Conditional-flow edge cases

- L [ ] M [ ] W [ ] Single-action conditional (no block): the **one**
  following action skips when false.
- L [ ] M [ ] W [ ] Start Block / End Block: **all** actions in the block
  run when true, **all** skip when false.
- L [ ] M [ ] W [ ] Else: first action vs else-action alternate correctly
  on true/false; an Else inside a then/else branch resolves to the right
  parent.
- L [ ] M [ ] W [ ] `exit_event` inside an if/else branch or a Repeat
  aborts the **whole** event.

### 5.4 rc.12 runtime features

- L [ ] M [ ] W [ ] **Pixel-perfect collision** (static, opt-in per
  sprite): two `precise=True` sprites whose AABBs overlap but whose masks
  don't → **no** collision; masks do overlap → collision fires; a
  rotated / non-unity-scaled `precise` instance falls back to AABB; GMK
  import carries the per-sprite flag through.
- L [ ] M [ ] W [ ] **Views / single camera**: `views_enabled = False`
  renders identically to no-views (regression guard); one visible view →
  only its port rect is drawn into; the follow target stays inside
  `(hborder, vborder)` and clamps to the room bounds.
- L [ ] M [ ] W [ ] **Views / split-screen**: two adjacent views with
  different follow targets render both; the gap shows the room background
  colour, not stale pixels; per-view `hspeed`/`vspeed` clamps camera
  movement (`-1` = instant); `room.current_view_index` is queryable in a
  draw event.

### 5.5 Runtime spot-checks from the 2026-06-11 audit

- L [ ] M [ ] W [ ] Imported maze/platformer samples run at the **authored
  speed**, not double-speed (GMK `room_speed` honoured).
- L [ ] M [ ] W [ ] Pushing a sprite with a transparent margin / nonzero
  origin lands **flush** against a wall (no jitter / off-grid).
- L [ ] M [ ] W [ ] A **persistent** player survives `restart_room`;
  after `restart_game` rooms 2..N are fresh; re-entering a room doesn't
  re-run its Create events.
- L [ ] M [ ] W [ ] Releasing a movement key **while a message dialog is
  open** does NOT leave the character moving after it closes.
- L [ ] M [ ] W [ ] `key_pressed` arrow conditions and `mouse_check`
  button / over-object conditions actually fire.
- L [ ] M [ ] W [ ] Next / Previous / Restart-Room dropdown options
  navigate.

### 5.6 Edge cases & performance

- L [ ] M [ ] W [ ] `create_instance` with a non-existent object name →
  warning, no crash; an invalid expression → falls back to 0, no crash.
- L [ ] M [ ] W [ ] Instance at a room edge / outside room bounds; Jump
  to Random in a very small room; Next Room from the last room / Previous
  from the first → no-op, no crash.
- L [ ] M [ ] W [ ] Multiple instances of one object have independent
  state; destroying one doesn't affect the others; two moving instances
  collide.
- L [ ] M [ ] W [ ] Press several arrow keys at once; rapid press/release
  → no stuck movement.
- L [ ] M [ ] W [ ] **50+ instances** each with a Step event → acceptable
  frame rate; rapid create/destroy cycles → no leak or slowdown.

---

## 6. Game execution — Test Game / Debug

- L [ ] M [ ] W [ ] F5 opens a game window; first room loads; objects at
  correct positions; sprites + animations render; events fire; collisions
  detected; keyboard + mouse input work; sound plays; room transitions
  (and the fade transition) work; window closes cleanly.
- L [ ] M [ ] W [ ] Closing the IDE mid-run stops the game subprocess
  (no orphan `python`); a crashing game logs its traceback rather than
  failing silently.
- L [ ] M [ ] W [ ] On Windows in dev mode: pressing F5 flashes **no**
  `python.exe` console window before pygame opens.
- L [ ] M [ ] W [ ] Debug mode: debug output visible; FPS display.
- L [ ] M [ ] W [ ] Name-entry dialog (high-score) accepts typed
  characters and doesn't crash on a synthetic `KEYDOWN` with no
  `unicode`.

---

## 7. Bundled samples — the play-through pass

- L [ ] M [ ] W [ ] **Welcome-tab flow**: each sample opens *immediately*
  (no destination prompt, no GMK wait); the title bar shows the sample
  name; the working copy lands under `<Documents>/PyGameMaker Projects/`;
  clicking the same sample twice opens a fresh `<name>_2/`; after an edit
  + Ctrl+S the bundled `samples/<name>/` on disk is **untouched**.
- L [ ] M [ ] W [ ] **maze_1** — arrows move; walls block; **every** arrow
  key still works after touching a wall.
- L [ ] M [ ] W [ ] **maze_2 / maze_3** — play through.
- L [ ] M [ ] W [ ] **maze_4** — starts on Space; the last level shows
  `CONGRATULATIONS` + the following sentence on **two lines**.
- L [ ] M [ ] W [ ] **plateforme_1** — jump and land.
- L [ ] M [ ] W [ ] **plateforme_2** — tiles visible; Pingus falls (not
  rises); keys don't launch him off-screen.
- L [ ] M [ ] W [ ] **plateforme_3** — tiles visible; bonus objects show
  **different images** (not all frame 0); Pingus starts on the ground;
  the stomp check doesn't cost an unearned life on a fast fall; **draw
  depth-order correct** (player in front of the exit, not behind).
- L [ ] M [ ] W [ ] **match3_1 / match3_2 / match3_3** — swap, match,
  score; match3_2 swap animation plays.
- L [ ] M [ ] W [ ] **views_1** — window is **800×600 while the room is
  2400×800**; the camera scrolls as you walk (seeing the whole room at
  once = window-sizing regression).
- L [ ] M [ ] W [ ] **views_2** — camera follows the player.
- L [ ] M [ ] W [ ] **sky_strike_1** — shoot, spawn, score, lives.
- L [ ] M [ ] W [ ] **treasure** — plays; the monster's `adapt_direction`
  script runs.

---

## 8. 2.5D raycast extension (`raycast_1`–`4`)

- L [ ] M [ ] W [ ] **raycast_1** — first-person view draws: textured
  walls, floor cast, sky, billboard sprites (`obj_goal` is visible);
  moving from spawn stays inside the map (no "press Down, end up outside"
  regression).
- L [ ] M [ ] W [ ] **raycast_2** — two rooms; gems + score; the
  patrolling billboard monster costs a life; the gem-gated exit; the
  second crystal-cavern room has its own texture theme.
- L [ ] M [ ] W [ ] **raycast_3** — monsters cost **health** (−25) with
  the 45-step invulnerability window; medkits +40; `no_more_health` →
  −1 life + refill + restart; HUD = score top-left / lives top-right /
  health bar bottom-left; `M` shows the minimap with walls + the player
  marker at the correct cell.
- L [ ] M [ ] W [ ] **raycast_4** — the DOOM status bar renders in the
  bottom band (shrunk viewport, horizon in the top band); the health-
  reactive face portrait; the **key** and the **gate** look different
  (grey portcullis vs gold key); collected keys appear on the minimap;
  walls block movement.
- L [ ] M [ ] W [ ] Minimap is north-up, shows walls + player only,
  whole-map scale; the `M` toggle works in every raycast sample.

---

## 9. Block World extension (`block_world_1`–`3`)

- L [ ] M [ ] W [ ] **block_world_1** — `H` toggles a **7-line** control
  overlay; walls solid at body height but a one-block step can be walked
  onto; blocks place on top of other blocks; a block's top face is
  textured like its sides; distance fog fades the far blocks.
- L [ ] M [ ] W [ ] **block_world_2** — terrain generates and is walkable;
  gravity + jump feel right.
- L [ ] M [ ] W [ ] **block_world_3** — crafting: `set_crafting_recipe`
  registers a recipe; `craft_item` consumes inputs and yields the output
  block type; hotbar / inventory / HUD update.
- L [ ] M [ ] W [ ] Block protection (`set_block_protection`) blocks
  break/place on protected types; block reward (`set_block_reward`) pays
  score on break.

---

## 10. Multiplayer LAN (`reseau_1`–`4`) — needs **two real machines**

→ `docs/MULTIPLAYER_LAN_V2_PLAN.md` checklist. **None of this is code
work** — it needs two machines on a real network. The two-process
loopback tests prove the protocol converges, not that it feels right.

- [ ] Two real machines on a **wired school LAN**: launch `reseau_4` (or
  any two-machine sample) on both; press **H** on one and **J** on the
  other; they connect via the discovery beacon without typing an IP.
- [ ] Manual-IP path: the connect screen's digit/`.`/`:`-filtered IP
  field; "Cette machine : <ip>" shows the host's real address; a bad IP
  gives a clear error, not a silent hang.
- [ ] Windows **firewall prompt** appears on first host; allowing it lets
  the connection through.
- [ ] Runner-window caption shows `🌐 Hôte — N joueurs` / `🌐 Client —
  connecté`, and restores on `leave_game`.
- [ ] **`reseau_1`** — Tier B shared room: both players' arrow-key avatars
  move on both screens; a client's own avatar is locally simulated
  (responsive), ghosts are interpolated.
- [ ] **`reseau_2`** — "Quiz de classe": a shared scoreboard with **4+
  clients**; answers register; the host's composed strings display.
- [ ] **`reseau_3`** — "Récolte en équipe": Tier B gems + shared score;
  monster patrol; instances spawn only after players join (not before).
- [ ] Host quits mid-game → clients get `connection_lost`, ghosts are
  destroyed, but each client keeps its own avatar and continues
  single-player.
- [ ] Exported **HTML5** game joins a running desktop host from a real
  browser on a Chromebook (client-only: it can view Tier B ghosts, not
  own a synced instance).
- [ ] Exported **Kivy/Android** game runs single-player (network actions
  no-op with a surfaced warning, don't crash the export).

---

## 11. Multiplayer file-exchange (`fichier_1`) — Phase 5 manual QA

→ `docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md` Phase 5. Needs two machines
sharing a folder (network drive / synced folder).

- [ ] Two machines, one shared folder: one hosts `fichier_1`
  (`host_game_files`), the other joins (`join_game_files folder="auto"`
  or the connect screen); the join / welcome / leave handshake completes.
- [ ] A full tic-tac-toe game plays to a win **and** to a draw; both
  instances learn the game ended (X-win and O-win messages are distinct).
- [ ] `session.json` republishes on join so a client's
  `global.waiting_for_players` clears.
- [ ] The connect screen handles a synthetic `KEYDOWN` with no `unicode`
  without an `AttributeError`.

---

## 12. Preferences & settings

- L [ ] M [ ] W [ ] Preferences dialog opens; **every tab's content fits
  its panel**, including Extensions.
- L [ ] M [ ] W [ ] Language selection changes visible labels at runtime.
- L [ ] M [ ] W [ ] Theme (light/dark) switch takes effect immediately.
- L [ ] M [ ] W [ ] Font settings; grid settings persist between sessions.
- L [ ] M [ ] W [ ] Auto-save toggles persist to the config the editor
  reads at startup.

---

## 13. Export — HTML5 (in a **real browser**)

- L [ ] M [ ] W [ ] Export a sample → a single `.html` file is written.
- L [ ] M [ ] W [ ] Open it by **double-click** (`file://`) — the game
  draws and plays, **no black window**.
- L [ ] M [ ] W [ ] Open it from a **served** directory
  (`python3 -m http.server`) — same result.
- L [ ] M [ ] W [ ] Browser console shows **no JavaScript error**.
- L [ ] M [ ] W [ ] Repeat for **maze_1** (no extension), **raycast_4**
  (extension renderer + status bar) and **block_world_1**.
- L [ ] M [ ] W [ ] **Firefox and a Chromium-based browser** both.
- L [ ] M [ ] W [ ] Keyboard works, arrows included (page doesn't scroll
  instead of the player moving).
- L [ ] M [ ] W [ ] Sound plays after the first click.
- L [ ] M [ ] W [ ] Accented text renders in the game canvas.
- L [ ] M [ ] W [ ] Offline Pyodide bundle export: the game loads with no
  network (Pyodide served from the bundle, not the CDN).
- L [ ] M [ ] W [ ] PWA export: installable; the mobile responsive layout
  + on-screen d-pad / action buttons appear on a narrow viewport.
- [ ] Real **mobile browser** (phone/tablet): touch controls work.

---

## 14. Export — Desktop (`.exe` / Linux binary / `.app`)

- L [ ] M [ ] W [ ] Build → the platform's own export completes with no
  error; the artifact appears where the dialog said (single `.exe` /
  single binary / `.app`).
- L [ ] M [ ] W [ ] **Double-click it** — a window opens, the game is
  playable **with sound**, controls behave the same as Test Game.
- L [ ] M [ ] W [ ] **No `game_error.log`** appears next to the
  executable (a frozen game has no console — that file is the only trace
  of a crash).
- L [ ] M [ ] W [ ] A game with a high-score table keeps scores **after
  quitting and relaunching** (`highscores.json` appears next to the
  executable, doesn't vanish with a one-file bundle's temp dir).
- L [ ] M [ ] W [ ] Exported from a **French** IDE → the game's messages
  are French.
- L [ ] M [ ] W [ ] Export a project **named with an apostrophe**
  (e.g. `L'aventure`) — it builds; a **locked output folder** reports
  failure and keeps the build, not fake success.
- L [ ] M [ ] W [ ] Copy the artifact to **another machine of the same
  OS with no Python** and run it there (this is how a student receives a
  game).
- L [ ] &nbsp; — Linux: the copied binary is still **executable** after a
  round-trip via a FAT USB stick.
- &nbsp; M [ ] &nbsp; — macOS: the `.app` opens without "damaged and
  can't be opened" (`xattr -cr` clears a re-applied quarantine); copying
  to exFAT can flatten its symlinks.
- &nbsp;&nbsp; W [ ] — Windows: note whether SmartScreen warns ("unknown
  publisher" is expected for an unsigned build — it should still run via
  *More info → Run anyway*); run an **antivirus scan** on the `.exe` and
  note any false positive.

---

## 15. Export — Mobile (Kivy → Android / iOS)

Desktop export moved off Kivy, but **Android and iOS still use it**. Its
four known gaps (tiles, keyboard handling, collision, physics/subimages)
were fixed 2026-08-17 — but every fix was verified by *executing the
generated code*, not by running a build, so **nobody has actually played
an exported mobile build**. This section is where that gets found out;
each row names what used to be wrong so a regression is recognisable.

- L [ ] M [ ] W [ ] Build → Mobile export produces a project / APK
  without crashing the IDE; an **accented project name** builds; a
  failed/cancelled build cleans its temp dir and doesn't double-report.
- [ ] On a real device: **tiles are visible** in plateforme_2 / _3.
- [ ] The player **falls, not rises**, and lands **on** the ground.
- [ ] **Jump works** (the ground probe is below the player).
- [ ] **Walls block** the player; you can still walk while grounded.
- [ ] **Each arrow moves its own way** — up goes up (all four used to go
  right, vertical inverted on top).
- [ ] **maze_4 starts** on any key.
- [ ] **plateforme_3's bonuses show different pictures** (subimage crop).
- [ ] raycast + block_world renderers draw on-device (viewport, HUD,
  minimap, DOOM bar).
- [ ] `execute_code` / `execute_script` bind `game` (score/lives/health
  proxy) without a `NameError`.

---

## 16. Export — Project & package round-trips

- L [ ] M [ ] W [ ] File → Export Project (`.zip`) then reopen it —
  assets, rooms, objects, code all intact.
- L [ ] M [ ] W [ ] Object / Room **package** export then import into a
  fresh project — round-trips **non-PNG** sprite/background assets;
  cross-references resolve; a package with a `../` asset name is rejected
  (Zip Slip guard).
- L [ ] M [ ] W [ ] Cross-platform "open folder?" prompt after each
  export uses the OS-native open command (start / open / xdg-open) —
  HTML5, exe, linux, macos, android, iOS.

---

## 17. Localization

- L [ ] M [ ] W [ ] Tools → Preferences → Language lists all **11**
  entries (English + de es fr it ja pt ru sl uk zh).
- L [ ] M [ ] W [ ] Switch to **French**: menus, dialogs, Welcome tab are
  French, correct accents, **no mojibake** (`Ã©`, `â€"`).
- L [ ] M [ ] W [ ] Welcome tab lists the 2.5D samples as
  `2.5 D — Level 1…4` (French `2.5 D — Niveau 1`), not longer pre-rename
  wording.
- L [ ] M [ ] W [ ] Spot-check **日本語 / 中文**: glyphs render, not
  boxes (a font-availability question — genuinely differs per platform).
- L [ ] M [ ] W [ ] **pt / ja / zh full-IDE eyeball** beyond Preferences +
  New Project: main window menu/toolbar/status bar, Room Editor, Object
  Editor, **Export dialog** — every string resolves, no truncation, no
  leftover English. (Known: the OK/Cancel button box falls back to
  `qtbase_<lang>.qm`, not this app's catalog — a packaging decision.)
- L [ ] M [ ] W [ ] Type accented characters into a **project name, an
  object name and a `draw_text` string** — they survive save → reopen.
- L [ ] M [ ] W [ ] With the IDE in French, a sample's **in-game
  messages** appear in French (e.g. raycast_4's *« La porte est
  verrouillée. Trouve d'abord toutes les clés ! »*).
- L [ ] M [ ] W [ ] Full Action Reference / Event Reference in a
  non-English language: run
  `PYTHONUTF8=1 python3 tools/gen_action_reference.py fr de uk ru it es pt sl`
  — no missing-string report, no crash.

---

## 18. Help / About / documentation

- L [ ] M [ ] W [ ] Help menu accessible; About dialog shows the **right
  version**; website / GitHub / LICENSE links open the right targets.
- L [ ] M [ ] W [ ] Documentation and Tutorials footer links open.
- L [ ] M [ ] W [ ] Tutorial panel: open each of the 9 in-app lessons —
  no "Tutorial not found" / "No content" / "Error loading page"; every
  page renders substantial content. Repeat with the IDE set to each of
  de/es/fr/it/pt/ru/sl/uk (their `Tutorials/<lang>/` folders); ja/zh fall
  back cleanly to English.

---

## 19. Published GitHub wiki spot-check

Not viewed live since the 2026-07-29 sweep + the 2026-09-10 tutorial-
screenshots publish. Open <https://github.com/Gabe1290/pythongm/wiki>:

- [ ] Home + the language-switcher banners on a few pages resolve (no
  404s).
- [ ] Accented pages (fr, de, it, es, pt, sl) render accents, **not
  mojibake**; accented section headers match their ToC anchors;
  `Full-Action-Reference#3d-view`-style deep links land.
- [ ] **Per-step tutorial screenshots**: open `Tutorial-Breakout`,
  `Tutorial-Pong`, … `Tutorial-LunarLander` and a few translated variants
  (`Tutorial-Platformer_fr`, `Tutorial-LunarLander_ru`) — the
  `images/tutorial-*.png` screenshots load (not broken-image icons) and
  sit under the right step.
- [ ] The re-synced `Tutorial-Platformer_*` / `Tutorial-LunarLander_*`
  pages read cleanly in each language (they were rewritten to full
  length — spot-check accents + that technical identifiers stayed
  English).
- [ ] Decide separately whether to publish the unrelated wiki backlog
  still sitting un-pushed in `wiki/` (FileExchange page,
  Full-Action-Reference regens, Home / Network / Extensions edits) via a
  full `scripts/sync_wiki.sh push`.

---

## 20. Packaged IDE (PyInstaller one-file build for students)

Build **on** the target OS with `python3 scripts/build_pyinstaller.py`
(spec: `PyGameMaker.spec` — CI/lite; `PyGameMaker-full.spec` adds Kivy so
the packaged IDE can also do EXE export).

- L [ ] M [ ] W [ ] The IDE launches from the packaged one-file
  executable (`.app` bundle on macOS); **no empty directories** created
  in the launch folder.
- L [ ] M [ ] W [ ] Projects create / open; games run (F5) — the real
  pygame engine, not a fallback; room preview shows an appropriate
  message.
- L [ ] M [ ] W [ ] The packaged build carries `extensions/` and
  `plugins/` — LAN multiplayer (`host_game` / the reseau_4 H/J keys),
  audio actions (`play_sound`), and the 2.5D + Block World renderers all
  **work in the packaged app**, not just from source (this regressed in
  1.3.0, was fixed in 1.3.1, and is regression-guarded by
  `tests/test_ide_bundle_spec.py`).
- L [ ] M [ ] W [ ] `samples/`, `Tutorials/` and Blockly assets present.
- L [ ] M [ ] W [ ] No Python-related errors in the console; all UI
  elements render.

---

## 21. Error handling & recovery

- L [ ] M [ ] W [ ] `project.json` survives a simulated mid-save failure
  (atomic write); a folder save **rolls back across files** on an error
  mid-write.
- L [ ] M [ ] W [ ] Syntax error in `execute_code` shows a helpful
  message, not a bare traceback that kills the game silently.
- L [ ] M [ ] W [ ] Undo works after a caught error.
- L [ ] M [ ] W [ ] Importing an object/room package **after unsaved
  edits** doesn't silently discard them.
- L [ ] M [ ] W [ ] A tutorial with an external link doesn't blank the
  page; an edition that gates tutorials shows a placeholder, not an empty
  list, when a curated tutorial is missing under a non-en/fr language.

---

## 22. Per-platform gotchas (read before you start each OS)

- **Linux** — Debian is what the school labs run. If a game window won't
  open, suspect `SDL_VIDEODRIVER` first (Wayland vs X11 differ). Confirm
  the IDE runs on the **distribution's own Python**, not only a venv.
- **macOS** — Gatekeeper *silently* kills an unsigned quarantined `.app`
  (nothing happens on double-click). `xattr -cr` clears it. The `.app` is
  a directory — copying to exFAT can flatten its symlinks. macOS does not
  claim Retina, so a slightly soft game window is expected.
- **Windows** — console codepage is cp1252: run from a terminal at least
  once and confirm log output is readable, not encoding errors. Use
  `py -3.12`, never bare `python3` (Store stub or unsupported 3.14).
  OneDrive-redirected Desktop/Documents: dialogs must default to the
  redirected path, not a non-existent `~/Desktop`.

---

## 23. Audit-fix regression sign-off (2026-06-11 full audit — 111 findings)

The automated suite (Section 1) is the primary validator for these — it
carries a regression test per fix. Re-run these platform-sensitive
spot-checks on **each** desktop OS. Runtime items are in §5.5 above; the
rest:

### 23.1 Editors

- L [ ] M [ ] W [ ] **Sprite editor**: eyedropper drag doesn't paint;
  frame add / duplicate / **delete** are undoable; drawing during
  playback doesn't lose strokes; margin clicks don't paint edge pixels;
  a selection marquee doesn't dirty the sprite.
- L [ ] M [ ] W [ ] **Room editor**: Clear All / Shift All are undoable;
  paste / duplicate / paint **redo** works; scaled instances are
  clickable over their whole footprint; Ctrl+D doesn't clobber the copy
  clipboard.
- L [ ] M [ ] W [ ] **Script editor**: toolbar Undo/Redo and Edit → Undo
  work (not just Ctrl+Z).
- L [ ] M [ ] W [ ] A room and an object that **share a name** can both
  be open; deleting one doesn't close the other.

### 23.2 Events / actions config dialogs

- L [ ] M [ ] W [ ] Editing a `set_sprite` action keeps `<self>` (doesn't
  silently re-point to the first sprite); a `draw_lives` empty-sprite is
  reachable.
- L [ ] M [ ] W [ ] `check_empty` dropdown shows only solid / all (no
  bogus object names); an unknown / Blockly-only action still appears as
  a row so Remove / Move hit the right action.

### 23.3 Importers

- L [ ] M [ ] W [ ] A normal `.gmk` imports; a hostile / corrupt one
  (huge declared image / zlib sizes) is rejected with a warning, not an
  OOM hang; GMK image dimensions are clamped.

### 23.4 Exporters (run the native target per OS)

- L [ ] M [ ] W [ ] Desktop export of a project **named with an
  apostrophe** (`L'aventure`) builds; a **locked output folder** reports
  failure and keeps the build, not fake success.
- L [ ] M [ ] W [ ] Kivy / desktop export: collision actions, jump,
  keyboard-release and non-PNG backgrounds all work; a quoted / newline
  message doesn't break the build.
- L [ ] M [ ] Android export (Linux/macOS native): an **accented project
  name** builds; a failed / cancelled build cleans its temp dir and
  doesn't double-report.
- L [ ] M [ ] W [ ] Object / Room **package** export+import round-trips
  **non-PNG** sprite / background assets.

### 23.5 Assets / project / widgets / IDE lifecycle

- L [ ] M [ ] W [ ] Deleting / renaming a room, object or playground
  removes / moves its `<type>/<name>.json` side file — no resurrection on
  reuse.
- L [ ] M [ ] W [ ] Editing object properties in the right panel with
  **no editor open** writes through and marks dirty; a drag-reorder isn't
  discarded by a later asset delete.
- L [ ] M [ ] W [ ] Importing an object / room package **after unsaved
  edits** doesn't silently discard them.
- L [ ] M [ ] W [ ] Imported assets are readable under the **dark theme**
  (not black-on-dark).
- L [ ] M [ ] W [ ] New Project description persists into Project
  Settings; Export Options checkboxes (Debug / Optimize) take effect.
- L [ ] M [ ] W [ ] Opening a `.zip` project then quitting / switching
  doesn't leave a temp extraction behind in TEMP.
- L [ ] M [ ] W [ ] A tutorial with an external link doesn't blank the
  page; a tutorial-gating edition shows a placeholder, not an empty
  list, when a curated tutorial is missing under a non-en/fr language.
- L [ ] M [ ] W [ ] `project.json` survives a simulated mid-save failure
  (atomic write); a folder save rolls back across files on error.

### 23.6 Latest audit

- [ ] Confirm no open **high**-severity items in
  `docs/FULL_AUDIT_2026-09-07.md` (6 high / 13 medium / 20 low — work the
  queue top-down; each fix lands with a regression test).

---

## Release sign-off

Fill in per OS. A release ships only when every OS row is signed and
every "needs a device / two machines" item above is either done or
explicitly waived in writing (with who waived it and why).

| Field | Linux | macOS | Windows |
|---|---|---|---|
| Build / tag under test | | | |
| Date tested | | | |
| OS + version | | | |
| Python / PySide6 / pygame | | | |
| `pytest` result (passed / failed / skipped) | | | |
| `smoke_run_samples` | | | |
| `verify_desktop_export --all --compare` | | | |
| Sections 2–12 (IDE + runtime) | | | |
| Section 13 (HTML5 export) | | | |
| Section 14 (desktop export) | | | |
| Section 15 (mobile export) | | | |
| Sections 16–22 | | | |
| Section 23 (audit regression) | | | |
| Tester | | | |
| Blocking issues found (count) | | | |
| **Signed off for release?** | | | |

### Cross-cutting items not tied to one OS

| Item | Status | Owner | Notes |
|---|---|---|---|
| §10 Multiplayer LAN — two real machines on a LAN | | | |
| §11 File-exchange — two machines, shared folder | | | |
| §15 Mobile — real Android/iOS device pass | | | |
| §13 HTML5 — real mobile browser / touch | | | |
| §19 Published wiki spot-check | | | |
| §14 Windows `.exe` antivirus false-positive scan | | | |

---

## Related docs (guides, not checklists)

- `docs/EXPORT_TESTING_GUIDE.md` — export deep-dive (per-target
  prerequisites, known limitations, how to diagnose a bad build)
- `docs/ANDROID_EXPORT.md`, `docs/BUILDING.md` — build prerequisites
- `docs/MULTIPLAYER_LAN_V2_PLAN.md`,
  `docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md` — the multiplayer QA lists
  §10 / §11 draw from
- `docs/FULL_AUDIT_2026-09-07.md` — the open-findings queue behind §23

### Formats

- **ODT**: `docs/RELEASE_QA_CHECKLIST.odt` (regenerate with
  `python3 scripts/generate_release_qa_odt.py`)
- **PDF**: `docs/PyGameMaker_Release_QA_Checklist.pdf` (regenerate with
  `python3 scripts/generate_checklist_pdf.py`)

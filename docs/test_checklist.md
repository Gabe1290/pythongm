# PyGameMaker IDE Test Checklist

A comprehensive checklist for testing all features of PyGameMaker IDE.

## 0. New in 1.0.0-rc.12 (audit + visual phase)

Specifically validates the work added in the rc.12 release. Each item
references the commit it shipped in so a regression is easy to bisect.

### Welcome tab (commits e42d4b6 / 7e86274 / 37d7186)
- [ ] Welcome tab is the default tab on first launch with no project
- [ ] Title "Welcome to PyGameMaker IDE" + version label "v1.0.0-rc.12" visible
- [ ] **Get started** column shows New Project, Open Project, **More options** dropdown
- [ ] "More options" dropdown opens a menu with Open ZIP / Import GMK / Import Roberta entries
- [ ] **Continue where you left off** list shows recent projects with "N days ago" timestamps
- [ ] Clicking a recent-project row opens that project
- [ ] Recent-project list is wrapped in a visible rectangle (themed frame)
- [ ] "Clear recent projects" link hides itself when the list is empty
- [ ] Footer links (Documentation / Tutorials / About) open the right targets

### Try a sample game — bundled samples + copy-on-open (commits a8f78d0 / f8a0eb7)
- [ ] **Try a sample game** dropdown opens a menu listing Maze 1–3
- [ ] Clicking a sample opens **immediately** — no "choose output folder" prompt, no GMK-import wait
- [ ] After clicking, the IDE title shows the sample's name (e.g. `maze_1 — PyGameMaker IDE`)
- [ ] The newly-opened project lives at `<Documents>/PyGameMaker Projects/<sample>/` — not under `samples/`
- [ ] Clicking the same sample twice opens a fresh copy at `<sample>_2/`, leaving the first one alone
- [ ] After editing and pressing Ctrl+S, only the working copy changes; `samples/<sample>/` on disk is untouched
- [ ] Each sample loads to an editable state (assets visible in the asset tree, rooms openable, etc.)

### Window title (commit 00911b3)
- [ ] No-project title: "PyGameMaker IDE"
- [ ] Project loaded: "&lt;ProjectName&gt; — PyGameMaker IDE"
- [ ] After unsaved edits: trailing " *" appears in title in real time
- [ ] After save: " *" disappears

### Toolbar (commit 00911b3)
- [ ] Hover any toolbar icon → tooltip with descriptive text + shortcut hint
  (e.g. "Save Project (Ctrl+S)", "Test Game (F5)")
- [ ] Save / Test / Debug / Export / Import Sprite / Import Sound icons grey
      out when no project is open
- [ ] Same icons enable correctly once a project is loaded
- [ ] New / Open icons stay enabled in both states

### Tools menu graying (commit 78e190d)
- [ ] No project loaded: "Validate Project", "Migrate to Modular Structure",
      and Thymio → Add Event / Add Action are greyed out
- [ ] No project loaded: Preferences, Configure Action Blocks, Configure
      Thymio Blocks, Language, Open Playground, Import Open Roberta XML
      stay enabled
- [ ] Project loaded: every Tools item becomes enabled

### Asset tree empty-state hint (commit 00911b3)
- [ ] No project loaded: italic hint visible below the category list
      ("No project loaded. Use File → New / Open Project to begin.")
- [ ] Hint disappears once a project loads
- [ ] Hint dims correctly under both light and dark themes

### Right panel empty-state placeholder (commit 00911b3)
- [ ] No project loaded: the Asset Information / Properties / Preview
      group boxes are hidden; one centred italic message takes their place
- [ ] Message appears in both light and dark themes
- [ ] Project loaded: the three group boxes reappear; placeholder is hidden

### Aseba code export (commit 71e19f3)
- [ ] File → Export menu contains "Export Aseba (Thymio) code…"
- [ ] Item is greyed out when no project is open, enabled when one is
- [ ] Clicking it prompts for an output directory
- [ ] On a project with Thymio objects: writes one `.aesl` per object + a
      `README.md` to the chosen directory
- [ ] On a project without Thymio objects: shows the "No Thymio objects
      found" warning instead of the generic failure dialog
- [ ] Success dialog offers to open the output folder; works on
      Windows / macOS / Linux

### Cross-platform export "open folder" prompts (commit a44f750)
- [ ] After a successful Linux-binary export, the "open folder?" prompt
      uses the correct OS-native open command (start / open / xdg-open)
- [ ] Same for iOS export (where reachable)
- [ ] Same for HTML5, exe, macos, android exports (regression check)

### Localised Desktop / Documents defaults (commit 53ec9ae)
- [ ] On Windows with OneDrive-redirected Desktop: export dialog defaults
      to the OneDrive-Desktop path, not a non-existent `~/Desktop`
- [ ] On Linux with non-English locale: export dialog defaults to the
      localised desktop folder (Bureau / Schreibtisch / etc.)
- [ ] New-project dialog defaults to the localised Documents folder

### Windows console flash suppressed (commit 53ec9ae)
- [ ] On Windows in dev mode, pressing F5 to Test Game: no `python.exe`
      console window flashes before pygame opens

### Dialog button bar ordering (commit 00911b3)
- [ ] Sprite Strip Import dialog: Cancel/OK button row follows the
      platform convention (OK-then-Cancel on Win/Linux, Cancel-then-OK
      on macOS)
- [ ] Blockly Block Config dialog: Select All / Select None stay on the
      left; Save/Cancel pair on the right follows the platform convention

### Translation coverage (commit ad47e68)
- [ ] Switching language at runtime (Tools → Language) actually changes
      the visible labels (sanity check that .qm files load)
- [ ] All 7 active languages (de, es, fr, it, ru, sl, uk) appear in the
      Language menu when their .qm files are present

---

## 1. Application Startup & Basic Operations

- [x] Application launches without errors  *(verified post-`afb9c75`: clean console, no Qt UniqueConnection warning, no duplicate `pygm.X` log lines)*
- [ ] Main window displays correctly
- [ ] Menu bar is visible and responsive
- [ ] Toolbar buttons are visible and clickable
- [ ] Status bar shows information
- [ ] Asset tree panel is visible
- [ ] Properties panel is visible

## 2. Project Management

- [ ] Create new project (File > New Project)
- [ ] Open existing project (File > Open Project)
- [ ] Save project (File > Save / Ctrl+S)
- [ ] Save project as new name (File > Save As)
- [ ] Close project (File > Close Project)
- [ ] Recent projects list works
- [ ] Project settings dialog opens and saves

## 3. Asset Tree Operations

### Sprites
- [ ] Create new sprite
- [ ] Import sprite from image file (PNG, JPG, GIF)
- [ ] Edit sprite properties (name, origin, collision mask)
- [ ] Delete sprite
- [ ] Duplicate sprite
- [ ] Rename sprite

### Sounds
- [ ] Create/import new sound (WAV, MP3, OGG)
- [ ] Preview sound playback
- [ ] Edit sound properties
- [ ] Delete sound

### Backgrounds
- [ ] Create new background
- [ ] Import background image
- [ ] Edit background properties (tiling, scrolling)
- [ ] Delete background

### Objects
- [ ] Create new object
- [ ] Assign sprite to object
- [ ] Edit object properties (visible, solid, depth, persistent)
- [ ] Add events to object
- [ ] Add actions to events
- [ ] Delete object
- [ ] Duplicate object
- [ ] Parent/child object relationships

### Rooms
- [ ] Create new room
- [ ] Edit room properties (width, height, speed)
- [ ] Set room background
- [ ] Place object instances in room
- [ ] Move/resize instances
- [ ] Delete instances
- [ ] Set room order (first room)
- [ ] Delete room

## 4. Object Events Testing

### Create Event
- [ ] Add Create event
- [ ] Actions execute when instance is created
- [ ] Variable initialization works

### Destroy Event
- [ ] Add Destroy event
- [ ] Actions execute when instance is destroyed

### Step Events
- [ ] Step event fires every frame
- [ ] Begin Step event fires before Step
- [ ] End Step event fires after Step

### Alarm Events
- [ ] Alarm 0-11 can be set
- [ ] Alarm triggers at correct time
- [ ] Alarm can be reset

### Keyboard Events
- [ ] Key Press event (fires once on key down)
- [ ] Key Release event (fires once on key up)
- [ ] Key Down event (fires continuously while held)
- [ ] Specific key detection (Arrow keys, WASD, Space, Enter, etc.)
- [ ] Any key detection

### Mouse Events
- [ ] Left button press/release/down
- [ ] Right button press/release/down
- [ ] Middle button press/release/down
- [ ] Mouse enter (cursor enters instance)
- [ ] Mouse leave (cursor leaves instance)
- [ ] Global mouse events (anywhere on screen)

### Collision Events
- [ ] Collision with specific object
- [ ] Collision detection accuracy
- [ ] Multiple collision events on same object

### Other Events
- [ ] Outside Room event
- [ ] Intersect Boundary event
- [ ] Game Start event
- [ ] Game End event
- [ ] Room Start event
- [ ] Room End event
- [ ] Animation End event
- [ ] User-defined events

### Draw Events
- [ ] Draw event overrides default sprite drawing
- [ ] Draw GUI event for HUD elements
- [ ] Draw Begin/End events

## 5. Actions Testing

### Movement Actions
- [ ] Move Fixed (8 directions + stop)
- [ ] Move Free (direction + speed)
- [ ] Move Towards (target point)
- [ ] Set Speed
- [ ] Set Direction
- [ ] Set Horizontal Speed (hspeed)
- [ ] Set Vertical Speed (vspeed)
- [ ] Reverse Horizontal
- [ ] Reverse Vertical
- [ ] Set Gravity
- [ ] Set Friction
- [ ] Jump to Position
- [ ] Jump to Start Position
- [ ] Jump to Random Position
- [ ] Snap to Grid
- [ ] Wrap Screen
- [ ] Move to Contact
- [ ] Bounce against objects

### Instance Actions
- [ ] Create Instance
- [ ] Create Instance with Motion
- [ ] Create Random Instance
- [ ] Change Instance (transform to different object)
- [ ] Destroy Instance
- [ ] Destroy at Position

### Control Flow Actions
- [ ] If Variable (comparison)
- [ ] If Instance Count
- [ ] If Dice (random chance)
- [ ] If Question (user prompt)
- [ ] If Expression
- [ ] If Mouse Button
- [ ] If Instance Aligned with Grid
- [ ] Start Block / End Block
- [ ] Else
- [ ] Exit Event
- [ ] Repeat
- [ ] Call Parent Event

### Room Actions
- [ ] Go to Next Room
- [ ] Go to Previous Room
- [ ] Restart Room
- [ ] Go to Room (specific)
- [ ] If Previous Room Exists
- [ ] If Next Room Exists

### Variable Actions
- [ ] Set Variable
- [ ] If Variable
- [ ] Draw Variable

### Score/Lives/Health Actions
- [ ] Set Score
- [ ] If Score
- [ ] Draw Score
- [ ] Set Lives
- [ ] If Lives
- [ ] Draw Lives
- [ ] Set Health
- [ ] If Health
- [ ] Draw Health
- [ ] Draw Health Bar

### Drawing Actions
- [ ] Draw Sprite
- [ ] Draw Background
- [ ] Draw Text
- [ ] Draw Text Transformed
- [ ] Draw Rectangle
- [ ] Draw Ellipse
- [ ] Draw Line
- [ ] Draw Arrow
- [ ] Set Color
- [ ] Set Font
- [ ] Set Full Screen

### Sound Actions
- [ ] Play Sound
- [ ] Stop Sound
- [ ] If Sound Playing
- [ ] Set Volume
- [ ] Set Pan

### Timing Actions
- [ ] Set Alarm
- [ ] Sleep (pause execution)
- [ ] Set Timeline

### Info/Game Actions
- [ ] Display Message
- [ ] Show Info
- [ ] Show Video
- [ ] Restart Game
- [ ] End Game
- [ ] Save Game
- [ ] Load Game

## 6. Room Editor

- [ ] Grid display toggle
- [ ] Grid snap toggle
- [ ] Zoom in/out
- [ ] Pan/scroll room view
- [ ] Instance placement
- [ ] Instance selection (click)
- [ ] Multi-select instances (Ctrl+click or drag box)
- [ ] Move selected instances
- [ ] Delete selected instances (Delete key)
- [ ] Copy/paste instances
- [ ] Instance properties panel
- [ ] Layer management (if applicable)
- [ ] Background layer editing
- [ ] View settings (show/hide elements)

## 7. Blockly Visual Programming

- [ ] Blockly editor opens for actions
- [ ] Blocks can be dragged from toolbox
- [ ] Blocks snap together correctly
- [ ] Block deletion works
- [ ] Undo/redo in Blockly
- [ ] Code generation from blocks
- [ ] All action categories available in toolbox
- [ ] Custom blocks (if any)

## 8. Code Editor

- [ ] Python code editor opens
- [ ] Syntax highlighting works
- [ ] Code completion (if available)
- [ ] Code can be saved
- [ ] Code executes correctly in game

## 9. Game Execution

### Run Game (F5)
- [ ] Game window opens
- [ ] First room loads correctly
- [ ] Objects appear at correct positions
- [ ] Sprites display correctly
- [ ] Animations play
- [ ] Events fire correctly
- [ ] Collisions detected
- [ ] Keyboard input works
- [ ] Mouse input works
- [ ] Sound plays
- [ ] Room transitions work
- [ ] Game can be closed cleanly

### Debug Mode
- [ ] Debug output visible
- [ ] FPS display (if enabled)
- [ ] Variable inspection (if available)
- [ ] Step-through execution (if available)

## 10. Export/Build

### HTML5 Export
- [ ] Export to HTML5 works
- [ ] Game runs in browser
- [ ] All features work in browser

### Standalone Export
- [ ] Export to executable works
- [ ] Game runs without IDE
- [ ] All assets bundled correctly

## 11. Preferences/Settings

- [ ] Preferences dialog opens
- [ ] Language selection works
- [ ] Theme selection works (light/dark)
- [ ] Font settings work
- [ ] Grid settings persist
- [ ] Settings save between sessions

## 12. Help System

- [ ] Help menu accessible
- [ ] Documentation opens
- [ ] About dialog shows version info
- [ ] Links work (website, GitHub, etc.)

## 13. Standalone Executable Testing

- [ ] Application launches from executable
- [ ] No empty directories created in launch folder
- [ ] Projects can be created/opened
- [ ] Games can be run (F5)
- [ ] Room preview shows appropriate message
- [ ] All UI elements render correctly
- [ ] No Python-related errors in console

## 14. Error Handling

- [ ] Invalid project file shows error message
- [ ] Missing asset references handled gracefully
- [ ] Syntax errors in code show helpful messages
- [ ] Crash recovery (autosave, if available)
- [ ] Undo works after errors

---

## 15. Audit-fix validation (2026-06-11 full audit: 15 high / 61 medium / 35 low)

Re-run on **each** desktop OS to confirm the audit fixes hold. Every line has a
per-platform tri-box — tick **L**inux / **W**indows / **m**acOS as you verify
it. Each item is tagged with the audit ID(s) it validates; full descriptions
live in `docs/FULL_AUDIT_2026-06-11.md`. The bulk of the fixes ship with
automated regression tests (15.0), so on a given OS you can run the suite first
and then spot-check the platform-sensitive items below.

### 15.0 Automated regression suite (the primary validator)

- [ ] L · [ ] W · [ ] m — `pytest tests/ -q` reports **0 failures**
      (Windows: `py -3.12 -m pytest tests/ -q`; Linux/macOS: `python3 -m pytest tests/ -q`).
      Expected ~1080 passed on the Windows box; pass count grows as tests are
      added, skip count is env-dependent — treat any non-zero **failure** as a
      regression (per CLAUDE.md).
- [ ] L · [ ] W · [ ] m — `python tools/smoke_run_samples.py` — all bundled
      samples boot and run their loop with no fatal crash (headless, SDL dummy).
- [ ] L · [ ] W · [ ] m — `python tools/smoke_room_lifecycle.py` — room
      restart / change / restart_game and create-once hold on real sample data
      (validates M48/M51/M52/M53).

### 15.1 Runtime / gameplay (Test Game on the bundled samples)

- [ ] L · [ ] W · [ ] m — Imported maze/platformer samples run at the authored
      speed, not double-speed (GMK `room_speed` honored) (M48)
- [ ] L · [ ] W · [ ] m — A spawner that creates instances each step no longer
      hard-hangs the frame; spawned instances appear next frame (M49, M46)
- [ ] L · [ ] W · [ ] m — Bullets/enemies spawned via Create Moving/Random
      Instance are **visible** and inherit parent events/collisions (M46, M47)
- [ ] L · [ ] W · [ ] m — `exit_event` inside an if/else branch or a repeat
      block aborts the whole event; an `if_condition` then-branch runs **once**
      (M43)
- [ ] L · [ ] W · [ ] m — Pushing a sprite with a transparent margin / nonzero
      origin lands flush against a wall (no jitter / off-grid) (M50)
- [ ] L · [ ] W · [ ] m — A persistent player survives `restart_room`; after
      `restart_game` rooms 2..N are fresh; re-entering a room doesn't re-run
      its create events (M51, M52, M53)
- [ ] L · [ ] W · [ ] m — Releasing a movement key while a message dialog is
      open does NOT leave the character moving after it closes (M54)
- [ ] L · [ ] W · [ ] m — `key_pressed` arrow conditions and `mouse_check`
      button/over-object conditions actually fire; numpad/punctuation keys work
      (M30, M31, L25)
- [ ] L · [ ] W · [ ] m — Test Health `<= 0` / `>= N` death checks trigger
      (M29); Next/Previous/Restart-Room dropdown options navigate (M28)
- [ ] L · [ ] W · [ ] m — `outside_room` fires when the sprite is fully
      off-screen for nonzero-origin sprites (L30)
- [ ] L · [ ] W · [ ] m — Custom `self.<var>` code in an event runs (no silent
      NameError); collision-spawned instances' create events read their **own**
      speed, not the colliding pair's (L28, L29, M45)

### 15.2 Thymio playground / simulator

- [ ] L · [ ] W · [ ] m — Ground sensors read the surface **in front** of the
      robot (line-following works); "Turn Left" rotates left on screen (M55, M56)
- [ ] L · [ ] W · [ ] m — Opening then closing the Thymio Playground / Run
      window repeatedly doesn't accumulate windows or memory (WA_DeleteOnClose) (L4)
- [ ] L · [ ] W · [ ] m — Blockly Thymio `if`-blocks execute their nested
      actions and don't skip the following sibling action (M44)

### 15.3 Editors (sprite / room / playground / object / script)

- [ ] L · [ ] W · [ ] m — Sprite editor: eyedropper drag doesn't paint; frame
      add/duplicate/**delete** are undoable; drawing during playback doesn't
      lose strokes; margin clicks don't paint edge pixels; selection marquees
      don't dirty the sprite (M25, M26, L15, L16, L17)
- [ ] L · [ ] W · [ ] m — Room editor: Clear All / Shift All are undoable;
      paste/duplicate/paint **redo** works; scaled instances are clickable over
      their whole footprint; Ctrl+D doesn't clobber the copy clipboard
      (M23, M24, L12, L13)
- [ ] L · [ ] W · [ ] m — Playground editor: robots get unique ports; Add
      Wall/Robot redo works; properties panel refreshes after undo/redo
      (M21, M22, L11)
- [ ] L · [ ] W · [ ] m — Script editor: toolbar Undo/Redo and Edit ▸ Undo work
      (not just Ctrl+Z) (L14)
- [ ] L · [ ] W · [ ] m — A room and an object that share a name can both be
      open; deleting one doesn't close the other (L5)

### 15.4 Events / actions config dialogs

- [ ] L · [ ] W · [ ] m — Editing a `set_sprite` action keeps `<self>` (doesn't
      silently re-point to the first sprite); `draw_lives` empty sprite is
      reachable (M27)
- [ ] L · [ ] W · [ ] m — `check_empty` dropdown shows only solid/all (no bogus
      object names); unknown/Blockly-only actions still appear as a row so
      Remove/Move hit the right action (L18, L19)

### 15.5 Importers (GMK / Roberta)

- [ ] L · [ ] W · [ ] m — Importing a normal `.gmk` works; a hostile/corrupt one
      (huge declared image/zlib sizes) is rejected with a warning, not an OOM
      hang (M40, M41, L26)
- [ ] L · [ ] W · [ ] m — Roberta import: LED colours apply (red/green/blue);
      a variable-driven LED colour doesn't crash the import (M42, L27)

### 15.6 Exporters (platform-sensitive — run the native target per OS)

- [ ] L · [ ] W · [ ] m — Desktop export of a project named with an apostrophe
      (e.g. "L'aventure") builds; a locked output folder reports failure and
      keeps the build instead of reporting fake success (M38, M39)
- [ ] L · [ ] W · [ ] m — Aseba `.aesl` export opens via Aseba Studio
      File ▸ Open (valid XML, no stray `end`) (M32, M33)
- [ ] L · [ ] W · [ ] m — Kivy/desktop export: collision actions, jump,
      keyboard-release and non-PNG backgrounds work; a quoted/newline message
      doesn't break the build (M34, M35, M36, M37, L21, L22)
- [ ] L · [ ] m — Android export (Linux/macOS native; Windows via WSL): an
      accented project name builds; a failed/cancelled build cleans its temp
      dir and doesn't double-report (L20, L23, L24)
- [ ] L · [ ] W · [ ] m — Object/Room **package** export+import round-trips
      non-PNG sprite/background assets (M58)

### 15.7 Assets / project / widgets / IDE lifecycle

- [ ] L · [ ] W · [ ] m — Deleting/renaming a room, object **or playground**
      removes/moves its `<type>/<name>.json` side file (no resurrection on reuse)
      (H3, M59)
- [ ] L · [ ] W · [ ] m — Editing object properties in the right panel with no
      editor open writes through and marks dirty; a drag-reorder isn't discarded
      by a later asset delete (M61, M60)
- [ ] L · [ ] W · [ ] m — Importing an object/room package after unsaved edits
      doesn't silently discard them (L2)
- [ ] L · [ ] W · [ ] m — Imported assets are readable under the **dark** theme
      (not black-on-dark) (L33)
- [ ] L · [ ] W · [ ] m — New Project description persists into Project Settings;
      Export Options checkboxes (Debug/Optimize) take effect (L8, L9)
- [ ] L · [ ] W · [ ] m — Opening a `.zip` project then quitting/switching
      doesn't leave a temp extraction behind in TEMP (L7)
- [ ] L · [ ] W · [ ] m — A tutorial with an external link doesn't blank the
      page; the committee edition shows a placeholder, not an empty list, under
      a non-en/fr language (L35, L1)
- [ ] L · [ ] W · [ ] m — `project.json` survives a simulated mid-save failure
      (atomic write); folder save rolls back across files on error (L34)

---

## Test Environment Notes

Track each OS pass separately so a platform-specific regression is obvious.

| Field | Linux | Windows | macOS |
|---|---|---|---|
| Date tested | | | |
| OS version | | | |
| Python / PySide6 | | | |
| `pytest` result (passed/failed) | | | |
| Tester | | | |
| Notes | | | |

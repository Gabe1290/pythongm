# PyGameMaker IDE Test Checklist

A comprehensive checklist for testing all features of PyGameMaker IDE.

> Each item has three checkboxes: **L** = Linux, **M** = macOS, **W** = Windows. Tick the box for every platform you tested it on.

## 0. New in 1.0.0-rc.12 (audit + visual phase)

Specifically validates the work added in the rc.12 release. Each item
references the commit it shipped in so a regression is easy to bisect.

### Welcome tab (commits e42d4b6 / 7e86274 / 37d7186)
- L [ ] M [ ] W [ ] Welcome tab is the default tab on first launch with no project
- L [ ] M [ ] W [ ] Title "Welcome to PyGameMaker IDE" + version label "v1.0.0-rc.13" visible
- L [ ] M [ ] W [ ] **Get started** column shows New Project, Open Project, **More options** dropdown
- L [ ] M [ ] W [ ] "More options" dropdown opens a menu with Open ZIP / Import GMK / Import Roberta entries
- L [ ] M [ ] W [ ] **Continue where you left off** list shows recent projects with "N days ago" timestamps
- L [ ] M [ ] W [ ] Clicking a recent-project row opens that project
- L [ ] M [ ] W [ ] Recent-project list is wrapped in a visible rectangle (themed frame)
- L [ ] M [ ] W [ ] "Clear recent projects" link hides itself when the list is empty
- L [ ] M [ ] W [ ] Footer links (Documentation / Tutorials / About) open the right targets

### Try a sample game — bundled samples + copy-on-open (commits a8f78d0 / f8a0eb7)
- L [ ] M [ ] W [ ] **Try a sample game** dropdown opens a menu listing Maze 1–3
- L [ ] M [ ] W [ ] Clicking a sample opens **immediately** — no "choose output folder" prompt, no GMK-import wait
- L [ ] M [ ] W [ ] After clicking, the IDE title shows the sample's name (e.g. `maze_1 — PyGameMaker IDE`)
- L [ ] M [ ] W [ ] The newly-opened project lives at `<Documents>/PyGameMaker Projects/<sample>/` — not under `samples/`
- L [ ] M [ ] W [ ] Clicking the same sample twice opens a fresh copy at `<sample>_2/`, leaving the first one alone
- L [ ] M [ ] W [ ] After editing and pressing Ctrl+S, only the working copy changes; `samples/<sample>/` on disk is untouched
- L [ ] M [ ] W [ ] Each sample loads to an editable state (assets visible in the asset tree, rooms openable, etc.)

### Window title (commit 00911b3)
- L [ ] M [ ] W [ ] No-project title: "PyGameMaker IDE"
- L [ ] M [ ] W [ ] Project loaded: "&lt;ProjectName&gt; — PyGameMaker IDE"
- L [ ] M [ ] W [ ] After unsaved edits: trailing " *" appears in title in real time
- L [ ] M [ ] W [ ] After save: " *" disappears

### Toolbar (commit 00911b3)
- L [ ] M [ ] W [ ] Hover any toolbar icon → tooltip with descriptive text + shortcut hint
  (e.g. "Save Project (Ctrl+S)", "Test Game (F5)")
- L [ ] M [ ] W [ ] Save / Test / Debug / Export / Import Sprite / Import Sound icons grey
      out when no project is open
- L [ ] M [ ] W [ ] Same icons enable correctly once a project is loaded
- L [ ] M [ ] W [ ] New / Open icons stay enabled in both states

### Tools menu graying (commit 78e190d)
- L [ ] M [ ] W [ ] No project loaded: "Validate Project", "Migrate to Modular Structure",
      and Thymio → Add Event / Add Action are greyed out
- L [ ] M [ ] W [ ] No project loaded: Preferences, Configure Action Blocks, Configure
      Thymio Blocks, Language, Open Playground, Import Open Roberta XML
      stay enabled
- L [ ] M [ ] W [ ] Project loaded: every Tools item becomes enabled

### Asset tree empty-state hint (commit 00911b3)
- L [ ] M [ ] W [ ] No project loaded: italic hint visible below the category list
      ("No project loaded. Use File → New / Open Project to begin.")
- L [ ] M [ ] W [ ] Hint disappears once a project loads
- L [ ] M [ ] W [ ] Hint dims correctly under both light and dark themes

### Right panel empty-state placeholder (commit 00911b3)
- L [ ] M [ ] W [ ] No project loaded: the Asset Information / Properties / Preview
      group boxes are hidden; one centred italic message takes their place
- L [ ] M [ ] W [ ] Message appears in both light and dark themes
- L [ ] M [ ] W [ ] Project loaded: the three group boxes reappear; placeholder is hidden

### Aseba code export (commit 71e19f3)
- L [ ] M [ ] W [ ] File → Export menu contains "Export Aseba (Thymio) code…"
- L [ ] M [ ] W [ ] Item is greyed out when no project is open, enabled when one is
- L [ ] M [ ] W [ ] Clicking it prompts for an output directory
- L [ ] M [ ] W [ ] On a project with Thymio objects: writes one `.aesl` per object + a
      `README.md` to the chosen directory
- L [ ] M [ ] W [ ] On a project without Thymio objects: shows the "No Thymio objects
      found" warning instead of the generic failure dialog
- L [ ] M [ ] W [ ] Success dialog offers to open the output folder; works on
      Windows / macOS / Linux

### Cross-platform export "open folder" prompts (commit a44f750)
- L [ ] M [ ] W [ ] After a successful Linux-binary export, the "open folder?" prompt
      uses the correct OS-native open command (start / open / xdg-open)
- L [ ] M [ ] W [ ] Same for iOS export (where reachable)
- L [ ] M [ ] W [ ] Same for HTML5, exe, macos, android exports (regression check)

### Localised Desktop / Documents defaults (commit 53ec9ae)
- L [ ] M [ ] W [ ] On Windows with OneDrive-redirected Desktop: export dialog defaults
      to the OneDrive-Desktop path, not a non-existent `~/Desktop`
- L [ ] M [ ] W [ ] On Linux with non-English locale: export dialog defaults to the
      localised desktop folder (Bureau / Schreibtisch / etc.)
- L [ ] M [ ] W [ ] New-project dialog defaults to the localised Documents folder

### Windows console flash suppressed (commit 53ec9ae)
- L [ ] M [ ] W [ ] On Windows in dev mode, pressing F5 to Test Game: no `python.exe`
      console window flashes before pygame opens

### Dialog button bar ordering (commit 00911b3)
- L [ ] M [ ] W [ ] Sprite Strip Import dialog: Cancel/OK button row follows the
      platform convention (OK-then-Cancel on Win/Linux, Cancel-then-OK
      on macOS)
- L [ ] M [ ] W [ ] Blockly Block Config dialog: Select All / Select None stay on the
      left; Save/Cancel pair on the right follows the platform convention

### Translation coverage (commit ad47e68)
- L [ ] M [ ] W [ ] Switching language at runtime (Tools → Language) actually changes
      the visible labels (sanity check that .qm files load)
- L [ ] M [ ] W [ ] All 7 active languages (de, es, fr, it, ru, sl, uk) appear in the
      Language menu when their .qm files are present

---

## 1. Application Startup & Basic Operations

- L [x] M [ ] W [ ] Application launches without errors  *(verified post-`afb9c75`: clean console, no Qt UniqueConnection warning, no duplicate `pygm.X` log lines)*
- L [ ] M [ ] W [ ] Main window displays correctly
- L [ ] M [ ] W [ ] Menu bar is visible and responsive
- L [ ] M [ ] W [ ] Toolbar buttons are visible and clickable
- L [ ] M [ ] W [ ] Status bar shows information
- L [ ] M [ ] W [ ] Asset tree panel is visible
- L [ ] M [ ] W [ ] Properties panel is visible

## 2. Project Management

- L [ ] M [ ] W [ ] Create new project (File > New Project)
- L [ ] M [ ] W [ ] Open existing project (File > Open Project)
- L [ ] M [ ] W [ ] Save project (File > Save / Ctrl+S)
- L [ ] M [ ] W [ ] Save project as new name (File > Save As)
- L [ ] M [ ] W [ ] Close project (File > Close Project)
- L [ ] M [ ] W [ ] Recent projects list works
- L [ ] M [ ] W [ ] Project settings dialog opens and saves

## 3. Asset Tree Operations

### Sprites
- L [ ] M [ ] W [ ] Create new sprite
- L [ ] M [ ] W [ ] Import sprite from image file (PNG, JPG, GIF)
- L [ ] M [ ] W [ ] Edit sprite properties (name, origin, collision mask)
- L [ ] M [ ] W [ ] Delete sprite
- L [ ] M [ ] W [ ] Duplicate sprite
- L [ ] M [ ] W [ ] Rename sprite

### Sounds
- L [ ] M [ ] W [ ] Create/import new sound (WAV, MP3, OGG)
- L [ ] M [ ] W [ ] Preview sound playback
- L [ ] M [ ] W [ ] Edit sound properties
- L [ ] M [ ] W [ ] Delete sound

### Backgrounds
- L [ ] M [ ] W [ ] Create new background
- L [ ] M [ ] W [ ] Import background image
- L [ ] M [ ] W [ ] Edit background properties (tiling, scrolling)
- L [ ] M [ ] W [ ] Delete background

### Objects
- L [ ] M [ ] W [ ] Create new object
- L [ ] M [ ] W [ ] Assign sprite to object
- L [ ] M [ ] W [ ] Edit object properties (visible, solid, depth, persistent)
- L [ ] M [ ] W [ ] Add events to object
- L [ ] M [ ] W [ ] Add actions to events
- L [ ] M [ ] W [ ] Delete object
- L [ ] M [ ] W [ ] Duplicate object
- L [ ] M [ ] W [ ] Parent/child object relationships

### Rooms
- L [ ] M [ ] W [ ] Create new room
- L [ ] M [ ] W [ ] Edit room properties (width, height, speed)
- L [ ] M [ ] W [ ] Set room background
- L [ ] M [ ] W [ ] Place object instances in room
- L [ ] M [ ] W [ ] Move/resize instances
- L [ ] M [ ] W [ ] Delete instances
- L [ ] M [ ] W [ ] Set room order (first room)
- L [ ] M [ ] W [ ] Delete room

## 4. Object Events Testing

### Create Event
- L [ ] M [ ] W [ ] Add Create event
- L [ ] M [ ] W [ ] Actions execute when instance is created
- L [ ] M [ ] W [ ] Variable initialization works

### Destroy Event
- L [ ] M [ ] W [ ] Add Destroy event
- L [ ] M [ ] W [ ] Actions execute when instance is destroyed

### Step Events
- L [ ] M [ ] W [ ] Step event fires every frame
- L [ ] M [ ] W [ ] Begin Step event fires before Step
- L [ ] M [ ] W [ ] End Step event fires after Step

### Alarm Events
- L [ ] M [ ] W [ ] Alarm 0-11 can be set
- L [ ] M [ ] W [ ] Alarm triggers at correct time
- L [ ] M [ ] W [ ] Alarm can be reset

### Keyboard Events
- L [ ] M [ ] W [ ] Key Press event (fires once on key down)
- L [ ] M [ ] W [ ] Key Release event (fires once on key up)
- L [ ] M [ ] W [ ] Key Down event (fires continuously while held)
- L [ ] M [ ] W [ ] Specific key detection (Arrow keys, WASD, Space, Enter, etc.)
- L [ ] M [ ] W [ ] Any key detection

### Mouse Events
- L [ ] M [ ] W [ ] Left button press/release/down
- L [ ] M [ ] W [ ] Right button press/release/down
- L [ ] M [ ] W [ ] Middle button press/release/down
- L [ ] M [ ] W [ ] Mouse enter (cursor enters instance)
- L [ ] M [ ] W [ ] Mouse leave (cursor leaves instance)
- L [ ] M [ ] W [ ] Global mouse events (anywhere on screen)

### Collision Events
- L [ ] M [ ] W [ ] Collision with specific object
- L [ ] M [ ] W [ ] Collision detection accuracy
- L [ ] M [ ] W [ ] Multiple collision events on same object

### Other Events
- L [ ] M [ ] W [ ] Outside Room event
- L [ ] M [ ] W [ ] Intersect Boundary event
- L [ ] M [ ] W [ ] Game Start event
- L [ ] M [ ] W [ ] Game End event
- L [ ] M [ ] W [ ] Room Start event
- L [ ] M [ ] W [ ] Room End event
- L [ ] M [ ] W [ ] Animation End event
- L [ ] M [ ] W [ ] User-defined events

### Draw Events
- L [ ] M [ ] W [ ] Draw event overrides default sprite drawing
- L [ ] M [ ] W [ ] Draw GUI event for HUD elements
- L [ ] M [ ] W [ ] Draw Begin/End events

## 5. Actions Testing

### Movement Actions
- L [ ] M [ ] W [ ] Move Fixed (8 directions + stop)
- L [ ] M [ ] W [ ] Move Free (direction + speed)
- L [ ] M [ ] W [ ] Move Towards (target point)
- L [ ] M [ ] W [ ] Set Speed
- L [ ] M [ ] W [ ] Set Direction
- L [ ] M [ ] W [ ] Set Horizontal Speed (hspeed)
- L [ ] M [ ] W [ ] Set Vertical Speed (vspeed)
- L [ ] M [ ] W [ ] Reverse Horizontal
- L [ ] M [ ] W [ ] Reverse Vertical
- L [ ] M [ ] W [ ] Set Gravity
- L [ ] M [ ] W [ ] Set Friction
- L [ ] M [ ] W [ ] Jump to Position
- L [ ] M [ ] W [ ] Jump to Start Position
- L [ ] M [ ] W [ ] Jump to Random Position
- L [ ] M [ ] W [ ] Snap to Grid
- L [ ] M [ ] W [ ] Wrap Screen
- L [ ] M [ ] W [ ] Move to Contact
- L [ ] M [ ] W [ ] Bounce against objects

### Instance Actions
- L [ ] M [ ] W [ ] Create Instance
- L [ ] M [ ] W [ ] Create Instance with Motion
- L [ ] M [ ] W [ ] Create Random Instance
- L [ ] M [ ] W [ ] Change Instance (transform to different object)
- L [ ] M [ ] W [ ] Destroy Instance
- L [ ] M [ ] W [ ] Destroy at Position

### Control Flow Actions
- L [ ] M [ ] W [ ] If Variable (comparison)
- L [ ] M [ ] W [ ] If Instance Count
- L [ ] M [ ] W [ ] If Dice (random chance)
- L [ ] M [ ] W [ ] If Question (user prompt)
- L [ ] M [ ] W [ ] If Expression
- L [ ] M [ ] W [ ] If Mouse Button
- L [ ] M [ ] W [ ] If Instance Aligned with Grid
- L [ ] M [ ] W [ ] Start Block / End Block
- L [ ] M [ ] W [ ] Else
- L [ ] M [ ] W [ ] Exit Event
- L [ ] M [ ] W [ ] Repeat
- L [ ] M [ ] W [ ] Call Parent Event

### Room Actions
- L [ ] M [ ] W [ ] Go to Next Room
- L [ ] M [ ] W [ ] Go to Previous Room
- L [ ] M [ ] W [ ] Restart Room
- L [ ] M [ ] W [ ] Go to Room (specific)
- L [ ] M [ ] W [ ] If Previous Room Exists
- L [ ] M [ ] W [ ] If Next Room Exists

### Variable Actions
- L [ ] M [ ] W [ ] Set Variable
- L [ ] M [ ] W [ ] If Variable
- L [ ] M [ ] W [ ] Draw Variable

### Score/Lives/Health Actions
- L [ ] M [ ] W [ ] Set Score
- L [ ] M [ ] W [ ] If Score
- L [ ] M [ ] W [ ] Draw Score
- L [ ] M [ ] W [ ] Set Lives
- L [ ] M [ ] W [ ] If Lives
- L [ ] M [ ] W [ ] Draw Lives
- L [ ] M [ ] W [ ] Set Health
- L [ ] M [ ] W [ ] If Health
- L [ ] M [ ] W [ ] Draw Health
- L [ ] M [ ] W [ ] Draw Health Bar

### Drawing Actions
- L [ ] M [ ] W [ ] Draw Sprite
- L [ ] M [ ] W [ ] Draw Background
- L [ ] M [ ] W [ ] Draw Text
- L [ ] M [ ] W [ ] Draw Text Transformed
- L [ ] M [ ] W [ ] Draw Rectangle
- L [ ] M [ ] W [ ] Draw Ellipse
- L [ ] M [ ] W [ ] Draw Line
- L [ ] M [ ] W [ ] Draw Arrow
- L [ ] M [ ] W [ ] Set Color
- L [ ] M [ ] W [ ] Set Font
- L [ ] M [ ] W [ ] Set Full Screen

### Sound Actions
- L [ ] M [ ] W [ ] Play Sound
- L [ ] M [ ] W [ ] Stop Sound
- L [ ] M [ ] W [ ] If Sound Playing
- L [ ] M [ ] W [ ] Set Volume
- L [ ] M [ ] W [ ] Set Pan

### Timing Actions
- L [ ] M [ ] W [ ] Set Alarm
- L [ ] M [ ] W [ ] Sleep (pause execution)
- L [ ] M [ ] W [ ] Set Timeline

### Info/Game Actions
- L [ ] M [ ] W [ ] Display Message
- L [ ] M [ ] W [ ] Show Info
- L [ ] M [ ] W [ ] Show Video
- L [ ] M [ ] W [ ] Restart Game
- L [ ] M [ ] W [ ] End Game
- L [ ] M [ ] W [ ] Save Game
- L [ ] M [ ] W [ ] Load Game

## 6. Room Editor

- L [ ] M [ ] W [ ] Grid display toggle
- L [ ] M [ ] W [ ] Grid snap toggle
- L [ ] M [ ] W [ ] Zoom in/out
- L [ ] M [ ] W [ ] Pan/scroll room view
- L [ ] M [ ] W [ ] Instance placement
- L [ ] M [ ] W [ ] Instance selection (click)
- L [ ] M [ ] W [ ] Multi-select instances (Ctrl+click or drag box)
- L [ ] M [ ] W [ ] Move selected instances
- L [ ] M [ ] W [ ] Delete selected instances (Delete key)
- L [ ] M [ ] W [ ] Copy/paste instances
- L [ ] M [ ] W [ ] Instance properties panel
- L [ ] M [ ] W [ ] Layer management (if applicable)
- L [ ] M [ ] W [ ] Background layer editing
- L [ ] M [ ] W [ ] View settings (show/hide elements)

## 7. Blockly Visual Programming

- L [ ] M [ ] W [ ] Blockly editor opens for actions
- L [ ] M [ ] W [ ] Blocks can be dragged from toolbox
- L [ ] M [ ] W [ ] Blocks snap together correctly
- L [ ] M [ ] W [ ] Block deletion works
- L [ ] M [ ] W [ ] Undo/redo in Blockly
- L [ ] M [ ] W [ ] Code generation from blocks
- L [ ] M [ ] W [ ] All action categories available in toolbox
- L [ ] M [ ] W [ ] Custom blocks (if any)

## 8. Code Editor

- L [ ] M [ ] W [ ] Python code editor opens
- L [ ] M [ ] W [ ] Syntax highlighting works
- L [ ] M [ ] W [ ] Code completion (if available)
- L [ ] M [ ] W [ ] Code can be saved
- L [ ] M [ ] W [ ] Code executes correctly in game

## 9. Game Execution

### Run Game (F5)
- L [ ] M [ ] W [ ] Game window opens
- L [ ] M [ ] W [ ] First room loads correctly
- L [ ] M [ ] W [ ] Objects appear at correct positions
- L [ ] M [ ] W [ ] Sprites display correctly
- L [ ] M [ ] W [ ] Animations play
- L [ ] M [ ] W [ ] Events fire correctly
- L [ ] M [ ] W [ ] Collisions detected
- L [ ] M [ ] W [ ] Keyboard input works
- L [ ] M [ ] W [ ] Mouse input works
- L [ ] M [ ] W [ ] Sound plays
- L [ ] M [ ] W [ ] Room transitions work
- L [ ] M [ ] W [ ] Game can be closed cleanly

### Debug Mode
- L [ ] M [ ] W [ ] Debug output visible
- L [ ] M [ ] W [ ] FPS display (if enabled)
- L [ ] M [ ] W [ ] Variable inspection (if available)
- L [ ] M [ ] W [ ] Step-through execution (if available)

## 10. Export/Build

### HTML5 Export
- L [ ] M [ ] W [ ] Export to HTML5 works
- L [ ] M [ ] W [ ] Game runs in browser
- L [ ] M [ ] W [ ] All features work in browser

### Standalone Export
- L [ ] M [ ] W [ ] Export to executable works
- L [ ] M [ ] W [ ] Game runs without IDE
- L [ ] M [ ] W [ ] All assets bundled correctly

## 11. Preferences/Settings

- L [ ] M [ ] W [ ] Preferences dialog opens
- L [ ] M [ ] W [ ] Language selection works
- L [ ] M [ ] W [ ] Theme selection works (light/dark)
- L [ ] M [ ] W [ ] Font settings work
- L [ ] M [ ] W [ ] Grid settings persist
- L [ ] M [ ] W [ ] Settings save between sessions

## 12. Help System

- L [ ] M [ ] W [ ] Help menu accessible
- L [ ] M [ ] W [ ] Documentation opens
- L [ ] M [ ] W [ ] About dialog shows version info
- L [ ] M [ ] W [ ] Links work (website, GitHub, etc.)

## 13. Standalone Executable Testing

- L [ ] M [ ] W [ ] Application launches from executable
- L [ ] M [ ] W [ ] No empty directories created in launch folder
- L [ ] M [ ] W [ ] Projects can be created/opened
- L [ ] M [ ] W [ ] Games can be run (F5)
- L [ ] M [ ] W [ ] Room preview shows appropriate message
- L [ ] M [ ] W [ ] All UI elements render correctly
- L [ ] M [ ] W [ ] No Python-related errors in console

## 14. Error Handling

- L [ ] M [ ] W [ ] Invalid project file shows error message
- L [ ] M [ ] W [ ] Missing asset references handled gracefully
- L [ ] M [ ] W [ ] Syntax errors in code show helpful messages
- L [ ] M [ ] W [ ] Crash recovery (autosave, if available)
- L [ ] M [ ] W [ ] Undo works after errors

---

## Test Environment Notes

**Date Tested:** _______________

**Version:** _______________

**OS:** _______________

**Tester:** _______________

**Notes:**

# PyGameMaker IDE User Manual

**Version 1.0.0-rc.4**
**A GameMaker-inspired visual game development IDE for creating 2D games with Python**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation and Setup](#2-installation-and-setup)
3. [IDE Overview](#3-ide-overview)
4. [Working with Projects](#4-working-with-projects)
5. [Sprites](#5-sprites)
6. [Sounds](#6-sounds)
7. [Backgrounds](#7-backgrounds)
8. [Objects](#8-objects)
9. [Rooms](#9-rooms)
10. [Events Reference](#10-events-reference)
11. [Actions Reference](#11-actions-reference)
12. [Testing and Running Games](#12-testing-and-running-games)
13. [Exporting Games](#13-exporting-games)
14. [Blockly Visual Programming](#14-blockly-visual-programming)
15. [Thymio Robot Support](#15-thymio-robot-support)
16. [Settings and Preferences](#16-settings-and-preferences)
17. [Keyboard Shortcuts](#17-keyboard-shortcuts)
18. [Tutorials](#18-tutorials)
19. [Troubleshooting](#19-troubleshooting)

---

## 1. Introduction

PyGameMaker is an educational game development IDE inspired by GameMaker. It allows you to create 2D games visually using a drag-and-drop event/action system, without needing to write code. It is designed with two goals in mind:

- **Teach game development** visually through an intuitive interface
- **Teach Python programming** through the IDE's open-source codebase

PyGameMaker uses PySide6 (Qt) for the IDE interface and Pygame for the game runtime. Games can be exported as standalone executables, mobile apps, or HTML5 web games.

### Key Features

- Visual event/action programming (80+ built-in actions)
- Sprite editor with animation support
- Room editor with instance placement, tile layers, and background scrolling
- Real-time game preview with F5
- Export to Windows EXE, mobile (Android/iOS via Kivy), HTML5, and Thymio robots
- Google Blockly integration for visual code blocks
- Thymio educational robot simulator
- Multi-language interface (8+ languages)
- Dark and light themes

---

## 2. Installation and Setup

### Requirements

- Python 3.10 or higher
- PySide6
- Pygame
- Pillow (PIL)

### Install Dependencies

```bash
pip install PySide6 pygame Pillow
```

### Optional Dependencies

For export features:

```bash
pip install pyinstaller    # For EXE export
pip install kivy           # For mobile export
pip install buildozer      # For Android builds
pip install jinja2         # For code generation templates
```

### Running the IDE

```bash
python main.py
```

The IDE window opens with default dimensions of 1400x900 pixels. Window position and size are saved between sessions.

---

## 3. IDE Overview

### Window Layout

The IDE uses a three-panel layout:

```
+-------------------+---------------------------+------------------+
|   Asset Tree      |      Editor Area          |   Properties     |
|   (Left Panel)    |      (Center Panel)       |   (Right Panel)  |
|                   |                           |                  |
|   - Sprites       |   Tabbed editors for      |   Context-       |
|   - Sounds        |   sprites, objects,       |   sensitive      |
|   - Backgrounds   |   and rooms               |   properties     |
|   - Objects       |                           |                  |
|   - Rooms         |                           |                  |
|   - Scripts       |                           |                  |
|   - Fonts         |                           |                  |
+-------------------+--------------------------+------------------+
|                       Status Bar                                 |
+------------------------------------------------------------------+
```

- **Left Panel (Asset Tree):** Displays all project assets organized by type. Double-click an asset to open it in the editor.
- **Center Panel (Editor Area):** Tabbed workspace where you edit sprites, objects, and rooms. A welcome tab is shown by default.
- **Right Panel (Properties):** Shows context-sensitive properties for the currently active editor. Can be collapsed.
- **Status Bar:** Shows current operation status and project name.

### Menu Bar

#### File Menu

| Command | Shortcut | Description |
|---------|----------|-------------|
| New Project... | Ctrl+N | Create a new project |
| Open Project... | Ctrl+O | Open an existing project |
| Save Project | Ctrl+S | Save the current project |
| Save Project As... | Ctrl+Shift+S | Save to a new location |
| Recent Projects | | Submenu of up to 10 recent projects |
| Export as HTML5... | | Export game as a single HTML file |
| Export as Zip... | | Package project as a ZIP archive |
| Export to Kivy... | | Export for mobile deployment |
| Export Project... | Ctrl+E | Open the export dialog |
| Open Zip Project... | | Open a ZIP-packaged project |
| Auto-Save to Zip | | Toggle auto-save to ZIP |
| Enable Auto-Save | | Toggle automatic project saving |
| Auto-Save Settings... | | Configure auto-save interval |
| Project Settings... | | Open project configuration |
| Exit | Ctrl+Q | Close the IDE |

#### Edit Menu

| Command | Shortcut | Description |
|---------|----------|-------------|
| Undo | Ctrl+Z | Undo last action |
| Redo | Ctrl+Y | Redo last undone action |
| Cut | Ctrl+X | Cut selection |
| Copy | Ctrl+C | Copy selection |
| Paste | Ctrl+V | Paste from clipboard |
| Duplicate | Ctrl+D | Duplicate selected items |
| Find... | Ctrl+F | Open find dialog |
| Find and Replace... | Ctrl+H | Open find and replace dialog |

#### Assets Menu

| Command | Description |
|---------|-------------|
| Import Sprite... | Import sprite images (PNG, JPG, BMP, GIF) |
| Import Sound... | Import audio files |
| Import Background... | Import background images |
| Create Object... | Create a new game object |
| Create Room... (Ctrl+R) | Create a new game room |
| Create Script... | Create a new script file |
| Create Font... | Create a new font asset |
| Import Object Package... | Import a .gmobj package |
| Import Room Package... | Import a .gmroom package |

#### Build Menu

| Command | Shortcut | Description |
|---------|----------|-------------|
| Test Game | F5 | Run game in test mode |
| Debug Game | F6 | Run game with debug output |
| Build Game... | F7 | Open build configuration |
| Build and Run | F8 | Build and immediately run |
| Export Game... | | Export compiled game |

#### Tools Menu

| Command | Description |
|---------|-------------|
| Preferences... | Open IDE preferences |
| Asset Manager... | Open asset management window |
| Configure Action Blocks... | Configure Blockly blocks |
| Configure Thymio Blocks... | Configure Thymio robot blocks |
| Validate Project | Check project for errors |
| Clean Project | Remove temporary files |
| Migrate to Modular Structure | Upgrade project format |
| Language | Change interface language |
| Thymio Programming | Robot programming submenu |

#### Help Menu

| Command | Shortcut | Description |
|---------|----------|-------------|
| Documentation | F1 | Open help documentation |
| Tutorials | | Open tutorial resources |
| About PyGameMaker | | Version and license info |

### Toolbar

The toolbar provides quick access to common actions (left to right):

| Button | Action |
|--------|--------|
| New | Create new project |
| Open | Open existing project |
| Save | Save current project |
| Test | Run game (F5) |
| Debug | Debug game (F6) |
| Export | Export game |
| Import Sprite | Import a sprite image |
| Import Sound | Import an audio file |
| Thymio | Add Thymio robot event |

### Asset Tree

The asset tree in the left panel organizes project assets into categories:

**Media Assets:**
- **Sprites** - Images and animation strips for game objects
- **Sounds** - Sound effects and music files
- **Backgrounds** - Background images and tilesets

**Game Logic:**
- **Objects** - Game object definitions with events and actions
- **Rooms** - Game levels/scenes with placed instances

**Code Assets:**
- **Scripts** - Code files
- **Fonts** - Custom font assets

**Context menu operations:**
- Right-click a category header to create or import assets
- Right-click an asset to rename, delete, export, or view properties
- Double-click an asset to open it in the editor
- Room assets can be reordered (Move Up/Down/Top/Bottom)

---

## 4. Working with Projects

### Creating a New Project

1. Choose **File > New Project** (Ctrl+N)
2. Enter a **Project Name**
3. Choose a **Location** for the project folder
4. Select a **Template** (optional):
   - **Empty Project** - A blank project
   - **Platform Game Template** - Pre-configured for platformers
   - **Top-Down Game Template** - Pre-configured for top-down games
5. Click **Create Project**

### Project Structure

```
MyProject/
├── project.json          # Main project file
├── sprites/              # Sprite images and metadata
│   ├── player.png
│   └── player.json
├── objects/              # Object definitions
│   └── obj_player.json
├── rooms/                # Room layout data
│   └── room_start.json
├── sounds/               # Audio files and metadata
├── backgrounds/          # Background images
└── thumbnails/           # Auto-generated previews
```

### Saving Projects

- **Ctrl+S** saves the project to its current location
- **Ctrl+Shift+S** saves to a new location
- **Auto-save** can be enabled in File > Enable Auto-Save
- Configure auto-save interval in File > Auto-Save Settings

### Opening Projects

- **Ctrl+O** opens a project folder
- Recent projects are listed in **File > Recent Projects**
- ZIP projects can be opened with **File > Open Zip Project**

---

## 5. Sprites

Sprites are the visual images used by game objects. They can be static images or animation strips with multiple frames.

### Creating a Sprite

1. Right-click **Sprites** in the asset tree and choose **Import Sprite...**
2. Select an image file (PNG, JPG, BMP, or GIF)
3. The sprite appears in the asset tree and opens in the sprite editor

### Sprite Editor

The sprite editor has four main areas:

- **Tool Panel (Left):** Drawing tools
- **Canvas (Center):** The editing area with zoom and grid
- **Color Palette (Right):** Foreground/background colors and swatches
- **Frame Timeline (Bottom):** Animation frame management

#### Drawing Tools

| Tool | Shortcut | Description |
|------|----------|-------------|
| Pencil | P | Standard pixel drawing |
| Eraser | E | Remove pixels (make transparent) |
| Color Picker | I | Sample a color from the canvas |
| Fill | G | Flood fill connected regions |
| Line | L | Draw straight lines |
| Rectangle | R | Draw rectangles (outline or filled) |
| Ellipse | O | Draw ellipses (outline or filled) |
| Selection | S | Select, cut, copy, paste regions |

#### Brush Size

Brush size ranges from 1 to 16 pixels and affects the Pencil, Eraser, and Line tools.

#### Filled Mode

Toggle between outline and filled mode for the Rectangle and Ellipse tools using the **Filled** button.

#### Color Palette

- **Left-click** the foreground swatch to choose a drawing color
- **Right-click** the background swatch to choose a secondary color
- **X button** swaps foreground and background colors
- Click any color in the quick palette to select it
- Double-click a palette swatch to customize it
- Full RGBA color picker with alpha (transparency) support

### Animation Frames

Sprites can have multiple animation frames arranged as a horizontal strip.

**Frame Timeline Controls:**
- **+ (Add):** Add a new blank frame
- **D (Duplicate):** Copy the current frame
- **- (Delete):** Remove the current frame (minimum 1 frame)
- **Play/Stop:** Preview the animation
- Frame counter shows current/total frames

**Animation Properties:**
- **Frame Count:** Number of animation frames
- **Animation Speed:** Frames per second (default: 10 FPS)
- **Animation Type:** single, strip_h (horizontal), strip_v (vertical), or grid

**Animated GIF Support:** Import animated GIF files directly. All frames are extracted automatically with transparency handling.

### Sprite Origin

The origin point is the anchor position used for placement and rotation in the game.

**Preset Positions:**
- Top-Left (0, 0)
- Top-Center
- Center (default for most sprites)
- Center-Bottom
- Bottom-Left
- Bottom-Right
- Custom (manual X/Y entry)

The origin is shown as a crosshair on the canvas.

### Canvas Controls

- **Ctrl+Mouse Wheel:** Zoom in/out (1x to 64x)
- **Grid Toggle:** Show/hide pixel grid (visible at 4x zoom and above)
- **Mirror H/V:** Flip the current frame horizontally or vertically
- **Resize/Scale:** Change sprite dimensions with scale or canvas resize options

### Sprite Properties (Saved)

| Property | Description |
|----------|-------------|
| name | Asset name |
| file_path | Path to PNG strip file |
| width | Full strip width |
| height | Frame height |
| frame_width | Single frame width |
| frame_height | Single frame height |
| frames | Number of frames |
| animation_type | single, strip_h, strip_v, grid |
| speed | Animation FPS |
| origin_x | Origin X coordinate |
| origin_y | Origin Y coordinate |

---

## 6. Sounds

Sounds are audio files used for sound effects and background music.

### Importing Sounds

1. Right-click **Sounds** in the asset tree and choose **Import Sound...**
2. Select an audio file (WAV, OGG, MP3)
3. The sound is added to the project

### Sound Properties

| Property | Description |
|----------|-------------|
| name | Sound asset name |
| file_path | Path to audio file |
| kind | "sound" (effect) or "music" (streaming) |
| volume | Default volume (0.0 to 1.0) |

**Sound effects** are loaded into memory for instant playback. **Music** files are streamed from disk and only one can play at a time.

---

## 7. Backgrounds

Backgrounds are images used behind game objects. They can also serve as tilesets for tile-based levels.

### Importing Backgrounds

1. Right-click **Backgrounds** in the asset tree and choose **Import Background...**
2. Select an image file

### Tileset Configuration

Backgrounds can be configured as tilesets with these properties:

| Property | Description |
|----------|-------------|
| tile_width | Width of each tile (default: 16) |
| tile_height | Height of each tile (default: 16) |
| h_offset | Horizontal offset to first tile |
| v_offset | Vertical offset to first tile |
| h_sep | Horizontal spacing between tiles |
| v_sep | Vertical spacing between tiles |
| use_as_tileset | Enable tileset mode |

---

## 8. Objects

Objects define game entities with properties, events, and actions. Each object can have a sprite for visual representation and contains event handlers that define its behavior.

### Creating an Object

1. Right-click **Objects** in the asset tree and choose **Create Object...**
2. Enter a name for the object
3. The object opens in the object editor

### Object Properties

| Property | Default | Description |
|----------|---------|-------------|
| Sprite | None | The visual sprite to display |
| Visible | Yes | Whether instances are drawn |
| Solid | No | Whether the object blocks movement |
| Persistent | No | Whether instances survive room changes |
| Depth | 0 | Drawing order (higher = behind, lower = in front) |
| Parent | None | Parent object for inheritance |

### Parent Objects

Objects can inherit from a parent object. Child objects receive all of the parent's collision events. This is useful for creating hierarchies like:

```
obj_enemy (parent - has collision with obj_player)
  ├── obj_enemy_melee (inherits collision handling)
  └── obj_enemy_ranged (inherits collision handling)
```

### Adding Events

1. Open the object editor
2. Click **Add Event** in the events panel
3. Select an event type from the list (see [Events Reference](#10-events-reference))
4. The event appears in the event tree

### Adding Actions to Events

1. Select an event in the event tree
2. Click **Add Action** or right-click and choose **Add Action**
3. Choose an action type from the categorized list
4. Configure the action's parameters in the dialog
5. Click OK to add the action

Actions execute in order from top to bottom when the event triggers.

### Conditional Logic

Actions support if/else conditional flow:

1. Add a conditional action (e.g., **If Collision At**, **Test Variable**)
2. Add a **Start Block** action (opening brace)
3. Add actions that execute when the condition is true
4. Add an **Else** action (optional)
5. Add a **Start Block** for the else branch
6. Add actions for the false case
7. Add **End Block** actions to close each block

Example action sequence:
```
If Collision At (self.x, self.y + 1, "solid")
  Start Block
    Set Vertical Speed (0)
  End Block
Else
  Start Block
    Set Vertical Speed (vspeed + 0.5)
  End Block
```

### View Code

Check the **View Code** option in the object editor to see the generated Python code for all events and actions. This is useful for understanding how the visual actions translate to code.

---

## 9. Rooms

Rooms are the scenes or levels of your game. Each room has a background, placed object instances, and optional tile layers.

### Creating a Room

1. Right-click **Rooms** in the asset tree and choose **Create Room...**
2. Enter a name for the room
3. The room opens in the room editor

### Room Properties

| Property | Default | Description |
|----------|---------|-------------|
| Width | 1024 | Room width in pixels |
| Height | 768 | Room height in pixels |
| Background Color | #87CEEB (sky blue) | Fill color behind everything |
| Background Image | None | Optional background image |
| Persistent | No | Preserve state when leaving |

### Placing Instances

1. Click an object in the **Object Palette** (left side of room editor)
2. Click in the room canvas to place an instance
3. Continue clicking to place more copies
4. Select placed instances to move or configure them

### Instance Properties

When you select a placed instance:

| Property | Range | Description |
|----------|-------|-------------|
| X Position | 0-9999 | Horizontal position |
| Y Position | 0-9999 | Vertical position |
| Visible | Yes/No | Instance visibility |
| Rotation | 0-360 | Rotation in degrees |
| Scale X | 10%-1000% | Horizontal scale |
| Scale Y | 10%-1000% | Vertical scale |

### Grid and Snapping

- **Grid Toggle:** Click the grid button to show/hide the placement grid
- **Snap Toggle:** Click the snap button to enable/disable grid snapping
- **Grid Size:** 32x32 pixels by default (configurable in Preferences)

### Instance Operations

| Action | Shortcut | Description |
|--------|----------|-------------|
| Move | Drag | Move instance to new position |
| Select Multiple | Shift+Click | Add/remove from selection |
| Rubber Band Select | Drag empty area | Select all instances in rectangle |
| Delete | Delete key | Remove selected instances |
| Cut | Ctrl+X | Cut to clipboard |
| Copy | Ctrl+C | Copy to clipboard |
| Paste | Ctrl+V | Paste from clipboard |
| Duplicate | Ctrl+D | Duplicate selected instances |
| Clear All | Toolbar button | Remove all instances (with confirmation) |

### Background Layers

Rooms support up to 8 background layers (indexed 0-7), each with independent settings:

| Property | Description |
|----------|-------------|
| Background Image | Which background asset to use |
| Visible | Show/hide the layer |
| Foreground | If true, drawn in front of instances |
| Tile Horizontal | Repeat across room width |
| Tile Vertical | Repeat down room height |
| H Scroll Speed | Horizontal scroll pixels per frame |
| V Scroll Speed | Vertical scroll pixels per frame |
| Stretch | Scale to fill entire room |
| X / Y Offset | Layer position offset |

### Tile Layers

For tile-based levels:

1. Click **Tile Palette...** to open the tile selector
2. Choose a tileset (background marked as tileset)
3. Set tile width and height
4. Click a tile in the palette to select it
5. Click in the room to place tiles
6. Select a **Layer** (0-7) for the tiles

### Room Ordering

Rooms execute in the order they appear in the asset tree. The first room is the starting room.

- Right-click a room and use **Move Up/Down/Top/Bottom** to reorder
- Use the **Next Room** and **Previous Room** actions to navigate between rooms at runtime

### View System

Rooms support up to 8 camera views (like GameMaker):

| Property | Description |
|----------|-------------|
| Visible | Enable/disable this view |
| View X/Y | Camera position in room |
| View W/H | Camera viewport size |
| Port X/Y | Screen position for this view |
| Port W/H | Screen size for this view |
| Follow Object | Object to track with camera |
| H/V Border | Scrolling margin around followed object |
| H/V Speed | Maximum camera scroll speed (-1 = instant) |

---

## 10. Events Reference

Events define when actions are executed. Each event triggers under specific conditions.

### Object Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Create | Object | Instance is first created |
| Destroy | Object | Instance is destroyed |
| Step | Step | Every game frame (~60 FPS) |
| Begin Step | Step | Start of each frame, before physics |
| End Step | Step | End of each frame, after collisions |

### Collision Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Collision With... | Collision | Two instances overlap (select target object) |

### Keyboard Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Keyboard | Input | Key is held down continuously (for smooth movement) |
| Keyboard Press | Input | Key is first pressed (once per press) |
| Keyboard Release | Input | Key is released |

**Available Keys:** A-Z, 0-9, Arrow keys, Space, Enter, Escape, Tab, Backspace, Delete, F1-F12, Numpad keys, Shift, Ctrl, Alt, and more (76+ keys total).

**Special Keyboard Events:**
- **No Key** - Fires when no key is pressed
- **Any Key** - Fires when any key is pressed

### Mouse Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Mouse Left/Right/Middle Press | Input | Button clicked on instance |
| Mouse Left/Right/Middle Release | Input | Button released on instance |
| Mouse Left/Right/Middle Down | Input | Button held on instance |
| Mouse Enter | Input | Cursor enters instance bounding box |
| Mouse Leave | Input | Cursor leaves instance bounding box |
| Mouse Wheel Up/Down | Input | Scroll wheel on instance |
| Global Mouse Press | Input | Button clicked anywhere in room |
| Global Mouse Release | Input | Button released anywhere in room |

### Timing Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Alarm 0-11 | Timing | Alarm countdown reaches zero (12 independent alarms) |

### Drawing Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Draw | Drawing | Instance is drawn (replaces default sprite drawing) |
| Draw GUI | Drawing | Drawn on top of everything (for HUD, score display) |

### Room Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Room Start | Room | Room begins (after create events) |
| Room End | Room | Room is about to end |

### Game Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Game Start | Game | Game initializes (first room only) |
| Game End | Game | Game is closing |

### Other Events

| Event | Category | Triggers When |
|-------|----------|---------------|
| Outside Room | Other | Instance is completely outside room bounds |
| Intersect Boundary | Other | Instance touches room edge |
| No More Lives | Other | Lives value reaches 0 or less |
| No More Health | Other | Health value reaches 0 or less |
| Animation End | Other | Sprite animation reaches last frame |
| User Event 0-15 | Other | 16 custom events triggered by code |

---

## 11. Actions Reference

Actions are the building blocks of game behavior. They are placed inside events and execute in order.

### Movement Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Move Grid | direction (left/right/up/down), grid_size (default: 32) | Move one grid unit in a direction |
| Set Horizontal Speed | speed (pixels/frame) | Set hspeed for smooth horizontal movement |
| Set Vertical Speed | speed (pixels/frame) | Set vspeed for smooth vertical movement |
| Stop Movement | (none) | Set both speeds to zero |
| Move Fixed | directions (8-way), speed | Start moving in a fixed direction |
| Move Free | direction (0-360 degrees), speed | Move at a precise angle |
| Move Towards | x, y, speed | Move toward a target position |
| Set Gravity | direction (270=down), gravity | Apply constant acceleration |
| Set Friction | friction | Apply deceleration each frame |
| Reverse Horizontal | (none) | Reverse hspeed direction |
| Reverse Vertical | (none) | Reverse vspeed direction |
| Set Speed | speed | Set movement magnitude |
| Set Direction | direction (degrees) | Set movement angle |
| Jump to Position | x, y | Teleport to position |
| Jump to Start | (none) | Teleport to starting position |
| Bounce | (none) | Reverse velocity on collision |

### Grid Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Snap to Grid | grid_size | Align position to nearest grid point |
| If On Grid | grid_size | Check if aligned to grid (conditional) |
| Stop If No Keys | grid_size | Stop on grid when movement keys released |

### Instance Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Create Instance | object, x, y, relative | Create a new object instance |
| Destroy Instance | target (self/other) | Remove an instance from the game |
| Change Sprite | sprite | Change the displayed sprite |
| Set Visible | visible (true/false) | Show or hide the instance |
| Set Scale | scale_x, scale_y | Change instance size |

### Score, Lives, and Health Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Set Score | value | Set score to a specific value |
| Add to Score | value | Add points (can be negative) |
| Set Lives | value | Set number of lives |
| Add Lives | value | Add/remove lives |
| Set Health | value | Set health (0-100) |
| Add Health | value | Add/remove health |
| Show Highscore Table | (none) | Display the highscore table |

### Room and Game Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Restart Room | (none) | Reload the current room |
| Next Room | (none) | Go to the next room in order |
| Previous Room | (none) | Go to the previous room |
| Go to Room | room | Jump to a specific room |
| If Next Room Exists | (none) | Conditional: is there a next room? |
| If Previous Room Exists | (none) | Conditional: is there a previous room? |
| Restart Game | (none) | Restart from the first room |
| End Game | (none) | Close the game |

### Timing Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Set Alarm | alarm_number (0-11), steps | Start countdown timer (30 steps = 0.5 sec at 60 FPS) |
| Delay Action | action, delay_frames | Execute an action after a delay |

### Message and Display Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Show Message | message | Display a popup message |
| Draw Text | text, x, y, color, size | Draw text on screen (use in Draw event) |
| Draw Rectangle | x1, y1, x2, y2, color, filled | Draw a rectangle |
| Draw Circle | x, y, radius, color, filled | Draw a circle |
| Draw Ellipse | x1, y1, x2, y2, color, filled | Draw an ellipse |
| Draw Line | x1, y1, x2, y2, color | Draw a line |
| Draw Sprite | sprite_name, x, y, subimage | Draw a sprite at position |
| Draw Background | background_name, x, y, tiled | Draw a background image |
| Draw Score | x, y, caption | Draw score value on screen |
| Draw Lives | x, y, sprite | Draw lives as sprite icons |
| Draw Health Bar | x, y, width, height | Draw health bar on screen |

### Sound Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| Play Sound | sound, loop | Play a sound effect |
| Stop Sound | sound | Stop a playing sound |
| Play Music | music | Play background music (streaming) |
| Stop Music | (none) | Stop background music |
| Set Volume | sound, volume (0.0-1.0) | Adjust sound volume |

### Control Flow Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| If Collision At | x, y, object_type | Check for collision at position |
| If Can Push | direction, object_type | Sokoban-style push check |
| Set Variable | name, value, scope, relative | Set a variable value |
| Test Variable | name, value, scope, operation | Compare a variable |
| Test Expression | expression | Evaluate a boolean expression |
| Check Empty | x, y, only_solid | Check if position is free |
| Check Collision | x, y, only_solid | Check for collision at position |
| Start Block | (none) | Begin a block of actions (opening brace) |
| End Block | (none) | End a block of actions (closing brace) |
| Else | (none) | Marks the else branch of a conditional |
| Repeat | times | Repeat the next action/block N times |
| Exit Event | (none) | Stop executing remaining actions |

### Variable Scope

Variables can be accessed using scoped references:

| Scope | Syntax | Description |
|-------|--------|-------------|
| Self | `self.variable` or just `variable` | Current instance's variable |
| Other | `other.variable` | The other instance in a collision |
| Global | `global.variable` | Game-wide variable |

Built-in instance variables: `x`, `y`, `hspeed`, `vspeed`, `direction`, `speed`, `gravity`, `friction`, `visible`, `depth`, `image_index`, `image_speed`, `scale_x`, `scale_y`

---

## 12. Testing and Running Games

### Quick Test (F5)

Press **F5** or click the **Test** button to run your game instantly. A separate Pygame window opens showing your game.

- Press **Escape** to stop the game and return to the IDE
- The IDE status bar shows "Game running..." while the game is active

### Debug Mode (F6)

Press **F6** for debug mode, which shows additional console output including:
- Event execution logging
- Collision detection details
- Action parameter values
- Instance creation and destruction

### Game Execution Order

Each frame follows the GameMaker 7.0 event order:

1. **Begin Step** events
2. **Alarm** countdown and triggers
3. **Step** events
4. **Keyboard/Mouse** input events
5. **Movement** (physics: gravity, friction, hspeed/vspeed)
6. **Collision** detection and events
7. **End Step** events
8. **Destroy** events for marked instances
9. **Draw** events and rendering

### Window Caption

The game window title can show score, lives, and health values. Enable this with the caption display settings in project settings or by using the score/lives/health actions.

---

## 13. Exporting Games

### HTML5 Export

**File > Export as HTML5**

Creates a single, self-contained HTML file that runs in any web browser.

- All sprites are embedded as base64 data
- Game data is compressed with gzip
- JavaScript engine handles rendering via HTML5 Canvas
- No server required - just open the file in a browser

### EXE Export (Windows)

**File > Export Project** or **Build > Export Game**

Creates a standalone Windows executable using PyInstaller.

**Requirements:** PyInstaller and Kivy must be installed.

**Process:**
1. Generates a Kivy-based game from your project
2. Bundles Python runtime and all dependencies
3. Creates a single EXE file (may take 5-10 minutes)

**Options:**
- Debug console (shows terminal window for debugging)
- Custom icon
- UPX compression (reduces file size)

### Mobile Export (Kivy)

**File > Export to Kivy**

Generates a Kivy project for mobile deployment.

**Output includes:**
- Python game code adapted for Kivy
- Asset bundle optimized for mobile
- `buildozer.spec` configuration for Android/iOS builds

**To build for Android:**
```bash
cd exported_project
buildozer android debug
```

### ZIP Export

**File > Export as Zip**

Packages the entire project as a ZIP archive for sharing or backup. The ZIP can be reopened with **File > Open Zip Project**.

### Aseba Export (Thymio Robot)

For Thymio robot projects, exports AESL code files compatible with Aseba Studio.

---

## 14. Blockly Visual Programming

PyGameMaker integrates Google Blockly for visual code-block programming.

### Configuring Blocks

Open **Tools > Configure Action Blocks** to customize which blocks are available.

### Block Presets

| Preset | Description |
|--------|-------------|
| Full (All Blocks) | All 173 blocks enabled |
| Beginner | Essential blocks only (events, basic movement, score, rooms) |
| Intermediate | Adds drawing, more movement, lives, health, sound |
| Platformer Game | Physics-focused: gravity, friction, collision |
| Grid-based RPG | Grid movement, health, room transitions |
| Sokoban (Box Puzzle) | Grid movement, push mechanics |
| Testing | Only validated blocks |
| Implemented Only | Excludes unimplemented blocks |
| Code Editor | For text-based programming |
| Blockly Editor | For visual-first development |
| Custom | Your own selection |

### Block Categories

Blocks are organized into color-coded categories:

| Category | Color | Blocks |
|----------|-------|--------|
| Events | Yellow | 13 event blocks |
| Movement | Blue | 14 movement blocks |
| Timing | Red | Timer and alarm blocks |
| Drawing | Purple | Shape and text drawing |
| Score/Lives/Health | Green | Score tracking blocks |
| Instance | Pink | Create/destroy instances |
| Room | Brown | Room navigation |
| Values | Dark Blue | Variables and expressions |
| Sound | | Audio playback |
| Output | | Messages and display |

### Block Dependencies

Some blocks require other blocks to function. The configuration dialog shows warnings when dependencies are missing. For example, the **Draw Score** block requires **Set Score** and **Add Score** to be enabled.

---

## 15. Thymio Robot Support

PyGameMaker includes support for the Thymio educational robot, allowing you to simulate and program Thymio robots within the IDE.

### What is Thymio?

Thymio is a small educational robot with sensors, LEDs, motors, and buttons. PyGameMaker can simulate Thymio behavior and export code to run on real robots.

### Enabling Thymio

Go to **Tools > Thymio Programming > Show Thymio Tab in Object Editor** to enable Thymio features in the object editor.

### Thymio Simulator

The simulator models the physical Thymio robot:

**Specifications:**
- Robot size: 110x110 pixels (11cm x 11cm)
- Wheel base: 95 pixels
- Motor speed range: -500 to +500

### Thymio Sensors

| Sensor | Count | Range | Description |
|--------|-------|-------|-------------|
| Proximity | 7 | 0-4000 | Horizontal distance sensors (10cm range) |
| Ground | 2 | 0-1023 | Detects light/dark surfaces |
| Buttons | 5 | 0/1 | Forward, backward, left, right, center |

### Thymio Events

| Event | Triggers When |
|-------|---------------|
| Button Forward/Backward/Left/Right/Center | Capacitive button pressed |
| Any Button | Any button state changes |
| Proximity Update | Proximity sensors update (10 Hz) |
| Ground Update | Ground sensors update (10 Hz) |
| Tap | Accelerometer detects tap/shock |
| Sound Detected | Microphone detects sound |
| Timer 0/1 | Timer period expires |
| Sound Finished | Sound playback completes |
| Message Received | IR communication received |

### Thymio Actions

**Motor Control:**
- Set Motor Speed (left, right independently)
- Move Forward / Backward
- Turn Left / Right
- Stop Motors

**LED Control:**
- Set Top LED (RGB color)
- Set Bottom Left/Right LED
- Set Circle LEDs (8 LEDs around perimeter)
- Turn Off All LEDs

**Sound:**
- Play Tone (frequency, duration)
- Play System Sound
- Stop Sound

**Sensor Conditions:**
- If Proximity (sensor, threshold, comparison)
- If Ground Dark / Light
- If Button Pressed / Released

**Timer:**
- Set Timer Period (timer 0 or 1, period in ms)

### Exporting to Real Thymio

1. Export your Thymio project via the Aseba exporter
2. Open the generated `.aesl` file in Aseba Studio
3. Connect your Thymio via USB
4. Click **Load** then **Run**

---

## 16. Settings and Preferences

Open **Tools > Preferences** to configure the IDE.

### Appearance Tab

| Setting | Options | Default |
|---------|---------|---------|
| Font Size | 8-24 pt | 10 |
| Font Family | System Default, Segoe UI, Arial, Ubuntu, Helvetica, SF Pro Text, Roboto | System Default |
| Theme | Default, Dark, Light | Default |
| UI Scale | 0.5x - 2.0x | 1.0x |
| Show Tooltips | Yes/No | Yes |

### Editor Tab

| Setting | Options | Default |
|---------|---------|---------|
| Enable Auto-Save | Yes/No | Yes |
| Auto-Save Interval | 1-30 minutes | 5 min |
| Show Grid | Yes/No | Yes |
| Grid Size | 8-128 px | 32 |
| Snap to Grid | Yes/No | Yes |
| Show Collision Boxes | Yes/No | No |

### Project Tab

| Setting | Options | Default |
|---------|---------|---------|
| Default Projects Folder | Path | ~/PyGameMaker Projects |
| Recent Projects Limit | 5-50 | 10 |
| Create Backup on Save | Yes/No | Yes |

### Advanced Tab

| Setting | Options | Default |
|---------|---------|---------|
| Debug Mode | Yes/No | No |
| Show Console Output | Yes/No | Yes |
| Maximum Undo Steps | 10-200 | 50 |

### Configuration File

Settings are stored in `~/.pygamemaker/config.json` and persist between sessions.

### Changing Language

Go to **Tools > Language** and select your preferred language.

**Supported Languages:**
- English
- Francais
- Espanol
- Deutsch
- Italiano
- Русский (Russian)
- Slovenscina (Slovenian)
- Українська (Ukrainian)

The interface updates immediately. Some changes may require restarting the IDE.

---

## 17. Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+O | Open Project |
| Ctrl+S | Save Project |
| Ctrl+Shift+S | Save Project As |
| Ctrl+E | Export Project |
| Ctrl+Q | Exit IDE |
| Ctrl+R | Create Room |
| F1 | Documentation |
| F5 | Test Game |
| F6 | Debug Game |
| F7 | Build Game |
| F8 | Build and Run |

### Editor Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+X | Cut |
| Ctrl+C | Copy |
| Ctrl+V | Paste |
| Ctrl+D | Duplicate |
| Ctrl+F | Find |
| Ctrl+H | Find and Replace |
| Delete | Delete selected |

### Sprite Editor Shortcuts

| Shortcut | Action |
|----------|--------|
| P | Pencil tool |
| E | Eraser tool |
| I | Color picker (eyedropper) |
| G | Fill (bucket) tool |
| L | Line tool |
| R | Rectangle tool |
| O | Ellipse tool |
| S | Selection tool |
| Ctrl+Mouse Wheel | Zoom in/out |

---

## 18. Tutorials

PyGameMaker includes built-in tutorials to help you get started. Access them from **Help > Tutorials** or from the Tutorials folder in the installation directory.

### Available Tutorials

| # | Tutorial | Description |
|---|----------|-------------|
| 01 | Getting Started | IDE introduction and first project |
| 02 | First Game | Creating your first playable game |
| 03 | Pong | Classic Pong game with paddle and ball |
| 04 | Breakout | Breakout-style brick breaker |
| 05 | Sokoban | Box-pushing puzzle game |
| 06 | Maze | Maze navigation game |
| 07 | Platformer | Side-scrolling platform game |
| 08 | Lunar Lander | Gravity-based landing game |

Tutorials are available in multiple languages (English, German, Spanish, French, Italian, Russian, Slovenian, Ukrainian).

---

## 19. Troubleshooting

### Game won't start (F5)

- Verify your project has at least one room with instances
- Check that objects have sprites assigned
- Look at the console output (F6 debug mode) for error messages

### Sprites not showing

- Confirm the sprite file exists in the `sprites/` folder
- Check that the object has a sprite assigned in its properties
- Verify the instance is set to `visible = true`

### Collision not working

- Ensure the target object is marked as **Solid** if using solid-based collision
- Verify you have a **Collision With** event set up for the correct object
- Check that instances are actually overlapping (use debug mode)

### Sound not playing

- Verify the sound file exists and is a supported format (WAV, OGG, MP3)
- Check that pygame.mixer initialized successfully (see console output)
- Music files stream from disk - ensure the file path is correct

### Export fails

- **EXE Export:** Ensure PyInstaller is installed (`pip install pyinstaller`)
- **Kivy Export:** Ensure Kivy is installed (`pip install kivy`)
- **HTML5 Export:** Check console for any encoding errors
- All exports require a valid project with at least one room

### Performance issues

- Reduce the number of instances in rooms
- Use the spatial grid collision system (enabled by default)
- Avoid expensive operations in Step events (runs 60 times per second)
- Use alarms for periodic tasks instead of counting frames in Step

---

**PyGameMaker IDE** - Version 1.0.0-rc.4
Copyright 2024-2025 Gabriel Thullen
Licensed under GNU General Public License v3 (GPLv3)
GitHub: https://github.com/Gabe1290/pythongm

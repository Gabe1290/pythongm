# PyGameMaker IDE v0.9.0 - Complete Test Plan

**Document Version:** 1.0
**Date:** November 2025
**GitHub:** https://github.com/Gabe1290/pythongm

---

## Table of Contents

1. [Test Environment Setup](#1-test-environment-setup)
2. [IDE Core Functions](#2-ide-core-functions)
3. [Project Management](#3-project-management)
4. [Asset Management](#4-asset-management)
5. [Object Editor](#5-object-editor)
6. [Blockly Visual Programming - Beginner Profile](#6-blockly-visual-programming---beginner-profile)
7. [Blockly Visual Programming - Intermediate Profile](#7-blockly-visual-programming---intermediate-profile)
8. [Blockly Visual Programming - Full Profile](#8-blockly-visual-programming---full-profile)
9. [Traditional Events Panel](#9-traditional-events-panel)
10. [Room Editor](#10-room-editor)
11. [Game Export & Run](#11-game-export--run)
12. [Localization](#12-localization)
13. [Bug Report Template](#13-bug-report-template)

---

## 1. Test Environment Setup

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] PySide6 installed
- [ ] Pygame installed
- [ ] All dependencies from requirements.txt installed

### Launch IDE
```bash
cd /path/to/pygm2
python3 main.py
```

### Initial Verification
| Test | Expected Result | Pass/Fail | Notes |
|------|-----------------|-----------|-------|
| IDE launches without errors | Main window appears | | |
| No console errors on startup | Clean startup log | | |
| Menu bar visible | File, Edit, Assets, Run, Settings, Help menus | | |
| Asset tree visible | Left panel shows asset categories | | |
| Properties panel visible | Right panel for asset properties | | |

---

## 2. IDE Core Functions

### 2.1 Menu Bar Tests

#### File Menu
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| New Project | File > New Project | New project dialog appears | | |
| Open Project | File > Open Project | File browser opens | | |
| Save Project | File > Save Project | Project saves (Ctrl+S works) | | |
| Recent Projects | File > Recent Projects | List of recent projects shown | | |
| Exit | File > Exit | IDE closes (prompts if unsaved) | | |

#### Edit Menu
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Undo | Edit > Undo (Ctrl+Z) | Last action undone | | |
| Redo | Edit > Redo (Ctrl+Y) | Undone action restored | | |
| Cut | Edit > Cut (Ctrl+X) | Selection cut to clipboard | | |
| Copy | Edit > Copy (Ctrl+C) | Selection copied | | |
| Paste | Edit > Paste (Ctrl+V) | Clipboard content pasted | | |

#### Settings Menu
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Language submenu | Settings > Language | Language options displayed | | |
| Change to French | Select Français | Restart dialog in French | | |
| Change to German | Select Deutsch | Restart dialog in German | | |
| Change to Italian | Select Italiano | Restart dialog in Italian | | |
| Change to English | Select English | Restart dialog in English | | |

#### Help Menu
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| About | Help > About PyGameMaker | About dialog shows v0.9.0 | | |
| GitHub link | Click GitHub URL in About | Opens browser to repository | | |
| Documentation | Help > Documentation | Documentation opens | | |

---

## 3. Project Management

### 3.1 Create New Project
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | File > New Project | New Project dialog appears | | |
| 2 | Enter project name "TestProject" | Name accepted | | |
| 3 | Select location | Folder browser works | | |
| 4 | Click Create | Project created and loaded | | |
| 5 | Verify in file system | project.json exists in folder | | |

### 3.2 Open Existing Project
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | File > Open Project | File browser opens | | |
| 2 | Navigate to project folder | Folders visible | | |
| 3 | Select project.json | File selected | | |
| 4 | Click Open | Project loads with all assets | | |

### 3.3 Save Project
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Make a change to project | Change made | | |
| 2 | File > Save (or Ctrl+S) | Project saved | | |
| 3 | Check file timestamp | project.json updated | | |

---

## 4. Asset Management

### 4.1 Sprites
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Create sprite | Right-click Sprites > Add Sprite | New sprite created | | |
| Import image | Import PNG/JPG file | Image loaded as sprite | | |
| Rename sprite | Double-click name | Name editable | | |
| Delete sprite | Right-click > Delete | Sprite removed | | |
| View sprite properties | Select sprite | Properties shown in panel | | |

### 4.2 Sounds
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Create sound | Right-click Sounds > Add Sound | New sound created | | |
| Import audio | Import WAV/MP3/OGG file | Audio loaded | | |
| Preview sound | Click play button | Sound plays | | |
| Delete sound | Right-click > Delete | Sound removed | | |

### 4.3 Objects
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Create object | Right-click Objects > Add Object | New object created | | |
| Open object editor | Double-click object | Object editor opens | | |
| Assign sprite | Select sprite in properties | Sprite assigned | | |
| Set visible | Toggle visible checkbox | Property saved | | |
| Set solid | Toggle solid checkbox | Property saved | | |
| Set persistent | Toggle persistent checkbox | Property saved | | |
| Delete object | Right-click > Delete | Object removed | | |

### 4.4 Rooms
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Create room | Right-click Rooms > Add Room | New room created | | |
| Open room editor | Double-click room | Room editor opens | | |
| Set room size | Change width/height | Size updated | | |
| Set background color | Select color | Background changes | | |
| Delete room | Right-click > Delete | Room removed | | |

---

## 5. Object Editor

### 5.1 Basic Functions
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Open editor | Double-click object | Editor window opens | | |
| Save button | Click Save (or Ctrl+S) | Object saved | | |
| Properties panel | View right side | Sprite, visible, solid, persistent shown | | |
| Events panel | View left side | Event categories visible | | |
| Tabs visible | Check center panel | Event List, Visual Programming, Code Editor tabs | | |

### 5.2 Tab Navigation
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Event List tab | Click tab | Traditional event view shown | | |
| Visual Programming tab | Click tab | Blockly editor shown | | |
| Code Editor tab | Click tab | Python code editor shown | | |
| View Generated Code | Enable checkbox | Code auto-updates | | |

---

## 6. Blockly Visual Programming - Beginner Profile

**Setup:** Settings > Configure Blocks > Select "Beginner (Basic Blocks)"

### 6.1 Available Blocks Verification
| Block | Category | Available | Pass/Fail | Notes |
|-------|----------|-----------|-----------|-------|
| On Create | Events | Yes | | |
| On Step | Events | Yes | | |
| On Key Press | Events | Yes | | |
| On Collision | Events | Yes | | |
| Set Horizontal Speed | Movement | Yes | | |
| Set Vertical Speed | Movement | Yes | | |
| Stop Movement | Movement | Yes | | |
| Jump To Position | Movement | Yes | | |
| Destroy Instance | Instance | Yes | | |
| Create Instance | Instance | Yes | | |
| Set Score | Score | Yes | | |
| Add to Score | Score | Yes | | |
| Draw Score | Score | Yes | | |
| Show Message | Output | Yes | | |

### 6.2 Event Blocks Tests

#### 6.2.1 On Create Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Drag "On Create" to workspace | Block placed | | |
| 2 | Add "Set Score to 0" inside | Block snaps inside | | |
| 3 | Click "Apply to Events" | Event created in Events panel | | |
| 4 | Run game | Score initialized to 0 | | |

#### 6.2.2 On Step Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Drag "On Step" to workspace | Block placed | | |
| 2 | Add "Add 1 to Score" inside | Block snaps inside | | |
| 3 | Apply and run game | Score increases each frame | | |

#### 6.2.3 On Key Press Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Drag "On Key Press" to workspace | Block placed | | |
| 2 | Select "Right Arrow" key | Key selected in dropdown | | |
| 3 | Add "Set Horizontal Speed to 5" | Block snaps inside | | |
| 4 | Apply and run game | Object moves right on key press | | |

**Test all keys:**
| Key | Action Added | Expected Result | Pass/Fail |
|-----|--------------|-----------------|-----------|
| Left Arrow | Set hspeed to -5 | Moves left | |
| Right Arrow | Set hspeed to 5 | Moves right | |
| Up Arrow | Set vspeed to -5 | Moves up | |
| Down Arrow | Set vspeed to 5 | Moves down | |
| Space | Show Message | Message appears | |
| Enter | Add 10 to Score | Score increases | |

#### 6.2.4 On Collision Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Create two objects (obj_player, obj_enemy) | Objects created | | |
| 2 | Drag "On Collision with" to workspace | Block placed | | |
| 3 | Select obj_enemy from dropdown | Object selected | | |
| 4 | Add "Destroy Instance" inside | Block snaps inside | | |
| 5 | Apply and run game | obj_player destroyed on collision | | |

### 6.3 Movement Blocks Tests

#### 6.3.1 Set Horizontal Speed
| Test | Value | Expected Result | Pass/Fail | Notes |
|------|-------|-----------------|-----------|-------|
| Positive speed | 5 | Object moves right | | |
| Negative speed | -5 | Object moves left | | |
| Zero speed | 0 | Object stops horizontally | | |
| Large speed | 20 | Object moves fast right | | |

#### 6.3.2 Set Vertical Speed
| Test | Value | Expected Result | Pass/Fail | Notes |
|------|-------|-----------------|-----------|-------|
| Positive speed | 5 | Object moves down | | |
| Negative speed | -5 | Object moves up | | |
| Zero speed | 0 | Object stops vertically | | |

#### 6.3.3 Stop Movement
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Set object moving (hspeed=5, vspeed=5) | Object moves | | |
| 2 | Trigger Stop Movement action | Object stops completely | | |

#### 6.3.4 Jump To Position
| Test | X | Y | Expected Result | Pass/Fail | Notes |
|------|---|---|-----------------|-----------|-------|
| Jump to origin | 0 | 0 | Object at top-left | | |
| Jump to center | 320 | 240 | Object at center | | |
| Jump to position | 100 | 200 | Object at (100,200) | | |

### 6.4 Instance Blocks Tests

#### 6.4.1 Destroy Instance
| Test | Target | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Destroy self | Self | Current instance removed | | |
| Destroy other | Other (in collision) | Colliding instance removed | | |

#### 6.4.2 Create Instance
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Create obj_bullet object | Object created | | |
| 2 | In obj_player, add Create Instance | Block placed | | |
| 3 | Select obj_bullet, position (x+32, y) | Parameters set | | |
| 4 | Trigger action | New bullet created at offset | | |

### 6.5 Score Blocks Tests

#### 6.5.1 Set Score
| Test | Value | Expected Result | Pass/Fail | Notes |
|------|-------|-----------------|-----------|-------|
| Set to 0 | 0 | Score becomes 0 | | |
| Set to 100 | 100 | Score becomes 100 | | |
| Set to -50 | -50 | Score becomes -50 | | |

#### 6.5.2 Add to Score
| Test | Current | Add | Expected Result | Pass/Fail | Notes |
|------|---------|-----|-----------------|-----------|-------|
| Add positive | 0 | 10 | Score = 10 | | |
| Add negative | 100 | -25 | Score = 75 | | |
| Multiple adds | 0 | 5 (x3) | Score = 15 | | |

#### 6.5.3 Draw Score
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Add Draw Score in draw event | Block placed | | |
| 2 | Set position (10, 10) | Position set | | |
| 3 | Run game | Score displayed at (10,10) | | |

### 6.6 Output Blocks Tests

#### 6.6.1 Show Message
| Test | Message | Expected Result | Pass/Fail | Notes |
|------|---------|-----------------|-----------|-------|
| Simple text | "Hello World" | Message dialog appears | | |
| Empty message | "" | Empty dialog or no dialog | | |
| Long message | "This is a very long..." | Full message displayed | | |

### 6.7 Blockly Editor Functions

| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Drag block | Drag from toolbox | Block appears on workspace | | |
| Connect blocks | Drag block to connection | Blocks snap together | | |
| Delete block | Right-click > Delete | Block removed | | |
| Undo | Ctrl+Z | Last action undone | | |
| Redo | Ctrl+Y | Action restored | | |
| Clear All | Click Clear All button | Workspace cleared | | |
| Apply to Events | Click Apply button | Events panel updated | | |
| Sync from Events | Click Sync button | Blocks loaded from events | | |
| Detach window | Click Detach button | Editor opens in new window | | |
| Attach window | Close detached window | Editor returns to tab | | |
| Reload | Click Reload button | Blockly reloads | | |

---

## 7. Blockly Visual Programming - Intermediate Profile

**Setup:** Settings > Configure Blocks > Select "Intermediate"

### 7.1 Additional Blocks Verification
| Block | Category | Available | Pass/Fail | Notes |
|-------|----------|-----------|-----------|-------|
| On Draw | Events | Yes | | |
| On Destroy | Events | Yes | | |
| On Mouse Click | Events | Yes | | |
| On Alarm | Events | Yes | | |
| Set Direction and Speed | Movement | Yes | | |
| Move Towards Point | Movement | Yes | | |
| Set Alarm | Timing | Yes | | |
| Set Lives | Score/Lives | Yes | | |
| Add to Lives | Score/Lives | Yes | | |
| Draw Lives | Score/Lives | Yes | | |
| Set Health | Health | Yes | | |
| Add to Health | Health | Yes | | |
| Draw Health Bar | Health | Yes | | |
| Play Sound | Sound | Yes | | |
| Play Music | Sound | Yes | | |
| Next Room | Room | Yes | | |
| Restart Room | Room | Yes | | |

### 7.2 Additional Event Tests

#### 7.2.1 On Draw Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Drag "On Draw" to workspace | Block placed | | |
| 2 | Add Draw Score block inside | Block snaps inside | | |
| 3 | Run game | Score drawn on screen | | |

#### 7.2.2 On Destroy Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Drag "On Destroy" to workspace | Block placed | | |
| 2 | Add "Add 100 to Score" inside | Block snaps inside | | |
| 3 | Destroy instance during game | Score increases by 100 | | |

#### 7.2.3 On Mouse Click Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Drag "On Mouse Click" to workspace | Block placed | | |
| 2 | Select "Left Button" | Button selected | | |
| 3 | Add action inside | Block snaps inside | | |
| 4 | Click on object in game | Action triggers | | |

#### 7.2.4 On Alarm Event
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | In Create event, add "Set Alarm 0 to 60" | Alarm set | | |
| 2 | Drag "On Alarm 0" to workspace | Block placed | | |
| 3 | Add action inside | Block snaps inside | | |
| 4 | Run game, wait 1 second | Alarm triggers | | |

### 7.3 Lives System Tests

| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Set Lives to 3 | Use Set Lives block | Lives = 3 | | |
| Add 1 Life | Use Add to Lives block | Lives increases | | |
| Subtract Life | Add -1 to Lives | Lives decreases | | |
| Draw Lives | Use Draw Lives block | Lives shown as images | | |
| Lives reach 0 | Subtract until 0 | Game Over event triggers | | |

### 7.4 Health System Tests

| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Set Health to 100 | Use Set Health block | Health = 100 | | |
| Reduce Health | Add -25 to Health | Health = 75 | | |
| Draw Health Bar | Use Draw Health Bar | Bar displayed | | |
| Health at 50% | Set to 50 | Bar shows half full | | |
| Health at 0 | Set to 0 | No More Health event triggers | | |

### 7.5 Sound Tests

| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Play Sound | Use Play Sound block | Sound effect plays once | | |
| Play Music | Use Play Music block | Background music loops | | |
| Stop Sound | Use Stop Sound block | Sound stops | | |

### 7.6 Room Navigation Tests

| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Next Room | Use Next Room block | Goes to next room | | |
| Restart Room | Use Restart Room block | Current room restarts | | |
| Previous Room | Use Previous Room block | Goes to previous room | | |

---

## 8. Blockly Visual Programming - Full Profile

**Setup:** Settings > Configure Blocks > Select "Full (All Blocks)"

### 8.1 Complete Block List Verification

#### Events Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| event_create | | | |
| event_destroy | | | |
| event_step | | | |
| event_begin_step | | | |
| event_end_step | | | |
| event_draw | | | |
| event_alarm | | | |
| event_keyboard | | | |
| event_keyboard_press | | | |
| event_keyboard_release | | | |
| event_mouse | | | |
| event_collision | | | |

#### Movement Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| set_hspeed | | | |
| set_vspeed | | | |
| set_direction_speed | | | |
| move_towards | | | |
| stop | | | |
| jump_to | | | |
| jump_random | | | |
| snap_to_grid | | | |
| wrap | | | |
| bounce | | | |
| reverse_h | | | |
| reverse_v | | | |
| gravity | | | |
| friction | | | |

#### Grid Movement Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| if_on_grid | | | |
| stop_if_no_keys | | | |
| check_keys_move | | | |

#### Timing Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| set_alarm | | | |

#### Drawing Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| draw_self | | | |
| draw_sprite | | | |
| draw_text | | | |
| draw_rectangle | | | |
| set_color | | | |

#### Score/Lives/Health Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| score_set | | | |
| score_add | | | |
| draw_score | | | |
| lives_set | | | |
| lives_add | | | |
| draw_lives | | | |
| health_set | | | |
| health_add | | | |
| draw_health_bar | | | |

#### Instance Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| destroy | | | |
| create | | | |
| change | | | |

#### Room Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| room_next | | | |
| room_previous | | | |
| room_restart | | | |
| room_goto | | | |

#### Values Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| value_x | | | |
| value_y | | | |
| value_hspeed | | | |
| value_vspeed | | | |
| value_direction | | | |
| value_speed | | | |
| value_score | | | |
| value_lives | | | |
| value_health | | | |

#### Sound Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| play_sound | | | |
| stop_sound | | | |
| play_music | | | |

#### Output Category
| Block | Available | Pass/Fail | Notes |
|-------|-----------|-----------|-------|
| message | | | |

---

## 9. Traditional Events Panel

### 9.1 Event Categories
| Category | Click to Expand | Events Listed | Pass/Fail | Notes |
|----------|-----------------|---------------|-----------|-------|
| Create | Click | create | | |
| Destroy | Click | destroy | | |
| Alarm | Click | alarm_0 to alarm_11 | | |
| Step | Click | begin_step, step, end_step | | |
| Collision | Click | collision (select object) | | |
| Keyboard | Click | keyboard, press, release | | |
| Mouse | Click | All mouse events | | |
| Other | Click | room_start, room_end, etc. | | |
| Draw | Click | draw | | |

### 9.2 Adding Events
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Add Create event | Right-click > Add Event > Create | Event added | | |
| Add Step event | Right-click > Add Event > Step | Event added | | |
| Add Keyboard event | Select key from dialog | Event added with key | | |
| Add Collision event | Select object from dialog | Event added | | |
| Delete event | Right-click event > Delete | Event removed | | |

### 9.3 Adding Actions to Events
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Select event | Click on event | Event highlighted | | |
| Add action | Right-click > Add Action | Action dialog appears | | |
| Select action | Choose from categories | Action added to event | | |
| Configure action | Set parameters | Parameters saved | | |
| Delete action | Right-click > Delete | Action removed | | |
| Reorder actions | Drag and drop | Order changed | | |

---

## 10. Room Editor

### 10.1 Basic Functions
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Open room editor | Double-click room | Editor opens | | |
| View grid | Grid visible | Grid lines shown | | |
| Toggle grid | Grid button | Grid toggles on/off | | |
| Zoom in | Zoom control | View zooms in | | |
| Zoom out | Zoom control | View zooms out | | |

### 10.2 Instance Placement
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Select object | Click object in list | Object selected | | |
| Place instance | Click in room | Instance appears | | |
| Move instance | Drag instance | Instance moves | | |
| Delete instance | Right-click > Delete | Instance removed | | |
| Snap to grid | Enable snap | Instances align to grid | | |

### 10.3 Room Properties
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Set room width | Change value | Width updated | | |
| Set room height | Change value | Height updated | | |
| Set background color | Pick color | Background changes | | |
| Set room speed | Change FPS | Speed updated | | |

---

## 11. Game Export & Run

### 11.1 Run Game
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Run from IDE | Run > Run Game (F5) | Game window opens | | |
| Game loads first room | Automatic | First room displayed | | |
| Objects appear | Automatic | All instances visible | | |
| Game responds to input | Press keys | Objects react | | |
| Stop game | Close window or Escape | Game closes | | |

### 11.2 Debug Mode
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Run in debug | Run > Debug | Debug info shown | | |
| View console output | Check console | Print statements visible | | |
| Error handling | Cause error | Error message shown | | |

### 11.3 Export
| Test | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| Export to folder | Run > Export | Files exported | | |
| Standalone executable | Export option | .exe/.app created | | |
| Run exported game | Double-click | Game runs independently | | |

---

## 12. Localization

### 12.1 Language Tests
For each language, verify the following are translated:

| Element | English | French | German | Italian | Pass/Fail |
|---------|---------|--------|--------|---------|-----------|
| Menu: File | File | Fichier | Datei | File | |
| Menu: Edit | Edit | Édition | Bearbeiten | Modifica | |
| Menu: Help | Help | Aide | Hilfe | Aiuto | |
| New Project | New Project | Nouveau projet | Neues Projekt | Nuovo progetto | |
| Save | Save | Sauvegarder | Speichern | Salva | |
| About dialog | English text | French text | German text | Italian text | |
| Blockly blocks | English | French | German | Italian | |

### 12.2 Language Switch Test
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Start in English | IDE in English | | |
| 2 | Change to French | Restart dialog in French | | |
| 3 | Restart | IDE fully in French | | |
| 4 | Change to English | Restart dialog in English | | |
| 5 | Restart | IDE fully in English | | |

---

## 13. Bug Report Template

When reporting bugs, please use this template:

```
### Bug Report

**Version:** 0.9.0
**OS:** [Windows/Linux/macOS] [version]
**Python Version:**

**Description:**
[Clear description of the bug]

**Steps to Reproduce:**
1.
2.
3.

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Screenshots:**
[If applicable]

**Console Output:**
```
[Any error messages from terminal]
```

**Additional Context:**
[Any other relevant information]
```

---

## Test Summary

| Section | Tests Passed | Tests Failed | Notes |
|---------|--------------|--------------|-------|
| IDE Core Functions | / | | |
| Project Management | / | | |
| Asset Management | / | | |
| Object Editor | / | | |
| Blockly - Beginner | / | | |
| Blockly - Intermediate | / | | |
| Blockly - Full | / | | |
| Traditional Events | / | | |
| Room Editor | / | | |
| Game Export & Run | / | | |
| Localization | / | | |
| **TOTAL** | / | | |

---

**Tested By:** _______________________
**Date:** _______________________
**Signature:** _______________________

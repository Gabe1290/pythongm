# Code Editor Test Projects

A comprehensive set of test projects for validating the Python Code Editor functionality in PyGameMaker. These projects are designed to systematically test all items in the Code Editor Checklist.

## Test Projects Overview

| Project | Description | Checklist Sections Covered |
|---------|-------------|---------------------------|
| test_01_movement_physics | Movement and physics actions | Section 2: Movement Actions |
| test_02_events | All event types | Section 1: Event Testing |
| test_03_instances | Instance creation/destruction | Section 3: Instance Actions |
| test_04_rooms | Room navigation | Section 4: Room Actions, Section 5: Game Actions |
| test_05_score_lives_health | Score, lives, health management | Section 6: Score/Lives/Health Actions |
| test_06_sound_sprite | Sound playback and sprite changes | Section 7: Sprite Actions, Section 9: Sound Actions |
| test_07_alarms | All 12 alarms (0-11) | Section 8: Timing Actions |
| test_08_bidirectional_sync | Code-to-blocks sync testing | Section 11: Bidirectional Sync Testing |

---

## Test Project 1: Movement & Physics

**Location:** `test_01_movement_physics/`

**Purpose:** Tests all movement and physics-related actions.

### Objects to Test:
- **obj_ball** - Main test object with all movement actions

### Checklist Items Covered:
- [ ] Set Horizontal Speed (hspeed) - Arrow keys and create event
- [ ] Set Vertical Speed (vspeed) - Arrow keys and create event
- [ ] Stop Movement - Press SPACE
- [ ] Reverse Horizontal - Press R
- [ ] Reverse Vertical - Press T
- [ ] Set Gravity - Applied in create event
- [ ] Set Friction - Applied in create event
- [ ] Jump to Position - Press J (jumps to center)
- [ ] Snap to Grid - Press G (32x32 grid)
- [ ] Set Direction and Speed - Press D

### Test Instructions:
1. Open project and edit obj_ball
2. Check Code Editor shows Python for all events
3. Verify blocks match the code
4. Test gameplay: arrow keys move, SPACE stops, R/T reverse, G snaps, J teleports

---

## Test Project 2: Events

**Location:** `test_02_events/`

**Purpose:** Tests all event types (create, destroy, step, keyboard, collision, draw).

### Objects to Test:
- **obj_player** - All keyboard and collision events
- **obj_enemy** - Create and step events
- **obj_dot** - Collision event (destroy on contact)

### Checklist Items Covered:
- [ ] Create Event - Player shows message
- [ ] Destroy Event - Player shows message
- [ ] Step Event - Present (empty for testing)
- [ ] Begin Step - Present (empty for testing)
- [ ] End Step - Present (empty for testing)
- [ ] Draw Event - Draws score, lives, health bar
- [ ] Keyboard (held) - Arrow keys and WASD
- [ ] Keyboard Press - Space, Enter, Escape
- [ ] Keyboard Release - Space
- [ ] Collision With Object - Multiple collision events

### Test Instructions:
1. Open obj_player and verify all events show in Code Editor
2. Switch between Code/Blocks tabs to verify sync
3. Run game and test all keyboard inputs
4. Collect dots (collision test)
5. Touch enemy (health decrease test)

---

## Test Project 3: Instance Management

**Location:** `test_03_instances/`

**Purpose:** Tests instance creation and destruction.

### Objects to Test:
- **obj_shooter** - Creates bullets (create_instance)
- **obj_bullet** - Self-destructs on collision (destroy_instance)
- **obj_target** - Creates explosion on death, destroys self
- **obj_explosion** - Destroys self after alarm

### Checklist Items Covered:
- [ ] Create Instance - Shooter creates bullets, targets create explosions
- [ ] Destroy Instance (self) - Bullets and explosions destroy themselves
- [ ] Destroy Instance (other) - Target destroyed by bullet collision

### Test Instructions:
1. Open obj_shooter - verify create_instance code for Space key
2. Open obj_bullet - verify destroy_instance in collision
3. Open obj_target - verify both create_instance and destroy_instance
4. Run game: move with arrows, shoot with Space
5. Verify bullets destroy targets, targets create explosions

---

## Test Project 4: Room Navigation

**Location:** `test_04_rooms/`

**Purpose:** Tests all room navigation actions.

### Rooms:
- **room_1** - Starting room (gray), has next door
- **room_2** - Middle room (purple), has prev and next doors
- **room_3** - Final room (green), has prev door and goto_room_1 door

### Checklist Items Covered:
- [ ] Next Room - Touch obj_door_next
- [ ] Previous Room - Touch obj_door_prev
- [ ] Restart Room - Press R
- [ ] Go to Room - Touch obj_door_goto (goes to room_1)
- [ ] End Game - Press Escape
- [ ] Restart Game - Press G

### Test Instructions:
1. Open obj_player - verify all room navigation code
2. Run game from room_1
3. Touch doors to navigate between rooms
4. Verify background colors change (gray -> purple -> green)
5. Test R to restart, G to restart game, Escape to quit

---

## Test Project 5: Score/Lives/Health

**Location:** `test_05_score_lives_health/`

**Purpose:** Tests all score, lives, and health actions.

### Objects to Test:
- **obj_player** - All set/add/draw actions
- **obj_coin** - Adds to score on collision
- **obj_enemy** - Reduces health on collision
- **obj_life_pickup** - Adds lives on collision
- **obj_health_pickup** - Adds health on collision

### Checklist Items Covered:
- [ ] Set Score - Create event, Press 1
- [ ] Add to Score - Collect coins (+100)
- [ ] Draw Score - Draw event
- [ ] Set Lives - Create event, Press 2
- [ ] Add Lives - Collect life pickup (+1)
- [ ] Draw Lives - Draw event
- [ ] Set Health - Create event, Press 3
- [ ] Add Health - Touch enemy (-25), collect health (+25)
- [ ] Draw Health Bar - Draw event

### Test Instructions:
1. Open obj_player - verify all score/lives/health code
2. Run game and observe HUD in top-left
3. Collect coins (score +100)
4. Touch enemies (health -25)
5. Collect pickups (lives +1, health +25)
6. Press 1/2/3 to set absolute values

---

## Test Project 6: Sound & Sprite

**Location:** `test_06_sound_sprite/`

**Purpose:** Tests sound playback and sprite/alpha changes.

### Sounds:
- **snd_pickup** - Played when collecting dots
- **snd_explosion** - Press S to play
- **mus_background** - Background music (looping)

### Checklist Items Covered:
- [ ] Play Sound - Collect pickups, Press S
- [ ] Play Music - Create event, Press P
- [ ] Stop Music - Press M
- [ ] Set Sprite - Direction changes player sprite
- [ ] Set Alpha - Press 1 (100%), 2 (50%), 3 (25%)

### Test Instructions:
1. Open obj_player - verify sound and sprite code
2. Run game - music should start automatically
3. Move with arrows - sprite should change direction
4. Collect dots - pickup sound plays
5. Press S - explosion sound
6. Press M - stop music, P - play music
7. Press 1/2/3 - change transparency

---

## Test Project 7: Alarms

**Location:** `test_07_alarms/`

**Purpose:** Tests all 12 alarms (0-11).

### Objects to Test:
- **obj_spawner** - Uses alarm 0 for repeated spawning
- **obj_particle** - Uses alarm 0 for timed destruction
- **obj_timer_demo** - Uses alarms 0-5 automatically, 6-10 on key press

### Checklist Items Covered:
- [ ] Alarm 0 - Spawner and timer demo
- [ ] Alarm 1 - Timer demo
- [ ] Alarm 2 - Timer demo
- [ ] Alarm 3 - Timer demo
- [ ] Alarm 4 - Timer demo
- [ ] Alarm 5 - Timer demo
- [ ] Alarm 6 - Press 6
- [ ] Alarm 7 - Press 7
- [ ] Alarm 8 - Press 8
- [ ] Alarm 9 - Press 9
- [ ] Alarm 10 - Press 0
- [ ] Alarm 11 - Available (no trigger key assigned)
- [ ] Set Alarm action - Used throughout

### Test Instructions:
1. Open obj_timer_demo - verify all alarm events and set_alarm actions
2. Run game - observe automatic alarm triggers (messages appear)
3. Watch spawners create particles
4. Press 6-9 and 0 to trigger additional alarms
5. Verify each alarm shows its message

---

## Test Project 8: Bidirectional Sync

**Location:** `test_08_bidirectional_sync/`

**Purpose:** Tests the bidirectional sync between Code Editor and Blockly.

### Objects to Test:
- **obj_simple_movement** - Basic actions (for simple sync testing)
- **obj_complex_events** - Multiple event types (for complex sync testing)
- **obj_all_actions** - Every action type (for comprehensive sync testing)

### Checklist Items Covered:
- [ ] Code to Blocks - Write code, verify blocks update
- [ ] Blocks to Code - Add blocks, verify code generates
- [ ] Round-Trip Testing - Edit in both views, verify no data loss

### Testing Procedure:

#### Code to Blocks Testing:
1. Open obj_simple_movement in Object Editor
2. Go to Code Editor tab
3. Manually edit the Python code (e.g., change `hspeed = 2` to `hspeed = 5`)
4. Switch to Blockly tab
5. Verify the block parameters show the updated value

#### Blocks to Code Testing:
1. Open obj_all_actions in Object Editor
2. Go to Blockly tab
3. Add a new block (e.g., add set_score action)
4. Switch to Code Editor tab
5. Verify the Python code includes the new action

#### Round-Trip Testing:
1. Open obj_complex_events
2. Make changes in Code Editor
3. Switch to Blockly, make additional changes
4. Switch back to Code Editor
5. Verify all changes are preserved
6. Run game to verify behavior matches code

---

## Comprehensive Testing Workflow

To fully validate the Code Editor against the checklist:

1. **Load each project** in PyGameMaker
2. **Open each object** in the Object Editor
3. **Check Code Editor tab** - verify Python code is displayed
4. **Check Blockly tab** - verify visual blocks match
5. **Run the game** - verify all actions work correctly
6. **Modify code** - verify changes sync to blocks
7. **Modify blocks** - verify changes sync to code
8. **Save and reload** - verify persistence

## Notes

- All projects use resources from the `resources/` folder
- Each project is self-contained with its own sprites, sounds, and objects
- Background colors differ between rooms/projects for easy identification
- Most keyboard controls use common gaming conventions (Arrow keys, WASD, Space)

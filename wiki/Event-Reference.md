# Event Reference

*[Home](Home) | [Preset Guide](Preset-Guide) | [Full Action Reference](Full-Action-Reference)*

This page documents all available events in PyGameMaker. Events are triggers that execute actions when specific conditions occur in your game.

## Event Categories

- [Object Events](#object-events) - Create, Step, Destroy
- [Input Events](#input-events) - Keyboard, Mouse
- [Collision Events](#collision-events) - Object collisions
- [Timing Events](#timing-events) - Alarms, Step variants
- [Drawing Events](#drawing-events) - Custom rendering
- [Room Events](#room-events) - Room transitions
- [Game Events](#game-events) - Game start/end
- [Other Events](#other-events) - Boundaries, Lives, Health

---

## Object Events

### Create
| Property | Value |
|----------|-------|
| **Name** | `create` |
| **Icon** | 🎯 |
| **Category** | Object |
| **Preset** | Beginner |

**Description:** Executed once when an instance is first created.

**When it fires:**
- When an instance is placed in a room at game start
- When created via the "Create Instance" action
- After room transitions for new instances

**Common uses:**
- Initialize variables
- Set starting values
- Configure initial state

---

### Step
| Property | Value |
|----------|-------|
| **Name** | `step` |
| **Icon** | ⭐ |
| **Category** | Object |
| **Preset** | Beginner |

**Description:** Executed every frame (typically 60 times per second).

**When it fires:** Continuously, every game frame.

**Common uses:**
- Continuous movement
- Checking conditions
- Updating positions
- Game logic

**Note:** Be careful with performance - code here runs constantly.

---

### Destroy
| Property | Value |
|----------|-------|
| **Name** | `destroy` |
| **Icon** | 💥 |
| **Category** | Object |
| **Preset** | Intermediate |

**Description:** Executed when an instance is destroyed.

**When it fires:** Just before the instance is removed from the game.

**Common uses:**
- Spawn effects (explosions, particles)
- Drop items
- Update scores
- Play sounds

---

## Input Events

### Keyboard (Continuous)
| Property | Value |
|----------|-------|
| **Name** | `keyboard` |
| **Icon** | ⌨️ |
| **Category** | Input |
| **Preset** | Beginner |

**Description:** Fires continuously while a key is held down.

**Best for:** Smooth, continuous movement

**Supported Keys:**
- Arrow keys (up, down, left, right)
- Letters (A-Z)
- Numbers (0-9)
- Space, Enter, Escape
- Function keys (F1-F12)
- Modifier keys (Shift, Ctrl, Alt)

---

### Keyboard Press
| Property | Value |
|----------|-------|
| **Name** | `keyboard_press` |
| **Icon** | 🔘 |
| **Category** | Input |
| **Preset** | Beginner |

**Description:** Fires once when a key is first pressed.

**Best for:** Single actions (jump, shoot, menu select)

**Difference from Keyboard:** Only fires once per press, not while held.

---

### Keyboard Release
| Property | Value |
|----------|-------|
| **Name** | `keyboard_release` |
| **Icon** | ⬆️ |
| **Category** | Input |
| **Preset** | Advanced |

**Description:** Fires once when a key is released.

**Common uses:**
- Stop movement when key released
- End charging attacks
- Toggle states

---

### Mouse
| Property | Value |
|----------|-------|
| **Name** | `mouse` |
| **Icon** | 🖱️ |
| **Category** | Input |
| **Preset** | Intermediate |

**Description:** Mouse button and movement events.

**Event Types:**

| Type | Description |
|------|-------------|
| Left Button | Click with left mouse button |
| Right Button | Click with right mouse button |
| Middle Button | Click with middle/scroll button |
| Mouse Enter | Cursor enters instance bounds |
| Mouse Leave | Cursor leaves instance bounds |
| Global Left Button | Left click anywhere |
| Global Right Button | Right click anywhere |

---

## Collision Events

### Collision
| Property | Value |
|----------|-------|
| **Name** | `collision` |
| **Icon** | 💥 |
| **Category** | Collision |
| **Preset** | Beginner |

**Description:** Fires when this instance overlaps with another object type.

**Configuration:** Select which object type triggers this collision.

**Special variable:** `other` - Reference to the colliding instance.

**When it fires:** Every frame that instances are overlapping.

**Common uses:**
- Collecting items
- Taking damage
- Hitting walls
- Triggering events

**Example collision events:**
- `collision_with_obj_coin` - Player touches a coin
- `collision_with_obj_enemy` - Player touches an enemy
- `collision_with_obj_wall` - Instance hits a wall

---

## Timing Events

### Alarm
| Property | Value |
|----------|-------|
| **Name** | `alarm` |
| **Icon** | ⏰ |
| **Category** | Timing |
| **Preset** | Intermediate |

**Description:** Fires when an alarm countdown reaches zero.

**Available alarms:** 12 independent alarms (alarm[0] through alarm[11])

**Setting alarms:** Use the "Set Alarm" action with steps (60 steps ≈ 1 second at 60 FPS)

**Common uses:**
- Timed spawning
- Cooldowns
- Delayed effects
- Repeating actions (set alarm again in alarm event)

---

### Begin Step
| Property | Value |
|----------|-------|
| **Name** | `begin_step` |
| **Icon** | ▶️ |
| **Category** | Step |
| **Preset** | Advanced |

**Description:** Fires at the beginning of each frame, before regular Step events.

**Execution order:** Begin Step → Step → End Step

**Common uses:**
- Input processing
- Pre-movement calculations

---

### End Step
| Property | Value |
|----------|-------|
| **Name** | `end_step` |
| **Icon** | ⏹️ |
| **Category** | Step |
| **Preset** | Advanced |

**Description:** Fires at the end of each frame, after collisions.

**Common uses:**
- Final position adjustments
- Cleanup operations
- State updates after collisions

---

## Drawing Events

### Draw
| Property | Value |
|----------|-------|
| **Name** | `draw` |
| **Icon** | 🎨 |
| **Category** | Drawing |
| **Preset** | Intermediate |

**Description:** Fires during the rendering phase.

**Important:** Adding a Draw event disables automatic sprite drawing. You must draw the sprite manually if you want it visible.

**Common uses:**
- Custom rendering
- Drawing shapes
- Displaying text
- Health bars
- HUD elements

**Available drawing actions:**
- Draw Sprite
- Draw Text
- Draw Rectangle
- Draw Circle
- Draw Line
- Draw Health Bar

---

## Room Events

### Room Start
| Property | Value |
|----------|-------|
| **Name** | `room_start` |
| **Icon** | 🚪 |
| **Category** | Room |
| **Preset** | Advanced |

**Description:** Fires when entering a room, after all Create events.

**Common uses:**
- Room initialization
- Play room music
- Set room-specific variables

---

### Room End
| Property | Value |
|----------|-------|
| **Name** | `room_end` |
| **Icon** | 🚪 |
| **Category** | Room |
| **Preset** | Advanced |

**Description:** Fires when leaving a room.

**Common uses:**
- Save progress
- Stop music
- Cleanup

---

## Game Events

### Game Start
| Property | Value |
|----------|-------|
| **Name** | `game_start` |
| **Icon** | 🎮 |
| **Category** | Game |
| **Preset** | Advanced |

**Description:** Fires once when the game first starts (in first room only).

**Common uses:**
- Initialize global variables
- Load saved data
- Play intro

---

### Game End
| Property | Value |
|----------|-------|
| **Name** | `game_end` |
| **Icon** | 🎮 |
| **Category** | Game |
| **Preset** | Advanced |

**Description:** Fires when the game is ending.

**Common uses:**
- Save game data
- Cleanup resources

---

## Other Events

### Outside Room
| Property | Value |
|----------|-------|
| **Name** | `outside_room` |
| **Icon** | 🚫 |
| **Category** | Other |
| **Preset** | Advanced |

**Description:** Fires when instance is completely outside room boundaries.

**Common uses:**
- Destroy off-screen bullets
- Wrap around to other side
- Trigger game over

---

### Intersect Boundary
| Property | Value |
|----------|-------|
| **Name** | `intersect_boundary` |
| **Icon** | ⚠️ |
| **Category** | Other |
| **Preset** | Advanced |

**Description:** Fires when instance touches the room boundary.

**Common uses:**
- Keep player in bounds
- Bounce off edges

---

### No More Lives
| Property | Value |
|----------|-------|
| **Name** | `no_more_lives` |
| **Icon** | 💀 |
| **Category** | Other |
| **Preset** | Intermediate |

**Description:** Fires when lives become 0 or less.

**Common uses:**
- Game over screen
- Restart game
- Show final score

---

### No More Health
| Property | Value |
|----------|-------|
| **Name** | `no_more_health` |
| **Icon** | 💔 |
| **Category** | Other |
| **Preset** | Intermediate |

**Description:** Fires when health becomes 0 or less.

**Common uses:**
- Lose a life
- Respawn player
- Trigger death animation

---

## Event Execution Order

Understanding when events fire helps create predictable game behavior:

1. **Begin Step** - Start of frame
2. **Alarm** - Any triggered alarms
3. **Keyboard/Mouse** - Input events
4. **Step** - Main game logic
5. **Collision** - After movement
6. **End Step** - After collisions
7. **Draw** - Rendering phase

---

## Events by Preset

| Preset | Events Included |
|--------|-----------------|
| **Beginner** | Create, Step, Keyboard Press, Collision |
| **Intermediate** | + Draw, Destroy, Mouse, Alarm |
| **Advanced** | + All keyboard variants, Begin/End Step, Room events, Game events, Boundary events |

---

## See Also

- [Full Action Reference](Full-Action-Reference) - Complete action list
- [Beginner Preset](Beginner-Preset) - Essential events for beginners
- [Intermediate Preset](Intermediate-Preset) - Additional events
- [Events and Actions](Events-and-Actions) - Core concepts overview

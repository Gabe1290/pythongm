# Beginner Preset

*[Home](Home) | [Preset Guide](Preset-Guide) | [Intermediate Preset](Intermediate-Preset)*

The **Beginner** preset is designed for users who are new to game development. It provides a curated set of essential events and actions that cover the fundamentals of creating simple 2D games without overwhelming beginners with too many options.

## Overview

The Beginner preset includes:
- **4 Event Types** - For responding to game situations
- **17 Action Types** - For controlling game behavior
- **6 Categories** - Events, Movement, Score/Lives/Health, Instance, Room, Output

---

## Events

Events are triggers that respond to specific situations in your game. When an event occurs, the actions you've defined for that event will execute.

### Create Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_create` |
| **Category** | Events |
| **Description** | Triggered once when an instance is first created |

**When it fires:** Immediately when an object instance is placed in a room or created with the "Create Instance" action.

**Common uses:**
- Initialize variables
- Set starting position
- Set initial speed or direction
- Reset score at game start

---

### Step Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_step` |
| **Category** | Events |
| **Description** | Triggered every frame (typically 60 times per second) |

**When it fires:** Continuously, every game frame.

**Common uses:**
- Continuous movement
- Checking conditions
- Updating game state
- Animation control

---

### Keyboard Press Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_keyboard_press` |
| **Category** | Events |
| **Description** | Triggered once when a specific key is pressed down |

**When it fires:** Once at the moment a key is pressed (not while held).

**Supported keys:** Arrow keys (up, down, left, right), Space, Enter, letters (A-Z), numbers (0-9)

**Common uses:**
- Player movement controls
- Jumping
- Shooting
- Menu navigation

---

### Collision Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_collision` |
| **Category** | Events |
| **Description** | Triggered when this instance collides with another object |

**When it fires:** Each frame that two instances are overlapping.

**Special variable:** In a collision event, `other` refers to the instance being collided with.

**Common uses:**
- Collecting items (coins, power-ups)
- Taking damage from enemies
- Hitting walls or obstacles
- Reaching goals or checkpoints

---

## Actions

Actions are commands that execute when an event is triggered. Multiple actions can be added to a single event and will execute in order.

---

## Movement Actions

### Set Horizontal Speed
| Property | Value |
|----------|-------|
| **Action Name** | `set_hspeed` |
| **Block Name** | `move_set_hspeed` |
| **Category** | Movement |
| **Icon** | ↔️ |

**Description:** Sets the horizontal movement speed of the instance.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Speed in pixels per frame. Positive = right, Negative = left |

**Example:** Set `value` to `4` to move right at 4 pixels per frame, or `-4` to move left.

---

### Set Vertical Speed
| Property | Value |
|----------|-------|
| **Action Name** | `set_vspeed` |
| **Block Name** | `move_set_vspeed` |
| **Category** | Movement |
| **Icon** | ↕️ |

**Description:** Sets the vertical movement speed of the instance.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Speed in pixels per frame. Positive = down, Negative = up |

**Example:** Set `value` to `-4` to move up at 4 pixels per frame, or `4` to move down.

---

### Stop Movement
| Property | Value |
|----------|-------|
| **Action Name** | `stop_movement` |
| **Block Name** | `move_stop` |
| **Category** | Movement |
| **Icon** | 🛑 |

**Description:** Stops all movement by setting both horizontal and vertical speed to zero.

**Parameters:** None

**Common uses:**
- Stop player when hitting a wall
- Stop enemies when reaching a destination
- Pause movement temporarily

---

### Jump to Position
| Property | Value |
|----------|-------|
| **Action Name** | `jump_to_position` |
| **Block Name** | `move_jump_to` |
| **Category** | Movement |
| **Icon** | 📍 |

**Description:** Instantly moves the instance to a specific position (no smooth movement).

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | Number | Target X coordinate |
| `y` | Number | Target Y coordinate |

**Example:** Jump to position (100, 200) to teleport the player to that location.

---

## Instance Actions

### Destroy Instance
| Property | Value |
|----------|-------|
| **Action Name** | `destroy_instance` |
| **Block Name** | `instance_destroy` |
| **Category** | Instance |
| **Icon** | 💥 |

**Description:** Removes an instance from the game.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `target` | Choice | `self` = destroy this instance, `other` = destroy the colliding instance |

**Common uses:**
- Remove collected coins (`target: other` in collision event)
- Destroy bullets when hitting something
- Remove enemies when defeated

---

### Create Instance
| Property | Value |
|----------|-------|
| **Action Name** | `create_instance` |
| **Block Name** | `instance_create` |
| **Category** | Instance |
| **Icon** | ✨ |

**Description:** Creates a new instance of an object at a specified position.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `object` | Object | The object type to create |
| `x` | Number | X coordinate for the new instance |
| `y` | Number | Y coordinate for the new instance |

**Example:** Create a bullet at the player's position when Space is pressed.

---

## Score Actions

### Set Score
| Property | Value |
|----------|-------|
| **Action Name** | `set_score` |
| **Block Name** | `score_set` |
| **Category** | Score/Lives/Health |
| **Icon** | 🏆 |

**Description:** Sets the score to a specific value, or adds/subtracts from the current score.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | The score value |
| `relative` | Boolean | If true, adds value to current score. If false, sets score to value |

**Examples:**
- Reset score: `value: 0`, `relative: false`
- Add 10 points: `value: 10`, `relative: true`
- Subtract 5 points: `value: -5`, `relative: true`

---

### Add to Score
| Property | Value |
|----------|-------|
| **Action Name** | `add_score` |
| **Block Name** | `score_add` |
| **Category** | Score/Lives/Health |
| **Icon** | ➕🏆 |

**Description:** Adds a value to the current score (shortcut for set_score with relative=true).

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Points to add (can be negative to subtract) |

---

### Draw Score
| Property | Value |
|----------|-------|
| **Action Name** | `draw_score` |
| **Block Name** | `draw_score` |
| **Category** | Score/Lives/Health |
| **Icon** | 🖼️🏆 |

**Description:** Displays the current score on screen.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | Number | X position to draw the score |
| `y` | Number | Y position to draw the score |
| `caption` | String | Text to display before the score (e.g., "Score: ") |

**Note:** This should be used in a Draw event (available in Intermediate preset).

---

## Room Actions

### Go to Next Room
| Property | Value |
|----------|-------|
| **Action Name** | `next_room` |
| **Block Name** | `room_goto_next` |
| **Category** | Room |
| **Icon** | ➡️ |

**Description:** Transitions to the next room in the room order.

**Parameters:** None

**Note:** If already in the last room, this action has no effect (use "If Next Room Exists" to check first).

---

### Go to Previous Room
| Property | Value |
|----------|-------|
| **Action Name** | `previous_room` |
| **Block Name** | `room_goto_previous` |
| **Category** | Room |
| **Icon** | ⬅️ |

**Description:** Transitions to the previous room in the room order.

**Parameters:** None

**Note:** If already in the first room, this action has no effect.

---

### Restart Room
| Property | Value |
|----------|-------|
| **Action Name** | `restart_room` |
| **Block Name** | `room_restart` |
| **Category** | Room |
| **Icon** | 🔄 |

**Description:** Restarts the current room, resetting all instances to their initial state.

**Parameters:** None

**Common uses:**
- Restart level after player dies
- Reset puzzle after failure
- Replay mini-game

---

### Go to Room
| Property | Value |
|----------|-------|
| **Action Name** | `goto_room` |
| **Block Name** | `room_goto` |
| **Category** | Room |
| **Icon** | 🚪 |

**Description:** Transitions to a specific room by name.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `room` | Room | The room to go to |

---

### If Next Room Exists
| Property | Value |
|----------|-------|
| **Action Name** | `if_next_room_exists` |
| **Block Name** | `room_if_next_exists` |
| **Category** | Room |
| **Icon** | ❓➡️ |

**Description:** Conditional block that only executes contained actions if there is a next room.

**Parameters:** None (actions are placed inside the block)

**Common uses:**
- Check before going to next room
- Show "You Win!" message if no more rooms

---

### If Previous Room Exists
| Property | Value |
|----------|-------|
| **Action Name** | `if_previous_room_exists` |
| **Block Name** | `room_if_previous_exists` |
| **Category** | Room |
| **Icon** | ❓⬅️ |

**Description:** Conditional block that only executes contained actions if there is a previous room.

**Parameters:** None (actions are placed inside the block)

---

## Output Actions

### Show Message
| Property | Value |
|----------|-------|
| **Action Name** | `show_message` |
| **Block Name** | `output_message` |
| **Category** | Output |
| **Icon** | 💬 |

**Description:** Displays a popup message dialog to the player.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | String | The text to display |

**Note:** The game pauses while the message is displayed. Player must click OK to continue.

**Common uses:**
- Game instructions
- Story dialogue
- Win/lose messages
- Debug information

---

### Execute Code
| Property | Value |
|----------|-------|
| **Action Name** | `execute_code` |
| **Block Name** | `execute_code` |
| **Category** | Output |
| **Icon** | 💻 |

**Description:** Execute custom Python code.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | String | Python code to execute |

**Note:** This is an advanced feature. Use with caution as incorrect code can cause errors.

---

## Categories Summary

| Category | Events | Actions |
|----------|--------|---------|
| **Events** | Create, Step, Keyboard Press, Collision | - |
| **Movement** | - | Set Horizontal Speed, Set Vertical Speed, Stop Movement, Jump to Position |
| **Instance** | - | Destroy Instance, Create Instance |
| **Score/Lives/Health** | - | Set Score, Add Score, Draw Score |
| **Room** | - | Next Room, Previous Room, Restart Room, Go to Room, If Next Room Exists, If Previous Room Exists |
| **Output** | - | Show Message, Execute Code |

---

## Example: Simple Coin Collector Game

Here's how to set up a basic coin collecting game using only Beginner preset features:

### Player Object (obj_player)

**Keyboard Press (Left Arrow):**
- Set Horizontal Speed: -4

**Keyboard Press (Right Arrow):**
- Set Horizontal Speed: 4

**Keyboard Press (Up Arrow):**
- Set Vertical Speed: -4

**Keyboard Press (Down Arrow):**
- Set Vertical Speed: 4

**Collision with obj_coin:**
- Set Score: 10 (relative: true)
- Destroy Instance: other

**Collision with obj_wall:**
- Stop Movement

**Collision with obj_goal:**
- Set Score: 100 (relative: true)
- Next Room

### Coin Object (obj_coin)
No events needed - just a collectible item.

### Wall Object (obj_wall)
No events needed - just a solid obstacle.

### Goal Object (obj_goal)
No events needed - triggers level complete when player collides.

---

## Upgrading to Intermediate

When you're comfortable with the Beginner preset, consider upgrading to **Intermediate** to access:
- Draw Event (for custom rendering)
- Destroy Event (cleanup when instance is destroyed)
- Mouse Events (click detection)
- Alarm Events (timed actions)
- Lives and Health systems
- Sound and Music actions
- More movement options (direction, move towards)

---

## See Also

- [Tutorials](Tutorials) - All tutorials in one place
- [Intermediate Preset](Intermediate-Preset) - Next level features
- [Full Action Reference](Full-Action-Reference) - Complete action list
- [Event Reference](Event-Reference) - Complete event list
- [Events and Actions](Events-and-Actions) - Core concepts
- [Creating Your First Game](Creating-Your-First-Game) - Step-by-step tutorial
- [Pong Tutorial](Tutorial-Pong) - Create a classic two-player Pong game
- [Breakout Tutorial](Tutorial-Breakout) - Create a classic brick breaker game
- [Introduction to Game Creation](Getting-Started-Breakout) - Comprehensive beginner tutorial

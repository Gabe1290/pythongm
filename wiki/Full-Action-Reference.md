# Full Action Reference

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

This page documents all available actions in PyGameMaker. Actions are commands that execute when events are triggered.

## Action Categories

- [Movement Actions](#movement-actions)
- [Instance Actions](#instance-actions)
- [Score, Lives & Health Actions](#score-lives--health-actions)
- [Room Actions](#room-actions)
- [Timing Actions](#timing-actions)
- [Sound Actions](#sound-actions)
- [Drawing Actions](#drawing-actions)
- [Control Flow Actions](#control-flow-actions)
- [Output Actions](#output-actions)

---

## Movement Actions

### Set Horizontal Speed
| Property | Value |
|----------|-------|
| **Name** | `set_hspeed` |
| **Icon** | ↔️ |
| **Preset** | Beginner |

**Description:** Set horizontal movement speed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 0 | Speed in pixels/frame. Positive=right, Negative=left |

---

### Set Vertical Speed
| Property | Value |
|----------|-------|
| **Name** | `set_vspeed` |
| **Icon** | ↕️ |
| **Preset** | Beginner |

**Description:** Set vertical movement speed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 0 | Speed in pixels/frame. Positive=down, Negative=up |

---

### Stop Movement
| Property | Value |
|----------|-------|
| **Name** | `stop_movement` |
| **Icon** | 🛑 |
| **Preset** | Beginner |

**Description:** Stop all movement (sets hspeed and vspeed to 0).

**Parameters:** None

---

### Jump to Position
| Property | Value |
|----------|-------|
| **Name** | `jump_to_position` |
| **Icon** | 📍 |
| **Preset** | Beginner |

**Description:** Instantly move to a specific position.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Number | 0 | Target X coordinate |
| `y` | Number | 0 | Target Y coordinate |

---

### Move Fixed
| Property | Value |
|----------|-------|
| **Name** | `move_fixed` |
| **Icon** | ➡️ |
| **Preset** | Advanced |

**Description:** Move in one of 8 fixed directions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `directions` | Choice | right | Direction(s) to move |
| `speed` | Number | 4 | Movement speed |

**Direction choices:** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Move Free
| Property | Value |
|----------|-------|
| **Name** | `move_free` |
| **Icon** | 🧭 |
| **Preset** | Advanced |

**Description:** Move in any direction (0-360 degrees).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `direction` | Number | 0 | Direction in degrees (0=right, 90=up) |
| `speed` | Number | 4 | Movement speed |

---

### Move Towards
| Property | Value |
|----------|-------|
| **Name** | `move_towards` |
| **Icon** | 🎯 |
| **Preset** | Intermediate |

**Description:** Move towards a target position.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Expression | 0 | Target X (can use expressions like `other.x`) |
| `y` | Expression | 0 | Target Y |
| `speed` | Number | 4 | Movement speed |

---

### Set Speed
| Property | Value |
|----------|-------|
| **Name** | `set_speed` |
| **Icon** | ⚡ |
| **Preset** | Advanced |

**Description:** Set movement speed magnitude (maintains direction).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `speed` | Number | 0 | Speed magnitude |

---

### Set Direction
| Property | Value |
|----------|-------|
| **Name** | `set_direction` |
| **Icon** | 🧭 |
| **Preset** | Advanced |

**Description:** Set movement direction (maintains speed).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `direction` | Number | 0 | Direction in degrees |

---

### Reverse Horizontal
| Property | Value |
|----------|-------|
| **Name** | `reverse_horizontal` |
| **Icon** | ↔️ |
| **Preset** | Advanced |

**Description:** Reverse horizontal direction (multiply hspeed by -1).

**Parameters:** None

---

### Reverse Vertical
| Property | Value |
|----------|-------|
| **Name** | `reverse_vertical` |
| **Icon** | ↕️ |
| **Preset** | Advanced |

**Description:** Reverse vertical direction (multiply vspeed by -1).

**Parameters:** None

---

### Set Gravity
| Property | Value |
|----------|-------|
| **Name** | `set_gravity` |
| **Icon** | ⬇️ |
| **Preset** | Platformer |

**Description:** Apply gravity to the instance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `direction` | Number | 270 | Gravity direction (270=down) |
| `gravity` | Number | 0.5 | Gravity strength |

---

### Set Friction
| Property | Value |
|----------|-------|
| **Name** | `set_friction` |
| **Icon** | 🛑 |
| **Preset** | Advanced |

**Description:** Apply friction (gradual slowdown).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `friction` | Number | 0.1 | Friction amount |

---

## Instance Actions

### Destroy Instance
| Property | Value |
|----------|-------|
| **Name** | `destroy_instance` |
| **Icon** | 💥 |
| **Preset** | Beginner |

**Description:** Remove an instance from the game.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | Choice | self | `self` or `other` (in collision events) |

---

### Create Instance
| Property | Value |
|----------|-------|
| **Name** | `create_instance` |
| **Icon** | ✨ |
| **Preset** | Beginner |

**Description:** Create a new instance of an object.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object` | Object | - | Object type to create |
| `x` | Number | 0 | X position |
| `y` | Number | 0 | Y position |

---

### Set Sprite
| Property | Value |
|----------|-------|
| **Name** | `set_sprite` |
| **Icon** | 🖼️ |
| **Preset** | Advanced |

**Description:** Change the instance's sprite.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sprite` | Sprite | - | New sprite |

---

## Score, Lives & Health Actions

### Set Score
| Property | Value |
|----------|-------|
| **Name** | `set_score` |
| **Icon** | 🏆 |
| **Preset** | Beginner |

**Description:** Set or modify the score.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 0 | Score value |
| `relative` | Boolean | false | If true, adds to current score |

---

### Add Score (Shortcut)
| Property | Value |
|----------|-------|
| **Name** | `add_score` |
| **Icon** | ➕🏆 |
| **Preset** | Beginner |

**Description:** Add points to the score.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 10 | Points to add (negative to subtract) |

---

### Set Lives
| Property | Value |
|----------|-------|
| **Name** | `set_lives` |
| **Icon** | ❤️ |
| **Preset** | Intermediate |

**Description:** Set or modify the lives count.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 3 | Lives value |
| `relative` | Boolean | false | If true, adds to current lives |

**Note:** Triggers `no_more_lives` event when reaching 0.

---

### Add Lives (Shortcut)
| Property | Value |
|----------|-------|
| **Name** | `add_lives` |
| **Icon** | ➕❤️ |
| **Preset** | Intermediate |

**Description:** Add or remove lives.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 1 | Lives to add (negative to subtract) |

---

### Set Health
| Property | Value |
|----------|-------|
| **Name** | `set_health` |
| **Icon** | 💚 |
| **Preset** | Intermediate |

**Description:** Set or modify health (0-100).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 100 | Health value |
| `relative` | Boolean | false | If true, adds to current health |

**Note:** Triggers `no_more_health` event when reaching 0.

---

### Add Health (Shortcut)
| Property | Value |
|----------|-------|
| **Name** | `add_health` |
| **Icon** | ➕💚 |
| **Preset** | Intermediate |

**Description:** Add or remove health.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | Number | 10 | Health to add (negative for damage) |

---

### Draw Score
| Property | Value |
|----------|-------|
| **Name** | `draw_score` |
| **Icon** | 🖼️🏆 |
| **Preset** | Beginner |

**Description:** Display the score on screen.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Number | 10 | X position |
| `y` | Number | 10 | Y position |
| `caption` | String | "Score: " | Text before score |

---

### Draw Lives
| Property | Value |
|----------|-------|
| **Name** | `draw_lives` |
| **Icon** | 🖼️❤️ |
| **Preset** | Intermediate |

**Description:** Display lives on screen.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Number | 10 | X position |
| `y` | Number | 30 | Y position |
| `sprite` | Sprite | - | Optional life icon sprite |

---

### Draw Health Bar
| Property | Value |
|----------|-------|
| **Name** | `draw_health_bar` |
| **Icon** | 📊💚 |
| **Preset** | Intermediate |

**Description:** Draw a health bar.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x1` | Number | 10 | Left X |
| `y1` | Number | 50 | Top Y |
| `x2` | Number | 110 | Right X |
| `y2` | Number | 60 | Bottom Y |
| `back_color` | Color | gray | Background color |
| `bar_color` | Color | green | Bar color |

---

## Room Actions

### Next Room
| Property | Value |
|----------|-------|
| **Name** | `next_room` |
| **Icon** | ➡️ |
| **Preset** | Beginner |

**Description:** Go to the next room in room order.

**Parameters:** None

---

### Previous Room
| Property | Value |
|----------|-------|
| **Name** | `previous_room` |
| **Icon** | ⬅️ |
| **Preset** | Beginner |

**Description:** Go to the previous room in room order.

**Parameters:** None

---

### Restart Room
| Property | Value |
|----------|-------|
| **Name** | `restart_room` |
| **Icon** | 🔄 |
| **Preset** | Beginner |

**Description:** Restart the current room.

**Parameters:** None

---

### Go to Room
| Property | Value |
|----------|-------|
| **Name** | `goto_room` |
| **Icon** | 🚪 |
| **Preset** | Beginner |

**Description:** Go to a specific room.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `room` | Room | - | Target room |

---

### If Next Room Exists
| Property | Value |
|----------|-------|
| **Name** | `if_next_room_exists` |
| **Icon** | ❓➡️ |
| **Preset** | Beginner |

**Description:** Conditional - execute actions only if there is a next room.

| Parameter | Type | Description |
|-----------|------|-------------|
| `then_actions` | Action List | Actions if next room exists |
| `else_actions` | Action List | Actions if no next room |

---

### If Previous Room Exists
| Property | Value |
|----------|-------|
| **Name** | `if_previous_room_exists` |
| **Icon** | ❓⬅️ |
| **Preset** | Beginner |

**Description:** Conditional - execute actions only if there is a previous room.

| Parameter | Type | Description |
|-----------|------|-------------|
| `then_actions` | Action List | Actions if previous room exists |
| `else_actions` | Action List | Actions if no previous room |

---

## Timing Actions

### Set Alarm
| Property | Value |
|----------|-------|
| **Name** | `set_alarm` |
| **Icon** | ⏰ |
| **Preset** | Intermediate |

**Description:** Set an alarm to trigger after a delay.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alarm` | Number | 0 | Alarm number (0-11) |
| `steps` | Number | 60 | Steps until alarm fires |

**Note:** At 60 FPS, 60 steps = 1 second.

---

## Sound Actions

### Play Sound
| Property | Value |
|----------|-------|
| **Name** | `play_sound` |
| **Icon** | 🔊 |
| **Preset** | Intermediate |

**Description:** Play a sound effect.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sound` | Sound | - | Sound resource |
| `loop` | Boolean | false | Loop the sound |

---

### Play Music
| Property | Value |
|----------|-------|
| **Name** | `play_music` |
| **Icon** | 🎵 |
| **Preset** | Intermediate |

**Description:** Play background music.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sound` | Sound | - | Music resource |
| `loop` | Boolean | true | Loop the music |

---

### Stop Music
| Property | Value |
|----------|-------|
| **Name** | `stop_music` |
| **Icon** | 🔇 |
| **Preset** | Intermediate |

**Description:** Stop all playing music.

**Parameters:** None

---

### Set Volume
| Property | Value |
|----------|-------|
| **Name** | `set_volume` |
| **Icon** | 🔉 |
| **Preset** | Advanced |

**Description:** Set the audio volume.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `volume` | Number | 1.0 | Volume level (0.0 to 1.0) |

---

## Drawing Actions

### Draw Text
| Property | Value |
|----------|-------|
| **Name** | `draw_text` |
| **Icon** | 📝 |
| **Preset** | Advanced |

**Description:** Draw text on screen.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Number | 0 | X position |
| `y` | Number | 0 | Y position |
| `text` | String | "" | Text to draw |
| `color` | Color | white | Text color |

---

### Draw Rectangle
| Property | Value |
|----------|-------|
| **Name** | `draw_rectangle` |
| **Icon** | ⬛ |
| **Preset** | Advanced |

**Description:** Draw a rectangle.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x1` | Number | 0 | Left X |
| `y1` | Number | 0 | Top Y |
| `x2` | Number | 32 | Right X |
| `y2` | Number | 32 | Bottom Y |
| `color` | Color | white | Fill color |
| `outline` | Boolean | false | Outline only |

---

### Draw Circle
| Property | Value |
|----------|-------|
| **Name** | `draw_circle` |
| **Icon** | ⚪ |
| **Preset** | Advanced |

**Description:** Draw a circle.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Number | 0 | Center X |
| `y` | Number | 0 | Center Y |
| `radius` | Number | 16 | Radius |
| `color` | Color | white | Fill color |
| `outline` | Boolean | false | Outline only |

---

### Set Alpha
| Property | Value |
|----------|-------|
| **Name** | `set_alpha` |
| **Icon** | 👻 |
| **Preset** | Advanced |

**Description:** Set drawing transparency.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alpha` | Number | 1.0 | Transparency (0.0=invisible, 1.0=opaque) |

---

## Control Flow Actions

### If Collision At
| Property | Value |
|----------|-------|
| **Name** | `if_collision_at` |
| **Icon** | 🎯 |
| **Preset** | Advanced |

**Description:** Check for collision at a position.

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | Expression | X position to check |
| `y` | Expression | Y position to check |
| `object_type` | Choice | `any` or `solid` |
| `then_actions` | Action List | If collision found |
| `else_actions` | Action List | If no collision |

---

## Output Actions

### Show Message
| Property | Value |
|----------|-------|
| **Name** | `show_message` |
| **Icon** | 💬 |
| **Preset** | Beginner |

**Description:** Display a popup message.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | String | "Hello!" | Message text |

**Note:** Game pauses while message is displayed.

---

### Execute Code
| Property | Value |
|----------|-------|
| **Name** | `execute_code` |
| **Icon** | 💻 |
| **Preset** | Beginner |

**Description:** Run custom Python code.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | Code | "" | Python code to execute |

**Warning:** Advanced feature. Use with caution.

---

### End Game
| Property | Value |
|----------|-------|
| **Name** | `end_game` |
| **Icon** | 🚪 |
| **Preset** | Advanced |

**Description:** End the game and close the window.

**Parameters:** None

---

### Restart Game
| Property | Value |
|----------|-------|
| **Name** | `restart_game` |
| **Icon** | 🔄 |
| **Preset** | Advanced |

**Description:** Restart the game from the first room.

**Parameters:** None

---

## Actions by Preset

| Preset | Action Count | Categories |
|--------|-------------|------------|
| **Beginner** | 17 | Movement, Instance, Score, Room, Output |
| **Intermediate** | 29 | + Lives, Health, Sound, Timing |
| **Advanced** | 40+ | + Drawing, Control Flow, Game |

---

## See Also

- [Event Reference](Event-Reference) - Complete event list
- [Beginner Preset](Beginner-Preset) - Essential actions for beginners
- [Intermediate Preset](Intermediate-Preset) - Additional actions
- [Events and Actions](Events-and-Actions) - Core concepts overview

# Full Action Reference

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

This page lists all **109** actions available in PyGameMaker, exactly as they appear in the IDE's action picker (including the Audio plugin and the 3D View extension). Actions are commands that run when an event fires.

## Categories

- [Movement](#movement) (20)
- [Instance](#instance) (12)
- [Score](#score) (11)
- [Room](#room) (9)
- [Timing](#timing) (2)
- [Audio](#audio) (6)
- [Game](#game) (20)
- [Control](#control) (19)
- [Grid](#grid) (4)
- [Views](#views) (2)
- [3D View](#3d-view) (4)

---

<a id="movement"></a>
## Movement

### Bounce

| Property | Value |
|----------|-------|
| **Name** | `bounce` |
| **Category** | Movement |

Bounce off solid objects

*Parameters:* none

### Jump To Position

| Property | Value |
|----------|-------|
| **Name** | `jump_to_position` |
| **Icon** | 📍 |
| **Category** | Movement |

Move instantly to a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `relative` | Yes/No | No | Add to current position instead of setting absolute |

### Jump to Random Position

| Property | Value |
|----------|-------|
| **Name** | `jump_to_random` |
| **Icon** | 🎲↪️ |
| **Category** | Movement |

Teleport to a random position (optionally grid-snapped)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `snap_h` | Number | `1` | Horizontal grid snap (1 = no snap) |
| `snap_v` | Number | `1` | Vertical grid snap (1 = no snap) |

### Jump to Start Position

| Property | Value |
|----------|-------|
| **Name** | `jump_to_start` |
| **Icon** | ↩️ |
| **Category** | Movement |

Move the instance back to its creation position

*Parameters:* none

### Move Free

| Property | Value |
|----------|-------|
| **Name** | `move_free` |
| **Icon** | 🧭 |
| **Category** | Movement |

Move in a precise direction (0-360 degrees)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Number | `0` | Direction in degrees (0=right, 90=up, counter-clockwise) |
| `speed` | Number | `4.0` | Movement speed |

### Move Grid

| Property | Value |
|----------|-------|
| **Name** | `move_grid` |
| **Icon** | ▦ |
| **Category** | Movement |

Move one grid unit in the specified direction

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Choice | `right` | Direction to move; Choices: `left`, `right`, `up`, `down` |
| `grid_size` | Number | `32` | Size of grid unit in pixels |

### Move Towards Point

| Property | Value |
|----------|-------|
| **Name** | `move_towards_point` |
| **Icon** | 🎯 |
| **Category** | Movement |

Move towards a point at a given speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Target X |
| `y` | Number | `0` | Target Y |
| `speed` | Number | `4.0` | Movement speed |

### Move to Contact

| Property | Value |
|----------|-------|
| **Name** | `move_to_contact` |
| **Icon** | 🎯 |
| **Category** | Movement |

Move in a direction until touching an object (or max distance)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Text | `direction` | Direction in degrees (0=right, 90=up, 180=left, 270=down), or an expression. Defaults to 'direction' = the instance's current heading (collision snap). |
| `max_distance` | Number | `1000` | Maximum distance to move, in pixels |
| `object` | Object | `all` | Stop on contact with: 'all' instances, 'solid' objects only, or a specific object name.; Choices: `all`, `solid`; optional |

### Reverse Horizontal

| Property | Value |
|----------|-------|
| **Name** | `reverse_horizontal` |
| **Icon** | ↔️ |
| **Category** | Movement |

Reverse horizontal movement direction

*Parameters:* none

### Reverse Vertical

| Property | Value |
|----------|-------|
| **Name** | `reverse_vertical` |
| **Icon** | ↕️ |
| **Category** | Movement |

Reverse vertical movement direction

*Parameters:* none

### Set Direction

| Property | Value |
|----------|-------|
| **Name** | `set_direction` |
| **Icon** | 🧭 |
| **Category** | Movement |

Set movement direction

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Number | `0` | Direction in degrees (0=right, 90=up) |

### Set Direction & Speed

| Property | Value |
|----------|-------|
| **Name** | `set_direction_speed` |
| **Icon** | 🧭 |
| **Category** | Movement |

Set the instance's direction (degrees) and speed magnitude

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Number | `0` | Direction in degrees (0=right, 90=up) |
| `speed` | Number | `4.0` | Speed in pixels per frame |

### Set Friction

| Property | Value |
|----------|-------|
| **Name** | `set_friction` |
| **Icon** | 🛑 |
| **Category** | Movement |

Set friction (deceleration)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `friction` | Number | `0.1` | Friction amount (subtracted from speed each step) |

### Set Gravity

| Property | Value |
|----------|-------|
| **Name** | `set_gravity` |
| **Icon** | ⬇️ |
| **Category** | Movement |

Set gravity direction and strength

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Number | `270` | Gravity direction in degrees (270=down) |
| `gravity` | Number | `0.5` | Gravity strength (added each step) |

### Set Horizontal Speed

| Property | Value |
|----------|-------|
| **Name** | `set_hspeed` |
| **Icon** | ↔️ |
| **Category** | Movement |

Set horizontal movement speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `0` | Speed in pixels per frame |

### Set Speed

| Property | Value |
|----------|-------|
| **Name** | `set_speed` |
| **Icon** | ⚡ |
| **Category** | Movement |

Set movement speed (magnitude)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `0` | Movement speed |

### Set Vertical Speed

| Property | Value |
|----------|-------|
| **Name** | `set_vspeed` |
| **Icon** | ↕️ |
| **Category** | Movement |

Set vertical movement speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `0` | Speed in pixels per frame |

### Start Moving (Direction)

| Property | Value |
|----------|-------|
| **Name** | `start_moving_direction` |
| **Icon** | ➡️ |
| **Category** | Movement |

Begin moving in a direction at a given speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `directions` | Multiple choice | right | Direction(s) to move — check one, or several to pick a random one each step. The centre cell is stop.; Choices: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Text | — | Alternative: free expression evaluated as degrees; optional |
| `speed` | Number | `4.0` | Speed in pixels per frame |

### Stop Movement

| Property | Value |
|----------|-------|
| **Name** | `stop_movement` |
| **Icon** | 🛑 |
| **Category** | Movement |

Set both speeds to zero

*Parameters:* none

### Wrap Around Room

| Property | Value |
|----------|-------|
| **Name** | `wrap_around_room` |
| **Icon** | 🔄 |
| **Category** | Movement |

Wrap to opposite side of the room

*Parameters:* none

---

<a id="instance"></a>
## Instance

### Change Instance

| Property | Value |
|----------|-------|
| **Name** | `change_instance` |
| **Icon** | 🔄 |
| **Category** | Instance |
| **Applies to** | self / other / object |

Transform into different object type

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | New object type |
| `perform_events` | Yes/No | Yes | Execute destroy/create events |

### Create Instance

| Property | Value |
|----------|-------|
| **Name** | `create_instance` |
| **Icon** | ✨ |
| **Category** | Instance |

Create a new instance

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | Object to create |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `relative` | Yes/No | No | Position relative to current instance |

### Create Moving Instance

| Property | Value |
|----------|-------|
| **Name** | `create_moving_instance` |
| **Icon** | ✨➡️ |
| **Category** | Instance |

Create an instance and start it moving in a direction

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | Object to create |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `speed` | Number | `0` | Initial speed magnitude |
| `direction` | Number | `0` | Initial direction in degrees |

### Create Random Instance

| Property | Value |
|----------|-------|
| **Name** | `create_random_instance` |
| **Icon** | 🎲 |
| **Category** | Instance |

Create one of several object types chosen at random

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `object1` | Object | — | First candidate object; optional |
| `object2` | Object | — | Second candidate object; optional |
| `object3` | Object | — | Third candidate object; optional |
| `object4` | Object | — | Fourth candidate object; optional |

### Destroy Instance

| Property | Value |
|----------|-------|
| **Name** | `destroy_instance` |
| **Icon** | 💥 |
| **Category** | Instance |
| **Applies to** | self / other / object |

Destroy an instance

*Parameters:* none

### Destroy at Position

| Property | Value |
|----------|-------|
| **Name** | `destroy_at_position` |
| **Icon** | 💣 |
| **Category** | Instance |

Destroy instances within radius of (x, y)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | `all` | Which object type to destroy. 'all' destroys every instance in range; 'solid' only solid ones (e.g. walls); 'non-solid' everything except solids.; Choices: `all`, `solid`, `non-solid` |
| `x` | Text | `self.x` | X position (expression OK, e.g. self.x) |
| `y` | Text | `self.y` | Y position (expression OK, e.g. self.y) |
| `relative` | Yes/No | No | Treat X/Y as offsets from this instance's position instead of absolute coordinates; optional |
| `radius` | Number | `32` | Pixel radius around (x, y). Default 32 = ~one grid cell. |

### Set Image Index

| Property | Value |
|----------|-------|
| **Name** | `set_image_index` |
| **Icon** | 🖼️ |
| **Category** | Instance |

Set the current animation frame of the instance's sprite

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `frame` | Number | `0` | Frame index |

### Set Image Speed

| Property | Value |
|----------|-------|
| **Name** | `set_image_speed` |
| **Icon** | ⏩ |
| **Category** | Instance |

Set the animation playback speed of the instance's sprite

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `1.0` | Frames advanced per step (0 = paused) |

### Set Sprite

| Property | Value |
|----------|-------|
| **Name** | `set_sprite` |
| **Icon** | 🖼️ |
| **Category** | Instance |

Change an instance's sprite and/or animation frame/speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite to use (or '<self>' to keep current) |
| `subimage` | Number | `-1` | Frame index to set; -1 to leave unchanged |
| `speed` | Number | `-1` | Animation speed; -1 to leave unchanged |

### Start Animation

| Property | Value |
|----------|-------|
| **Name** | `start_animation` |
| **Icon** | ▶️ |
| **Category** | Instance |

Resume the instance's sprite animation (image_speed = 1)

*Parameters:* none

### Stop Animation

| Property | Value |
|----------|-------|
| **Name** | `stop_animation` |
| **Icon** | ⏸️ |
| **Category** | Instance |

Pause the instance's sprite animation (image_speed = 0)

*Parameters:* none

### Test Instance Count

| Property | Value |
|----------|-------|
| **Name** | `test_instance_count` |
| **Icon** | ❓🔢 |
| **Category** | Instance |

Conditional: compare the number of instances of an object

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | Object to count |
| `number` | Number | `0` | Value to compare against |
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Score

### Clear High-Score Table

| Property | Value |
|----------|-------|
| **Name** | `clear_highscore` |
| **Icon** | 🗑️🏆 |
| **Category** | Score |

Clear all high-score entries

*Parameters:* none

### Draw Health Bar

| Property | Value |
|----------|-------|
| **Name** | `draw_health_bar` |
| **Icon** | 🩺 |
| **Category** | Score |

Draw the current health as a two-colour bar

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Left X |
| `y1` | Number | `0` | Top Y |
| `x2` | Number | `100` | Right X |
| `y2` | Number | `20` | Bottom Y |
| `back_color` | Color | `#FF0000` | Background (empty) colour |
| `bar_color` | Color | `#00FF00` | Filled (health) colour |

### Draw Lives

| Property | Value |
|----------|-------|
| **Name** | `draw_lives` |
| **Icon** | 🖍️❤️ |
| **Category** | Score |

Draw the current life count as repeated sprite images

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `sprite` | Sprite | — | Sprite drawn once per remaining life; optional |
| `scale` | Number | `1.0` | Uniform scale factor for the life icon (1.0 = native size); optional |
| `relative` | Yes/No | No | Draw relative to this instance's position instead of absolute screen coordinates; optional |

### Draw Score

| Property | Value |
|----------|-------|
| **Name** | `draw_score` |
| **Icon** | 🖍️🏆 |
| **Category** | Score |

Draw the current score on screen

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `caption` | Text | `Score: ` | Text shown before the score value; optional |
| `relative` | Yes/No | No | Draw relative to this instance's position instead of absolute screen coordinates; optional |

### Set Health

| Property | Value |
|----------|-------|
| **Name** | `set_health` |
| **Icon** | 💚 |
| **Category** | Score |

Set the health, or add to it with Relative

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Number | `100` | Health value (0-100) |
| `relative` | Yes/No | No | Add to the current health instead of replacing it |

### Set Lives

| Property | Value |
|----------|-------|
| **Name** | `set_lives` |
| **Icon** | ❤️ |
| **Category** | Score |

Set the lives, or add to them with Relative

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Number | `3` | Number of lives |
| `relative` | Yes/No | No | Add to the current lives instead of replacing them |

### Set Score

| Property | Value |
|----------|-------|
| **Name** | `set_score` |
| **Icon** | 🏆 |
| **Category** | Score |

Set the score, or add to it with Relative

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Number | `0` | Score value to set |
| `relative` | Yes/No | No | Add to the current score instead of replacing it |

### Show High-Score Table

| Property | Value |
|----------|-------|
| **Name** | `show_highscore` |
| **Icon** | 🏆 |
| **Category** | Score |

Display the high-score table dialog

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `background` | Color | `#FFFFDD` | Dialog background colour; optional |
| `new_color` | Color | `#FF0000` | Colour used for the new (qualifying) entry; optional |
| `other_color` | Color | `#000000` | Colour used for the other entries; optional |
| `allow_new_entry` | Yes/No | Yes | Prompt for name if the current score qualifies |

### Test Health

| Property | Value |
|----------|-------|
| **Name** | `test_health` |
| **Icon** | ❓💚 |
| **Category** | Score |

Conditional: compare current health against a value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Number | `0` | Value to compare against |

### Test Lives

| Property | Value |
|----------|-------|
| **Name** | `test_lives` |
| **Icon** | ❓❤️ |
| **Category** | Score |

Conditional: compare the life count against a value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Number | `0` | Value to compare against |
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Test Score

| Property | Value |
|----------|-------|
| **Name** | `test_score` |
| **Icon** | ❓🏆 |
| **Category** | Score |

Conditional: compare the score against a value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Number | `0` | Value to compare against |
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Room

### Check Room

| Property | Value |
|----------|-------|
| **Name** | `check_room` |
| **Icon** | ❓🚪 |
| **Category** | Room |

Conditional: true if the current room matches

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `room` | Room | — | Room to compare against |
| `not_flag` | Yes/No | No | Invert the result; optional |

### End Game

| Property | Value |
|----------|-------|
| **Name** | `game_end` |
| **Icon** | 🛑🎮 |
| **Category** | Room |

End the game

*Parameters:* none

### Go to Room

| Property | Value |
|----------|-------|
| **Name** | `goto_room` |
| **Icon** | 🚪 |
| **Category** | Room |

Switch to a specific room

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `room` | Room | — | Target room name |
| `transition` | Choice | `none` | Transition effect (currently accepted but not rendered); Choices: `none`; optional |

### If Next Room Exists

| Property | Value |
|----------|-------|
| **Name** | `if_next_room_exists` |
| **Icon** | ❓➡️ |
| **Category** | Room |

Check if there is a next room after the current one

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `then_actions` | Action list | — | Actions if next room exists |
| `else_actions` | Action list | — | Actions if next room does not exist |

### If Previous Room Exists

| Property | Value |
|----------|-------|
| **Name** | `if_previous_room_exists` |
| **Icon** | ❓⬅️ |
| **Category** | Room |

Check if there is a previous room before the current one

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `then_actions` | Action list | — | Actions if previous room exists |
| `else_actions` | Action list | — | Actions if previous room does not exist |

### Next Room

| Property | Value |
|----------|-------|
| **Name** | `next_room` |
| **Icon** | ➡️ |
| **Category** | Room |

Go to next room

*Parameters:* none

### Previous Room

| Property | Value |
|----------|-------|
| **Name** | `previous_room` |
| **Icon** | ⬅️ |
| **Category** | Room |

Go to previous room

*Parameters:* none

### Restart Room

| Property | Value |
|----------|-------|
| **Name** | `restart_room` |
| **Icon** | 🔄 |
| **Category** | Room |

Restart current room

*Parameters:* none

### Set Room Caption

| Property | Value |
|----------|-------|
| **Name** | `set_room_caption` |
| **Icon** | 🏷️ |
| **Category** | Room |

Set the game window's title caption

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `caption` | Text | — | Window title text |

---

<a id="timing"></a>
## Timing

### Set Alarm

| Property | Value |
|----------|-------|
| **Name** | `set_alarm` |
| **Icon** | ⏰ |
| **Category** | Timing |

Set an alarm clock

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `alarm_number` | Number | `0` | Which alarm (0-11) |
| `steps` | Number | `30` | Number of steps until alarm triggers (30 = 0.5 sec at 60 FPS) |

### Sleep

| Property | Value |
|----------|-------|
| **Name** | `sleep` |
| **Icon** | 💤 |
| **Category** | Timing |

Pause the game for a number of milliseconds, then continue. Sounds keep playing during the pause (e.g. let a sound finish before changing rooms). Note: rendering and input are frozen while sleeping, so keep durations short

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `milliseconds` | Number | `1000` | How long to pause, in milliseconds (1000 = 1 second) |

---

<a id="audio"></a>
## Audio

### Check Sound Playing

| Property | Value |
|----------|-------|
| **Name** | `check_sound` |
| **Icon** | ❓🔊 |
| **Category** | Audio |

Conditional: true if the given sound is currently playing

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sound` | Sound | — | Sound to check |
| `not_flag` | Yes/No | No | Invert the result; optional |

### Play Music

| Property | Value |
|----------|-------|
| **Name** | `play_music` |
| **Icon** | 🎵 |
| **Category** | Audio |

Play background music (looping)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `music` | Sound | — | Music file to play |
| `loop` | Yes/No | Yes | Loop the music |
| `volume` | Number | `0.7` | Volume (0.0 to 1.0) |

### Play Sound

| Property | Value |
|----------|-------|
| **Name** | `play_sound` |
| **Icon** | 🔊 |
| **Category** | Audio |

Play a sound effect once

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sound` | Sound | — | Sound to play |
| `volume` | Number | `1.0` | Volume (0.0 to 1.0) |

### Set Volume

| Property | Value |
|----------|-------|
| **Name** | `set_volume` |
| **Icon** | 🔉 |
| **Category** | Audio |

Set global sound/music volume

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `volume` | Number | `1.0` | Volume (0.0 to 1.0) |

### Stop Music

| Property | Value |
|----------|-------|
| **Name** | `stop_music` |
| **Icon** | 🔇 |
| **Category** | Audio |

Stop background music

*Parameters:* none

### Stop Sound

| Property | Value |
|----------|-------|
| **Name** | `stop_sound` |
| **Icon** | 🔇 |
| **Category** | Audio |

Stop a playing sound

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sound` | Sound | — | Sound to stop |

---

<a id="game"></a>
## Game

### Draw Arrow

| Property | Value |
|----------|-------|
| **Name** | `draw_arrow` |
| **Icon** | ➡️ |
| **Category** | Game |

Draw an arrow from one point to another

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Start X |
| `y1` | Number | `0` | Start Y |
| `x2` | Number | `100` | Tip X |
| `y2` | Number | `100` | Tip Y |
| `tip_size` | Number | `10` | Arrowhead size in pixels |

### Draw Background

| Property | Value |
|----------|-------|
| **Name** | `draw_background` |
| **Icon** | 🌄 |
| **Category** | Game |

Draw a background image, optionally tiled across the screen

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `background` | Text | — | Background asset name |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `tiled` | Yes/No | No | Tile across the screen; optional |

### Draw Circle

| Property | Value |
|----------|-------|
| **Name** | `draw_circle` |
| **Icon** | ⭕ |
| **Category** | Game |

Draw a filled or outlined circle

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Centre X |
| `y` | Number | `0` | Centre Y |
| `radius` | Number | `50` | Circle radius |
| `filled` | Yes/No | Yes | Filled, or outline only; optional |

### Draw Ellipse

| Property | Value |
|----------|-------|
| **Name** | `draw_ellipse` |
| **Icon** | 🥚 |
| **Category** | Game |

Draw a filled or outlined ellipse within a bounding box

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Left X |
| `y1` | Number | `0` | Top Y |
| `x2` | Number | `100` | Right X |
| `y2` | Number | `100` | Bottom Y |
| `filled` | Yes/No | Yes | Filled, or outline only; optional |

### Draw Line

| Property | Value |
|----------|-------|
| **Name** | `draw_line` |
| **Icon** | 📏 |
| **Category** | Game |

Draw a line between two points

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Start X |
| `y1` | Number | `0` | Start Y |
| `x2` | Number | `100` | End X |
| `y2` | Number | `100` | End Y |

### Draw Rectangle

| Property | Value |
|----------|-------|
| **Name** | `draw_rectangle` |
| **Icon** | 🟥 |
| **Category** | Game |

Draw a filled or outlined rectangle

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Left X |
| `y1` | Number | `0` | Top Y |
| `x2` | Number | `100` | Right X |
| `y2` | Number | `100` | Bottom Y |
| `filled` | Yes/No | Yes | Filled, or outline only; optional |

### Draw Scaled Text

| Property | Value |
|----------|-------|
| **Name** | `draw_scaled_text` |
| **Icon** | 🖍️ |
| **Category** | Game |

Draw text at an arbitrary scale

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Text to draw |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `xscale` | Number | `1.0` | Horizontal scale factor |
| `yscale` | Number | `1.0` | Vertical scale factor |

### Draw Sprite

| Property | Value |
|----------|-------|
| **Name** | `draw_sprite` |
| **Icon** | 🖼️ |
| **Category** | Game |

Draw a sprite frame at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `subimage` | Number | `0` | Frame index to draw |

### Draw Text

| Property | Value |
|----------|-------|
| **Name** | `draw_text` |
| **Icon** | 🖍️ |
| **Category** | Game |

Draw a text string at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Text to draw (supports expressions) |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `relative` | Yes/No | No | Draw relative to this instance's position instead of absolute screen coordinates; optional |

### Draw Variable

| Property | Value |
|----------|-------|
| **Name** | `draw_variable` |
| **Icon** | 🔢 |
| **Category** | Game |

Draw the value of a variable on screen

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `variable` | Text | — | Variable name (self.var, global.var, or bare name) |

### Fill Screen Color

| Property | Value |
|----------|-------|
| **Name** | `fill_color` |
| **Icon** | 🪣 |
| **Category** | Game |

Fill the entire viewport with a solid colour

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | RGB hex colour |

### Open Webpage

| Property | Value |
|----------|-------|
| **Name** | `open_webpage` |
| **Icon** | 🌐 |
| **Category** | Game |

Open a URL in the default browser

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `url` | Text | — | Web address to open |

### Restart Game

| Property | Value |
|----------|-------|
| **Name** | `restart_game` |
| **Icon** | 🔁🎮 |
| **Category** | Game |

Restart the game from the start room

*Parameters:* none

### Set Alpha

| Property | Value |
|----------|-------|
| **Name** | `set_alpha` |
| **Icon** | 🌫️ |
| **Category** | Game |

Set the drawing transparency for subsequent draws

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `alpha` | Number | `1.0` | Opacity 0.0 (clear) to 1.0 (opaque) |

### Set Color

| Property | Value |
|----------|-------|
| **Name** | `set_color` |
| **Icon** | 🎨 |
| **Category** | Game |

Set the draw colour and alpha for subsequent draws

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#FFFFFF` | RGB hex colour |
| `alpha` | Number | `1.0` | Opacity 0.0–1.0; optional |

### Set Draw Color

| Property | Value |
|----------|-------|
| **Name** | `set_draw_color` |
| **Icon** | 🎨 |
| **Category** | Game |

Set the colour used by subsequent draw_* actions

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | RGB hex colour |

### Set Draw Font

| Property | Value |
|----------|-------|
| **Name** | `set_draw_font` |
| **Icon** | 🔤 |
| **Category** | Game |

Set the font and alignment for subsequent text drawing

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `font` | Text | — | Font asset name (blank = default font); optional |
| `halign` | Choice | `left` | Horizontal text alignment; Choices: `left`, `center`, `right` |
| `valign` | Choice | `top` | Vertical text alignment; Choices: `top`, `middle`, `bottom` |

### Set Window Caption

| Property | Value |
|----------|-------|
| **Name** | `set_window_caption` |
| **Icon** | 🪟 |
| **Category** | Game |

Configure score/lives/health display in window title

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `show_score` | Yes/No | Yes | Append the current score to the window caption |
| `show_lives` | Yes/No | Yes | Append the current lives count to the window caption |
| `show_health` | Yes/No | No | Append the current health value to the window caption |
| `caption` | Text | — | Optional caption prefix shown before the counters; optional |

### Show Game Info

| Property | Value |
|----------|-------|
| **Name** | `show_info` |
| **Icon** | ℹ️ |
| **Category** | Game |

Display the game information screen

*Parameters:* none

### Show Message

| Property | Value |
|----------|-------|
| **Name** | `show_message` |
| **Icon** | 💬 |
| **Category** | Game |

Display a message

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `message` | Text | `Hello!` | Message text |

---

<a id="control"></a>
## Control

### Check Empty

| Property | Value |
|----------|-------|
| **Name** | `check_empty` |
| **Icon** | 🔍 |
| **Category** | Control |

True when (x, y) is collision-free. Use with start_block/end_block to gate the following action(s), GM-style

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Text | `self.x` | X position to check (expression OK, e.g. self.x + 32) |
| `y` | Text | `self.y` | Y position to check (expression OK, e.g. self.y + 32) |
| `relative` | Yes/No | No | Treat X/Y as offsets from this instance's position instead of absolute coordinates; optional |
| `objects` | Choice | `solid` | Which instances count as occupying the position; Choices: `solid`, `all` |

### Comment

| Property | Value |
|----------|-------|
| **Name** | `comment` |
| **Icon** | ⚠️ |
| **Category** | Control |

A comment in the action list (no runtime effect)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Free-form comment text; optional |

### Else

| Property | Value |
|----------|-------|
| **Name** | `else_action` |
| **Icon** | ⚡ |
| **Category** | Control |

Marks the else branch of a conditional

*Parameters:* none

### End Block

| Property | Value |
|----------|-------|
| **Name** | `end_block` |
| **Icon** | 📁 |
| **Category** | Control |

End a block of actions

*Parameters:* none

### Execute Code

| Property | Value |
|----------|-------|
| **Name** | `execute_code` |
| **Icon** | 📜 |
| **Category** | Control |

Run an inline block of Python code

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `code` | Code | — | Python source to evaluate against the instance |

### Execute Script

| Property | Value |
|----------|-------|
| **Name** | `execute_script` |
| **Icon** | 📜 |
| **Category** | Control |

Run one of the project's script assets

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `script` | Script | — | Name of the project script to run |
| `arg0` | Text | — | Available in the script as argument0; optional |
| `arg1` | Text | — | Available in the script as argument1; optional |
| `arg2` | Text | — | Available in the script as argument2; optional |
| `arg3` | Text | — | Available in the script as argument3; optional |
| `arg4` | Text | — | Available in the script as argument4; optional |

### Exit Event

| Property | Value |
|----------|-------|
| **Name** | `exit_event` |
| **Icon** | 🚪 |
| **Category** | Control |

Stop executing remaining actions in this event

*Parameters:* none

### If Can Push

| Property | Value |
|----------|-------|
| **Name** | `if_can_push` |
| **Icon** | 📦 |
| **Category** | Control |

Check if a box/object can be pushed in the current direction (Sokoban-style)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Choice | `facing` | Direction to check for push; Choices: `facing` |
| `object_type` | Text | `box` | Type of object being pushed |
| `then_action` | Choice | `push_and_move` | Action if push is possible; Choices: `push_and_move`, `none` |
| `else_action` | Choice | `stop_movement` | Action if push is blocked; Choices: `stop_movement`, `none` |

### If Collision

| Property | Value |
|----------|-------|
| **Name** | `if_collision` |
| **Icon** | ❓💥 |
| **Category** | Control |

Conditional: true if the instance would collide at offset (x, y)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Horizontal offset to test |
| `y` | Number | `0` | Vertical offset to test |
| `object` | Text | `any` | 'any', 'solid', or an object name; Choices: `any`, `solid`; optional |
| `not_flag` | Yes/No | No | Negate the result; optional |

### If Collision At

| Property | Value |
|----------|-------|
| **Name** | `if_collision_at` |
| **Icon** | 🎯 |
| **Category** | Control |

Check for collision at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Text | `self.x + 32` | X position expression |
| `y` | Text | `self.y` | Y position expression |
| `object_type` | Choice | `any` | Object type to check; Choices: `any`, `solid` |
| `then_actions` | Action list | — | Actions if collision found |
| `else_actions` | Action list | — | Actions if no collision |

### If Condition

| Property | Value |
|----------|-------|
| **Name** | `if_condition` |
| **Icon** | ❓ |
| **Category** | Control |

Conditional check with then/else actions

*Parameters:* none

### If Object Exists

| Property | Value |
|----------|-------|
| **Name** | `if_object_exists` |
| **Icon** | ❓ |
| **Category** | Control |

Conditional: true if at least one instance of object exists

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | Object type to check |
| `not_flag` | Yes/No | No | Negate the result (act when the object does NOT exist); optional |

### Repeat

| Property | Value |
|----------|-------|
| **Name** | `repeat` |
| **Icon** | 🔁 |
| **Category** | Control |

Repeat next action/block N times

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `times` | Number | `10` | Number of times to repeat |
| `actions` | Action list | — | Actions to repeat |

### Set Variable

| Property | Value |
|----------|-------|
| **Name** | `set_variable` |
| **Icon** | 📝 |
| **Category** | Control |

Set an instance or global variable

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `variable` | Text | — | Variable name |
| `value` | Text | `0` | Value (number, string, or expression) |
| `scope` | Choice | `self` | Variable scope; Choices: `self`, `other`, `global` |
| `relative` | Yes/No | No | Add to current value instead of replacing |

### Start Block

| Property | Value |
|----------|-------|
| **Name** | `start_block` |
| **Icon** | 📂 |
| **Category** | Control |

Start a block of actions (for grouping)

*Parameters:* none

### Test Chance

| Property | Value |
|----------|-------|
| **Name** | `test_chance` |
| **Icon** | 🎲❓ |
| **Category** | Control |

Conditional: true with probability 1 in 'sides'

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sides` | Number | `6` | A 1-in-N chance of being true |

### Test Expression

| Property | Value |
|----------|-------|
| **Name** | `test_expression` |
| **Icon** | ❓ |
| **Category** | Control |

Test if an expression is true

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `expression` | Text | — | Expression to evaluate (true if >= 0.5) |
| `then_actions` | Action list | — | Actions if true |
| `else_actions` | Action list | — | Actions if false |

### Test Question

| Property | Value |
|----------|-------|
| **Name** | `test_question` |
| **Icon** | ❓💬 |
| **Category** | Control |

Conditional: show a yes/no dialog; true if the user answers yes

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `question` | Text | `Continue?` | Question shown to the player |

### Test Variable

| Property | Value |
|----------|-------|
| **Name** | `test_variable` |
| **Icon** | ❓ |
| **Category** | Control |

Test an instance or global variable value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `variable` | Text | — | Variable name |
| `value` | Text | `0` | Value to compare |
| `scope` | Choice | `self` | Variable scope; Choices: `self`, `other`, `global` |
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Grid

### If On Grid

| Property | Value |
|----------|-------|
| **Name** | `if_on_grid` |
| **Icon** | ▦ |
| **Category** | Grid |

Check if object is aligned to grid

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `grid_size` | Number | `32` | Grid cell size in pixels |
| `then_actions` | Action list | — | Actions if on grid |
| `else_actions` | Action list | — | Actions if not on grid |

### Snap to Grid

| Property | Value |
|----------|-------|
| **Name** | `snap_to_grid` |
| **Icon** | ▦ |
| **Category** | Grid |

Align instance position to grid

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `grid_size` | Number | `32` | Grid cell size in pixels |

### Stop If No Keys Pressed

| Property | Value |
|----------|-------|
| **Name** | `stop_if_no_keys` |
| **Icon** | ▦ |
| **Category** | Grid |

Stop movement on grid when no movement keys are pressed (perfect for smooth grid snapping)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `grid_size` | Number | `32` | Grid cell size in pixels |

### Test Grid Alignment

| Property | Value |
|----------|-------|
| **Name** | `test_alignment` |
| **Icon** | ❓▦ |
| **Category** | Grid |

Conditional: true if the instance is aligned to a grid

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `hsnap` | Number | `32` | Horizontal grid spacing in pixels |
| `vsnap` | Number | `32` | Vertical grid spacing in pixels |

---

<a id="views"></a>
## Views

### Enable Views

| Property | Value |
|----------|-------|
| **Name** | `enable_views` |
| **Icon** | 🎥 |
| **Category** | Views |

Turn the room's camera/view system on or off (lets a level scroll when it is larger than the window)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `enable` | Yes/No | Yes | On = camera views; off = draw the whole room at once |

### Set View

| Property | Value |
|----------|-------|
| **Name** | `set_view` |
| **Icon** | 🎥 |
| **Category** | Views |

Configure a camera view: which part of the room it shows, where on screen it draws, and an object to follow

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `view` | Choice | `0` | Which of the 8 views to configure; Choices: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Yes/No | Yes | Draw this view |
| `view_x` | Number | `0` | Left edge of the room region shown |
| `view_y` | Number | `0` | Top edge of the room region shown |
| `view_w` | Number | `800` | Width of the room region shown |
| `view_h` | Number | `600` | Height of the room region shown |
| `port_x` | Number | `0` | Left edge on screen |
| `port_y` | Number | `0` | Top edge on screen |
| `port_w` | Number | `800` | Width drawn on screen |
| `port_h` | Number | `600` | Height drawn on screen |
| `follow` | Object | — | Object the camera tracks (blank = fixed view); optional |
| `hborder` | Number | `32` | Horizontal border before the camera scrolls |
| `vborder` | Number | `32` | Vertical border before the camera scrolls |
| `hspeed` | Number | `-1` | Max horizontal scroll speed (-1 = instant) |
| `vspeed` | Number | `-1` | Max vertical scroll speed (-1 = instant) |

---

<a id="3d-view"></a>
## 3D View

### Draw DOOM HUD

| Property | Value |
|----------|-------|
| **Name** | `draw_doom_hud` |
| **Icon** | 🎯 |
| **Category** | 3D View |

Draw a DOOM-style bottom status bar (health bar + number, score, lives, an objective counter, and a health-reactive face icon) over the raycast view

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Bar's left edge, in screen pixels |
| `y` | Number | `-1` | Bar's top edge; negative auto-aligns to the bottom of the window, under the shrunk viewport; optional |
| `width` | Number | `0` | Bar width (0 = full window width); optional |
| `height` | Number | `42` | Bar height; keep it matched to the viewport_height band you reserved on enable_raycast_view; optional |
| `back_color` | Color | `#101010` | Bar background panel; optional |
| `divider_color` | Color | `#505050` | Top border and the health-bar backing; optional |
| `text_color` | Color | `#ffffff` | Colour of all bar text; optional |
| `health_label` | Text | `Health` | optional |
| `health_bar_width` | Number | `90` | optional |
| `health_bar_height` | Number | `14` | optional |
| `bar_color` | Color | `#20c020` | Fill colour of the health bar; optional |
| `face_sprite` | Sprite | — | Horizontal strip of face frames, healthiest first (blank = no face icon); optional |
| `face_frames` | Number | `4` | How many frames the face strip has; health is bucketed evenly across them; optional |
| `score_label` | Text | `Score: ` | optional |
| `lives_sprite` | Sprite | — | Sprite drawn once per remaining life; optional |
| `lives_scale` | Number | `1.0` | optional |
| `objective_value` | Text | `0` | Expression shown after the objective label (bind your own key/quest variable); optional |
| `objective_label` | Text | `Keys: ` | optional |

### Draw Minimap

| Property | Value |
|----------|-------|
| **Name** | `draw_minimap` |
| **Icon** | 🗺️ |
| **Category** | 3D View |

Draw a north-up minimap of the raycast room's walls, with a marker showing where the camera is and which way it faces

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Left edge of the minimap, in screen pixels |
| `y` | Number | `0` | Top edge of the minimap, in screen pixels |
| `size` | Number | `120` | Width and height of the minimap square, in pixels; optional |
| `back_color` | Color | `#101018` | Panel colour behind the map; optional |
| `wall_color` | Color | `#8080a0` | Colour of the wall lines; optional |
| `player_color` | Color | `#ffd040` | Colour of the camera marker and its heading line; optional |

### Enable Raycast View

| Property | Value |
|----------|-------|
| **Name** | `enable_raycast_view` |
| **Icon** | 🕹️ |
| **Category** | 3D View |

Render the room as a Doom/Wolfenstein-style first-person 3D view (walls, sky, floor) instead of the top-down view

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `enable` | Yes/No | Yes | On = first-person raycast view; off = normal top-down |
| `camera_object` | Object | — | Object whose position + facing angle is the camera (blank = the object running this action); optional |
| `fov` | Number | `66` | Horizontal FOV in degrees; optional |
| `render_distance` | Number | `20` | Max ray length in grid cells; optional |
| `cell_size` | Number | `32` | Grid cell size in pixels (match the wall placement grid); optional |
| `columns` | Number | `320` | Screen columns to raycast (lower = faster/chunkier); optional |
| `wall_color` | Color | `#993333` | Flat wall colour when no wall texture is set; optional |
| `floor_color` | Color | `#464632` | Flat floor colour when no floor texture is set; optional |
| `ceiling_color` | Color | `#87CEEB` | Flat ceiling colour when no sky/ceiling texture is set; optional |
| `wall_texture` | Sprite | — | Sprite to texture every wall (blank = flat colour); optional |
| `sky_texture` | Sprite | — | Sprite for a panning sky over the ceiling (blank = flat); optional |
| `floor_texture` | Sprite | — | Sprite cast onto the floor (blank = flat colour); optional |
| `ceiling_texture` | Sprite | — | Sprite cast onto the ceiling when no sky is set; optional |
| `wall_textured` | Yes/No | Yes | Off forces flat wall colours even when a texture is set; optional |
| `floor_cast_res` | Number | `4` | Floor-cast downsample (higher = faster + chunkier); optional |
| `viewport_height` | Number | `0` | Letterbox the 3D view into this many pixels tall, reserving the band below for a DOOM-style status bar (0 = full window height, unchanged); optional |

### Set Facing Angle

| Property | Value |
|----------|-------|
| **Name** | `set_facing_angle` |
| **Icon** | 🧭 |
| **Category** | 3D View |

Set the instance's look direction for a raycast (first-person) camera — independent of movement speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `angle` | Number | `0` | Degrees (0=right, 90=up, 180=left, 270=down) |
| `relative` | Yes/No | No | Add to the current facing angle instead of replacing it; optional |

---

## See Also

- [Event Reference](Event-Reference) — the events that trigger actions
- [Preset Guide](Preset-Guide) — which actions each preset/edition exposes
- [3D View](3D-View) — the raycast first-person actions
- [Extensions](Extensions) — how the 3D View actions are provided

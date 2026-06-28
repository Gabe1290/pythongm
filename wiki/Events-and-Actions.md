# Events and Actions

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Back to Home](Home)

This is a complete reference of all events and actions available in PyGameMaker.

---

## Events Reference

Events are triggers that cause your game logic to execute.

### Create Event
**When:** Once when an instance is created
**Use for:** Initialization, setting variables, starting timers

### Destroy Event
**When:** When the instance is destroyed
**Use for:** Cleanup, spawning effects, awarding points

### Step Events

| Event | When |
|-------|------|
| **Step** | Every frame (60 times/second) |
| **Begin Step** | Before collision checks |
| **End Step** | After all other events |

### Alarm Events

| Event | When |
|-------|------|
| **Alarm[0-11]** | When alarm counter reaches 0 |

Use `Set Alarm` action to start a countdown. Alarm values are in frames (60 = 1 second at 60 FPS).

### Keyboard Events

| Event | When |
|-------|------|
| **Keyboard [key]** | While key is held down (repeats) |
| **Key Press [key]** | Once when key is pressed |
| **Key Release [key]** | Once when key is released |
| **No Key** | When no keys are pressed |

Available keys: Letters (A-Z), Numbers (0-9), Arrow keys, Space, Enter, Shift, Ctrl, Alt, Function keys (F1-F12)

### Mouse Events

| Event | When |
|-------|------|
| **Left Button** | Left click on instance |
| **Right Button** | Right click on instance |
| **Middle Button** | Middle click on instance |
| **Left Press** | Left button pressed (once) |
| **Left Release** | Left button released (once) |
| **Mouse Enter** | Cursor enters instance bounds |
| **Mouse Leave** | Cursor exits instance bounds |
| **Global Left Button** | Left click anywhere |
| **Global Right Button** | Right click anywhere |

### Collision Events

| Event | When |
|-------|------|
| **Collision with [object]** | When touching specified object |

Collision checks happen between the Step and Draw events.

### Other Events

| Event | When |
|-------|------|
| **Outside Room** | Instance is fully outside room |
| **Intersect Boundary** | Instance touches room edge |
| **Game Start** | Game begins (first room loads) |
| **Game End** | Game is closing |
| **Room Start** | Entering a room |
| **Room End** | Leaving a room |
| **No More Lives** | Lives reach 0 |
| **No More Health** | Health reaches 0 |
| **Animation End** | Sprite animation completes |

### Draw Events

| Event | When |
|-------|------|
| **Draw** | During rendering phase |
| **Draw GUI** | After room drawing (screen-space) |

Use Draw events to customize how instances appear or to draw UI elements.

---

## Actions Reference

Actions are operations that execute when events trigger.

### Movement Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Set Speed** | Set movement speed | speed, relative |
| **Set Direction** | Set movement direction | direction (0-360), relative |
| **Set Horizontal Speed** | Set hspeed | hspeed, relative |
| **Set Vertical Speed** | Set vspeed | vspeed, relative |
| **Set Gravity** | Set gravity force | gravity, direction |
| **Set Friction** | Set friction | friction |
| **Move to Point** | Move toward coordinates | x, y, speed |
| **Move in Direction** | Move in a direction | direction, speed |
| **Jump to Position** | Teleport to coordinates | x, y |
| **Jump to Start** | Return to creation position | - |
| **Jump to Random** | Move to random position | - |
| **Wrap Around Room** | Wrap at room edges | horizontal, vertical |
| **Reverse Horizontal** | Flip hspeed | - |
| **Reverse Vertical** | Flip vspeed | - |
| **Move to Contact** | Move until collision | direction, max_distance |
| **Bounce** | Bounce off solid objects | precise |

### Instance Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Create Instance** | Spawn new object | object, x, y, relative |
| **Create Moving** | Spawn with velocity | object, x, y, speed, direction |
| **Create Random** | Spawn one of several | objects[], x, y |
| **Destroy Instance** | Remove instance | - |
| **Destroy at Position** | Destroy instances at point | x, y, object |
| **Change Instance** | Transform to another object | object, perform_events |

### Timing Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Set Alarm** | Start countdown timer | alarm_id (0-11), steps |
| **Sleep** | Pause execution | milliseconds |

### Score/Lives/Health Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Set Score** | Change score | value, relative |
| **Set Lives** | Change lives | value, relative |
| **Set Health** | Change health | value, relative |
| **Draw Score** | Display score | x, y, caption |
| **Draw Lives** | Display lives | x, y, caption |
| **Draw Health** | Display health bar | x, y, width, height |

### Drawing Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Draw Sprite** | Draw a sprite | sprite, x, y, subimage |
| **Draw Text** | Display text | x, y, text |
| **Draw Rectangle** | Draw rectangle | x1, y1, x2, y2, filled |
| **Draw Circle** | Draw circle | x, y, radius, filled |
| **Draw Line** | Draw line | x1, y1, x2, y2 |
| **Draw Arrow** | Draw arrow | x1, y1, x2, y2 |
| **Set Color** | Set drawing color | color |
| **Set Font** | Set text font | font |
| **Set Alignment** | Set text alignment | halign, valign |

### Room Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Next Room** | Go to next room | transition |
| **Previous Room** | Go to previous room | transition |
| **Restart Room** | Reset current room | - |
| **Go to Room** | Jump to specific room | room, transition |
| **If Next Room Exists** | Check if there's a next room | - |
| **If Previous Room Exists** | Check if there's a previous room | - |

### Sound Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Play Sound** | Play sound effect | sound, loop |
| **Stop Sound** | Stop a sound | sound |
| **If Sound Playing** | Check if sound is playing | sound |
| **Play Music** | Play background music | sound, loop |
| **Stop Music** | Stop all music | - |

### Variable Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Set Variable** | Assign value | variable, value, relative |
| **If Variable** | Check value | variable, value, operation |
| **Draw Variable** | Display variable | x, y, variable, caption |

### Control Flow Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **If Expression** | Conditional check | expression |
| **Else** | Alternative branch | - |
| **Start Block** | Begin action group | - |
| **End Block** | End action group | - |
| **Repeat** | Loop N times | count |
| **Exit Event** | Stop current event | - |

### Miscellaneous Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| **Show Message** | Display popup message | message |
| **Show Info** | Show information window | - |
| **Restart Game** | Restart the game | - |
| **End Game** | Close the game | - |

---

## Built-in Variables

These variables are available for all instances:

| Variable | Description |
|----------|-------------|
| `x` | Horizontal position |
| `y` | Vertical position |
| `xstart` | Starting x position |
| `ystart` | Starting y position |
| `hspeed` | Horizontal speed |
| `vspeed` | Vertical speed |
| `speed` | Total movement speed |
| `direction` | Movement direction (0-360) |
| `gravity` | Gravity force |
| `gravity_direction` | Direction of gravity |
| `friction` | Movement friction |
| `image_index` | Current animation frame |
| `image_speed` | Animation speed |
| `image_xscale` | Horizontal scale |
| `image_yscale` | Vertical scale |
| `image_angle` | Rotation angle |
| `visible` | Whether drawn |
| `solid` | Whether solid for collisions |
| `depth` | Drawing depth |
| `sprite_index` | Current sprite |
| `alarm[0-11]` | Alarm timers |

### Global Variables

| Variable | Description |
|----------|-------------|
| `score` | Game score |
| `lives` | Player lives |
| `health` | Player health (0-100) |
| `room` | Current room |
| `room_width` | Current room width |
| `room_height` | Current room height |
| `mouse_x` | Mouse x position |
| `mouse_y` | Mouse y position |

---

## Next Steps

- [[Visual-Programming]] - Use Blockly blocks for the same logic
- [[Object-Editor]] - Apply events and actions to objects
- [[Creating-Your-First-Game]] - See events in action

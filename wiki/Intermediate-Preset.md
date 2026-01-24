# Intermediate Preset

*[Home](Home) | [Preset Guide](Preset-Guide) | [Beginner Preset](Beginner-Preset)*

The **Intermediate** preset builds upon the [Beginner Preset](Beginner-Preset) by adding more advanced events and actions. It's designed for users who have mastered the basics and want to create more complex games with features like timed events, sound, lives, and health systems.

## Overview

The Intermediate preset includes everything from Beginner, plus:
- **4 Additional Event Types** - Draw, Destroy, Mouse, Alarm
- **12 Additional Action Types** - Lives, Health, Sound, Timing, and more movement options
- **3 Additional Categories** - Timing, Sound, Drawing

---

## Additional Events (Beyond Beginner)

### Draw Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_draw` |
| **Category** | Drawing |
| **Icon** | 🎨 |
| **Description** | Triggered when the object needs to be rendered |

**When it fires:** Every frame during the drawing phase, after all step events.

**Important:** When you add a Draw event, the default sprite drawing is disabled. You must manually draw the sprite if you want it visible.

**Common uses:**
- Custom rendering
- Drawing health bars
- Displaying text
- Drawing shapes and effects
- HUD elements

---

### Destroy Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_destroy` |
| **Category** | Object |
| **Icon** | 💥 |
| **Description** | Triggered when the instance is destroyed |

**When it fires:** Just before the instance is removed from the game.

**Common uses:**
- Create explosion effects
- Drop items
- Play death sound
- Update score
- Spawn particles

---

### Mouse Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_mouse` |
| **Category** | Input |
| **Icon** | 🖱️ |
| **Description** | Triggered on mouse interactions |

**Types of mouse events:**
- Left button (press, release, held)
- Right button (press, release, held)
- Middle button (press, release, held)
- Mouse enter (cursor enters instance)
- Mouse leave (cursor leaves instance)
- Global mouse events (anywhere on screen)

**Common uses:**
- Clickable buttons
- Drag and drop
- Hover effects
- Menu interactions

---

### Alarm Event
| Property | Value |
|----------|-------|
| **Block Name** | `event_alarm` |
| **Category** | Timing |
| **Icon** | ⏰ |
| **Description** | Triggered when an alarm timer reaches zero |

**When it fires:** When the corresponding alarm countdown reaches 0.

**Available alarms:** 12 independent alarms (0-11)

**Common uses:**
- Timed spawning
- Delayed actions
- Cooldowns
- Animation timing
- Periodic events

---

## Additional Actions (Beyond Beginner)

### Movement Actions

#### Move in Direction
| Property | Value |
|----------|-------|
| **Action Name** | `move_direction` |
| **Block Name** | `move_direction` |
| **Category** | Movement |

**Description:** Set movement using direction (0-360 degrees) and speed.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `direction` | Number | Direction in degrees (0=right, 90=up, 180=left, 270=down) |
| `speed` | Number | Movement speed |

---

#### Move Towards Point
| Property | Value |
|----------|-------|
| **Action Name** | `move_towards` |
| **Block Name** | `move_towards` |
| **Category** | Movement |

**Description:** Move towards a specific position.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | Number/Expression | Target X coordinate |
| `y` | Number/Expression | Target Y coordinate |
| `speed` | Number | Movement speed |

---

### Timing Actions

#### Set Alarm
| Property | Value |
|----------|-------|
| **Action Name** | `set_alarm` |
| **Block Name** | `set_alarm` |
| **Category** | Timing |
| **Icon** | ⏰ |

**Description:** Set an alarm to trigger after a number of steps.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `alarm` | Number | Alarm number (0-11) |
| `steps` | Number | Steps until alarm fires (at 60 FPS, 60 steps = 1 second) |

**Example:** Set alarm 0 to 180 steps for a 3-second delay.

---

### Lives Actions

#### Set Lives
| Property | Value |
|----------|-------|
| **Action Name** | `set_lives` |
| **Block Name** | `lives_set` |
| **Category** | Score/Lives/Health |
| **Icon** | ❤️ |

**Description:** Set the number of lives.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Lives value |
| `relative` | Boolean | If true, adds to current lives |

---

#### Add Lives
| Property | Value |
|----------|-------|
| **Action Name** | `add_lives` |
| **Block Name** | `lives_add` |
| **Category** | Score/Lives/Health |
| **Icon** | ➕❤️ |

**Description:** Add to or subtract from lives.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Amount to add (negative to subtract) |

**Note:** When lives reach 0, the `no_more_lives` event is triggered.

---

#### Draw Lives
| Property | Value |
|----------|-------|
| **Action Name** | `draw_lives` |
| **Block Name** | `draw_lives` |
| **Category** | Score/Lives/Health |
| **Icon** | 🖼️❤️ |

**Description:** Display lives on screen.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | Number | X position |
| `y` | Number | Y position |
| `sprite` | Sprite | Optional sprite to use as life icon |

---

### Health Actions

#### Set Health
| Property | Value |
|----------|-------|
| **Action Name** | `set_health` |
| **Block Name** | `health_set` |
| **Category** | Score/Lives/Health |
| **Icon** | 💚 |

**Description:** Set the health value (0-100).

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Health value (0-100) |
| `relative` | Boolean | If true, adds to current health |

---

#### Add Health
| Property | Value |
|----------|-------|
| **Action Name** | `add_health` |
| **Block Name** | `health_add` |
| **Category** | Score/Lives/Health |
| **Icon** | ➕💚 |

**Description:** Add to or subtract from health.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | Number | Amount to add (negative for damage) |

**Note:** When health reaches 0, the `no_more_health` event is triggered.

---

#### Draw Health Bar
| Property | Value |
|----------|-------|
| **Action Name** | `draw_health_bar` |
| **Block Name** | `draw_health_bar` |
| **Category** | Score/Lives/Health |
| **Icon** | 📊💚 |

**Description:** Draw a health bar on screen.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `x1` | Number | Left X position |
| `y1` | Number | Top Y position |
| `x2` | Number | Right X position |
| `y2` | Number | Bottom Y position |
| `back_color` | Color | Background color |
| `bar_color` | Color | Health bar color |

---

### Sound Actions

#### Play Sound
| Property | Value |
|----------|-------|
| **Action Name** | `play_sound` |
| **Block Name** | `sound_play` |
| **Category** | Sound |
| **Icon** | 🔊 |

**Description:** Play a sound effect.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `sound` | Sound | Sound resource to play |
| `loop` | Boolean | Whether to loop the sound |

---

#### Play Music
| Property | Value |
|----------|-------|
| **Action Name** | `play_music` |
| **Block Name** | `music_play` |
| **Category** | Sound |
| **Icon** | 🎵 |

**Description:** Play background music.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `sound` | Sound | Music resource to play |
| `loop` | Boolean | Whether to loop (usually true for music) |

---

#### Stop Music
| Property | Value |
|----------|-------|
| **Action Name** | `stop_music` |
| **Block Name** | `music_stop` |
| **Category** | Sound |
| **Icon** | 🔇 |

**Description:** Stop all currently playing music.

**Parameters:** None

---

## Complete Feature List

### Events in Intermediate Preset

| Event | Category | Description |
|-------|----------|-------------|
| Create | Object | Instance created |
| Step | Object | Every frame |
| Destroy | Object | Instance destroyed |
| Draw | Drawing | Rendering phase |
| Keyboard Press | Input | Key pressed once |
| Mouse | Input | Mouse interactions |
| Collision | Collision | Instance overlap |
| Alarm | Timing | Timer reached zero |

### Actions in Intermediate Preset

| Category | Actions |
|----------|---------|
| **Movement** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Instance** | Create, Destroy |
| **Score** | Set Score, Add Score, Draw Score |
| **Lives** | Set Lives, Add Lives, Draw Lives |
| **Health** | Set Health, Add Health, Draw Health Bar |
| **Room** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Timing** | Set Alarm |
| **Sound** | Play Sound, Play Music, Stop Music |
| **Output** | Show Message, Execute Code |

---

## Example: Shooter Game with Lives

### Player Object

**Create:**
- Set Lives: 3

**Keyboard Press (Space):**
- Create Instance: obj_bullet at (x, y-20)
- Set Alarm: 0 to 15 (cooldown)

**Collision with obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Enemy Object

**Create:**
- Set Alarm: 0 to 60

**Alarm 0:**
- Create Instance: obj_enemy_bullet at (x, y+20)
- Set Alarm: 0 to 60 (repeat)

**Collision with obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Upgrading to Advanced Presets

When you need more features, consider:
- **Platformer Preset** - Gravity, jumping, platform mechanics
- **Full Preset** - All available events and actions

---

## See Also

- [Beginner Preset](Beginner-Preset) - Start here if new
- [Full Action Reference](Full-Action-Reference) - Complete action list
- [Event Reference](Event-Reference) - Complete event list
- [Events and Actions](Events-and-Actions) - Core concepts

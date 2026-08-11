# Instance

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (2)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (20)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (4)

[← Back to Full Action Reference](Full-Action-Reference)

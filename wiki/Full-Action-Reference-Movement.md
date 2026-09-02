# Movement

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

## Other Categories

- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (16)
- [Particles](Full-Action-Reference-Particles) (8)
- [Network](Full-Action-Reference-Network-Actions) (15)

[← Back to Full Action Reference](Full-Action-Reference)

# Room

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

### Set Background

| Property | Value |
|----------|-------|
| **Name** | `set_background` |
| **Icon** | 🖼️ |
| **Category** | Room |

Set the current room's background image, with tiling and scrolling options

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `background` | Text | — | Background or sprite asset name |
| `visible` | Yes/No | Yes | Show the background; optional |
| `foreground` | Yes/No | No | Draw in front of instances instead of behind them; optional |
| `tiled_h` | Yes/No | No | Repeat the background across the width of the room; optional |
| `tiled_v` | Yes/No | No | Repeat the background across the height of the room; optional |
| `hspeed` | Number | `0` | Horizontal auto-scroll speed in pixels/frame; optional |
| `vspeed` | Number | `0` | Vertical auto-scroll speed in pixels/frame; optional |

### Set Background Color

| Property | Value |
|----------|-------|
| **Name** | `set_background_color` |
| **Icon** | 🎨 |
| **Category** | Room |

Change the current room's background color

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#87CEEB` | Background color |
| `show_color` | Yes/No | Yes | Whether the background color is visible (off fills black instead); optional |

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

### Set Room Persistent

| Property | Value |
|----------|-------|
| **Name** | `set_room_persistent` |
| **Icon** | 💾 |
| **Category** | Room |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `persistent` | Yes/No | Yes | Keep this room's state across a revisit |

### Set Room Speed

| Property | Value |
|----------|-------|
| **Name** | `set_room_speed` |
| **Icon** | ⏱️ |
| **Category** | Room |

Change the game's frame rate (frames per second)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `30` | Target frames per second (1-240) |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
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

# Views

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [3D View](Full-Action-Reference-3D-View-Actions) (16)
- [Particles](Full-Action-Reference-Particles) (8)
- [Network](Full-Action-Reference-Network-Actions) (15)

[← Back to Full Action Reference](Full-Action-Reference)

# Score

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (21)
- [Instance](Full-Action-Reference-Instance) (12)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (14)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (3)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (18)
- [Drawing](Full-Action-Reference-Drawing) (11)
- [Network](Full-Action-Reference-Network-Actions) (22)
- [Particles](Full-Action-Reference-Particles) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions) (16)

[← Back to Full Action Reference](Full-Action-Reference)

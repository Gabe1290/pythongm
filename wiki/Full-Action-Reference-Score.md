# Score

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
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

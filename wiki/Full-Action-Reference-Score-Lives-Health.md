# Score/Lives/Health

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Clear High-Score Table

| Property | Value |
|----------|-------|
| **Name** | `clear_highscore` |
| **Icon** | 🗑️🏆 |
| **Category** | Score/Lives/Health |

Clear all high-score entries

*Parameters:* none

### Show High-Score Table

| Property | Value |
|----------|-------|
| **Name** | `show_highscore` |
| **Icon** | 🏆 |
| **Category** | Score/Lives/Health |

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
| **Category** | Score/Lives/Health |

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
| **Category** | Score/Lives/Health |

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
| **Category** | Score/Lives/Health |

Conditional: compare the score against a value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `value` | Number | `0` | Value to compare against |
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (21)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (6)
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
- [micro:bit](Full-Action-Reference-Microbit-Actions) (16)

[← Back to Full Action Reference](Full-Action-Reference)

# Audio

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (2)
- [Game](Full-Action-Reference-Game) (20)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (4)

[← Back to Full Action Reference](Full-Action-Reference)

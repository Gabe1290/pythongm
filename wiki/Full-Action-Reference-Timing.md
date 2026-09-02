# Timing

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Pause Timeline

| Property | Value |
|----------|-------|
| **Name** | `pause_timeline` |
| **Icon** | ⏸️ |
| **Category** | Timing |

Pause timeline playback at the current position

*Parameters:* none

### Set Alarm

| Property | Value |
|----------|-------|
| **Name** | `set_alarm` |
| **Icon** | ⏰ |
| **Category** | Timing |

Set an alarm clock

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `alarm_number` | Number | `0` | Which alarm (0-11) |
| `steps` | Number | `30` | Number of steps until alarm triggers (30 = 0.5 sec at 60 FPS) |

### Set Timeline

| Property | Value |
|----------|-------|
| **Name** | `set_timeline` |
| **Icon** | ⏱️ |
| **Category** | Timing |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `timeline` | Text | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Property | Value |
|----------|-------|
| **Name** | `set_timeline_position` |
| **Icon** | ⏱️ |
| **Category** | Timing |

Set (or offset) this instance's timeline position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `position` | Number | `0` | Position in steps |
| `relative` | Yes/No | No | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Property | Value |
|----------|-------|
| **Name** | `set_timeline_speed` |
| **Icon** | ⏱️ |
| **Category** | Timing |

Set the timeline playback speed multiplier

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Sleep

| Property | Value |
|----------|-------|
| **Name** | `sleep` |
| **Icon** | 💤 |
| **Category** | Timing |

Pause the game for a number of milliseconds, then continue. Sounds keep playing during the pause (e.g. let a sound finish before changing rooms). Note: rendering and input are frozen while sleeping, so keep durations short

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `milliseconds` | Number | `1000` | How long to pause, in milliseconds (1000 = 1 second) |

### Start Timeline

| Property | Value |
|----------|-------|
| **Name** | `start_timeline` |
| **Icon** | ▶️ |
| **Category** | Timing |

Begin or resume timeline playback from the current position

*Parameters:* none

### Stop Timeline

| Property | Value |
|----------|-------|
| **Name** | `stop_timeline` |
| **Icon** | ⏹️ |
| **Category** | Timing |

Stop timeline playback and reset the position to 0

*Parameters:* none

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (16)
- [Particles](Full-Action-Reference-Particles) (8)
- [Network](Full-Action-Reference-Network-Actions) (15)

[← Back to Full Action Reference](Full-Action-Reference)

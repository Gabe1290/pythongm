# Timing

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (20)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (4)

[← Back to Full Action Reference](Full-Action-Reference)

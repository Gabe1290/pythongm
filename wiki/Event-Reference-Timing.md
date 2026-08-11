# Timing Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Alarm
| Property | Value |
|----------|-------|
| **Name** | `alarm` |
| **Icon** | ⏰ |
| **Category** | Timing |
| **Preset** | Beginner |

**Description:** Fires when an alarm countdown reaches zero.

**Available alarms:** 12 independent alarms (alarm[0] through alarm[11])

**Setting alarms:** Use the "Set Alarm" action with steps (60 steps ≈ 1 second at 60 FPS)

**Common uses:**
- Timed spawning
- Cooldowns
- Delayed effects
- Repeating actions (set alarm again in alarm event)

---

### Begin Step
| Property | Value |
|----------|-------|
| **Name** | `begin_step` |
| **Icon** | ▶️ |
| **Category** | Step |
| **Preset** | Beginner |

**Description:** Fires at the beginning of each frame, before regular Step events.

**Execution order:** Begin Step → Step → End Step

**Common uses:**
- Input processing
- Pre-movement calculations

---

### End Step
| Property | Value |
|----------|-------|
| **Name** | `end_step` |
| **Icon** | ⏹️ |
| **Category** | Step |
| **Preset** | Beginner |

**Description:** Fires at the end of each frame, after collisions.

**Common uses:**
- Final position adjustments
- Cleanup operations
- State updates after collisions

---

## Other Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

[← Back to Event Reference](Event-Reference)

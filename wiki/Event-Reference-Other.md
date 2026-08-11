# Other Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Outside Room
| Property | Value |
|----------|-------|
| **Name** | `outside_room` |
| **Icon** | 🚫 |
| **Category** | Other |
| **Preset** | Beginner |

**Description:** Fires when instance is completely outside room boundaries.

**Common uses:**
- Destroy off-screen bullets
- Wrap around to other side
- Trigger game over

---

### Intersect Boundary
| Property | Value |
|----------|-------|
| **Name** | `intersect_boundary` |
| **Icon** | ⚠️ |
| **Category** | Other |
| **Preset** | Beginner |

**Description:** Fires when instance touches the room boundary.

**Common uses:**
- Keep player in bounds
- Bounce off edges

---

### No More Lives
| Property | Value |
|----------|-------|
| **Name** | `no_more_lives` |
| **Icon** | 💀 |
| **Category** | Other |
| **Preset** | Beginner |

**Description:** Fires when lives become 0 or less.

**Common uses:**
- Game over screen
- Restart game
- Show final score

---

### No More Health
| Property | Value |
|----------|-------|
| **Name** | `no_more_health` |
| **Icon** | 💔 |
| **Category** | Other |
| **Preset** | Beginner |

**Description:** Fires when health becomes 0 or less.

**Common uses:**
- Lose a life
- Respawn player
- Trigger death animation

---

### Animation End
| Property | Value |
|----------|-------|
| **Name** | `animation_end` |
| **Icon** | 🎞️ |
| **Category** | Other |
| **Preset** | Beginner |

**Description:** Fires when the instance's sprite animation completes a full cycle (wraps from the last frame back to the first).

**Common uses:**
- Destroy a one-shot effect (explosion) after it plays once
- Switch to another animation when the current one finishes
- Advance a state machine on animation completion

---

## Other Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end

[← Back to Event Reference](Event-Reference)

# Game Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Game Start
| Property | Value |
|----------|-------|
| **Name** | `game_start` |
| **Icon** | 🎮 |
| **Category** | Game |
| **Preset** | Beginner |

**Description:** Fires once when the game first starts (in first room only).

**Common uses:**
- Initialize global variables
- Load saved data
- Play intro

---

### Game End
| Property | Value |
|----------|-------|
| **Name** | `game_end` |
| **Icon** | 🎮 |
| **Category** | Game |
| **Preset** | Beginner |

**Description:** Fires when the game is ending.

**Common uses:**
- Save game data
- Cleanup resources

---

## Other Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

[← Back to Event Reference](Event-Reference)

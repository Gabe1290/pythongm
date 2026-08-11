# Object Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Create
| Property | Value |
|----------|-------|
| **Name** | `create` |
| **Icon** | 🎯 |
| **Category** | Object |
| **Preset** | Beginner |

**Description:** Executed once when an instance is first created.

**When it fires:**
- When an instance is placed in a room at game start
- When created via the "Create Instance" action
- After room transitions for new instances

**Common uses:**
- Initialize variables
- Set starting values
- Configure initial state

---

### Step
| Property | Value |
|----------|-------|
| **Name** | `step` |
| **Icon** | ⭐ |
| **Category** | Object |
| **Preset** | Beginner |

**Description:** Executed every frame (typically 60 times per second).

**When it fires:** Continuously, every game frame.

**Common uses:**
- Continuous movement
- Checking conditions
- Updating positions
- Game logic

**Note:** Be careful with performance - code here runs constantly.

---

### Destroy
| Property | Value |
|----------|-------|
| **Name** | `destroy` |
| **Icon** | 💥 |
| **Category** | Object |
| **Preset** | Intermediate |

**Description:** Executed when an instance is destroyed.

**When it fires:** Just before the instance is removed from the game.

**Common uses:**
- Spawn effects (explosions, particles)
- Drop items
- Update scores
- Play sounds

---

## Other Event Categories

- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

[← Back to Event Reference](Event-Reference)

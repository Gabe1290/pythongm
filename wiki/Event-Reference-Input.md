# Input Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Keyboard (Continuous)
| Property | Value |
|----------|-------|
| **Name** | `keyboard` |
| **Icon** | ⌨️ |
| **Category** | Input |
| **Preset** | Beginner |

**Description:** Fires continuously while a key is held down.

**Best for:** Smooth, continuous movement

**Supported Keys:**
- Arrow keys (up, down, left, right)
- Letters (A-Z)
- Numbers (0-9)
- Space, Enter, Escape
- Function keys (F1-F12)
- Modifier keys (Shift, Ctrl, Alt)

---

### Keyboard Press
| Property | Value |
|----------|-------|
| **Name** | `keyboard_press` |
| **Icon** | 🔘 |
| **Category** | Input |
| **Preset** | Intermediate |

**Description:** Fires once when a key is first pressed.

**Best for:** Single actions (jump, shoot, menu select)

**Difference from Keyboard:** Only fires once per press, not while held.

---

### Keyboard Release
| Property | Value |
|----------|-------|
| **Name** | `keyboard_release` |
| **Icon** | ⬆️ |
| **Category** | Input |
| **Preset** | Full (Development edition) |

**Description:** Fires once when a key is released.

**Common uses:**
- Stop movement when key released
- End charging attacks
- Toggle states

---

### Keyboard (No Key)
| Property | Value |
|----------|-------|
| **Name** | `keyboard_no_key` |
| **Icon** | ⌨️ |
| **Category** | Input |
| **Preset** | Beginner |

**Description:** Fires each frame while **no** key is being held.

**When it fires:** Every frame that the keyboard is idle, *before* the Step event.

**Common uses:**
- Stop movement when the player releases all keys (grid/maze games)
- Idle animations

---

### Mouse
| Property | Value |
|----------|-------|
| **Name** | `mouse` |
| **Icon** | 🖱️ |
| **Category** | Input |
| **Preset** | Full (Development edition) |

**Description:** Mouse button and movement events.

**Event Types:**

| Type | Description |
|------|-------------|
| Left Button | Click with left mouse button |
| Right Button | Click with right mouse button |
| Middle Button | Click with middle/scroll button |
| Mouse Enter | Cursor enters instance bounds |
| Mouse Leave | Cursor leaves instance bounds |
| Global Left Button | Left click anywhere |
| Global Right Button | Right click anywhere |

---

## Other Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

[← Back to Event Reference](Event-Reference)

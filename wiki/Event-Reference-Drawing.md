# Drawing Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Draw
| Property | Value |
|----------|-------|
| **Name** | `draw` |
| **Icon** | 🎨 |
| **Category** | Drawing |
| **Preset** | Beginner |

**Description:** Fires during the rendering phase.

**Important:** Adding a Draw event disables automatic sprite drawing. You must draw the sprite manually if you want it visible.

**Common uses:**
- Custom rendering
- Drawing shapes
- Displaying text
- Health bars
- HUD elements

**Available drawing actions:**
- Draw Sprite
- Draw Text
- Draw Rectangle
- Draw Circle
- Draw Line
- Draw Health Bar

---

### Draw GUI
| Property | Value |
|----------|-------|
| **Name** | `draw_gui` |
| **Icon** | 🖥️ |
| **Category** | Drawing |
| **Preset** | Beginner |

**Description:** Draws in **screen (GUI) space**, on top of the room and unaffected by views/camera scrolling.

**Difference from Draw:** the regular Draw event is in room coordinates (it scrolls with the view); Draw GUI stays fixed to the screen — use it for HUDs, scores, and menus.

---

## Other Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Collision Events](Event-Reference-Collision) - Object collisions
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

[← Back to Event Reference](Event-Reference)

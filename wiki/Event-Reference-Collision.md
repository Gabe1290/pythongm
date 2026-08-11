# Collision Events

*[Home](Home) | [Event Reference](Event-Reference) | [Full Action Reference](Full-Action-Reference)*

### Collision
| Property | Value |
|----------|-------|
| **Name** | `collision` |
| **Icon** | 💥 |
| **Category** | Collision |
| **Preset** | Beginner |

**Description:** Fires when this instance overlaps with another object type.

**Configuration:** Select which object type triggers this collision.

**Special variable:** `other` - Reference to the colliding instance.

**When it fires:** Every frame that instances are overlapping.

**Common uses:**
- Collecting items
- Taking damage
- Hitting walls
- Triggering events

**Example collision events:**
- `collision_with_obj_coin` - Player touches a coin
- `collision_with_obj_enemy` - Player touches an enemy
- `collision_with_obj_wall` - Instance hits a wall

---

## Other Event Categories

- [Object Events](Event-Reference-Object) - Create, Step, Destroy
- [Input Events](Event-Reference-Input) - Keyboard, Mouse
- [Timing Events](Event-Reference-Timing) - Alarms, Step variants
- [Drawing Events](Event-Reference-Drawing) - Custom rendering
- [Room Events](Event-Reference-Room) - Room transitions
- [Game Events](Event-Reference-Game) - Game start/end
- [Other Events](Event-Reference-Other) - Boundaries, Lives, Health

[← Back to Event Reference](Event-Reference)

# Preset Guide

*[English](Preset-Guide) | [Back to Home](Home)*

PyGameMaker offers different presets that control which events and actions are available. This helps beginners focus on essential features while allowing experienced users to access the full toolset.

## Choose Your Skill Level

| Preset | Best For | Features |
|--------|----------|----------|
| [**Beginner**](Beginner-Preset) | New users | Basic movement, collisions, score, rooms |
| [**Intermediate**](Intermediate-Preset) | Some experience | + Lives, health, sound, alarms, drawing |
| **Advanced** | Experienced users | All features available |

---

## Preset Documentation

### Presets
| Page | Description |
|------|-------------|
| [Beginner Preset](Beginner-Preset) | 4 events, 17 actions - Essential features |
| [Intermediate Preset](Intermediate-Preset) | +4 events, +12 actions - Lives, health, sound |

### Reference
| Page | Description |
|------|-------------|
| [Event Reference](Event-Reference) | Complete list of all events |
| [Full Action Reference](Full-Action-Reference) | Complete list of all actions |

---

## Quick Start Example

Here's a simple coin collector game using only Beginner features:

### 1. Create Objects
- `obj_player` - The controllable character
- `obj_coin` - Collectible items
- `obj_wall` - Solid obstacles

### 2. Add Events to Player

**Keyboard (Arrow Keys):**
```
Left Arrow  → Set Horizontal Speed: -4
Right Arrow → Set Horizontal Speed: 4
Up Arrow    → Set Vertical Speed: -4
Down Arrow  → Set Vertical Speed: 4
```

**Collision with obj_coin:**
```
Add Score: 10
Destroy Instance: other
```

**Collision with obj_wall:**
```
Stop Movement
```

### 3. Create a Room
- Place the player
- Add some coins
- Add walls around the edges

### 4. Run the Game!
Press the Play button to test your game.

---

## Tips for Success

1. **Start Simple** - Use the Beginner preset first
2. **Test Often** - Run your game frequently to catch issues
3. **One Thing at a Time** - Add features gradually
4. **Use Collisions** - Most game mechanics involve collision events
5. **Read the Docs** - Check the reference pages when stuck

---

## See Also

- [Home](Home) - Main wiki page
- [Getting Started](Getting-Started) - Installation and setup
- [Events and Actions](Events-and-Actions) - Core concepts
- [Creating Your First Game](Creating-Your-First-Game) - Tutorial
- [Breakout Tutorial](Tutorial-Breakout) - Create a classic brick breaker game
- [Introduction to Game Creation](Getting-Started-Breakout) - Comprehensive beginner tutorial

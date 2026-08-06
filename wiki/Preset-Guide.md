# Preset Guide

*[English](Preset-Guide) | [Back to Home](Home)*

PyGameMaker offers different presets that control which events and actions are available — in **both** the Blockly visual-block picker and the structured Events/Actions panel ("Add Event"/"Add Action") that every tutorial on this wiki uses. This helps beginners focus on essential features while allowing experienced users to access the full toolset.

A project's preset is set two ways: **`Preferences > IDE Edition`** picks the default preset for *new* projects (existing projects are never changed by switching edition), and **`Tools > Configure Action Blocks...`** changes the preset for the *currently open* project at any time. The IDE's default edition is Beginner, so a fresh install's new projects start on the Beginner preset already.

## Choose Your Skill Level

| IDE Edition | Best For | Preset it uses |
|--------|----------|----------|
| **Beginner** (default) | New users | [Beginner Preset](Beginner-Preset) — basic movement, collisions, score, rooms |
| **Advanced** | Some experience | [Intermediate Preset](Intermediate-Preset) — + lives, health, sound, alarms, grid movement |
| **Development** | Experienced users | The `full` preset — every event and action available |

Note the naming isn't 1:1: the "Advanced" *edition* uses the `intermediate` *preset* (there's no separate "advanced" preset) — see [Beginner Preset](Beginner-Preset)/[Intermediate Preset](Intermediate-Preset) for the exact, always-current event and action counts each one enables.

---

## Preset Documentation

### Presets
| Page | Description |
|------|-------------|
| [Beginner Preset](Beginner-Preset) | Essential features — exact counts on that page |
| [Intermediate Preset](Intermediate-Preset) | Adds lives, health, sound, alarms, grid movement — exact counts on that page |

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

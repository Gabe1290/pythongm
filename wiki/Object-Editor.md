# Object Editor

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

> [Back to Home](Home)

Objects are the core building blocks of your game. They represent everything from players and enemies to collectibles and UI elements.

---

## Opening the Object Editor

1. Double-click an existing object in the resource tree, or
2. Right-click **Objects** > **Create Object**

---

## Object Properties

### Basic Properties

| Property | Description |
|----------|-------------|
| **Name** | Unique identifier for the object (e.g., `obj_player`) |
| **Sprite** | The visual representation of the object |
| **Visible** | Whether the object is drawn (default: true) |
| **Solid** | Used for collision detection with solid objects |
| **Depth** | Drawing order (lower = drawn on top) |
| **Persistent** | Object survives room changes |

### Naming Convention

Use the `obj_` prefix for objects:
- `obj_player`
- `obj_enemy`
- `obj_coin`
- `obj_wall`

---

## Events

Events are triggers that cause actions to execute. Click **Add Event** to add one.

### Common Events

| Event | When It Triggers |
|-------|------------------|
| **Create** | Once when an instance is created |
| **Destroy** | When the instance is destroyed |
| **Step** | Every game frame (60 times per second) |
| **Draw** | During the drawing phase |
| **Alarm [0-11]** | When an alarm timer reaches zero |

### Keyboard Events

| Event | When It Triggers |
|-------|------------------|
| **Key Press** | Once when a key is pressed down |
| **Key Release** | Once when a key is released |
| **Keyboard** | Every frame while a key is held |
| **No Key** | When no keys are pressed |

### Mouse Events

| Event | When It Triggers |
|-------|------------------|
| **Mouse Button** | When clicking on the instance |
| **Global Mouse** | When clicking anywhere |
| **Mouse Enter** | When cursor enters the instance |
| **Mouse Leave** | When cursor exits the instance |

### Collision Events

| Event | When It Triggers |
|-------|------------------|
| **Collision with [object]** | When touching another object type |

### Other Events

| Event | When It Triggers |
|-------|------------------|
| **Outside Room** | When instance leaves the room boundaries |
| **Intersect Boundary** | When instance touches room edge |
| **Game Start** | Once when the game begins |
| **Game End** | Once when the game closes |
| **Room Start** | When entering a room |
| **Room End** | When leaving a room |

---

## Actions

Actions are operations performed when events trigger. Each event can have multiple actions that execute in order.

### Movement Actions

- **Set Speed** - Set movement speed
- **Set Direction** - Set movement direction (0-360 degrees)
- **Set Horizontal Speed** - Set left/right velocity
- **Set Vertical Speed** - Set up/down velocity
- **Move Toward Point** - Move toward coordinates
- **Jump to Position** - Instantly move to coordinates
- **Jump to Start** - Return to starting position
- **Jump to Random** - Move to random position

### Instance Actions

- **Create Instance** - Spawn a new object
- **Destroy Instance** - Remove the current instance
- **Change Instance** - Transform into another object type

### Timing Actions

- **Set Alarm** - Start a countdown timer
- **Sleep** - Pause execution briefly

### Drawing Actions

- **Draw Sprite** - Draw a sprite image
- **Draw Text** - Display text on screen
- **Draw Rectangle** - Draw a filled or outlined rectangle
- **Draw Score** - Display the current score
- **Draw Lives** - Display remaining lives
- **Draw Health** - Display health bar

### Score/Lives/Health

- **Set Score** - Change the score value
- **Set Lives** - Change lives count
- **Set Health** - Change health value
- **If Score** - Check score condition
- **If Lives** - Check lives condition
- **If Health** - Check health condition

### Room Actions

- **Next Room** - Go to the next room
- **Previous Room** - Go to the previous room
- **Restart Room** - Reset the current room
- **Go to Room** - Jump to a specific room

### Sound Actions

- **Play Sound** - Play a sound effect
- **Stop Sound** - Stop a playing sound
- **Play Music** - Play background music
- **Stop Music** - Stop background music

### Variable Actions

- **Set Variable** - Assign a value to a variable
- **If Variable** - Check a variable condition

---

## Visual Programming with Blockly

Instead of using the action list, you can switch to the **Blockly** tab for visual programming:

1. Open an object
2. Click the **Blockly** tab
3. Drag blocks from the toolbox to create logic
4. Blocks snap together to form complete programs

See [[Visual-Programming]] for more details.

---

## Tips and Best Practices

### Organization
- Give objects descriptive names
- Group related objects with similar prefixes
- Keep the Create event for initialization only

### Performance
- Avoid heavy calculations in the Step event
- Use alarms instead of counting frames manually
- Destroy instances that leave the room

### Debugging
- Use the **Show Message** action to display values
- Check the console output for errors
- Test frequently as you build

---

## Example: Simple Enemy AI

```
Create Event:
  - Set Alarm[0] = 60 (1 second at 60 FPS)
  - Set direction = random(360)
  - Set speed = 2

Alarm[0] Event:
  - Set direction = random(360)
  - Set Alarm[0] = 60

Collision with obj_player:
  - Set Lives relative = -1
  - Destroy Instance
```

---

## Next Steps

- [[Room-Editor]] - Place objects in your game levels
- [[Events-and-Actions]] - Complete reference of all events and actions
- [[Visual-Programming]] - Learn Blockly block programming

# Visual Programming

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

> [Back to Home](Home)

PyGameMaker includes Google Blockly for visual, drag-and-drop programming. Build game logic by connecting blocks instead of writing code.

---

## Accessing Blockly

1. Open an object in the Object Editor
2. Click the **Blockly** tab (next to the Events tab)
3. The Blockly workspace appears with a toolbox on the left

---

## The Blockly Workspace

### Toolbox
The left panel contains block categories:
- **Events** - Event trigger blocks
- **Movement** - Motion and position blocks
- **Timing** - Alarms and delays
- **Drawing** - Visual rendering blocks
- **Score/Lives/Health** - Game state blocks
- **Instance** - Object creation/destruction
- **Room** - Room navigation
- **Values** - Variables and expressions
- **Sound** - Audio playback
- **Logic** - If/else and loops
- **Math** - Mathematical operations
- **Text** - String manipulation

### Workspace
The center area where you build your program by:
- Dragging blocks from the toolbox
- Connecting blocks together
- Configuring block parameters

### Trash Can
Drag unwanted blocks here to delete them, or press Delete key.

---

## Block Types

### Hat Blocks (Events)
Hat blocks have a rounded top and start a sequence. They represent events:

```
┌─────────────────┐
│ When Create     │
└─────────────────┘
```

### Stack Blocks (Actions)
Stack blocks have notches that connect to other blocks:

```
├─────────────────┤
│ Set speed to 5  │
├─────────────────┤
```

### Reporter Blocks (Values)
Reporter blocks are rounded and return values:

```
( x position )    ( score )    ( 100 )
```

### Boolean Blocks (Conditions)
Boolean blocks are hexagonal and return true/false:

```
< touching obj_wall >    < key pressed: space >
```

### C-Blocks (Containers)
C-blocks wrap around other blocks:

```
┌─────────────────┐
│ if < condition >│
│  ├─────────────┤│
│  │ do action   ││
│  ├─────────────┤│
└─────────────────┘
```

---

## Event Blocks

### Create Event
```
┌─────────────────────┐
│ When Create         │
├─────────────────────┤
│ [actions go here]   │
└─────────────────────┘
```

### Step Event
```
┌─────────────────────┐
│ When Step           │
├─────────────────────┤
│ [runs every frame]  │
└─────────────────────┘
```

### Keyboard Events
```
┌─────────────────────────┐
│ When key [arrow_left] ▼│
├─────────────────────────┤
│ [actions go here]       │
└─────────────────────────┘
```

### Collision Events
```
┌────────────────────────────┐
│ When colliding with [obj] ▼│
├────────────────────────────┤
│ [actions go here]          │
└────────────────────────────┘
```

---

## Movement Blocks

| Block | Description |
|-------|-------------|
| `set speed to [5]` | Set movement speed |
| `set direction to [90]` | Set movement direction |
| `set hspeed to [4]` | Set horizontal velocity |
| `set vspeed to [-5]` | Set vertical velocity |
| `move to x: [100] y: [200]` | Jump to position |
| `move toward x: [100] y: [200] at speed [3]` | Move toward point |
| `jump to start position` | Return to creation spot |
| `jump to random position` | Move randomly |
| `bounce off solid objects` | Reverse on collision |

---

## Drawing Blocks

| Block | Description |
|-------|-------------|
| `draw sprite [spr] at x: [0] y: [0]` | Draw a sprite |
| `draw text [Hello] at x: [10] y: [10]` | Display text |
| `draw score at x: [10] y: [10]` | Show the score |
| `draw rectangle from [x1,y1] to [x2,y2]` | Draw rectangle |
| `set drawing color to [color]` | Change draw color |

---

## Score/Lives/Health Blocks

| Block | Description |
|-------|-------------|
| `set score to [100]` | Set exact score |
| `change score by [10]` | Add/subtract score |
| `set lives to [3]` | Set exact lives |
| `change lives by [-1]` | Add/subtract lives |
| `set health to [100]` | Set exact health |
| `change health by [-25]` | Add/subtract health |

---

## Instance Blocks

| Block | Description |
|-------|-------------|
| `create [obj] at x: [100] y: [200]` | Spawn new instance |
| `create [obj] at this position` | Spawn at self |
| `destroy this instance` | Remove self |
| `destroy all [obj]` | Remove all of type |

---

## Room Blocks

| Block | Description |
|-------|-------------|
| `go to next room` | Advance to next room |
| `go to previous room` | Go back one room |
| `restart current room` | Reset room |
| `go to room [room_name]` | Jump to specific room |

---

## Sound Blocks

| Block | Description |
|-------|-------------|
| `play sound [snd]` | Play sound once |
| `play sound [snd] looping` | Loop sound |
| `stop sound [snd]` | Stop specific sound |
| `stop all sounds` | Silence everything |

---

## Logic Blocks

### If/Else
```
┌─────────────────────────┐
│ if < condition >        │
│  ├─────────────────────┤│
│  │ [then do this]      ││
│  ├─────────────────────┤│
│ else                    │
│  ├─────────────────────┤│
│  │ [otherwise this]    ││
│  └─────────────────────┤│
└─────────────────────────┘
```

### Repeat
```
┌─────────────────────────┐
│ repeat [10] times       │
│  ├─────────────────────┤│
│  │ [do this]           ││
│  └─────────────────────┤│
└─────────────────────────┘
```

### Comparison
- `< [x] = [10] >`
- `< [score] > [100] >`
- `< [lives] < [1] >`

### Boolean Logic
- `< [condition1] and [condition2] >`
- `< [condition1] or [condition2] >`
- `< not [condition] >`

---

## Value Blocks

### Variables
- `( x )` - X position
- `( y )` - Y position
- `( speed )` - Movement speed
- `( direction )` - Movement direction
- `( score )` - Current score
- `( lives )` - Current lives
- `( health )` - Current health

### Math
- `( [5] + [3] )` - Addition
- `( [10] - [2] )` - Subtraction
- `( [4] × [3] )` - Multiplication
- `( [20] ÷ [4] )` - Division
- `( random 1 to [100] )` - Random number

---

## Example: Player Movement

```
┌──────────────────────────┐
│ When key [arrow_left]    │
├──────────────────────────┤
│ set hspeed to [-4]       │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [arrow_right]   │
├──────────────────────────┤
│ set hspeed to [4]        │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ set hspeed to [0]        │
└──────────────────────────┘
```

---

## Example: Collecting Coins

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ change score by [10]        │
├─────────────────────────────┤
│ play sound [snd_coin]       │
├─────────────────────────────┤
│ destroy other instance      │
└─────────────────────────────┘
```

---

## Tips

1. **Start with Events** - Always begin with an event block (hat block)
2. **Connect Vertically** - Stack blocks connect top-to-bottom
3. **Use Colors** - Block colors indicate their category
4. **Right-click** - Access duplicate, delete, and help options
5. **Zoom** - Use scroll wheel or zoom controls for large programs

---

## Next Steps

- [[Events-and-Actions]] - See the action list equivalent
- [[Creating-Your-First-Game]] - Build a complete game
- [[Object-Editor]] - Where Blockly integrates

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

**Which blocks you see depends on your preset.** `Tools > Configure Action
Blocks...` (or `Preferences > IDE Edition`, which sets the default for new
projects) controls the block set — see the [Preset Guide](Preset-Guide) for
details. The tables below list every block that exists in any preset; a
given project may show fewer.

---

## The Blockly Workspace

### Toolbox
The left panel contains block categories:
- **Events** - Event trigger blocks
- **Control** - Conditionals, variables, and grouping (this project's
  conditional blocks are stack blocks, not classic if/else containers —
  see "Block Types" below)
- **Movement** - Motion, speed, and physics blocks
- **Timing** - Alarms
- **Drawing** - Text and shape rendering
- **Score/Lives/Health** - Game state blocks
- **Instance** - Object creation/destruction
- **Room** - Room navigation
- **Values** - Reporter blocks (position, speed, score, lives, health, mouse)
- **Sound** - Audio playback
- **Output** - Messages and custom Python code
- **Game** - End/restart game, highscore table

There is no separate Math, Text, or Logic category — number/text fields are
typed directly into each block, and there's no generic boolean/comparison
reporter block. See "Block Types" below for how conditionals work instead.

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
Stack blocks have notches that connect to other blocks. Almost every block
outside the Values category is a stack block — including the conditional
blocks:

```
├─────────────────┤
│ Set Horizontal Speed [5] │
├─────────────────┤
```

### Reporter Blocks (Values)
Reporter blocks are rounded and plug into a number field on another block
(e.g. into Move Direction's speed field, or Set Variable's value field).
This project has 9 of them — X Position, Y Position, Horizontal Speed,
Vertical Speed, Score, Lives, Health, Mouse X, Mouse Y:

```
( X Position )    ( Score )    ( 100 )
```

There's no `( speed )` or `( direction )` reporter — those aren't tracked
as single values in this engine (movement speed/direction are derived from
Horizontal Speed + Vertical Speed together), and there's no reporter for
custom variables either (read them with Test Variable's comparison instead).

### Conditionals — stack blocks, not C-block containers
Unlike Scratch-style visual languages, this project's If Condition / Test
Variable blocks are **stack blocks with one "then" slot**, not two-sided
if/else containers, and there's no hexagonal boolean reporter to plug into
them — the comparison is built from fields directly on the block:

```
┌───────────────────────────────────┐
│ If count of [obj_coin] [==] [0]   │
├───────────────────────────────────┤
│  then [actions go here]           │
└───────────────────────────────────┘
```

To add an "otherwise" branch or run more than one action on either side,
combine it with three more Control blocks:
- **Else** - runs its own next block only when the preceding test was false
- **Start Block** / **End Block** - bracket several actions so the
  preceding test (or Else) applies to the whole group, not just the next
  block

This is the same GM80-style flat conditional flow the structured
Events/Actions panel uses (see [Events and Actions](Events-and-Actions)) —
Blockly is a drag-and-drop skin over the same underlying action list, not a
separate execution model.

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
There are four separate keyboard hat blocks — Key Held, Key Press, Key
Release, and No Key — each with a key-name dropdown (No Key has none, since
it fires whenever nothing is held):
```
┌─────────────────────────┐
│ When key [held: left] ▼ │
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
| `Set Horizontal Speed [4]` | Set X velocity |
| `Set Vertical Speed [-5]` | Set Y velocity |
| `Stop Movement` | Set both speeds to zero |
| `Move [direction ▼] speed [3]` | Move in one of 4 directions (or diagonals, or "stop") |
| `Move Free [direction] [speed]` | Move at an arbitrary angle and speed |
| `Set Speed [5]` | Set speed magnitude, preserving current direction |
| `Set Direction [90]` | Set direction angle, preserving current speed |
| `Move Towards x:[100] y:[200] speed:[3]` | Move toward a point |
| `Snap to Grid` | Align position to the grid |
| `Jump to Position x:[100] y:[200]` | Instant teleport |
| `Move Grid [direction]` | Move exactly one grid cell |
| `Stop if No Keys` / `Check Keys and Move` / `If On Grid` | Grid-movement helpers |
| `Set Gravity` | Apply a constant downward (or any-direction) force each step |
| `Set Friction` | Apply speed decay each step |
| `Reverse Horizontal` / `Reverse Vertical` | Flip X or Y direction |
| `Bounce` | Reverse off solid objects |
| `Wrap Around Room` | Wrap to the opposite edge |
| `Move to Contact` | Move until touching something |

There's no "Jump to Start Position" or "Jump to Random Position" **block**
— those two actions exist only in the structured Actions panel, not in
Blockly.

---

## Drawing Blocks

| Block | Description |
|-------|-------------|
| `Draw Text [Hello] at x:[10] y:[10]` | Display text |
| `Draw Rectangle from x1,y1 to x2,y2` | Draw a filled rectangle |
| `Draw Circle at x,y radius [r]` | Draw a filled circle |
| `Set Sprite [spr]` | Change the instance's sprite |
| `Set Transparency [0-1]` | Set alpha |

There's no "Draw Sprite at position" or "Set Drawing Color" block in
Blockly (both exist as structured-editor-only actions). Draw Score/Draw
Lives/Draw Health Bar are listed under Score/Lives/Health below, not here.

---

## Score/Lives/Health Blocks

| Block | Description |
|-------|-------------|
| `Set Score [100]` | Set exact score |
| `Add to Score [10]` | Add/subtract score |
| `Set Lives [3]` | Set exact lives |
| `Add to Lives [-1]` | Add/subtract lives |
| `Set Health [100]` | Set exact health |
| `Add to Health [-25]` | Add/subtract health |
| `Draw Score` | Display score text |
| `Draw Lives` | Display lives as repeated icons |
| `Draw Health Bar` | Display health as a two-colour bar |

---

## Instance Blocks

| Block | Description |
|-------|-------------|
| `Create Instance [obj] at x:[100] y:[200]` | Spawn new instance |
| `Destroy Instance` | Remove self |
| `Destroy Other` | Remove the colliding instance (in a collision event) |
| `Change Instance [obj]` | Transform into a different object type |
| `If Can Push [obj] [direction]` | Sokoban-style push check |

There's no "destroy all of type" or "create at this position" block.

---

## Room Blocks

| Block | Description |
|-------|-------------|
| `Next Room` | Advance to next room |
| `Previous Room` | Go back one room |
| `Restart Room` | Reset current room |
| `Go to Room [room_name]` | Jump to specific room |
| `If Next Room Exists` / `If Previous Room Exists` | Guard multi-room navigation |

---

## Sound Blocks

| Block | Description |
|-------|-------------|
| `Play Sound [snd]` | Play sound effect |
| `Play Music [music]` | Play background music (loops) |
| `Stop Music` | Stop music |

There's no per-sound "Stop Sound" or "Stop All Sounds" block in Blockly
(only Stop Music, which stops music specifically).

---

## Control Blocks

| Block | Description |
|-------|-------------|
| `If count of [obj] [==] [0] then...` | Compare an object's instance count; run the next block(s) when true |
| `If variable [var] [==] [value] then...` | Compare a custom variable; run the next block(s) when true |
| `Set Variable [name] to [value]` | Assign an instance or global variable |
| `Check Empty at x,y` | True when a position has no collision (grid movement) |
| `Exit Event` | Stop running the rest of this event's actions |
| `Else` | Runs its own next block when the preceding test was false |
| `Start Block` / `End Block` | Group multiple actions under one test/Else |

---

## Output & Game Blocks

| Block | Description |
|-------|-------------|
| `Show Message [text]` | Display a popup message |
| `Execute Code` | Run custom Python (real Python — see [Events and Actions](Events-and-Actions)) |
| `End Game` | Close the game |
| `Restart Game` | Restart from the first room |
| `Show Highscore` / `Clear Highscore` | Display or reset the highscore table |

---

## Value Blocks

Reporter blocks — plug these into a number field on another block:

| Block | Description |
|-------|-------------|
| `X Position` | This instance's X coordinate |
| `Y Position` | This instance's Y coordinate |
| `Horizontal Speed` | This instance's X velocity |
| `Vertical Speed` | This instance's Y velocity |
| `Score` | Current score |
| `Lives` | Current lives |
| `Health` | Current health |
| `Mouse X` / `Mouse Y` | Current mouse position |

---

## Example: Player Movement

```
┌──────────────────────────┐
│ When key [held: left]    │
├──────────────────────────┤
│ Set Horizontal Speed [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ When key [held: right]   │
├──────────────────────────┤
│ Set Horizontal Speed [4] │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ Set Horizontal Speed [0] │
└──────────────────────────┘
```

---

## Example: Collecting Coins

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ Add to Score [10]           │
├─────────────────────────────┤
│ Play Sound [snd_coin]       │
├─────────────────────────────┤
│ Destroy Other                │
└─────────────────────────────┘
```

---

## Tips

1. **Start with Events** - Always begin with an event block (hat block)
2. **Connect Vertically** - Stack blocks connect top-to-bottom
3. **Use Colors** - Block colors indicate their category
4. **Right-click** - Access duplicate, delete, and help options
5. **Zoom** - Use scroll wheel or zoom controls for large programs
6. **Switching to the structured panel** - Everything Blockly can do maps
   to an action in the Events tab's structured panel, and the reverse
   isn't always true (e.g. Jump to Start/Random Position and per-sound
   Stop Sound have no Blockly block) — if you need one of those, use the
   structured panel for that event instead of Blockly.

---

## Next Steps

- [[Events-and-Actions]] - See the action list equivalent
- [[Creating-Your-First-Game]] - Build a complete game
- [[Object-Editor]] - Where Blockly integrates
- [[Preset-Guide]] - Which blocks are available in your project

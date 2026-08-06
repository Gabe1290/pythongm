# Tutorial: Create a Sokoban Puzzle Game

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Introduction

In this tutorial, you'll create a **Sokoban** puzzle game - a classic box-pushing puzzle where the player must push all crates onto target locations. Sokoban (meaning "warehouse keeper" in Japanese) is perfect for learning grid-based movement and puzzle game logic.

**What you'll learn:**
- Grid-based movement (moving in fixed steps)
- Push mechanics for moving objects
- Collision detection with multiple object types
- Win condition detection
- Level design for puzzle games

**Difficulty:** Beginner
**Preset:** Intermediate Preset (the push mechanic and grid movement used
here aren't in the Beginner preset)

---

## Step 1: Understand the Game

### Game Rules
1. The player can move up, down, left, or right
2. The player can push crates (but not pull them)
3. Only one crate can be pushed at a time
4. Crates cannot be pushed through walls or other crates
5. The level is complete when all crates are on target spots

### What We Need

| Element | Purpose |
|---------|---------|
| **Player** | The warehouse keeper you control |
| **Crate** | Boxes the player pushes |
| **Wall** | Solid obstacles that block movement |
| **Target** | Goal spots where crates must be placed |
| **Floor** | Walkable ground (optional visual) |

---

## Step 2: Create the Sprites

All sprites should be the same size (32x32 pixels works well) to create a proper grid.

### 2.1 Player Sprite

1. In the **Resource Tree**, right-click on **Sprites** and select **Create Sprite**
2. Name it `spr_player`
3. Click **Edit Sprite** to open the sprite editor
4. Draw a simple character (a person or robot shape)
5. Use a distinct color like blue or green
6. Size: 32x32 pixels
7. Click **OK** to save

### 2.2 Crate Sprite

1. Create a new sprite named `spr_crate`
2. Draw a wooden crate or box shape
3. Use brown or orange colors
4. Size: 32x32 pixels

### 2.3 Crate on Target Sprite

1. Create a new sprite named `spr_crate_ok`
2. Draw the same crate but with a different color (green) to show it's correctly placed
3. Size: 32x32 pixels

### 2.4 Wall Sprite

1. Create a new sprite named `spr_wall`
2. Draw a solid brick or stone pattern
3. Use gray or dark colors
4. Size: 32x32 pixels

### 2.5 Target Sprite

1. Create a new sprite named `spr_target`
2. Draw an X mark or a goal indicator
3. Use a bright color like red or yellow
4. Size: 32x32 pixels

### 2.6 Floor Sprite (Optional)

1. Create a new sprite named `spr_floor`
2. Draw a simple floor tile pattern
3. Use a neutral color
4. Size: 32x32 pixels

---

## Step 3: Create the Wall Object

The wall is the simplest object - it just blocks movement.

1. Right-click on **Objects** and select **Create Object**
2. Name it `obj_wall`
3. Set the sprite to `spr_wall`
4. **Check the "Solid" checkbox**
5. No events needed

---

## Step 4: Create the Target Object

Targets mark where crates should be placed.

1. Create a new object named `obj_target`
2. Set the sprite to `spr_target`
3. No events needed - it's just a marker
4. Leave "Solid" unchecked (player and crates can be on top of it)

---

## Step 5: Create the Crate Object

The crate is pushed by the player and changes appearance when on a target.

1. Create a new object named `obj_crate`
2. Set the sprite to `spr_crate`
3. **Check the "Solid" checkbox**

**Event: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Add Action: **Control** → **Else**
5. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

This makes the crate turn green when it's on a target spot — **If Collision**
with both offsets at `0` checks whether the crate's *current* position
overlaps an `obj_target`.

---

## Step 6: Create the Player Object

The player moves one grid cell at a time and pushes crates it walks into.

1. Create a new object named `obj_player`
2. Set the sprite to `spr_player`

### 6.1 Grid Movement

Add one **Key Press** event per direction, each with a **Move** → **Move Grid** action:

| Event | Move Grid action |
|---|---|
| Key Press → Right Arrow | Direction: `right`, Grid Size: `32` |
| Key Press → Left Arrow | Direction: `left`, Grid Size: `32` |
| Key Press → Up Arrow | Direction: `up`, Grid Size: `32` |
| Key Press → Down Arrow | Direction: `down`, Grid Size: `32` |

**Move Grid** steps the instance exactly one grid cell and is collision-aware on its
own — it won't move the player into a solid `obj_wall`, so no extra wall check is
needed here.

### 6.2 Stop at Walls

**Event: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

### 6.3 Push Crates

**Event: Collision with obj_crate**
1. Add Event → Collision → `obj_crate`
2. Add Action: **Control** → **If Can Push**
   - Direction: `facing`
   - Object Type: `obj_crate`
   - Then Action: `push_and_move`

**If Can Push** checks whether the space behind the crate (in the direction the
player is moving) is free, and — if so — pushes the crate one cell and moves the
player into its place, all in a single action. If the space behind the crate is
blocked by a wall or another crate, nothing moves.

---

## Step 7: Create the Win Condition Checker

We need an invisible controller that watches whether every crate is on a target.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Create** — set up the target count once, using **Control** → **Execute
Code** (this project's Execute Code action runs real Python, not GameMaker
Language — `self` is the current instance, `game` is the game runner):

```python
# Count how many target spots exist in the room
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Event: Step** — check every frame whether all crates are on a target:

```python
# Count crates currently overlapping a target
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` is how a raw Execute Code block triggers the same
room restart the **Restart Room** action performs — the main loop checks it every
frame. Add a **Show Message** action (from **Output**, message `Level Complete!`)
right after the Execute Code block if you want a popup before the restart.

**Event: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Step 9: Design Your Level

1. Right-click on **Rooms** and select **Create Room**
2. Name it `room_level1`
3. Set the room size to a multiple of 32 (e.g., 640x480)
4. Enable "Snap to Grid" and set grid to 32x32

### Placing Objects

Build your level following these guidelines:

1. **Surround the level with walls** - Create a border
2. **Add internal walls** - Create the puzzle structure
3. **Place targets** - Where crates need to go
4. **Place crates** - Same number as targets!
5. **Place the player** - Starting position
6. **Place the game controller** - Anywhere (it's invisible)

### Example Level Layout

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Wall
P = Player
C = Crate
T = Target
. = Empty floor
```

**Important:** Always have the same number of crates and targets!

---

## Step 10: Test Your Game!

1. Click **Run** or press **F5** to test
2. Use arrow keys to move
3. Push crates onto the red X targets
4. When all crates are on targets, you win!

---

## Enhancements (Optional)

### Add a Move Counter

In `obj_game_controller`'s **Create** event, add **Control** → **Set Variable**
(Variable: `global.moves`, Value: `0`, Scope: `global`).

In each of `obj_player`'s four **Move Grid** key-press events, add a second
action right after Move Grid: **Control** → **Set Variable** (Variable:
`global.moves`, Value: `1`, Scope: `global`, **Relative** checked) — this adds
1 to the counter every key press, whether or not the move was actually blocked
by a wall.

In `obj_game_controller`'s **Draw** event, add **Draw** → **Draw Variable**
(Variable: `global.moves`, X: `10`, Y: `30`).

### Add Undo Feature

Store previous positions and allow pressing Z to undo the last move.

### Add Multiple Levels

Create more rooms (`room_level2`, `room_level3`, etc.) and use the **Next
Room** action (Room category) instead of **Restart Room** in the win-check
Execute Code block (`self.next_room_flag = True` instead of
`self.restart_room_flag = True`) when completing a level.

### Add Sound Effects

Add sounds for:
- Player moving
- Pushing a crate
- Crate landing on target
- Level complete

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Player moves through walls | Check that `obj_wall` has "Solid" checked |
| Crate doesn't change color | Verify the Step event's **If Collision** action targets `obj_target` |
| Can push crate through wall | Check collision detection before moving crate |
| Win message appears immediately | Make sure targets are placed separately from crates |
| Player moves multiple squares | Use Keyboard Press event, not Keyboard event |

---

## What You Learned

Congratulations! You've created a complete Sokoban puzzle game! You learned:

- **Grid-based movement** - Moving in fixed 32-pixel steps
- **Push mechanics** - Detecting and moving objects the player pushes
- **Complex collision logic** - Checking multiple conditions before allowing movement
- **State changes** - Changing sprite based on object position
- **Win conditions** - Checking when all objectives are complete
- **Level design** - Creating solvable puzzle layouts

---

## Challenge: Design Your Own Levels!

The real fun of Sokoban is designing puzzles. Try creating levels that:
- Start easy and get progressively harder
- Require planning ahead
- Have only one solution
- Use minimal space efficiently

Remember: A good Sokoban puzzle should be challenging but fair!

---

## See Also

- [Tutorials](Tutorials) - More game tutorials
- [Intermediate Preset](Intermediate-Preset) - Overview of the preset this tutorial needs
- [Tutorial: Pong](Tutorial-Pong) - Create a two-player game
- [Tutorial: Breakout](Tutorial-Breakout) - Create a brick breaker game
- [Event Reference](Event-Reference) - Complete event documentation

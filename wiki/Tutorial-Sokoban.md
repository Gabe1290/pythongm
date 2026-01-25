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
**Preset:** Beginner Preset

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
2. Add Action: **Control** → **Test Variable**
   - Variable: `place_meeting(x, y, obj_target)`
   - Value: `1`
   - Operation: Equal to
3. Add Action: **Main1** → **Change Sprite**
   - Sprite: `spr_crate_ok`
   - Subimage: `0`
   - Speed: `1`
4. Add Action: **Control** → **Else**
5. Add Action: **Main1** → **Change Sprite**
   - Sprite: `spr_crate`
   - Subimage: `0`
   - Speed: `1`

This makes the crate turn green when it's on a target spot.

---

## Step 6: Create the Player Object

The player is the most complex object with grid-based movement and push mechanics.

1. Create a new object named `obj_player`
2. Set the sprite to `spr_player`

### 6.1 Moving Right

**Event: Keyboard Press Right Arrow**
1. Add Event → Keyboard → Press Right

First, check if there's a wall in the way:
2. Add Action: **Control** → **Test Collision**
   - Object: `obj_wall`
   - X: `32`
   - Y: `0`
   - Check: NOT (meaning "if there's NO wall")

If no wall, check if there's a crate:
3. Add Action: **Control** → **Test Collision**
   - Object: `obj_crate`
   - X: `32`
   - Y: `0`

If there's a crate, we need to check if we can push it:
4. Add Action: **Control** → **Test Collision** (for the crate's destination)
   - Object: `obj_wall`
   - X: `64`
   - Y: `0`
   - Check: NOT

5. Add Action: **Control** → **Test Collision**
   - Object: `obj_crate`
   - X: `64`
   - Y: `0`
   - Check: NOT

If both checks pass, push the crate:
6. Add Action: **Control** → **Code Block**
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Now move the player:
7. Add Action: **Move** → **Jump to Position**
   - X: `32`
   - Y: `0`
   - Check "Relative"

### 6.2 Moving Left

**Event: Keyboard Press Left Arrow**
Follow the same pattern as moving right, but use:
- X offset: `-32` for checking wall/crate
- X offset: `-64` for checking if crate can be pushed
- Move crate by `-32`
- Jump to position X: `-32`

### 6.3 Moving Up

**Event: Keyboard Press Up Arrow**
Follow the same pattern, but use Y values:
- Y offset: `-32` for checking
- Y offset: `-64` for crate destination
- Move crate by Y: `-32`
- Jump to position Y: `-32`

### 6.4 Moving Down

**Event: Keyboard Press Down Arrow**
Use:
- Y offset: `32` for checking
- Y offset: `64` for crate destination
- Move crate by Y: `32`
- Jump to position Y: `32`

---

## Step 7: Simplified Player Movement (Alternative)

If the block-based approach above seems complex, here's a simpler code-based approach for each direction:

**Event: Keyboard Press Right Arrow**
Add Action: **Control** → **Execute Code**
```
// Check if we can move right
if (!place_meeting(x + 32, y, obj_wall)) {
    // Check if there's a crate
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // There's a crate - can we push it?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // No crate, just move
        x += 32;
    }
}
```

Repeat for other directions with appropriate coordinate changes.

---

## Step 8: Create the Win Condition Checker

We need an object to check if all crates are on targets.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Create**
1. Add Event → Create
2. Add Action: **Score** → **Set Variable**
   - Variable: `global.total_targets`
   - Value: `0`
3. Add Action: **Control** → **Execute Code**
```
// Count how many targets exist
global.total_targets = instance_number(obj_target);
```

**Event: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **Execute Code**
```
// Count crates that are on targets
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Check if all targets have crates
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Level complete!
    show_message("Level Complete!");
    room_restart();
}
```

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

In `obj_game_controller`:

**Event: Create** - Add:
```
global.moves = 0;
```

In `obj_player`, after each successful move, add:
```
global.moves += 1;
```

In `obj_game_controller` **Event: Draw** - Add:
```
draw_text(10, 30, "Moves: " + string(global.moves));
```

### Add Undo Feature

Store previous positions and allow pressing Z to undo the last move.

### Add Multiple Levels

Create more rooms (`room_level2`, `room_level3`, etc.) and use:
```
room_goto_next();
```
instead of `room_restart()` when completing a level.

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
| Crate doesn't change color | Verify the Step event checks `place_meeting` correctly |
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
- [Beginner Preset](Beginner-Preset) - Overview of beginner features
- [Tutorial: Pong](Tutorial-Pong) - Create a two-player game
- [Tutorial: Breakout](Tutorial-Breakout) - Create a brick breaker game
- [Event Reference](Event-Reference) - Complete event documentation

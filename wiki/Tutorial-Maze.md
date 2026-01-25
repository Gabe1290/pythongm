# Tutorial: Create a Maze Game

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Introduction

In this tutorial, you'll create a **Maze Game** where the player navigates through corridors to reach the exit while avoiding obstacles and collecting coins. This classic game type is perfect for learning smooth movement, collision detection, and level design.

**What you'll learn:**
- Smooth player movement with keyboard input
- Wall collision handling
- Goal detection (reaching the exit)
- Collectible items
- Simple timer system

**Difficulty:** Beginner
**Preset:** Beginner Preset

---

## Step 1: Understand the Game

### Game Rules
1. The player moves through a maze using arrow keys
2. Walls block the player's movement
3. Collect coins for points
4. Reach the exit to complete the level
5. Complete the maze as fast as possible!

### What We Need

| Element | Purpose |
|---------|---------|
| **Player** | The character you control |
| **Wall** | Solid obstacles that block movement |
| **Exit** | Goal that ends the level |
| **Coin** | Collectible items for score |
| **Floor** | Visual background (optional) |

---

## Step 2: Create the Sprites

All wall and floor sprites should be 32x32 pixels to create a proper grid.

### 2.1 Player Sprite

1. In the **Resource Tree**, right-click on **Sprites** and select **Create Sprite**
2. Name it `spr_player`
3. Click **Edit Sprite** to open the sprite editor
4. Draw a small character (circle, person, or arrow shape)
5. Use a bright color like blue or green
6. Size: 24x24 pixels (smaller than walls for easier navigation)
7. Click **OK** to save

### 2.2 Wall Sprite

1. Create a new sprite named `spr_wall`
2. Draw a solid brick or stone pattern
3. Use gray or dark colors
4. Size: 32x32 pixels

### 2.3 Exit Sprite

1. Create a new sprite named `spr_exit`
2. Draw a door, flag, or bright goal marker
3. Use green or gold colors
4. Size: 32x32 pixels

### 2.4 Coin Sprite

1. Create a new sprite named `spr_coin`
2. Draw a small yellow/gold circle
3. Size: 16x16 pixels

### 2.5 Floor Sprite (Optional)

1. Create a new sprite named `spr_floor`
2. Draw a simple floor tile pattern
3. Use a light neutral color
4. Size: 32x32 pixels

---

## Step 3: Create the Wall Object

The wall blocks player movement.

1. Right-click on **Objects** and select **Create Object**
2. Name it `obj_wall`
3. Set the sprite to `spr_wall`
4. **Check the "Solid" checkbox**
5. No events needed

---

## Step 4: Create the Exit Object

The exit ends the level when the player reaches it.

1. Create a new object named `obj_exit`
2. Set the sprite to `spr_exit`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Main2** → **Show Message**
   - Message: `You Win! Time: ` + string(floor(global.timer)) + ` seconds`
3. Add Action: **Main1** → **Next Room** (or **Restart Room** for single level)

---

## Step 5: Create the Coin Object

Coins add to the score when collected.

1. Create a new object named `obj_coin`
2. Set the sprite to `spr_coin`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Check "Relative" to add 10 points
3. Add Action: **Main1** → **Destroy Instance**
   - Applies to: Self

---

## Step 6: Create the Player Object

The player moves smoothly using arrow keys.

1. Create a new object named `obj_player`
2. Set the sprite to `spr_player`

### 6.1 Create Event - Initialize Variables

**Event: Create**
1. Add Event → Create
2. Add Action: **Control** → **Set Variable**
   - Variable: `move_speed`
   - Value: `4`

### 6.2 Movement with Collision

**Event: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **Execute Code**

```gml
// Horizontal movement
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Vertical movement
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Horizontal collision check
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // Move as close to wall as possible
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Vertical collision check
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // Move as close to wall as possible
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternative: Simple Block Movement

If you prefer using action blocks instead of code:

**Event: Keyboard Down - Right Arrow**
1. Add Event → Keyboard → \<Right\>
2. Add Action: **Control** → **Test Collision**
   - Object: `obj_wall`
   - X: `4`
   - Y: `0`
   - Check: NOT
3. Add Action: **Move** → **Jump to Position**
   - X: `4`
   - Y: `0`
   - Check "Relative"

Repeat for Left (-4, 0), Up (0, -4), and Down (0, 4).

---

## Step 7: Create the Game Controller

The game controller manages the timer and displays information.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Create**
1. Add Event → Create
2. Add Action: **Control** → **Set Variable**
   - Variable: `global.timer`
   - Value: `0`

**Event: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **Set Variable**
   - Variable: `global.timer`
   - Value: `1/room_speed`
   - Check "Relative"

**Event: Draw**
1. Add Event → Draw → Draw
2. Add Action: **Control** → **Execute Code**

```gml
// Draw score
draw_set_color(c_white);
draw_text(10, 10, "Score: " + string(score));

// Draw timer
draw_text(10, 30, "Time: " + string(floor(global.timer)) + "s");

// Draw coins remaining
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Coins: " + string(coins_left));
```

---

## Step 8: Design Your Maze

1. Right-click on **Rooms** and select **Create Room**
2. Name it `room_maze`
3. Set the room size (e.g., 640x480)
4. Enable "Snap to Grid" and set grid to 32x32

### Placing Objects

Build your maze following these guidelines:

1. **Create the border** - Surround the room with walls
2. **Build corridors** - Create paths through the maze
3. **Place the exit** - Put it at the end of the maze
4. **Scatter coins** - Place them throughout the paths
5. **Place the player** - Near the entrance
6. **Add game controller** - Anywhere (it's invisible)

### Example Maze Layout

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Wall    P = Player    E = Exit    C = Coin    . = Empty
```

---

## Step 9: Test Your Game!

1. Click **Run** or press **F5** to test
2. Use arrow keys to navigate the maze
3. Collect coins for points
4. Find the exit to win!

---

## Enhancements (Optional)

### Add Enemies

Create a simple patrolling enemy:

1. Create `spr_enemy` (red colored, 24x24)
2. Create `obj_enemy` with sprite `spr_enemy`

**Event: Create**
```gml
hspeed = 2;  // Moves horizontally
```

**Event: Collision with obj_wall**
```gml
hspeed = -hspeed;  // Reverse direction
```

**Event: Collision with obj_player**
```gml
room_restart();  // Player loses
```

### Add a Lives System

In `obj_game_controller` Create event:
```gml
global.lives = 3;
```

When player hits enemy (instead of restarting):
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Game Over!");
    game_restart();
} else {
    // Respawn player at start
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Add Keys and Locked Doors

1. Create `obj_key` - disappears when collected, sets `global.has_key = true`
2. Create `obj_locked_door` - only opens when `global.has_key == true`

### Add Multiple Levels

1. Create additional rooms (`room_maze2`, `room_maze3`)
2. In `obj_exit`, use `room_goto_next()` instead of `room_restart()`

### Add Sound Effects

Add sounds for:
- Collecting coins
- Reaching the exit
- Hitting enemies (if added)
- Background music

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Player moves through walls | Check that `obj_wall` has "Solid" checked |
| Player gets stuck in walls | Make sure player sprite is smaller than wall gaps |
| Coins don't disappear | Verify collision event destroys Self, not Other |
| Timer doesn't work | Ensure game controller is placed in the room |
| Movement feels jerky | Adjust `move_speed` value (try 3-5) |

---

## What You Learned

Congratulations! You've created a maze game! You learned:

- **Smooth movement** - Checking keyboard held state for continuous movement
- **Collision detection** - Using `place_meeting` to check before moving
- **Pixel-perfect collision** - Moving as close to walls as possible
- **Collectibles** - Creating items that increase score and disappear
- **Timer system** - Tracking elapsed time with variables
- **Level design** - Creating navigable maze layouts

---

## Challenge Ideas

1. **Time Attack** - Add a countdown timer. Reach the exit before time runs out!
2. **Perfect Score** - Require collecting all coins before the exit opens
3. **Random Maze** - Research procedural maze generation
4. **Fog of War** - Only show the area around the player
5. **Minimap** - Display a small overview of the maze

---

## See Also

- [Tutorials](Tutorials) - More game tutorials
- [Beginner Preset](Beginner-Preset) - Overview of beginner features
- [Tutorial: Pong](Tutorial-Pong) - Create a two-player game
- [Tutorial: Breakout](Tutorial-Breakout) - Create a brick breaker game
- [Tutorial: Sokoban](Tutorial-Sokoban) - Create a box-pushing puzzle
- [Event Reference](Event-Reference) - Complete event documentation

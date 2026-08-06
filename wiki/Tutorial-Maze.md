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
**Preset:** Intermediate Preset (the Execute Code action used for the timer
isn't in the Beginner preset)

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
2. Add Action: **Output** → **Show Message**
   - Message: `You Win!`
3. Add Action: **Room** → **Next Room** (or **Restart Room** for single level)

Show Message's text is a plain, static string — it can't embed a live value
like the elapsed time. The timer stays visible in the HUD (Step 7) right up
to the win, so the player has already seen their time.

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

### 6.1 Movement

Add four **Keyboard** (held) events plus a **No Key** event, each with a
**Move** → **Set Horizontal/Vertical Speed** action:

| Event | Action |
|---|---|
| Keyboard (held) → Right Arrow | Set Horizontal Speed to `4` |
| Keyboard (held) → Left Arrow | Set Horizontal Speed to `-4` |
| Keyboard (held) → Down Arrow | Set Vertical Speed to `4` |
| Keyboard (held) → Up Arrow | Set Vertical Speed to `-4` |
| Keyboard: No Key | Set Horizontal Speed to `0` **and** Set Vertical Speed to `0` |

### 6.2 Stop at Walls

**Event: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

No manual position-checking code is needed here. This engine's movement
loop already refuses to move an instance into a solid object before the
frame is drawn (`obj_wall` is Solid), so the player can never actually
overlap a wall — the collision event above just zeroes any leftover
speed so the player doesn't keep "pushing" against it.

---

## Step 7: Create the Game Controller

The game controller manages the timer and displays information.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Create** — start the timer, using **Control** → **Execute Code**
(this project's Execute Code action runs real Python, not GameMaker
Language):

```python
self.timer = 0.0
```

**Event: Step** — advance it every frame:

```python
self.timer += 1.0 / game.fps
```

**Event: Draw** — build the HUD from real draw-queue commands. Add three
**Draw** → **Draw Text** actions:

| Draw Text action | Text | Position |
|---|---|---|
| 1st | `Score:` | X `10`, Y `10` |
| 2nd | `Time:` | X `10`, Y `30` |
| 3rd | `Coins:` | X `10`, Y `50` |

then three **Draw** → **Draw Variable** actions right after them to show the
live numbers next to each label:

| Draw Variable action | Variable | Position |
|---|---|---|
| 1st | `score` | X `70`, Y `10` |
| 2nd | `self.timer` | X `70`, Y `30` |
| 3rd | *(see below)* | X `70`, Y `50` |

There's no built-in "coins remaining" counter to point Draw Variable at —
add one more **Control** → **Execute Code** action, right before the Draw
Variable actions, to compute it into an instance variable Draw Variable can
then read:

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(then set the 3rd Draw Variable's Variable field to `self.coins_left`).

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

**Event: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Event: Collision with obj_wall** — Add Action: **Move** → **Reverse
Horizontal** (turns the enemy around when it hits a wall — no code needed;
combined with the built-in solid collision from Step 6.2, the enemy can
never walk through a wall in the first place)

**Event: Collision with obj_player** — Add Action: **Room** → **Restart
Room**

### Add a Lives System

In `obj_game_controller`'s **Create** event, add **Score** → **Set Lives**
(Value: `3`).

In `obj_enemy`'s **Collision with obj_player** event, replace **Restart
Room** with two actions: **Score** → **Set Lives** (Value: `-1`, **Relative**
checked), then **Move** → **Jump to Start Position** (on the player, via
**Applies to: Other**) to respawn the player instead of restarting the whole
maze.

Add one more event to `obj_game_controller`: **Other Events** → **No More
Lives** — this fires automatically the moment lives reach 0, so you don't
poll it yourself. Add **Output** → **Show Message** (`Game Over!`) followed
by **Room** → **Restart Game**.

### Add Keys and Locked Doors

1. Create `obj_key` — on collision with `obj_player`, **Set Variable**
   (Variable: `global.has_key`, Value: `true`, Scope: `global`), then
   **Destroy Instance** (self).
2. Create `obj_locked_door`, Solid checked. Give it a **Step** event with
   **Control** → **Test Variable** (Variable: `global.has_key`, Value:
   `true`, Scope: `global`) → **Instance** → **Destroy Instance** (self) —
   the door disappears (and stops blocking) as soon as the key is picked up.

### Add Multiple Levels

1. Create additional rooms (`room_maze2`, `room_maze3`)
2. In `obj_exit`, use the **Next Room** action instead of **Restart Room**

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
- **Built-in solid collision** - Walls block movement automatically once marked Solid, no manual position-checking code needed
- **Collectibles** - Creating items that increase score and disappear
- **Timer system** - Tracking elapsed time with instance variables
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
- [Intermediate Preset](Intermediate-Preset) - Overview of the preset this tutorial needs
- [Tutorial: Pong](Tutorial-Pong) - Create a two-player game
- [Tutorial: Breakout](Tutorial-Breakout) - Create a brick breaker game
- [Tutorial: Sokoban](Tutorial-Sokoban) - Create a box-pushing puzzle
- [Event Reference](Event-Reference) - Complete event documentation

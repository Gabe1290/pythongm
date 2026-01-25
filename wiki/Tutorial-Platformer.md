# Tutorial: Create a Platformer Game

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introduction

In this tutorial, you'll create a **Platformer Game** - a side-scrolling action game where the player runs, jumps, and navigates platforms while avoiding hazards and collecting coins. This classic genre is perfect for learning gravity, jumping mechanics, and platform collision.

**What you'll learn:**
- Gravity and falling physics
- Jump mechanics with ground detection
- Platform collision (landing on top)
- Left/right movement
- Collectibles and hazards

**Difficulty:** Beginner
**Preset:** Beginner Preset

---

## Step 1: Understand the Game

### Game Mechanics
1. The player is affected by gravity and falls down
2. The player can move left and right
3. The player can jump when standing on ground
4. Platforms stop the player from falling through
5. Collect coins for points
6. Reach the flag to complete the level

### What We Need

| Element | Purpose |
|---------|---------|
| **Player** | The character you control |
| **Ground/Platform** | Solid surfaces to stand on |
| **Coin** | Collectible items for score |
| **Spike** | Hazard that hurts the player |
| **Flag** | Goal that ends the level |

---

## Step 2: Create the Sprites

### 2.1 Player Sprite

1. In the **Resource Tree**, right-click on **Sprites** and select **Create Sprite**
2. Name it `spr_player`
3. Click **Edit Sprite** to open the sprite editor
4. Draw a simple character (rectangle with face, or stick figure)
5. Use a bright color like blue or red
6. Size: 32x48 pixels (taller than wide for a character)
7. Click **OK** to save

### 2.2 Ground Sprite

1. Create a new sprite named `spr_ground`
2. Draw a grass/dirt platform tile
3. Use brown and green colors
4. Size: 32x32 pixels

### 2.3 Platform Sprite

1. Create a new sprite named `spr_platform`
2. Draw a floating platform (wood or stone)
3. Size: 64x16 pixels (wide and thin)

### 2.4 Coin Sprite

1. Create a new sprite named `spr_coin`
2. Draw a small yellow/gold circle
3. Size: 16x16 pixels

### 2.5 Spike Sprite

1. Create a new sprite named `spr_spike`
2. Draw triangle spikes pointing up
3. Use gray or red colors
4. Size: 32x32 pixels

### 2.6 Flag Sprite

1. Create a new sprite named `spr_flag`
2. Draw a flag on a pole
3. Use bright colors (green flag, brown pole)
4. Size: 32x64 pixels

---

## Step 3: Create the Ground Object

The ground is a solid platform that stops the player from falling.

1. Right-click on **Objects** and select **Create Object**
2. Name it `obj_ground`
3. Set the sprite to `spr_ground`
4. **Check the "Solid" checkbox**
5. No events needed

---

## Step 4: Create the Platform Object

Platforms work the same as ground but can be placed in the air.

1. Create a new object named `obj_platform`
2. Set the sprite to `spr_platform`
3. **Check the "Solid" checkbox**
4. No events needed

**Tip:** You can make the platform a child of `obj_ground` to share the same collision behavior.

---

## Step 5: Create the Player Object

The player is the most complex object with gravity, jumping, and movement.

1. Create a new object named `obj_player`
2. Set the sprite to `spr_player`

### 5.1 Create Event - Initialize Variables

**Event: Create**
1. Add Event → Create
2. Add Action: **Control** → **Execute Code**

```gml
// Movement variables
hspeed_max = 4;      // Maximum horizontal speed
vspeed_max = 10;     // Maximum fall speed
jump_force = -10;    // Jump strength (negative = up)
gravity_force = 0.5; // How fast we fall

// Current speeds
hsp = 0;
vsp = 0;

// State
on_ground = false;
```

### 5.2 Step Event - Movement and Physics

**Event: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **Execute Code**

```gml
// === HORIZONTAL MOVEMENT ===
// Get input
var move_input = keyboard_check(vk_right) - keyboard_check(vk_left);

// Set horizontal speed
hsp = move_input * hspeed_max;

// === GRAVITY ===
// Apply gravity
vsp += gravity_force;

// Cap fall speed
if (vsp > vspeed_max) {
    vsp = vspeed_max;
}

// === GROUND CHECK ===
// Check if we're on ground (1 pixel below us)
on_ground = place_meeting(x, y + 1, obj_ground);

// === JUMPING ===
// Jump if on ground and pressing up/space
if (on_ground && (keyboard_check_pressed(vk_up) || keyboard_check_pressed(vk_space))) {
    vsp = jump_force;
}

// === HORIZONTAL COLLISION ===
if (place_meeting(x + hsp, y, obj_ground)) {
    // Move as close as possible
    while (!place_meeting(x + sign(hsp), y, obj_ground)) {
        x += sign(hsp);
    }
    hsp = 0;
}
x += hsp;

// === VERTICAL COLLISION ===
if (place_meeting(x, y + vsp, obj_ground)) {
    // Move as close as possible
    while (!place_meeting(x, y + sign(vsp), obj_ground)) {
        y += sign(vsp);
    }
    vsp = 0;
}
y += vsp;
```

---

## Step 6: Create the Coin Object

Coins add to the score when collected.

1. Create a new object named `obj_coin`
2. Set the sprite to `spr_coin`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Check "Relative"
3. Add Action: **Main1** → **Destroy Instance**
   - Applies to: Self

---

## Step 7: Create the Spike Object

Spikes hurt the player and restart the level.

1. Create a new object named `obj_spike`
2. Set the sprite to `spr_spike`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Main2** → **Show Message**
   - Message: `Ouch! You hit a spike!`
3. Add Action: **Main1** → **Restart Room**

---

## Step 8: Create the Flag Object

The flag ends the level when the player reaches it.

1. Create a new object named `obj_flag`
2. Set the sprite to `spr_flag`

**Event: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Main2** → **Show Message**
   - Message: `Level Complete! Score: ` + string(score)
3. Add Action: **Main1** → **Next Room** (or **Restart Room** for single level)

---

## Step 9: Create the Game Controller

The game controller displays the score.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Draw**
1. Add Event → Draw → Draw
2. Add Action: **Control** → **Execute Code**

```gml
draw_set_color(c_white);
draw_text(10, 10, "Score: " + string(score));

// Optional: Draw lives
// draw_text(10, 30, "Lives: " + string(global.lives));
```

---

## Step 10: Design Your Level

1. Right-click on **Rooms** and select **Create Room**
2. Name it `room_level1`
3. Set the room size (e.g., 800x480)
4. Enable "Snap to Grid" and set grid to 32x32

### Placing Objects

Build your level following these guidelines:

1. **Create ground** - Place `obj_ground` along the bottom
2. **Add platforms** - Place `obj_platform` in the air for jumping challenges
3. **Add gaps** - Leave spaces in the ground (pits)
4. **Place coins** - Scatter them on platforms and in hard-to-reach spots
5. **Add spikes** - Place near pits or on platforms for challenge
6. **Place the flag** - At the end of the level
7. **Place the player** - At the start (left side)
8. **Add game controller** - Anywhere (it's invisible)

### Example Level Layout

```
                                        F
                                      ===
                          C       C
                        =====   =====
            C                           C
          ===== X     X         X     =====
    P                   C
  ====== === ===   ===   === === ===== ======
  GGGGGG     GGG   GGG   GGG         GGGGGGGG

G = Ground    P = Player    F = Flag    C = Coin
X = Spike     === = Platform
```

---

## Step 11: Test Your Game!

1. Click **Run** or press **F5** to test
2. Use **Left/Right** arrows to move
3. Press **Up** or **Space** to jump
4. Collect coins for points
5. Avoid spikes!
6. Reach the flag to win!

---

## Enhancements (Optional)

### Add Variable Jump Height

In the Step event, add this after jump code:
```gml
// Variable jump - release early for short jump
if (vsp < 0 && !keyboard_check(vk_up) && !keyboard_check(vk_space)) {
    vsp = max(vsp, jump_force / 2);
}
```

### Add Double Jump

In Create event:
```gml
can_double_jump = true;
```

In Step event (modify jump section):
```gml
if (keyboard_check_pressed(vk_up) || keyboard_check_pressed(vk_space)) {
    if (on_ground) {
        vsp = jump_force;
        can_double_jump = true;
    } else if (can_double_jump) {
        vsp = jump_force;
        can_double_jump = false;
    }
}
```

### Add Moving Platforms

1. Create `obj_moving_platform` as a child of `obj_platform`

**Event: Create**
```gml
move_distance = 100;
start_x = x;
hspeed = 2;
```

**Event: Step**
```gml
if (x > start_x + move_distance) hspeed = -2;
if (x < start_x) hspeed = 2;
```

### Add Enemy

1. Create `obj_enemy` with a simple AI

**Event: Create**
```gml
hspeed = 2;
```

**Event: Collision with obj_ground (horizontal)**
```gml
hspeed = -hspeed;  // Reverse at walls
```

**Event: Collision with obj_player**
```gml
// Check if player is above (stomping)
if (other.y < y - 16) {
    instance_destroy();
    with (other) { vsp = jump_force / 2; }
} else {
    room_restart();  // Player dies
}
```

### Add Lives System

In `obj_game_controller` Create event:
```gml
if (!variable_global_exists("lives")) {
    global.lives = 3;
}
```

When player dies:
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Game Over!");
    global.lives = 3;
    room_goto_first();
} else {
    room_restart();
}
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Player falls through ground | Check that `obj_ground` has "Solid" checked |
| Player can't jump | Verify `on_ground` check is working; ground must be solid |
| Player gets stuck in walls | Make sure collision code moves pixel by pixel |
| Jump feels floaty | Increase `gravity_force` or make `jump_force` more negative |
| Jump feels too weak | Decrease `gravity_force` or make `jump_force` more negative |

---

## What You Learned

Congratulations! You've created a platformer game! You learned:

- **Gravity physics** - Applying constant downward force
- **Jump mechanics** - Setting negative vertical speed when on ground
- **Ground detection** - Using `place_meeting` to check what's below
- **Collision handling** - Moving pixel by pixel to walls
- **Hazards** - Creating objects that restart the level
- **Level design** - Building platforming challenges

---

## Challenge Ideas

1. **Wall Jump** - Allow jumping off walls
2. **Dash Move** - Quick horizontal burst of speed
3. **Crumbling Platforms** - Platforms that fall after stepped on
4. **Checkpoints** - Save progress mid-level
5. **Boss Battle** - Add a final enemy with multiple hits

---

## See Also

- [Tutorials](Tutorials) - More game tutorials
- [Beginner Preset](Beginner-Preset) - Overview of beginner features
- [Tutorial: Maze](Tutorial-Maze) - Create a maze navigation game
- [Tutorial: Breakout](Tutorial-Breakout) - Create a brick breaker game
- [Event Reference](Event-Reference) - Complete event documentation

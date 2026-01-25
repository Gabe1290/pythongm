# Tutorial: Create a Lunar Lander Game

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introduction

In this tutorial, you'll create a **Lunar Lander Game** - a classic arcade game where you control a spacecraft descending onto a landing pad. You must manage your thrust to counteract gravity and land gently without crashing. This game is perfect for learning physics concepts like gravity, thrust, velocity, and fuel management.

**What you'll learn:**
- Gravity and thrust physics
- Velocity-based landing detection
- Fuel management system
- Rotation or directional control
- Safe landing zones

**Difficulty:** Beginner
**Preset:** Beginner Preset

---

## Step 1: Understand the Game

### Game Mechanics
1. The lander is pulled down by gravity
2. Pressing UP applies upward thrust (uses fuel)
3. LEFT/RIGHT controls rotate or move the lander
4. Land gently on the landing pad to win
5. Crash if you land too fast or miss the pad
6. Run out of fuel and you can't slow down!

### What We Need

| Element | Purpose |
|---------|---------|
| **Lander** | The spacecraft you control |
| **Landing Pad** | Safe zone to land on |
| **Ground** | Terrain that causes crash |
| **Fuel Display** | Shows remaining fuel |
| **Velocity Display** | Shows current speed |

---

## Step 2: Create the Sprites

### 2.1 Lander Sprite

1. In the **Resource Tree**, right-click on **Sprites** and select **Create Sprite**
2. Name it `spr_lander`
3. Click **Edit Sprite** to open the sprite editor
4. Draw a simple spacecraft (triangle or classic lander shape)
5. Size: 32x32 pixels
6. **Important:** Set the origin to center-bottom for proper landing

### 2.2 Landing Pad Sprite

1. Create a new sprite named `spr_pad`
2. Draw a flat platform with markings (like an "H")
3. Use bright colors (yellow/green)
4. Size: 64x16 pixels

### 2.3 Ground Sprite

1. Create a new sprite named `spr_ground`
2. Draw rocky/rough terrain
3. Use gray/brown colors
4. Size: 32x32 pixels

### 2.4 Flame Sprite (Optional)

1. Create a new sprite named `spr_flame`
2. Draw a small flame/exhaust
3. Use orange/yellow colors
4. Size: 16x16 pixels

---

## Step 3: Create the Ground Object

The ground is dangerous terrain that causes a crash.

1. Right-click on **Objects** and select **Create Object**
2. Name it `obj_ground`
3. Set the sprite to `spr_ground`
4. **Check the "Solid" checkbox**
5. No events needed

---

## Step 4: Create the Landing Pad Object

The landing pad is where the player must land safely.

1. Create a new object named `obj_pad`
2. Set the sprite to `spr_pad`
3. **Check the "Solid" checkbox**
4. No events needed (collision handled by lander)

---

## Step 5: Create the Lander Object

The lander is the main player-controlled object with physics.

1. Create a new object named `obj_lander`
2. Set the sprite to `spr_lander`

### 5.1 Create Event - Initialize Variables

**Event: Create**
1. Add Event → Create
2. Add Action: **Control** → **Execute Code**

```gml
// Physics variables
gravity_force = 0.05;  // Gentle gravity
thrust_force = 0.1;    // Thrust power
max_speed = 5;         // Maximum velocity

// Current velocity
hsp = 0;  // Horizontal speed
vsp = 0;  // Vertical speed

// Fuel system
fuel = 100;
fuel_use = 0.5;  // Fuel used per frame when thrusting

// Game state
landed = false;
crashed = false;

// Safe landing speed
safe_speed = 2;
```

### 5.2 Step Event - Physics and Controls

**Event: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **Execute Code**

```gml
// Don't update if game is over
if (landed || crashed) exit;

// === GRAVITY ===
vsp += gravity_force;

// === THRUST (Up Arrow) ===
if (keyboard_check(vk_up) && fuel > 0) {
    vsp -= thrust_force;
    fuel -= fuel_use;
    if (fuel < 0) fuel = 0;
}

// === HORIZONTAL CONTROL ===
if (keyboard_check(vk_left)) {
    hsp -= 0.05;
}
if (keyboard_check(vk_right)) {
    hsp += 0.05;
}

// === LIMIT SPEED ===
hsp = clamp(hsp, -max_speed, max_speed);
vsp = clamp(vsp, -max_speed, max_speed);

// === APPLY MOVEMENT ===
x += hsp;
y += vsp;

// === SCREEN BOUNDARIES ===
if (x < 16) { x = 16; hsp = 0; }
if (x > room_width - 16) { x = room_width - 16; hsp = 0; }
if (y < 16) { y = 16; vsp = 0; }
```

### 5.3 Collision with Landing Pad

**Event: Collision with obj_pad**
1. Add Event → Collision → obj_pad
2. Add Action: **Control** → **Execute Code**

```gml
// Check landing speed
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    // Safe landing!
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("Perfect Landing! You Win!");
} else {
    // Too fast - crash!
    crashed = true;
    show_message("Crashed! Too fast! Speed: " + string(total_speed));
    room_restart();
}
```

### 5.4 Collision with Ground

**Event: Collision with obj_ground**
1. Add Event → Collision → obj_ground
2. Add Action: **Control** → **Execute Code**

```gml
crashed = true;
show_message("Crashed into terrain!");
room_restart();
```

---

## Step 6: Create the Flame Object (Optional)

Visual feedback when thrusting.

1. Create a new object named `obj_flame`
2. Set the sprite to `spr_flame`

This will be created by the lander when thrusting (advanced feature).

For a simpler approach, you can draw the flame in the lander's Draw event.

---

## Step 7: Create the Game Controller

The game controller displays fuel, velocity, and instructions.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Draw**
1. Add Event → Draw → Draw
2. Add Action: **Control** → **Execute Code**

```gml
draw_set_color(c_white);

// Get lander info
var lander = instance_find(obj_lander, 0);
if (lander != noone) {
    var spd = sqrt(lander.hsp*lander.hsp + lander.vsp*lander.vsp);

    // Draw HUD
    draw_text(10, 10, "LUNAR LANDER");
    draw_text(10, 30, "Fuel: " + string(floor(lander.fuel)) + "%");
    draw_text(10, 50, "Speed: " + string_format(spd, 1, 2));
    draw_text(10, 70, "Safe Speed: < " + string(lander.safe_speed));

    // Speed warning
    if (spd > lander.safe_speed) {
        draw_set_color(c_red);
        draw_text(10, 90, "TOO FAST!");
    } else {
        draw_set_color(c_lime);
        draw_text(10, 90, "Speed OK");
    }

    // Fuel warning
    if (lander.fuel <= 0) {
        draw_set_color(c_red);
        draw_text(10, 110, "NO FUEL!");
    }
}

draw_set_color(c_gray);
draw_text(10, room_height - 20, "UP: Thrust | LEFT/RIGHT: Move");
```

---

## Step 8: Design Your Level

1. Right-click on **Rooms** and select **Create Room**
2. Name it `room_game`
3. Set the room size (e.g., 640x480)
4. Set background color to black (space)

### Placing Objects

Build your level following these guidelines:

1. **Ground** - Place `obj_ground` along the bottom to create terrain
2. **Landing Pad** - Place `obj_pad` in a gap in the terrain
3. **Lander** - Place `obj_lander` at the top of the room
4. **Game Controller** - Place `obj_game_controller` anywhere

### Example Level Layout

```
    L                          <- Lander starts here





GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Ground    L = Lander    P = Landing Pad
```

---

## Step 9: Test Your Game!

1. Click **Run** or press **F5** to test
2. Use **UP** arrow to thrust (watch your fuel!)
3. Use **LEFT/RIGHT** arrows to steer
4. Land gently on the pad (speed must be under 2)
5. Avoid the rocky terrain!

---

## Enhancements (Optional)

### Add Rotation Control

Instead of left/right movement, rotate the lander:

In Create event:
```gml
rotation = 90;  // Pointing up
rotation_speed = 3;
```

In Step event:
```gml
// Rotation
if (keyboard_check(vk_left)) rotation -= rotation_speed;
if (keyboard_check(vk_right)) rotation += rotation_speed;

// Thrust in direction of rotation
if (keyboard_check(vk_up) && fuel > 0) {
    hsp += lengthdir_x(thrust_force, rotation);
    vsp += lengthdir_y(thrust_force, rotation);
    fuel -= fuel_use;
}

image_angle = rotation - 90;  // Adjust sprite angle
```

### Add Multiple Landing Pads

Create different sized pads with different point values:
- Small pad = 100 points (harder)
- Large pad = 50 points (easier)

### Add Fuel Pickups

1. Create `obj_fuel` that floats in the air
2. On collision with lander, add fuel and destroy

### Add Levels

Create multiple rooms with increasingly difficult terrain and smaller landing pads.

### Add Wind

Add a random horizontal force that pushes the lander:
```gml
// In Step event
hsp += wind_force;  // Set wind_force in Create event
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Lander falls too fast | Decrease `gravity_force` or increase `thrust_force` |
| Can't slow down enough | Increase `thrust_force` or `safe_speed` |
| Fuel runs out too fast | Decrease `fuel_use` or increase starting `fuel` |
| Lander goes off screen | Add boundary checks in Step event |
| Landing doesn't register | Make sure landing pad has "Solid" checked |

---

## What You Learned

Congratulations! You've created a Lunar Lander game! You learned:

- **Thrust physics** - Counteracting gravity with upward force
- **Velocity management** - Controlling speed for safe landing
- **Fuel system** - Resource management gameplay
- **Collision detection** - Different outcomes for pad vs ground
- **HUD display** - Showing game state to the player

---

## Challenge Ideas

1. **Realistic Rotation** - Rotate and thrust in facing direction
2. **Multiple Levels** - Increasingly difficult terrain
3. **Scoring System** - Points based on fuel remaining and landing accuracy
4. **Asteroids** - Add moving hazards to avoid
5. **Two-Player Mode** - Race to land first

---

## See Also

- [Tutorials](Tutorials) - More game tutorials
- [Beginner Preset](Beginner-Preset) - Overview of beginner features
- [Tutorial: Platformer](Tutorial-Platformer) - Create a platform jumping game
- [Tutorial: Maze](Tutorial-Maze) - Create a maze navigation game
- [Event Reference](Event-Reference) - Complete event documentation


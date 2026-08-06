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
**Preset:** Intermediate Preset (the thrust/fuel physics rely on Execute
Code throughout, which isn't in the Beginner preset)

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

The lander is the main player-controlled object with physics. Unlike the
other movement tutorials on this wiki, the lander's controls need to
accumulate speed gradually and track a fuel resource, so this object leans
more on **Control** → **Execute Code** (real Python — `self` is the current
instance, `game` is the game runner, `keyboard.check(name)` reports a held
key) than on structured actions alone. Everywhere a structured action does
the job, this tutorial still uses one.

1. Create a new object named `obj_lander`
2. Set the sprite to `spr_lander`

### 5.1 Gravity and Starting Variables

**Event: Create**
1. Add Action: **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — a gentle downward pull; the engine adds this to the lander's vertical
   speed automatically every step, same as the Platformer tutorial's gravity,
   just weaker.
2. Add Action: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

This project's movement system already tracks velocity as `self.hspeed`/
`self.vspeed` and moves the instance by that amount every frame (with solid
collision built in) — there's no need for separate `hsp`/`vsp` variables the
way a raw physics simulation would track them.

### 5.2 Step Event — Thrust and Controls

**Event: Step** — Add Action: **Control** → **Execute Code**:

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Limit top speed
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Keep the lander from drifting off the sides or above the room
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

The whole block is wrapped in `if not self.landed and not self.crashed:` so
thrust and steering stop the instant the game ends — the `self` object
doesn't have a way to bail out of an event partway through (no GML-style
`exit`), so an `if` around the rest of the code is the equivalent.

### 5.3 Collision with Landing Pad

**Event: Collision with obj_pad**
1. Add Action: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — the landing speed is the length of the velocity vector; Pythagoras,
     not a `speed` variable (in this engine `speed` is the *sprite animation*
     rate, not movement magnitude — a genuine gotcha coming from GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) — stops
        gravity from quietly building up vertical speed again on a lander
        that's already landed
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

Show Message's text is a fixed string — it can't embed the actual landing
speed. The HUD (Step 7) already displays the live speed right up to the
moment of touchdown, so the player has already seen the number.

### 5.4 Collision with Ground

**Event: Collision with obj_ground**
1. Add Action: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Add Action: **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Add Action: **Room** → **Restart Room**

---

## Step 6: Create the Flame Object (Optional)

Visual feedback when thrusting.

1. Create a new object named `obj_flame`
2. Set the sprite to `spr_flame`

This will be created by the lander when thrusting (advanced feature).

For a simpler approach, you can draw the flame in the lander's Draw event.

---

## Step 7: Create the Game Controller

The game controller displays fuel, velocity, and instructions by reading
them off the lander instance each frame.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Draw**
1. Add Action: **Control** → **Execute Code** — find the lander and compute
   the values the Draw actions below will display:

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Add Action: **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Add Action: **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Add Action: **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Add Action: **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Add Action: **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Add Action: **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Add Action: **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Then the two warning lines, each gated by **Control** → **Test Expression**
(no Else needed — nothing draws when the condition is false):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Add Action: **Game** → **Set Draw Color** (Color: `#808080`)
12. Add Action: **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — pick a Y near the bottom of whatever room size you
    use in Step 8.

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

Instead of left/right movement, rotate the lander and thrust in the
direction it's facing. This engine's instances have a real `rotation`
attribute (degrees, 0 = right, increasing counter-clockwise) used to spin
the sprite — no `image_angle`/`lengthdir_x`/`lengthdir_y` needed, since
`math` is already available in Execute Code:

Replace 5.1's Create-event code with:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # pointing up
self.rotation_speed = 3
```

Replace 5.2's steering lines (the `left`/`right` → `hspeed` block) with:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

And replace the thrust lines with:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(the `-=` on `vspeed` matches the engine's own gravity code — screen Y
increases downward, so "up" is negative vertical speed).

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

Add a small constant horizontal push. In `obj_lander`'s Create event code,
add `self.wind_force = 0.02`; then at the top of the Step event's `if not
self.landed and not self.crashed:` block, add:
```python
self.hspeed += self.wind_force
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Lander falls too fast | Decrease Set Gravity's `Gravity` value, or increase `thrust_force` in the Create event code |
| Can't slow down enough | Increase `thrust_force`, or increase `safe_speed` |
| Fuel runs out too fast | Decrease `fuel_use`, or increase the starting `fuel` |
| Lander goes off screen | Check the boundary block at the end of the Step event code |
| Landing doesn't register | Make sure `obj_pad` has "Solid" checked |

---

## What You Learned

Congratulations! You've created a Lunar Lander game! You learned:

- **Thrust physics** - Nudging `self.vspeed` against a continuous Set Gravity pull
- **Velocity management** - Computing speed from `hspeed`/`vspeed` with the Pythagorean theorem
- **Fuel system** - Resource management gameplay with a plain instance variable
- **Collision detection** - Different outcomes for pad vs ground, chosen with Test Expression
- **HUD display** - Computing display values in Execute Code, then showing them with Draw Text/Draw Variable

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
- [Intermediate Preset](Intermediate-Preset) - Overview of the preset this tutorial needs
- [Tutorial: Platformer](Tutorial-Platformer) - Create a platform jumping game
- [Tutorial: Maze](Tutorial-Maze) - Create a maze navigation game
- [Event Reference](Event-Reference) - Complete event documentation

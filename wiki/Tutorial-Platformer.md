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

### 5.1 Gravity

**Event: Create** — Add Action: **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° is straight down; the value is
added to the player's vertical speed every step, so the player accelerates
downward on its own from here on.

### 5.2 Movement, Jumping, and Ground Collision

Add these events, matching the pattern the earlier tutorials in this wiki
already use:

| Event | Action |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed to `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed to `4` |
| Keyboard: No Key | Set Horizontal Speed to `0` |
| Key Press → Up Arrow | Set Vertical Speed to `-10` |
| Collision with obj_ground | Stop Movement |

Two details that make this feel right:

- **No Key sets only horizontal speed to 0** — never use Stop Movement
  there, because Stop Movement zeroes vertical speed too, and that would
  cancel gravity every time the player lets go of a direction key.
- **Key Press (not held)** is what makes Up a single jump impulse instead
  of launching the player upward every frame it's held. **Stop Movement**
  on landing then zeroes that impulse, so the player doesn't keep
  climbing once it lands — the engine's own solid collision (Step 3
  already made `obj_ground` Solid) stops the player from ever sinking into
  the ground in the first place; the event here just clears the leftover
  fall speed.

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
2. Add Action: **Output** → **Show Message**
   - Message: `Level Complete!`
3. Add Action: **Room** → **Next Room** (or **Restart Room** for single level)

Show Message's text is a fixed string — it can't embed a live value like the
score. The game controller's HUD (Step 9) already shows the score on
screen throughout the level, so the player has already seen it.

---

## Step 9: Create the Game Controller

The game controller displays the score.

1. Create a new object named `obj_game_controller`
2. No sprite needed

**Event: Draw**
1. Add Event → Draw → Draw
2. Add Action: **Draw** → **Draw Text** (Text: `Score:`, X: `10`, Y: `10`)
3. Add Action: **Draw** → **Draw Variable** (Variable: `score`, X: `70`, Y: `10`)

Optional: add a **Draw Text** (`Lives:`, X `10`, Y `30`) + **Draw Variable**
(`lives`, X `70`, Y `30`) pair the same way, once the Lives System
enhancement below is in place.

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

Add a **Step** event to `obj_player` with **Control** → **Execute Code**
(real Python — `self` is the current instance, `keyboard` lets you check a
held key by name):

```python
# Cut the jump short if Up is released while still rising
if self.vspeed < 0 and not keyboard.check('up'):
    self.vspeed = max(self.vspeed, -5)  # half of the -10 jump impulse
```

### Add Double Jump

This can be done entirely with structured actions — no code needed.

**Event: Create** — Add Action: **Control** → **Set Variable** (Variable:
`jumps_left`, Value: `2`)

**Event: Collision with obj_ground** — after **Stop Movement**, add
**Control** → **Set Variable** (Variable: `jumps_left`, Value: `2`) to
refill both jumps on landing.

Replace the existing **Key Press → Up Arrow** event's single action with
three, in order:
1. **Control** → **Test Variable** (Variable: `jumps_left`, Value: `0`,
   Operation: `greater`)
2. **Control** → **Start Block**
3. **Move** → **Set Vertical Speed** (`-10`)
4. **Control** → **Set Variable** (Variable: `jumps_left`, Value: `-1`,
   **Relative** checked)
5. **Control** → **End Block**

The Start/End Block pair means both actions inside only run when the Test
Variable above them is true — the same guarded-block pattern the Sokoban
and Maze tutorials use for their own conditionals.

### Add Moving Platforms

1. Create `obj_moving_platform` as a child of `obj_platform`

**Event: Create** — Add Action: **Control** → **Execute Code**:

```python
self.start_x = self.x
self.hspeed = 2
```

**Event: Step** — Add Action: **Control** → **Execute Code**:

```python
if self.x > self.start_x + 100:
    self.hspeed = -2
elif self.x < self.start_x:
    self.hspeed = 2
```

### Add Enemy

1. Create `obj_enemy` with a simple AI

**Event: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Event: Collision with obj_ground** — Add Action: **Move** → **Reverse
Horizontal** (turns around at walls; combined with `obj_ground` being
Solid, the enemy can never walk off a platform's edge into the ground
below or through a wall)

**Event: Collision with obj_player** — this event fires on `obj_enemy`, so
`self` is the enemy and `other` is the player. Add Action: **Control** →
**Test Expression**, with nested Then/Else actions (the same pattern
`plateforme_3`'s bundled sample uses for exactly this "stomp" check, just
mirrored since the check lives on the enemy here instead of the player):
   - Expression: `other.vspeed > 0 and other.y - other.vspeed < y - 16`
   - Then Actions: **Control** → **Execute Code** with `other.vspeed = -5`
     (a small bounce for the player — `set_vspeed` has no "applies to
     other" option, so this is the one spot that needs a line of real
     Python instead of a structured action), then **Instance** → **Destroy
     Instance** (self)
   - Else Actions: **Room** → **Restart Room** (the player dies)

`other.vspeed > 0 and other.y - other.vspeed < y - 16` checks the
*player's* position from before this frame's fall movement (using the
player's own `vspeed`, since the player is the one falling), so a fast
fall can't tunnel past the 16px stomp window in one step — see
`plateforme_3`'s README for the full story of why the naive
`other.y < y - 16` version is fragile.

### Add Lives System

In `obj_game_controller`'s **Create** event, add **Score** → **Set Lives**
(Value: `3`).

When the player dies (the spike collision, and the enemy's Else branch
above), replace **Restart Room** with **Score** → **Set Lives** (Value:
`-1`, **Relative** checked) — the room restarts automatically because the
**No More Lives** event only fires once lives actually reach 0. Add that
event to `obj_game_controller`: **Other Events** → **No More Lives** →
**Output** → **Show Message** (`Game Over!`) → **Room** → **Restart
Game**.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Player falls through ground | Check that `obj_ground` has "Solid" checked |
| Player can't jump | Verify the Key Press → Up Arrow event exists and Set Vertical Speed is negative |
| Player keeps rising after landing | Make sure Collision with obj_ground has a Stop Movement action |
| Jump feels floaty | Increase Set Gravity's Gravity value, or make Set Vertical Speed's jump value more negative |
| Jump feels too weak | Decrease Set Gravity's Gravity value, or make Set Vertical Speed's jump value more negative |

---

## What You Learned

Congratulations! You've created a platformer game! You learned:

- **Gravity physics** - Set Gravity applies a constant downward force every step
- **Jump mechanics** - A Key Press (not held) event gives a single upward speed impulse
- **Built-in solid collision** - The ground blocks the player automatically once marked Solid, no manual position-checking code needed
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

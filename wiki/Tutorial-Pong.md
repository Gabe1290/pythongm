# Tutorial: Create a Classic Pong Game

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Introduction

In this tutorial, you'll create a classic **Pong** game - one of the first video games ever made! Pong is a two-player game where each player controls a paddle and tries to hit the ball past their opponent's paddle to score points.

**What you'll learn:**
- Creating sprites for paddles, ball, and walls
- Handling keyboard input for two players
- Making objects bounce off each other
- Tracking and displaying scores for both players
- Using global variables

**Difficulty:** Beginner
**Preset:** Beginner Preset

---

## Step 1: Plan Your Game

Before we start, let's understand what we need:

| Element | Purpose |
|---------|---------|
| **Ball** | Bounces between players |
| **Left Paddle** | Player 1 controls with W/S keys |
| **Right Paddle** | Player 2 controls with Up/Down arrows |
| **Walls** | Top and bottom boundaries |
| **Goals** | Invisible areas behind each paddle to detect scoring |
| **Score Display** | Shows both players' scores |

---

## Step 2: Create the Sprites

### 2.1 Ball Sprite

1. In the **Resource Tree**, right-click on **Sprites** and select **Create Sprite**
2. Name it `spr_ball`
3. Click **Edit Sprite** to open the sprite editor
4. Draw a small white circle (about 16x16 pixels)
5. Click **OK** to save

### 2.2 Paddle Sprites

We'll create two paddles - one for each player:

**Left Paddle (Player 1):**
1. Create a new sprite named `spr_paddle_left`
2. Draw a tall, thin rectangle curved like a parenthesis ")" - blue color recommended
3. Size: approximately 16x64 pixels

**Right Paddle (Player 2):**
1. Create a new sprite named `spr_paddle_right`
2. Draw a tall, thin rectangle curved like a parenthesis "(" - red color recommended
3. Size: approximately 16x64 pixels

### 2.3 Wall Sprite

1. Create a new sprite named `spr_wall`
2. Draw a solid rectangle (gray or white)
3. Size: 32x32 pixels (we'll stretch it in the room)

### 2.4 Goal Sprite (Invisible)

1. Create a new sprite named `spr_goal`
2. Make it 32x32 pixels
3. Leave it transparent or make it a solid color (it will be invisible in the game)

---

## Step 3: Create the Wall Object

The wall object creates boundaries at the top and bottom of the play area.

1. Right-click on **Objects** and select **Create Object**
2. Name it `obj_wall`
3. Set the sprite to `spr_wall`
4. **Check the "Solid" checkbox** - this is important for bouncing!
5. No events needed - the wall just sits there

---

## Step 4: Create the Paddle Objects

### 4.1 Left Paddle (Player 1)

1. Create a new object named `obj_paddle_left`
2. Set the sprite to `spr_paddle_left`
3. **Check the "Solid" checkbox**

**Add Keyboard Events for Movement:**

**Event: Keyboard Press W**
1. Add Event → Keyboard → Press W
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `-8` (moves up)

**Event: Key Release W**
1. Add Event → Keyboard → Release W
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `0` (stops moving)

**Event: Keyboard Press S**
1. Add Event → Keyboard → Press S
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `8` (moves down)

**Event: Key Release S**
1. Add Event → Keyboard → Release S
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `0` (stops moving)

**Event: Collision with obj_wall**
1. Add Event → Collision → obj_wall
2. Add Action: **Move** → **Bounce Against Objects**
3. Select "Against solid objects"

### 4.2 Right Paddle (Player 2)

1. Create a new object named `obj_paddle_right`
2. Set the sprite to `spr_paddle_right`
3. **Check the "Solid" checkbox**

**Add Keyboard Events for Movement:**

**Event: Keyboard Press Up Arrow**
1. Add Event → Keyboard → Press Up
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `-8`

**Event: Key Release Up Arrow**
1. Add Event → Keyboard → Release Up
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `0`

**Event: Keyboard Press Down Arrow**
1. Add Event → Keyboard → Press Down
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `8`

**Event: Key Release Down Arrow**
1. Add Event → Keyboard → Release Down
2. Add Action: **Move** → **Set Vertical Speed**
3. Set vertical speed to `0`

**Event: Collision with obj_wall**
1. Add Event → Collision → obj_wall
2. Add Action: **Move** → **Bounce Against Objects**
3. Select "Against solid objects"

---

## Step 5: Create the Ball Object

1. Create a new object named `obj_ball`
2. Set the sprite to `spr_ball`

**Event: Create**
1. Add Event → Create
2. Add Action: **Move** → **Start Moving in Direction**
3. Choose a diagonal direction (not straight up or down)
4. Set speed to `6`

**Event: Collision with obj_paddle_left**
1. Add Event → Collision → obj_paddle_left
2. Add Action: **Move** → **Bounce Against Objects**
3. Select "Against solid objects"

**Event: Collision with obj_paddle_right**
1. Add Event → Collision → obj_paddle_right
2. Add Action: **Move** → **Bounce Against Objects**
3. Select "Against solid objects"

**Event: Collision with obj_wall**
1. Add Event → Collision → obj_wall
2. Add Action: **Move** → **Bounce Against Objects**
3. Select "Against solid objects"

---

## Step 6: Create the Goal Objects

Goals are invisible areas behind each paddle. When the ball enters a goal, the opposing player scores.

### 6.1 Left Goal

1. Create a new object named `obj_goal_left`
2. Set the sprite to `spr_goal`
3. **Uncheck "Visible"** - the goal should be invisible
4. **Check "Solid"**

### 6.2 Right Goal

1. Create a new object named `obj_goal_right`
2. Set the sprite to `spr_goal`
3. **Uncheck "Visible"**
4. **Check "Solid"**

### 6.3 Add Goal Collision Events to the Ball

Go back to `obj_ball` and add these events:

**Event: Collision with obj_goal_left**
1. Add Event → Collision → obj_goal_left
2. Add Action: **Move** → **Jump to Start Position** (resets the ball)
3. Add Action: **Score** → **Set Score**
   - Variable: `global.p2score`
   - Value: `1`
   - Check "Relative" (adds 1 to current score)

**Event: Collision with obj_goal_right**
1. Add Event → Collision → obj_goal_right
2. Add Action: **Move** → **Jump to Start Position**
3. Add Action: **Score** → **Set Score**
   - Variable: `global.p1score`
   - Value: `1`
   - Check "Relative"

---

## Step 7: Create the Score Display Object

1. Create a new object named `obj_score`
2. No sprite needed

**Event: Create**
1. Add Event → Create
2. Add Action: **Score** → **Set Score**
   - Variable: `global.p1score`
   - Value: `0`
3. Add Action: **Score** → **Set Score**
   - Variable: `global.p2score`
   - Value: `0`

**Event: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Player 1:`
   - X: `10`
   - Y: `10`
3. Add Action: **Draw** → **Draw Variable**
   - Variable: `global.p1score`
   - X: `100`
   - Y: `10`
4. Add Action: **Draw** → **Draw Text**
   - Text: `Player 2:`
   - X: `10`
   - Y: `30`
5. Add Action: **Draw** → **Draw Variable**
   - Variable: `global.p2score`
   - X: `100`
   - Y: `30`

---

## Step 8: Design the Room

1. Right-click on **Rooms** and select **Create Room**
2. Name it `room_pong`
3. Set the room size (e.g., 640x480)

**Place the objects:**

1. **Walls**: Place `obj_wall` instances along the top and bottom edges of the room
2. **Left Paddle**: Place `obj_paddle_left` near the left edge, centered vertically
3. **Right Paddle**: Place `obj_paddle_right` near the right edge, centered vertically
4. **Ball**: Place `obj_ball` in the center of the room
5. **Goals**:
   - Place `obj_goal_left` instances along the left edge (behind where the paddle is)
   - Place `obj_goal_right` instances along the right edge
6. **Score Display**: Place `obj_score` anywhere (it doesn't have a sprite, it just draws text)

**Room Layout Example:**
```
[WALL WALL WALL WALL WALL WALL WALL WALL WALL WALL]
[GOAL]  [PADDLE_L]            [BALL]            [PADDLE_R]  [GOAL]
[GOAL]  [PADDLE_L]                              [PADDLE_R]  [GOAL]
[GOAL]                                                      [GOAL]
[WALL WALL WALL WALL WALL WALL WALL WALL WALL WALL]
```

---

## Step 9: Test Your Game!

1. Click **Run** or press **F5** to test your game
2. Player 1 uses **W** (up) and **S** (down)
3. Player 2 uses **Up Arrow** and **Down Arrow**
4. Try to hit the ball past your opponent's paddle!

---

## Enhancements (Optional)

### Speed Increase
Make the ball faster each time it hits a paddle by adding to the collision events:
- After the bounce action, add **Move** → **Set Speed**
- Set speed to `speed + 0.5` with "Relative" checked

### Sound Effects
Add sounds when:
- The ball hits a paddle
- The ball hits a wall
- A player scores

### Win Condition
Add a check in the Draw event:
- If `global.p1score >= 10`, display "Player 1 Wins!"
- If `global.p2score >= 10`, display "Player 2 Wins!"

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Ball goes through paddle | Make sure paddles have "Solid" checked |
| Paddle doesn't stop at walls | Add collision event with obj_wall |
| Score doesn't update | Check that variable names match exactly (global.p1score, global.p2score) |
| Ball doesn't move | Check the Create event has the movement action |

---

## What You Learned

Congratulations! You've created a complete two-player Pong game! You learned:

- How to handle keyboard input for two different players
- How to use Key Release events to stop movement
- How to make objects bounce off each other
- How to use global variables to track scores
- How to display text and variables on screen

---

## See Also

- [Beginner Preset](Beginner-Preset) - Overview of beginner features
- [Tutorial: Breakout](Tutorial-Breakout) - Create a brick breaker game
- [Event Reference](Event-Reference) - Complete event documentation
- [Full Action Reference](Full-Action-Reference) - All available actions

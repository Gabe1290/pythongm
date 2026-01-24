# Tutorial: Create a Breakout Game

*[Home](Home) | [Beginner Preset](Beginner-Preset) | [Français](Tutorial-Breakout_fr)*

This tutorial will guide you through creating a classic Breakout game. It's a perfect first project for learning PyGameMaker!

![Breakout Game Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## What You'll Learn

- Creating and using sprites
- Setting up game objects with events and actions
- Keyboard controls for player movement
- Collision detection and bouncing
- Destroying objects on collision
- Building a game room

---

## Step 1: Create the Sprites

First, we need to create the visual elements for our game.

### 1.1 Create the Paddle Sprite
1. In the **Assets** panel, right-click on **Sprites** → **Create Sprite**
2. Name it `spr_paddle`
3. Draw a horizontal rectangle (about 64x16 pixels)
4. **Important:** Click **Center** to set the origin to the center

### 1.2 Create the Ball Sprite
1. Create another sprite named `spr_ball`
2. Draw a small circle (about 16x16 pixels)
3. Click **Center** to set the origin

### 1.3 Create the Brick Sprite
1. Create a sprite named `spr_brick`
2. Draw a rectangle (about 48x24 pixels)
3. Click **Center** to set the origin

### 1.4 Create the Wall Sprite
1. Create a sprite named `spr_wall`
2. Draw a square (about 32x32 pixels) - this will be the boundary
3. Click **Center** to set the origin

### 1.5 Create a Background (Optional)
1. Right-click on **Backgrounds** → **Create Background**
2. Name it `bg_game`
3. Draw or load a background image

---

## Step 2: Create the Paddle Object

Now let's program the paddle that the player controls.

### 2.1 Create the Object
1. Right-click on **Objects** → **Create Object**
2. Name it `obj_paddle`
3. Set the **Sprite** to `spr_paddle`
4. Check the **Solid** checkbox

### 2.2 Add Right Arrow Movement
1. Click **Add Event** → **Keyboard** → select **Right Arrow**
2. Add the action **Set Horizontal Speed**
3. Set **value** to `5` (or any speed you prefer)

### 2.3 Add Left Arrow Movement
1. Click **Add Event** → **Keyboard** → select **Left Arrow**
2. Add the action **Set Horizontal Speed**
3. Set **value** to `-5`

### 2.4 Stop When Keys Released
The paddle keeps moving even after releasing the key! Let's fix that.

1. Click **Add Event** → **Keyboard Release** → select **Right Arrow**
2. Add the action **Set Horizontal Speed**
3. Set **value** to `0`

4. Click **Add Event** → **Keyboard Release** → select **Left Arrow**
5. Add the action **Set Horizontal Speed**
6. Set **value** to `0`

Now the paddle stops when you release the arrow keys.

---

## Step 3: Create the Ball Object

### 3.1 Create the Object
1. Create a new object named `obj_ball`
2. Set the **Sprite** to `spr_ball`
3. Check the **Solid** checkbox

### 3.2 Set Initial Movement
1. Click **Add Event** → **Create**
2. Add the action **Move in Direction** (or **Set Horizontal/Vertical Speed**)
3. Set a diagonal direction with speed `5`
   - For example: **hspeed** = `4`, **vspeed** = `-4`

This makes the ball start moving when the game begins.

### 3.3 Bounce Off the Paddle
1. Click **Add Event** → **Collision** → select `obj_paddle`
2. Add the action **Reverse Vertical** (to bounce)

### 3.4 Bounce Off Walls
1. Click **Add Event** → **Collision** → select `obj_wall`
2. Add the action **Reverse Horizontal** or **Reverse Vertical** as needed
   - Or use both to handle corner bounces

---

## Step 4: Create the Brick Object

### 4.1 Create the Object
1. Create a new object named `obj_brick`
2. Set the **Sprite** to `spr_brick`
3. Check the **Solid** checkbox

### 4.2 Destroy on Ball Collision
1. Click **Add Event** → **Collision** → select `obj_ball`
2. Add the action **Destroy Instance** with target **self**

This destroys the brick when the ball hits it!

### 4.3 Bounce the Ball
In the same collision event, also add:
1. Add action **Reverse Vertical** (applied to **other** - the ball)

Or go back to `obj_ball` and add:
1. **Add Event** → **Collision** → select `obj_brick`
2. Add action **Reverse Vertical**

---

## Step 5: Create the Wall Object

### 5.1 Create the Object
1. Create a new object named `obj_wall`
2. Set the **Sprite** to `spr_wall`
3. Check the **Solid** checkbox

That's all - the wall just needs to be solid for the ball to bounce off.

---

## Step 6: Create the Game Room

### 6.1 Create the Room
1. Right-click on **Rooms** → **Create Room**
2. Name it `room_game`

### 6.2 Set the Background (Optional)
1. In the room settings, find **Background**
2. Select your `bg_game` background
3. Check **Stretch** if you want it to fill the room

### 6.3 Place the Objects

Now place your objects in the room:

1. **Place the Paddle:** Put `obj_paddle` at the bottom center of the room

2. **Place the Walls:** Put `obj_wall` instances around the edges:
   - Along the top
   - Along the left side
   - Along the right side
   - Leave the bottom open (this is where the ball can escape!)

3. **Place the Ball:** Put `obj_ball` somewhere in the middle

4. **Place the Bricks:** Arrange `obj_brick` instances in rows at the top of the room

---

## Step 7: Test Your Game!

1. Click the **Play** button (green arrow)
2. Use the **Left** and **Right** arrow keys to move the paddle
3. Try to bounce the ball to destroy all the bricks!
4. Press **Escape** to quit

---

## What's Next?

Your basic Breakout game is complete! Here are some improvements to try:

### Add a Life System
- Add a **No More Lives** event to show "Game Over"
- Lose a life when the ball goes off the bottom

### Add Scoring
- Use **Add Score** action when destroying bricks
- Display the score with **Draw Score**

### Add Multiple Levels
- Create more rooms with different brick layouts
- Use **Next Room** when all bricks are destroyed

### Add Sound Effects
- Add sounds for bouncing and brick destruction
- Use **Play Sound** action

---

## Summary of Objects

| Object | Sprite | Solid | Events |
|--------|--------|-------|--------|
| `obj_paddle` | `spr_paddle` | Yes | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Yes | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Yes | Collision (ball) - Destroy self |
| `obj_wall` | `spr_wall` | Yes | None needed |

---

## See Also

- [Beginner Preset](Beginner-Preset) - Events and actions used in this tutorial
- [Event Reference](Event-Reference) - All available events
- [Full Action Reference](Full-Action-Reference) - All available actions

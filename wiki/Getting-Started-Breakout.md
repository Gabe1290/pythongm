# Introduction to Video Game Creation with PyGameMaker

*[Home](Home) | [Beginner Preset](Beginner-Preset) | [Français](Getting-Started-Breakout_fr)*

**By the PyGameMaker Team**

---

In this tutorial, we'll learn the basics of game creation with PyGameMaker. Since it's a relatively complete software with many features, we'll focus only on those that will help us during this tutorial.

We'll create a simple Breakout-style game that will look like this:

![Breakout Game Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

This tutorial is for you, even if you have no programming knowledge, since PyGameMaker allows beginners to easily create games regardless of their skill level.

Alright, let's begin designing our game!

---

## Step 1: Getting Started

Start by opening PyGameMaker. You should see the main interface with the **Assets** panel on the left side, listing different resource categories: Sprites, Sounds, Backgrounds, Fonts, Objects, and Rooms.

Before anything else, in a video game, the first thing the player notices is what they see on screen. This is actually the foundation of a game: a game without graphics doesn't exist (or it's a very special case). We'll therefore start by inserting images into our game, which will be the graphical representation of the objects the player will see on screen. In game development terminology, these images are called **Sprites**.

---

## Step 2: Creating the Sprites

### 2.1 Creating the Paddle Sprite

1. Right-click on the **Sprites** folder at the top of the left column
2. Click on **Create Sprite**
3. A window called **Sprite Properties** will open - this is where you'll define all your sprite's characteristics
4. Use the built-in editor to draw a horizontal rectangle (about 64x16 pixels) in a color you like
5. **Important:** Click **Center** to set the origin at the center of your sprite
   > The origin of a sprite is its center point, its X:0 and Y:0 coordinates. These are its base coordinates.
6. Change the name of your sprite using the text field at the top, and enter `spr_paddle`
   > This has no technical impact - it's just to help you navigate your files better once you have more of them. You can choose any name you like; this is just an example.
7. Click **OK**

You've just created your first sprite! This is your paddle, the object the player will control to catch the ball.

### 2.2 Creating the Ball Sprite

Let's continue and add more sprites. Repeat the same process:

1. Right-click on **Sprites** → **Create Sprite**
2. Draw a small circle (about 16x16 pixels)
3. Click **Center** to set the origin
4. Name it `spr_ball`
5. Click **OK**

### 2.3 Creating the Brick Sprites

We need three types of bricks. Create them one by one:

**First Brick (Destructible):**
1. Create a new sprite
2. Draw a rectangle (about 48x24 pixels) - use a bright color like red
3. Click **Center**, name it `spr_brick_1`
4. Click **OK**

**Second Brick (Destructible):**
1. Create a new sprite
2. Draw a rectangle (same size) - use a different color like blue
3. Click **Center**, name it `spr_brick_2`
4. Click **OK**

**Third Brick (Indestructible Wall):**
1. Create a new sprite
2. Draw a rectangle (same size) - use a darker color like gray
3. Click **Center**, name it `spr_brick_3`
4. Click **OK**

You should now have all the sprites for our game:
- `spr_paddle` - The player's paddle
- `spr_ball` - The bouncing ball
- `spr_brick_1` - First destructible brick
- `spr_brick_2` - Second destructible brick
- `spr_brick_3` - Indestructible wall brick

> **Note:** In games, there are generally two main sources of graphical rendering: **Sprites** and **Backgrounds**. That's all that makes up what you see on screen. A Background is, as its name suggests, a backdrop image.

---

## Step 3: Understanding Objects and Events

What did we say at the beginning? The first thing the player notices is what they see on screen. We've taken care of that with our sprites. But a game made only of images isn't a game - it's a painting! We'll now move to the next stage: **Objects**.

An Object is an entity in your game that can have behaviors, respond to events, and interact with other objects. The sprite is just the visual representation; the object is what gives it life.

### How Game Logic Works

Everything in game programming follows this pattern: **If this happens, then I execute that.**

- If the player presses a key, then I do this
- If this variable equals this value, then I do that
- If two objects collide, then something happens

This is what we call **Events** and **Actions** in PyGameMaker:
- **Events** = Things that can happen (keyboard press, collision, timer, etc.)
- **Actions** = Things you want to do when events occur (move, destroy, change score, etc.)

---

## Step 4: Creating the Paddle Object

Let's create the object that the player will control: the paddle.

### 4.1 Create the Object

1. Right-click on the **Objects** folder → **Create Object**
2. Name it `obj_paddle`
3. In the **Sprite** dropdown, select `spr_paddle` - now our object has a visual appearance!
4. Check the **Solid** checkbox (we'll need this for collisions)

### 4.2 Programming the Movement

In a Breakout game, we need to move the paddle to prevent the ball from escaping at the bottom. We'll control it with the keyboard.

**Moving Right:**
1. Click **Add Event** → **Keyboard** → **Right Arrow**
2. From the actions panel on the right, add the action **Set Horizontal Speed**
3. Set the **value** to `5`
4. Click **OK**

This means: "When the Right Arrow key is pressed, set horizontal speed to 5 (moving right)."

**Moving Left:**
1. Click **Add Event** → **Keyboard** → **Left Arrow**
2. Add the action **Set Horizontal Speed**
3. Set the **value** to `-5`
4. Click **OK**

**Stopping When Keys Released:**

If we test now, the paddle would keep moving even after releasing the key! Let's fix that:

1. Click **Add Event** → **Keyboard Release** → **Right Arrow**
2. Add action **Set Horizontal Speed** with value `0`
3. Click **OK**

4. Click **Add Event** → **Keyboard Release** → **Left Arrow**
5. Add action **Set Horizontal Speed** with value `0`
6. Click **OK**

Now our paddle moves when keys are pressed and stops when they're released. We're done with this object for now!

---

## Step 5: Creating the Wall Brick Object

Let's create an indestructible wall brick - this will form the boundaries of our play area.

1. Create a new object named `obj_brick_3`
2. Assign the sprite `spr_brick_3`
3. Check the **Solid** checkbox

The ball will bounce off this brick. Since it's just a wall, we don't need any events - it just needs to be solid. Click **OK** to save.

---

## Step 6: Creating the Ball Object

Now let's create the ball, the essential element of our game.

### 6.1 Create the Object

1. Create a new object named `obj_ball`
2. Assign the sprite `spr_ball`
3. Check the **Solid** checkbox

### 6.2 Initial Movement

We want the ball to move by itself from the start. Let's give it an initial speed and direction.

1. Click **Add Event** → **Create**
   > The Create event executes actions when the object appears in the game, i.e., when it enters the scene.
2. Add the action **Set Horizontal Speed** with value `4`
3. Add the action **Set Vertical Speed** with value `-4`
4. Click **OK**

This gives the ball a diagonal movement (right and up) at the start of the game.

### 6.3 Bouncing Off the Paddle

We need the ball to bounce when it hits the paddle.

1. Click **Add Event** → **Collision** → select `obj_paddle`
   > This event triggers when the ball collides with the paddle.
2. Add the action **Reverse Vertical**
   > This reverses the vertical direction, making the ball bounce.
3. Click **OK**

### 6.4 Bouncing Off Walls

Same operation for the wall bricks:

1. Click **Add Event** → **Collision** → select `obj_brick_3`
2. Add the action **Reverse Vertical**
3. Add the action **Reverse Horizontal**
   > We add both because the ball might hit the wall from different angles.
4. Click **OK**

---

## Step 7: Testing Our Progress - Creating a Room

After Sprites and Objects, here come the **Rooms**. A room is where the game takes place: it's a map, a level. This is where you place all your game elements, where you organize what will appear on screen.

### 7.1 Create the Room

1. Right-click on **Rooms** → **Create Room**
2. Name it `room_game`

### 7.2 Place Your Objects

Now place your objects using the mouse:
- **Left-click** to place an object
- **Right-click** to delete an object

Select the object to place from the dropdown menu in the room editor.

**Build your level:**
1. Place `obj_brick_3` instances around the edges (top, left, right) - leave the bottom open!
2. Place `obj_paddle` at the bottom center
3. Place `obj_ball` somewhere in the middle

### 7.3 Test the Game!

Click the **Play** button (green arrow) in the toolbar. This lets you test your game at any time.

You can already have fun bouncing the ball off the walls and paddle!

It's minimal, but already a good start - you have your game foundation!

---

## Step 8: Adding Destructible Bricks

Let's add some bricks to break, to make our game more fun.

### 8.1 First Destructible Brick

1. Create a new object named `obj_brick_1`
2. Assign sprite `spr_brick_1`
3. Check **Solid**

We'll add the behavior to destroy itself when hit by the ball:

1. Click **Add Event** → **Collision** → select `obj_ball`
2. Add the action **Destroy Instance** with target **self**
   > This action removes an object during the game - here, the brick itself.
3. Click **OK**

And just like that, you have your new destructible brick!

### 8.2 Second Destructible Brick (Using Parent)

Now we'll create a second destructible brick, but without having to reprogram it. We'll make it a "clone" using the **Parent** feature.

1. Create a new object named `obj_brick_2`
2. Assign sprite `spr_brick_2`
3. Check **Solid**
4. In the **Parent** dropdown, select `obj_brick_1`

What does this mean? Simply that what we programmed in `obj_brick_1` will be inherited by `obj_brick_2`, without having to reproduce it ourselves. The parent-child relationship allows objects to share behaviors!

Click **OK** to save.

### 8.3 Make the Ball Bounce Off New Bricks

Reopen `obj_ball` by double-clicking on it, and add collision events for our new bricks:

1. Click **Add Event** → **Collision** → select `obj_brick_1`
2. Add action **Reverse Vertical**
3. Click **OK**

4. Click **Add Event** → **Collision** → select `obj_brick_2`
5. Add action **Reverse Vertical**
6. Click **OK**

---

## Step 9: Game Over - Restarting the Room

We need to restart the level if the ball escapes the screen (if the player fails to catch it).

In `obj_ball`:

1. Click **Add Event** → **Other** → **Outside Room**
2. Add the action **Restart Room**
   > This action restarts the current room during the game.
3. Click **OK**

---

## Step 10: Final Level Design

Now place everything in your room to create your final Breakout level:

1. Open `room_game`
2. Arrange `obj_brick_3` walls around the top and sides
3. Place rows of `obj_brick_1` and `obj_brick_2` in patterns at the top
4. Keep `obj_paddle` at the bottom center
5. Place `obj_ball` above the paddle

**Example layout:**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]         (ball)         [3]
[3]                        [3]
[3]        [paddle]        [3]
```

---

## Congratulations!

Your Breakout game is complete! You can now enjoy your work by playing the game you just created!

You can also refine it further, like adding:
- **Sound effects** for bouncing and brick destruction
- **Score tracking** using the Add Score action
- **Additional brick types** with different behaviors
- **Multiple levels** with different layouts

---

## Summary of What You Learned

| Concept | Description |
|---------|-------------|
| **Sprites** | Visual images that represent objects in your game |
| **Objects** | Game entities with behaviors, combining sprites with events and actions |
| **Events** | Triggers that execute actions (Create, Keyboard, Collision, etc.) |
| **Actions** | Operations to perform (Move, Destroy, Bounce, etc.) |
| **Solid** | Property that enables collision detection |
| **Parent** | Allows objects to inherit behaviors from other objects |
| **Rooms** | Game levels where you place object instances |

---

## Objects Summary

| Object | Sprite | Solid | Events |
|--------|--------|-------|--------|
| `obj_paddle` | `spr_paddle` | Yes | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Yes | Create, Collision (paddle, bricks), Outside Room |
| `obj_brick_1` | `spr_brick_1` | Yes | Collision (ball) - Destroy self |
| `obj_brick_2` | `spr_brick_2` | Yes | Inherits from `obj_brick_1` |
| `obj_brick_3` | `spr_brick_3` | Yes | None (just a wall) |

---

## See Also

- [Beginner Preset](Beginner-Preset) - Events and actions available for beginners
- [Event Reference](Event-Reference) - Complete list of all events
- [Full Action Reference](Full-Action-Reference) - Complete list of all actions
- [Tutorial: Breakout](Tutorial-Breakout) - Shorter version of this tutorial

---

You are now initiated into the basics of video game creation with PyGameMaker. It's your turn to create your own games!

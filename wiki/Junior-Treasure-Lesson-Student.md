# Treasure Maze: Gems, Keys, Doors and Bombs

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Junior-Treasure-Lesson-Student.pdf) · [ODT](downloads/Junior-Treasure-Lesson-Student.odt)

---

## How to Use This Handout

You have about 90 minutes. Do each part on your screen, then tick the box.
Stuck? Ask a neighbour first, then your teacher. At the end you will have a
real treasure game, and you will turn it into **one file** that works in a web
browser, and even on a phone!

## Part 1: Open Your Game (5 min)

- [ ] Click **File > Open Project** and open the folder **Treasure Maze**.
- [ ] Look at the list on the left. You already have seven pictures (sprites):
      **spr_wall**, **spr_door**, **spr_gem**, **spr_key**, **spr_heart**,
      **spr_bomb** and **spr_goal**. There is also an **obj_wall** and a room
      called **room0** with walls around the edge.
- [ ] Press the green triangle (or **F5**) to test. You see an empty room.
      Close the game window.

> TIP: Press **Save** often. The disk button saves your game.

## Part 2: Draw Your Hero (10 min)

All the other pictures are ready. The hero is yours!

- [ ] Click **Assets > Create Sprite**. Name it `spr_hero`, then OK.
- [ ] Draw your hero. Fill the square. Click **Save**.

> TIP: Names use letters, numbers and `_` only. No spaces!

## Part 3: Make the Objects (12 min)

A picture alone does nothing. An **object** is something in your game that can
do things. Make one object for each picture.

- [ ] Open **obj_wall** (double-click it). Tick **Solid**.
- [ ] Click **Assets > Create Object** for each line of this table. Choose
      the sprite. Tick **Solid** only where the table says Yes.

| Object name | Sprite | Solid? |
|---|---|---|
| obj_wall (already there) | spr_wall | **Yes** |
| obj_door | spr_door | **Yes** |
| obj_gem | spr_gem | No |
| obj_key | spr_key | No |
| obj_heart | spr_heart | No |
| obj_bomb | spr_bomb | No |
| obj_goal | spr_goal | No |
| obj_hero | spr_hero | No |

> INFO: A **Solid** object is a wall-like object. Walls and doors are solid.
> Things you can pick up are not.

> DONE: You should see eight objects in the list.

## Part 4: Build Your Maze (15 min)

- [ ] Open **room0** (double-click it in the list).
- [ ] Click **obj_wall**, hold the mouse button down and **drag** to paint
      walls inside the border.
- [ ] Place the other objects with one click each:

| Place | How many |
|---|---|
| **obj_hero** | 1, at the start |
| **obj_goal** | 1, far from the hero |
| **obj_gem** | at least 3 |
| **obj_key** | 1, **before** the door |
| **obj_door** | across a path, as wide as the path |
| **obj_heart** | 1, a little hidden |
| **obj_bomb** | 2 or 3, along the edge of a path |

> INFO: Make **every path two squares wide** or more. Your hero does not always
> stop in the middle of a path. In a path of only one square it can get stuck.

> TIP: Put a bomb on the side of a wide path, never across the whole path. The
> hero must be able to go around it.

> TIP: The key must be somewhere the hero can reach **without** going through
> a door!

- [ ] Press **F5**. You see your maze. Nothing moves yet. That is next!

## Part 5: Make It Work (33 min)

Open each object and build its blocks in the **Blockly** area. Drag the blocks
from the left. Click **Save** after each object.

### 5a. The hero moves (8 min)

Open **obj_hero**.

| When this happens | Do this |
|---|---|
| **Keyboard:** Left Arrow (held) | **Set horizontal speed to** -4 |
| **Keyboard:** Right Arrow (held) | **Set horizontal speed to** 4 |
| **Keyboard:** Up Arrow (held) | **Set vertical speed to** -4 |
| **Keyboard:** Down Arrow (held) | **Set vertical speed to** 4 |
| **Keyboard: No key** | **Stop movement** |
| **When colliding with** obj_wall | **Stop movement** |
| **When colliding with** obj_door | **Stop movement** |

> TIP: Right-click a block to **Duplicate** it. It is faster than dragging a
> new one every time.

> DONE: Press **F5**. The hero walks and stops at walls and doors.

### 5b. Gems (4 min)

Open **obj_gem**. Put both blocks under the same event.

| When this happens | Do this |
|---|---|
| **When colliding with** obj_hero | **Add to score** 10 |
| (the same event) | **Destroy this instance** |

### 5c. The key opens the doors (4 min)

Open **obj_key**.

| When this happens | Do this |
|---|---|
| **When colliding with** obj_hero | **Destroy all instances of** obj_door |
| (the same event) | **Destroy this instance** |

### 5d. The heart (3 min)

Open **obj_heart**.

| When this happens | Do this |
|---|---|
| **When colliding with** obj_hero | **Add to lives** 1 |
| (the same event) | **Destroy this instance** |

### 5e. Bombs (6 min)

The hero decides what happens. Open **obj_hero** again and add this event:

| When this happens | Do this |
|---|---|
| **When colliding with** obj_bomb | **Add to lives** -1 |
| (the same event) | **Destroy other instance** |
| (the same event) | **Stop movement** |
| (the same event) | **Jump to Start Position** |

> INFO: "Other instance" means the other thing that was touched: the bomb. The
> bomb explodes and disappears. The hero goes back to the start.

### 5f. The goal (6 min)

Open **obj_goal**. This one asks a question: are there any gems left? Use the
**If** block. It has two slots: **then** (when the answer is yes) and **else**
(when the answer is no).

| Where | Blocks |
|---|---|
| The event | **When colliding with** obj_hero |
| Under the event | **If** count of object: type `obj_gem` in the box, keep `==`, and make the number **0** |
| Inside **then** | **Show message** "You win!", then **Restart Game** under it |
| Inside **else** | **Show message** "Collect every gem first!" |

> TIP: The **If** block starts with the name `obj_coin` in its box. Click the
> box and type `obj_gem` instead.

> INFO: If there are no gems left (the number of gems is 0), the blocks inside
> **then** happen. If not, the blocks inside **else** happen.

### 5g. Game over (2 min)

Open **obj_hero** again.

| When this happens | Do this |
|---|---|
| **Other event:** No More Lives | **Show message** "Game over!" |
| (the same event) | **Restart Game** |

> DONE: Press **F5** and play! Collect every gem, take the key, open the door,
> avoid the bombs and reach the goal.

## Part 6: Share Your Game (7 min)

- [ ] Click **File > Export as HTML5**.
- [ ] Choose a folder. Click **Yes** to open the game in your browser.
- [ ] Look in the folder: you have **one file** ending in `.html`. That is your game!
- [ ] Play it. Then show it to a friend.

> TIP: On a phone or a tablet, arrow buttons appear on the screen. Hold a
> button to move.

## Stuck?

| What happens | Try this |
|---|---|
| The hero does not move | Is the hero in the room? Is there a block under **Keyboard**? |
| The hero goes through walls or doors | Add **When colliding with** obj_wall (or obj_door) with **Stop movement** |
| The hero is stuck in a path | Make the path two squares wide |
| The key does nothing | Did you build **Destroy all instances of** obj_door in obj_key? |
| I cannot open the door | Is the key placed where the hero can reach it without passing a door? |
| The goal says "Collect every gem first!" | There is still a gem somewhere. Find it! |
| I lost all my lives | The game starts again. Be careful with bombs! |
| I deleted something by mistake | **Tools > Restore Deleted Assets** |

## Words to Know

- **Sprite**: a picture
- **Object**: something in your game that can do things
- **Solid**: an object that is a wall-like block
- **Event**: "when something happens"
- **Collision**: when two things touch
- **Lives**: how many tries you have left

## Challenges

- **Try this (5 min):** change the points a gem gives, or the messages.
- **Push further:** add a second key and more doors, or hide a gem behind a door.
- **Invent:** swap computers with a friend and try to win their maze.

## Think About It

1. What does the key do when the hero touches it?
2. Why can the goal say "Collect every gem first!"?
3. What happens when you lose all your lives?

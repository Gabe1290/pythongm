# My First Maze: Make a Game You Can Play on a Phone

## How to Use This Handout

You have about 90 minutes. Do each part on your screen, then tick the box.
Stuck? Ask a neighbour first, then your teacher. At the end you will make
a game that you can play in a web browser, and even on a phone!

## Part 1: Open Your Maze (5 min)

- [ ] Click **File > Open Project** and open the folder **My Maze**.
- [ ] Look at the list on the left. You have a **spr_wall** (picture), an
      **obj_wall** (the wall) and a room called **room0**.
- [ ] Press the green triangle (or **F5**) to test. You see an empty box.
      Close the game window.

> TIP: Press **Save** often. The disk button saves your game.

## Part 2: Draw Your Hero and Your Goal (15 min)

- [ ] Click **Assets > Create Sprite**. Name it `spr_hero`, then OK.
- [ ] Draw your hero! Fill the square. Click **Save**.
- [ ] Do it again for the goal. Name it `spr_goal`. Make it look different from
      the hero and the walls.

> TIP: Names use letters, numbers and `_` only. No spaces!

## Part 3: Make the Hero Move (20 min)

- [ ] Click **Assets > Create Object**. Name it `obj_hero`.
- [ ] In **Sprite**, choose `spr_hero`.
- [ ] In the **Blockly** area, build these blocks. Drag them from the left.

| When this happens | Do this |
|---|---|
| **Keyboard:** Left Arrow (held) | **Set horizontal speed to** -4 |
| **Keyboard:** Right Arrow (held) | **Set horizontal speed to** 4 |
| **Keyboard:** Up Arrow (held) | **Set vertical speed to** -4 |
| **Keyboard:** Down Arrow (held) | **Set vertical speed to** 4 |
| **Keyboard: No key** | **Stop movement** |
| **When colliding with** obj_wall | **Stop movement** |

- [ ] Click **Save**.

> TIP: Right-click a block to **Duplicate** it. It is faster than dragging a
> new one every time.

> INFO: A minus sign makes the hero go left or up. A plus number goes right or down.

## Part 4: Make the Goal (10 min)

- [ ] Create an object named `obj_goal`. Give it `spr_goal`.
- [ ] Build these blocks:

| When this happens | Do this |
|---|---|
| **When colliding with** obj_hero | **Show message** "You win!" |
| (the same event) | **Restart room** |

Put the two blocks one under the other, under the same event.

## Part 5: Build Your Maze (20 min)

- [ ] Open **room0** (double-click it in the list).
- [ ] Click **obj_wall**. Hold the mouse button down and **drag** to paint a wall.
- [ ] Click **obj_hero** and click once inside the top-left of the room.
- [ ] Click **obj_goal** and click once far away from your hero.
- [ ] Press **F5** and play! Can you reach the goal?

> INFO: Make **every path two squares wide**. Your hero is one square wide
> and does not always stop in the middle of a path. In a path of only one
> square the hero can get stuck.

> DONE: You should see your hero, your goal and your walls. The hero stops at a
> wall. When you touch the goal, "You win!" appears.

## Part 6: Share Your Game (10 min)

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
| The hero never stops | Add **Keyboard: No key** with **Stop movement** |
| The hero goes through walls | Add **When colliding with** obj_wall with **Stop movement** |
| The hero is stuck in a path | Make the path two squares wide |
| Nothing happens at the goal | The goal needs **When colliding with** obj_hero |
| I deleted something by mistake | **Tools > Restore Deleted Assets** |

## Words to Know

- **Sprite**: a picture
- **Object**: something in your game that can do things
- **Room**: a level
- **Event**: "when something happens"
- **Collision**: when two things touch
- **Export**: make a copy of your game that works on its own

## Challenges

- **Try this (5 min):** change the message to something funny.
- **Push further:** make a second goal, or draw a better wall sprite.
- **Invent:** swap computers with a friend and try to finish their maze.

## Think About It

1. Why must the hero stop when it touches a wall?
2. What does the goal do when the hero touches it?
3. Why do we make the paths two squares wide?

## My Notes

[[notes:6]]

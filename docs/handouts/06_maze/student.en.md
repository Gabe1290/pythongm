# PyGameMaker — Tutorial 6: Maze

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Maze: Navigate to the Exit** (4 pages, about 20-25 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A maze game: you steer a character through corridors with the arrow keys, collect coins for points, and reach the exit to win.

## Phase 1: Player and Maze

- [ ] **1.** Create two sprites (32×32): `spr_player` and `spr_wall`.
- [ ] **2.** Create `obj_wall` (sprite `spr_wall`, **Solid** ticked) and `obj_player` (sprite `spr_player`, not solid).
- [ ] **3.** In `obj_player` add five events: **Keyboard: Right Arrow (held)** with *Set horizontal speed to 4*; **Left Arrow (held)** with *-4*; **Down Arrow (held)** with *Set vertical speed to 4*; **Up Arrow (held)** with *-4*; and **Keyboard: No key** with *Stop movement*.
- [ ] **4.** Add **Collision with obj_wall** with *Stop movement*.
- [ ] **5.** Create `room_maze` (640×480) and turn on **Snap to Grid** 32×32. Place walls around the border and inside to make corridors, and place the player at the top left. Every corridor must be at least one tile wide.

> DONE: **You should see:** press **F5**. The arrow keys move the player, it stops at walls, and it stops when you let go.

## Phase 2: Coins and Exit

- [ ] **6.** Create sprites `spr_coin` and `spr_exit` (32×32).
- [ ] **7.** Create `obj_coin` and `obj_exit`, each with its sprite and **not** solid.
- [ ] **8.** In `obj_coin`, add **Collision with obj_player**: *Add to score 10*, then *Destroy this instance*.
- [ ] **9.** In `obj_exit`, add **Collision with obj_player**: *Show message* "You Win!", then *Restart room*.
- [ ] **10.** In the room, scatter coins along the corridors and put the exit as far from the start as you can.

> DONE: **You should see:** press **F5**. Coins vanish when you touch them. Reaching the exit shows "You Win!" and the room starts again.

## Phase 3: Score Display

- [ ] **11.** Create `obj_game_controller` (no sprite, not solid).
- [ ] **12.** **Create** event: *Set score to 0*. **Draw** event: *Draw score at x 10, y 10*.
- [ ] **13.** Place `obj_game_controller` anywhere in the room.

> DONE: **You should see:** "Score: 0" at the top left, going up by 10 for every coin. After "You Win!" the coins come back and the score is 0 again.

## Stuck?

| What is wrong | Most likely cause | What to do |
| The player does not move | The events are on the wrong object, or the player is not in the room | Check the five events on `obj_player`; check the room |
| The player slides forever | The **No key** event is missing | Add **Keyboard: No key** with *Stop movement* |
| The player walks through walls | `obj_wall` is not Solid, or the player has no **Collision with obj_wall** | Tick **Solid**; add the event with *Stop movement* |
| The player gets stuck in corridors | Walls or the player were not placed on the grid | Turn on **Snap to Grid** 32×32 and place them again |
| Coins do nothing | The coin has no **Collision with obj_player** event | Add it to `obj_coin` |
| The whole game freezes at the exit | *Show message* is waiting for a click | Click OK on the message |
| No score on the screen | `obj_game_controller` is not in the room | Place it in the room |
| The score does not go back to 0 after winning | *Set score to 0* is missing in the controller's **Create** | Add it |

## Challenges

- **Try this (5 minutes):** change the player's speed, or the value of a coin.
- **Push further:** make a second maze in another room and use **Go to next room** at the exit.
- **Invent:** add a patrolling enemy, a countdown timer, or a key that must be collected before the exit works.

## Vocabulary

| Term | What it means |
| Solid | An object that blocks movement |
| Collectible | An object that disappears when the player touches it |
| Exit | An object that ends or advances the level |
| Snap to Grid | Placing objects exactly on a regular grid |
| Level design | Planning the maze so it is fair and solvable |

## Check Yourself

Write your answers in the notes below.

1. Why does the player need a **No key** event with *Stop movement*?
2. Why does the coin destroy *this* instance, and what would *Destroy other instance* have done in the coin's event?
3. Why do we place objects on a grid when we build the maze?

## My Notes

[[notes:10]]

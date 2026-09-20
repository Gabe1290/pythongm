# PyGameMaker — Tutorial 5: Sokoban

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Sokoban: Box-Pushing Puzzle** (4 pages, about 20-25 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A classic puzzle: you walk on a grid, one square at a time, and push crates onto target spots. A crate turns green when it is on a target, and you can press **R** to restart the level.

## Phase 1: Player and Walls

- [ ] **1.** Create two sprites (32×32): `spr_player` and `spr_wall`.
- [ ] **2.** Create `obj_wall` (sprite `spr_wall`, **Solid**) and `obj_player` (sprite `spr_player`).
- [ ] **3.** In `obj_player` add four **Key press** events (Right, Left, Up, Down arrows). Each does *Move grid* in its direction with size **32**.
- [ ] **4.** Add **Collision with obj_wall** with *Stop movement*.
- [ ] **5.** Create `room_sokoban` (320×320, a 10×10 grid), turn on grid snap 32×32, put walls around the edge and a few inside, and place the player.

> DONE: **You should see:** press **F5**. Each key press moves you exactly one square. Walls stop you.

## Phase 2: Pushing Crates

- [ ] **6.** Create a sprite `spr_crate` and an object `obj_crate` (sprite `spr_crate`, **Solid**).
- [ ] **7.** In `obj_player` add **Collision with obj_crate**: *If can push (facing)* then *Push other instance 32*.
- [ ] **8.** In `obj_crate` add **Collision with obj_wall** with *Stop movement*.
- [ ] **9.** Place 2 or 3 crates in the room, each with room to move (not in a corner!).

> DONE: **You should see:** press **F5**. Walk into a crate and it moves one square. It does not move if a wall or another crate is behind it.

## Phase 3: Targets and Controller

- [ ] **10.** Create sprites `spr_target` and `spr_crate_ok` (a green crate).
- [ ] **11.** Create `obj_target` (sprite `spr_target`) — **not Solid**, so crates and the player can go over it.
- [ ] **12.** In `obj_crate` add a **Step** event: *If colliding with obj_target*, *Set sprite to spr_crate_ok*; *Else*, *Set sprite to spr_crate*.
- [ ] **13.** Create `obj_controller` (no sprite). **Draw** event: *Draw text* "Push crates onto targets!" at x 10, y 10. **Key press R**: *Restart room*.
- [ ] **14.** In the room, place the targets **first**, then **delete the player and the crates and place them again**. Place `obj_controller` anywhere. The number of targets must equal the number of crates.

> DONE: **You should see:** press **F5**. Push a crate onto a target and it turns green; push it off and it turns brown again. **R** puts everything back.

> TIP: **Why place the targets first?** The game draws things in the order you placed them. A target placed after a crate or the player is drawn on top of them, so a crate on a target would stay hidden under the red mark.

## Stuck?

| What is wrong | Most likely cause | What to do |
| I move several squares at once, or not at all | The events are *Keyboard* (held) instead of *Key press*, or *Move grid* size is not 32 | Use **Key press** events and *Move grid* size 32 |
| I walk through walls | `obj_wall` is not Solid, or the player has no **Collision with obj_wall** | Tick **Solid**; add the event with *Stop movement* |
| The crate does not move | The player has no collision event for the crate, or the crate is not Solid | Add **Collision with obj_crate** with *If can push*; tick **Solid** on the crate |
| The crate moves through walls | The crate has no **Collision with obj_wall** event | Add it with *Stop movement* |
| The crate never turns green | The Step event is missing, or the target is drawn over the crate | Add the Step event; place the targets first, then place the crates again |
| I cannot push a crate onto a target | `obj_target` is Solid | Untick **Solid** on `obj_target` |
| The crate is stuck in a corner at the start | It was placed in a corner | Place crates with room to move |
| The text is hard to read | It is black text over the dark room | Look at the top row, or ask your teacher about *Set draw color* |

## Challenges

- **Try this (5 minutes):** draw a nicer player or crate.
- **Push further:** design a harder level with tighter corridors; check you can solve it yourself first.
- **Invent:** count the moves with a variable, or make several rooms and go to the next one when all crates are on targets.

## Vocabulary

| Term | What it means |
| Grid movement | Moving in fixed steps (here, 32 pixels) instead of smoothly |
| Key press | An event that happens once when a key goes down |
| Solid | An object that blocks movement |
| Target | A marker on the floor; not solid |
| Restart room | Put the level back the way it started |

## Check Yourself

Write your answers in the notes below.

1. Why do we use **Key press** events and not *Keyboard (held)* for a Sokoban player?
2. Why must the targets not be Solid?
3. Why is a crate not pushed if there is another crate behind it?

## My Notes

[[notes:10]]

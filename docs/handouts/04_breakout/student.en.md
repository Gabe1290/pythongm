# PyGameMaker — Tutorial 4: Breakout

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Breakout: Brick Breaker** (7 pages, about 25-30 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

The classic brick breaker: a paddle at the bottom, a ball that bounces off walls and the paddle, four rows of coloured bricks to destroy, three lives and a score. You will use a **parent object** so one collision rule works for every brick colour.

## Phase 1: A Bouncing Ball

- [ ] **1.** Create four sprites: `spr_ball` (16×16), `spr_paddle` (64×16), `spr_wall` (32×32) and `spr_death_zone` (32×32). Draw them or import the sample images from `Tutorials/04_breakout/assets/`.
- [ ] **2.** Create the objects: `obj_wall_side` and `obj_wall_top` (sprite `spr_wall`, **Solid**), `obj_paddle` (**Solid**), `obj_ball` (**not** solid), and `obj_death_zone` (sprite `spr_death_zone`, **Visible unchecked**).
- [ ] **3.** Paddle: **Keyboard: Left Arrow (held)** with *Set horizontal speed to -8*, **Keyboard: Right Arrow (held)** with *Set horizontal speed to 8*, **Keyboard: No key** with *Stop movement*, and **Collision with obj_wall_side** with *Stop movement*.
- [ ] **4.** Ball: **Create** with *Set horizontal speed to 3* and *Set vertical speed to -3*.
- [ ] **5.** Ball collisions: with `obj_wall_side` → *Reverse horizontal movement*; with `obj_wall_top` → *Reverse vertical movement*; with `obj_paddle` → *Reverse vertical movement*; with `obj_death_zone` → *Jump to x: 320 y: 100*.
- [ ] **6.** Create `room_breakout` (640×480). Place side walls down both edges, top walls along the top, the death zone along the **bottom** (there is no bottom wall), the paddle near the bottom centre and the ball just above it.

> DONE: **You should see:** press **F5**. The paddle moves with the arrow keys and stops at the walls. The ball bounces around; if it falls past the paddle it comes back at the top.

## Phase 2: First Row of Bricks

- [ ] **7.** Create a sprite `spr_brick_red` (32×16).
- [ ] **8.** Create `obj_brick_parent` (no sprite, **Solid**) — a template. Then create `obj_brick_red` (sprite `spr_brick_red`, **Parent** `obj_brick_parent`, **Solid**).
- [ ] **9.** In `obj_ball`, add **Collision with obj_brick_parent**: *Reverse vertical movement*, *Destroy other instance*, *Add to score 10*.
- [ ] **10.** In the room, fill one row of `obj_brick_red` near the top (turn on **Snap to Grid** 32×16).

> DONE: **You should see:** press **F5**. The ball destroys bricks and bounces back. Each brick is worth 10 points (you cannot see the score yet).

## Phase 3: More Brick Rows

- [ ] **11.** Create sprites `spr_brick_orange`, `spr_brick_yellow` and `spr_brick_green` (32×16).
- [ ] **12.** Create `obj_brick_orange`, `obj_brick_yellow` and `obj_brick_green`, each with its sprite, **Parent** `obj_brick_parent` and **Solid**. Do **not** change the ball.
- [ ] **13.** Fill four rows: red, orange, yellow, green.

> DONE: **You should see:** press **F5**. Bricks of every colour break when the ball hits them.

## Phase 4: Game Controller

- [ ] **14.** Create `obj_game_controller` (no sprite). **Create**: *Set lives to 3*, *Set score to 0*. **Draw**: *Draw score at x 10, y 10* and *Draw lives at x 200, y 10*.
- [ ] **15.** In `obj_ball`, in the **Collision with obj_death_zone** event, add *Add to lives -1* **before** the jump.
- [ ] **16.** In `obj_game_controller`, add the event **Other Events > No More Lives** with *Show message "Game Over!"*, then *Show Highscore*, then *End Game*.
- [ ] **17.** Place `obj_game_controller` anywhere in the room.

> DONE: **You should see:** the score and lives show at the top. Each fall costs a life. After the third fall you get a Game Over message, the highscore table, and the game closes.

## Stuck?

| What is wrong | Most likely cause | What to do |
| The ball flies out of the room | A wall is missing or not Solid, or the ball has no bounce event for it | Check the walls; check the ball's collision events |
| The ball bounces but the bricks stay | The brick collision event is on the wrong object, or bricks do not have the parent set | Put the event on `obj_ball` for `obj_brick_parent`; set the **Parent** on every brick |
| Only red bricks break | The new bricks have no **Parent** | Set **Parent** to `obj_brick_parent` on orange, yellow and green |
| The paddle goes through the side walls | No **Collision with obj_wall_side** event on the paddle | Add it with *Stop movement* |
| The ball is never lost / lives do not go down | The death zone is missing, or *Add to lives -1* was not added | Place the death zone at the bottom; add the action |
| No score or lives on screen | `obj_game_controller` is not in the room | Place it in the room |
| Lives start at 0 or the game ends at once | *Set lives to 3* is missing | Add it to the controller's **Create** event |
| The ball goes through a brick without breaking it | The brick is not Solid or not in the room properly | Tick **Solid** on the brick objects |

## Challenges

- **Try this (5 minutes):** change the ball speed or the paddle speed.
- **Push further:** give each colour a different score (red 40, orange 30, yellow 20, green 10), or speed the ball up as bricks disappear.
- **Invent:** build a second level with a different brick layout, or play a sound when the game ends.

## Vocabulary

| Term | What it means |
| Parent object | A template object; objects that use it inherit its events |
| Child object | An object that has a parent (each brick colour) |
| Death zone | An invisible object that detects when the ball is lost |
| Lives | How many times you can lose the ball |
| Highscore | The best scores, kept in a table |

## Check Yourself

Write your answers in the notes below.

1. Why is the collision event written for `obj_brick_parent` and not for each colour?
2. Why is there no wall at the bottom of the room?
3. What does *Reverse vertical movement* do, and why is it used for the top wall and the paddle but *Reverse horizontal* for the side walls?

## My Notes

[[notes:10]]

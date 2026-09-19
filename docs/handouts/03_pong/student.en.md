# PyGameMaker — Tutorial 3: Classic Pong

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Classic Pong: Two-Player Game** (4 pages, about 20-25 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher. You will need a partner to play at the end!

## What You Will Make

The classic arcade game: two paddles, a bouncing ball, invisible goals behind each paddle, and a score on the screen. Player 1 uses **W** and **S**; Player 2 uses the **Up** and **Down** arrows.

## Phase 1: Paddles and Ball

- [ ] **1.** Create three sprites: `spr_ball` (16×16, white circle), `spr_paddle` (16×64, tall rectangle) and `spr_wall` (32×32, grey block).
- [ ] **2.** Create the objects: `obj_wall` (sprite `spr_wall`, **Solid**), `obj_paddle_left` and `obj_paddle_right` (sprite `spr_paddle`, **Solid**), and `obj_ball` (sprite `spr_ball`, **not** solid).
- [ ] **3.** Left paddle: **Keyboard: W (held)** with *Set vertical speed to -8*, **Keyboard: S (held)** with *Set vertical speed to 8*, **Keyboard: No key** with *Stop movement*, and **Collision with obj_wall** with *Stop movement*.
- [ ] **4.** Right paddle: the same four events, but with **Up Arrow** and **Down Arrow**.
- [ ] **5.** Ball: **Create** with *Start moving in direction 45 at speed 6*; and three collision events (with `obj_wall`, `obj_paddle_left`, `obj_paddle_right`), each with *Bounce against solid objects*.
- [ ] **6.** Create `room_pong` (640×480). Place walls along the top and bottom, a paddle near each side edge, and the ball in the centre.

> DONE: **You should see:** press **F5**. Both paddles move with their own keys and stop at the walls. The ball flies up and to the right, bounces off walls and paddles, and if you miss it flies off the side of the screen. That is expected for now.

## Phase 2: Goals and Scoring

- [ ] **7.** Create a sprite `spr_goal` (32×32, any colour).
- [ ] **8.** Create `obj_goal_left` and `obj_goal_right` (sprite `spr_goal`, **Visible unchecked**, **Solid** checked).
- [ ] **9.** In `obj_ball`, add **Collision with obj_goal_left**: *Set variable* `global.p2score` *relative* +1, then *Jump to start position*. Add **Collision with obj_goal_right**: the same with `global.p1score`.
- [ ] **10.** In the room, stack `obj_goal_left` along the left edge and `obj_goal_right` along the right edge, behind the paddles.

> DONE: **You should see:** press **F5**. When the ball passes a paddle it goes back to the centre. You cannot see the score yet.

## Phase 3: Score Display

- [ ] **11.** Create `obj_score` (no sprite). Its **Create** event sets `global.p1score` and `global.p2score` to 0.
- [ ] **12.** Its **Draw** event: first *Set draw color* to white (`#ffffff`); then *Draw text* "Player 1:" at x 10, y 40; *Draw variable* `global.p1score` at x 100, y 40; *Draw text* "Player 2:" at x 10, y 60; *Draw variable* `global.p2score` at x 100, y 60.
- [ ] **13.** Place `obj_score` anywhere in the room.

> DONE: **You should see:** press **F5** and play a point with your partner. The scores show at the top left and go up when the other player misses.

## Stuck?

| What is wrong | Most likely cause | What to do |
| A paddle goes through the wall | The paddle has no **Collision with obj_wall** event, or `obj_wall` is not Solid | Add the event (with *Stop movement*); tick **Solid** on `obj_wall` |
| The ball goes right through walls or paddles | The Bounce events are missing, or the walls and paddles are not Solid | Add **Bounce against solid objects** for each collision; tick **Solid** |
| The ball only moves sideways | The direction is not what you expect | Check *Start moving in direction 45* in the ball's **Create** event |
| The ball is stuck in the middle | The ball's **Create** event is missing, or the ball is not in the room | Add the event; place the ball in the room |
| The ball never scores | The goals are not in the room, or are not Solid | Place goals behind the paddles; tick **Solid** |
| The score does not show | `obj_score` is not in the room, there is no **Draw** event, or the text is black on the black room | Place it; add the Draw event; add *Set draw color* white first |
| The score is always 0 | The variables are called something different in different places | Use exactly `global.p1score` and `global.p2score` everywhere |
| Both players' keys move the same paddle | Both paddles have the same keys | Left: W and S. Right: Up and Down |

## Challenges

- **Try this (5 minutes):** change the ball speed, or the paddle speed.
- **Push further:** add a dotted line down the middle, or make the ball go faster every time it hits a paddle.
- **Invent:** end the game when a player reaches 10 points and show who won, or change the ball's angle depending on where it hits the paddle.

## Vocabulary

| Term | What it means |
| Solid | An object that other objects can bounce off or be stopped by |
| Bounce | Reverse the direction of movement after hitting something |
| Global variable | A value shared by all objects, written `global.name` |
| Draw event | The event that draws things on the screen every frame |
| Goal | An (invisible) object that detects when the ball has passed |

## Check Yourself

Write your answers in the notes below.

1. Why do the goals have **Visible** unchecked but **Solid** checked?
2. What does the `global.` in `global.p1score` mean, and why do we need it here?
3. After a goal, the ball is put back in the middle. Which way does it move, and why?

## My Notes

[[notes:10]]

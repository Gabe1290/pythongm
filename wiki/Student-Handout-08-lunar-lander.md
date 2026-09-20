# PyGameMaker — Tutorial 8: Lunar Lander

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Student-Handout-08-lunar-lander.pdf) · [ODT](downloads/Student-Handout-08-lunar-lander.odt)

---

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Lunar Lander: Land on the Moon** (4 pages, about 20-25 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A lunar lander game: your spacecraft falls slowly under the Moon's weak gravity. You use the arrow keys to thrust and steer, and you must land on the green pad. Hit the rocky ground and you crash.

## Phase 1: A Flying Lander

- [ ] **1.** Create two sprites (32×32): `spr_lander` and `spr_ground`.
- [ ] **2.** Create `obj_ground` (sprite `spr_ground`, **Solid**) and `obj_lander` (sprite `spr_lander`).
- [ ] **3.** In `obj_lander`, **Create** event: *Set gravity* direction **270**, strength **0.05**. (The Moon's gravity is about a sixth of Earth's, so the value is small.)
- [ ] **4.** **Keyboard: Up Arrow (held)** with *Set vertical speed -2*.
- [ ] **5.** **Keyboard: Left Arrow (held)** with *Set horizontal speed -2* and **Right Arrow (held)** with *2*.
- [ ] **6.** **Keyboard: No key** with *Set horizontal speed 0*. Do not reset the vertical speed, or gravity stops working.
- [ ] **7.** Create `room_game` (640×480, **black** background, Snap to Grid 32×32). Put ground along the bottom row and the lander near the top.

> **Done:** **You should see:** press **F5**. The lander falls slowly. Hold **Up** to climb, **Left** and **Right** to steer. Let go of everything and it drifts down. (It passes through the ground for now: no collision event yet.)

## Phase 2: Landing and Crashing

- [ ] **8.** Create `spr_pad` (a flat green rectangle) and `obj_pad` (sprite `spr_pad`, **Solid**).
- [ ] **9.** In `obj_lander`, add **Collision with obj_pad**: *Stop movement*, then *Set gravity* direction 270 strength **0**, then *Show message* "Landing successful!".
- [ ] **10.** Add **Collision with obj_ground**: *Show message* "Crashed!", then *Restart room*.
- [ ] **11.** Change the room: make the ground uneven with hills, leave a gap in the bottom row, and put `obj_pad` in the gap (one or two blocks).

> **Done:** **You should see:** press **F5**. Touch the pad and you get "Landing successful!" once. Touch the ground and you get "Crashed!" and the level restarts. Use short taps of **Up** to control your fall.

## Phase 3: Game Controller

- [ ] **12.** Create `obj_game_controller` (no sprite). **Create** event: *Set score to 0*.
- [ ] **13.** **Draw** event: first *Set draw color* to white (`#ffffff`), then *Draw text* "Lunar Lander" at x 10, y 10 and *Draw text* "Land on the green pad!" at x 10, y 30.
- [ ] **14.** Place `obj_game_controller` anywhere in the room.

> **Done:** **You should see:** press **F5**. The title and the instructions are shown at the top left in white.

## Stuck?

| What is wrong | Most likely cause | What to do |
|---|---|---|
| The lander does not fall | The gravity action is missing from **Create**, or **No key** uses *Stop movement* | Add gravity; make **No key** *Set horizontal speed 0* |
| The lander falls very fast | The gravity strength is too big (for example 5 instead of 0.05) | Set the strength to 0.05 |
| The lander goes through the ground | No **Collision with obj_ground**, or `obj_ground` is not Solid | Add the event; tick **Solid** |
| "Landing successful!" keeps popping up | Gravity is not switched off after landing | Add *Set gravity* strength 0 to the pad event |
| I crash every time, even on the pad | The pad is missing, or too small or too high to reach | Check `obj_pad` is in the room and Solid; use one or two blocks |
| The lander sticks to the ground after a crash | *Restart room* is missing | Add it after *Show message* |
| The text does not show | The text is black on the black room | Add *Set draw color* white before the text |
| The lander is too hard to control | Long presses of Up make it climb fast | Tap Up in short bursts |


## Challenges

- **Try this (5 minutes):** change the gravity or the thrust and see how the game feels.
- **Push further:** make the pad smaller, or build a second, harder level in another room.
- **Invent:** add a fuel counter that goes down while you thrust and stops the thrust at 0, or make a landing that is too fast count as a crash.

## Vocabulary

| Term | What it means |
|---|---|
| Thrust | A push that fights gravity (here, setting the vertical speed to -2) |
| Gravity | A force that pulls down a little more every step |
| Vertical / horizontal speed | How fast the lander moves up-down / left-right |
| Landing pad | The only place where touching down is a success |
| HUD | Text on the screen that gives the player information |


## Check Yourself

Write your answers in the notes below.

1. Why is the gravity value 0.05 and not 0.5 as in the platformer?
2. Why does **No key** reset only the horizontal speed?
3. Why must gravity be switched off when the lander lands on the pad?

## My Notes

<br>

<br>

<br>

<br>

<br>

<br>


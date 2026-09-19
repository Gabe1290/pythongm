# PyGameMaker — Tutorial 2: Your First Game — Catch the Star

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Student-Handout-02-first-game.pdf) · [ODT](downloads/Student-Handout-02-first-game.odt)

---

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Your First Game: Catch the Star** (5 pages, about 15-20 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase before moving on. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A complete little game: you move a spaceship left and right along the bottom of the screen, stars fall from the sky, and every star you catch gives you 10 points.

## Phase 1: A Moving Player

- [ ] **1.** Make a new project called `CatchTheStar` (**File > New Project**).
- [ ] **2.** Create a sprite `spr_player` (32×32) and draw a spaceship, a person or a basket. Save with **Ctrl+S**.
- [ ] **3.** Create an object `obj_player` and give it the sprite `spr_player`.
- [ ] **4.** Create a room `room_game` and place `obj_player` near the bottom centre.
- [ ] **5.** In `obj_player`, open the **Blockly** tab and add three events: **Keyboard: Left Arrow (held)** with *Set horizontal speed to -5*, **Keyboard: Right Arrow (held)** with *Set horizontal speed to 5*, and **Keyboard: No key** with *Stop movement*.

> **Done:** **You should see:** press **F5**. The arrow keys move your player left and right, and it stops when you let go. It can leave the screen — that is expected for now.

## Phase 2: Falling Stars

- [ ] **6.** Create a sprite `spr_star` (32×32) and an object `obj_star` that uses it.
- [ ] **7.** In `obj_star`, add a **Create** event with *Set vertical speed to 3*.
- [ ] **8.** Create an object `obj_spawner` with **no sprite**. Its **Create** event does *Set Alarm 0 to 60*. Its **Alarm 0** event does *Create instance of obj_star at x: random, y: 0* and then *Set Alarm 0 to 60* again.
- [ ] **9.** Place `obj_spawner` anywhere in `room_game`.

> **Done:** **You should see:** press **F5**. About one star per second appears at the top, in a different place each time, and falls. Stars pass straight through your player — that is expected for now.

## Phase 3: Catching and Scoring

- [ ] **10.** In `obj_player`, add **Collision with obj_star**: *Add to score 10*, then *Destroy other instance*.
- [ ] **11.** Create `obj_game_controller` (no sprite). Its **Create** event does *Set score to 0*; its **Draw** event does *Draw score at x: 10, y: 10*.
- [ ] **12.** In `obj_star`, add an **Outside Room** event with *Destroy this instance*.
- [ ] **13.** Place `obj_game_controller` anywhere in the room.

> **Done:** **You should see:** press **F5**. Catch a star: it disappears and the score at the top left goes up by 10. Stars you miss disappear at the bottom.

## Phase 4: Finishing Touches

- [ ] **14.** In `obj_player`, add a **Step** event that keeps the player on the screen: if x is less than 0, set x to 0; if x is greater than the room width minus the sprite width, set x to that value.
- [ ] **15.** Give `room_game` a background colour you like.

> **Done:** **You should see:** the player stops at both edges of the window, and your finished game is ready to play.

## Stuck?

| What is wrong | Most likely cause | What to do |
|---|---|---|
| The player does not move | The events are on the wrong object, or `obj_player` is not in the room | Open `obj_player` and check the three Keyboard events; open the room and check the player is placed |
| The player keeps sliding after I let go | The **No key** event is missing | Add **Keyboard: No key** with *Stop movement* |
| No stars appear | `obj_spawner` is not in the room, or its Create event does not set the alarm | Place the spawner; check *Set Alarm 0 to 60* is in its **Create** event |
| Only one star ever appears | The alarm is not set again at the end of **Alarm 0** | Add *Set Alarm 0 to 60* as the last action of **Alarm 0** |
| The score does not show | `obj_game_controller` is not in the room, or it has no Draw event | Place it; add *Draw score* in a **Draw** event |
| The score never goes up | The Collision event is on the wrong object or has no *Add to score* | Put **Collision with obj_star** on `obj_player` |
| My player disappears when it touches a star | I used *Destroy this instance* instead of *Destroy other instance* | Use **Destroy other instance** |


## Challenges

- **Try this (5 minutes):** change the star's fall speed, or the number of points for a star.
- **Push further:** make stars fall faster as the score goes up, or add a second kind of star worth more points.
- **Invent:** add a "bomb" object that ends the game if you catch it, or lives that you lose when a star reaches the bottom.

## Vocabulary

| Term | What it means |
|---|---|
| Event | Something that happens in the game (a key is pressed, two objects touch) |
| Action | What an object does when an event happens |
| Alarm | A timer; it counts down and then triggers its Alarm event |
| Spawner | An invisible object that creates other objects |
| Collision | When two objects touch |


## Check Yourself

Write your answers in the notes below.

1. What does an **alarm** do, and why does the spawner set it again at the end?
2. What is the difference between *Destroy this instance* and *Destroy other instance* in the collision event?
3. Which object draws the score, and why is it not the player?

## My Notes

<br>

<br>

<br>

<br>

<br>

<br>


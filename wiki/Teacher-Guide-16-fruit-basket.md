# PyGameMaker — Tutorial 16: Fruit Basket — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-16-fruit-basket.pdf) · [ODT](downloads/Teacher-Guide-16-fruit-basket.odt) · [Reference projects (ZIP)](downloads/solutions/16_fruit_basket_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > Fruit Basket: Catch and Avoid!**, 6 pages) and the matching student handout and worksheet. No earlier tutorial is required — this is the right first project for a student who isn't ready for Tutorial 15's "remember what you're holding" variable yet. Every action in this game is a single, ready-made block; nothing is created, named, or read back by the student.

## Overview

Students build a complete catch/avoid/win game without ever touching the idea of a variable. A basket moves along the bottom of the room; fruit and bombs are placed once and never move or respawn, so there's nothing to recycle and nothing to remember between frames. Four phases: a moving basket; placing fruit and bombs with no behaviour yet; wiring up collisions (catch a fruit for points, touch a bomb and the room restarts); and a win check once every fruit is gone.

> **Info:** If a student asks "how does the game know I caught every fruit", the honest answer is: it counts, every single step, how many `obj_fruit` instances still exist in the room — the **If count of** block. Nothing is stored or remembered on purpose; the count is just read fresh each time.

## Suggested Timing (30-35 minutes)

The tutorial says 10-15 minutes for a confident student; allow extra time for the first-ever collision event and the first-ever room restart, since both are new ideas even though neither needs a variable.

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Show the finished game; ask what happens if you touch a bomb |
| Phase 1: moving basket | 5 min | Page 2 |
| Phase 2: fruit and bombs | 5 min | Page 3 (placement only, no behaviour yet) |
| Phase 3: catching and avoiding | 10 min | Page 4 (two new collision events) |
| Phase 4: winning | 5-10 min | Page 5 |
| Worksheet / exit ticket | 5 min | Worksheet Parts A-C |


## Step-by-Step Walkthrough and Common Issues

**Phase 1: moving basket**

- Three keyboard events, exactly as in Tutorial 2 / Tutorial 9 / Tutorial 15. The basket may leave the screen; that is expected and not fixed in this tutorial.

**Phase 2: fruit and bombs**

- The most common placement mistake: a fruit placed too close to where the basket starts, so the basket "catches" it just by existing, before the player presses a key. Walk students through checking the basket's starting box against each fruit's position if this happens.
- Nothing falls and nothing moves here — a student coming from Tutorial 9 or Tutorial 15 may expect a **Create** event setting a fall speed. There isn't one; that's the point.

**Phase 3: catching and avoiding**

- `obj_fruit`'s collision handler lives on `obj_player`, not on the fruit itself — same **Destroy other instance** pattern as every other catch-game tutorial (Tutorial 2, 9, 15). A student who writes *Destroy this instance* destroys the basket instead.
- **Restart Room** is new vocabulary this tutorial introduces. It is deliberately NOT a punishment with lives or a game-over screen — make sure students notice it just starts the current room over, fruit and all, so touching a bomb costs a little time, not the game.
- A student who skips the **Draw** event will still have a working game — the score just isn't visible. This is an easy, low-stakes thing to notice and fix without re-explaining anything.

**Phase 4: winning**

- The win check is a **Step** event on `obj_player`, exactly Tutorial 9's pattern (`If count of obj_coin` becomes `If count of obj_fruit`) — a student who has done Tutorial 9 will recognise this immediately.
- If a student placed zero fruit in Phase 2 (unlikely, but it happens), the win room appears the instant the game starts. This is a good moment to point out that the count really is checked fresh every step, not stored.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`16_fruit_basket_checkpoints.zip`): one project for the end of each phase. Give a stuck student the previous phase rather than troubleshooting their collisions from scratch.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Collision | An event that fires the moment two objects touch |
| Instance count | How many copies of an object exist right now |
| Restart Room | An action that puts the current room back exactly how it started |
| Step event | An event that runs every single frame of the game, over and over |


## Discussion Questions

- Why doesn't `obj_fruit` need any events of its own, when `obj_coin` in Tutorial 9 needed a Create event and an Outside Room event?
- What's the difference between **Restart Room** and **Restart Game**? When would you want one instead of the other?
- Why can the win check in Phase 4 "just count" instead of needing to remember anything from a previous step?
- What other games let you "just try again" instead of punishing a mistake with a game-over screen?

## Differentiation

- **Support:** give the Phase 2 checkpoint, so a struggling student only has to wire up the two collision events in Phase 3-4.
- **Extension:** a second fruit type worth more points; a timer that shows how fast the room was cleared; a basket that can also move up and down to reach a second row of fruit.

## Worksheet Answer Key

**Part A:** 1-C, 2-B, 3-A, 4-D.

**Part B:** 1. `obj_player`, Collision with `obj_fruit`. 2. `obj_player`, Collision with `obj_bomb`. 3. `obj_player`, Step. 4. `obj_win_text`, When drawing. 5. `obj_win_text`, Key press: space.

**Part C:**

1. `obj_fruit` never moves and never changes — it just sits in the room waiting to be touched. All the *behaviour* ("what happens when you touch me") lives on `obj_player`'s collision events instead, the same way `obj_coin` in Tutorial 9 only needed a fall speed and `obj_fruit` here needs nothing at all, since it doesn't even fall.
2. The game would check how many bombs are left instead of how much fruit is left — since bombs are never destroyed by anything in this game, that count would never reach zero, so the win room would never appear.
3. If a bomb sat close to a fruit, a student aiming for the fruit could touch the bomb by accident while lining up the catch, turning "collect everything" into a precision-dodging challenge instead of the intended "move toward what you want" game.

**Parts D and E:** completion and reflection.

## Rubric: Fruit Basket

| Level | What the game shows |
|---|---|
| 4 - Complete | The basket moves; fruit and bombs sit in the room; catching a fruit adds 10 to the score and removes it; touching a bomb restarts the room; collecting every fruit shows YOU WIN! and SPACE restarts |
| 3 - Working | Moving and catching fruit work; the bomb restart or the win screen is missing or incorrect |
| 2 - Partly there | The basket moves and fruit/bombs are placed, but catching or avoiding doesn't work correctly |
| 1 - Started | The basket exists and moves; nothing else is placed yet |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student reached at least Phase 3 (catching a fruit works end to end)
- [ ] Note who needs the checkpoint project next time

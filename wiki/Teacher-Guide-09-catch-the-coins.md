# PyGameMaker — Tutorial 9: Catch the Coins — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-09-catch-the-coins.pdf) · [ODT](downloads/Teacher-Guide-09-catch-the-coins.odt) · [Reference projects (ZIP)](downloads/solutions/09_catch_the_coins_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > Catch the Coins: Win and Lose**, 5 pages) and the matching student handout and worksheet. Students should have finished Tutorial 2 (events, collisions, score). This is the best first "complete game" lesson: it has a clear win and a clear lose state.

## Overview

Students build a game with two endings in four phases: a moving player; coins and an enemy; catching, crashing and score; and a win check. New ideas: **room transitions** (going to a win or Game Over room), **counting instances** (*If count of obj_coin equals 0*), the **project template** "With Game Over Screen", and **Restart game**.

> **Info:** Ask "how does the game know I won?" The answer, "it counts the coins that are left", is the key idea of the lesson.

## Suggested Timing (45 minutes)

The tutorial says 15-20 minutes for a confident student; allow extra time for the template and the win room.

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Show the finished game; ask how a game decides "win" or "lose" |
| Phase 1: moving player | 5-10 min | Pages 1-2 (create the project from the template) |
| Phase 2: coins and enemy | 10 min | Page 3 |
| Phase 3: catching and crashing | 10 min | Page 4 |
| Phase 4: winning | 10 min | Page 5 |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


## Step-by-Step Walkthrough and Common Issues

**Phase 1: moving player**

- The project must be created with the **"With Game Over Screen"** template; it supplies `room_gameover`, which the crash event uses later. A project made without it has no Game Over room.
- Three keyboard events on the player, as in Tutorial 2. The player may leave the screen; that is expected.

**Phase 2: coins and an enemy**

- Coins and the enemy fall straight down (*Set vertical speed 3* in **Create**).
- **Missed coins must come back.** A coin that falls off the bottom of the room is not destroyed: it still exists, far below the screen, so the coin count never reaches 0 and the game becomes impossible to win (in the reference project a missed coin stays alive indefinitely). The tutorial therefore gives the coin and the enemy an **Outside Room** event with *Set variable y = 0*, so anything missed reappears at the top. As a side effect the enemy keeps returning, which keeps the game tense.
- The number of coins placed is the number the player must catch. Five is a good start.

**Phase 3: catching and crashing**

- Coin collision: *Add to score 1* and **Destroy other instance** (the coin). *Destroy this instance* would remove the player.
- Enemy collision: *Go to room* `room_gameover`. The room name must match exactly.
- The score is set to 0 in the player's **Create** event and drawn by a **Draw** event on the player.

**Phase 4: winning**

- A **Step** event on the player checks *If count of obj_coin equals 0*, then goes to `room_win`. It runs every frame, so as soon as the last coin is caught the win room appears.
- **If there are no coins in the room, the count is 0 immediately** and the game shows YOU WIN! on the first frame. That is the usual "instant win" mistake.
- `obj_win_text` draws the message at fixed coordinates in a default-sized room (1024×768), and restarts the game on SPACE. The Game Over room from the template restarts the same way.
- The text in the win room is drawn in the default colour (black), which is readable on the bright background the tutorial suggests. On a dark background, use *Set draw color* white.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`09_catch_the_coins_checkpoints.zip`): one project for the end of each phase. In the reference project, `room_gameover` is a small hand-made room, not the template's own. Give a stuck student the previous phase.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Win state / lose state | The two possible endings of the game |
| Room transition | Moving to another room with *Go to room* |
| Instance count | The number of copies of an object that exist, tested with *If count of* |
| Template | A ready-made project to start from |
| Step event | Runs every frame; used here to check for a win |


## Discussion Questions

- How does the game know the player has won?
- What would happen if a coin stayed alive off the bottom of the screen?
- How could we make winning harder? (More coins, faster fall, more enemies.)
- What other games use "collect them all" as the goal?

## Differentiation

- **Support:** give the Phase 2 checkpoint; use fewer coins.
- **Extension:** lives; a timer; a second enemy; coins worth different points; a "next level" room instead of the win room.

## Worksheet Answer Key

**Part A:** 1-C, 2-D, 3-B, 4-A.

**Part B:** 1. `obj_player`, Collision with `obj_coin`. 2. `obj_player`, Collision with `obj_enemy`. 3. `obj_player`, Step. 4. `obj_coin` (and `obj_enemy`), Outside Room. 5. `obj_win_text` (and the Game Over room's object), Key press: space.

**Part C:**

1. The count is already 0, so the game jumps to the win room on the first step (an instant win).
2. No. The missed coin still exists off-screen, so the count never reaches 0. That is why missed coins are sent back to the top.
3. Change *Add to score 1* in the player's **Collision with obj_coin** event to 5 (or use a second coin object with its own value).

**Parts D and E:** completion and reflection.

## Rubric: Catch the Coins

| Level | What the game shows |
|---|---|
| 4 - Complete | The player moves; coins and enemy fall and return when missed; catching scores and removes the coin; the enemy leads to Game Over; the score is displayed; catching every coin leads to a win room; SPACE restarts |
| 3 - Working | Moving, catching and crashing work; the win check or the score display is missing |
| 2 - Partly there | The player moves and coins fall, but catching or crashing does not work |
| 1 - Started | The player exists and moves; nothing falls |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student reached at least Phase 3 (a coin can be caught and the enemy ends the game)
- [ ] Note who needs the checkpoint project next time

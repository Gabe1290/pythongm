# PyGameMaker — Tutorial 2: Your First Game — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-02-first-game.pdf) · [ODT](downloads/Teacher-Guide-02-first-game.odt) · [Reference projects (ZIP)](downloads/solutions/02_first_game_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > Your First Game: Catch the Star**, 5 pages) and the matching student handout and worksheet. Students should have finished Tutorial 1 (project, sprite, object, room, F5).

## Overview

Students build a complete, playable game in four phases and test it after each one: a player that moves, stars that fall, catching and scoring, and finishing touches. New ideas: **events and actions** (keyboard, create, alarm, collision, draw, step, outside room), a **spawner** object, and **score**.

> **Info:** The most important idea of the lesson is "an object reacts to events". If a student can say "when the arrow key is held, the player's horizontal speed is set to -5", they have understood it.

## Suggested Timing (45-60 minutes)

The tutorial says 15-20 minutes for a confident student; in class allow more.

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Ask: "How could an object move?" Show the finished game on the projector |
| Phase 1: moving player | 10-15 min | Pages 1-2; check every student can move the player |
| Phase 2: falling stars | 10-15 min | Page 3; the spawner is the hardest part, walk the room |
| Phase 3: catching and scoring | 10-15 min | Page 4 |
| Phase 4 and challenges | 5-10 min | Page 5; fast students take the challenges |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


For a 45-minute slot, do Phases 1-3 and leave Phase 4 as homework.

## Step-by-Step Walkthrough and Common Issues

**Phase 1: moving player**

- The three keyboard events must all be on `obj_player`. The commonest mistake is adding them to the room or forgetting **No key**, so the player slides forever.
- *Set horizontal speed to -5* moves left, *5* moves right. Ask why one is negative.
- **Expected:** the player can leave the screen. Do not fix this yet; Phase 4 does.

**Phase 2: falling stars**

- The star's Create event sets vertical speed 3. Students often forget to assign the sprite to `obj_star`.
- The spawner has **no sprite** and must be placed in the room. If no stars appear, check this first.
- The Alarm event must set the alarm again at its end, or only one star ever appears.
- At the default 60 steps per second, *Set Alarm 0 to 60* creates **one star per second**. Ask students how to make it 2 per second (set 30).

**Phase 3: catching and scoring**

- Use **Destroy other instance**. Destroying "this" removes the player instead of the star; it is a good mistake to provoke on purpose and discuss.
- The score is drawn by a separate `obj_game_controller` that must be placed in the room. Two objects that "must be placed" (spawner and controller) are a common source of "nothing appears" questions.
- Stars that fall off the bottom are destroyed by **Outside Room**; without it they accumulate invisibly.

**Phase 4: finishing touches**

- The boundary check is the least detailed step in the tutorial: it says "if x < 0, set x = 0". Students need a conditional (test expression) block with the comparison, then a "set x" action. Give a hint or show it once. In the reference project the player can overshoot by one step (5 pixels) before being pulled back; that is normal.
- The tutorial suggests a "dark space colour" background. The score text is white, so it stays readable on dark colours.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`02_first_game_checkpoints.zip`): one project for the end of each phase. Give a stuck student the checkpoint of the previous phase so they can continue instead of falling behind.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Event | Something that happens (key held, alarm fires, collision) |
| Action | A block that does something when an event happens |
| Alarm | A countdown timer; when it reaches 0 its event runs |
| Spawner | An invisible object whose job is to create others |
| Instance | One copy of an object in a room (each star is an instance of `obj_star`) |


## Discussion Questions

- Why is the spawner invisible? (It is a helper; players should not see it.)
- What would change if the alarm were 120 instead of 60?
- Why do we need *Destroy other instance* and not just *Destroy*?
- How does the game know a star touched the player? (Collision event.)

## Differentiation

- **Support:** pair students; give the checkpoint project of the previous phase; let them skip drawing and import an image.
- **Extension:** the three challenge tiers on the handout; add lives, faster stars as score increases, or a bomb.

## Worksheet Answer Key

**Part A:** 1-C, 2-D, 3-B, 4-A.

**Part B:** 1. Keyboard: Left Arrow (held). 2. Create (on `obj_star`). 3. Collision with `obj_star` (on the player). 4. Outside Room (on `obj_star`). 5. Draw (on the controller).

**Part C:**

1. In the spawner's **Create** event (to start the timer) and at the end of **Alarm 0** (to restart it, so stars keep coming).
2. One per second (60 steps at 60 steps per second). Set the alarm to 30 for twice as often.
3. The player would be destroyed when it touches a star (the game would seem to end); *Destroy other instance* removes the star.

**Parts D and E:** completion and reflection.

## Rubric: Catch the Star

| Level | What the game shows |
|---|---|
| 4 - Complete | Player moves and is kept on screen; stars spawn at random places; catching scores 10 and removes the star; score is displayed; missed stars are cleaned up |
| 3 - Working | Movement, stars and scoring work; one polish item missing (boundary, cleanup or display) |
| 2 - Partly there | Player moves and stars fall, but catching or scoring does not work |
| 1 - Started | Player moves; no stars or scoring |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student reached at least Phase 3 (a star can be caught)
- [ ] Note who needs the checkpoint project next time

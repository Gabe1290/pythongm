# PyGameMaker — Tutorial 13: 2.5D Goals, Gems and Monsters

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Student-Handout-13-raycast-goals-monsters.pdf) · [ODT](downloads/Student-Handout-13-raycast-goals-monsters.odt)

---

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > 2.5D: Goals, Gems and Monsters** (4 pages, about 30 minutes). You continue the room from Tutorial 11 (textures from Tutorial 12 are optional). This lesson is not in the beginner edition. Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

Your first-person maze becomes a real game: collect gems for points, dodge a patrolling monster (touching it costs a life), and reach the exit, which only opens once every gem is yours.

## Phase 1: Gems and Score

- [ ] **1.** Create a sprite `spr_gem` (16×16, a yellow diamond) and an object `obj_gem` with it. Leave **Solid** off.
- [ ] **2.** In `obj_gem`: **Collision with obj_player** with *Destroy this instance*; and a **Destroy** event with *Add to score 10*.
- [ ] **3.** In `obj_player`, add a **Game Start** event (from *Other Events*): *Set score to 0* and *Set lives to 3*. Do **not** put these in Create.
- [ ] **4.** In the room, place a few gems in open corridors, off the walls, with the first one straight ahead of the player.

> **Done:** **You should see:** press **F5**. Gems float in front of you and grow as you get near. Walk into one: it disappears and you score 10. A gem behind a wall is hidden until the wall no longer blocks it. (You cannot see the score yet: that is Tutorial 14.)

## Phase 2: The Monster and Lives

- [ ] **5.** Create a sprite `spr_monster` (16×16, red) and a non-solid `obj_monster`. **When created**: *Start moving in direction* left and right, speed 2. **Collision with obj_wall**: *Reverse horizontal direction*.
- [ ] **6.** Place the monster in a long straight row so it has room to patrol.
- [ ] **7.** In `obj_player`: **Collision with obj_monster**: *Set lives to -1* (Relative), then *Restart room*. **No More Lives**: *Restart Game*.

> **Done:** **You should see:** press **F5**. The monster slides along its corridor and turns at each end. You see it coming, and it hides behind walls. Touching it costs one life; after the third, the game starts over.

## Phase 3: The Exit

- [ ] **8.** Create a sprite `spr_goal` (16×16, blue) and a non-solid `obj_goal`.
- [ ] **9.** In `obj_goal`, **Collision with obj_player** with two checks: *If count of* `obj_gem` *equals 0*: *Start block*, *Show message* "You win!", *Restart Game*, *End block*. Then *If count of* `obj_gem` *is greater than 0*: *Start block*, *Show message* "Collect all the gems first!", *End block*.
- [ ] **10.** Place `obj_goal` in the room.

> **Done:** **You should see:** press **F5**. Walk into the goal with gems left: you get the warning. Collect every gem, then walk into the goal: "You win!".

## Stuck?

| What is wrong | Most likely cause | What to do |
|---|---|---|
| I cannot see the gems | The gem is Solid (so it becomes a wall) or has no sprite | Untick **Solid**; give it a sprite |
| The gem does not vanish | The collision event is missing, or it is on the wrong object | Add **Collision with obj_player** to `obj_gem` |
| I get no points | The **Destroy** event with *Add to score 10* is missing | Add it to `obj_gem` |
| I get all my lives back after a hit | Lives were set in **Create**, which runs again on every restart | Set score and lives in **Game Start** |
| The monster does not move | The **When created** event is missing, or the monster is not in the room | Add *Start moving in direction*; place it |
| The monster goes through the walls | No **Collision with obj_wall** event on the monster | Add it with *Reverse horizontal direction* |
| The exit lets me leave with gems left | The count check is missing or uses the wrong number | Use *If count of obj_gem equals 0* for the win branch |
| The exit never wins | The checks use a wrong object name, or a gem is unreachable | Check the name; make sure every gem can be reached |


## Challenges

- **Try this (5 minutes):** make the monster faster (speed 4), or change the value of a gem.
- **Push further:** add a second monster in another corridor, or a "treasure" gem worth 50.
- **Invent:** build a second room with **Next room** at the exit, with its own camera object and textures.

## Vocabulary

| Term | What it means |
|---|---|
| Billboard | A picture that always faces you, drawn in the 3D view for non-solid objects |
| Occlusion | Hidden behind something (a gem behind a wall) |
| Game Start | An event that runs once, when the whole game begins |
| Instance count | How many copies of an object exist right now |
| Patrol | Moving back and forth along a fixed path |


## Check Yourself

Write your answers in the notes below.

1. Which objects appear as billboards in the first-person view, and which become walls?
2. Why do we set the lives in **Game Start** and not in **Create**?
3. How does the exit know that all the gems have been collected?

## My Notes

<br>

<br>

<br>

<br>

<br>

<br>


# PyGameMaker — Tutorial 13: 2.5D Goals, Gems and Monsters — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-13-raycast-goals-monsters.pdf) · [ODT](downloads/Teacher-Guide-13-raycast-goals-monsters.odt) · [Reference projects (ZIP)](downloads/solutions/13_raycast_goals_monsters_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > 2.5D: Goals, Gems and Monsters**, 4 pages) and the matching student handout and worksheet. Students continue their room from Tutorial 11 (textures from Tutorial 12 are optional). The 2.5D lessons are **hidden in the beginner edition**: switch the edition first.

## Overview

Students turn the first-person room into a game in three phases: gems and score, a patrolling monster and lives, and a gem-gated exit. New ideas: **billboards** (non-solid objects with sprites are drawn as pictures that face you, hidden behind walls), **score and lives** with **Game Start**, and the condition **If count of**.

## Suggested Timing (45-60 minutes)

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Ask: how could a flat picture stand in a 3D world? |
| Phase 1: gems and score | 15 min | Pages 1-2 |
| Phase 2: monster and lives | 15 min | Page 3 |
| Phase 3: the exit | 10-15 min | Page 4 |
| Play and swap | 5 min | Students play each other's mazes |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


## Step-by-Step Walkthrough and Common Issues

**Phase 1: gems and score**

- Every **visible, non-solid** object with a sprite is drawn automatically as a billboard, scaled by distance and **hidden behind walls**. A solid gem would become a wall. The player is the camera and is never drawn as a billboard.
- The gem's **Collision with obj_player** destroys it; its **Destroy** event adds 10 to the score. In the reference project one gem gives 10 points and vanishes.
- **Score and lives belong in Game Start, not Create.** Create runs again every time the room restarts, and the monster restarts the room. With Create, the lives would be refilled after every death. (Game Start runs once.) It is the same trap as in Tutorial 7.
- The score is not shown yet: the 3D view draws only the world. That comes in Tutorial 14.
- Place gems off the walls; an unreachable gem makes the exit impossible later.

**Phase 2: the monster and lives**

- The monster is non-solid. **When created**: *Start moving in direction* left and right, speed 2. **Collision with obj_wall**: *Reverse horizontal direction*. Place it in a long straight corridor. In the reference project it stays inside its corridor and turns around at each end.
- **Collision with obj_monster** on the player: *Set lives to -1* (relative) and *Restart room*. A collision fires when the objects **start** touching, so standing on a monster costs one life, not one per frame. **No More Lives**: *Restart Game*.
- The room restart puts the gems back, but the lives and score are kept (set in Game Start).
- A restart can cause a second hit if the monster is right at the start; keep the monster away from the player's start.

**Phase 3: the exit**

- The goal has two checks: *If count of obj_gem equals 0* (win) and *If count of obj_gem is greater than 0* (warning). With gems left, the exit only complains; with none left, it ends the game. The "count" parameter is a number (0).
- **Show message** waits for a click; students may think the game froze.
- A second room with **Next room** at the exit is the tutorial's main challenge: give that room its own camera object (with different textures) and set its Camera Object to `obj_player`.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`13_raycast_goals_monsters_checkpoints.zip`): the project at the start of the lesson (from Tutorial 11) and the finished game with one gem, a monster and the exit. Give a stuck student the finished project to compare.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Billboard | A picture that always faces the camera; used for non-solid objects |
| Occlusion | Something hidden behind a wall |
| Game Start | An event that runs once when the game begins, not on restarts |
| Instance count | The number of copies of an object, tested with *If count of* |
| Patrol | Moving back and forth |


## Discussion Questions

- How does the engine decide what is a wall and what is a billboard?
- Why can a monster in a corridor "sneak up on you" behind a corner?
- Why must the lives be set in Game Start?
- What makes a maze fair? (Reachable gems, a monster you can dodge.)

## Differentiation

- **Support:** give the finished project and let students change positions and values; keep one monster.
- **Extension:** a second, faster monster; a treasure gem worth 50; a second room with its own textures; a timer.

## Worksheet Answer Key

**Part A:** 1-B, 2-D, 3-C, 4-A.

**Part B:** 1. `obj_gem`, Destroy. 2. `obj_monster`, Collision with `obj_wall`. 3. `obj_player`, Collision with `obj_monster`. 4. `obj_goal`, Collision with `obj_player` (If count of `obj_gem`). 5. `obj_player`, Game Start.

**Part C:**

1. No: billboards are hidden behind walls until nothing blocks the line of sight.
2. One life: the collision event fires when the objects start touching, not on every frame.
3. The room restarts and Create runs again, so the lives are set back to 3: you never run out. It has to be Game Start.

**Parts D and E:** completion and reflection.

## Rubric: 2.5D Goals, Gems and Monsters

| Level | What the project shows |
|---|---|
| 4 - Complete | Gems give points and vanish; the monster patrols and costs a life that stays lost; the exit checks the gem count and wins or warns; score and lives are set in Game Start |
| 3 - Working | Gems, the monster and the exit work; the lives are refilled by restarts, or the exit is not gated |
| 2 - Partly there | Gems work, but the monster or exit does not |
| 1 - Started | Objects exist but do not appear in the first-person view |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student reached at least Phase 1 (a gem can be collected)
- [ ] Note who needs the checkpoint project next time

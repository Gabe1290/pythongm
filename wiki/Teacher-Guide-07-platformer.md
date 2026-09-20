# PyGameMaker — Tutorial 7: Platformer — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-07-platformer.pdf) · [ODT](downloads/Teacher-Guide-07-platformer.odt) · [Reference projects (ZIP)](downloads/solutions/07_platformer_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > Platformer: Run, Jump, Collect**, 4 pages) and the matching student handout and worksheet. Students should have finished Tutorials 2 and 6 (events, collisions, solid objects, score).

## Overview

Students build a platformer in three phases: gravity, running and jumping; coins, spikes and a flag; and a score and lives display. New ideas: **gravity**, **jumping** with a vertical-speed impulse, **hazards**, and lives that survive a room restart.

> **Info:** Gravity is a good place to ask "what does the computer do every step?": add 0.5 to the vertical speed, then move. A jump is just a big upward speed that gravity slowly cancels.

## Suggested Timing (60 minutes)

The tutorial says 25-30 minutes for a confident student; level building adds time.

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Ask what forces act on a jumping character |
| Phase 1: gravity, running, jumping | 15-20 min | Pages 1-2; the level layout takes time |
| Phase 2: coins, spikes, flag | 15 min | Page 3 |
| Phase 3: controller and lives | 10 min | Page 4 |
| Play and tune | 5 min | Change gravity and jump speed; play each other's levels |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


For a 45-minute slot, do Phases 1-2 and leave Phase 3 for homework.

## Step-by-Step Walkthrough and Common Issues

**Phase 1: gravity, running, jumping**

- Gravity is set once in the player's **Create** event: direction **270** (down), strength **0.5**. Angles start at 0 (right) and go counter-clockwise; 90 is up.
- **No key** must be *Set horizontal speed to 0*, **not** *Stop movement*. Stop Movement also wipes the vertical speed that gravity builds, so the player hangs in the air (in the reference project it drifts about 15 pixels in half a second instead of falling more than 100). This is the most common cause of "the player does not fall".
- The jump is on **Key press** (once per press), not *Keyboard (held)*.
- The ground needs to be **Solid**, and the player needs **Collision with obj_ground** with *Stop movement*; otherwise it falls through.
- **Keep the space above the player free** when placing them. A platform directly above the starting position blocks the jump and looks like "the jump does not work". The jump in the reference project is about 95 pixels (three tiles) high.
- Players must be placed standing on the ground (or above it). Snap to Grid 32×32 makes that easy.

**Phase 2: coins, hazards and flag**

- All the interactions are collision events **on the player**; the coin, spike and flag objects need no events.
- The spike uses *Restart room*. In Phase 2 nothing is remembered between restarts; the coins come back.
- The flag shows a message; there is no next level yet.

**Phase 3: game controller and lives**

- The controller must be placed in the room.
- **Set the score and lives in Game Start, not Create.** A Create event runs again every time the room restarts, and a spike restarts the room, so with Create the lives were reset to 3 after every spike and could never run out. (The tutorial used Create until this was corrected; if a student's screen shows "Create", it is an old copy of the instructions.) Game Start runs once, at the very start of the game.
- With Game Start, the score is also kept across restarts, so a student can collect the same coins again after each death. Ask students whether that is fair; resetting the score in the spike event is a good change.
- Nothing special happens when the lives reach 0 (no Game Over): that is a challenge at the end of the tutorial.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`07_platformer_checkpoints.zip`): one project for the end of each phase, with a small level. Give a stuck student the previous phase.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Gravity | Adds to the vertical speed every step, in the given direction |
| Vertical speed | Up is negative, down is positive |
| Impulse | A single change of speed, like the jump |
| Hazard | An object that harms the player (spike) |
| Game Start | An event that runs once when the game begins, not on room restarts |


## Discussion Questions

- Why is the jump speed negative?
- What happens to the jump if we double the gravity? Half the jump speed?
- Why does the player need a collision event with the ground as well as the ground being Solid?
- Why can't the lives be set in Create?

## Differentiation

- **Support:** give the Phase 1 checkpoint and let students build the level on top; keep the level small.
- **Extension:** moving platforms; patrolling enemies; a double jump; Game Over at 0 lives; a second room from the flag.

## Worksheet Answer Key

**Part A:** 1-C, 2-D, 3-A, 4-B.

**Part B:** 1. Create (Set gravity). 2. Key press: Up Arrow. 3. Collision with `obj_coin` (on the player). 4. Game Start (on the controller). 5. Draw (on the controller).

**Part C:**

1. About 20 steps (10 ÷ 0.5 = 20).
2. *Stop movement* in **No key**; it should be *Set horizontal speed to 0*.
3. The room restarts and the Create event runs again, so the lives are set back to 3 after every spike and never run out. It has to be Game Start.

**Parts D and E:** completion and reflection.

## Rubric: Platformer

| Level | What the game shows |
|---|---|
| 4 - Complete | Gravity, running and one jump per press work; platforms are solid; coins score and disappear; spikes cost a life that stays lost; flag shows a message; score and lives are displayed |
| 3 - Working | Movement, jumping, coins and spikes work; lives or display is missing |
| 2 - Partly there | The player falls, runs and jumps, but coins or hazards do not work |
| 1 - Started | The player and ground exist, but the player falls through or cannot move |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student reached at least Phase 1 (run and jump)
- [ ] Note who needs the checkpoint project next time

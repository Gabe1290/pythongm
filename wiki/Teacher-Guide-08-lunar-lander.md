# PyGameMaker — Tutorial 8: Lunar Lander — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-08-lunar-lander.pdf) · [ODT](downloads/Teacher-Guide-08-lunar-lander.odt) · [Reference projects (ZIP)](downloads/solutions/08_lunar_lander_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > Lunar Lander: Land on the Moon**, 4 pages) and the matching student handout and worksheet. Students should have finished Tutorial 7 (gravity, held keys, collisions).

## Overview

Students build a lunar lander in three phases: a lander with gravity and thrust, a landing pad and crash detection, and a HUD with a title. New ideas: **very weak gravity**, **thrust** as a vertical-speed change, **success and failure collisions**, and drawing text on a **black room**.

> **Info:** This is a physics-flavoured lesson. Ask "why is the Moon's gravity 0.05?" (about a sixth of Earth's; the platformer used 0.5 for a snappier feel) and let students try other values.

## Suggested Timing (45 minutes)

The tutorial says 20-25 minutes for a confident student.

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Compare with the platformer: what is different when there is almost no gravity? |
| Phase 1: flying lander | 10-15 min | Pages 1-2 |
| Phase 2: landing and crashing | 10-15 min | Page 3; includes the gravity-off point below |
| Phase 3: controller and HUD | 5 min | Page 4 |
| Play and compare | 5 min | Students try each other's levels |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


## Step-by-Step Walkthrough and Common Issues

**Phase 1: a flying lander**

- Gravity is set in **Create**: direction **270**, strength **0.05**. At 0.05 the lander reaches a speed of about 2.5 after 50 steps and about 5 after 100 steps: slow and floaty.
- **Up (held)** *sets* the vertical speed to -2 (a steady climb); it does not accelerate. After letting go, gravity slowly cancels the climb (it takes about 40 steps to stop) and then the lander falls again.
- **No key** must reset **only the horizontal** speed. Using *Stop movement* would erase the vertical speed and the lander would hang in the air.
- In this phase there is no ground collision, so the lander falls **through** the ground. That is expected.
- Use a **black** room background (space).

**Phase 2: landing and crashing**

- Ground and pad must be **Solid**, and the lander needs a collision event for each.
- Any contact with the ground is a crash, and any contact with the pad is a landing, **at any speed and from any side**. A hard landing on the pad still says "Landing successful!". Speed-based landing is the tutorial's own challenge idea.
- **Switch gravity off after landing.** Otherwise gravity keeps pushing the resting lander into the pad on every frame, the collision fires again each time, and the "Landing successful!" message pops up over and over (in the reference project it appeared 190 times in a few seconds). The tutorial now includes *Set gravity strength 0* in the pad event. This is the most likely cause of "the game is stuck showing messages".
- After the crash message the room restarts, so the lander starts again from the top.
- A pad made of one or two blocks is a fair challenge.

**Phase 3: controller and HUD**

- The controller must be placed in the room.
- Text is drawn in **black by default**, invisible on the black room, so the Draw event starts with *Set draw color* white. Without it the title and instructions do not show.
- The controller's *Set score 0* is not used further in this tutorial (there is no scoring yet); a score based on remaining fuel is a challenge.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`08_lunar_lander_checkpoints.zip`): one project for the end of each phase, with a level that has a landing pad in a gap. Give a stuck student the previous phase.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Thrust | An upward push against gravity |
| Gravity strength | How much speed is added downward each step |
| Landing pad | An object whose collision means success |
| HUD | Text on the screen for the player |
| Draw colour | The colour used by the drawing actions that follow |


## Discussion Questions

- What changes if we double the gravity? If we halve the thrust?
- Why is a very low gravity harder to control than it looks?
- How could the game tell a soft landing from a hard one? (Compare the vertical speed with a limit.)
- Why do we switch off gravity after landing?

## Differentiation

- **Support:** give the Phase 1 checkpoint; use the reference level with its pad.
- **Extension:** a fuel counter; speed-limited landing; a smaller pad; more levels; a score for remaining fuel.

## Worksheet Answer Key

**Part A:** 1-C, 2-B, 3-D, 4-A.

**Part B:** 1. Create (Set gravity). 2. Keyboard: Up Arrow (held). 3. Collision with `obj_pad`. 4. Collision with `obj_ground` (with Restart room). 5. Draw (on the controller).

**Part C:**

1. The vertical speed stays at about -2 and gravity adds only 0.05 each step, so it takes about 40 steps for the climb to stop. That is why the lander keeps rising before it falls.
2. No, the speed does not matter in the tutorial's game. To make a hard landing a crash, test the vertical speed in the pad event: if it is above a limit, crash; otherwise land.
3. Gravity keeps pushing the lander into the pad, so the collision event fires again and again. Switch gravity off (strength 0) in the pad event.

**Parts D and E:** completion and reflection.

## Rubric: Lunar Lander

| Level | What the game shows |
|---|---|
| 4 - Complete | Slow gravity, thrust and steering work; the pad gives one landing message and stops the lander; the ground crashes and restarts; the HUD text is visible |
| 3 - Working | Flying, landing and crashing work; the HUD is missing or invisible, or the landing message repeats |
| 2 - Partly there | The lander flies, but landing or crashing does not work |
| 1 - Started | The lander exists but does not fall or cannot be steered |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student reached at least Phase 1 (fly the lander)
- [ ] Note who needs the checkpoint project next time

# PyGameMaker — Tutorial 3: Classic Pong — Teacher Guide

Companion for the in-app tutorial (**Help > Tutorials > Classic Pong: Two-Player Game**, 4 pages) and the matching student handout and worksheet. Students should have finished Tutorial 2 (events, actions, collisions, score, draw).

## Overview

Students build Pong in three phases: paddles and a bouncing ball, invisible goals, and a score display. New ideas: **two players on one keyboard**, **solid objects and bouncing**, **global variables** (`global.p1score`), and drawing a variable's value.

> INFO: Pong is a good moment to talk about *rules*. Every rule is an event plus actions on one object: "when the ball touches the left goal, add 1 to Player 2's score and put the ball back".

## Suggested Timing (45-60 minutes)

The tutorial says 20-25 minutes for a confident student; in class allow more.

| Segment | Time | What happens |
| Recap and predict | 5 min | Ask: "What objects does Pong need?" Let students list them before starting |
| Phase 1: paddles and ball | 15-20 min | Pages 1-2; the longest phase, many objects |
| Phase 2: goals and scoring | 10 min | Page 3 |
| Phase 3: score display | 5-10 min | Page 4 |
| Play and swap | 5 min | Pairs play each other; then swap computers |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |

For a 45-minute slot, do Phases 1-2 in class, Phase 3 as homework.

## Step-by-Step Walkthrough and Common Issues

**Phase 1: paddles and ball**

- Students create six objects here. Suggest a checklist on the board: wall, two paddles, ball, then later two goals and a score object.
- **Solid** matters. Walls and paddles must be Solid so that *Bounce against solid objects* has something to bounce off. The ball is *not* Solid.
- Each paddle needs its own **Collision with obj_wall** event with *Stop movement*. Without it, a solid wall does not stop a paddle that has no collision event for it.
- The ball needs a Bounce event **for each object** it should bounce off (wall, left paddle, right paddle). Students often add only the wall.
- In this phase, the ball leaves the screen at the sides; that is **expected**.
- If students have the ball moving only sideways: the direction field of *Start moving in direction* must be 45 (up and to the right, 0 is right and 90 is up).

**Phase 2: goals and scoring**

- Goals are **invisible** but **Solid**: invisible so players don't see them, present so the ball's collision event fires.
- The score variables are **global**: `global.p1score`, `global.p2score`. A typo in one place (for example `global.p1Score`) creates a second, different variable, and the score seems stuck at 0.
- Left goal scores for **Player 2**, right goal for **Player 1** (the player who did not miss).
- After a goal the ball is returned to its start position but keeps its direction, so it heads for the same goal again. This is normal; it makes a good challenge ("reverse the ball's direction after each goal").

**Phase 3: score display**

- `obj_score` has no sprite and must be placed in the room, like the controller in Tutorial 2.
- Draw text is **black by default** and a new room's background is black, so without *Set draw color* the score is invisible. The tutorial page includes that block. The text is placed at y 40 and 60, below the 32-pixel wall row, so it does not overlap the top wall.

> TIP: **Reference projects.** Download the checkpoint projects from the wiki (`03_pong_checkpoints.zip`): one project for the end of each phase. Give a stuck student the previous phase so they can continue.

## Vocabulary Introduced

| Term | What it means here |
| Solid | Objects that block or bounce others (walls, paddles) |
| Bounce | An action that reverses the direction of movement after a collision |
| Global variable | A named value shared by all objects; always written with `global.` |
| Draw event | Runs every frame; used to show text and numbers |
| Start position | Where an object was placed in the room |

## Discussion Questions

- Which objects does Pong need, and which are invisible?
- Why do we keep the score in a global variable?
- What would happen if the goals were not Solid?
- Is the game fair? (The ball keeps its direction after a goal.) How could we fix it?

## Differentiation

- **Support:** give the Phase 1 checkpoint and start at Phase 2; pair a stronger and a weaker student.
- **Extension:** speed the ball up on each paddle hit; end the game at 10 points; change the bounce angle by where the ball hits the paddle.

## Worksheet Answer Key

**Part A:** 1-D, 2-C, 3-A, 4-B.

**Part B:** 1. `obj_paddle_left`. 2. `obj_ball`. 3. The ball (its Collision with a goal event adds to the score). 4. `obj_score`. 5. The paddle's Collision with `obj_wall` event.

**Part C:**

1. A collision event belongs to one specific other object; the game only runs the bounce for objects that have an event.
2. The left goal is behind Player 1's paddle; when the ball gets there, Player 1 missed, so Player 2 scores.
3. The score has to survive the ball being reset, and several objects (the ball adds to it, the score object draws it) use it, so it lives in a shared global variable.

**Parts D and E:** completion and reflection.

## Rubric: Pong

| Level | What the game shows |
| 4 - Complete | Both paddles move and are held by the walls; the ball bounces off walls and paddles; goals score for the right player and reset the ball; both scores are displayed |
| 3 - Working | Paddles, ball and scoring work; the score display or one bounce is missing |
| 2 - Partly there | Paddles move and the ball bounces, but goals do not score |
| 1 - Started | Some objects exist, but the ball does not bounce or a paddle does not move |

## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every pair has played at least one point
- [ ] Note who needs the Phase 1 checkpoint next time

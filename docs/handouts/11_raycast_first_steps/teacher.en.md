# PyGameMaker — Tutorial 11: 2.5D First Steps — Teacher Guide

Companion for the in-app tutorial (**Help > Tutorials > 2.5D: First Steps**, 4 pages) and the matching student handout and worksheet. Students should have finished Tutorial 2 and, ideally, Tutorial 6 (solid walls). This is the first of four 2.5D lessons (11-14).

> INFO: The 2.5D lessons are **hidden in the beginner edition**. Switch the edition in the preferences before the lesson, or students will not see them in the Tutorials list.

## Overview

Students build a walled room and look at it in the first person, as in Wolfenstein 3D. New ideas: a **raycast (2.5D) view**, the **camera object** (here the player), the **facing angle**, walking in the facing direction, and **solid blocks becoming walls**. It is 2.5D, not 3D: everything still has a normal 2D position and walls work like any other solid.

## Suggested Timing (45 minutes)

| Segment | Time | What happens |
| Introduction and demo | 5 min | Show the finished view; ask how a flat room can look 3D |
| Phase 1: room and walls | 15 min | Pages 1-2; 30+ blocks to place (drag to place quickly) |
| Phase 2: camera and controls | 15 min | Page 3 |
| Phase 3: test and tune | 5-10 min | Page 4; one setting at a time |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |

## Step-by-Step Walkthrough and Common Issues

**Phase 1: room and walls**

- Everything sits on a **32×32 grid**. The wall sprite must be exactly 32×32: a roughly square solid block blocks all four sides of its cell.
- The room is 320×320 (10×10 cells). The **game window takes the size of the room**, so a small room gives a small window.
- Walls must be **Solid**; the player is **not** solid. Blocks off the grid make gaps and odd wall edges.
- The player sprite (16×16) is never seen but every object needs one.

**Phase 2: camera and controls**

- The player object runs *Enable Raycast View* in its **When created** event: Field of View 66, Cell Size 32, Render Distance 20. Leave Camera Object empty (= this object).
- Turning: *Set Facing Angle* 3 and -3 with **Relative** on (add to the current angle). Left is a positive turn.
- Walking uses *Set Direction & Speed* with direction `facing_angle` (forward) or `facing_angle+180` (backward), speed 3; **No key** sets direction 0 and speed 0.
- **Do not skip the empty Collision with obj_wall.** A solid object only stops another object that has a collision event for it, even an empty one. Without it the player walks out of the room (in the reference project it ended more than 400 pixels outside). With it, the player is held inside.
- Walls are read once when the room starts, so they are fixed.

**Phase 3: test and tune**

- Suggest changing one setting at a time (Field of View, Render Distance, the three colours, Columns). Ask students to predict before they run.
- Columns: fewer columns draw faster but look chunkier.

> TIP: **Reference projects.** Download the finished lesson project from the wiki (`11_raycast_first_steps_checkpoints.zip`). Give a stuck student the finished project to compare with.

## Vocabulary Introduced

| Term | What it means here |
| Raycast / 2.5D | A first-person picture drawn from a 2D room |
| Camera | The object the view is drawn from |
| Facing angle | The direction you look, in degrees (0 right, 90 up, 180 left, 270 down) |
| Field of view | How wide the view is |
| Solid | Objects that block movement (the walls) |

## Discussion Questions

- Why is the game called 2.5D and not 3D?
- Why does the picture stay correct when you turn if the room is flat?
- What changes if the field of view is very wide? Very narrow?
- Which old lesson does the wall collision remind you of?

## Differentiation

- **Support:** give the finished project and let students only change settings.
- **Extension:** a larger room with corridors; changing the turning speed; a different wall colour per room.

## Worksheet Answer Key

**Part A:** 1-C, 2-B, 3-D, 4-A.

**Part B:** 1. Set Facing Angle (a positive value turns left). 2. Set Direction & Speed with direction `facing_angle`. 3. Render Distance (make it smaller). 4. Wall, Floor and Ceiling Colors (darker colours). 5. Tick Solid on the block's object.

**Part C:**

1. Every object needs a sprite in this engine, even if it is never drawn.
2. That `obj_wall` is Solid, and that the player has a **Collision with obj_wall** event (it may be empty).
3. 180 is left. Walking backwards uses **Down Arrow (held)** with direction `facing_angle+180`.

**Parts D and E:** completion and reflection.

## Rubric: 2.5D First Steps

| Level | What the project shows |
| 4 - Complete | A grid-aligned walled room; the raycast view is on; turning and walking work in the facing direction; walls stop the player; the student has tried at least two settings |
| 3 - Working | The view and controls work, but the walls do not stop the player or a few blocks are off the grid |
| 2 - Partly there | The room and walls exist, but the first-person view is not on |
| 1 - Started | Objects exist, but there is no room or no wall |

## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student saw the first-person view
- [ ] Note who needs the finished project next time

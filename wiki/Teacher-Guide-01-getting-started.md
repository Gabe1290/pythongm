# PyGameMaker — Tutorial 1: First Steps — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-01-getting-started.pdf) · [ODT](downloads/Teacher-Guide-01-getting-started.odt)

---

Companion for leading students through the in-app tutorial
(**Help > Tutorials > First Steps**, 4 pages) and the matching student
handout. No programming experience is assumed for you or the students.

## Overview

This first tutorial is an interface tour plus one hands-on project. By
the end, every student will have a project with one sprite, one object,
one room, and will have pressed **F5** to see it run.

> **Info:** The object students place will not move or react to anything
> yet — events and behaviors are introduced in Tutorial 2 ("First
> Game"). If a student asks "why doesn't it do anything?", that is the
> expected, correct result for this lesson, not a mistake.

## Suggested Timing (about 45 minutes)

These are starting points — adjust freely to your class and lab setup.

| Segment | Time | What happens |
|---|---|---|
| Welcome & discussion | 5 min | Open the tutorial panel (page 1), talk through what the series covers |
| Interface tour | 10 min | Page 2 — point out the 3 panels live on your own screen/projector |
| Hands-on: first project | 20-25 min | Page 3 — the 6 steps below, walk the room |
| Test & celebrate | 5 min | Everyone presses F5 and sees their object appear |
| Wrap-up / next time | 5 min | Page 4 — preview what Tutorial 2 adds |


## Step-by-Step Walkthrough & Common Issues

1. **New Project** (`File > New Project`, `Ctrl+N`) — Have students save
to a location they will remember (their own folder / the class shared
drive). Decide this convention before class starts.
2. **Create a Sprite** (`spr_player`) — The `spr_` prefix is a
PyGameMaker naming convention, not a requirement, but establishing it
now keeps later projects organized. Students can import an image or
draw one; drawing takes longer, so set a time limit (e.g. "2 minutes,
just a quick shape") if the session is tight.
3. **Create an Object** (`obj_player`) — **Most common mistake**:
forgetting to assign the sprite to the object. If a student's character
does not appear later, this is almost always why — check the object's
Sprite field first.
4. **Create a Room** (`room_game`) — Nothing visual happens at this
step; that is expected, not an error.
5. **Place the Object** — **Common mistake**: opening the room editor
but not actually selecting `obj_player` in the object list before
clicking in the room, so nothing gets placed. There is no "correct"
position for this exercise — anywhere in the room is fine.
6. **Test the Game** (`F5` or `Build > Test Game`) — A window opens
showing the room and the placed sprite. It will not move or respond to
keys yet — that is next lesson.

> **Tip:** The Test Game window. When a student presses F5, the PyGameMaker
> editor window automatically minimizes itself for the duration of the
> test and comes back when the student closes the game window. This
> stops the game window from getting lost behind the editor. On most
> lab machines the editor will also jump back to the front by itself;
> on a few Linux desktop setups it may only flash/highlight in the
> taskbar instead — if that happens, tell students to just click on it
> once to bring it forward.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Asset | Any resource in your project: a sprite, sound, object, or room |
| Sprite | An image (or animation) used to draw something on screen |
| Object | A game entity — what actually appears and behaves in a room |
| Room | A game level or screen; where objects are placed |


## If Time Allows / Sneak Peek

From the tutorial's own "Next Steps" page: next lesson adds **movement**
(a Keyboard event) and introduces **Blockly** visual programming. If a
student finishes early and asks what is next, it is fine to mention this
by name, but there is no need to have them attempt it today — there is
not yet an event to attach it to.

## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student pressed F5 and saw their object appear in the room
- [ ] Note which students want to keep exploring — good candidates to
pair with a struggling classmate next session

> **Info:** Full tutorial series: `Help > Tutorials` inside PyGameMaker.
> Written documentation and more sample projects: the project wiki.

## Worksheet Answer Key

**Part A:** 1-B, 2-D, 3-C, 4-A.

**Part B:** 1. The Asset Tree (left panel). 2. The Sprite Editor (Editor Area, opened by double-clicking the sprite). 3. The Properties panel (right). 4. The toolbar (or **Build > Test Game**, or F5).

**Part C:**

1. An object is only a description until it is placed in a room; the room is what the game actually shows. Accept any answer that separates "made" from "placed".
2. Any two of: the object has no sprite assigned; the object was never placed in the room; the wrong room was tested; the sprite is empty or transparent.
3. No. Movement needs a Keyboard event with an action, which is introduced in Tutorial 2. Students who expected movement have understood correctly that objects can move; the missing piece is the event.

**Parts D and E:** completion and reflection; no single correct answer. Use Part E to pick pairs for next session (a student who found something easy with one who found it hard).

## Rubric: The First Project

| Level | What the project shows |
|---|---|
| 4 - Complete | Saved project with a named sprite, an object using that sprite, a room with the object placed, and a game that runs with F5; names follow the `spr_` / `obj_` / `room_` pattern |
| 3 - Working | Runs with F5 and the object is visible; one naming or organisation slip |
| 2 - Partly there | All assets exist, but the object is missing from the room, or has no sprite |
| 1 - Started | Project created, but fewer than three of sprite, object, room exist |


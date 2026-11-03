# My First Maze (Junior Edition): Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Junior-Maze-Lesson-Teacher.pdf) · [ODT](downloads/Junior-Maze-Lesson-Teacher.odt) · [Starter project](downloads/Junior-Maze-Starter.zip) · [Finished project](downloads/Junior-Maze-Finished.zip)

---

## At a Glance

| | |
|---|---|
| Age | 8 to 9, using the **Junior** edition of PyGameMaker |
| Time | 90 minutes |
| Students make | A one-screen maze: draw a hero and a goal, move the hero with the arrow keys, stop at walls, win at the goal, export as one `.html` file |
| Needs | PyGameMaker in Junior mode, the starter project, a web browser. Internet is **not** needed to play this game |
| Student sheet | Junior Maze: Student Handout (one for each student) |

Everything in the lesson uses only blocks that exist in the Junior toolbox. The
finished game was run in the real game engine, exported, and played in a
browser to check it.

## Before the Lesson (15 minutes, once)

1. **Switch on Junior mode** on each computer: Tools > Preferences > General >
   IDE Edition > Junior, then restart the IDE.
2. **Copy the starter project** (`Junior-Maze-Starter.zip`, from the wiki page
   or `wiki/downloads/`) and unzip it so each student has a folder called
   **My Maze**.
3. **Try the lesson yourself once.** The finished version is in
   `Junior-Maze-Finished.zip` to compare with.
4. **Decide how the game will get to a phone** (see "Playing on a Phone" below).
   Do this before class, not after.
5. Print the student handout, or put it on a second screen.

> INFO: If a computer was ever set to another theme or font in Preferences,
> Junior's bigger text will not apply. Reset them there.

## What the Starter Contains

A brown wall picture (`spr_wall`), a **Solid** wall object (`obj_wall`) and an
empty 640 by 416 room (`room0`) with its border already built. Students draw
their own hero and goal and do the rest. The room is on a 32-pixel grid and
snap-to-grid is on.

## Lesson Plan (90 minutes)

| Time | Part | What happens | If you are late |
|---|---|---|---|
| 0-10 | Warm-up | Show the finished game (play it, ideally on a phone). Ask: what does it need? A hero, walls, a goal | Skip the discussion |
| 10-15 | 1. Open | Open the starter, press F5 | |
| 15-30 | 2. Sprites | Create Sprite twice (hero, goal) | Give them the art from the Finished project |
| 30-50 | 3. Hero | Create Object, six Blockly rows | Show the first row on the board, then they copy it |
| 50-60 | 4. Goal | One object, two blocks | |
| 60-80 | 5. Maze | Paint walls, place hero and goal, test | Give a ready maze: open the Finished room |
| 80-88 | 6. Export | Export as HTML5, open in browser | Do the export as a class demo |
| 88-90 | Wrap-up | Swap and play; the "Think About It" questions | |

Parts 2 to 4 are the same for everyone. Part 5 is where students spend their
creativity, so protect that time.

## Walkthrough and Common Problems

**Part 2, drawing.** Create Sprite opens a blank 32 by 32 picture in the sprite
editor. Remind students to click Save in the editor. A sprite name that exists
already gives a "Name Already Used" message instead of overwriting.

**Part 3, the hero.** Six events: four held arrow keys, No key, and a collision
with `obj_wall`. The rows are copy-able: students use right-click > Duplicate
and change the key and number.

- Without **No key** the hero never stops.
- Without the **collision** row the hero walks straight through the walls: the
  wall being Solid does not stop it by itself (checked: it left the room). The
  collision row with **Stop movement** is what makes the wall a wall.
- A speed of 4 moves the hero 4 pixels each step, 60 steps a second.

**Part 4, the goal.** The goal object holds the win logic: *when colliding with
obj_hero: Show message, then Restart room*. The message can say anything, and
punctuation is safe.

**Part 5, the maze.**

- **Two squares wide.** This is the rule that matters most. The hero stops
  wherever a key is released, not on the grid. In a one-square path it can end
  up a few pixels off and jam. Every corridor in the reference maze is two
  squares wide, and a test plays it with the hero placed up to 24 pixels off the
  grid and always reaches the goal.
- Holding the mouse down and dragging paints a row of walls. A click places one.
- Check that the maze can be finished before swapping.
- Place the hero and the goal inside the border, on empty squares.

## Exporting

File > Export as HTML5 asks for a folder and offers to open the game in the
browser. The result is **one file**, named after the project. This game has no
Python code, so it needs no internet to play. The window above the game
shows **Score** and **Lives**; this maze does not use them, so students may ask
about them. They can be ignored.

## Playing on a Phone

What is known:

- The exported page detects a touchscreen and then shows four arrow buttons
  under the game. Holding a button moves the hero. This was
  checked in a phone-sized browser on a computer, **not on a real phone**.
- The game page is built for narrow screens and shrinks to fit.

What to plan for:

- **Getting the file onto the phone.** Phones often cannot open an `.html` file
  from their storage (iPhones in particular). The dependable way is to put the
  file on a **web address** (the school's web space or a free site host), then
  open that address on the phone. This was not tested here.
- **Speed on a fast screen.** The exported game takes one step per screen
  refresh. On a 60 Hz screen this is the intended speed. On a phone with a
  90 or 120 Hz screen the hero will move faster, up to twice as fast. This is
  a known limit of the HTML5 export that has not been fixed. A maze is still
  playable, but keep it in mind for any game that needs careful timing.

## Differentiation

- **Needs support:** start from the Finished project's room and only change the
  walls, or give a printed maze to copy.
- **Going further:** add coins that give points (Tutorial 2, "Your First
  Game", teaches the score blocks), or a second goal. Both use blocks that are
  in the Junior toolbox.

## Assessment

Ask each student to show you: a sprite they drew, a hero that moves and stops
at walls, a maze that can be finished, and the exported `.html` file working in
a browser. The three "Think About It" questions work as an exit ticket.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Hero does not move | The hero is not placed in the room, or the arrow rows are missing |
| Hero goes through walls | Missing the collision row (**When colliding with** obj_wall, **Stop movement**) on the hero |
| Hero stuck in a path | Path is one square wide. Widen it |
| Nothing at the goal | Goal needs the collision event with `obj_hero` |
| "You win!" repeats | It should show once, then the room restarts. Check **Restart room** is under the same event |
| Grey game window | Slow or low-memory computer. Wait, then try again |
| Something deleted | Tools > Restore Deleted Assets |

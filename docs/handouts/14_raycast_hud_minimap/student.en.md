# PyGameMaker — Tutorial 14: 2.5D HUD and Minimap

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > 2.5D: HUD and Minimap** (4 pages, about 25 minutes). You continue the game from Tutorial 13. This lesson is not in the beginner edition. Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A dashboard for your first-person game (a **HUD**, heads-up display): score and lives on the screen, a minimap in the corner, and a DOOM-style status bar with a health meter.

## Phase 1: Score and Lives

- [ ] **1.** Open `obj_player` and add a **Draw** event.
- [ ] **2.** In it: *Set draw color* white (`#ffffff`); *Draw score* at x 8, y 8, caption "Score: "; *Draw lives* at x 230, y 6 with the sprite `spr_player`.

> DONE: **You should see:** press **F5**. The score is at the top left, and one small icon per life at the top right. Pick up a gem and the score goes up; touch the monster and an icon disappears.

> TIP: **Draw text is black by default, Draw score is white.** Set the colour once at the top of the Draw event so everything is predictable. The object that draws the HUD must be **visible**.

## Phase 2: The Minimap

- [ ] **3.** In the same **Draw** event, after the other actions, add *Draw Minimap* with X 230, Y 10, Size 80.

> DONE: **You should see:** press **F5**. A small map of the walls appears in the top right. An arrow shows where you are and looks the way you look. North is always at the top; the map does not turn, the arrow does. It does not show gems or monsters.

## Phase 3: The Status Bar

- [ ] **4.** Make room: in `obj_player`'s **When created**, on *Enable Raycast View* set **Viewport Height** to **256** (the room is 320 tall and the bar is 64).
- [ ] **5.** In **Game Start**, add *Set health* to 100 after the score and lives.
- [ ] **6.** In the **Draw** event, replace the score and lives with *Draw DOOM HUD*: X 0, Y **-1** (bottom of the window), Width **0** (full width), Height **64**, Health Label "HEALTH", Score Label "SCORE ". Keep *Draw Minimap*.

> DONE: **You should see:** press **F5**. The 3D view sits above a dark bar showing a green health bar with its number, your score and your lives. The minimap is still in the corner.

## Stuck?

| What is wrong | Most likely cause | What to do |
| I see no HUD at all | The HUD object is invisible, or has no **Draw** event | Keep **Visible** on; add a Draw event |
| My text is invisible | It is black text on a dark scene | Add *Set draw color* white first |
| The score never changes | No score events (Tutorial 13), or the object is not in the room | Check the gem events |
| The status bar covers part of the view | **Viewport Height** is 0 or too big | Set it to the room height minus the bar (320 - 64 = 256) |
| The bar is at the wrong place | Y is not -1, or Height does not match | Use Y -1 and Height 64 |
| The health bar is empty | *Set health* was not set | Add *Set health* 100 in **Game Start** |
| The minimap is in the wrong corner | X and Y are wrong | Use X 230, Y 10 for a 320-wide room |
| The minimap shows no arrow | The camera was not found | Check that the player runs *Enable Raycast View* |

## Challenges

- **Try this (5 minutes):** change the minimap size or colours.
- **Push further:** the monster takes 25 health instead of a life, and health refills when a life is lost.
- **Invent:** a minimap you can switch on and off with the M key, a face picture in the bar that changes with health, or an objective counter.

## Vocabulary

| Term | What it means |
| HUD | Text and pictures on the screen that inform the player |
| Draw event | Draws things on top of the view every frame |
| Minimap | A small top-down map of the walls with a marker for you |
| Viewport | The part of the window where the 3D view is drawn |
| Status bar | A panel along the bottom with health, score and lives |

## Check Yourself

Write your answers in the notes below.

1. Why must the object that draws the HUD be visible?
2. Why does the 3D view need a **Viewport Height** for the status bar?
3. Why does the minimap not show the gems?

## My Notes

[[notes:10]]

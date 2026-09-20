# PyGameMaker — Tutorial 11: 2.5D First Steps

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > 2.5D: First Steps** (4 pages, about 20-25 minutes). This lesson is not in the beginner edition: your teacher may need to switch the edition first. Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A small room you explore **in the first person**, like the classic game Wolfenstein 3D. It is still an ordinary 2D room (walls have a normal x and y); only the picture on the screen is drawn as if you were standing inside. You turn with the arrow keys, walk forward and back, and bump into real walls.

## Phase 1: The Room and the Walls

- [ ] **1.** Create a project `FirstPerson` with the **Empty Project** template.
- [ ] **2.** Create sprite `spr_wall` (**32×32**, grey or bricks) and sprite `spr_player` (16×16, any colour; you will never see it).
- [ ] **3.** Create `obj_wall` (sprite `spr_wall`) and tick **Solid**. Create `obj_player` (sprite `spr_player`), **not** solid.
- [ ] **4.** Create `room_main` with width and height **320**, and show the grid (32 by default, so blocks snap).
- [ ] **5.** Place walls in every border cell: top row x 0 to 288 (y 0), bottom row (y 288), left and right columns between the corners, and three blocks inside at (128, 128), (160, 128) and (128, 160).
- [ ] **6.** Place `obj_player` at (48, 48).

> DONE: **You should see:** a 10×10 grid of cells with a ring of wall blocks and three blocks inside. (You cannot see the 3D view yet.)

## Phase 2: The Camera and the Controls

- [ ] **7.** In `obj_player`, **When created**: *Enable Raycast View* with Field of View **66**, Cell Size **32**, Render Distance **20**. Leave Camera Object empty (it means "this object").
- [ ] **8.** **Keyboard: Left Arrow (held)**: *Set Facing Angle* **3**, Relative on. **Right Arrow (held)**: *Set Facing Angle* **-3**, Relative on.
- [ ] **9.** **Up Arrow (held)**: *Set Direction & Speed* direction `facing_angle`, speed **3**. **Down Arrow (held)**: direction `facing_angle+180`, speed **3**. **No key**: direction 0, speed 0.
- [ ] **10.** Add **Collision with obj_wall** and leave it **empty**. Do not skip it: without it the player walks through the walls.

> DONE: **You should see:** press **F5**. The room appears in first person: grey walls, a blue ceiling and a dark floor. The arrows turn and walk you, and you cannot leave the room.

## Phase 3: Test and Tune

- [ ] **11.** Change one setting of *Enable Raycast View* at a time and press **F5**: Field of View 40 and 100; Render Distance 3; Wall Color, Floor Color, Ceiling Color; Columns.
- [ ] **12.** Write down what each change did in your notes.

> DONE: **You should see:** a narrow view for 40, a wide, slightly fish-eyed view for 100, far walls disappearing for a short Render Distance, and new colours.

## Stuck?

| What is wrong | Most likely cause | What to do |
| I see the normal top-down room | The *Enable Raycast View* action is missing, or it is on an object that is not in the room | Put it in `obj_player`'s **When created** and place the player in the room |
| I walk through walls | The empty **Collision with obj_wall** is missing, or `obj_wall` is not Solid | Add the event (leave it empty); tick **Solid** |
| The walls look wrong or have gaps | A wall is off the 32-pixel grid, or Cell Size is not 32 | Use grid snapping; set Cell Size 32 |
| I turn the wrong way | The 3 and -3 are swapped | Swap them on the two turning events |
| I cannot move but I can turn | Up and Down have no *Set Direction & Speed*, or the direction is not `facing_angle` | Check the direction text exactly |
| I keep walking after I let go | The **No key** event is missing | Add direction 0, speed 0 |
| The window is tiny | The window takes the size of the room (320×320) | Make a bigger room, keeping walls on the grid |
| Nothing is visible on the walls | The wall sprite is fully transparent | Draw a filled 32×32 sprite |

## Challenges

- **Try this (5 minutes):** make a dungeon or a Mars base with the three colour settings.
- **Push further:** build a larger room with corridors (keep every wall on the 32-pixel grid).
- **Invent:** make the turning faster or slower by changing the 3 and -3.

## Vocabulary

| Term | What it means |
| 2.5D (raycast) | A first-person picture drawn from a 2D room, as in Wolfenstein 3D |
| Camera | The object the view is drawn from (here, the player) |
| Facing angle | The direction you look, in degrees (0 = right, 90 = up) |
| Field of view | How wide the view is, in degrees |
| Cell size | The size of one grid cell (32 pixels); walls must be on this grid |

## Check Yourself

Write your answers in the notes below.

1. Why is this called 2.5D and not 3D?
2. Why does the player need a **Collision with obj_wall** event that has no actions?
3. What does *Relative* mean when the facing angle is set?

## My Notes

[[notes:10]]

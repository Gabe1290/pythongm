# PyGameMaker — Tutorial 12: 2.5D Textures, Sky and Floor

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > 2.5D: Textures, Sky and Floor** (4 pages, about 20-25 minutes). You need your finished project from Tutorial 11 (or your teacher's copy). This lesson is not in the beginner edition. Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

The same first-person room, dressed up: brick walls, a sky that slides when you turn, and a tiled floor. Nothing about how the game plays changes; only how it looks.

## Phase 1: Textured Walls

- [ ] **1.** Create a sprite `spr_wall_texture`, **64×64**: a brick red fill with lighter mortar lines (a horizontal line every 16 pixels, and short vertical lines shifted by half a brick on every other row). Or import a square picture.
- [ ] **2.** In `obj_player`'s **When created**, on *Enable Raycast View* set **Wall Texture** to `spr_wall_texture`.

> DONE: **You should see:** press **F5**. Every wall shows bricks. Walls facing away from the light are darker. Bricks grow when you walk closer.

## Phase 2: Sky and Floor

- [ ] **3.** Create a sprite `spr_sky`, **256×64** (wide and short, like a strip of a panorama): sky blue with clouds, a sun or mountains.
- [ ] **4.** Create a sprite `spr_floor`, **32×32**, the size of one grid cell: a checkerboard, flagstones or planks.
- [ ] **5.** On *Enable Raycast View* set **Sky Texture** to `spr_sky` and **Floor Texture** to `spr_floor`.
- [ ] **6.** Optional: no sky? Leave **Sky Texture** empty and set **Ceiling Texture** instead (it is used only when there is no sky).

> DONE: **You should see:** press **F5**. The sky slides sideways when you turn, but does not get bigger when you walk. The floor tiles shrink toward the horizon and meet the walls neatly.

## Phase 3: Tune the Look

- [ ] **7.** Clear **Sky Texture** and run again: you get the flat ceiling colour back.
- [ ] **8.** Set **Textured Walls** off: flat wall colours even though a Wall Texture is set.
- [ ] **9.** Try **Columns** (default 320) and **Floor Detail** (default 4) with different values. Raise Floor Detail to 6 or 8 for speed; lower Columns if it is still slow.

> DONE: **You should see:** the fallback colours when a texture is empty, and a chunkier but faster picture with higher Floor Detail or fewer Columns.

## Stuck?

| What is wrong | Most likely cause | What to do |
| The walls are still plain colour | Wall Texture is empty or misspelled, or **Textured Walls** is off | Type the exact sprite name; turn Textured Walls on |
| The sky does not appear | Sky Texture is empty or the name is wrong | Set it to `spr_sky` exactly |
| The floor looks blurry | The tile is not 32×32, or Floor Detail is high | Use a 32×32 tile; try Floor Detail 4 |
| The bricks look stretched | The picture is not square | Use a square picture such as 64×64 |
| The ceiling texture does nothing | A Sky Texture is set (the sky wins) | Clear Sky Texture to see the ceiling |
| The game is slow | Floor Detail is low or Columns is high | Raise Floor Detail, lower Columns |
| The sky jumps when I turn | The picture is too narrow | Use a wide picture such as 256×64 |
| The texture name has a typo | Names must match exactly | Copy the sprite name |

## Challenges

- **Try this (5 minutes):** make a second wall look (mossy stone) and swap by changing one name.
- **Push further:** design an indoor room with no sky and a **Ceiling Texture** of wooden planks.
- **Invent:** a dark cave with a nearly black ceiling colour and a short Render Distance (5).

## Vocabulary

| Term | What it means |
| Texture | An ordinary sprite used to cover a wall, the floor or the ceiling |
| Panorama | A wide picture that wraps around you (the sky) |
| Tile | A small picture repeated over an area (the floor) |
| Fallback colour | The plain colour used when a texture is empty |
| Floor Detail | How coarse the floor is; higher is faster but blockier |

## Check Yourself

Write your answers in the notes below.

1. What does the sky do when you turn, and what does it not do when you walk?
2. What happens to the walls if you leave **Wall Texture** empty?
3. Which two settings trade picture detail for speed?

## My Notes

[[notes:10]]

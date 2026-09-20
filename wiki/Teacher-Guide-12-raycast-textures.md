# PyGameMaker — Tutorial 12: 2.5D Textures, Sky and Floor — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-12-raycast-textures.pdf) · [ODT](downloads/Teacher-Guide-12-raycast-textures.odt) · [Reference projects (ZIP)](downloads/solutions/12_raycast_textures_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > 2.5D: Textures, Sky and Floor**, 4 pages) and the matching student handout and worksheet. Students continue their project from Tutorial 11. The 2.5D lessons are **hidden in the beginner edition**: switch the edition first.

## Overview

Students dress up the first-person room with textures. New ideas: a **texture is just a sprite** chosen in *Enable Raycast View*, a **panning sky**, a **tiled floor**, **fallback colours**, and the **detail versus speed** settings. The game does not change, so this is a good art and design lesson.

## Suggested Timing (45 minutes)

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Show flat grey walls vs textured; ask what makes it look real |
| Phase 1: textured walls | 10-15 min | Pages 1-2; drawing the brick takes time, or import an image |
| Phase 2: sky and floor | 15 min | Page 3 |
| Phase 3: tune the look | 10 min | Page 4 |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


## Step-by-Step Walkthrough and Common Issues

**Phase 1: textured walls**

- A texture is an ordinary sprite. Set **Wall Texture** on *Enable Raycast View* to the sprite's exact name. **Square** pictures such as 64×64 look best.
- If **Wall Texture** is empty the walls are drawn in the flat **Wall Color**. **Textured Walls = off** forces flat colour even when a texture is set (useful for comparing).
- Walls facing away from the light are drawn darker; this is a normal shading trick that makes corners look solid.

**Phase 2: sky and floor**

- The **sky** is a wide picture (256×64). It pans sideways as you turn (one full turn slides the picture past once) but does not change size as you walk, like a far-away horizon.
- The **floor** tile should be 32×32, one grid cell. It repeats once per cell and lines up with the bottoms of the walls.
- **Ceiling Texture** is used **only when no sky is set**; a Sky Texture always wins.
- Empty names mean fallback colours (Wall, Floor and Ceiling Color). In the reference project, clearing the texture names gives the flat colours again.

**Phase 3: tune the look**

- **Columns** (default 320) and **Floor Detail** (default 4) trade detail for speed: fewer columns and a higher Floor Detail are faster but chunkier. A good order to try on a slow computer: raise Floor Detail to 6-8 first, then lower Columns.
- Typos in texture names are the most common problem; ask students to copy names.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`12_raycast_textures_checkpoints.zip`): the project at the start of the lesson (the result of Tutorial 11) and the finished, textured project. The textures in the reference project are simple generated images; students should draw or import their own.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Texture | A sprite used to cover a wall, floor or ceiling |
| Panorama | A wide picture that pans as you turn (the sky) |
| Tile | A small picture repeated across the floor |
| Fallback colour | The plain colour used when a texture is not set |
| Columns / Floor Detail | The two speed versus detail settings |


## Discussion Questions

- Why does the sky move when we turn but not when we walk?
- Why should a floor tile match the size of a grid cell?
- How do old games get away with such simple pictures?
- What would you change to make a spooky level?

## Differentiation

- **Support:** provide ready-made texture images to import; start from the finished project and change one texture.
- **Extension:** several wall looks; an indoor ceiling; a cave with dark colours and short Render Distance.

## Worksheet Answer Key

**Part A:** 1-C, 2-D, 3-A, 4-B.

**Part B:** 1. Wall Texture. 2. Sky Texture. 3. Floor Texture. 4. Set Textured Walls off. 5. Raise Floor Detail.

**Part C:**

1. The sky: a Sky Texture always wins over a Ceiling Texture.
2. The floor is drawn one tile per cell, so a 32×32 tile lines up with the cells and the wall bottoms, and the floor does not seem to slide.
3. That the texture name is spelled exactly like the sprite, and that **Textured Walls** is on.

**Parts D and E:** completion and reflection.

## Rubric: 2.5D Textures

| Level | What the project shows |
|---|---|
| 4 - Complete | Textured walls, a sky that pans and a tiled floor; the student can explain the fallback colours and the detail settings |
| 3 - Working | Walls and either the sky or the floor are textured |
| 2 - Partly there | Only the walls are textured, or names are wrong so some textures do not show |
| 1 - Started | The room still shows flat colours |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student saw a textured wall
- [ ] Note who needs the checkpoint project next time

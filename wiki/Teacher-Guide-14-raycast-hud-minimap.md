# PyGameMaker — Tutorial 14: 2.5D HUD and Minimap — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-14-raycast-hud-minimap.pdf) · [ODT](downloads/Teacher-Guide-14-raycast-hud-minimap.odt) · [Reference projects (ZIP)](downloads/solutions/14_raycast_hud_minimap_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > 2.5D: HUD and Minimap**, 4 pages) and the matching student handout and worksheet. Students continue the game from Tutorial 13. The 2.5D lessons are **hidden in the beginner edition**: switch the edition first. This is the last lesson of the series.

## Overview

Students add a HUD to the first-person game in three phases: score and lives text, a minimap, and a DOOM-style status bar. New ideas: the **Draw event over the 3D view**, why the HUD object must be **visible**, one-action helpers (**Draw Minimap**, **Draw DOOM HUD**), and the **Viewport Height** letterbox.

## Suggested Timing (45 minutes)

| Segment | Time | What happens |
|---|---|---|
| Recap and predict | 5 min | Show a classic shooter dashboard; ask what information it shows |
| Phase 1: score and lives | 10 min | Pages 1-2 |
| Phase 2: minimap | 10 min | Page 3 |
| Phase 3: status bar | 15 min | Page 4 |
| Worksheet / exit ticket | 5 min | Worksheet parts A-C |


## Step-by-Step Walkthrough and Common Issues

**Phase 1: score and lives**

- The 3D view draws only the world. Anything on top comes from a **Draw** event, on the player here.
- **The HUD object must be visible.** Its Draw event runs only while the object is visible. The player (camera) is never drawn in the 3D view but is still "visible", so its Draw event works. An invisible HUD object silently draws nothing.
- **Draw colour.** *Draw text* is **black** by default, *Draw score* is **white**. A dark scene hides black text, so start the Draw event with *Set draw color* white. (In the reference project the score text shows white on the view and the lives icons sit at the top right.)
- One icon per remaining life is drawn from a sprite (the player's).

**Phase 2: the minimap**

- One action draws the whole map. It is **north-up** (the map does not rotate; the arrow does) and shows **walls and the player only**, on purpose: a map that shows every gem makes a collect-them-all game too easy.
- Position it with X, Y (top-left corner, in screen pixels) and Size; in the reference project a size-80 map at X 230, Y 10 draws in the top-right corner and nowhere else.
- The three colours have good defaults.

**Phase 3: the status bar**

- The bar needs room. **Viewport Height** on *Enable Raycast View* squeezes the 3D view into the top band; the default 0 uses the whole window (and the bar would cover part of it). For a 320-pixel room and a 64-pixel bar, Viewport Height = 320 - 64 = 256.
- *Draw DOOM HUD*: **Y = -1** means the bottom of the window, **Width = 0** means full width, and **Height** must match the band you reserved (64). It shows a health bar with a number, the score and the lives.
- **Health:** set it in **Game Start** (*Set health* 100); otherwise the bar is empty.
- The bar's Objective Label and Face Sprite are for the challenges; the defaults show "Keys" and no face.

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`14_raycast_hud_minimap_checkpoints.zip`): the project at the start of the lesson (the result of Tutorial 13) and the finished game with the status bar and the minimap. In the finished project the score/lives text is replaced by the bar, as in the tutorial.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| HUD | The information drawn over the game view |
| Minimap | A small north-up map of the walls |
| Viewport | The part of the window used by the 3D view |
| Status bar | A panel along the bottom (health, score, lives) |
| Letterbox | Squeezing the view to leave a band for something else |


## Discussion Questions

- What information does a player need at every moment?
- Why is the minimap north-up? What would rotating it change?
- Why should the map not show the gems?
- How would you design a HUD for a different kind of game?

## Differentiation

- **Support:** give the Phase 1 project and add one HUD element at a time.
- **Extension:** a map toggle with M; a face picture in the bar; monsters that take 25 health; an objective counter.

## Worksheet Answer Key

**Part A:** 1-C, 2-D, 3-B, 4-A.

**Part B:** 1. Draw score. 2. Set draw color (white). 3. Draw Minimap. 4. Viewport Height on Enable Raycast View. 5. Draw DOOM HUD.

**Part C:**

1. Viewport Height 480 - 60 = 420; the bar's Height is 60.
2. The arrow turns; the walls and the map do not (north stays at the top).
3. The text colour is black on a dark scene (no Set draw color), or the object is invisible or has no Draw event.

**Parts D and E:** completion and reflection.

## Rubric: 2.5D HUD and Minimap

| Level | What the project shows |
|---|---|
| 4 - Complete | Score and lives (or the status bar) are visible and correct; a minimap with an arrow; a correct Viewport Height with a status bar that does not cover the view; health is set |
| 3 - Working | The HUD text and the minimap work; the status bar is missing or covers part of the view |
| 2 - Partly there | Only the score is displayed |
| 1 - Started | The HUD object exists but nothing is drawn |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every student saw the HUD over the 3D view
- [ ] Note who needs the checkpoint project next time

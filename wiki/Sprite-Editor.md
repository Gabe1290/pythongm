# Sprite Editor

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es)

---

> [Back to Home](Home)

Sprites are the images and animations attached to objects. The Sprite Editor is a built-in pixel-art tool — draw sprites directly in PyGameMaker, no external image editor required.

---

## Opening the Sprite Editor

1. Double-click an existing sprite in the resource tree, or
2. Right-click **Sprites** > **Create Sprite**

![The Sprite Editor: drawing tools and brush size on the left, the origin
picker and Precise Collision toggle below them, a colour palette, the
canvas in the center showing a pixel-art character at 10x zoom, and the
frame strip along the bottom (8 frames, Play button, frame add/duplicate/
delete)](images/sprite-editor.png)

---

## Drawing Tools

| Tool | Shortcut | What it does |
|------|----------|---------------|
| **Pencil** | P | Draw individual pixels |
| **Eraser** | E | Erase pixels to transparent |
| **Picker** | I | Pick a color from the canvas |
| **Fill** | G | Flood-fill a connected area |
| **Line** | L | Draw a straight line |
| **Rect** | R | Draw a rectangle (toggle **Filled** for solid vs. outline) |
| **Ellipse** | O | Draw an ellipse (also respects **Filled**) |
| **Select** | S | Rectangular selection — move, copy, cut, paste, or delete the selected pixels |

**Brush size** applies to Pencil, Eraser, and line/shape outlines. The
color palette holds a working set of colors plus the standard 12-color
quick palette; click a swatch to pick, or use the Picker tool to lift a
color straight from the sprite.

---

## Canvas Operations

- **Mirror H / Mirror V** — flip the current frame horizontally or vertically
- **Resize** — opens a dialog with two distinct modes:
  - **Scale Image** — stretches the existing content to a new size
  - **Resize Canvas** — keeps content at its original size and adds/crops
    space around it, anchored to a corner, edge, or center you pick
- **Grid** — toggles a pixel-boundary grid overlay (doesn't affect the
  saved image)
- **Zoom In / Zoom Out** — the canvas commonly works at 10x or higher,
  since sprites are usually small (16×16 to 64×64 is typical)
- **Export PNG…** — saves the current frame as a standalone `.png` file
- Right-click the canvas for **Copy / Cut / Paste / Delete / Deselect /
  Select All** (standard shortcuts: Ctrl+C / Ctrl+X / Ctrl+V / Del / Esc)

---

## Frames and Animation

A sprite can hold multiple frames, played back as an animation at
runtime. The frame strip along the bottom of the editor:

| Control | Effect |
|---------|--------|
| **+** | Add a new blank frame |
| **D** | Duplicate the current frame |
| **-** | Delete the current frame |
| **Play** | Preview the animation in the editor at the sprite's frame rate |

Click any frame thumbnail to jump to it and draw on that frame specifically.

---

## Origin and Collision

- **Origin** — the point objects using this sprite treat as position
  `(x, y)`. Presets: Top-Left, Top-Center, Center, Center-Bottom,
  Bottom-Left, Bottom-Right, or **Custom** (set exact X/Y). Most
  platformer/top-down characters use **Center-Bottom** so the sprite's
  feet sit at the object's Y position.
- **Precise Collision** — enabled, collisions against this sprite test
  actual non-transparent pixels rather than the sprite's bounding box.
  More accurate for irregularly-shaped sprites, more expensive to compute
  — leave it off for simple shapes (walls, coins) and reserve it for
  sprites where bounding-box collision would feel visibly wrong.

---

## Next Steps

- [[Object-Editor]] - Attach a sprite to a game object
- [[Room-Editor]] - Place object instances that use your sprite
- [[Creating-Your-First-Game]] - A full tutorial walkthrough that starts with drawing sprites

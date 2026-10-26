# Drawing

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Draw Arrow

| Property | Value |
|----------|-------|
| **Name** | `draw_arrow` |
| **Icon** | ➡️ |
| **Category** | Drawing |

Draw an arrow from one point to another

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Start X |
| `y1` | Number | `0` | Start Y |
| `x2` | Number | `100` | Tip X |
| `y2` | Number | `100` | Tip Y |
| `tip_size` | Number | `10` | Arrowhead size in pixels |

### Draw Background

| Property | Value |
|----------|-------|
| **Name** | `draw_background` |
| **Icon** | 🌄 |
| **Category** | Drawing |

Draw a background image, optionally tiled across the screen

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `background` | Text | — | Background asset name |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `tiled` | Yes/No | No | Tile across the screen; optional |

### Draw Ellipse

| Property | Value |
|----------|-------|
| **Name** | `draw_ellipse` |
| **Icon** | 🥚 |
| **Category** | Drawing |

Draw a filled or outlined ellipse within a bounding box

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Left X |
| `y1` | Number | `0` | Top Y |
| `x2` | Number | `100` | Right X |
| `y2` | Number | `100` | Bottom Y |
| `filled` | Yes/No | Yes | Filled, or outline only; optional |

### Draw Line

| Property | Value |
|----------|-------|
| **Name** | `draw_line` |
| **Icon** | 📏 |
| **Category** | Drawing |

Draw a line between two points

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Start X |
| `y1` | Number | `0` | Start Y |
| `x2` | Number | `100` | End X |
| `y2` | Number | `100` | End Y |

### Draw Scaled Text

| Property | Value |
|----------|-------|
| **Name** | `draw_scaled_text` |
| **Icon** | 🖍️ |
| **Category** | Drawing |

Draw text at an arbitrary scale

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Text to draw |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `xscale` | Number | `1.0` | Horizontal scale factor |
| `yscale` | Number | `1.0` | Vertical scale factor |

### Draw Sprite

| Property | Value |
|----------|-------|
| **Name** | `draw_sprite` |
| **Icon** | 🖼️ |
| **Category** | Drawing |

Draw a sprite frame at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `subimage` | Number | `0` | Frame index to draw |

### Draw Variable

| Property | Value |
|----------|-------|
| **Name** | `draw_variable` |
| **Icon** | 🔢 |
| **Category** | Drawing |

Draw the value of a variable on screen

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `variable` | Text | — | Variable name (self.var, global.var, or bare name) |

### Fill Screen Color

| Property | Value |
|----------|-------|
| **Name** | `fill_color` |
| **Icon** | 🪣 |
| **Category** | Drawing |

Fill the entire viewport with a solid colour

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | RGB hex colour |

### Set Color

| Property | Value |
|----------|-------|
| **Name** | `set_color` |
| **Icon** | 🎨 |
| **Category** | Drawing |

Set the draw colour and alpha for subsequent draws

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#FFFFFF` | RGB hex colour |
| `alpha` | Number | `1.0` | Opacity 0.0–1.0; optional |

### Set Draw Color

| Property | Value |
|----------|-------|
| **Name** | `set_draw_color` |
| **Icon** | 🎨 |
| **Category** | Drawing |

Set the colour used by subsequent draw_* actions

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | RGB hex colour |

### Set Draw Font

| Property | Value |
|----------|-------|
| **Name** | `set_draw_font` |
| **Icon** | 🔤 |
| **Category** | Drawing |

Set the font and alignment for subsequent text drawing

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `font` | Text | — | Font asset name (blank = default font); optional |
| `halign` | Choice | `left` | Horizontal text alignment; Choices: `left`, `center`, `right` |
| `valign` | Choice | `top` | Vertical text alignment; Choices: `top`, `middle`, `bottom` |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (21)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (6)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (14)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (3)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (18)
- [Network](Full-Action-Reference-Network-Actions) (22)
- [Particles](Full-Action-Reference-Particles) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions) (16)

[← Back to Full Action Reference](Full-Action-Reference)

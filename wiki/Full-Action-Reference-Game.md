# Game

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Draw Arrow

| Property | Value |
|----------|-------|
| **Name** | `draw_arrow` |
| **Icon** | ➡️ |
| **Category** | Game |

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
| **Category** | Game |

Draw a background image, optionally tiled across the screen

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `background` | Text | — | Background asset name |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `tiled` | Yes/No | No | Tile across the screen; optional |

### Draw Circle

| Property | Value |
|----------|-------|
| **Name** | `draw_circle` |
| **Icon** | ⭕ |
| **Category** | Game |

Draw a filled or outlined circle

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Centre X |
| `y` | Number | `0` | Centre Y |
| `radius` | Number | `50` | Circle radius |
| `filled` | Yes/No | Yes | Filled, or outline only; optional |

### Draw Ellipse

| Property | Value |
|----------|-------|
| **Name** | `draw_ellipse` |
| **Icon** | 🥚 |
| **Category** | Game |

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
| **Category** | Game |

Draw a line between two points

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Start X |
| `y1` | Number | `0` | Start Y |
| `x2` | Number | `100` | End X |
| `y2` | Number | `100` | End Y |

### Draw Rectangle

| Property | Value |
|----------|-------|
| **Name** | `draw_rectangle` |
| **Icon** | 🟥 |
| **Category** | Game |

Draw a filled or outlined rectangle

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x1` | Number | `0` | Left X |
| `y1` | Number | `0` | Top Y |
| `x2` | Number | `100` | Right X |
| `y2` | Number | `100` | Bottom Y |
| `filled` | Yes/No | Yes | Filled, or outline only; optional |

### Draw Scaled Text

| Property | Value |
|----------|-------|
| **Name** | `draw_scaled_text` |
| **Icon** | 🖍️ |
| **Category** | Game |

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
| **Category** | Game |

Draw a sprite frame at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `subimage` | Number | `0` | Frame index to draw |

### Draw Text

| Property | Value |
|----------|-------|
| **Name** | `draw_text` |
| **Icon** | 🖍️ |
| **Category** | Game |

Draw a text string at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Text to draw (supports expressions) |
| `x` | Number | `0` | X position |
| `y` | Number | `0` | Y position |
| `relative` | Yes/No | No | Draw relative to this instance's position instead of absolute screen coordinates; optional |

### Draw Variable

| Property | Value |
|----------|-------|
| **Name** | `draw_variable` |
| **Icon** | 🔢 |
| **Category** | Game |

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
| **Category** | Game |

Fill the entire viewport with a solid colour

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | RGB hex colour |

### Open Webpage

| Property | Value |
|----------|-------|
| **Name** | `open_webpage` |
| **Icon** | 🌐 |
| **Category** | Game |

Open a URL in the default browser

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `url` | Text | — | Web address to open |

### Restart Game

| Property | Value |
|----------|-------|
| **Name** | `restart_game` |
| **Icon** | 🔁🎮 |
| **Category** | Game |

Restart the game from the start room

*Parameters:* none

### Set Alpha

| Property | Value |
|----------|-------|
| **Name** | `set_alpha` |
| **Icon** | 🌫️ |
| **Category** | Game |

Set the drawing transparency for subsequent draws

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `alpha` | Number | `1.0` | Opacity 0.0 (clear) to 1.0 (opaque) |

### Set Color

| Property | Value |
|----------|-------|
| **Name** | `set_color` |
| **Icon** | 🎨 |
| **Category** | Game |

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
| **Category** | Game |

Set the colour used by subsequent draw_* actions

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `color` | Color | `#000000` | RGB hex colour |

### Set Draw Font

| Property | Value |
|----------|-------|
| **Name** | `set_draw_font` |
| **Icon** | 🔤 |
| **Category** | Game |

Set the font and alignment for subsequent text drawing

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `font` | Text | — | Font asset name (blank = default font); optional |
| `halign` | Choice | `left` | Horizontal text alignment; Choices: `left`, `center`, `right` |
| `valign` | Choice | `top` | Vertical text alignment; Choices: `top`, `middle`, `bottom` |

### Set Window Caption

| Property | Value |
|----------|-------|
| **Name** | `set_window_caption` |
| **Icon** | 🪟 |
| **Category** | Game |

Configure score/lives/health display in window title

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `show_score` | Yes/No | Yes | Append the current score to the window caption |
| `show_lives` | Yes/No | Yes | Append the current lives count to the window caption |
| `show_health` | Yes/No | No | Append the current health value to the window caption |
| `caption` | Text | — | Optional caption prefix shown before the counters; optional |

### Show Game Info

| Property | Value |
|----------|-------|
| **Name** | `show_info` |
| **Icon** | ℹ️ |
| **Category** | Game |

Display the game information screen

*Parameters:* none

### Show Message

| Property | Value |
|----------|-------|
| **Name** | `show_message` |
| **Icon** | 💬 |
| **Category** | Game |

Display a message

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `message` | Text | `Hello!` | Message text |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (2)
- [Audio](Full-Action-Reference-Audio) (6)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (4)

[← Back to Full Action Reference](Full-Action-Reference)

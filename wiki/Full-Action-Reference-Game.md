# Game

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

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
| `color` | Color | — | Text colour (e.g. #ffffff). Blank = the active Set Drawing Color, or black.; optional |

### Load Game

| Property | Value |
|----------|-------|
| **Name** | `load_game` |
| **Icon** | 📂 |
| **Category** | Game |

Restore room, score/lives/health, global variables, and instance states from a save file

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `filename` | Text | `savegame.sav` | Save file name to load (from the project's saves/ folder) |

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

### Save Game

| Property | Value |
|----------|-------|
| **Name** | `save_game` |
| **Icon** | 💾 |
| **Category** | Game |

Save the current room, score/lives/health, global variables, and instance states to a file

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `filename` | Text | `savegame.sav` | Save file name (written to the project's saves/ folder) |

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

### Show Video

| Property | Value |
|----------|-------|
| **Name** | `show_video` |
| **Icon** | 🎬 |
| **Category** | Game |

Play a video file in your system's default video player -- opens as a separate window, not rendered inside the game itself

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `filename` | Text | — | Path to the video file |
| `fullscreen` | Yes/No | No | Request fullscreen playback (support depends on your system's player); optional |

### Splash: Show Image

| Property | Value |
|----------|-------|
| **Name** | `splash_show_image` |
| **Icon** | 🖼️ |
| **Category** | Game |

Show a sprite full-screen and pause the game until the player dismisses it

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite to display full-screen |

### Splash: Show Text

| Property | Value |
|----------|-------|
| **Name** | `splash_show_text` |
| **Icon** | 💬 |
| **Category** | Game |

Show a message and pause the game until the player dismisses it

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Message to display |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (21)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (6)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (3)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (18)
- [Drawing](Full-Action-Reference-Drawing) (11)
- [Network](Full-Action-Reference-Network-Actions) (22)
- [Particles](Full-Action-Reference-Particles) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions) (16)

[← Back to Full Action Reference](Full-Action-Reference)

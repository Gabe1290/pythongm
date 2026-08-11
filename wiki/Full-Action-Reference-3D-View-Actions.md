# 3D View

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Draw DOOM HUD

| Property | Value |
|----------|-------|
| **Name** | `draw_doom_hud` |
| **Icon** | 🎯 |
| **Category** | 3D View |

Draw a DOOM-style bottom status bar (health bar + number, score, lives, an objective counter, and a health-reactive face icon) over the raycast view

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Bar's left edge, in screen pixels |
| `y` | Number | `-1` | Bar's top edge; negative auto-aligns to the bottom of the window, under the shrunk viewport; optional |
| `width` | Number | `0` | Bar width (0 = full window width); optional |
| `height` | Number | `42` | Bar height; keep it matched to the viewport_height band you reserved on enable_raycast_view; optional |
| `back_color` | Color | `#101010` | Bar background panel; optional |
| `divider_color` | Color | `#505050` | Top border and the health-bar backing; optional |
| `text_color` | Color | `#ffffff` | Colour of all bar text; optional |
| `health_label` | Text | `Health` | optional |
| `health_bar_width` | Number | `90` | optional |
| `health_bar_height` | Number | `14` | optional |
| `bar_color` | Color | `#20c020` | Fill colour of the health bar; optional |
| `face_sprite` | Sprite | — | Horizontal strip of face frames, healthiest first (blank = no face icon); optional |
| `face_frames` | Number | `4` | How many frames the face strip has; health is bucketed evenly across them; optional |
| `score_label` | Text | `Score: ` | optional |
| `lives_sprite` | Sprite | — | Sprite drawn once per remaining life; optional |
| `lives_scale` | Number | `1.0` | optional |
| `objective_value` | Text | `0` | Expression shown after the objective label (bind your own key/quest variable); optional |
| `objective_label` | Text | `Keys: ` | optional |

### Draw Minimap

| Property | Value |
|----------|-------|
| **Name** | `draw_minimap` |
| **Icon** | 🗺️ |
| **Category** | 3D View |

Draw a north-up minimap of the raycast room's walls, with a marker showing where the camera is and which way it faces

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Left edge of the minimap, in screen pixels |
| `y` | Number | `0` | Top edge of the minimap, in screen pixels |
| `size` | Number | `120` | Width and height of the minimap square, in pixels; optional |
| `back_color` | Color | `#101018` | Panel colour behind the map; optional |
| `wall_color` | Color | `#8080a0` | Colour of the wall lines; optional |
| `player_color` | Color | `#ffd040` | Colour of the camera marker and its heading line; optional |

### Enable Raycast View

| Property | Value |
|----------|-------|
| **Name** | `enable_raycast_view` |
| **Icon** | 🕹️ |
| **Category** | 3D View |

Render the room as a Doom/Wolfenstein-style first-person 3D view (walls, sky, floor) instead of the top-down view

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `enable` | Yes/No | Yes | On = first-person raycast view; off = normal top-down |
| `camera_object` | Object | — | Object whose position + facing angle is the camera (blank = the object running this action); optional |
| `fov` | Number | `66` | Horizontal FOV in degrees; optional |
| `render_distance` | Number | `20` | Max ray length in grid cells; optional |
| `cell_size` | Number | `32` | Grid cell size in pixels (match the wall placement grid); optional |
| `columns` | Number | `320` | Screen columns to raycast (lower = faster/chunkier); optional |
| `wall_color` | Color | `#993333` | Flat wall colour when no wall texture is set; optional |
| `floor_color` | Color | `#464632` | Flat floor colour when no floor texture is set; optional |
| `ceiling_color` | Color | `#87CEEB` | Flat ceiling colour when no sky/ceiling texture is set; optional |
| `wall_texture` | Sprite | — | Sprite to texture every wall (blank = flat colour); optional |
| `sky_texture` | Sprite | — | Sprite for a panning sky over the ceiling (blank = flat); optional |
| `floor_texture` | Sprite | — | Sprite cast onto the floor (blank = flat colour); optional |
| `ceiling_texture` | Sprite | — | Sprite cast onto the ceiling when no sky is set; optional |
| `wall_textured` | Yes/No | Yes | Off forces flat wall colours even when a texture is set; optional |
| `floor_cast_res` | Number | `4` | Floor-cast downsample (higher = faster + chunkier); optional |
| `viewport_height` | Number | `0` | Letterbox the 3D view into this many pixels tall, reserving the band below for a DOOM-style status bar (0 = full window height, unchanged); optional |

### Set Facing Angle

| Property | Value |
|----------|-------|
| **Name** | `set_facing_angle` |
| **Icon** | 🧭 |
| **Category** | 3D View |

Set the instance's look direction for a raycast (first-person) camera — independent of movement speed

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `angle` | Number | `0` | Degrees (0=right, 90=up, 180=left, 270=down) |
| `relative` | Yes/No | No | Add to the current facing angle instead of replacing it; optional |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (2)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (20)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)

[← Back to Full Action Reference](Full-Action-Reference)

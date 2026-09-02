# 3D View

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Apply Gravity

| Property | Value |
|----------|-------|
| **Name** | `apply_gravity` |
| **Icon** | ⬇️ |
| **Category** | 3D View |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Parameters:* none

### Break Block

| Property | Value |
|----------|-------|
| **Name** | `break_block` |
| **Icon** | ⛏️ |
| **Category** | 3D View |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `reach` | Number | `5` | How many cells ahead you can reach, in grid cells; optional |

### Draw Block World HUD

| Property | Value |
|----------|-------|
| **Name** | `draw_block_world_hud` |
| **Icon** | 🧰 |
| **Category** | 3D View |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `slot_size` | Number | `40` | Width and height of each hotbar slot, in pixels; optional |
| `gap` | Number | `6` | Space between hotbar slots, in pixels; optional |
| `margin_bottom` | Number | `16` | Space between the hotbar and the bottom of the screen; optional |
| `back_color` | Color | `#202020` | Fill colour of an unselected slot; optional |
| `selected_color` | Color | `#ffd040` | Fill colour of the currently selected slot; optional |
| `border_color` | Color | `#ffffff` | Outline colour of every slot; optional |
| `text_color` | Color | `#ffffff` | Colour of each slot's block-type label; optional |
| `crosshair_size` | Number | `12` | Width and height of the centre crosshair, in pixels; optional |
| `crosshair_color` | Color | `#ffffff` | Colour of the centre crosshair; optional |

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
| `mark_object` | Object | — | Also dot every instance of this object onto the map (blank = show walls and player only); optional |
| `mark_color` | Color | `#40e0ff` | Colour of the Mark Object dots; optional |
| `mark_object_2` | Object | — | A second object to dot on, in its own colour; optional |
| `mark_color_2` | Color | `#ff5050` | Colour of the Mark Object 2 dots; optional |

### Enable Block World View

| Property | Value |
|----------|-------|
| **Name** | `enable_block_world_view` |
| **Icon** | 🧱 |
| **Category** | 3D View |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `enable` | Yes/No | Yes | On = first-person block view; off = normal top-down |
| `camera_object` | Object | — | Object whose position + facing angle is the camera (blank = the object running this action); optional |
| `z_layer` | Number | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); optional |
| `fov` | Number | `66` | Horizontal FOV in degrees; optional |
| `render_distance` | Number | `20` | Max ray length in grid cells; optional |
| `cell_size` | Number | `32` | Grid cell size in pixels (match the block-placement grid); optional |
| `columns` | Number | `320` | Screen columns to raycast (lower = faster/chunkier); optional |
| `wall_color` | Color | `#8a8a8a` | Flat colour used only if Textured Blocks is off; optional |
| `floor_color` | Color | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); optional |
| `ceiling_color` | Color | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); optional |
| `pitch` | Number | `0` | Degrees to look up (+) or down (-); 0 is level; optional |
| `wall_textured` | Yes/No | Yes | Off forces flat block colours even though real textures are available; optional |
| `top_cast_res` | Number | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); optional |
| `eye_height` | Number | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); optional |
| `gravity` | Number | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; optional |
| `inventory` | Yes/No | No | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; optional |
| `generate` | Yes/No | No | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; optional |
| `seed` | Number | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; optional |

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

### Jump

| Property | Value |
|----------|-------|
| **Name** | `jump` |
| **Icon** | ⬆️ |
| **Category** | 3D View |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `speed` | Number | `0.35` | Initial upward velocity, in cells/step; optional |

### Load Block World

| Property | Value |
|----------|-------|
| **Name** | `load_block_world` |
| **Icon** | 📂 |
| **Category** | 3D View |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `data_file` | Text | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Property | Value |
|----------|-------|
| **Name** | `set_look_pitch` |
| **Icon** | 🔭 |
| **Category** | 3D View |

Tilt the block-world view up or down

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `pitch` | Number | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Yes/No | No | On = add to the current angle, for a look control you can hold down; off = set it outright; optional |

### Move And Collide

| Property | Value |
|----------|-------|
| **Name** | `move_and_collide` |
| **Icon** | 🚶 |
| **Category** | 3D View |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `dx` | Number | `0` | How far to move on x this step, in pixels |
| `dy` | Number | `0` | How far to move on y this step, in pixels |
| `collide` | Yes/No | Yes | Off ignores the block grid entirely (flying/debug); optional |

### Place Block

| Property | Value |
|----------|-------|
| **Name** | `place_block` |
| **Icon** | 🧱 |
| **Category** | 3D View |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `block` | Choice | `stone` | Which kind of block to place; Choices: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Number | `5` | How many cells ahead you can build, in grid cells; optional |

### Select Hotbar Slot

| Property | Value |
|----------|-------|
| **Name** | `select_hotbar_slot` |
| **Icon** | 🔢 |
| **Category** | 3D View |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `index` | Number | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Yes/No | No | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; optional |

### Set Block Protection

| Property | Value |
|----------|-------|
| **Name** | `set_block_protection` |
| **Icon** | 🔒 |
| **Category** | 3D View |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `block_type` | Choice | `diamond_block` | Which block type becomes protected; Choices: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Choice | `gold_block` | Which block type must be in inventory to break it; Choices: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Property | Value |
|----------|-------|
| **Name** | `set_block_reward` |
| **Icon** | 💎 |
| **Category** | 3D View |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `block_type` | Choice | `diamond_block` | Which block type awards score when broken; Choices: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Number | `10` | Score awarded per block of this type broken |

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
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Control](Full-Action-Reference-Control) (19)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [Particles](Full-Action-Reference-Particles) (8)
- [Network](Full-Action-Reference-Network-Actions) (15)

[← Back to Full Action Reference](Full-Action-Reference)

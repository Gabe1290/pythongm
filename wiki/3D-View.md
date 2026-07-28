# 3D View (First-Person Raycast Rendering)

*[Home](Home) | [Full Action Reference](Full-Action-Reference) | [Extensions](Extensions)*

---

PyGameMaker can render a room as a **Doom/Wolfenstein-style first-person 3D
view** instead of the usual top-down picture — walls as vertical strips, a
textured or coloured floor and ceiling, an optional panning sky, and billboard
sprites for pickups and monsters. The game *logic* (movement, collisions,
events) is unchanged; only how the room is **drawn** changes.

This is provided by the built-in **2.5D Raycast** [extension](Extensions), which
ships enabled. It exports to all three targets — desktop, HTML5, and
Kivy/Android — so a first-person game runs the same everywhere.

The bundled samples **`raycast_1`–`raycast_4`** are complete, playable examples
(a plain maze, a two-level game with pickups and a monster, a health/medkit
variant, and a DOOM-style status-bar showcase).

---

## How it works

- A room becomes first-person when an object runs the **Enable Raycast View**
  action (usually in its Create event). That object is the **camera** by
  default — its position is the viewpoint and its `facing_angle` is the look
  direction.
- **Walls are your solid instances.** The renderer derives thin wall *edges*
  from every solid object in the room, on a grid whose size is the action's
  `cell_size` (32 by default — the size every `maze_*`/`raycast_*` sample uses).
  A wall-sprited solid textures the wall; otherwise a flat `wall_color` is used.
- **The camera turns** by changing `facing_angle` (see **Set Facing Angle**),
  and moves with the ordinary movement actions (e.g. `set_direction_speed`
  with `direction = "facing_angle"` to walk forward).
- **Non-solid sprited instances** (goals, pickups, monsters) draw as
  camera-facing **billboards**, correctly occluded by walls.

---

## The actions (category **3D View**)

| Action | What it does |
|--------|--------------|
| **Enable Raycast View** (`enable_raycast_view`) | Switch the current room to (or from) the first-person view, and configure the camera: `camera_object`, `fov`, `render_distance`, `cell_size`, wall/floor/ceiling colours and textures, an optional `sky_texture`, and `viewport_height` (a DOOM-bar letterbox). |
| **Set Facing Angle** (`set_facing_angle`) | Turn the camera. Angle in GameMaker degrees (0 = right, 90 = up); `relative` adds to the current facing. |
| **Draw Minimap** (`draw_minimap`) | Draw a north-up minimap of the room's walls with a "you are here" marker. A HUD action — put it in a Draw event. |
| **Draw DOOM HUD** (`draw_doom_hud`) | Draw a DOOM-style bottom status bar: health bar + number, a health-reactive face, score, lives, and an objective counter. Pairs with `enable_raycast_view`'s `viewport_height`. |

See the [Full Action Reference](Full-Action-Reference#3d-view) for every
parameter.

---

## A minimal first-person controller

In the player object:

- **Create:** `Enable Raycast View` (leave `camera_object` empty so the player
  *is* the camera).
- **Keyboard Left / Right:** `Set Facing Angle` with `relative` on (e.g. ±3°).
- **Keyboard Up:** `Set Direction Speed` with `direction = facing_angle` and a
  small speed to walk forward.

Build the room out of solid wall objects on a 32-pixel grid, exactly like the
`maze_*` samples — the raycaster turns those walls into the 3D corridors.

---

## Notes and limits

- The HUD actions (`draw_minimap`, `draw_doom_hud`, and the ordinary
  `draw_score` / `draw_lives` / `draw_text`) composite **on top** of the
  first-person frame, in screen space.
- Walls are static for the first-person pass — walls created/destroyed after the
  room loads don't reshape the 3D geometry.
- If the 2.5D Raycast extension is **disabled**, a room that enables the view
  simply renders top-down and the IDE warns you on load — see
  [Extensions](Extensions).

---

## See Also

- [Extensions](Extensions) — how the 3D View ships and how to turn it off
- [Full Action Reference](Full-Action-Reference#3d-view) — the four actions in full
- [Room Editor](Room-Editor) — placing the wall objects the view is built from

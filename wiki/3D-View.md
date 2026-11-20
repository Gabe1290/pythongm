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
| **Enable Raycast View** (`enable_raycast_view`) | Switch the current room to (or from) the first-person view, and configure the camera: `camera_object`, `fov`, `render_distance`, `cell_size`, wall/floor/ceiling colours and textures, an optional `sky_texture`, `viewport_height` (a DOOM-bar letterbox), `wall_height` (walls and ceiling height in cells, default 1.5) and `max_step` (the highest climbable step in pixels, default 12). |
| **Set Facing Angle** (`set_facing_angle`) | Turn the camera. Angle in GameMaker degrees (0 = right, 90 = up); `relative` adds to the current facing. |
| **Draw Minimap** (`draw_minimap`) | Draw a north-up minimap of the room's walls with a "you are here" marker. A HUD action — put it in a Draw event. |
| **Set Floor Height** (`set_floor_height`) | Make this instance a **step**: the grid cells its sprite covers become raised floor of that height (pixels). Put it in the Create event of a non-solid object. Optional top and side textures. See *Stairs and platforms* below. |
| **Set Billboard Rotation** (`set_billboard_rotation`) | Give a billboard several view-angle frames, so it shows its sides as you walk around it. |
| **Draw DOOM HUD** (`draw_doom_hud`) | Draw a DOOM-style bottom status bar: health bar + number, a health-reactive face, score, lives, and an objective counter. Pairs with `enable_raycast_view`'s `viewport_height`. |

See the [Full Action Reference](Full-Action-Reference-3D-View-Actions) for every
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

## Stairs and platforms

A **step** is an ordinary object that is *not solid*, with **Set Floor Height**
in its Create event (`height` in pixels). Every grid cell its sprite covers
becomes raised floor; place steps on the grid like walls — one object per
height is the easy way (`obj_step_8`, `obj_step_16`, …).

- **Climbing:** anything that moves (the player, monsters) can walk up a step
  of at most **Max Step** pixels (on Enable Raycast View, default 12); a higher
  step blocks it like a wall, and it slides along. Walking **down** is always
  allowed. The view rises and falls smoothly.
- **Headroom:** raise **Wall Height** (e.g. `3`) — at the default 1.5 there is
  room for only 20 px of floor under the ceiling (higher floors are clamped).
- **Two variables on every moving instance:** `raycast_step_blocked` (1 on a
  frame when a step was too high — a refused step fires no event, so a monster
  can *Test Variable* it in End Step to turn back) and `raycast_floor_z` (the
  floor height under it).
- Pickups and monsters stand on the floor of their cell, and steps hide what
  is behind them. The minimap shades raised cells by height.

The **raycast_5** sample (*2.5 D — Level 5*) is a small level built around
stairs. Stairs work on desktop, HTML5 and Kivy (Android/iOS) exports.

---

## Notes and limits

- The HUD actions (`draw_minimap`, `draw_doom_hud`, and the ordinary
  `draw_score` / `draw_lives` / `draw_text`) composite **on top** of the
  first-person frame, in screen space.
- Walls and steps are rebuilt every frame, so a wall or step created or
  destroyed while the game runs (a door, a bridge) shows up immediately.
- There is one ceiling height per room (Wall Height), no looking up or down,
  no jumping, and no slopes — build ramps from small steps.
- If the 2.5D Raycast extension is **disabled**, a room that enables the view
  simply renders top-down and the IDE warns you on load — see
  [Extensions](Extensions).

---

## See Also

- [Extensions](Extensions) — how the 3D View ships and how to turn it off
- [Full Action Reference](Full-Action-Reference-3D-View-Actions) — every 3D View action in full
- [Room Editor](Room-Editor) — placing the wall objects the view is built from

## Tutorials

The in-app Tutorials panel has a four-lesson 2.5D series: First Steps, Textures/Sky/Floor, Goals/Gems/Monsters, and HUD/Minimap (Lessons 11-14). They are hidden in the beginner edition.

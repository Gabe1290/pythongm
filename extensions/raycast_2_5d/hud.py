#!/usr/bin/env python3
"""HUD command builders for the raycast extension's macro actions.

Moved out of ``runtime/action_executor.py`` (Stage B3, docs/RAYCAST_EXTENSION_
PLAN.md). These are pure functions that turn game state into ordinary
draw-queue commands ('rectangle' / 'line' / 'text' / 'sprite' / 'lives') — the
reason ``draw_minimap`` / ``draw_doom_hud`` can be MACRO actions that need no
new renderer on any target.

Each function here is THE single source for its geometry; the HTML5
(engine.js) and Kivy (kivy_exporter.py / code_generator.py) ports mirror the
arithmetic, and ``tests/test_raycast_export_parity.py`` compares them against
these — the same discipline that keeps the three ``cast_ray`` copies honest.

Coordinates are SCREEN space with y DOWN, matching every other HUD draw
command; Kivy's y-flip happens once, later, in its shared draw-queue path.
"""
import math


# Length of the camera's heading line on the minimap, in minimap pixels, and
# the half-length of the position cross. Kept together with the builder so the
# HTML5 / Kivy ports and tests/test_raycast_export_parity.py can pin the same
# numbers.
MINIMAP_HEADING_LEN = 7.0
MINIMAP_MARKER_HALF = 2.0


def build_minimap_commands(v_walls, h_walls, cell_size, room_width, room_height,
                           cam_x, cam_y, facing_angle, x, y, size,
                           back_color, wall_color, player_color):
    """Project raycast wall edges to a north-up minimap; return draw commands.

    THE single source for the minimap's geometry. The HTML5 (engine.js) and
    Kivy (kivy_exporter.py) ports mirror this arithmetic, and
    tests/test_raycast_export_parity.py compares them against it — the same
    approach that keeps the three cast_ray copies honest.

    Returns a list of ordinary draw-queue commands ('rectangle' / 'line'), so
    no target needs a bespoke minimap renderer.

    Coordinates are SCREEN space with y DOWN, matching every other HUD draw
    command; Kivy's y-flip happens once, later, in its shared draw-queue path.

    v_walls: {(line_x, row)} vertical edges; h_walls: {(col, line_y)}.
    """
    cmds = [{
        'type': 'rectangle',
        'x1': x, 'y1': y, 'x2': x + size, 'y2': y + size,
        'color': back_color, 'filled': True,
    }]

    span = max(float(room_width or 0), float(room_height or 0))
    if span <= 0 or not cell_size:
        return cmds                      # nothing sensible to project onto
    scale = float(size) / span

    def px(wx, wy):
        return x + wx * scale, y + wy * scale

    cs = float(cell_size)
    for (line_x, row) in sorted(v_walls or ()):
        x1, y1 = px(line_x * cs, row * cs)
        x2, y2 = px(line_x * cs, (row + 1) * cs)
        cmds.append({'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                     'color': wall_color})
    for (col, line_y) in sorted(h_walls or ()):
        x1, y1 = px(col * cs, line_y * cs)
        x2, y2 = px((col + 1) * cs, line_y * cs)
        cmds.append({'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                     'color': wall_color})

    if cam_x is None or cam_y is None:
        return cmds                      # no camera in this room yet

    cx, cy = px(float(cam_x), float(cam_y))
    m = MINIMAP_MARKER_HALF
    cmds.append({'type': 'line', 'x1': cx - m, 'y1': cy, 'x2': cx + m, 'y2': cy,
                 'color': player_color})
    # Heading: GM angles are 0=right / 90=up, screen y is DOWN — hence the
    # negation, the same convention the three raycast renderers use.
    rad = math.radians(-float(facing_angle or 0.0))
    cmds.append({
        'type': 'line', 'x1': cx, 'y1': cy,
        'x2': cx + math.cos(rad) * MINIMAP_HEADING_LEN,
        'y2': cy + math.sin(rad) * MINIMAP_HEADING_LEN,
        'color': player_color,
    })
    return cmds

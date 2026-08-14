#!/usr/bin/env python3
"""HUD command builder for the Block World extension's macro action
(Phase 4 Unit 6).

Mirrors extensions/raycast_2_5d/hud.py: a pure function that turns game
state into ordinary draw-queue commands ('rectangle' / 'line' / 'text') --
the reason draw_block_world_hud can be a MACRO action that needs no new
renderer on any target. No pygame import, same reason raycast's hud.py has
none: the IDE loads extensions for their schemas only, and a HUD builder is
plain arithmetic over already-resolved values, never image data.

Coordinates are SCREEN space with y DOWN, matching every other HUD draw
command in this codebase.
"""


def build_block_world_hud_commands(screen_width, screen_height, hotbar,
                                   selected_index, slot_size, gap,
                                   margin_bottom, back_color, border_color,
                                   selected_color, text_color,
                                   crosshair_size, crosshair_color):
    """Compose the Block World HUD -- a centre crosshair plus a hotbar strip
    centred along the bottom, the selected slot highlighted -- as ordinary
    draw-queue commands.

    Blocks have no project sprite asset to reference by name (their
    textures are extension-bundled files, not room._all_sprites entries --
    see state.py's own docstring on why), so a slot is a coloured rectangle
    plus a short text label rather than an icon; nothing here needs pygame
    to compute.

    hotbar: the list of block type ids to draw (state.DEFAULT_HOTBAR).
    selected_index: which slot to highlight (instance.hotbar_index).
    """
    cmds = []

    ccx, ccy = screen_width / 2.0, screen_height / 2.0
    half = crosshair_size / 2.0
    cmds.append({'type': 'line', 'x1': ccx - half, 'y1': ccy,
                 'x2': ccx + half, 'y2': ccy, 'color': crosshair_color})
    cmds.append({'type': 'line', 'x1': ccx, 'y1': ccy - half,
                 'x2': ccx, 'y2': ccy + half, 'color': crosshair_color})

    n = len(hotbar)
    if n == 0:
        return cmds
    total_w = n * slot_size + (n - 1) * gap
    x0 = (screen_width - total_w) / 2.0
    y0 = screen_height - margin_bottom - slot_size
    for i, block_type in enumerate(hotbar):
        sx = x0 + i * (slot_size + gap)
        fill = selected_color if i == selected_index else back_color
        cmds.append({'type': 'rectangle', 'x1': sx, 'y1': y0,
                     'x2': sx + slot_size, 'y2': y0 + slot_size,
                     'color': fill, 'filled': True})
        cmds.append({'type': 'rectangle', 'x1': sx, 'y1': y0,
                     'x2': sx + slot_size, 'y2': y0 + slot_size,
                     'color': border_color, 'filled': False})
        cmds.append({'type': 'text', 'text': block_type[:4],
                     'x': sx + 2, 'y': y0 + slot_size - 14,
                     'color': text_color})
    return cmds

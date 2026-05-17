"""Shared object colour / placeholder rendering for the room editor.

Before this module, `get_object_color` and the "filled rect + border +
abbreviated name" placeholder draw were copy-pasted across
`room_canvas.RoomCanvas` (3 sites), `object_palette` and
`utils/room_preview_generator.RoomPreviewGenerator` — and had drifted
(the preview used a different colour algorithm, so room thumbnails did
not match the editor canvas). Both helpers below are the canvas/palette
behaviour, now used everywhere so the editor and preview render
identically.
"""

from PySide6.QtGui import QColor, QPen, QFont

# Curated colours for well-known object names; everything else falls back
# to one of six pleasant colours chosen by a stable hash of the name.
_NAMED_COLORS = {
    'player': "#00FF00",
    'enemy': "#FF0000",
    'wall': "#808080",
    'coin': "#FFFF00",
    'door': "#8B4513",
    'key': "#FFD700",
}

_FALLBACK_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1",
    "#96CEB4", "#FECA57", "#FF9FF3",
]


def object_color(object_name):
    """Return the QColor used to represent *object_name*.

    Identical to the previous RoomCanvas/object_palette ``get_object_color``
    (curated palette, with a ``hash(name) % 6`` fallback).
    """
    colors = {name: QColor(hex_) for name, hex_ in _NAMED_COLORS.items()}

    if object_name not in colors:
        hash_val = hash(object_name) % 6
        default_colors = [QColor(h) for h in _FALLBACK_COLORS]
        return default_colors[hash_val]

    return colors[object_name]


def draw_object_placeholder(painter, object_name, x, y, width, height):
    """Draw the in-place placeholder for an object without a sprite.

    Exactly the block that was duplicated in RoomCanvas.draw_instance
    (both branches), RoomCanvas.draw_instance_preview and
    RoomPreviewGenerator._draw_placeholder: a colour-filled rectangle, a
    1px black border, and the (abbreviated) object name in white near the
    top-left. Coordinates are passed through unchanged so float positions
    (the canvas's centred/transformed branch) behave exactly as before.
    """
    color = object_color(object_name)
    painter.fillRect(x, y, width, height, color)
    painter.setPen(QPen(QColor("#000000"), 1))
    painter.drawRect(x, y, width, height)

    painter.setPen(QPen(QColor("#FFFFFF"), 1))
    font = QFont()
    font.setPointSize(8)
    painter.setFont(font)

    name = object_name
    if len(name) > 6:
        name = name[:4] + ".."

    painter.drawText(x + 2, y + 12, name)

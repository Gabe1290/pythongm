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

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen, QFont, QPixmap, QPainter

from core.logger import get_logger

logger = get_logger(__name__)

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


def create_default_sprite(object_name, abbrev_over=6, abbrev_keep=4):
    """Create a 32x32 default sprite pixmap for objects without a sprite.

    Verbatim of the former RoomCanvas.create_default_sprite (bold, centred
    abbreviated name) so canvas and preview produce the identical fallback.
    The default abbreviation (name truncated to ``abbrev_keep`` chars when
    longer than ``abbrev_over``) matches the canvas/preview behaviour; the
    object palette delegates with its own shorter rule (4/2) so its 32px
    icons keep their previous appearance.
    """
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    color = object_color(object_name)
    painter.fillRect(0, 0, 32, 32, color)
    painter.setPen(QPen(QColor("#000000"), 1))
    painter.drawRect(0, 0, 31, 31)

    painter.setPen(QPen(QColor("#FFFFFF"), 1))
    font = QFont()
    font.setPointSize(8)
    font.setBold(True)
    painter.setFont(font)

    name = object_name
    if len(name) > abbrev_over:
        name = name[:abbrev_keep] + ".."

    text_rect = painter.fontMetrics().boundingRect(name)
    x = (32 - text_rect.width()) // 2
    y = (32 + text_rect.height()) // 2 - 2
    painter.drawText(x, y, name)

    painter.end()
    return pixmap


def resolve_object_sprite(project_data, project_path, object_name, cache):
    """Resolve an object's display sprite (first frame, ≤64px, default fallback).

    Verbatim of the former RoomCanvas.load_object_sprite. `cache` is the
    caller's dict (kept by reference, so caching semantics are unchanged).
    Returns None only when project info is missing or the object is unknown;
    otherwise always returns a pixmap (a default sprite if needed).
    """
    if not project_data or not project_path:
        return None

    if object_name in cache:
        return cache[object_name]

    try:
        objects = project_data.get('assets', {}).get('objects', {})
        if object_name not in objects:
            return None

        object_data = objects[object_name]
        sprite_name = object_data.get('sprite', '')

        if not sprite_name:
            pixmap = create_default_sprite(object_name)
            cache[object_name] = pixmap
            return pixmap

        sprites = project_data.get('assets', {}).get('sprites', {})
        if sprite_name not in sprites:
            pixmap = create_default_sprite(object_name)
            cache[object_name] = pixmap
            return pixmap

        sprite_data = sprites[sprite_name]
        sprite_file_path = sprite_data.get('file_path', '')

        if not sprite_file_path:
            pixmap = create_default_sprite(object_name)
            cache[object_name] = pixmap
            return pixmap

        full_sprite_path = project_path / sprite_file_path
        if full_sprite_path.exists():
            pixmap = QPixmap(str(full_sprite_path))

            if not pixmap.isNull():
                # Check if this is an animated sprite - extract first frame
                animation_type = sprite_data.get('animation_type', 'single')
                frames = sprite_data.get('frames', 1)

                if frames > 1 and animation_type != 'single':
                    # Extract first frame from sprite sheet
                    frame_width = sprite_data.get('frame_width', pixmap.width())
                    frame_height = sprite_data.get('frame_height', pixmap.height())

                    # Ensure frame dimensions are valid
                    frame_width = min(frame_width, pixmap.width())
                    frame_height = min(frame_height, pixmap.height())

                    # Extract first frame (top-left corner)
                    pixmap = pixmap.copy(0, 0, frame_width, frame_height)

                # Scale if too large for room editor display
                if pixmap.width() > 64 or pixmap.height() > 64:
                    pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                cache[object_name] = pixmap
                return pixmap

        pixmap = create_default_sprite(object_name)
        cache[object_name] = pixmap
        return pixmap

    except Exception as e:
        logger.error(f"Error loading sprite for {object_name}: {e}")
        pixmap = create_default_sprite(object_name)
        cache[object_name] = pixmap
        return pixmap


def load_image_asset(project_data, project_path, image_name, cache, cache_key, on_error):
    """Load a background/sprite image asset by name. Returns QPixmap or None.

    Shared body of the former RoomCanvas.load_background_image and
    RoomPreviewGenerator._load_background_image, which were byte-identical
    except for the cache key and the error logger. Behaviour is preserved
    per caller: each passes its own ``cache_key`` (canvas uses the raw
    image name, the preview uses ``bg_<name>``) and ``on_error`` callback
    (canvas → logger.error, preview → print), so the message text and
    return value (None on miss/error) are unchanged.
    """
    if not project_data or not project_path:
        return None

    if cache_key in cache:
        return cache[cache_key]

    try:
        for asset_type in ['backgrounds', 'sprites']:
            assets = project_data.get('assets', {}).get(asset_type, {})
            if image_name in assets:
                asset_data = assets[image_name]
                file_path = asset_data.get('file_path', '')

                if file_path:
                    full_path = project_path / file_path
                    if full_path.exists():
                        pixmap = QPixmap(str(full_path))
                        if not pixmap.isNull():
                            cache[cache_key] = pixmap
                            return pixmap
        return None
    except Exception as e:
        on_error(f"Error loading background image {image_name}: {e}")
        return None

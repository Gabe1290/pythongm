"""Color-parsing helpers shared by the runtime and the Kivy exporter.

Two flavours coexist because the two consumers want different output types:

- ``to_rgb255`` returns ``(r, g, b)`` integers in 0-255. Used throughout the
  runtime (pygame surface fills, draw-color state, action handlers).
- ``to_kivy_rgba`` returns ``[r, g, b, a]`` floats in 0-1. Used by the Kivy
  exporter, which needs the Kivy ``Color`` instruction format.

Both accept the same input forms (hex strings with optional ``#``, RGB
tuples/lists, GameMaker BGR integers) so callers don't have to second-guess
which parser to reach for. The two flavours are *intentionally separate* —
the unit gap between 0-255 ints and 0-1 floats is exactly where conversion
bugs hide, so each consumer asks for the format it actually wants.
"""

from typing import Any, List, Tuple


def to_rgb255(value: Any, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
    """Parse ``value`` to an ``(r, g, b)`` 0-255 integer tuple.

    Supports:
    - Hex strings: ``"#FF0000"``, ``"FF0000"``, short form ``"#f00"``
    - RGB tuples/lists: ``(255, 0, 0)`` or ``[255, 0, 0]``
    - Integer values (GameMaker BGR-packed format)
    - ``None`` (returns ``default``)
    """
    if value is None:
        return default

    if isinstance(value, (tuple, list)) and len(value) >= 3:
        return (int(value[0]), int(value[1]), int(value[2]))

    if isinstance(value, str):
        s = value.strip().lstrip('#')
        try:
            if len(s) == 3:
                # Short form: "RGB" -> "RRGGBB"
                s = ''.join(c * 2 for c in s)
            if len(s) >= 6:
                return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
        except (ValueError, IndexError):
            return default
        return default

    if isinstance(value, int):
        # GameMaker stores colours BGR-packed: 0xBBGGRR.
        b = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        r = value & 0xFF
        return (r, g, b)

    return default


def to_kivy_rgba(value: Any) -> List[float]:
    """Parse ``value`` to ``[r, g, b, a]`` floats in 0-1.

    Falls back to opaque black on parse failure. Used by the Kivy exporter
    to feed ``kivy.graphics.Color(...)``.
    """
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        result = [float(v) for v in value[:4]]
        # Heuristic: if any channel is >1, treat the whole thing as 0-255 and rescale.
        if any(v > 1.0 for v in result):
            result = [v / 255.0 for v in result]
        if len(result) == 3:
            result.append(1.0)
        return result

    if isinstance(value, str):
        s = value.strip().lstrip('#')
        try:
            if len(s) == 6:
                return [
                    int(s[0:2], 16) / 255.0,
                    int(s[2:4], 16) / 255.0,
                    int(s[4:6], 16) / 255.0,
                    1.0,
                ]
            if len(s) == 8:
                return [
                    int(s[0:2], 16) / 255.0,
                    int(s[2:4], 16) / 255.0,
                    int(s[4:6], 16) / 255.0,
                    int(s[6:8], 16) / 255.0,
                ]
        except (ValueError, IndexError):
            pass

    return [0.0, 0.0, 0.0, 1.0]

#!/usr/bin/env python3
"""Where everything on the drawn micro:bit sits (Stage S5).

Pure geometry -- no pygame -- so the renderer, the mouse hit-testing (S6),
the sensor strip (S7) and the tests all read the same numbers. All
coordinates are screen pixels. ``board_layout(cx, cy, scale)`` places the
board centred on ``(cx, cy)``; at scale 1.0 it is ``BODY_W`` pixels wide.
"""
from dataclasses import dataclass
from typing import Dict, Tuple

from .state import option_of

# Design units (scale 1.0): the real board is 52 x 42 mm, drawn at ~4.2 px/mm.
BODY_W = 220
BODY_H = 178
LED_PITCH = 24
LED_SIZE = 14
LED_CENTER_DY = -8          # the LED grid sits a little above centre
BUTTON_DX = 85
BUTTON_RADIUS = 15
LOGO_DY = -76
LOGO_RX = 14
LOGO_RY = 9
PAD_PITCH = 36
PAD_W = 26
PAD_H = 22
PAD_NAMES = ("0", "1", "2", "3V", "GND")
TOUCH_PINS = (0, 1, 2)

OFF_COLOR = (62, 22, 22)
ON_COLOR = (255, 52, 40)


@dataclass(frozen=True)
class BoardLayout:
    cx: float
    cy: float
    scale: float
    body: Tuple[int, int, int, int]                  # x, y, w, h
    led_size: int
    leds: Tuple[Tuple[Tuple[int, int], ...], ...]    # leds[y][x] = (cx, cy)
    buttons: Dict[str, Tuple[int, int, int]]         # name -> (cx, cy, r)
    logo: Tuple[int, int, int, int]                  # cx, cy, rx, ry
    pads: Dict[str, Tuple[int, int, int, int]]       # name -> x, y, w, h
    speaker: Tuple[int, int, int] = (0, 0, 0)        # cx, cy, r (S8)

    def led_center(self, x, y):
        return self.leds[y][x]


def _r(value):
    return int(round(value))


def board_layout(cx, cy, scale=1.0) -> BoardLayout:
    scale = max(0.1, float(scale))
    s = lambda v: v * scale  # noqa: E731

    body_w, body_h = _r(s(BODY_W)), _r(s(BODY_H))
    body = (_r(cx - body_w / 2), _r(cy - body_h / 2), body_w, body_h)

    grid_cy = cy + s(LED_CENTER_DY)
    leds = tuple(
        tuple((_r(cx + (x - 2) * s(LED_PITCH)), _r(grid_cy + (y - 2) * s(LED_PITCH)))
              for x in range(5))
        for y in range(5))

    buttons = {
        "a": (_r(cx - s(BUTTON_DX)), _r(grid_cy), _r(s(BUTTON_RADIUS))),
        "b": (_r(cx + s(BUTTON_DX)), _r(grid_cy), _r(s(BUTTON_RADIUS))),
    }
    logo = (_r(cx), _r(cy + s(LOGO_DY)), _r(s(LOGO_RX)), _r(s(LOGO_RY)))

    pad_w, pad_h = _r(s(PAD_W)), _r(s(PAD_H))
    pad_y = body[1] + body_h - pad_h
    pads = {
        name: (_r(cx + (i - 2) * s(PAD_PITCH) - pad_w / 2), pad_y, pad_w, pad_h)
        for i, name in enumerate(PAD_NAMES)
    }
    speaker = (_r(cx + s(BUTTON_DX)), _r(cy + s(LOGO_DY)), max(3, _r(s(7))))
    return BoardLayout(cx, cy, scale, body, max(2, _r(s(LED_SIZE))), leds,
                       buttons, logo, pads, speaker)


def led_color(level, brightness=255):
    """The glow of one LED: ``level`` 0-9 scaled by the display brightness
    (0-255), from a dark red (off) to a bright red (on)."""
    amount = max(0, min(9, level)) / 9.0 * max(0, min(255, brightness)) / 255.0
    return tuple(int(round(o + (n - o) * amount)) for o, n in zip(OFF_COLOR, ON_COLOR))


def hit_test(layout, x, y):
    """What a click at screen ``(x, y)`` lands on: ``"a"``, ``"b"``,
    ``"logo"``, ``"pin0"``/``"pin1"``/``"pin2"`` -- or ``None``."""
    for name, (bx, by, r) in layout.buttons.items():
        if (x - bx) ** 2 + (y - by) ** 2 <= r * r:
            return name
    lx, ly, rx, ry = layout.logo
    if rx and ry and ((x - lx) / rx) ** 2 + ((y - ly) / ry) ** 2 <= 1:
        return "logo"
    for pin in TOUCH_PINS:
        px, py, pw, ph = layout.pads[str(pin)]
        if px <= x < px + pw and py <= y < py + ph:
            return f"pin{pin}"
    return None


def scale_of(instance):
    """The board's size multiplier: an instance variable, else the object's
    ``microbit_scale`` property, else 1.0."""
    value = option_of(instance, "microbit_scale", 1.0)
    try:
        return max(0.1, float(value))
    except (TypeError, ValueError):
        return 1.0


def center_of(instance):
    """Screen position the board is centred on: the instance's own point
    when it has no sprite, else the middle of its sprite."""
    sprite = getattr(instance, "sprite", None)
    if sprite is None:
        return instance.x, instance.y
    return (instance.x - sprite.origin_x + sprite.width / 2,
            instance.y - sprite.origin_y + sprite.height / 2)


def layout_for(instance):
    cx, cy = center_of(instance)
    return board_layout(cx, cy, scale_of(instance))


# --- sensor strip (Stage S7) -------------------------------------------------------------
# Two panels flanking the board: the tilt pad on the left, the shake button
# and four sliders stacked on the right.

STRIP_GAP = 20                    # gap between the board and each side panel
STRIP_PAD = 8
TILT_SIZE = 100
SHAKE_H = 22
RIGHT_CONTENT_W = 110              # inner width of the shake/sliders panel
RIGHT_TOP_GAP = 14                 # extra room between the shake button and the first slider
SLIDER_STEP = 22
SLIDER_TRACK_H = 8
TILT_FULL = 1024                  # pad edge = one g, so tilt gestures trigger there

# slider name -> (minimum, maximum), in the order they are stacked
SLIDERS = {
    "light": (0, 255),
    "temperature": (-5, 50),
    "compass": (0, 359),
    "sound": (0, 255),
}


@dataclass(frozen=True)
class StripLayout:
    panel_left: Tuple[int, int, int, int]     # tilt pad's panel
    panel_right: Tuple[int, int, int, int]    # shake + sliders' panel
    tilt: Tuple[int, int, int, int]
    shake: Tuple[int, int, int, int]
    sliders: Dict[str, Tuple[int, int, int, int]]    # name -> track x, y, w, h


def strip_layout(layout: BoardLayout) -> StripLayout:
    s = layout.scale
    bx, by, bw, bh = layout.body
    cy = by + bh / 2
    pad = _r(STRIP_PAD * s)
    gap = _r(STRIP_GAP * s)

    # Left panel: the tilt pad, flanking the board on the left.
    tilt_size = _r(TILT_SIZE * s)
    left_w = tilt_size + 2 * pad
    left_h = tilt_size + 2 * pad
    left_x = bx - gap - left_w
    left_y = _r(cy - left_h / 2)
    panel_left = (left_x, left_y, left_w, left_h)
    tilt = (left_x + pad, left_y + pad, tilt_size, tilt_size)

    # Right panel: the shake button above four sliders, flanking the board
    # on the right.
    col_w = _r(RIGHT_CONTENT_W * s)
    shake_h = _r(SHAKE_H * s)
    step = _r(SLIDER_STEP * s)
    track_h = max(3, _r(SLIDER_TRACK_H * s))
    first_dy = pad + shake_h + _r(RIGHT_TOP_GAP * s)
    right_h = first_dy + 3 * step + track_h + pad
    right_w = col_w + 2 * pad
    right_x = bx + bw + gap
    right_y = _r(cy - right_h / 2)
    panel_right = (right_x, right_y, right_w, right_h)
    shake = (right_x + pad, right_y + pad, col_w, shake_h)
    sliders = {}
    for i, name in enumerate(SLIDERS):
        sliders[name] = (right_x + pad, right_y + first_dy + i * step, col_w, track_h)
    return StripLayout(panel_left, panel_right, tilt, shake, sliders)


def tilt_from_pos(rect, x, y):
    """Accelerometer ``(x, y, z)`` for a point on the tilt pad: the pad edge is
    one g of tilt, up on the pad is "logo up" (+y) and right is +x. z fills
    the rest of one g, so the middle of the pad is the resting face-up board."""
    px, py, pw, ph = rect
    u = max(-1.0, min(1.0, (x - (px + pw / 2)) / (pw / 2)))
    v = max(-1.0, min(1.0, ((py + ph / 2) - y) / (ph / 2)))
    ax, ay = u * TILT_FULL, v * TILT_FULL
    radius = (ax * ax + ay * ay) ** 0.5
    if radius > TILT_FULL:
        ax, ay = ax * TILT_FULL / radius, ay * TILT_FULL / radius
    az = -((max(0.0, TILT_FULL ** 2 - ax * ax - ay * ay)) ** 0.5)
    return int(round(ax)), int(round(ay)), int(round(az))


def tilt_to_pos(rect, ax, ay):
    """Where the tilt pad's dot sits for an acceleration (inverse of the above)."""
    px, py, pw, ph = rect
    u = max(-1.0, min(1.0, ax / TILT_FULL))
    v = max(-1.0, min(1.0, ay / TILT_FULL))
    return int(round(px + pw / 2 + u * pw / 2)), int(round(py + ph / 2 - v * ph / 2))


def slider_value(name, track, x):
    """The value a drag at screen ``x`` sets on slider ``name``."""
    lo, hi = SLIDERS[name]
    tx, _, tw, _ = track
    fraction = max(0.0, min(1.0, (x - tx) / float(tw))) if tw else 0.0
    return int(round(lo + fraction * (hi - lo)))


def slider_fraction(name, value):
    lo, hi = SLIDERS[name]
    return max(0.0, min(1.0, (value - lo) / float(hi - lo)))


def strip_hit_test(strip, x, y):
    """What a click lands on in the strip: ``"tilt"``, ``"shake"``,
    ``"slider:<name>"`` -- or ``None``."""
    def inside(rect, grow=0, grow_x=0):
        rx, ry, rw, rh = rect
        return (rx - grow_x <= x < rx + rw + grow_x
                and ry - grow <= y < ry + rh + grow)
    if inside(strip.tilt):
        return "tilt"
    if inside(strip.shake):
        return "shake"
    for name, track in strip.sliders.items():
        if inside(track, grow=7, grow_x=6):   # the knob overhangs the ends
            return f"slider:{name}"
    return None


def strip_visible(instance):
    """The sensor strip shows unless ``microbit_show_sensors`` is off."""
    value = option_of(instance, "microbit_show_sensors", True)
    if isinstance(value, str):
        return value.strip().lower() not in ("false", "0", "no", "")
    return bool(value)

#!/usr/bin/env python3
"""Where everything on the drawn micro:bit sits (Stage S5).

Pure geometry -- no pygame -- so the renderer, the mouse hit-testing (S6),
the sensor strip (S7) and the tests all read the same numbers. All
coordinates are screen pixels. ``board_layout(cx, cy, scale)`` places the
board centred on ``(cx, cy)``; at scale 1.0 it is ``BODY_W`` pixels wide.
"""
from dataclasses import dataclass
from typing import Dict, Tuple

# Design units (scale 1.0): the real board is 52 x 42 mm, drawn at ~4.2 px/mm.
BODY_W = 220
BODY_H = 178
LED_PITCH = 24
LED_SIZE = 14
LED_CENTER_DY = -8          # the LED grid sits a little above centre
BUTTON_DX = 85
BUTTON_RADIUS = 15
LOGO_DY = -68
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
    return BoardLayout(cx, cy, scale, body, max(2, _r(s(LED_SIZE))), leds,
                       buttons, logo, pads)


def led_color(level, brightness=255):
    """The glow of one LED: ``level`` 0-9 scaled by the display brightness
    (0-255), from a dark red (off) to a bright red (on)."""
    amount = max(0, min(9, level)) / 9.0 * max(0, min(255, brightness)) / 255.0
    return tuple(int(round(o + (n - o) * amount)) for o, n in zip(OFF_COLOR, ON_COLOR))

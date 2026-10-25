#!/usr/bin/env python3
"""``MicrobitSimulator`` -- the pure state of one simulated micro:bit.

No pygame, no Qt: the frame update, the overlay and (later) the serial
link all read and write this object. Stage S1 only gives it the 5x5
display buffer; Stage S2 adds buttons, sensors, gestures and the display
queue (docs/MICROBIT_EXTENSION_PLAN.md).
"""

WIDTH = 5
HEIGHT = 5
MAX_BRIGHTNESS = 9


class MicrobitSimulator:
    def __init__(self):
        # display[y][x], brightness 0-9 like MicroPython's display.get_pixel
        self.display = [[0] * WIDTH for _ in range(HEIGHT)]

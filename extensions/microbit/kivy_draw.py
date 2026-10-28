"""The drawn micro:bit as draw-queue commands (Stage P, unit K3).

Shipped into a Kivy export as ``microbit_sim/draw.py`` and pure (no pygame, no
Kivy). It mirrors ``renderer.py`` -- same layout numbers (``layout.py``, shipped
verbatim), same colours -- but emits the command dicts the exported game's own
draw-queue renderer already understands (``rectangle`` / ``circle`` /
``ellipse`` / ``line`` / ``scaled_text``, room coordinates, y down), so Kivy's
y-up flip happens in one place that already exists.

Deliberate simplifications, because the draw queue has no such primitives:
square corners instead of rounded ones, and no silkscreen corner wedge or A/B
tags (purely decorative). tests/test_kivy_microbit_draw.py rasterises these
commands and compares them with the pygame renderer.
"""
from .layout import (led_color, strip_layout, tilt_to_pos, slider_fraction,
                     PAD_NAMES, TOUCH_PINS)

BODY_COLOR = (34, 36, 40)
BODY_EDGE = (12, 12, 14)
LED_WELL = (18, 8, 8)
LED_CHIP = (140, 142, 148)
BUTTON_COLOR = (205, 205, 200)
BUTTON_DOWN = (255, 214, 90)
BUTTON_EDGE = (110, 110, 105)
LOGO_COLOR = (54, 199, 149)
LOGO_TOUCHED = (150, 255, 210)
LOGO_DOT = (16, 80, 62)
PAD_COLOR = (196, 150, 60)
PAD_TOUCHED = (255, 240, 150)
PAD_EDGE = (80, 60, 20)
PAD_HOLE = (70, 52, 18)
LABEL_COLOR = (200, 200, 200)
PANEL_COLOR = (46, 48, 54)
PANEL_EDGE = (20, 20, 24)
PAD_WELL = (24, 26, 30)
PAD_DOT = (255, 214, 90)
TRACK_COLOR = (90, 92, 100)
TRACK_FILL = (96, 170, 255)
KNOB_COLOR = (230, 230, 235)
SHAKE_COLOR = (96, 110, 150)
SHAKE_ACTIVE = (255, 214, 90)
SPEAKER_ON = (120, 220, 255)
SPEAKER_OFF = (60, 62, 70)
SLIDER_TITLES = {"light": "Light", "temperature": "Temp", "compass": "Compass",
                 "sound": "Sound"}

# The exported text is one fixed-size font; scaled_text scales it. A pygame
# Font(None, n) glyph is about n/28 of that font's size.
TEXT_UNIT = 28.0


def _rect(x, y, w, h, color, filled=True):
    return {"type": "rectangle", "x1": x, "y1": y, "x2": x + w, "y2": y + h,
            "filled": filled, "color": color}


def _circle(x, y, radius, color, filled=True):
    return {"type": "circle", "x": x, "y": y, "radius": radius,
            "filled": filled, "color": color}


def _ellipse(x, y, rx, ry, color):
    return {"type": "ellipse", "x1": x - rx, "y1": y - ry, "x2": x + rx, "y2": y + ry,
            "filled": True, "color": color}


def _line(x1, y1, x2, y2, color):
    return {"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color}


def _text(text, x, y, size, color, anchor="topleft"):
    scale = size / TEXT_UNIT
    return {"type": "scaled_text", "text": str(text), "x": x, "y": y,
            "xscale": scale, "yscale": scale, "anchor": anchor, "color": color}


def _slider_value(sim, name):
    return {"light": sim.light_level, "temperature": sim.temperature,
            "compass": sim.compass_heading, "sound": sim.sound_level}[name]


def board_commands(layout, sim, draw_body=True):
    """The board (body, LEDs, buttons, speaker, logo, edge connector)."""
    cmds = []
    if draw_body:
        bx, by, bw, bh = layout.body
        cmds.append(_rect(bx, by, bw, bh, BODY_COLOR))
        cmds.append(_rect(bx, by, bw, bh, BODY_EDGE, filled=False))

    size = layout.led_size
    half = size // 2
    chip_w = max(2, int(size * 0.18))
    chip_margin = max(1, int(size * 0.05))
    for y in range(5):
        for x in range(5):
            px, py = layout.led_center(x, y)
            cmds.append(_rect(px - half - 1, py - half - 1, size + 2, size + 2, LED_WELL))
            cmds.append(_rect(px - half, py - half, size, size,
                              led_color(sim.display[y][x], sim.brightness)))
            if sim.display[y][x] == 0:
                # The unlit LED's grey component mark, as two halves with the
                # 1px seam at the centre pixel left untouched (as renderer.py).
                chip_half_h = max(2, half - chip_margin - 1)
                cx0 = px - chip_w // 2
                cmds.append(_rect(cx0, py - half + chip_margin, chip_w, chip_half_h, LED_CHIP))
                cmds.append(_rect(cx0, py + 1, chip_w, chip_half_h, LED_CHIP))

    for name, (bx, by, br) in layout.buttons.items():
        down = sim.buttons.get(name, False)
        cmds.append(_circle(bx, by, br, BUTTON_DOWN if down else BUTTON_COLOR))
        cmds.append(_circle(bx, by, br, BUTTON_EDGE, filled=False))
        cmds.append(_text(name.upper(), bx, by, max(12, int(28 * layout.scale)),
                          (40, 40, 40), "center"))

    kx, ky, kr = layout.speaker
    playing = getattr(sim, "tone", 0) > 0
    cmds.append(_circle(kx, ky, kr, SPEAKER_ON if playing else SPEAKER_OFF))
    if playing:
        for grow in (kr + 4, kr + 9):
            cmds.append(_circle(kx, ky, grow, SPEAKER_ON, filled=False))

    lx, ly, rx, ry = layout.logo
    cmds.append(_ellipse(lx, ly, rx, ry, LOGO_TOUCHED if sim.logo_touched else LOGO_COLOR))
    dot_r = max(1, int(ry * 0.35))
    dot_dx = rx * 0.45
    if dot_dx > dot_r:
        cmds.append(_circle(int(lx - dot_dx), ly, dot_r, LOGO_DOT))
        cmds.append(_circle(int(lx + dot_dx), ly, dot_r, LOGO_DOT))

    for name in PAD_NAMES:
        x, y, w, h = layout.pads[name]
        touched = name.isdigit() and int(name) in TOUCH_PINS \
            and sim.pins_touched.get(int(name), False)
        cmds.append(_rect(x, y, w, h, PAD_TOUCHED if touched else PAD_COLOR))
        cmds.append(_rect(x, y, w, h, PAD_EDGE, filled=False))
        hole_r = max(1, int(min(w, h) * 0.18))
        hole_cy = y + hole_r + max(1, int(2 * layout.scale))
        if hole_cy + hole_r < y + h - max(4, int(4 * layout.scale)):
            cmds.append(_circle(x + w // 2, hole_cy, hole_r, PAD_HOLE))
        cmds.append(_text(name, x + w // 2, y - 2, max(10, int(19 * layout.scale)),
                          LABEL_COLOR, "midbottom"))
    return cmds


def strip_commands(layout, sim):
    """The sensor strip: tilt pad on the left, shake button and sliders on the right."""
    strip = strip_layout(layout)
    scale = layout.scale
    cmds = []
    for panel in (strip.panel_left, strip.panel_right):
        cmds.append(_rect(*panel, PANEL_COLOR))
        cmds.append(_rect(*panel, PANEL_EDGE, filled=False))

    tx, ty, tw, th = strip.tilt
    cmds.append(_rect(tx, ty, tw, th, PAD_WELL))
    cmds.append(_line(tx + tw // 2, ty, tx + tw // 2, ty + th - 1, TRACK_COLOR))
    cmds.append(_line(tx, ty + th // 2, tx + tw - 1, ty + th // 2, TRACK_COLOR))
    cmds.append(_rect(tx, ty, tw, th, PANEL_EDGE, filled=False))
    ax, ay, _ = sim.acceleration
    dx, dy = tilt_to_pos(strip.tilt, ax, ay)
    cmds.append(_circle(dx, dy, max(3, int(6 * scale)), PAD_DOT))
    cmds.append(_text("TILT", tx + 3, ty + 2, max(11, int(19 * scale)), LABEL_COLOR))

    sx, sy, sw, sh = strip.shake
    active = sim.current_gesture == "shake"
    cmds.append(_rect(sx, sy, sw, sh, SHAKE_ACTIVE if active else SHAKE_COLOR))
    cmds.append(_text("SHAKE", sx + sw // 2, sy + sh // 2, max(12, int(21 * scale)),
                      (20, 20, 20) if active else (235, 235, 240), "center"))

    for name, (kx, ky, kw, kh) in strip.sliders.items():
        value = _slider_value(sim, name)
        cmds.append(_text("%s %s" % (SLIDER_TITLES[name], value), kx, ky - 1,
                          max(11, int(19 * scale)), LABEL_COLOR, "bottomleft"))
        cmds.append(_rect(kx, ky, kw, kh, TRACK_COLOR))
        filled = int(kw * slider_fraction(name, value))
        if filled:
            cmds.append(_rect(kx, ky, filled, kh, TRACK_FILL))
        cmds.append(_circle(kx + filled, ky + kh // 2, max(3, kh // 2 + 2), KNOB_COLOR))
    return cmds

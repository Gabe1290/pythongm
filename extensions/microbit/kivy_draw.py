"""The drawn micro:bit as draw-queue commands (Stage P, unit K3).

Shipped into a Kivy export as ``microbit_sim/draw.py`` and pure (no pygame, no
Kivy). It mirrors ``renderer.py`` -- same layout numbers (``layout.py``, shipped
verbatim), same colours -- but emits the command dicts the exported game's own
draw-queue renderer already understands (``rectangle`` / ``circle`` /
``ellipse`` / ``line`` / ``scaled_text``, room coordinates, y down), so Kivy's
y-up flip happens in one place that already exists.

The draw queue gained a ``radius`` on ``rectangle`` and a ``polygon`` command for this, so the
rounded panels and pads, the silkscreen corner wedge and the A/B tags are all drawn. The only
thing left out is the unlit-LED chip's two half-rounded rectangles (a few pixels each).
tests/test_kivy_microbit_draw.py rasterises these commands and compares them with the pygame
renderer; tests/test_kivy_microbit_real_render.py renders them through REAL Kivy.
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
CORNER_GREEN = (54, 199, 149)         # silkscreen corner decoration + A/B tags
TAG_LABEL = (16, 54, 42)
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


def _rect(x, y, w, h, color, filled=True, radius=0):
    cmd = {"type": "rectangle", "x1": x, "y1": y, "x2": x + w, "y2": y + h,
           "filled": filled, "color": color}
    if radius:
        cmd["radius"] = radius
    return cmd


def _polygon(points, color):
    return {"type": "polygon", "points": [[x, y] for x, y in points], "color": color}


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


def _button_tag(name, bx, by, br, layout):
    """The small triangular 'A'/'B' flag beside a button (renderer._button_tag): 'A' hangs below
    its button pointing down-left, 'B' sits above it pointing up-right."""
    sc = layout.scale
    tw, th = max(6, int(20 * sc)), max(6, int(18 * sc))
    tx = bx - tw // 2
    gap = max(2, int(4 * sc))
    if name == "a":
        ty = by + br + gap
        pts = [(tx, ty + th), (tx + tw, ty + th), (tx + tw, ty)]
        centroid = (tx + tw * 2 / 3, ty + th * 2 / 3)
    else:
        ty = by - br - gap - th
        pts = [(tx + tw, ty), (tx, ty), (tx, ty + th)]
        centroid = (tx + tw / 3, ty + th / 3)
    return [_polygon(pts, CORNER_GREEN),
            _text(name.upper(), int(centroid[0]), int(centroid[1]), max(8, int(14 * sc)),
                  TAG_LABEL, "center")]


def board_commands(layout, sim, draw_body=True):
    """The board (body, LEDs, buttons, speaker, logo, edge connector)."""
    cmds = []
    if draw_body:
        bx, by, bw, bh = layout.body
        cmds.append(_rect(bx, by, bw, bh, BODY_COLOR))
        cmds.append(_rect(bx, by, bw, bh, BODY_EDGE, filled=False))
        # the jagged green silkscreen wedge in the top-left corner (purely decorative)
        cmds.append(_polygon([
            (bx, by), (bx + bw * 0.42, by), (bx + bw * 0.30, by + bh * 0.12),
            (bx + bw * 0.22, by + bh * 0.05), (bx + bw * 0.12, by + bh * 0.20),
            (bx + bw * 0.05, by + bh * 0.10), (bx, by + bh * 0.36)], CORNER_GREEN))

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
        if draw_body:
            cmds += _button_tag(name, bx, by, br, layout)

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
        cmds.append(_rect(x, y, w, h, PAD_TOUCHED if touched else PAD_COLOR, radius=3))
        cmds.append(_rect(x, y, w, h, PAD_EDGE, filled=False, radius=3))
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
    radius = max(2, int(8 * scale))
    for panel in (strip.panel_left, strip.panel_right):
        cmds.append(_rect(*panel, PANEL_COLOR, radius=radius))
        cmds.append(_rect(*panel, PANEL_EDGE, filled=False, radius=radius))

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
    cmds.append(_rect(sx, sy, sw, sh, SHAKE_ACTIVE if active else SHAKE_COLOR, radius=4))
    cmds.append(_text("SHAKE", sx + sw // 2, sy + sh // 2, max(12, int(21 * scale)),
                      (20, 20, 20) if active else (235, 235, 240), "center"))

    for name, (kx, ky, kw, kh) in strip.sliders.items():
        value = _slider_value(sim, name)
        cmds.append(_text("%s %s" % (SLIDER_TITLES[name], value), kx, ky - 1,
                          max(11, int(19 * scale)), LABEL_COLOR, "bottomleft"))
        cmds.append(_rect(kx, ky, kw, kh, TRACK_COLOR, radius=kh // 2))
        filled = int(kw * slider_fraction(name, value))
        if filled:
            cmds.append(_rect(kx, ky, filled, kh, TRACK_FILL, radius=kh // 2))
        cmds.append(_circle(kx + filled, ky + kh // 2, max(3, kh // 2 + 2), KNOB_COLOR))
    return cmds

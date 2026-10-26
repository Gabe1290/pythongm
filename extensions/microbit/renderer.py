#!/usr/bin/env python3
"""Draws a simulated micro:bit with pygame (Stage S5).

Procedural -- no sprite asset needed. ``draw_board`` paints from a
``BoardLayout`` (layout.py, the one source of geometry) and a
``MicrobitSimulator``; ``draw_overlay`` is the instance-overlay entry point
that works out where the board goes for a game instance.
"""
import pygame

from .layout import (led_color, layout_for, scale_of, center_of,  # noqa: F401
                     strip_layout, strip_visible, tilt_to_pos, slider_fraction,
                     PAD_NAMES, TOUCH_PINS)
from .state import simulator_of

BODY_COLOR = (34, 36, 40)
BODY_EDGE = (12, 12, 14)
LED_WELL = (18, 8, 8)
BUTTON_COLOR = (205, 205, 200)
BUTTON_DOWN = (255, 214, 90)
BUTTON_EDGE = (110, 110, 105)
LOGO_COLOR = (212, 175, 55)
LOGO_TOUCHED = (255, 240, 150)
LOGO_DOT = (120, 95, 20)              # accent dots inside the logo oval
PAD_COLOR = (196, 150, 60)
PAD_TOUCHED = (255, 240, 150)
PAD_EDGE = (80, 60, 20)
PAD_HOLE = (70, 52, 18)               # decorative pin-hole on each pad
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

_label_cache = {}


def _label(text, size, color):
    """A rendered text surface, cached by what it shows. Surfaces are cached
    rather than ``pygame.font.Font`` objects: a Font outlives a
    ``pygame.quit()`` as a dangling pointer (an access violation on the next
    render), a Surface doesn't."""
    key = (text, size, color)
    surface = _label_cache.get(key)
    if surface is None:
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.Font(None, size)
        if len(_label_cache) > 600:       # slider values make new strings
            _label_cache.clear()
        surface = _label_cache[key] = font.render(text, True, color)
    return surface


def _slider_value(sim, name):
    return {"light": sim.light_level, "temperature": sim.temperature,
            "compass": sim.compass_heading, "sound": sim.sound_level}[name]


def draw_strip(screen, strip, sim, scale=1.0):
    """Paint the sensor strip: tilt pad, shake button and the four sliders."""
    radius = max(2, int(8 * scale))
    pygame.draw.rect(screen, PANEL_COLOR, strip.panel, border_radius=radius)
    pygame.draw.rect(screen, PANEL_EDGE, strip.panel, width=1, border_radius=radius)

    tx, ty, tw, th = strip.tilt
    pygame.draw.rect(screen, PAD_WELL, strip.tilt)
    pygame.draw.line(screen, TRACK_COLOR, (tx + tw // 2, ty), (tx + tw // 2, ty + th - 1))
    pygame.draw.line(screen, TRACK_COLOR, (tx, ty + th // 2), (tx + tw - 1, ty + th // 2))
    pygame.draw.rect(screen, PANEL_EDGE, strip.tilt, width=1)
    ax, ay, _ = sim.acceleration
    pygame.draw.circle(screen, PAD_DOT, tilt_to_pos(strip.tilt, ax, ay),
                       max(3, int(6 * scale)))
    screen.blit(_label("TILT", max(11, int(15 * scale)), LABEL_COLOR), (tx + 3, ty + 2))

    sx, sy, sw, sh = strip.shake
    active = sim.current_gesture == "shake"
    pygame.draw.rect(screen, SHAKE_ACTIVE if active else SHAKE_COLOR, strip.shake,
                     border_radius=4)
    text = _label("SHAKE", max(12, int(17 * scale)),
                  (20, 20, 20) if active else (235, 235, 240))
    screen.blit(text, text.get_rect(center=(sx + sw // 2, sy + sh // 2)))

    for name, (kx, ky, kw, kh) in strip.sliders.items():
        value = _slider_value(sim, name)
        label = _label(f"{SLIDER_TITLES[name]} {value}", max(11, int(15 * scale)),
                       LABEL_COLOR)
        screen.blit(label, (kx, ky - label.get_height() - 1))
        pygame.draw.rect(screen, TRACK_COLOR, (kx, ky, kw, kh), border_radius=kh // 2)
        filled = int(kw * slider_fraction(name, value))
        if filled:
            pygame.draw.rect(screen, TRACK_FILL, (kx, ky, filled, kh),
                             border_radius=kh // 2)
        pygame.draw.circle(screen, KNOB_COLOR, (kx + filled, ky + kh // 2),
                           max(3, kh // 2 + 2))


def _corner_decoration(screen, layout):
    """The jagged green silkscreen wedge in the board's top-left corner --
    purely decorative, inset from the literal corner so it sits inside the
    body's rounded edge instead of poking past it."""
    bx, by, bw, bh = layout.body
    sc = layout.scale
    inset = max(2, int(5 * sc))
    x0, y0 = bx + inset, by + inset
    pts = [
        (x0, y0),
        (bx + bw * 0.42, by),
        (bx + bw * 0.30, by + bh * 0.12),
        (bx + bw * 0.22, by + bh * 0.05),
        (bx + bw * 0.12, by + bh * 0.20),
        (bx + bw * 0.05, by + bh * 0.10),
        (bx, by + bh * 0.36),
    ]
    pygame.draw.polygon(screen, CORNER_GREEN, pts)


def _button_tag(screen, name, bx, by, br, layout):
    """The small triangular 'A'/'B' flag beside a button, matching the real
    board's silkscreen tag -- separate from (and in addition to) the letter
    already drawn on the button cap for at-a-glance readability."""
    sc = layout.scale
    tw, th = max(6, int(16 * sc)), max(6, int(14 * sc))
    tx = bx - tw // 2
    ty = by + br + max(2, int(3 * sc))
    if name == "a":
        pts = [(tx, ty), (tx + tw, ty), (tx, ty + th)]
        centroid = (tx + tw / 3, ty + th / 3)
    else:
        pts = [(tx, ty), (tx + tw, ty), (tx + tw, ty + th)]
        centroid = (tx + tw * 2 / 3, ty + th / 3)
    pygame.draw.polygon(screen, CORNER_GREEN, pts)
    label = _label(name.upper(), max(8, int(11 * sc)), TAG_LABEL)
    screen.blit(label, label.get_rect(center=(int(centroid[0]), int(centroid[1]))))


def draw_board(screen, layout, sim, draw_body=True):
    """Paint the board. ``draw_body=False`` leaves the body out, for an
    instance whose own sprite is the board (LEDs and controls draw on top)."""
    if draw_body:
        bx, by, bw, bh = layout.body
        radius = max(2, int(14 * layout.scale))
        pygame.draw.rect(screen, BODY_COLOR, (bx, by, bw, bh), border_radius=radius)
        pygame.draw.rect(screen, BODY_EDGE, (bx, by, bw, bh), width=2,
                         border_radius=radius)
        _corner_decoration(screen, layout)

    # LEDs
    size = layout.led_size
    half = size // 2
    for y in range(5):
        for x in range(5):
            px, py = layout.led_center(x, y)
            pygame.draw.rect(screen, LED_WELL,
                             (px - half - 1, py - half - 1, size + 2, size + 2))
            pygame.draw.rect(screen, led_color(sim.display[y][x], sim.brightness),
                             (px - half, py - half, size, size))

    # Buttons
    for name, (bx, by, br) in layout.buttons.items():
        down = sim.buttons.get(name, False)
        pygame.draw.circle(screen, BUTTON_DOWN if down else BUTTON_COLOR, (bx, by), br)
        pygame.draw.circle(screen, BUTTON_EDGE, (bx, by), br, 2)
        label = _label(name.upper(), max(12, int(22 * layout.scale)), (40, 40, 40))
        screen.blit(label, label.get_rect(center=(bx, by)))
        if draw_body:
            _button_tag(screen, name, bx, by, br, layout)

    # Speaker: lit with sound waves while a tone plays
    kx, ky, kr = layout.speaker
    playing = getattr(sim, "tone", 0) > 0
    pygame.draw.circle(screen, SPEAKER_ON if playing else SPEAKER_OFF, (kx, ky), kr)
    if playing:
        for grow in (kr + 4, kr + 9):
            pygame.draw.circle(screen, SPEAKER_ON, (kx, ky), grow, 1)

    # Touch logo: filled oval (the exact fill colour, including at its
    # centre, is what the touch state reflects) plus two off-centre accent
    # dots so it reads as the real board's two-eyes logo/mic icon.
    lx, ly, rx, ry = layout.logo
    pygame.draw.ellipse(screen, LOGO_TOUCHED if sim.logo_touched else LOGO_COLOR,
                        (lx - rx, ly - ry, rx * 2, ry * 2))
    dot_r = max(1, int(ry * 0.35))
    dot_dx = rx * 0.45
    if dot_dx > dot_r:
        pygame.draw.circle(screen, LOGO_DOT, (int(lx - dot_dx), ly), dot_r)
        pygame.draw.circle(screen, LOGO_DOT, (int(lx + dot_dx), ly), dot_r)

    # Edge connector
    for name in PAD_NAMES:
        x, y, w, h = layout.pads[name]
        touched = name.isdigit() and int(name) in TOUCH_PINS \
            and sim.pins_touched.get(int(name), False)
        pygame.draw.rect(screen, PAD_TOUCHED if touched else PAD_COLOR, (x, y, w, h),
                         border_radius=3)
        pygame.draw.rect(screen, PAD_EDGE, (x, y, w, h), width=1, border_radius=3)
        hole_r = max(1, int(min(w, h) * 0.18))
        hole_cy = y + hole_r + max(1, int(2 * layout.scale))
        if hole_cy + hole_r < y + h - max(4, int(4 * layout.scale)):
            pygame.draw.circle(screen, PAD_HOLE, (x + w // 2, hole_cy), hole_r)
        label = _label(name, max(10, int(15 * layout.scale)), LABEL_COLOR)
        screen.blit(label, label.get_rect(midbottom=(x + w // 2, y - 2)))


def draw_overlay(instance, screen):
    """Instance-overlay hook: draw the board for a micro:bit instance."""
    sim = simulator_of(instance)
    if sim is None or not getattr(instance, "visible", True):
        return
    layout = layout_for(instance)
    draw_board(screen, layout, sim,
               draw_body=getattr(instance, "sprite", None) is None)
    if strip_visible(instance):
        draw_strip(screen, strip_layout(layout), sim, layout.scale)

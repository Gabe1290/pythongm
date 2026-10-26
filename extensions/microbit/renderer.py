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
PAD_COLOR = (196, 150, 60)
PAD_TOUCHED = (255, 240, 150)
PAD_EDGE = (80, 60, 20)
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


def draw_board(screen, layout, sim, draw_body=True):
    """Paint the board. ``draw_body=False`` leaves the body out, for an
    instance whose own sprite is the board (LEDs and controls draw on top)."""
    if draw_body:
        bx, by, bw, bh = layout.body
        radius = max(2, int(14 * layout.scale))
        pygame.draw.rect(screen, BODY_COLOR, (bx, by, bw, bh), border_radius=radius)
        pygame.draw.rect(screen, BODY_EDGE, (bx, by, bw, bh), width=2,
                         border_radius=radius)

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

    # Speaker: lit with sound waves while a tone plays
    kx, ky, kr = layout.speaker
    playing = getattr(sim, "tone", 0) > 0
    pygame.draw.circle(screen, SPEAKER_ON if playing else SPEAKER_OFF, (kx, ky), kr)
    if playing:
        for grow in (kr + 4, kr + 9):
            pygame.draw.circle(screen, SPEAKER_ON, (kx, ky), grow, 1)

    # Touch logo
    lx, ly, rx, ry = layout.logo
    pygame.draw.ellipse(screen, LOGO_TOUCHED if sim.logo_touched else LOGO_COLOR,
                        (lx - rx, ly - ry, rx * 2, ry * 2))

    # Edge connector
    for name in PAD_NAMES:
        x, y, w, h = layout.pads[name]
        touched = name.isdigit() and int(name) in TOUCH_PINS \
            and sim.pins_touched.get(int(name), False)
        pygame.draw.rect(screen, PAD_TOUCHED if touched else PAD_COLOR, (x, y, w, h),
                         border_radius=3)
        pygame.draw.rect(screen, PAD_EDGE, (x, y, w, h), width=1, border_radius=3)
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

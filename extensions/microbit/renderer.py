#!/usr/bin/env python3
"""Draws a simulated micro:bit with pygame (Stage S5).

Procedural -- no sprite asset needed. ``draw_board`` paints from a
``BoardLayout`` (layout.py, the one source of geometry) and a
``MicrobitSimulator``; ``draw_overlay`` is the instance-overlay entry point
that works out where the board goes for a game instance.
"""
import pygame

from .layout import (led_color, layout_for, scale_of, center_of,  # noqa: F401
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
        surface = _label_cache[key] = font.render(text, True, color)
    return surface


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
    draw_board(screen, layout_for(instance), sim,
               draw_body=getattr(instance, "sprite", None) is None)

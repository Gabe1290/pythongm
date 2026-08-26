#!/usr/bin/env python3
"""Draw samples/sky_strike_1's sprites and scrolling ground texture.

Committed rather than hand-drawn so the art is reviewable as intent and can
be regenerated, matching tools/gen_raycast_4_gate.py's precedent: flat
colours, no antialiasing (pygame scales these directly with no smoothing
pass, so soft edges turn to mud at small sizes).

    python3 tools/gen_sky_strike_1_sprites.py
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: pip install --user pillow")

ROOT = Path(__file__).resolve().parent.parent / "samples" / "sky_strike_1"
SPRITES = ROOT / "sprites"
BACKGROUNDS = ROOT / "backgrounds"


def _new(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def draw_player():
    """24x24 delta-wing fighter, nose up (screen convention: -y is up)."""
    img = _new((24, 24))
    d = ImageDraw.Draw(img)
    hull = (70, 150, 230, 255)
    hull_lit = (140, 200, 255, 255)
    canopy = (20, 40, 60, 255)
    d.polygon([(12, 1), (3, 20), (12, 16), (21, 20)], fill=hull)
    d.polygon([(12, 1), (10, 14), (12, 16), (14, 14)], fill=hull_lit)
    d.rectangle([10, 6, 13, 10], fill=canopy)
    d.polygon([(3, 20), (0, 23), (8, 21)], fill=hull)
    d.polygon([(21, 20), (24, 23), (16, 21)], fill=hull)
    img.save(SPRITES / "spr_player.png")


def draw_bullet():
    """4x10 tracer round, player's air-to-air weapon."""
    img = _new((4, 10))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 0, 2, 9], fill=(255, 230, 80, 255))
    d.point([(1, 0), (2, 0)], fill=(255, 255, 200, 255))
    img.save(SPRITES / "spr_bullet.png")


def draw_bomb():
    """6x8 falling bomb, player's air-to-ground weapon."""
    img = _new((6, 8))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, 5, 6], fill=(40, 40, 44, 255))
    d.point([(1, 1)], fill=(90, 90, 96, 255))
    d.rectangle([2, 6, 3, 7], fill=(180, 60, 40, 255))  # tail fin
    img.save(SPRITES / "spr_bomb.png")


def draw_enemy_plane():
    """24x24 enemy fighter, nose down -- mirrors the player, reads as
    "coming at you" rather than "friendly," different hull colour."""
    img = _new((24, 24))
    d = ImageDraw.Draw(img)
    hull = (200, 60, 50, 255)
    hull_lit = (240, 120, 100, 255)
    canopy = (50, 20, 20, 255)
    d.polygon([(12, 23), (3, 4), (12, 8), (21, 4)], fill=hull)
    d.polygon([(12, 23), (10, 10), (12, 8), (14, 10)], fill=hull_lit)
    d.rectangle([10, 14, 13, 18], fill=canopy)
    d.polygon([(3, 4), (0, 1), (8, 3)], fill=hull)
    d.polygon([(21, 4), (24, 1), (16, 3)], fill=hull)
    img.save(SPRITES / "spr_enemy_plane.png")


def draw_ground_target():
    """28x28 ground bunker/turret -- only vulnerable to bombs, never
    bullets, so it needs to read as clearly "not a plane": square, dug in,
    earth-toned rather than the fighters' sleek hull colours."""
    img = _new((28, 28))
    d = ImageDraw.Draw(img)
    earth = (90, 70, 40, 255)
    earth_lit = (120, 96, 58, 255)
    metal = (86, 90, 96, 255)
    metal_lit = (130, 134, 140, 255)
    d.ellipse([1, 14, 26, 27], fill=earth)
    d.ellipse([3, 12, 24, 22], fill=earth_lit)
    d.rectangle([9, 6, 18, 16], fill=metal)
    d.rectangle([9, 6, 11, 16], fill=metal_lit)
    d.rectangle([12, 2, 15, 8], fill=metal)  # gun barrel
    img.save(SPRITES / "spr_ground_target.png")


def draw_crosshair():
    """18x18 bombing reticle -- drawn ahead of the ship every frame so the
    player can see which column a dropped bomb will travel straight up,
    matching the classic arcade-shooter targeting-ring convention. An open
    ring + tick marks (not a filled shape) so it never obscures a ground
    target sitting under it."""
    img = _new((18, 18))
    d = ImageDraw.Draw(img)
    ring = (255, 210, 40, 255)
    d.ellipse([1, 1, 16, 16], outline=ring, width=2)
    d.line([(9, 0), (9, 4)], fill=ring, width=2)
    d.line([(9, 13), (9, 17)], fill=ring, width=2)
    d.line([(0, 9), (4, 9)], fill=ring, width=2)
    d.line([(13, 9), (17, 9)], fill=ring, width=2)
    img.save(SPRITES / "spr_crosshair.png")


def draw_ground_background():
    """64x64 tiling scroll-ground texture -- a coarse grid over a green
    field, so continuous downward scroll (set_background's vspeed) reads
    unambiguously as motion rather than a static painted backdrop."""
    img = Image.new("RGBA", (64, 64), (58, 110, 62, 255))
    d = ImageDraw.Draw(img)
    dark = (46, 92, 50, 255)
    d.rectangle([0, 0, 63, 1], fill=dark)
    d.rectangle([0, 32, 63, 33], fill=dark)
    d.rectangle([0, 0, 1, 63], fill=dark)
    d.rectangle([32, 0, 33, 63], fill=dark)
    for x, y in ((8, 8), (44, 20), (20, 44), (50, 50)):
        d.ellipse([x, y, x + 5, y + 5], fill=(70, 128, 74, 255))
    img.save(BACKGROUNDS / "bg_ground.png")


if __name__ == "__main__":
    SPRITES.mkdir(parents=True, exist_ok=True)
    BACKGROUNDS.mkdir(parents=True, exist_ok=True)
    draw_player()
    draw_bullet()
    draw_bomb()
    draw_enemy_plane()
    draw_ground_target()
    draw_crosshair()
    draw_ground_background()
    print("Wrote sprites + background to", ROOT)

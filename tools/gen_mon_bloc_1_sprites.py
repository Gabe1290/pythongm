#!/usr/bin/env python3
"""Draw samples/mon_bloc_1's sprites: the player and three coin types.

Committed rather than hand-drawn so the art is reviewable as intent and
can be regenerated, matching tools/gen_sky_strike_1_sprites.py's
precedent: flat colours, no antialiasing (pygame scales these directly
with no smoothing pass, so soft edges turn to mud at small sizes).

    python3 tools/gen_mon_bloc_1_sprites.py
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: pip install --user pillow")

ROOT = Path(__file__).resolve().parent.parent / "samples" / "mon_bloc_1"
SPRITES = ROOT / "sprites"


def _circle(name, size, fill, outline):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = 1
    draw.ellipse([pad, pad, size - 1 - pad, size - 1 - pad],
                 fill=fill, outline=outline, width=2)
    img.save(SPRITES / f"{name}.png")


def main():
    SPRITES.mkdir(parents=True, exist_ok=True)
    _circle("spr_joueur", 24, (40, 110, 220, 255), (20, 60, 140, 255))
    _circle("spr_piece_bronze", 16, (205, 127, 50, 255), (120, 70, 25, 255))
    _circle("spr_piece_argent", 16, (200, 200, 205, 255), (120, 120, 125, 255))
    _circle("spr_piece_or", 16, (255, 210, 60, 255), (170, 130, 20, 255))
    print(f"Wrote 4 sprites into {SPRITES}")


if __name__ == "__main__":
    main()

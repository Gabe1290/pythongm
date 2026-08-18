#!/usr/bin/env python3
"""Draw raycast_4's locked-gate sprite (samples/raycast_4/sprites/spr_gate.png).

Why this exists: obj_goal and obj_key both pointed at `spr_key`, so the exit
you are looking for was drawn as another gold key -- in a level whose entire
task is "find three keys, then find the gate", the one thing that must not
look like a key looked exactly like one.

Committed rather than hand-drawn so the art is reviewable as intent and can
be regenerated: 32x32 to match spr_key/spr_monster, RGBA, flat colours, no
antialiasing (the raycast billboard renderer scales it hard, and soft edges
turn to mud).

Read as a PORTCULLIS -- stone arch, vertical bars, dark gap behind -- which
shares no shape or colour with a small gold key. Deliberately grey, not gold:
another gold object in a key-hunting level is the mistake being fixed.

    py -3.12 tools/gen_raycast_4_gate.py
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: py -3.12 -m pip install --user pillow")

SIZE = 32
OUT = (Path(__file__).resolve().parent.parent
       / "samples" / "raycast_4" / "sprites" / "spr_gate.png")

VOID = (26, 24, 32, 255)        # the dark beyond the bars
BAR = (86, 90, 102, 255)        # cold steel, no warmth that could read as gold
BAR_LIT = (122, 128, 142, 255)  # top-left highlight on each bar
STONE = (146, 142, 136, 255)    # matches the wall/ceiling stone family
STONE_LIT = (178, 174, 166, 255)
STONE_DARK = (104, 100, 96, 255)


def draw_gate():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Arched opening, 3px stone jambs either side, springing from y=9.
    d.rectangle([4, 8, 27, 31], fill=VOID)
    d.ellipse([4, 2, 27, 15], fill=VOID)

    # Four vertical bars across the opening, with a lit left edge each.
    for x in range(7, 26, 6):
        d.rectangle([x, 4, x + 2, 31], fill=BAR)
        d.line([(x, 5), (x, 31)], fill=BAR_LIT)

    # Two cross-rails, so it reads as a gate rather than a cage.
    for y in (13, 23):
        d.rectangle([5, y, 26, y + 1], fill=BAR)
        d.line([(5, y), (26, y)], fill=BAR_LIT)

    # Stone surround last, so it sits in front of the bars.
    d.arc([2, 1, 29, 16], start=180, end=360, fill=STONE, width=3)
    d.rectangle([1, 9, 3, 31], fill=STONE)
    d.rectangle([28, 9, 30, 31], fill=STONE)
    d.line([(1, 9), (1, 31)], fill=STONE_LIT)      # lit left jamb
    d.line([(30, 9), (30, 31)], fill=STONE_DARK)   # shaded right jamb
    d.rectangle([0, 29, 31, 31], fill=STONE_DARK)  # threshold

    return img


def main():
    img = draw_gate()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    opaque = sum(1 for a in img.getchannel("A").tobytes() if a)
    print("wrote %s (%dx%d, %d opaque px)" % (OUT, SIZE, SIZE, opaque))


if __name__ == "__main__":
    main()

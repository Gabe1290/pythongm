#!/usr/bin/env python3
"""Eyeball the Block World renderer (Phase 2a of docs/VOXEL_WORLD_PLAN.md).

Every automated check on this renderer so far samples individual pixels
(tests/test_block_world_renderer.py) -- enough to prove a strip got drawn,
useless for judging whether the CC0 textures actually READ well at a
distance, which is the stated point of Phase 2a. This script is the
human-eyes half.

    py -3.12 tools/preview_block_world.py              # walk around
    py -3.12 tools/preview_block_world.py --shots out  # save fixed frames

The walkaround needs a real display; --shots works headless (it forces
SDL_VIDEODRIVER=dummy) and writes one PNG per viewpoint in VIEWPOINTS.

This calls extensions.block_world.renderer.render_block_world_view directly
against a real GameRoom -- the same entry point the room-renderer hook uses
in a running game -- so what you see here is what the engine draws. It does
NOT go through the IDE, a project, or a sample; Phase 5 is where a real
playable sample lands.

Demo-only caveats, deliberately not engine features:
  - Movement/collision here are this script's own (Phase 4 is where the
    engine gets voxel collision). Press C to fly through walls and inspect
    geometry from inside a block.
  - The world is hand-built in build_world() below, not loaded from a file
    (Phase 3 is where a world-authoring path lands).
"""

import argparse
import math
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CELL = 32
WORLD_W, WORLD_H = 28, 24


def build_world(room):
    """A showcase scene: one z-layer (all Phase 2a can draw), holding every
    block type in the registry, arranged so texture legibility gets tested at
    genuinely different distances.

    Layout (y grows DOWNWARD, GM convention):

        y 1..8    upper yard -- brick hut, isolated stone pillars
        y 9, 13   the long cobble corridor's two walls, x 4..25
        y 14..22  lower yard -- material rows, each in its own clear lane

    Every VIEWPOINT below stands in open air in one of those bands; keep that
    true when adding blocks, or a viewpoint ends up nose-to-wall.
    """
    from extensions.block_world.state import set_block, remove_block

    def fill(x0, y0, x1, y1, block_type):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                set_block(room, x, y, 0, block_type)

    def row(x0, y, block_types):
        for i, block_type in enumerate(block_types):
            set_block(room, x0 + i, y, 0, block_type)

    # Perimeter wall -- stone, so the eye has a neutral reference everywhere.
    fill(0, 0, WORLD_W - 1, 0, "stone")
    fill(0, WORLD_H - 1, WORLD_W - 1, WORLD_H - 1, "stone")
    fill(0, 0, 0, WORLD_H - 1, "stone")
    fill(WORLD_W - 1, 0, WORLD_W - 1, WORLD_H - 1, "stone")

    # A long cobble corridor: the distance test. The same texture repeats from
    # 2 cells away out past 20, so shading, fog and texel aliasing are all
    # visible in a single frame, with a brick end wall to stop the eye.
    fill(4, 9, 25, 9, "cobble")
    fill(4, 13, 25, 13, "cobble")
    fill(25, 10, 25, 12, "brick")

    # A brick hut in the upper yard with a doorway gap, for silhouette and
    # inside-corner reading.
    fill(4, 3, 9, 3, "brick")
    fill(4, 7, 9, 7, "brick")
    fill(4, 3, 4, 7, "brick")
    fill(9, 3, 9, 7, "brick")
    remove_block(room, 9, 5, 0)

    # Isolated single-cell pillars: corner geometry and the side-shade depth
    # cue, without a long flat face confusing the picture.
    for x in (14, 17, 20):
        set_block(room, x, 5, 0, "stone")

    # Lower yard, one material family per lane.
    # Shiny / transparent-flagged types. Phase 2a draws these fully opaque --
    # BLOCK_TYPES' "transparent" flag is not honoured by the renderer yet,
    # which is exactly the sort of thing worth SEEING before Phase 2b.
    row(3, 15, ["glass", "water", "ice", "obsidian",
                "coal_block", "gold_block", "diamond_block", "mese_block"])
    # Wool: flat colour, the quickest way to spot a shading or channel-order
    # bug. All six, side by side. Parked on the far lane (y 21, not 18) so the
    # shiny row above it can be viewed from far enough back to fit in frame --
    # at FOV 66 a row N cells wide needs roughly N/1.3 cells of standoff.
    row(3, 21, ["wool_red", "wool_blue", "wool_green",
                "wool_yellow", "wool_white", "wool_black"])
    # Naturals: the busiest textures, where per-column texel sampling
    # artifacts show up first.
    row(13, 17, ["grass", "dirt", "sand", "desert_sand",
                 "sandstone", "gravel", "clay", "snow"])
    row(13, 21, ["wood_log", "wood_plank", "jungle_plank",
                 "pine_plank", "leaves"])

    # --- Phase 2b: the parts that need more than one layer ----------------
    # A raised terrace in the upper-right yard, reached by a staircase, with
    # a pit dug into it and a tower rising off it. Everything below is at
    # z >= 1, so the flat showcase above is untouched and still renders
    # exactly as it did under 2a.
    def slab(x0, y0, x1, y1, z_top, block_type):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(0, z_top + 1):
                    set_block(room, x, y, z, block_type)

    # Three single-block steps: stand on one at a time, layer 1, 2, then 3.
    slab(14, 2, 14, 3, 0, "sandstone")
    slab(15, 2, 15, 3, 1, "sandstone")
    slab(16, 2, 16, 3, 2, "sandstone")
    # The terrace itself -- walking surface at z = 3, so an eye standing here
    # looks DOWN on every one-high wall in the flat yard below.
    slab(17, 1, 24, 4, 2, "cobble")
    # A pit dug two deep into it. Its floor is the top face of the block at
    # z = 0, so it reads as a hole rather than a gap in the world.
    for z in (1, 2):
        remove_block(room, 20, 2, z)
        remove_block(room, 20, 3, z)
    # A tower off the terrace's far end: three more blocks above the deck.
    slab(22, 2, 22, 2, 5, "brick")


def make_room():
    from runtime.game_runner import GameRoom, GameInstance
    from extensions.block_world.state import block_world_state

    room = GameRoom("block_world_preview",
                    {"width": WORLD_W * CELL, "height": WORLD_H * CELL},
                    action_executor=None)
    build_world(room)

    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = CELL
    camera._cached_height = CELL
    camera.facing_angle = 0.0
    room.instances.append(camera)

    block_world_state(room)["camera"].update({
        "enabled": True,
        "camera_object": "obj_person",
        "cell_size": CELL,
        "z_layer": 0,
        "fov": 66,
        "render_distance": 24,
        "wall_textured": True,
    })
    return room, camera


def place(room, camera, cell_x, cell_y, facing_deg, z_layer=0):
    """Put the camera at the CENTRE of a grid cell, standing on layer
    z_layer. The renderer casts from top_left + size/2, so setting x/y to the
    cell's own corner is what puts the eye in the middle of it -- the exact
    off-by-one-cell trap the Phase 2a test helper hit (see the plan doc)."""
    from extensions.block_world.state import block_world_state
    camera.x = cell_x * CELL
    camera.y = cell_y * CELL
    camera.facing_angle = facing_deg
    block_world_state(room)["camera"]["z_layer"] = z_layer


def ground_layer(room, cell_x, cell_y):
    """The layer a body standing at this cell occupies: one above whatever it
    is standing on, or 0 over open ground. Demo-only -- the engine gets no
    gravity or footing until Phase 4."""
    from extensions.block_world.state import stack_top
    top = stack_top(room, cell_x, cell_y)
    return 0 if top is None else top + 1


# (label, cell_x, cell_y, facing_deg, z_layer, what it's for). GM angles:
# 0 = +x (right), 90 = up the screen, 180 = left, 270 = down.
VIEWPOINTS = [
    ("corridor", 5, 11, 0, 0, "20-cell cobble corridor -- distance/fog/aliasing"),
    ("endwall", 22, 11, 0, 0, "corridor's brick end wall up close"),
    ("hut", 12, 5, 180, 0, "brick hut silhouette + doorway gap"),
    ("pillars", 13, 6, 315, 0, "isolated pillars, oblique -- side-shade depth cue"),
    ("shiny", 6, 20, 90, 0, "glass/water/ice/obsidian/metal row"),
    ("wool", 5, 17, 270, 0, "six wool colours -- flat-colour fidelity"),
    ("naturals", 19, 22, 90, 0, "grass/dirt/sand/gravel/snow at mid distance"),
    ("wood", 19, 19, 225, 0, "wood family, oblique -- both faces of each block"),
    ("corner", 3, 3, 135, 0, "stone perimeter corner, both faces at once"),
    # Phase 2b
    ("steps", 10, 3, 0, 0, "2b: staircase from below -- three stacked heights"),
    ("terrace", 23, 3, 180, 3, "2b: standing on the terrace, looking back down"),
    ("overlook", 22, 4, 270, 3, "2b: see OVER the one-high yard walls from up top"),
    # A level camera cannot look down, so a pit right at your feet falls
    # below the frame -- you see its far lip, not its floor. That is the
    # limitation Phase 2c (free vertical look) exists to lift, and it is
    # worth having a picture of rather than a paragraph about.
    ("pit", 23, 2, 180, 3, "2b: pit -- floor is BELOW a level camera's view"),
    ("tower", 18, 2, 0, 3, "2b: tower across the pit, three blocks above deck"),
]


def save_shots(out_dir, size):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))  # convert_alpha() needs a video mode

    from extensions.block_world.renderer import render_block_world_view

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    room, camera = make_room()
    screen = pygame.Surface(size)
    for label, cx, cy, facing, z, note in VIEWPOINTS:
        place(room, camera, cx, cy, facing, z)
        render_block_world_view(room, screen)
        path = out / ("block_world_%s.png" % label)
        pygame.image.save(screen, str(path))
        print("%-10s %s  (%s)" % (label, path, note))
    print("\n%d frames written to %s" % (len(VIEWPOINTS), out.resolve()))


MAX_STEP_UP = 1


def _can_enter(room, cell_x, cell_y, standing_layer):
    """Walk onto a cell if its surface is at most one block higher than the
    one underfoot. Dropping any distance is allowed -- this demo has no
    gravity to fall with, so a drop is just a step down."""
    return ground_layer(room, cell_x, cell_y) - standing_layer <= MAX_STEP_UP


def walk(size):
    import pygame
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Block World preview -- Phase 2b")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas,couriernew,monospace", 15)

    from extensions.block_world.renderer import render_block_world_view
    from extensions.block_world.state import block_world_state

    room, camera = make_room()
    place(room, camera, *VIEWPOINTS[0][1:5])
    collide = True
    shot_n = 0
    move_speed, turn_speed = 110.0, 120.0  # px/sec, deg/sec

    hud_lines = [
        "WASD/arrows move+turn  Q,E strafe  1-%d viewpoints  C collision  "
        "P screenshot  ESC quit" % min(9, len(VIEWPOINTS)),
    ]
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    collide = not collide
                elif event.key == pygame.K_p:
                    shot_n += 1
                    name = "block_world_shot_%02d.png" % shot_n
                    pygame.image.save(screen, name)
                    print("saved", name)
                elif pygame.K_1 <= event.key < pygame.K_1 + min(9, len(VIEWPOINTS)):
                    place(room, camera, *VIEWPOINTS[event.key - pygame.K_1][1:5])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            camera.facing_angle += turn_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            camera.facing_angle -= turn_speed * dt

        # GM angles: 0 = +x, counter-clockwise, y DOWN -- so a step forward is
        # (cos, -sin), the same convention the renderer's own facing_screen_rad
        # conversion assumes.
        rad = math.radians(camera.facing_angle)
        fwd = (math.cos(rad), -math.sin(rad))
        dx = dy = 0.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dx += fwd[0]; dy += fwd[1]
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx -= fwd[0]; dy -= fwd[1]
        if keys[pygame.K_q]:
            dx += fwd[1]; dy -= fwd[0]
        if keys[pygame.K_e]:
            dx -= fwd[1]; dy += fwd[0]
        cell_of = lambda v: int((v + CELL / 2) // CELL)  # noqa: E731
        standing = ground_layer(room, cell_of(camera.x), cell_of(camera.y))
        if dx or dy:
            mag = math.hypot(dx, dy)
            step = move_speed * dt / mag
            nx, ny = camera.x + dx * step, camera.y + dy * step
            # Demo-only movement, axis-separated so sliding along a wall
            # works. The engine has no collision or footing until Phase 4.
            if not collide or _can_enter(room, cell_of(nx), cell_of(camera.y), standing):
                camera.x = nx
            if not collide or _can_enter(room, cell_of(camera.x), cell_of(ny), standing):
                camera.y = ny
            standing = ground_layer(room, cell_of(camera.x), cell_of(camera.y))

        # Climbing a step is exactly this: the layer underfoot going up by
        # one, which raises the eye and re-projects the whole view.
        block_world_state(room)["camera"]["z_layer"] = standing

        render_block_world_view(room, screen)

        cell = (cell_of(camera.x), cell_of(camera.y))
        status = "cell %s  layer %d  angle %6.1f  fps %4.1f  collision %s" % (
            cell, standing, camera.facing_angle % 360, clock.get_fps(),
            "ON" if collide else "OFF")
        for i, line in enumerate(hud_lines + [status]):
            surf = font.render(line, True, (255, 255, 255))
            shadow = font.render(line, True, (0, 0, 0))
            screen.blit(shadow, (9, 9 + i * 18))
            screen.blit(surf, (8, 8 + i * 18))
        pygame.display.flip()

    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--shots", metavar="DIR", default=None,
                        help="render the fixed VIEWPOINTS to PNGs instead of "
                             "opening a window (works headless)")
    parser.add_argument("--size", default="800x600", metavar="WxH")
    args = parser.parse_args()

    w, h = (int(part) for part in args.size.lower().split("x"))
    if args.shots:
        save_shots(args.shots, (w, h))
    else:
        walk((w, h))


if __name__ == "__main__":
    main()

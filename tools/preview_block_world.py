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

# Block heights, in layers. A step rises exactly ONE block and MAX_STEP_UP is
# one, so anything two or more is unclimbable -- that difference is the only
# thing separating a staircase from a wall in a world made of unit cubes.
# Keep every wall at 2+ or it stops being a wall and becomes a kerb.
WALL_H = 4        # perimeter -- a step is a quarter of it
CORRIDOR_H = 3    # one lower, so the terrace deck can see over it
HUT_H = 3
DISPLAY_H = 2     # the material sample rows: tall enough not to walk onto
TERRACE_Z = 5     # deck surface, reached by five one-block steps


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

    def fill(x0, y0, x1, y1, block_type, height=WALL_H):
        """Blocks from z=0 up to `height` layers tall, over a rectangle."""
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(height):
                    set_block(room, x, y, z, block_type)

    def row(x0, y, block_types, height=DISPLAY_H):
        for i, block_type in enumerate(block_types):
            for z in range(height):
                set_block(room, x0 + i, y, z, block_type)

    # Perimeter wall -- stone, so the eye has a neutral reference everywhere.
    fill(0, 0, WORLD_W - 1, 0, "stone")
    fill(0, WORLD_H - 1, WORLD_W - 1, WORLD_H - 1, "stone")
    fill(0, 0, 0, WORLD_H - 1, "stone")
    fill(WORLD_W - 1, 0, WORLD_W - 1, WORLD_H - 1, "stone")

    # A long cobble corridor: the distance test. The same texture repeats from
    # 2 cells away out past 20, so shading, fog and texel aliasing are all
    # visible in a single frame, with a brick end wall to stop the eye.
    # One block SHORTER than the perimeter, so the terrace deck (higher still)
    # can see over it -- that is the "overlook" viewpoint.
    fill(4, 9, 25, 9, "cobble", CORRIDOR_H)
    fill(4, 13, 25, 13, "cobble", CORRIDOR_H)
    fill(25, 10, 25, 12, "brick", CORRIDOR_H)

    # A brick hut in the upper yard with a doorway gap, for silhouette and
    # inside-corner reading. The doorway is a hole through the FULL height.
    fill(4, 3, 9, 3, "brick", HUT_H)
    fill(4, 7, 9, 7, "brick", HUT_H)
    fill(4, 3, 4, 7, "brick", HUT_H)
    fill(9, 3, 9, 7, "brick", HUT_H)
    for z in range(HUT_H):
        remove_block(room, 9, 5, z)

    # Isolated pillars of three different heights: corner geometry and the
    # side-shade depth cue, plus an at-a-glance height reference. All are
    # taller than one block, so none of them can be climbed.
    for x, height in ((14, 2), (17, 3), (20, 4)):
        for z in range(height):
            set_block(room, x, 5, z, "stone")

    # Lower yard, one material family per lane.
    # Shiny / transparent-flagged types. The renderer still draws these fully
    # opaque -- BLOCK_TYPES' "transparent" flag is not honoured -- though
    # alpha textures now composite with whatever stands behind them.
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
    # a pit dug into it and a tower rising off it.
    #
    # The staircase is the ONLY climbable thing in the world, and that is the
    # point: a step rises one block, every wall here is at least two, and the
    # movement rule below only allows a one-block rise. Build a wall one block
    # tall and you can simply walk up onto it, which is what a wall must not
    # let you do.
    for i in range(TERRACE_Z):  # five steps, each one block higher
        for z in range(i + 1):
            for y in (2, 3):
                set_block(room, 12 + i, y, z, "sandstone")
    # The terrace itself -- walking surface at z = TERRACE_Z, high enough to
    # look down on the corridor walls and every display row below.
    fill(17, 1, 24, 4, "cobble", TERRACE_Z)
    # A pit dug two deep into the deck. Its floor is the top face of the block
    # below, so it reads as a hole rather than a gap in the world.
    for z in (TERRACE_Z - 1, TERRACE_Z - 2):
        remove_block(room, 20, 2, z)
        remove_block(room, 20, 3, z)
    # A tower off the terrace: three more blocks above the deck.
    for z in range(TERRACE_Z + 3):
        set_block(room, 22, 2, z, "brick")


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
    # Head-on, a staircase correctly reads as a stepped wall -- each tread is
    # hidden behind the riser in front of it. Seeing the profile needs a
    # side-on view from ~10 cells back (5 stacked blocks only fit in frame at
    # that range) and this world has no clear sightline that long. Walk it
    # instead: the layer counter in the HUD ticks 0-1-2-3-4-5.
    ("steps", 2, 1, 0, 0, "2b: staircase head-on -- WALK it to feel the rises"),
    ("terrace", 23, 3, 180, 5, "2b: standing on the terrace, looking back down"),
    ("overlook", 22, 4, 270, 5, "2b: see OVER the 3-high corridor walls from up top"),
    # A level camera cannot look down, so a pit right at your feet falls
    # below the frame -- you see its far lip, not its floor. That is the
    # limitation Phase 2c (free vertical look) exists to lift, and it is
    # worth having a picture of rather than a paragraph about.
    ("pit", 23, 2, 180, 5, "2b: pit -- floor is BELOW a level camera's view"),
    ("tower", 18, 2, 0, 5, "2b: tower across the pit, three blocks above deck"),
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

# A proto-hotbar for the walkaround. Phase 3's real hotbar is an instance
# variable on the player; this is just enough selection to test building by
# hand, the same way the movement here stands in for Phase 4's footing.
HOTBAR = ["cobble", "brick", "wood_plank", "glass", "wool_red", "sandstone",
          "gold_block", "leaves"]


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
    from extensions.block_world.state import (block_world_state, set_block,
                                              remove_block, get_block,
                                              is_breakable)
    from extensions.block_world.renderer import pick_block, draw_cell_outline

    room, camera = make_room()
    view_i = 0
    place(room, camera, *VIEWPOINTS[view_i][1:5])
    collide = True
    building = False
    shot_n = 0
    slot = 0
    reach = 5
    move_speed, turn_speed = 110.0, 120.0  # px/sec, deg/sec

    # Every edit records what the cell held before it, so Ctrl+Z can put it
    # back. Building is also OFF until you ask for it -- one stray click
    # should not cost you a wall. Both are demo affordances: the engine has
    # no undo and no modes, and per docs/VOXEL_WORLD_PLAN.md it should not
    # grow modes; undo belongs to the eventual world editor.
    history = []

    def edit(cell, block_type):
        """Set (or clear, with None) a cell, remembering the old contents."""
        history.append((cell, get_block(room, *cell)))
        if block_type is None:
            remove_block(room, *cell)
        else:
            set_block(room, *cell, block_type)

    def undo():
        if not history:
            return
        cell, previous = history.pop()
        if previous is None:
            remove_block(room, *cell)
        else:
            set_block(room, *cell, previous)

    def aim():
        """What the middle of the screen is pointing at.

        Calls the same pick_block the place_block / break_block actions call,
        resolved the same way. The walkaround has no ActionExecutor to
        dispatch real actions through, so it drives the layer underneath
        them -- which is also where a picking-vs-rendering disagreement would
        show up first."""
        cfg = block_world_state(room)["camera"]
        cx, cy = room._sprite_top_left(camera)
        return pick_block(room, cx + camera._cached_width / 2,
                          cy + camera._cached_height / 2,
                          int(cfg["z_layer"]),
                          math.radians(-camera.facing_angle), CELL, reach)

    hud_lines = [
        "WASD/arrows move+turn   Q,E strafe   [ ] viewpoint (1-9 direct)",
        "B build mode   LMB break   RMB place   , . block   Ctrl+Z undo",
        "C collision   P screenshot   ESC quit",
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
                elif event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                    # Cycling reaches ALL viewpoints; the number keys only
                    # cover the first nine, and every Phase 2b viewpoint sits
                    # past that.
                    view_i = (view_i + (1 if event.key == pygame.K_RIGHTBRACKET
                                        else -1)) % len(VIEWPOINTS)
                    place(room, camera, *VIEWPOINTS[view_i][1:5])
                elif event.key == pygame.K_b:
                    building = not building
                elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                    undo()
                elif event.key in (pygame.K_COMMA, pygame.K_PERIOD):
                    slot = (slot + (1 if event.key == pygame.K_PERIOD else -1)) % len(HOTBAR)
                elif pygame.K_1 <= event.key < pygame.K_1 + min(9, len(VIEWPOINTS)):
                    view_i = event.key - pygame.K_1
                    place(room, camera, *VIEWPOINTS[view_i][1:5])
            elif event.type == pygame.MOUSEBUTTONDOWN and building:
                target, placement = aim()
                if event.button == 1 and target is not None:
                    # Mirrors break_block's own rule -- this harness calls
                    # the state API directly, so it has to honour the flag
                    # itself or the demo would contradict the engine.
                    if is_breakable(get_block(room, *target)):
                        edit(target, None)
                elif event.button == 3 and placement is not None:
                    edit(placement, HOTBAR[slot])

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

        # Crosshair, and a readout of what it is actually on -- the fastest
        # way to spot picking drifting away from what is drawn.
        target, placement = aim()
        w, h = screen.get_size()

        # Show where the next block would land, before committing to it.
        if building and placement is not None:
            cfg = block_world_state(room)["camera"]
            ccx, ccy = room._sprite_top_left(camera)
            draw_cell_outline(
                screen, placement,
                ccx + camera._cached_width / 2, ccy + camera._cached_height / 2,
                int(cfg["z_layer"]) + 0.5, math.radians(-camera.facing_angle),
                math.radians(cfg.get("fov", 66)), CELL)

        if not building:
            cross = (110, 110, 110)          # dim: clicks do nothing
        else:
            cross = (235, 235, 235) if target else (150, 150, 150)
        pygame.draw.line(screen, cross, (w // 2 - 7, h // 2), (w // 2 + 7, h // 2))
        pygame.draw.line(screen, cross, (w // 2, h // 2 - 7), (w // 2, h // 2 + 7))

        cell = (cell_of(camera.x), cell_of(camera.y))
        status = "cell %s  layer %d  angle %6.1f  fps %4.1f  collision %s" % (
            cell, standing, camera.facing_angle % 360, clock.get_fps(),
            "ON" if collide else "OFF")
        aiming = "%s   holding %s   aim %s   build %s   undo %d" % (
            "BUILD MODE" if building else "build off (B)",
            HOTBAR[slot],
            "%s,%s,%s" % target if target else "-",
            "%s,%s,%s" % placement if placement else "-",
            len(history))
        label, _cx, _cy, _fa, _cz, note = VIEWPOINTS[view_i]
        legend = "[%d/%d] %s -- %s" % (view_i + 1, len(VIEWPOINTS), label, note)
        for i, line in enumerate(hud_lines + [status, aiming, legend]):
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

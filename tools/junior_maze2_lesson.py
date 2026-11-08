"""Reference projects for the Junior-edition lesson "Treasure Maze" (90 min),
the second maze lesson (after tools/junior_maze_lesson.py).

* ``build_starter(root)``  -- what the TEACHER hands out: seven ready-made
  sprites (wall, door, gem, key, heart, bomb, goal), an ``obj_wall`` that is NOT
  yet Solid (the room's border already uses it), and an empty 960x640 room with
  its border built. Students draw the hero, create the other objects, build the
  maze, then program it.
* ``build_finished(root)`` -- the finished game (a worked example).

Mechanics (all with blocks from the Junior toolbox, see
``BlocklyConfig.JUNIOR_BLOCKS``): gems add score; a key destroys every door;
a heart adds a life; a bomb costs a life and sends the hero home; the goal wins
only when no gem is left; no lives left ends the game. Pinned by
tests/test_junior_maze2_lesson.py.

    python tools/junior_maze2_lesson.py    # writes the two zips for the wiki
"""
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from tutorial_reference_projects import Project, act  # noqa: E402

CELL = 32
COLS, ROWS = 30, 20
SPEED = 4
GEM_POINTS = 10

# W wall, D door (a vertical door is three cells), G gem, K key, H heart,
# B bomb, E goal, P hero start. Every corridor is at least TWO cells wide (the
# hero stops wherever a key is released, so it is rarely on the grid), and each
# bomb sits on a band's edge row so the hero can pass it with room to spare.
def _make_level():
    rows = [["." for _ in range(COLS)] for _ in range(ROWS)]

    def put(c, r, ch):
        rows[r][c] = ch

    for c in range(COLS):
        put(c, 0, "W")
        put(c, ROWS - 1, "W")
    for r in range(ROWS):
        put(0, r, "W")
        put(COLS - 1, r, "W")
    # Two horizontal walls, each with a two-cell gap (right, then left).
    for c in range(1, COLS - 1):
        put(c, 6, "W" if c not in (27, 28) else ".")
        put(c, 13, "W" if c not in (1, 2) else ".")
    # A door across the middle band.
    for r in range(7, 13):
        put(15, r, "D")
    for (c, r, ch) in [
        (1, 1, "P"), (15, 3, "G"), (20, 1, "B"), (28, 1, "H"),     # band A
        (22, 10, "K"), (24, 7, "B"), (8, 9, "G"), (11, 12, "B"),   # band B
        (8, 16, "G"), (20, 16, "G"), (14, 18, "B"), (28, 16, "E"),  # band C
    ]:
        put(c, r, ch)
    return ["".join(r) for r in rows]


LEVEL = _make_level()

OBJECT_FOR = {"W": "obj_wall", "D": "obj_door", "G": "obj_gem", "K": "obj_key",
              "H": "obj_heart", "B": "obj_bomb", "E": "obj_goal", "P": "obj_hero"}


# ------------------------------------------------------------------ the art

def _canvas():
    big = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    return big, ImageDraw.Draw(big)


def _finish(big):
    return big.resize((CELL, CELL), Image.LANCZOS)


def art_wall():
    im = Image.new("RGBA", (CELL, CELL), (120, 100, 80, 255))
    d = ImageDraw.Draw(im)
    for y in (0, 16):
        d.line((0, y, CELL, y), fill=(80, 65, 50, 255))
    for x, y0 in ((8, 0), (24, 0), (0, 16), (16, 16)):
        d.line((x, y0, x, y0 + 16), fill=(80, 65, 50, 255))
    d.rectangle((0, 0, CELL - 1, CELL - 1), outline=(90, 75, 60, 255))
    return im


def art_door():
    big, d = _canvas()
    d.rectangle((0, 0, 127, 127), fill=(150, 90, 40, 255))
    for x in (40, 72, 104):
        d.line((x, 0, x, 127), fill=(100, 60, 25, 255), width=4)
    d.rectangle((0, 0, 127, 127), outline=(70, 40, 15, 255), width=6)
    d.ellipse((84, 56, 108, 80), fill=(250, 210, 60, 255), outline=(150, 110, 20, 255), width=3)
    return _finish(big)


def art_gem():
    big, d = _canvas()
    d.polygon([(64, 8), (112, 44), (64, 120), (16, 44)], fill=(40, 200, 240, 255),
              outline=(10, 110, 160, 255))
    d.polygon([(64, 8), (88, 44), (64, 120), (40, 44)], fill=(130, 230, 250, 255))
    d.line((16, 44, 112, 44), fill=(10, 110, 160, 255), width=3)
    return _finish(big)


def art_key():
    big, d = _canvas()
    gold, edge = (250, 205, 40, 255), (150, 110, 10, 255)
    d.ellipse((12, 12, 62, 62), fill=gold, outline=edge, width=4)
    d.ellipse((28, 28, 46, 46), fill=(0, 0, 0, 0), outline=edge, width=4)
    d.rectangle((54, 30, 118, 44), fill=gold, outline=edge, width=3)
    d.rectangle((92, 44, 104, 66), fill=gold, outline=edge, width=3)
    d.rectangle((110, 44, 120, 60), fill=gold, outline=edge, width=3)
    return _finish(big)


def art_heart():
    big, d = _canvas()
    red, edge = (230, 40, 70, 255), (130, 10, 30, 255)
    d.ellipse((12, 18, 68, 74), fill=red, outline=edge, width=3)
    d.ellipse((60, 18, 116, 74), fill=red, outline=edge, width=3)
    d.polygon([(16, 56), (112, 56), (64, 116)], fill=red)
    d.line((16, 56, 64, 116), fill=edge, width=3)
    d.line((112, 56, 64, 116), fill=edge, width=3)
    d.ellipse((24, 28, 40, 44), fill=(255, 150, 160, 255))
    return _finish(big)


def art_bomb():
    big, d = _canvas()
    d.ellipse((16, 36, 112, 124), fill=(35, 35, 45, 255), outline=(0, 0, 0, 255), width=4)
    d.ellipse((34, 54, 52, 72), fill=(120, 120, 140, 255))
    d.rectangle((58, 22, 74, 44), fill=(90, 90, 100, 255))
    d.line((66, 22, 92, 6), fill=(190, 150, 80, 255), width=5)
    d.polygon([(92, 0), (102, 12), (112, 2), (104, 16), (116, 22), (100, 22), (96, 34), (92, 20), (80, 16), (90, 12)],
              fill=(255, 150, 20, 255))
    return _finish(big)


def art_goal():
    big, d = _canvas()
    d.rectangle((22, 6, 32, 122), fill=(200, 200, 205, 255), outline=(90, 90, 100, 255), width=3)
    d.polygon([(32, 10), (112, 36), (32, 66)], fill=(40, 200, 90, 255), outline=(10, 110, 40, 255))
    d.ellipse((14, 114, 42, 126), fill=(90, 90, 100, 255))
    return _finish(big)


ART = {"spr_wall": art_wall, "spr_door": art_door, "spr_gem": art_gem,
       "spr_key": art_key, "spr_heart": art_heart, "spr_bomb": art_bomb,
       "spr_goal": art_goal}


def _add_art(p):
    for name, make in ART.items():
        p.sprite_from_image(name, make(), CELL, CELL)


# -------------------------------------------------------------- the projects

def _wall_cells(border_only=False):
    out = []
    for r, row in enumerate(LEVEL):
        for c, ch in enumerate(row):
            if ch == "W" and (not border_only or r in (0, ROWS - 1) or c in (0, COLS - 1)):
                out.append((c, r))
    return out


def build_starter(root):
    p = Project(root, "Treasure Maze", COLS * CELL, ROWS * CELL)
    _add_art(p)
    p.obj("obj_wall", "spr_wall", solid=False)      # students tick Solid themselves
    p.room("room0", COLS * CELL, ROWS * CELL,
           [("obj_wall", c * CELL, r * CELL) for c, r in _wall_cells(border_only=True)],
           color="#202020")
    return p.save()


def _hero_events():
    arrows = {"left": ("set_hspeed", -SPEED), "right": ("set_hspeed", SPEED),
              "up": ("set_vspeed", -SPEED), "down": ("set_vspeed", SPEED)}
    return {
        "keyboard": {**{k: {"actions": [act(a, speed=v)]} for k, (a, v) in arrows.items()},
                     "nokey": {"actions": [act("stop_movement")]}},
        "collision_with_obj_wall": {"target_object": "obj_wall", "actions": [act("stop_movement")]},
        "collision_with_obj_door": {"target_object": "obj_door", "actions": [act("stop_movement")]},
        # A bomb costs a life, goes off (disappears) and sends the hero home.
        "collision_with_obj_bomb": {"target_object": "obj_bomb", "actions": [
            act("set_lives", value=-1, relative=True),
            act("destroy_instance", target="other"),
            act("stop_movement"),
            act("jump_to_start")]},
        "no_more_lives": {"actions": [act("show_message", message="Game over!"),
                                      act("restart_game")]},
    }


def build_finished(root, hero_offset=(0, 0)):
    p = Project(root, "Treasure Maze", COLS * CELL, ROWS * CELL)
    _add_art(p)
    p.sprite("spr_hero", "circle", CELL, CELL, (60, 120, 240, 255))
    p.obj("obj_wall", "spr_wall", solid=True)
    p.obj("obj_door", "spr_door", solid=True)
    p.obj("obj_gem", "spr_gem", {"collision_with_obj_hero": {"target_object": "obj_hero", "actions": [
        act("set_score", value=GEM_POINTS, relative=True), act("destroy_instance", target="self")]}})
    p.obj("obj_key", "spr_key", {"collision_with_obj_hero": {"target_object": "obj_hero", "actions": [
        act("destroy_instance", target="object", target_object="obj_door"),
        act("destroy_instance", target="self")]}})
    p.obj("obj_heart", "spr_heart", {"collision_with_obj_hero": {"target_object": "obj_hero", "actions": [
        act("set_lives", value=1, relative=True), act("destroy_instance", target="self")]}})
    p.obj("obj_bomb", "spr_bomb")
    p.obj("obj_goal", "spr_goal", {"collision_with_obj_hero": {"target_object": "obj_hero", "actions": [
        # The nested If block: "If count of obj_gem == 0, then ... else ...".
        act("if_condition", condition_type="instance_count", object_name="obj_gem",
            operator="==", value=0,
            then_actions=[act("show_message", message="You win!"), act("restart_game")],
            else_actions=[act("show_message", message="Collect every gem first!")])]}})
    p.obj("obj_hero", "spr_hero", _hero_events())
    placements = []
    for r, row in enumerate(LEVEL):
        for c, ch in enumerate(row):
            if ch in OBJECT_FOR:
                x, y = c * CELL, r * CELL
                if ch == "P":
                    x, y = x + hero_offset[0], y + hero_offset[1]
                placements.append((OBJECT_FOR[ch], x, y))
    # The hero goes last so it is drawn on top.
    placements.sort(key=lambda t: t[0] == "obj_hero")
    p.room("room0", COLS * CELL, ROWS * CELL, placements, color="#202020")
    return p.save()


def write_zips(out_dir):
    import tempfile
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, folder, builder in (
            ("Junior-Treasure-Starter", "Treasure Maze", build_starter),
            ("Junior-Treasure-Finished", "Treasure Maze (finished)", build_finished)):
        with tempfile.TemporaryDirectory() as tmp:
            builder(tmp)
            target = out_dir / f"{name}.zip"
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(Path(tmp).rglob("*")):
                    if f.is_file():
                        info = zipfile.ZipInfo(f"{folder}/{f.relative_to(tmp).as_posix()}",
                                               date_time=(2026, 1, 1, 0, 0, 0))
                        info.compress_type = zipfile.ZIP_DEFLATED
                        z.writestr(info, f.read_bytes())
            print("wrote", target)


if __name__ == "__main__":
    write_zips(ROOT / "wiki" / "downloads")

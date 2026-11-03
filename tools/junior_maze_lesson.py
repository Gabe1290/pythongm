"""Reference projects for the Junior-edition lesson "My First Maze" (90 min).

* ``build_starter(root)``  -- the project the TEACHER hands out: a wall sprite,
  a Solid ``obj_wall`` and an empty 640x416 room whose border is already walled.
  Students draw their own hero and goal sprites and do everything else.
* ``build_finished(root)`` -- what a student has at the end (a worked example).

Only actions that exist as blocks in the Junior toolbox
(``BlocklyConfig.JUNIOR_BLOCKS``) are used; tests/test_junior_maze_lesson.py
pins that, runs the finished game through the real GameRunner, and checks the
HTML5 export. Sprite art is generated (flat shapes); students draw their own.

    python tools/junior_maze_lesson.py     # writes the two zips for the wiki
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from tutorial_reference_projects import Project, act  # noqa: E402

CELL = 32
COLS, ROWS = 20, 13

# W wall, P hero start, E goal. Every corridor is TWO cells wide on purpose:
# the hero stops wherever a key is released (not on the grid), and a hero that
# is a few pixels off a one-cell corridor jams at its entrance.
def _row(inner, open_cols=()):
    """One 20-cell row: wall, ``inner`` (18 chars), wall."""
    assert len(inner) == COLS - 2, inner
    return "W" + inner + "W"


_OPEN = "." * (COLS - 2)
_SOLID = "W" * (COLS - 2)
_GAP_RIGHT = "W" * (COLS - 4) + ".."    # opening at the two right-most cells
_GAP_LEFT = ".." + "W" * (COLS - 4)      # opening at the two left-most cells

LEVEL = [
    "W" * COLS,
    _row("P" + "." * (COLS - 3)),
    _row(_OPEN),
    _row(_GAP_RIGHT),
    _row(_OPEN),
    _row(_OPEN),
    _row(_GAP_LEFT),
    _row(_OPEN),
    _row(_OPEN),
    _row(_GAP_RIGHT),
    _row("E" + "." * (COLS - 3)),
    _row(_OPEN),
    "W" * COLS,
]
assert len(LEVEL) == ROWS and all(len(r) == COLS for r in LEVEL)

SPEED = 4


def _wall_placements(level=LEVEL, border_only=False):
    out = []
    for r, row in enumerate(level):
        for c, ch in enumerate(row):
            if ch != "W":
                continue
            if border_only and not (r in (0, ROWS - 1) or c in (0, COLS - 1)):
                continue
            out.append(("obj_wall", c * CELL, r * CELL))
    return out


def _find(level, ch):
    for r, row in enumerate(level):
        for c, x in enumerate(row):
            if x == ch:
                return c, r
    raise ValueError(ch)


def _add_walls(p):
    p.sprite("spr_wall", "rect", CELL, CELL, (120, 100, 80, 255))
    p.obj("obj_wall", "spr_wall", solid=True)


def build_starter(root):
    """The teacher's starter: wall sprite + Solid wall object + bordered room."""
    p = Project(root, "My Maze", COLS * CELL, ROWS * CELL)
    _add_walls(p)
    p.room("room0", COLS * CELL, ROWS * CELL, _wall_placements(border_only=True),
           color="#202020")
    return p.save()


def build_finished(root, hero_offset=(0, 0)):
    """The finished game. ``hero_offset`` shifts the hero off the grid so a
    test can prove the two-cell corridors forgive imprecise placement."""
    p = Project(root, "My Maze", COLS * CELL, ROWS * CELL)
    _add_walls(p)
    p.sprite("spr_hero", "circle", CELL, CELL, (60, 120, 240, 255))
    p.sprite("spr_goal", "rect", CELL, CELL, (40, 200, 90, 255))
    p.obj("obj_hero", "spr_hero", {
        "keyboard": {
            "left": {"actions": [act("set_hspeed", speed=-SPEED)]},
            "right": {"actions": [act("set_hspeed", speed=SPEED)]},
            "up": {"actions": [act("set_vspeed", speed=-SPEED)]},
            "down": {"actions": [act("set_vspeed", speed=SPEED)]},
            "nokey": {"actions": [act("stop_movement")]},
        },
        "collision_with_obj_wall": {"target_object": "obj_wall",
                                    "actions": [act("stop_movement")]},
    })
    p.obj("obj_goal", "spr_goal", {
        "collision_with_obj_hero": {"target_object": "obj_hero", "actions": [
            act("show_message", message="You win!"),
            act("restart_room", transition=0)]},
    })
    hc, hr = _find(LEVEL, "P")
    gc, gr = _find(LEVEL, "E")
    placements = _wall_placements() + [
        ("obj_goal", gc * CELL, gr * CELL),
        ("obj_hero", hc * CELL + hero_offset[0], hr * CELL + hero_offset[1]),
    ]
    p.room("room0", COLS * CELL, ROWS * CELL, placements, color="#202020")
    return p.save()


def write_zips(out_dir):
    import tempfile
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # (zip name, folder students get after unzipping, builder). The starter's
    # folder is "My Maze" because the lesson sheets tell students to open it.
    for name, folder, builder in (
            ("Junior-Maze-Starter", "My Maze", build_starter),
            ("Junior-Maze-Finished", "My Maze (finished)", build_finished)):
        with tempfile.TemporaryDirectory() as tmp:
            builder(tmp)
            target = out_dir / f"{name}.zip"
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(Path(tmp).rglob("*")):
                    if f.is_file():
                        # Fixed timestamp: rebuilding must not change the zip.
                        info = zipfile.ZipInfo(
                            f"{folder}/{f.relative_to(tmp).as_posix()}",
                            date_time=(2026, 1, 1, 0, 0, 0))
                        info.compress_type = zipfile.ZIP_DEFLATED
                        z.writestr(info, f.read_bytes())
            print("wrote", target)


if __name__ == "__main__":
    write_zips(ROOT / "wiki" / "downloads")

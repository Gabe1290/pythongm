"""Kivy export: vertical motion must go the way the author meant.

Instance coordinates in a generated Kivy game are KIVY coordinates -- y up.
The exporter establishes this when it places instances: plateforme_2 authors
its player at GM y=576 in a 640-tall room and the generated scene constructs it
at y=32. So a POSITIVE vspeed moves up the screen.

Most of the exporter already knew that: `move_grid`'s direction map is
commented "Kivy Y is inverted", `set_vspeed`'s codegen negates the authored
value, and `move_to_collision` steps by +sin. The physics layer did not -- it
was copied from the desktop runtime, where y grows downward -- so:

* gravity_direction 270 ("down") produced a positive vspeed and pulled
  everything UP the screen. That is plateforme_2's "Pingus rises" (issue 7);
* every direction-driven vertical move was inverted, so an up arrow moved the
  player down (part of the "erratic keys" reports);
* `if_collision`'s y offset was passed through unflipped, so a platformer
  asking "is there ground 1px below me?" asked about the ceiling instead and
  the jump never found the floor.

These assert SCREEN DIRECTION, not stored values. A previous test of mine
asserted that the up arrow yields `direction = 90` and passed happily while the
player moved downward -- the value was right and the motion was inverted, which
is exactly the gap this file closes.
"""
import json
import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

UP, DOWN, STILL = "up", "down", "still"


def _merged(sample: Path) -> dict:
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    assets = data.get("assets", {})
    for kind in ("rooms", "objects"):
        for name, entry in assets.get(kind, {}).items():
            side = sample / kind / ("%s.json" % name)
            if side.exists():
                entry.update(json.loads(side.read_text(encoding="utf-8")))
    return data


class _Stub:
    def __init__(self, *a, **k):
        self.args, self.kw = a, k


class _Group(_Stub):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.children = []

    def add(self, c):
        self.children.append(c)

    def remove(self, c):
        if c in self.children:
            self.children.remove(c)

    def clear(self):
        self.children = []


class _Widget:
    def __init__(self, **kwargs):
        pass

    def add_widget(self, *a, **k):
        pass


@pytest.fixture(scope="module")
def game_object():
    sample = REPO_ROOT / "samples" / "plateforme_2"
    out = Path(tempfile.mkdtemp(prefix="kivy_vert_"))
    assert KivyExporter(_merged(sample), sample, out).export()

    source = (out / "game" / "objects" / "base_object.py").read_text(
        encoding="utf-8")
    compile(source, "base_object.py", "exec")

    module = types.ModuleType("generated_base_object_vert")
    module.__dict__.update({
        "Widget": _Widget, "Rectangle": _Stub, "Color": _Stub, "Line": _Stub,
        "Ellipse": _Stub, "InstructionGroup": _Group, "PushMatrix": _Stub,
        "PopMatrix": _Stub, "Label": object,
        "Window": types.SimpleNamespace(size=(800, 600)),
        "load_image": lambda *a, **k: None,
        "SPRITE_PATHS": {}, "SOUND_PATHS": {}, "BACKGROUND_PATHS": {},
        "get_game_app": lambda: None, "_ScriptGameProxy": object,
        "math": __import__("math"), "random": __import__("random"),
    })
    stripped = "\n".join(line for line in source.splitlines()
                         if not line.startswith(("from ", "import ")))
    exec(stripped, module.__dict__)  # noqa: S102 - our own generated code
    return next(v for v in module.__dict__.values()
                if isinstance(v, type) and v.__name__ == "GameObject")


class _Scene:
    def __init__(self):
        self.instances = []
        self.room_width = self.room_height = 640
        self.room_speed = 60.0

    @staticmethod
    def _class_name_to_snake_case(name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _instance(cls, scene, x=100, y=300):
    made = type("ObjThing", (cls,), {})
    instance = made.__new__(made)
    instance.__dict__.update({
        "_x": float(x), "_y": float(y),
        "_hspeed": 0.0, "_vspeed": 0.0, "_speed": 0.0, "_direction": 0.0,
        "_gravity": 0.0, "_gravity_direction": 270.0, "_friction": 0.0,
        "solid": False, "scene": scene, "has_sprite": True, "size": (32, 32),
        "visible": True, "_destroyed": False, "grid_size": 32,
        "_sprite_frames": 1, "image_index": 0, "image_speed": 0,
        "rect": _Stub(), "pos": (float(x), float(y)),
    })
    scene.instances.append(instance)
    return instance


def _screen_motion(cls, setup, frames=3):
    """Which way the instance moves ON SCREEN. y up, so +dy is upward."""
    scene = _Scene()
    instance = _instance(cls, scene)
    setup(instance)
    start = instance.y
    for _ in range(frames):
        instance._process_movement(1 / 60.0)
    delta = instance.y - start
    if delta > 1e-9:
        return UP
    if delta < -1e-9:
        return DOWN
    return STILL


# --- the convention itself -------------------------------------------------

def test_positive_vspeed_moves_up(game_object):
    """States the convention this file rests on, so a future reader does not
    have to re-derive it."""
    assert _screen_motion(game_object, lambda i: setattr(i, "vspeed", 4)) == UP
    assert _screen_motion(game_object, lambda i: setattr(i, "vspeed", -4)) == DOWN


def test_instances_are_placed_in_kivy_coordinates():
    """Where the convention comes from. plateforme_2 authors its player near
    the BOTTOM of the room (GM y=576 of 640); the generated scene must place it
    at a small y, because Kivy measures up from the bottom."""
    sample = REPO_ROOT / "samples" / "plateforme_2"
    data = _merged(sample)
    room = next(iter(data["assets"]["rooms"].values()))
    authored = next(i for i in room["instances"]
                    if "personnage" in str(i.get("object_name", "")))
    assert authored["y"] > room["height"] * 0.8, "expected a low-on-screen spawn"

    out = Path(tempfile.mkdtemp(prefix="kivy_vert_coords_"))
    assert KivyExporter(data, sample, out).export()
    scene = next(p for p in (out / "game" / "scenes").glob("*.py")
                 if p.stem != "__init__").read_text(encoding="utf-8")
    line = next(l for l in scene.splitlines() if "Personnage(self," in l)
    generated_y = int(line.rsplit(",", 1)[1].strip().rstrip(")"))
    assert generated_y < room["height"] * 0.2, (
        "instance y should be flipped into Kivy space, got %s" % generated_y)


# --- gravity ---------------------------------------------------------------

def test_gravity_pulls_down(game_object):
    """The headline of issue 7: Pingus rose instead of falling. 270 is
    GameMaker's "down"."""
    motion = _screen_motion(game_object, lambda i: (
        setattr(i, "gravity", 0.45), setattr(i, "gravity_direction", 270)))
    assert motion == DOWN, "gravity_direction 270 must pull DOWN the screen"


def test_upward_gravity_still_works(game_object):
    """The sign must be a real conversion, not a hardcoded downward push."""
    motion = _screen_motion(game_object, lambda i: (
        setattr(i, "gravity", 0.45), setattr(i, "gravity_direction", 90)))
    assert motion == UP


def test_sideways_gravity_does_not_move_vertically(game_object):
    motion = _screen_motion(game_object, lambda i: (
        setattr(i, "gravity", 0.45), setattr(i, "gravity_direction", 0)))
    assert motion == STILL


def test_the_samples_authored_gravity_falls(game_object):
    """Exactly what plateforme_2 and plateforme_3 author."""
    for strength in (0.45, 0.5):
        motion = _screen_motion(game_object, lambda i, s=strength: (
            setattr(i, "gravity", s), setattr(i, "gravity_direction", 270)))
        assert motion == DOWN, strength


# --- speed/direction -------------------------------------------------------

@pytest.mark.parametrize("degrees,expected", [
    (90, UP),      # GameMaker's "up"
    (270, DOWN),   # GameMaker's "down"
    (0, STILL),    # right: no vertical component
    (180, STILL),  # left
])
def test_direction_moves_the_authored_way(game_object, degrees, expected):
    """`direction` keeps GameMaker's values, so 90 must move UP on screen. It
    moved down, which inverted every vertical arrow in every sample."""
    motion = _screen_motion(game_object, lambda i: (
        setattr(i, "direction", degrees), setattr(i, "speed", 4)))
    assert motion == expected


def test_the_arrow_keys_move_the_way_they_are_labelled(game_object):
    """End to end on the arrows: maze_1 authors them as start_moving_direction
    with a name, whose codegen yields these degrees."""
    generator = ActionCodeGenerator()
    for name, expected in (("up", UP), ("down", DOWN)):
        code = generator._convert_simple_action(
            "start_moving_direction", {"directions": name, "speed": "4"},
            "keyboard")
        degrees = int(code.split("self.direction = ")[1].split(";")[0])
        motion = _screen_motion(game_object, lambda i, d=degrees: (
            setattr(i, "direction", d), setattr(i, "speed", 4)))
        assert motion == expected, "'%s' generated %d and moved %s" % (
            name, degrees, motion)


def test_speed_and_direction_round_trip(game_object):
    """Setting vspeed updates direction and vice versa (GM 7.0 keeps them in
    step). Both syncs must use the same convention, or reading direction back
    after setting vspeed reports the opposite heading."""
    scene = _Scene()
    instance = _instance(game_object, scene)

    instance.vspeed = 4          # upward
    assert 45 < instance.direction < 135, (
        "an upward vspeed should read back as an upward direction, got %s"
        % instance.direction)

    instance.vspeed = -4         # downward
    assert 225 < (instance.direction % 360) < 315, (
        "a downward vspeed should read back as a downward direction, got %s"
        % instance.direction)


# --- collision offsets ----------------------------------------------------

def test_a_ground_probe_looks_below():
    """`if_collision` with y=1 means "1 pixel below me" to the author. Passed
    through unflipped it asked about the ceiling, so a platformer's jump could
    never find the floor."""
    generator = ActionCodeGenerator()
    generator.process_action(
        {"action": "if_collision",
         "parameters": {"x": "0", "y": "1", "object": "solid"}}, "keyboard")
    code = generator.get_code()
    assert "self.y - (1)" in code, code
    assert "self.y + (1)" not in code


def test_an_upward_probe_looks_above():
    generator = ActionCodeGenerator()
    generator.process_action(
        {"action": "if_collision",
         "parameters": {"x": "0", "y": "-8", "object": "solid"}}, "keyboard")
    assert "self.y - (-8)" in generator.get_code()


def test_the_horizontal_offset_is_untouched():
    """Only y flips. Flipping x too would be a new bug."""
    generator = ActionCodeGenerator()
    generator.process_action(
        {"action": "if_collision",
         "parameters": {"x": "4", "y": "0", "object": "solid"}}, "keyboard")
    assert "self.x + (4)" in generator.get_code()


def test_relative_check_empty_flips_too():
    generator = ActionCodeGenerator()
    generator.process_action(
        {"action": "check_empty",
         "parameters": {"x": "0", "y": "1", "relative": True}}, "keyboard")
    assert "self.y - (1)" in generator.get_code()


def test_the_platformers_own_ground_probe_is_generated_correctly():
    """Against the real sample rather than a hand-built action."""
    sample = REPO_ROOT / "samples" / "plateforme_2"
    out = Path(tempfile.mkdtemp(prefix="kivy_vert_probe_"))
    assert KivyExporter(_merged(sample), sample, out).export()

    source = (out / "game" / "objects" / "obj_personnage.py").read_text(
        encoding="utf-8")
    compile(source, "obj_personnage.py", "exec")
    assert "check_collision_at" in source, "the jump should probe for ground"
    assert "self.y + (1)" not in source, (
        "a downward probe must not be written as +1 in Kivy space")


# --- the generated files stay valid ---------------------------------------

def test_every_platformer_still_generates_compiling_code():
    for name in ("plateforme_1", "plateforme_2", "plateforme_3"):
        sample = REPO_ROOT / "samples" / name
        out = Path(tempfile.mkdtemp(prefix="kivy_vert_%s_" % name))
        assert KivyExporter(_merged(sample), sample, out).export()
        for path in (out / "game").rglob("*.py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")

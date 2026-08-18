"""Kivy export: solid objects must actually block movement.

`GameObject._process_movement` only blocked a move when the MOVING instance was
solid. A player is normally not solid and the walls are, so nothing ever blocked
a player: it walked straight through the level. That is issue 4 of the
2026-08-16 pass (raycast_4 has no wall collision) and half of issue 7
(plateforme_2's Pingus flies off screen).

The fix is deliberately larger than that one condition, and this file exists to
pin the reason. Kivy reverted BOTH axes on a collision; the desktop engine
resolves each axis independently and, on a blocked vertical move, slides
pixel-by-pixel until flush against the blocker. Both differences are
load-bearing:

* gravity pushes an instance into the floor every frame, so a both-axes revert
  cancels horizontal movement too and the player cannot walk -- trading "falls
  through the floor" for "cannot move";
* all-or-nothing vertical movement leaves a fast faller up to |vspeed| px above
  the floor, past the 1px ground probe platformers use, so the character hangs
  in mid-air with its walk animation still cycling.

So the tests below cover walking along the ground and landing flush, not just
"a wall blocks" -- a suite that only checked blocking would pass while the game
was unplayable.

Kivy cannot run in CI, so these execute the real generated base object under
stub kivy modules (the tests/test_kivy_raycast.py harness pattern).
"""
import json
import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402


def _merged(sample: Path) -> dict:
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    assets = data.get("assets", {})
    for kind in ("rooms", "objects"):
        for name, entry in assets.get(kind, {}).items():
            side = sample / kind / ("%s.json" % name)
            if side.exists():
                entry.update(json.loads(side.read_text(encoding="utf-8")))
    return data


@pytest.fixture(scope="module")
def base_object_class():
    """The real generated GameObject, exec'd with kivy stubbed out."""
    sample = REPO_ROOT / "samples" / "maze_1"
    out = Path(tempfile.mkdtemp(prefix="kivy_collide_"))
    assert KivyExporter(_merged(sample), sample, out).export()

    source = (out / "game" / "objects" / "base_object.py").read_text(
        encoding="utf-8")
    compile(source, "base_object.py", "exec")

    module = types.ModuleType("generated_base_object")
    module.__dict__.update({
        "Widget": _StubWidget,
        "Rectangle": _StubInstr, "Color": _StubInstr, "Line": _StubInstr,
        "Ellipse": _StubInstr, "InstructionGroup": _StubGroup,
        "PushMatrix": _StubInstr, "PopMatrix": _StubInstr,
        "Label": object, "Window": types.SimpleNamespace(size=(800, 600)),
        "load_image": lambda *_a, **_k: None,
        "SPRITE_PATHS": {}, "SOUND_PATHS": {}, "BACKGROUND_PATHS": {},
        "get_game_app": lambda: None, "_ScriptGameProxy": object,
    })
    stripped = "\n".join(line for line in source.splitlines()
                         if not line.startswith(("from ", "import ")))
    exec(stripped, module.__dict__)  # noqa: S102 - our own generated code

    return next(v for v in module.__dict__.values()
                if isinstance(v, type) and v.__name__ == "GameObject")


class _StubWidget:
    def __init__(self, **kwargs):
        pass

    def add_widget(self, *a, **k):
        pass


class _StubInstr:
    def __init__(self, *a, **k):
        self.args, self.kw = a, k


class _StubGroup(_StubInstr):
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


class _Scene:
    """Just enough scene for the movement code: an instance list and the
    snake-case helper the collision-event lookup goes through."""

    def __init__(self):
        self.instances = []
        self.room_width = self.room_height = 640
        self.room_speed = 60.0

    @staticmethod
    def _class_name_to_snake_case(name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _actor(cls, scene, name, x, y, *, w=32, h=32, solid=False,
           collides_with=()):
    """A live instance of a subclass named `name`.

    `collides_with` lists snake_case type names this object handles a collision
    with -- the second half of GameMaker's blocking rule, which needs a
    collision event to exist between the pair.
    """
    made = type(name, (cls,), {})
    instance = made.__new__(made)
    instance.__dict__.update({
        "_x": float(x), "_y": float(y),
        "_hspeed": 0.0, "_vspeed": 0.0, "_speed": 0.0, "_direction": 0.0,
        "_gravity": 0.0, "_gravity_direction": 270.0, "_friction": 0.0,
        "solid": solid, "scene": scene, "has_sprite": True,
        "size": (w, h), "visible": True, "_destroyed": False,
        "grid_size": 32, "collisions_fired": [],
        # _process_movement advances the sprite animation first. _sprite_frames
        # is a frame COUNT, not a list, and a count of 1 makes the advance an
        # early return without having to stub the method out.
        "_sprite_frames": 1, "image_index": 0, "image_speed": 0,
        # _update_position writes the canvas rectangle's pos/size.
        "rect": _StubInstr(), "pos": (float(x), float(y)),
    })
    for target in collides_with:
        def handler(other, _self=instance, _t=target):
            _self.collisions_fired.append(_t)
        setattr(instance, "on_collision_" + target, handler)
    scene.instances.append(instance)
    return instance


def _world(cls):
    scene = _Scene()
    return scene


# --- the blocking rule -----------------------------------------------------

def test_a_non_solid_player_is_blocked_by_a_solid_wall(base_object_class):
    """The bug. The player is not solid; the wall is. Requiring the MOVING
    instance to be solid meant nothing ever stopped a player."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    _actor(base_object_class, scene, "ObjWall", 32, 0, solid=True)

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.x == 0, (
        "the player walked into the wall (x=%s); solid must block" % player.x)


def test_the_player_still_moves_where_nothing_blocks(base_object_class):
    """The other half: blocking must not freeze ordinary movement."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    _actor(base_object_class, scene, "ObjWall", 320, 0, solid=True)

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.x == 32


def test_two_non_solid_objects_do_not_block_each_other(base_object_class):
    """GameMaker fires their collision events after the move instead. This is
    how a maze monster runs through the player rather than standing on it."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_monster",))
    _actor(base_object_class, scene, "ObjMonster", 32, 0, solid=False)

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.x == 32, "non-solid pairs must overlap freely"


def test_a_solid_wall_with_no_collision_event_does_not_block(base_object_class):
    """The rule needs BOTH halves. GameMaker requires a collision event between
    the two types as well as one of them being solid."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0)  # no handler
    _actor(base_object_class, scene, "ObjWall", 32, 0, solid=True)

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.x == 32


def test_the_event_may_be_declared_on_either_object(base_object_class):
    """"in EITHER direction" -- the wall may be the one that handles it."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0)
    _actor(base_object_class, scene, "ObjWall", 32, 0, solid=True,
           collides_with=("obj_person",))

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.x == 0


def test_a_destroyed_instance_does_not_block(base_object_class):
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    wall = _actor(base_object_class, scene, "ObjWall", 32, 0, solid=True)
    wall._destroyed = True

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.x == 32


# --- per-axis resolution: the reason the one-line fix was wrong ------------

def test_a_walking_player_is_not_frozen_by_the_floor(base_object_class):
    """THE test that makes this fix safe.

    A platformer applies downward speed every frame, so the player is always
    pushing into the floor. Reverting both axes on that collision would cancel
    the horizontal move too and the player could not walk at all -- which would
    have traded "falls through the floor" for "cannot move" and passed a suite
    that only checked blocking.
    """
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 64,
                    collides_with=("obj_ground",))
    # Ground directly below the player's feet (GM y grows downward).
    _actor(base_object_class, scene, "ObjGround", 0, 96, w=320, h=32,
           solid=True)

    player._hspeed = 4.0
    player._vspeed = 8.0      # gravity pressing into the ground
    player._process_movement(1 / 60.0)

    assert player.x == 4, (
        "the player must still walk while resting on the ground (x=%s)"
        % player.x)
    assert player.y == 64, "the player must not sink into the ground"


def test_a_falling_player_lands_flush_on_the_floor(base_object_class):
    """All-or-nothing vertical movement left a fast faller up to |vspeed| px
    above the floor -- past the 1px ground probe platformers use, so the
    character hung in mid-air with its animation still cycling."""
    scene = _world(base_object_class)
    # 32px tall, ground top at y=96, so resting position is y=64. Starting at
    # 50 with a 24px fall would land at 74 -- 10px INSIDE the ground -- which
    # is exactly the case all-or-nothing movement cancelled outright, leaving
    # the player hanging 14px up.
    player = _actor(base_object_class, scene, "ObjPerson", 0, 50,
                    collides_with=("obj_ground",))
    _actor(base_object_class, scene, "ObjGround", 0, 96, w=320, h=32,
           solid=True)

    player._vspeed = 24.0     # terminal velocity: most of a tile per frame
    player._process_movement(1 / 60.0)

    assert player.y == 64, (
        "the player should come to rest flush on the ground (y=64), got %s"
        % player.y)
    assert player.y + player.size[1] == 96, "feet should touch the ground"


def test_the_faller_stops_short_rather_than_overlapping(base_object_class):
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_ground",))
    ground = _actor(base_object_class, scene, "ObjGround", 0, 96, w=320, h=32,
                    solid=True)

    player._vspeed = 100.0
    player._process_movement(1 / 60.0)

    assert player.y + player.size[1] <= ground.y, (
        "the player overlapped the ground: y=%s" % player.y)


def test_a_blocked_axis_does_not_stop_the_free_one(base_object_class):
    """Vertical blocked, horizontal clear: the horizontal move must still
    happen. This is what per-axis resolution buys."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 64,
                    collides_with=("obj_ground",))
    _actor(base_object_class, scene, "ObjGround", 0, 96, w=640, h=32,
           solid=True)

    player._hspeed = 10.0
    player._vspeed = 40.0
    player._process_movement(1 / 60.0)

    assert player.x == 10
    assert player.y == 64


# --- the collision event still fires when a move is blocked ---------------

def test_a_blocked_move_fires_the_collision_handler(base_object_class):
    """Blocking prevents the overlap, so the post-move detection pass never
    sees the pair. Without firing here, plateforme_2's authored
    move_to_contact + set_hspeed(0) would never run and the player would sit
    against the wall with its speed still set."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    _actor(base_object_class, scene, "ObjWall", 32, 0, solid=True)

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.collisions_fired == ["obj_wall"], player.collisions_fired


def test_the_walls_own_handler_also_fires(base_object_class):
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    wall = _actor(base_object_class, scene, "ObjWall", 32, 0, solid=True,
                  collides_with=("obj_person",))

    player._hspeed = 32.0
    player._process_movement(1 / 60.0)

    assert wall.collisions_fired == ["obj_person"], wall.collisions_fired


def test_both_axes_blocked_by_one_wall_fires_the_handler_once(base_object_class):
    """Both axes blocked against the SAME instance must run the handler once.
    The desktop engine keys its blocked-collisions map by instance for this.

    Reaching that state needs a deliberately awkward setup, and the geometry is
    worth recording. For a single AABB, "moving on x alone overlaps AND moving
    on y alone overlaps" implies the two rectangles ALREADY overlap where they
    start -- each single-axis test requires the other axis's projections to
    overlap at the current position. So an instance that begins cleanly
    separated can only ever be blocked on one axis by any one wall, and two
    blockers means two different walls (which should fire twice -- next test).

    Hence the overlapping start below. The deduplication is therefore defensive
    rather than routine, which is worth knowing before anyone deletes it.
    """
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    _actor(base_object_class, scene, "ObjWall", 20, 20, w=64, h=64, solid=True)

    player._hspeed = 32.0
    player._vspeed = 32.0
    player._process_movement(1 / 60.0)

    assert player.collisions_fired.count("obj_wall") == 1, (
        "handler ran %d times" % player.collisions_fired.count("obj_wall"))


def test_two_different_walls_each_fire(base_object_class):
    """The flip side: distinct blockers are distinct collisions, so each one's
    handler runs. Deduplication must not collapse them."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 32, 32,
                    collides_with=("obj_wall", "obj_ground"))
    _actor(base_object_class, scene, "ObjWall", 64, 32, solid=True)
    _actor(base_object_class, scene, "ObjGround", 32, 64, solid=True)

    player._hspeed = 32.0
    player._vspeed = 32.0
    player._process_movement(1 / 60.0)

    assert sorted(player.collisions_fired) == ["obj_ground", "obj_wall"], (
        player.collisions_fired)


def test_an_unblocked_move_fires_nothing(base_object_class):
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0,
                    collides_with=("obj_wall",))
    _actor(base_object_class, scene, "ObjWall", 320, 0, solid=True)

    player._hspeed = 4.0
    player._process_movement(1 / 60.0)

    assert player.collisions_fired == []


def test_movement_without_a_scene_is_still_applied(base_object_class):
    """An instance not yet added to a scene must still move rather than raise."""
    scene = _world(base_object_class)
    player = _actor(base_object_class, scene, "ObjPerson", 0, 0)
    scene.instances.remove(player)
    player.scene = None

    player._hspeed = 5.0
    player._process_movement(1 / 60.0)

    assert player.x == 5


# --- the generated file is still valid -----------------------------------

def test_every_sample_still_generates_a_compiling_base_object():
    """The base object is a .format() template, so a stray brace in the added
    code breaks every export at once."""
    for name in ("maze_1", "plateforme_2", "raycast_4"):
        sample = REPO_ROOT / "samples" / name
        out = Path(tempfile.mkdtemp(prefix="kivy_collide_%s_" % name))
        assert KivyExporter(_merged(sample), sample, out).export()
        path = out / "game" / "objects" / "base_object.py"
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

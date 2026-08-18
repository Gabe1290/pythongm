"""Kivy export: held keyboard events must fire every frame, and anykey at all.

GameMaker's `keyboard` event fires on EVERY FRAME the key is down -- that is
what `runtime/game_runner.py::_process_held_keys` does. The Kivy exporter bound
those actions to Window's `on_key_down` instead, which fires once per press plus
the OS auto-repeat, so a maze player moved in stuttering bursts at the keyboard
repeat rate rather than continuously (issue 5 of the 2026-08-16 pass).

Two further bugs surfaced while fixing it, both silent:

* `keyboard` (held) and `keyboard_press` (one-shot) BOTH generated a method
  called `on_keyboard`, so an object with one of each had the second definition
  shadow the first. maze_3's and maze_4's `controller_main` are exactly that
  shape.
* `anykey` fell through `key_map.get(name, '0')` and compiled to `if key == 0:`,
  which no real keycode matches. maze_4's start screen advances on
  `anykey -> next_room`, so the exported game drew its background and no key
  would start it -- issue 6, reported as "won't start on space".

Kivy cannot run in CI, so these execute the real generated handlers under stub
kivy modules, following the tests/test_kivy_raycast.py harness pattern.
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN = 275, 276, 273, 274


def _merged(sample: Path) -> dict:
    """project.json with rooms/ and objects/ side files merged, as the real
    exporters do -- the events live in the side files."""
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    assets = data.get("assets", {})
    for kind in ("rooms", "objects"):
        for name, entry in assets.get(kind, {}).items():
            side = sample / kind / ("%s.json" % name)
            if side.exists():
                entry.update(json.loads(side.read_text(encoding="utf-8")))
    return data


def _export(sample_name: str) -> Path:
    sample = REPO_ROOT / "samples" / sample_name
    out = Path(tempfile.mkdtemp(prefix="kivy_kb_%s_" % sample_name))
    assert KivyExporter(_merged(sample), sample, out).export()
    return out / "game"


@pytest.fixture(scope="module")
def maze_1():
    return _export("maze_1")


@pytest.fixture(scope="module")
def maze_4():
    return _export("maze_4")


@pytest.fixture(scope="module")
def maze_3():
    """maze_3's controller_main is the object that has BOTH a held `keyboard`
    event and a `keyboard_press` group -- maze_4's has only the held one."""
    return _export("maze_3")


def _object_source(game_dir: Path, stem: str) -> str:
    path = game_dir / "objects" / ("%s.py" % stem)
    assert path.exists(), "%s was not exported" % stem
    return path.read_text(encoding="utf-8")


def _methods(source: str):
    """Method names defined in a generated object module."""
    import ast

    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ClassDef):
            found += [n.name for n in node.body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return found


# --- the held handler is separate from the one-shot one -------------------

def test_held_keyboard_generates_its_own_method(maze_1):
    """It must not be called on_keyboard: that name belongs to the one-shot
    press handler, and the scene calls the two at different times."""
    methods = _methods(_object_source(maze_1, "obj_person"))
    assert "on_keyboard_held" in methods
    assert "on_keyboard" not in methods


def test_held_and_press_events_no_longer_shadow_each_other(maze_3):
    """maze_3's controller_main has a held `keyboard` event AND a
    `keyboard_press` group. Both used to generate `def on_keyboard`, so
    whichever came second silently replaced the other."""
    methods = _methods(_object_source(maze_3, "controller_main"))
    assert "on_keyboard_held" in methods, methods
    assert "on_keyboard" in methods, methods
    assert methods.count("on_keyboard") == 1, (
        "two definitions of the same method: one is dead")
    assert methods.count("on_keyboard_held") == 1


def test_generated_objects_still_compile(maze_1, maze_4):
    for game_dir in (maze_1, maze_4):
        for path in (game_dir / "objects").glob("*.py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")


# --- anykey ----------------------------------------------------------------

def test_anykey_generates_a_real_handler(maze_4):
    """The bug behind issue 6: anykey compiled to `if key == 0:`."""
    source = _object_source(maze_4, "controller_start")
    assert "on_keyboard_anykey" in _methods(source)
    assert "key == 0" not in source, (
        "anykey must not compile to a keycode comparison; no key is 0")


def test_maze_4_start_screen_can_advance(maze_4):
    """End to end on the reported symptom: the start room's controller must
    carry the action that moves to the next room."""
    source = _object_source(maze_4, "controller_start")
    body = source.split("def on_keyboard_anykey")[1]
    assert "goto_next_room" in body, body[:400]


def test_anykey_only_object_gets_no_empty_held_handler(maze_4):
    """controller_start listens on anykey alone. An empty on_keyboard_held
    would be invoked once per held key per frame to do nothing."""
    methods = _methods(_object_source(maze_4, "controller_start"))
    assert "on_keyboard_held" not in methods, methods


# --- the scene dispatches them every frame -------------------------------

def _names_looked_up_in(source: str, *methods: str):
    """Handler names the given methods actually resolve, by parsing them.

    Not a substring search on the method's text. A first draft asserted
    `"on_keyboard_held" in update`, and a mutation that deleted the dispatch
    still passed, because the name appeared in the explanatory comment right
    above it. Only the AST distinguishes code from prose.

    Several method names are accepted because the per-frame path is split: the
    Clock calls `update`, which delegates to `_update_impl` inside a try. A
    text search on "def update(" happened to cover both by reading to the end
    of the file, which is another reason it was not really testing anything.
    """
    import ast

    tree = ast.parse(source)
    targets = [node for node in ast.walk(tree)
               if isinstance(node, ast.FunctionDef) and node.name in methods]
    assert targets, "none of %r in the generated scene" % (methods,)

    names = set()
    for target in targets:
        for node in ast.walk(target):
            # getattr(instance, 'on_keyboard_held', None)
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ("getattr", "hasattr")
                    and len(node.args) >= 2
                    and isinstance(node.args[1], ast.Constant)
                    and isinstance(node.args[1].value, str)):
                names.add(node.args[1].value)
            # instance.on_keyboard_held(key)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
    return names


def test_the_scene_dispatches_held_keys_every_frame(maze_1):
    """The whole point. Held keys must be dispatched from the per-frame
    update, not from the window's key-down event."""
    scene = next(f for f in (maze_1 / "scenes").glob("*.py")
                 if f.stem != "__init__").read_text(encoding="utf-8")

    in_update = _names_looked_up_in(scene, "update", "_update_impl")
    assert "on_keyboard_held" in in_update, (
        "update() must dispatch held keys, and must do so in code rather than "
        "only mention it: %r" % sorted(n for n in in_update if "key" in n))
    assert "on_keyboard_anykey" in in_update

    # ...and NOT from on_keyboard, which is the key-down event.
    in_keydown = _names_looked_up_in(scene, "on_keyboard")
    assert "on_keyboard_held" not in in_keydown, (
        "key-down must not fire held events: that reintroduces the OS "
        "auto-repeat behaviour this fixes")


def test_held_dispatch_is_skipped_when_no_key_is_down(maze_1):
    """nokey and held are mutually exclusive, as on the desktop."""
    scene = next(f for f in (maze_1 / "scenes").glob("*.py")
                 if f.stem != "__init__").read_text(encoding="utf-8")
    update = scene.split("def update(")[1]
    nokey_at = update.index("on_nokey")
    held_at = update.index("on_keyboard_held")
    between = update[nokey_at:held_at]
    assert "else:" in between, (
        "the held dispatch should sit in the else of the `not keys_pressed` "
        "check, so it cannot run on a frame with no keys down")


def test_scene_update_compiles(maze_1):
    for path in (maze_1 / "scenes").glob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


# --- executing the generated handler -------------------------------------

def test_the_held_handler_acts_on_the_key_it_is_given(maze_1):
    """Execute the generated method for real: pressing Right must run the
    Right branch and nothing else."""
    source = _object_source(maze_1, "obj_person")
    body = source.split("def on_keyboard_held(self, key):")[1].split("\n    def ")[0]

    # Each authored direction should appear as its own keycode comparison.
    for code in (KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN):
        assert ("key == %d" % code) in body, (
            "keycode %d missing from the held handler:\n%s" % (code, body))

    # And they must be distinct branches, not one block that runs for any key.
    assert body.count("elif key ==") == 3, body


EXPECTED_DIRECTION = {KEY_RIGHT: 0, KEY_UP: 90, KEY_LEFT: 180, KEY_DOWN: 270}


@pytest.mark.parametrize("key,degrees", sorted(EXPECTED_DIRECTION.items()))
def test_each_arrow_moves_its_own_way(maze_1, key, degrees):
    """The core of issue 5, executed rather than inspected.

    maze_1 authors each arrow as `start_moving_direction` with a direction NAME
    ("right", "up", ...). The Kivy generator treated that string as a list of
    directions, so it iterated the characters -- "right" became five
    unrecognised names, each defaulting to 0. Every arrow key therefore set
    direction 0 and the player only ever moved right, until a wall, and then
    appeared stuck.

    This checks the direction VALUE only. The stored value being right does not
    mean the motion is: when this test was written the export also inverted
    every vertical move, so direction 90 dutifully moved the player DOWN and
    this test passed anyway. Instance coordinates here are KIVY coordinates
    (y up), not GameMaker's -- see tests/test_kivy_vertical_convention.py,
    which asserts the resulting screen direction.
    """
    cls = _load_object_namespace(maze_1, "obj_person")["cls"]
    instance = cls.__new__(cls)
    _stub_instance(instance)

    instance.on_keyboard_held(key)

    assert instance.speed == 4, "the key set no speed"
    assert instance.direction == degrees, (
        "keycode %d should move at %d degrees, got %s"
        % (key, degrees, instance.direction))


def test_the_four_arrows_do_not_all_go_the_same_way(maze_1):
    """States the bug directly, so a regression to per-character iteration
    cannot pass by coincidence."""
    cls = _load_object_namespace(maze_1, "obj_person")["cls"]

    seen = {}
    for key in EXPECTED_DIRECTION:
        instance = cls.__new__(cls)
        _stub_instance(instance)
        instance.on_keyboard_held(key)
        seen[key] = instance.direction

    assert len(set(seen.values())) == 4, (
        "all four arrows produced %r -- the directions collapsed again"
        % (seen,))


def test_the_held_handler_can_run_every_frame(maze_1):
    """It is called once per held key per frame now, so it must be safe to
    call repeatedly and stay stable rather than accumulating."""
    cls = _load_object_namespace(maze_1, "obj_person")["cls"]
    instance = cls.__new__(cls)
    _stub_instance(instance)

    for _frame in range(5):
        instance.on_keyboard_held(KEY_UP)

    assert instance.direction == 90
    assert instance.speed == 4


def test_an_unbound_key_does_nothing(maze_1):
    """A key with no authored event must leave the instance alone -- the held
    dispatch offers every held key to every instance."""
    cls = _load_object_namespace(maze_1, "obj_person")["cls"]
    instance = cls.__new__(cls)
    _stub_instance(instance)

    instance.on_keyboard_held(ord("q"))

    assert instance.speed == 0
    assert instance.direction == 0


# --- the direction parameter, at the unit level ---------------------------

@pytest.mark.parametrize("directions,expected", [
    # A single name as a plain string: the samples' and GMK's shape, and the
    # one that broke.
    ("right", "self.direction = 0; self.speed = 4"),
    ("up", "self.direction = 90; self.speed = 4"),
    ("left", "self.direction = 180; self.speed = 4"),
    ("down", "self.direction = 270; self.speed = 4"),
    ("up-left", "self.direction = 135; self.speed = 4"),
    # A list: what the events panel's 3x3 checkbox picker emits.
    (["right"], "self.direction = 0; self.speed = 4"),
    # 'stop' halts, whichever shape it arrives in.
    ("stop", "self.speed = 0"),
    (["up", "stop"], "self.speed = 0"),
    # Nothing chosen: halt rather than silently moving right.
    ("", "self.speed = 0"),
    ([], "self.speed = 0"),
])
def test_direction_parameter_shapes(directions, expected):
    from export.Kivy.code_generator import ActionCodeGenerator

    generated = ActionCodeGenerator()._convert_simple_action(
        "start_moving_direction", {"directions": directions, "speed": "4"},
        "keyboard")
    assert generated == expected


def test_multiple_directions_still_pick_one_at_random():
    """GameMaker's move-fixed semantics: several checked directions means one
    is chosen per call. That behaviour must survive the normalisation."""
    from export.Kivy.code_generator import ActionCodeGenerator

    generated = ActionCodeGenerator()._convert_simple_action(
        "start_moving_direction", {"directions": ["up", "down"], "speed": "4"},
        "keyboard")
    assert "random.choice([90, 270])" in generated


def test_a_comma_separated_string_is_read_as_several_directions():
    """Hand-edited project JSON writes it this way; per-character iteration
    turned it into nine unknown names."""
    from export.Kivy.code_generator import ActionCodeGenerator

    generated = ActionCodeGenerator()._convert_simple_action(
        "start_moving_direction", {"directions": "up, down", "speed": "4"},
        "keyboard")
    assert "random.choice([90, 270])" in generated


def test_stop_is_matched_exactly_not_as_a_substring():
    """`'stop' in "unstoppable"` is True for a raw string, which would have
    turned an unknown direction into a halt."""
    from export.Kivy.code_generator import ActionCodeGenerator

    generated = ActionCodeGenerator()._convert_simple_action(
        "start_moving_direction", {"directions": "unstoppable", "speed": "4"},
        "keyboard")
    assert generated != "self.speed = 0"


def _load_object_namespace(game_dir: Path, stem: str):
    """Exec a generated object module with its base class stubbed out.

    Cheaper and more direct than importing the whole generated package: the
    method under test only touches attributes we control.
    """
    import types

    source = _object_source(game_dir, stem)
    module = types.ModuleType("generated_" + stem)
    module.__dict__["__name__"] = "generated_" + stem

    class _Base:
        def __init__(self, *a, **k):
            pass

        def __getattr__(self, name):
            # Any engine call the generated code makes is recorded, not run.
            def record(*args, **kwargs):
                self.calls.append((name, args))
            return record

    # Replace the base-class import with our stub.
    lines = [line for line in source.splitlines()
             if not line.startswith("from ") and not line.startswith("import ")]
    module.__dict__["GameObject"] = _Base
    module.__dict__["BaseGameObject"] = _Base
    exec("\n".join(lines), module.__dict__)  # noqa: S102 - our own generated code

    cls = next(v for v in module.__dict__.values()
               if isinstance(v, type) and v is not _Base
               and issubclass(v, _Base))
    return {"module": module, "cls": cls}


def _stub_instance(instance):
    instance.calls = []
    instance.x = instance.y = 0.0
    instance.hspeed = instance.vspeed = 0.0
    instance.speed = 0.0
    instance.direction = 0.0
    instance.scene = None

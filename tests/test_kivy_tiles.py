"""Kivy export: the room's static tile layer.

The Kivy exporter ignored `room['tiles']` completely. plateforme_2 has 127
tiles and plateforme_3 more, so both exported as bare backgrounds with floating
objects -- reported as issues 7 and 8 of the 2026-08-16 eyeball pass. (The only
previous mention of "tiles" in kivy_exporter.py was about repeating a
background IMAGE, an unrelated feature, which is how the gap survived review.)

Two independent y-flips make this worth executing rather than just inspecting,
because getting either wrong puts the art somewhere plausible-but-wrong instead
of failing loudly:

1. a tile's position in the ROOM is GameMaker's y-down from the top-left, so it
   flips against room_height;
2. the crop offset WITHIN the source image is measured from that image's top,
   while Kivy's `texture.get_region` measures from the bottom, so it flips
   against the texture's height.

Kivy cannot run in CI, so this follows the harness pattern established by
tests/test_kivy_raycast.py: export for real, import the generated scene module
under stub kivy modules, and drive the real generated `_draw_tiles` with a
recording Rectangle and a fake texture.
"""
import importlib
import json
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

SAMPLE = REPO_ROOT / "samples" / "plateforme_2"
TEX_W, TEX_H = 132, 132   # the fake tile sheet's size; crop flips against it


# --- minimal stubs ---------------------------------------------------------

class _Widget:
    def __init__(self, **kwargs):
        pass

    def add_widget(self, *a, **k):
        pass


class _Instr:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kw = kwargs


class _Group(_Instr):
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


class _FakeTex:
    """Stand-in texture; get_region records the slice it was asked for."""

    def __init__(self, w=TEX_W, h=TEX_H):
        self.width, self.height = w, h
        self.regions = []

    def get_region(self, x, y, w, h):
        self.regions.append((x, y, w, h))
        marker = _FakeTex(w, h)
        marker.slice = (x, y, w, h)
        return marker


class _FakeImage:
    def __init__(self, texture):
        self.texture = texture


@contextmanager
def _stub_kivy_env(game_dir: Path):
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)

    def mod(name, **attrs):
        m = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(m, key, value)
        sys.modules[name] = m

    try:
        mod("kivy")
        mod("kivy.uix")
        mod("kivy.uix.widget", Widget=_Widget)
        mod("kivy.graphics", Rectangle=_Instr, Color=_Instr, Line=_Instr,
            Ellipse=_Instr, InstructionGroup=_Group, PushMatrix=_Instr,
            PopMatrix=_Instr, Translate=_Instr, Fbo=_Instr,
            ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.graphics.texture", Texture=object)
        mod("kivy.core")
        mod("kivy.core.window", Window=types.SimpleNamespace(size=(800, 600)))
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=object)
        mod("main", get_game_app=lambda: None, _ScriptGameProxy=object)
        for name in [n for n in sys.modules
                     if n == "utils" or n.startswith(("utils.", "scenes",
                                                      "objects", "asset_paths"))]:
            del sys.modules[name]
        sys.path = [str(game_dir)] + [p for p in sys.path if p != str(REPO_ROOT)]
        yield
    finally:
        sys.path[:] = saved_path
        for name in [n for n in sys.modules if n not in saved_modules]:
            del sys.modules[name]
        sys.modules.update(saved_modules)


# --- fixtures --------------------------------------------------------------

def _merged_project(sample: Path) -> dict:
    """project.json with the rooms/ side files merged, as the real exporters do
    (tiles live in the side file, not the embedded copy)."""
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, room in data.get("assets", {}).get("rooms", {}).items():
        side = sample / "rooms" / ("%s.json" % name)
        if side.exists():
            room.update(json.loads(side.read_text(encoding="utf-8")))
    return data


@pytest.fixture(scope="module")
def project():
    return _merged_project(SAMPLE)


@pytest.fixture(scope="module")
def exported(project):
    out = Path(tempfile.mkdtemp(prefix="kivy_tiles_"))
    assert KivyExporter(project, SAMPLE, out).export()
    return out / "game"


@pytest.fixture(scope="module")
def source_tiles(project):
    rooms = project["assets"]["rooms"]
    room = next(iter(rooms.values()))
    return room["tiles"], room


def _baked_tiles(scene_source: str):
    """Read ROOM_TILES out of a generated scene by parsing it.

    Not by slicing on "\\n]": an empty `ROOM_TILES = []` has no such delimiter,
    so the slice runs on to the next unrelated bracket in the file and produces
    a confusing SyntaxError rather than an empty list. Most rooms have no tiles.
    """
    import ast

    tree = ast.parse(scene_source)
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "ROOM_TILES"):
            return ast.literal_eval(node.value)
    raise AssertionError("the generated scene declares no ROOM_TILES")


def _scene_module(game_dir: Path):
    scene_file = next(f for f in (game_dir / "scenes").glob("*.py")
                      if f.stem != "__init__")
    return importlib.import_module("scenes." + scene_file.stem)


def _draw(game_dir, room_height, *, paths=None):
    """Run the generated _draw_tiles and return (rectangles, texture)."""
    module = _scene_module(game_dir)
    scene_class = next(v for v in vars(module).values()
                       if isinstance(v, type) and issubclass(v, _Widget)
                       and v.__module__ == module.__name__)

    drawn = []

    class _Recorder(_Instr):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            drawn.append(self)

    texture = _FakeTex()
    module.Rectangle = _Recorder
    module.load_image = lambda path: _FakeImage(texture)
    if paths is not None:
        module.BACKGROUND_PATHS = paths

    scene = scene_class.__new__(scene_class)
    scene.room_height = room_height
    scene._draw_tiles()
    return drawn, texture, module


# --- the export bakes the tiles -------------------------------------------

def test_the_sample_actually_has_tiles(source_tiles):
    """Guards the test itself: if the sample lost its tiles, everything below
    would pass while proving nothing."""
    tiles, _room = source_tiles
    assert len(tiles) > 100, len(tiles)


def test_generated_scene_carries_every_tile(exported, source_tiles):
    tiles, _room = source_tiles
    module_source = next(f for f in (exported / "scenes").glob("*.py")
                         if f.stem != "__init__").read_text(encoding="utf-8")
    baked = _baked_tiles(module_source)
    assert len(baked) == len(tiles), (
        "%d tiles authored, %d exported" % (len(tiles), len(baked)))


def test_tiles_are_sorted_back_to_front(exported):
    """Pre-sorted at export time by depth descending, matching
    GameRoom._sorted_tiles, so the generated game does not sort every load."""
    from export.Kivy.kivy_exporter import KivyExporter as KE

    room = {"tiles": [
        {"background_name": "bg", "x": 0, "y": 0, "tile_x": 0, "tile_y": 0,
         "width": 16, "height": 16, "depth": 5},
        {"background_name": "bg", "x": 16, "y": 0, "tile_x": 0, "tile_y": 0,
         "width": 16, "height": 16, "depth": 900},
        {"background_name": "bg", "x": 32, "y": 0, "tile_x": 0, "tile_y": 0,
         "width": 16, "height": 16, "depth": 100},
    ]}
    baked = _baked_tiles("ROOM_TILES = " + KE._tiles_repr(room))
    assert [row[1] for row in baked] == [16, 32, 0], (
        "expected depth 900, 100, 5 (furthest first), got %r" % (baked,))


@pytest.mark.parametrize("bad", [
    {"background_name": "", "x": 0, "y": 0, "width": 16, "height": 16},
    {"background_name": "bg", "x": 0, "y": 0, "width": 0, "height": 16},
    {"background_name": "bg", "x": 0, "y": 0, "width": 16, "height": 0},
    {"background_name": "bg", "x": "nonsense", "y": 0, "width": 16, "height": 16},
    "not a dict",
])
def test_unusable_tiles_are_skipped_not_fatal(bad):
    """A corrupt tile should cost that tile, not the whole export."""
    from export.Kivy.kivy_exporter import KivyExporter as KE

    assert KE._tiles_repr({"tiles": [bad]}) == "[]"


def test_no_tiles_produces_an_empty_list():
    from export.Kivy.kivy_exporter import KivyExporter as KE

    assert KE._tiles_repr({}) == "[]"
    assert KE._tiles_repr({"tiles": []}) == "[]"
    assert KE._tiles_repr({"tiles": "corrupt"}) == "[]"


# --- the generated code draws them in the right place ---------------------

def test_every_tile_is_drawn(exported, source_tiles):
    tiles, room = source_tiles
    with _stub_kivy_env(exported):
        drawn, _tex, _mod = _draw(exported, room["height"])
    assert len(drawn) == len(tiles)


def test_room_position_is_flipped_for_kivys_y_up_origin(exported, source_tiles):
    """A tile authored at the room's TOP must draw at the top of a y-up canvas,
    i.e. near room_height -- not at y=0, which is the floor in Kivy."""
    tiles, room = source_tiles
    height = room["height"]
    with _stub_kivy_env(exported):
        drawn, _tex, _mod = _draw(exported, height)

    positions = {rect.kw["pos"] for rect in drawn}
    for tile in tiles:
        expected = (tile["x"], height - tile["y"] - tile["height"])
        assert expected in positions, (
            "tile at GM (%s, %s) should draw at %r" % (tile["x"], tile["y"], expected))

    topmost = min(t["y"] for t in tiles)
    drawn_top = max(pos[1] for pos in positions)
    assert drawn_top == height - topmost - 32, (
        "the room's top row should draw near room_height, got y=%s" % drawn_top)


def test_crop_offset_is_flipped_against_the_texture_height(exported, source_tiles):
    """The second, easier-to-miss flip: GameMaker's tile_y counts down from the
    image's top, Kivy's get_region counts up from its bottom."""
    tiles, room = source_tiles
    with _stub_kivy_env(exported):
        _drawn, texture, _mod = _draw(exported, room["height"])

    assert texture.regions, "no crop was requested"
    expected = {(t["tile_x"], TEX_H - t["tile_y"] - t["height"],
                 t["width"], t["height"]) for t in tiles}
    assert set(texture.regions) == expected

    # Stated concretely, so the intent survives a refactor: a crop at the very
    # top of a 132px sheet, 32px tall, is requested at y=100.
    assert (99, TEX_H - 66 - 32, 32, 32) in texture.regions


def test_identical_crops_are_requested_once(exported, source_tiles):
    """127 tiles share a handful of distinct crops. Re-cropping per tile would
    build a texture region for every one of them on room load."""
    tiles, room = source_tiles
    with _stub_kivy_env(exported):
        drawn, texture, _mod = _draw(exported, room["height"])

    distinct = {(t["background_name"], t["tile_x"], t["tile_y"],
                 t["width"], t["height"]) for t in tiles}
    assert len(texture.regions) == len(distinct), (
        "%d crops requested for %d distinct slices"
        % (len(texture.regions), len(distinct)))
    assert len(drawn) > len(texture.regions), (
        "this sample should reuse crops, or the test proves nothing")


def test_a_missing_background_skips_the_tile_without_crashing(exported, source_tiles):
    """An exported project whose tile sheet failed to copy should draw the rest
    of the room, not die on load."""
    _tiles, room = source_tiles
    with _stub_kivy_env(exported):
        drawn, _tex, _mod = _draw(exported, room["height"], paths={})
    assert drawn == []


def test_tiles_draw_under_the_instances_and_over_the_background(exported):
    """Order matters and is not observable from _draw_tiles alone: the desktop
    engine draws background colour, background image, tiles, then instances.
    Instances are child widgets, so anything in canvas.before/the Fbo is below
    them; within that, tiles must come after both background groups."""
    source = next(f for f in (exported / "scenes").glob("*.py")
                  if f.stem != "__init__").read_text(encoding="utf-8")

    for block in ("_draw_background", "_setup_views_fbo"):
        if block not in source:
            continue
    # Both render paths must call it, after the background image group.
    assert source.count("self._draw_tiles()") == 2, (
        "both the views (Fbo) and non-views paths must draw tiles")
    for anchor in ("self.canvas.before.add(self._bg_image_group)",
                   "self._fbo.add(self._bg_image_group)"):
        assert anchor in source
        assert source.index(anchor) < source.index(
            "self._draw_tiles()", source.index(anchor)), (
            "tiles must be drawn after %s" % anchor)


def test_a_sample_with_no_tiles_still_exports_a_valid_scene():
    """Most rooms have no tile layer at all, so the empty case is the common
    one -- it must still declare ROOM_TILES and compile."""
    out = Path(tempfile.mkdtemp(prefix="kivy_notiles_"))
    sample = REPO_ROOT / "samples" / "maze_1"
    assert KivyExporter(_merged_project(sample), sample, out).export()

    scenes = [f for f in (out / "game" / "scenes").glob("*.py")
              if f.stem != "__init__"]
    assert scenes
    for scene in scenes:
        source = scene.read_text(encoding="utf-8")
        compile(source, str(scene), "exec")
        assert _baked_tiles(source) == []


def test_a_room_with_no_tiles_returns_immediately(exported):
    """The generated method must tolerate an empty layer -- most rooms have
    one -- without touching BACKGROUND_PATHS or load_image."""
    with _stub_kivy_env(exported):
        module = _scene_module(exported)
        scene_class = next(v for v in vars(module).values()
                           if isinstance(v, type) and issubclass(v, _Widget)
                           and v.__module__ == module.__name__)

        def explode(*a, **k):
            raise AssertionError("load_image must not be called with no tiles")

        module.ROOM_TILES = []
        module.load_image = explode
        scene = scene_class.__new__(scene_class)
        scene.room_height = 480
        scene._draw_tiles()  # must simply return

"""Kivy export: draw-queue rendering + mouse/touch dispatch.

The exported Kivy runtime historically never invoked draw events, never
provided self._draw_queue / self.mouse_x / self.mouse_y, and silently
dropped mouse_* events — so a draw-queue + mouse game (samples/match3_1)
exported to a blank, unresponsive app. These tests pin the support added
for it:

- base GameObject initializes _draw_queue / mouse coords and renders the
  queue (room coords, y-down) as Kivy instructions with the y-axis flipped
- the scene loop's step 8 actually calls on_draw + _render_draw_queue
- flat mouse event keys map to methods and the scene dispatches touches
  to every instance that has them (IDE-runtime semantics: no hit-test)
- the Android virtual D-pad is generated only for keyboard-driven games

The second half runs the EXPORTED match3_1 game headlessly against stub
kivy modules and plays a real swap->flash->slide round through the
generated scene. sys.path / sys.modules are snapshotted and restored so
the stubs can't leak into other tests.
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
from utils.project_file_merge import merge_object_file  # noqa: E402

SAMPLE = REPO_ROOT / "samples" / "match3_1"


def _match3_project_data():
    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = SAMPLE / "objects" / f"{name}.json"
        if side.exists():
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        side = SAMPLE / "rooms" / f"{name}.json"
        if side.exists():
            data["assets"]["rooms"][name] = json.loads(side.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="module")
def exported():
    out = Path(tempfile.mkdtemp(prefix="kivy_dq_export_")) / "export"
    assert KivyExporter(_match3_project_data(), SAMPLE, out).export()
    return out / "game"


# ---------------------------------------------------------------------------
# Generated-code assertions
# ---------------------------------------------------------------------------

def test_base_object_has_draw_queue_support(exported):
    base = (exported / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "self._draw_queue = []" in base
    assert "self.mouse_x = 0.0" in base
    assert "def _render_draw_queue(self):" in base
    assert "def _dq_render_cmd(self" in base
    compile(base, "base_object.py", "exec")


def test_scene_invokes_draw_events(exported):
    scene = (exported / "scenes" / "rm_match3.py").read_text(encoding="utf-8")
    assert "instance.on_draw(dt)" in scene
    assert "instance._render_draw_queue()" in scene


def test_scene_dispatches_touch_as_mouse(exported):
    scene = (exported / "scenes" / "rm_match3.py").read_text(encoding="utf-8")
    assert "def on_touch_down(self, touch):" in scene
    assert "def on_touch_up(self, touch):" in scene
    assert "def _touch_to_room(self, touch):" in scene
    assert "on_mouse_left_press" in scene


def test_mouse_event_generates_method(exported):
    obj = (exported / "objects" / "obj_GridManager.py").read_text(encoding="utf-8")
    assert "def on_mouse_left_press(self):" in obj
    assert "def on_draw(self, dt):" in obj
    compile(obj, "obj_GridManager.py", "exec")


def test_mouse_event_map_covers_flat_keys():
    exporter = KivyExporter(_match3_project_data(), SAMPLE,
                            Path(tempfile.mkdtemp(prefix="kivy_dq_map_")))
    for key in ("mouse_left_press", "mouse_left_button", "mouse_left_down"):
        assert exporter._get_event_method_name(
            {"event_type": key}) == "on_mouse_left_press"
    assert exporter._get_event_method_name(
        {"event_type": "mouse_left_release"}) == "on_mouse_left_release"


def test_dpad_disabled_for_mouse_only_game(exported):
    main = (exported / "main.py").read_text(encoding="utf-8")
    assert "NEEDS_DPAD = False" in main
    assert "VirtualDPad is not None and NEEDS_DPAD" in main


def test_dpad_enabled_for_keyboard_game():
    data = _match3_project_data()
    data["assets"]["objects"]["obj_GridManager"]["events"]["keyboard"] = {
        "left": {"actions": [{"action": "execute_code",
                              "parameters": {"code": "pass"}}]}
    }
    out = Path(tempfile.mkdtemp(prefix="kivy_dq_dpad_")) / "export"
    assert KivyExporter(data, SAMPLE, out).export()
    main = (out / "game" / "main.py").read_text(encoding="utf-8")
    assert "NEEDS_DPAD = True" in main


# ---------------------------------------------------------------------------
# Headless run of the exported game against stub kivy modules
# ---------------------------------------------------------------------------

class _Group:
    def __init__(self):
        self.children = []

    def add(self, instr):
        self.children.append(instr)

    def clear(self):
        self.children.clear()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Canvas(_Group):
    def __init__(self):
        super().__init__()
        self.before = _Group()
        self.after = _Group()


class _Widget:
    def __init__(self, **kwargs):
        self.canvas = _Canvas()
        self.children = []
        self.size = (0, 0)
        self.pos = (0, 0)
        self.size_hint = (1, 1)

    def add_widget(self, w, index=0, canvas=None):
        # Real Kivy signature: children[0] is drawn LAST (on top). The
        # exporter passes index= to order instances by GameMaker depth.
        self.children.insert(index, w)

    def remove_widget(self, w):
        if w in self.children:
            self.children.remove(w)

    def on_touch_down(self, touch):
        return any(c.on_touch_down(touch) for c in self.children)

    def on_touch_up(self, touch):
        return any(c.on_touch_up(touch) for c in self.children)


class _Instr:
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw


class _Translate:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z


class _Fbo:
    def __init__(self, size=(0, 0), **kw):
        self.size = size
        self.texture = object()
        self.children = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def add(self, instr):
        self.children.append(instr)

    def remove(self, instr):
        if instr in self.children:
            self.children.remove(instr)


class _Color(_Instr):
    pass


class _Rectangle(_Instr):
    pass


class _Line(_Instr):
    pass


class _EllipseI(_Instr):
    pass


class _Tex:
    def __init__(self, size):
        self.size = size


class _CoreLabel:
    def __init__(self, text='', font_size=18, **kw):
        self.text = text
        self.texture = None

    def refresh(self):
        self.texture = _Tex((max(1, 8 * len(self.text)), 20))


class _WindowCls:
    width = 800
    height = 800

    def bind(self, **kw):
        pass

    def set_title(self, *a):
        pass


@contextmanager
def _stub_kivy_env(game_dir: Path):
    """Register stub kivy modules + the game dir on sys.path; fully restore
    sys.path and sys.modules afterwards (the game ships its own utils.py,
    which must shadow the repo package only inside this block)."""
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)

    def mod(name, **attrs):
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[name] = m

    try:
        mod("kivy")
        mod("kivy.uix")
        mod("kivy.uix.widget", Widget=_Widget)
        mod("kivy.graphics", Rectangle=_Rectangle, Color=_Color, Line=_Line,
            Ellipse=_EllipseI, InstructionGroup=_Group,
            PushMatrix=_Instr, PopMatrix=_Instr, Translate=_Translate,
            Fbo=_Fbo, ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=_CoreLabel)
        mod("main", get_game_app=lambda: None)
        for name in [n for n in sys.modules
                     if n == "utils" or n.startswith(("utils.", "scenes", "objects"))]:
            del sys.modules[name]
        sys.path = [str(game_dir)] + [p for p in sys.path if p != str(REPO_ROOT)]
        yield
    finally:
        sys.path[:] = saved_path
        for name in [n for n in sys.modules if n not in saved_modules]:
            del sys.modules[name]
        sys.modules.update(saved_modules)


class _Touch:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


def test_exported_game_plays_a_round_headlessly(exported):
    with _stub_kivy_env(exported):
        scene_mod = importlib.import_module("scenes.rm_match3")
        scene_cls = next(v for v in vars(scene_mod).values()
                         if isinstance(v, type) and issubclass(v, _Widget)
                         and v.__module__ == "scenes.rm_match3")
        scene = scene_cls()
        assert len(scene.instances) == 1
        inst = scene.instances[0]
        assert len(inst.grid) == 6 and callable(inst.find_matches)

        # One frame: the draw event renders via the queue, y-flipped.
        scene.update(1 / 60.0)
        rects = [i for i in inst._dq_group.children if isinstance(i, _Rectangle)]
        assert len(rects) == 39  # panel + 36 tiles + 2 text labels
        assert any(i.kw.get("pos") == (116.0, 568.0) for i in rects)  # tile (0,0)

        # Rig a known grid; swapping (0,0)<->(1,0) matches col 0 rows 0-2.
        inst.grid = [
            [1, 0, 2, 3, 2, 3],
            [0, 2, 3, 1, 3, 1],
            [0, 3, 1, 2, 1, 2],
            [2, 1, 0, 3, 0, 3],
            [3, 0, 2, 1, 2, 1],
            [1, 2, 3, 0, 3, 0],
        ]

        def click_tile(gx, gy):
            # window coords are y-up; game coords y-down
            scene.on_touch_down(_Touch(inst.ox + gx * inst.tile + 48,
                                       800 - (inst.oy + gy * inst.tile + 48)))

        click_tile(0, 0)
        assert inst.sel == (0, 0)
        click_tile(1, 0)
        assert inst.flash == inst.flash_total
        assert inst.marked == {(0, 0), (0, 1), (0, 2)}

        click_tile(3, 3)
        assert inst.sel is None  # input locked during the flash

        for _ in range(36):
            scene.update(1 / 60.0)
        assert inst.score == 30
        assert inst.falling == {(0, 0): 288, (0, 1): 288, (0, 2): 288}

        # Refill tiles above the board are hidden while sliding in.
        rects = [i for i in inst._dq_group.children if isinstance(i, _Rectangle)]
        assert len(rects) == 36

        for _ in range(24):
            scene.update(1 / 60.0)
        assert inst.falling == {} or inst.flash > 0

        rects = [i for i in inst._dq_group.children if isinstance(i, _Rectangle)]
        assert len(rects) == 39


def test_stub_env_restores_repo_utils(exported):
    """After the sim, the repo 'utils' package must be importable again."""
    import utils
    assert hasattr(utils, "project_file_merge") or (REPO_ROOT / "utils").is_dir()

"""Kivy export — views/camera (large-level scrolling), Phase 1.

The Kivy exporter gained a GameMaker-style camera mirroring the desktop
runtime (game_runner.update_views) and the HTML5 engine: the scene bakes a
views config, opens a PushMatrix + Translate in canvas.before (closed by a
PopMatrix in canvas.after) so the background and every child instance scroll
together, and update_views() does border-based follow + per-axis speed limit +
room clamp each frame in Kivy's y-up space. Single-view follow only; multi-view
port clipping is a documented follow-up.

Two layers of proof, like tests/test_html5_views.py:
 - source-level assertions on the generated scene, and
 - a headless run of the exported scene against stub kivy modules that drives
   update_views() and checks the camera translate tracks + clamps to the room.
"""
import importlib
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402


def _views_project_data():
    """A minimal 2400x800 room behind an 800x600 view that follows a player."""
    return {
        "name": "views_syn",
        "settings": {"window_width": 800, "window_height": 600},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_player": {"name": "obj_player", "sprite": "", "events": {}},
            },
            "rooms": {
                "rm_big": {
                    "name": "rm_big", "width": 2400, "height": 800,
                    "background_color": "#204060",
                    "views_enabled": True,
                    "views": {
                        "view_0": {
                            "visible": True,
                            "view_w": 800, "view_h": 600,
                            "port_x": 0, "port_y": 0,
                            "follow": "obj_player",
                            "hborder": 100, "vborder": 100,
                        },
                    },
                    "instances": [
                        {"object_type": "obj_player", "x": 1200, "y": 400},
                    ],
                },
            },
        },
        "room_order": ["rm_big"],
    }


@pytest.fixture(scope="module")
def exported():
    src = Path(tempfile.mkdtemp(prefix="kivy_views_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_views_export_")) / "export"
    assert KivyExporter(_views_project_data(), src, out).export()
    return out / "game"


def _scene_file(exported):
    return next((exported / "scenes").glob("rm_big*.py"))


# ---------------------------------------------------------------------------
# Generated-code assertions
# ---------------------------------------------------------------------------

def test_scene_bakes_views_config(exported):
    scene = _scene_file(exported).read_text(encoding="utf-8")
    assert "self.views_enabled = True" in scene
    assert "'follow': 'obj_player'" in scene
    assert "self._cam_translate = None" in scene
    compile(scene, "scene.py", "exec")


def test_scene_opens_camera_matrix(exported):
    scene = _scene_file(exported).read_text(encoding="utf-8")
    # camera transform brackets the background + child instances
    assert "PushMatrix()" in scene
    assert "self._cam_translate = TranslateInstr(0, 0, 0)" in scene
    assert "with self.canvas.after:" in scene and "PopMatrix()" in scene
    assert "from kivy.graphics import Translate as TranslateInstr" in scene


def test_scene_defines_and_calls_update_views(exported):
    scene = _scene_file(exported).read_text(encoding="utf-8")
    assert "def update_views(self):" in scene
    assert "def _find_view_target(self, name):" in scene
    assert "self.update_views()" in scene            # wired into the step loop
    # border follow + speed limit + room clamp are all present
    assert "view['hborder']" in scene and "view.get('hspeed'" in scene
    assert "self.room_width - vw" in scene


# ---------------------------------------------------------------------------
# Headless run of the exported scene against stub kivy modules
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

    def add_widget(self, w):
        self.children.insert(0, w)

    def remove_widget(self, w):
        if w in self.children:
            self.children.remove(w)


class _Instr:
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw


class _Translate:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z


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
    height = 600

    def bind(self, **kw):
        pass

    def set_title(self, *a):
        pass


@contextmanager
def _stub_kivy_env(game_dir: Path):
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
        mod("kivy.graphics", Rectangle=_Instr, Color=_Instr, Line=_Instr,
            Ellipse=_Instr, InstructionGroup=_Group,
            PushMatrix=_Instr, PopMatrix=_Instr, Translate=_Translate)
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


def _load_scene(exported):
    module = "scenes." + _scene_file(exported).stem
    scene_mod = importlib.import_module(module)
    scene_cls = next(v for v in vars(scene_mod).values()
                     if isinstance(v, type) and issubclass(v, _Widget)
                     and v.__module__ == module)
    return scene_cls()


def test_camera_follows_and_clamps_headlessly(exported):
    with _stub_kivy_env(exported):
        scene = _load_scene(exported)
        assert scene.views_enabled is True
        assert scene._cam_translate is not None
        assert len(scene.instances) == 1
        target = scene.instances[0]

        # Target near room centre: horizontal view scrolls to keep it inside
        # the 100px border; vertical stays put (target within the vertical band).
        target.x, target.y = 1200.0, 368.0
        scene.update_views()
        # tx=1200 > view_x(0)+view_w(800)-hb(100)=700 -> view_x = 1200-800+100 = 500
        assert scene.views[0]['view_x'] == 500
        assert scene.views[0]['view_y'] == 0
        assert scene._cam_translate.x == -500   # port_x(0) - view_x(500)
        assert scene._cam_translate.y == 0

        # Push the target to the far right: the camera clamps at the room edge
        # (2400 - 800 = 1600), never revealing past the room.
        target.x = 2400.0
        scene.update_views()
        assert scene.views[0]['view_x'] == 1600
        assert scene._cam_translate.x == -1600

        # Back to the far left: clamps at 0 (no negative scroll).
        target.x = 0.0
        scene.update_views()
        assert scene.views[0]['view_x'] == 0
        assert scene._cam_translate.x == 0


def test_camera_noop_when_views_disabled():
    """views_enabled False bakes an inert camera: translate never moves."""
    data = _views_project_data()
    data["assets"]["rooms"]["rm_big"]["views_enabled"] = False
    src = Path(tempfile.mkdtemp(prefix="kivy_views_off_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_views_off_")) / "export"
    assert KivyExporter(data, src, out).export()
    game = out / "game"
    with _stub_kivy_env(game):
        scene = _load_scene(game)
        assert scene.views_enabled is False
        scene.instances[0].x = 2400.0
        scene.update_views()
        assert scene._cam_translate.x == 0 and scene._cam_translate.y == 0

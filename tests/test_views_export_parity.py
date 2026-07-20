"""Views/camera — 3-target parity (Phase 1, step 4 of VIEWS_SAMPLES_PLAN.md).

There are three independent copies of the GameMaker view-follow math — the
desktop runtime (runtime/game_runner.GameRoom.update_views), the HTML5 engine
(export/HTML5/templates/engine.js updateViews), and the Kivy exporter's
generated scene (export/Kivy update_views). Three copies means drift risk, so
this pins them to a single reference: feed the *same* synthetic scenario (a
2400x800 room, an 800x600 view with 100px borders and no speed cap, following
one object) through each and assert the horizontal scroll (view_x) is identical.

view_x is the coordinate-system-independent axis: desktop/HTML5 are y-down and
Kivy is y-up, but a room x-coordinate means the same thing in all three, and
instances keep their x on export. So view_x is exactly the quantity that must
match across targets; the per-target y handling is covered by each target's own
test (test_html5_views / test_kivy_views).

Legs:
 - reference: the canonical formula, in this file.
 - desktop: the real GameRoom.update_views, driven headlessly (pygame patched).
 - Kivy: the exported scene's update_views, driven against stub kivy.
 - HTML5: engine.js can't run without node (not a CI dep), so its updateViews
   source is asserted to contain the same defining expressions. The behavioural
   proof is the Playwright run recorded in VIEWS_SAMPLES_PLAN.md.
"""
import importlib
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Shared synthetic scenario -------------------------------------------------
ROOM_W, ROOM_H = 2400, 800
VIEW_W, VIEW_H = 800, 600
HB, VB = 100, 100
# A target path that exercises: centre push-right, far-right clamp, far-left
# clamp, and a mid return. view_x carries between steps (the follow is stateful).
TARGET_XS = [1200, 2400, 0, 900]


def _reference_view_x_sequence():
    """The canonical GameMaker follow+clamp for view_x, run statefully."""
    vx = 0
    out = []
    for tx in TARGET_XS:
        new = vx
        if tx < vx + HB:
            new = tx - HB
        elif tx > vx + VIEW_W - HB:
            new = tx - VIEW_W + HB
        # no speed limit in this scenario
        new = max(0, min(new, ROOM_W - VIEW_W)) if VIEW_W < ROOM_W else 0
        out.append(new)
        vx = new
    return out


EXPECTED = _reference_view_x_sequence()


def test_reference_sequence_is_what_we_expect():
    # Guards the scenario itself so a later edit can't silently weaken it.
    assert EXPECTED == [500, 1600, 0, 200]


# Desktop leg ---------------------------------------------------------------

def _room_data():
    return {
        "name": "rm_big", "width": ROOM_W, "height": ROOM_H,
        "views_enabled": True,
        "views": {"view_0": {"visible": True, "view_w": VIEW_W, "view_h": VIEW_H,
                             "follow": "obj_player", "hborder": HB, "vborder": VB}},
        "instances": [{"object_name": "obj_player", "x": 0, "y": 0}],
    }


def test_desktop_view_x_matches_reference():
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameRoom
        room = GameRoom("rm_big", _room_data())
        target = room._find_first_instance("obj_player")
        assert target is not None
        seq = []
        for tx in TARGET_XS:
            target.x = float(tx)
            room.update_views()
            seq.append(room.views[0]['view_x'])
    assert seq == EXPECTED


# Kivy leg ------------------------------------------------------------------

class _Group:
    def __init__(self):
        self.children = []

    def add(self, i):
        self.children.append(i)

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
    def __init__(self, **kw):
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


class _Instr:
    def __init__(self, *a, **k):
        self.args = a
        self.kw = k


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

    def ask_update(self):
        pass


class _Win:
    width = 800
    height = 600

    def bind(self, **k):
        pass

    def set_title(self, *a):
        pass


@contextmanager
def _stub_kivy_env(game_dir: Path):
    saved_path, saved_modules = list(sys.path), dict(sys.modules)

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
            PushMatrix=_Instr, PopMatrix=_Instr, Translate=_Translate,
            Fbo=_Fbo, ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.core")
        mod("kivy.core.window", Window=_Win())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=object)
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


def test_kivy_view_x_matches_reference():
    from export.Kivy.kivy_exporter import KivyExporter
    project = {
        "name": "views_syn",
        "settings": {"window_width": VIEW_W, "window_height": VIEW_H},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {},
                   "objects": {"obj_player": {"name": "obj_player", "sprite": "", "events": {}}},
                   "rooms": {"rm_big": _room_data()}},
        "room_order": ["rm_big"],
    }
    src = Path(tempfile.mkdtemp(prefix="views_parity_src_"))
    out = Path(tempfile.mkdtemp(prefix="views_parity_kivy_")) / "export"
    assert KivyExporter(project, src, out).export()
    game = out / "game"
    with _stub_kivy_env(game):
        scene_file = next((game / "scenes").glob("rm_big*.py"))
        module = "scenes." + scene_file.stem
        scene_mod = importlib.import_module(module)
        scene_cls = next(v for v in vars(scene_mod).values()
                         if isinstance(v, type) and issubclass(v, _Widget)
                         and v.__module__ == module)
        scene = scene_cls()
        target = scene.instances[0]
        seq = []
        for tx in TARGET_XS:
            target.x = float(tx)   # Kivy x == GM x (only y is flipped on export)
            scene.update_views()
            seq.append(scene.views[0]['view_x'])
    assert seq == EXPECTED


# HTML5 leg -----------------------------------------------------------------

def test_html5_view_x_formula_matches_reference():
    """engine.js updateViews uses the same border-push + room-clamp as the
    reference (behavioural proof is the recorded Playwright run; node isn't a
    CI dependency so the source is checked here)."""
    engine = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    # left-edge push, right-edge push, and the room clamp — the three lines
    # that define view_x, matching _reference_view_x_sequence above.
    assert "newVx = Math.trunc(target.x - hb)" in engine
    assert "newVx = Math.trunc(target.x - vw + hb)" in engine
    assert "Math.max(0, Math.min(newVx, this.width - vw))" in engine

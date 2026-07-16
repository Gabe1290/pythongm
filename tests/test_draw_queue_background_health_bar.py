"""Kivy + HTML5 export: draw-queue 'background' and 'health_bar' commands.

TODO.md's "Draw-queue types sprite/background/lives/health_bar are not
rendered by the Kivy _render_draw_queue" (and the matching HTML5 note)
was half stale by the time this was written — sprite/lives shipped with
the match3_2 sound-queue work. This closes the other half: 'background'
(resolved by name via a new BACKGROUND_PATHS map on Kivy, and via the
same game.sprites map sprites/backgrounds already share on HTML5 — see
html5_exporter.py's encode_sprites, which merges both into one dict) and
'health_bar' (plain rectangles + a border, no asset lookup needed).

Both mirror runtime/game_runner.py's _draw_background / _draw_health_bar
exactly (same tiling math, same health-percentage math) since those are
the reference implementation these two exporters are catching up to.
"""
import importlib
import json
import re
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# HTML5 — static source checks (Node isn't a CI dep; see test_html5_views.py)
# ---------------------------------------------------------------------------

def test_html5_background_case_present():
    m = re.search(r"case 'background':\s*\{(.*?)\n            \}", ENGINE, re.S)
    assert m, "case 'background' not found in renderDrawCommands"
    body = m.group(1)
    assert "game.sprites[cmd.background_name]" in body
    assert "cmd.tiled" in body
    assert "ctx.drawImage(img, bx, by)" in body


def test_html5_health_bar_case_present():
    m = re.search(r"case 'health_bar':\s*\{(.*?)\n            \}", ENGINE, re.S)
    assert m, "case 'health_bar' not found in renderDrawCommands"
    body = m.group(1)
    assert "cmd.back_color" in body and "cmd.bar_color" in body
    assert "Math.max(0, Math.min(100, health))" in body
    assert "ctx.strokeRect" in body


# ---------------------------------------------------------------------------
# Kivy — asset_paths.py generation + static source checks
# ---------------------------------------------------------------------------

def _minimal_project(tmp_path):
    """A synthetic 1-object, 1-background, 1-room project — not a bundled
    sample, so this test doesn't depend on samples/ staying a particular
    shape (same reasoning as test_kivy_parity_batch's synthetic codegen
    tests for create_moving_instance/jump_to_random)."""
    (tmp_path / "backgrounds").mkdir()
    from PIL import Image
    Image.new("RGB", (64, 48), (10, 20, 30)).save(tmp_path / "backgrounds" / "bg_test.png")

    draw_code = (
        "q = self._draw_queue\n"
        "q.append({'type': 'background', 'background_name': 'bg_test', "
        "'x': 0, 'y': 0, 'tiled': False})\n"
        "q.append({'type': 'health_bar', 'x1': 10, 'y1': 10, 'x2': 110, "
        "'y2': 30, 'health': 60, 'back_color': '#FF0000', "
        "'bar_color': '#00FF00'})\n"
    )
    return {
        "name": "DrawQueueTest",
        "settings": {"window_width": 320, "window_height": 240, "room_speed": 30},
        "assets": {
            "sprites": {},
            "sounds": {},
            "backgrounds": {
                "bg_test": {"name": "bg_test", "asset_type": "background",
                            "file_path": "backgrounds/bg_test.png",
                            "width": 64, "height": 48},
            },
            "objects": {
                "obj_drawer": {
                    "name": "obj_drawer", "asset_type": "object", "sprite": "",
                    "events": {"draw": {"actions": [
                        {"action": "execute_code", "parameters": {"code": draw_code}}]}},
                },
            },
            "rooms": {
                "room0": {
                    "name": "room0", "asset_type": "room",
                    "width": 320, "height": 240,
                    "instances": [{"object_name": "obj_drawer", "x": 0, "y": 0}],
                    "tiles": [],
                },
            },
        },
        "room_order": ["room0"],
    }


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    src = tmp_path_factory.mktemp("draw_queue_bg_hb_src")
    out = tmp_path_factory.mktemp("draw_queue_bg_hb_export") / "export"
    assert KivyExporter(_minimal_project(src), src, out).export()
    return out / "game"


def test_background_paths_module_generated(exported):
    mod = (exported / "asset_paths.py").read_text(encoding="utf-8")
    assert "BACKGROUND_PATHS" in mod
    assert '"bg_test": "assets/images/bg_test.png"' in mod
    compile(mod, "asset_paths.py", "exec")


def test_asset_file_copied(exported):
    assert (exported / "assets" / "images" / "bg_test.png").exists()


def test_base_object_has_both_branches(exported):
    base = (exported / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "elif ctype == 'background':" in base
    assert "elif ctype == 'health_bar':" in base
    assert "from kivy.core.window import Window" in base
    compile(base, "base_object.py", "exec")


# ---------------------------------------------------------------------------
# Kivy — headless run against stub kivy modules (real rendering, not just
# source checks). Self-contained stub, matching the pattern established in
# tests/test_kivy_match3_2_sound_sprite_export.py / test_kivy_parity_batch.py.
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


class _Tex:
    def __init__(self, size=(64, 48)):
        self.size = size
        self.width, self.height = size


class _CoreImage:
    def __init__(self, path, **kw):
        self.path = path
        self.texture = _Tex()


class _CoreLabel:
    def __init__(self, text='', font_size=18, **kw):
        self.text = text
        self.texture = None

    def refresh(self):
        self.texture = _Tex((max(1, 8 * len(self.text)), 20))


class _WindowCls:
    width = 320
    height = 240


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
            Ellipse=_Instr, InstructionGroup=_Group)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=_CoreImage)
        mod("kivy.core.text", Label=_CoreLabel)
        mod("main", get_game_app=lambda: None, play_sound=lambda *a, **k: None)
        for name in [n for n in sys.modules
                     if n == "utils" or n.startswith(("utils.", "scenes", "objects", "asset_paths", "sprite_meta"))]:
            del sys.modules[name]
        sys.path = [str(game_dir)] + [p for p in sys.path if p != str(REPO_ROOT)]
        yield
    finally:
        sys.path[:] = saved_path
        for name in [n for n in sys.modules if n not in saved_modules]:
            del sys.modules[name]
        sys.modules.update(saved_modules)


def test_background_and_health_bar_actually_render(exported):
    with _stub_kivy_env(exported):
        obj_mod = importlib.import_module("objects.obj_drawer")
        cls = next(v for v in vars(obj_mod).values()
                  if isinstance(v, type) and v.__module__ == "objects.obj_drawer")
        inst = cls(scene=None, x=0, y=0)
        inst._draw_queue = []
        inst.on_draw(1 / 30.0)
        inst._render_draw_queue()

        rects = [i for i in inst._dq_group.children if isinstance(i, _Instr)]
        # background: one Rectangle sized to the 64x48 texture
        bg_rects = [r for r in rects if r.kw.get("size") == (64, 48)]
        assert bg_rects, f"expected a 64x48 background Rectangle, got {rects}"

        # health_bar: back rect (100x20) + health rect (60x20, 60% of 100) + border Line
        health_back = [r for r in rects if r.kw.get("size") == (100.0, 20.0)]
        health_fill = [r for r in rects if r.kw.get("size") == (60.0, 20.0)]
        assert health_back, f"expected a 100x20 back-color Rectangle, got {rects}"
        assert health_fill, f"expected a 60x20 health-fill Rectangle (60% of 100), got {rects}"


def test_stub_env_restores_repo_utils():
    import utils  # noqa: F401

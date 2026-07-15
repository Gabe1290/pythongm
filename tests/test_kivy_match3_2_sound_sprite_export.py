"""Kivy export: the cross-platform sound-queue primitive + by-name sprite
resolution, as exercised by samples/match3_2.

match3_1's execute_code architecture had no live `game` object on the Kivy
runtime, so execute_code couldn't trigger sound at all, and a hand-authored
`{'type': 'sprite', 'sprite_name': ...}` draw-queue command (as opposed to a
structured draw_sprite action) silently failed to render — the Kivy
draw-queue renderer only resolved a sprite via a `sprite_path` baked in at
code-generation time for structured actions. match3_2 needed both, so this
pins the fix: a generated `asset_paths.py` (SPRITE_PATHS / SOUND_PATHS) that
base_object.py's `_drain_sound_queue` and `_dq_render_cmd`'s 'sprite' branch
both fall back to by name. Runs headlessly against stub kivy modules, mirroring
tests/test_kivy_draw_queue_mouse_export.py's harness (this file is
self-contained on purpose, matching that file's pattern of not sharing
fixtures across test modules).
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

SAMPLE = REPO_ROOT / "samples" / "match3_2"


def _match3_2_project_data():
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
    out = Path(tempfile.mkdtemp(prefix="kivy_match3_2_export_")) / "export"
    assert KivyExporter(_match3_2_project_data(), SAMPLE, out).export()
    return out / "game"


# ---------------------------------------------------------------------------
# Static generated-code assertions
# ---------------------------------------------------------------------------

def test_asset_paths_module_has_sprites_and_sounds(exported):
    mod = (exported / "asset_paths.py").read_text(encoding="utf-8")
    for name in ("spr_gem_red", "spr_gem_blue", "spr_gem_green", "spr_gem_yellow"):
        assert f'"{name}"' in mod
        assert f"assets/images/{name}.png" in mod
    for name in ("snd_swap", "snd_match", "snd_cascade"):
        assert f'"{name}"' in mod
        assert f"assets/sounds/{name}.wav" in mod
    compile(mod, "asset_paths.py", "exec")


def test_base_object_has_sound_queue_and_sprite_fallback(exported):
    base = (exported / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "self._sound_queue = []" in base
    assert "def _drain_sound_queue(self):" in base
    assert "from asset_paths import SPRITE_PATHS, SOUND_PATHS" in base
    assert "SPRITE_PATHS.get(cmd.get('sprite_name'), '')" in base
    compile(base, "base_object.py", "exec")


def test_scene_drains_sound_queue_every_frame(exported):
    scene = (exported / "scenes" / "rm_match3.py").read_text(encoding="utf-8")
    assert "instance._drain_sound_queue()" in scene
    compile(scene, "scenes/rm_match3.py", "exec")


def test_assets_actually_copied(exported):
    for name in ("spr_gem_red", "spr_gem_blue", "spr_gem_green", "spr_gem_yellow"):
        assert (exported / "assets" / "images" / f"{name}.png").exists()
    for name in ("snd_swap", "snd_match", "snd_cascade"):
        assert (exported / "assets" / "sounds" / f"{name}.wav").exists()


# ---------------------------------------------------------------------------
# Headless run against stub kivy modules
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
    def __init__(self, size=(88, 88)):
        self.size = size
        self.width, self.height = size


class _CoreImage:
    """Stub for kivy.core.image.Image — just needs a .texture with a size,
    matching what _dq_render_cmd's 'sprite' branch reads."""

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
    width = 800
    height = 800

    def bind(self, **kw):
        pass

    def set_title(self, *a):
        pass


@contextmanager
def _stub_kivy_env(game_dir: Path, play_sound_calls):
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)

    def mod(name, **attrs):
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[name] = m

    def _play_sound(path, volume=1.0):
        play_sound_calls.append((path, volume))

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
        mod("kivy.core.image", Image=_CoreImage)
        mod("kivy.core.text", Label=_CoreLabel)
        mod("main", get_game_app=lambda: None, play_sound=_play_sound)
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


class _Touch:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


def test_exported_game_plays_sounds_and_renders_sprites_headlessly(exported):
    play_sound_calls = []
    with _stub_kivy_env(exported, play_sound_calls):
        scene_mod = importlib.import_module("scenes.rm_match3")
        scene_cls = next(v for v in vars(scene_mod).values()
                         if isinstance(v, type) and issubclass(v, _Widget)
                         and v.__module__ == "scenes.rm_match3")
        # Deterministic tile refills: match3 fills cleared cells with
        # random.randrange, and an unlucky refill can form an accidental cascade
        # that shifts the render/score counts asserted below (a rare flake).
        # Seed the shared random module so the sim is reproducible.
        import random
        random.seed(20260715)
        scene = scene_cls()
        assert len(scene.instances) == 1
        inst = scene.instances[0]

        # One frame with no interaction: idle tiles render as sprite
        # Rectangles (texture from the stub CoreImage), not filled color
        # rectangles.
        scene.update(1 / 60.0)
        rects = [i for i in inst._dq_group.children if isinstance(i, _Rectangle)]
        # Text labels also render as textured Rectangles (score/instructions);
        # tile sprites are the ones sized (88, 88), matching the stub image.
        tile_rects = [r for r in rects if r.kw.get("size") == (88, 88)]
        assert len(tile_rects) == inst.cols * inst.rows, (
            "expected every idle tile to render via the sprite fallback path")

        # Rig a guaranteed match at (2,0)/(2,1), same cells the standalone
        # logic harness used during development.
        inst.grid[0][0] = 0
        inst.grid[0][1] = 0
        inst.grid[0][2] = 1
        inst.grid[1][2] = 0

        def click_tile(gx, gy):
            scene.on_touch_down(_Touch(inst.ox + gx * inst.tile + 48,
                                       800 - (inst.oy + gy * inst.tile + 48)))

        click_tile(2, 0)
        click_tile(2, 1)
        assert inst.swap_phase == "forward"
        assert inst.pending_marks, "expected the rigged swap to match"

        # snd_swap must have played already (queued the same frame as the
        # click, drained by the scene's next update()).
        scene.update(1 / 60.0)
        assert any(p == "assets/sounds/snd_swap.wav" for p, _v in play_sound_calls), (
            f"expected snd_swap to play via the sound queue, got {play_sound_calls}")

        # Drain the swap slide + flash + fall, well within a generous frame
        # budget; the state machine must settle back to idle.
        for _ in range(200):
            scene.update(1 / 60.0)
            if (inst.swap_phase is None and inst.flash == 0
                    and not inst.falling and not inst.swap_off):
                break
        assert inst.swap_phase is None and inst.flash == 0 and not inst.falling
        assert inst.score >= 10

        match_paths = {"assets/sounds/snd_match.wav", "assets/sounds/snd_cascade.wav"}
        assert any(p in match_paths for p, _v in play_sound_calls), (
            f"expected a match/cascade sound to play, got {play_sound_calls}")


def test_stub_env_restores_repo_utils_and_state():
    """After the sim, the repo 'utils' package must be importable again
    (same guard as test_kivy_draw_queue_mouse_export.py)."""
    import utils  # noqa: F401

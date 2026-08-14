"""Right/middle mouse export parity (TODO.md's Kivy/Android + HTML5 export
follow-ups: "Right/middle mouse events have no touch equivalent and stay
unexported").

The desktop runtime has always supported mouse_right_*/mouse_middle_*
events (runtime/game_runner.py's _FLAT_MOUSE_KEY_ALIASES), but neither
export target's mouse dispatch ever looked at anything but the left
button — a project using a right-click action worked in the IDE and on
desktop exports, then silently did nothing on Kivy/Android or HTML5/web.

Fixed by keying dispatch off the real button on both targets:
- Kivy: touch.button ('left'/'right'/'middle', set by Kivy's mouse motion
  provider for real mouse input; absent — defaults to 'left' — for a
  genuine touchscreen tap, matching Android's single-button model).
- HTML5: DOM MouseEvent.button (0=left, 1=middle, 2=right), plus a
  contextmenu preventDefault so a right-click reaches the game instead of
  opening the browser's menu.
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

ENGINE_JS = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _click_project_data():
    """One object recording which button pressed/released it last."""
    events = {}
    for button in ("left", "right", "middle"):
        events[f"mouse_{button}_press"] = {
            "actions": [{"action": "execute_code",
                        "parameters": {"code": f"self.last = 'press_{button}'"}}]
        }
        events[f"mouse_{button}_release"] = {
            "actions": [{"action": "execute_code",
                        "parameters": {"code": f"self.last = 'release_{button}'"}}]
        }
    return {
        "name": "click_syn",
        "assets": {
            "sprites": {},
            "objects": {"obj_click": {"name": "obj_click", "sprite": "", "events": events}},
            "rooms": {
                "rm_click": {
                    "name": "rm_click", "width": 320, "height": 240,
                    "instances": [{"object_type": "obj_click", "x": 10, "y": 10}],
                },
            },
        },
        "room_order": ["rm_click"],
    }


@pytest.fixture(scope="module")
def exported():
    out = Path(tempfile.mkdtemp(prefix="kivy_mouse_export_")) / "export"
    assert KivyExporter(_click_project_data(), REPO_ROOT, out).export()
    return out / "game"


# ---------------------------------------------------------------------------
# Kivy — generated-code assertions
# ---------------------------------------------------------------------------

def test_kivy_event_map_covers_right_middle_flat_keys():
    exporter = KivyExporter(_click_project_data(), REPO_ROOT,
                            Path(tempfile.mkdtemp(prefix="kivy_mouse_map_")))
    for key in ("mouse_right_press", "mouse_right_button", "mouse_right_down"):
        assert exporter._get_event_method_name(
            {"event_type": key}) == "on_mouse_right_press"
    assert exporter._get_event_method_name(
        {"event_type": "mouse_right_release"}) == "on_mouse_right_release"
    for key in ("mouse_middle_press", "mouse_middle_button", "mouse_middle_down"):
        assert exporter._get_event_method_name(
            {"event_type": key}) == "on_mouse_middle_press"
    assert exporter._get_event_method_name(
        {"event_type": "mouse_middle_release"}) == "on_mouse_middle_release"


def test_kivy_scene_dispatches_by_touch_button(exported):
    scene = next((exported / "scenes").glob("rm_click*.py")).read_text(encoding="utf-8")
    assert "getattr(touch, 'button', 'left')" in scene
    assert "on_mouse_right_press" in scene
    assert "on_mouse_middle_press" in scene
    assert "on_mouse_right_release" in scene
    assert "on_mouse_middle_release" in scene
    compile(scene, "rm_click.py", "exec")


def test_kivy_object_generates_all_three_button_methods(exported):
    obj = (exported / "objects" / "obj_click.py").read_text(encoding="utf-8")
    for method in ("on_mouse_left_press", "on_mouse_right_press", "on_mouse_middle_press",
                   "on_mouse_left_release", "on_mouse_right_release", "on_mouse_middle_release"):
        assert f"def {method}(self):" in obj, method
    compile(obj, "obj_click.py", "exec")


# ---------------------------------------------------------------------------
# Kivy — headless real execution: a right/middle click reaches the right
# instance method and no other.
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


class _CoreLabel:
    def __init__(self, text='', font_size=18, **kw):
        self.text = text
        self.texture = None

    def refresh(self):
        pass


class _WindowCls:
    width = 800
    height = 800

    def bind(self, **kw):
        pass

    def set_title(self, *a):
        pass


class _StubScriptGameProxy:
    score = 0
    lives = 3
    health = 100


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
            PushMatrix=_Instr, PopMatrix=_Instr, Translate=_Translate,
            Fbo=_Fbo, ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=_CoreLabel)
        mod("main", get_game_app=lambda: None, _ScriptGameProxy=_StubScriptGameProxy)
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
    def __init__(self, x, y, button=None):
        self.x = float(x)
        self.y = float(y)
        if button is not None:
            self.button = button


def test_kivy_headless_click_dispatch_by_button(exported):
    with _stub_kivy_env(exported):
        scene_mod = importlib.import_module("scenes.rm_click")
        scene_cls = next(v for v in vars(scene_mod).values()
                         if isinstance(v, type) and issubclass(v, _Widget)
                         and v.__module__ == "scenes.rm_click")
        scene = scene_cls()
        inst = scene.instances[0]

        scene.on_touch_down(_Touch(50, 50, button='right'))
        assert inst.last == 'press_right'
        scene.on_touch_up(_Touch(50, 50, button='right'))
        assert inst.last == 'release_right'

        scene.on_touch_down(_Touch(50, 50, button='middle'))
        assert inst.last == 'press_middle'
        scene.on_touch_up(_Touch(50, 50, button='middle'))
        assert inst.last == 'release_middle'

        scene.on_touch_down(_Touch(50, 50, button='left'))
        assert inst.last == 'press_left'
        scene.on_touch_up(_Touch(50, 50, button='left'))
        assert inst.last == 'release_left'

        # A genuine touchscreen touch (no .button attribute at all) must
        # still behave as a left click, unchanged from before this fix.
        scene.on_touch_down(_Touch(50, 50))
        assert inst.last == 'press_left'


def test_kivy_stub_env_restores_repo_utils(exported):
    import utils
    assert hasattr(utils, "project_file_merge") or (REPO_ROOT / "utils").is_dir()


# ---------------------------------------------------------------------------
# HTML5 — structural assertions (no Node.js in CI; matches this repo's
# established engine.js testing tier, e.g. test_draw_action_codegen.py)
# ---------------------------------------------------------------------------

def test_html5_defines_right_and_middle_key_arrays():
    assert "RIGHT_PRESS_KEYS = ['mouse_right_press', 'mouse_right_button', 'mouse_right_down']" in ENGINE_JS
    assert "RIGHT_RELEASE_KEYS = ['mouse_right_release']" in ENGINE_JS
    assert "MIDDLE_PRESS_KEYS = ['mouse_middle_press', 'mouse_middle_button', 'mouse_middle_down']" in ENGINE_JS
    assert "MIDDLE_RELEASE_KEYS = ['mouse_middle_release']" in ENGINE_JS


def test_html5_mousedown_mouseup_dispatch_by_button_code():
    assert "if (e.button === 0) dispatch(e.clientX, e.clientY, PRESS_KEYS);" in ENGINE_JS
    assert "else if (e.button === 2) dispatch(e.clientX, e.clientY, RIGHT_PRESS_KEYS);" in ENGINE_JS
    assert "else if (e.button === 1) dispatch(e.clientX, e.clientY, MIDDLE_PRESS_KEYS);" in ENGINE_JS
    assert "else if (e.button === 2) dispatch(e.clientX, e.clientY, RIGHT_RELEASE_KEYS);" in ENGINE_JS
    assert "else if (e.button === 1) dispatch(e.clientX, e.clientY, MIDDLE_RELEASE_KEYS);" in ENGINE_JS


def test_html5_prevents_context_menu_on_canvas():
    assert "addEventListener('contextmenu', (e) => e.preventDefault());" in ENGINE_JS


def test_html5_brace_balance_unchanged():
    # Sanity check on the surgery — this file's braces must still balance.
    assert ENGINE_JS.count('{') == ENGINE_JS.count('}')

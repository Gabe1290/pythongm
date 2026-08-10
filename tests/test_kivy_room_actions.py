"""Kivy export — Room-category action codegen: set_room_speed,
set_background_color, set_room_persistent.

These three actions had working runtime handlers on desktop
(runtime/action_executor.py) but were "Unknown action type" on the Kivy
export target — this closes that gap with real, non-stub codegen + scene
support (see docs/DEFERRED_ITEMS_PLAN.md's room-actions follow-up).

Semantics ported from the desktop runtime, adapted to Kivy's dt-scaled
movement model (GameObject._process_movement already scales speed by
`dt * <baseline>` for frame-rate independence, unlike desktop's raw
per-step model — room_speed replaces the hardcoded 60.0 baseline, so
changing it scales real-world velocity exactly like changing the desktop
runtime's FPS clock does):
 - set_room_speed(fps) sets Scene.room_speed, read every
   GameObject._process_movement call.
 - set_background_color(rgb, show) mutates whichever ClearColor/Color
   instruction the room actually built (non-views: _bg_color_instr;
   views/Fbo: _fbo_clear) — show=False fills black rather than skipping
   the fill, matching the desktop runtime's fallback (this canvas redraws
   every frame; skipping would smear the previous frame).
 - set_room_persistent(flag) sets Scene.persistent directly; GameApp
   caches a persistent room's scene instance on exit and reuses it on a
   later revisit instead of rebuilding — mirrors the desktop runtime's
   change_room reuse-on-revisit fix. restart_room/restart_game both force
   a fresh rebuild regardless of persistent (verified against desktop's
   restart_current_room/restart_game, which do the same).

Two layers of proof, matching this repo's established Kivy test pattern
(test_kivy_views.py, test_kivy_raycast.py):
 - source-level assertions on the generated scene.py/main.py, and
 - a headless run of the exported scene/app against stub kivy modules.
The App-level room-cache reuse (GameApp._do_room_switch/restart_game) is
real, nontrivial control flow, so it gets a genuine headless execution
test too, not just structural assertions — see _stub_kivy_env, which
extends test_kivy_views.py's scene-only stub set with the additional
kivy.app/kivy.config/kivy.clock/kivy.uix.* stubs main.py's module-level
code needs to import cleanly.
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
from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402


def _room_actions_project_data():
    """Two small rooms: rm_a is persistent (with one moving instance for the
    room_speed/movement test), rm_b is not (the default)."""
    return {
        "name": "room_actions_syn",
        "settings": {},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_walker": {"name": "obj_walker", "sprite": "", "events": {}},
            },
            "rooms": {
                "rm_a": {
                    "name": "rm_a", "width": 320, "height": 240,
                    "background_color": "#204060",
                    "persistent": True,
                    "instances": [
                        {"object_type": "obj_walker", "x": 10, "y": 10},
                    ],
                },
                "rm_b": {
                    "name": "rm_b", "width": 320, "height": 240,
                    "background_color": "#402060",
                    "instances": [],
                },
            },
        },
        "room_order": ["rm_a", "rm_b"],
    }


@pytest.fixture(scope="module")
def exported():
    src = Path(tempfile.mkdtemp(prefix="kivy_room_actions_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_room_actions_export_")) / "export"
    assert KivyExporter(_room_actions_project_data(), src, out).export()
    return out / "game"


def _scene_file(exported, room_name):
    return next((exported / "scenes").glob(f"{room_name}*.py"))


# ---------------------------------------------------------------------------
# Generated-code assertions
# ---------------------------------------------------------------------------

def test_scene_bakes_persistent_flag(exported):
    rm_a = _scene_file(exported, "rm_a").read_text(encoding="utf-8")
    rm_b = _scene_file(exported, "rm_b").read_text(encoding="utf-8")
    assert "self.persistent = True" in rm_a
    assert "self.persistent = False" in rm_b
    compile(rm_a, "rm_a.py", "exec")
    compile(rm_b, "rm_b.py", "exec")


def test_scene_bakes_room_speed_and_bg_instr_slots(exported):
    scene = _scene_file(exported, "rm_a").read_text(encoding="utf-8")
    assert "self.room_speed = 60.0" in scene
    assert "self._bg_color_instr = None" in scene
    assert "self._fbo_clear = None" in scene
    assert "def set_room_speed(self, fps):" in scene
    assert "def set_background_color(self, rgb, show=True):" in scene


def test_base_object_movement_uses_scene_room_speed(exported):
    base_obj = (exported / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "room_speed = self.scene.room_speed if self.scene else 60.0" in base_obj
    assert "speed_factor = dt * room_speed if dt > 0 else 1.0" in base_obj


def test_main_app_has_room_cache_and_restart_game(exported):
    main_src = (exported / "main.py").read_text(encoding="utf-8")
    assert "self._room_cache = {}" in main_src
    assert "self._visited_rooms = set()" in main_src
    assert "def restart_game(self):" in main_src
    assert "self._room_cache.clear()" in main_src
    assert "self._visited_rooms.clear()" in main_src
    compile(main_src, "main.py", "exec")


# ---------------------------------------------------------------------------
# Codegen — direct ActionCodeGenerator checks (no export needed)
# ---------------------------------------------------------------------------

def test_codegen_emits_set_room_speed():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("set_room_speed", {"speed": "45"}, "create")
    assert code == "self.scene.set_room_speed(45)"


def test_codegen_emits_set_room_speed_expression():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_room_speed", {"speed": "room_speed_var + 10"}, "create")
    assert code.startswith("self.scene.set_room_speed((")
    assert "self.room_speed_var" in code


def test_codegen_emits_set_room_persistent():
    gen = ActionCodeGenerator()
    assert gen._convert_simple_action(
        "set_room_persistent", {"persistent": "true"}, "create"
    ) == "self.scene.persistent = True"
    assert gen._convert_simple_action(
        "set_room_persistent", {"persistent": "false"}, "create"
    ) == "self.scene.persistent = False"
    # default (no param) matches the ActionType's own True default
    assert gen._convert_simple_action(
        "set_room_persistent", {}, "create"
    ) == "self.scene.persistent = True"


def test_codegen_emits_set_background_color():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "set_background_color", {"color": "#FF8000", "show_color": "true"}, "create")
    assert code == "self.scene.set_background_color((1.0, 0.5019607843137255, 0.0), True)"
    code_off = gen._convert_simple_action(
        "set_background_color", {"color": "#000000", "show_color": "false"}, "create")
    assert code_off == "self.scene.set_background_color((0.0, 0.0, 0.0), False)"


def test_codegen_emits_restart_game_via_helper():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("restart_game", {}, "create")
    assert "_app.restart_game()" in code
    assert "_switch_to_room(0)" not in code  # goes through the cache-clearing helper now


def test_codegen_restart_room_forces_rebuild():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("restart_room", {}, "create")
    assert "app._switch_to_room(app.current_room_index, force_rebuild=True)" in code


# ---------------------------------------------------------------------------
# Headless run: scene-level methods (Scene construction only, no App)
# ---------------------------------------------------------------------------

class _Group:
    def __init__(self):
        self.children = []

    def add(self, instr):
        self.children.append(instr)

    def remove(self, instr):
        if instr in self.children:
            self.children.remove(instr)

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


class _Instr:
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw


class _Translate:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z


class _Fbo(_Group):
    def __init__(self, size=(0, 0), **kw):
        super().__init__()
        self.size = size
        self.texture = object()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def ask_update(self):
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
    height = 600

    def bind(self, **kw):
        pass

    def unbind(self, **kw):
        pass

    def set_title(self, *a):
        pass


class _StubScriptGameProxy:
    score = 0
    lives = 3
    health = 100


class _ClockStub:
    """schedule_once runs its callback IMMEDIATELY (dt=0) so App-level room
    switches (deferred via Clock on real Kivy, to let the current frame
    finish) happen synchronously in a headless test."""

    def schedule_once(self, func, delay=0):
        func(0)
        return object()

    def schedule_interval(self, func, interval):
        return object()

    def unschedule(self, ev):
        pass


class _ConfigStub:
    def set(self, *a, **kw):
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
        mod("kivy.uix.floatlayout", FloatLayout=_Widget)
        mod("kivy.uix.popup", Popup=_Widget)
        mod("kivy.uix.label", Label=_Widget)
        mod("kivy.uix.boxlayout", BoxLayout=_Widget)
        mod("kivy.uix.button", Button=_Widget)
        mod("kivy.graphics", Rectangle=_Instr, Color=_Instr, Line=_Instr,
            Ellipse=_Instr, Triangle=_Instr, InstructionGroup=_Group,
            PushMatrix=_Instr, PopMatrix=_Instr, Translate=_Translate,
            Scale=_Translate, Fbo=_Fbo, ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=_CoreLabel)
        mod("kivy.app", App=object)
        mod("kivy.clock", Clock=_ClockStub())
        mod("kivy.config", Config=_ConfigStub())
        # No fake "main" module here (unlike test_kivy_views.py's stub set):
        # the App-level tests below need the REAL generated main.py
        # importable, and pre-registering a fake one would permanently
        # shadow it in sys.modules for the rest of the `with` block.
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


def _load_scene(exported, room_name):
    module = "scenes." + _scene_file(exported, room_name).stem
    scene_mod = importlib.import_module(module)
    scene_cls = next(v for v in vars(scene_mod).values()
                      if isinstance(v, type) and issubclass(v, _Widget)
                      and v.__module__ == module)
    return scene_cls()


def test_set_room_speed_scales_movement(exported):
    with _stub_kivy_env(exported):
        scene = _load_scene(exported, "rm_a")
        walker = scene.instances[0]
        assert scene.room_speed == 60.0

        walker.hspeed = 6.0
        start_x = walker.x
        walker._process_movement(1.0 / 60.0)
        # default room_speed=60 -> dt*60 == 1.0 -> a full per-step move
        assert walker.x == pytest.approx(start_x + 6.0)

        scene.set_room_speed(30)
        assert scene.room_speed == 30
        start_x = walker.x
        walker._process_movement(1.0 / 60.0)
        # room_speed=30 -> dt*30 == 0.5 -> half a per-step move
        assert walker.x == pytest.approx(start_x + 3.0)


def test_set_room_speed_clamps_and_defaults_on_bad_input(exported):
    with _stub_kivy_env(exported):
        scene = _load_scene(exported, "rm_a")
        scene.set_room_speed(9999)
        assert scene.room_speed == 240
        scene.set_room_speed(-5)
        assert scene.room_speed == 1
        scene.set_room_speed("not a number")
        assert scene.room_speed == 60


def test_set_background_color_updates_the_live_instruction(exported):
    with _stub_kivy_env(exported):
        scene = _load_scene(exported, "rm_a")
        assert scene._bg_color_instr is not None
        assert scene._fbo_clear is None  # rm_a is not a views room

        scene.set_background_color((1.0, 0.0, 0.0), True)
        assert scene._bg_color_instr.rgb == (1.0, 0.0, 0.0)
        assert scene.show_background_color is True

        scene.set_background_color((1.0, 0.0, 0.0), False)
        assert scene._bg_color_instr.rgb == (0.0, 0.0, 0.0)
        assert scene.show_background_color is False
        assert scene.background_color == (1.0, 0.0, 0.0)  # stored regardless of show


# ---------------------------------------------------------------------------
# Headless run: App-level persistent-room cache (GameApp._do_room_switch /
# restart_game), imported for real (not reimplemented as a parallel model).
# ANDROID_APP_PATH is redirected to tmp_path so main.py's faulthandler crash
# log lands there instead of the repo root.
# ---------------------------------------------------------------------------

def _load_main(exported, tmp_path, monkeypatch):
    monkeypatch.setenv("ANDROID_APP_PATH", str(tmp_path))
    module = importlib.import_module("main")
    return module


def test_persistent_room_is_reused_non_persistent_is_rebuilt(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = main.GameApp()
        app.root_layout = _Widget()
        app.scene_container = None
        app.dpad = None
        app.current_room_index = 0
        app.scene = main.ROOM_CLASSES["rm_a"]()
        app._visited_rooms = {0}
        app._room_cache = {}
        app.update_event = None

        rm_a_first = app.scene
        rm_a_first.instances[0].x = 12345  # a live-state marker to prove reuse

        # Leave the persistent room for the non-persistent one and back again.
        app._do_room_switch(1)
        assert app.current_room_index == 1
        rm_b_first = app.scene

        app._do_room_switch(0)
        assert app.scene is rm_a_first  # persistent room instance reused
        assert app.scene.instances[0].x == 12345  # its live state survived

        app._do_room_switch(1)
        assert app.scene is not rm_b_first  # non-persistent room rebuilt fresh


def test_restart_room_forces_rebuild_of_a_persistent_room(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = main.GameApp()
        app.root_layout = _Widget()
        app.scene_container = None
        app.dpad = None
        app.current_room_index = 0
        app.scene = main.ROOM_CLASSES["rm_a"]()
        app._visited_rooms = {0}
        app._room_cache = {}
        app.update_event = None

        original = app.scene
        original.instances[0].x = 999

        app._do_room_switch(0, force_rebuild=True)

        assert app.scene is not original  # forced fresh rebuild, not the marked instance
        assert app.scene.instances[0].x == 10  # back to the authored start position


def test_restart_game_clears_the_whole_cache(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = main.GameApp()
        app.root_layout = _Widget()
        app.scene_container = None
        app.dpad = None
        app.current_room_index = 1
        app.scene = main.ROOM_CLASSES["rm_b"]()
        app._visited_rooms = {0, 1}
        app._room_cache = {0: main.ROOM_CLASSES["rm_a"]()}
        app.update_event = None

        app.restart_game()

        assert app.current_room_index == 0
        assert app._room_cache == {}
        assert app._visited_rooms == {0}  # re-seeded by the switch to room 0

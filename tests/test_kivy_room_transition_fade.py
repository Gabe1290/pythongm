"""Kivy export — goto_room's transition='fade' (TODO.md: "Room-transition
fade effect isn't ported to HTML5/Kivy exports").

Desktop's GameRunner.change_room/_fade_overlay blocks in a pygame
sub-loop for the duration of the fade -- Kivy's event loop can't block
like that, so this is a small, explicitly-ticked state machine instead
(GameApp._start_fade_out/_fade_tick), driven by Clock.schedule_interval
at ~60fps, FADE_FRAMES total steps per phase (not wall-clock time, so a
slow/dropped frame just takes one more tick rather than skipping visible
steps -- the same per-frame-step model as desktop's own `for step in
range(frame_count)` loop). A pre-created _FadeOverlay widget (same
"always exists, only Color.a changes" pattern as the existing
_MsgOverlay) is raised to the top of the widget tree before each
widget-tree change the fade touches, since Kivy renders the
most-recently-added child on top -- otherwise _do_room_switch's own
add_widget(new_scene) would silently bury the overlay mid-transition.

Only goto_room's own explicit transition param ever carries this --
next_room/previous_room/restart_room/restart_game never do, matching
desktop's execute_goto_room_action/change_room scope exactly.

Headless execution against the REAL generated main.py (not a
reimplemented model), same pattern as test_kivy_room_actions.py's
App-level tests: construct main.GameApp() directly, hand-set the
attributes _do_room_switch/_switch_to_room depend on, and drive the
methods directly -- Clock.schedule_once runs its callback immediately in
the stub (matching real Kivy's deferred-to-next-frame intent closely
enough for a deterministic headless test); schedule_interval's callback
is driven manually, frame by frame, since nothing here needs real wall
time.
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


def _two_room_project_data():
    return {
        "name": "fade_transition_syn",
        "settings": {},
        "assets": {
            "sprites": {}, "sounds": {},
            "backgrounds": {},
            "objects": {},
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 320, "height": 240,
                          "background_color": "#204060", "instances": []},
                "rm_b": {"name": "rm_b", "width": 320, "height": 240,
                          "background_color": "#402060", "instances": []},
            },
        },
        "room_order": ["rm_a", "rm_b"],
    }


@pytest.fixture(scope="module")
def exported():
    src = Path(tempfile.mkdtemp(prefix="kivy_fade_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_fade_export_")) / "export"
    assert KivyExporter(_two_room_project_data(), src, out).export()
    return out / "game"


# ---------------------------------------------------------------------------
# Codegen
# ---------------------------------------------------------------------------

def test_codegen_passes_transition_through():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action(
        "goto_room", {"room": "rm_b", "transition": "fade"}, "create")
    assert code == "from main import goto_room; goto_room('rm_b', 'fade')"


def test_codegen_defaults_transition_to_none_when_absent():
    gen = ActionCodeGenerator()
    code = gen._convert_simple_action("goto_room", {"room": "rm_b"}, "create")
    assert code == "from main import goto_room; goto_room('rm_b', 'none')"


def test_generated_main_py_compiles(exported):
    import py_compile
    py_compile.compile(str(exported / "main.py"), doraise=True)


# ---------------------------------------------------------------------------
# Headless run against the real generated main.py
# ---------------------------------------------------------------------------

class _Group:
    def __init__(self):
        self.children = []

    def add(self, instr):
        self.children.append(instr)

    def insert(self, index, instr):
        self.children.insert(index, instr)

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
        # Matches real Kivy: the most-recently-added widget lands at
        # children[0], which Kivy's renderer draws LAST (i.e. on top) --
        # confirmed against this exporter's own _MsgOverlay, which relies
        # on being add_widget'd after the scene/dpad to render above them.
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


class _CoreImageStub:
    def __init__(self, path, **kw):
        self.texture = _Tex((64, 64))


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


class _ClockStub:
    """schedule_once runs its callback IMMEDIATELY (dt=0), matching
    test_kivy_room_actions.py's established stub. schedule_interval does
    NOT auto-invoke anything -- tests drive _fade_tick manually, frame by
    frame, since nothing here needs real wall-clock timing."""

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
        mod("kivy.core.image", Image=_CoreImageStub)
        mod("kivy.core.text", Label=_CoreLabel)
        mod("kivy.app", App=object)
        mod("kivy.clock", Clock=_ClockStub())
        mod("kivy.config", Config=_ConfigStub())
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


def _load_main(exported, tmp_path, monkeypatch):
    monkeypatch.setenv("ANDROID_APP_PATH", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module("main")
    return module


def _bare_app(main, tmp_path):
    app = main.GameApp()
    app.root_layout = _Widget()
    app.scene_container = None
    app.dpad = None
    app.current_room_index = 0
    app.scene = main.ROOM_CLASSES["rm_a"]()
    app.root_layout.add_widget(app.scene)
    app._visited_rooms = {0}
    app._room_cache = {}
    app.update_event = None
    return app


def test_transition_none_switches_immediately_no_overlay(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app._switch_to_room(1, transition='none')

        assert app.current_room_index == 1
        assert app._fade_overlay is None  # never created -- no fade requested


def test_fade_transition_starts_an_overlay_and_does_not_switch_immediately(
        exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app._switch_to_room(1, transition='fade')

        # The room has NOT switched yet -- only fade-out has started.
        assert app.current_room_index == 0
        assert app._fade_phase == 'out'
        assert app._fade_overlay is not None
        assert app._fade_overlay in app.root_layout.children


def test_fade_out_ramps_alpha_up_to_1_then_switches_room(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app._switch_to_room(1, transition='fade')
        overlay = app._fade_overlay
        frames = main._FADE_FRAMES

        for _ in range(frames - 1):
            app._fade_tick(1 / 60)
        assert app._fade_phase == 'out'
        assert 0 < overlay._color.a < 1.0
        assert app.current_room_index == 0  # still the old room

        app._fade_tick(1 / 60)  # the frame that crosses the fade-out threshold
        assert app._fade_phase == 'in'
        assert app.current_room_index == 1  # switched at the midpoint
        # Fade-in just started (step 0 of _FADE_FRAMES): still fully
        # opaque black, same as the last frame of fade-out -- no visible
        # pop/flash at the crossover.
        assert overlay._color.a == pytest.approx(1.0)


def test_fade_in_ramps_alpha_down_to_0_and_cleans_up(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app._switch_to_room(1, transition='fade')
        frames = main._FADE_FRAMES
        for _ in range(frames):  # completes fade-out, crosses into fade-in
            app._fade_tick(1 / 60)
        assert app._fade_phase == 'in'

        for _ in range(frames - 1):
            app._fade_tick(1 / 60)
        assert app._fade_phase == 'in'
        assert app._fade_tick(1 / 60) is False  # the final tick stops rescheduling
        assert app._fade_phase is None


def test_overlay_is_raised_above_the_newly_switched_scene(exported, tmp_path, monkeypatch):
    """The real reason _raise_fade_overlay exists: _do_room_switch's own
    add_widget(new_scene) would otherwise bury the overlay the instant the
    room actually switches, making the fade-in invisible."""
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app._switch_to_room(1, transition='fade')
        frames = main._FADE_FRAMES
        for _ in range(frames):
            app._fade_tick(1 / 60)

        assert app.current_room_index == 1
        # The overlay is the most-recently add_widget'd -- children[0] in
        # this stub's "insert at index 0" convention (see _Widget above).
        assert app.root_layout.children[0] is app._fade_overlay
        assert app.scene in app.root_layout.children


def test_fade_does_not_affect_next_room_or_restart_room(exported, tmp_path, monkeypatch):
    """Matches desktop's scope exactly: only goto_room's own transition
    param can request a fade."""
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app.goto_next_room()
        assert app.current_room_index == 1
        assert app._fade_overlay is None

        app._switch_to_room(0, force_rebuild=True)  # restart_room's call shape
        assert app._fade_overlay is None


def test_goto_room_accepts_and_forwards_transition(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app.goto_room("rm_b", transition="fade")

        assert app._fade_phase == 'out'
        assert app.current_room_index == 0  # not switched yet


def test_a_second_fade_mid_transition_cancels_the_first(exported, tmp_path, monkeypatch):
    """Starting a fresh fade-out while one is already in flight must not
    leave two competing Clock.schedule_interval callbacks ticking the
    same overlay -- _start_fade_out explicitly unschedules any prior one."""
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _bare_app(main, tmp_path)

        app._switch_to_room(1, transition='fade')
        app._fade_tick(1 / 60)
        first_step = app._fade_step
        assert first_step > 0

        app._switch_to_room(0, transition='fade')  # restart mid fade-out
        assert app._fade_step == 0  # restarted cleanly, not accumulated
        assert app._fade_phase == 'out'

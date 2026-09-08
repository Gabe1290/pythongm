"""L17, docs/FULL_AUDIT_2026-09-07.md: Kivy export has no
remember_destroyed support.

The desktop runtime's "stay destroyed" opt-in (GameRunner.
_destroyed_memory / _remember_destroyed_instance / _apply_destroyed_memory)
had no Kivy counterpart at all -- an object flagged remember_destroyed
respawned on every room restart/revisit on Android/iOS exports, exactly
as if the flag did nothing.

Fix: GameApp gains its own _destroyed_memory dict (room_name -> set of
(object_name, xstart, ystart) identity tuples), mirroring the desktop
mechanism exactly:
- Scene.update's per-frame cleanup step records a destroyed instance's
  identity there when it opts in (self.remember_destroyed, baked into
  the generated object class alongside self.solid/self.persistent).
- GameApp._do_room_switch prunes remembered instances from a freshly
  BUILT scene (never from a reused persistent-room scene, which already
  reflects any earlier destruction in its own live state).
- GameApp.restart_game clears the whole memory, matching the desktop
  runtime's own full-restart reset.

Follows tests/test_kivy_room_actions.py's established two-layer pattern
(generated-code assertions, then a real headless run against stub kivy
modules) and copies its stub environment verbatim -- each Kivy export
test file is self-contained by this repo's own convention (see that
file's docstring).

Also worth recording here: this session independently verified the
audit's own "(desktop + HTML5 honour it)" parenthetical is WRONG --
`grep remember_destroyed export/HTML5` is empty too, so HTML5 has the
identical gap. That is a separate, not-yet-fixed finding (not silently
folded into this one, which is scoped to the audit's literal Kivy ask)
-- logged in TODO.md.
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


def _project_data():
    """One room with two instances of the SAME object at different
    positions -- obj_gem opts into remember_destroyed, so destroying just
    one of the two must leave the other respawning normally on restart."""
    return {
        "name": "remember_destroyed_syn",
        "settings": {},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_gem": {"name": "obj_gem", "sprite": "", "events": {},
                            "remember_destroyed": True},
                "obj_plain": {"name": "obj_plain", "sprite": "", "events": {}},
            },
            "rooms": {
                "rm_a": {
                    "name": "rm_a", "width": 320, "height": 240,
                    "instances": [
                        {"object_type": "obj_gem", "x": 10, "y": 10},
                        {"object_type": "obj_gem", "x": 50, "y": 50},
                        {"object_type": "obj_plain", "x": 90, "y": 90},
                    ],
                },
            },
        },
        "room_order": ["rm_a"],
    }


@pytest.fixture(scope="module")
def exported():
    src = Path(tempfile.mkdtemp(prefix="kivy_remember_destroyed_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_remember_destroyed_export_")) / "export"
    assert KivyExporter(_project_data(), src, out).export()
    return out / "game"


def _scene_file(exported, room_name):
    return next((exported / "scenes").glob(f"{room_name}*.py"))


# ---------------------------------------------------------------------------
# Generated-code assertions
# ---------------------------------------------------------------------------

def test_object_bakes_remember_destroyed_flag(exported):
    obj_gem = (exported / "objects" / "obj_gem.py").read_text(encoding="utf-8")
    obj_plain = (exported / "objects" / "obj_plain.py").read_text(encoding="utf-8")
    assert "self.remember_destroyed = True" in obj_gem
    assert "self.remember_destroyed = False" in obj_plain
    compile(obj_gem, "obj_gem.py", "exec")
    compile(obj_plain, "obj_plain.py", "exec")


def test_scene_bakes_room_name(exported):
    scene = _scene_file(exported, "rm_a").read_text(encoding="utf-8")
    assert 'self.room_name = "rm_a"' in scene
    compile(scene, "rm_a.py", "exec")


def test_main_app_has_destroyed_memory_and_clears_it_on_restart(exported):
    main_src = (exported / "main.py").read_text(encoding="utf-8")
    assert "self._destroyed_memory = {}" in main_src
    assert "self._destroyed_memory.clear()" in main_src
    compile(main_src, "main.py", "exec")


# ---------------------------------------------------------------------------
# Headless run: stub kivy environment (copied from test_kivy_room_actions.py
# -- each Kivy export test file keeps its own self-contained stub set).
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
    """schedule_once runs its callback IMMEDIATELY (dt=0) so App-level room
    switches (deferred via Clock on real Kivy) happen synchronously here."""

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
            Scale=_Translate, Fbo=_Group, ClearColor=_Instr, ClearBuffers=_Instr)
        mod("kivy.core")
        mod("kivy.core.window", Window=_WindowCls())
        mod("kivy.core.image", Image=object)
        mod("kivy.core.text", Label=object)
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


def _load_scene(exported, room_name):
    module = "scenes." + _scene_file(exported, room_name).stem
    scene_mod = importlib.import_module(module)
    scene_cls = next(v for v in vars(scene_mod).values()
                      if isinstance(v, type) and issubclass(v, _Widget)
                      and v.__module__ == module)
    return scene_cls()


def _load_main(exported, tmp_path, monkeypatch):
    monkeypatch.setenv("ANDROID_APP_PATH", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module("main")
    return module


def _app_for(main, room_name):
    app = main.GameApp()
    app.root_layout = _Widget()
    app.scene_container = None
    app.dpad = None
    app.current_room_index = main.ROOM_ORDER.index(room_name)
    app.scene = main.ROOM_CLASSES[room_name]()
    app._visited_rooms = {app.current_room_index}
    app._room_cache = {}
    app.update_event = None
    # Only GameApp.build() (never called by this headless harness) sets
    # main's module-level _game_app -- but the Scene's own remember_destroyed
    # bookkeeping reaches the app through get_game_app(), exactly like every
    # other app-level access a scene makes. Set it directly, matching what a
    # real run's build() does before any gameplay happens.
    main._game_app = app
    return app


def test_destroyed_gem_does_not_respawn_after_restart_room(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _app_for(main, "rm_a")

        gems = [i for i in app.scene.instances if i.object_name == "obj_gem"]
        assert len(gems) == 2
        app.scene.destroy_instance(gems[0])
        app.scene.update(1 / 60.0)

        # The exact bug: without remember_destroyed support, restart_room
        # rebuilds the room from the authored layout and both gems come
        # back, as if the destruction never happened.
        app._do_room_switch(app.current_room_index, force_rebuild=True)

        remaining_gems = [i for i in app.scene.instances if i.object_name == "obj_gem"]
        assert len(remaining_gems) == 1, (
            "the destroyed gem respawned on restart despite remember_destroyed")
        assert remaining_gems[0].x == 50  # the OTHER gem, untouched
        # A plain (non-opted-in) object is unaffected by any of this.
        assert any(i.object_name == "obj_plain" for i in app.scene.instances)


def test_non_flagged_object_still_respawns_normally(exported, tmp_path, monkeypatch):
    """The fix must not accidentally suppress ordinary instances -- only
    ones that opted in."""
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _app_for(main, "rm_a")

        plain = next(i for i in app.scene.instances if i.object_name == "obj_plain")
        app.scene.destroy_instance(plain)
        app.scene.update(1 / 60.0)

        app._do_room_switch(app.current_room_index, force_rebuild=True)

        assert any(i.object_name == "obj_plain" for i in app.scene.instances)
        assert len([i for i in app.scene.instances if i.object_name == "obj_gem"]) == 2


def test_restart_game_clears_destroyed_memory(exported, tmp_path, monkeypatch):
    with _stub_kivy_env(exported):
        main = _load_main(exported, tmp_path, monkeypatch)
        app = _app_for(main, "rm_a")

        gems = [i for i in app.scene.instances if i.object_name == "obj_gem"]
        app.scene.destroy_instance(gems[0])
        app.scene.update(1 / 60.0)
        app._do_room_switch(app.current_room_index, force_rebuild=True)
        assert len([i for i in app.scene.instances if i.object_name == "obj_gem"]) == 1

        app.restart_game()

        assert app._destroyed_memory == {}
        assert len([i for i in app.scene.instances if i.object_name == "obj_gem"]) == 2

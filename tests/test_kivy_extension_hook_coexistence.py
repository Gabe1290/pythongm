"""Queue item A8: several extensions share the Kivy scene's hooks.

Until 2026-10-30 each extension's ``SCENE_CODE`` *overrode* one shared method name
(``_init_extensions``, ``_render_extension_overlay``, ``_update_extensions``, ...). With more than one
extension enabled -- the default, and what CI runs -- every generated scene held several
definitions of the same name and Python kept the last: raycast's ``_render_extension_overlay``
silently shadowed Block World's, so a Block World game exported for Android never drew its world.
Now the scene template owns the dispatchers and each extension adds ``_ext_<hook>__<extension>``
methods, which every dispatcher calls in name order.
"""
import ast
import importlib
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_microbit_actions import _stub_kivy  # noqa: E402
from test_microbit_export_fallthrough import _project  # noqa: E402

HOOKS = ("_init_extensions", "_render_extension_overlay", "_update_extensions",
         "_extension_touch_down", "_extension_touch_up", "_extension_touch_move",
         "_extension_key_down", "_extension_key_up")


@pytest.fixture(scope="module")
def game():
    """A real Kivy export with EVERY extension enabled (this box's own config may disable some)."""
    import events.plugin_loader as loader
    from export.Kivy import code_generator
    from export.Kivy.kivy_exporter import KivyExporter
    original = loader.list_available_extensions
    loader.list_available_extensions = lambda *a, **k: [dict(i, enabled=True) for i in original(*a, **k)]
    code_generator._EXTENSION_CODEGEN = None
    try:
        out = Path(tempfile.mkdtemp(prefix="mb_hooks_")) / "export"
        assert KivyExporter(_project({"create": {"actions": []}}), Path(tempfile.mkdtemp()), out).export()
    finally:
        loader.list_available_extensions = original
        code_generator._EXTENSION_CODEGEN = None
    return out / "game"


def _scene_methods(game):
    tree = ast.parse((game / "scenes" / "room0.py").read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Room0")
    names = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
    return names


def test_the_export_really_holds_several_extensions(game):
    names = _scene_methods(game)
    for expected in ("_ext_overlay__block_world", "_ext_overlay__raycast_2_5d", "_ext_update__microbit",
                     "_ext_init__block_world", "_ext_init__raycast_2_5d"):
        assert expected in names, expected


@pytest.mark.parametrize("hook", HOOKS)
def test_each_shared_hook_is_defined_exactly_once(game, hook):
    assert _scene_methods(game).count(hook) == 1, hook


def test_no_method_of_the_scene_is_defined_twice(game):
    names = _scene_methods(game)
    twice = sorted({n for n in names if names.count(n) > 1})
    assert not twice, twice


def _scene(game, extra=None):
    scene_mod = importlib.import_module("scenes.room0")
    cls = scene_mod.Room0
    if extra:
        cls = type("Room0WithExtra", (cls,), extra)
    scene = cls.__new__(cls)
    scene.instances, scene.room_height = [], 480
    return scene


def test_every_extensions_state_is_initialised(game):
    with _stub_kivy(game):
        scene = _scene(game)
        scene._init_extensions()
        assert scene.raycast_camera is None and scene.block_world_camera is None
        assert scene._bw_blocks == {} and scene._raycast_tex_cache == {}


def test_each_overlay_draws_when_its_camera_is_on_and_only_one_claims_the_frame(game):
    with _stub_kivy(game):
        drawn = []
        scene = _scene(game, {"_render_block_world": lambda self: drawn.append("block_world"),
                              "_render_raycast": lambda self: drawn.append("raycast")})
        scene._init_extensions()
        assert scene._render_extension_overlay() is False and drawn == []
        scene.raycast_camera = {"enabled": True}
        assert scene._render_extension_overlay() is True and drawn == ["raycast"]
        drawn.clear()
        scene.raycast_camera, scene.block_world_camera = None, {"enabled": True}
        assert scene._render_extension_overlay() is True and drawn == ["block_world"]
        drawn.clear()
        scene.raycast_camera = {"enabled": True}              # both on: the first by name claims it
        assert scene._render_extension_overlay() is True and drawn == ["block_world"]


def test_every_updater_runs_in_name_order(game):
    with _stub_kivy(game):
        calls = []
        scene = _scene(game, {"_ext_update__aaa": lambda self, dt: calls.append(("aaa", dt)),
                              "_ext_update__zzz": lambda self, dt: calls.append(("zzz", dt))})
        scene._update_extensions(0.5)
        assert calls == [("aaa", 0.5), ("zzz", 0.5)]          # microbit's own step is in between, silent


def test_a_touch_stops_at_the_first_extension_that_swallows_it(game):
    with _stub_kivy(game):
        seen = []

        def make(name, result):
            return lambda self, touch, mx, my, button: (seen.append(name), result)[1]
        scene = _scene(game, {"_ext_touch_down__aaa": make("aaa", False), "_ext_touch_down__bbb": make("bbb", True),
                              "_ext_touch_down__ccc": make("ccc", True)})
        assert scene._extension_touch_down(None, 1, 2, "left") is True
        assert seen == ["aaa", "bbb"]                           # ccc never sees a swallowed touch
        seen.clear()
        plain = _scene(game, {"_ext_touch_down__aaa": make("aaa", False)})
        assert plain._extension_touch_down(None, 1, 2, "left") is False and seen == ["aaa"]


def test_a_second_extension_does_not_disturb_the_micro_bit(game):
    """The micro:bit still gets its keys and its per-frame step next to another extension."""
    import test_kivy_microbit_draw as helper
    with _stub_kivy(game):
        keys = []
        scene = _scene(game, {"_ext_key_down__aaa": lambda self, key: keys.append(key)})
        board, _ = helper._board(microbit_keyboard=True)
        board._mb_draw = lambda room_h: None
        scene.instances = [board]
        scene._extension_key_down(97)
        assert keys == [97] and board._mb_sim().buttons["a"]


def test_handlers_are_found_once_per_hook_and_cached(game):
    with _stub_kivy(game):
        scene = _scene(game)
        first = scene._ext_handlers("update")
        assert scene._ext_handlers("update") is first
        assert scene._ext_handlers("key_up") is not first
        assert scene._ext_handlers("no_such_hook") == []


def test_an_extension_method_that_is_not_a_hook_is_never_called(game):
    with _stub_kivy(game):
        called = []
        scene = _scene(game, {"_ext_update_missing_separator": lambda self, dt: called.append(1),
                              "_ext_unknownhook__x": lambda self, *a: called.append(2)})
        scene._update_extensions(0.1)
        scene._extension_key_down(1)
        assert called == []


@pytest.mark.parametrize("dispatcher,hook,args", [
    ("_extension_key_down", "key_down", (97,)),
    ("_extension_key_up", "key_up", (97,)),
])
def test_key_hooks_reach_every_extension_and_never_swallow(game, dispatcher, hook, args):
    with _stub_kivy(game):
        seen = []
        scene = _scene(game, {f"_ext_{hook}__aaa": lambda self, key: seen.append(("aaa", key)),
                              f"_ext_{hook}__bbb": lambda self, key: seen.append(("bbb", key))})
        assert getattr(scene, dispatcher)(*args) is None
        assert seen == [("aaa", 97), ("bbb", 97)]


@pytest.mark.parametrize("dispatcher,hook,args", [
    ("_extension_touch_up", "touch_up", (None, 1, 2, "left")),
    ("_extension_touch_move", "touch_move", (None, 1, 2)),
])
def test_touch_up_and_move_stop_at_the_first_swallow(game, dispatcher, hook, args):
    with _stub_kivy(game):
        seen = []

        def make(name, result):
            return lambda self, *a: (seen.append(name), result)[1]
        scene = _scene(game, {f"_ext_{hook}__aaa": make("aaa", False), f"_ext_{hook}__bbb": make("bbb", True),
                              f"_ext_{hook}__ccc": make("ccc", True)})
        assert getattr(scene, dispatcher)(*args) is True
        assert seen == ["aaa", "bbb"]

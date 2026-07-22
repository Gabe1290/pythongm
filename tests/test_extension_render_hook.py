"""Room-render hook: an extension can draw a room itself (Stage B1).

Actions are enough for most plugins, but the 2.5D raycast view *replaces how a
room is drawn*. This is the seam that makes that possible from an extension
instead of from core — proven here with a fixture extension BEFORE raycast is
moved onto it (Stage B2/B3).

Contract (runtime/extension_hooks.py):
  render_room(room, screen) -> True if it drew the room, False to decline.
A claiming renderer replaces the top-down pass; the draw-event pass still runs
so HUD actions composite on top.
"""
import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

from runtime import extension_hooks  # noqa: E402


@pytest.fixture(autouse=True)
def clean_hooks():
    """Never leak a fixture renderer into other tests — it would repaint every
    room in the suite. RESTORE (don't just clear) on the way out: real
    extensions (raycast_2_5d) register once per process via load_all_plugins,
    so leaving the registry empty would silently strip their rendering from
    every later test in the same run."""
    saved = extension_hooks.get_room_renderers()
    extension_hooks.clear_room_renderers()
    yield
    extension_hooks.clear_room_renderers()
    for func in saved:
        extension_hooks.register_room_renderer(func)


# --- The registry itself ---------------------------------------------------

def test_registered_renderer_is_called_and_can_claim():
    calls = []

    def renderer(room, screen):
        calls.append(room)
        return True

    extension_hooks.register_room_renderer(renderer)
    assert extension_hooks.render_room("ROOM", "SCREEN") is True
    assert calls == ["ROOM"]


def test_declining_renderer_falls_through():
    extension_hooks.register_room_renderer(lambda room, screen: False)
    assert extension_hooks.render_room(None, None) is False


def test_first_claimer_wins_and_later_ones_are_not_called():
    order = []

    def first(room, screen):
        order.append("first")
        return True

    def second(room, screen):           # must not run
        order.append("second")
        return True

    extension_hooks.register_room_renderer(first)
    extension_hooks.register_room_renderer(second)
    assert extension_hooks.render_room(None, None) is True
    assert order == ["first"]


def test_a_raising_renderer_cannot_take_the_game_down():
    """A broken extension must not crash the engine — it's skipped and the
    engine falls back to its own rendering."""
    def broken(room, screen):
        raise RuntimeError("extension bug")

    extension_hooks.register_room_renderer(broken)
    assert extension_hooks.render_room(None, None) is False


def test_registration_is_idempotent_and_guards_non_callables():
    def renderer(room, screen):
        return False

    extension_hooks.register_room_renderer(renderer)
    extension_hooks.register_room_renderer(renderer)      # loader may re-run
    extension_hooks.register_room_renderer("not callable")
    assert extension_hooks.get_room_renderers() == [renderer]


def test_get_room_renderers_returns_a_copy():
    extension_hooks.register_room_renderer(lambda r, s: False)
    got = extension_hooks.get_room_renderers()
    got.clear()
    assert len(extension_hooks.get_room_renderers()) == 1


# --- Loading a renderer from a real extension folder -----------------------

def test_extension_folder_can_declare_a_room_renderer(tmp_path):
    """PLUGIN_ROOM_RENDERERS is declarative, like PLUGIN_ACTIONS — no import
    side effects needed to hook in."""
    from events.plugin_loader import PluginLoader

    folder = tmp_path / "demo_renderer"
    folder.mkdir()
    (folder / "extension.json").write_text(json.dumps({
        "name": "Demo Renderer", "version": "1.0.0"}), encoding="utf-8")
    (folder / "__init__.py").write_text(textwrap.dedent("""
        def render_room(room, screen):
            return False
        PLUGIN_ROOM_RENDERERS = [render_room]
    """), encoding="utf-8")

    assert PluginLoader().load_extensions_from_directory(tmp_path) == 1
    assert len(extension_hooks.get_room_renderers()) == 1


# --- End to end through the real engine ------------------------------------

def _room():
    """A minimal GameRoom without running a whole game."""
    from runtime.game_runner import GameRoom
    return GameRoom("r", {"width": 320, "height": 240, "instances": []})


def test_room_has_extension_state():
    """Extensions stash per-room state here instead of adding attributes to
    engine classes."""
    room = _room()
    assert room.extension_state == {}
    room.extension_state["my_ext"] = {"enabled": True}
    assert _room().extension_state == {}, "state must be per-room, not shared"


def test_claiming_renderer_replaces_the_top_down_pass():
    """The engine must not also draw its normal view underneath."""
    room = _room()
    painted = {}

    def renderer(r, screen):
        screen.fill((7, 11, 13))
        painted["yes"] = True
        return True

    extension_hooks.register_room_renderer(renderer)
    screen = pygame.Surface((320, 240))
    drew_normally = {"bg": False}
    room._render_bg_layers = lambda *a, **k: drew_normally.update(bg=True)

    room._render_room(screen, (0, 0))

    assert painted.get("yes"), "extension renderer was not called"
    assert screen.get_at((5, 5))[:3] == (7, 11, 13)
    assert not drew_normally["bg"], "engine drew its own pass over an extension's"


def test_draw_events_still_composite_over_an_extension_render():
    """HUD actions must still land on top — the same guarantee the built-in
    raycast view gets."""
    room = _room()
    composited = {"n": 0}
    room._render_draw_events = lambda screen: composited.update(n=composited["n"] + 1)
    extension_hooks.register_room_renderer(lambda r, s: True)

    room._render_room(pygame.Surface((320, 240)), (0, 0))
    assert composited["n"] == 1, "draw-event pass did not run after an extension render"


def test_declining_renderer_leaves_normal_rendering_intact():
    room = _room()
    extension_hooks.register_room_renderer(lambda r, s: False)
    drew = {"bg": False}
    room._render_bg_layers = lambda *a, **k: drew.update(bg=True)
    room.bg_layers = [{"background": "x"}]

    room._render_room(pygame.Surface((320, 240)), (0, 0))
    assert drew["bg"], "engine should render normally when no extension claims the room"


def test_no_renderers_registered_is_the_untouched_path():
    """The overwhelmingly common case: nothing registered, zero behaviour
    change for every existing game."""
    assert extension_hooks.get_room_renderers() == []
    room = _room()
    drew = {"bg": False}
    room._render_bg_layers = lambda *a, **k: drew.update(bg=True)
    room.bg_layers = [{"background": "x"}]
    room._render_room(pygame.Surface((320, 240)), (0, 0))
    assert drew["bg"]

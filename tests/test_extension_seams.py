"""The generic core seams extensions plug into (docs/THYMIO_EXTENSION_PLAN.md
Stage 0).

Each Stage-0 unit adds one seam to core and one section here proving it with
a DUMMY registrant — no Thymio code involved — so a seam bug can never be
confused with a bug in the code that later moves onto it.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# 0.1 — Instance.extension_state
# ---------------------------------------------------------------------------

def _instance(name="obj_a"):
    from runtime.instance import GameInstance
    return GameInstance(name, 0, 0, {}, action_executor=None)


def test_instance_has_empty_extension_state_by_default():
    inst = _instance()
    assert inst.extension_state == {}


def test_instance_extension_state_is_per_instance():
    """A shared class-level dict would leak one robot's state into every
    instance; each instance must own its own mapping."""
    a, b = _instance("obj_a"), _instance("obj_b")
    a.extension_state["dummy"] = {"hp": 3}
    assert b.extension_state == {}
    assert a.extension_state is not b.extension_state


def test_instance_extension_state_mirrors_room_pattern():
    """Same shape as GameRoom.extension_state so an extension namespaces the
    two identically (room.extension_state['x'] / inst.extension_state['x'])."""
    from runtime.game_runner import GameRoom
    room = GameRoom("r", {"width": 64, "height": 64}, action_executor=None)
    inst = _instance()
    assert type(inst.extension_state) is type(room.extension_state) is dict


# ---------------------------------------------------------------------------
# 0.2 — PLUGIN_INSTANCE_OVERLAYS
# ---------------------------------------------------------------------------

import pytest


@pytest.fixture
def clean_overlays():
    from runtime import extension_hooks
    saved = extension_hooks.get_instance_overlays()
    extension_hooks.clear_instance_overlays()
    yield extension_hooks
    extension_hooks.clear_instance_overlays()
    for f in saved:
        extension_hooks.register_instance_overlay(f)


def test_instance_overlay_registry_is_idempotent_and_skips_bad_input(clean_overlays):
    hooks = clean_overlays

    def ov(instance, screen):
        pass

    hooks.register_instance_overlay(ov)
    hooks.register_instance_overlay(ov)          # loader may re-run
    hooks.register_instance_overlay("nope")      # logged, not registered
    assert hooks.get_instance_overlays() == [ov]


def test_run_instance_overlays_offers_to_all_and_survives_a_raise(clean_overlays):
    hooks = clean_overlays
    seen = []

    def broken(instance, screen):
        raise RuntimeError("boom")

    def good(instance, screen):
        seen.append(instance)

    hooks.register_instance_overlay(broken)
    hooks.register_instance_overlay(good)
    inst = _instance()
    hooks.run_instance_overlays(inst, object())
    assert seen == [inst], "a raising overlay must not stop the next one"


def test_loader_registers_plugin_instance_overlays(clean_overlays):
    from events.plugin_loader import PluginLoader

    def ov(instance, screen):
        pass

    assert PluginLoader._load_instance_overlays(object.__new__(PluginLoader), [ov]) == 1
    assert ov in clean_overlays.get_instance_overlays()


def test_game_runner_render_offers_every_instance_to_overlays(clean_overlays):
    """Drive the real GameRunner.render on a minimal stand-in: every instance
    of the current room reaches the overlay, after the room is drawn and
    with the real screen surface."""
    import pygame
    from types import SimpleNamespace
    from runtime.game_runner import GameRunner

    pygame.display.init()
    screen = pygame.display.set_mode((32, 32))
    order = []
    a, b = _instance("obj_a"), _instance("obj_b")
    room = SimpleNamespace(
        instances=[a, b],
        update_views=lambda: order.append("views"),
        render=lambda s: order.append("room"),
    )
    fake = SimpleNamespace(screen=screen, current_room=room,
                           update_caption=lambda: None)

    got = []
    clean_overlays.register_instance_overlay(
        lambda inst, s: got.append((inst, s)))
    try:
        GameRunner.render(fake)
    finally:
        pygame.display.quit()

    assert order == ["views", "room"]
    assert [i for i, _ in got] == [a, b]
    assert all(s is screen for _, s in got)


# ---------------------------------------------------------------------------
# 0.3 — PLUGIN_INPUT_HANDLERS
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_input():
    from runtime import extension_hooks
    saved = extension_hooks.get_input_handlers()
    extension_hooks.clear_input_handlers()
    yield extension_hooks
    extension_hooks.clear_input_handlers()
    for h in saved:
        extension_hooks.register_input_handler(h)


def test_input_registry_validates_and_is_idempotent(clean_input):
    hooks = clean_input
    good = {"key_down": lambda i, k: False}
    hooks.register_input_handler(good)
    hooks.register_input_handler(good)
    hooks.register_input_handler({"bogus": lambda: None})      # unknown kind
    hooks.register_input_handler({"key_up": "not callable"})
    hooks.register_input_handler(["not", "a", "dict"])
    assert hooks.get_input_handlers() == [good]


def test_run_input_aggregates_and_survives_a_raise(clean_input):
    hooks = clean_input
    hooks.register_input_handler({"mouse_down": lambda r, b, x, y: 1 / 0})
    hooks.register_input_handler({"mouse_down": lambda r, b, x, y: True})
    hooks.register_input_handler({"key_up": lambda i, k: None})   # no mouse_down
    assert hooks.run_mouse_down(object(), 1, 0, 0) is True
    assert hooks.run_mouse_up(object(), 1, 0, 0) is False           # nobody handles
    assert hooks.run_key_down(object(), "up") is False


def test_loader_registers_plugin_input_handlers(clean_input):
    from events.plugin_loader import PluginLoader
    h = {"key_down": lambda i, k: True}
    assert PluginLoader._load_input_handlers(object.__new__(PluginLoader), [h]) == 1
    assert h in clean_input.get_input_handlers()


def _runner_with(instances):
    """Minimal stand-in for the InputMixin's `self`, with a room whose
    screen_to_room is the identity."""
    from types import SimpleNamespace
    import pygame
    room = SimpleNamespace(instances=instances,
                           screen_to_room=lambda x, y: (x, y))
    return SimpleNamespace(current_room=room, _thymio_mouse_presses={},
                           thymio_renderer=None,
                           # Core's own Thymio precedence check, still in
                           # place until Stage B2 moves it onto this hook.
                           _handle_thymio_button_press=lambda b, x, y: False,
                           _get_key_name=lambda key: "up" if key == pygame.K_UP else None)


def _instance_with_events(name, events):
    inst = _instance(name)
    inst.object_data = {"events": events}
    inst.keys_pressed = set()
    inst.action_executor = None
    return inst


def test_keyboard_hooks_run_per_instance_in_loop_order(clean_input):
    """key_down/key_up see each instance, interleaved with the engine's own
    per-instance dispatch — so the extension's ordering matches authored
    keyboard events exactly. Orphan instances (no object_data) are skipped
    like everywhere else."""
    import pygame
    from runtime.game_runner import GameRunner
    a = _instance_with_events("obj_a", {})
    b = _instance_with_events("obj_b", {})
    orphan = _instance("obj_gone")
    orphan.keys_pressed = set()
    runner = _runner_with([a, orphan, b])

    seen = []
    clean_input.register_input_handler({
        "key_down": lambda inst, key: seen.append(("down", inst, key)) or True,
        "key_up": lambda inst, key: seen.append(("up", inst, key)),
    })
    GameRunner.handle_keyboard_press(runner, pygame.K_UP)
    GameRunner.handle_keyboard_release(runner, pygame.K_UP)
    assert seen == [("down", a, "up"), ("down", b, "up"),
                    ("up", a, "up"), ("up", b, "up")]


def test_mouse_hooks_swallow_the_click_before_mouse_events(clean_input):
    """A handler returning True on mouse_down/mouse_up stops the engine's
    per-instance mouse dispatch, with raw screen coordinates; returning
    False lets it through untouched."""
    import pygame
    from runtime.game_runner import GameRunner

    fired = []

    class _Exec:
        def execute_action_list(self, inst, actions):
            fired.append(actions)

    inst = _instance_with_events("obj_a", {
        "mouse": {"left_button": {"actions": ["press"]},
                  "left_button_released": {"actions": ["release"]}},
    })
    inst.action_executor = _Exec()
    runner = _runner_with([inst])

    calls = []
    swallow = {"v": True}
    clean_input.register_input_handler({
        "mouse_down": lambda r, b, x, y: calls.append(("down", b, x, y)) or swallow["v"],
        "mouse_up": lambda r, b, x, y: calls.append(("up", b, x, y)) or swallow["v"],
    })
    GameRunner.handle_mouse_press(runner, 1, (12, 34))
    GameRunner.handle_mouse_release(runner, 1, (12, 34))
    assert calls == [("down", 1, 12, 34), ("up", 1, 12, 34)]
    assert fired == [], "swallowed click must not reach mouse events"

    swallow["v"] = False
    GameRunner.handle_mouse_press(runner, 1, (12, 34))
    GameRunner.handle_mouse_release(runner, 1, (12, 34))
    assert fired == [["press"], ["release"]]

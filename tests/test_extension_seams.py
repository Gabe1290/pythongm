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

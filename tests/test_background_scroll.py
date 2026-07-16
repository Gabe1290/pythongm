"""set_background's hspeed/vspeed parameters now actually drive
auto-scroll (deferred-items plan Tier 2 item 6, TODO.md's "Background
auto-scroll on set_background" entry).

execute_set_background_action (runtime/action_executor.py) parsed
hspeed/vspeed but never wrote them anywhere -- GameRoom already has a
fully working bg_hspeed/bg_vspeed-driven scroll renderer
(_render_legacy_background, used by room-config-authored backgrounds and
set_view), so the whole gap was that the action never wired its own
parameters into it. Fixed by writing hspeed/vspeed onto
game_runner.current_room.bg_hspeed/bg_vspeed alongside the existing
tiled_h/tiled_v wiring.

Uses ActionExecutor imported directly from the module file (bypassing
runtime/__init__.py, which imports GameRunner and therefore pygame),
matching test_action_executor.py's established pattern. game_runner is
a minimal stand-in exposing exactly what execute_set_background_action
reads (see MockGameRunner/MockRoom there) plus a real pygame.Surface for
the sprite path, since GameRoom.bg_hspeed/bg_vspeed are plain floats and
don't need a live pygame display.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import import_module_directly, skip_without_pygame

pytestmark = skip_without_pygame

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockInstance:
    def __init__(self):
        self.object_name = "test_object"
        self.x = 0.0
        self.y = 0.0


class MockRoom:
    def __init__(self):
        self.background_surface = None
        self.background_image_name = ""
        self.tile_horizontal = False
        self.tile_vertical = False
        self.bg_hspeed = 0.0
        self.bg_vspeed = 0.0


class MockGameRunner:
    def __init__(self, sprites=None):
        self.current_room = MockRoom()
        self.sprites = sprites or {}
        self.project_data = {'assets': {'backgrounds': {}}}
        self.global_variables = {}


def _sprite_with_surface():
    import pygame
    return SimpleNamespace(surface=pygame.Surface((32, 32)))


class TestSetBackgroundScroll:
    def test_hspeed_vspeed_written_onto_current_room(self):
        runner = MockGameRunner(sprites={'bg_test': _sprite_with_surface()})
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()

        executor.execute_set_background_action(instance, {
            'background': 'bg_test', 'hspeed': 2, 'vspeed': -3,
        })

        assert runner.current_room.bg_hspeed == 2.0
        assert runner.current_room.bg_vspeed == -3.0
        assert runner.current_room.background_surface is not None
        assert runner.current_room.background_image_name == 'bg_test'

    def test_default_hspeed_vspeed_is_zero(self):
        runner = MockGameRunner(sprites={'bg_test': _sprite_with_surface()})
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()

        executor.execute_set_background_action(instance, {'background': 'bg_test'})

        assert runner.current_room.bg_hspeed == 0.0
        assert runner.current_room.bg_vspeed == 0.0

    def test_string_hspeed_vspeed_coerced_to_float(self):
        runner = MockGameRunner(sprites={'bg_test': _sprite_with_surface()})
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()

        executor.execute_set_background_action(instance, {
            'background': 'bg_test', 'hspeed': '1.5', 'vspeed': '2',
        })

        assert runner.current_room.bg_hspeed == 1.5
        assert runner.current_room.bg_vspeed == 2.0

    def test_bad_hspeed_vspeed_falls_back_to_zero_without_crashing(self):
        runner = MockGameRunner(sprites={'bg_test': _sprite_with_surface()})
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()

        executor.execute_set_background_action(instance, {
            'background': 'bg_test', 'hspeed': 'not-a-number', 'vspeed': None,
        })

        assert runner.current_room.bg_hspeed == 0.0
        assert runner.current_room.bg_vspeed == 0.0

    def test_not_visible_does_not_touch_scroll_speed(self):
        runner = MockGameRunner(sprites={'bg_test': _sprite_with_surface()})
        runner.current_room.bg_hspeed = 5.0
        executor = ActionExecutor(game_runner=runner)
        instance = MockInstance()

        executor.execute_set_background_action(instance, {
            'background': 'bg_test', 'visible': False, 'hspeed': 9,
        })

        # Hiding the background shouldn't silently start/change a scroll
        # that has no visible surface to scroll.
        assert runner.current_room.bg_hspeed == 5.0
        assert runner.current_room.background_surface is None


class TestLegacyBackgroundRenderHonorsScroll:
    """End-to-end: the room-level renderer that already existed
    (_render_legacy_background) actually animates once set_background
    wires hspeed/vspeed into it -- not just that the attribute is set."""

    def test_scroll_accumulates_and_wraps_across_frames(self):
        import pygame
        pygame.display.set_mode((1, 1))

        # Import GameRoom directly; runtime/__init__ pulls in the rest of
        # the runtime package, which is fine here since pygame is already
        # a hard dependency of this test module (skip_without_pygame).
        from runtime.game_runner import GameRoom

        room = GameRoom("test_room", {"width": 100, "height": 100})
        room.background_surface = pygame.Surface((20, 20))
        room.background_surface.fill((255, 0, 0))
        room.bg_hspeed = 5.0
        room.bg_vspeed = 0.0

        screen = pygame.Surface((100, 100))
        room._render_legacy_background(screen)
        assert room.bg_scroll_x == 5.0

        room._render_legacy_background(screen)
        assert room.bg_scroll_x == 10.0

        # Wraps modulo the background image width (20px) rather than
        # growing unboundedly.
        for _ in range(3):
            room._render_legacy_background(screen)
        assert room.bg_scroll_x == (10.0 + 5.0 * 3) % 20

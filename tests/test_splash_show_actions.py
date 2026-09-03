"""Regression for docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.5.

splash_show_text / splash_show_image previously had placeholder handlers
that only logged their parameter and did nothing (no ActionType existed
for either, so there was no dead-end UI path -- an internal placeholder
only). Real implementations: splash_show_text reuses the same blocking
modal machinery show_message/show_info already use
(ActionExecutor._show_or_queue_message); splash_show_image reuses the
sprite registry draw_sprite reads from plus a new
GameRunner.show_splash_image blocking loop, the image counterpart of
show_message_dialog.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

from events.action_types import get_action_type  # noqa: E402


def test_both_actions_registered_with_real_descriptions():
    text_action = get_action_type("splash_show_text")
    image_action = get_action_type("splash_show_image")
    assert text_action is not None and image_action is not None
    assert "text" in {p.name for p in text_action.parameters}
    assert "image" in {p.name for p in image_action.parameters}
    image_param = next(p for p in image_action.parameters if p.name == "image")
    assert image_param.param_type == "sprite"


def test_dead_placeholder_handlers_are_gone():
    # extra_handlers.py itself was deleted 2026-09-03 (no-producer sweep in
    # docs/POST_1_0_REFACTOR.md); the guarantee is unchanged -- these dead
    # placeholder handlers must not exist, in that file or any successor.
    path = REPO_ROOT / "runtime" / "action_handlers" / "extra_handlers.py"
    src = path.read_text(encoding="utf-8") if path.exists() else ""
    assert "def handle_splash_show_text" not in src
    assert "def handle_splash_show_image" not in src
    assert '"splash_show_text": handle_splash_show_text' not in src
    assert '"splash_show_image": handle_splash_show_image' not in src


def test_splash_show_text_uses_the_real_handler_and_queues_headlessly():
    """No live screen (headless test) -- _show_or_queue_message falls back
    to instance.pending_messages rather than blocking, so this is safely
    testable without a display."""
    from runtime.action_executor import ActionExecutor

    class _Instance:
        pass

    executor = ActionExecutor()
    instance = _Instance()
    executor.execute_action(instance, {
        "action": "splash_show_text",
        "parameters": {"text": "Hello!"},
    })
    assert getattr(instance, "pending_messages", []) == ["Hello!"]


def test_splash_show_text_empty_is_a_noop():
    from runtime.action_executor import ActionExecutor

    class _Instance:
        pass

    executor = ActionExecutor()
    instance = _Instance()
    executor.execute_action(instance, {"action": "splash_show_text", "parameters": {}})
    assert getattr(instance, "pending_messages", []) == []


def test_splash_show_image_noop_without_a_live_screen():
    """Headless (no runner.screen) -- must not attempt to open pygame
    display machinery, matching every other splash/message action's
    headless-safe behaviour."""
    from runtime.action_executor import ActionExecutor

    class _Runner:
        screen = None
        sprites = {}
        global_variables = {}

    class _Instance:
        pass

    executor = ActionExecutor(game_runner=_Runner())
    instance = _Instance()
    # Call the handler directly (not through execute_action, which swallows
    # AttributeError generically) so a real exception here fails the test
    # instead of masquerading as a correct no-op.
    executor.execute_splash_show_image_action(instance, {"image": "spr_test"})


def test_splash_show_image_calls_show_splash_image_with_the_resolved_surface():
    """With a live screen and a known sprite, splash_show_image must resolve
    the sprite's surface through runner.sprites (the same registry
    draw_sprite reads) and hand it to GameRunner.show_splash_image."""
    import pygame
    from runtime.action_executor import ActionExecutor

    pygame.display.init()
    try:
        screen = pygame.display.set_mode((64, 64))
        surface = pygame.Surface((10, 10))

        class _Sprite:
            frames = []
            surface = None

        sprite = _Sprite()
        sprite.surface = surface

        calls = []

        class _Runner:
            def __init__(self):
                self.screen = screen
                self.sprites = {"spr_test": sprite}
                # _parse_value's bare-name fallback checks this
                # unconditionally once there's no instance attribute match.
                self.global_variables = {}

            def show_splash_image(self, surf):
                calls.append(surf)

        executor = ActionExecutor(game_runner=_Runner())

        class _Instance:
            pass

        executor.execute_action(_Instance(), {
            "action": "splash_show_image",
            "parameters": {"image": "spr_test"},
        })
        assert calls == [surface]
    finally:
        pygame.display.quit()

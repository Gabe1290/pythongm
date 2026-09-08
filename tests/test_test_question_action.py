"""M4, docs/FULL_AUDIT_2026-09-07.md: test_question is always "yes" in the
real game process.

The removed implementation built a QMessageBox and returned True whenever
QApplication.instance() was None -- which is EVERY real game process,
since runtime/run_game.py (the Test Game subprocess, and every desktop
export) never creates a QApplication. Authors got a conditional that
never actually asked.

Fix: GameRunner.show_question_dialog, the pygame-side counterpart of
show_message_dialog (same blocking-loop shape: overlay, centered box,
word-wrapped text, speed-pause/restore, KEYUP forwarding to
_release_held_key_silent per M54), with two buttons instead of one and a
boolean return. execute_test_question_action calls it when there's a
live screen, and only falls back to True when there genuinely is none
(headless).

Two tiers: action-dispatch level (does execute_test_question_action call
show_question_dialog and return exactly what it returns, using the same
stubbed-runner pattern tests/test_splash_show_actions.py established for
splash_show_image), then GameRunner.show_question_dialog itself, using
tests/test_audit_game_runner_lifecycle.py's own fully-mocked-pygame
pattern (TestDialogKeyup) -- no real display needed.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


# ---------------------------------------------------------------------------
# Action-dispatch level
# ---------------------------------------------------------------------------

class TestExecuteTestQuestionAction:
    def test_calls_show_question_dialog_with_a_live_screen_and_returns_its_answer(self):
        from runtime.action_executor import ActionExecutor

        calls = []

        class _Runner:
            def __init__(self):
                self.screen = object()  # any truthy "there is a live screen"
                self.global_variables = {}

            def show_question_dialog(self, question):
                calls.append(question)
                return True

        class _Instance:
            pass

        executor = ActionExecutor(game_runner=_Runner())
        result = executor.execute_action(_Instance(), {
            "action": "test_question",
            "parameters": {"question": "Continue?"},
        })

        assert calls == ["Continue?"]
        assert result is True

    def test_returns_false_when_the_dialog_answers_no(self):
        from runtime.action_executor import ActionExecutor

        class _Runner:
            def __init__(self):
                self.screen = object()
                self.global_variables = {}

            def show_question_dialog(self, question):
                return False

        class _Instance:
            pass

        executor = ActionExecutor(game_runner=_Runner())
        result = executor.execute_action(_Instance(), {
            "action": "test_question",
            "parameters": {"question": "Quit?"},
        })

        assert result is False

    def test_defaults_to_true_without_a_live_screen(self):
        """Headless (no runner.screen) -- must not attempt to open pygame
        display machinery, matching every other splash/message action's
        headless-safe behaviour, and must not silently answer via some
        stale Qt fallback."""
        from runtime.action_executor import ActionExecutor

        class _Runner:
            screen = None
            global_variables = {}

        class _Instance:
            pass

        executor = ActionExecutor(game_runner=_Runner())
        result = executor.execute_action(_Instance(), {
            "action": "test_question",
            "parameters": {"question": "Continue?"},
        })

        assert result is True

    def test_defaults_to_true_with_no_game_runner_at_all(self):
        from runtime.action_executor import ActionExecutor

        class _Instance:
            pass

        executor = ActionExecutor(game_runner=None)
        result = executor.execute_action(_Instance(), {
            "action": "test_question",
            "parameters": {"question": "Continue?"},
        })

        assert result is True

    def test_default_question_text_when_none_given(self):
        from runtime.action_executor import ActionExecutor

        calls = []

        class _Runner:
            def __init__(self):
                self.screen = object()
                self.global_variables = {}

            def show_question_dialog(self, question):
                calls.append(question)
                return True

        class _Instance:
            pass

        executor = ActionExecutor(game_runner=_Runner())
        executor.execute_action(_Instance(), {"action": "test_question", "parameters": {}})

        assert calls == ["Continue?"]


# ---------------------------------------------------------------------------
# GameRunner.show_question_dialog itself -- fully mocked pygame, no display.
# Pattern from tests/test_audit_game_runner_lifecycle.py's TestDialogKeyup
# (the same M54 modal-dialog KEYUP-forwarding precedent this dialog reuses).
# ---------------------------------------------------------------------------

def _make_runner():
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            runner = GameRunner.__new__(GameRunner)
            runner.action_executor = MagicMock()
            runner.current_room = None
            return runner


def _fake_pygame(events_by_iteration):
    """A MagicMock pygame with just what show_question_dialog touches,
    yielding the given event lists in order (then an empty list forever)."""
    fake_pygame = MagicMock()
    fake_pygame.QUIT = 256
    fake_pygame.KEYDOWN = 768
    fake_pygame.KEYUP = 769
    fake_pygame.MOUSEBUTTONDOWN = 1025
    fake_pygame.K_RETURN = 13
    fake_pygame.K_ESCAPE = 27
    fake_pygame.K_y = 121
    fake_pygame.K_n = 110

    fake_pygame.event.get.side_effect = list(events_by_iteration) + [[]] * 5

    fake_font = MagicMock()
    fake_font.size.return_value = (10, 10)
    rendered = MagicMock()
    rendered.get_width.return_value = 10
    rendered.get_height.return_value = 10
    fake_font.render.return_value = rendered
    fake_pygame.font.Font.return_value = fake_font
    fake_pygame.font.SysFont.return_value = fake_font
    fake_pygame.mouse.get_pos.return_value = (0, 0)
    return fake_pygame


class TestShowQuestionDialog:
    def test_enter_answers_yes(self):
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()

        dismiss_evt = SimpleNamespace(type=768, key=13)  # KEYDOWN RETURN
        fake_pygame = _fake_pygame([[dismiss_evt]])

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                with patch.object(gr.GameRunner, '_frame_budget', return_value=0):
                    result = runner.show_question_dialog("Continue?")

        assert result is True

    def test_y_key_answers_yes(self):
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()

        dismiss_evt = SimpleNamespace(type=768, key=121)  # KEYDOWN 'y'
        fake_pygame = _fake_pygame([[dismiss_evt]])

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                with patch.object(gr.GameRunner, '_frame_budget', return_value=0):
                    result = runner.show_question_dialog("Continue?")

        assert result is True

    def test_escape_answers_no(self):
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()

        dismiss_evt = SimpleNamespace(type=768, key=27)  # KEYDOWN ESCAPE
        fake_pygame = _fake_pygame([[dismiss_evt]])

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                with patch.object(gr.GameRunner, '_frame_budget', return_value=0):
                    result = runner.show_question_dialog("Quit?")

        assert result is False

    def test_n_key_answers_no(self):
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()

        dismiss_evt = SimpleNamespace(type=768, key=110)  # KEYDOWN 'n'
        fake_pygame = _fake_pygame([[dismiss_evt]])

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                with patch.object(gr.GameRunner, '_frame_budget', return_value=0):
                    result = runner.show_question_dialog("Continue?")

        assert result is False

    def test_keyup_forwards_to_release_held_key_silent_without_answering(self):
        """Same M54 contract show_message_dialog already has: a KEYUP
        arriving while the dialog is open must not get lost, but must not
        answer the question either."""
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()

        keyup_evt = SimpleNamespace(type=769, key=100)   # KEYUP, some key
        dismiss_evt = SimpleNamespace(type=768, key=13)  # KEYDOWN RETURN
        fake_pygame = _fake_pygame([[keyup_evt, dismiss_evt]])

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                with patch.object(gr.GameRunner, '_frame_budget', return_value=0):
                    result = runner.show_question_dialog("Continue?")

        runner._release_held_key_silent.assert_called_once_with(100)
        assert result is True

    def test_no_screen_defaults_to_true(self):
        runner = _make_runner()
        runner.screen = None

        assert runner.show_question_dialog("Continue?") is True

    def test_frame_budget_auto_dismisses_to_true(self):
        """Same contract as show_message_dialog's own frame-budget
        auto-dismiss: a headless verification run has no real input to
        answer with (tools/verify_desktop_export.py's PYGM_MAX_FRAMES)."""
        import runtime.game_runner as gr

        runner = _make_runner()
        runner.screen = MagicMock()

        with patch.object(gr.GameRunner, '_frame_budget', return_value=5):
            result = runner.show_question_dialog("Continue?")

        assert result is True

    def test_instance_speeds_are_paused_then_restored(self):
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()

        inst = SimpleNamespace(hspeed=4.0, vspeed=-2.0, render=lambda *a, **k: None)
        room = MagicMock()
        room.instances = [inst]
        runner.current_room = room

        dismiss_evt = SimpleNamespace(type=768, key=13)
        fake_pygame = _fake_pygame([[dismiss_evt]])

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                with patch.object(gr.GameRunner, '_frame_budget', return_value=0):
                    runner.show_question_dialog("Continue?")

        assert inst.hspeed == 4.0
        assert inst.vspeed == -2.0

#!/usr/bin/env python3
"""Score, lives and health actions for
:class:`~runtime.action_executor.ActionExecutor`.

The eight methods that read or write the three player-progress counters: the
three setters (which also drive the window-caption display and the
no_more_lives / no_more_health crossings), the three test_* conditionals, and
the high-score screen pair.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 3) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

The cluster is unusually self-contained: it calls no other ``ActionExecutor``
method at all, and touches only ``self.game_runner``. Its one module-level
dependency, ``_hex_to_rgb``, moved to ``runtime/action_colors.py`` in the same
commit -- ``set_draw_color`` (still on the base) uses it too, so neither module
can own it without the other importing back through a cycle.
"""

from typing import Any, Dict

from runtime.action_colors import _hex_to_rgb
from core.logger import get_logger

logger = get_logger(__name__)


class ScoreLivesHealthMixin:
    """Score / lives / health ``execute_*_action`` methods."""

    def execute_set_score_action(self, instance, parameters: Dict[str, Any]):
        """Set the score value"""
        if not self.game_runner:
            logger.warning("⚠️  Warning: set_score requires game_runner reference")
            return

        value = int(parameters.get("value", 0))
        relative = parameters.get("relative", False)

        if relative:
            self.game_runner.score += value
        else:
            self.game_runner.score = value

        # Auto-enable score in caption when score is used
        self.game_runner.show_score_in_caption = True

        logger.debug(f"🏆 Score set to: {self.game_runner.score}")
    def execute_test_score_action(self, instance, parameters: Dict[str, Any]):
        """Test score value and execute conditional actions

        Returns True if condition met, False otherwise
        """
        if not self.game_runner:
            return False

        value = int(parameters.get("value", 0))
        operation = parameters.get("operation", "equal")

        current_score = self.game_runner.score

        # Evaluate comparison
        result = False
        if operation == "equal":
            result = current_score == value
        elif operation == "less":
            result = current_score < value
        elif operation == "greater":
            result = current_score > value
        elif operation == "less_equal":
            result = current_score <= value
        elif operation == "greater_equal":
            result = current_score >= value
        elif operation == "not_equal":
            result = current_score != value

        return result
    def execute_set_lives_action(self, instance, parameters: Dict[str, Any]):
        """Set the lives value"""
        if not self.game_runner:
            logger.warning("⚠️  Warning: set_lives requires game_runner reference")
            return

        value = int(parameters.get("value", 3))
        relative = parameters.get("relative", False)

        old_lives = self.game_runner.lives

        if relative:
            self.game_runner.lives += value
        else:
            self.game_runner.lives = value

        # Ensure lives doesn't go negative
        self.game_runner.lives = max(0, self.game_runner.lives)

        # Auto-enable lives in caption when lives are used
        self.game_runner.show_lives_in_caption = True

        logger.debug(f"❤️  Lives set to: {self.game_runner.lives}")

        # Trigger no_more_lives event if lives just reached 0
        if old_lives > 0 and self.game_runner.lives <= 0:
            logger.debug("💀 No more lives! Triggering no_more_lives event...")
            self.game_runner.trigger_no_more_lives_event(instance)
    def execute_test_lives_action(self, instance, parameters: Dict[str, Any]):
        """Test lives value and execute conditional actions"""
        if not self.game_runner:
            return False

        value = int(parameters.get("value", 0))
        operation = parameters.get("operation", "equal")

        current_lives = self.game_runner.lives

        # Evaluate comparison
        result = False
        if operation == "equal":
            result = current_lives == value
        elif operation == "less":
            result = current_lives < value
        elif operation == "greater":
            result = current_lives > value
        elif operation == "less_equal":
            result = current_lives <= value
        elif operation == "greater_equal":
            result = current_lives >= value
        elif operation == "not_equal":
            result = current_lives != value

        return result
    def execute_set_health_action(self, instance, parameters: Dict[str, Any]):
        """Set health value (0-100)"""
        if not self.game_runner:
            logger.warning("⚠️  Warning: set_health requires game_runner reference")
            return

        value = float(parameters.get("value", 100))
        relative = parameters.get("relative", False)

        old_health = self.game_runner.health

        if relative:
            self.game_runner.health += value
        else:
            self.game_runner.health = value

        # Clamp health between 0 and 100
        self.game_runner.health = max(0, min(100, self.game_runner.health))

        # Auto-enable health in caption when health is used
        self.game_runner.show_health_in_caption = True

        logger.debug(f"💚 Health set to: {self.game_runner.health}")

        # Trigger no_more_health event if health just reached 0
        if old_health > 0 and self.game_runner.health <= 0:
            logger.debug("💔 No more health! Triggering no_more_health event...")
            self.game_runner.trigger_no_more_health_event(instance)
    def execute_test_health_action(self, instance, parameters: Dict[str, Any]):
        """Test health value and execute conditional actions"""
        if not self.game_runner:
            return False

        value = float(parameters.get("value", 0))
        operation = parameters.get("operation", "equal")
        # Heal the legacy *_or_equal spellings the editor used to save so
        # already-authored projects keep working (M29).
        if operation == "less_or_equal":
            operation = "less_equal"
        elif operation == "greater_or_equal":
            operation = "greater_equal"

        current_health = self.game_runner.health

        # Evaluate comparison
        result = False
        if operation == "equal":
            result = abs(current_health - value) < 0.001  # Float comparison tolerance
        elif operation == "less":
            result = current_health < value
        elif operation == "greater":
            result = current_health > value
        elif operation == "less_equal":
            result = current_health <= value
        elif operation == "greater_equal":
            result = current_health >= value
        elif operation == "not_equal":
            result = abs(current_health - value) >= 0.001

        return result
    def execute_show_highscore_action(self, instance, parameters: Dict[str, Any]):
        """Show highscore table dialog

        Parameters:
            background: Background color (hex string like "#FFFFDD")
            new_color: Color for new entry (hex string)
            other_color: Color for other entries (hex string)
            allow_new_entry: Whether to prompt for name if score qualifies (default True)
        """
        if not self.game_runner:
            return

        # Parse color parameters (GameMaker uses BGR format, we use RGB)
        background = _hex_to_rgb(parameters.get('background'), (255, 255, 220))
        new_color = _hex_to_rgb(parameters.get('new_color'), (255, 0, 0))
        other_color = _hex_to_rgb(parameters.get('other_color'), (0, 0, 0))
        allow_new_entry = parameters.get('allow_new_entry', True)

        logger.debug(f"🏆 Show highscore action - current score: {self.game_runner.score}")

        # Show the dialog
        self.game_runner.show_highscore_dialog(
            background_color=background,
            new_color=new_color,
            other_color=other_color,
            allow_name_entry=allow_new_entry
        )
    def execute_clear_highscore_action(self, instance, parameters: Dict[str, Any]):
        """Clear highscore table"""
        if not self.game_runner:
            return

        self.game_runner.clear_highscores()

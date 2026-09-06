#!/usr/bin/env python3
"""Dialog, splash and system actions for
:class:`~runtime.action_executor.ActionExecutor`.

The actions that interrupt or step outside the game loop: the message and info
dialogs, the two splash screens (text and image), video playback, opening a web
page, sleep and delay, and the window caption. ``_show_or_queue_message`` is
the shared worker that either shows a dialog now or queues it, depending on
whether the runner is in a state that can block.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 10) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

Everything heavy here -- ``pygame``, ``webbrowser``, ``subprocess``, ``os``,
``sys``, ``pathlib.Path`` -- is imported *inside* the individual methods, as it
was before the move. That is what lets this module, like the engine module it
came from, be imported without pygame.

``SLEEP_MAX_MS`` stays a class attribute on ``ActionExecutor`` and is reached
through ``self``; it is a cap the base owns, not a drawing-time constant.
"""

from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


class DialogSystemMixin:
    """Dialog / splash / system ``execute_*_action`` methods."""

    def _show_or_queue_message(self, instance, message):
        """Display a message dialog in authored action order.

        Shown **synchronously** (blocking) when a live screen is available, so
        message-style actions (show_message, show_info) appear in the order the
        user placed them — matching show_highscore, which already shows
        immediately. Queuing them into ``pending_messages`` (drained by the
        game loop after the event) made them appear *after* any same-event
        immediate dialog, inverting the order. Falls back to the queue when
        there is no live screen yet (headless runs / tests).
        """
        runner = self.game_runner
        if (runner is not None and getattr(runner, 'screen', None) is not None
                and hasattr(runner, 'show_message_dialog')):
            runner.show_message_dialog(message)
            return

        if not hasattr(instance, 'pending_messages'):
            instance.pending_messages = []
        instance.pending_messages.append(message)
    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action with optional translation support."""
        message = self.localize_param(parameters, "message", "")

        logger.debug(f"💬 MESSAGE: {message}")
        self._show_or_queue_message(instance, message)
    def execute_delay_action_action(self, instance, parameters: Dict[str, Any]):
        """Execute an action after a delay (in frames)

        Parameters:
            frames: Number of frames to wait before executing the action
            then_action: The action to execute after the delay (e.g., "change_room", "next_room")
            room_name: Room name for change_room action (optional)
            (other parameters are passed to the delayed action)
        """
        frames = parameters.get("frames", 60)
        then_action = parameters.get("then_action", "")

        try:
            frames = int(frames)
        except (ValueError, TypeError):
            frames = 60

        if not then_action:
            logger.warning("⚠️ delay_action: No then_action specified")
            return

        # _delayed_actions is now eagerly initialised in GameInstance.__init__,
        # so no lazy-init guard is needed here.

        # Store the delayed action with remaining frames and parameters
        delayed = {
            'frames_remaining': frames,
            'action': then_action,
            'parameters': parameters.copy()
        }
        instance._delayed_actions.append(delayed)

        logger.debug(f"⏱️ Scheduled {then_action} action in {frames} frames for {instance.object_name}")
    def execute_sleep_action(self, instance, parameters: Dict[str, Any]):
        """Pause the game for a number of milliseconds, then continue.

        This is a *blocking* pause (pygame.time.delay): rendering and input are
        frozen for the duration. Sounds play on independent mixer channels, so
        they keep playing through the sleep — the intended use is letting a sound
        finish before the next action (e.g. a room change) cuts it off.

        Parameters:
            milliseconds (or ms / duration): how long to pause; clamped to
                [0, SLEEP_MAX_MS]. Accepts a number, variable, or expression.
        """
        ms_param = parameters.get(
            "milliseconds", parameters.get("ms", parameters.get("duration", 1000))
        )

        ms = self._parse_value(str(ms_param), instance)
        if not isinstance(ms, (int, float)):
            logger.warning(f"⚠️ sleep: Invalid milliseconds value '{ms_param}', defaulting to 1000")
            ms = 1000
        ms = int(ms)

        if ms <= 0:
            return

        if ms > self.SLEEP_MAX_MS:
            logger.warning(
                f"⚠️ sleep: {ms}ms exceeds the {self.SLEEP_MAX_MS}ms cap; clamping"
            )
            ms = self.SLEEP_MAX_MS

        try:
            import pygame
            pygame.time.delay(ms)
        except Exception as e:
            logger.warning(f"⚠️ sleep: could not delay ({e})")
    def execute_set_window_caption_action(self, instance, parameters: Dict[str, Any]):
        """Set game window caption settings (score/lives/health display)"""
        if not self.game_runner:
            return

        # Update caption display settings on game_runner
        self.game_runner.show_score_in_caption = parameters.get("show_score", True)
        self.game_runner.show_lives_in_caption = parameters.get("show_lives", True)
        self.game_runner.show_health_in_caption = parameters.get("show_health", False)
        self.game_runner.window_caption = parameters.get("caption", "")

        logger.debug(f"🪟 Caption settings updated: score={self.game_runner.show_score_in_caption}, "
              f"lives={self.game_runner.show_lives_in_caption}, health={self.game_runner.show_health_in_caption}")
    def execute_show_info_action(self, instance, parameters: Dict[str, Any]):
        """Display game information screen

        Shows the game info defined in project settings.
        In GameMaker, this displays an RTF document with game information.
        We'll show a simple info dialog with project metadata.
        """
        if not self.game_runner or not self.game_runner.project_data:
            logger.debug("⚠️ show_info: No project data available")
            return

        # Get game info from project data
        project = self.game_runner.project_data
        name = project.get('name', 'Unknown Game')
        version = project.get('version', '1.0.0')
        author = project.get('author', 'Unknown')
        description = project.get('description', '')

        # Build info message
        info_text = f"{name}\nVersion: {version}\nBy: {author}"
        if description:
            info_text += f"\n\n{description}"

        logger.debug(f"ℹ️ GAME INFO:\n{info_text}")
        self._show_or_queue_message(instance, info_text)
    def execute_splash_show_text_action(self, instance, parameters: Dict[str, Any]):
        """Show a blocking text message -- reuses the same modal machinery
        show_message/show_info already use, rather than the old placeholder
        that only logged the text and did nothing (see
        docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.5).

        Parameters:
            text: the message to show
        """
        text = self._parse_value(parameters.get("text", ""), instance)
        if not text:
            logger.debug("⚠️ splash_show_text: No text specified")
            return
        logger.debug(f"💬 SPLASH TEXT: {text}")
        self._show_or_queue_message(instance, str(text))
    def execute_splash_show_image_action(self, instance, parameters: Dict[str, Any]):
        """Show a sprite full-screen, blocking until dismissed -- reuses the
        same sprite registry draw_sprite reads from and
        GameRunner.show_splash_image's blocking-loop shape (mirrors
        show_message_dialog). Replaces the old placeholder that only
        logged the image name (Tier 2.5).

        Parameters:
            image: name of the sprite to show full-screen
        """
        image_name = self._parse_value(parameters.get("image", ""), instance)
        if not image_name:
            logger.debug("⚠️ splash_show_image: No image specified")
            return

        runner = self.game_runner
        if runner is None or not getattr(runner, 'screen', None):
            logger.debug("⚠️ splash_show_image: No live screen (headless) -- no-op")
            return

        sprite = runner.sprites.get(str(image_name))
        if sprite is None:
            logger.warning(f"⚠️ splash_show_image: Sprite '{image_name}' not found")
            return

        surface = sprite.frames[0] if sprite.frames else sprite.surface
        if surface is None:
            logger.warning(f"⚠️ splash_show_image: Sprite '{image_name}' has no surface")
            return

        logger.debug(f"🖼️ SPLASH IMAGE: {image_name}")
        runner.show_splash_image(surface)
    def execute_show_video_action(self, instance, parameters: Dict[str, Any]):
        """Play a video file

        Parameters:
            filename: Path to the video file
            fullscreen: Whether to play in fullscreen mode

        Note: Video playback requires additional libraries (moviepy/opencv).
        This implementation logs the request but actual playback may be limited.
        """
        from pathlib import Path

        filename = self._parse_value(parameters.get("filename", ""), instance)
        fullscreen = self._parse_value(parameters.get("fullscreen", False), instance)

        if not filename:
            logger.debug("⚠️ show_video: No filename specified")
            return

        # Convert to boolean if string
        if isinstance(fullscreen, str):
            fullscreen = fullscreen.lower() in ('true', '1', 'yes')

        # Resolve the file path
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ show_video: Video file not found: {file_path}")
            return

        logger.debug(f"🎬 Video playback requested: {file_path} (fullscreen={fullscreen})")

        # Try to play video using available methods
        try:
            # Attempt to use system default video player
            import sys
            import subprocess

            if sys.platform == 'win32':
                import os
                os.startfile(str(file_path))
            elif sys.platform == 'darwin':
                subprocess.call(['open', str(file_path)])
            else:
                subprocess.call(['xdg-open', str(file_path)])

            logger.debug(f"🎬 Opened video with system player: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not play video: {e}")
    def execute_open_webpage_action(self, instance, parameters: Dict[str, Any]):
        """Open a URL in the default web browser

        Parameters:
            url: The web address to open
        """
        import webbrowser

        url = self._parse_value(parameters.get("url", ""), instance)

        if not url:
            logger.debug("⚠️ open_webpage: No URL specified")
            return

        # Ensure URL has a protocol
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url

        logger.debug(f"🌐 Opening web page: {url}")

        try:
            webbrowser.open(url)
        except Exception as e:
            logger.warning(f"⚠️ Could not open web page: {e}")

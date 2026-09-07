#!/usr/bin/env python3
"""
Audio Actions Plugin
Adds sound and music actions to PyGameMaker
"""

from events.action_types import ActionType, ActionParameter

from core.logger import get_logger

logger = get_logger(__name__)

# Plugin Metadata
PLUGIN_NAME = "Audio Actions"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "PyGameMaker Team"
PLUGIN_DESCRIPTION = "Adds sound effects and music actions"

# Define audio actions
PLUGIN_ACTIONS = {
    "play_sound": ActionType(
        name="play_sound",
        display_name="Play Sound",
        description="Play a sound effect once",
        category="Audio",
        icon="🔊",
        parameters=[
            ActionParameter(
                name="sound",
                display_name="Sound",
                param_type="sound",
                default_value="",
                description="Sound to play"
            ),
            ActionParameter(
                name="volume",
                display_name="Volume",
                param_type="float",
                default_value=1.0,
                description="Volume (0.0 to 1.0)",
                min_value=0,
                max_value=1
            )
        ]
    ),

    "stop_sound": ActionType(
        name="stop_sound",
        display_name="Stop Sound",
        description="Stop a playing sound effect",
        category="Audio",
        icon="🔕",
        parameters=[
            ActionParameter(
                name="sound",
                display_name="Sound",
                param_type="sound",
                default_value="",
                description="Sound to stop"
            )
        ]
    ),

    "play_music": ActionType(
        name="play_music",
        display_name="Play Music",
        description="Play background music (looping)",
        category="Audio",
        icon="🎵",
        parameters=[
            ActionParameter(
                name="music",
                display_name="Music",
                param_type="sound",
                default_value="",
                description="Music file to play"
            ),
            ActionParameter(
                name="loop",
                display_name="Loop",
                param_type="boolean",
                default_value=True,
                description="Loop the music"
            ),
            ActionParameter(
                name="volume",
                display_name="Volume",
                param_type="float",
                default_value=0.7,
                description="Volume (0.0 to 1.0)",
                min_value=0,
                max_value=1
            )
        ]
    ),

    "stop_music": ActionType(
        name="stop_music",
        display_name="Stop Music",
        description="Stop background music",
        category="Audio",
        icon="🔇",
        parameters=[]
    ),

    "set_volume": ActionType(
        name="set_volume",
        display_name="Set Volume",
        description="Set global sound/music volume",
        category="Audio",
        icon="🔉",
        parameters=[
            ActionParameter(
                name="volume",
                display_name="Volume",
                param_type="float",
                default_value=1.0,
                description="Volume (0.0 to 1.0)",
                min_value=0,
                max_value=1
            )
        ]
    ),
}


# Action executors
class PluginExecutor:
    """Handles execution of audio actions"""

    def _get_game_runner(self, instance):
        """Get the game runner from instance"""
        if hasattr(instance, 'action_executor') and hasattr(instance.action_executor, 'game_runner'):
            return instance.action_executor.game_runner
        return None

    def _safe_volume(self, instance, parameters, default):
        """Resolve a volume parameter safely (M7, docs/FULL_AUDIT_2026-09-07.md).

        The raw value can be an expression (e.g. a global variable name),
        so it's routed through the action executor's own _parse_value
        first when reachable; either way, the final float() coercion is
        guarded, so a value that is still not a real number (a typo, an
        unresolved expression, a stray string) falls back to `default`
        instead of raising ValueError/TypeError and aborting the action.
        Clamped to pygame's valid 0.0-1.0 range, matching this action's
        own declared min_value/max_value.
        """
        raw = parameters.get("volume", default)
        parse_value = getattr(getattr(instance, "action_executor", None), "_parse_value", None)
        if callable(parse_value):
            try:
                raw = parse_value(raw, instance)
            except Exception:
                pass
        try:
            volume = float(raw)
        except (TypeError, ValueError):
            logger.warning("audio: could not parse volume %r, using default %r", raw, default)
            return default
        return max(0.0, min(1.0, volume))

    def execute_play_sound_action(self, instance, parameters):
        """Play a sound effect"""
        sound_name = parameters.get("sound", "")
        volume = self._safe_volume(instance, parameters, 1.0)

        logger.debug("audio: playing sound %r at volume %s", sound_name, volume)

        try:
            game_runner = self._get_game_runner(instance)
            if game_runner and hasattr(game_runner, 'sounds'):
                if sound_name in game_runner.sounds:
                    sound = game_runner.sounds[sound_name]
                    sound.set_volume(volume)
                    sound.play()
                else:
                    logger.warning("audio: sound not found: %r", sound_name)
            else:
                logger.warning("audio: no game sound system available")
        except Exception as e:
            logger.error("audio: error playing sound: %s", e)

    def execute_play_music_action(self, instance, parameters):
        """Play background music"""
        music_name = parameters.get("music", "")
        loop = parameters.get("loop", True)
        volume = self._safe_volume(instance, parameters, 0.7)

        logger.debug("audio: playing music %r (loop=%s, volume=%s)", music_name, loop, volume)

        try:
            import pygame
            game_runner = self._get_game_runner(instance)
            if game_runner and hasattr(game_runner, 'music_files'):
                if music_name in game_runner.music_files:
                    music_file = game_runner.music_files[music_name]
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(-1 if loop else 0)
                else:
                    logger.warning("audio: music not found: %r", music_name)
            else:
                logger.warning("audio: no game music system available")
        except Exception as e:
            logger.error("audio: error playing music: %s", e)

    def execute_stop_music_action(self, instance, parameters):
        """Stop background music"""
        logger.debug("audio: stopping music")

        try:
            import pygame
            pygame.mixer.music.stop()
        except Exception as e:
            logger.error("audio: error stopping music: %s", e)

    def execute_set_volume_action(self, instance, parameters):
        """Set global volume"""
        volume = self._safe_volume(instance, parameters, 1.0)

        logger.debug("audio: setting volume to %s", volume)

        try:
            import pygame
            # Set music volume
            pygame.mixer.music.set_volume(volume)

            # Set sound volume for all loaded sounds
            game_runner = self._get_game_runner(instance)
            if game_runner and hasattr(game_runner, 'sounds'):
                for sound in game_runner.sounds.values():
                    sound.set_volume(volume)
        except Exception as e:
            logger.error("audio: error setting volume: %s", e)

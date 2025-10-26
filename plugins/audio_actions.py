#!/usr/bin/env python3
"""
Audio Actions Plugin
Adds sound and music actions to PyGameMaker
"""

from events.action_types import ActionType, ActionParameter

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

    def execute_play_sound_action(self, instance, parameters):
        """Play a sound effect"""
        sound_name = parameters.get("sound", "")
        volume = float(parameters.get("volume", 1.0))

        print(f"🔊 Playing sound: {sound_name} at volume {volume}")

        try:
            import pygame
            # Get sound from game manager
            if hasattr(instance, 'game') and hasattr(instance.game, 'sounds'):
                if sound_name in instance.game.sounds:
                    sound = instance.game.sounds[sound_name]
                    sound.set_volume(volume)
                    sound.play()
                else:
                    print(f"⚠️  Sound not found: {sound_name}")
            else:
                print("⚠️  No game sound system available")
        except Exception as e:
            print(f"❌ Error playing sound: {e}")

    def execute_play_music_action(self, instance, parameters):
        """Play background music"""
        music_name = parameters.get("music", "")
        loop = parameters.get("loop", True)
        volume = float(parameters.get("volume", 0.7))

        print(f"🎵 Playing music: {music_name} (loop={loop}, volume={volume})")

        try:
            import pygame
            # Music is handled differently in pygame
            if hasattr(instance, 'game') and hasattr(instance.game, 'music_files'):
                if music_name in instance.game.music_files:
                    music_file = instance.game.music_files[music_name]
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(-1 if loop else 0)
                else:
                    print(f"⚠️  Music not found: {music_name}")
            else:
                print("⚠️  No game music system available")
        except Exception as e:
            print(f"❌ Error playing music: {e}")

    def execute_stop_music_action(self, instance, parameters):
        """Stop background music"""
        print("🔇 Stopping music")

        try:
            import pygame
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"❌ Error stopping music: {e}")

    def execute_set_volume_action(self, instance, parameters):
        """Set global volume"""
        volume = float(parameters.get("volume", 1.0))

        print(f"🔉 Setting volume to {volume}")

        try:
            import pygame
            # Set music volume
            pygame.mixer.music.set_volume(volume)

            # Set sound volume for all loaded sounds
            if hasattr(instance, 'game') and hasattr(instance.game, 'sounds'):
                for sound in instance.game.sounds.values():
                    sound.set_volume(volume)
        except Exception as e:
            print(f"❌ Error setting volume: {e}")

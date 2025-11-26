#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Main2 Actions
"""

from actions.core import ActionDefinition, ActionParameter


# TAB 3: MAIN2 ACTIONS
# ============================================================================

MAIN2_ACTIONS = {
    "set_sprite": ActionDefinition(
        name="set_sprite",
        display_name="Set Sprite",
        category="appearance",
        tab="main2",
        description="Change the sprite",
        icon="🖼️",
        parameters=[
            ActionParameter("sprite", "sprite", "Sprite", "New sprite to display"),
            ActionParameter("subimage", "int", "Subimage", "Frame index", default=0),
            ActionParameter("speed", "float", "Speed", "Animation speed", default=1.0)
        ]
    ),
    "transform_sprite": ActionDefinition(
        name="transform_sprite",
        display_name="Transform Sprite",
        category="appearance",
        tab="main2",
        description="Scale and rotate sprite",
        icon="🔄",
        parameters=[
            ActionParameter("xscale", "float", "X Scale", "Horizontal scale", default=1.0),
            ActionParameter("yscale", "float", "Y Scale", "Vertical scale", default=1.0),
            ActionParameter("angle", "float", "Rotation", "Rotation angle", default=0.0)
        ]
    ),
    "set_color": ActionDefinition(
        name="set_color",
        display_name="Set Color",
        category="appearance",
        tab="main2",
        description="Colorize the sprite",
        icon="🎨",
        parameters=[
            ActionParameter("color", "color", "Color", "Blend color", default="#FFFFFF"),
            ActionParameter("alpha", "float", "Alpha", "Transparency (0-1)", default=1.0)
        ]
    ),
    "play_sound": ActionDefinition(
        name="play_sound",
        display_name="Play Sound",
        category="audio",
        tab="main2",
        description="Play a sound effect",
        icon="🔊",
        parameters=[
            ActionParameter("sound", "sound", "Sound", "Sound to play"),
            ActionParameter("loop", "boolean", "Loop", "Loop sound", default=False)
        ]
    ),
    "stop_sound": ActionDefinition(
        name="stop_sound",
        display_name="Stop Sound",
        category="audio",
        tab="main2",
        description="Stop playing a sound",
        icon="🔇",
        parameters=[
            ActionParameter("sound", "sound", "Sound", "Sound to stop")
        ]
    ),
    "check_sound": ActionDefinition(
        name="check_sound",
        display_name="Check Sound",
        category="audio",
        tab="main2",
        description="Check if sound is playing",
        icon="🎵",
        parameters=[
            ActionParameter("sound", "sound", "Sound", "Sound to check"),
            ActionParameter("not_flag", "boolean", "NOT", "Invert condition", default=False)
        ]
    ),
}

# ============================================================================

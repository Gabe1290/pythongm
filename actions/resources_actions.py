#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Resources Actions
"""

from actions.core import ActionDefinition, ActionParameter


RESOURCES_ACTIONS = {
    "replace_sprite": ActionDefinition(
        name="replace_sprite",
        display_name="Replace Sprite from File",
        category="resources",
        tab="resources",
        description="Load sprite from file",
        icon="📁",
        parameters=[
            ActionParameter("sprite", "sprite", "Sprite", "Sprite to replace"),
            ActionParameter("filename", "string", "Filename", "Image file path", default=""),
            ActionParameter("frames", "int", "Number of Frames", "Animation frames", default=1),
            ActionParameter("remove_background", "boolean", "Remove Background", "Make transparent", default=False),
            ActionParameter("smooth_edges", "boolean", "Smooth Edges", "Anti-alias edges", default=False)
        ]
    ),
    "replace_sound": ActionDefinition(
        name="replace_sound",
        display_name="Replace Sound from File",
        category="resources",
        tab="resources",
        description="Load sound from file",
        icon="🔊",
        parameters=[
            ActionParameter("sound", "sound", "Sound", "Sound to replace"),
            ActionParameter("filename", "string", "Filename", "Audio file path", default=""),
            ActionParameter("kind", "choice", "Kind", "Sound type",
                          default="normal", options=["normal", "background", "3d", "mmplayer"])
        ]
    ),
    "replace_background": ActionDefinition(
        name="replace_background",
        display_name="Replace Background from File",
        category="resources",
        tab="resources",
        description="Load background from file",
        icon="🖼️",
        parameters=[
            ActionParameter("background", "background", "Background", "Background to replace"),
            ActionParameter("filename", "string", "Filename", "Image file path", default=""),
            ActionParameter("remove_background", "boolean", "Remove Background", "Make transparent", default=False),
            ActionParameter("smooth_edges", "boolean", "Smooth Edges", "Anti-alias edges", default=False)
        ]
    ),
}


# Export all action collections

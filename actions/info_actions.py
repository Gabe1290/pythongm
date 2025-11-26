#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Info Actions
"""

from actions.core import ActionDefinition, ActionParameter


INFO_ACTIONS = {
    "display_message": ActionDefinition(
        name="display_message",
        display_name="Display Message",
        category="info",
        tab="info",
        description="Show message dialog",
        icon="💬",
        parameters=[
            ActionParameter("message", "string", "Message", "Message text", default="")
        ]
    ),
    "show_info": ActionDefinition(
        name="show_info",
        display_name="Show Game Information",
        category="info",
        tab="info",
        description="Display game info screen",
        icon="ℹ️"
    ),
    "show_video": ActionDefinition(
        name="show_video",
        display_name="Show Video",
        category="info",
        tab="info",
        description="Play video file",
        icon="🎬",
        parameters=[
            ActionParameter("filename", "string", "Filename", "Video file path", default=""),
            ActionParameter("fullscreen", "boolean", "Fullscreen", "Play fullscreen", default=False)
        ]
    ),
    "open_webpage": ActionDefinition(
        name="open_webpage",
        display_name="Open Web Page",
        category="info",
        tab="info",
        description="Open URL in browser",
        icon="🌐",
        parameters=[
            ActionParameter("url", "string", "URL", "Web address", default="")
        ]
    ),
    "restart_game": ActionDefinition(
        name="restart_game",
        display_name="Restart Game",
        category="info",
        tab="info",
        description="Restart from first room",
        icon="🔄"
    ),
    "end_game": ActionDefinition(
        name="end_game",
        display_name="End Game",
        category="info",
        tab="info",
        description="Close the game",
        icon="🚪"
    ),
    "save_game": ActionDefinition(
        name="save_game",
        display_name="Save Game",
        category="info",
        tab="info",
        description="Save game state",
        icon="💾",
        parameters=[
            ActionParameter("filename", "string", "Filename", "Save file name", default="savegame.sav")
        ]
    ),
    "load_game": ActionDefinition(
        name="load_game",
        display_name="Load Game",
        category="info",
        tab="info",
        description="Load game state",
        icon="📂",
        parameters=[
            ActionParameter("filename", "string", "Filename", "Save file name", default="savegame.sav")
        ]
    ),
}

# ============================================================================

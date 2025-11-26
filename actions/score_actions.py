#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Score Actions
"""

from actions.core import ActionDefinition, ActionParameter


SCORE_ACTIONS = {
    "set_score": ActionDefinition(
        name="set_score",
        display_name="Set Score",
        category="score",
        tab="score",
        description="Set the score value",
        icon="🏆",
        parameters=[
            ActionParameter("value", "int", "New Score", "New score value", default=0),
            ActionParameter("relative", "boolean", "Relative", "Add to current score", default=False)
        ]
    ),
    "test_score": ActionDefinition(
        name="test_score",
        display_name="Test Score",
        category="score",
        tab="score",
        description="Compare score value",
        icon="🏆",
        parameters=[
            ActionParameter("value", "int", "Value", "Value to compare", default=0),
            ActionParameter("operation", "choice", "Operation", "Comparison operator",
                          options=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"])
        ]
    ),
    "draw_score": ActionDefinition(
        name="draw_score",
        display_name="Draw Score",
        category="score",
        tab="score",
        description="Draw score value on screen",
        icon="📊",
        parameters=[
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("caption", "string", "Caption", "Text before score", default="Score: ")
        ]
    ),
    "show_highscore": ActionDefinition(
        name="show_highscore",
        display_name="Show Highscore Table",
        category="score",
        tab="score",
        description="Display highscore table",
        icon="🥇"
    ),
    "clear_highscore": ActionDefinition(
        name="clear_highscore",
        display_name="Clear Highscore Table",
        category="score",
        tab="score",
        description="Reset all highscores",
        icon="🧹"
    ),
    "set_lives": ActionDefinition(
        name="set_lives",
        display_name="Set Lives",
        category="score",
        tab="score",
        description="Set number of lives",
        icon="❤️",
        parameters=[
            ActionParameter("value", "int", "Lives", "Number of lives", default=3),
            ActionParameter("relative", "boolean", "Relative", "Add to current lives", default=False)
        ]
    ),
    "test_lives": ActionDefinition(
        name="test_lives",
        display_name="Test Lives",
        category="score",
        tab="score",
        description="Compare lives value",
        icon="❤️",
        parameters=[
            ActionParameter("value", "int", "Value", "Value to compare", default=0),
            ActionParameter("operation", "choice", "Operation", "Comparison operator",
                          options=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"])
        ]
    ),
    "draw_lives": ActionDefinition(
        name="draw_lives",
        display_name="Draw Lives",
        category="score",
        tab="score",
        description="Draw lives as images",
        icon="❤️",
        parameters=[
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("sprite", "sprite", "Sprite", "Sprite to use for lives icon")
        ]
    ),
    "set_health": ActionDefinition(
        name="set_health",
        display_name="Set Health",
        category="score",
        tab="score",
        description="Set health value (0-100)",
        icon="💚",
        parameters=[
            ActionParameter("value", "float", "Health", "Health value (0-100)", default=100),
            ActionParameter("relative", "boolean", "Relative", "Add to current health", default=False)
        ]
    ),
    "test_health": ActionDefinition(
        name="test_health",
        display_name="Test Health",
        category="score",
        tab="score",
        description="Compare health value",
        icon="💚",
        parameters=[
            ActionParameter("value", "float", "Value", "Value to compare", default=0),
            ActionParameter("operation", "choice", "Operation", "Comparison operator",
                          options=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"])
        ]
    ),
    "draw_health_bar": ActionDefinition(
        name="draw_health_bar",
        display_name="Draw Health Bar",
        category="score",
        tab="score",
        description="Draw health as bar",
        icon="📊",
        parameters=[
            ActionParameter("x1", "int", "X1", "Left position", default=0),
            ActionParameter("y1", "int", "Y1", "Top position", default=0),
            ActionParameter("x2", "int", "X2", "Right position", default=100),
            ActionParameter("y2", "int", "Y2", "Bottom position", default=20),
            ActionParameter("back_color", "color", "Back Color", "Background color", default="#FF0000"),
            ActionParameter("bar_color", "color", "Bar Color", "Bar color", default="#00FF00")
        ]
    ),
    "set_window_caption": ActionDefinition(
        name="set_window_caption",
        display_name="Set Window Caption",
        category="score",
        tab="score",
        description="Set game window title",
        icon="🪟",
        parameters=[
            ActionParameter("show_score", "boolean", "Show Score", "Include score in title", default=True),
            ActionParameter("show_lives", "boolean", "Show Lives", "Include lives in title", default=True),
            ActionParameter("show_health", "boolean", "Show Health", "Include health in title", default=False),
            ActionParameter("caption", "string", "Caption", "Window title text", default="")
        ]
    ),
}

# ============================================================================

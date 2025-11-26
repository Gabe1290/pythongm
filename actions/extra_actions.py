#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Extra Actions
"""

from actions.core import ActionDefinition, ActionParameter


EXTRA_ACTIONS = {
    "set_variable": ActionDefinition(
        name="set_variable",
        display_name="Set Variable",
        category="variables",
        tab="extra",
        description="Set a variable value",
        icon="📝",
        parameters=[
            ActionParameter("variable", "string", "Variable", "Variable name", default=""),
            ActionParameter("value", "string", "Value", "New value", default="0"),
            ActionParameter("relative", "boolean", "Relative", "Add to current value", default=False)
        ]
    ),
    "test_variable": ActionDefinition(
        name="test_variable",
        display_name="Test Variable",
        category="variables",
        tab="extra",
        description="Compare variable value",
        icon="❓",
        parameters=[
            ActionParameter("variable", "string", "Variable", "Variable name", default=""),
            ActionParameter("value", "string", "Value", "Value to compare", default="0"),
            ActionParameter("operation", "choice", "Operation", "Comparison operator",
                          options=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"])
        ]
    ),
    "draw_variable": ActionDefinition(
        name="draw_variable",
        display_name="Draw Variable",
        category="variables",
        tab="extra",
        description="Draw variable value on screen",
        icon="📊",
        parameters=[
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("variable", "string", "Variable", "Variable to display", default="")
        ]
    ),
    "previous_room": ActionDefinition(
        name="previous_room",
        display_name="Previous Room",
        category="rooms",
        tab="extra",
        description="Go to previous room",
        icon="⬅️",
        parameters=[
            ActionParameter("transition", "choice", "Transition", "Transition effect",
                          default="none",
                          options=["none", "create_from_left", "create_from_right", "create_from_top", "create_from_bottom"])
        ]
    ),
    "next_room": ActionDefinition(
        name="next_room",
        display_name="Next Room",
        category="rooms",
        tab="extra",
        description="Go to next room",
        icon="➡️",
        parameters=[
            ActionParameter("transition", "choice", "Transition", "Transition effect",
                          default="none",
                          options=["none", "create_from_left", "create_from_right", "create_from_top", "create_from_bottom"])
        ]
    ),
    "restart_room": ActionDefinition(
        name="restart_room",
        display_name="Restart Room",
        category="rooms",
        tab="extra",
        description="Restart current room",
        icon="🔄",
        parameters=[
            ActionParameter("transition", "choice", "Transition", "Transition effect",
                          default="none",
                          options=["none", "create_from_left", "create_from_right", "create_from_top", "create_from_bottom"])
        ]
    ),
    "goto_room": ActionDefinition(
        name="goto_room",
        display_name="Go to Different Room",
        category="rooms",
        tab="extra",
        description="Go to specific room",
        icon="🚪",
        parameters=[
            ActionParameter("room", "room", "Room", "Target room"),
            ActionParameter("transition", "choice", "Transition", "Transition effect",
                          default="none",
                          options=["none", "create_from_left", "create_from_right", "create_from_top", "create_from_bottom"])
        ]
    ),
    "check_room": ActionDefinition(
        name="check_room",
        display_name="Test Room",
        category="rooms",
        tab="extra",
        description="Check if in specific room",
        icon="❓",
        parameters=[
            ActionParameter("room", "room", "Room", "Room to check"),
            ActionParameter("not_flag", "boolean", "NOT", "Invert condition", default=False)
        ]
    ),
}

# ============================================================================

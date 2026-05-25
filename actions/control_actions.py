#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Control Actions
"""

from actions.core import ActionDefinition, ActionParameter


CONTROL_ACTIONS = {
    "check_empty": ActionDefinition(
        name="check_empty",
        display_name="Check Empty",
        category="control",
        tab="control",
        description="True when (x, y) has no collision. Pair with start_block/end_block to gate following actions.",
        icon="🔍",
        parameters=[
            ActionParameter("x", "string", "X", "X position (expression OK, e.g. self.x + 32)", default="self.x"),
            ActionParameter("y", "string", "Y", "Y position (expression OK, e.g. self.y + 32)", default="self.y"),
            ActionParameter("objects", "choice", "Objects", "Which instances count as occupying the position",
                            default="solid", options=["solid", "all"]),
        ]
    ),
    "if_collision": ActionDefinition(
        name="if_collision",
        display_name="Check Collision",
        category="control",
        tab="control",
        description="Test for collision with object (use 'any' to check for any object)",
        icon="❓",
        parameters=[
            ActionParameter("x", "string", "X", "X offset (number or expression like other.hspeed*8)", default="0"),
            ActionParameter("y", "string", "Y", "Y offset (number or expression like other.vspeed*8)", default="0"),
            ActionParameter("object", "object", "Object", "Object to check ('any' for any object, 'solid' for solid objects only)", default="any"),
            ActionParameter("not_flag", "boolean", "NOT", "Invert condition", default=False)
        ]
    ),
    "if_object_exists": ActionDefinition(
        name="if_object_exists",
        display_name="Check Object Exists",
        category="control",
        tab="control",
        description="Test if object type exists",
        icon="❓",
        parameters=[
            ActionParameter("object", "object", "Object", "Object to check for"),
            ActionParameter("not_flag", "boolean", "NOT", "Invert condition", default=False)
        ]
    ),
    "if_can_push": ActionDefinition(
        name="if_can_push",
        display_name="If Can Push",
        category="control",
        tab="control",
        description="Check if a box/object can be pushed in the current direction (Sokoban-style)",
        icon="📦",
        parameters=[
            ActionParameter("direction", "string", "Direction", "Push direction ('facing' = current movement)", default="facing"),
            ActionParameter("object_type", "string", "Object Type", "Type of object being pushed", default="box"),
            ActionParameter("then_action", "string", "Then Action", "Action if push possible ('push_and_move' or 'none')", default="push_and_move"),
            ActionParameter("else_action", "string", "Else Action", "Action if push blocked ('stop_movement' or 'none')", default="stop_movement"),
        ]
    ),
    "test_instance_count": ActionDefinition(
        name="test_instance_count",
        display_name="Test Instance Count",
        category="control",
        tab="control",
        description="Compare number of instances",
        icon="🔢",
        parameters=[
            ActionParameter("object", "object", "Object", "Object type"),
            ActionParameter("number", "int", "Number", "Count to compare", default=0),
            ActionParameter("operation", "choice", "Operation", "Comparison operator",
                          options=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"])
        ]
    ),
    "test_chance": ActionDefinition(
        name="test_chance",
        display_name="Test Chance",
        category="control",
        tab="control",
        description="Random probability test",
        icon="🎲",
        parameters=[
            ActionParameter("sides", "int", "Number of Sides", "Dice sides (1/N chance)", default=6)
        ]
    ),
    "test_question": ActionDefinition(
        name="test_question",
        display_name="Ask Question",
        category="control",
        tab="control",
        description="Show yes/no dialog",
        icon="❔",
        parameters=[
            ActionParameter("question", "string", "Question", "Question text", default="")
        ]
    ),
    "test_expression": ActionDefinition(
        name="test_expression",
        display_name="Test Expression",
        category="control",
        tab="control",
        description="Evaluate GML expression",
        icon="📝",
        parameters=[
            ActionParameter("expression", "string", "Expression", "GML code to evaluate", default="")
        ]
    ),
    "start_block": ActionDefinition(
        name="start_block",
        display_name="Start of Block",
        category="control",
        tab="control",
        description="Begin conditional block",
        icon="{"
    ),
    "end_block": ActionDefinition(
        name="end_block",
        display_name="End of Block",
        category="control",
        tab="control",
        description="End conditional block",
        icon="}"
    ),
    "else_block": ActionDefinition(
        name="else_block",
        display_name="Else",
        category="control",
        tab="control",
        description="Alternative condition",
        icon="⚡"
    ),
    "repeat": ActionDefinition(
        name="repeat",
        display_name="Repeat",
        category="control",
        tab="control",
        description="Repeat following actions N times (use Start/End Block for multiple actions)",
        icon="🔁",
        parameters=[
            ActionParameter("times", "string", "Times", "Number of repetitions (number or variable)", default="1")
        ]
    ),
    "exit_event": ActionDefinition(
        name="exit_event",
        display_name="Exit Event",
        category="control",
        tab="control",
        description="Stop executing current event",
        icon="🚪"
    ),
    "set_variable": ActionDefinition(
        name="set_variable",
        display_name="Set Variable",
        category="control",
        tab="control",
        description="Set an instance or global variable",
        icon="📝",
        parameters=[
            ActionParameter("variable", "string", "Variable", "Variable name", default=""),
            ActionParameter("value", "string", "Value", "Value (number, string, or expression)", default="0"),
            ActionParameter("scope", "choice", "Scope", "Variable scope",
                          default="self", options=["self", "other", "global"]),
            ActionParameter("relative", "boolean", "Relative", "Add to current value", default=False)
        ]
    ),
    "test_variable": ActionDefinition(
        name="test_variable",
        display_name="Test Variable",
        category="control",
        tab="control",
        description="Test an instance or global variable",
        icon="❓",
        parameters=[
            ActionParameter("variable", "string", "Variable", "Variable name", default=""),
            ActionParameter("value", "string", "Value", "Value to compare", default="0"),
            ActionParameter("scope", "choice", "Scope", "Variable scope",
                          default="self", options=["self", "other", "global"]),
            ActionParameter("operation", "choice", "Operation", "Comparison operator",
                          default="equal", options=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"])
        ]
    ),
}

# ============================================================================

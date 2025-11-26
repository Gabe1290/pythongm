#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Control Actions
"""

from actions.core import ActionDefinition, ActionParameter


CONTROL_ACTIONS = {
    "if_collision": ActionDefinition(
        name="if_collision",
        display_name="Check Collision",
        category="control",
        tab="control",
        description="Test for collision with object",
        icon="❓",
        parameters=[
            ActionParameter("x", "float", "X", "X offset", default=0),
            ActionParameter("y", "float", "Y", "Y offset", default=0),
            ActionParameter("object", "object", "Object", "Object to check"),
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
        display_name="Repeat Next Action",
        category="control",
        tab="control",
        description="Repeat following action N times",
        icon="🔁",
        parameters=[
            ActionParameter("times", "int", "Times", "Number of repetitions", default=1)
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
}

# ============================================================================

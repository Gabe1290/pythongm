#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Code Actions
"""

from actions.core import ActionDefinition, ActionParameter


CODE_ACTIONS = {
    "execute_code": ActionDefinition(
        name="execute_code",
        display_name="Execute Code",
        category="code",
        tab="code",
        description="Execute GML code",
        icon="💻",
        parameters=[
            ActionParameter("code", "code", "Code", "GML code to execute", default="")
        ]
    ),
    "execute_script": ActionDefinition(
        name="execute_script",
        display_name="Execute Script",
        category="code",
        tab="code",
        description="Call a script",
        icon="📜",
        parameters=[
            ActionParameter("script", "script", "Script", "Script to execute"),
            ActionParameter("arg0", "string", "Argument 0", "First argument", default=""),
            ActionParameter("arg1", "string", "Argument 1", "Second argument", default=""),
            ActionParameter("arg2", "string", "Argument 2", "Third argument", default=""),
            ActionParameter("arg3", "string", "Argument 3", "Fourth argument", default=""),
            ActionParameter("arg4", "string", "Argument 4", "Fifth argument", default="")
        ],
        implemented=False
    ),
    "comment": ActionDefinition(
        name="comment",
        display_name="Comment",
        category="code",
        tab="code",
        description="Add a comment (does nothing)",
        icon="💬",
        parameters=[
            ActionParameter("text", "string", "Comment", "Comment text", default="")
        ]
    ),
}

# ============================================================================

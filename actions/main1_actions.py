#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Main1 Actions
"""

from actions.core import ActionDefinition, ActionParameter


# TAB 2: MAIN1 ACTIONS
# ============================================================================

MAIN1_ACTIONS = {
    "create_instance": ActionDefinition(
        name="create_instance",
        display_name="Create Instance",
        category="instances",
        tab="main1",
        description="Create an instance of an object",
        icon="➕",
        parameters=[
            ActionParameter("object", "object", "Object", "Object type to create"),
            ActionParameter("x", "float", "X", "X position", default=0),
            ActionParameter("y", "float", "Y", "Y position", default=0),
            ActionParameter("relative", "boolean", "Relative", "Position relative to current instance", default=False)
        ]
    ),
    "create_random_instance": ActionDefinition(
        name="create_random_instance",
        display_name="Create Random Instance",
        category="instances",
        tab="main1",
        description="Create one of four random objects",
        icon="🎲",
        parameters=[
            ActionParameter("object1", "object", "Object 1", "First object choice"),
            ActionParameter("object2", "object", "Object 2", "Second object choice"),
            ActionParameter("object3", "object", "Object 3", "Third object choice"),
            ActionParameter("object4", "object", "Object 4", "Fourth object choice"),
            ActionParameter("x", "float", "X", "X position", default=0),
            ActionParameter("y", "float", "Y", "Y position", default=0)
        ],
        implemented=False
    ),
    "create_moving_instance": ActionDefinition(
        name="create_moving_instance",
        display_name="Create Moving Instance",
        category="instances",
        tab="main1",
        description="Create instance with initial motion",
        icon="🚀",
        parameters=[
            ActionParameter("object", "object", "Object", "Object type"),
            ActionParameter("x", "float", "X", "X position", default=0),
            ActionParameter("y", "float", "Y", "Y position", default=0),
            ActionParameter("speed", "float", "Speed", "Initial speed", default=0),
            ActionParameter("direction", "float", "Direction", "Initial direction", default=0)
        ],
        implemented=False
    ),
    "change_instance": ActionDefinition(
        name="change_instance",
        display_name="Change Instance",
        category="instances",
        tab="main1",
        description="Transform into different object type",
        icon="🔄",
        parameters=[
            ActionParameter("object", "object", "Change Into", "New object type"),
            ActionParameter("perform_events", "boolean", "Perform Events",
                          "Execute destroy/create events", default=True)
        ]
    ),
    "destroy_instance": ActionDefinition(
        name="destroy_instance",
        display_name="Destroy Instance",
        category="instances",
        tab="main1",
        description="Destroy an instance",
        icon="💥",
        parameters=[
            ActionParameter("target", "choice", "Applies to", "Which instance to destroy",
                          default="self", options=["self", "other"])
        ]
    ),
    "destroy_at_position": ActionDefinition(
        name="destroy_at_position",
        display_name="Destroy at Position",
        category="instances",
        tab="main1",
        description="Destroy instances at coordinates",
        icon="💣",
        parameters=[
            ActionParameter("x", "float", "X", "X position", default=0),
            ActionParameter("y", "float", "Y", "Y position", default=0),
            ActionParameter("object", "object", "Object", "Object type to destroy")
        ],
        implemented=False
    ),
}

# ... Continue with remaining action tabs ...

# I'll create the complete actions list but split it for readability
# This is a comprehensive but very long file, so I'll continue with the key categories

# ============================================================================

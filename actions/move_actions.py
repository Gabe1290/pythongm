#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Move Actions
"""

from actions.core import ActionDefinition, ActionParameter


MOVE_ACTIONS = {
    "start_moving_direction": ActionDefinition(
        name="start_moving_direction",
        display_name="Start Moving in a Direction",
        category="movement",
        tab="move",
        description="Start moving in one of 8 directions or use expression (e.g. other.direction)",
        icon="➡️",
        parameters=[
            ActionParameter("directions", "direction_buttons", "Directions",
                          "Select movement directions (8-way + center)", default=[]),
            ActionParameter("direction_expr", "string", "Or Direction Expression",
                          "Expression like other.direction, self.direction, or angle in degrees", default=""),
            ActionParameter("speed", "string", "Speed", "Movement speed (number or expression like other.speed)", default="4.0")
        ]
    ),
    "set_direction_speed": ActionDefinition(
        name="set_direction_speed",
        display_name="Set Direction and Speed",
        category="movement",
        tab="move",
        description="Set exact direction and speed",
        icon="🧭",
        parameters=[
            ActionParameter("direction", "float", "Direction", "Direction in degrees (0-360)", default=0),
            ActionParameter("speed", "float", "Speed", "Movement speed", default=4.0)
        ],
        implemented=False
    ),
    "move_towards_point": ActionDefinition(
        name="move_towards_point",
        display_name="Move Towards a Point",
        category="movement",
        tab="move",
        description="Move towards specific coordinates",
        icon="🎯",
        parameters=[
            ActionParameter("x", "float", "X", "Target X position", default=0),
            ActionParameter("y", "float", "Y", "Target Y position", default=0),
            ActionParameter("speed", "float", "Speed", "Movement speed", default=4.0)
        ],
        implemented=False
    ),
    "set_hspeed": ActionDefinition(
        name="set_hspeed",
        display_name="Set Horizontal Speed",
        category="movement",
        tab="move",
        description="Set horizontal movement speed",
        icon="↔️",
        parameters=[
            ActionParameter("hspeed", "string", "Horizontal Speed", "Pixels per step (number or variable like other.hspeed)", default="0")
        ]
    ),
    "set_vspeed": ActionDefinition(
        name="set_vspeed",
        display_name="Set Vertical Speed",
        category="movement",
        tab="move",
        description="Set vertical movement speed",
        icon="↕️",
        parameters=[
            ActionParameter("vspeed", "string", "Vertical Speed", "Pixels per step (number or variable like other.vspeed)", default="0")
        ]
    ),
    "set_gravity": ActionDefinition(
        name="set_gravity",
        display_name="Set Gravity",
        category="movement",
        tab="move",
        description="Apply gravity to the instance",
        icon="⬇️",
        parameters=[
            ActionParameter("direction", "float", "Direction", "Gravity direction", default=270),
            ActionParameter("gravity", "float", "Gravity", "Gravity strength", default=0.5)
        ]
    ),
    "reverse_horizontal": ActionDefinition(
        name="reverse_horizontal",
        display_name="Reverse Horizontal Direction",
        category="movement",
        tab="move",
        description="Reverse horizontal movement",
        icon="↔️"
    ),
    "reverse_vertical": ActionDefinition(
        name="reverse_vertical",
        display_name="Reverse Vertical Direction",
        category="movement",
        tab="move",
        description="Reverse vertical movement",
        icon="↕️"
    ),
    "set_friction": ActionDefinition(
        name="set_friction",
        display_name="Set Friction",
        category="movement",
        tab="move",
        description="Set movement friction",
        icon="🛑",
        parameters=[
            ActionParameter("friction", "float", "Friction", "Friction amount", default=0)
        ]
    ),
    "jump_to_position": ActionDefinition(
        name="jump_to_position",
        display_name="Jump to Position",
        category="movement",
        tab="move",
        description="Instantly move to coordinates (supports expressions like other.x, self.hspeed*8)",
        icon="📍",
        parameters=[
            ActionParameter("x", "string", "X", "X position (number or expression like other.x, self.hspeed*8)", default="0"),
            ActionParameter("y", "string", "Y", "Y position (number or expression like other.y, self.vspeed*8)", default="0"),
            ActionParameter("relative", "boolean", "Relative", "Add to current position instead of setting absolute", default=False)
        ]
    ),
    "jump_to_start": ActionDefinition(
        name="jump_to_start",
        display_name="Jump to Start Position",
        category="movement",
        tab="move",
        description="Return to creation position",
        icon="🏠"
    ),
    "jump_to_random": ActionDefinition(
        name="jump_to_random",
        display_name="Jump to Random Position",
        category="movement",
        tab="move",
        description="Move to random position in room",
        icon="🎲",
        parameters=[
            ActionParameter("snap_h", "int", "Snap Horizontal", "Horizontal snap grid", default=1),
            ActionParameter("snap_v", "int", "Snap Vertical", "Vertical snap grid", default=1)
        ]
    ),
    "snap_to_grid": ActionDefinition(
        name="snap_to_grid",
        display_name="Snap to Grid",
        category="movement",
        tab="move",
        description="Align to grid",
        icon="▦",
        parameters=[
            ActionParameter("hsnap", "int", "Horizontal Snap", "Horizontal grid size", default=32),
            ActionParameter("vsnap", "int", "Vertical Snap", "Vertical grid size", default=32)
        ]
    ),
    "wrap_around_room": ActionDefinition(
        name="wrap_around_room",
        display_name="Wrap Around Room",
        category="movement",
        tab="move",
        description="Wrap to opposite side when leaving room",
        icon="🔄",
        parameters=[
            ActionParameter("horizontal", "boolean", "Horizontal", "Wrap horizontally", default=True),
            ActionParameter("vertical", "boolean", "Vertical", "Wrap vertically", default=True)
        ]
    ),
    "move_to_contact": ActionDefinition(
        name="move_to_contact",
        display_name="Move to Contact",
        category="movement",
        tab="move",
        description="Move until touching an object",
        icon="👉",
        parameters=[
            ActionParameter("direction", "float", "Direction", "Direction to move", default=0),
            ActionParameter("max_distance", "float", "Max Distance", "Maximum pixels to move", default=1000),
            ActionParameter("object", "object", "Against Object", "Object to stop at", default="all")
        ],
        implemented=False
    ),
    "bounce": ActionDefinition(
        name="bounce",
        display_name="Bounce Against Objects",
        category="movement",
        tab="move",
        description="Bounce off objects",
        icon="⚽",
        parameters=[
            ActionParameter("precise", "boolean", "Precise", "Use precise collision", default=False),
            ActionParameter("object", "object", "Against Object", "Object to bounce off", default="solid")
        ]
    ),
    "stop_movement": ActionDefinition(
        name="stop_movement",
        display_name="Stop Movement",
        category="movement",
        tab="move",
        description="Stop all movement (set speed to 0)",
        icon="🛑",
        parameters=[]
    ),
    "if_on_grid": ActionDefinition(
        name="if_on_grid",
        display_name="If On Grid",
        category="control",
        tab="control",
        description="Check if aligned to grid (use with Start/End Block for multiple actions)",
        icon="▦",
        parameters=[
            ActionParameter("grid_size", "int", "Grid Size", "Grid cell size in pixels", default=32)
        ]
    ),
    "stop_if_no_keys": ActionDefinition(
        name="stop_if_no_keys",
        display_name="Stop If No Keys",
        category="control",
        tab="control",
        description="Stop movement if no arrow keys are pressed",
        icon="▦",
        parameters=[
            ActionParameter("grid_size", "int", "Grid Size", "Grid to snap to when stopping", default=32)
        ]
    ),
    "check_keys_and_move": ActionDefinition(
        name="check_keys_and_move",
        display_name="Check Keys and Move",
        category="control",
        tab="control",
        description="Check if movement keys are held and restart grid-based movement",
        icon="▦",
        parameters=[
            ActionParameter("grid_size", "int", "Grid Size", "Grid cell size in pixels", default=32),
            ActionParameter("speed", "float", "Speed", "Movement speed in pixels per frame", default=4.0)
        ]
    ),
}

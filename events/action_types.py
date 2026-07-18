#!/usr/bin/env python3
"""
Action types - WITH GRID SNAPPING
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ActionParameter:
    """Defines a parameter for an action

    Supported param_types:
        - string: Text input
        - number: Integer input
        - float: Decimal number input
        - choice: Dropdown selection
        - boolean: Checkbox
        - action_list: List of actions
        - color: Color picker
        - sprite: Sprite selector from project assets
        - object: Object selector from project assets
        - sound: Sound selector from project assets
        - room: Room selector from project assets
        - code: Multi-line code editor
        - position: X,Y coordinate pair
    """
    name: str
    display_name: str
    param_type: str  # See supported types above
    default_value: Any
    description: str = ""
    required: bool = True
    choices: List[str] = field(default_factory=list)

    # Additional widget configuration
    min_value: Optional[int] = None  # For number/float types
    max_value: Optional[int] = None  # For number/float types
    multi_select: bool = False  # For choice types - allow multiple selections
    # Legacy parameter names that older saved JSON might use under different keys.
    # The dialog and code generator look these up as a fallback so projects from before
    # an action's canonical name was finalized continue to load and edit correctly.
    aliases: List[str] = field(default_factory=list)

@dataclass
class ActionType:
    """Defines an action type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: Optional[str] = None
    parameters: List[ActionParameter] = field(default_factory=list)
    # When True, the action dialog shows a GM-style "Applies to: Self / Other / Object"
    # selector at the top; the chosen value is saved as `target` ("self"|"other"|"object")
    # and the object name as `target_object` in the action's params.
    supports_applies_to: bool = False

ACTION_TYPES = {
    "move_grid": ActionType(
        name="move_grid",
        display_name="Move Grid",
        description="Move one grid unit in the specified direction",
        category="Movement",
        icon="▦",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="choice",
                default_value="right",
                description="Direction to move",
                choices=["left", "right", "up", "down"]
            ),
            ActionParameter(
                name="grid_size",
                display_name="Grid Size",
                param_type="number",
                default_value=32,
                description="Size of grid unit in pixels"
            )
        ]
    ),

    "set_hspeed": ActionType(
        name="set_hspeed",
        display_name="Set Horizontal Speed",
        description="Set horizontal movement speed",
        category="Movement",
        icon="↔️",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Horizontal Speed",
                param_type="number",
                default_value=0,
                description="Speed in pixels per frame"
            )
        ]
    ),

    "set_vspeed": ActionType(
        name="set_vspeed",
        display_name="Set Vertical Speed",
        description="Set vertical movement speed",
        category="Movement",
        icon="↕️",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Vertical Speed",
                param_type="number",
                default_value=0,
                description="Speed in pixels per frame"
            )
        ]
    ),

    "stop_movement": ActionType(
        name="stop_movement",
        display_name="Stop Movement",
        description="Set both speeds to zero",
        category="Movement",
        icon="🛑",
        parameters=[]
    ),

    "snap_to_grid": ActionType(
        name="snap_to_grid",
        display_name="Snap to Grid",
        description="Align instance position to grid",
        category="Grid",
        icon="▦",
        parameters=[
            ActionParameter(
                name="grid_size",
                display_name="Grid Size",
                param_type="number",
                default_value=32,
                description="Grid cell size in pixels"
            )
        ]
    ),

    "if_on_grid": ActionType(
        name="if_on_grid",
        display_name="If On Grid",
        description="Check if object is aligned to grid",
        category="Grid",
        icon="▦",
        parameters=[
            ActionParameter(
                name="grid_size",
                display_name="Grid Size",
                param_type="number",
                default_value=32,
                description="Grid cell size in pixels"
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if on grid"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if not on grid"
            )
        ]
    ),

    "stop_if_no_keys": ActionType(
        name="stop_if_no_keys",
        display_name="Stop If No Keys Pressed",
        description="Stop movement on grid when no movement keys are pressed (perfect for smooth grid snapping)",
        category="Grid",
        icon="▦",
        parameters=[
            ActionParameter(
                name="grid_size",
                display_name="Grid Size",
                param_type="number",
                default_value=32,
                description="Grid cell size in pixels"
            )
        ]
    ),

    "if_condition": ActionType(
        name="if_condition",
        display_name="If Condition",
        description="Conditional check with then/else actions",
        category="Control",
        icon="❓",
        parameters=[]
    ),

    "if_collision_at": ActionType(
        name="if_collision_at",
        display_name="If Collision At",
        description="Check for collision at a position",
        category="Control",
        icon="🎯",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x + 32",
                description="X position expression"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position expression"
            ),
            ActionParameter(
                name="object_type",
                display_name="Object Type",
                param_type="choice",
                default_value="any",
                description="Object type to check",
                choices=["any", "solid"]
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if collision found"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if no collision"
            )
        ]
    ),

    "if_can_push": ActionType(
        name="if_can_push",
        display_name="If Can Push",
        description="Check if a box/object can be pushed in the current direction (Sokoban-style)",
        category="Control",
        icon="📦",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="choice",
                default_value="facing",
                description="Direction to check for push",
                choices=["facing"]
            ),
            ActionParameter(
                name="object_type",
                display_name="Object Type",
                param_type="string",
                default_value="box",
                description="Type of object being pushed"
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Action",
                param_type="choice",
                default_value="push_and_move",
                description="Action if push is possible",
                choices=["push_and_move", "none"]
            ),
            ActionParameter(
                name="else_action",
                display_name="Else Action",
                param_type="choice",
                default_value="stop_movement",
                description="Action if push is blocked",
                choices=["stop_movement", "none"]
            )
        ]
    ),

    "set_variable": ActionType(
        name="set_variable",
        display_name="Set Variable",
        description="Set an instance or global variable",
        category="Control",
        icon="📝",
        parameters=[
            ActionParameter(
                name="variable",
                display_name="Variable",
                param_type="string",
                default_value="",
                description="Variable name",
                aliases=["variable_name"],
            ),
            ActionParameter(
                name="value",
                display_name="Value",
                param_type="string",
                default_value="0",
                description="Value (number, string, or expression)"
            ),
            ActionParameter(
                name="scope",
                display_name="Scope",
                param_type="choice",
                default_value="self",
                description="Variable scope",
                choices=["self", "other", "global"]
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Add to current value instead of replacing"
            )
        ]
    ),

    "test_variable": ActionType(
        name="test_variable",
        display_name="Test Variable",
        description="Test an instance or global variable value",
        category="Control",
        icon="❓",
        parameters=[
            ActionParameter(
                name="variable",
                display_name="Variable",
                param_type="string",
                default_value="",
                description="Variable name",
                aliases=["variable_name"],
            ),
            ActionParameter(
                name="value",
                display_name="Value",
                param_type="string",
                default_value="0",
                description="Value to compare"
            ),
            ActionParameter(
                name="scope",
                display_name="Scope",
                param_type="choice",
                default_value="self",
                description="Variable scope",
                choices=["self", "other", "global"]
            ),
            ActionParameter(
                name="operation",
                display_name="Operation",
                param_type="choice",
                default_value="equal",
                description="Comparison operator",
                choices=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"]
            )
        ]
    ),

    "show_message": ActionType(
        name="show_message",
        display_name="Show Message",
        description="Display a message",
        category="Game",
        icon="💬",
        parameters=[
            ActionParameter(
                name="message",
                display_name="Message",
                param_type="string",
                default_value="Hello!",
                description="Message text"
            )
        ]
    ),

    "restart_room": ActionType(
        name="restart_room",
        display_name="Restart Room",
        description="Restart current room",
        category="Room",
        icon="🔄",
        parameters=[]
    ),

    "next_room": ActionType(
        name="next_room",
        display_name="Next Room",
        description="Go to next room",
        category="Room",
        icon="➡️",
        parameters=[]
    ),

    # Views / camera. Lets a level be larger than the window and scroll.
    # Works on the desktop runtime (Test Game) and the HTML5 export; the
    # Kivy/Android export's camera is still pending (see
    # docs/VIEWS_SAMPLES_PLAN.md).
    "enable_views": ActionType(
        name="enable_views",
        display_name="Enable Views",
        description="Turn the room's camera/view system on or off (lets a "
                    "level scroll when it is larger than the window)",
        category="Views",
        icon="🎥",
        parameters=[
            ActionParameter(
                name="enable",
                display_name="Enable",
                param_type="boolean",
                default_value=True,
                description="On = camera views; off = draw the whole room at once",
                aliases=["enabled"],
            )
        ]
    ),

    "set_view": ActionType(
        name="set_view",
        display_name="Set View",
        description="Configure a camera view: which part of the room it shows, "
                    "where on screen it draws, and an object to follow",
        category="Views",
        icon="🎥",
        parameters=[
            ActionParameter(name="view", display_name="View (0-7)", param_type="choice",
                default_value="0", description="Which of the 8 views to configure",
                choices=["0", "1", "2", "3", "4", "5", "6", "7"]),
            ActionParameter(name="visible", display_name="Visible", param_type="boolean",
                default_value=True, description="Draw this view"),
            ActionParameter(name="view_x", display_name="View X (room)", param_type="number",
                default_value=0, description="Left edge of the room region shown"),
            ActionParameter(name="view_y", display_name="View Y (room)", param_type="number",
                default_value=0, description="Top edge of the room region shown"),
            ActionParameter(name="view_w", display_name="View Width", param_type="number",
                default_value=800, description="Width of the room region shown"),
            ActionParameter(name="view_h", display_name="View Height", param_type="number",
                default_value=600, description="Height of the room region shown"),
            ActionParameter(name="port_x", display_name="Port X (screen)", param_type="number",
                default_value=0, description="Left edge on screen"),
            ActionParameter(name="port_y", display_name="Port Y (screen)", param_type="number",
                default_value=0, description="Top edge on screen"),
            ActionParameter(name="port_w", display_name="Port Width", param_type="number",
                default_value=800, description="Width drawn on screen"),
            ActionParameter(name="port_h", display_name="Port Height", param_type="number",
                default_value=600, description="Height drawn on screen"),
            ActionParameter(name="follow", display_name="Follow Object", param_type="object",
                default_value="", required=False,
                description="Object the camera tracks (blank = fixed view)"),
            ActionParameter(name="hborder", display_name="H Border", param_type="number",
                default_value=32, description="Horizontal border before the camera scrolls"),
            ActionParameter(name="vborder", display_name="V Border", param_type="number",
                default_value=32, description="Vertical border before the camera scrolls"),
            ActionParameter(name="hspeed", display_name="Max H Scroll", param_type="number",
                default_value=-1, description="Max horizontal scroll speed (-1 = instant)"),
            ActionParameter(name="vspeed", display_name="Max V Scroll", param_type="number",
                default_value=-1, description="Max vertical scroll speed (-1 = instant)"),
        ]
    ),

    # Runtime: execute_set_facing_angle_action / execute_enable_raycast_view_action
    # (runtime/action_executor.py). Registered so the DOOM-style raycast view
    # (docs/RAYCAST_2_5D_PLAN.md) round-trips through the action editor and the
    # exporters can dispatch on it — the shared prerequisite for HTML5/Kivy
    # raycast parity (Phases 2/3), mirroring the enable_views/set_view work.
    "set_facing_angle": ActionType(
        name="set_facing_angle",
        display_name="Set Facing Angle",
        description="Set the instance's look direction for a raycast (first-person) "
                    "camera — independent of movement speed",
        category="3D View",
        icon="🧭",
        parameters=[
            ActionParameter(name="angle", display_name="Angle", param_type="number",
                default_value=0,
                description="Degrees (0=right, 90=up, 180=left, 270=down)"),
            ActionParameter(name="relative", display_name="Relative", param_type="boolean",
                default_value=False, required=False,
                description="Add to the current facing angle instead of replacing it"),
        ]
    ),

    "enable_raycast_view": ActionType(
        name="enable_raycast_view",
        display_name="Enable Raycast View",
        description="Render the room as a Doom/Wolfenstein-style first-person "
                    "3D view (walls, sky, floor) instead of the top-down view",
        category="3D View",
        icon="🕹️",
        parameters=[
            ActionParameter(name="enable", display_name="Enable", param_type="boolean",
                default_value=True,
                description="On = first-person raycast view; off = normal top-down"),
            ActionParameter(name="camera_object", display_name="Camera Object",
                param_type="object", default_value="", required=False,
                description="Object whose position + facing angle is the camera "
                            "(blank = the object running this action)"),
            ActionParameter(name="fov", display_name="Field of View", param_type="number",
                default_value=66, required=False, description="Horizontal FOV in degrees"),
            ActionParameter(name="render_distance", display_name="Render Distance",
                param_type="number", default_value=20, required=False,
                description="Max ray length in grid cells"),
            ActionParameter(name="cell_size", display_name="Cell Size", param_type="number",
                default_value=32, required=False,
                description="Grid cell size in pixels (match the wall placement grid)"),
            ActionParameter(name="columns", display_name="Columns", param_type="number",
                default_value=320, required=False,
                description="Screen columns to raycast (lower = faster/chunkier)"),
            ActionParameter(name="wall_color", display_name="Wall Color", param_type="color",
                default_value="#993333", required=False,
                description="Flat wall colour when no wall texture is set"),
            ActionParameter(name="floor_color", display_name="Floor Color", param_type="color",
                default_value="#464632", required=False,
                description="Flat floor colour when no floor texture is set"),
            ActionParameter(name="ceiling_color", display_name="Ceiling Color", param_type="color",
                default_value="#87CEEB", required=False,
                description="Flat ceiling colour when no sky/ceiling texture is set"),
            ActionParameter(name="wall_texture", display_name="Wall Texture", param_type="sprite",
                default_value="", required=False,
                description="Sprite to texture every wall (blank = flat colour)"),
            ActionParameter(name="sky_texture", display_name="Sky Texture", param_type="sprite",
                default_value="", required=False,
                description="Sprite for a panning sky over the ceiling (blank = flat)"),
            ActionParameter(name="floor_texture", display_name="Floor Texture", param_type="sprite",
                default_value="", required=False,
                description="Sprite cast onto the floor (blank = flat colour)"),
            ActionParameter(name="ceiling_texture", display_name="Ceiling Texture",
                param_type="sprite", default_value="", required=False,
                description="Sprite cast onto the ceiling when no sky is set"),
            ActionParameter(name="wall_textured", display_name="Textured Walls",
                param_type="boolean", default_value=True, required=False,
                description="Off forces flat wall colours even when a texture is set"),
            ActionParameter(name="floor_cast_res", display_name="Floor Detail",
                param_type="number", default_value=4, required=False,
                description="Floor-cast downsample (higher = faster + chunkier)"),
        ]
    ),

    "previous_room": ActionType(
        name="previous_room",
        display_name="Previous Room",
        description="Go to previous room",
        category="Room",
        icon="⬅️",
        parameters=[]
    ),

    "if_next_room_exists": ActionType(
        name="if_next_room_exists",
        display_name="If Next Room Exists",
        description="Check if there is a next room after the current one",
        category="Room",
        icon="❓➡️",
        parameters=[
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if next room exists"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if next room does not exist"
            )
        ]
    ),

    "if_previous_room_exists": ActionType(
        name="if_previous_room_exists",
        display_name="If Previous Room Exists",
        description="Check if there is a previous room before the current one",
        category="Room",
        icon="❓⬅️",
        parameters=[
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if previous room exists"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if previous room does not exist"
            )
        ]
    ),


    # GAMEMAKER 7.0 MOVEMENT ACTIONS
    "move_free": ActionType(
        name="move_free",
        display_name="Move Free",
        description="Move in a precise direction (0-360 degrees)",
        category="Movement",
        icon="🧭",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="float",
                default_value=0,
                description="Direction in degrees (0=right, 90=up, counter-clockwise)",
                min_value=0,
                max_value=360
            ),
            ActionParameter(
                name="speed",
                display_name="Speed",
                param_type="float",
                default_value=4.0,
                description="Movement speed"
            )
        ]
    ),

    "set_gravity": ActionType(
        name="set_gravity",
        display_name="Set Gravity",
        description="Set gravity direction and strength",
        category="Movement",
        icon="⬇️",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="float",
                default_value=270,
                description="Gravity direction in degrees (270=down)",
                min_value=0,
                max_value=360
            ),
            ActionParameter(
                name="gravity",
                display_name="Gravity",
                param_type="float",
                default_value=0.5,
                description="Gravity strength (added each step)"
            )
        ]
    ),

    "set_friction": ActionType(
        name="set_friction",
        display_name="Set Friction",
        description="Set friction (deceleration)",
        category="Movement",
        icon="🛑",
        parameters=[
            ActionParameter(
                name="friction",
                display_name="Friction",
                param_type="float",
                default_value=0.1,
                description="Friction amount (subtracted from speed each step)"
            )
        ]
    ),

    "reverse_horizontal": ActionType(
        name="reverse_horizontal",
        display_name="Reverse Horizontal",
        description="Reverse horizontal movement direction",
        category="Movement",
        icon="↔️",
        parameters=[]
    ),

    "reverse_vertical": ActionType(
        name="reverse_vertical",
        display_name="Reverse Vertical",
        description="Reverse vertical movement direction",
        category="Movement",
        icon="↕️",
        parameters=[]
    ),

    "bounce": ActionType(
        name="bounce",
        display_name="Bounce",
        description="Bounce off solid objects",
        category="Movement",
        icon="",
        parameters=[]
    ),

    "move_to_contact": ActionType(
        name="move_to_contact",
        display_name="Move to Contact",
        description="Move in a direction until touching an object (or max distance)",
        category="Movement",
        icon="🎯",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="string",
                default_value="direction",
                description="Direction in degrees (0=right, 90=up, 180=left, "
                            "270=down), or an expression. Defaults to 'direction' "
                            "= the instance's current heading (collision snap).",
            ),
            ActionParameter(
                name="max_distance",
                display_name="Max Distance",
                param_type="number",
                default_value=1000,
                description="Maximum distance to move, in pixels",
            ),
            ActionParameter(
                name="object",
                display_name="Against",
                param_type="object",
                default_value="all",
                description="Stop on contact with: 'all' instances, 'solid' "
                            "objects only, or a specific object name.",
                required=False,
                # The dialog's "object" branch prepends these sentinels to the
                # available-objects list.
                choices=["all", "solid"],
            ),
        ]
    ),

    "wrap_around_room": ActionType(
        name="wrap_around_room",
        display_name="Wrap Around Room",
        description="Wrap to opposite side of the room",
        category="Movement",
        icon="🔄",
        parameters=[]
    ),

    "set_speed": ActionType(
        name="set_speed",
        display_name="Set Speed",
        description="Set movement speed (magnitude)",
        category="Movement",
        icon="⚡",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Speed",
                param_type="float",
                default_value=0,
                description="Movement speed"
            )
        ]
    ),

    "set_direction": ActionType(
        name="set_direction",
        display_name="Set Direction",
        description="Set movement direction",
        category="Movement",
        icon="🧭",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="float",
                default_value=0,
                description="Direction in degrees (0=right, 90=up)"
            )
        ]
    ),

    # GAMEMAKER 7.0 CONTROL ACTIONS
    "test_expression": ActionType(
        name="test_expression",
        display_name="Test Expression",
        description="Test if an expression is true",
        category="Control",
        icon="❓",
        parameters=[
            ActionParameter(
                name="expression",
                display_name="Expression",
                param_type="string",
                default_value="",
                description="Expression to evaluate (true if >= 0.5)"
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if true"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if false"
            )
        ]
    ),

    "check_empty": ActionType(
        name="check_empty",
        display_name="Check Empty",
        description="True when (x, y) is collision-free. Use with start_block/end_block "
                    "to gate the following action(s), GM-style.",
        category="Control",
        icon="🔍",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X",
                param_type="string",
                default_value="self.x",
                description="X position to check (expression OK, e.g. self.x + 32)"
            ),
            ActionParameter(
                name="y",
                display_name="Y",
                param_type="string",
                default_value="self.y",
                description="Y position to check (expression OK, e.g. self.y + 32)"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Treat X/Y as offsets from this instance's position "
                            "instead of absolute coordinates",
                required=False,
            ),
            ActionParameter(
                name="objects",
                display_name="Objects",
                param_type="choice",
                default_value="solid",
                description="Which instances count as occupying the position",
                choices=["solid", "all"]
            ),
        ]
    ),

    "start_block": ActionType(
        name="start_block",
        display_name="Start Block",
        description="Start a block of actions (for grouping)",
        category="Control",
        icon="📂",
        parameters=[]
    ),

    "end_block": ActionType(
        name="end_block",
        display_name="End Block",
        description="End a block of actions",
        category="Control",
        icon="📁",
        parameters=[]
    ),

    "else_action": ActionType(
        name="else_action",
        display_name="Else",
        description="Marks the else branch of a conditional",
        category="Control",
        icon="⚡",
        parameters=[]
    ),

    "repeat": ActionType(
        name="repeat",
        display_name="Repeat",
        description="Repeat next action/block N times",
        category="Control",
        icon="🔁",
        parameters=[
            ActionParameter(
                name="times",
                display_name="Times",
                param_type="number",
                default_value=10,
                description="Number of times to repeat"
            ),
            ActionParameter(
                name="actions",
                display_name="Actions",
                param_type="action_list",
                default_value=[],
                description="Actions to repeat"
            )
        ]
    ),

    "exit_event": ActionType(
        name="exit_event",
        display_name="Exit Event",
        description="Stop executing remaining actions in this event",
        category="Control",
        icon="🚪",
        parameters=[]
    ),

    # ALARM ACTIONS
    "set_alarm": ActionType(
        name="set_alarm",
        display_name="Set Alarm",
        description="Set an alarm clock",
        category="Timing",
        icon="⏰",
        parameters=[
            ActionParameter(
                name="alarm_number",
                display_name="Alarm Number",
                param_type="number",
                default_value=0,
                description="Which alarm (0-11)",
                min_value=0,
                max_value=11
            ),
            ActionParameter(
                name="steps",
                display_name="Steps",
                param_type="number",
                default_value=30,
                description="Number of steps until alarm triggers (30 = 0.5 sec at 60 FPS)"
            )
        ]
    ),

    # Runtime: execute_sleep_action
    "sleep": ActionType(
        name="sleep",
        display_name="Sleep",
        description="Pause the game for a number of milliseconds, then continue. "
                    "Sounds keep playing during the pause (e.g. let a sound finish "
                    "before changing rooms). Note: rendering and input are frozen "
                    "while sleeping, so keep durations short.",
        category="Timing",
        icon="💤",
        parameters=[
            ActionParameter(
                name="milliseconds",
                display_name="Milliseconds",
                param_type="number",
                default_value=1000,
                description="How long to pause, in milliseconds (1000 = 1 second)",
                min_value=0
            )
        ]
    ),

    # SCORE/LIVES/HEALTH ACTIONS
    "set_score": ActionType(
        name="set_score",
        display_name="Set Score",
        description="Set the score, or add to it with Relative",
        category="Score",
        icon="🏆",
        parameters=[
            ActionParameter(
                name="value",
                display_name="Score Value",
                param_type="number",
                default_value=0,
                description="Score value to set"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Add to the current score instead of replacing it"
            )
        ]
    ),

    "set_lives": ActionType(
        name="set_lives",
        display_name="Set Lives",
        description="Set the lives, or add to them with Relative",
        category="Score",
        icon="❤️",
        parameters=[
            ActionParameter(
                name="value",
                display_name="Lives",
                param_type="number",
                default_value=3,
                description="Number of lives"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Add to the current lives instead of replacing them"
            )
        ]
    ),

    "set_health": ActionType(
        name="set_health",
        display_name="Set Health",
        description="Set the health, or add to it with Relative",
        category="Score",
        icon="💚",
        parameters=[
            ActionParameter(
                name="value",
                display_name="Health",
                param_type="number",
                default_value=100,
                description="Health value (0-100)"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Add to the current health instead of replacing it"
            )
        ]
    ),

    # Runtime: runtime/action_executor.py:2361 execute_set_window_caption_action.
    # Configures whether the score/lives/health counters are appended to
    # the window title in addition to (or replacing) the project's static
    # title. Common in GameMaker projects that surface the player's state
    # via the title bar rather than an in-game HUD.
    "set_window_caption": ActionType(
        name="set_window_caption",
        display_name="Set Window Caption",
        description="Configure score/lives/health display in window title",
        category="Game",
        icon="🪟",
        parameters=[
            ActionParameter(
                name="show_score",
                display_name="Show Score",
                param_type="boolean",
                default_value=True,
                description="Append the current score to the window caption"
            ),
            ActionParameter(
                name="show_lives",
                display_name="Show Lives",
                param_type="boolean",
                default_value=True,
                description="Append the current lives count to the window caption"
            ),
            ActionParameter(
                name="show_health",
                display_name="Show Health",
                param_type="boolean",
                default_value=False,
                description="Append the current health value to the window caption"
            ),
            ActionParameter(
                name="caption",
                display_name="Caption Prefix",
                param_type="string",
                default_value="",
                description="Optional caption prefix shown before the counters",
                required=False,
            ),
        ],
    ),

    # INSTANCE ACTIONS
    "destroy_instance": ActionType(
        name="destroy_instance",
        display_name="Destroy Instance",
        description="Destroy an instance",
        category="Instance",
        icon="💥",
        supports_applies_to=True,
        parameters=[]
    ),

    "destroy_at_position": ActionType(
        name="destroy_at_position",
        display_name="Destroy at Position",
        description="Destroy instances within radius of (x, y)",
        category="Instance",
        icon="💣",
        parameters=[
            ActionParameter(
                name="object",
                display_name="Object",
                param_type="object",
                default_value="all",
                description="Which object type to destroy. 'all' destroys "
                            "every instance in range; 'solid' only solid ones "
                            "(e.g. walls); 'non-solid' everything except solids.",
                choices=["all", "solid", "non-solid"],
            ),
            ActionParameter(
                name="x",
                display_name="X",
                param_type="string",
                default_value="self.x",
                description="X position (expression OK, e.g. self.x)",
            ),
            ActionParameter(
                name="y",
                display_name="Y",
                param_type="string",
                default_value="self.y",
                description="Y position (expression OK, e.g. self.y)",
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Treat X/Y as offsets from this instance's position "
                            "instead of absolute coordinates",
                required=False,
            ),
            ActionParameter(
                name="radius",
                display_name="Radius",
                param_type="number",
                default_value=32,
                description="Pixel radius around (x, y). Default 32 = ~one grid cell.",
            ),
        ]
    ),

    "create_instance": ActionType(
        name="create_instance",
        display_name="Create Instance",
        description="Create a new instance",
        category="Instance",
        icon="✨",
        parameters=[
            ActionParameter(
                name="object",
                display_name="Object",
                param_type="object",
                default_value="",
                description="Object to create"
            ),
            ActionParameter(
                name="x",
                display_name="X",
                param_type="number",
                default_value=0,
                description="X position"
            ),
            ActionParameter(
                name="y",
                display_name="Y",
                param_type="number",
                default_value=0,
                description="Y position"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Position relative to current instance"
            )
        ]
    ),

    "change_instance": ActionType(
        name="change_instance",
        display_name="Change Instance",
        description="Transform into different object type",
        category="Instance",
        icon="🔄",
        supports_applies_to=True,
        parameters=[
            ActionParameter(
                name="object",
                display_name="Change Into",
                param_type="object",
                default_value="",
                description="New object type"
            ),
            ActionParameter(
                name="perform_events",
                display_name="Perform Events",
                param_type="boolean",
                default_value=True,
                description="Execute destroy/create events"
            )
        ]
    ),

    # Runtime: runtime/action_executor.py:4321 execute_set_sprite_action.
    # The "<self>" sentinel keeps the sprite name unchanged so only
    # subimage / speed get overwritten — used by GameMaker imports to
    # restart an animation without re-pointing the sprite.
    "set_sprite": ActionType(
        name="set_sprite",
        display_name="Set Sprite",
        description="Change an instance's sprite and/or animation frame/speed",
        category="Instance",
        icon="🖼️",
        parameters=[
            ActionParameter(
                name="sprite",
                display_name="Sprite",
                param_type="sprite",
                default_value="<self>",
                description="Sprite to use (or '<self>' to keep current)"
            ),
            ActionParameter(
                name="subimage",
                display_name="Frame",
                param_type="number",
                default_value=-1,
                description="Frame index to set; -1 to leave unchanged"
            ),
            ActionParameter(
                name="speed",
                display_name="Speed",
                param_type="float",
                default_value=-1,
                description="Animation speed; -1 to leave unchanged"
            ),
        ],
    ),

    # POSITION ACTIONS
    "jump_to_position": ActionType(
        name="jump_to_position",
        display_name="Jump To Position",
        description="Move instantly to a position",
        category="Movement",
        icon="📍",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X",
                param_type="number",
                default_value=0,
                description="X position"
            ),
            ActionParameter(
                name="y",
                display_name="Y",
                param_type="number",
                default_value=0,
                description="Y position"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",
                default_value=False,
                description="Add to current position instead of setting absolute"
            )
        ]
    ),

    # ROOM ACTIONS
    # restart_room, next_room, previous_room are defined above as the canonical names.
    # Legacy aliases (room_restart, room_goto_next, room_goto_previous) are handled
    # through ACTION_TYPE_ALIASES so older project JSON still loads in the dialog.
    #
    # "Go to Room" is single-sourced as `goto_room` (defined below — it carries
    # the richer param set and is what saved projects use) and "Restart Game" as
    # `restart_game`. The older `room_goto` / `game_restart` UI duplicates were
    # removed (they produced two identical entries in the Add Action menu); both
    # names remain runtime-aliased (ACTION_ALIASES) and dialog-aliased
    # (ACTION_TYPE_ALIASES) to their canonical equivalents.

    "game_end": ActionType(
        name="game_end",
        display_name="End Game",
        description="End the game",
        category="Room",
        icon="🛑🎮",
        parameters=[]
    ),

    # ---------------------------------------------------------------------
    # Bulk-added in rc.12: actions that the runtime already handled but had
    # no UI metadata, so the events panel logged "Unknown action type: X"
    # when loading bundled samples (maze_*, treasure). Source line numbers
    # reference runtime/action_executor.py unless noted otherwise. See
    # `.scratch_find_missing_actions.py` (one-shot survey, removed) for
    # the discovery method.
    # ---------------------------------------------------------------------

    # Comment — modular handler `handle_comment` is a no-op; the UI shows
    # the freeform text for documentation purposes. Yellow ⚠️ icon matches
    # the classic GameMaker convention for inline comment markers.
    "comment": ActionType(
        name="comment",
        display_name="Comment",
        description="A comment in the action list (no runtime effect)",
        category="Control",
        icon="⚠️",
        parameters=[
            ActionParameter(
                name="text",
                display_name="Comment",
                param_type="text",
                default_value="",
                description="Free-form comment text",
                required=False,
            ),
        ],
    ),

    # Runtime: execute_goto_room_action (line 5103)
    "goto_room": ActionType(
        name="goto_room",
        display_name="Go to Room",
        description="Switch to a specific room",
        category="Room",
        icon="🚪",
        parameters=[
            ActionParameter(
                name="room",
                display_name="Room",
                param_type="room",
                default_value="",
                description="Target room name"
            ),
            ActionParameter(
                name="transition",
                display_name="Transition",
                param_type="choice",
                default_value="none",
                description="Transition effect (currently accepted but not rendered)",
                choices=["none"],
                required=False,
            ),
        ],
    ),

    # Runtime: execute_create_random_instance_action (line 4510)
    "create_random_instance": ActionType(
        name="create_random_instance",
        display_name="Create Random Instance",
        description="Create one of several object types chosen at random",
        category="Instance",
        icon="🎲",
        parameters=[
            ActionParameter(
                name="x", display_name="X", param_type="number", default_value=0,
                description="X position"
            ),
            ActionParameter(
                name="y", display_name="Y", param_type="number", default_value=0,
                description="Y position"
            ),
            ActionParameter(
                name="object1", display_name="Object 1", param_type="object",
                default_value="", description="First candidate object", required=False,
            ),
            ActionParameter(
                name="object2", display_name="Object 2", param_type="object",
                default_value="", description="Second candidate object", required=False,
            ),
            ActionParameter(
                name="object3", display_name="Object 3", param_type="object",
                default_value="", description="Third candidate object", required=False,
            ),
            ActionParameter(
                name="object4", display_name="Object 4", param_type="object",
                default_value="", description="Fourth candidate object", required=False,
            ),
        ],
    ),

    # Runtime: execute_start_moving_direction_action (line 960). Supports either
    # an 8-direction bitmask (GameMaker convention) or a direct expression.
    "start_moving_direction": ActionType(
        name="start_moving_direction",
        display_name="Start Moving (Direction)",
        description="Begin moving in a direction at a given speed",
        category="Movement",
        icon="➡️",
        parameters=[
            ActionParameter(
                name="directions", display_name="Directions",
                # `string` rather than `number` because the GMK importer
                # converts the original 9-bit bitmask into a Python list
                # of direction names (e.g. `['down', 'up']` so
                # start_moving_direction can pick at random). The events
                # panel currently has no multi-select widget for list
                # params, so the value round-trips through a QLineEdit
                # as its stringified repr. The runtime tolerates both
                # forms (list, stringified list, single name, numeric
                # angle, expression) — see execute_start_moving_direction_action.
                param_type="string", default_value="right",
                description="Direction name ('up', 'down', 'left', 'right'), comma-separated list, or a single numeric angle",
            ),
            ActionParameter(
                name="direction_expr", display_name="Direction Expression",
                param_type="string", default_value="",
                description="Alternative: free expression evaluated as degrees",
                required=False,
            ),
            ActionParameter(
                name="speed", display_name="Speed",
                param_type="float", default_value=4.0,
                description="Speed in pixels per frame",
            ),
        ],
    ),

    # Runtime: execute_execute_code_action (line 2709)
    "execute_code": ActionType(
        name="execute_code",
        display_name="Execute Code",
        description="Run an inline block of Python code",
        category="Control",
        icon="📜",
        parameters=[
            ActionParameter(
                name="code", display_name="Code",
                param_type="code", default_value="",
                description="Python source to evaluate against the instance",
            ),
        ],
    ),

    # Runtime: execute_execute_script_action (action_executor.py). GMK imports
    # emit this for GM's "execute script" action (treasure's monster calls its
    # adapt_direction project script from step/collision events); without this
    # entry the events panel logged "Unknown action type: execute_script" and
    # refused to open the editor dialog for a working runtime action.
    "execute_script": ActionType(
        name="execute_script",
        display_name="Execute Script",
        description="Run one of the project's script assets",
        category="Control",
        icon="📜",
        parameters=[
            ActionParameter(
                name="script", display_name="Script",
                param_type="script", default_value="",
                description="Name of the project script to run",
            ),
            ActionParameter(
                name="arg0", display_name="Argument 0",
                param_type="string", default_value="", required=False,
                description="Available in the script as argument0",
            ),
            ActionParameter(
                name="arg1", display_name="Argument 1",
                param_type="string", default_value="", required=False,
                description="Available in the script as argument1",
            ),
            ActionParameter(
                name="arg2", display_name="Argument 2",
                param_type="string", default_value="", required=False,
                description="Available in the script as argument2",
            ),
            ActionParameter(
                name="arg3", display_name="Argument 3",
                param_type="string", default_value="", required=False,
                description="Available in the script as argument3",
            ),
            ActionParameter(
                name="arg4", display_name="Argument 4",
                param_type="string", default_value="", required=False,
                description="Available in the script as argument4",
            ),
        ],
    ),

    # Runtime: execute_test_health_action (line 2307)
    "test_health": ActionType(
        name="test_health",
        display_name="Test Health",
        description="Conditional: compare current health against a value",
        category="Score",
        icon="❓💚",
        parameters=[
            ActionParameter(
                name="operation", display_name="Operation",
                param_type="choice", default_value="equal",
                description="Comparison operator",
                choices=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"],
            ),
            ActionParameter(
                name="value", display_name="Value",
                param_type="number", default_value=0,
                description="Value to compare against",
            ),
        ],
    ),

    # Runtime: execute_show_highscore_action (line 2375)
    "show_highscore": ActionType(
        name="show_highscore",
        display_name="Show High-Score Table",
        description="Display the high-score table dialog",
        category="Score",
        icon="🏆",
        parameters=[
            ActionParameter(
                name="background", display_name="Background Color",
                param_type="color", default_value="#FFFFDD",
                description="Dialog background colour",
                required=False,
            ),
            ActionParameter(
                name="new_color", display_name="New Entry Color",
                param_type="color", default_value="#FF0000",
                description="Colour used for the new (qualifying) entry",
                required=False,
            ),
            ActionParameter(
                name="other_color", display_name="Other Entries Color",
                param_type="color", default_value="#000000",
                description="Colour used for the other entries",
                required=False,
            ),
            ActionParameter(
                name="allow_new_entry", display_name="Allow New Entry",
                param_type="boolean", default_value=True,
                description="Prompt for name if the current score qualifies",
            ),
        ],
    ),

    # Runtime: execute_if_object_exists_action (line 1316)
    "if_object_exists": ActionType(
        name="if_object_exists",
        display_name="If Object Exists",
        description="Conditional: true if at least one instance of object exists",
        category="Control",
        icon="❓",
        parameters=[
            ActionParameter(
                name="object", display_name="Object",
                param_type="object", default_value="",
                description="Object type to check",
            ),
            ActionParameter(
                name="not_flag", display_name="Negate",
                param_type="boolean", default_value=False,
                description="Negate the result (act when the object does NOT exist)",
                required=False,
            ),
        ],
    ),

    # Runtime: execute_restart_game_action (line 2420) — no parameters
    "restart_game": ActionType(
        name="restart_game",
        display_name="Restart Game",
        description="Restart the game from the start room",
        category="Game",
        icon="🔁🎮",
        parameters=[],
    ),

    # Runtime: execute_jump_to_start_action (line 852) — no parameters
    "jump_to_start": ActionType(
        name="jump_to_start",
        display_name="Jump to Start Position",
        description="Move the instance back to its creation position",
        category="Movement",
        icon="↩️",
        parameters=[],
    ),

    # Runtime: execute_if_collision_action (line 1229). Note: the existing
    # `check_collision` UI entry covers a similar feature with different
    # parameter names; this one mirrors what the GMK importer actually
    # emits so legacy projects load without "Unknown action type" warnings.
    "if_collision": ActionType(
        name="if_collision",
        display_name="If Collision",
        description="Conditional: true if the instance would collide at offset (x, y)",
        category="Control",
        icon="❓💥",
        parameters=[
            ActionParameter(
                name="x", display_name="X Offset",
                param_type="number", default_value=0,
                description="Horizontal offset to test"
            ),
            ActionParameter(
                name="y", display_name="Y Offset",
                param_type="number", default_value=0,
                description="Vertical offset to test"
            ),
            ActionParameter(
                name="object", display_name="Against",
                param_type="string", default_value="any",
                description="'any', 'solid', or an object name",
                required=False,
                # The dialog's "object" branch prepends these to the
                # available-objects list so the user can pick the
                # built-in selectors as easily as a specific object.
                choices=["any", "solid"],
            ),
            ActionParameter(
                name="not_flag", display_name="Negate",
                param_type="boolean", default_value=False,
                description="Negate the result", required=False,
            ),
        ],
    ),

    # Runtime: execute_set_direction_speed_action (line 566)
    "set_direction_speed": ActionType(
        name="set_direction_speed",
        display_name="Set Direction & Speed",
        description="Set the instance's direction (degrees) and speed magnitude",
        category="Movement",
        icon="🧭",
        parameters=[
            ActionParameter(
                name="direction", display_name="Direction",
                param_type="number", default_value=0,
                description="Direction in degrees (0=right, 90=up)",
            ),
            ActionParameter(
                name="speed", display_name="Speed",
                param_type="float", default_value=4.0,
                description="Speed in pixels per frame",
            ),
        ],
    ),

    # Runtime: execute_create_moving_instance_action (line 4609)
    "create_moving_instance": ActionType(
        name="create_moving_instance",
        display_name="Create Moving Instance",
        description="Create an instance and start it moving in a direction",
        category="Instance",
        icon="✨➡️",
        parameters=[
            ActionParameter(
                name="object", display_name="Object",
                param_type="object", default_value="",
                description="Object to create",
            ),
            ActionParameter(
                name="x", display_name="X",
                param_type="number", default_value=0,
                description="X position",
            ),
            ActionParameter(
                name="y", display_name="Y",
                param_type="number", default_value=0,
                description="Y position",
            ),
            ActionParameter(
                name="speed", display_name="Speed",
                param_type="float", default_value=0,
                description="Initial speed magnitude",
            ),
            ActionParameter(
                name="direction", display_name="Direction",
                param_type="number", default_value=0,
                description="Initial direction in degrees",
            ),
        ],
    ),

    # Runtime: execute_draw_score_action (line 2180)
    "draw_score": ActionType(
        name="draw_score",
        display_name="Draw Score",
        description="Draw the current score on screen",
        category="Score",
        icon="🖍️🏆",
        parameters=[
            ActionParameter(
                name="x", display_name="X", param_type="number", default_value=0,
                description="X position",
            ),
            ActionParameter(
                name="y", display_name="Y", param_type="number", default_value=0,
                description="Y position",
            ),
            ActionParameter(
                name="caption", display_name="Caption",
                param_type="string", default_value="Score: ",
                description="Text shown before the score value",
                required=False,
            ),
        ],
    ),

    # Runtime: execute_draw_text_action (line 3234)
    "draw_text": ActionType(
        name="draw_text",
        display_name="Draw Text",
        description="Draw a text string at a position",
        category="Game",
        icon="🖍️",
        parameters=[
            ActionParameter(
                name="text", display_name="Text",
                param_type="string", default_value="",
                description="Text to draw (supports expressions)",
            ),
            ActionParameter(
                name="x", display_name="X", param_type="number", default_value=0,
                description="X position",
            ),
            ActionParameter(
                name="y", display_name="Y", param_type="number", default_value=0,
                description="Y position",
            ),
        ],
    ),

    # Runtime: execute_draw_lives_action (line 2350)
    "draw_lives": ActionType(
        name="draw_lives",
        display_name="Draw Lives",
        description="Draw the current life count as repeated sprite images",
        category="Score",
        icon="🖍️❤️",
        parameters=[
            ActionParameter(
                name="x", display_name="X", param_type="number", default_value=0,
                description="X position",
            ),
            ActionParameter(
                name="y", display_name="Y", param_type="number", default_value=0,
                description="Y position",
            ),
            ActionParameter(
                name="sprite", display_name="Sprite",
                param_type="sprite", default_value="",
                description="Sprite drawn once per remaining life",
                required=False,
            ),
            ActionParameter(
                name="scale", display_name="Scale",
                param_type="float", default_value=1.0,
                description="Uniform scale factor for the life icon (1.0 = native size)",
                required=False,
            ),
        ],
    ),

    # Runtime: execute_set_draw_font_action (line 5197)
    "set_draw_font": ActionType(
        name="set_draw_font",
        display_name="Set Draw Font",
        description="Set the font and alignment for subsequent text drawing",
        category="Game",
        icon="🔤",
        parameters=[
            ActionParameter(
                name="font", display_name="Font",
                param_type="string", default_value="",
                description="Font asset name (blank = default font)",
                required=False,
            ),
            ActionParameter(
                name="halign", display_name="Horizontal Align",
                param_type="choice", default_value="left",
                description="Horizontal text alignment",
                choices=["left", "center", "right"],
            ),
            ActionParameter(
                name="valign", display_name="Vertical Align",
                param_type="choice", default_value="top",
                description="Vertical text alignment",
                choices=["top", "middle", "bottom"],
            ),
        ],
    ),

    # Runtime: execute_test_alignment_action (line 1076)
    "test_alignment": ActionType(
        name="test_alignment",
        display_name="Test Grid Alignment",
        description="Conditional: true if the instance is aligned to a grid",
        category="Grid",
        icon="❓▦",
        parameters=[
            ActionParameter(
                name="hsnap", display_name="Horizontal Snap",
                param_type="number", default_value=32,
                description="Horizontal grid spacing in pixels",
            ),
            ActionParameter(
                name="vsnap", display_name="Vertical Snap",
                param_type="number", default_value=32,
                description="Vertical grid spacing in pixels",
            ),
        ],
    ),

    # Runtime: execute_set_draw_color_action (line 3065)
    "set_draw_color": ActionType(
        name="set_draw_color",
        display_name="Set Draw Color",
        description="Set the colour used by subsequent draw_* actions",
        category="Game",
        icon="🎨",
        parameters=[
            ActionParameter(
                name="color", display_name="Color",
                param_type="color", default_value="#000000",
                description="RGB hex colour",
            ),
        ],
    ),

    # Runtime: execute_fill_color_action (line 4969)
    "fill_color": ActionType(
        name="fill_color",
        display_name="Fill Screen Color",
        description="Fill the entire viewport with a solid colour",
        category="Game",
        icon="🪣",
        parameters=[
            ActionParameter(
                name="color", display_name="Color",
                param_type="color", default_value="#000000",
                description="RGB hex colour",
            ),
        ],
    ),

    # Runtime: execute_jump_to_random_action (line 866)
    "jump_to_random": ActionType(
        name="jump_to_random",
        display_name="Jump to Random Position",
        description="Teleport to a random position (optionally grid-snapped)",
        category="Movement",
        icon="🎲↪️",
        parameters=[
            ActionParameter(
                name="snap_h", display_name="Horizontal Snap",
                param_type="number", default_value=1,
                description="Horizontal grid snap (1 = no snap)",
            ),
            ActionParameter(
                name="snap_v", display_name="Vertical Snap",
                param_type="number", default_value=1,
                description="Vertical grid snap (1 = no snap)",
            ),
        ],
    ),

    # Runtime: execute_draw_scaled_text_action (line 3115)
    "draw_scaled_text": ActionType(
        name="draw_scaled_text",
        display_name="Draw Scaled Text",
        description="Draw text at an arbitrary scale",
        category="Game",
        icon="🖍️",
        parameters=[
            ActionParameter(
                name="text", display_name="Text",
                param_type="string", default_value="",
                description="Text to draw",
            ),
            ActionParameter(
                name="x", display_name="X", param_type="number", default_value=0,
                description="X position",
            ),
            ActionParameter(
                name="y", display_name="Y", param_type="number", default_value=0,
                description="Y position",
            ),
            ActionParameter(
                name="xscale", display_name="X Scale",
                param_type="float", default_value=1.0,
                description="Horizontal scale factor",
            ),
            ActionParameter(
                name="yscale", display_name="Y Scale",
                param_type="float", default_value=1.0,
                description="Vertical scale factor",
            ),
        ],
    ),

    # ---------------------------------------------------------------------
    # rc.12 follow-up sweep (2026-06-05): the remaining "safe & worth it"
    # bucket — runtime actions that already work but had no UI metadata, so
    # they logged "Unknown action type: X" and were uneditable in the events
    # panel. Params mirror exactly what each runtime handler reads via
    # parameters.get(...). Deferred buckets (particles, timelines,
    # save/load, views/camera, room background) are intentionally NOT added
    # here — they wait until after the 1.0 release. Line numbers reference
    # runtime/action_executor.py.
    # ---------------------------------------------------------------------

    # Drawing primitives -------------------------------------------------

    # Runtime: execute_draw_rectangle_action (line 3309)
    "draw_rectangle": ActionType(
        name="draw_rectangle",
        display_name="Draw Rectangle",
        description="Draw a filled or outlined rectangle",
        category="Game",
        icon="🟥",
        parameters=[
            ActionParameter(name="x1", display_name="X1", param_type="number", default_value=0, description="Left X"),
            ActionParameter(name="y1", display_name="Y1", param_type="number", default_value=0, description="Top Y"),
            ActionParameter(name="x2", display_name="X2", param_type="number", default_value=100, description="Right X"),
            ActionParameter(name="y2", display_name="Y2", param_type="number", default_value=100, description="Bottom Y"),
            ActionParameter(name="filled", display_name="Filled", param_type="boolean", default_value=True, description="Filled, or outline only", required=False),
        ],
    ),

    # Runtime: execute_draw_circle_action
    "draw_circle": ActionType(
        name="draw_circle",
        display_name="Draw Circle",
        description="Draw a filled or outlined circle",
        category="Game",
        icon="⭕",
        parameters=[
            ActionParameter(name="x", display_name="X", param_type="number", default_value=0, description="Centre X"),
            ActionParameter(name="y", display_name="Y", param_type="number", default_value=0, description="Centre Y"),
            ActionParameter(name="radius", display_name="Radius", param_type="number", default_value=50, description="Circle radius"),
            ActionParameter(name="filled", display_name="Filled", param_type="boolean", default_value=True, description="Filled, or outline only", required=False),
        ],
    ),

    # Runtime: execute_draw_line_action
    "draw_line": ActionType(
        name="draw_line",
        display_name="Draw Line",
        description="Draw a line between two points",
        category="Game",
        icon="📏",
        parameters=[
            ActionParameter(name="x1", display_name="X1", param_type="number", default_value=0, description="Start X"),
            ActionParameter(name="y1", display_name="Y1", param_type="number", default_value=0, description="Start Y"),
            ActionParameter(name="x2", display_name="X2", param_type="number", default_value=100, description="End X"),
            ActionParameter(name="y2", display_name="Y2", param_type="number", default_value=100, description="End Y"),
        ],
    ),

    # Runtime: execute_draw_ellipse_action
    "draw_ellipse": ActionType(
        name="draw_ellipse",
        display_name="Draw Ellipse",
        description="Draw a filled or outlined ellipse within a bounding box",
        category="Game",
        icon="🥚",
        parameters=[
            ActionParameter(name="x1", display_name="X1", param_type="number", default_value=0, description="Left X"),
            ActionParameter(name="y1", display_name="Y1", param_type="number", default_value=0, description="Top Y"),
            ActionParameter(name="x2", display_name="X2", param_type="number", default_value=100, description="Right X"),
            ActionParameter(name="y2", display_name="Y2", param_type="number", default_value=100, description="Bottom Y"),
            ActionParameter(name="filled", display_name="Filled", param_type="boolean", default_value=True, description="Filled, or outline only", required=False),
        ],
    ),

    # Runtime: execute_draw_arrow_action
    "draw_arrow": ActionType(
        name="draw_arrow",
        display_name="Draw Arrow",
        description="Draw an arrow from one point to another",
        category="Game",
        icon="➡️",
        parameters=[
            ActionParameter(name="x1", display_name="X1", param_type="number", default_value=0, description="Start X"),
            ActionParameter(name="y1", display_name="Y1", param_type="number", default_value=0, description="Start Y"),
            ActionParameter(name="x2", display_name="X2", param_type="number", default_value=100, description="Tip X"),
            ActionParameter(name="y2", display_name="Y2", param_type="number", default_value=100, description="Tip Y"),
            ActionParameter(name="tip_size", display_name="Tip Size", param_type="number", default_value=10, description="Arrowhead size in pixels"),
        ],
    ),

    # Runtime: execute_draw_sprite_action (line 3466)
    "draw_sprite": ActionType(
        name="draw_sprite",
        display_name="Draw Sprite",
        description="Draw a sprite frame at a position",
        category="Game",
        icon="🖼️",
        parameters=[
            ActionParameter(name="sprite", display_name="Sprite", param_type="sprite", default_value="", description="Sprite to draw"),
            ActionParameter(name="x", display_name="X", param_type="number", default_value=0, description="X position"),
            ActionParameter(name="y", display_name="Y", param_type="number", default_value=0, description="Y position"),
            ActionParameter(name="subimage", display_name="Frame", param_type="number", default_value=0, description="Frame index to draw"),
        ],
    ),

    # Runtime: execute_draw_background_action
    "draw_background": ActionType(
        name="draw_background",
        display_name="Draw Background",
        description="Draw a background image, optionally tiled across the screen",
        category="Game",
        icon="🌄",
        parameters=[
            ActionParameter(name="background", display_name="Background", param_type="string", default_value="", description="Background asset name"),
            ActionParameter(name="x", display_name="X", param_type="number", default_value=0, description="X position"),
            ActionParameter(name="y", display_name="Y", param_type="number", default_value=0, description="Y position"),
            ActionParameter(name="tiled", display_name="Tiled", param_type="boolean", default_value=False, description="Tile across the screen", required=False),
        ],
    ),

    # Runtime: execute_draw_variable_action
    "draw_variable": ActionType(
        name="draw_variable",
        display_name="Draw Variable",
        description="Draw the value of a variable on screen",
        category="Game",
        icon="🔢",
        parameters=[
            ActionParameter(name="x", display_name="X", param_type="number", default_value=0, description="X position"),
            ActionParameter(name="y", display_name="Y", param_type="number", default_value=0, description="Y position"),
            ActionParameter(name="variable", display_name="Variable", param_type="string", default_value="", description="Variable name (self.var, global.var, or bare name)"),
        ],
    ),

    # Runtime: execute_draw_health_bar_action (line 2427)
    "draw_health_bar": ActionType(
        name="draw_health_bar",
        display_name="Draw Health Bar",
        description="Draw the current health as a two-colour bar",
        category="Score",
        icon="🩺",
        parameters=[
            ActionParameter(name="x1", display_name="X1", param_type="number", default_value=0, description="Left X"),
            ActionParameter(name="y1", display_name="Y1", param_type="number", default_value=0, description="Top Y"),
            ActionParameter(name="x2", display_name="X2", param_type="number", default_value=100, description="Right X"),
            ActionParameter(name="y2", display_name="Y2", param_type="number", default_value=20, description="Bottom Y"),
            ActionParameter(name="back_color", display_name="Back Color", param_type="color", default_value="#FF0000", description="Background (empty) colour"),
            ActionParameter(name="bar_color", display_name="Bar Color", param_type="color", default_value="#00FF00", description="Filled (health) colour"),
        ],
    ),

    # Sprite / drawing state --------------------------------------------

    # Runtime: execute_set_alpha_action
    "set_alpha": ActionType(
        name="set_alpha",
        display_name="Set Alpha",
        description="Set the drawing transparency for subsequent draws",
        category="Game",
        icon="🌫️",
        parameters=[
            ActionParameter(name="alpha", display_name="Alpha", param_type="float", default_value=1.0, description="Opacity 0.0 (clear) to 1.0 (opaque)", min_value=0, max_value=1),
        ],
    ),

    # Runtime: execute_set_color_action
    "set_color": ActionType(
        name="set_color",
        display_name="Set Color",
        description="Set the draw colour and alpha for subsequent draws",
        category="Game",
        icon="🎨",
        parameters=[
            ActionParameter(name="color", display_name="Color", param_type="color", default_value="#FFFFFF", description="RGB hex colour"),
            ActionParameter(name="alpha", display_name="Alpha", param_type="float", default_value=1.0, description="Opacity 0.0–1.0", required=False, min_value=0, max_value=1),
        ],
    ),

    # Runtime: execute_set_image_index_action
    "set_image_index": ActionType(
        name="set_image_index",
        display_name="Set Image Index",
        description="Set the current animation frame of the instance's sprite",
        category="Instance",
        icon="🖼️",
        parameters=[
            ActionParameter(name="frame", display_name="Frame", param_type="number", default_value=0, description="Frame index"),
        ],
    ),

    # Runtime: execute_set_image_speed_action
    "set_image_speed": ActionType(
        name="set_image_speed",
        display_name="Set Image Speed",
        description="Set the animation playback speed of the instance's sprite",
        category="Instance",
        icon="⏩",
        parameters=[
            ActionParameter(name="speed", display_name="Speed", param_type="float", default_value=1.0, description="Frames advanced per step (0 = paused)"),
        ],
    ),

    # Runtime: execute_start_animation_action — no parameters
    "start_animation": ActionType(
        name="start_animation",
        display_name="Start Animation",
        description="Resume the instance's sprite animation (image_speed = 1)",
        category="Instance",
        icon="▶️",
        parameters=[],
    ),

    # Runtime: execute_stop_animation_action — no parameters
    "stop_animation": ActionType(
        name="stop_animation",
        display_name="Stop Animation",
        description="Pause the instance's sprite animation (image_speed = 0)",
        category="Instance",
        icon="⏸️",
        parameters=[],
    ),

    # Conditionals (skip-next-action-if-false model) --------------------

    # Runtime: execute_test_score_action
    "test_score": ActionType(
        name="test_score",
        display_name="Test Score",
        description="Conditional: compare the score against a value",
        category="Score",
        icon="❓🏆",
        parameters=[
            ActionParameter(name="value", display_name="Value", param_type="number", default_value=0, description="Value to compare against"),
            ActionParameter(name="operation", display_name="Comparison", param_type="choice", default_value="equal", description="Comparison operator", choices=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"]),
        ],
    ),

    # Runtime: execute_test_lives_action
    "test_lives": ActionType(
        name="test_lives",
        display_name="Test Lives",
        description="Conditional: compare the life count against a value",
        category="Score",
        icon="❓❤️",
        parameters=[
            ActionParameter(name="value", display_name="Value", param_type="number", default_value=0, description="Value to compare against"),
            ActionParameter(name="operation", display_name="Comparison", param_type="choice", default_value="equal", description="Comparison operator", choices=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"]),
        ],
    ),

    # Runtime: execute_test_chance_action
    "test_chance": ActionType(
        name="test_chance",
        display_name="Test Chance",
        description="Conditional: true with probability 1 in 'sides'",
        category="Control",
        icon="🎲❓",
        parameters=[
            ActionParameter(name="sides", display_name="Sides", param_type="number", default_value=6, description="A 1-in-N chance of being true"),
        ],
    ),

    # Runtime: execute_test_question_action
    "test_question": ActionType(
        name="test_question",
        display_name="Test Question",
        description="Conditional: show a yes/no dialog; true if the user answers yes",
        category="Control",
        icon="❓💬",
        parameters=[
            ActionParameter(name="question", display_name="Question", param_type="string", default_value="Continue?", description="Question shown to the player"),
        ],
    ),

    # Runtime: execute_test_instance_count_action
    "test_instance_count": ActionType(
        name="test_instance_count",
        display_name="Test Instance Count",
        description="Conditional: compare the number of instances of an object",
        category="Instance",
        icon="❓🔢",
        parameters=[
            ActionParameter(name="object", display_name="Object", param_type="object", default_value="", description="Object to count"),
            ActionParameter(name="number", display_name="Number", param_type="number", default_value=0, description="Value to compare against"),
            ActionParameter(name="operation", display_name="Comparison", param_type="choice", default_value="equal", description="Comparison operator", choices=["equal", "less", "greater", "less_equal", "greater_equal", "not_equal"]),
        ],
    ),

    # Runtime: execute_check_sound_action
    "check_sound": ActionType(
        name="check_sound",
        display_name="Check Sound Playing",
        description="Conditional: true if the given sound is currently playing",
        category="Audio",
        icon="❓🔊",
        parameters=[
            ActionParameter(name="sound", display_name="Sound", param_type="sound", default_value="", description="Sound to check"),
            ActionParameter(name="not_flag", display_name="Negate", param_type="boolean", default_value=False, description="Invert the result", required=False),
        ],
    ),

    # Runtime: execute_check_room_action
    "check_room": ActionType(
        name="check_room",
        display_name="Check Room",
        description="Conditional: true if the current room matches",
        category="Room",
        icon="❓🚪",
        parameters=[
            ActionParameter(name="room", display_name="Room", param_type="room", default_value="", description="Room to compare against"),
            ActionParameter(name="not_flag", display_name="Negate", param_type="boolean", default_value=False, description="Invert the result", required=False),
        ],
    ),

    # Sound --------------------------------------------------------------

    # Runtime: execute_stop_sound_action
    "stop_sound": ActionType(
        name="stop_sound",
        display_name="Stop Sound",
        description="Stop a playing sound",
        category="Audio",
        icon="🔇",
        parameters=[
            ActionParameter(name="sound", display_name="Sound", param_type="sound", default_value="", description="Sound to stop"),
        ],
    ),

    # Movement / misc ----------------------------------------------------

    # Runtime: execute_move_towards_point_action
    "move_towards_point": ActionType(
        name="move_towards_point",
        display_name="Move Towards Point",
        description="Move towards a point at a given speed",
        category="Movement",
        icon="🎯",
        parameters=[
            ActionParameter(name="x", display_name="X", param_type="number", default_value=0, description="Target X"),
            ActionParameter(name="y", display_name="Y", param_type="number", default_value=0, description="Target Y"),
            ActionParameter(name="speed", display_name="Speed", param_type="float", default_value=4.0, description="Movement speed"),
        ],
    ),

    # Runtime: execute_open_webpage_action
    "open_webpage": ActionType(
        name="open_webpage",
        display_name="Open Webpage",
        description="Open a URL in the default browser",
        category="Game",
        icon="🌐",
        parameters=[
            ActionParameter(name="url", display_name="URL", param_type="string", default_value="", description="Web address to open"),
        ],
    ),

    # Runtime: execute_show_info_action — no parameters
    "show_info": ActionType(
        name="show_info",
        display_name="Show Game Info",
        description="Display the game information screen",
        category="Game",
        icon="ℹ️",
        parameters=[],
    ),

    # Runtime: execute_set_room_caption_action
    "set_room_caption": ActionType(
        name="set_room_caption",
        display_name="Set Room Caption",
        description="Set the game window's title caption",
        category="Room",
        icon="🏷️",
        parameters=[
            ActionParameter(name="caption", display_name="Caption", param_type="string", default_value="", description="Window title text"),
        ],
    ),

    # Runtime: execute_clear_highscore_action (line 2403) — no parameters
    "clear_highscore": ActionType(
        name="clear_highscore",
        display_name="Clear High-Score Table",
        description="Clear all high-score entries",
        category="Score",
        icon="🗑️🏆",
        parameters=[],
    ),
}

# Mapping from Blockly block types to action_types names
# This allows filtering actions based on Blockly configuration presets
BLOCKLY_TO_ACTION_MAP = {
    # Movement
    "move_set_hspeed": "set_hspeed",
    "move_set_vspeed": "set_vspeed",
    "move_stop": "stop_movement",
    "move_snap_to_grid": "snap_to_grid",
    "move_jump_to": "jump_to_position",
    "move_direction": "move_fixed",
    "move_free": "move_free",
    "set_speed": "set_speed",
    "set_direction": "set_direction",
    "move_towards": "move_towards",
    "set_gravity": "set_gravity",
    "set_friction": "set_friction",
    "reverse_horizontal": "reverse_horizontal",
    "reverse_vertical": "reverse_vertical",
    "bounce": "bounce",
    "wrap_around_room": "wrap_around_room",
    "move_to_contact": "move_to_contact",
    # Grid movement
    "grid_stop_if_no_keys": "stop_if_no_keys",
    "grid_check_keys_and_move": "check_keys_and_move",
    "grid_if_on_grid": "if_on_grid",
    "move_grid": "move_grid",
    # Timing
    "set_alarm": "set_alarm",
    # Drawing
    "draw_text": "draw_text",
    "draw_rectangle": "draw_rectangle",
    "draw_circle": "draw_circle",
    "set_sprite": "set_sprite",
    "set_alpha": "set_alpha",
    # Score/Lives/Health. The *_add Blockly blocks emit the same set_* action
    # with relative=True (see blockly_generators.js), so the set_* mapping
    # covers both blocks; there is no separate add_* action to map to.
    "score_set": "set_score",
    "lives_set": "set_lives",
    "health_set": "set_health",
    "draw_score": "draw_score",
    "draw_lives": "draw_lives",
    "draw_health_bar": "draw_health_bar",
    # Instance
    "instance_destroy": "destroy_instance",
    "instance_destroy_other": "destroy_other",
    "instance_create": "create_instance",
    "instance_change": "change_instance",
    "if_can_push": "if_can_push",
    # Room — block names map to the action names the Blockly generators
    # actually emit (verified in blockly_generators.js cases for these blocks).
    "room_goto_next": "next_room",
    "room_goto_previous": "previous_room",
    "room_restart": "restart_room",
    "room_goto": "goto_room",
    "room_if_next_exists": "if_next_room_exists",
    "room_if_previous_exists": "if_previous_room_exists",
    # No "game_restart" entry: the canonical action is `restart_game`, which has
    # no Blockly block and is intentionally always-available (unmapped) in the
    # Add Action menu. The legacy game_restart block-name has no generator.
    "game_end": "game_end",
    # Values/Control flow
    "if_condition": "if_condition",
    "set_variable": "set_variable",
    "test_variable": "test_variable",
    "if_collision_at": "if_collision_at",
    "check_empty": "check_empty",
    "check_collision": "check_collision",
    "test_expression": "test_expression",
    "start_block": "start_block",
    "end_block": "end_block",
    "else_action": "else_action",
    "repeat": "repeat",
    "exit_event": "exit_event",
    # Sound — the Audio Actions plugin (plugins/audio_actions.py) actions
    # (play_sound, stop_sound, play_music, stop_music, set_volume) are
    # intentionally NOT mapped here. Actions with no block mapping fall through
    # the "include if unmapped" path in get_actions_by_category, so basic audio
    # is available in every preset. Future, more specialised audio actions
    # (e.g. microphone input) can opt into preset gating by adding a
    # block-name -> action-name entry here plus a matching BLOCK_REGISTRY block.
    # Output — show_message gates on the BLOCK_REGISTRY "output_message" block
    # (the registry uses the block-name, the action uses the runtime-name).
    "output_message": "show_message",
    "display_message": "display_message",
}

# Reverse mapping: action_types name -> Blockly block type
ACTION_TO_BLOCKLY_MAP = {v: k for k, v in BLOCKLY_TO_ACTION_MAP.items()}

# Some actions are registered in ACTION_TYPES under their block-style alias
# (e.g. ``room_goto_next``) while the runtime executor knows them by a
# different canonical name (``next_room``). For those, the reverse mapping
# above only covers the canonical -> block direction; the picker also needs
# alias -> alias self-mapping or the alias variant falls through the
# "include if unmapped" backward-compat path and leaks past preset gating.
#
# This is single-sourced: any Blockly block name that is *also* an
# ACTION_TYPES key gets a self-mapping automatically, so adding a new alias
# in those two dicts is the only edit required.
for _block_name in BLOCKLY_TO_ACTION_MAP:
    if _block_name in ACTION_TYPES:
        ACTION_TO_BLOCKLY_MAP[_block_name] = _block_name
del _block_name


# Legacy action-name aliases. When a project's saved JSON references an alias name
# (typically older GameMaker-style names like "room_restart" / "room_goto_next" that we've
# consolidated under their canonical equivalents), look up the canonical entry instead so
# the action dialog still loads. The runtime keeps its own alias map at
# runtime/action_executor.py:ACTION_ALIASES for handler dispatch.
ACTION_TYPE_ALIASES = {
    "room_restart": "restart_room",
    "room_goto_next": "next_room",
    "room_goto_previous": "previous_room",
    # "Go to Room" / "Restart Game" duplicate UI actions consolidated into the
    # canonical goto_room / restart_game (the names saved projects actually use).
    "room_goto": "goto_room",
    "game_restart": "restart_game",
    # Legacy duplicates consolidated into set_* + the Relative checkbox. Kept so
    # any add_* still in older project JSON resolves to the right dialog; the
    # relative semantics are restored by migrate_legacy_actions() on load.
    "add_score": "set_score",
    "add_lives": "set_lives",
    "add_health": "set_health",
}


# Legacy GameMaker-style duplicate actions that were merged into their set_*
# counterpart plus a Relative flag. Old project JSON (and the deprecated
# runtime aliases) referenced these standalone names; migrate_legacy_actions()
# rewrites them to the canonical set_*(relative=True) form on load so a single
# action with a Relative checkbox is the only thing users see or edit.
LEGACY_RELATIVE_ADD_ACTIONS = {
    "add_score": "set_score",
    "add_lives": "set_lives",
    "add_health": "set_health",
}


def migrate_legacy_actions(node) -> int:
    """Recursively rewrite legacy add_* actions to set_*(relative=True) in place.

    Walks any nested structure (asset dicts, event dicts, action lists,
    then/else branches, action_list parameters) and normalises every
    ``{"action": "add_*"}`` node it finds. Returns the number of actions
    migrated so callers can log/skip a no-op save.
    """
    count = 0
    if isinstance(node, dict):
        action = node.get("action")
        if isinstance(action, str) and action in LEGACY_RELATIVE_ADD_ACTIONS:
            node["action"] = LEGACY_RELATIVE_ADD_ACTIONS[action]
            params = node.get("parameters")
            if not isinstance(params, dict):
                params = {}
                node["parameters"] = params
            params["relative"] = True
            count += 1
        for value in node.values():
            count += migrate_legacy_actions(value)
    elif isinstance(node, list):
        for item in node:
            count += migrate_legacy_actions(item)
    return count


def get_action_type(action_name: str) -> Optional[ActionType]:
    """Get action type by name. Follows ACTION_TYPE_ALIASES for legacy names."""
    if action_name in ACTION_TYPES:
        return ACTION_TYPES[action_name]
    aliased = ACTION_TYPE_ALIASES.get(action_name)
    if aliased:
        return ACTION_TYPES.get(aliased)
    return None


def get_actions_by_category(blockly_config=None) -> Dict[str, List[ActionType]]:
    """Get actions organized by category

    Args:
        blockly_config: Optional BlocklyConfig to filter actions.
                       If provided, only actions enabled in the config are returned.
    """
    categories = {}
    for action in ACTION_TYPES.values():
        # If a config is provided, check if action is enabled
        if blockly_config is not None:
            # Get the Blockly block type for this action
            blockly_type = ACTION_TO_BLOCKLY_MAP.get(action.name)
            if blockly_type:
                # Check if this block is enabled in the config
                if not blockly_config.is_block_enabled(blockly_type):
                    continue
            # If no mapping exists, include the action (backward compatibility)

        if action.category not in categories:
            categories[action.category] = []
        categories[action.category].append(action)
    return categories

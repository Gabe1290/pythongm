#!/usr/bin/env python3
"""
Action types for the GameMaker IDE
Defines available actions and their parameters
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ActionParameter:
    """Defines a parameter for an action"""
    name: str
    display_name: str
    param_type: str  # "number", "string", "object", "sprite", "boolean"
    default_value: Any
    description: str = ""
    required: bool = True
    choices: List[str] = field(default_factory=list)  # Add this line

@dataclass  
class ActionType:
    """Defines an action type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: Optional[str] = None
    parameters: List[ActionParameter] = field(default_factory=list)

# Define available action types
ACTION_TYPES = {
    "move": ActionType(
        name="move",
        display_name="Move Fixed",  # Changed name for clarity
        description="Move the object in a fixed direction with specified speed",
        category="Movement",
        icon="➡️",
        parameters=[
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="choice",  # Changed from "number" to "choice"
                default_value="right",
                description="Direction to move",
                choices=["right", "up", "left", "down", "up-right", "up-left", "down-right", "down-left"]  # Add this line
            ),
            ActionParameter(
                name="speed",
                display_name="Speed",
                param_type="number",
                default_value=4,  # Changed from 1 to 4 for better default
                description="Speed in pixels per frame"
            ),
            ActionParameter(
                name="relative",
                display_name="Relative",
                param_type="boolean",  # This creates a checkbox
                default_value=False,
                description="If checked, speed is added to current speed. If unchecked, speed replaces current speed"
            )
        ]
    ),
    "set_variable": ActionType(
        name="set_variable",
        display_name="Set Variable", 
        description="Set a variable to a value",
        category="Variables",
        icon="📝",
        parameters=[
            ActionParameter(
                name="variable_name",
                display_name="Variable Name",
                param_type="string",
                default_value="my_variable",
                description="Name of the variable to set"
            ),
            ActionParameter(
                name="value",
                display_name="Value", 
                param_type="string",
                default_value="0",
                description="Value to assign to the variable"
            )
        ]
    ),
    "destroy_instance": ActionType(
        name="destroy_instance",
        display_name="Destroy Instance",
        description="Destroy this object instance",
        category="Instance",
        icon="💀",
        parameters=[]
    ),
    "bounce": ActionType(
        name="bounce",
        display_name="Bounce",
        description="Bounce off the collision by reversing direction",
        category="Movement",
        icon="🎾",
        parameters=[
            ActionParameter(
                name="bounce_type",
                display_name="Bounce Type",
                param_type="string",
                default_value="horizontal",
                description="horizontal, vertical, reverse or bounce"
            )
        ]
    ),
    "stop_movement": ActionType(
        name="stop_movement",
        display_name="Stop Movement",
        description="Stop the object's movement",
        category="Movement", 
        icon="🛑",
        parameters=[]
    ),
    "play_sound": ActionType(
        name="play_sound",
        display_name="Play Sound",
        description="Play a sound effect",
        category="Audio",
        icon="🔊",
        parameters=[
            ActionParameter(
                name="sound_name",
                display_name="Sound Name",
                param_type="string",
                default_value="sound1",
                description="Name of the sound to play"
            )
        ]
    ),
    "create_instance": ActionType(
        name="create_instance",
        display_name="Create Instance",
        description="Create a new object instance",
        category="Instance",
        icon="✨",
        parameters=[
            ActionParameter(
                name="object_name",
                display_name="Object Name",
                param_type="string",
                default_value="obj_object1",
                description="Name of the object to create"
            ),
            ActionParameter(
                name="x_offset",
                display_name="X Offset",
                param_type="number",
                default_value=0,
                description="X offset from current position"
            ),
            ActionParameter(
                name="y_offset",
                display_name="Y Offset", 
                param_type="number",
                default_value=0,
                description="Y offset from current position"
            )
        ]
    ),
    "set_horizontal_speed": ActionType(
        name="set_horizontal_speed",
        display_name="Set Horizontal Speed",
        description="Set horizontal movement speed (negative = left, positive = right)",
        category="Movement",
        icon="↔️",
        parameters=[
            ActionParameter(
                name="hspeed",
                display_name="Horizontal Speed",
                param_type="number",
                default_value=0,
                description="Speed in pixels per frame (negative moves left, positive moves right)"
            )
        ]
    ),
    "set_vertical_speed": ActionType(
        name="set_vertical_speed",
        display_name="Set Vertical Speed",
        description="Set vertical movement speed (negative = up, positive = down)",
        category="Movement",
        icon="↕️",
        parameters=[
            ActionParameter(
                name="vspeed",
                display_name="Vertical Speed",
                param_type="number",
                default_value=0,
                description="Speed in pixels per frame (negative moves up, positive moves down)"
            )
        ]
    ),
    "move_grid": ActionType(
        name="move_grid",
        display_name="Move Grid",
        description="Move one grid unit in the specified direction",
        category="Movement",
        icon="⬛",
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
    # Conditional Logic Actions

    "if_position_empty": ActionType(
        name="if_position_empty",
        display_name="If Position Empty",
        description="Check if a grid position is empty, then perform action",
        category="Logic", 
        icon="❓",
        parameters=[
            ActionParameter(
                name="check_direction",
                display_name="Check Direction",
                param_type="choice",
                default_value="ahead",
                description="Which position to check",
                choices=["ahead", "behind", "left", "right", "current"]
            ),
            ActionParameter(
                name="distance",
                display_name="Distance",
                param_type="number",
                default_value=1,
                description="How many grid units away to check"
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Do",
                param_type="choice",
                default_value="allow_movement",
                description="What to do if position is empty",
                choices=["allow_movement", "move_object", "create_object", "nothing"]
            )
        ]
    ),

    "if_key_pressed": ActionType(
        name="if_key_pressed",
        display_name="If Key Pressed",
        description="Check if a specific key is currently pressed",
        category="Logic",
        icon="⌨️",
        parameters=[
            ActionParameter(
                name="key",
                display_name="Key",
                param_type="choice",
                default_value="space",
                description="Which key to check",
                choices=["space", "enter", "shift", "ctrl", "alt"]
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Do",
                param_type="choice",
                default_value="create_object",
                description="Action to perform if key is pressed",
                choices=["create_object", "destroy_object", "play_sound", "change_sprite"]
            )
        ]
    ),

    "if_instance_count": ActionType(
        name="if_instance_count",
        display_name="If Instance Count",
        description="Check the number of instances of an object and perform action if condition is met",
        category="Logic",
        icon="🔢",
        parameters=[
            ActionParameter(
                name="object_name",
                display_name="Object Type",
                param_type="string",
                default_value="obj_box",
                description="Object type to count"
            ),
            ActionParameter(
                name="operator",
                display_name="Comparison",
                param_type="choice",
                default_value="==",
                description="How to compare the count",
                choices=["==", "!=", "<", ">", "<=", ">="]
            ),
            ActionParameter(
                name="count",
                display_name="Count Value",
                param_type="number",
                default_value=0,
                description="Number to compare against"
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Do Action",
                param_type="choice",
                default_value="change_room",
                description="Action to perform if condition is true",
                choices=["change_room", "create_instance", "destroy_instance", "play_sound"]
            ),
            ActionParameter(
                name="room_name",
                display_name="Room Name (for change_room)",
                param_type="string",
                default_value="Room02",
                description="Name of room to change to (only used if Then Do is change_room)",
                required=False
            )
        ]
    ),

    "change_room": ActionType(
        name="change_room",
        display_name="Change Room",
        description="Change to a different room",
        category="Game Flow",
        icon="🚪",
        parameters=[
            ActionParameter(
                name="room_name",
                display_name="Room Name",
                param_type="string",
                default_value="Room01",
                description="Name of the room to change to"
            )
        ]
    ),
    "if_variable_equals": ActionType(
        name="if_variable_equals",
        display_name="If Variable Equals",
        description="Check if a variable equals a value, then execute an action",
        category="Logic",
        icon="🔍",
        parameters=[
            ActionParameter(
                name="variable_name",
                display_name="Variable Name",
                param_type="string",
                default_value="soko_active",
                description="Name of the variable to check"
            ),
            ActionParameter(
                name="value",
                display_name="Value",
                param_type="string",
                default_value="1",
                description="Value to compare against"
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Execute",
                param_type="choice",
                default_value="if_instance_count",
                description="Action to execute if condition is true",
                choices=["if_instance_count", "change_room", "destroy_instance", "play_sound"]
            )
        ]
    ),
    "delay_action": ActionType(
        name="delay_action",
        display_name="Delay Action / Wait",
        description="Wait for a specified time, then execute an action",
        category="Logic",
        icon="⏰",
        parameters=[
            ActionParameter(
                name="frames",
                display_name="Wait Time (frames)",
                param_type="number",
                default_value=60,
                description="Number of frames to wait (60 frames = 1 second at 60 FPS)"
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Execute",
                param_type="choice",
                default_value="change_room",
                description="Action to execute after waiting",
                choices=["change_room", "destroy_instance", "play_sound", "if_instance_count"]
            ),
            ActionParameter(
                name="room_name",
                display_name="Room Name (for change_room)",
                param_type="string",
                default_value="Room02",
                description="Name of room to change to (only used if Then Do is change_room)"
            )
        ]
    ),
    "if_condition": ActionType(
        name="if_condition",
        display_name="If Condition",
        description="Execute different actions based on a condition",
        category="Logic",
        icon="🔀",
        parameters=[
            ActionParameter(
                name="condition_type",
                display_name="Condition Type",
                param_type="choice",
                default_value="instance_count",
                description="Type of condition to check",
                choices=["instance_count", "variable_compare"]
            ),
            ActionParameter(
                name="object_name",
                display_name="Object Name",
                param_type="string",
                default_value="obj_box",
                description="Object to count (for instance_count)"
            ),
            ActionParameter(
                name="operator",
                display_name="Operator",
                param_type="choice",
                default_value="==",
                description="Comparison operator",
                choices=["==", "!=", "<", ">", "<=", ">="]
            ),
            ActionParameter(
                name="value",
                display_name="Value",
                param_type="number",
                default_value=0,
                description="Value to compare against"
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Do (if true)",
                param_type="action_list",
                default_value=[],
                description="Actions to execute if condition is true"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Do (if false)",
                param_type="action_list",
                default_value=[],
                description="Actions to execute if condition is false"
            )
        ]
    ),
    "show_message": ActionType(
        name="show_message",
        display_name="Show Message Box",
        description="Display a message box that pauses the game until dismissed",
        category="Interface",
        icon="💬",
        parameters=[
            ActionParameter(
                name="message",
                display_name="Message Text",
                param_type="string",
                default_value="Hello, World!",
                description="The message to display"
            ),
            ActionParameter(
                name="title",
                display_name="Title",
                param_type="string",
                default_value="Message",
                description="Title of the message box"
            ),
            ActionParameter(
                name="button_text",
                display_name="Button Text",
                param_type="string",
                default_value="OK",
                description="Text for the dismiss button"
            ),
            ActionParameter(
                name="pause_game",
                display_name="Pause Game",
                param_type="boolean",
                default_value=True,
                description="Pause the game while the message is shown"
            )
        ]
    ),
    "next_room": ActionType(
        name="next_room",
        display_name="Next Room",
        description="Go to the next room in the room list",
        category="Game Flow",
        icon="➡️",
        parameters=[]
    ),

    "previous_room": ActionType(
        name="previous_room",
        display_name="Previous Room",
        description="Go to the previous room in the room list",
        category="Game Flow",
        icon="⬅️",
        parameters=[]
    ),

    "if_next_room_exists": ActionType(
        name="if_next_room_exists",
        display_name="If Next Room Exists",
        description="Check if there's a next room and execute actions",
        category="Logic",
        icon="❓",
        parameters=[
            ActionParameter(
                name="then_action",
                display_name="If Exists, Do",
                param_type="choice",
                default_value="next_room",
                description="Action to perform if next room exists",
                choices=["next_room", "show_message", "set_variable", "play_sound"]
            ),
            ActionParameter(
                name="else_action",
                display_name="If Not Exists, Do",
                param_type="choice",
                default_value="show_message",
                description="Action to perform if no next room",
                choices=["show_message", "change_room", "restart_game", "nothing"]
            ),
            ActionParameter(
                name="else_room",
                display_name="Else Go To Room",
                param_type="string",
                default_value="Room01",
                description="Room to go to if no next room (for change_room option)"
            )
        ]
    ),

    "if_previous_room_exists": ActionType(
        name="if_previous_room_exists",
        display_name="If Previous Room Exists",
        description="Check if there's a previous room and execute actions",
        category="Logic",
        icon="❓",
        parameters=[
            ActionParameter(
                name="then_action",
                display_name="If Exists, Do",
                param_type="choice",
                default_value="previous_room",
                description="Action to perform if previous room exists",
                choices=["previous_room", "show_message", "set_variable", "play_sound"]
            ),
            ActionParameter(
                name="else_action",
                display_name="If Not Exists, Do",
                param_type="choice",
                default_value="show_message",
                description="Action to perform if no previous room",
                choices=["show_message", "change_room", "restart_game", "nothing"]
            ),
            ActionParameter(
                name="else_room",
                display_name="Else Go To Room",
                param_type="string",
                default_value="Room01",
                description="Room to go to if no previous room (for change_room option)"
            ),
        ]
    ),

    "push_object": ActionType(
        name="push_object",
        display_name="Push Object",
        description="Push another object in a direction",
        category="Instance",
        icon="👉",
        parameters=[
            ActionParameter(
                name="target",
                display_name="Target",
                param_type="choice",
                default_value="other",
                description="Which object to push",
                choices=["other", "self"]
            ),
            ActionParameter(
                name="direction",
                display_name="Direction",
                param_type="choice",
                default_value="right",
                description="Direction to push",
                choices=["right", "left", "up", "down"]
            ),
            ActionParameter(
                name="distance",
                display_name="Distance",
                param_type="number",
                default_value=32,
                description="Distance in pixels"
            ),
            ActionParameter(
                name="check_collision",
                display_name="Check Collision",
                param_type="boolean",
                default_value=True,
                description="Check if destination is free"
            )
        ]
    ),

    "snap_to_grid": ActionType(
        name="snap_to_grid",
        display_name="Snap to Grid",
        description="Align instance position to grid",
        category="Movement",
        icon="📐",
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

    "if_place_free": ActionType(
        name="if_place_free",
        display_name="If Place Free",
        description="Check if a position is collision-free (supports expressions)",
        category="Control",
        icon="🔍",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x + 32",
                description="X position (can use: self.x, other.x, expressions like self.x + other.hspeed)"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position (can use: self.y, other.y, expressions like self.y + other.vspeed)"
            ),
            ActionParameter(
                name="then_action",
                display_name="Then Action",
                param_type="choice",
                default_value="move_to_position",
                description="Action to execute if free",
                choices=["move_to_position", "push_object", "stop_movement", "destroy_instance", "create_instance"]
            ),
            ActionParameter(
                name="else_action",
                display_name="Else Action",
                param_type="choice",
                default_value="stop_movement",
                description="Action to execute if blocked",
                choices=["stop_movement", "bounce", "destroy_instance", "move_to_position"]
            )
        ]
    ),

    "move_to_position": ActionType(
        name="move_to_position",
        display_name="Move to Position",
        description="Set instance position directly",
        category="Movement",
        icon="📍",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x",
                description="X position (can use expressions like self.x + 32)"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position (can use expressions like self.y + 32)"
            ),
            ActionParameter(
                name="smooth",
                display_name="Smooth Movement",
                param_type="boolean",
                default_value=False,
                description="Use smooth grid movement animation"
            )
        ]
    ),

    "if_collision_at": ActionType(
        name="if_collision_at",
        display_name="If Collision At",
        description="Check for collision at a position (supports expressions like self.x + 32, other.x, etc.)",
        category="Control",
        icon="🎯",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x + 32",
                description="X position (can use: self.x, other.x, self.x + 32, self.hspeed, etc.)"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position (can use: self.y, other.y, self.y + 32, self.vspeed, etc.)"
            ),
            ActionParameter(
                name="object_type",
                display_name="Object Type",
                param_type="choice",  # ← MUST be "choice", not "string"
                default_value="any",
                description="Object type to check (or 'any' 'solid'",
                choices=["any", "solid"]  
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Action if collision found"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Action if no collision"
            )
        ]
    ),

    "set_hspeed": ActionType(
        name="set_hspeed",
        display_name="Set Horizontal Speed",
        description="Set horizontal velocity component",
        category="Movement",
        icon="↔️",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Horizontal Speed",
                param_type="string",
                default_value="0",
                description="Horizontal speed (can use expressions)"
            )
        ]
    ),

    "set_vspeed": ActionType(
        name="set_vspeed",
        display_name="Set Vertical Speed",
        description="Set vertical velocity component",
        category="Movement",
        icon="↕️",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Vertical Speed",
                param_type="string",
                default_value="0",
                description="Vertical speed (can use expressions)"
            )
        ]
    ),

    "transform_to": ActionType(
        name="transform_to",
        display_name="Transform To Object",
        description="Transform this instance into a different object type",
        category="Instance",
        icon="🔄",
        parameters=[
            ActionParameter(
                name="object_name",
                display_name="New Object Type",
                param_type="string",
                default_value="obj_box_store",
                description="Name of the object to transform into"
            )
        ]
    )
}

def get_action_type(action_name: str) -> Optional[ActionType]:
    """Get action type by name"""
    return ACTION_TYPES.get(action_name)

def get_available_actions() -> List[ActionType]:
    """Get list of all available actions"""
    return list(ACTION_TYPES.values())

def get_actions_by_category() -> Dict[str, List[ActionType]]:
    """Get actions organized by category"""
    categories = {}
    for action in ACTION_TYPES.values():
        if action.category not in categories:
            categories[action.category] = []
        categories[action.category].append(action)
    return categories
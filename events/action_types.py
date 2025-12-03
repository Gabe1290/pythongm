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

@dataclass  
class ActionType:
    """Defines an action type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: Optional[str] = None
    parameters: List[ActionParameter] = field(default_factory=list)

ACTION_TYPES = {
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
    
    "if_on_grid": ActionType(
        name="if_on_grid",
        display_name="If On Grid",
        description="Check if object is aligned to grid",
        category="Grid",
        icon="🎯",
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
        icon="⏸️",
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
        category="Game",
        icon="🔄",
        parameters=[]
    ),
    
    "next_room": ActionType(
        name="next_room",
        display_name="Next Room",
        description="Go to next room",
        category="Game",
        icon="➡️",
        parameters=[]
    ),

    "previous_room": ActionType(
        name="previous_room",
        display_name="Previous Room",
        description="Go to previous room",
        category="Game",
        icon="⬅️",
        parameters=[]
    ),

    "if_next_room_exists": ActionType(
        name="if_next_room_exists",
        display_name="If Next Room Exists",
        description="Check if there is a next room after the current one",
        category="Game",
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
        category="Game",
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

    "destroy_instance": ActionType(
        name="destroy_instance",
        display_name="Destroy Instance",
        description="Destroy an instance (self or other)",
        category="Instance",
        icon="💀",
        parameters=[
            ActionParameter(
                name="target",
                display_name="Target",
                param_type="choice",
                default_value="self",
                description="Which instance to destroy",
                choices=["self", "other"]
            )
        ]
    ),

    # GAMEMAKER 7.0 MOVEMENT ACTIONS
    "move_fixed": ActionType(
        name="move_fixed",
        display_name="Move Fixed",
        description="Start moving in a fixed direction (8-way)",
        category="Movement",
        icon="➡️",
        parameters=[
            ActionParameter(
                name="directions",
                display_name="Directions",
                param_type="choice",
                default_value="right",
                description="Direction to move (can select multiple for random choice)",
                choices=["left", "right", "up", "down", "up-left", "up-right", "down-left", "down-right", "stop"],
                multi_select=True
            ),
            ActionParameter(
                name="speed",
                display_name="Speed",
                param_type="float",
                default_value=4.0,
                description="Movement speed in pixels per step"
            )
        ]
    ),

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

    "move_towards": ActionType(
        name="move_towards",
        display_name="Move Towards",
        description="Move towards a specific position",
        category="Movement",
        icon="🎯",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="0",
                description="Target X position (can be expression)"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="0",
                description="Target Y position (can be expression)"
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
        description="Check if position is collision-free",
        category="Control",
        icon="🔍",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x",
                description="X position to check"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position to check"
            ),
            ActionParameter(
                name="only_solid",
                display_name="Only Solid Objects",
                param_type="boolean",
                default_value=True,
                description="Check only solid objects"
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if empty"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if not empty"
            )
        ]
    ),

    "check_collision": ActionType(
        name="check_collision",
        display_name="Check Collision",
        description="Check if there's a collision at position",
        category="Control",
        icon="💥",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x",
                description="X position to check"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position to check"
            ),
            ActionParameter(
                name="only_solid",
                display_name="Only Solid Objects",
                param_type="boolean",
                default_value=True,
                description="Check only solid objects"
            ),
            ActionParameter(
                name="then_actions",
                display_name="Then Actions",
                param_type="action_list",
                default_value=[],
                description="Actions if collision"
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

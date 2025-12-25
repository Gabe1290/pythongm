#!/usr/bin/env python3
"""
Action types for the GameMaker IDE - EXPANDED FOR SMOOTH MOVEMENT
Defines available actions and their parameters
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ActionParameter:
    """Defines a parameter for an action"""
    name: str
    display_name: str
    param_type: str  # "number", "string", "object", "sprite", "boolean", "choice"
    default_value: Any
    description: str = ""
    required: bool = True
    choices: List[str] = field(default_factory=list)

@dataclass
class ActionType:
    """Defines an action type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: Optional[str] = None
    parameters: List[ActionParameter] = field(default_factory=list)

# Define available action types - EXPANDED SET WITH SMOOTH MOVEMENT
ACTION_TYPES = {
    # ==================== MOVEMENT ACTIONS ====================

    "move_grid": ActionType(
        name="move_grid",
        display_name="Move Grid",
        description="Move one grid unit in the specified direction (instant grid-based)",
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
        description="Set horizontal movement speed (negative=left, positive=right)",
        category="Movement",
        icon="↔️",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Horizontal Speed",
                param_type="number",
                default_value=0,
                description="Speed in pixels per frame (negative moves left, positive moves right)"
            )
        ]
    ),

    "set_vspeed": ActionType(
        name="set_vspeed",
        display_name="Set Vertical Speed",
        description="Set vertical movement speed (negative=up, positive=down)",
        category="Movement",
        icon="↕️",
        parameters=[
            ActionParameter(
                name="speed",
                display_name="Vertical Speed",
                param_type="number",
                default_value=0,
                description="Speed in pixels per frame (negative moves up, positive moves down)"
            )
        ]
    ),

    "stop_movement": ActionType(
        name="stop_movement",
        display_name="Stop Movement",
        description="Set both horizontal and vertical speed to zero",
        category="Movement",
        icon="🛑",
        parameters=[]
    ),

    # ==================== GRID ACTIONS ====================

    "snap_to_grid": ActionType(
        name="snap_to_grid",
        display_name="Snap to Grid",
        description="Align instance position to nearest grid cell",
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
        description="Check if object is aligned to grid and execute actions conditionally",
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
                description="Actions to execute if on grid"
            ),
            ActionParameter(
                name="else_actions",
                display_name="Else Actions",
                param_type="action_list",
                default_value=[],
                description="Actions to execute if not on grid"
            )
        ]
    ),

    # ==================== CONTROL/LOGIC ACTIONS ====================

    "if_collision_at": ActionType(
        name="if_collision_at",
        display_name="If Collision At",
        description="Check for collision at a position and execute actions conditionally",
        category="Control",
        icon="🎯",
        parameters=[
            ActionParameter(
                name="x",
                display_name="X Position",
                param_type="string",
                default_value="self.x + 32",
                description="X position (can use: self.x, self.x + 32, etc.)"
            ),
            ActionParameter(
                name="y",
                display_name="Y Position",
                param_type="string",
                default_value="self.y",
                description="Y position (can use: self.y, self.y + 32, etc.)"
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

    # ==================== GAME CONTROL ACTIONS ====================

    "show_message": ActionType(
        name="show_message",
        display_name="Show Message",
        description="Display a message to the player",
        category="Game",
        icon="💬",
        parameters=[
            ActionParameter(
                name="message",
                display_name="Message",
                param_type="string",
                default_value="Hello!",
                description="Message text to display"
            )
        ]
    ),

    "restart_room": ActionType(
        name="restart_room",
        display_name="Restart Room",
        description="Restart the current room/level",
        category="Game",
        icon="🔄",
        parameters=[]
    ),

    "next_room": ActionType(
        name="next_room",
        display_name="Next Room",
        description="Go to the next room/level",
        category="Game",
        icon="➡️",
        parameters=[]
    ),

    # ==================== INSTANCE ACTIONS ====================

    "destroy_instance": ActionType(
        name="destroy_instance",
        display_name="Destroy Instance",
        description="Destroy this object instance",
        category="Instance",
        icon="💀",
        parameters=[]
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

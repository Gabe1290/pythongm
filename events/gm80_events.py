#!/usr/bin/env python3
"""
GameMaker 8.0 Complete Event System
All events organized exactly as they appeared in GM8.0
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class EventDefinition:
    """Definition of a GameMaker event"""
    name: str
    display_name: str
    category: str
    description: str
    icon: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    gm_version: str = "8.0"


# ============================================================================
# GAMEMAKER 8.0 EVENT CATEGORIES
# ============================================================================

GM80_EVENT_CATEGORIES = {
    "create": {
        "name": "Create",
        "icon": "🎯",
        "order": 0,
        "description": "Events that occur when instances are created"
    },
    "destroy": {
        "name": "Destroy",
        "icon": "💥",
        "order": 1,
        "description": "Events that occur when instances are destroyed"
    },
    "alarm": {
        "name": "Alarm",
        "icon": "⏰",
        "order": 2,
        "description": "Timer events (12 independent alarms)"
    },
    "step": {
        "name": "Step",
        "icon": "⚡",
        "order": 3,
        "description": "Events that occur every game step"
    },
    "collision": {
        "name": "Collision",
        "icon": "💥",
        "order": 4,
        "description": "Events triggered by collisions with other objects"
    },
    "keyboard": {
        "name": "Keyboard",
        "icon": "⌨️",
        "order": 5,
        "description": "Events triggered by keyboard input"
    },
    "mouse": {
        "name": "Mouse",
        "icon": "🖱️",
        "order": 6,
        "description": "Events triggered by mouse input"
    },
    "other": {
        "name": "Other",
        "icon": "📋",
        "order": 7,
        "description": "Miscellaneous special events"
    },
    "draw": {
        "name": "Draw",
        "icon": "🎨",
        "order": 8,
        "description": "Events for custom drawing"
    }
}


# ============================================================================
# COMPLETE EVENT DEFINITIONS
# ============================================================================

GM80_EVENTS = {
    # CREATE EVENTS
    "create": EventDefinition(
        name="create",
        display_name="Create",
        category="create",
        description="Executed when the instance is created",
        icon="🎯"
    ),

    # DESTROY EVENTS
    "destroy": EventDefinition(
        name="destroy",
        display_name="Destroy",
        category="destroy",
        description="Executed when the instance is destroyed",
        icon="💥"
    ),

    # ALARM EVENTS (0-11)
    **{f"alarm_{i}": EventDefinition(
        name=f"alarm_{i}",
        display_name=f"Alarm {i}",
        category="alarm",
        description=f"Executes when alarm {i} reaches zero",
        icon="⏰"
    ) for i in range(12)},

    # STEP EVENTS
    "begin_step": EventDefinition(
        name="begin_step",
        display_name="Begin Step",
        category="step",
        description="Executed at the beginning of each step, before instances move",
        icon="▶️"
    ),
    "step": EventDefinition(
        name="step",
        display_name="Step",
        category="step",
        description="Normal step event - executed every frame",
        icon="⚡"
    ),
    "end_step": EventDefinition(
        name="end_step",
        display_name="End Step",
        category="step",
        description="Executed at the end of each step, after instances move",
        icon="⏹️"
    ),

    # COLLISION EVENTS - Dynamic based on objects
    "collision": EventDefinition(
        name="collision",
        display_name="Collision",
        category="collision",
        description="Collision with another object",
        icon="💥",
        parameters=[{"type": "object_selector", "description": "Select object to collide with"}]
    ),

    # KEYBOARD EVENTS
    "keyboard_no_key": EventDefinition(
        name="keyboard_no_key",
        display_name="<No Key>",
        category="keyboard",
        description="No keyboard key is currently pressed",
        icon="⌨️"
    ),
    "keyboard_any_key": EventDefinition(
        name="keyboard_any_key",
        display_name="<Any Key>",
        category="keyboard",
        description="Any keyboard key is pressed",
        icon="⌨️"
    ),
    "keyboard": EventDefinition(
        name="keyboard",
        display_name="Keyboard",
        category="keyboard",
        description="Specific key is held down (continuous)",
        icon="⌨️",
        parameters=[{"type": "key_selector", "description": "Select key"}]
    ),
    "keyboard_press": EventDefinition(
        name="keyboard_press",
        display_name="Key Press",
        category="keyboard",
        description="Specific key is pressed (once)",
        icon="🔘",
        parameters=[{"type": "key_selector", "description": "Select key"}]
    ),
    "keyboard_release": EventDefinition(
        name="keyboard_release",
        display_name="Key Release",
        category="keyboard",
        description="Specific key is released",
        icon="⬆️",
        parameters=[{"type": "key_selector", "description": "Select key"}]
    ),

    # MOUSE EVENTS
    "mouse_left_button": EventDefinition(
        name="mouse_left_button",
        display_name="Left Button",
        category="mouse",
        description="Left mouse button is held (continuous)",
        icon="🖱️"
    ),
    "mouse_right_button": EventDefinition(
        name="mouse_right_button",
        display_name="Right Button",
        category="mouse",
        description="Right mouse button is held (continuous)",
        icon="🖱️"
    ),
    "mouse_middle_button": EventDefinition(
        name="mouse_middle_button",
        display_name="Middle Button",
        category="mouse",
        description="Middle mouse button is held (continuous)",
        icon="🖱️"
    ),
    "mouse_no_button": EventDefinition(
        name="mouse_no_button",
        display_name="No Button",
        category="mouse",
        description="No mouse button is pressed",
        icon="🖱️"
    ),
    "mouse_left_press": EventDefinition(
        name="mouse_left_press",
        display_name="Left Pressed",
        category="mouse",
        description="Left mouse button is pressed down (once)",
        icon="🖱️"
    ),
    "mouse_right_press": EventDefinition(
        name="mouse_right_press",
        display_name="Right Pressed",
        category="mouse",
        description="Right mouse button is pressed down (once)",
        icon="🖱️"
    ),
    "mouse_middle_press": EventDefinition(
        name="mouse_middle_press",
        display_name="Middle Pressed",
        category="mouse",
        description="Middle mouse button is pressed down (once)",
        icon="🖱️"
    ),
    "mouse_left_release": EventDefinition(
        name="mouse_left_release",
        display_name="Left Released",
        category="mouse",
        description="Left mouse button is released",
        icon="🖱️"
    ),
    "mouse_right_release": EventDefinition(
        name="mouse_right_release",
        display_name="Right Released",
        category="mouse",
        description="Right mouse button is released",
        icon="🖱️"
    ),
    "mouse_middle_release": EventDefinition(
        name="mouse_middle_release",
        display_name="Middle Released",
        category="mouse",
        description="Middle mouse button is released",
        icon="🖱️"
    ),
    "mouse_enter": EventDefinition(
        name="mouse_enter",
        display_name="Mouse Enter",
        category="mouse",
        description="Mouse cursor enters the instance's bounding box",
        icon="➡️"
    ),
    "mouse_leave": EventDefinition(
        name="mouse_leave",
        display_name="Mouse Leave",
        category="mouse",
        description="Mouse cursor leaves the instance's bounding box",
        icon="⬅️"
    ),
    "mouse_wheel_up": EventDefinition(
        name="mouse_wheel_up",
        display_name="Mouse Wheel Up",
        category="mouse",
        description="Mouse wheel is scrolled up",
        icon="⬆️"
    ),
    "mouse_wheel_down": EventDefinition(
        name="mouse_wheel_down",
        display_name="Mouse Wheel Down",
        category="mouse",
        description="Mouse wheel is scrolled down",
        icon="⬇️"
    ),
    "mouse_global_left_button": EventDefinition(
        name="mouse_global_left_button",
        display_name="Global Left Button",
        category="mouse",
        description="Left button anywhere in room (continuous)",
        icon="🌐"
    ),
    "mouse_global_right_button": EventDefinition(
        name="mouse_global_right_button",
        display_name="Global Right Button",
        category="mouse",
        description="Right button anywhere in room (continuous)",
        icon="🌐"
    ),
    "mouse_global_middle_button": EventDefinition(
        name="mouse_global_middle_button",
        display_name="Global Middle Button",
        category="mouse",
        description="Middle button anywhere in room (continuous)",
        icon="🌐"
    ),
    "mouse_global_left_press": EventDefinition(
        name="mouse_global_left_press",
        display_name="Global Left Pressed",
        category="mouse",
        description="Left button pressed anywhere in room (once)",
        icon="🌐"
    ),
    "mouse_global_right_press": EventDefinition(
        name="mouse_global_right_press",
        display_name="Global Right Pressed",
        category="mouse",
        description="Right button pressed anywhere in room (once)",
        icon="🌐"
    ),
    "mouse_global_middle_press": EventDefinition(
        name="mouse_global_middle_press",
        display_name="Global Middle Pressed",
        category="mouse",
        description="Middle button pressed anywhere in room (once)",
        icon="🌐"
    ),
    "mouse_global_left_release": EventDefinition(
        name="mouse_global_left_release",
        display_name="Global Left Released",
        category="mouse",
        description="Left button released anywhere in room",
        icon="🌐"
    ),
    "mouse_global_right_release": EventDefinition(
        name="mouse_global_right_release",
        display_name="Global Right Released",
        category="mouse",
        description="Right button released anywhere in room",
        icon="🌐"
    ),
    "mouse_global_middle_release": EventDefinition(
        name="mouse_global_middle_release",
        display_name="Global Middle Released",
        category="mouse",
        description="Middle button released anywhere in room",
        icon="🌐"
    ),

    # OTHER EVENTS
    "outside_room": EventDefinition(
        name="outside_room",
        display_name="Outside Room",
        category="other",
        description="Instance is completely outside the room boundaries",
        icon="🚪"
    ),
    "intersect_boundary": EventDefinition(
        name="intersect_boundary",
        display_name="Intersect Boundary",
        category="other",
        description="Instance intersects the room boundary",
        icon="📏"
    ),
    "game_start": EventDefinition(
        name="game_start",
        display_name="Game Start",
        category="other",
        description="Executed once when the game starts (first room)",
        icon="🎮"
    ),
    "game_end": EventDefinition(
        name="game_end",
        display_name="Game End",
        category="other",
        description="Executed when the game ends",
        icon="🏁"
    ),
    "room_start": EventDefinition(
        name="room_start",
        display_name="Room Start",
        category="other",
        description="Executed when a room starts",
        icon="🚪"
    ),
    "room_end": EventDefinition(
        name="room_end",
        display_name="Room End",
        category="other",
        description="Executed when a room ends",
        icon="🚪"
    ),
    "no_more_lives": EventDefinition(
        name="no_more_lives",
        display_name="No More Lives",
        category="other",
        description="Executed when lives become 0 or less",
        icon="💀"
    ),
    "no_more_health": EventDefinition(
        name="no_more_health",
        display_name="No More Health",
        category="other",
        description="Executed when health becomes 0 or less",
        icon="❤️"
    ),
    "animation_end": EventDefinition(
        name="animation_end",
        display_name="Animation End",
        category="other",
        description="Executed when sprite animation reaches the last frame",
        icon="🎬"
    ),
    "end_of_path": EventDefinition(
        name="end_of_path",
        display_name="End of Path",
        category="other",
        description="Executed when instance reaches the end of its path",
        icon="🛤️"
    ),
    "close_button": EventDefinition(
        name="close_button",
        display_name="Close Button",
        category="other",
        description="Executed when the game window close button is pressed",
        icon="❌"
    ),
    **{f"user_event_{i}": EventDefinition(
        name=f"user_event_{i}",
        display_name=f"User Event {i}",
        category="other",
        description=f"Custom user-defined event {i}",
        icon="👤"
    ) for i in range(16)},

    # DRAW EVENT
    "draw": EventDefinition(
        name="draw",
        display_name="Draw",
        category="draw",
        description="Custom drawing event - overrides default sprite drawing",
        icon="🎨"
    ),
}


def get_events_by_category(category: str) -> List[EventDefinition]:
    """Get all events in a specific category"""
    return [event for event in GM80_EVENTS.values() if event.category == category]


def get_event_categories_ordered() -> List[Dict[str, Any]]:
    """Get event categories in display order"""
    return sorted(GM80_EVENT_CATEGORIES.items(), key=lambda x: x[1]["order"])


def get_event(event_name: str) -> EventDefinition:
    """Get a specific event definition"""
    return GM80_EVENTS.get(event_name)

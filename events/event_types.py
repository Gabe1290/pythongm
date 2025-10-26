#!/usr/bin/env python3
"""
Event types for the GameMaker IDE
Defines available events and their properties
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class EventType:
    """Defines an event type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: Optional[str] = None
    parameters: List[Any] = field(default_factory=list)  

# Define available event types
EVENT_TYPES = {
    "create": EventType(
        name="create",
        display_name="Create",
        description="Executed when the object is first created",
        icon="🎯",
        category="Object",
        parameters=[]
    ),
    "step": EventType(
        name="step", 
        display_name="Step",
        description="Executed every frame",
        icon="⏭️",
        category="Object",
        parameters=[]
    ),
    "destroy": EventType(
        name="destroy",
        display_name="Destroy", 
        description="Executed when the object is destroyed",
        icon="💥",
        category="Object",
        parameters=[]
    ),
    "collision": EventType(
        name="collision",
        display_name="Collision",
        description="Executed when colliding with another object",
        icon="💥",
        category="Collision",
        parameters=[
            {
                "type": "object_collision",
                "description": "Select which object type triggers this collision"
            }
        ]
    ),
    "keyboard": EventType(
        name="keyboard",
        display_name="Keyboard",
        description="Executed when a key is pressed",
        category="Input",
        icon="⌨️",
        parameters=[
            {
                "type": "sub_events",
                "keys": ["left", "right", "up", "down"]
            }
        ]
    ),
    "keyboard_press": EventType(
        name="keyboard_press",
        display_name="Keyboard Press",
        description="Executed once when a key is first pressed",
        category="Input",
        icon="🔘",
        parameters=[
            {
                "type": "sub_events",
                "keys": ["left", "right", "up", "down"]
            }
        ]
    )
}

def get_event_type(event_name: str) -> Optional[EventType]:
    """Get event type by name"""
    return EVENT_TYPES.get(event_name)

def get_available_events() -> List[EventType]:
    """Get list of all available events"""
    return list(EVENT_TYPES.values())
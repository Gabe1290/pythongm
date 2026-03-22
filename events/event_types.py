#!/usr/bin/env python3
"""
Event types for the GameMaker IDE - COMPLETE EVENT SYSTEM
Defines available events and their properties
Includes all keyboard (A-Z, 0-9, special keys) and mouse events
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from events.keyboard_events_complete import PYGAME_KEY_CODES, get_all_keyboard_events
from events.mouse_events_complete import PYGAME_MOUSE_BUTTONS, get_all_mouse_events
from events.thymio_events import THYMIO_EVENT_TYPES

@dataclass
class EventType:
    """Defines an event type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: Optional[str] = None
    parameters: List[Any] = field(default_factory=list)

# Define available event types - EXPANDED SET WITH SMOOTH MOVEMENT
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
        description="Executed every frame (use for continuous checks)",
        icon="⭐",
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
        display_name="Collision With...",
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
        description="Executed continuously while a key is held down (for smooth movement)",
        category="Input",
        icon="⌨️",
        parameters=[
            {
                "type": "key_selector",
                "description": "Select which key to respond to",
                "available_keys": "all"  # Will use complete keyboard events
            }
        ]
    ),
    "keyboard_press": EventType(
        name="keyboard_press",
        display_name="Keyboard Press",
        description="Executed once when a key is first pressed (for grid-based movement)",
        category="Input",
        icon="🔘",
        parameters=[
            {
                "type": "key_selector",
                "description": "Select which key to respond to",
                "available_keys": "all"  # Will use complete keyboard events
            }
        ]
    ),
    "keyboard_release": EventType(
        name="keyboard_release",
        display_name="Keyboard Release",
        description="Executed once when a key is released",
        category="Input",
        icon="⬆️",
        parameters=[
            {
                "type": "key_selector",
                "description": "Select which key to respond to",
                "available_keys": "all"  # Will use complete keyboard events
            }
        ]
    ),
    "keyboard_no_key": EventType(
        name="keyboard_no_key",
        display_name="Keyboard <No Key>",
        description="Executed when no keyboard key is currently pressed",
        category="Input",
        icon="⌨️",
        parameters=[]
    ),
    "mouse": EventType(
        name="mouse",
        display_name="Mouse",
        description="Mouse button and movement events",
        category="Input",
        icon="🖱️",
        parameters=[
            {
                "type": "mouse_event_selector",
                "description": "Select which mouse event to respond to",
                "available_events": "all"  # Will use complete mouse events
            }
        ]
    ),
    "begin_step": EventType(
        name="begin_step",
        display_name="Begin Step",
        description="Executed at the beginning of each step, before other events",
        category="Step",
        icon="▶️",
        parameters=[]
    ),
    "end_step": EventType(
        name="end_step",
        display_name="End Step",
        description="Executed at the end of each step, after collisions but before drawing",
        category="Step",
        icon="⏹️",
        parameters=[]
    ),
    "draw": EventType(
        name="draw",
        display_name="Draw",
        description="Executed when the object is drawn (replaces default sprite drawing)",
        category="Drawing",
        icon="🎨",
        parameters=[]
    ),
    "draw_gui": EventType(
        name="draw_gui",
        display_name="Draw GUI",
        description="Drawn on top of everything (not affected by camera/view). Use for HUD, score, lives.",
        category="Drawing",
        icon="🖼️",
        parameters=[]
    ),
    "alarm": EventType(
        name="alarm",
        display_name="Alarm",
        description="Executed when an alarm clock reaches zero",
        category="Timing",
        icon="⏰",
        parameters=[
            {
                "type": "alarm_number",
                "description": "Alarm number (0-11)",
                "min": 0,
                "max": 11
            }
        ]
    ),
    "room_start": EventType(
        name="room_start",
        display_name="Room Start",
        description="Executed when the room starts (after create events)",
        category="Room",
        icon="🚪",
        parameters=[]
    ),
    "room_end": EventType(
        name="room_end",
        display_name="Room End",
        description="Executed when the room ends",
        category="Room",
        icon="🚪",
        parameters=[]
    ),
    "game_start": EventType(
        name="game_start",
        display_name="Game Start",
        description="Executed when the game starts (in first room only)",
        category="Game",
        icon="🎮",
        parameters=[]
    ),
    "game_end": EventType(
        name="game_end",
        display_name="Game End",
        description="Executed when the game ends",
        category="Game",
        icon="🎮",
        parameters=[]
    ),
    "outside_room": EventType(
        name="outside_room",
        display_name="Outside Room",
        description="Executed when instance is completely outside the room",
        category="Other",
        icon="🚫",
        parameters=[]
    ),
    "intersect_boundary": EventType(
        name="intersect_boundary",
        display_name="Intersect Boundary",
        description="Executed when instance intersects the room boundary",
        category="Other",
        icon="⚠️",
        parameters=[]
    ),
    "no_more_lives": EventType(
        name="no_more_lives",
        display_name="No More Lives",
        description="Executed when lives become 0 or less",
        category="Other",
        icon="💀",
        parameters=[]
    ),
    "no_more_health": EventType(
        name="no_more_health",
        display_name="No More Health",
        description="Executed when health becomes 0 or less",
        category="Other",
        icon="💔",
        parameters=[]
    ),

    # ========================================================================
    # THYMIO ROBOT EVENTS
    # ========================================================================
    **THYMIO_EVENT_TYPES
}

def get_event_type(event_name: str) -> Optional[EventType]:
    """Get event type by name"""
    return EVENT_TYPES.get(event_name)


# ============================================================================
# EVENT TO BLOCKLY BLOCK TYPE MAPPING
# Maps event type names to their corresponding Blockly block types
# ============================================================================

EVENT_TO_BLOCKLY_MAP = {
    # Object events
    "create": "event_create",
    "step": "event_step",
    "destroy": "event_destroy",
    # Input events
    "keyboard": "event_keyboard_held",
    "keyboard_press": "event_keyboard_press",
    "keyboard_release": "event_keyboard_release",
    "keyboard_no_key": "event_keyboard_nokey",
    "mouse": "event_mouse",
    # Collision
    "collision": "event_collision",
    # Step events
    "begin_step": "event_step",
    "end_step": "event_step",
    # Drawing
    "draw": "event_draw",
    "draw_gui": "event_draw",
    # Timing
    "alarm": "event_alarm",
    # Other events
    "room_start": "event_other",
    "room_end": "event_other",
    "game_start": "event_other",
    "game_end": "event_other",
    "outside_room": "event_other",
    "intersect_boundary": "event_other",
    "no_more_lives": "event_other",
    "no_more_health": "event_other",
}
# Thymio events map directly (event name == blockly block type)
for _thymio_name in THYMIO_EVENT_TYPES:
    EVENT_TO_BLOCKLY_MAP[_thymio_name] = _thymio_name


def get_available_events(blockly_config=None) -> List[EventType]:
    """Get list of available events, optionally filtered by BlocklyConfig.

    Args:
        blockly_config: Optional BlocklyConfig to filter events.
                       If provided, only events enabled in the config are returned.
    """
    if blockly_config is None:
        return list(EVENT_TYPES.values())

    result = []
    for event in EVENT_TYPES.values():
        blockly_type = EVENT_TO_BLOCKLY_MAP.get(event.name)
        if blockly_type:
            if not blockly_config.is_block_enabled(blockly_type):
                continue
        # If no mapping exists, include the event (backward compatibility)
        result.append(event)
    return result

def get_keyboard_events_for_selector() -> List[Dict]:
    """
    Get all keyboard events for the event selector UI.
    Returns organized keyboard events (letters, numbers, special keys, etc.)
    """
    all_kb_events = get_all_keyboard_events()

    # Organize by category for better UI
    organized = {
        'Letters': [],
        'Numbers': [],
        'Arrow Keys': [],
        'Function Keys': [],
        'Special Keys': [],
        'Numpad': [],
    }

    for event in all_kb_events:
        category = event.get('category', 'Other')
        if category in organized:
            organized[category].append(event)

    return organized

def get_mouse_events_for_selector() -> List[Dict]:
    """
    Get all mouse events for the event selector UI.
    Returns organized mouse events (buttons, movement, wheel, etc.)
    """
    all_mouse_events = get_all_mouse_events()

    # Organize by category for better UI
    organized = {
        'Mouse Buttons': [],
        'Mouse Movement': [],
        'Mouse Wheel': [],
        'Global Mouse': [],
        'Mouse Drag': [],
    }

    for event in all_mouse_events:
        category = event.get('category', 'Other')
        if category in organized:
            organized[category].append(event)

    return organized

def get_keyboard_event_by_key_code(key_code: int) -> Optional[Dict]:
    """Get keyboard event info by key code"""
    for key, code in PYGAME_KEY_CODES.items():
        if code == key_code:
            return {
                'key': key,
                'key_code': code,
                'name': f'Key {key}',
                'display_name': f'Keyboard <{key}>',
            }
    return None

def get_mouse_event_by_button_code(button_code: int) -> Optional[Dict]:
    """Get mouse event info by button code"""
    for button, code in PYGAME_MOUSE_BUTTONS.items():
        if code == button_code:
            return {
                'button': button,
                'button_code': code,
                'name': f'Mouse {button}',
                'display_name': f'Mouse <{button}>',
            }
    return None

#!/usr/bin/env python3
"""
Thymio Robot Event Types
Events specific to the Thymio educational robot
"""

from typing import Dict
from dataclasses import dataclass, field


# Define EventType locally to avoid circular import
@dataclass
class EventType:
    """Defines an event type"""
    name: str
    display_name: str
    description: str
    category: str
    icon: str = None
    parameters: list = field(default_factory=list)


# ============================================================================
# THYMIO EVENT TYPES
# ============================================================================

THYMIO_EVENT_TYPES = {
    # ========================================================================
    # BUTTON EVENTS - Triggered by Thymio's 5 capacitive touch buttons
    # ========================================================================

    "thymio_button_forward": EventType(
        name="thymio_button_forward",
        display_name="Button Forward",
        description="Executed when the forward button is pressed",
        category="Thymio Buttons",
        icon="⬆️",
        parameters=[]
    ),

    "thymio_button_backward": EventType(
        name="thymio_button_backward",
        display_name="Button Backward",
        description="Executed when the backward button is pressed",
        category="Thymio Buttons",
        icon="⬇️",
        parameters=[]
    ),

    "thymio_button_left": EventType(
        name="thymio_button_left",
        display_name="Button Left",
        description="Executed when the left button is pressed",
        category="Thymio Buttons",
        icon="⬅️",
        parameters=[]
    ),

    "thymio_button_right": EventType(
        name="thymio_button_right",
        display_name="Button Right",
        description="Executed when the right button is pressed",
        category="Thymio Buttons",
        icon="➡️",
        parameters=[]
    ),

    "thymio_button_center": EventType(
        name="thymio_button_center",
        display_name="Button Center",
        description="Executed when the center button is pressed",
        category="Thymio Buttons",
        icon="⏺️",
        parameters=[]
    ),

    "thymio_any_button": EventType(
        name="thymio_any_button",
        display_name="Any Button",
        description="Executed when any button state changes (use button conditions to check which)",
        category="Thymio Buttons",
        icon="🔘",
        parameters=[]
    ),

    # ========================================================================
    # SENSOR EVENTS - Triggered by sensor updates
    # ========================================================================

    "thymio_proximity_update": EventType(
        name="thymio_proximity_update",
        display_name="Proximity Sensors Update",
        description="Executed when proximity sensors update (10 Hz / every 100ms)",
        category="Thymio Sensors",
        icon="📡",
        parameters=[]
    ),

    "thymio_ground_update": EventType(
        name="thymio_ground_update",
        display_name="Ground Sensors Update",
        description="Executed when ground sensors update (10 Hz / every 100ms)",
        category="Thymio Sensors",
        icon="⬛",
        parameters=[]
    ),

    # ========================================================================
    # TIMER EVENTS - Periodic events from configurable timers
    # ========================================================================

    "thymio_timer_0": EventType(
        name="thymio_timer_0",
        display_name="Timer 0",
        description="Executed when timer 0 period expires (configure with Set Timer Period action)",
        category="Thymio Timing",
        icon="⏱️",
        parameters=[]
    ),

    "thymio_timer_1": EventType(
        name="thymio_timer_1",
        display_name="Timer 1",
        description="Executed when timer 1 period expires (configure with Set Timer Period action)",
        category="Thymio Timing",
        icon="⏲️",
        parameters=[]
    ),

    # ========================================================================
    # ACCELEROMETER EVENTS
    # ========================================================================

    "thymio_tap": EventType(
        name="thymio_tap",
        display_name="Tap/Shock Detected",
        description="Executed when accelerometer detects a tap or shock",
        category="Thymio Sensors",
        icon="💥",
        parameters=[]
    ),

    # ========================================================================
    # SOUND EVENTS
    # ========================================================================

    "thymio_sound_detected": EventType(
        name="thymio_sound_detected",
        display_name="Sound Detected",
        description="Executed when microphone detects sound above threshold",
        category="Thymio Sensors",
        icon="🔊",
        parameters=[]
    ),

    "thymio_sound_finished": EventType(
        name="thymio_sound_finished",
        display_name="Sound Finished",
        description="Executed when sound playback completes",
        category="Thymio Sound",
        icon="🔇",
        parameters=[]
    ),

    # ========================================================================
    # COMMUNICATION EVENTS (for advanced multi-robot scenarios)
    # ========================================================================

    "thymio_message_received": EventType(
        name="thymio_message_received",
        display_name="Message Received",
        description="Executed when IR communication receives message from another Thymio",
        category="Thymio Communication",
        icon="📨",
        parameters=[]
    ),
}


# ============================================================================
# EVENT MAPPING FOR ASEBA EXPORT
# Maps PyGameMaker events to Aseba onevent handlers
# ============================================================================

THYMIO_EVENT_TO_ASEBA = {
    # Button events
    "thymio_button_forward": "onevent button.forward",
    "thymio_button_backward": "onevent button.backward",
    "thymio_button_left": "onevent button.left",
    "thymio_button_right": "onevent button.right",
    "thymio_button_center": "onevent button.center",
    "thymio_any_button": "onevent buttons",

    # Sensor events
    "thymio_proximity_update": "onevent prox",
    "thymio_ground_update": "onevent prox",  # Ground sensors update with proximity

    # Timer events
    "thymio_timer_0": "onevent timer0",
    "thymio_timer_1": "onevent timer1",

    # Accelerometer
    "thymio_tap": "onevent tap",

    # Sound
    "thymio_sound_detected": "onevent mic",
    "thymio_sound_finished": "onevent sound.finished",

    # Communication
    "thymio_message_received": "onevent prox.comm",
}


# ============================================================================
# EVENT KEYBOARD MAPPINGS FOR SIMULATION
# Maps Thymio button events to keyboard keys for testing
# ============================================================================

THYMIO_BUTTON_TO_KEYBOARD = {
    "thymio_button_forward": "up",      # Arrow Up or W
    "thymio_button_backward": "down",   # Arrow Down or S
    "thymio_button_left": "left",       # Arrow Left or A
    "thymio_button_right": "right",     # Arrow Right or D
    "thymio_button_center": "space",    # Space or Enter
}


# ============================================================================
# EVENT UPDATE RATES (for simulation timing)
# ============================================================================

THYMIO_EVENT_UPDATE_RATES = {
    # Sensor update rates (Hz)
    "thymio_proximity_update": 10,      # 10 Hz (every 100ms)
    "thymio_ground_update": 10,         # 10 Hz (every 100ms)
    "thymio_any_button": 20,            # 20 Hz (every 50ms)

    # Timer events are configurable via set_timer_period action
    "thymio_timer_0": None,  # User-configurable
    "thymio_timer_1": None,  # User-configurable
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_thymio_event(event_name: str) -> EventType:
    """Get a specific Thymio event type"""
    return THYMIO_EVENT_TYPES.get(event_name)


def get_thymio_events_by_category(category: str) -> Dict[str, EventType]:
    """Get all Thymio events in a specific category"""
    return {
        name: event
        for name, event in THYMIO_EVENT_TYPES.items()
        if event.category == category
    }


def get_all_thymio_categories() -> list:
    """Get list of all Thymio event categories"""
    categories = set()
    for event in THYMIO_EVENT_TYPES.values():
        categories.add(event.category)
    return sorted(list(categories))


def is_thymio_event(event_name: str) -> bool:
    """Check if an event name is a Thymio event"""
    return event_name in THYMIO_EVENT_TYPES


def get_aseba_event_name(pygm_event_name: str) -> str:
    """Get the corresponding Aseba event handler name for a PyGameMaker event"""
    return THYMIO_EVENT_TO_ASEBA.get(pygm_event_name, "")


def get_keyboard_mapping(thymio_button_event: str) -> str:
    """Get the keyboard key mapped to a Thymio button event (for simulation)"""
    return THYMIO_BUTTON_TO_KEYBOARD.get(thymio_button_event, "")


def get_event_update_rate(event_name: str) -> int:
    """Get the update rate (Hz) for a Thymio event, or None if not periodic"""
    return THYMIO_EVENT_UPDATE_RATES.get(event_name)


# ============================================================================
# EVENT CATEGORIES FOR UI ORGANIZATION
# ============================================================================

THYMIO_EVENT_CATEGORIES = {
    "Thymio Buttons": {
        "name": "Thymio Buttons",
        "icon": "🔘",
        "order": 200,
        "description": "Thymio capacitive button events"
    },
    "Thymio Sensors": {
        "name": "Thymio Sensors",
        "icon": "📡",
        "order": 201,
        "description": "Thymio sensor update events"
    },
    "Thymio Timing": {
        "name": "Thymio Timing",
        "icon": "⏱️",
        "order": 202,
        "description": "Thymio timer events"
    },
    "Thymio Sound": {
        "name": "Thymio Sound",
        "icon": "🔊",
        "order": 203,
        "description": "Thymio sound events"
    },
    "Thymio Communication": {
        "name": "Thymio Communication",
        "icon": "📡",
        "order": 204,
        "description": "Thymio inter-robot communication"
    },
}

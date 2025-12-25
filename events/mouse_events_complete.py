#!/usr/bin/env python3
"""
Complete Mouse Events for PyGameMaker IDE
Defines all mouse events for buttons, movement, and wheel
Compatible with both pygame and Kivy mouse events
"""

from typing import Dict, List


# Mouse button codes (pygame standard)
PYGAME_MOUSE_BUTTONS = {
    'LEFT': 1,
    'MIDDLE': 2,
    'RIGHT': 3,
    'WHEEL_UP': 4,
    'WHEEL_DOWN': 5,
    'WHEEL_LEFT': 6,   # Some mice support horizontal scroll
    'WHEEL_RIGHT': 7,
    'BUTTON_4': 8,     # Extra mouse buttons (gaming mice)
    'BUTTON_5': 9,
}


# Kivy mouse button codes (compatible with pygame)
KIVY_MOUSE_BUTTONS = {
    'LEFT': 'left',
    'MIDDLE': 'middle',
    'RIGHT': 'right',
    'SCROLLUP': 'scrollup',
    'SCROLLDOWN': 'scrolldown',
}


# Mouse event types
MOUSE_EVENT_TYPES = {
    # Button events
    'MOUSE_LEFT_PRESSED': 'mouse_left_pressed',
    'MOUSE_LEFT_RELEASE': 'mouse_left_released',
    'MOUSE_LEFT_DOWN': 'mouse_left_down',  # Held down

    'MOUSE_RIGHT_PRESSED': 'mouse_right_pressed',
    'MOUSE_RIGHT_RELEASE': 'mouse_right_released',
    'MOUSE_RIGHT_DOWN': 'mouse_right_down',

    'MOUSE_MIDDLE_PRESSED': 'mouse_middle_pressed',
    'MOUSE_MIDDLE_RELEASE': 'mouse_middle_released',
    'MOUSE_MIDDLE_DOWN': 'mouse_middle_down',

    # Movement events
    'MOUSE_ENTER': 'mouse_enter',          # Mouse enters object
    'MOUSE_LEAVE': 'mouse_leave',          # Mouse leaves object
    'MOUSE_HOVER': 'mouse_hover',          # Mouse over object
    'MOUSE_MOVE': 'mouse_move',            # Mouse moves anywhere

    # Global mouse events
    'GLOBAL_LEFT_PRESSED': 'global_left_pressed',
    'GLOBAL_LEFT_RELEASE': 'global_left_released',
    'GLOBAL_RIGHT_PRESSED': 'global_right_pressed',
    'GLOBAL_RIGHT_RELEASE': 'global_right_released',
    'GLOBAL_MIDDLE_PRESSED': 'global_middle_pressed',
    'GLOBAL_MIDDLE_RELEASE': 'global_middle_released',

    # Wheel events
    'MOUSE_WHEEL_UP': 'mouse_wheel_up',
    'MOUSE_WHEEL_DOWN': 'mouse_wheel_down',

    # Drag events
    'MOUSE_DRAG_START': 'mouse_drag_start',
    'MOUSE_DRAG': 'mouse_drag',
    'MOUSE_DRAG_END': 'mouse_drag_end',

    # Double click
    'MOUSE_LEFT_DOUBLE_CLICK': 'mouse_left_double_click',
    'MOUSE_RIGHT_DOUBLE_CLICK': 'mouse_right_double_click',
}


def get_all_mouse_events() -> List[Dict]:
    """
    Get all mouse events for buttons, movement, and wheel.
    Returns a list of event dictionaries suitable for the IDE event system.
    """
    events = []

    # Left button events
    events.extend([
        {
            'name': 'Mouse Left Button',
            'type': 'mouse',
            'button': 'LEFT',
            'button_code': PYGAME_MOUSE_BUTTONS['LEFT'],
            'event_type': 'press',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Left Button>',
            'description': 'Left mouse button pressed',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Left Released',
            'type': 'mouse',
            'button': 'LEFT',
            'button_code': PYGAME_MOUSE_BUTTONS['LEFT'],
            'event_type': 'release',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Left Released>',
            'description': 'Left mouse button released',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Left Down',
            'type': 'mouse',
            'button': 'LEFT',
            'button_code': PYGAME_MOUSE_BUTTONS['LEFT'],
            'event_type': 'down',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Left Down>',
            'description': 'Left mouse button held down',
            'icon': '🖱️',
        },
    ])

    # Right button events
    events.extend([
        {
            'name': 'Mouse Right Button',
            'type': 'mouse',
            'button': 'RIGHT',
            'button_code': PYGAME_MOUSE_BUTTONS['RIGHT'],
            'event_type': 'press',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Right Button>',
            'description': 'Right mouse button pressed',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Right Released',
            'type': 'mouse',
            'button': 'RIGHT',
            'button_code': PYGAME_MOUSE_BUTTONS['RIGHT'],
            'event_type': 'release',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Right Released>',
            'description': 'Right mouse button released',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Right Down',
            'type': 'mouse',
            'button': 'RIGHT',
            'button_code': PYGAME_MOUSE_BUTTONS['RIGHT'],
            'event_type': 'down',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Right Down>',
            'description': 'Right mouse button held down',
            'icon': '🖱️',
        },
    ])

    # Middle button events
    events.extend([
        {
            'name': 'Mouse Middle Button',
            'type': 'mouse',
            'button': 'MIDDLE',
            'button_code': PYGAME_MOUSE_BUTTONS['MIDDLE'],
            'event_type': 'press',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Middle Button>',
            'description': 'Middle mouse button pressed',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Middle Released',
            'type': 'mouse',
            'button': 'MIDDLE',
            'button_code': PYGAME_MOUSE_BUTTONS['MIDDLE'],
            'event_type': 'release',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Middle Released>',
            'description': 'Middle mouse button released',
            'icon': '🖱️',
        },
    ])

    # Mouse wheel events
    events.extend([
        {
            'name': 'Mouse Wheel Up',
            'type': 'mouse',
            'button': 'WHEEL_UP',
            'button_code': PYGAME_MOUSE_BUTTONS['WHEEL_UP'],
            'event_type': 'wheel',
            'category': 'Mouse Wheel',
            'display_name': 'Mouse <Wheel Up>',
            'description': 'Mouse wheel scrolled up',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Wheel Down',
            'type': 'mouse',
            'button': 'WHEEL_DOWN',
            'button_code': PYGAME_MOUSE_BUTTONS['WHEEL_DOWN'],
            'event_type': 'wheel',
            'category': 'Mouse Wheel',
            'display_name': 'Mouse <Wheel Down>',
            'description': 'Mouse wheel scrolled down',
            'icon': '🖱️',
        },
    ])

    # Mouse movement events
    events.extend([
        {
            'name': 'Mouse Enter',
            'type': 'mouse',
            'event_type': 'enter',
            'category': 'Mouse Movement',
            'display_name': 'Mouse <Enter>',
            'description': 'Mouse cursor enters the object',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Leave',
            'type': 'mouse',
            'event_type': 'leave',
            'category': 'Mouse Movement',
            'display_name': 'Mouse <Leave>',
            'description': 'Mouse cursor leaves the object',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Hover',
            'type': 'mouse',
            'event_type': 'hover',
            'category': 'Mouse Movement',
            'display_name': 'Mouse <Hover>',
            'description': 'Mouse cursor over the object',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Move',
            'type': 'mouse',
            'event_type': 'move',
            'category': 'Mouse Movement',
            'display_name': 'Mouse <Move>',
            'description': 'Mouse cursor moves',
            'icon': '🖱️',
        },
    ])

    # Global mouse events (anywhere on screen)
    events.extend([
        {
            'name': 'Global Left Button',
            'type': 'mouse',
            'button': 'LEFT',
            'button_code': PYGAME_MOUSE_BUTTONS['LEFT'],
            'event_type': 'global_press',
            'category': 'Global Mouse',
            'display_name': 'Global Mouse <Left Button>',
            'description': 'Left button pressed anywhere',
            'icon': '🌐',
        },
        {
            'name': 'Global Left Released',
            'type': 'mouse',
            'button': 'LEFT',
            'button_code': PYGAME_MOUSE_BUTTONS['LEFT'],
            'event_type': 'global_release',
            'category': 'Global Mouse',
            'display_name': 'Global Mouse <Left Released>',
            'description': 'Left button released anywhere',
            'icon': '🌐',
        },
        {
            'name': 'Global Right Button',
            'type': 'mouse',
            'button': 'RIGHT',
            'button_code': PYGAME_MOUSE_BUTTONS['RIGHT'],
            'event_type': 'global_press',
            'category': 'Global Mouse',
            'display_name': 'Global Mouse <Right Button>',
            'description': 'Right button pressed anywhere',
            'icon': '🌐',
        },
        {
            'name': 'Global Right Released',
            'type': 'mouse',
            'button': 'RIGHT',
            'button_code': PYGAME_MOUSE_BUTTONS['RIGHT'],
            'event_type': 'global_release',
            'category': 'Global Mouse',
            'display_name': 'Global Mouse <Right Released>',
            'description': 'Right button released anywhere',
            'icon': '🌐',
        },
    ])

    # Double click events
    events.extend([
        {
            'name': 'Mouse Left Double Click',
            'type': 'mouse',
            'button': 'LEFT',
            'button_code': PYGAME_MOUSE_BUTTONS['LEFT'],
            'event_type': 'double_click',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Left Double Click>',
            'description': 'Left button double clicked',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Right Double Click',
            'type': 'mouse',
            'button': 'RIGHT',
            'button_code': PYGAME_MOUSE_BUTTONS['RIGHT'],
            'event_type': 'double_click',
            'category': 'Mouse Buttons',
            'display_name': 'Mouse <Right Double Click>',
            'description': 'Right button double clicked',
            'icon': '🖱️',
        },
    ])

    # Drag events
    events.extend([
        {
            'name': 'Mouse Drag Start',
            'type': 'mouse',
            'event_type': 'drag_start',
            'category': 'Mouse Drag',
            'display_name': 'Mouse <Drag Start>',
            'description': 'Mouse drag started',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Drag',
            'type': 'mouse',
            'event_type': 'drag',
            'category': 'Mouse Drag',
            'display_name': 'Mouse <Drag>',
            'description': 'Mouse being dragged',
            'icon': '🖱️',
        },
        {
            'name': 'Mouse Drag End',
            'type': 'mouse',
            'event_type': 'drag_end',
            'category': 'Mouse Drag',
            'display_name': 'Mouse <Drag End>',
            'description': 'Mouse drag ended',
            'icon': '🖱️',
        },
    ])

    return events


def get_mouse_event_by_button(button: str, event_type: str = 'press') -> Dict:
    """Get mouse event info by button name and type"""
    button = button.upper()
    if button in PYGAME_MOUSE_BUTTONS:
        return {
            'name': f'Mouse {button} {event_type.title()}',
            'type': 'mouse',
            'button': button,
            'button_code': PYGAME_MOUSE_BUTTONS[button],
            'event_type': event_type,
            'kivy_button': KIVY_MOUSE_BUTTONS.get(button, button.lower()),
        }
    return None


def get_mouse_position_event() -> Dict:
    """Get mouse position tracking event"""
    return {
        'name': 'Mouse Position',
        'type': 'mouse',
        'event_type': 'position',
        'category': 'Mouse Position',
        'display_name': 'Mouse Position',
        'description': 'Get current mouse position (x, y)',
        'icon': '📍',
    }


# Export for easy importing
__all__ = [
    'PYGAME_MOUSE_BUTTONS',
    'KIVY_MOUSE_BUTTONS',
    'MOUSE_EVENT_TYPES',
    'get_all_mouse_events',
    'get_mouse_event_by_button',
    'get_mouse_position_event',
]


if __name__ == "__main__":
    # Test/demo
    print("=" * 60)
    print("Complete Mouse Events")
    print("=" * 60)

    all_events = get_all_mouse_events()

    # Group by category
    categories = {}
    for event in all_events:
        cat = event.get('category', 'Other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(event)

    for category, events in sorted(categories.items()):
        print(f"\n{category} ({len(events)} events):")
        for event in events:
            icon = event.get('icon', '•')
            print(f"  {icon} {event['display_name']}")
            print(f"     └─ {event['description']}")

    print(f"\nTotal mouse events: {len(all_events)}")

#!/usr/bin/env python3
"""
Complete Keyboard Events for PyGameMaker IDE
Defines all keyboard events for letters (A-Z), numbers (0-9), and special keys
Compatible with both pygame and Kivy key codes
"""

from typing import Dict, List


# Pygame key codes (used in runtime)
PYGAME_KEY_CODES = {
    # Letters A-Z
    'A': 97,   # ord('a')
    'B': 98,
    'C': 99,
    'D': 100,
    'E': 101,
    'F': 102,
    'G': 103,
    'H': 104,
    'I': 105,
    'J': 106,
    'K': 107,
    'L': 108,
    'M': 109,
    'N': 110,
    'O': 111,
    'P': 112,
    'Q': 113,
    'R': 114,
    'S': 115,
    'T': 116,
    'U': 117,
    'V': 118,
    'W': 119,
    'X': 120,
    'Y': 121,
    'Z': 122,

    # Numbers 0-9
    '0': 48,   # ord('0')
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,

    # Number pad (numpad)
    'NUMPAD_0': 256,
    'NUMPAD_1': 257,
    'NUMPAD_2': 258,
    'NUMPAD_3': 259,
    'NUMPAD_4': 260,
    'NUMPAD_5': 261,
    'NUMPAD_6': 262,
    'NUMPAD_7': 263,
    'NUMPAD_8': 264,
    'NUMPAD_9': 265,

    # Arrow keys
    'UP': 273,
    'DOWN': 274,
    'RIGHT': 275,
    'LEFT': 276,

    # Special keys
    'SPACE': 32,
    'RETURN': 13,
    'ENTER': 13,
    'BACKSPACE': 8,
    'TAB': 9,
    'ESCAPE': 27,
    'DELETE': 127,
    'INSERT': 277,
    'HOME': 278,
    'END': 279,
    'PAGEUP': 280,
    'PAGEDOWN': 281,

    # Function keys F1-F12
    'F1': 282,
    'F2': 283,
    'F3': 284,
    'F4': 285,
    'F5': 286,
    'F6': 287,
    'F7': 288,
    'F8': 289,
    'F9': 290,
    'F10': 291,
    'F11': 292,
    'F12': 293,

    # Modifier keys
    'LSHIFT': 304,
    'RSHIFT': 303,
    'LCTRL': 306,
    'RCTRL': 305,
    'LALT': 308,
    'RALT': 307,
    'LSUPER': 311,  # Windows/Command key
    'RSUPER': 312,

    # Punctuation and symbols
    'MINUS': 45,        # -
    'EQUALS': 61,       # =
    'LEFTBRACKET': 91,  # [
    'RIGHTBRACKET': 93, # ]
    'BACKSLASH': 92,    # \
    'SEMICOLON': 59,    # ;
    'QUOTE': 39,        # '
    'COMMA': 44,        # ,
    'PERIOD': 46,       # .
    'SLASH': 47,        # /
    'BACKQUOTE': 96,    # `

    # Numpad operators
    'NUMPAD_DIVIDE': 267,
    'NUMPAD_MULTIPLY': 268,
    'NUMPAD_MINUS': 269,
    'NUMPAD_PLUS': 270,
    'NUMPAD_ENTER': 271,
    'NUMPAD_PERIOD': 266,

    # Lock keys
    'CAPSLOCK': 301,
    'NUMLOCK': 300,
    'SCROLLLOCK': 302,

    # Other
    'PRINT': 316,
    'PAUSE': 19,
    'MENU': 319,
}


# Kivy key codes (used in Kivy exporter)
KIVY_KEY_CODES = {
    # Letters A-Z (same as pygame for letters)
    'A': 97,
    'B': 98,
    'C': 99,
    'D': 100,
    'E': 101,
    'F': 102,
    'G': 103,
    'H': 104,
    'I': 105,
    'J': 106,
    'K': 107,
    'L': 108,
    'M': 109,
    'N': 110,
    'O': 111,
    'P': 112,
    'Q': 113,
    'R': 114,
    'S': 115,
    'T': 116,
    'U': 117,
    'V': 118,
    'W': 119,
    'X': 120,
    'Y': 121,
    'Z': 122,

    # Numbers 0-9 (same as pygame)
    '0': 48,
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,

    # Arrow keys (same as pygame)
    'UP': 273,
    'DOWN': 274,
    'RIGHT': 275,
    'LEFT': 276,

    # Special keys
    'SPACE': 32,
    'ENTER': 13,
    'BACKSPACE': 8,
    'TAB': 9,
    'ESCAPE': 27,
    'DELETE': 127,
}


# Keyboard event types
KEYBOARD_EVENT_TYPES = {
    'KEY_PRESS': 'keyboard_press',
    'KEY_RELEASE': 'keyboard_release',
    'KEY_DOWN': 'keyboard_down',  # Held down
}


def get_all_keyboard_events() -> List[Dict]:
    """
    Get all keyboard events for letters, numbers, and special keys.
    Returns a list of event dictionaries suitable for the IDE event system.
    """
    events = []

    # Letters A-Z
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        events.append({
            'name': f'Key {letter}',
            'type': 'keyboard',
            'key': letter,
            'key_code': PYGAME_KEY_CODES[letter],
            'category': 'Letters',
            'display_name': f'Keyboard <{letter}>',
        })

    # Numbers 0-9
    for num in '0123456789':
        events.append({
            'name': f'Key {num}',
            'type': 'keyboard',
            'key': num,
            'key_code': PYGAME_KEY_CODES[num],
            'category': 'Numbers',
            'display_name': f'Keyboard <{num}>',
        })

    # Arrow keys
    for arrow in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        events.append({
            'name': f'Key {arrow}',
            'type': 'keyboard',
            'key': arrow,
            'key_code': PYGAME_KEY_CODES[arrow],
            'category': 'Arrow Keys',
            'display_name': f'Keyboard <{arrow}>',
        })

    # Common special keys
    special_keys = ['SPACE', 'ENTER', 'ESCAPE', 'BACKSPACE', 'TAB', 'DELETE']
    for key in special_keys:
        events.append({
            'name': f'Key {key}',
            'type': 'keyboard',
            'key': key,
            'key_code': PYGAME_KEY_CODES[key],
            'category': 'Special Keys',
            'display_name': f'Keyboard <{key}>',
        })

    # Function keys F1-F12
    for i in range(1, 13):
        key = f'F{i}'
        events.append({
            'name': f'Key {key}',
            'type': 'keyboard',
            'key': key,
            'key_code': PYGAME_KEY_CODES[key],
            'category': 'Function Keys',
            'display_name': f'Keyboard <{key}>',
        })

    # Numpad numbers
    for i in range(10):
        key = f'NUMPAD_{i}'
        events.append({
            'name': f'Key Numpad {i}',
            'type': 'keyboard',
            'key': key,
            'key_code': PYGAME_KEY_CODES[key],
            'category': 'Numpad',
            'display_name': f'Keyboard <Numpad {i}>',
        })

    return events


def get_keyboard_event_by_key(key: str) -> Dict:
    """Get keyboard event info by key name (e.g., 'A', 'SPACE', 'UP')"""
    key = key.upper()
    if key in PYGAME_KEY_CODES:
        return {
            'name': f'Key {key}',
            'type': 'keyboard',
            'key': key,
            'key_code': PYGAME_KEY_CODES[key],
            'kivy_code': KIVY_KEY_CODES.get(key, PYGAME_KEY_CODES[key]),
        }
    return None


def get_keyboard_event_by_code(key_code: int) -> Dict:
    """Get keyboard event info by key code"""
    for key, code in PYGAME_KEY_CODES.items():
        if code == key_code:
            return {
                'name': f'Key {key}',
                'type': 'keyboard',
                'key': key,
                'key_code': code,
                'kivy_code': KIVY_KEY_CODES.get(key, code),
            }
    return None


# Export for easy importing
__all__ = [
    'PYGAME_KEY_CODES',
    'KIVY_KEY_CODES',
    'KEYBOARD_EVENT_TYPES',
    'get_all_keyboard_events',
    'get_keyboard_event_by_key',
    'get_keyboard_event_by_code',
]


if __name__ == "__main__":
    # Test/demo
    print("=" * 60)
    print("Complete Keyboard Events")
    print("=" * 60)

    all_events = get_all_keyboard_events()

    # Group by category
    categories = {}
    for event in all_events:
        cat = event.get('category', 'Other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(event)

    for category, events in sorted(categories.items()):
        print(f"\n{category} ({len(events)} events):")
        for event in events[:5]:  # Show first 5
            print(f"  • {event['display_name']} (code: {event['key_code']})")
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more")

    print(f"\nTotal keyboard events: {len(all_events)}")

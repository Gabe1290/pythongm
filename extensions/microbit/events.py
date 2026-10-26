#!/usr/bin/env python3
"""micro:bit event types (Stage S4).

One flat event name per trigger -- ``microbit_gesture_shake``,
``microbit_pin_0`` -- the way ``collision_with_<object>`` is flat, so the
editor, Blockly and the runtime all need no sub-event selector. (The plan
sketched sub-events; flat names give the same vocabulary for no extra UI.)
``event_name_for`` maps what the simulator reports onto these names.
"""
from events.event_types import EventType

CATEGORY = "micro:bit"

# The simulator reports MicroPython's gesture names; students see MakeCode's.
GESTURE_NAMES = {
    "shake": ("shake", "Shake", "📳"),
    "up": ("logo_up", "Logo Up", "⬆️"),
    "down": ("logo_down", "Logo Down", "⬇️"),
    "left": ("tilt_left", "Tilt Left", "⬅️"),
    "right": ("tilt_right", "Tilt Right", "➡️"),
    "face up": ("screen_up", "Screen Up", "🔼"),
    "face down": ("screen_down", "Screen Down", "🔽"),
    "freefall": ("free_fall", "Free Fall", "🪂"),
    "2g": ("2g", "2g Impact", "💥"),
    "3g": ("3g", "3g Impact", "💥"),
    "6g": ("6g", "6g Impact", "💥"),
    "8g": ("8g", "8g Impact", "💥"),
}

# (simulator kind, detail) -> event name, for everything but gestures.
_FIXED = {
    ("button", "a"): "microbit_button_a",
    ("button", "b"): "microbit_button_b",
    ("button", "ab"): "microbit_button_ab",
    ("logo", "touched"): "microbit_logo_touched",
    ("pin", 0): "microbit_pin_0",
    ("pin", 1): "microbit_pin_1",
    ("pin", 2): "microbit_pin_2",
    ("sound", "loud"): "microbit_loud_sound",
    ("sound", "quiet"): "microbit_quiet_sound",
    ("display_done", None): "microbit_display_done",
    ("sound_done", None): "microbit_sound_done",
}


def event_name_for(kind, detail):
    """The event a simulator report fires, or ``None`` if it has none."""
    if kind == "radio":
        return "microbit_radio_received"
    if kind == "gesture":
        entry = GESTURE_NAMES.get(detail)
        return f"microbit_gesture_{entry[0]}" if entry else None
    return _FIXED.get((kind, detail))


def _event(name, display, description, icon):
    return EventType(name=name, display_name=display, description=description,
                     category=CATEGORY, icon=icon, parameters=[])


MICROBIT_EVENT_TYPES = {
    e.name: e for e in [
        _event("microbit_button_a", "Button A Pressed",
               "Executed when button A goes down", "🅰️"),
        _event("microbit_button_b", "Button B Pressed",
               "Executed when button B goes down", "🅱️"),
        _event("microbit_button_ab", "Buttons A+B Pressed",
               "Executed when both buttons are down together", "🔘"),
        _event("microbit_logo_touched", "Logo Touched",
               "Executed when the touch logo is touched", "👆"),
        _event("microbit_pin_0", "Pin 0 Touched",
               "Executed when pin 0 is touched", "0️⃣"),
        _event("microbit_pin_1", "Pin 1 Touched",
               "Executed when pin 1 is touched", "1️⃣"),
        _event("microbit_pin_2", "Pin 2 Touched",
               "Executed when pin 2 is touched", "2️⃣"),
        *[
            _event(f"microbit_gesture_{key}", label,
                   f"Executed when the board detects: {label.lower()}", icon)
            for key, label, icon in GESTURE_NAMES.values()
        ],
        _event("microbit_loud_sound", "Loud Sound",
               "Executed when the microphone hears a loud sound", "🔊"),
        _event("microbit_quiet_sound", "Quiet Sound",
               "Executed when the sound drops back to quiet", "🔈"),
        _event("microbit_display_done", "Display Finished",
               "Executed when the display queue has played everything", "✅"),
        _event("microbit_radio_received", "Radio Message Received",
               "Executed when another micro:bit in the same radio group sends "
               "a message. The value is in the variables radio_number and "
               "radio_string", "📻"),
        _event("microbit_sound_done", "Sound Finished",
               "Executed when every queued tone and melody has played", "🎵"),
    ]
}

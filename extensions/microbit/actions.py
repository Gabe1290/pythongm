#!/usr/bin/env python3
"""Action SCHEMAS the micro:bit extension contributes (Stage S3).

English-first (docs/MICROBIT_EXTENSION_PLAN.md "Ground rules"): French comes
through the Blockly translation tables in S10, not from these strings. The
loader merges ``PLUGIN_ACTIONS`` into ``ACTION_TYPES`` at startup, so the
action picker and Blockly see them; handlers are in ``handlers.py``.

Every action works on the micro:bit that runs it -- put the events on the
``microbit*`` object itself. Radio sends reach the other micro:bits in the same group.
"""
from events.action_types import ActionType, ActionParameter

CATEGORY = "micro:bit"

# Picker tab, registered by __init__ (same seam Thymio uses).
MICROBIT_TAB = {
    "microbit": {
        "name": "micro:bit",
        "icon": "🔲",
        "order": 90,
        "description": "BBC micro:bit simulator actions",
    }
}

# MicroPython's gesture names, so Stage X can emit them verbatim.
GESTURES = ["shake", "up", "down", "left", "right", "face up", "face down",
            "freefall", "2g", "3g", "6g", "8g"]

# What microbit_read_sensor can read, in the order the picker lists them.
SENSORS = ["accelerometer x", "accelerometer y", "accelerometer z",
           "acceleration strength", "compass heading", "light level",
           "temperature", "sound level", "pin 0 analog", "pin 1 analog",
           "pin 2 analog"]

COMPARISONS = ["<", "<=", "==", ">=", ">", "!="]

PLUGIN_ACTIONS = {
    # -- Display -----------------------------------------------------------
    "microbit_show_image": ActionType(
        name="microbit_show_image",
        display_name="Show Image",
        description="Show an image on the LED display: a built-in name "
                    "(HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL...) or "
                    "five rows of brightness digits such as "
                    "\"09090:99999:99999:09990:00900\". Display actions "
                    "queue and play one after another.",
        category=CATEGORY, icon="❤️",
        parameters=[
            ActionParameter(name="image", display_name="Image",
                param_type="string", default_value="HEART",
                description="Built-in image name, or 5 rows of 5 digits "
                            "(0-9) separated by colons"),
            ActionParameter(name="hold", display_name="Hold (ms)",
                param_type="number", default_value=0, required=False,
                description="How long it stays before the next queued "
                            "item (0 = until something else is shown)"),
        ],
    ),
    "microbit_scroll_text": ActionType(
        name="microbit_scroll_text",
        display_name="Scroll Text",
        description="Scroll text across the LED display. Put literal text "
                    "in double quotes (\"Hello\"); otherwise a dash or "
                    "plus is read as arithmetic. Accented letters show as "
                    "? as on the real board.",
        category=CATEGORY, icon="🔤",
        parameters=[
            ActionParameter(name="text", display_name="Text",
                param_type="string", default_value="\"Hello\"",
                description="Text or expression to scroll"),
            ActionParameter(name="delay", display_name="Delay per column (ms)",
                param_type="number", default_value=150, required=False,
                description="Scroll speed (MicroPython default 150)"),
        ],
    ),
    "microbit_show_number": ActionType(
        name="microbit_show_number",
        display_name="Show Number",
        description="Show a number: one digit stays still, longer numbers "
                    "scroll",
        category=CATEGORY, icon="🔢",
        parameters=[
            ActionParameter(name="value", display_name="Number",
                param_type="string", default_value="0",
                description="Number or expression"),
        ],
    ),
    "microbit_set_pixel": ActionType(
        name="microbit_set_pixel",
        display_name="Set LED",
        description="Light one LED now (x and y are 0-4, brightness 0-9)",
        category=CATEGORY, icon="💡",
        parameters=[
            ActionParameter(name="x", display_name="X (0-4)",
                param_type="string", default_value="0"),
            ActionParameter(name="y", display_name="Y (0-4)",
                param_type="string", default_value="0"),
            ActionParameter(name="brightness", display_name="Brightness (0-9)",
                param_type="string", default_value="9", required=False),
        ],
    ),
    "microbit_clear_display": ActionType(
        name="microbit_clear_display",
        display_name="Clear Display",
        description="Turn every LED off and drop anything still queued",
        category=CATEGORY, icon="⬛",
        parameters=[],
    ),
    "microbit_set_brightness": ActionType(
        name="microbit_set_brightness",
        display_name="Set Display Brightness",
        description="Overall LED brightness, 0 (dark) to 255 (full)",
        category=CATEGORY, icon="🔆",
        parameters=[
            ActionParameter(name="brightness", display_name="Brightness (0-255)",
                param_type="string", default_value="255"),
        ],
    ),

    # -- Sound -------------------------------------------------------------
    "microbit_play_tone": ActionType(
        name="microbit_play_tone",
        display_name="Play Tone",
        description="Beep at a frequency for a number of milliseconds. "
                    "Sounds queue and play one after another.",
        category=CATEGORY, icon="🔔",
        parameters=[
            ActionParameter(name="frequency", display_name="Frequency (Hz)",
                param_type="string", default_value="440",
                description="Pitch in hertz (440 = the note A)"),
            ActionParameter(name="duration", display_name="Duration (ms)",
                param_type="string", default_value="500", required=False),
        ],
    ),
    "microbit_play_melody": ActionType(
        name="microbit_play_melody",
        display_name="Play Melody",
        description="Play a built-in melody (DADADADUM, ENTERTAINER, PRELUDE, "
                    "ODE, NYAN, RINGTONE, FUNK, BLUES, BIRTHDAY, WEDDING, "
                    "FUNERAL, PUNCHLINE, PYTHON, BADDY, CHASE, BA_DING, "
                    "WAWAWAWAA, JUMP_UP, JUMP_DOWN, POWER_UP, POWER_DOWN) or "
                    "your own notes such as \"C4:4 E G C5:8 R:4\" "
                    "(note, octave, :length; R is a rest).",
        category=CATEGORY, icon="🎵",
        parameters=[
            ActionParameter(name="melody", display_name="Melody",
                param_type="string", default_value="DADADADUM",
                description="Built-in name, or notes separated by spaces"),
            ActionParameter(name="tempo", display_name="Tempo (bpm)",
                param_type="string", default_value="120", required=False),
        ],
    ),
    "microbit_stop_sound": ActionType(
        name="microbit_stop_sound",
        display_name="Stop Sound",
        description="Silence the speaker and drop any queued sounds",
        category=CATEGORY, icon="🔇",
        parameters=[],
    ),

    # -- Radio ---------------------------------------------------------------
    "microbit_radio_set_group": ActionType(
        name="microbit_radio_set_group",
        display_name="Set Radio Group",
        description="Choose the radio group (0-255). Only micro:bits in the "
                    "same group hear each other; every board starts in "
                    "group 0.",
        category=CATEGORY, icon="📡",
        parameters=[
            ActionParameter(name="group", display_name="Group (0-255)",
                param_type="string", default_value="0"),
        ],
    ),
    "microbit_radio_send": ActionType(
        name="microbit_radio_send",
        display_name="Send Radio Message",
        description="Send a number or text to the other micro:bits in the "
                    "same group (not to this one). They get the Radio "
                    "Message Received event, with the value in radio_number "
                    "and radio_string. Put literal text in double quotes; "
                    "text is cut to 32 characters.",
        category=CATEGORY, icon="📻",
        parameters=[
            ActionParameter(name="value", display_name="Message",
                param_type="string", default_value="1",
                description="A number, an expression or quoted text"),
        ],
    ),

    # -- Sensors -----------------------------------------------------------
    "microbit_read_sensor": ActionType(
        name="microbit_read_sensor",
        display_name="Read Sensor",
        description="Read a micro:bit sensor into a variable of this "
                    "object (or a global variable if the name starts with "
                    "\"global.\")",
        category=CATEGORY, icon="📡",
        parameters=[
            ActionParameter(name="sensor", display_name="Sensor",
                param_type="choice", default_value="accelerometer x",
                choices=SENSORS),
            ActionParameter(name="variable", display_name="Variable",
                param_type="string", default_value="sensor_value",
                description="Variable that receives the reading"),
        ],
    ),

    # -- Conditions (true/false; the then/else blocks follow) ----------------
    "microbit_if_button": ActionType(
        name="microbit_if_button",
        display_name="If Button Pressed",
        description="True while the button is held down (A+B = both)",
        category=CATEGORY, icon="🔘",
        parameters=[
            ActionParameter(name="button", display_name="Button",
                param_type="choice", default_value="a",
                choices=["a", "b", "ab", "logo"]),
        ],
    ),
    "microbit_if_gesture": ActionType(
        name="microbit_if_gesture",
        display_name="If Gesture",
        description="True while the board is in this gesture or posture",
        category=CATEGORY, icon="🤝",
        parameters=[
            ActionParameter(name="gesture", display_name="Gesture",
                param_type="choice", default_value="shake", choices=GESTURES),
        ],
    ),
    "microbit_if_tilt": ActionType(
        name="microbit_if_tilt",
        display_name="If Tilt",
        description="Compare an accelerometer axis (milli-g, -2048..2048) "
                    "with a value",
        category=CATEGORY, icon="📐",
        parameters=[
            ActionParameter(name="axis", display_name="Axis",
                param_type="choice", default_value="x", choices=["x", "y", "z"]),
            ActionParameter(name="comparison", display_name="Comparison",
                param_type="choice", default_value=">", choices=COMPARISONS),
            ActionParameter(name="value", display_name="Value",
                param_type="string", default_value="300"),
        ],
    ),
    "microbit_if_pixel": ActionType(
        name="microbit_if_pixel",
        display_name="If LED Brightness",
        description="Compare one LED's brightness (0-9) with a value; the "
                    "default asks \"is it lit?\"",
        category=CATEGORY, icon="🔍",
        parameters=[
            ActionParameter(name="x", display_name="X (0-4)",
                param_type="string", default_value="0"),
            ActionParameter(name="y", display_name="Y (0-4)",
                param_type="string", default_value="0"),
            ActionParameter(name="comparison", display_name="Comparison",
                param_type="choice", default_value=">", choices=COMPARISONS,
                required=False),
            ActionParameter(name="value", display_name="Value",
                param_type="string", default_value="0", required=False),
        ],
    ),
}

#!/usr/bin/env python3
"""
Thymio Robot Actions
Actions specific to the Thymio educational robot for simulation and Aseba code export
"""

from actions.core import ActionDefinition, ActionParameter


THYMIO_ACTIONS = {
    # ========================================================================
    # MOTOR CONTROL ACTIONS
    # ========================================================================

    "thymio_set_motor_speed": ActionDefinition(
        name="thymio_set_motor_speed",
        display_name="Set Motor Speeds",
        category="thymio_motors",
        tab="thymio",
        description="Set left and right motor speeds independently (-500 to 500)",
        icon="🤖",
        parameters=[
            ActionParameter(
                name="left_speed",
                type="string",
                display_name="Left Motor Speed",
                description="Left motor speed (-500 to 500, or variable)",
                default="0"
            ),
            ActionParameter(
                name="right_speed",
                type="string",
                display_name="Right Motor Speed",
                description="Right motor speed (-500 to 500, or variable)",
                default="0"
            )
        ]
    ),

    "thymio_move_forward": ActionDefinition(
        name="thymio_move_forward",
        display_name="Move Forward",
        category="thymio_motors",
        tab="thymio",
        description="Move forward at specified speed (both motors same speed)",
        icon="⬆️",
        parameters=[
            ActionParameter(
                name="speed",
                type="string",
                display_name="Speed",
                description="Forward speed (0 to 500, or variable)",
                default="200"
            )
        ]
    ),

    "thymio_move_backward": ActionDefinition(
        name="thymio_move_backward",
        display_name="Move Backward",
        category="thymio_motors",
        tab="thymio",
        description="Move backward at specified speed",
        icon="⬇️",
        parameters=[
            ActionParameter(
                name="speed",
                type="string",
                display_name="Speed",
                description="Backward speed (0 to 500, or variable)",
                default="200"
            )
        ]
    ),

    "thymio_turn_left": ActionDefinition(
        name="thymio_turn_left",
        display_name="Turn Left",
        category="thymio_motors",
        tab="thymio",
        description="Turn left in place (left motor stops, right motor moves)",
        icon="↶",
        parameters=[
            ActionParameter(
                name="speed",
                type="string",
                display_name="Turn Speed",
                description="Rotation speed (0 to 500, or variable)",
                default="300"
            )
        ]
    ),

    "thymio_turn_right": ActionDefinition(
        name="thymio_turn_right",
        display_name="Turn Right",
        category="thymio_motors",
        tab="thymio",
        description="Turn right in place (right motor stops, left motor moves)",
        icon="↷",
        parameters=[
            ActionParameter(
                name="speed",
                type="string",
                display_name="Turn Speed",
                description="Rotation speed (0 to 500, or variable)",
                default="300"
            )
        ]
    ),

    "thymio_stop_motors": ActionDefinition(
        name="thymio_stop_motors",
        display_name="Stop Motors",
        category="thymio_motors",
        tab="thymio",
        description="Stop both motors (set speeds to 0)",
        icon="🛑"
    ),

    # ========================================================================
    # LED CONTROL ACTIONS
    # ========================================================================

    "thymio_set_led_top": ActionDefinition(
        name="thymio_set_led_top",
        display_name="Set Top LED Color",
        category="thymio_leds",
        tab="thymio",
        description="Set the top RGB LED color (0-32 for each channel)",
        icon="💡",
        parameters=[
            ActionParameter(
                name="red",
                type="string",
                display_name="Red",
                description="Red intensity (0-32, or variable)",
                default="0"
            ),
            ActionParameter(
                name="green",
                type="string",
                display_name="Green",
                description="Green intensity (0-32, or variable)",
                default="0"
            ),
            ActionParameter(
                name="blue",
                type="string",
                display_name="Blue",
                description="Blue intensity (0-32, or variable)",
                default="0"
            )
        ]
    ),

    "thymio_set_led_bottom_left": ActionDefinition(
        name="thymio_set_led_bottom_left",
        display_name="Set Bottom Left LED",
        category="thymio_leds",
        tab="thymio",
        description="Set the bottom left RGB LED color",
        icon="💡",
        parameters=[
            ActionParameter(
                name="red",
                type="string",
                display_name="Red",
                description="Red intensity (0-32, or variable)",
                default="0"
            ),
            ActionParameter(
                name="green",
                type="string",
                display_name="Green",
                description="Green intensity (0-32, or variable)",
                default="0"
            ),
            ActionParameter(
                name="blue",
                type="string",
                display_name="Blue",
                description="Blue intensity (0-32, or variable)",
                default="0"
            )
        ]
    ),

    "thymio_set_led_bottom_right": ActionDefinition(
        name="thymio_set_led_bottom_right",
        display_name="Set Bottom Right LED",
        category="thymio_leds",
        tab="thymio",
        description="Set the bottom right RGB LED color",
        icon="💡",
        parameters=[
            ActionParameter(
                name="red",
                type="string",
                display_name="Red",
                description="Red intensity (0-32, or variable)",
                default="0"
            ),
            ActionParameter(
                name="green",
                type="string",
                display_name="Green",
                description="Green intensity (0-32, or variable)",
                default="0"
            ),
            ActionParameter(
                name="blue",
                type="string",
                display_name="Blue",
                description="Blue intensity (0-32, or variable)",
                default="0"
            )
        ]
    ),

    "thymio_set_led_circle": ActionDefinition(
        name="thymio_set_led_circle",
        display_name="Set Circle LED",
        category="thymio_leds",
        tab="thymio",
        description="Set one of the 8 circle LEDs (yellow/orange)",
        icon="🔆",
        parameters=[
            ActionParameter(
                name="led_index",
                type="choice",
                display_name="LED Position",
                description="Which circle LED to control (0-7, clockwise from front)",
                default="0",
                options=["0", "1", "2", "3", "4", "5", "6", "7"]
            ),
            ActionParameter(
                name="intensity",
                type="string",
                display_name="Intensity",
                description="LED intensity (0-32, or variable)",
                default="32"
            )
        ]
    ),

    "thymio_set_led_circle_all": ActionDefinition(
        name="thymio_set_led_circle_all",
        display_name="Set All Circle LEDs",
        category="thymio_leds",
        tab="thymio",
        description="Set all 8 circle LEDs at once (comma-separated values)",
        icon="⭕",
        parameters=[
            ActionParameter(
                name="led0",
                type="string",
                display_name="LED 0 (Front)",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led1",
                type="string",
                display_name="LED 1",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led2",
                type="string",
                display_name="LED 2",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led3",
                type="string",
                display_name="LED 3 (Right)",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led4",
                type="string",
                display_name="LED 4 (Back)",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led5",
                type="string",
                display_name="LED 5",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led6",
                type="string",
                display_name="LED 6",
                description="Intensity 0-32",
                default="0"
            ),
            ActionParameter(
                name="led7",
                type="string",
                display_name="LED 7 (Left)",
                description="Intensity 0-32",
                default="0"
            )
        ]
    ),

    "thymio_leds_off": ActionDefinition(
        name="thymio_leds_off",
        display_name="Turn Off All LEDs",
        category="thymio_leds",
        tab="thymio",
        description="Turn off all LEDs (top, bottom, and circle)",
        icon="⚫"
    ),

    # ========================================================================
    # SOUND ACTIONS
    # ========================================================================

    "thymio_play_tone": ActionDefinition(
        name="thymio_play_tone",
        display_name="Play Tone",
        category="thymio_sound",
        tab="thymio",
        description="Play a tone at specified frequency and duration",
        icon="🔊",
        parameters=[
            ActionParameter(
                name="frequency",
                type="string",
                display_name="Frequency (Hz)",
                description="Tone frequency in Hertz (e.g., 440 for A4, or variable)",
                default="440"
            ),
            ActionParameter(
                name="duration",
                type="string",
                display_name="Duration",
                description="Duration in 1/60 second units (e.g., 60 = 1 second, -1 = continuous, or variable)",
                default="60"
            )
        ]
    ),

    "thymio_play_system_sound": ActionDefinition(
        name="thymio_play_system_sound",
        display_name="Play System Sound",
        category="thymio_sound",
        tab="thymio",
        description="Play a built-in system sound",
        icon="🔔",
        parameters=[
            ActionParameter(
                name="sound_id",
                type="choice",
                display_name="System Sound",
                description="Which system sound to play",
                default="0",
                options=[
                    "0 - Startup",
                    "1 - Shutdown",
                    "2 - Arrow",
                    "3 - Central",
                    "4 - Free Fall",
                    "5 - Collision",
                    "6 - Target Friendly",
                    "7 - Target Detected"
                ]
            )
        ]
    ),

    "thymio_stop_sound": ActionDefinition(
        name="thymio_stop_sound",
        display_name="Stop Sound",
        category="thymio_sound",
        tab="thymio",
        description="Stop currently playing sound",
        icon="🔇"
    ),

    # ========================================================================
    # SENSOR READING ACTIONS (Get Values)
    # ========================================================================

    "thymio_read_proximity": ActionDefinition(
        name="thymio_read_proximity",
        display_name="Read Proximity Sensor",
        category="thymio_sensors",
        tab="thymio",
        description="Read a proximity sensor value and store in variable",
        icon="📡",
        parameters=[
            ActionParameter(
                name="sensor_index",
                type="choice",
                display_name="Sensor",
                description="Which proximity sensor to read",
                default="2",
                options=[
                    "0 - Front Left Far",
                    "1 - Front Left",
                    "2 - Front Center",
                    "3 - Front Right",
                    "4 - Front Right Far",
                    "5 - Back Left",
                    "6 - Back Right"
                ]
            ),
            ActionParameter(
                name="variable",
                type="string",
                display_name="Store in Variable",
                description="Variable name to store the sensor value (0-4000)",
                default="prox_value"
            )
        ]
    ),

    "thymio_read_ground": ActionDefinition(
        name="thymio_read_ground",
        display_name="Read Ground Sensor",
        category="thymio_sensors",
        tab="thymio",
        description="Read a ground sensor value and store in variable",
        icon="⬛",
        parameters=[
            ActionParameter(
                name="sensor_index",
                type="choice",
                display_name="Sensor",
                description="Which ground sensor to read",
                default="0",
                options=[
                    "0 - Left",
                    "1 - Right"
                ]
            ),
            ActionParameter(
                name="variable",
                type="string",
                display_name="Store in Variable",
                description="Variable name to store the sensor value",
                default="ground_value"
            )
        ]
    ),

    "thymio_read_button": ActionDefinition(
        name="thymio_read_button",
        display_name="Read Button State",
        category="thymio_sensors",
        tab="thymio",
        description="Read button state and store in variable (0=released, 1=pressed)",
        icon="🔘",
        parameters=[
            ActionParameter(
                name="button",
                type="choice",
                display_name="Button",
                description="Which button to read",
                default="center",
                options=[
                    "forward",
                    "backward",
                    "left",
                    "right",
                    "center"
                ]
            ),
            ActionParameter(
                name="variable",
                type="string",
                display_name="Store in Variable",
                description="Variable name to store button state (0 or 1)",
                default="button_state"
            )
        ]
    ),

    # ========================================================================
    # SENSOR CONDITIONAL ACTIONS (If/Test)
    # ========================================================================

    "thymio_if_proximity": ActionDefinition(
        name="thymio_if_proximity",
        display_name="If Proximity Detected",
        category="thymio_conditions",
        tab="thymio",
        description="Check if proximity sensor detects obstacle above threshold",
        icon="🎯",
        parameters=[
            ActionParameter(
                name="sensor_index",
                type="choice",
                display_name="Sensor",
                description="Which proximity sensor to check",
                default="2",
                options=[
                    "0 - Front Left Far",
                    "1 - Front Left",
                    "2 - Front Center",
                    "3 - Front Right",
                    "4 - Front Right Far",
                    "5 - Back Left",
                    "6 - Back Right"
                ]
            ),
            ActionParameter(
                name="threshold",
                type="string",
                display_name="Threshold",
                description="Detection threshold (0-4000, typically 2000 for ~5cm, or variable)",
                default="2000"
            ),
            ActionParameter(
                name="comparison",
                type="choice",
                display_name="Comparison",
                description="How to compare sensor value to threshold",
                default=">",
                options=[">", ">=", "<", "<=", "==", "!="]
            )
        ]
    ),

    "thymio_if_ground_dark": ActionDefinition(
        name="thymio_if_ground_dark",
        display_name="If Ground is Dark",
        category="thymio_conditions",
        tab="thymio",
        description="Check if ground sensor detects dark surface (line following)",
        icon="⬛",
        parameters=[
            ActionParameter(
                name="sensor_index",
                type="choice",
                display_name="Sensor",
                description="Which ground sensor to check",
                default="0",
                options=[
                    "0 - Left",
                    "1 - Right"
                ]
            ),
            ActionParameter(
                name="threshold",
                type="string",
                display_name="Threshold",
                description="Dark detection threshold (typically 300, or variable)",
                default="300"
            )
        ]
    ),

    "thymio_if_ground_light": ActionDefinition(
        name="thymio_if_ground_light",
        display_name="If Ground is Light",
        category="thymio_conditions",
        tab="thymio",
        description="Check if ground sensor detects light surface",
        icon="⬜",
        parameters=[
            ActionParameter(
                name="sensor_index",
                type="choice",
                display_name="Sensor",
                description="Which ground sensor to check",
                default="0",
                options=[
                    "0 - Left",
                    "1 - Right"
                ]
            ),
            ActionParameter(
                name="threshold",
                type="string",
                display_name="Threshold",
                description="Light detection threshold (typically 300, or variable)",
                default="300"
            )
        ]
    ),

    "thymio_if_button_pressed": ActionDefinition(
        name="thymio_if_button_pressed",
        display_name="If Button Pressed",
        category="thymio_conditions",
        tab="thymio",
        description="Check if a button is currently pressed",
        icon="🔘",
        parameters=[
            ActionParameter(
                name="button",
                type="choice",
                display_name="Button",
                description="Which button to check",
                default="center",
                options=[
                    "forward",
                    "backward",
                    "left",
                    "right",
                    "center"
                ]
            )
        ]
    ),

    "thymio_if_button_released": ActionDefinition(
        name="thymio_if_button_released",
        display_name="If Button Released",
        category="thymio_conditions",
        tab="thymio",
        description="Check if a button is currently released",
        icon="⚪",
        parameters=[
            ActionParameter(
                name="button",
                type="choice",
                display_name="Button",
                description="Which button to check",
                default="center",
                options=[
                    "forward",
                    "backward",
                    "left",
                    "right",
                    "center"
                ]
            )
        ]
    ),

    # ========================================================================
    # TIMER ACTIONS
    # ========================================================================

    "thymio_set_timer_period": ActionDefinition(
        name="thymio_set_timer_period",
        display_name="Set Timer Period",
        category="thymio_timing",
        tab="thymio",
        description="Set timer period in milliseconds (triggers on_timer event)",
        icon="⏱️",
        parameters=[
            ActionParameter(
                name="timer_id",
                type="choice",
                display_name="Timer",
                description="Which timer to configure (0 or 1)",
                default="0",
                options=["0", "1"]
            ),
            ActionParameter(
                name="period",
                type="string",
                display_name="Period (ms)",
                description="Timer period in milliseconds (e.g., 1000 = 1 second, or variable)",
                default="1000"
            )
        ]
    ),

    # ========================================================================
    # VARIABLE ACTIONS (Thymio uses 16-bit integers only)
    # ========================================================================

    "thymio_set_variable": ActionDefinition(
        name="thymio_set_variable",
        display_name="Set Variable",
        category="thymio_variables",
        tab="thymio",
        description="Set a variable to a value (16-bit integer: -32768 to 32767)",
        icon="📝",
        parameters=[
            ActionParameter(
                name="variable",
                type="string",
                display_name="Variable Name",
                description="Variable name (will be declared in Aseba)",
                default="state"
            ),
            ActionParameter(
                name="value",
                type="string",
                display_name="Value",
                description="Value to assign (integer, or expression)",
                default="0"
            )
        ]
    ),

    "thymio_increase_variable": ActionDefinition(
        name="thymio_increase_variable",
        display_name="Increase Variable",
        category="thymio_variables",
        tab="thymio",
        description="Increase variable by specified amount",
        icon="➕",
        parameters=[
            ActionParameter(
                name="variable",
                type="string",
                display_name="Variable Name",
                description="Variable name to increase",
                default="counter"
            ),
            ActionParameter(
                name="amount",
                type="string",
                display_name="Amount",
                description="Amount to add (default 1)",
                default="1"
            )
        ]
    ),

    "thymio_decrease_variable": ActionDefinition(
        name="thymio_decrease_variable",
        display_name="Decrease Variable",
        category="thymio_variables",
        tab="thymio",
        description="Decrease variable by specified amount",
        icon="➖",
        parameters=[
            ActionParameter(
                name="variable",
                type="string",
                display_name="Variable Name",
                description="Variable name to decrease",
                default="counter"
            ),
            ActionParameter(
                name="amount",
                type="string",
                display_name="Amount",
                description="Amount to subtract (default 1)",
                default="1"
            )
        ]
    ),

    "thymio_if_variable": ActionDefinition(
        name="thymio_if_variable",
        display_name="If Variable",
        category="thymio_conditions",
        tab="thymio",
        description="Check variable value against a condition",
        icon="❓",
        parameters=[
            ActionParameter(
                name="variable",
                type="string",
                display_name="Variable Name",
                description="Variable to check",
                default="state"
            ),
            ActionParameter(
                name="comparison",
                type="choice",
                display_name="Comparison",
                description="Comparison operator",
                default="==",
                options=["==", "!=", "<", "<=", ">", ">="]
            ),
            ActionParameter(
                name="value",
                type="string",
                display_name="Value",
                description="Value to compare against",
                default="0"
            )
        ]
    ),
}


# ============================================================================
# Register Thymio tab in GM80 action tabs
# ============================================================================

THYMIO_TAB = {
    "thymio": {
        "name": "Thymio",
        "icon": "🤖",
        "order": 100,  # Put after standard tabs
        "description": "Thymio robot control actions"
    }
}

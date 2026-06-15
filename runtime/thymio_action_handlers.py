#!/usr/bin/env python3
"""
Thymio Action Handlers

Implements all 28 Thymio robot actions for the ActionExecutor.
These handlers control the Thymio robot simulator including motors,
LEDs, sounds, and sensor readings.
"""

import re
from typing import Any, Dict, Union

from core.logger import get_logger

logger = get_logger(__name__)

# Type aliases for clarity
Instance = Any  # Game instance with thymio_simulator attribute
Parameters = Dict[str, Any]

# Choice params (sensor_index, sound_id) are persisted as their full label
# string, e.g. "2 - Front Center" / "0 - Startup" — the GM80 action dialog
# saves widget.currentText(). Match a leading integer index followed by a
# " - <letter...>" label so the index can be recovered (audit M1). A plain
# number ("440") or a variable name never matches this shape.
_CHOICE_LABEL_RE = re.compile(r'^\s*(\d+)\s*-\s*[A-Za-z]')


def register_thymio_actions(action_executor: Any) -> None:
    """Register all Thymio action handlers with the ActionExecutor.

    Args:
        action_executor: ActionExecutor instance to register handlers with
    """

    # ========================================================================
    # MOTOR CONTROL ACTIONS
    # ========================================================================

    def execute_thymio_set_motor_speed_action(instance, parameters):
        """Set left and right motor speeds independently"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        left_speed = _parse_value(parameters.get('left_speed', 0), instance)
        right_speed = _parse_value(parameters.get('right_speed', 0), instance)

        sim.set_motor_speed(int(left_speed), int(right_speed))

    def execute_thymio_move_forward_action(instance, parameters):
        """Move forward at specified speed"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        speed = _parse_value(parameters.get('speed', 200), instance)
        sim.set_motor_speed(int(speed), int(speed))

    def execute_thymio_move_backward_action(instance, parameters):
        """Move backward at specified speed"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        speed = _parse_value(parameters.get('speed', 200), instance)
        sim.set_motor_speed(-int(speed), -int(speed))

    def execute_thymio_turn_left_action(instance, parameters):
        """Turn left in place"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        speed = _parse_value(parameters.get('speed', 300), instance)
        sim.set_motor_speed(0, int(speed))

    def execute_thymio_turn_right_action(instance, parameters):
        """Turn right in place"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        speed = _parse_value(parameters.get('speed', 300), instance)
        sim.set_motor_speed(int(speed), 0)

    def execute_thymio_stop_motors_action(instance, parameters):
        """Stop both motors"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        sim.set_motor_speed(0, 0)

    # ========================================================================
    # LED CONTROL ACTIONS
    # ========================================================================

    def execute_thymio_set_led_top_action(instance, parameters):
        """Set top RGB LED color"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        r = _parse_value(parameters.get('red', 0), instance)
        g = _parse_value(parameters.get('green', 0), instance)
        b = _parse_value(parameters.get('blue', 0), instance)

        sim.set_led_top(int(r), int(g), int(b))

    def execute_thymio_set_led_bottom_left_action(instance, parameters):
        """Set bottom left RGB LED color"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        r = _parse_value(parameters.get('red', 0), instance)
        g = _parse_value(parameters.get('green', 0), instance)
        b = _parse_value(parameters.get('blue', 0), instance)

        sim.set_led_bottom_left(int(r), int(g), int(b))

    def execute_thymio_set_led_bottom_right_action(instance, parameters):
        """Set bottom right RGB LED color"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        r = _parse_value(parameters.get('red', 0), instance)
        g = _parse_value(parameters.get('green', 0), instance)
        b = _parse_value(parameters.get('blue', 0), instance)

        sim.set_led_bottom_right(int(r), int(g), int(b))

    def execute_thymio_set_led_circle_action(instance, parameters):
        """Set one circle LED"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        led_index = _parse_value(parameters.get('led_index', 0), instance)
        intensity = _parse_value(parameters.get('intensity', 32), instance)

        sim.set_led_circle(int(led_index), int(intensity))

    def execute_thymio_set_led_circle_all_action(instance, parameters):
        """Set all 8 circle LEDs"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        intensities = []
        for i in range(8):
            value = _parse_value(parameters.get(f'led{i}', 0), instance)
            intensities.append(int(value))

        sim.set_led_circle_all(intensities)

    def execute_thymio_leds_off_action(instance, parameters):
        """Turn off all LEDs"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        sim.leds_off()

    # ========================================================================
    # SOUND ACTIONS
    # ========================================================================

    def execute_thymio_play_tone_action(instance, parameters):
        """Play a tone"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        frequency = _parse_value(parameters.get('frequency', 440), instance)
        duration = _parse_value(parameters.get('duration', 60), instance)

        sim.play_tone(int(frequency), int(duration))

    def execute_thymio_play_system_sound_action(instance, parameters):
        """Approximate a Thymio system sound with a distinct tone.

        The simulator's audio surface is tone-only (no sampled playback),
        so each of the 8 built-in system sounds is rendered as a half-second
        tone at a distinguishing frequency.
        """
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        sound_id = _parse_value(parameters.get('sound_id', 0), instance)

        sound_frequencies = {
            0: 440,   # Startup
            1: 330,   # Shutdown
            2: 523,   # Arrow
            3: 659,   # Central
            4: 220,   # Free Fall
            5: 880,   # Collision
            6: 587,   # Target Friendly
            7: 698,   # Target Detected
        }

        freq = sound_frequencies.get(int(sound_id), 440)
        sim.play_tone(freq, 30)  # 30/60s = 0.5s

    def execute_thymio_stop_sound_action(instance, parameters):
        """Stop currently playing sound"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        sim.stop_sound()

    # ========================================================================
    # SENSOR READING ACTIONS
    # ========================================================================

    def execute_thymio_read_proximity_action(instance, parameters):
        """Read proximity sensor value and store in variable"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        sensor_index = int(_parse_value(parameters.get('sensor_index', 2), instance))
        variable = parameters.get('variable', 'prox_value')

        if 0 <= sensor_index < 7:
            value = sim.sensors.proximity[sensor_index]
            setattr(instance, variable, value)

    def execute_thymio_read_ground_action(instance, parameters):
        """Read ground sensor value and store in variable"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        sensor_index = int(_parse_value(parameters.get('sensor_index', 0), instance))
        variable = parameters.get('variable', 'ground_value')

        if 0 <= sensor_index < 2:
            value = sim.sensors.ground_delta[sensor_index]
            setattr(instance, variable, value)

    def execute_thymio_read_button_action(instance, parameters):
        """Read button state and store in variable"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        button = parameters.get('button', 'center')
        variable = parameters.get('variable', 'button_state')

        value = sim.get_button(button)
        setattr(instance, variable, value)

    # ========================================================================
    # SENSOR CONDITIONAL ACTIONS
    # ========================================================================

    def execute_thymio_if_proximity_action(instance, parameters):
        """Check if proximity sensor detects obstacle"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return False

        sensor_index = int(_parse_value(parameters.get('sensor_index', 2), instance))
        threshold = _parse_value(parameters.get('threshold', 2000), instance)
        comparison = parameters.get('comparison', '>')

        if 0 <= sensor_index < 7:
            sensor_value = sim.sensors.proximity[sensor_index]
            return _compare_values(sensor_value, comparison, threshold)

        return False

    def execute_thymio_if_ground_dark_action(instance, parameters):
        """Check if ground sensor detects dark surface"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return False

        sensor_index = int(_parse_value(parameters.get('sensor_index', 0), instance))
        threshold = _parse_value(parameters.get('threshold', 300), instance)

        if 0 <= sensor_index < 2:
            sensor_value = sim.sensors.ground_delta[sensor_index]
            return sensor_value < threshold

        return False

    def execute_thymio_if_ground_light_action(instance, parameters):
        """Check if ground sensor detects light surface"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return False

        sensor_index = int(_parse_value(parameters.get('sensor_index', 0), instance))
        threshold = _parse_value(parameters.get('threshold', 300), instance)

        if 0 <= sensor_index < 2:
            sensor_value = sim.sensors.ground_delta[sensor_index]
            return sensor_value >= threshold

        return False

    def execute_thymio_if_button_pressed_action(instance, parameters):
        """Check if button is pressed"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return False

        button = parameters.get('button', 'center')
        return sim.get_button(button) == 1

    def execute_thymio_if_button_released_action(instance, parameters):
        """Check if button is released"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return False

        button = parameters.get('button', 'center')
        return sim.get_button(button) == 0

    # ========================================================================
    # TIMER ACTIONS
    # ========================================================================

    def execute_thymio_set_timer_period_action(instance, parameters):
        """Set timer period in milliseconds"""
        sim = getattr(instance, 'thymio_simulator', None)
        if sim is None:
            return

        timer_id = int(_parse_value(parameters.get('timer_id', 0), instance))
        period = _parse_value(parameters.get('period', 1000), instance)

        sim.set_timer_period(timer_id, int(period))

    # ========================================================================
    # VARIABLE ACTIONS
    # ========================================================================

    def execute_thymio_set_variable_action(instance, parameters):
        """Set a variable value, preserving the value's type.

        The old `int(_parse_value(...))` truncated floats (1.5 -> 1) and
        turned non-numeric strings into 0 (audit M18). Now a float stays a
        float, a numeric string is parsed to its number, a variable name
        resolves to the referenced attribute, and any other string is kept
        verbatim."""
        variable = parameters.get('variable', 'state')
        raw = parameters.get('value', 0)

        if isinstance(raw, bool) or isinstance(raw, (int, float)):
            value = raw
        elif isinstance(raw, str):
            stripped = raw.strip()
            try:
                value = float(stripped) if '.' in stripped else int(stripped)
            except ValueError:
                # Variable reference -> its current value; else a string literal.
                value = getattr(instance, raw, raw)
        else:
            value = _parse_value(raw, instance)

        setattr(instance, variable, value)

    def execute_thymio_increase_variable_action(instance, parameters):
        """Increase a variable"""
        variable = parameters.get('variable', 'counter')
        amount = _parse_value(parameters.get('amount', 1), instance)

        current_value = getattr(instance, variable, 0)
        setattr(instance, variable, int(current_value) + int(amount))

    def execute_thymio_decrease_variable_action(instance, parameters):
        """Decrease a variable"""
        variable = parameters.get('variable', 'counter')
        amount = _parse_value(parameters.get('amount', 1), instance)

        current_value = getattr(instance, variable, 0)
        setattr(instance, variable, int(current_value) - int(amount))

    def execute_thymio_if_variable_action(instance, parameters):
        """Check variable value"""
        variable = parameters.get('variable', 'state')
        comparison = parameters.get('comparison', '==')
        value = _parse_value(parameters.get('value', 0), instance)

        current_value = getattr(instance, variable, 0)
        return _compare_values(current_value, comparison, value)

    # ========================================================================
    # REGISTER ALL HANDLERS
    # ========================================================================

    handlers = {
        # Motors
        'thymio_set_motor_speed': execute_thymio_set_motor_speed_action,
        'thymio_move_forward': execute_thymio_move_forward_action,
        'thymio_move_backward': execute_thymio_move_backward_action,
        'thymio_turn_left': execute_thymio_turn_left_action,
        'thymio_turn_right': execute_thymio_turn_right_action,
        'thymio_stop_motors': execute_thymio_stop_motors_action,

        # LEDs
        'thymio_set_led_top': execute_thymio_set_led_top_action,
        'thymio_set_led_bottom_left': execute_thymio_set_led_bottom_left_action,
        'thymio_set_led_bottom_right': execute_thymio_set_led_bottom_right_action,
        'thymio_set_led_circle': execute_thymio_set_led_circle_action,
        'thymio_set_led_circle_all': execute_thymio_set_led_circle_all_action,
        'thymio_leds_off': execute_thymio_leds_off_action,

        # Sound
        'thymio_play_tone': execute_thymio_play_tone_action,
        'thymio_play_system_sound': execute_thymio_play_system_sound_action,
        'thymio_stop_sound': execute_thymio_stop_sound_action,

        # Sensor reading
        'thymio_read_proximity': execute_thymio_read_proximity_action,
        'thymio_read_ground': execute_thymio_read_ground_action,
        'thymio_read_button': execute_thymio_read_button_action,

        # Sensor conditions
        'thymio_if_proximity': execute_thymio_if_proximity_action,
        'thymio_if_ground_dark': execute_thymio_if_ground_dark_action,
        'thymio_if_ground_light': execute_thymio_if_ground_light_action,
        'thymio_if_button_pressed': execute_thymio_if_button_pressed_action,
        'thymio_if_button_released': execute_thymio_if_button_released_action,

        # Timers
        'thymio_set_timer_period': execute_thymio_set_timer_period_action,

        # Variables
        'thymio_set_variable': execute_thymio_set_variable_action,
        'thymio_increase_variable': execute_thymio_increase_variable_action,
        'thymio_decrease_variable': execute_thymio_decrease_variable_action,
        'thymio_if_variable': execute_thymio_if_variable_action,
    }

    for action_name, handler in handlers.items():
        action_executor.register_custom_action(action_name, handler)

    logger.info(f"✅ Registered {len(handlers)} Thymio action handlers")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_value(value: Any, instance: Instance) -> Union[int, float]:
    """Parse a value that might be a string, number, or variable reference.

    Args:
        value: The value to parse (string, int, or float)
        instance: Game instance for variable resolution

    Returns:
        Parsed numeric value (int or float), defaults to 0
    """
    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        # Choice params arrive as their full label ("2 - Front Center"); pull
        # the leading index so the selection isn't silently collapsed to 0
        # (audit M1).
        choice = _CHOICE_LABEL_RE.match(value)
        if choice:
            return int(choice.group(1))

        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            # Not a number - check if it's a variable reference
            if hasattr(instance, value):
                return getattr(instance, value)
            return 0

    return 0


def _compare_values(value1: Union[int, float], comparison: str, value2: Union[int, float]) -> bool:
    """Compare two values using the specified comparison operator.

    Args:
        value1: First value to compare
        comparison: Comparison operator (>, >=, <, <=, ==, !=)
        value2: Second value to compare

    Returns:
        Result of the comparison
    """
    if comparison == '>':
        return value1 > value2
    elif comparison == '>=':
        return value1 >= value2
    elif comparison == '<':
        return value1 < value2
    elif comparison == '<=':
        return value1 <= value2
    elif comparison == '==':
        return value1 == value2
    elif comparison == '!=':
        return value1 != value2
    else:
        return False

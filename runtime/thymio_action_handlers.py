#!/usr/bin/env python3
"""
Thymio Action Handlers
Implements all 28 Thymio robot actions for the ActionExecutor
"""


def register_thymio_actions(action_executor):
    """
    Register all Thymio action handlers with the ActionExecutor

    Args:
        action_executor: ActionExecutor instance to register handlers with
    """

    # ========================================================================
    # MOTOR CONTROL ACTIONS
    # ========================================================================

    def execute_thymio_set_motor_speed_action(instance, parameters):
        """Set left and right motor speeds independently"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        left_speed = _parse_value(parameters.get('left_speed', 0), instance)
        right_speed = _parse_value(parameters.get('right_speed', 0), instance)

        instance.thymio_simulator.set_motor_speed(int(left_speed), int(right_speed))

    def execute_thymio_move_forward_action(instance, parameters):
        """Move forward at specified speed"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        speed = _parse_value(parameters.get('speed', 200), instance)
        instance.thymio_simulator.set_motor_speed(int(speed), int(speed))

    def execute_thymio_move_backward_action(instance, parameters):
        """Move backward at specified speed"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        speed = _parse_value(parameters.get('speed', 200), instance)
        instance.thymio_simulator.set_motor_speed(-int(speed), -int(speed))

    def execute_thymio_turn_left_action(instance, parameters):
        """Turn left in place"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        speed = _parse_value(parameters.get('speed', 300), instance)
        instance.thymio_simulator.set_motor_speed(0, int(speed))

    def execute_thymio_turn_right_action(instance, parameters):
        """Turn right in place"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        speed = _parse_value(parameters.get('speed', 300), instance)
        instance.thymio_simulator.set_motor_speed(int(speed), 0)

    def execute_thymio_stop_motors_action(instance, parameters):
        """Stop both motors"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        instance.thymio_simulator.set_motor_speed(0, 0)

    # ========================================================================
    # LED CONTROL ACTIONS
    # ========================================================================

    def execute_thymio_set_led_top_action(instance, parameters):
        """Set top RGB LED color"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        r = _parse_value(parameters.get('red', 0), instance)
        g = _parse_value(parameters.get('green', 0), instance)
        b = _parse_value(parameters.get('blue', 0), instance)

        instance.thymio_simulator.set_led_top(int(r), int(g), int(b))

    def execute_thymio_set_led_bottom_left_action(instance, parameters):
        """Set bottom left RGB LED color"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        r = _parse_value(parameters.get('red', 0), instance)
        g = _parse_value(parameters.get('green', 0), instance)
        b = _parse_value(parameters.get('blue', 0), instance)

        instance.thymio_simulator.set_led_bottom_left(int(r), int(g), int(b))

    def execute_thymio_set_led_bottom_right_action(instance, parameters):
        """Set bottom right RGB LED color"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        r = _parse_value(parameters.get('red', 0), instance)
        g = _parse_value(parameters.get('green', 0), instance)
        b = _parse_value(parameters.get('blue', 0), instance)

        instance.thymio_simulator.set_led_bottom_right(int(r), int(g), int(b))

    def execute_thymio_set_led_circle_action(instance, parameters):
        """Set one circle LED"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        led_index = _parse_value(parameters.get('led_index', 0), instance)
        intensity = _parse_value(parameters.get('intensity', 32), instance)

        instance.thymio_simulator.set_led_circle(int(led_index), int(intensity))

    def execute_thymio_set_led_circle_all_action(instance, parameters):
        """Set all 8 circle LEDs"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        intensities = []
        for i in range(8):
            value = _parse_value(parameters.get(f'led{i}', 0), instance)
            intensities.append(int(value))

        instance.thymio_simulator.set_led_circle_all(intensities)

    def execute_thymio_leds_off_action(instance, parameters):
        """Turn off all LEDs"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        instance.thymio_simulator.leds_off()

    # ========================================================================
    # SOUND ACTIONS
    # ========================================================================

    def execute_thymio_play_tone_action(instance, parameters):
        """Play a tone"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        frequency = _parse_value(parameters.get('frequency', 440), instance)
        duration = _parse_value(parameters.get('duration', 60), instance)

        instance.thymio_simulator.play_tone(int(frequency), int(duration))

    def execute_thymio_play_system_sound_action(instance, parameters):
        """Play a system sound (placeholder - just play a tone)"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        sound_id = _parse_value(parameters.get('sound_id', 0), instance)

        # Map system sounds to frequencies (simplified)
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
        instance.thymio_simulator.play_tone(freq, 30)  # 0.5 seconds

    def execute_thymio_stop_sound_action(instance, parameters):
        """Stop currently playing sound"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        instance.thymio_simulator.stop_sound()

    # ========================================================================
    # SENSOR READING ACTIONS
    # ========================================================================

    def execute_thymio_read_proximity_action(instance, parameters):
        """Read proximity sensor value and store in variable"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        sensor_index = int(_parse_value(parameters.get('sensor_index', 2), instance))
        variable = parameters.get('variable', 'prox_value')

        if 0 <= sensor_index < 7:
            value = instance.thymio_simulator.sensors.proximity[sensor_index]
            setattr(instance, variable, value)

    def execute_thymio_read_ground_action(instance, parameters):
        """Read ground sensor value and store in variable"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        sensor_index = int(_parse_value(parameters.get('sensor_index', 0), instance))
        variable = parameters.get('variable', 'ground_value')

        if 0 <= sensor_index < 2:
            value = instance.thymio_simulator.sensors.ground_delta[sensor_index]
            setattr(instance, variable, value)

    def execute_thymio_read_button_action(instance, parameters):
        """Read button state and store in variable"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        button = parameters.get('button', 'center')
        variable = parameters.get('variable', 'button_state')

        value = instance.thymio_simulator.get_button(button)
        setattr(instance, variable, value)

    # ========================================================================
    # SENSOR CONDITIONAL ACTIONS
    # ========================================================================

    def execute_thymio_if_proximity_action(instance, parameters):
        """Check if proximity sensor detects obstacle"""
        if not hasattr(instance, 'thymio_simulator'):
            return False

        sensor_index = int(_parse_value(parameters.get('sensor_index', 2), instance))
        threshold = _parse_value(parameters.get('threshold', 2000), instance)
        comparison = parameters.get('comparison', '>')

        if 0 <= sensor_index < 7:
            sensor_value = instance.thymio_simulator.sensors.proximity[sensor_index]
            return _compare_values(sensor_value, comparison, threshold)

        return False

    def execute_thymio_if_ground_dark_action(instance, parameters):
        """Check if ground sensor detects dark surface"""
        if not hasattr(instance, 'thymio_simulator'):
            return False

        sensor_index = int(_parse_value(parameters.get('sensor_index', 0), instance))
        threshold = _parse_value(parameters.get('threshold', 300), instance)

        if 0 <= sensor_index < 2:
            sensor_value = instance.thymio_simulator.sensors.ground_delta[sensor_index]
            return sensor_value < threshold

        return False

    def execute_thymio_if_ground_light_action(instance, parameters):
        """Check if ground sensor detects light surface"""
        if not hasattr(instance, 'thymio_simulator'):
            return False

        sensor_index = int(_parse_value(parameters.get('sensor_index', 0), instance))
        threshold = _parse_value(parameters.get('threshold', 300), instance)

        if 0 <= sensor_index < 2:
            sensor_value = instance.thymio_simulator.sensors.ground_delta[sensor_index]
            return sensor_value >= threshold

        return False

    def execute_thymio_if_button_pressed_action(instance, parameters):
        """Check if button is pressed"""
        if not hasattr(instance, 'thymio_simulator'):
            return False

        button = parameters.get('button', 'center')
        return instance.thymio_simulator.get_button(button) == 1

    def execute_thymio_if_button_released_action(instance, parameters):
        """Check if button is released"""
        if not hasattr(instance, 'thymio_simulator'):
            return False

        button = parameters.get('button', 'center')
        return instance.thymio_simulator.get_button(button) == 0

    # ========================================================================
    # TIMER ACTIONS
    # ========================================================================

    def execute_thymio_set_timer_period_action(instance, parameters):
        """Set timer period in milliseconds"""
        if not hasattr(instance, 'thymio_simulator'):
            return

        timer_id = int(_parse_value(parameters.get('timer_id', 0), instance))
        period = _parse_value(parameters.get('period', 1000), instance)

        instance.thymio_simulator.set_timer_period(timer_id, int(period))

    # ========================================================================
    # VARIABLE ACTIONS
    # ========================================================================

    def execute_thymio_set_variable_action(instance, parameters):
        """Set a variable value"""
        variable = parameters.get('variable', 'state')
        value = _parse_value(parameters.get('value', 0), instance)

        setattr(instance, variable, int(value))

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

    print(f"✅ Registered {len(handlers)} Thymio action handlers")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_value(value, instance):
    """Parse a value that might be a string, number, or variable reference"""
    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
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


def _compare_values(value1, comparison, value2):
    """Compare two values using the specified comparison operator"""
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

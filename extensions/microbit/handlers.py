#!/usr/bin/env python3
"""Runtime handlers for the micro:bit actions (Stage S3).

A plugin's handlers run as methods of a ``PluginExecutor`` and reach the
engine through ``instance.action_executor`` (the audio/raycast pattern).
Each acts on the micro:bit that runs it; on any other instance an action
does nothing and a condition is false. Conditions return a bool, which the
action executor turns into then/else branches.
"""
import operator

from core.logger import get_logger

from .actions import SENSORS
from .simulator import MAX_BRIGHTNESS, SCROLL_DELAY, WIDTH, HEIGHT
from .state import simulator_of

logger = get_logger(__name__)

_COMPARE = {
    "<": operator.lt, "<=": operator.le, "==": operator.eq,
    ">=": operator.ge, ">": operator.gt, "!=": operator.ne,
}


def _value(instance, raw, default=0):
    """A value param through the expression evaluator (numbers, variables,
    quoted text). Falls back to ``default`` when blank or unparseable."""
    if raw is None or raw == "":
        return default
    ae = getattr(instance, "action_executor", None)
    if ae is None:
        return raw
    try:
        result = ae._parse_value(raw, instance)
    except Exception:
        return default
    return default if result is None or result == "" else result


def _int(instance, raw, default=0):
    try:
        return int(float(_value(instance, raw, default)))
    except (TypeError, ValueError):
        return default


def _seconds(instance, raw, default_ms):
    """A milliseconds param as seconds, never negative."""
    return max(0.0, _int(instance, raw, default_ms) / 1000.0)


def _compare(left, comparison, right):
    return _COMPARE.get(str(comparison).strip(), operator.gt)(left, right)


def read_sensor(sim, sensor):
    """One reading by the names in ``actions.SENSORS``; ``None`` if unknown."""
    x, y, z = sim.acceleration
    if sensor == "accelerometer x":
        return x
    if sensor == "accelerometer y":
        return y
    if sensor == "accelerometer z":
        return z
    if sensor == "acceleration strength":
        return int(round((x * x + y * y + z * z) ** 0.5))
    if sensor == "compass heading":
        return sim.compass_heading
    if sensor == "light level":
        return sim.light_level
    if sensor == "temperature":
        return sim.temperature
    if sensor == "sound level":
        return sim.sound_level
    if sensor.startswith("pin ") and sensor.endswith(" analog"):
        try:
            return sim.pins_analog[int(sensor.split()[1])]
        except (ValueError, KeyError):
            return None
    return None


class PluginExecutor:
    """The micro:bit's display, sensor and condition actions."""

    # -- Display -----------------------------------------------------------

    def execute_microbit_show_image_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        spec = str(parameters.get("image", "HEART")).strip()
        try:
            sim.show_image(spec, hold=_seconds(instance, parameters.get("hold"), 0))
        except ValueError:
            logger.warning(f"micro:bit: not an image: {spec!r}")

    def execute_microbit_scroll_text_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        text = _value(instance, parameters.get("text", ""), "")
        delay = _seconds(instance, parameters.get("delay"), SCROLL_DELAY * 1000)
        sim.scroll_text(str(text), delay or SCROLL_DELAY)

    def execute_microbit_show_number_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        value = _value(instance, parameters.get("value", 0), 0)
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0
        sim.show_number(int(number) if number.is_integer() else number)

    def execute_microbit_set_pixel_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        sim.set_pixel(_int(instance, parameters.get("x")),
                      _int(instance, parameters.get("y")),
                      _int(instance, parameters.get("brightness", MAX_BRIGHTNESS),
                           MAX_BRIGHTNESS))

    def execute_microbit_clear_display_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is not None:
            sim.clear()

    def execute_microbit_set_brightness_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is not None:
            sim.set_brightness(_int(instance, parameters.get("brightness", 255), 255))

    # -- Sound -------------------------------------------------------------

    def execute_microbit_play_tone_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        sim.play_tone(_int(instance, parameters.get("frequency"), 440),
                      _int(instance, parameters.get("duration"), 500))

    def execute_microbit_play_melody_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        spec = str(_value(instance, parameters.get("melody"), "")
                   if str(parameters.get("melody", "")).startswith('"')
                   else parameters.get("melody", "")).strip()
        try:
            sim.play_melody(spec, _int(instance, parameters.get("tempo"), 120))
        except ValueError:
            logger.warning(f"micro:bit: can't play melody {spec!r}")

    def execute_microbit_stop_sound_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is not None:
            sim.stop_sound()

    # -- Sensors -----------------------------------------------------------

    def execute_microbit_read_sensor_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return
        sensor = str(parameters.get("sensor", SENSORS[0])).strip().lower()
        name = str(parameters.get("variable") or "sensor_value").strip()
        value = read_sensor(sim, sensor)
        if value is None or not name:
            return
        if name.startswith("global."):
            ae = getattr(instance, "action_executor", None)
            runner = getattr(ae, "game_runner", None)
            if runner is not None:
                runner.global_variables[name[len("global."):]] = value
        else:
            setattr(instance, name, value)

    # -- Conditions --------------------------------------------------------

    def execute_microbit_if_button_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return False
        button = str(parameters.get("button", "a")).strip().lower()
        if button == "logo":
            return sim.logo_touched
        try:
            return sim.is_pressed(button)
        except KeyError:
            return False

    def execute_microbit_if_gesture_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return False
        return sim.current_gesture == str(
            parameters.get("gesture", "shake")).strip().lower()

    def execute_microbit_if_tilt_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return False
        axis = str(parameters.get("axis", "x")).strip().lower()
        if axis not in ("x", "y", "z"):
            return False
        reading = sim.acceleration["xyz".index(axis)]
        return _compare(reading, parameters.get("comparison", ">"),
                        _int(instance, parameters.get("value"), 0))

    def execute_microbit_if_pixel_action(self, instance, parameters):
        sim = simulator_of(instance)
        if sim is None:
            return False
        x = _int(instance, parameters.get("x"))
        y = _int(instance, parameters.get("y"))
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return False
        return _compare(sim.get_pixel(x, y), parameters.get("comparison", ">"),
                        _int(instance, parameters.get("value"), 0))

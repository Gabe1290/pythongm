#!/usr/bin/env python3
"""Thymio's Python<->action parsing vocabulary, plus the Standard
object-editor panel's post-load events-data transform
(docs/THYMIO_EXTENSION_PLAN.md, Stage G5b.4).

Two separate things live here, extracted at two different times:

- ``parse_execute_code_actions`` (moved verbatim out of
  ``editors/object_editor/events/_panel.py``'s
  ``_parse_execute_code_actions``, ``self`` -> ``panel``). Registered as a
  ``PLUGIN_EVENTS_DATA_TRANSFORMS`` entry (``core/ide_extension_points``),
  run by ``ObjectEventsPanel.load_events_data`` right after a project
  loads, so an object edited on a build without the Thymio tab still gets
  its ``execute_code`` actions parsed back into real ``thymio_*`` actions.
- ``ThymioParser`` (``docs/PROJECT_STATUS.md``'s Thymio-extraction
  follow-up, "moving python_code_parser.py's Thymio-aware parsing engine
  behind a generic seam"): the Thymio-specific method/action/event tables
  and AST pattern-matchers that used to be hardcoded inside
  ``editors/object_editor/python_code_parser.py`` directly. Implements
  that module's ``RobotPlatformParser`` contract and self-registers at
  the bottom of this file via ``register_robot_platform_parser`` -- the
  generic parser's own bottom-of-file bootstrap
  (``_register_builtin_robot_platforms``) imports this module for exactly
  that side effect, so Thymio parsing keeps working the moment
  ``python_code_parser.py`` is imported, with no dependency on the
  Thymio extension/plugin actually being loaded or enabled.

``PythonToActionsParser``/``ActionsToPythonGenerator`` (``editors/
object_editor/python_code_parser.py``) are the generic parsing engine
both pieces here call into.
"""
import ast
from typing import Any, Dict, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


def parse_execute_code_actions(panel) -> None:
    """Parse execute_code actions to extract proper action types (especially Thymio)"""
    from editors.object_editor.python_code_parser import PythonToActionsParser, ActionsToPythonGenerator

    parser = PythonToActionsParser()
    generator = ActionsToPythonGenerator()

    for event_name, event_info in panel.current_events_data.items():
        if not isinstance(event_info, dict):
            continue

        actions = event_info.get('actions', [])
        if not actions:
            continue

        # Build new actions list, parsing execute_code actions
        new_actions = []
        for action in actions:
            action_name = action.get('action') or action.get('type', '')
            if action_name == 'execute_code':
                code = action.get('parameters', {}).get('code', '')
                if code and 'thymio.' in code:
                    # This execute_code contains Thymio code - parse it
                    try:
                        result = parser.parse_event_code(code, event_name)
                        parsed_actions = result.get('actions', [])
                        if parsed_actions:
                            # Check if we got meaningful actions (not just execute_code)
                            has_thymio_actions = any(
                                (a.get('action', '') or a.get('type', '')).startswith('thymio_')
                                for a in parsed_actions
                            )
                            if has_thymio_actions:
                                # Only accept the rewrite if it's LOSSLESS -- the
                                # parse is idempotent under regeneration (L14,
                                # docs/FULL_AUDIT_2026-09-07.md). This is what
                                # guards against the real failure mode: a
                                # `'thymio' in code` substring match against the
                                # RAW text (comments included) gates a heuristic
                                # that reclassifies plain assignments as
                                # thymio_set_variable, so code that merely
                                # MENTIONS "thymio." in a comment could get an
                                # unrelated statement silently reinterpreted.
                                # Regenerating code from parsed_actions and
                                # re-parsing it fresh re-derives whether "thymio"
                                # genuinely appears in the REAL (comment-free)
                                # code; if that disagrees with the first parse,
                                # the rewrite isn't safe to persist.
                                regenerated = generator.generate_event_code(
                                    event_name, {"actions": parsed_actions})
                                reparsed_actions = parser.parse_event_code(
                                    regenerated, event_name).get('actions', [])
                                if reparsed_actions == parsed_actions:
                                    logger.debug(f"Parsed execute_code in {event_name}: {len(parsed_actions)} actions")
                                    new_actions.extend(parsed_actions)
                                    continue
                                logger.debug(
                                    f"Skipping lossy thymio rewrite in {event_name}: "
                                    "parse did not round-trip, keeping original execute_code")
                    except Exception as e:
                        logger.warning(f"Failed to parse execute_code in {event_name}: {e}")
                # Keep original execute_code if not Thymio code or parsing failed
                new_actions.append(action)
            else:
                # Keep non-execute_code actions as-is
                new_actions.append(action)

        # Update the event's actions
        event_info['actions'] = new_actions


# ============================================================================
# ROBOT PLATFORM PARSER: Thymio
# ============================================================================

# method_name -> (action_name, [positional parameter names]).
_METHOD_TO_ACTION = {
    # Motor control
    'set_motor_speed': ('thymio_set_motor_speed', ['left_speed', 'right_speed']),
    'move_forward': ('thymio_move_forward', ['speed']),
    'move_backward': ('thymio_move_backward', ['speed']),
    'turn_left': ('thymio_turn_left', ['speed']),
    'turn_right': ('thymio_turn_right', ['speed']),
    'stop_motors': ('thymio_stop_motors', []),

    # LED control
    'set_led_top': ('thymio_set_led_top', ['red', 'green', 'blue']),
    'set_led_bottom_left': ('thymio_set_led_bottom_left', ['red', 'green', 'blue']),
    'set_led_bottom_right': ('thymio_set_led_bottom_right', ['red', 'green', 'blue']),
    'set_led_circle': ('thymio_set_led_circle', ['led_index', 'intensity']),
    'set_led_circle_all': ('thymio_set_led_circle_all', ['led0', 'led1', 'led2', 'led3', 'led4', 'led5', 'led6', 'led7']),
    'leds_off': ('thymio_leds_off', []),

    # Sound
    'play_tone': ('thymio_play_tone', ['frequency', 'duration']),
    'play_system_sound': ('thymio_play_system_sound', ['sound_id']),
    'stop_sound': ('thymio_stop_sound', []),

    # Timer
    'set_timer_period': ('thymio_set_timer_period', ['timer_id', 'period']),

    # Note: Sensor reads (read_proximity, read_ground, read_button) are handled specially
    # because they return values and are typically used in assignments or conditions
}

# action_name -> Python code template, merged into ACTION_TO_PYTHON.
_ACTION_TO_PYTHON = {
    # Motor control
    'thymio_set_motor_speed': 'thymio.set_motor_speed({left_speed}, {right_speed})',
    'thymio_move_forward': 'thymio.move_forward({speed})',
    'thymio_move_backward': 'thymio.move_backward({speed})',
    'thymio_turn_left': 'thymio.turn_left({speed})',
    'thymio_turn_right': 'thymio.turn_right({speed})',
    'thymio_stop_motors': 'thymio.stop_motors()',

    # LED control
    'thymio_set_led_top': 'thymio.set_led_top({red}, {green}, {blue})',
    'thymio_set_led_bottom_left': 'thymio.set_led_bottom_left({red}, {green}, {blue})',
    'thymio_set_led_bottom_right': 'thymio.set_led_bottom_right({red}, {green}, {blue})',
    'thymio_set_led_circle': 'thymio.set_led_circle({led_index}, {intensity})',
    'thymio_set_led_circle_all': 'thymio.set_led_circle_all({led0}, {led1}, {led2}, {led3}, {led4}, {led5}, {led6}, {led7})',
    'thymio_leds_off': 'thymio.leds_off()',

    # Sound
    'thymio_play_tone': 'thymio.play_tone({frequency}, {duration})',
    'thymio_play_system_sound': 'thymio.play_system_sound({sound_id})',
    'thymio_stop_sound': 'thymio.stop_sound()',

    # Sensor reading (store in variable)
    'thymio_read_proximity': '{variable} = thymio.read_proximity({sensor_index})',
    'thymio_read_ground': '{variable} = thymio.read_ground({sensor_index})',
    'thymio_read_button': '{variable} = thymio.read_button("{button}")',

    # Timer
    'thymio_set_timer_period': 'thymio.set_timer_period({timer_id}, {period})',

    # Variables
    'thymio_set_variable': '{variable} = {value}',
    'thymio_increase_variable': '{variable} += {amount}',
    'thymio_decrease_variable': '{variable} -= {amount}',

    # Conditionals (handled specially in _generate_action_code for sub_actions)
    'thymio_if_proximity': 'if thymio.read_proximity({sensor_index}) {comparison} {threshold}:',
    'thymio_if_ground_dark': 'if thymio.read_ground({sensor_index}) < {threshold}:',
    'thymio_if_ground_light': 'if thymio.read_ground({sensor_index}) >= {threshold}:',
    'thymio_if_button_pressed': 'if thymio.read_button("{button}"):',
    'thymio_if_button_released': 'if not thymio.read_button("{button}"):',
    'thymio_if_variable': 'if {variable} {comparison} {value}:',
}

# action_name -> tuple of its double-quoted string param names.
_QUOTED_STRING_PARAMS = {
    'thymio_read_button': ('button',),
    'thymio_if_button_pressed': ('button',),
    'thymio_if_button_released': ('button',),
}

# event_method_name -> event_name.
_EVENT_METHOD_NAMES = {
    'thymio_button_forward': 'on_thymio_button_forward',
    'thymio_button_backward': 'on_thymio_button_backward',
    'thymio_button_left': 'on_thymio_button_left',
    'thymio_button_right': 'on_thymio_button_right',
    'thymio_button_center': 'on_thymio_button_center',
    'thymio_any_button': 'on_thymio_any_button',
    'thymio_proximity_update': 'on_thymio_proximity_update',
    'thymio_ground_update': 'on_thymio_ground_update',
    'thymio_timer_0': 'on_thymio_timer_0',
    'thymio_timer_1': 'on_thymio_timer_1',
    'thymio_tap': 'on_thymio_tap',
    'thymio_sound_detected': 'on_thymio_sound_detected',
    'thymio_sound_finished': 'on_thymio_sound_finished',
    'thymio_message_received': 'on_thymio_message_received',
}


from editors.object_editor.python_code_parser import (  # noqa: E402
    RobotPlatformParser, register_robot_platform_parser,
)


class ThymioParser(RobotPlatformParser):
    """Thymio's implementation of ``python_code_parser.RobotPlatformParser``.

    Every method here is a verbatim move from
    ``editors/object_editor/python_code_parser.py``'s old
    ``_try_parse_thymio_*``/``THYMIO_METHOD_TO_ACTION`` -- only ``self.`` ->
    ``parser.`` for the shared parser utilities (``_eval_value``,
    ``_extract_actions_from_body``, ``_get_compare_op_str``) that live on
    ``PythonToActionsParser``, not on this class.
    """

    namespace = 'thymio'
    method_to_action = _METHOD_TO_ACTION
    action_to_python = _ACTION_TO_PYTHON
    quoted_string_params = _QUOTED_STRING_PARAMS
    event_method_names = _EVENT_METHOD_NAMES
    conditional_action_prefixes = ('thymio_if_',)

    def try_parse_call(self, call: ast.Call, parser) -> Optional[Dict[str, Any]]:
        """Try to parse a Thymio method call as an action"""
        method_name = call.func.attr

        # Check if this is a known Thymio method
        if method_name in self.method_to_action:
            action_name, param_names = self.method_to_action[method_name]

            # Build parameters dict from positional arguments
            params = {}
            for i, param_name in enumerate(param_names):
                if i < len(call.args):
                    params[param_name] = parser._eval_value(call.args[i])
                else:
                    # Use default value if available
                    params[param_name] = 0

            # Also handle keyword arguments
            for kw in call.keywords:
                if kw.arg in param_names:
                    params[kw.arg] = parser._eval_value(kw.value)

            return {"action": action_name, "parameters": params}

        return None

    def try_parse_assignment(self, stmt: ast.Assign, parser) -> Optional[Dict[str, Any]]:
        """Try to parse a Thymio-related assignment as an action"""
        if len(stmt.targets) != 1:
            return None

        target = stmt.targets[0]
        value = stmt.value

        # Handle variable = thymio.read_*() patterns
        if isinstance(target, ast.Name) and isinstance(value, ast.Call):
            if (isinstance(value.func, ast.Attribute) and
                isinstance(value.func.value, ast.Name) and
                value.func.value.id == self.namespace):

                method_name = value.func.attr
                var_name = target.id

                if method_name == 'read_proximity' and value.args:
                    return {
                        "action": "thymio_read_proximity",
                        "parameters": {
                            "variable": var_name,
                            "sensor_index": parser._eval_value(value.args[0])
                        }
                    }
                elif method_name == 'read_ground' and value.args:
                    return {
                        "action": "thymio_read_ground",
                        "parameters": {
                            "variable": var_name,
                            "sensor_index": parser._eval_value(value.args[0])
                        }
                    }
                elif method_name == 'read_button' and value.args:
                    return {
                        "action": "thymio_read_button",
                        "parameters": {
                            "variable": var_name,
                            "button": parser._eval_value(value.args[0])
                        }
                    }

        # Handle simple variable = value assignments (thymio_set_variable).
        # Only when the code actually uses the Thymio API — otherwise an
        # ordinary `points = 0` in a desktop game was misclassified as a
        # robot action whose runtime handler int()-coerced the value, so
        # `speed_mult = 1.5` stored 1 and `name = "Bob"` stored 0. Without a
        # Thymio context it falls through to the execute_code fallback, which
        # preserves the exact value (audit M18).
        if (self.namespace in parser._active_platform_names
                and isinstance(target, ast.Name)
                and isinstance(value, (ast.Constant, ast.Num))):
            var_name = target.id
            # Only treat as Thymio variable if it looks like a user variable (not Python builtins)
            if not var_name.startswith('_') and var_name not in ('self', 'game', self.namespace):
                return {
                    "action": "thymio_set_variable",
                    "parameters": {
                        "variable": var_name,
                        "value": parser._eval_value(value)
                    }
                }

        return None

    def try_parse_aug_assignment(self, stmt: ast.AugAssign, parser) -> Optional[Dict[str, Any]]:
        """Try to parse Thymio variable increment/decrement"""
        target = stmt.target
        value = stmt.value

        # Handle variable += amount or variable -= amount
        if isinstance(target, ast.Name) and isinstance(value, (ast.Constant, ast.Num)):
            var_name = target.id
            amount = parser._eval_value(value)

            # Only treat as Thymio variable if it looks like a user variable
            if not var_name.startswith('_') and var_name not in ('self', 'game', self.namespace):
                if isinstance(stmt.op, ast.Add):
                    return {
                        "action": "thymio_increase_variable",
                        "parameters": {"variable": var_name, "amount": amount}
                    }
                elif isinstance(stmt.op, ast.Sub):
                    return {
                        "action": "thymio_decrease_variable",
                        "parameters": {"variable": var_name, "amount": amount}
                    }

        return None

    def try_parse_conditional(self, stmt: ast.If, parser) -> Optional[Dict[str, Any]]:
        """Try to parse an if statement as a Thymio conditional action"""
        if stmt.orelse:
            # An if/else (or elif) cannot be represented by a thymio_if_*
            # action — its sub_actions hold only the then-branch, so
            # converting would silently delete the else branch (audit H5).
            # Returning None routes the whole statement through the
            # unrecognized-statement path, which preserves it verbatim as
            # execute_code (the same lossless round-trip non-Thymio if/else
            # statements already get).
            return None

        test = stmt.test

        # Handle: if thymio.read_proximity(n) <comparison> threshold:
        if isinstance(test, ast.Compare):
            result = self._try_parse_compare(test, stmt.body, parser)
            if result:
                return result

        # Handle: if thymio.read_button("name"):
        if isinstance(test, ast.Call):
            result = self._try_parse_button_check(test, stmt.body, True, parser)
            if result:
                return result

        # Handle: if not thymio.read_button("name"):
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.Call):
                result = self._try_parse_button_check(test.operand, stmt.body, False, parser)
                if result:
                    return result

        return None

    def _try_parse_compare(self, test: ast.Compare, body: List[ast.stmt], parser) -> Optional[Dict[str, Any]]:
        """Parse a comparison with Thymio sensor read"""
        if len(test.ops) != 1 or len(test.comparators) != 1:
            return None

        left = test.left
        op = test.ops[0]
        right = test.comparators[0]

        # Check if left side is thymio.read_*()
        if not (isinstance(left, ast.Call) and
                isinstance(left.func, ast.Attribute) and
                isinstance(left.func.value, ast.Name) and
                left.func.value.id == self.namespace):
            return None

        method_name = left.func.attr

        # Get comparison operator
        comparison = parser._get_compare_op_str(op)
        threshold = parser._eval_value(right)

        # Parse body as sub_actions
        sub_actions = parser._extract_actions_from_body(body)

        if method_name == 'read_proximity' and left.args:
            sensor_index = parser._eval_value(left.args[0])
            return {
                "action": "thymio_if_proximity",
                "parameters": {
                    "sensor_index": sensor_index,
                    "comparison": comparison,
                    "threshold": threshold
                },
                "sub_actions": sub_actions
            }

        elif method_name == 'read_ground' and left.args:
            sensor_index = parser._eval_value(left.args[0])
            # Determine if it's "dark" (< threshold) or "light" (>= threshold)
            if isinstance(op, ast.Lt) or isinstance(op, ast.LtE):
                return {
                    "action": "thymio_if_ground_dark",
                    "parameters": {
                        "sensor_index": sensor_index,
                        "threshold": threshold
                    },
                    "sub_actions": sub_actions
                }
            else:
                return {
                    "action": "thymio_if_ground_light",
                    "parameters": {
                        "sensor_index": sensor_index,
                        "threshold": threshold
                    },
                    "sub_actions": sub_actions
                }

        return None

    def _try_parse_button_check(self, call: ast.Call, body: List[ast.stmt], pressed: bool, parser) -> Optional[Dict[str, Any]]:
        """Parse if thymio.read_button("name"): or if not thymio.read_button("name"):"""
        if not (isinstance(call.func, ast.Attribute) and
                isinstance(call.func.value, ast.Name) and
                call.func.value.id == self.namespace and
                call.func.attr == 'read_button'):
            return None

        if not call.args:
            return None

        button = parser._eval_value(call.args[0])
        sub_actions = parser._extract_actions_from_body(body)

        if pressed:
            return {
                "action": "thymio_if_button_pressed",
                "parameters": {"button": button},
                "sub_actions": sub_actions
            }
        else:
            return {
                "action": "thymio_if_button_released",
                "parameters": {"button": button},
                "sub_actions": sub_actions
            }


register_robot_platform_parser(ThymioParser())

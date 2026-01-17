#!/usr/bin/env python3
"""
Control Action Handlers

Handles conditional actions, collision checks, and flow control.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_bool, get_collision_other,
)

logger = get_logger(__name__)


def handle_if_collision(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Execute collision check (GameMaker-style).

    Supports 'any', 'solid', or specific object name.
    Returns True if collision exists, False otherwise.
    """
    x_offset = parse_float(ctx, params.get("x", 0), instance, default=0.0)
    y_offset = parse_float(ctx, params.get("y", 0), instance, default=0.0)
    object_type = params.get("object", "any")
    not_flag = parse_bool(params.get("not_flag", False))

    check_x = instance.x + x_offset
    check_y = instance.y + y_offset

    has_collision = False
    exclude_instance = get_collision_other(ctx)

    if ctx.game_runner:
        has_collision = ctx.game_runner.check_collision_at_position(
            instance, check_x, check_y, object_type, exclude_instance
        )

    result = not has_collision if not_flag else has_collision
    logger.debug(f"  ❓ if_collision at ({check_x}, {check_y}) for '{object_type}': result={result}")
    return result


def handle_if_collision_at(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute collision check with conditional actions (Blockly-style)."""
    x_expr = params.get("x", "self.x")
    y_expr = params.get("y", "self.y")
    object_type = params.get("object_type", params.get("object", "any"))
    then_actions = params.get("then_actions", [])
    else_actions = params.get("else_actions", [])

    if not hasattr(instance, 'collision_checks'):
        instance.collision_checks = []

    instance.collision_checks.append({
        'x': x_expr,
        'y': y_expr,
        'object_type': object_type,
        'then_actions': then_actions,
        'else_actions': else_actions
    })


def handle_if_object_exists(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if any instance of an object type exists in the room."""
    object_type = params.get("object", "")
    not_flag = parse_bool(params.get("not_flag", False))

    if not object_type:
        return False

    exists = False
    if ctx.game_runner and ctx.game_runner.current_room:
        for room_instance in ctx.game_runner.current_room.instances:
            if room_instance.object_name == object_type:
                exists = True
                break

    result = not exists if not_flag else exists
    logger.debug(f"  ❓ if_object_exists: '{object_type}' exists={exists}, result={result}")
    return result


def handle_if_variable(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if a variable meets a condition."""
    variable = params.get("variable", "")
    operation = params.get("operation", "equals")
    value = params.get("value", 0)
    not_flag = parse_bool(params.get("not_flag", False))

    if not variable:
        return False

    # Get variable value
    var_value = ctx._parse_value(variable, instance)
    compare_value = ctx._parse_value(str(value), instance)

    # Perform comparison
    try:
        if operation == "equals":
            result = var_value == compare_value
        elif operation == "not_equals":
            result = var_value != compare_value
        elif operation == "less_than":
            result = float(var_value) < float(compare_value)
        elif operation == "greater_than":
            result = float(var_value) > float(compare_value)
        elif operation == "less_equal":
            result = float(var_value) <= float(compare_value)
        elif operation == "greater_equal":
            result = float(var_value) >= float(compare_value)
        else:
            result = var_value == compare_value
    except (ValueError, TypeError):
        result = False

    if not_flag:
        result = not result

    logger.debug(f"  ❓ if_variable: {variable} {operation} {value} = {result}")
    return result


def handle_if_random_chance(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Random chance conditional - returns True with given probability."""
    import random

    sides = parse_float(ctx, params.get("sides", 2), instance, default=2.0)
    not_flag = parse_bool(params.get("not_flag", False))

    if sides < 1:
        sides = 1

    result = random.random() < (1.0 / sides)

    if not_flag:
        result = not result

    logger.debug(f"  🎲 if_random_chance: 1 in {sides} = {result}")
    return result


def handle_if_dice(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if dice roll equals target."""
    import random

    sides = parse_float(ctx, params.get("sides", 6), instance, default=6.0)
    target = parse_float(ctx, params.get("target", 1), instance, default=1.0)
    not_flag = parse_bool(params.get("not_flag", False))

    roll = random.randint(1, max(1, int(sides)))
    result = roll == int(target)

    if not_flag:
        result = not result

    logger.debug(f"  🎲 if_dice: rolled {roll} on d{int(sides)}, target={int(target)}, result={result}")
    return result


def handle_if_expression(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Evaluate a boolean expression."""
    expression = params.get("expression", "false")
    not_flag = parse_bool(params.get("not_flag", False))

    result = ctx._evaluate_expression(expression, instance)

    if isinstance(result, bool):
        pass
    elif isinstance(result, (int, float)):
        result = result != 0
    else:
        result = bool(result)

    if not_flag:
        result = not result

    logger.debug(f"  📝 if_expression: '{expression}' = {result}")
    return result


def handle_if_mouse_button(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if a mouse button is pressed."""
    button = params.get("button", "left")
    not_flag = parse_bool(params.get("not_flag", False))

    result = False
    if ctx.game_runner:
        mouse_buttons = getattr(ctx.game_runner, 'mouse_buttons', set())
        button_map = {"left": 1, "right": 3, "middle": 2}
        button_id = button_map.get(button, 1) if isinstance(button, str) else int(button)
        result = button_id in mouse_buttons

    if not_flag:
        result = not result

    logger.debug(f"  🖱️ if_mouse_button: {button} pressed = {result}")
    return result


def handle_if_key_pressed(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Check if a key is currently pressed."""
    key = params.get("key", "")
    not_flag = parse_bool(params.get("not_flag", False))

    result = False
    if ctx.game_runner:
        keys_pressed = getattr(ctx.game_runner, 'keys_pressed', set())
        result = key in keys_pressed or key.lower() in keys_pressed

    if not_flag:
        result = not result

    logger.debug(f"  ⌨️ if_key_pressed: '{key}' = {result}")
    return result


def handle_test_chance(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Test random chance - returns True with 1/sides probability."""
    import random
    from runtime.action_handlers.base import parse_int

    sides = parse_int(ctx, params.get("sides", 2), instance, default=2)
    not_flag = parse_bool(params.get("not_flag", False))

    if sides < 1:
        sides = 1

    result = random.randint(1, sides) == 1

    if not_flag:
        result = not result

    logger.debug(f"  🎲 test_chance: 1 in {sides} = {result}")
    return result


def handle_test_expression(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Test if an expression evaluates to true."""
    expression = params.get("expression", "0")
    not_flag = parse_bool(params.get("not_flag", False))

    result = ctx._evaluate_expression(expression, instance)

    if isinstance(result, (int, float)):
        result = result != 0
    else:
        result = bool(result)

    if not_flag:
        result = not result

    logger.debug(f"  📝 test_expression: '{expression}' = {result}")
    return result


def handle_test_instance_count(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Test if instance count of an object meets condition."""
    from runtime.action_handlers.base import parse_int

    object_name = params.get("object", "")
    count = parse_int(ctx, params.get("count", 0), instance, default=0)
    operation = params.get("operation", "equals")
    not_flag = parse_bool(params.get("not_flag", False))

    actual_count = 0
    if ctx.game_runner:
        for inst in getattr(ctx.game_runner, 'instances', []):
            if getattr(inst, 'object_name', '') == object_name:
                actual_count += 1

    if operation == "equals":
        result = actual_count == count
    elif operation == "less_than":
        result = actual_count < count
    elif operation == "greater_than":
        result = actual_count > count
    else:
        result = actual_count == count

    if not_flag:
        result = not result

    logger.debug(f"  🔢 test_instance_count: {object_name} count={actual_count} {operation} {count} = {result}")
    return result


def handle_test_question(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Display a yes/no question and return result."""
    question = params.get("question", "")

    # Queue the question for the game runner to display
    if ctx.game_runner:
        if not hasattr(ctx.game_runner, 'pending_questions'):
            ctx.game_runner.pending_questions = []
        ctx.game_runner.pending_questions.append(question)

    logger.debug(f"  ❓ test_question: '{question}'")
    # Default to True (yes) - actual result comes from dialog
    return True


def handle_code(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute inline code (limited GML support)."""
    code = params.get("code", "")

    if not code:
        return

    logger.debug(f"💻 Execute code: {code[:50]}...")

    # Simple assignment pattern
    if '=' in code and not any(op in code for op in ['==', '!=', '<=', '>=']):
        lines = code.split(';')
        for line in lines:
            line = line.strip()
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value_expr = parts[1].strip()
                    parsed_value = ctx._parse_value(value_expr, instance)

                    if '.' in var_name:
                        scope, name = var_name.split('.', 1)
                        if scope.lower() == 'self':
                            setattr(instance, name, parsed_value)
                        elif scope.lower() == 'global' and ctx.game_runner:
                            ctx.game_runner.global_variables[name] = parsed_value
                    else:
                        setattr(instance, var_name, parsed_value)


def handle_script(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute a named script."""
    script_name = params.get("script", params.get("name", ""))
    arguments = params.get("arguments", params.get("args", []))

    if not script_name:
        logger.debug("⚠️ execute_script: No script specified")
        return

    if ctx.game_runner and hasattr(ctx.game_runner, 'scripts'):
        script = ctx.game_runner.scripts.get(script_name)
        if script:
            try:
                # Execute script with arguments
                if callable(script):
                    script(instance, *arguments)
                logger.debug(f"📜 Executed script: {script_name}")
            except Exception as e:
                logger.error(f"❌ Script error in {script_name}: {e}")
        else:
            logger.debug(f"⚠️ Script not found: {script_name}")
    else:
        logger.debug(f"📜 Script execution (stub): {script_name}")


# =============================================================================
# Handler Registry
# =============================================================================

def handle_test_variable(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Test variable condition (alias for if_variable)."""
    return handle_if_variable(ctx, instance, params)


CONTROL_HANDLERS: Dict[str, Any] = {
    "if_collision": handle_if_collision,
    "if_collision_at": handle_if_collision_at,
    "if_object_exists": handle_if_object_exists,
    "if_variable": handle_if_variable,
    "if_random_chance": handle_if_random_chance,
    "if_dice": handle_if_dice,
    "if_expression": handle_if_expression,
    "if_mouse_button": handle_if_mouse_button,
    "if_key_pressed": handle_if_key_pressed,
    # Test actions (alternate names)
    "test_chance": handle_test_chance,
    "test_expression": handle_test_expression,
    "test_instance_count": handle_test_instance_count,
    "test_question": handle_test_question,
    "test_variable": handle_test_variable,
    # Code execution
    "code": handle_code,
    "script": handle_script,
    # Aliases
    "collision": handle_if_collision,
}

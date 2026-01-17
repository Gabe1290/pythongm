#!/usr/bin/env python3
"""
Variable Action Handlers

Handles variable manipulation: set, change, test variables.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_float, parse_bool,
)

logger = get_logger(__name__)


def handle_set_variable(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set a variable to a value."""
    variable = params.get("variable", "")
    value = params.get("value", 0)
    relative = parse_bool(params.get("relative", False))

    if not variable:
        logger.debug("⚠️ set_variable: No variable name specified")
        return

    # Parse the value
    parsed_value = ctx._parse_value(str(value), instance)

    # Determine scope
    if '.' in variable:
        scope, var_name = variable.split('.', 1)
        scope = scope.lower()
    else:
        scope = 'self'
        var_name = variable

    # Get current value for relative mode
    if relative:
        if scope == 'self':
            current = getattr(instance, var_name, 0)
        elif scope == 'global' and ctx.game_runner:
            current = ctx.game_runner.global_variables.get(var_name, 0)
        else:
            current = 0

        try:
            parsed_value = float(current) + float(parsed_value)
        except (ValueError, TypeError):
            pass

    # Set the value
    if scope == 'self':
        setattr(instance, var_name, parsed_value)
        logger.debug(f"  📝 Set self.{var_name} = {parsed_value}")
    elif scope == 'global' and ctx.game_runner:
        ctx.game_runner.global_variables[var_name] = parsed_value
        logger.debug(f"  📝 Set global.{var_name} = {parsed_value}")
    elif scope == 'other':
        other = getattr(ctx, '_collision_other', None)
        if other:
            setattr(other, var_name, parsed_value)
            logger.debug(f"  📝 Set other.{var_name} = {parsed_value}")


def handle_test_variable(ctx: HandlerContext, instance: Instance, params: Parameters) -> bool:
    """Test a variable against a value - returns True/False."""
    variable = params.get("variable", "")
    operation = params.get("operation", "equals")
    value = params.get("value", 0)
    not_flag = parse_bool(params.get("not_flag", False))

    if not variable:
        return False

    var_value = ctx._parse_value(variable, instance)
    compare_value = ctx._parse_value(str(value), instance)

    try:
        var_float = float(var_value) if var_value is not None else 0
        cmp_float = float(compare_value) if compare_value is not None else 0

        if operation == "equals":
            result = var_value == compare_value or var_float == cmp_float
        elif operation == "not_equals":
            result = var_value != compare_value and var_float != cmp_float
        elif operation == "less_than":
            result = var_float < cmp_float
        elif operation == "greater_than":
            result = var_float > cmp_float
        elif operation == "less_equal":
            result = var_float <= cmp_float
        elif operation == "greater_equal":
            result = var_float >= cmp_float
        else:
            result = var_value == compare_value
    except (ValueError, TypeError):
        result = str(var_value) == str(compare_value) if operation == "equals" else False

    if not_flag:
        result = not result

    logger.debug(f"  ❓ test_variable: {variable} {operation} {value} = {result}")
    return result


def handle_draw_variable(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Draw the value of a variable at a position."""
    from runtime.action_handlers.base import parse_int, queue_draw_command

    x = parse_int(ctx, params.get("x", 0), instance, default=0)
    y = parse_int(ctx, params.get("y", 0), instance, default=0)
    variable_name = params.get("variable", "")

    if not variable_name:
        value = ""
    else:
        value = ctx._parse_value(variable_name, instance)

    text = str(value)
    color = getattr(instance, 'draw_color', (0, 0, 0))

    queue_draw_command(instance, {
        'type': 'text',
        'x': x,
        'y': y,
        'text': text,
        'color': color
    })

    logger.debug(f"📊 Queued draw_variable: '{variable_name}' = '{text}' at ({x}, {y})")


def handle_execute_code(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute custom code (limited support)."""
    code = params.get("code", "")

    if not code:
        return

    # Very limited execution support - mainly for simple assignments
    # Real GML execution would require a full parser
    logger.debug(f"💻 Execute code: {code[:50]}...")

    # Simple assignment pattern: variable = value
    if '=' in code and not any(op in code for op in ['==', '!=', '<=', '>=']):
        parts = code.split('=', 1)
        if len(parts) == 2:
            var_name = parts[0].strip()
            value_expr = parts[1].strip().rstrip(';')

            parsed_value = ctx._parse_value(value_expr, instance)

            if '.' in var_name:
                scope, name = var_name.split('.', 1)
                if scope.lower() == 'self':
                    setattr(instance, name, parsed_value)
                elif scope.lower() == 'global' and ctx.game_runner:
                    ctx.game_runner.global_variables[name] = parsed_value
            else:
                setattr(instance, var_name, parsed_value)


def handle_execute_script(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute a named script (placeholder)."""
    script_name = params.get("script", "")
    logger.debug(f"📜 Execute script: {script_name} (not fully implemented)")


def handle_comment(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Comment action - does nothing at runtime."""
    pass


# =============================================================================
# Handler Registry
# =============================================================================

VARIABLE_HANDLERS: Dict[str, Any] = {
    "set_variable": handle_set_variable,
    "test_variable": handle_test_variable,
    "draw_variable": handle_draw_variable,
    "execute_code": handle_execute_code,
    "execute_script": handle_execute_script,
    "comment": handle_comment,
}

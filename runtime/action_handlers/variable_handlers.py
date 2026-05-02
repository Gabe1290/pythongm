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


# NOTE: handle_set_variable and handle_test_variable previously lived here as
# modular handlers, but ActionExecutor.execute_set_variable_action and
# .execute_test_variable_action take Phase-1 priority and the modular versions
# were never reached. Worse, they used different operation strings (e.g.
# "equals" vs "equal") and a different scope-encoding ("self.name" vs separate
# `scope` param), which made their presence actively misleading. They have
# been removed; the executor methods are the canonical implementations.
# (See also: ~115 other actions with the same dead-modular-handler pattern.)


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
    "draw_variable": handle_draw_variable,
    "execute_code": handle_execute_code,
    "execute_script": handle_execute_script,
    "comment": handle_comment,
}

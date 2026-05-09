#!/usr/bin/env python3
"""
Variable Action Handlers

Handles variable manipulation: set, change, test variables.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
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





def handle_comment(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Comment action - does nothing at runtime."""
    pass


# =============================================================================
# Handler Registry
# =============================================================================

VARIABLE_HANDLERS: Dict[str, Any] = {
    "comment": handle_comment,
}

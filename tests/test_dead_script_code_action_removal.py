#!/usr/bin/env python3
"""
Regression: the "script"/"code" action stub removal (2026-08-14).

runtime/action_handlers/control_handlers.py used to register two handlers
(handle_script, handle_code) under the action names "script"/"code". Neither
name ever had an events/action_types.py entry, and no sample/importer ever
emitted either name -- confirmed dead code, distinct from the real, working
execute_script/execute_code actions. This pins their removal and confirms
the real actions are unaffected.
"""

from events.action_types import get_action_type
from runtime.action_handlers.control_handlers import CONTROL_HANDLERS


def test_dead_action_names_not_in_control_handlers():
    assert "script" not in CONTROL_HANDLERS
    assert "code" not in CONTROL_HANDLERS


def test_dead_action_names_not_resolvable():
    assert get_action_type("script") is None
    assert get_action_type("code") is None


def test_real_execute_script_and_execute_code_untouched():
    assert get_action_type("execute_script") is not None
    assert get_action_type("execute_code") is not None

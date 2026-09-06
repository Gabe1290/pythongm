#!/usr/bin/env python3
"""
Regression: the "script"/"code" action stub removal (2026-08-14).

`runtime/action_handlers/control_handlers.py` used to register two handlers
(handle_script, handle_code) under the action names "script"/"code". Neither
name ever had an events/action_types.py entry, and no sample or importer ever
emitted either -- confirmed dead code, distinct from the real, working
execute_script / execute_code actions.

That module itself was deleted on 2026-09-06 (the docs/POST_1_0_REFACTOR.md
action_handlers teardown, once the "do we keep legacy action names?" question
was answered: no). So this no longer imports it. The assertions moved to the
LIVE dispatch table instead, which is a stronger statement of the same intent
-- it holds no matter which module a handler might come back from -- and the
same treatment the extra_handlers.py deletion gave its own tests.
"""

from events.action_types import get_action_type


def test_dead_action_names_are_not_dispatchable():
    """The point of the original removal: nothing anywhere registers these."""
    from runtime.action_executor import ActionExecutor

    executor = ActionExecutor()
    assert "script" not in executor.action_handlers
    assert "code" not in executor.action_handlers


def test_the_module_that_defined_them_is_gone():
    """It carried only legacy pre-if_condition conditionals besides these two;
    if it comes back, the teardown has been undone and the names above deserve
    re-checking rather than assuming."""
    import importlib

    try:
        importlib.import_module("runtime.action_handlers.control_handlers")
    except ImportError:
        return
    raise AssertionError(
        "runtime/action_handlers/control_handlers.py is back -- re-verify that "
        "it does not reintroduce the dead 'script'/'code' handlers")


def test_dead_action_names_not_resolvable():
    assert get_action_type("script") is None
    assert get_action_type("code") is None


def test_real_execute_script_and_execute_code_untouched():
    assert get_action_type("execute_script") is not None
    assert get_action_type("execute_code") is not None

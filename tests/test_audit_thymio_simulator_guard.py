"""Regression tests for audit finding L31.

Thymio action handlers guarded with `hasattr(instance, 'thymio_simulator')`,
but GameInstance unconditionally defines the attribute (set to None for any
non-Thymio object). The hasattr guard therefore always passed, the handler
dereferenced None, raised AttributeError (swallowed by execute_action and
converted to a return of None), and the authored `return False` fallback in
the condition handlers was never reached. None means "not a conditional" to
the flow control, so flat-form Thymio conditions on a non-Thymio object acted
as always-true and nested then/else branches both skipped.

The fix replaces every guard with
    sim = getattr(instance, 'thymio_simulator', None)
    if sim is None: return False  # (or `return` for command actions)

so a non-Thymio instance (thymio_simulator is None) returns the correct
sentinel without raising.
"""

from runtime.action_executor import ActionExecutor
from runtime.thymio_action_handlers import register_thymio_actions


class _FakeInstance:
    """Mimics a non-Thymio GameInstance: thymio_simulator is defined as None."""
    def __init__(self):
        self.thymio_simulator = None  # game_runner.py:578 default
        self.object_name = "MonRobot"  # no 'thymio' prefix -> no simulator


def _make_executor():
    ex = ActionExecutor.__new__(ActionExecutor)
    ex.action_handlers = {}
    ex.ACTION_ALIASES = {}
    register_thymio_actions(ex)
    return ex


CONDITION_ACTIONS = [
    'thymio_if_proximity',
    'thymio_if_ground_dark',
    'thymio_if_ground_light',
    'thymio_if_button_pressed',
    'thymio_if_button_released',
]

COMMAND_ACTIONS = [
    'thymio_set_motor_speed',
    'thymio_move_forward',
    'thymio_move_backward',
    'thymio_turn_left',
    'thymio_turn_right',
    'thymio_stop_motors',
    'thymio_set_led_top',
    'thymio_set_led_bottom_left',
    'thymio_set_led_bottom_right',
    'thymio_set_led_circle',
    'thymio_set_led_circle_all',
    'thymio_leds_off',
    'thymio_play_tone',
    'thymio_play_system_sound',
    'thymio_stop_sound',
    'thymio_read_proximity',
    'thymio_read_ground',
    'thymio_read_button',
    'thymio_set_timer_period',
]


def test_condition_handlers_return_false_not_none_on_non_thymio():
    """Each condition handler must return False (not None / not raise) when
    the instance has no simulator, so flow control correctly treats it as a
    false conditional."""
    ex = _make_executor()
    inst = _FakeInstance()
    for name in CONDITION_ACTIONS:
        handler = ex.action_handlers[name]
        result = handler(inst, {})
        assert result is False, f"{name} returned {result!r}, expected False"


def test_command_handlers_no_op_without_raising_on_non_thymio():
    """Command handlers must simply return (None) without dereferencing the
    None simulator and raising AttributeError."""
    ex = _make_executor()
    inst = _FakeInstance()
    for name in COMMAND_ACTIONS:
        handler = ex.action_handlers[name]
        # Must not raise; returns None (a command, not a conditional).
        assert handler(inst, {}) is None, f"{name} should no-op to None"


def test_flat_form_condition_skips_following_action_when_false():
    """End-to-end: a flat-form Thymio condition on a non-Thymio instance
    evaluates to False, so the next action in a flat list IS skipped.

    Before the fix the condition leaked None -> the following action ran
    unconditionally (condition behaved as always-true)."""
    ex = _make_executor()
    inst = _FakeInstance()

    handler = ex.action_handlers['thymio_if_ground_dark']
    result = handler(inst, {})
    # execute_action_list (action_executor.py:290) skips the next action only
    # when `result is False`. None would NOT skip.
    assert result is False


def test_nested_else_branch_selected_when_condition_false():
    """With dialog-authored then/else, a false condition selects the ELSE
    branch. execute_action (action_executor.py:455-461) only dispatches a
    branch when the handler returns an actual bool; a leaked None would skip
    branch dispatch entirely (neither then nor else runs). Here we assert the
    handler yields a real False so the documented dispatch picks else."""
    ex = _make_executor()
    inst = _FakeInstance()

    handler = ex.action_handlers['thymio_if_button_pressed']
    result = handler(inst, {})

    # The exact predicate execute_action uses to decide branch dispatch.
    assert result is not None and isinstance(result, bool)
    selected = 'then' if result else 'else'
    assert selected == 'else'


def test_condition_still_works_for_real_thymio_instance():
    """Sanity: with a simulator attached the handler reads it (no regression)."""
    ex = _make_executor()

    class _Sensors:
        ground_delta = [50, 50]  # below the default dark threshold of 300

    class _Sim:
        sensors = _Sensors()

    class _ThymioInstance:
        thymio_simulator = _Sim()

    inst = _ThymioInstance()
    handler = ex.action_handlers['thymio_if_ground_dark']
    # ground_delta 50 < threshold 300 -> dark -> True
    assert handler(inst, {}) is True

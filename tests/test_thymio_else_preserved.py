"""Regression tests for Thymio if/else parsing (audit H5).

docs/FULL_AUDIT_2026-06-11.md: _try_parse_thymio_conditional (and its
compare/button helpers) parsed stmt.test and stmt.body into a thymio_if_*
action but never read stmt.orelse — the entire else branch was silently
deleted. Amplified by ObjectEventsPanel._parse_execute_code_actions,
which re-parses any stored execute_code containing 'thymio.' on EVERY
load and replaces it whenever the parse yields a thymio_ action — so a
saved, working project lost its else logic just by being opened.

The parser now refuses to convert a Thymio if that has an else/elif and
preserves the whole statement verbatim as execute_code (the lossless path
non-Thymio conditionals already used). Plain Thymio ifs (no else) still
convert to block actions.
"""

import pytest

from editors.object_editor.python_code_parser import (
    python_to_events, events_to_python)


IF_ELSE_CODE = (
    "class obj:\n"
    "    def on_step(self):\n"
    '        if thymio.read_button("center"):\n'
    "            thymio.set_led_top(32, 0, 0)\n"
    "        else:\n"
    "            thymio.leds_off()\n"
)


def _step_actions(code):
    events, errors = python_to_events(code)
    assert not errors
    return events['step']['actions']


class TestElseBranchPreserved:

    def test_if_else_is_not_lossily_converted(self):
        actions = _step_actions(IF_ELSE_CODE)
        # The whole statement is preserved as one execute_code action
        assert len(actions) == 1
        assert actions[0]['action'] == 'execute_code'
        code = actions[0]['parameters']['code']
        assert 'set_led_top' in code
        assert 'leds_off' in code  # pre-fix: silently deleted
        assert 'else' in code

    def test_round_trip_keeps_else(self):
        events, _ = python_to_events(IF_ELSE_CODE)
        regenerated = events_to_python('obj', events)
        assert 'leds_off' in regenerated
        assert 'else' in regenerated

        # And a second parse of the regenerated code still has it
        events2, errors2 = python_to_events(regenerated)
        assert not errors2
        flat = str(events2)
        assert 'leds_off' in flat

    def test_elif_also_preserved(self):
        code = (
            "class obj:\n"
            "    def on_step(self):\n"
            "        if thymio.read_proximity(2) > 2000:\n"
            "            thymio.move_backward(200)\n"
            "        elif thymio.read_proximity(0) > 2000:\n"
            "            thymio.turn_left(150)\n"
        )
        actions = _step_actions(code)
        assert len(actions) == 1
        assert actions[0]['action'] == 'execute_code'
        assert 'turn_left' in actions[0]['parameters']['code']

    def test_plain_thymio_if_still_converts(self):
        code = (
            "class obj:\n"
            "    def on_step(self):\n"
            '        if thymio.read_button("center"):\n'
            "            thymio.set_led_top(32, 0, 0)\n"
        )
        actions = _step_actions(code)
        assert len(actions) == 1
        assert actions[0]['action'] == 'thymio_if_button_pressed'
        assert len(actions[0]['sub_actions']) == 1


class TestEventsPanelAmplifier:
    """The on-load re-parse must not destroy a saved project's else logic."""

    def _run_panel_reparse(self, events_data):
        from editors.object_editor.object_events_panel import ObjectEventsPanel
        host = type('Host', (), {})()
        host.current_events_data = events_data
        ObjectEventsPanel._parse_execute_code_actions(host)
        return host.current_events_data

    def test_saved_execute_code_with_else_survives_load(self, qapp):
        inner = ('if thymio.read_button("center"):\n'
                 '    thymio.set_led_top(32, 0, 0)\n'
                 'else:\n'
                 '    thymio.leds_off()')
        events = {'step': {'actions': [
            {'action': 'execute_code', 'parameters': {'code': inner}}]}}

        result = self._run_panel_reparse(events)

        flat = str(result)
        assert 'leds_off' in flat  # pre-fix: gone after one open+save

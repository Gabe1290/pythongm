"""Regression tests for plain-assignment misclassification (audit M18).

docs/FULL_AUDIT_2026-06-11.md: _try_parse_thymio_assignment treated ANY
`name = constant` statement as a thymio_set_variable action, with no check
that the project uses Thymio. The runtime handler then setattr'd
int(_parse_value(value)), so in a non-robot game `speed_mult = 1.5` stored
1 and `name = "Bob"` stored 0.

Now the plain-assignment heuristic only fires when the code references the
Thymio API (otherwise the statement falls through to execute_code, which
preserves the exact value), and the runtime handler preserves the value's
type.
"""

import pytest

from conftest import import_module_directly
from editors.object_editor.python_code_parser import python_to_events

_handlers_mod = import_module_directly("runtime/thymio_action_handlers.py")


def _create_actions(body_line):
    code = f"class obj:\n    def on_create(self):\n        {body_line}\n"
    events, errors = python_to_events(code)
    assert not errors
    return events.get('create', {}).get('actions', [])


class TestParserContextGate:
    def test_plain_assignment_in_non_thymio_is_not_thymio_action(self):
        actions = _create_actions("bounce_factor = 1.5")
        kinds = [a.get('action') for a in actions]
        assert 'thymio_set_variable' not in kinds
        # Falls through to execute_code, which preserves the literal
        assert any(a.get('action') == 'execute_code'
                   and 'bounce_factor = 1.5' in a['parameters']['code']
                   for a in actions)

    def test_plain_assignment_with_thymio_context_is_thymio_action(self):
        code = ("class obj:\n"
                "    def on_create(self):\n"
                "        thymio.set_led_top(0, 0, 0)\n"
                "        points = 0\n")
        events, errors = python_to_events(code)
        assert not errors
        actions = events['create']['actions']
        kinds = [a.get('action') for a in actions]
        assert 'thymio_set_variable' in kinds


class TestRuntimeTypePreserved:
    def _handler(self):
        captured = {}

        class FakeExec:
            def register_custom_action(self, name, handler):
                captured[name] = handler

        self._handlers_mod = _handlers_mod
        _handlers_mod.register_thymio_actions(FakeExec())
        return captured['thymio_set_variable']

    def _inst(self):
        return type("Inst", (), {})()

    def test_float_preserved(self):
        h = self._handler()
        inst = self._inst()
        h(inst, {'variable': 'speed_mult', 'value': 1.5})
        assert inst.speed_mult == 1.5  # pre-fix: 1

    def test_string_preserved(self):
        h = self._handler()
        inst = self._inst()
        h(inst, {'variable': 'status', 'value': 'alive'})
        assert inst.status == 'alive'  # pre-fix: 0

    def test_numeric_string_parsed(self):
        h = self._handler()
        inst = self._inst()
        h(inst, {'variable': 'a', 'value': '3'})
        h(inst, {'variable': 'b', 'value': '2.5'})
        assert inst.a == 3
        assert inst.b == 2.5

    def test_int_unchanged(self):
        h = self._handler()
        inst = self._inst()
        h(inst, {'variable': 'n', 'value': 7})
        assert inst.n == 7

    def test_variable_reference_resolves(self):
        h = self._handler()
        inst = self._inst()
        inst.hp = 42
        h(inst, {'variable': 'copy', 'value': 'hp'})
        assert inst.copy == 42

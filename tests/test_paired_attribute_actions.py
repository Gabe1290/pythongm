"""Regression tests for paired-attribute assignments in the code editor.

Audit H4 (docs/FULL_AUDIT_2026-06-11.md): assigning one half of a paired
attribute (`self.x = 100`, `self.direction = 90`,
`self.gravity_direction = 180`) parsed into a multi-parameter action with
the other parameter missing. At runtime the missing half defaulted (the
instance teleported to y=0); at regeneration the template KeyError'd into
a '# Missing parameter' comment, and the next auto-apply silently deleted
the user's statement.

Now the parser fills the missing half with its identity expression
(`self.y`, `self.speed`, `self.gravity` — evaluated by the runtime), the
generator emits paired actions per attribute skipping identity halves
(so round-trips are exact and stable), and set_gravity evaluates
expressions like its siblings.
"""

import pytest

from conftest import import_module_directly

from editors.object_editor.python_code_parser import (
    python_to_events, events_to_python)

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


def _parse_one(line):
    code = f"class obj:\n    def on_create(self):\n        {line}\n"
    result = python_to_events(code)
    events, errors = result if isinstance(result, tuple) else (result, [])
    assert not errors
    actions = events['create']['actions'] if 'create' in events else \
        next(iter(events.values()))['actions']
    assert len(actions) == 1
    return actions[0]


def _regen(action):
    events = {'create': {'actions': [action]}}
    return events_to_python('obj', events)


class TestParseFillsIdentity:

    def test_x_assignment_keeps_y(self):
        action = _parse_one("self.x = 100")
        assert action['action'] == 'jump_to_position'
        assert action['parameters']['x'] == 100
        assert action['parameters']['y'] == 'self.y'

    def test_direction_assignment_keeps_speed(self):
        action = _parse_one("self.direction = 90")
        assert action['action'] == 'set_direction_speed'
        assert action['parameters']['direction'] == 90
        assert action['parameters']['speed'] == 'self.speed'

    def test_gravity_direction_assignment_keeps_gravity(self):
        action = _parse_one("self.gravity_direction = 180")
        assert action['action'] == 'set_gravity'
        assert action['parameters']['direction'] == 180
        assert action['parameters']['gravity'] == 'self.gravity'

    def test_relative_x_uses_additive_identity(self):
        action = _parse_one("self.x += 5")
        assert action['action'] == 'jump_to_position'
        assert action['parameters']['relative'] is True
        assert action['parameters']['y'] == 0


class TestRoundTrip:

    @pytest.mark.parametrize("line", [
        "self.x = 100",
        "self.y = 50",
        "self.direction = 90",
        "self.speed = 4",
        "self.gravity_direction = 180",
        "self.x += 5",
    ])
    def test_statement_round_trips_exactly(self, line):
        action = _parse_one(line)
        code = _regen(action)
        assert "Missing parameter" not in code
        assert line in code

        # And the regenerated code re-parses to the same action (stable —
        # no growth, no loss, no teleport-y default sneaking in)
        lines = [l.strip() for l in code.splitlines()
                 if l.strip() and not l.strip().startswith(('#', 'def', 'class', '"""'))]
        assert lines == [line]

    def test_legacy_half_filled_action_regenerates_without_comment(self):
        """Older saves may hold the pre-fix shape (missing 'y')."""
        action = {'action': 'jump_to_position',
                  'parameters': {'x': 100, 'relative': False}}
        code = _regen(action)
        assert "Missing parameter" not in code
        assert "self.x = 100" in code

    def test_both_halves_still_emit(self):
        action = {'action': 'set_direction_speed',
                  'parameters': {'direction': 90, 'speed': 4, 'relative': False}}
        code = _regen(action)
        assert "self.direction = 90" in code
        assert "self.speed = 4" in code


class TestRuntimeIdentity:

    def _instance(self):
        class Inst:
            object_name = "obj"
            x = 100.0
            y = 240.0
            hspeed = 0.0
            vspeed = 0.0
            direction = 0.0
            speed = 0.0
            gravity = 0.7
            gravity_direction = 270.0
        return Inst()

    def test_jump_with_identity_y_keeps_y(self):
        executor = ActionExecutor()
        inst = self._instance()
        executor.execute_jump_to_position_action(
            inst, {'x': 100, 'y': 'self.y', 'relative': False})
        assert inst.x == 100
        assert inst.y == 240  # pre-fix: teleported to 0

    def test_set_gravity_with_identity_gravity_keeps_gravity(self):
        executor = ActionExecutor()
        inst = self._instance()
        executor.execute_set_gravity_action(
            inst, {'direction': 180, 'gravity': 'self.gravity'})
        assert inst.gravity_direction == 180
        assert inst.gravity == pytest.approx(0.7)

"""Regression tests for Kivy export code-generation bugs.

Registry: docs/FULL_AUDIT_2026-06-11.md (High findings H6-H9).
Each test compiles the generated code — the audit's core failure mode was
exported games that die with SyntaxError/IndentationError at import.
"""

import json
from pathlib import Path

import pytest

SAMPLES = Path(__file__).parent.parent / "samples"


def _make_exporter(tmp_path, project_data=None):
    from export.Kivy.kivy_exporter import KivyExporter

    if project_data is None:
        project_data = {
            'name': 'TestGame',
            'settings': {'window_width': 800, 'window_height': 600},
            'assets': {
                'sprites': {}, 'sounds': {}, 'backgrounds': {},
                'objects': {}, 'rooms': {},
            },
        }
    project_dir = tmp_path / "project"
    project_dir.mkdir(exist_ok=True)
    output_path = tmp_path / "kivy_output"
    output_path.mkdir(exist_ok=True)
    return KivyExporter(project_data, project_dir, output_path)


def _compile_method(method_code: str):
    """Wrap a generated method (indented one level) in a class and compile."""
    source = "class Obj:\n" + method_code + "\n"
    compile(source, "<generated>", "exec")


def _generate_event(actions, event='step'):
    """Run an action list through ActionCodeGenerator, compile, return code."""
    from export.Kivy.code_generator import ActionCodeGenerator
    gen = ActionCodeGenerator(base_indent=2)
    for action in actions:
        gen.process_action(action, event)
    code = gen.get_code()
    compile("class Obj:\n    def on_step(self):\n" + code + "\n",
            "<generated>", "exec")
    return code


class TestConditionalScoping:
    """H6 — conditionals left their indent open 'for sequential action
    handling', swallowing every later action of the event into the branch
    (plateforme_2's jump impulse ran unconditionally every airborne frame)
    or producing IndentationError for flat if;block;after sequences."""

    def test_flat_conditional_guards_only_next_action(self):
        code = _generate_event([
            {'action': 'test_expression', 'parameters': {'expression': 'self.x > 0'}},
            {'action': 'set_hspeed', 'parameters': {'value': 4}},
            {'action': 'set_vspeed', 'parameters': {'value': 2}},
        ])
        lines = code.splitlines()
        assert any(l.strip() == 'if self.x > 0:' for l in lines)
        hs = next(l for l in lines if 'hspeed' in l)
        vs = next(l for l in lines if 'vspeed' in l)
        # hspeed is guarded (deeper), vspeed is back at event level
        assert len(hs) - len(hs.lstrip()) > len(vs) - len(vs.lstrip())

    def test_flat_if_block_then_after_compiles_and_dedents(self):
        """if_condition; start_block; A; end_block; B — pre-fix this was
        'unindent does not match any outer indentation level'."""
        code = _generate_event([
            {'action': 'if_condition', 'parameters': {'condition': 'self.x > 0'}},
            {'action': 'start_block', 'parameters': {}},
            {'action': 'set_hspeed', 'parameters': {'value': 4}},
            {'action': 'end_block', 'parameters': {}},
            {'action': 'set_vspeed', 'parameters': {'value': 2}},
        ])
        lines = code.splitlines()
        guarded = next(l for l in lines if 'hspeed' in l)
        after = next(l for l in lines if 'vspeed' in l)
        assert len(guarded) - len(guarded.lstrip()) > len(after) - len(after.lstrip())

    def test_if_else_each_guard_one_unit(self):
        code = _generate_event([
            {'action': 'if_collision', 'parameters': {'object': 'solid', 'x': 0, 'y': 1}},
            {'action': 'set_gravity', 'parameters': {'gravity': 0, 'direction': 270}},
            {'action': 'else_action', 'parameters': {}},
            {'action': 'set_gravity', 'parameters': {'gravity': 0.45, 'direction': 270}},
            {'action': 'set_hspeed', 'parameters': {'value': 4}},
        ])
        lines = code.splitlines()
        assert any(l.strip() == 'else:' for l in lines)
        trailing = next(l for l in lines if 'hspeed' in l)
        else_line = next(l for l in lines if l.strip() == 'else:')
        # The trailing action sits at the if/else level, not inside else
        assert len(trailing) - len(trailing.lstrip()) == len(else_line) - len(else_line.lstrip())

    def test_collision_not_flag_negates(self):
        code = _generate_event([
            {'action': 'if_collision',
             'parameters': {'object': 'solid', 'x': 0, 'y': 1, 'not_flag': True}},
            {'action': 'set_gravity', 'parameters': {'gravity': 0.45, 'direction': 270}},
        ])
        assert 'if not self.check_collision_at' in code

    def test_trailing_conditional_auto_closes_validly(self):
        code = _generate_event([
            {'action': 'test_expression', 'parameters': {'expression': 'self.x > 0'}},
        ])
        assert 'pass' in code  # empty suite padded

    def test_plateforme_2_step_event_compiles_with_guarded_jump(self):
        """The audit's H6 in-the-wild case: gravity if/else plus a
        test_variable-gated jump. Pre-fix everything after else_action sat
        inside the else branch and the jump fired unconditionally."""
        sample = SAMPLES / "plateforme_2" / "objects" / "obj_personnage.json"
        if not sample.exists():
            pytest.skip("plateforme_2 sample not present")
        with open(sample, encoding='utf-8') as f:
            actions = json.load(f)['events']['step']['actions']
        code = _generate_event(actions)
        lines = code.splitlines()
        jump_cond = next(l for l in lines if 'if ' in l and 'vspeed' in l)
        jump = next(l for l in lines if l.strip().startswith('self.vspeed = -('))
        # The jump is guarded by (exactly one level under) the condition
        assert (len(jump) - len(jump.lstrip())) == \
            (len(jump_cond) - len(jump_cond.lstrip())) + 4


class TestUnknownAndMissingConditionals:
    """H7 — test_instance_count / test_variable fell into the 'pass # TODO'
    fallback: no block opened (the following start_block was a SyntaxError)
    and the guarded actions ran unconditionally."""

    def test_test_instance_count_opens_block(self):
        code = _generate_event([
            {'action': 'test_instance_count',
             'parameters': {'object': 'obj_diamond', 'count': '0', 'operation': 'equal'}},
            {'action': 'start_block', 'parameters': {}},
            {'action': 'destroy_instance', 'parameters': {}},
            {'action': 'end_block', 'parameters': {}},
        ])
        assert "if self.scene.count_instances('obj_diamond') == 0:" in code
        lines = code.splitlines()
        cond = next(l for l in lines if 'count_instances' in l)
        body = next(l for l in lines if 'destroy' in l)
        assert len(body) - len(body.lstrip()) > len(cond) - len(cond.lstrip())

    def test_test_variable_guards_next_action(self):
        code = _generate_event([
            {'action': 'test_variable',
             'parameters': {'variable_name': 'vspeed', 'value': '24',
                            'scope': 'self', 'operation': 'greater_equal'}},
            {'action': 'set_vspeed', 'parameters': {'value': 24}},
        ])
        # vspeed compares in GameMaker space (Kivy axis is flipped)
        assert 'if -(self.vspeed) >= 24:' in code

    def test_maze_3_door_step_event_compiles(self):
        """Pre-fix: 'pass # TODO: test_instance_count' followed by a
        deeper-indented block — SyntaxError at import of every maze_3
        export."""
        sample = SAMPLES / "maze_3" / "objects" / "obj_door.json"
        if not sample.exists():
            pytest.skip("maze_3 sample not present")
        with open(sample, encoding='utf-8') as f:
            actions = json.load(f)['events']['step']['actions']
        code = _generate_event(actions)
        assert 'count_instances' in code

    def test_unknown_action_after_conditional_stays_valid(self):
        # An unknown simple action consumes the guard slot; following
        # actions land back at event level and everything compiles.
        code = _generate_event([
            {'action': 'test_expression', 'parameters': {'expression': 'True'}},
            {'action': 'some_future_action', 'parameters': {}},
            {'action': 'set_hspeed', 'parameters': {'value': 1}},
        ])
        assert 'TODO: some_future_action' in code

    def test_comment_is_a_statement(self):
        code = _generate_event([
            {'action': 'test_expression', 'parameters': {'expression': 'True'}},
            {'action': 'comment', 'parameters': {'text': 'just a note'}},
        ])
        assert 'just a note' in code  # and the suite compiled (pass-carrying)


class TestKeyboardHandlerSyntax:
    """H8 — _generate_keyboard_handler emitted 'i'/'eli' instead of 'if'/'elif'."""

    def _keyboard_events(self):
        # Non-grid actions so the plain (broken) branch is taken, not the
        # grid-movement handler.
        return [
            {
                'key_name': 'right',
                'actions': [{'action': 'create_instance',
                             'parameters': {'object': 'obj_bullet',
                                            'x': '0', 'y': '0'}}],
            },
            {
                'key_name': 'left',
                'actions': [{'action': 'jump_to_position',
                             'parameters': {'x': '0', 'y': '0'}}],
            },
        ]

    def test_uses_if_and_elif_keywords(self, tmp_path):
        exporter = _make_exporter(tmp_path)
        code = exporter._generate_keyboard_handler(self._keyboard_events())

        assert "if key == 275:" in code  # right
        assert "elif key == 276:" in code  # left
        assert "\n        i key" not in code
        assert "eli key" not in code

    def test_generated_handler_compiles(self, tmp_path):
        exporter = _make_exporter(tmp_path)
        code = exporter._generate_keyboard_handler(self._keyboard_events())
        _compile_method(code)  # raised SyntaxError before the fix

    def test_single_event_compiles(self, tmp_path):
        exporter = _make_exporter(tmp_path)
        code = exporter._generate_keyboard_handler(self._keyboard_events()[:1])
        _compile_method(code)


class TestBackgroundColorAdapter:
    """H9 — the Mobile (Kivy) adapter rewrote background_color to an RGBA
    float list while the exporter expected a hex string; every export
    failed with AttributeError: 'list' object has no attribute 'startswith'.
    """

    def test_bg_color_helper_accepts_both_forms(self):
        from export.Kivy.kivy_exporter import _bg_color_to_rgb

        assert _bg_color_to_rgb('#c0c0c0') == pytest.approx(
            (192 / 255, 192 / 255, 192 / 255))
        assert _bg_color_to_rgb('c0c0c0') == pytest.approx(
            (192 / 255, 192 / 255, 192 / 255))
        assert _bg_color_to_rgb([0.25, 0.5, 0.75, 1.0]) == pytest.approx(
            (0.25, 0.5, 0.75))
        assert _bg_color_to_rgb(None) == (0.5, 0.5, 0.5)
        assert _bg_color_to_rgb('not-a-color') == (0.5, 0.5, 0.5)

    def test_adapter_passes_hex_color_through(self, tmp_path):
        from types import SimpleNamespace
        from export.Kivy.project_adapter import adapt_project_for_kivy_export

        pm = SimpleNamespace(
            current_project_data={
                'name': 'AdapterGame',
                'settings': {},
                'assets': {
                    'sprites': {}, 'sounds': {}, 'backgrounds': {},
                    'objects': {},
                    'rooms': {'room0': {'width': 640, 'height': 480,
                                        'background_color': '#c0c0c0',
                                        'instances': []}},
                },
            },
            project_path=str(tmp_path),
        )
        adapted = adapt_project_for_kivy_export(pm)
        room = adapted['assets']['rooms']['room0']
        assert room['background_color'] == '#c0c0c0'

    def test_export_with_adapter_succeeds(self, tmp_path):
        """End-to-end: the dialog's Mobile (Kivy) path used to always
        return False (AttributeError swallowed by export()'s except)."""
        from types import SimpleNamespace
        from export.Kivy.project_adapter import export_with_adapter

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        output = tmp_path / "out"
        output.mkdir()

        pm = SimpleNamespace(
            current_project_data={
                'name': 'AdapterGame',
                'settings': {'window_width': 800, 'window_height': 600},
                'assets': {
                    'sprites': {}, 'sounds': {}, 'backgrounds': {},
                    'objects': {},
                    'rooms': {'room0': {'width': 640, 'height': 480,
                                        'background_color': '#c0c0c0',
                                        'instances': []}},
                },
            },
            project_path=str(project_dir),
        )

        assert export_with_adapter(pm, output) is True
        main_py = output / "game" / "main.py"
        assert main_py.exists()
        compile(main_py.read_text(encoding='utf-8'), str(main_py), 'exec')

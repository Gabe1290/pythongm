"""Regression tests for Kivy export code-generation bugs.

Registry: docs/FULL_AUDIT_2026-06-11.md (High findings H6-H9).
Each test compiles the generated code — the audit's core failure mode was
exported games that die with SyntaxError/IndentationError at import.
"""

import pytest


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

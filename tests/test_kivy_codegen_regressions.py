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

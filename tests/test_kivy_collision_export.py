"""Regression test for Kivy export collision generation (audit M34).

The Kivy code generator emitted self.check_collision_at(...) for if_collision /
check_collision / check_empty, but no such method existed in the generated
GameObject — every such event raised AttributeError in the exported app. The
generated base object now defines check_collision_at, the generator uses
offset-from-self semantics matching the pygame runtime, and honors not_flag.
"""

from pathlib import Path

import pytest

from export.Kivy.code_generator import ActionCodeGenerator


def _gen(action):
    g = ActionCodeGenerator(base_indent=0)
    g.process_action(action, 'step')
    return g.get_code()


class TestIfCollisionCodegen:
    def test_uses_check_collision_at_with_offsets(self):
        code = _gen({"action": "if_collision",
                     "parameters": {"x": "0", "y": "1", "object": "solid"}})
        assert "check_collision_at(self.x + (0), self.y + (1), 'solid')" in code

    def test_not_flag_inverts(self):
        code = _gen({"action": "if_collision",
                     "parameters": {"x": "0", "y": "1", "object": "solid",
                                    "not_flag": True}})
        assert "if not self.check_collision_at(" in code

    def test_default_offsets_zero(self):
        code = _gen({"action": "if_collision",
                     "parameters": {"object": "obj_wall"}})
        assert "self.x + (0)" in code and "self.y + (0)" in code


def test_base_object_defines_check_collision_at(tmp_path):
    from export.Kivy.kivy_exporter import KivyExporter
    out = tmp_path / "export"
    (out / "game" / "objects").mkdir(parents=True)
    exporter = KivyExporter({"name": "T", "assets": {}}, tmp_path, out)
    exporter._generate_base_object()
    src = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "def check_collision_at(self, x, y, object_name=None):" in src
    # Sanity: the generated base object must still be importable Python.
    compile(src, "base_object.py", "exec")

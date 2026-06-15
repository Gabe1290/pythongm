"""
Regression test for audit M34 (deferred cross-file half).

The Kivy action code generator emits calls to self.check_collision_at(x, y,
'obj_name'), but that method was never defined on the generated GameObject base
class — so every exported game raised AttributeError the first time an
if_collision / check_empty action ran. This pins:

  1. the GameObject base source DEFINES check_collision_at, and
  2. each generated object subclass sets self.object_name (so a named-target
     collision check can match), and
  3. the generated base parses as valid Python and the method is real.

Pure source-level checks: building the generated runtime needs Kivy (Widget),
which isn't a test dependency, so we assert against the generated source the
exporter produces.
"""

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from export.Kivy.kivy_exporter import KivyExporter


@pytest.fixture
def exporter(tmp_path):
    project_data = {
        'name': 'TestGame',
        'settings': {'window_width': 800, 'window_height': 600},
        'assets': {'sprites': {}, 'sounds': {}, 'backgrounds': {},
                   'objects': {}, 'rooms': {}},
    }
    out = tmp_path / "out"
    out.mkdir()
    exp = KivyExporter(project_data, tmp_path, out)
    exp._create_directory_structure()
    return exp


def _objects_dir(exporter):
    return exporter.output_path / "game" / "objects"


def test_base_object_defines_check_collision_at(exporter):
    exporter._generate_base_object()
    src = (_objects_dir(exporter) / "base_object.py").read_text()
    assert "def check_collision_at(self, x, y, object_name=None):" in src
    # The base must parse and actually carry the method (not just a comment).
    tree = ast.parse(src)
    methods = {
        n.name
        for cls in tree.body if isinstance(cls, ast.ClassDef)
        for n in cls.body if isinstance(n, ast.FunctionDef)
    }
    assert "check_collision_at" in methods


def test_object_subclass_sets_object_name(exporter):
    exporter._generate_object("obj_wall", {"solid": True})
    # Find the written subclass file (named after the class).
    srcs = [p.read_text() for p in _objects_dir(exporter).glob("*.py")
            if p.name != "base_object.py"]
    joined = "\n".join(srcs)
    assert 'self.object_name = "obj_wall"' in joined
    for s in srcs:
        ast.parse(s)


def test_generated_call_target_is_defined(exporter):
    """The code generator's emitted call must resolve to a real base method —
    this is the two-halves contract that closes M34."""
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=0)
    g.process_action(
        {"action": "if_collision", "parameters": {"object": "obj_wall"}}, "step"
    )
    call = g.get_code()
    assert "self.check_collision_at(" in call
    exporter._generate_base_object()
    base = (_objects_dir(exporter) / "base_object.py").read_text()
    assert "def check_collision_at(" in base

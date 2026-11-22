"""The events list's second column (the parameter summary) reads in the IDE language
(docs/OPEN_WORK_2026-11-22.md U1).

English keeps the parameter keys exactly as before ("speed=4"); another language shows the
parameter's label and drop-down words in that language, and the fixed words ("with:", "then:")
come from the catalogues. A real offscreen QApplication, no pytest-qt.
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture
def lang():
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from core.language_manager import get_language_manager
    manager = get_language_manager()
    yield manager.set_language
    manager.set_language("en")


def _fmt(action, params):
    from editors.object_editor.object_actions_formatter import ActionParametersFormatter
    return ActionParametersFormatter.format_action_parameters(action, params)


def test_french_shows_labels_and_words(lang):
    lang("fr")
    out = _fmt("set_hspeed", {"speed": 4})
    assert "Vitesse" in out and "speed=" not in out, out
    assert _fmt("if_collision_at", {"object_type": "solid", "x": "0", "y": "0"}).startswith("avec : solide"), \
        _fmt("if_collision_at", {"object_type": "solid", "x": "0", "y": "0"})
    assert "alors : 1, sinon : 0" in _fmt("if_collision_at", {"object_type": "any", "then_actions": [{}]})
    assert _fmt("show_message", {"message": "Hi", "message_translations": {"fr": "Salut"}}).endswith("[1 traduction]")


def test_english_is_byte_identical_to_the_previous_formatter(lang):
    """Every action, with its default parameters, formats exactly as the formatter did before U1."""
    lang("en")
    old_src = subprocess.run(["git", "show", "f01d3d7a:editors/object_editor/object_actions_formatter.py"],
                             cwd=ROOT, capture_output=True, text=True)
    if old_src.returncode != 0:
        pytest.skip("previous version not in this checkout")
    spec = importlib.util.spec_from_loader("old_formatter", loader=None)
    old = importlib.util.module_from_spec(spec)
    exec(old_src.stdout, old.__dict__)
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from events.action_types import ACTION_TYPES
    checked = 0
    for name, action in ACTION_TYPES.items():
        params = {p.name: p.default_value for p in action.parameters}
        assert _fmt(name, params) == old.ActionParametersFormatter.format_action_parameters(name, params), name
        checked += 1
    special = [("if_collision_at", {"object_type": "solid", "x": "self.x + 32", "y": "self.y", "then_actions": [1]}),
               ("if_can_push", {"object_type": "box"}), ("push_object", {"target": "other", "check_collision": False}),
               ("move_to_position", {"x": "1", "y": "2", "smooth": True}),
               ("show_message", {"message": "x", "message_translations": {"fr": "a", "de": "b"}})]
    for name, params in special:
        assert _fmt(name, params) == old.ActionParametersFormatter.format_action_parameters(name, params), name
    assert checked > 100

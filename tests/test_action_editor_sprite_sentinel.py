"""Regression test for the set_sprite '<self>' sentinel (audit M27).

ActionConfigDialog's sprite combo was non-editable and built only from project
sprites, so setCurrentText('<self>') was a no-op and the selection silently
fell to the first project sprite. Merely opening a set_sprite action whose
sprite is '<self>' and clicking OK rewrote it to a concrete sprite. draw_lives'
empty optional sprite had the same defect.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _parent_with_sprites(names):
    from PySide6.QtWidgets import QWidget
    w = QWidget()
    w.current_project_data = {
        "assets": {"sprites": {n: {} for n in names}}
    }
    return w


def _dialog(action_key, initial_params, sprite_names):
    from events.action_editor import ActionConfigDialog
    from events.action_types import ACTION_TYPES
    parent = _parent_with_sprites(sprite_names)
    dlg = ActionConfigDialog(ACTION_TYPES[action_key], initial_params, parent)
    dlg._keepalive_parent = parent  # keep parent alive for the test
    return dlg


def test_set_sprite_self_round_trips(_qapp):
    dlg = _dialog("set_sprite", {"sprite": "<self>"},
                  ["spr_zebra", "spr_apple"])
    assert dlg.get_parameter_values()["sprite"] == "<self>"


def test_new_set_sprite_defaults_to_self(_qapp):
    dlg = _dialog("set_sprite", {}, ["spr_zebra", "spr_apple"])
    assert dlg.get_parameter_values()["sprite"] == "<self>"


def test_set_sprite_concrete_value_preserved(_qapp):
    dlg = _dialog("set_sprite", {"sprite": "spr_apple"},
                  ["spr_zebra", "spr_apple"])
    assert dlg.get_parameter_values()["sprite"] == "spr_apple"


def test_draw_lives_empty_sprite_reachable(_qapp):
    dlg = _dialog("draw_lives", {"sprite": ""}, ["spr_heart"])
    assert dlg.get_parameter_values()["sprite"] == ""

"""Regression test for the multi_choice param widget (GMK-hardening follow-up).

start_moving_direction's `directions` param used to be a plain `string`, so the
events panel edited it through a single-line QLineEdit. A list value (what the
GMK importer emits from GM's 3×3 direction bitmask, e.g. ['down', 'up']) had no
real widget, so it round-tripped as its stringified repr "['down', 'up']" — the
runtime tolerated it only via an explicit ast.literal_eval fallback.

`directions` is now a `multi_choice` param: a 3×3 grid of checkboxes whose value
round-trips as a real Python list of the checked direction names. This test
pins the widget round-trip and the legacy-form parsing that lets old saves
(list, stringified list, comma-separated, single name) still populate it.
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


def _dialog(initial_params):
    from events.action_editor import ActionConfigDialog
    from events.action_types import ACTION_TYPES
    return ActionConfigDialog(ACTION_TYPES["start_moving_direction"],
                              initial_params)


# --- pure parser ----------------------------------------------------------

def test_parse_handles_every_legacy_form():
    from events.action_editor import ActionConfigDialog
    p = ActionConfigDialog._parse_multi_choice
    assert p(["down", "up"]) == ["down", "up"]        # real list (canonical)
    assert p("['down', 'up']") == ["down", "up"]      # legacy stringified repr
    assert p("down, up") == ["down", "up"]            # comma-separated
    assert p("right") == ["right"]                    # single name
    assert p("") == []
    assert p(None) == []
    assert p([]) == []


# --- widget round-trip ----------------------------------------------------

def test_param_is_multi_choice_with_grid_order():
    from events.action_types import ACTION_TYPES
    param = next(p for p in ACTION_TYPES["start_moving_direction"].parameters
                 if p.name == "directions")
    assert param.param_type == "multi_choice"
    # GM 3×3 reading order (top row = up), so a 3-column grid reproduces the
    # familiar direction picker.
    assert param.choices == ["up-left", "up", "up-right",
                             "left", "stop", "right",
                             "down-left", "down", "down-right"]


def test_real_list_round_trips(_qapp):
    dlg = _dialog({"directions": ["down", "up"]})
    out = dlg.get_parameter_values()["directions"]
    assert isinstance(out, list)
    assert set(out) == {"down", "up"}


def test_stringified_legacy_value_is_recovered(_qapp):
    # An old save whose directions round-tripped through a QLineEdit.
    dlg = _dialog({"directions": "['down', 'up']"})
    out = dlg.get_parameter_values()["directions"]
    assert isinstance(out, list)
    assert set(out) == {"down", "up"}


def test_single_name_value_preserved(_qapp):
    dlg = _dialog({"directions": "right"})
    assert dlg.get_parameter_values()["directions"] == ["right"]


def test_new_action_uses_list_default(_qapp):
    dlg = _dialog({})
    assert dlg.get_parameter_values()["directions"] == ["right"]


def test_checking_a_box_updates_the_value(_qapp):
    dlg = _dialog({"directions": ["right"]})
    boxes = dict(dlg.param_widgets["directions"]._choice_boxes)
    boxes["up"].setChecked(True)          # add "up" to the existing "right"
    out = dlg.get_parameter_values()["directions"]
    assert set(out) == {"right", "up"}
    boxes["right"].setChecked(False)      # now clear "right"
    assert dlg.get_parameter_values()["directions"] == ["up"]

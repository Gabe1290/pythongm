"""L13, docs/FULL_AUDIT_2026-09-07.md: sound combo saves the placeholder
as a value.

ActionConfigDialog's sound combo, on a project with no sound assets,
added ONLY the translated "(No sounds available)" placeholder text as
a combo item -- unlike the sprite combo just above it, which always
adds a real "" sentinel item so an empty selection round-trips as an
empty string. get_parameter_values() reads any QComboBox via
widget.currentText() with no per-param-type check, so simply opening a
sound-typed action's config dialog on a project with no sounds and
clicking OK saved the literal string "(No sounds available)" as the
action's `sound` parameter.
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


def _parent_with_sounds(names):
    from PySide6.QtWidgets import QWidget
    w = QWidget()
    w.current_project_data = {
        "assets": {"sounds": {n: {} for n in names}}
    }
    return w


def _dialog(action_key, initial_params, sound_names):
    from events.action_editor import ActionConfigDialog
    from events.action_types import ACTION_TYPES
    parent = _parent_with_sounds(sound_names)
    dlg = ActionConfigDialog(ACTION_TYPES[action_key], initial_params, parent)
    dlg._keepalive_parent = parent  # keep parent alive for the test
    return dlg


def test_no_sounds_in_project_saves_empty_string_not_the_placeholder(_qapp):
    dlg = _dialog("check_sound", {}, [])
    assert dlg.get_parameter_values()["sound"] == ""


def test_no_sounds_in_project_with_existing_empty_value_stays_empty(_qapp):
    dlg = _dialog("check_sound", {"sound": ""}, [])
    assert dlg.get_parameter_values()["sound"] == ""


def test_sound_still_populated_normally_when_project_has_sounds(_qapp):
    dlg = _dialog("check_sound", {"sound": "snd_coin"}, ["snd_coin", "snd_jump"])
    assert dlg.get_parameter_values()["sound"] == "snd_coin"

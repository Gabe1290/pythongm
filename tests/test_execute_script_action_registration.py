"""execute_script registered as a structured action (treasure playtest finding #1).

GMK imports emit `execute_script` for GM's "execute script" action — treasure's
monster calls its adapt_direction project script from step/collision events, and
the runtime executes it (execute_execute_script_action). But the action had no
entry in events/action_types.py, so the object editor's events panel logged
"Unknown action type: execute_script" and refused to open the editor dialog:
double-clicking the action did nothing. This registers it (with a new "script"
param type: an editable combo of the project's script assets) and pins:
 - the registration matches the runtime handler's parameter reads
   (script + arg0..arg4),
 - the dialog opens for the exact action data treasure imports, and
 - the saved script name round-trips through the dialog.

Dialog tests use a hand-rolled offscreen QApplication (no pytest-qt needed),
mirroring tests/test_room_canvas_cache_clear.py.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from events.action_types import get_action_type  # noqa: E402


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_execute_script_registered():
    at = get_action_type("execute_script")
    assert at is not None
    assert at.category == "Control"
    names = [p.name for p in at.parameters]
    # exactly the parameters the runtime handler reads
    assert names == ["script", "arg0", "arg1", "arg2", "arg3", "arg4"]
    script = at.parameters[0]
    assert script.param_type == "script"
    for arg in at.parameters[1:]:
        assert arg.required is False


def test_registration_backed_by_runtime_handler():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    assert callable(getattr(ex, "execute_execute_script_action", None))


def test_dialog_opens_for_treasure_style_action(_qapp):
    """The exact shape treasure imports: {'script': 'adapt_direction'} —
    previously the panel's get_action_type() returned None and edit_action
    bailed with 'Unknown action type'."""
    from events.conditional_editor import create_action_dialog
    at = get_action_type("execute_script")
    dlg = create_action_dialog(at, {"script": "adapt_direction"})
    # Saved name shows even with no project context (editable combo keeps it
    # instead of snapping to a nonexistent list item).
    values = dlg.get_parameter_values()
    assert values["script"] == "adapt_direction"


def test_dialog_round_trips_arguments(_qapp):
    from events.conditional_editor import create_action_dialog
    at = get_action_type("execute_script")
    dlg = create_action_dialog(at, {"script": "my_script", "arg0": "5", "arg1": "player"})
    values = dlg.get_parameter_values()
    assert values["script"] == "my_script"
    assert values["arg0"] == "5"
    assert values["arg1"] == "player"

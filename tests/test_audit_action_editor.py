"""
Regression tests for events/action_editor.py audit findings M27, M28, L18, L19.

- M27: the sprite combo must offer (and round-trip) the "<self>" sentinel for
  set_sprite and the empty/"no sprite" sentinel for optional sprite params,
  instead of silently snapping to the first project sprite on OK.
- M28: the room dropdown must offer ONLY real room names — the old
  navigation entries saved sentinels ('__next__'/'__prev__'/'__current__')
  that the pygame runtime never consumed (silent no-ops).
- L18: check_empty's "objects" choice param must offer ONLY its declared
  choices ("solid"/"all"), not every project object name (the runtime
  collapses anything != "solid" to "all").
- L19: MultiActionEditor.refresh_display must render one tree row per
  action_list entry — including unknown action types — so Remove / Move
  index correctly into the underlying list.

Constructs a real (offscreen) QApplication rather than pytest-qt, so it runs
on Python 3.11 too.
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


def _make_parent(project_data):
    """A minimal QWidget exposing current_project_data for the parent walk."""
    from PySide6.QtWidgets import QWidget
    w = QWidget()
    w.current_project_data = project_data
    return w


_PROJECT = {
    "assets": {
        "sprites": {"spr_alpha": {}, "spr_beta": {}},
        "objects": {"obj_player": {}, "obj_box": {}, "obj_enemy": {}},
        "rooms": {"room_intro": {}, "room_level1": {}},
    }
}


# ---------------------------------------------------------------------------
# M27 — sprite sentinel round-trip
# ---------------------------------------------------------------------------

def test_set_sprite_self_sentinel_roundtrips(_qapp):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("set_sprite")
    assert at is not None

    # Open an existing set_sprite action whose sprite is the "<self>" sentinel.
    dlg = ActionConfigDialog(at, {"sprite": "<self>", "subimage": 0}, parent=parent)
    combo = dlg.param_widgets["sprite"]

    # The sentinel must be present and currently selected — NOT snapped to the
    # first project sprite.
    items = [combo.itemText(i) for i in range(combo.count())]
    assert "<self>" in items
    assert combo.currentText() == "<self>"

    # Clicking OK must preserve "<self>" rather than rewriting it to a sprite.
    values = dlg.get_parameter_values()
    assert values["sprite"] == "<self>"

    parent.deleteLater()


def test_set_sprite_default_is_self_not_first_sprite(_qapp):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("set_sprite")

    # A brand-new set_sprite action (no initial params) defaults to "<self>".
    dlg = ActionConfigDialog(at, {}, parent=parent)
    values = dlg.get_parameter_values()
    assert values["sprite"] == "<self>"

    parent.deleteLater()


def test_draw_lives_empty_sprite_roundtrips(_qapp):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("draw_lives")
    assert at is not None

    # draw_lives' sprite param is optional (default "") — an empty selection
    # must be reachable and round-trip as "".
    dlg = ActionConfigDialog(at, {"x": 0, "y": 0, "sprite": ""}, parent=parent)
    values = dlg.get_parameter_values()
    assert values["sprite"] == ""

    parent.deleteLater()


def test_set_sprite_concrete_sprite_still_works(_qapp):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("set_sprite")

    dlg = ActionConfigDialog(at, {"sprite": "spr_beta"}, parent=parent)
    assert dlg.param_widgets["sprite"].currentText() == "spr_beta"
    assert dlg.get_parameter_values()["sprite"] == "spr_beta"

    parent.deleteLater()


# ---------------------------------------------------------------------------
# M28 — room dropdown offers only real rooms (no dead navigation sentinels)
# ---------------------------------------------------------------------------

def test_room_dropdown_has_no_navigation_sentinels(_qapp):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("goto_room")
    assert at is not None

    dlg = ActionConfigDialog(at, {}, parent=parent)
    combo = dlg.param_widgets["room"]
    items = [combo.itemText(i) for i in range(combo.count())]

    # No navigation labels, and selecting any option can never produce a dead
    # sentinel that the runtime ignores.
    assert "→ Next Room" not in items
    assert "← Previous Room" not in items
    assert "↺ Restart Current Room" not in items
    assert "room_intro" in items and "room_level1" in items

    # Walk every selectable room and confirm none save a sentinel.
    for i in range(combo.count()):
        combo.setCurrentIndex(i)
        saved = dlg.get_parameter_values()["room"]
        assert saved not in ("__next__", "__prev__", "__current__")

    parent.deleteLater()


# ---------------------------------------------------------------------------
# L18 — check_empty objects offers only its declared choices
# ---------------------------------------------------------------------------

def test_check_empty_objects_offers_only_choices(_qapp):
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("check_empty")
    assert at is not None

    dlg = ActionConfigDialog(at, {}, parent=parent)
    combo = dlg.param_widgets["objects"]
    items = [combo.itemText(i) for i in range(combo.count())]

    assert items == ["solid", "all"]
    # Project object names must NOT leak into this dropdown.
    assert "obj_player" not in items
    assert "obj_box" not in items

    parent.deleteLater()


def test_move_to_contact_object_still_lists_objects(_qapp):
    # Sanity: a genuine object-reference param (param_type == "object") still
    # gets the project object list plus its built-in selectors.
    from events.action_editor import ActionConfigDialog
    from events.action_types import get_action_type

    parent = _make_parent(_PROJECT)
    at = get_action_type("move_to_contact")
    assert at is not None

    dlg = ActionConfigDialog(at, {}, parent=parent)
    combo = dlg.param_widgets["object"]
    items = [combo.itemText(i) for i in range(combo.count())]
    assert "obj_player" in items
    assert "all" in items  # built-in choice selector still present

    parent.deleteLater()


# ---------------------------------------------------------------------------
# L19 — unknown actions stay aligned with the underlying list
# ---------------------------------------------------------------------------

def test_multi_action_editor_keeps_unknown_actions_aligned(_qapp):
    from events.action_editor import MultiActionEditor

    action_list = [
        {"action": "totally_unknown_action", "parameters": {"foo": 1}},
        {"action": "set_score", "parameters": {"value": 10}},
        {"action": "another_unknown", "parameters": {}},
    ]
    ed = MultiActionEditor(action_list)

    # One tree row per list entry — unknowns included.
    assert ed.action_tree.topLevelItemCount() == len(action_list)

    # Selecting the middle (known) row and removing it must drop exactly that
    # entry, not an off-by-one neighbour.
    ed.action_tree.setCurrentItem(ed.action_tree.topLevelItem(1))
    ed.remove_action()

    remaining = [a["action"] for a in ed.get_action_list()]
    assert remaining == ["totally_unknown_action", "another_unknown"]

    ed.deleteLater()


def test_multi_action_editor_move_with_unknown_actions(_qapp):
    from events.action_editor import MultiActionEditor

    action_list = [
        {"action": "unknown_one", "parameters": {}},
        {"action": "set_score", "parameters": {"value": 5}},
    ]
    ed = MultiActionEditor(action_list)

    # Move the second (known) row up; it must swap with the unknown row, not
    # silently no-op or corrupt the order.
    ed.action_tree.setCurrentItem(ed.action_tree.topLevelItem(1))
    ed.move_up()

    order = [a["action"] for a in ed.get_action_list()]
    assert order == ["set_score", "unknown_one"]

    ed.deleteLater()

"""
Regression test: right-click Copy/Paste of an action in the object editor's
events panel.

Covers the data-model side of the feature added to ObjectEventsPanel:
- copy_action stashes a deep copy on the shared clipboard,
- paste_action_after inserts a copy immediately after the selected action,
- paste_action_append drops a copy at the end of an event's action list,
- the clipboard is shared across panels (cross-object paste), and
- pastes are deep copies (mutating one action never touches its twin).

Constructs a real (offscreen) QApplication rather than using pytest-qt, so it
runs anywhere PySide6 is installed.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _events():
    """A small project: two leaf events plus a keyboard sub-event."""
    return {
        "create": {"actions": [
            {"action": "set_gravity", "parameters": {"gravity": "0.5", "direction": "270"}},
        ]},
        "step": {"actions": [
            {"action": "move_stop", "parameters": {}},
        ]},
        "keyboard": {
            "left": {"actions": [
                {"action": "move_set_hspeed", "parameters": {"hspeed": "-4"}},
            ]},
        },
    }


def _make_panel(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    panel = ObjectEventsPanel()
    panel.load_events_data(_events())
    return panel


def _top_item(panel, event_name):
    tree = panel.events_tree
    for i in range(tree.topLevelItemCount()):
        from PySide6.QtCore import Qt
        item = tree.topLevelItem(i)
        if item.data(0, Qt.UserRole) == event_name:
            return item
    raise AssertionError(f"event node not found: {event_name}")


def test_copy_then_paste_after_inserts_duplicate(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None  # isolate from other tests

    panel = _make_panel(_qapp)
    create_item = _top_item(panel, "create")
    action_item = create_item.child(0)

    panel.copy_action(action_item)
    assert isinstance(ObjectEventsPanel._action_clipboard, list)
    assert [a["action"] for a in ObjectEventsPanel._action_clipboard] == ["set_gravity"]

    panel.paste_action_after(action_item)
    actions = panel.current_events_data["create"]["actions"]
    assert len(actions) == 2
    assert actions[0]["action"] == "set_gravity"
    assert actions[1]["action"] == "set_gravity"
    # Inserted directly after the source, and is a distinct object.
    assert actions[0] is not actions[1]


def test_paste_append_targets_end_of_event(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    panel.copy_action(_top_item(panel, "create").child(0))

    # Append the copied create-action onto the (unrelated) step event.
    panel.paste_action_append(_top_item(panel, "step"))
    step_actions = panel.current_events_data["step"]["actions"]
    assert [a["action"] for a in step_actions] == ["move_stop", "set_gravity"]


def test_paste_into_keyboard_sub_event(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    from PySide6.QtCore import Qt
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    panel.copy_action(_top_item(panel, "create").child(0))

    keyboard_item = _top_item(panel, "keyboard")
    # Find the "left" sub-event node.
    sub_item = None
    for i in range(keyboard_item.childCount()):
        child = keyboard_item.child(i)
        if child.data(0, Qt.UserRole) == "keyboard_left":
            sub_item = child
            break
    assert sub_item is not None

    panel.paste_action_append(sub_item)
    sub_actions = panel.current_events_data["keyboard"]["left"]["actions"]
    assert [a["action"] for a in sub_actions] == ["move_set_hspeed", "set_gravity"]


def test_clipboard_is_shared_across_panels(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    source = _make_panel(_qapp)
    source.copy_action(_top_item(source, "create").child(0))

    # A separate panel (think: a different object's editor) sees the clipboard.
    dest = _make_panel(_qapp)
    dest.paste_action_append(_top_item(dest, "step"))
    assert [a["action"] for a in dest.current_events_data["step"]["actions"]] == \
        ["move_stop", "set_gravity"]


def test_paste_is_deep_copy(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    panel.copy_action(_top_item(panel, "create").child(0))
    panel.paste_action_after(_top_item(panel, "create").child(0))

    actions = panel.current_events_data["create"]["actions"]
    # Mutate the original's parameters; the pasted twin must be unaffected.
    actions[0]["parameters"]["gravity"] = "99"
    assert actions[1]["parameters"]["gravity"] == "0.5"
    # And neither aliases the clipboard entry.
    ObjectEventsPanel._action_clipboard[0]["parameters"]["gravity"] = "-1"
    assert actions[1]["parameters"]["gravity"] == "0.5"


def test_shortcut_handlers_copy_and_paste_after(_qapp):
    """Ctrl+C then Ctrl+V on a selected action inserts after it."""
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    action_item = _top_item(panel, "create").child(0)
    panel.events_tree.setCurrentItem(action_item)

    panel.copy_selected_action()
    assert [a["action"] for a in ObjectEventsPanel._action_clipboard] == ["set_gravity"]

    # Re-resolve selection (still the same action) and paste.
    panel.events_tree.setCurrentItem(_top_item(panel, "create").child(0))
    panel.paste_selected_action()
    assert [a["action"] for a in panel.current_events_data["create"]["actions"]] == \
        ["set_gravity", "set_gravity"]


def test_shortcut_paste_on_event_node_appends(_qapp):
    """Ctrl+V with an event node selected appends to that event."""
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    panel.copy_action(_top_item(panel, "create").child(0))

    panel.events_tree.setCurrentItem(_top_item(panel, "step"))
    panel.paste_selected_action()
    assert [a["action"] for a in panel.current_events_data["step"]["actions"]] == \
        ["move_stop", "set_gravity"]


def test_shortcut_copy_ignores_non_action_selection(_qapp):
    """Ctrl+C on an event node (not an action) leaves the clipboard untouched."""
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    panel.events_tree.setCurrentItem(_top_item(panel, "create"))
    panel.copy_selected_action()
    assert ObjectEventsPanel._action_clipboard is None


def _multi_events():
    """A 'step' event holding two actions, for multi-select tests."""
    return {
        "create": {"actions": [
            {"action": "set_gravity", "parameters": {"gravity": "0.5"}},
        ]},
        "step": {"actions": [
            {"action": "move_stop", "parameters": {}},
            {"action": "move_set_hspeed", "parameters": {"hspeed": "3"}},
        ]},
    }


def _load(_qapp, data):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    panel = ObjectEventsPanel()
    panel.load_events_data(data)
    return panel


def test_copy_multiple_selected_actions(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _load(_qapp, _multi_events())
    step = _top_item(panel, "step")
    step.child(0).setSelected(True)
    step.child(1).setSelected(True)

    panel.copy_selected_action()
    assert [a["action"] for a in ObjectEventsPanel._action_clipboard] == \
        ["move_stop", "move_set_hspeed"]

    # Append both onto create, preserving order.
    panel.paste_action_append(_top_item(panel, "create"))
    assert [a["action"] for a in panel.current_events_data["create"]["actions"]] == \
        ["set_gravity", "move_stop", "move_set_hspeed"]


def test_paste_block_inserts_after_target_in_order(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _load(_qapp, _multi_events())
    step = _top_item(panel, "step")
    step.child(0).setSelected(True)
    step.child(1).setSelected(True)
    panel.copy_selected_action()

    # Paste the 2-action block right after create's single action.
    panel.paste_action_after(_top_item(panel, "create").child(0))
    assert [a["action"] for a in panel.current_events_data["create"]["actions"]] == \
        ["set_gravity", "move_stop", "move_set_hspeed"]


def test_selection_copied_in_visual_order_regardless_of_click_order(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _load(_qapp, _multi_events())
    step = _top_item(panel, "step")
    # Select bottom first, then top — visual order must still win.
    step.child(1).setSelected(True)
    step.child(0).setSelected(True)

    panel.copy_selected_action()
    assert [a["action"] for a in ObjectEventsPanel._action_clipboard] == \
        ["move_stop", "move_set_hspeed"]


def test_copy_action_within_selection_copies_whole_selection(_qapp):
    """Right-clicking one action of a multi-selection copies them all."""
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _load(_qapp, _multi_events())
    step = _top_item(panel, "step")
    step.child(0).setSelected(True)
    step.child(1).setSelected(True)

    # Context-menu copy invoked on the first selected action.
    panel.copy_action(step.child(0))
    assert [a["action"] for a in ObjectEventsPanel._action_clipboard] == \
        ["move_stop", "move_set_hspeed"]


def test_copy_action_outside_selection_copies_only_clicked(_qapp):
    """Right-clicking an unselected action copies just that one."""
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _load(_qapp, _multi_events())
    step = _top_item(panel, "step")
    step.child(1).setSelected(True)  # selection is the second action

    panel.copy_action(step.child(0))  # but we right-clicked the first
    assert [a["action"] for a in ObjectEventsPanel._action_clipboard] == ["move_stop"]


def test_paste_without_clipboard_is_noop(_qapp):
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    ObjectEventsPanel._action_clipboard = None

    panel = _make_panel(_qapp)
    before = [a["action"] for a in panel.current_events_data["create"]["actions"]]
    panel.paste_action_after(_top_item(panel, "create").child(0))
    panel.paste_action_append(_top_item(panel, "step"))
    after_create = [a["action"] for a in panel.current_events_data["create"]["actions"]]
    after_step = [a["action"] for a in panel.current_events_data["step"]["actions"]]
    assert after_create == before
    assert after_step == ["move_stop"]

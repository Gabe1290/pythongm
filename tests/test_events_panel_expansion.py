"""
Regression test: ObjectEventsPanel preserves the expanded/collapsed state of
its event tree across a refresh.

Bug: every time an action was added or modified, refresh_events_display() rebuilt
the tree and called collapseAll() unconditionally, collapsing whatever event the
user had open and forcing them to re-expand it before they could keep editing.
The fix captures the set of expanded items (by their stable Qt.UserRole key)
before clear() and restores that expansion after the rebuild.

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


def _make_panel():
    from editors.object_editor.object_events_panel import ObjectEventsPanel
    panel = ObjectEventsPanel()
    return panel


def _find_top_item(panel, event_name):
    from PySide6.QtCore import Qt
    tree = panel.events_tree
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        if item.data(0, Qt.UserRole) == event_name:
            return item
    return None


def test_expanded_event_stays_expanded_after_refresh(_qapp):
    panel = _make_panel()
    panel.current_events_data = {
        "create": {"actions": [{"action_type": "move_fixed", "params": {}}]},
    }
    panel.refresh_events_display()

    item = _find_top_item(panel, "create")
    assert item is not None
    # User expands the event to see/edit its actions.
    item.setExpanded(True)

    # Simulate adding another action, which triggers a full rebuild.
    panel.current_events_data["create"]["actions"].append(
        {"action_type": "move_fixed", "params": {}}
    )
    panel.refresh_events_display()

    item = _find_top_item(panel, "create")
    assert item is not None
    assert item.isExpanded(), "event collapsed after refresh — regression in expansion-state preservation"


def test_collapsed_event_stays_collapsed_after_refresh(_qapp):
    panel = _make_panel()
    panel.current_events_data = {
        "create": {"actions": [{"action_type": "move_fixed", "params": {}}]},
        "step": {"actions": [{"action_type": "move_fixed", "params": {}}]},
    }
    panel.refresh_events_display()

    # Expand only 'create'; leave 'step' collapsed.
    _find_top_item(panel, "create").setExpanded(True)

    panel.refresh_events_display()

    assert _find_top_item(panel, "create").isExpanded()
    assert not _find_top_item(panel, "step").isExpanded()


def test_expanded_keyboard_subevent_stays_expanded(_qapp):
    """Nested sub-event nodes (keyboard keys) also keep their expansion state."""
    from PySide6.QtCore import Qt
    panel = _make_panel()
    panel.current_events_data = {
        "keyboard": {
            "left": {"actions": [{"action_type": "move_fixed", "params": {}}]},
        },
    }
    panel.refresh_events_display()

    kb_item = _find_top_item(panel, "keyboard")
    assert kb_item is not None
    kb_item.setExpanded(True)
    sub_item = kb_item.child(0)
    assert sub_item.data(0, Qt.UserRole) == "keyboard_left"
    sub_item.setExpanded(True)

    panel.refresh_events_display()

    kb_item = _find_top_item(panel, "keyboard")
    assert kb_item.isExpanded()
    assert kb_item.child(0).isExpanded(), "keyboard sub-event collapsed after refresh"

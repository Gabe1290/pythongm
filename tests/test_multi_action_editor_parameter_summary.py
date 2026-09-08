"""L18, docs/FULL_AUDIT_2026-09-07.md: MultiActionEditor parameter summary
leaks nested action lists into the tree text.

MultiActionEditor.refresh_display (the Then/Else branch editor) built its
per-row parameter-column text with a naive `", ".join(f"{k}={v}" ...)`
over every parameter, including then_actions/else_actions -- whole
nested action lists rendered as raw dict reprs, truncated at 50
characters, making a nested conditional inside a Then/Else branch
unreadable. Fix: route through ActionParametersFormatter, the same
formatter the main object-editor events panel
(editors/object_editor/events/_render.py) already uses, whose default
fallback explicitly skips then_actions/else_actions/
then_action_params/else_action_params rather than stringifying them.
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


def test_nested_then_else_actions_do_not_leak_into_the_summary(_qapp):
    """Deliberately short/minimal params: the old naive join truncated at
    50 characters, so with anything longer ahead of them the nested lists
    fell outside the truncation window and the bug wouldn't reproduce --
    this keeps then_actions/else_actions the first thing the (pre-fix)
    join would emit, so the test genuinely exercises the leak."""
    from events.action_editor import MultiActionEditor

    action_list = [
        {"action": "if_collision_at", "parameters": {
            "then_actions": [{"action": "set_health", "parameters": {"value": 100}}],
            "else_actions": [{"action": "destroy_instance", "parameters": {}}],
        }},
    ]
    ed = MultiActionEditor(action_list)

    row_text = ed.action_tree.topLevelItem(0).text(1)

    # The exact bug: a raw dict repr of the nested action list (its own
    # 'action'/'parameters' keys, or the literal Python list/dict
    # punctuation) must not appear in the summary column at all.
    assert "set_health" not in row_text
    assert "destroy_instance" not in row_text
    assert "{'action'" not in row_text
    assert "[{" not in row_text

    ed.deleteLater()


def test_generic_action_with_then_actions_is_still_summarized_cleanly(_qapp):
    """An action type with no special-cased formatter branch (the default
    fallback) must also skip then_actions/else_actions rather than
    stringifying them, matching ActionParametersFormatter's own contract."""
    from events.action_editor import MultiActionEditor

    action_list = [
        {"action": "some_unspecialized_conditional", "parameters": {
            "check": "true",
            "then_actions": [{"action": "set_score", "parameters": {"value": 1}}],
            "else_actions": [],
        }},
    ]
    ed = MultiActionEditor(action_list)

    row_text = ed.action_tree.topLevelItem(0).text(1)

    assert "set_score" not in row_text
    assert "then_actions" not in row_text
    assert "check=true" in row_text

    ed.deleteLater()


def test_ordinary_action_summary_still_shows_its_parameters(_qapp):
    """The fix must not silently blank the summary column for a normal
    action -- only nested action lists are the thing being hidden."""
    from events.action_editor import MultiActionEditor

    action_list = [
        {"action": "set_score", "parameters": {"value": 42}},
    ]
    ed = MultiActionEditor(action_list)

    row_text = ed.action_tree.topLevelItem(0).text(1)
    assert "42" in row_text

    ed.deleteLater()

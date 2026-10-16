"""docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 1: the "junior" edition hides
the Object Editor's "Event List" and "Code Editor" tabs entirely, leaving
Blockly as the only authoring surface a young student sees -- every other
edition is unaffected, and the underlying widgets/data model must still
exist (removeTab() only detaches a tab from the bar, it doesn't destroy
the widget) so a project with custom code still loads and runs correctly
even though the tab to edit it isn't shown in this tier.
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


@pytest.fixture
def _edition(request):
    """Pin Config's "edition" key for the test, then restore it -- the
    real end-to-end path (Config -> get_current_edition -> the Object
    Editor), not a mocked function, since that's the actual plumbing
    being tested."""
    from utils.config import Config
    original = Config.get("edition", None)
    Config.set("edition", request.param)
    yield request.param
    Config.set("edition", original)


def _tab_titles(editor):
    tabs = editor.center_tabs
    return [tabs.tabText(i) for i in range(tabs.count())]


@pytest.mark.parametrize("_edition", ["junior"], indirect=True)
def test_junior_edition_hides_event_list_and_code_editor(_qapp, _edition):
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    titles = _tab_titles(editor)
    assert not any("Event List" in t for t in titles), titles
    assert not any("Code Editor" in t for t in titles), titles
    assert any("Blockly" in t for t in titles), titles


@pytest.mark.parametrize("_edition", ["beginner", "advanced", "development"], indirect=True)
def test_other_editions_keep_all_three_tabs(_qapp, _edition):
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    titles = _tab_titles(editor)
    assert any("Event List" in t for t in titles), titles
    assert any("Code Editor" in t for t in titles), titles
    assert any("Blockly" in t for t in titles), titles


@pytest.mark.parametrize("_edition", ["junior"], indirect=True)
def test_junior_edition_still_builds_the_hidden_tabs_data_model(_qapp, _edition):
    """Hiding the tabs must not remove the underlying widgets/data a saved
    project's custom code still depends on -- only remove them from the
    visible tab bar."""
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    assert hasattr(editor, "code_editor")
    assert hasattr(editor, "custom_code_by_event")
    assert hasattr(editor, "actions_widget")
    assert hasattr(editor, "code_tab_index")
    assert hasattr(editor, "_event_list_tab_index")
    # Confirmed detached, not merely absent: the widget is still a real
    # child, just not inside the tab bar's current index range.
    assert editor.center_tabs.indexOf(editor.code_editor.parentWidget()) == -1


@pytest.mark.parametrize("_edition", ["junior"], indirect=True)
def test_junior_blockly_tab_actually_initialises(_qapp, _edition):
    """With the other tabs removed, Blockly is already current, so the
    lazy initialiser used to never run and the tab stayed an empty
    placeholder (reported from a real junior session)."""
    from PySide6.QtCore import QCoreApplication
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    QCoreApplication.processEvents()
    assert editor._blockly_initialized
    assert editor.center_tabs.count() == 1
    assert editor.center_tabs.widget(0) is editor.blockly_tab
    assert editor.center_tabs.widget(0) is not editor._blockly_placeholder

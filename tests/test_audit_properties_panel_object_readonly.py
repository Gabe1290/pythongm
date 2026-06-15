"""
Regression test for M61: object property edits in the properties panel were
silently discarded when no object editor was open, while the sprite preview
updated as if they worked.

Fix: when there is no current_object_editor (a single click in the asset tree,
no editor tab open), show_object_properties renders read-only rows (the same
style used for rooms/sprites) instead of editable controls wired to a dead
handler. When an object editor IS in context, the controls remain live-editable.

Constructs a real offscreen QApplication rather than using pytest-qt, so it
runs on Python 3.11 too.
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


OBJ = {
    'name': 'obj_coin',
    'sprite': '',
    'visible': True,
    'solid': False,
    'persistent': False,
    'events': {},
}


def _editable_widgets(panel):
    """Collect any live editable controls the panel attached as attributes."""
    found = []
    for attr in ('sprite_combo', 'visible_check', 'solid_check', 'persistent_check'):
        w = getattr(panel, attr, None)
        if w is not None:
            found.append(attr)
    return found


def test_no_editor_context_renders_readonly_rows(_qapp):
    from widgets.enhanced_properties_panel import EnhancedPropertiesPanel
    from PySide6.QtWidgets import QComboBox, QCheckBox

    panel = EnhancedPropertiesPanel()
    assert panel.current_object_editor is None

    # Tree single-click path: object asset, no editor open.
    panel.show_asset_properties('objects', 'obj_coin', dict(OBJ))

    # No live editable controls should be attached / wired.
    assert _editable_widgets(panel) == [], (
        "read-only object view must not expose editable controls that drop edits"
    )

    # And the form must contain no editable combo/checkbox widgets at all.
    layout = panel.properties_layout
    editable = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        w = item.widget() if item is not None else None
        if isinstance(w, (QComboBox, QCheckBox)):
            editable.append(w)
    assert editable == [], "object rows must be read-only labels, not editable controls"


def test_editor_context_keeps_editable_controls(_qapp):
    from widgets.enhanced_properties_panel import EnhancedPropertiesPanel
    from PySide6.QtWidgets import QComboBox

    panel = EnhancedPropertiesPanel()

    class FakeEditor:
        def __init__(self):
            self.updates = []

        def update_object_property_from_ide(self, name, value):
            self.updates.append((name, value))

    editor = FakeEditor()
    panel.set_object_editor_context(editor, 'obj_coin', dict(OBJ))

    # Editor context: the live sprite combo must exist (editable path preserved).
    assert isinstance(getattr(panel, 'sprite_combo', None), QComboBox)

    # A property change forwards to the editor (the live write path).
    panel._updating_properties = False
    panel.on_object_property_changed('solid', True)
    assert ('solid', True) in editor.updates


def test_readonly_path_does_not_forward_or_crash(_qapp):
    """With no editor, on_object_property_changed must not raise and there is
    nowhere to forward to (no current_object_editor)."""
    from widgets.enhanced_properties_panel import EnhancedPropertiesPanel

    panel = EnhancedPropertiesPanel()
    panel.show_asset_properties('objects', 'obj_coin', dict(OBJ))

    panel._updating_properties = False
    # Must be a no-op write-wise (no editor) and must not raise.
    panel.on_object_property_changed('sprite', 'spr_coin')
    assert panel.current_object_editor is None

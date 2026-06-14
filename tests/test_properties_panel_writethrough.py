"""Regression test for property-panel object edits with no editor open (M61).

Clicking an object in the asset tree (no editor open) showed editable
Visible/Solid/Persistent controls, but on_object_property_changed only
forwarded to current_object_editor (None in that path) — the edit went nowhere
while the preview confirmed it. The handler now writes through to the live
project model and marks dirty.
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


def _panel_with_object(_qapp, obj_data):
    from PySide6.QtWidgets import QWidget
    from widgets.enhanced_properties_panel import EnhancedPropertiesPanel

    class _AssetManager:
        def __init__(self, objects):
            self._objects = objects

        def get_asset(self, asset_type, name):
            return self._objects.get(name)

    class _ProjectManager:
        def __init__(self, objects):
            self.current_project_data = {"assets": {"objects": objects}}
            self.asset_manager = _AssetManager(objects)
            self.dirty = False

        def mark_dirty(self):
            self.dirty = True

    objects = {"obj_coin": obj_data}
    parent = QWidget()
    parent.project_manager = _ProjectManager(objects)

    panel = EnhancedPropertiesPanel()
    panel.setParent(parent)
    panel.current_object_editor = None
    panel.current_asset = ('object_editor', 'obj_coin', obj_data)
    return panel, parent, parent.project_manager, objects


def test_solid_edit_persists_without_editor(_qapp):
    panel, parent, pm, objects = _panel_with_object(_qapp, {"name": "obj_coin", "solid": False})
    panel.on_object_property_changed('solid', True)
    assert objects["obj_coin"]["solid"] is True
    assert pm.dirty is True


def test_persistent_edit_persists_without_editor(_qapp):
    panel, parent, pm, objects = _panel_with_object(_qapp, {"name": "obj_coin"})
    panel.on_object_property_changed('persistent', True)
    assert objects["obj_coin"]["persistent"] is True
    assert pm.dirty is True


def test_sprite_edit_persists_without_editor(_qapp):
    panel, parent, pm, objects = _panel_with_object(_qapp, {"name": "obj_coin", "sprite": ""})
    # Avoid heavy preview work; we only assert the write-through.
    panel.show_object_preview = lambda data: None
    panel.on_object_property_changed('sprite', 'spr_coin')
    assert objects["obj_coin"]["sprite"] == 'spr_coin'
    assert pm.dirty is True

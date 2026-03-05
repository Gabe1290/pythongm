#!/usr/bin/env python3
"""
Object Properties Panel
Manages object properties: visible, persistent, solid, sprite
"""

from typing import Dict, Any
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QComboBox
from PySide6.QtCore import Signal


class ObjectPropertiesPanel(QGroupBox):
    """Panel for object properties (visible, persistent, solid, parent)"""

    property_changed = Signal(str, object)  # property_name, value (bool or str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.available_sprites = {}
        self.available_objects = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the properties UI"""
        self.setTitle(self.tr("Object Properties"))

        # Use vertical layout for better organization
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Sprite selector (using form layout for label)
        sprite_layout = QFormLayout()
        sprite_layout.setContentsMargins(0, 0, 0, 0)

        self.sprite_combo = QComboBox()
        self.sprite_combo.addItem("None")
        self.sprite_combo.setToolTip(self.tr("Sprite to display for this object"))
        self.sprite_combo.currentTextChanged.connect(self._on_sprite_changed)

        sprite_layout.addRow(self.tr("Sprite:"), self.sprite_combo)

        # Parent object selector
        self.parent_combo = QComboBox()
        self.parent_combo.addItem(self.tr("<no parent>"))
        self.parent_combo.setToolTip(self.tr("Parent object (inherits collision events)"))
        self.parent_combo.currentTextChanged.connect(self._on_parent_changed)
        sprite_layout.addRow(self.tr("Parent:"), self.parent_combo)

        main_layout.addLayout(sprite_layout)

        # Checkboxes in horizontal layout
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setContentsMargins(0, 0, 0, 0)

        # Visible checkbox
        self.visible_checkbox = QCheckBox(self.tr("Visible"))
        self.visible_checkbox.setChecked(True)
        self.visible_checkbox.setToolTip(self.tr("Object is visible in the game"))
        self.visible_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('visible', self.visible_checkbox.isChecked())
        )
        checkbox_layout.addWidget(self.visible_checkbox)

        # Persistent checkbox
        self.persistent_checkbox = QCheckBox(self.tr("Persistent"))
        self.persistent_checkbox.setChecked(False)
        self.persistent_checkbox.setToolTip(self.tr("Object persists between rooms"))
        self.persistent_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('persistent', self.persistent_checkbox.isChecked())
        )
        checkbox_layout.addWidget(self.persistent_checkbox)

        # Solid checkbox
        self.solid_checkbox = QCheckBox(self.tr("Solid"))
        self.solid_checkbox.setChecked(False)
        self.solid_checkbox.setToolTip(self.tr("Solid objects block movement"))
        self.solid_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('solid', self.solid_checkbox.isChecked())
        )
        checkbox_layout.addWidget(self.solid_checkbox)

        checkbox_layout.addStretch()
        main_layout.addLayout(checkbox_layout)

        # View Code checkbox (second row)
        view_code_layout = QHBoxLayout()
        view_code_layout.setContentsMargins(0, 0, 0, 0)

        self.view_code_checkbox = QCheckBox(self.tr("View Code"))
        self.view_code_checkbox.setChecked(False)
        self.view_code_checkbox.setToolTip(self.tr("Show generated code in Code Editor tab"))
        self.view_code_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('view_code', self.view_code_checkbox.isChecked())
        )
        view_code_layout.addWidget(self.view_code_checkbox)
        view_code_layout.addStretch()

        main_layout.addLayout(view_code_layout)

    def _on_sprite_changed(self, sprite_name: str):
        """Handle sprite selection change"""
        value = sprite_name if sprite_name != "None" else ''
        self.property_changed.emit('sprite', value)

    def _on_parent_changed(self, parent_name: str):
        """Handle parent object selection change"""
        no_parent = self.tr("<no parent>")
        value = parent_name if parent_name != no_parent else ''
        self.property_changed.emit('parent', value)

    def set_available_objects(self, objects: Dict[str, Any], current_object_name: str = ''):
        """Update available objects in parent combo box"""
        self.available_objects = objects

        self.parent_combo.blockSignals(True)
        current_selection = self.parent_combo.currentText()
        self.parent_combo.clear()
        self.parent_combo.addItem(self.tr("<no parent>"))
        for obj_name in objects.keys():
            if obj_name != current_object_name:  # Can't be own parent
                self.parent_combo.addItem(obj_name)
        # Restore selection if it still exists
        index = self.parent_combo.findText(current_selection)
        if index >= 0:
            self.parent_combo.setCurrentIndex(index)
        self.parent_combo.blockSignals(False)

    def set_available_sprites(self, sprites: Dict[str, Any]):
        """Update available sprites in combo box"""
        self.available_sprites = sprites

        # Block signals while updating
        self.sprite_combo.blockSignals(True)

        current_selection = self.sprite_combo.currentText()

        self.sprite_combo.clear()
        self.sprite_combo.addItem("None")

        for sprite_name in sprites.keys():
            self.sprite_combo.addItem(sprite_name)

        # Restore selection if it still exists
        index = self.sprite_combo.findText(current_selection)
        if index >= 0:
            self.sprite_combo.setCurrentIndex(index)

        self.sprite_combo.blockSignals(False)

    def load_properties(self, data: Dict[str, Any]):
        """Load properties from data"""
        # Block signals while loading to avoid marking as modified
        self.sprite_combo.blockSignals(True)
        self.parent_combo.blockSignals(True)
        self.visible_checkbox.blockSignals(True)
        self.persistent_checkbox.blockSignals(True)
        self.solid_checkbox.blockSignals(True)

        # Load sprite
        sprite_name = data.get('sprite', '')
        if sprite_name:
            index = self.sprite_combo.findText(sprite_name)
            if index >= 0:
                self.sprite_combo.setCurrentIndex(index)
            else:
                self.sprite_combo.setCurrentIndex(0)  # "None"
        else:
            self.sprite_combo.setCurrentIndex(0)  # "None"

        # Load parent
        parent_name = data.get('parent', '')
        if parent_name:
            index = self.parent_combo.findText(parent_name)
            if index >= 0:
                self.parent_combo.setCurrentIndex(index)
            else:
                self.parent_combo.setCurrentIndex(0)
        else:
            self.parent_combo.setCurrentIndex(0)

        self.visible_checkbox.setChecked(data.get('visible', True))
        self.persistent_checkbox.setChecked(data.get('persistent', False))
        self.solid_checkbox.setChecked(data.get('solid', False))

        # Unblock signals after loading
        self.sprite_combo.blockSignals(False)
        self.parent_combo.blockSignals(False)
        self.visible_checkbox.blockSignals(False)
        self.persistent_checkbox.blockSignals(False)
        self.solid_checkbox.blockSignals(False)

    def get_properties(self) -> Dict[str, Any]:
        """Get current property values"""
        sprite_name = self.sprite_combo.currentText()
        parent_name = self.parent_combo.currentText()
        no_parent = self.tr("<no parent>")
        return {
            'sprite': sprite_name if sprite_name != "None" else '',
            'parent': parent_name if parent_name != no_parent else '',
            'visible': self.visible_checkbox.isChecked(),
            'persistent': self.persistent_checkbox.isChecked(),
            'solid': self.solid_checkbox.isChecked(),
        }

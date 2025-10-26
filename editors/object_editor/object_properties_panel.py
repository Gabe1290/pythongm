#!/usr/bin/env python3
"""
Object Properties Panel
Manages object properties: visible, persistent, solid, sprite
"""

from typing import Dict, Any
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox
from PySide6.QtCore import Signal


class ObjectPropertiesPanel(QGroupBox):
    """Panel for object properties (visible, persistent, solid)"""
    
    property_changed = Signal(str, bool)  # property_name, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the properties UI"""
        self.setTitle(self.tr("Object Properties"))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Visible checkbox
        self.visible_checkbox = QCheckBox(self.tr("Visible"))
        self.visible_checkbox.setChecked(True)
        self.visible_checkbox.setToolTip(self.tr("Object is visible in the game"))
        self.visible_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('visible', self.visible_checkbox.isChecked())
        )
        layout.addWidget(self.visible_checkbox)
        
        # Persistent checkbox
        self.persistent_checkbox = QCheckBox(self.tr("Persistent"))
        self.persistent_checkbox.setChecked(False)
        self.persistent_checkbox.setToolTip(self.tr("Object persists between rooms"))
        self.persistent_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('persistent', self.persistent_checkbox.isChecked())
        )
        layout.addWidget(self.persistent_checkbox)
        
        # Solid checkbox
        self.solid_checkbox = QCheckBox(self.tr("Solid"))
        self.solid_checkbox.setChecked(False)
        self.solid_checkbox.setToolTip(self.tr("Solid objects block movement"))
        self.solid_checkbox.stateChanged.connect(
            lambda: self.property_changed.emit('solid', self.solid_checkbox.isChecked())
        )
        layout.addWidget(self.solid_checkbox)
        
        layout.addStretch()
    
    def load_properties(self, data: Dict[str, Any]):
        """Load properties from data"""
        # Block signals while loading to avoid marking as modified
        self.visible_checkbox.blockSignals(True)
        self.persistent_checkbox.blockSignals(True)
        self.solid_checkbox.blockSignals(True)
        
        self.visible_checkbox.setChecked(data.get('visible', True))
        self.persistent_checkbox.setChecked(data.get('persistent', False))
        self.solid_checkbox.setChecked(data.get('solid', False))
        
        # Unblock signals after loading
        self.visible_checkbox.blockSignals(False)
        self.persistent_checkbox.blockSignals(False)
        self.solid_checkbox.blockSignals(False)
    
    def get_properties(self) -> Dict[str, bool]:
        """Get current property values"""
        return {
            'visible': self.visible_checkbox.isChecked(),
            'persistent': self.persistent_checkbox.isChecked(),
            'solid': self.solid_checkbox.isChecked(),
        }
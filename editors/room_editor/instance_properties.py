#!/usr/bin/env python3
"""
Instance Properties widget for Room Editor
Displays and edits properties of selected object instances
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QSpinBox, QCheckBox, QPushButton)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont


class InstanceProperties(QWidget):
    """Widget for editing instance properties"""

    property_changed = Signal(object, str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_instance = None

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self.tr("Instance Properties"))
        title.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(title)

        # Properties form
        form_layout = QVBoxLayout()

        # Object name (read-only)
        self.object_label = QLabel(self.tr("Object: None"))
        form_layout.addWidget(self.object_label)

        # Position
        pos_group = QGroupBox(self.tr("Position"))
        pos_layout = QHBoxLayout(pos_group)

        pos_layout.addWidget(QLabel(self.tr("X:")))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.valueChanged.connect(self.on_x_changed)
        pos_layout.addWidget(self.x_spin)

        pos_layout.addWidget(QLabel(self.tr("Y:")))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.valueChanged.connect(self.on_y_changed)
        pos_layout.addWidget(self.y_spin)

        form_layout.addWidget(pos_group)

        # Visibility
        self.visible_check = QCheckBox(self.tr("Visible"))
        self.visible_check.setChecked(True)
        self.visible_check.toggled.connect(self.on_visible_changed)
        form_layout.addWidget(self.visible_check)

        # Rotation
        rot_group = QGroupBox(self.tr("Rotation"))
        rot_layout = QHBoxLayout(rot_group)
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.setValue(0)
        self.rotation_spin.valueChanged.connect(self.on_rotation_changed)
        rot_layout.addWidget(self.rotation_spin)
        form_layout.addWidget(rot_group)

        # Scale
        scale_group = QGroupBox(self.tr("Scale"))
        scale_layout = QHBoxLayout(scale_group)

        scale_layout.addWidget(QLabel(self.tr("X:")))
        self.scale_x_spin = QSpinBox()
        self.scale_x_spin.setRange(10, 1000)
        self.scale_x_spin.setSuffix("%")
        self.scale_x_spin.setValue(100)
        self.scale_x_spin.valueChanged.connect(self.on_scale_x_changed)
        scale_layout.addWidget(self.scale_x_spin)

        scale_layout.addWidget(QLabel(self.tr("Y:")))
        self.scale_y_spin = QSpinBox()
        self.scale_y_spin.setRange(10, 1000)
        self.scale_y_spin.setSuffix("%")
        self.scale_y_spin.setValue(100)
        self.scale_y_spin.valueChanged.connect(self.on_scale_y_changed)
        scale_layout.addWidget(self.scale_y_spin)

        form_layout.addWidget(scale_group)

        # Delete button
        delete_btn = QPushButton(self.tr("Delete Instance"))
        delete_btn.clicked.connect(self.delete_instance)
        form_layout.addWidget(delete_btn)

        layout.addLayout(form_layout)
        layout.addStretch()

    def set_instance(self, instance):
        """Set the current instance to edit"""
        self.current_instance = instance

        if instance:
            # Block all signals while loading
            self.x_spin.blockSignals(True)
            self.y_spin.blockSignals(True)
            self.visible_check.blockSignals(True)
            self.rotation_spin.blockSignals(True)
            self.scale_x_spin.blockSignals(True)
            self.scale_y_spin.blockSignals(True)

            # Load values
            self.object_label.setText(self.tr("Object: {0}").format(instance.object_name))
            self.x_spin.setValue(instance.x)
            self.y_spin.setValue(instance.y)
            self.visible_check.setChecked(instance.visible)
            self.rotation_spin.setValue(int(instance.rotation))
            self.scale_x_spin.setValue(int(instance.scale_x * 100))
            self.scale_y_spin.setValue(int(instance.scale_y * 100))

            # Unblock signals
            self.x_spin.blockSignals(False)
            self.y_spin.blockSignals(False)
            self.visible_check.blockSignals(False)
            self.rotation_spin.blockSignals(False)
            self.scale_x_spin.blockSignals(False)
            self.scale_y_spin.blockSignals(False)

            self.setEnabled(True)
        else:
            self.object_label.setText(self.tr("Object: None"))
            self.setEnabled(False)

    def on_x_changed(self, value):
        """Handle X position change"""
        if self.current_instance:
            self.current_instance.x = value
            self.property_changed.emit(self.current_instance, "x", value)

    def on_y_changed(self, value):
        """Handle Y position change"""
        if self.current_instance:
            self.current_instance.y = value
            self.property_changed.emit(self.current_instance, "y", value)

    def on_visible_changed(self, checked):
        """Handle visibility change"""
        if self.current_instance:
            self.current_instance.visible = checked
            self.property_changed.emit(self.current_instance, "visible", checked)

    def delete_instance(self):
        """Delete the current instance"""
        if self.current_instance:
            # Emit a special signal for deletion
            self.property_changed.emit(self.current_instance, "delete", True)

    def on_rotation_changed(self, value):
        """Handle rotation change"""
        if self.current_instance:
            self.current_instance.rotation = value
            self.property_changed.emit(self.current_instance, "rotation", value)

    def on_scale_x_changed(self, value):
        """Handle X scale change"""
        if self.current_instance:
            self.current_instance.scale_x = value / 100.0
            self.property_changed.emit(self.current_instance, "scale_x", value / 100.0)

    def on_scale_y_changed(self, value):
        """Handle Y scale change"""
        if self.current_instance:
            self.current_instance.scale_y = value / 100.0
            self.property_changed.emit(self.current_instance, "scale_y", value / 100.0)

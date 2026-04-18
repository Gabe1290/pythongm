#!/usr/bin/env python3
"""
Properties panel for playground elements (walls and robots).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QSpinBox, QComboBox, QLineEdit, QCheckBox, QGroupBox, QPushButton,
)
from PySide6.QtCore import Signal, Qt

from editors.playground_editor.playground_elements import PlaygroundWall, PlaygroundRobot


class PlaygroundElementProperties(QWidget):
    """Properties panel that shows fields for the selected playground element"""

    property_changed = Signal(object, str, object)  # element, prop_name, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_element = None
        self._updating = False  # Block signals during programmatic updates

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.title_label = QLabel(self.tr("No Selection"))
        self.title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.title_label)

        # ── Wall properties group ──
        self.wall_group = QGroupBox(self.tr("Wall"))
        wl = QVBoxLayout(self.wall_group)
        wl.setSpacing(3)

        # Position
        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("X:"))
        self.wall_x = QDoubleSpinBox()
        self.wall_x.setRange(-9999, 9999)
        self.wall_x.setDecimals(1)
        self.wall_x.valueChanged.connect(lambda v: self._on_changed('x', v))
        pos_row.addWidget(self.wall_x)
        pos_row.addWidget(QLabel("Y:"))
        self.wall_y = QDoubleSpinBox()
        self.wall_y.setRange(-9999, 9999)
        self.wall_y.setDecimals(1)
        self.wall_y.valueChanged.connect(lambda v: self._on_changed('y', v))
        pos_row.addWidget(self.wall_y)
        wl.addLayout(pos_row)

        # Dimensions
        dim_row = QHBoxLayout()
        dim_row.addWidget(QLabel("L1:"))
        self.wall_l1 = QDoubleSpinBox()
        self.wall_l1.setRange(1, 9999)
        self.wall_l1.setDecimals(1)
        self.wall_l1.valueChanged.connect(lambda v: self._on_changed('l1', v))
        dim_row.addWidget(self.wall_l1)
        dim_row.addWidget(QLabel("L2:"))
        self.wall_l2 = QDoubleSpinBox()
        self.wall_l2.setRange(1, 9999)
        self.wall_l2.setDecimals(1)
        self.wall_l2.valueChanged.connect(lambda v: self._on_changed('l2', v))
        dim_row.addWidget(self.wall_l2)
        wl.addLayout(dim_row)

        # Height
        h_row = QHBoxLayout()
        h_row.addWidget(QLabel(self.tr("Height:")))
        self.wall_h = QDoubleSpinBox()
        self.wall_h.setRange(1, 100)
        self.wall_h.setDecimals(1)
        self.wall_h.valueChanged.connect(lambda v: self._on_changed('h', v))
        h_row.addWidget(self.wall_h)
        wl.addLayout(h_row)

        # Angle (display in degrees, store in radians)
        angle_row = QHBoxLayout()
        angle_row.addWidget(QLabel(self.tr("Angle:")))
        self.wall_angle_deg = QDoubleSpinBox()
        self.wall_angle_deg.setRange(-360, 360)
        self.wall_angle_deg.setDecimals(1)
        self.wall_angle_deg.setSuffix("°")
        self.wall_angle_deg.valueChanged.connect(self._on_angle_changed)
        angle_row.addWidget(self.wall_angle_deg)
        wl.addLayout(angle_row)

        # Color
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel(self.tr("Color:")))
        self.wall_color = QComboBox()
        self.wall_color.currentTextChanged.connect(
            lambda v: self._on_changed('color', v))
        color_row.addWidget(self.wall_color)
        wl.addLayout(color_row)

        # Mass (pushable)
        mass_row = QHBoxLayout()
        self.wall_has_mass = QCheckBox(self.tr("Pushable"))
        self.wall_has_mass.toggled.connect(self._on_mass_toggled)
        mass_row.addWidget(self.wall_has_mass)
        self.wall_mass = QDoubleSpinBox()
        self.wall_mass.setRange(1, 9999)
        self.wall_mass.setDecimals(0)
        self.wall_mass.setEnabled(False)
        self.wall_mass.valueChanged.connect(
            lambda v: self._on_changed('mass', v))
        mass_row.addWidget(self.wall_mass)
        wl.addLayout(mass_row)

        layout.addWidget(self.wall_group)
        self.wall_group.hide()

        # ── Robot properties group ──
        self.robot_group = QGroupBox(self.tr("Robot"))
        rl = QVBoxLayout(self.robot_group)
        rl.setSpacing(3)

        # Type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel(self.tr("Type:")))
        self.robot_type = QComboBox()
        self.robot_type.addItems(["thymio2", "e-puck"])
        self.robot_type.currentTextChanged.connect(
            lambda v: self._on_changed('robot_type', v))
        type_row.addWidget(self.robot_type)
        rl.addLayout(type_row)

        # Name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel(self.tr("Name:")))
        self.robot_name = QLineEdit()
        self.robot_name.editingFinished.connect(
            lambda: self._on_changed('name', self.robot_name.text()))
        name_row.addWidget(self.robot_name)
        rl.addLayout(name_row)

        # Position
        rpos_row = QHBoxLayout()
        rpos_row.addWidget(QLabel("X:"))
        self.robot_x = QDoubleSpinBox()
        self.robot_x.setRange(-9999, 9999)
        self.robot_x.setDecimals(1)
        self.robot_x.valueChanged.connect(lambda v: self._on_changed('x', v))
        rpos_row.addWidget(self.robot_x)
        rpos_row.addWidget(QLabel("Y:"))
        self.robot_y = QDoubleSpinBox()
        self.robot_y.setRange(-9999, 9999)
        self.robot_y.setDecimals(1)
        self.robot_y.valueChanged.connect(lambda v: self._on_changed('y', v))
        rpos_row.addWidget(self.robot_y)
        rl.addLayout(rpos_row)

        # Angle
        rangle_row = QHBoxLayout()
        rangle_row.addWidget(QLabel(self.tr("Angle:")))
        self.robot_angle_deg = QDoubleSpinBox()
        self.robot_angle_deg.setRange(-360, 360)
        self.robot_angle_deg.setDecimals(1)
        self.robot_angle_deg.setSuffix("°")
        self.robot_angle_deg.valueChanged.connect(self._on_robot_angle_changed)
        rangle_row.addWidget(self.robot_angle_deg)
        rl.addLayout(rangle_row)

        # Port
        port_row = QHBoxLayout()
        port_row.addWidget(QLabel(self.tr("Port:")))
        self.robot_port = QSpinBox()
        self.robot_port.setRange(1024, 65535)
        self.robot_port.valueChanged.connect(
            lambda v: self._on_changed('port', v))
        port_row.addWidget(self.robot_port)
        rl.addLayout(port_row)

        # Linked object (for in-IDE simulation)
        linked_row = QHBoxLayout()
        linked_row.addWidget(QLabel(self.tr("Code:")))
        self.robot_linked = QComboBox()
        self.robot_linked.setToolTip(
            self.tr("Which Thymio object's code to run when simulating"))
        self.robot_linked.currentTextChanged.connect(self._on_linked_changed)
        linked_row.addWidget(self.robot_linked)
        rl.addLayout(linked_row)

        layout.addWidget(self.robot_group)
        self.robot_group.hide()

        # Delete button
        self.delete_btn = QPushButton(self.tr("Delete"))
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.hide()
        layout.addWidget(self.delete_btn)

        layout.addStretch()

    def set_color_names(self, names):
        """Update the color combo box options"""
        current = self.wall_color.currentText()
        self.wall_color.blockSignals(True)
        self.wall_color.clear()
        self.wall_color.addItems(names)
        idx = self.wall_color.findText(current)
        if idx >= 0:
            self.wall_color.setCurrentIndex(idx)
        self.wall_color.blockSignals(False)

    def set_linkable_objects(self, object_names):
        """Update the linked-object dropdown with available Thymio objects"""
        current = self.robot_linked.currentText()
        self.robot_linked.blockSignals(True)
        self.robot_linked.clear()
        self.robot_linked.addItem("")  # "none" option
        for name in object_names:
            self.robot_linked.addItem(name)
        idx = self.robot_linked.findText(current)
        if idx >= 0:
            self.robot_linked.setCurrentIndex(idx)
        self.robot_linked.blockSignals(False)

    def set_element(self, element):
        """Show properties for the given element"""
        self.current_element = element
        self._updating = True

        self.wall_group.hide()
        self.robot_group.hide()
        self.delete_btn.hide()

        if element is None:
            self.title_label.setText(self.tr("No Selection"))
            self._updating = False
            return

        self.delete_btn.show()

        if isinstance(element, PlaygroundWall):
            self.title_label.setText(self.tr("Wall Properties"))
            self.wall_group.show()
            self.wall_x.setValue(element.x)
            self.wall_y.setValue(element.y)
            self.wall_l1.setValue(element.l1)
            self.wall_l2.setValue(element.l2)
            self.wall_h.setValue(element.h)
            self.wall_angle_deg.setValue(round(element.angle * 180 / 3.14159265, 1))
            idx = self.wall_color.findText(element.color)
            if idx >= 0:
                self.wall_color.setCurrentIndex(idx)
            has_mass = element.mass is not None
            self.wall_has_mass.setChecked(has_mass)
            self.wall_mass.setEnabled(has_mass)
            if has_mass:
                self.wall_mass.setValue(element.mass)

        elif isinstance(element, PlaygroundRobot):
            self.title_label.setText(self.tr("Robot Properties"))
            self.robot_group.show()
            idx = self.robot_type.findText(element.robot_type)
            if idx >= 0:
                self.robot_type.setCurrentIndex(idx)
            self.robot_name.setText(element.name)
            self.robot_x.setValue(element.x)
            self.robot_y.setValue(element.y)
            self.robot_angle_deg.setValue(round(element.angle * 180 / 3.14159265, 1))
            self.robot_port.setValue(element.port)
            # Linked object
            linked = getattr(element, 'linked_object', '') or ''
            idx = self.robot_linked.findText(linked)
            if idx >= 0:
                self.robot_linked.setCurrentIndex(idx)
            else:
                self.robot_linked.setCurrentIndex(0)  # "none"

        self._updating = False

    def _on_changed(self, prop, value):
        if self._updating or not self.current_element:
            return
        self.property_changed.emit(self.current_element, prop, value)

    def _on_angle_changed(self, degrees):
        if self._updating or not self.current_element:
            return
        radians = degrees * 3.14159265 / 180
        self.property_changed.emit(self.current_element, 'angle', radians)

    def _on_robot_angle_changed(self, degrees):
        if self._updating or not self.current_element:
            return
        radians = degrees * 3.14159265 / 180
        self.property_changed.emit(self.current_element, 'angle', radians)

    def _on_mass_toggled(self, checked):
        if self._updating or not self.current_element:
            return
        self.wall_mass.setEnabled(checked)
        if checked:
            value = self.wall_mass.value()
            self.property_changed.emit(self.current_element, 'mass', value)
        else:
            self.property_changed.emit(self.current_element, 'mass', None)

    def _on_linked_changed(self, value):
        if self._updating or not self.current_element:
            return
        self.property_changed.emit(self.current_element, 'linked_object', value)

    def _on_delete(self):
        if self.current_element:
            self.property_changed.emit(self.current_element, 'delete', None)

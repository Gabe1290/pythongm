#!/usr/bin/env python3
"""
Node Properties Panel - Edit properties of selected nodes
"""

from typing import Optional, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                                QCheckBox, QGroupBox, QPushButton, QTextEdit)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from .visual_node import VisualNode


class NodePropertiesPanel(QWidget):
    """Panel for editing node properties"""
    
    # Signals
    property_changed = Signal(object, str, object)  # node, property_name, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: Optional[VisualNode] = None
        self.updating = False  # Flag to prevent circular updates
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Node Properties")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title)
        
        # Node info group
        self.info_group = QGroupBox("Node Info")
        info_layout = QVBoxLayout(self.info_group)
        
        self.node_title_label = QLabel("No node selected")
        self.node_title_label.setWordWrap(True)
        info_layout.addWidget(self.node_title_label)
        
        self.node_type_label = QLabel("")
        self.node_type_label.setStyleSheet("color: #888;")
        info_layout.addWidget(self.node_type_label)
        
        self.node_id_label = QLabel("")
        self.node_id_label.setStyleSheet("color: #888; font-size: 8pt;")
        info_layout.addWidget(self.node_id_label)
        
        layout.addWidget(self.info_group)
        
        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_group)
        layout.addWidget(self.params_group)
        
        # Connections info
        self.connections_group = QGroupBox("Connections")
        connections_layout = QVBoxLayout(self.connections_group)
        
        self.connections_label = QLabel("No connections")
        self.connections_label.setWordWrap(True)
        connections_layout.addWidget(self.connections_label)
        
        layout.addWidget(self.connections_group)
        
        # Delete button
        self.delete_button = QPushButton("Delete Node")
        self.delete_button.clicked.connect(self.delete_current_node)
        self.delete_button.setEnabled(False)
        layout.addWidget(self.delete_button)
        
        # Stretch
        layout.addStretch()
        
        # Initially hide parameter groups
        self.params_group.setVisible(False)
        self.connections_group.setVisible(False)
    
    def set_node(self, node: Optional[VisualNode]):
        """Set the current node to display/edit"""
        self.current_node = node
        self.updating = True
        
        if node:
            self.show_node_properties(node)
            self.delete_button.setEnabled(True)
        else:
            self.clear_properties()
            self.delete_button.setEnabled(False)
        
        self.updating = False
    
    def show_node_properties(self, node: VisualNode):
        """Display node properties"""
        # Update info
        self.node_title_label.setText(f"<b>{node.title}</b>")
        self.node_type_label.setText(f"Category: {node.category}")
        self.node_id_label.setText(f"ID: {node.node_id}")
        
        # Clear and rebuild parameters
        self.clear_parameter_widgets()
        
        if node.parameters:
            self.params_group.setVisible(True)
            
            for param_name, param_value in node.parameters.items():
                self.add_parameter_widget(param_name, param_value)
        else:
            self.params_group.setVisible(False)
        
        # Show connections
        self.show_connections_info(node)
    
    def clear_properties(self):
        """Clear all property displays"""
        self.node_title_label.setText("No node selected")
        self.node_type_label.setText("")
        self.node_id_label.setText("")
        self.clear_parameter_widgets()
        self.params_group.setVisible(False)
        self.connections_group.setVisible(False)
    
    def clear_parameter_widgets(self):
        """Clear parameter widgets"""
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def add_parameter_widget(self, param_name: str, param_value: Any):
        """Add a widget for editing a parameter"""
        label = QLabel(param_name.replace('_', ' ').title() + ":")
        
        # Create appropriate widget based on value type
        if isinstance(param_value, bool):
            widget = QCheckBox()
            widget.setChecked(param_value)
            widget.toggled.connect(lambda value: self.on_parameter_changed(param_name, value))
        
        elif isinstance(param_value, int):
            widget = QSpinBox()
            widget.setRange(-9999, 9999)
            widget.setValue(param_value)
            widget.valueChanged.connect(lambda value: self.on_parameter_changed(param_name, value))
        
        elif isinstance(param_value, float):
            widget = QDoubleSpinBox()
            widget.setRange(-9999.0, 9999.0)
            widget.setValue(param_value)
            widget.valueChanged.connect(lambda value: self.on_parameter_changed(param_name, value))
        
        elif isinstance(param_value, str):
            # Check if this should be a dropdown (for specific parameters)
            if param_name in ['direction', 'operator']:
                widget = QComboBox()
                if param_name == 'direction':
                    widget.addItems(['left', 'right', 'up', 'down'])
                elif param_name == 'operator':
                    widget.addItems(['==', '!=', '<', '>', '<=', '>='])
                
                if param_value in [widget.itemText(i) for i in range(widget.count())]:
                    widget.setCurrentText(param_value)
                
                widget.currentTextChanged.connect(lambda value: self.on_parameter_changed(param_name, value))
            else:
                widget = QLineEdit()
                widget.setText(str(param_value))
                widget.textChanged.connect(lambda value: self.on_parameter_changed(param_name, value))
        
        else:
            widget = QLineEdit()
            widget.setText(str(param_value))
            widget.textChanged.connect(lambda value: self.on_parameter_changed(param_name, value))
        
        self.params_layout.addRow(label, widget)
    
    def on_parameter_changed(self, param_name: str, value: Any):
        """Handle parameter value change"""
        if self.updating or not self.current_node:
            return
        
        # Update node parameter
        self.current_node.parameters[param_name] = value
        
        # Emit signal
        self.property_changed.emit(self.current_node, param_name, value)
    
    def show_connections_info(self, node: VisualNode):
        """Show connection information"""
        input_connections = []
        output_connections = []
        
        for port in node.input_ports:
            if port.connections:
                input_connections.append(f"• {port.name or 'exec'}: {len(port.connections)} connection(s)")
        
        for port in node.output_ports:
            if port.connections:
                output_connections.append(f"• {port.name or 'exec'}: {len(port.connections)} connection(s)")
        
        if input_connections or output_connections:
            self.connections_group.setVisible(True)
            
            info_text = ""
            if input_connections:
                info_text += "<b>Inputs:</b><br>" + "<br>".join(input_connections)
            if output_connections:
                if info_text:
                    info_text += "<br><br>"
                info_text += "<b>Outputs:</b><br>" + "<br>".join(output_connections)
            
            self.connections_label.setText(info_text)
        else:
            self.connections_group.setVisible(False)
    
    def delete_current_node(self):
        """Delete the current node"""
        if self.current_node:
            # Emit signal to request deletion
            # The canvas should handle the actual deletion
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Delete Node",
                f"Are you sure you want to delete '{self.current_node.title}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Signal to parent/canvas to delete
                if self.parent() and hasattr(self.parent(), 'delete_selected_node'):
                    self.parent().delete_selected_node()
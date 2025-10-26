#!/usr/bin/env python3
"""
Visual Node - Base class for visual programming nodes
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class PortType(Enum):
    """Type of port on a node"""
    EXECUTION_IN = "exec_in"      # Execution flow input
    EXECUTION_OUT = "exec_out"    # Execution flow output
    DATA_IN = "data_in"           # Data input
    DATA_OUT = "data_out"         # Data output


class NodePort:
    """Represents an input or output port on a node"""
    
    def __init__(self, name: str, port_type: PortType, data_type: str = "any", position: QPointF = None):
        self.name = name
        self.port_type = port_type
        self.data_type = data_type  # "any", "number", "string", "boolean", "object", etc.
        self.position = position or QPointF(0, 0)  # Relative to node
        self.connections = []  # List of NodeConnection objects
        
    def is_input(self) -> bool:
        """Check if this is an input port"""
        return self.port_type in [PortType.EXECUTION_IN, PortType.DATA_IN]
    
    def is_output(self) -> bool:
        """Check if this is an output port"""
        return self.port_type in [PortType.EXECUTION_OUT, PortType.DATA_OUT]
    
    def is_execution(self) -> bool:
        """Check if this is an execution port"""
        return self.port_type in [PortType.EXECUTION_IN, PortType.EXECUTION_OUT]
    
    def can_connect_to(self, other: 'NodePort') -> bool:
        """Check if this port can connect to another port"""
        # Can't connect to self
        if other == self:
            return False
        
        # Must be input->output or output->input
        if self.is_input() == other.is_input():
            return False
        
        # Execution ports only connect to execution ports
        if self.is_execution() != other.is_execution():
            return False
        
        # Check data type compatibility (for data ports)
        if not self.is_execution():
            if self.data_type != "any" and other.data_type != "any":
                if self.data_type != other.data_type:
                    return False
        
        return True


class VisualNode(QGraphicsItem):
    """Base class for visual programming nodes"""
    
    # Node styling
    NODE_WIDTH = 180
    NODE_HEIGHT = 60
    NODE_PADDING = 10
    PORT_RADIUS = 6
    TITLE_HEIGHT = 30
    
    def __init__(self, node_id: str, title: str, category: str = "General"):
        super().__init__()
        
        self.node_id = node_id
        self.title = title
        self.category = category
        
        # Visual properties
        self.color = QColor("#4A90E2")  # Default blue
        self.selected_color = QColor("#FFA500")
        
        # Ports
        self.input_ports: List[NodePort] = []
        self.output_ports: List[NodePort] = []
        
        # Parameters (editable values)
        self.parameters: Dict[str, Any] = {}
        
        # Graphics settings
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Size
        self.width = self.NODE_WIDTH
        self.height = self.NODE_HEIGHT
        
        # Title text item
        self.title_item = None
    
    def add_input_port(self, name: str, port_type: PortType, data_type: str = "any") -> NodePort:
        """Add an input port"""
        port = NodePort(name, port_type, data_type)
        self.input_ports.append(port)
        self.update_port_positions()
        return port
    
    def add_output_port(self, name: str, port_type: PortType, data_type: str = "any") -> NodePort:
        """Add an output port"""
        port = NodePort(name, port_type, data_type)
        self.output_ports.append(port)
        self.update_port_positions()
        return port
    
    def update_port_positions(self):
        """Update port positions based on node size"""
        # Calculate port spacing
        input_spacing = (self.height - self.TITLE_HEIGHT) / (len(self.input_ports) + 1) if self.input_ports else 0
        output_spacing = (self.height - self.TITLE_HEIGHT) / (len(self.output_ports) + 1) if self.output_ports else 0
        
        # Position input ports on left side
        for i, port in enumerate(self.input_ports):
            y = self.TITLE_HEIGHT + input_spacing * (i + 1)
            port.position = QPointF(0, y)
        
        # Position output ports on right side
        for i, port in enumerate(self.output_ports):
            y = self.TITLE_HEIGHT + output_spacing * (i + 1)
            port.position = QPointF(self.width, y)
    
    def get_port_scene_position(self, port: NodePort) -> QPointF:
        """Get port position in scene coordinates"""
        return self.mapToScene(port.position)
    
    def find_port_at_position(self, pos: QPointF) -> Optional[NodePort]:
        """Find port at given position (in item coordinates)"""
        for port in self.input_ports + self.output_ports:
            port_rect = QRectF(
                port.position.x() - self.PORT_RADIUS,
                port.position.y() - self.PORT_RADIUS,
                self.PORT_RADIUS * 2,
                self.PORT_RADIUS * 2
            )
            if port_rect.contains(pos):
                return port
        return None
    
    def boundingRect(self) -> QRectF:
        """Return bounding rectangle"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Paint the node"""
        # Choose color based on selection
        color = self.selected_color if self.isSelected() else self.color
        
        # Draw main body
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)
        
        # Draw title bar
        painter.setBrush(QBrush(color.darker(120)))
        painter.drawRoundedRect(0, 0, self.width, self.TITLE_HEIGHT, 5, 5)
        painter.drawRect(0, self.TITLE_HEIGHT - 5, self.width, 5)
        
        # Draw title text
        painter.setPen(QPen(Qt.white))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        title_rect = QRectF(self.NODE_PADDING, 0, self.width - 2 * self.NODE_PADDING, self.TITLE_HEIGHT)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)
        
        # Draw ports
        self.draw_ports(painter)
        
        # Draw parameters text
        self.draw_parameters(painter)
    
    def draw_ports(self, painter: QPainter):
        """Draw input and output ports"""
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        # Draw input ports (left side)
        for port in self.input_ports:
            # Port circle
            port_color = QColor("#FF6B6B") if port.is_execution() else QColor("#4ECDC4")
            painter.setBrush(QBrush(port_color))
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.drawEllipse(
                port.position.x() - self.PORT_RADIUS,
                port.position.y() - self.PORT_RADIUS,
                self.PORT_RADIUS * 2,
                self.PORT_RADIUS * 2
            )
            
            # Port label
            painter.setPen(QPen(Qt.white))
            text_rect = QRectF(
                self.PORT_RADIUS + 5,
                port.position.y() - 10,
                self.width / 2 - self.PORT_RADIUS - 10,
                20
            )
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, port.name)
        
        # Draw output ports (right side)
        for port in self.output_ports:
            # Port circle
            port_color = QColor("#FF6B6B") if port.is_execution() else QColor("#4ECDC4")
            painter.setBrush(QBrush(port_color))
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.drawEllipse(
                port.position.x() - self.PORT_RADIUS,
                port.position.y() - self.PORT_RADIUS,
                self.PORT_RADIUS * 2,
                self.PORT_RADIUS * 2
            )
            
            # Port label
            painter.setPen(QPen(Qt.white))
            text_rect = QRectF(
                self.width / 2,
                port.position.y() - 10,
                self.width / 2 - self.PORT_RADIUS - 10,
                20
            )
            painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, port.name)
    
    def draw_parameters(self, painter: QPainter):
        """Draw parameter values on the node"""
        if not self.parameters:
            return
        
        painter.setPen(QPen(Qt.white))
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        y_offset = self.TITLE_HEIGHT + 20
        for key, value in self.parameters.items():
            if y_offset + 15 > self.height:
                break
            
            text = f"{key}: {value}"
            text_rect = QRectF(self.NODE_PADDING, y_offset, self.width - 2 * self.NODE_PADDING, 15)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
            y_offset += 15
    
    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.ItemPositionChange:
            # Update connections when node moves
            if self.scene():
                for port in self.input_ports + self.output_ports:
                    for connection in port.connections:
                        connection.update_path()
        
        return super().itemChange(change, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dictionary"""
        return {
            'node_id': self.node_id,
            'title': self.title,
            'category': self.category,
            'position': {'x': self.pos().x(), 'y': self.pos().y()},
            'parameters': self.parameters.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualNode':
        """Deserialize node from dictionary"""
        node = cls(data['node_id'], data['title'], data.get('category', 'General'))
        pos = data.get('position', {'x': 0, 'y': 0})
        node.setPos(pos['x'], pos['y'])
        node.parameters = data.get('parameters', {})
        return node
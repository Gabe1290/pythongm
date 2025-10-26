#!/usr/bin/env python3
"""
Node Connection - Represents connections between node ports
"""

from typing import Optional
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainterPath, QPen, QColor


class NodeConnection(QGraphicsPathItem):
    """Represents a connection/wire between two node ports"""
    
    def __init__(self, source_port, target_port=None):
        super().__init__()
        
        self.source_port = source_port
        self.target_port = target_port
        
        # Visual properties
        self.setPen(QPen(QColor("#FFFFFF"), 3))
        self.setZValue(-1)  # Draw behind nodes
        
        # Add to port's connection list
        if source_port:
            source_port.connections.append(self)
        if target_port:
            target_port.connections.append(self)
        
        self.update_path()
    
    def set_target_port(self, target_port):
        """Set the target port"""
        if self.target_port:
            self.target_port.connections.remove(self)
        
        self.target_port = target_port
        if target_port:
            target_port.connections.append(self)
        
        self.update_path()
    
    def set_temp_end_position(self, pos: QPointF):
        """Set temporary end position (for dragging)"""
        self.temp_end = pos
        self.update_path()
    
    def update_path(self):
        """Update the connection path"""
        if not self.source_port or not self.source_port.position:
            return
        
        # Get source position
        source_node = None
        for item in self.scene().items() if self.scene() else []:
            from .visual_node import VisualNode
            if isinstance(item, VisualNode):
                if self.source_port in item.input_ports + item.output_ports:
                    source_node = item
                    break
        
        if not source_node:
            return
        
        start_pos = source_node.get_port_scene_position(self.source_port)
        
        # Get target position
        if self.target_port:
            target_node = None
            for item in self.scene().items() if self.scene() else []:
                from .visual_node import VisualNode
                if isinstance(item, VisualNode):
                    if self.target_port in item.input_ports + item.output_ports:
                        target_node = item
                        break
            
            if target_node:
                end_pos = target_node.get_port_scene_position(self.target_port)
            else:
                return
        elif hasattr(self, 'temp_end'):
            end_pos = self.temp_end
        else:
            return
        
        # Create bezier curve path
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calculate control points for smooth curve
        distance = abs(end_pos.x() - start_pos.x())
        ctrl_offset = min(distance * 0.5, 100)
        
        ctrl1 = QPointF(start_pos.x() + ctrl_offset, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - ctrl_offset, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        
        self.setPath(path)
        
        # Set color based on port type
        if self.source_port.is_execution():
            self.setPen(QPen(QColor("#FF6B6B"), 3))  # Red for execution
        else:
            self.setPen(QPen(QColor("#4ECDC4"), 3))  # Cyan for data
    
    def remove(self):
        """Remove this connection"""
        # Remove from ports
        if self.source_port and self in self.source_port.connections:
            self.source_port.connections.remove(self)
        if self.target_port and self in self.target_port.connections:
            self.target_port.connections.remove(self)
        
        # Remove from scene
        if self.scene():
            self.scene().removeItem(self)
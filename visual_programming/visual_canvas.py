#!/usr/bin/env python3
"""
Visual Canvas - Canvas for node-based visual programming
"""

from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QWheelEvent, QMouseEvent, QKeyEvent

from .visual_node import VisualNode, NodePort, PortType
from .connection import NodeConnection


class VisualCanvas(QGraphicsView):
    """Canvas for visual node-based programming"""
    
    # Signals
    node_selected = Signal(object)  # VisualNode
    node_deselected = Signal()
    nodes_modified = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Visual settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setBackgroundBrush(QColor("#2B2B2B"))
        
        # Grid settings
        self.show_grid = True
        self.grid_size = 20
        
        # Zoom settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        
        # Pan settings
        self.is_panning = False
        self.pan_start_pos = QPointF()
        
        # Connection creation
        self.temp_connection: Optional[NodeConnection] = None
        self.connection_start_port: Optional[NodePort] = None
        
        # Node tracking
        self.nodes: List[VisualNode] = []
        self.connections: List[NodeConnection] = []
        
        # Selection
        self.setMouseTracking(True)
    
    def add_node(self, node: VisualNode, position: QPointF = None):
        """Add a node to the canvas"""
        if position:
            node.setPos(position)
        
        self.scene.addItem(node)
        self.nodes.append(node)
        self.nodes_modified.emit()
        
        return node
    
    def remove_node(self, node: VisualNode):
        """Remove a node from the canvas"""
        if node not in self.nodes:
            return
        
        # Remove all connections to/from this node
        ports_to_check = node.input_ports + node.output_ports
        for port in ports_to_check:
            connections_copy = port.connections.copy()
            for connection in connections_copy:
                self.remove_connection(connection)
        
        # Remove node
        self.scene.removeItem(node)
        self.nodes.remove(node)
        self.nodes_modified.emit()
    
    def add_connection(self, source_port: NodePort, target_port: NodePort) -> Optional[NodeConnection]:
        """Add a connection between two ports"""
        # Validate connection
        if not source_port.can_connect_to(target_port):
            print(f"Cannot connect {source_port.name} to {target_port.name}")
            return None
        
        # Ensure source is output and target is input
        if source_port.is_input():
            source_port, target_port = target_port, source_port
        
        # For execution ports, remove existing output connections
        if source_port.is_execution():
            # Remove existing connections from this output
            connections_copy = source_port.connections.copy()
            for conn in connections_copy:
                self.remove_connection(conn)
        
        # For input ports, remove existing connections
        if target_port.is_input():
            connections_copy = target_port.connections.copy()
            for conn in connections_copy:
                self.remove_connection(conn)
        
        # Create new connection
        connection = NodeConnection(source_port, target_port)
        self.scene.addItem(connection)
        self.connections.append(connection)
        self.nodes_modified.emit()
        
        return connection
    
    def remove_connection(self, connection: NodeConnection):
        """Remove a connection"""
        if connection in self.connections:
            self.connections.remove(connection)
        connection.remove()
        self.nodes_modified.emit()
    
    def clear_all(self):
        """Clear all nodes and connections"""
        # Remove all connections
        for connection in self.connections.copy():
            self.remove_connection(connection)
        
        # Remove all nodes
        for node in self.nodes.copy():
            self.remove_node(node)
    
    def get_node_at_position(self, pos: QPointF) -> Optional[VisualNode]:
        """Get node at scene position"""
        items = self.scene.items(pos)
        for item in items:
            if isinstance(item, VisualNode):
                return item
        return None
    
    def get_port_at_position(self, scene_pos: QPointF) -> Optional[tuple]:
        """Get port at scene position, returns (node, port) or None"""
        for node in self.nodes:
            item_pos = node.mapFromScene(scene_pos)
            port = node.find_port_at_position(item_pos)
            if port:
                return (node, port)
        return None
    
    def drawBackground(self, painter: QPainter, rect):
        """Draw background with grid"""
        super().drawBackground(painter, rect)
        
        if not self.show_grid:
            return
        
        # Draw grid
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        # Grid lines
        lines = []
        x = left
        while x < rect.right():
            lines.append((x, rect.top(), x, rect.bottom()))
            x += self.grid_size
        
        y = top
        while y < rect.bottom():
            lines.append((rect.left(), y, rect.right(), y))
            y += self.grid_size
        
        # Draw lines
        painter.setPen(QColor("#3B3B3B"))
        for line in lines:
            painter.drawLine(line[0], line[1], line[2], line[3])
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with mouse wheel"""
        # Calculate zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        # Calculate new zoom level
        new_zoom = self.zoom_factor * zoom_factor
        
        # Clamp zoom
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        
        # Apply zoom
        self.scale(zoom_factor, zoom_factor)
        self.zoom_factor = new_zoom
        
        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == Qt.MiddleButton:
            # Start panning
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        
        elif event.button() == Qt.LeftButton:
            # Check if clicking on a port to start connection
            port_result = self.get_port_at_position(scene_pos)
            
            if port_result:
                node, port = port_result
                # Start creating connection
                self.connection_start_port = port
                self.temp_connection = NodeConnection(port)
                self.scene.addItem(self.temp_connection)
                self.temp_connection.set_temp_end_position(scene_pos)
                return
            
            # Check if clicking on a node
            node = self.get_node_at_position(scene_pos)
            if node:
                self.node_selected.emit(node)
            else:
                self.node_deselected.emit()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        scene_pos = self.mapToScene(event.pos())
        
        if self.is_panning:
            # Pan the view
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()
            
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            return
        
        if self.temp_connection:
            # Update temporary connection end position
            self.temp_connection.set_temp_end_position(scene_pos)
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == Qt.MiddleButton:
            # Stop panning
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
            return
        
        elif event.button() == Qt.LeftButton:
            if self.temp_connection and self.connection_start_port:
                # Try to complete connection
                port_result = self.get_port_at_position(scene_pos)
                
                if port_result:
                    node, target_port = port_result
                    
                    # Try to create connection
                    connection = self.add_connection(self.connection_start_port, target_port)
                    
                    if not connection:
                        # Connection failed, remove temp connection
                        self.scene.removeItem(self.temp_connection)
                    else:
                        # Connection succeeded, remove temp connection and use real one
                        self.scene.removeItem(self.temp_connection)
                else:
                    # No target port, remove temp connection
                    self.scene.removeItem(self.temp_connection)
                
                # Clear temporary connection
                self.temp_connection = None
                self.connection_start_port = None
                return
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press"""
        if event.key() == Qt.Key_Delete:
            # Delete selected nodes
            selected_items = self.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, VisualNode):
                    self.remove_node(item)
                elif isinstance(item, NodeConnection):
                    self.remove_connection(item)
        
        elif event.key() == Qt.Key_F:
            # Frame all nodes
            self.frame_all()
        
        super().keyPressEvent(event)
    
    def frame_all(self):
        """Frame all nodes in view"""
        if not self.nodes:
            return
        
        rect = self.scene.itemsBoundingRect()
        self.fitInView(rect, Qt.KeepAspectRatio)
        self.zoom_factor = self.transform().m11()
    
    def contextMenuEvent(self, event):
        """Show context menu"""
        menu = QMenu(self)
        
        scene_pos = self.mapToScene(event.pos())
        item = self.get_node_at_position(scene_pos)
        
        if item and isinstance(item, VisualNode):
            # Node context menu
            delete_action = menu.addAction("Delete Node")
            delete_action.triggered.connect(lambda: self.remove_node(item))
        else:
            # Canvas context menu
            frame_action = menu.addAction("Frame All (F)")
            frame_action.triggered.connect(self.frame_all)
            
            menu.addSeparator()
            
            grid_action = menu.addAction("Toggle Grid")
            grid_action.setCheckable(True)
            grid_action.setChecked(self.show_grid)
            grid_action.triggered.connect(self.toggle_grid)
        
        menu.exec(event.globalPos())
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.show_grid = not self.show_grid
        self.viewport().update()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize canvas to dictionary"""
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'connections': [
                {
                    'source_node': self._get_node_id_for_port(conn.source_port),
                    'source_port': conn.source_port.name,
                    'target_node': self._get_node_id_for_port(conn.target_port),
                    'target_port': conn.target_port.name
                }
                for conn in self.connections if conn.source_port and conn.target_port
            ]
        }
    
    def _get_node_id_for_port(self, port: NodePort) -> Optional[str]:
        """Get node ID for a port"""
        for node in self.nodes:
            if port in node.input_ports + node.output_ports:
                return node.node_id
        return None
    
    def from_dict(self, data: Dict[str, Any], node_factory):
        """Deserialize canvas from dictionary"""
        self.clear_all()
        
        # Create nodes
        node_map = {}
        for node_data in data.get('nodes', []):
            node = node_factory(node_data)
            if node:
                self.add_node(node)
                node_map[node.node_id] = node
        
        # Create connections
        for conn_data in data.get('connections', []):
            source_node = node_map.get(conn_data['source_node'])
            target_node = node_map.get(conn_data['target_node'])
            
            if not source_node or not target_node:
                continue
            
            # Find ports
            source_port = None
            target_port = None
            
            for port in source_node.output_ports:
                if port.name == conn_data['source_port']:
                    source_port = port
                    break
            
            for port in target_node.input_ports:
                if port.name == conn_data['target_port']:
                    target_port = port
                    break
            
            if source_port and target_port:
                self.add_connection(source_port, target_port)
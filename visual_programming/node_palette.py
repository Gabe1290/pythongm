#!/usr/bin/env python3
"""
Node Palette - Library of available nodes for visual programming
"""

from typing import Dict, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                                QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag, QFont

from .node_types import get_node_types, NodeTypeDefinition, create_node_from_type


class NodePalette(QWidget):
    """Palette widget showing available node types"""
    
    # Signals
    node_requested = Signal(str)  # type_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.node_types = get_node_types()
        self.setup_ui()
        self.populate_tree()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Node Library")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(title)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search nodes...")
        self.search_box.textChanged.connect(self.filter_nodes)
        layout.addWidget(self.search_box)
        
        # Node tree
        self.node_tree = QTreeWidget()
        self.node_tree.setHeaderLabel("Nodes")
        self.node_tree.setDragEnabled(True)
        self.node_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.node_tree)
        
        # Info label
        self.info_label = QLabel("Double-click or drag to add node")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(self.info_label)
    
    def populate_tree(self):
        """Populate the tree with node types"""
        self.node_tree.clear()
        
        # Group nodes by category
        categories = {}
        for type_id, node_def in self.node_types.items():
            category = node_def.category
            if category not in categories:
                categories[category] = []
            categories[category].append((type_id, node_def))
        
        # Add categories and nodes
        for category_name in sorted(categories.keys()):
            category_item = QTreeWidgetItem(self.node_tree)
            category_item.setText(0, category_name)
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsDragEnabled)
            
            # Set category styling
            font = QFont("Arial", 9, QFont.Bold)
            category_item.setFont(0, font)
            
            # Add nodes to category
            for type_id, node_def in sorted(categories[category_name], key=lambda x: x[1].display_name):
                node_item = QTreeWidgetItem(category_item)
                node_item.setText(0, node_def.display_name)
                node_item.setData(0, Qt.UserRole, type_id)
                node_item.setToolTip(0, node_def.description)
                
                # Color indicator
                from PySide6.QtGui import QColor, QBrush
                color = QColor(node_def.color)
                color.setAlpha(100)
                node_item.setBackground(0, QBrush(color))
            
            category_item.setExpanded(True)
    
    def filter_nodes(self, text: str):
        """Filter nodes based on search text"""
        text = text.lower()
        
        # Show/hide items based on search
        for i in range(self.node_tree.topLevelItemCount()):
            category_item = self.node_tree.topLevelItem(i)
            category_visible = False
            
            for j in range(category_item.childCount()):
                node_item = category_item.child(j)
                node_text = node_item.text(0).lower()
                
                if text in node_text or not text:
                    node_item.setHidden(False)
                    category_visible = True
                else:
                    node_item.setHidden(True)
            
            category_item.setHidden(not category_visible)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double click on node item"""
        type_id = item.data(0, Qt.UserRole)
        if type_id:
            self.node_requested.emit(type_id)
    
    def mousePressEvent(self, event):
        """Start drag operation"""
        if event.button() == Qt.LeftButton:
            item = self.node_tree.itemAt(self.node_tree.mapFromGlobal(event.globalPosition().toPoint()))
            if item:
                type_id = item.data(0, Qt.UserRole)
                if type_id:
                    # Start drag
                    drag = QDrag(self)
                    mime_data = QMimeData()
                    mime_data.setText(type_id)
                    drag.setMimeData(mime_data)
                    drag.exec(Qt.CopyAction)
        
        super().mousePressEvent(event)
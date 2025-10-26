#!/usr/bin/env python3
"""
PyGameMaker IDE with Room Editor
A complete IDE resembling GameMaker 8.1 with visual room editing capabilities
Built with PySide6
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QVBoxLayout, QHBoxLayout, QWidget, 
    QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel, QFrame,
    QFormLayout, QLineEdit, QGroupBox, QScrollArea, QGridLayout, QPushButton,
    QTabWidget, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QDialog, QDialogButtonBox, QSpinBox, QCheckBox, QColorDialog, QGraphicsView,
    QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QSlider, QToolBar,
    QStatusBar, QComboBox, QTextBrowser, QSizePolicy, QGraphicsItem
)
from PySide6.QtCore import Qt, QSize, Signal, QRectF, QPointF, QTimer
from PySide6.QtGui import (
    QAction, QFont, QPixmap, QPainter, QColor, QPen, QBrush, 
    QKeySequence, QIcon, QCursor, QWheelEvent, QMouseEvent, QActionGroup
)


class WelcomeTab(QWidget):
    """Welcome tab shown when no editors are open"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Welcome message
        title = QLabel("Welcome to PyGameMaker IDE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        subtitle = QLabel("Create amazing 2D games with visual scripting")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #666; margin: 10px;")
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.Box)
        actions_frame.setMaximumWidth(400)
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel("Quick Actions")
        actions_title.setAlignment(Qt.AlignCenter)
        actions_title.setStyleSheet("font-weight: bold; margin: 10px;")
        
        new_project_btn = QPushButton("📁 New Project (Ctrl+N)")
        open_project_btn = QPushButton("📂 Open Project (Ctrl+O)")
        new_room_btn = QPushButton("🏠 Create Room (Ctrl+R)")
        
        for btn in [new_project_btn, open_project_btn, new_room_btn]:
            btn.setStyleSheet("QPushButton { padding: 8px; margin: 2px; text-align: left; }")
        
        actions_layout.addWidget(actions_title)
        actions_layout.addWidget(new_project_btn)
        actions_layout.addWidget(open_project_btn)
        actions_layout.addWidget(new_room_btn)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(actions_frame)


class RoomEditor(QWidget):
    """Visual room editor widget"""
    
    # Signals
    room_modified = Signal(str)  # room_name
    
    def __init__(self, room_name: str, room_data: Dict[str, Any]):
        super().__init__()
        self.room_name = room_name
        self.room_data = room_data
        self.is_modified = False
        self.zoom_factor = 1.0
        self.grid_size = 32
        self.show_grid = True
        
        self.setup_ui()
        self.setup_room()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QToolBar()
        
        # Grid controls
        self.grid_action = QAction("🔲 Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(self.grid_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_out_action = QAction("🔍➖", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        self.zoom_label = QLabel("100%")
        toolbar.addWidget(self.zoom_label)
        
        zoom_in_action = QAction("🔍➕", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        toolbar.addSeparator()
        
        # Room settings
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_room_settings)
        toolbar.addAction(settings_action)
        
        layout.addWidget(toolbar)
        
        # Graphics view for room editing
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        
        layout.addWidget(self.graphics_view)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.coords_label = QLabel("X: 0, Y: 0")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.coords_label)
        
        layout.addLayout(status_layout)
    
    def setup_room(self):
        """Setup the room based on room_data"""
        # Clear scene
        self.graphics_scene.clear()
        
        # Get room dimensions
        width = self.room_data.get('width', 800)
        height = self.room_data.get('height', 600)
        
        # Set scene rectangle
        self.graphics_scene.setSceneRect(0, 0, width, height)
        
        # Draw room boundaries
        boundary_pen = QPen(QColor(255, 0, 0), 2, Qt.DashLine)
        self.graphics_scene.addRect(0, 0, width, height, boundary_pen)
        
        # Draw grid if enabled
        self.update_grid()
        
        # Add background if specified
        bg_color = QColor(self.room_data.get('background_color', '#87CEEB'))
        self.graphics_scene.setBackgroundBrush(QBrush(bg_color))
        
        # Add instances (objects placed in room)
        instances = self.room_data.get('instances', [])
        for instance in instances:
            self.add_instance(instance)
    
    def update_grid(self):
        """Update grid display"""
        if not self.show_grid:
            return
        
        width = self.room_data.get('width', 800)
        height = self.room_data.get('height', 600)
        
        grid_pen = QPen(QColor(200, 200, 200), 1, Qt.DotLine)
        
        # Vertical grid lines
        for x in range(0, width + 1, self.grid_size):
            self.graphics_scene.addLine(x, 0, x, height, grid_pen)
        
        # Horizontal grid lines
        for y in range(0, height + 1, self.grid_size):
            self.graphics_scene.addLine(0, y, width, y, grid_pen)
    
    def add_instance(self, instance_data: Dict[str, Any]):
        """Add an object instance to the room"""
        x = instance_data.get('x', 0)
        y = instance_data.get('y', 0)
        obj_name = instance_data.get('object', 'unknown')
        
        # Create a simple rectangle for now
        rect_item = QGraphicsRectItem(0, 0, 32, 32)
        rect_item.setPos(x, y)
        rect_item.setBrush(QBrush(QColor(100, 150, 255)))
        rect_item.setPen(QPen(QColor(0, 0, 0)))
        rect_item.setFlag(QGraphicsItem.ItemIsMovable, True)
        rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        self.graphics_scene.addItem(rect_item)
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.show_grid = self.grid_action.isChecked()
        self.setup_room()  # Refresh room display
    
    def zoom_in(self):
        """Zoom in the view"""
        self.zoom_factor *= 1.2
        self.graphics_view.setTransform(self.graphics_view.transform().scale(1.2, 1.2))
        self.update_zoom_label()
    
    def zoom_out(self):
        """Zoom out the view"""
        self.zoom_factor /= 1.2
        self.graphics_view.setTransform(self.graphics_view.transform().scale(1/1.2, 1/1.2))
        self.update_zoom_label()
    
    def update_zoom_label(self):
        """Update zoom percentage label"""
        percentage = int(self.zoom_factor * 100)
        self.zoom_label.setText(f"{percentage}%")
    
    def show_room_settings(self):
        """Show room settings dialog"""
        dialog = RoomSettingsDialog(self.room_data, self)
        if dialog.exec() == QDialog.Accepted:
            self.room_data.update(dialog.get_room_data())
            self.setup_room()
            self.mark_modified()
    
    def mark_modified(self):
        """Mark room as modified"""
        if not self.is_modified:
            self.is_modified = True
            self.room_modified.emit(self.room_name)
    
    def get_room_data(self) -> Dict[str, Any]:
        """Get current room data"""
        return self.room_data.copy()


class RoomSettingsDialog(QDialog):
    """Dialog for editing room settings"""
    
    def __init__(self, room_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.room_data = room_data.copy()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Room Settings")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Room properties
        form_layout = QFormLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 4000)
        self.width_spin.setValue(self.room_data.get('width', 800))
        form_layout.addRow("Width:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 4000)
        self.height_spin.setValue(self.room_data.get('height', 600))
        form_layout.addRow("Height:", self.height_spin)
        
        # Background color
        self.bg_color_btn = QPushButton()
        self.bg_color = QColor(self.room_data.get('background_color', '#87CEEB'))
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color.name()}")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        form_layout.addRow("Background Color:", self.bg_color_btn)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def choose_bg_color(self):
        """Choose background color"""
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.bg_color = color
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
    
    def get_room_data(self) -> Dict[str, Any]:
        """Get the updated room data"""
        return {
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'background_color': self.bg_color.name(),
            'instances': self.room_data.get('instances', [])
        }


class AssetTreeWidget(QTreeWidget):
    """Enhanced asset tree widget with context menus"""
    
    # Signals
    asset_double_clicked = Signal(str, str)  # asset_type, asset_name
    
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Project Assets")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.project_data = {}
        self.setup_asset_tree()
    
    def setup_asset_tree(self):
        """Setup the asset tree with GameMaker-style categories"""
        self.clear()
        
        # Define asset categories
        categories = [
            ("Sprites", "🖼️"),
            ("Sounds", "🔊"),
            ("Backgrounds", "🖼️"),
            ("Objects", "📦"),
            ("Rooms", "🏠"),
            ("Scripts", "📜"),
            ("Fonts", "🔤")
        ]
        
        for category, icon in categories:
            category_item = QTreeWidgetItem([f"{icon} {category}"])
            category_item.setData(0, Qt.UserRole, {'type': 'category', 'name': category.lower()})
            self.addTopLevelItem(category_item)
            
            # Add assets from project data
            assets = self.project_data.get('assets', {}).get(category.lower(), {})
            for asset_name, asset_data in assets.items():
                asset_item = QTreeWidgetItem([asset_name])
                asset_item.setData(0, Qt.UserRole, {'type': 'asset', 'category': category.lower(), 'name': asset_name})
                category_item.addChild(asset_item)
        
        self.expandAll()
    
    def load_project(self, project_data: Dict[str, Any]):
        """Load project data and refresh tree"""
        self.project_data = project_data
        self.setup_asset_tree()
    
    def add_asset(self, category: str, name: str, data: Dict[str, Any]):
        """Add a new asset to the tree"""
        if 'assets' not in self.project_data:
            self.project_data['assets'] = {}
        
        if category not in self.project_data['assets']:
            self.project_data['assets'][category] = {}
        
        self.project_data['assets'][category][name] = data
        self.setup_asset_tree()
    
    def show_context_menu(self, position):
        """Show context menu for tree items"""
        item = self.itemAt(position)
        if not item:
            return
        
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        menu = self.create_context_menu(item_data)
        if menu:
            menu.exec(self.mapToGlobal(position))
    
    def create_context_menu(self, item_data: Dict[str, Any]):
        """Create appropriate context menu based on item type"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        if item_data['type'] == 'category':
            category = item_data['name']
            if category == 'rooms':
                menu.addAction("📁 New Room", lambda: self.create_room())
            elif category == 'sprites':
                menu.addAction("🖼️ Import Sprite", lambda: self.import_sprite())
            elif category == 'sounds':
                menu.addAction("🔊 Import Sound", lambda: self.import_sound())
            elif category == 'objects':
                menu.addAction("📦 New Object", lambda: self.create_object())
            elif category == 'scripts':
                menu.addAction("📜 New Script", lambda: self.create_script())
        
        elif item_data['type'] == 'asset':
            category = item_data['category']
            name = item_data['name']
            
            if category == 'rooms':
                menu.addAction("✏️ Edit Room", lambda: self.edit_room(name))
            
            menu.addSeparator()
            menu.addAction("📋 Duplicate", lambda: self.duplicate_asset(category, name))
            menu.addAction("✏️ Rename", lambda: self.rename_asset(category, name))
            menu.addAction("🗑️ Delete", lambda: self.delete_asset(category, name))
        
        return menu if menu.actions() else None
    
    def on_item_double_clicked(self, item, column):
        """Handle double-click on items"""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data['type'] == 'asset':
            category = item_data['category']
            name = item_data['name']
            self.asset_double_clicked.emit(category, name)
    
    def create_room(self):
        """Create a new room"""
        self.parent().parent().parent().create_new_room()  # Navigate to main window
    
    def edit_room(self, room_name: str):
        """Edit an existing room"""
        self.asset_double_clicked.emit('rooms', room_name)
    
    def import_sprite(self):
        """Import a sprite (placeholder)"""
        QMessageBox.information(self, "Import Sprite", "Sprite import not yet implemented")
    
    def import_sound(self):
        """Import a sound (placeholder)"""
        QMessageBox.information(self, "Import Sound", "Sound import not yet implemented")
    
    def create_object(self):
        """Create a new object (placeholder)"""
        QMessageBox.information(self, "Create Object", "Object creation not yet implemented")
    
    def create_script(self):
        """Create a new script (placeholder)"""
        QMessageBox.information(self, "Create Script", "Script creation not yet implemented")
    
    def duplicate_asset(self, category: str, name: str):
        """Duplicate an asset (placeholder)"""
        QMessageBox.information(self, "Duplicate Asset", f"Duplicating {category}/{name} not yet implemented")
    
    def rename_asset(self, category: str, name: str):
        """Rename an asset (placeholder)"""
        QMessageBox.information(self, "Rename Asset", f"Renaming {category}/{name} not yet implemented")
    
    def delete_asset(self, category: str, name: str):
        """Delete an asset"""
        reply = QMessageBox.question(
            self, "Delete Asset", 
            f"Are you sure you want to delete {category}/{name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from project data
            if (category in self.project_data.get('assets', {}) and 
                name in self.project_data['assets'][category]):
                del self.project_data['assets'][category][name]
                self.setup_asset_tree()


class PropertiesWidget(QWidget):
    """Enhanced properties widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_asset = None
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Asset info
        info_group = QGroupBox("Asset Information")
        info_layout = QFormLayout(info_group)
        
        self.name_label = QLabel("No asset selected")
        self.type_label = QLabel("-")
        self.status_label = QLabel("-")
        
        info_layout.addRow("Name:", self.name_label)
        info_layout.addRow("Type:", self.type_label)
        info_layout.addRow("Status:", self.status_label)
        
        layout.addWidget(info_group)
        
        # Properties
        self.properties_group = QGroupBox("Properties")
        self.properties_layout = QFormLayout(self.properties_group)
        layout.addWidget(self.properties_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("No preview available")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        
        layout.addStretch()
    
    def show_asset_properties(self, asset_type: str, asset_name: str, asset_data: Dict[str, Any]):
        """Show properties for an asset"""
        self.current_asset = (asset_type, asset_name, asset_data)
        
        # Update info
        self.name_label.setText(asset_name)
        self.type_label.setText(asset_type.title())
        self.status_label.setText("Loaded")
        
        # Clear previous properties
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add properties based on asset type
        if asset_type == 'rooms':
            width_edit = QLineEdit(str(asset_data.get('width', 800)))
            height_edit = QLineEdit(str(asset_data.get('height', 600)))
            bg_color_edit = QLineEdit(asset_data.get('background_color', '#87CEEB'))
            
            self.properties_layout.addRow("Width:", width_edit)
            self.properties_layout.addRow("Height:", height_edit)
            self.properties_layout.addRow("Background:", bg_color_edit)
            
            # Update preview
            self.preview_label.setText(f"Room: {asset_name}\n{asset_data.get('width', 800)} x {asset_data.get('height', 600)}")
        
        elif asset_type == 'sprites':
            # Sprite properties
            frames_edit = QLineEdit(str(asset_data.get('frames', 1)))
            origin_x_edit = QLineEdit(str(asset_data.get('origin_x', 0)))
            origin_y_edit = QLineEdit(str(asset_data.get('origin_y', 0)))
            
            self.properties_layout.addRow("Frames:", frames_edit)
            self.properties_layout.addRow("Origin X:", origin_x_edit)
            self.properties_layout.addRow("Origin Y:", origin_y_edit)
            
            self.preview_label.setText(f"Sprite: {asset_name}\nFrames: {asset_data.get('frames', 1)}")
        
        else:
            # Generic properties
            for key, value in asset_data.items():
                if key not in ['name', 'type']:
                    prop_edit = QLineEdit(str(value))
                    self.properties_layout.addRow(f"{key.title()}:", prop_edit)
            
            self.preview_label.setText(f"{asset_type.title()}: {asset_name}")


class GameMakerIDE(QMainWindow):
    """Main IDE window with room editor integration"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyGameMaker IDE v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Project state
        self.current_project_path = None
        self.project_data = {}
        self.unsaved_changes = False
        
        # Editor tabs
        self.open_editors = {}  # name -> editor_widget
        self.modified_editors = set()
        
        self.setup_ui()
        self.create_sample_project()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create horizontal splitter for three panes
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left pane - Asset tree
        self.asset_tree = AssetTreeWidget()
        self.asset_tree.setMinimumWidth(200)
        self.asset_tree.setMaximumWidth(300)
        self.asset_tree.asset_double_clicked.connect(self.open_asset_editor)
        
        # Center pane - Tabbed editors
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Add welcome tab
        self.welcome_tab = WelcomeTab()
        self.editor_tabs.addTab(self.welcome_tab, "Welcome")
        
        # Right pane - Properties
        self.properties_widget = PropertiesWidget()
        self.properties_widget.setMinimumWidth(250)
        self.properties_widget.setMaximumWidth(350)
        
        # Add to splitter
        main_splitter.addWidget(self.asset_tree)
        main_splitter.addWidget(self.editor_tabs)
        main_splitter.addWidget(self.properties_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([250, 800, 300])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        main_splitter.setCollapsible(2, False)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(main_splitter)
        
        # Set styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 3px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSplitter::handle {
                background-color: #ccc;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #999;
            }
        """)
    
    def create_menu_bar(self):
        """Create comprehensive menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save Project", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        recent_menu = file_menu.addMenu("Recent Projects")
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("&Undo", self.undo, QKeySequence.Undo)
        edit_menu.addAction("&Redo", self.redo, QKeySequence.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Cu&t", self.cut, QKeySequence.Cut)
        edit_menu.addAction("&Copy", self.copy, QKeySequence.Copy)
        edit_menu.addAction("&Paste", self.paste, QKeySequence.Paste)
        edit_menu.addSeparator()
        edit_menu.addAction("&Preferences...", self.show_preferences)
        
        # Assets menu
        assets_menu = menubar.addMenu("&Assets")
        assets_menu.addAction("📁 &Import Sprite...", self.import_sprite)
        assets_menu.addAction("🔊 Import &Sound...", self.import_sound)
        assets_menu.addAction("🖼️ Import &Background...", self.import_background)
        assets_menu.addSeparator()
        assets_menu.addAction("📦 Create &Object", self.create_object)
        
        create_room_action = QAction("🏠 Create &Room", self)
        create_room_action.setShortcut("Ctrl+R")
        create_room_action.triggered.connect(self.create_new_room)
        assets_menu.addAction(create_room_action)
        
        assets_menu.addAction("📜 Create &Script", self.create_script)
        assets_menu.addAction("🔤 Create &Font", self.create_font)
        assets_menu.addSeparator()
        assets_menu.addAction("✏️ Edit Selected Room", self.edit_selected_room)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("🏠 &Room Editor", self.open_room_editor)
        tools_menu.addSeparator()
        tools_menu.addAction("🔨 &Compile Game", self.compile_game)
        tools_menu.addAction("▶️ &Run Game", self.run_game)
        
        # Window menu
        window_menu = menubar.addMenu("&Window")
        window_menu.addAction("💾 Save &All", self.save_all_editors)
        window_menu.addSeparator()
        window_menu.addAction("❌ &Close Current Editor", self.close_current_editor)
        window_menu.addAction("❌ Close &All Editors", self.close_all_editors)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("📚 &Documentation", self.show_documentation)
        help_menu.addAction("🎓 &Tutorials", self.show_tutorials)
        help_menu.addSeparator()
        help_menu.addAction("ℹ️ &About", self.show_about)
    
    def create_toolbar(self):
        """Create main toolbar"""
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        
        # File operations
        toolbar.addAction("📁 New", self.new_project)
        toolbar.addAction("📂 Open", self.open_project)
        toolbar.addAction("💾 Save", self.save_project)
        toolbar.addSeparator()
        
        # Asset creation
        toolbar.addAction("🏠 Room", self.create_new_room)
        toolbar.addAction("📦 Object", self.create_object)
        toolbar.addAction("🖼️ Sprite", self.import_sprite)
        toolbar.addSeparator()
        
        # Game operations
        toolbar.addAction("▶️ Run", self.run_game)
        toolbar.addAction("🔨 Build", self.compile_game)
    
    def create_sample_project(self):
        """Create a sample project for demonstration"""
        self.project_data = {
            'name': 'Sample Project',
            'version': '1.0',
            'assets': {
                'rooms': {
                    'room_main': {
                        'width': 800,
                        'height': 600,
                        'background_color': '#87CEEB',
                        'instances': []
                    },
                    'room_menu': {
                        'width': 640,
                        'height': 480,
                        'background_color': '#2C3E50',
                        'instances': []
                    }
                },
                'sprites': {
                    'spr_player': {'frames': 1, 'origin_x': 16, 'origin_y': 16},
                    'spr_enemy': {'frames': 2, 'origin_x': 16, 'origin_y': 16}
                },
                'objects': {
                    'obj_player': {'sprite': 'spr_player'},
                    'obj_enemy': {'sprite': 'spr_enemy'}
                }
            }
        }
        
        self.asset_tree.load_project(self.project_data)
        self.status_bar.showMessage("Sample project loaded")
    
    def open_asset_editor(self, asset_type: str, asset_name: str):
        """Open editor for an asset"""
        if asset_type == 'rooms':
            self.open_room_editor_for_room(asset_name)
        else:
            QMessageBox.information(self, "Editor", f"Editor for {asset_type} not yet implemented")
    
    def open_room_editor_for_room(self, room_name: str):
        """Open room editor for a specific room"""
        # Check if already open
        if room_name in self.open_editors:
            # Switch to existing tab
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) == self.open_editors[room_name]:
                    self.editor_tabs.setCurrentIndex(i)
                    return
        
        # Get room data
        room_data = self.project_data.get('assets', {}).get('rooms', {}).get(room_name, {})
        if not room_data:
            QMessageBox.warning(self, "Error", f"Room '{room_name}' not found")
            return
        
        # Create room editor
        room_editor = RoomEditor(room_name, room_data)
        room_editor.room_modified.connect(self.on_room_modified)
        
        # Add tab
        tab_index = self.editor_tabs.addTab(room_editor, f"🏠 {room_name}")
        self.editor_tabs.setCurrentIndex(tab_index)
        
        # Track editor
        self.open_editors[room_name] = room_editor
        
        # Hide welcome tab if it exists
        if hasattr(self, 'welcome_tab'):
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) == self.welcome_tab:
                    self.editor_tabs.removeTab(i)
                    break
    
    def on_room_modified(self, room_name: str):
        """Handle room modification"""
        self.modified_editors.add(room_name)
        self.unsaved_changes = True
        self.update_tab_title(room_name)
        self.status_bar.showMessage(f"Room '{room_name}' modified")
    
    def update_tab_title(self, editor_name: str):
        """Update tab title to show modification status"""
        if editor_name in self.open_editors:
            editor = self.open_editors[editor_name]
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) == editor:
                    title = f"🏠 {editor_name}"
                    if editor_name in self.modified_editors:
                        title += "*"
                    self.editor_tabs.setTabText(i, title)
                    break
    
    def close_editor_tab(self, index: int):
        """Close an editor tab"""
        widget = self.editor_tabs.widget(index)
        
        # Find the editor name
        editor_name = None
        for name, editor in self.open_editors.items():
            if editor == widget:
                editor_name = name
                break
        
        if editor_name:
            # Check for unsaved changes
            if editor_name in self.modified_editors:
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"'{editor_name}' has unsaved changes. Save before closing?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Save:
                    self.save_editor(editor_name)
            
            # Remove from tracking
            del self.open_editors[editor_name]
            self.modified_editors.discard(editor_name)
        
        # Remove tab
        self.editor_tabs.removeTab(index)
        
        # Show welcome tab if no editors open
        if self.editor_tabs.count() == 0:
            self.editor_tabs.addTab(self.welcome_tab, "Welcome")
    
    def on_tab_changed(self, index: int):
        """Handle tab change"""
        widget = self.editor_tabs.widget(index)
        
        # Update properties panel based on current editor
        if isinstance(widget, RoomEditor):
            room_data = widget.get_room_data()
            self.properties_widget.show_asset_properties('rooms', widget.room_name, room_data)
    
    def create_new_room(self):
        """Create a new room"""
        from PySide6.QtWidgets import QInputDialog
        
        room_name, ok = QInputDialog.getText(self, "New Room", "Room name:")
        if ok and room_name:
            # Check if room already exists
            if room_name in self.project_data.get('assets', {}).get('rooms', {}):
                QMessageBox.warning(self, "Error", f"Room '{room_name}' already exists")
                return
            
            # Create room data
            room_data = {
                'width': 800,
                'height': 600,
                'background_color': '#87CEEB',
                'instances': []
            }
            
            # Add to project
            if 'assets' not in self.project_data:
                self.project_data['assets'] = {}
            if 'rooms' not in self.project_data['assets']:
                self.project_data['assets']['rooms'] = {}
            
            self.project_data['assets']['rooms'][room_name] = room_data
            
            # Refresh asset tree
            self.asset_tree.load_project(self.project_data)
            
            # Open room editor
            self.open_room_editor_for_room(room_name)
            
            self.status_bar.showMessage(f"Created room '{room_name}'")
    
    def save_editor(self, editor_name: str):
        """Save a specific editor"""
        if editor_name in self.open_editors:
            editor = self.open_editors[editor_name]
            if isinstance(editor, RoomEditor):
                # Update project data with room data
                room_data = editor.get_room_data()
                self.project_data['assets']['rooms'][editor_name] = room_data
                
                # Mark as saved
                self.modified_editors.discard(editor_name)
                self.update_tab_title(editor_name)
                
                self.status_bar.showMessage(f"Saved room '{editor_name}'")
    
    def save_all_editors(self):
        """Save all modified editors"""
        for editor_name in list(self.modified_editors):
            self.save_editor(editor_name)
        
        if self.unsaved_changes:
            self.save_project()
    
    # Menu action implementations
    def new_project(self):
        """Create a new project"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "New Project", "", "JSON Files (*.json)"
        )
        
        if file_path:
            self.project_data = {
                'name': Path(file_path).stem,
                'version': '1.0',
                'assets': {'rooms': {}, 'sprites': {}, 'objects': {}}
            }
            
            self.current_project_path = file_path
            self.asset_tree.load_project(self.project_data)
            self.save_project()
            self.status_bar.showMessage(f"Created new project: {Path(file_path).name}")
    
    def open_project(self):
        """Open an existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.project_data = json.load(f)
                
                self.current_project_path = file_path
                self.asset_tree.load_project(self.project_data)
                self.status_bar.showMessage(f"Opened project: {Path(file_path).name}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project: {e}")
    
    def save_project(self):
        """Save the current project"""
        if not self.current_project_path:
            self.save_project_as()
            return
        
        try:
            # Save all editors first
            for editor_name in list(self.modified_editors):
                self.save_editor(editor_name)
            
            with open(self.current_project_path, 'w') as f:
                json.dump(self.project_data, f, indent=2)
            
            self.unsaved_changes = False
            self.status_bar.showMessage("Project saved")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    
    def save_project_as(self):
        """Save project with new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", "JSON Files (*.json)"
        )
        
        if file_path:
            self.current_project_path = file_path
            self.save_project()
    
    def close_current_editor(self):
        """Close current editor"""
        current_index = self.editor_tabs.currentIndex()
        if current_index >= 0:
            self.close_editor_tab(current_index)
    
    def close_all_editors(self):
        """Close all editors"""
        while self.editor_tabs.count() > 0:
            self.close_editor_tab(0)
    
    # Placeholder methods for unimplemented features
    def undo(self): QMessageBox.information(self, "Info", "Undo not yet implemented")
    def redo(self): QMessageBox.information(self, "Info", "Redo not yet implemented")
    def cut(self): QMessageBox.information(self, "Info", "Cut not yet implemented")
    def copy(self): QMessageBox.information(self, "Info", "Copy not yet implemented")
    def paste(self): QMessageBox.information(self, "Info", "Paste not yet implemented")
    def show_preferences(self): QMessageBox.information(self, "Info", "Preferences not yet implemented")
    
    def import_sprite(self): QMessageBox.information(self, "Info", "Sprite import not yet implemented")
    def import_sound(self): QMessageBox.information(self, "Info", "Sound import not yet implemented")
    def import_background(self): QMessageBox.information(self, "Info", "Background import not yet implemented")
    def create_object(self): QMessageBox.information(self, "Info", "Object creation not yet implemented")
    def create_script(self): QMessageBox.information(self, "Info", "Script creation not yet implemented")
    def create_font(self): QMessageBox.information(self, "Info", "Font creation not yet implemented")
    def edit_selected_room(self): QMessageBox.information(self, "Info", "Edit selected room not yet implemented")
    
    def open_room_editor(self): QMessageBox.information(self, "Info", "Room editor already integrated!")
    def compile_game(self): QMessageBox.information(self, "Info", "Game compilation not yet implemented")
    def run_game(self): QMessageBox.information(self, "Info", "Game execution not yet implemented")
    
    def show_documentation(self): QMessageBox.information(self, "Info", "Documentation not yet implemented")
    def show_tutorials(self): QMessageBox.information(self, "Info", "Tutorials not yet implemented")
    def show_about(self): 
        QMessageBox.about(self, "About", "PyGameMaker IDE v1.0\n\nA GameMaker-inspired 2D game development environment")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PyGameMaker IDE")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = GameMakerIDE()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Asset Tree Item for PyGameMaker IDE
Custom tree widget item for displaying individual game assets
"""

from pathlib import Path
from typing import Dict
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AssetTreeItem(QTreeWidgetItem):
    """Custom tree item for assets"""
    
    def __init__(self, parent=None, asset_type: str = "", asset_name: str = "", asset_data: Dict = None):
        super().__init__(parent)
        
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.asset_data = asset_data or {}
        self.is_category = asset_name == ""
        
        # Create camelCase aliases for compatibility
        self.assetType = asset_type
        self.assetName = asset_name
        self.assetData = asset_data or {}
        self.isCategory = self.is_category
        
        self.setup_item()
    
    def setup_item(self):
        """Setup the appearance and properties of the tree item"""
        if self.is_category:
            # Category item with emojis
            self.setText(0, self.asset_type.title())
            self.setFont(0, QFont("", 9, QFont.Weight.Bold))
            
            # Set category icons with emojis - UPDATED
            icon_map = {
                "sprites": "🖼️ Sprites",
                "sounds": "🔊 Sounds", 
                "backgrounds": "🖼️ Backgrounds",
                "objects": "📦 Objects",
                "rooms": "🏠 Rooms",
                "scripts": "📜 Scripts",
                "fonts": "🔤 Fonts",
                "data": "📄 Data"
            }
            
            if self.asset_type in icon_map:
                self.setText(0, icon_map[self.asset_type])
            
            # Make categories non-selectable but expandable
            self.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDropEnabled)
            
        else:
            # Asset item - keep existing logic but ensure emojis work
            self.setText(0, self.asset_name)
            
            # Check if asset is imported
            asset_imported = self.asset_data.get('imported', False)
            
            if asset_imported:
                # Show imported asset normally with type icons
                self.setForeground(0, Qt.GlobalColor.black)
                
                # Add type-specific icon - UPDATED to match target
                if self.asset_type == "sprites":
                    # Try to load actual sprite image as icon
                    sprite_path = self.asset_data.get('project_path', '')
                    if not self.load_sprite_icon(sprite_path):
                        # Fallback to emoji if image loading fails
                        self.setText(0, f"🖼️ {self.asset_name}")
                    else:
                        self.setText(0, self.asset_name)  # Just name, icon shows the image
                elif self.asset_type == "sounds":
                    self.setText(0, f"🔊 {self.asset_name}")
                elif self.asset_type == "backgrounds":
                    # Try to load actual background image as icon
                    bkg_path = self.asset_data.get('project_path', '')
                    if not self.load_sprite_icon(bkg_path):
                        # Fallback to emoji if image loading fails
                        self.setText(0, f"🖼️ {self.asset_name}")
                    else:
                        self.setText(0, self.asset_name)  # Just name, icon shows the image
                elif self.asset_type == "objects":
                    self.setText(0, f"📦 {self.asset_name}")
                elif self.asset_type == "rooms":
                    self.setText(0, f"🏠 {self.asset_name}")
                elif self.asset_type == "scripts":
                    self.setText(0, f"📜 {self.asset_name}")
                elif self.asset_type == "fonts":
                    self.setText(0, f"🔤 {self.asset_name}")
            else:
                # Show not-imported assets in gray
                self.setText(0, f"❌ {self.asset_name} (not imported)")
                self.setForeground(0, Qt.GlobalColor.gray)
            
            # Make assets selectable and draggable
            self.setFlags(Qt.ItemFlag.ItemIsEnabled | 
                        Qt.ItemFlag.ItemIsSelectable | 
                        Qt.ItemFlag.ItemIsDragEnabled)

        """Setup the appearance and properties of the tree item"""
        if self.is_category:
            # Category item
            self.setText(0, self.asset_type.title())
            self.setFont(0, QFont("", 9, QFont.Weight.Bold))
            
            # Set category icons
            icon_map = {
                "sprites": "🖼️",
                "sounds": "🔊", 
                "backgrounds": "🖼️",
                "objects": "⚙️",
                "rooms": "🏠",
                "scripts": "📜",
                "fonts": "🔤",
                "data": "📄"
            }
            
            if self.asset_type in icon_map:
                self.setText(0, f"{icon_map[self.asset_type]} {self.asset_type.title()}")
            
            # Make categories non-selectable but expandable
            self.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDropEnabled)
            
        else:
            # Asset item
            self.setText(0, self.asset_name)
            
            # Check if asset is imported
            asset_imported = self.asset_data.get('imported', False)
            
            if asset_imported:
                # Show imported asset normally
                self.setForeground(0, Qt.GlobalColor.black)
                
                # Add type-specific icon
                if self.asset_type == "sprites":
                    self.setText(0, f"🖼️ {self.asset_name}")
                elif self.asset_type == "sounds":
                    self.setText(0, f"🔊 {self.asset_name}")
                elif self.asset_type == "backgrounds":
                    self.setText(0, f"🖼️ {self.asset_name}")
                elif self.asset_type == "objects":
                    self.setText(0, f"⚙️ {self.asset_name}")
                elif self.asset_type == "rooms":
                    self.setText(0, f"🏠 {self.asset_name}")
                elif self.asset_type == "scripts":
                    self.setText(0, f"📜 {self.asset_name}")
                elif self.asset_type == "fonts":
                    self.setText(0, f"🔤 {self.asset_name}")
            else:
                # Show not-imported assets in gray
                self.setText(0, f"❌ {self.asset_name} (not imported)")
                self.setForeground(0, Qt.GlobalColor.gray)
            
            # Make assets selectable and draggable
            self.setFlags(Qt.ItemFlag.ItemIsEnabled | 
                         Qt.ItemFlag.ItemIsSelectable | 
                         Qt.ItemFlag.ItemIsDragEnabled)
            
    def load_sprite_icon(self, sprite_path):
        """Load sprite as icon for tree item"""
        try:
            from PySide6.QtGui import QPixmap, QIcon
            
            if sprite_path and Path(sprite_path).exists():
                pixmap = QPixmap(str(sprite_path))
                if not pixmap.isNull():
                    # Scale to small icon size
                    scaled_pixmap = pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    self.setIcon(0, icon)
                    return True
        except Exception as e:
            print(f"Failed to load sprite icon: {e}")
        return False
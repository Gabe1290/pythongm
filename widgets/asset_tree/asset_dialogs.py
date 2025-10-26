#!/usr/bin/env python3
"""
Asset Dialogs for PyGameMaker IDE
UI dialogs for asset management operations
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt

from .asset_utils import validate_asset_name


class AssetRenameDialog(QDialog):
    """Dialog for renaming assets"""
    
    def __init__(self, current_name: str, asset_type: str, parent=None):
        super().__init__(parent)
        self.current_name = current_name
        self.asset_type = asset_type
        self.new_name = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the rename dialog UI"""
        self.setWindowTitle(f"Rename {self.asset_type.title()}")
        self.setFixedSize(400, 180)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Current name label
        current_label = QLabel(f"Current name: <b>{self.current_name}</b>")
        layout.addWidget(current_label)
        
        # New name input
        name_label = QLabel("New name:")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.current_name)
        self.name_edit.selectAll()
        self.name_edit.setFocus()
        layout.addWidget(self.name_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.accept_rename)
        self.rename_btn.setDefault(True)
        button_layout.addWidget(self.rename_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key to rename
        self.name_edit.returnPressed.connect(self.accept_rename)
        
        # Validate input as user types
        self.name_edit.textChanged.connect(self.validate_name)
        
    def validate_name(self, text: str):
        """Validate the new name as user types"""
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Use utility function for validation
        is_valid, error_msg = validate_asset_name(text)
        
        # Check if name changed
        if text == self.current_name:
            self.rename_btn.setEnabled(False)
            return
            
        self.rename_btn.setEnabled(is_valid)
        
    def accept_rename(self):
        """Accept the rename if valid"""
        new_name = self.name_edit.text().strip()
        
        # Final validation
        is_valid, error_msg = validate_asset_name(new_name)
        
        if not is_valid:
            QMessageBox.warning(self, "Invalid Name", error_msg)
            return
            
        if new_name == self.current_name:
            self.reject()
            return
            
        self.new_name = new_name
        self.accept()


class AssetPropertiesDialog(QDialog):
    """Dialog for viewing/editing detailed asset properties"""
    
    def __init__(self, asset_data: dict, parent=None):
        super().__init__(parent)
        self.asset_data = asset_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the properties dialog UI"""
        asset_name = self.asset_data.get('name', 'Unknown')
        asset_type = self.asset_data.get('asset_type', 'Unknown')
        
        self.setWindowTitle(f"{asset_type.title()} Properties - {asset_name}")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Asset info
        info_label = QLabel(f"<h3>{asset_name}</h3>")
        layout.addWidget(info_label)
        
        type_label = QLabel(f"Type: {asset_type}")
        layout.addWidget(type_label)
        
        # File path info
        if 'project_path' in self.asset_data:
            path_label = QLabel(f"File: {self.asset_data['project_path']}")
            layout.addWidget(path_label)
        
        # Import status
        imported = self.asset_data.get('imported', False)
        status_label = QLabel(f"Status: {'Imported' if imported else 'Not imported'}")
        layout.addWidget(status_label)
        
        # Import button for sprites without images
        if asset_type == "sprite" and not imported:
            context_menu.addSeparator()
            
            import_button_layout = QHBoxLayout()
            self.import_btn = QPushButton("📥 Import Image...")
            self.import_btn.clicked.connect(self.import_sprite_image)
            import_button_layout.addWidget(self.import_btn)
            layout.addLayout(import_button_layout)

        # Creation date
        if 'created_date' in self.asset_data:
            date_label = QLabel(f"Created: {self.asset_data['created_date']}")
            layout.addWidget(date_label)
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addStretch()
        layout.addLayout(button_layout)

    def import_sprite_image(self):
        """Import an image for this sprite"""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path
        
        # Open file dialog for image selection
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sprite Image",
            str(Path.home()),
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        # Get the IDE window to access asset import functionality
        parent = self.parent()
        while parent and not hasattr(parent, 'asset_manager'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'asset_manager'):
            # Import the sprite image
            sprite_name = self.asset_data.get('name')
            asset_type = 'sprites'
            
            try:
                result = parent.asset_manager.import_asset(
                    Path(file_path), 
                    asset_type,
                    sprite_name  # Use existing sprite name
                )
                
                if result:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Image imported successfully for sprite '{sprite_name}'"
                    )
                    # Update the dialog to show new status
                    self.asset_data = result
                    self.accept()  # Close and let parent refresh
                else:
                    QMessageBox.warning(
                        self,
                        "Import Failed",
                        "Failed to import the image. Please try again."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error importing image: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Could not access asset manager. Please try again."
            )

class CreateAssetDialog(QDialog):
    """Dialog for creating new assets"""
    
    def __init__(self, asset_type: str, parent=None):
        super().__init__(parent)
        self.asset_type = asset_type
        self.asset_name = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the create asset dialog UI"""
        self.setWindowTitle(f"Create {self.asset_type.title()}")
        self.setFixedSize(400, 150)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(f"<h3>Create New {self.asset_type.title()}</h3>")
        layout.addWidget(title_label)
        
        # Name input
        name_label = QLabel("Asset name:")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(f"Enter {self.asset_type} name...")
        self.name_edit.setFocus()
        layout.addWidget(self.name_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.accept_create)
        self.create_btn.setDefault(True)
        self.create_btn.setEnabled(False)
        button_layout.addWidget(self.create_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key to create
        self.name_edit.returnPressed.connect(self.accept_create)
        
        # Validate input as user types
        self.name_edit.textChanged.connect(self.validate_name)
    
    def validate_name(self, text: str):
        """Validate the asset name as user types"""
        text = text.strip()
        is_valid, _ = validate_asset_name(text)
        self.create_btn.setEnabled(is_valid)
    
    def accept_create(self):
        """Accept the create if valid"""
        name = self.name_edit.text().strip()
        
        is_valid, error_msg = validate_asset_name(name)
        
        if not is_valid:
            QMessageBox.warning(self, "Invalid Name", error_msg)
            return
        
        self.asset_name = name
        self.accept()
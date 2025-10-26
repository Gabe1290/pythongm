#!/usr/bin/env python3
"""
Properties Panel Widget for PyGameMaker IDE - Complete Clean Version
Displays asset properties, preview, and information with import functionality
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QScrollArea, QPushButton,
    QSplitter, QFrame, QGridLayout, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QSlider, QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont, QPalette, QIcon


class PropertiesPanel(QWidget):
    """
    Properties panel widget that displays asset properties, preview, and information
    """
    
    # Signals
    assetModified = Signal(str, dict)  # asset_name, asset_data
    propertyChanged = Signal(str, str, object)  # asset_name, property_name, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Current asset data
        self.current_asset = None
        self.current_asset_name = ""
        self.project_data = None
        self.property_widgets = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        print("✅ PropertiesWidget initialized")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Create main splitter for vertical sections
        splitter = QSplitter(Qt.Vertical)
        
        # === PREVIEW SECTION ===
        preview_section = self.create_preview_section()
        splitter.addWidget(preview_section)
        
        # === IMPORT SECTION (for sprites) ===
        import_section = self.create_import_section()
        splitter.addWidget(import_section)
        
        # === PROPERTIES SECTION ===
        properties_section = self.create_properties_section()
        splitter.addWidget(properties_section)
        
        # === INFO SECTION ===
        info_section = self.create_info_section()
        splitter.addWidget(info_section)
        
        # Set initial splitter sizes (preview larger)
        splitter.setSizes([300, 80, 150, 100])
        splitter.setCollapsible(0, False)  # Don't collapse preview
        splitter.setCollapsible(1, True)   # Allow collapsing import
        splitter.setCollapsible(2, False)  # Don't collapse properties
        splitter.setCollapsible(3, True)   # Allow collapsing info
        
        layout.addWidget(splitter)
        
        # Set initial state
        self.clear_display()
    
    def create_preview_section(self):
        """Create the asset preview section"""
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Main preview label
        self.preview_label = QLabel("Select an asset to preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setMaximumHeight(300)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #f8f8f8;
                color: #666666;
                font-size: 14px;
                padding: 20px;
            }
        """)
        
        preview_layout.addWidget(self.preview_label)
        
        # Preview controls
        controls_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setMaximumWidth(40)
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.setEnabled(False)
        
        self.zoom_out_btn = QPushButton("🔍-") 
        self.zoom_out_btn.setMaximumWidth(40)
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.setEnabled(False)
        
        self.reset_zoom_btn = QPushButton("🔄")
        self.reset_zoom_btn.setMaximumWidth(40)
        self.reset_zoom_btn.setToolTip("Reset Zoom")
        self.reset_zoom_btn.setEnabled(False)
        
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.reset_zoom_btn)
        controls_layout.addStretch()
        
        preview_layout.addLayout(controls_layout)
        
        return preview_group
    
    def create_import_section(self):
        """Create import section for sprites"""
        import_group = QGroupBox("Import Image")
        import_layout = QVBoxLayout(import_group)
        
        # Import button
        self.import_image_btn = QPushButton("📁 Import Image File")
        self.import_image_btn.clicked.connect(self.import_image_file)
        self.import_image_btn.setEnabled(False)
        self.import_image_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # Status label
        self.import_status_label = QLabel("Select a sprite to import an image")
        self.import_status_label.setStyleSheet("color: gray; font-style: italic;")
        self.import_status_label.setAlignment(Qt.AlignCenter)
        
        import_layout.addWidget(self.import_image_btn)
        import_layout.addWidget(self.import_status_label)
        
        return import_group
    
    def create_properties_section(self):
        """Create the asset properties section"""
        properties_group = QGroupBox("Properties")
        properties_layout = QVBoxLayout(properties_group)
        
        # Create scrollable area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        # Properties form widget
        self.properties_form_widget = QWidget()
        self.properties_form_layout = QFormLayout(self.properties_form_widget)
        self.properties_form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        
        # Standard property fields
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        self.properties_form_layout.addRow("Name:", self.name_edit)
        
        self.type_edit = QLineEdit()
        self.type_edit.setReadOnly(True)
        self.properties_form_layout.addRow("Type:", self.type_edit)
        
        self.width_edit = QLineEdit()
        self.width_edit.setReadOnly(True)
        self.properties_form_layout.addRow("Width:", self.width_edit)
        
        self.height_edit = QLineEdit()
        self.height_edit.setReadOnly(True)
        self.properties_form_layout.addRow("Height:", self.height_edit)
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.properties_form_layout.addRow("File Path:", self.file_path_edit)
        
        self.size_edit = QLineEdit()
        self.size_edit.setReadOnly(True)
        self.properties_form_layout.addRow("File Size:", self.size_edit)
        
        # Store property widgets for easy access
        self.property_widgets = {
            'name': self.name_edit,
            'type': self.type_edit,
            'width': self.width_edit,
            'height': self.height_edit,
            'file_path': self.file_path_edit,
            'size': self.size_edit
        }
        
        scroll_area.setWidget(self.properties_form_widget)
        properties_layout.addWidget(scroll_area)
        
        return properties_group
    
    def create_info_section(self):
        """Create the asset information section"""
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        # Info text area
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)
        self.info_text.setPlainText("Asset information will appear here...")
        
        # Set font for better readability
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier", 9)
        self.info_text.setFont(font)
        
        info_layout.addWidget(self.info_text)
        
        return info_group
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect zoom buttons (for future implementation)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
    
    def set_project(self, project_path, project_data):
        """Set project (compatibility method)"""
        print(f"✅ Properties panel set to project: {project_path}")
        return self.set_project_data(project_data)
    
    def set_project_data(self, project_data: Dict):
        """Set the current project data"""
        self.project_data = project_data
        print("✅ Properties panel set to project data")
    

    def set_asset(self, asset_data: dict):
        """
        Set the current asset and update the display
        ADD THIS METHOD TO YOUR PropertiesPanel CLASS
        """
        try:
            # Prevent duplicate calls for the same asset
            if hasattr(self, '_current_asset_data') and self._current_asset_data == asset_data:
                return  # Skip if same asset data
            
            self._current_asset_data = asset_data  # Store current asset

            if not asset_data:
                # Clear display if no asset
                if hasattr(self, 'name_edit'):
                    self.name_edit.setText("")
                if hasattr(self, 'asset_type_edit'):
                    self.asset_type_edit.setText("")
                if hasattr(self, 'info_text'):
                    self.info_text.setPlainText("No asset selected")
                if hasattr(self, 'preview_label'):
                    self.preview_label.setText("Select an asset to preview")
                return
            
            # Parse and merge data (same logic as before)
            full_asset_data = asset_data.copy()
            
            if 'data' in asset_data and asset_data['data']:
                data_value = asset_data['data']
                parsed_data = None
                
                if isinstance(data_value, str):
                    # Try JSON first, then Python dict string
                    try:
                        import json
                        parsed_data = json.loads(data_value)
                    except json.JSONDecodeError:
                        try:
                            import ast
                            parsed_data = ast.literal_eval(data_value)
                        except (ValueError, SyntaxError):
                            print(f"⚠️  Could not parse asset data string")
                elif isinstance(data_value, dict):
                    parsed_data = data_value
                
                if parsed_data:
                    full_asset_data.update(parsed_data)
            
            # Extract asset information
            name = full_asset_data.get('name', 'Unknown')
            asset_type = full_asset_data.get('asset_type', 'unknown')
            file_path = full_asset_data.get('file_path', '')
            project_path = full_asset_data.get('project_path', '')
            
            print(f"✅ PropertiesPanel: Setting asset: {name} (type: {asset_type})")
            
            # Update basic properties if they exist
            if hasattr(self, 'name_edit'):
                self.name_edit.setText(name)
            
            if hasattr(self, 'asset_type_edit'):
                self.asset_type_edit.setText(asset_type.title())
            
            # Update info text if it exists
            if hasattr(self, 'info_text'):
                info_text = f"Asset: {name}\n"
                info_text += f"Type: {asset_type.title()}\n"
                if file_path:
                    info_text += f"File: {file_path}\n"
                if full_asset_data.get('imported'):
                    info_text += "Status: Imported"
                self.info_text.setPlainText(info_text)
            
            # Update preview if it exists
            if hasattr(self, 'preview_label'):
                if asset_type == 'sprite':
                    self.preview_label.setText(f"Sprite Preview\n{name}")
                elif asset_type == 'sound':
                    self.preview_label.setText(f"♪ {name} ♪")
                else:
                    self.preview_label.setText(f"Asset Preview\n{name}")
            
            # Call any other existing update methods if they exist
            if hasattr(self, 'update_basic_properties'):
                self.update_basic_properties(full_asset_data)
            
            if hasattr(self, 'display_image_asset') and asset_type in ['sprite', 'background']:
                self.display_image_asset(full_asset_data)
            
        except Exception as e:
            print(f"❌ Error in PropertiesPanel.set_asset: {e}")
            import traceback
            traceback.print_exc()

    def update_basic_properties(self, asset_data: Dict):
        """Update the basic property fields"""
        try:
            name = asset_data.get('name', 'Unknown')
            asset_type = asset_data.get('asset_type', 'unknown')
            file_path = asset_data.get('file_path', '')
            
            # NEW: Get absolute path using the new system
            image_path = None
            if hasattr(self.parent(), 'asset_tree'):
                image_path = self.parent().asset_tree.get_asset_absolute_path(asset_data)
            else:
                project_path = getattr(self.parent(), 'current_project_path', None)
                if project_path and asset_data.get('file_path'):
                    image_path = str(Path(project_path) / asset_data['file_path'])
            
            # Update property widgets
            self.name_edit.setText(name)
            self.type_edit.setText(asset_type.title())
            self.file_path_edit.setText(file_path)
            
            # Get file size if file exists
            if image_path and os.path.exists(image_path):
                try:
                    file_size = os.path.getsize(image_path)
                    if file_size < 1024:
                        size_str = f"{file_size} bytes"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    
                    self.size_edit.setText(size_str)
                except:
                    self.size_edit.setText("Unknown")
            else:
                self.size_edit.setText("File not found")
                
        except Exception as e:
            print(f"❌ Error updating basic properties: {e}")

    def display_image_asset(self, asset_data: Dict):
        """Display an image asset (sprite or background)"""
        try:
            name = asset_data.get('name', 'Unknown')
            
            # Get absolute path using the correct parent access
            image_path = None
            
            # Find the IDE window (it might be parent or grandparent)
            ide_window = self.parent()
            while ide_window and not hasattr(ide_window, 'asset_tree'):
                ide_window = ide_window.parent()
            
            if ide_window and hasattr(ide_window, 'asset_tree'):
                image_path = ide_window.asset_tree.get_asset_absolute_path(asset_data)
            else:
                # Try to find project path from IDE window
                ide_window = self.parent()
                while ide_window and not hasattr(ide_window, 'current_project_path'):
                    ide_window = ide_window.parent()
                
                if ide_window and hasattr(ide_window, 'current_project_path'):
                    project_path = ide_window.current_project_path
                    if project_path and asset_data.get('file_path'):
                        from pathlib import Path
                        image_path = str(Path(project_path) / asset_data['file_path'])
            
            if image_path and os.path.exists(image_path):
                # Load and display image
                pixmap = QPixmap(image_path)
                
                if not pixmap.isNull():
                    # Update size information
                    self.width_edit.setText(str(pixmap.width()))
                    self.height_edit.setText(str(pixmap.height()))
                    
                    # Scale image to fit preview while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        260, 260,  # Max size for preview
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    # Display the image
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.preview_label.setText("")  # Clear text when showing image
                    
                    # Enable zoom controls
                    self.zoom_in_btn.setEnabled(True)
                    self.zoom_out_btn.setEnabled(True)
                    self.reset_zoom_btn.setEnabled(True)
                    
                    print(f"Image preview loaded: {os.path.basename(image_path)}")
                    
                else:
                    # Failed to load image
                    self.preview_label.setText(f"Unable to load image\n{name}")
                    self.preview_label.setPixmap(QPixmap())
                    self.width_edit.setText("N/A")
                    self.height_edit.setText("N/A")
            else:
                # File not found
                self.preview_label.setText(f"No image file\n{name}\n\nClick 'Import Image File' below")
                self.preview_label.setPixmap(QPixmap())
                self.width_edit.setText("N/A")
                self.height_edit.setText("N/A")
                
        except Exception as e:
            print(f"Error displaying image asset: {e}")
            self.preview_label.setText(f"Error loading image\n{str(e)}")
            self.preview_label.setPixmap(QPixmap())
    
    def display_sound_asset(self, asset_data: Dict):
        """Display a sound asset"""
        try:
            name = asset_data.get('name', 'Unknown')
            project_path = asset_data.get('project_path', '')
            
            self.width_edit.setText("N/A")
            self.height_edit.setText("N/A")

            # Get sound file path using new system
            sound_path = None
            if hasattr(self.parent(), 'asset_tree'):
                sound_path = self.parent().asset_tree.get_asset_absolute_path(asset_data)

            if sound_path and os.path.exists(sound_path):
                self.preview_label.setText(f"🔊 Sound Asset\n{name}\n\n(Audio preview not available)")
            else:
                self.preview_label.setText(f"🔊 Sound Asset\n{name}\n\n📁 File not found")
            
            self.preview_label.setPixmap(QPixmap())
            
            # Disable zoom controls for sounds
            self.zoom_in_btn.setEnabled(False)
            self.zoom_out_btn.setEnabled(False)
            self.reset_zoom_btn.setEnabled(False)
            
        except Exception as e:
            print(f"❌ Error displaying sound asset: {e}")
    
    def display_object_asset(self, asset_data: Dict):
        """Display an object asset"""
        try:
            name = asset_data.get('name', 'Unknown')
            
            self.width_edit.setText("N/A")
            self.height_edit.setText("N/A")
            
            self.preview_label.setText(f"🎮 Object\n{name}\n\n(Object editor not available)")
            self.preview_label.setPixmap(QPixmap())
            
            # Disable zoom controls
            self.zoom_in_btn.setEnabled(False)
            self.zoom_out_btn.setEnabled(False)
            self.reset_zoom_btn.setEnabled(False)
            
        except Exception as e:
            print(f"❌ Error displaying object asset: {e}")
    
    def display_room_asset(self, asset_data: Dict):
        """Display a room asset"""
        try:
            name = asset_data.get('name', 'Unknown')
            
            # Rooms might have dimensions
            width = asset_data.get('width', 'N/A')
            height = asset_data.get('height', 'N/A')
            
            self.width_edit.setText(str(width))
            self.height_edit.setText(str(height))
            
            self.preview_label.setText(f"🏠 Room\n{name}\n\n(Room editor not available)")
            self.preview_label.setPixmap(QPixmap())
            
            # Disable zoom controls
            self.zoom_in_btn.setEnabled(False)
            self.zoom_out_btn.setEnabled(False)
            self.reset_zoom_btn.setEnabled(False)
            
        except Exception as e:
            print(f"❌ Error displaying room asset: {e}")
    
    def display_generic_asset(self, asset_data: Dict):
        """Display a generic asset"""
        try:
            name = asset_data.get('name', 'Unknown')
            asset_type = asset_data.get('asset_type', 'unknown')
            
            self.width_edit.setText("N/A")
            self.height_edit.setText("N/A")
            
            self.preview_label.setText(f"📄 {asset_type.title()}\n{name}\n\n(No preview available)")
            self.preview_label.setPixmap(QPixmap())
            
            # Disable zoom controls
            self.zoom_in_btn.setEnabled(False)
            self.zoom_out_btn.setEnabled(False)
            self.reset_zoom_btn.setEnabled(False)
            
        except Exception as e:
            print(f"❌ Error displaying generic asset: {e}")
    
    def update_info_text(self, asset_data: Dict):
        """Update the information text area"""
        try:
            name = asset_data.get('name', 'Unknown')
            asset_type = asset_data.get('asset_type', 'unknown')
            file_path = asset_data.get('file_path', '')
            
            # Get absolute path using the new system
            image_path = None
            if hasattr(self.parent(), 'asset_tree'):
                image_path = self.parent().asset_tree.get_asset_absolute_path(asset_data)
            else:
                project_path = getattr(self.parent(), 'current_project_path', None)
                if project_path and asset_data.get('file_path'):
                    from pathlib import Path
                    image_path = str(Path(image_path) / asset_data['file_path'])
            
            imported = asset_data.get('imported', False)
            created_date = asset_data.get('created_date', 'Unknown')
            
            info_lines = [
                f"Asset Name: {name}",
                f"Asset Type: {asset_type.title()}",
                f"File Path: {file_path}",
                f"Imported: {'Yes' if imported else 'No'}",
                f"Created: {created_date}",
                ""
            ]
            
            # Add file-specific information
            if image_path and os.path.exists(image_path):
                info_lines.append("File Status: ✅ Found")
                
                # Add image-specific info
                if asset_type in ['sprite', 'background']:
                    try:
                        pixmap = QPixmap(image_path)
                        if not pixmap.isNull():
                            info_lines.append(f"Dimensions: {pixmap.width()} × {pixmap.height()}")
                            info_lines.append(f"Aspect Ratio: {pixmap.width() / pixmap.height():.2f}")
                    except:
                        pass
                
                # Add file format info
                file_ext = Path(image_path).suffix.upper()
                if file_ext:
                    info_lines.append(f"Format: {file_ext}")
                
            else:
                info_lines.append("File Status: ❌ Not Found")
                if asset_type == 'sprite':
                    info_lines.append("Note: Use 'Import Image File' button to add image")
            
            # Join and display
            info_text = "\n".join(info_lines)
            self.info_text.setPlainText(info_text)
            
        except Exception as e:
            print(f"❌ Error updating info text: {e}")
            self.info_text.setPlainText(f"Error loading asset information:\n{str(e)}")
    
    def clear_display(self):
        """Clear all displays and reset to default state"""
        try:
            # Clear preview
            self.preview_label.setText("Select an asset to preview")
            self.preview_label.setPixmap(QPixmap())
            
            # Clear property fields
            for widget in self.property_widgets.values():
                if hasattr(widget, 'clear'):
                    widget.clear()
            
            # Clear info
            self.info_text.setPlainText("Asset information will appear here...")
            
            # Disable zoom controls
            self.zoom_in_btn.setEnabled(False)
            self.zoom_out_btn.setEnabled(False)
            self.reset_zoom_btn.setEnabled(False)
            
            # Disable import button
            if hasattr(self, "import_image_btn"):
                self.import_image_btn.setEnabled(False)
                self.import_status_label.setText("Select a sprite to import an image")
            
            # Reset current asset
            self.current_asset = None
            self.current_asset_name = ""
            
        except Exception as e:
            print(f"❌ Error clearing display: {e}")
    
    def import_image_file(self):
        """Import image file for current sprite"""
        if not self.current_asset or self.current_asset.get('asset_type') != 'sprite':
            QMessageBox.warning(self, "No Sprite", "Please select a sprite first.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image for Sprite",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                sprite_name = self.current_asset.get('name', 'unknown')
                
                # Create project directories
                project_dir = Path("/home/gabe/Documents/PyGameMaker Projects/MyPyGM_v1.1")
                sprites_dir = project_dir / "sprites"
                sprites_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy image to project
                source = Path(file_path)
                dest = sprites_dir / f"{sprite_name}{source.suffix}"
                shutil.copy2(source, dest)
                
                # Update asset data
                self.current_asset['project_path'] = str(dest)
                self.current_asset['file_path'] = f"sprites/{sprite_name}{source.suffix}"
                self.current_asset['imported'] = True
                
                # Refresh display
                self.set_asset(self.current_asset)
                
                QMessageBox.information(self, "Success", f"Image imported for {sprite_name}!")
                print(f"✅ Image imported for sprite: {sprite_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import image: {str(e)}")
                print(f"❌ Error importing image: {e}")
    
    # Zoom functionality (for future implementation)
    def zoom_in(self):
        """Zoom in on preview (future feature)"""
        print("🔍 Zoom in (not implemented yet)")
    
    def zoom_out(self):
        """Zoom out on preview (future feature)"""
        print("🔍 Zoom out (not implemented yet)")
    
    def reset_zoom(self):
        """Reset zoom to 100% (future feature)"""
        print("🔄 Reset zoom (not implemented yet)")


# Compatibility alias
PropertiesWidget = PropertiesPanel


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = PropertiesPanel()
    widget.show()
    
    app.exec()

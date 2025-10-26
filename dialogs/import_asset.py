#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QLineEdit, QPushButton, QComboBox,
                               QTextEdit, QGroupBox, QDialogButtonBox,
                               QFileDialog, QMessageBox, QCheckBox, QListWidget,
                               QListWidgetItem, QSplitter, QFrame, QScrollArea,
                               QSpinBox, QDoubleSpinBox, QSlider, QProgressBar,
                               QTabWidget, QFormLayout, QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPalette, QMovie

from utils.config import Config


class AssetPreviewWidget(QLabel):
    """Widget for previewing assets during import"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(200, 150)
        self.setMaximumSize(300, 300)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: #f8f8f8;
                color: #666666;
            }
        """)
        
        self.current_file = None
        self.setText("No preview available")
    
    def set_preview_file(self, file_path: Path):
        """Set the file to preview"""
        self.current_file = file_path
        
        try:
            if not file_path or not file_path.exists():
                self.clear_preview()
                return
            
            # Handle different file types
            suffix = file_path.suffix.lower()
            
            if suffix in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga', '.webp']:
                self.preview_image(file_path)
            elif suffix in ['.wav', '.mp3', '.ogg', '.m4a', '.aac', '.flac']:
                self.preview_audio(file_path)
            elif suffix in ['.ttf', '.otf', '.woff', '.woff2']:
                self.preview_font(file_path)
            else:
                self.preview_generic(file_path)
        
        except Exception as e:
            self.setText(f"Preview error:\n{str(e)}")
    
    def preview_image(self, file_path: Path):
        """Preview image files"""
        pixmap = QPixmap(str(file_path))
        if not pixmap.isNull():
            # Scale while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            
            # Update tooltip with image info
            self.setToolTip(f"Image: {pixmap.width()}×{pixmap.height()}\n"
                          f"Size: {self.format_file_size(file_path.stat().st_size)}")
        else:
            self.setText("Invalid image file")
    
    def preview_audio(self, file_path: Path):
        """Preview audio files"""
        file_size = file_path.stat().st_size
        size_str = self.format_file_size(file_size)
        
        # Try to get duration using pygame
        try:
            import pygame
            pygame.mixer.init()
            sound = pygame.mixer.Sound(str(file_path))
            duration = sound.get_length()
            duration_str = f"{duration:.1f}s"
        except:
            duration_str = "Unknown"
        
        self.setText(f"🎵 Audio File\n"
                    f"{file_path.suffix.upper()[1:]}\n"
                    f"Size: {size_str}\n"
                    f"Duration: {duration_str}")
        
        self.setToolTip(f"Audio file: {file_path.name}")
    
    def preview_font(self, file_path: Path):
        """Preview font files"""
        file_size = file_path.stat().st_size
        size_str = self.format_file_size(file_size)
        
        self.setText(f"🔤 Font File\n"
                    f"{file_path.suffix.upper()[1:]}\n"
                    f"Size: {size_str}")
        
        self.setToolTip(f"Font file: {file_path.name}")
    
    def preview_generic(self, file_path: Path):
        """Preview generic files"""
        file_size = file_path.stat().st_size
        size_str = self.format_file_size(file_size)
        
        self.setText(f"📄 {file_path.suffix.upper()[1:]} File\n"
                    f"Size: {size_str}")
        
        self.setToolTip(f"File: {file_path.name}")
    
    def clear_preview(self):
        """Clear the preview"""
        self.clear()
        self.setText("No preview available")
        self.setToolTip("")
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


class ImportFileItem(QFrame):
    """Widget representing a file to be imported"""
    
    remove_requested = Signal(object)  # self
    
    def __init__(self, file_path: Path, asset_type: str, parent=None):
        super().__init__(parent)
        
        self.file_path = file_path
        self.asset_type = asset_type
        self.import_name = file_path.stem
        self.import_enabled = True
        
        self.setup_ui()
        self.setFrameStyle(QFrame.StyledPanel)
    
    def setup_ui(self):
        """Setup the UI for this item"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # Checkbox for enabling/disabling import
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        self.enabled_check.stateChanged.connect(self.on_enabled_changed)
        layout.addWidget(self.enabled_check)
        
        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # File name and path
        file_name_label = QLabel(self.file_path.name)
        file_name_label.setFont(QFont("", 9, QFont.Bold))
        info_layout.addWidget(file_name_label)
        
        path_label = QLabel(str(self.file_path.parent))
        path_label.setStyleSheet("color: #666666; font-size: 8px;")
        info_layout.addWidget(path_label)
        
        layout.addLayout(info_layout, 1)
        
        # Import name edit
        name_layout = QVBoxLayout()
        name_layout.setSpacing(2)
        
        name_label = QLabel("Import as:")
        name_label.setStyleSheet("font-size: 8px; color: #666666;")
        name_layout.addWidget(name_label)
        
        self.name_edit = QLineEdit(self.import_name)
        self.name_edit.setMaximumWidth(120)
        self.name_edit.textChanged.connect(self.on_name_changed)
        name_layout.addWidget(self.name_edit)
        
        layout.addLayout(name_layout)
        
        # File size
        file_size = self.file_path.stat().st_size if self.file_path.exists() else 0
        size_label = QLabel(self.format_file_size(file_size))
        size_label.setStyleSheet("color: #666666; font-size: 8px;")
        size_label.setMinimumWidth(60)
        layout.addWidget(size_label)
        
        # Remove button
        remove_button = QPushButton("×")
        remove_button.setMaximumSize(20, 20)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_button)
    
    def on_enabled_changed(self, state):
        """Handle enabled state change"""
        self.import_enabled = state == Qt.Checked
        self.name_edit.setEnabled(self.import_enabled)
        
        # Update visual style
        if self.import_enabled:
            self.setStyleSheet("QFrame { background-color: #ffffff; }")
        else:
            self.setStyleSheet("QFrame { background-color: #f0f0f0; }")
    
    def on_name_changed(self, text):
        """Handle name change"""
        self.import_name = text
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def get_import_data(self) -> Optional[Dict[str, Any]]:
        """Get import data for this file"""
        if not self.import_enabled:
            return None
        
        return {
            "file_path": self.file_path,
            "import_name": self.import_name,
            "asset_type": self.asset_type
        }


class ImportOptionsWidget(QWidget):
    """Widget for import options specific to asset type"""
    
    def __init__(self, asset_type: str, parent=None):
        super().__init__(parent)
        
        self.asset_type = asset_type
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the options UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.asset_type == "sprites":
            self.create_sprite_options(layout)
        elif self.asset_type == "sounds":
            self.create_sound_options(layout)
        elif self.asset_type == "backgrounds":
            self.create_background_options(layout)
        elif self.asset_type == "fonts":
            self.create_font_options(layout)
        else:
            self.create_generic_options(layout)
    
    def create_sprite_options(self, layout):
        """Create options for sprite imports"""
        group = QGroupBox("Sprite Import Options")
        form_layout = QFormLayout(group)
        
        # Origin settings
        self.origin_combo = QComboBox()
        self.origin_combo.addItems([
            "Top Left", "Top Center", "Top Right",
            "Middle Left", "Middle Center", "Middle Right",
            "Bottom Left", "Bottom Center", "Bottom Right",
            "Custom"
        ])
        self.origin_combo.setCurrentText("Middle Center")
        form_layout.addRow("Origin:", self.origin_combo)
        
        # Custom origin
        origin_layout = QHBoxLayout()
        self.origin_x_spin = QSpinBox()
        self.origin_x_spin.setRange(-999, 999)
        self.origin_y_spin = QSpinBox()
        self.origin_y_spin.setRange(-999, 999)
        self.origin_x_spin.setEnabled(False)
        self.origin_y_spin.setEnabled(False)
        
        origin_layout.addWidget(QLabel("X:"))
        origin_layout.addWidget(self.origin_x_spin)
        origin_layout.addWidget(QLabel("Y:"))
        origin_layout.addWidget(self.origin_y_spin)
        origin_layout.addStretch()
        
        form_layout.addRow("Custom Origin:", origin_layout)
        
        # Enable custom origin when selected
        self.origin_combo.currentTextChanged.connect(
            lambda text: self.toggle_custom_origin(text == "Custom")
        )
        
        # Animation settings
        self.frame_count_spin = QSpinBox()
        self.frame_count_spin.setRange(1, 100)
        self.frame_count_spin.setValue(1)
        form_layout.addRow("Frame Count:", self.frame_count_spin)
        
        self.frame_speed_spin = QDoubleSpinBox()
        self.frame_speed_spin.setRange(0.1, 10.0)
        self.frame_speed_spin.setValue(1.0)
        self.frame_speed_spin.setDecimals(1)
        form_layout.addRow("Animation Speed:", self.frame_speed_spin)
        
        layout.addWidget(group)
    
    def create_sound_options(self, layout):
        """Create options for sound imports"""
        group = QGroupBox("Sound Import Options")
        form_layout = QFormLayout(group)
        
        # Volume settings
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("100%")
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%")
        )
        volume_layout.addWidget(self.volume_label)
        
        form_layout.addRow("Default Volume:", volume_layout)
        
        # Loop setting
        self.loop_check = QCheckBox("Loop by default")
        form_layout.addRow(self.loop_check)
        
        # Compression
        self.compress_check = QCheckBox("Compress audio")
        self.compress_check.setChecked(True)
        form_layout.addRow(self.compress_check)
        
        layout.addWidget(group)
    
    def create_background_options(self, layout):
        """Create options for background imports"""
        group = QGroupBox("Background Import Options")
        form_layout = QFormLayout(group)
        
        # Tiling options
        self.tile_h_check = QCheckBox("Tile horizontally")
        self.tile_v_check = QCheckBox("Tile vertically")
        
        form_layout.addRow(self.tile_h_check)
        form_layout.addRow(self.tile_v_check)
        
        # Scaling
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Keep original", "Scale to room", "Scale to fit"])
        form_layout.addRow("Scaling:", self.scale_combo)
        
        layout.addWidget(group)
    
    def create_font_options(self, layout):
        """Create options for font imports"""
        group = QGroupBox("Font Import Options")
        form_layout = QFormLayout(group)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(12)
        form_layout.addRow("Default Size:", self.font_size_spin)
        
        # Font style
        self.bold_check = QCheckBox("Bold")
        self.italic_check = QCheckBox("Italic")
        
        form_layout.addRow(self.bold_check)
        form_layout.addRow(self.italic_check)
        
        # Character set
        self.charset_combo = QComboBox()
        self.charset_combo.addItems(["ASCII", "Extended ASCII", "Unicode"])
        form_layout.addRow("Character Set:", self.charset_combo)
        
        layout.addWidget(group)
    
    def create_generic_options(self, layout):
        """Create generic import options"""
        group = QGroupBox("Import Options")
        form_layout = QFormLayout(group)
        
        # Generic settings
        self.overwrite_check = QCheckBox("Overwrite existing assets")
        form_layout.addRow(self.overwrite_check)
        
        layout.addWidget(group)
    
    def toggle_custom_origin(self, enabled):
        """Toggle custom origin inputs"""
        self.origin_x_spin.setEnabled(enabled)
        self.origin_y_spin.setEnabled(enabled)
    
    def get_options(self) -> Dict[str, Any]:
        """Get the import options"""
        options = {}
        
        if self.asset_type == "sprites":
            origin_text = self.origin_combo.currentText()
            if origin_text == "Custom":
                options["origin_x"] = self.origin_x_spin.value()
                options["origin_y"] = self.origin_y_spin.value()
            else:
                # Convert origin text to coordinates (assuming 32x32 default)
                origin_map = {
                    "Top Left": (0, 0), "Top Center": (16, 0), "Top Right": (32, 0),
                    "Middle Left": (0, 16), "Middle Center": (16, 16), "Middle Right": (32, 16),
                    "Bottom Left": (0, 32), "Bottom Center": (16, 32), "Bottom Right": (32, 32)
                }
                origin_x, origin_y = origin_map.get(origin_text, (16, 16))
                options["origin_x"] = origin_x
                options["origin_y"] = origin_y
            
            options["frames"] = self.frame_count_spin.value()
            options["speed"] = self.frame_speed_spin.value()
        
        elif self.asset_type == "sounds":
            options["volume"] = self.volume_slider.value() / 100.0
            options["loop"] = self.loop_check.isChecked()
            options["compress"] = self.compress_check.isChecked()
        
        elif self.asset_type == "backgrounds":
            options["tile_horizontal"] = self.tile_h_check.isChecked()
            options["tile_vertical"] = self.tile_v_check.isChecked()
            options["scaling"] = self.scale_combo.currentText().lower().replace(" ", "_")
        
        elif self.asset_type == "fonts":
            options["size"] = self.font_size_spin.value()
            options["bold"] = self.bold_check.isChecked()
            options["italic"] = self.italic_check.isChecked()
            options["charset"] = self.charset_combo.currentText().lower()
        
        return options


class ImportAssetDialog(QDialog):
    """Dialog for importing assets"""
    
    def __init__(self, parent=None, asset_type: str = "sprites"):
        super().__init__(parent)
        self.parent_window = parent
        
        self.asset_type = asset_type
        self.selected_files = []
        self.import_items = []
        
        self.setWindowTitle(f"Import {asset_type.title()}")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.update_ui_state()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(f"Import {self.asset_type.title()}")
        title_label.setFont(QFont("", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - File selection and list
        left_widget = self.create_file_selection_section()
        splitter.addWidget(left_widget)
        
        # Right side - Preview and options
        right_widget = self.create_preview_options_section()
        splitter.addWidget(right_widget)
        
        splitter.setSizes([500, 300])
        layout.addWidget(splitter)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.select_files_button = QPushButton("Add Files...")
        self.select_files_button.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.select_files_button)
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_files)
        buttons_layout.addWidget(self.clear_all_button)
        
        buttons_layout.addStretch()
        
        # Standard buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.import_button = buttons.button(QDialogButtonBox.Ok)
        self.import_button.setText("Import")
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        buttons_layout.addWidget(buttons)
        layout.addLayout(buttons_layout)
    
    def create_file_selection_section(self) -> QWidget:
        """Create the file selection section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 10, 0)
        
        # File list header
        header_layout = QHBoxLayout()
        
        files_label = QLabel("Files to Import")
        files_label.setFont(QFont("", 10, QFont.Bold))
        header_layout.addWidget(files_label)
        
        header_layout.addStretch()
        
        # File count
        self.file_count_label = QLabel("0 files")
        self.file_count_label.setStyleSheet("color: #666666;")
        header_layout.addWidget(self.file_count_label)
        
        layout.addLayout(header_layout)
        
        # Files scroll area
        self.files_scroll_area = QScrollArea()
        self.files_scroll_area.setWidgetResizable(True)
        self.files_scroll_area.setMinimumHeight(300)
        
        # Container for file items
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setSpacing(5)
        self.files_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add stretch to push items to top
        self.files_layout.addStretch()
        
        self.files_scroll_area.setWidget(self.files_container)
        layout.addWidget(self.files_scroll_area)
        
        # Drag and drop info
        drop_label = QLabel("Tip: You can also drag and drop files here")
        drop_label.setStyleSheet("color: #888888; font-style: italic; font-size: 9px;")
        drop_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(drop_label)
        
        return widget
    
    def create_preview_options_section(self) -> QWidget:
        """Create the preview and options section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 0, 0, 0)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_widget = AssetPreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        layout.addWidget(preview_group)
        
        # Options section
        self.options_widget = ImportOptionsWidget(self.asset_type)
        layout.addWidget(self.options_widget)
        
        layout.addStretch()
        
        return widget
    
    def select_files(self):
        """Select files to import"""
        # File filters based on asset type
        filters = {
            "sprites": "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tga *.webp)",
            "sounds": "Audio Files (*.wav *.mp3 *.ogg *.m4a *.aac *.flac)",
            "backgrounds": "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tga *.webp)",
            "fonts": "Font Files (*.ttf *.otf *.woff *.woff2)",
            "data": "Data Files (*.json *.xml *.txt *.csv)"
        }
        
        file_filter = filters.get(self.asset_type, "All Files (*.*)")
        
        # Get last used directory
        last_dir = Config.get(f"last_import_dir_{self.asset_type}", str(Path.home()))
        
        files, _ = QFileDialog.getOpenFileNames(
            self, f"Select {self.asset_type.title()} Files",
            last_dir, file_filter
        )
        
        if files:
            # Save last used directory
            Config.set(f"last_import_dir_{self.asset_type}", str(Path(files[0]).parent))
            
            # Add files to import list
            self.add_files([Path(f) for f in files])
    
    def add_files(self, file_paths: List[Path]):
        """Add files to the import list"""
        added_count = 0
        
        for file_path in file_paths:
            # Check if file is already in the list
            if any(item.file_path == file_path for item in self.import_items):
                continue
            
            # Create import item
            import_item = ImportFileItem(file_path, self.asset_type)
            import_item.remove_requested.connect(self.remove_import_item)
            
            # Insert before stretch
            self.files_layout.insertWidget(len(self.import_items), import_item)
            self.import_items.append(import_item)
            
            added_count += 1
        
        if added_count > 0:
            self.update_ui_state()
            
            # Show preview of first added file
            if self.import_items:
                first_file = self.import_items[0].file_path
                self.preview_widget.set_preview_file(first_file)
    
    def remove_import_item(self, import_item: ImportFileItem):
        """Remove an import item"""
        if import_item in self.import_items:
            self.import_items.remove(import_item)
            import_item.setParent(None)
            import_item.deleteLater()
            
            self.update_ui_state()
    
    def clear_all_files(self):
        """Clear all files from the import list"""
        for item in self.import_items[:]:
            self.remove_import_item(item)
    
    def update_ui_state(self):
        """Update the UI state based on current files"""
        file_count = len(self.import_items)
        enabled_count = len([item for item in self.import_items if item.import_enabled])
        
        self.file_count_label.setText(f"{file_count} files ({enabled_count} enabled)")
        
        # Enable/disable buttons
        has_files = file_count > 0
        has_enabled_files = enabled_count > 0
        
        self.clear_all_button.setEnabled(has_files)
        self.import_button.setEnabled(has_enabled_files)
        
        # Update scroll area visibility
        self.files_scroll_area.setVisible(has_files)
        
        if not has_files:
            self.preview_widget.clear_preview()
    
    def get_selected_files(self) -> List[Dict[str, Any]]:
        """Get the list of files selected for import"""
        files_to_import = []
        
        # Get global options
        options = self.options_widget.get_options()
        
        for item in self.import_items:
            import_data = item.get_import_data()
            if import_data:
                import_data["options"] = options.copy()
                files_to_import.append(import_data)
        
        return files_to_import
    
    def accept(self):
        """Handle dialog acceptance"""
        files_to_import = self.get_selected_files()
        
        if not files_to_import:
            QMessageBox.warning(self, "No Files", 
                              "Please select at least one file to import.")
            return
        
        # Check for naming conflicts
        names = [item["import_name"] for item in files_to_import]
        duplicate_names = [name for name in names if names.count(name) > 1]
        
        if duplicate_names:
            QMessageBox.warning(self, "Naming Conflicts",
                              f"The following names are used multiple times: "
                              f"{', '.join(set(duplicate_names))}\n\n"
                              f"Please ensure all import names are unique.")
            return
        
        # Validate file names
        invalid_names = [name for name in names if not self.is_valid_asset_name(name)]
        if invalid_names:
            QMessageBox.warning(self, "Invalid Names",
                              f"The following names contain invalid characters: "
                              f"{', '.join(invalid_names)}\n\n"
                              f"Asset names should only contain letters, numbers, and underscores.")
            return
        
        super().accept()
    
    def is_valid_asset_name(self, name: str) -> bool:
        """Check if asset name is valid"""
        if not name or not name.replace("_", "").replace("-", "").isalnum():
            return False
        
        # Can't start with number
        if name[0].isdigit():
            return False
        
        return True
    
    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dropEvent(self, event):
        """Handle file drops"""
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = Path(url.toLocalFile())
                    if path.is_file():
                        file_paths.append(path)
            
            if file_paths:
                self.add_files(file_paths)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            super().dropEvent(event)

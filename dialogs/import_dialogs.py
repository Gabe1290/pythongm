#!/usr/bin/env python3
"""
Import dialogs for PyGameMaker IDE
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem,
    QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path

class ImportAssetsDialog(QDialog):
    """Dialog for importing multiple assets"""

    assetsImported = Signal(list)

    def __init__(self, asset_type, parent=None):
        super().__init__(parent)
        self.asset_type = asset_type
        self.setWindowTitle(self.tr("Import Assets"))
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)

        # File selection
        files_group = QGroupBox(self.tr("Select Files to Import"))
        files_layout = QVBoxLayout(files_group)

        self.file_list = QListWidget()
        files_layout.addWidget(self.file_list)

        buttons_layout = QHBoxLayout()

        add_files_btn = QPushButton(self.tr("Add Files..."))
        add_files_btn.clicked.connect(self.add_files)
        buttons_layout.addWidget(add_files_btn)

        add_folder_btn = QPushButton(self.tr("Add Folder..."))
        add_folder_btn.clicked.connect(self.add_folder)
        buttons_layout.addWidget(add_folder_btn)

        clear_btn = QPushButton(self.tr("Clear All"))
        clear_btn.clicked.connect(self.clear_files)
        buttons_layout.addWidget(clear_btn)

        buttons_layout.addStretch()
        files_layout.addLayout(buttons_layout)
        layout.addWidget(files_group)

        # Options
        options_group = QGroupBox(self.tr("Import Options"))
        options_layout = QVBoxLayout(options_group)

        self.auto_detect_type = QCheckBox(self.tr("Auto-detect asset type"))
        self.auto_detect_type.setChecked(True)
        options_layout.addWidget(self.auto_detect_type)

        self.copy_files = QCheckBox(self.tr("Copy files to project folder"))
        self.copy_files.setChecked(True)
        options_layout.addWidget(self.copy_files)

        layout.addWidget(options_group)

        # Dialog buttons
        dialog_buttons = QHBoxLayout()

        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)

        import_btn = QPushButton(self.tr("Import"))
        import_btn.clicked.connect(self.start_import)
        import_btn.setDefault(True)

        dialog_buttons.addStretch()
        dialog_buttons.addWidget(cancel_btn)
        dialog_buttons.addWidget(import_btn)

        layout.addLayout(dialog_buttons)

    def add_files(self):
        """Add files to import"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Select Files to Import"),
            "",
            self.tr("Images (*.png *.jpg *.jpeg *.bmp *.gif);;Sounds (*.wav *.mp3 *.ogg);;All Files (*)")
        )

        if files:
            self.selected_file = files[0]  # Store the first file
        else:
            print("🔥 : No files selected in QFileDialog")

        for file_path in files:
            item = QListWidgetItem(Path(file_path).name)
            item.setData(Qt.UserRole, file_path)
            self.file_list.addItem(item)

    def add_folder(self):
        """Add folder contents"""
        folder = QFileDialog.getExistingDirectory(self, self.tr("Select Folder"))
        if folder:
            folder_path = Path(folder)
            for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.wav', '.mp3', '.ogg']:
                for file_path in folder_path.rglob(f'*{ext}'):
                    item = QListWidgetItem(file_path.name)
                    item.setData(Qt.UserRole, str(file_path))
                    self.file_list.addItem(item)

    def clear_files(self):
        """Clear all files"""
        self.file_list.clear()

    def start_import(self):
        """Start importing"""
        files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            files.append(item.data(Qt.UserRole))

        if files:
            self.assetsImported.emit(files)
            self.accept()

    def get_selected_files(self):
        """Get the selected files for import"""

        if hasattr(self, 'selected_file') and self.selected_file:
            return [self.selected_file]

        return []

    def get_asset_names(self):
        """Get the asset names for import"""
        if hasattr(self, 'asset_name') and self.asset_name:
            return [self.asset_name]
        return []
    def exec(self):
        # Auto-open file dialog
        self.add_files()

        # Only proceed if file was selected
        if hasattr(self, 'selected_file') and self.selected_file:
            return 1  # Accept
        else:
            return 0  # Cancel

# Aliases for compatibility
AssetImportDialog = ImportAssetsDialog
ImportDialog = ImportAssetsDialog


# Additional aliases for compatibility
ImportAssetDialog = ImportAssetsDialog
AssetImportDialog = ImportAssetsDialog
ImportDialog = ImportAssetsDialog

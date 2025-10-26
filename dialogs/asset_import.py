#!/usr/bin/env python3
"""
Asset Import Dialog for PyGameMaker IDE
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QFileDialog, QGroupBox,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path

class AssetImportDialog(QDialog):
    """Dialog for importing game assets"""
    
    assetsImported = Signal(list)  # List of imported asset paths
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Assets")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Files to import
        files_group = QGroupBox("Files to Import")
        files_layout = QVBoxLayout(files_group)
        
        # File list
        self.file_list = QListWidget()
        files_layout.addWidget(self.file_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        
        self.add_files_button = QPushButton("Add Files...")
        self.add_files_button.clicked.connect(self.add_files)
        
        self.add_folder_button = QPushButton("Add Folder...")  
        self.add_folder_button.clicked.connect(self.add_folder)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected)
        
        button_layout.addWidget(self.add_files_button)
        button_layout.addWidget(self.add_folder_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        
        files_layout.addLayout(button_layout)
        layout.addWidget(files_group)
        
        # Import progress
        progress_group = QGroupBox("Import Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(100)
        self.progress_text.setReadOnly(True)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_text)
        
        layout.addWidget(progress_group)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.import_button = QPushButton("Import Assets")
        self.import_button.clicked.connect(self.import_assets)
        self.import_button.setDefault(True)
        
        dialog_buttons.addStretch()
        dialog_buttons.addWidget(self.cancel_button)
        dialog_buttons.addWidget(self.import_button)
        
        layout.addLayout(dialog_buttons)
        
    def add_files(self):
        """Add files to import list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Assets to Import",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;Sounds (*.wav *.mp3 *.ogg);;All Files (*)"
        )
        
        for file_path in files:
            self.file_list.addItem(file_path)
            
    def add_folder(self):
        """Add folder contents to import list"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Import")
        
        if folder:
            folder_path = Path(folder)
            # Add supported files from folder
            for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.wav', '.mp3', '.ogg']:
                for file_path in folder_path.rglob(f'*{ext}'):
                    self.file_list.addItem(str(file_path))
                    
    def remove_selected(self):
        """Remove selected items from list"""
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
            
    def import_assets(self):
        """Import the selected assets"""
        file_paths = []
        for i in range(self.file_list.count()):
            file_paths.append(self.file_list.item(i).text())
            
        if not file_paths:
            return
            
        # Simulate import process
        self.progress_bar.setMaximum(len(file_paths))
        self.progress_text.clear()
        
        for i, file_path in enumerate(file_paths):
            self.progress_bar.setValue(i + 1)
            self.progress_text.append(f"Imported: {Path(file_path).name}")
            
        self.assetsImported.emit(file_paths)
        self.accept()

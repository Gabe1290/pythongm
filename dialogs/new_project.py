#!/usr/bin/env python3
"""
New Project Dialog for PyGameMaker IDE
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Signal
from pathlib import Path

class NewProjectDialog(QDialog):
    """Dialog for creating new projects"""

    projectCreated = Signal(str, str)  # project_path, project_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # Project details group
        details_group = QGroupBox("Project Details")
        details_layout = QFormLayout(details_group)

        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name...")
        details_layout.addRow("Project Name:", self.name_edit)

        # Project location
        location_layout = QHBoxLayout()
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Select project location...")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_location)

        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(self.browse_button)
        details_layout.addRow("Location:", location_layout)

        layout.addWidget(details_group)

        # Template group (placeholder)
        template_group = QGroupBox("Project Template")
        template_layout = QVBoxLayout(template_group)
        template_layout.addWidget(QLabel("• Empty Project (default)"))
        template_layout.addWidget(QLabel("• Platform Game Template"))
        template_layout.addWidget(QLabel("• Top-Down Game Template"))
        layout.addWidget(template_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.create_button = QPushButton("Create Project")
        self.create_button.clicked.connect(self.create_project)
        self.create_button.setDefault(True)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)

        layout.addLayout(button_layout)

        # Set default location
        self.location_edit.setText(str(Path.home() / "Documents"))

    def browse_location(self):
        """Browse for project location"""
        location = QFileDialog.getExistingDirectory(
            self,
            "Select Project Location",
            self.location_edit.text()
        )

        if location:
            self.location_edit.setText(location)

    def create_project(self):
        """Create the project"""
        project_name = self.name_edit.text().strip()
        project_location = self.location_edit.text().strip()

        if not project_name:
            QMessageBox.warning(self, "Error", "Please enter a project name.")
            return

        if not project_location:
            QMessageBox.warning(self, "Error", "Please select a project location.")
            return

        project_path = Path(project_location) / project_name

        if project_path.exists():
            reply = QMessageBox.question(
                self,
                "Project Exists",
                f"A folder named '{project_name}' already exists.\nDo you want to use it anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Emit signal with project details
        self.projectCreated.emit(str(project_path), project_name)
        self.accept()

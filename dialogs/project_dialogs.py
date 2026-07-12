#!/usr/bin/env python3
"""
Project dialogs for PyGameMaker IDE: New Project and Project Settings.

ExportProjectDialog and BuildProjectDialog were retired 2026-07-12: the
IDE had TWO overlapping export UIs (File > Export Project vs Build >
Export Game). Everything now routes through the registry-driven dialog
in core/ide_window.export_game (export/registry.py); the old dialog's
distinct targets live on as registry entries (kivy_project, source_zip)
and its host-OS desktop routing moved to
export.registry.desktop_exporter_for_host.
"""

from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QTextEdit, QFileDialog,
                               QDialogButtonBox, QGroupBox, QCheckBox,
                               QComboBox, QSpinBox, QMessageBox)

from utils import documents_dir


class NewProjectDialog(QDialog):
    """FIXED New Project Dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_data = {}
        self.parent_ide = parent

        self.setWindowTitle(self.tr("New Project"))
        self.setModal(True)
        self.resize(500, 400)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        details_group = QGroupBox(self.tr("Project Details"))
        details_layout = QFormLayout(details_group)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText(self.tr("Enter project name..."))
        details_layout.addRow(self.tr("Project Name:"), self.project_name_edit)

        path_layout = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText(self.tr("Choose project location..."))

        self.browse_button = QPushButton(self.tr("Browse..."))
        self.browse_button.clicked.connect(self.browse_project_path)

        path_layout.addWidget(self.project_path_edit)
        path_layout.addWidget(self.browse_button)
        details_layout.addRow(self.tr("Location:"), path_layout)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText(self.tr("Optional project description..."))
        details_layout.addRow(self.tr("Description:"), self.description_edit)

        # Template selection: display name -> template id passed to ProjectManager
        self.template_combo = QComboBox()
        self._template_options = [
            (self.tr("Empty Project"), "empty"),
            (self.tr("With Game Over Screen"), "gameover"),
        ]
        for label, _id in self._template_options:
            self.template_combo.addItem(label)
        details_layout.addRow(self.tr("Template:"), self.template_combo)

        layout.addWidget(details_group)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_project)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_settings(self):
        try:
            if isinstance(self.project_data, dict):
                name = self.project_data.get("name", "")
                path = self.project_data.get("path", "")
            else:
                name = ""
                path = ""

            self.project_name_edit.setText(name)
            self.project_path_edit.setText(path)

            if not path:
                default_path = str(documents_dir() / "PyGameMaker Projects")
                self.project_path_edit.setText(default_path)

            print("✅ New project dialog settings loaded")
        except Exception as e:
            print(f"⚠️  New project dialog error: {e}")
            self.project_name_edit.setText("")
            default_path = str(documents_dir() / "PyGameMaker Projects")
            self.project_path_edit.setText(default_path)

    def browse_project_path(self):
        current_path = self.project_path_edit.text()
        if not current_path:
            current_path = str(documents_dir())

        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose Project Location"), current_path)
        if folder:
            self.project_path_edit.setText(folder)

    def accept_project(self):
        project_name = self.project_name_edit.text().strip()
        project_path = self.project_path_edit.text().strip()

        if not project_name:
            QMessageBox.warning(self, self.tr("Invalid Input"), self.tr("Please enter a project name."))
            return

        if not project_path:
            QMessageBox.warning(self, self.tr("Invalid Input"), self.tr("Please choose a project location."))
            return

        template_id = self._template_options[self.template_combo.currentIndex()][1]

        self.project_data = {
            "name": project_name,
            "path": project_path,
            "location": project_path,
            "template": template_id,
            "description": self.description_edit.toPlainText(),
            "create_folder": True,
            "target_platform": "Desktop"
        }

        self.accept()

    def get_project_info(self):
        return self.project_data


class ProjectSettingsDialog(QDialog):
    """Project Settings Dialog"""

    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)

        if isinstance(project_data, dict):
            self.project_data = project_data.copy()
        else:
            self.project_data = {}

        self.parent_ide = parent

        self.setWindowTitle(self.tr("Project Settings"))
        self.setModal(True)
        self.resize(500, 400)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        info_group = QGroupBox(self.tr("Project Information"))
        info_layout = QFormLayout(info_group)

        self.project_name_edit = QLineEdit()
        info_layout.addRow(self.tr("Project Name:"), self.project_name_edit)

        self.project_path_edit = QLineEdit()
        self.project_path_edit.setReadOnly(True)
        info_layout.addRow(self.tr("Project Path:"), self.project_path_edit)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        info_layout.addRow(self.tr("Description:"), self.description_edit)

        layout.addWidget(info_group)

        settings_group = QGroupBox(self.tr("Settings"))
        settings_layout = QFormLayout(settings_group)

        self.auto_save_check = QCheckBox()
        settings_layout.addRow(self.tr("Auto-save:"), self.auto_save_check)

        self.target_platform = QComboBox()
        self.target_platform.addItems([self.tr("Desktop"), self.tr("Web"), self.tr("Mobile")])
        settings_layout.addRow(self.tr("Target Platform:"), self.target_platform)

        layout.addWidget(settings_group)

        # Game Settings group
        game_group = QGroupBox(self.tr("Game Settings"))
        game_layout = QFormLayout(game_group)

        self.starting_lives_spin = QSpinBox()
        self.starting_lives_spin.setRange(0, 99)
        self.starting_lives_spin.setValue(3)
        game_layout.addRow(self.tr("Starting Lives:"), self.starting_lives_spin)

        self.show_lives_check = QCheckBox()
        game_layout.addRow(self.tr("Show Lives in Caption:"), self.show_lives_check)

        self.starting_score_spin = QSpinBox()
        self.starting_score_spin.setRange(0, 999999)
        self.starting_score_spin.setValue(0)
        game_layout.addRow(self.tr("Starting Score:"), self.starting_score_spin)

        self.show_score_check = QCheckBox()
        game_layout.addRow(self.tr("Show Score in Caption:"), self.show_score_check)

        self.starting_health_spin = QSpinBox()
        self.starting_health_spin.setRange(0, 1000)
        self.starting_health_spin.setValue(100)
        game_layout.addRow(self.tr("Starting Health:"), self.starting_health_spin)

        self.show_health_check = QCheckBox()
        game_layout.addRow(self.tr("Show Health in Caption:"), self.show_health_check)

        layout.addWidget(game_group)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_settings(self):
        try:
            if isinstance(self.project_data, dict):
                self.project_name_edit.setText(self.project_data.get("name", ""))
                self.project_path_edit.setText(self.project_data.get("path", ""))
                self.description_edit.setPlainText(self.project_data.get("description", ""))
                self.auto_save_check.setChecked(self.project_data.get("auto_save", True))

                platform = self.project_data.get("target_platform", "Desktop")
                index = self.target_platform.findText(platform)
                if index >= 0:
                    self.target_platform.setCurrentIndex(index)

                # Load game settings from nested 'settings' dict
                settings = self.project_data.get("settings", {})
                self.starting_lives_spin.setValue(settings.get("starting_lives", 3))
                self.show_lives_check.setChecked(settings.get("show_lives_in_caption", False))
                self.starting_score_spin.setValue(settings.get("starting_score", 0))
                self.show_score_check.setChecked(settings.get("show_score_in_caption", False))
                self.starting_health_spin.setValue(int(settings.get("starting_health", 100)))
                self.show_health_check.setChecked(settings.get("show_health_in_caption", False))
            else:
                self.project_name_edit.setText("Untitled Project")
                self.auto_save_check.setChecked(True)

            print("✅ Project settings loaded")
        except Exception as e:
            print(f"⚠️  Project settings error: {e}")
            self.project_name_edit.setText("Untitled Project")
            self.auto_save_check.setChecked(True)

    def accept_settings(self):
        if not isinstance(self.project_data, dict):
            self.project_data = {}

        self.project_data.update({
            "name": self.project_name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "auto_save": self.auto_save_check.isChecked(),
            "target_platform": self.target_platform.currentText()
        })

        # Save game settings to nested 'settings' dict
        if "settings" not in self.project_data:
            self.project_data["settings"] = {}

        self.project_data["settings"].update({
            "starting_lives": self.starting_lives_spin.value(),
            "show_lives_in_caption": self.show_lives_check.isChecked(),
            "starting_score": self.starting_score_spin.value(),
            "show_score_in_caption": self.show_score_check.isChecked(),
            "starting_health": self.starting_health_spin.value(),
            "show_health_in_caption": self.show_health_check.isChecked()
        })

        self.accept()

    def get_project_info(self):
        return self.project_data

    def get_settings(self):
        """Alias for get_project_info for compatibility"""
        return self.project_data


__all__ = [
    'NewProjectDialog',
    'ProjectSettingsDialog',
]

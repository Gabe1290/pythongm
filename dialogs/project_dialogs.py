#!/usr/bin/env python3
"""
ULTIMATE COMPLETE Project Dialogs for PyGameMaker IDE
Includes ALL dialog classes that could possibly be imported
"""

import os
import json
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QTextEdit, QLabel, 
                               QFileDialog, QDialogButtonBox, QGroupBox,
                               QCheckBox, QComboBox, QSpinBox, QMessageBox,
                               QListWidget, QSplitter, QProgressBar, QTabWidget,
                               QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt


class NewProjectDialog(QDialog):
    """FIXED New Project Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_data = {}
        self.parent_ide = parent
        
        self.setWindowTitle("New Project")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        details_group = QGroupBox("Project Details")
        details_layout = QFormLayout(details_group)
        
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("Enter project name...")
        details_layout.addRow("Project Name:", self.project_name_edit)
        
        path_layout = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText("Choose project location...")
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_project_path)
        
        path_layout.addWidget(self.project_path_edit)
        path_layout.addWidget(self.browse_button)
        details_layout.addRow("Location:", path_layout)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Optional project description...")
        details_layout.addRow("Description:", self.description_edit)
        
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
                default_path = str(Path.home() / "Documents" / "PyGameMaker Projects")
                self.project_path_edit.setText(default_path)
            
            print("✅ New project dialog settings loaded")
        except Exception as e:
            print(f"⚠️  New project dialog error: {e}")
            self.project_name_edit.setText("")
            default_path = str(Path.home() / "Documents" / "PyGameMaker Projects")
            self.project_path_edit.setText(default_path)
    
    def browse_project_path(self):
        current_path = self.project_path_edit.text()
        if not current_path:
            current_path = str(Path.home() / "Documents")
        
        folder = QFileDialog.getExistingDirectory(self, "Choose Project Location", current_path)
        if folder:
            self.project_path_edit.setText(folder)
    
    def accept_project(self):
        project_name = self.project_name_edit.text().strip()
        project_path = self.project_path_edit.text().strip()
        
        if not project_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a project name.")
            return
        
        if not project_path:
            QMessageBox.warning(self, "Invalid Input", "Please choose a project location.")
            return
        
        self.project_data = {
            "name": project_name,
            "path": project_path,
            "location": project_path,
            "template": "Empty Project",
            "description": self.description_edit.toPlainText(),
            "create_folder": True,
            "target_platform": "Desktop"
        }
        
        self.accept()
    
    def get_project_info(self):
        return self.project_data


class OpenProjectDialog(QDialog):
    """Open Project Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_data = {}
        self.parent_ide = parent
        self.selected_project_path = None
        
        self.setWindowTitle("Open Project")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        recent_group = QGroupBox("Recent Projects")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_projects_list = QListWidget()
        self.recent_projects_list.itemDoubleClicked.connect(self.open_selected_project)
        recent_layout.addWidget(self.recent_projects_list)
        layout.addWidget(recent_group)
        
        browse_group = QGroupBox("Browse for Project")
        browse_layout = QHBoxLayout(browse_group)
        
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText("Select project file...")
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_project)
        
        browse_layout.addWidget(self.project_path_edit)
        browse_layout.addWidget(self.browse_button)
        layout.addWidget(browse_group)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_project)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_settings(self):
        try:
            from utils.config import Config
            recent_projects = Config.get_recent_projects()
            
            for project_path in recent_projects:
                if Path(project_path).exists():
                    project_name = Path(project_path).name
                    self.recent_projects_list.addItem(f"{project_name} - {project_path}")
            
            print("✅ Recent projects loaded")
        except Exception as e:
            print(f"⚠️  Error loading recent projects: {e}")
    
    def browse_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PyGameMaker Project", str(Path.home() / "Documents"),
            "PyGameMaker Projects (*.json);;All Files (*)"
        )
        if file_path:
            self.project_path_edit.setText(file_path)
    
    def open_selected_project(self, item):
        text = item.text()
        if " - " in text:
            project_path = text.split(" - ", 1)[1]
            self.project_path_edit.setText(project_path)
    
    def accept_project(self):
        """Handle project creation - COMPLETE FIX with ALL expected keys"""
        project_name = self.project_name_edit.text().strip()
        project_path = self.project_path_edit.text().strip()

        if not project_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a project name.")
            return

        if not project_path:
            QMessageBox.warning(self, "Invalid Input", "Please choose a project location.")
            return

        # Store ALL expected project information
        self.project_data = {
            "name": project_name,
            "path": project_path,
            "location": project_path,  # IDE expects both path and location
            "description": self.description_edit.toPlainText(),
            "template": "Empty Project",  # FIX: Add missing template key
            "project_type": "2D Game",
            "target_platform": "Desktop",
            "create_folder": True,
            "version": "1.0.0",
            "author": "",
            "copyright": ""
        }

        self.accept()

    def get_project_info(self):
        return {
            "path": self.selected_project_path,
            "data": self.project_data
        }


class ProjectSettingsDialog(QDialog):
    """Project Settings Dialog"""
    
    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        
        if isinstance(project_data, dict):
            self.project_data = project_data.copy()
        else:
            self.project_data = {}
        
        self.parent_ide = parent
        
        self.setWindowTitle("Project Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("Project Information")
        info_layout = QFormLayout(info_group)
        
        self.project_name_edit = QLineEdit()
        info_layout.addRow("Project Name:", self.project_name_edit)
        
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setReadOnly(True)
        info_layout.addRow("Project Path:", self.project_path_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        info_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(info_group)
        
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.auto_save_check = QCheckBox()
        settings_layout.addRow("Auto-save:", self.auto_save_check)
        
        self.target_platform = QComboBox()
        self.target_platform.addItems(["Desktop", "Web", "Mobile"])
        settings_layout.addRow("Target Platform:", self.target_platform)
        
        layout.addWidget(settings_group)
        
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
        
        self.accept()
    
    def get_project_info(self):
        return self.project_data


class ExportProjectDialog(QDialog):
    """Export Project Dialog - ADDED to fix import error"""
    
    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        
        if isinstance(project_data, dict):
            self.project_data = project_data.copy()
        else:
            self.project_data = {}
        
        self.parent_ide = parent
        self.export_settings = {}
        
        self.setWindowTitle("Export Project")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Export target
        target_group = QGroupBox("Export Target")
        target_layout = QFormLayout(target_group)
        
        self.export_platform = QComboBox()
        self.export_platform.addItems([
            "Desktop Executable (.exe/.app)", 
            "Web (HTML5)", 
            "Mobile (Kivy)",
            "Mobile (APK)", 
            "Source Code (.zip)"
        ])
        target_layout.addRow("Target Platform:", self.export_platform)
        
        # Output path
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Choose export location...")
        
        self.browse_output_button = QPushButton("Browse...")
        self.browse_output_button.clicked.connect(self.browse_output_path)
        
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_output_button)
        target_layout.addRow("Output Location:", output_layout)
        
        layout.addWidget(target_group)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout(options_group)
        
        self.include_assets_check = QCheckBox()
        self.include_assets_check.setChecked(True)
        options_layout.addRow("Include Assets:", self.include_assets_check)
        
        self.optimize_check = QCheckBox()
        self.optimize_check.setChecked(True)
        options_layout.addRow("Optimize for Release:", self.optimize_check)
        
        self.include_debug_check = QCheckBox()
        self.include_debug_check.setChecked(False)
        options_layout.addRow("Include Debug Info:", self.include_debug_check)
        
        layout.addWidget(options_group)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_export)
        button_box.rejected.connect(self.reject)
        
        self.export_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.export_button.setText("Export")
        
        layout.addWidget(button_box)
    
    def load_settings(self):
        try:
            # Set default output path
            if isinstance(self.project_data, dict):
                project_name = self.project_data.get("name", "Untitled")
                default_output = str(Path.home() / "Desktop" / f"{project_name}_export")
                self.output_path_edit.setText(default_output)
            
            print("✅ Export dialog settings loaded")
        except Exception as e:
            print(f"⚠️  Export dialog error: {e}")
            self.output_path_edit.setText(str(Path.home() / "Desktop" / "exported_game"))
    
    def browse_output_path(self):
        current_path = self.output_path_edit.text()
        if not current_path:
            current_path = str(Path.home() / "Desktop")
        
        folder = QFileDialog.getExistingDirectory(self, "Choose Export Location", current_path)
        if folder:
            self.output_path_edit.setText(folder)
    
    def get_project_info(self):
        return {
            "export_settings": self.export_settings,
            "project_data": self.project_data
        }

    def accept_export(self):
        output_path = self.output_path_edit.text().strip()

        if not output_path:
            QMessageBox.warning(self, "Invalid Output", "Please choose an export location.")
            return

        # Store export settings
        self.export_settings = {
            "platform": self.export_platform.currentText(),
            "output_path": output_path,
            "include_assets": self.include_assets_check.isChecked(),
            "optimize": self.optimize_check.isChecked(),
            "include_debug": self.include_debug_check.isChecked()
        }

        # Route to appropriate exporter based on platform
        platform = self.export_platform.currentText()

        if platform == "Web (HTML5)":
            self._export_html5()
        elif platform == "Mobile (Kivy)" or platform == "Mobile (APK)":
            self._export_kivy()
        elif platform == "Source Code (.zip)":
            self._export_zip()
        elif platform == "Desktop Executable (.exe/.app)":
            self._export_executable()
        else:
            # Unknown platform - just accept
            self.accept()

    def _export_kivy(self):
        """Export project using Kivy exporter with project adapter"""
        try:
            from export.Kivy.project_adapter import export_with_adapter  # ✅ NEW
            import subprocess
            import platform
            
            output_path = self.output_path_edit.text()
            
            # Get the project_manager from parent IDE
            if hasattr(self.parent_ide, 'project_manager'):
                project_manager = self.parent_ide.project_manager
            else:
                QMessageBox.critical(self, "Export Error", 
                                "Could not access project manager")
                return
            
            # Use the adapter to export
            success = export_with_adapter(project_manager, output_path)  # ✅ NEW
            
            if success:
                result = QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Kivy project exported to:\n{output_path}\n\n"
                    "Would you like to open the export directory?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if result == QMessageBox.StandardButton.Yes:
                    if platform.system() == 'Windows':
                        os.startfile(output_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', output_path])
                
                self.accept()
            else:
                QMessageBox.warning(self, "Export Failed", 
                                "Failed to export project. Check console for errors.")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "Export Error",
                                f"Error during export:\n{str(e)}\n\n{error_details}")

    def _export_html5(self):
        """Export project as HTML5"""
        try:
            from export.HTML5.html5_exporter import HTML5Exporter
            from pathlib import Path

            output_path = Path(self.output_path_edit.text())
            project_path = Path(self.parent_ide.current_project_path)

            exporter = HTML5Exporter()
            success = exporter.export(project_path, output_path)

            if success:
                html_file = output_path / f"{self.project_data.get('name', 'game')}.html"
                result = QMessageBox.information(
                    self,
                    "Export Successful",
                    f"HTML5 game exported to:\n{html_file}\n\n"
                    "Would you like to open the export directory?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if result == QMessageBox.StandardButton.Yes:
                    import subprocess
                    import platform
                    if platform.system() == 'Windows':
                        os.startfile(output_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', str(output_path)])
                    else:  # Linux
                        subprocess.run(['xdg-open', str(output_path)])

                self.accept()
            else:
                QMessageBox.warning(self, "Export Failed",
                                  "Failed to export HTML5 game. Check console for errors.")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "Export Error",
                                f"Error during HTML5 export:\n{str(e)}\n\n{error_details}")

    def _export_zip(self):
        """Export project as ZIP"""
        try:
            from pathlib import Path

            # Create output filename
            project_name = self.project_data.get('name', 'project')
            output_dir = Path(self.output_path_edit.text())
            output_file = output_dir / f"{project_name}.zip"

            # Use project manager to export
            if hasattr(self.parent_ide, 'project_manager'):
                success = self.parent_ide.project_manager.export_project_as_zip(output_file)

                if success:
                    result = QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Project exported to:\n{output_file}\n\n"
                        "Would you like to open the export directory?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if result == QMessageBox.StandardButton.Yes:
                        import subprocess
                        import platform
                        if platform.system() == 'Windows':
                            os.startfile(output_dir)
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', str(output_dir)])
                        else:  # Linux
                            subprocess.run(['xdg-open', str(output_dir)])

                    self.accept()
                else:
                    QMessageBox.warning(self, "Export Failed",
                                      "Failed to export ZIP file. Check console for errors.")
            else:
                QMessageBox.critical(self, "Export Error",
                                   "Could not access project manager")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "Export Error",
                                f"Error during ZIP export:\n{str(e)}\n\n{error_details}")

    def _export_executable(self):
        """Export project as executable (.exe/.app)"""
        try:
            from export.exe import ExeExporter
            from pathlib import Path
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt

            # Get project path (directory containing project.json)
            project_dir = Path(self.parent_ide.current_project_path)
            project_file = project_dir / "project.json"

            if not project_file.exists():
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Project file not found: {project_file}"
                )
                return

            # Get output directory
            output_dir = Path(self.output_path_edit.text())

            # Export settings
            export_settings = {
                'include_assets': True,
                'include_debug': False,  # No console window by default
                'optimize': True         # Use UPX compression
            }

            # Create progress dialog
            progress = QProgressDialog(
                "Initializing export...",
                "Cancel",
                0, 100,
                self
            )
            progress.setWindowTitle("Exporting Executable")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            # Create exporter
            exporter = ExeExporter()

            # Connect signals
            def update_progress(value, message):
                progress.setValue(value)
                progress.setLabelText(message)

            success_result = [False]  # Use list to allow modification in nested function
            error_message = [""]

            def export_finished(success, message):
                success_result[0] = success
                error_message[0] = message
                progress.close()

            exporter.progress_update.connect(update_progress)
            exporter.export_complete.connect(export_finished)

            # Run export
            exporter.export_project(str(project_file), str(output_dir), export_settings)

            # Show result
            if success_result[0]:
                result = QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Executable exported to:\n{output_dir}\n\n"
                    "Would you like to open the export directory?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if result == QMessageBox.StandardButton.Yes:
                    import subprocess
                    import platform
                    if platform.system() == 'Windows':
                        os.startfile(str(output_dir))
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', str(output_dir)])
                    else:  # Linux
                        subprocess.run(['xdg-open', str(output_dir)])

                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    f"Failed to export executable:\n\n{error_message[0]}"
                )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self,
                "Export Error",
                f"Error during executable export:\n{str(e)}\n\n{error_details}"
            )

class BuildProjectDialog(QDialog):
    """Build Project Dialog - ADDED for completeness"""
    
    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        
        if isinstance(project_data, dict):
            self.project_data = project_data.copy()
        else:
            self.project_data = {}
        
        self.parent_ide = parent
        self.build_settings = {}
        
        self.setWindowTitle("Build Project")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Build configuration
        config_group = QGroupBox("Build Configuration")
        config_layout = QFormLayout(config_group)
        
        self.build_type = QComboBox()
        self.build_type.addItems(["Debug", "Release"])
        config_layout.addRow("Build Type:", self.build_type)
        
        self.optimization_level = QComboBox()
        self.optimization_level.addItems(["None", "Basic", "Full"])
        config_layout.addRow("Optimization:", self.optimization_level)
        
        layout.addWidget(config_group)
        
        # Build options
        options_group = QGroupBox("Build Options")
        options_layout = QFormLayout(options_group)
        
        self.clean_build_check = QCheckBox()
        options_layout.addRow("Clean Build:", self.clean_build_check)
        
        self.verbose_output_check = QCheckBox()
        options_layout.addRow("Verbose Output:", self.verbose_output_check)
        
        layout.addWidget(options_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_build)
        button_box.rejected.connect(self.reject)
        
        self.build_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.build_button.setText("Build")
        
        layout.addWidget(button_box)
    
    def load_settings(self):
        try:
            # Set defaults
            self.build_type.setCurrentText("Debug")
            self.optimization_level.setCurrentText("Basic")
            
            print("✅ Build dialog settings loaded")
        except Exception as e:
            print(f"⚠️  Build dialog error: {e}")
    
    def accept_build(self):
        self.build_settings = {
            "build_type": self.build_type.currentText(),
            "optimization": self.optimization_level.currentText(),
            "clean_build": self.clean_build_check.isChecked(),
            "verbose_output": self.verbose_output_check.isChecked()
        }
        
        self.accept()
    
    def get_project_info(self):
        return {
            "build_settings": self.build_settings,
            "project_data": self.project_data
        }


# Export ALL possible dialog classes to prevent ANY import errors
__all__ = [
    'NewProjectDialog',
    'OpenProjectDialog', 
    'ProjectSettingsDialog',
    'ExportProjectDialog',
    'BuildProjectDialog'
]

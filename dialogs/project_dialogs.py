#!/usr/bin/env python3
"""
ULTIMATE COMPLETE Project Dialogs for PyGameMaker IDE
Includes ALL dialog classes that could possibly be imported
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QTextEdit, QFileDialog,
                               QDialogButtonBox, QGroupBox, QCheckBox,
                               QComboBox, QSpinBox, QMessageBox, QListWidget,
                               QProgressBar)

from utils import desktop_dir, documents_dir


def _desktop_exporter_for_host(host_os):
    """Return the PyInstaller-based exporter class that builds a native
    desktop artifact for ``host_os`` (a ``platform.system()`` value): a
    Windows ``.exe``, a macOS ``.app``, or a Linux ELF binary.

    PyInstaller cannot cross-compile — it always builds for the platform it
    runs on — so the host OS, not a user choice, determines the target. This
    is why the Export dialog offers a single "Desktop Executable (.exe/.app)"
    option rather than three platform buttons. Anything that isn't macOS or
    Windows (Linux and other Unixes) gets the Linux exporter.
    """
    if host_os == 'Darwin':
        from export.macos import MacOSExporter
        return MacOSExporter
    if host_os == 'Windows':
        from export.exe import ExeExporter
        return ExeExporter
    from export.linux import LinuxExporter
    return LinuxExporter


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

        self.setWindowTitle(self.tr("Export Project"))
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Export target
        target_group = QGroupBox(self.tr("Export Target"))
        target_layout = QFormLayout(target_group)

        self.export_platform = QComboBox()
        # Store a locale-independent id as userData and route on currentData():
        # accept_export used to compare the (translated) display text against
        # English literals, so 'Desktop Executable' and 'Source Code' exports
        # silently no-op'd in French/etc. with a false success message
        # (audit M13).
        self.export_platform.addItem(self.tr("Desktop Executable (.exe/.app)"), "exe")
        self.export_platform.addItem(self.tr("Web (HTML5)"), "html5")
        self.export_platform.addItem(self.tr("Mobile (Kivy)"), "kivy")
        self.export_platform.addItem(self.tr("Mobile (APK)"), "apk")
        self.export_platform.addItem(self.tr("Source Code (.zip)"), "zip")
        target_layout.addRow(self.tr("Target Platform:"), self.export_platform)

        # Output path
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText(self.tr("Choose export location..."))

        self.browse_output_button = QPushButton(self.tr("Browse..."))
        self.browse_output_button.clicked.connect(self.browse_output_path)

        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_output_button)
        target_layout.addRow(self.tr("Output Location:"), output_layout)

        layout.addWidget(target_group)

        # Export options
        options_group = QGroupBox(self.tr("Export Options"))
        options_layout = QFormLayout(options_group)

        self.include_assets_check = QCheckBox()
        self.include_assets_check.setChecked(True)
        options_layout.addRow(self.tr("Include Assets:"), self.include_assets_check)

        self.optimize_check = QCheckBox()
        self.optimize_check.setChecked(True)
        options_layout.addRow(self.tr("Optimize for Release:"), self.optimize_check)

        self.include_debug_check = QCheckBox()
        self.include_debug_check.setChecked(False)
        options_layout.addRow(self.tr("Include Debug Info:"), self.include_debug_check)

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
        self.export_button.setText(self.tr("Export"))

        layout.addWidget(button_box)

    def load_settings(self):
        try:
            # Set default output path
            if isinstance(self.project_data, dict):
                project_name = self.project_data.get("name", "Untitled")
                default_output = str(desktop_dir() / f"{project_name}_export")
                self.output_path_edit.setText(default_output)

            print("✅ Export dialog settings loaded")
        except Exception as e:
            print(f"⚠️  Export dialog error: {e}")
            self.output_path_edit.setText(str(desktop_dir() / "exported_game"))

    def browse_output_path(self):
        current_path = self.output_path_edit.text()
        if not current_path:
            current_path = str(desktop_dir())

        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose Export Location"), current_path)
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
            QMessageBox.warning(self, self.tr("Invalid Output"), self.tr("Please choose an export location."))
            return

        # Route on the locale-independent userData id, not the display text
        # (audit M13).
        platform = self.export_platform.currentData()

        # Store export settings (id is stable across locales)
        self.export_settings = {
            "platform": platform,
            "output_path": output_path,
            "include_assets": self.include_assets_check.isChecked(),
            "optimize": self.optimize_check.isChecked(),
            "include_debug": self.include_debug_check.isChecked()
        }

        if platform == "html5":
            self._export_html5()
        elif platform in ("kivy", "apk"):
            self._export_kivy()
        elif platform == "zip":
            self._export_zip()
        elif platform == "exe":
            self._export_executable()
        else:
            # Unknown platform — surface it instead of a silent false success.
            QMessageBox.warning(
                self, self.tr("Export Failed"),
                self.tr("Unknown export target: {0}").format(
                    self.export_platform.currentText())
            )

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
                QMessageBox.critical(self, self.tr("Export Error"),
                                self.tr("Could not access project manager"))
                return

            # Use the adapter to export
            success = export_with_adapter(project_manager, output_path)  # ✅ NEW

            if success:
                result = QMessageBox.information(
                    self,
                    self.tr("Export Successful"),
                    self.tr("Kivy project exported to:\n{0}\n\nWould you like to open the export directory?").format(output_path),
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
                QMessageBox.warning(self, self.tr("Export Failed"),
                                self.tr("Failed to export project. Check console for errors."))
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, self.tr("Export Error"),
                                self.tr("Error during export:\n{0}\n\n{1}").format(str(e), error_details))

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
                    self.tr("Export Successful"),
                    self.tr("HTML5 game exported to:\n{0}\n\nWould you like to open the export directory?").format(html_file),
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
                QMessageBox.warning(self, self.tr("Export Failed"),
                                  self.tr("Failed to export HTML5 game. Check console for errors."))
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, self.tr("Export Error"),
                                self.tr("Error during HTML5 export:\n{0}\n\n{1}").format(str(e), error_details))

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
                        self.tr("Export Successful"),
                        self.tr("Project exported to:\n{0}\n\nWould you like to open the export directory?").format(output_file),
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
                    QMessageBox.warning(self, self.tr("Export Failed"),
                                      self.tr("Failed to export ZIP file. Check console for errors."))
            else:
                QMessageBox.critical(self, self.tr("Export Error"),
                                   self.tr("Could not access project manager"))
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, self.tr("Export Error"),
                                self.tr("Error during ZIP export:\n{0}\n\n{1}").format(str(e), error_details))

    def _collect_export_settings(self) -> dict:
        """Read the Export Options checkboxes into a settings dict (L9)."""
        return {
            'include_assets': self.include_assets_check.isChecked(),
            'include_debug': self.include_debug_check.isChecked(),
            'optimize': self.optimize_check.isChecked(),
        }

    def _export_executable(self):
        """Export project as a native desktop executable for the host OS.

        The single "Desktop Executable (.exe/.app)" target builds for the
        machine the IDE is running on — PyInstaller cannot cross-compile, so
        a Windows .exe must be built on Windows, a Linux ELF on Linux, and a
        macOS .app on macOS. Previously this always used the Windows-only
        ExeExporter, so on macOS/Linux it failed with "Windows EXE export
        must be run on a Windows system" and never reached the matching
        Linux/macOS exporters.
        """
        try:
            import platform as _host_platform
            from pathlib import Path
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt

            _DesktopExporter = _desktop_exporter_for_host(_host_platform.system())

            # Get project path (directory containing project.json)
            project_dir = Path(self.parent_ide.current_project_path)
            project_file = project_dir / "project.json"

            if not project_file.exists():
                QMessageBox.critical(
                    self,
                    self.tr("Export Error"),
                    self.tr("Project file not found: {0}").format(project_file)
                )
                return

            # Get output directory
            output_dir = Path(self.output_path_edit.text())

            # Export settings — honor the dialog's Export Options checkboxes
            # instead of hardcoding them (L9). ExeExporter consumes
            # include_debug (console/debug build) and optimize (UPX).
            export_settings = self._collect_export_settings()

            # Create progress dialog
            progress = QProgressDialog(
                self.tr("Initializing export..."),
                self.tr("Cancel"),
                0, 100,
                self
            )
            progress.setWindowTitle(self.tr("Exporting Executable"))
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            # Create the host-appropriate exporter (selected above).
            exporter = _DesktopExporter()

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
                    self.tr("Export Successful"),
                    self.tr("Executable exported to:\n{0}\n\nWould you like to open the export directory?").format(output_dir),
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
                    self.tr("Export Failed"),
                    self.tr("Failed to export executable:\n\n{0}").format(error_message[0])
                )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self,
                self.tr("Export Error"),
                self.tr("Error during executable export:\n{0}\n\n{1}").format(str(e), error_details)
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

        self.setWindowTitle(self.tr("Build Project"))
        self.setModal(True)
        self.resize(500, 400)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Build configuration
        config_group = QGroupBox(self.tr("Build Configuration"))
        config_layout = QFormLayout(config_group)

        self.build_type = QComboBox()
        self.build_type.addItems([self.tr("Debug"), self.tr("Release")])
        config_layout.addRow(self.tr("Build Type:"), self.build_type)

        self.optimization_level = QComboBox()
        self.optimization_level.addItems([self.tr("None"), self.tr("Basic"), self.tr("Full")])
        config_layout.addRow(self.tr("Optimization:"), self.optimization_level)

        layout.addWidget(config_group)

        # Build options
        options_group = QGroupBox(self.tr("Build Options"))
        options_layout = QFormLayout(options_group)

        self.clean_build_check = QCheckBox()
        options_layout.addRow(self.tr("Clean Build:"), self.clean_build_check)

        self.verbose_output_check = QCheckBox()
        options_layout.addRow(self.tr("Verbose Output:"), self.verbose_output_check)

        layout.addWidget(options_group)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_build)
        button_box.rejected.connect(self.reject)

        self.build_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.build_button.setText(self.tr("Build"))

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
    'ProjectSettingsDialog',
    'ExportProjectDialog',
    'BuildProjectDialog'
]

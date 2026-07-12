#!/usr/bin/env python3
"""
IDE Export Functions Module
Extracted from ide_window.py for better code organization
This module can be progressively integrated into the main IDE window
"""

from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QFileDialog
from utils.config import Config


class IDEExporters:
    """
    Handles all export operations for the IDE.
    This class contains methods extracted from PyGameMakerIDE for better organization.

    Usage (when integrated):
        self.exporters = IDEExporters(self)
        self.exporters.export_html5()
    """

    def __init__(self, ide_window):
        """
        Initialize the exporters module

        Args:
            ide_window: Reference to the main PyGameMakerIDE window
        """
        self.ide = ide_window

    def export_html5(self):
        """Export project as HTML5"""
        # Check if project is open
        if not self.ide.current_project_path:
            QMessageBox.warning(
                self.ide,
                self.ide.tr("No Project"),
                self.ide.tr("Please open or create a project first before exporting.")
            )
            return

        from export.HTML5.html5_exporter import HTML5Exporter

        output_dir = QFileDialog.getExistingDirectory(
            self.ide,
            self.ide.tr("Select Export Directory"),
            str(Path.home())
        )

        if output_dir:
            exporter = HTML5Exporter()

            # Show progress
            self.ide.update_status(self.ide.tr("Exporting to HTML5..."))

            if exporter.export(self.ide.current_project_path, Path(output_dir)):
                output_file = Path(output_dir) / f"{self.ide.current_project_data['name']}.html"

                reply = QMessageBox.question(
                    self.ide,
                    self.ide.tr("Export Successful"),
                    self.ide.tr("Game exported as HTML5!\n\n{0}\n\nOpen in browser now?").format(output_file.name),
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    import webbrowser
                    webbrowser.open(str(output_file))

                self.ide.update_status(self.ide.tr("HTML5 export complete"))
            else:
                QMessageBox.warning(
                    self.ide,
                    self.ide.tr("Export Failed"),
                    self.ide.tr("Failed to export game as HTML5. Check console for details.")
                )
                self.ide.update_status(self.ide.tr("Export failed"))

    @staticmethod
    def _open_directory(path):
        """Open a folder in the OS file manager (best effort)."""
        import platform
        import subprocess
        try:
            if platform.system() == 'Windows':
                import os
                os.startfile(str(path))  # nosec B606 - user-chosen export dir
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(path)])
            else:
                subprocess.run(['xdg-open', str(path)])
        except Exception:
            pass  # opening the folder is a convenience, never an error

    def export_kivy_project(self):
        """Export the project as a raw Kivy/buildozer source project.

        This emits the runnable Kivy game + buildozer.spec WITHOUT building
        an APK (that is export_android_apk's job) — useful for building on
        another machine or inspecting the generated code. Ported from the
        retired ExportProjectDialog._export_kivy.
        """
        if not self.ide.current_project_path:
            QMessageBox.warning(
                self.ide,
                self.ide.tr("No Project"),
                self.ide.tr("Please open or create a project first before exporting.")
            )
            return

        output_dir = QFileDialog.getExistingDirectory(
            self.ide,
            self.ide.tr("Select Export Directory"),
            str(Path.home())
        )
        if not output_dir:
            return

        from export.Kivy.project_adapter import export_with_adapter
        self.ide.update_status(self.ide.tr("Exporting Kivy project..."))
        if export_with_adapter(self.ide.project_manager, output_dir):
            reply = QMessageBox.question(
                self.ide,
                self.ide.tr("Export Successful"),
                self.ide.tr("Kivy project exported to:\n{0}\n\n"
                            "Would you like to open the export directory?").format(output_dir),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._open_directory(output_dir)
            self.ide.update_status(self.ide.tr("Kivy export complete"))
        else:
            QMessageBox.warning(
                self.ide,
                self.ide.tr("Export Failed"),
                self.ide.tr("Failed to export project. Check console for errors.")
            )
            self.ide.update_status(self.ide.tr("Export failed"))

    def export_project_zip(self):
        """Export current project as a .zip file"""
        # Get default filename
        project_name = self.ide.current_project_data.get('name', 'project')
        default_filename = f"{project_name}.zip"

        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self.ide,
            self.ide.tr("Export Project as Zip"),
            str(Path.home() / default_filename),
            self.ide.tr("Zip Files (*.zip)")
        )

        if file_path:
            zip_path = Path(file_path)

            # Show progress
            self.ide.update_status(self.ide.tr("Exporting project..."))

            # Export
            if self.ide.project_manager.export_project_as_zip(zip_path):
                QMessageBox.information(
                    self.ide,
                    self.ide.tr("Export Successful"),
                    self.ide.tr("Project exported to:\n{0}").format(zip_path)
                )
                self.ide.update_status(self.ide.tr("Project exported"))
            else:
                QMessageBox.warning(
                    self.ide,
                    self.ide.tr("Export Failed"),
                    self.ide.tr("Failed to export project as zip")
                )
                self.ide.update_status(self.ide.tr("Export failed"))

    def open_project_zip(self):
        """Open a project from a .zip file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.ide,
            self.ide.tr("Open Zip Project"),
            Config.get("last_project_directory", str(Path.home())),
            self.ide.tr("Zip Files (*.zip)")
        )

        if file_path:
            zip_path = Path(file_path)

            # Check if it's a valid project zip
            from utils.project_compression import ProjectCompressor
            if not ProjectCompressor.is_project_zip(zip_path):
                QMessageBox.warning(
                    self.ide,
                    self.ide.tr("Invalid Zip"),
                    self.ide.tr("This zip file does not contain a valid PyGameMaker project")
                )
                return

            # Show progress
            self.ide.update_status(self.ide.tr("Loading project from zip..."))

            # Load
            if self.ide.project_manager.load_project_from_zip(zip_path):
                Config.set("last_project_directory", str(zip_path.parent))
                self.ide.update_status(self.ide.tr("Project loaded from zip"))
            else:
                QMessageBox.warning(
                    self.ide,
                    self.ide.tr("Error"),
                    self.ide.tr("Failed to load project from zip")
                )
                self.ide.update_status(self.ide.tr("Failed to load"))

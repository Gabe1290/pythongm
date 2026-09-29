#!/usr/bin/env python3
"""Aseba (.aesl) export and Open Roberta Lab XML import (docs/
THYMIO_EXTENSION_PLAN.md, Stage D). ``export_aseba_code``/``import_roberta_xml``
are the File-menu action handlers moved verbatim out of
``core/ide/_export.py``/``core/ide/_assets.py`` -- ``self`` renamed to the
explicit ``ide`` parameter, same pattern ``extensions/thymio/editor``'s
``open_playground_editor`` already established (Stage C5). Generic export
infra (``ide._require_open_project()``, ``ide._ask_export_dir()``) stays in
core -- every platform exporter uses those, not just this one.
"""
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QFileDialog

from core.logger import get_logger

logger = get_logger(__name__)


def export_aseba_code(ide) -> None:
    """Export Thymio objects from the project as Aseba AESL code.

    Aseba export is synchronous and fast (it just writes text files), so it
    bypasses the progress-dialog helper used by the platform binary
    exporters and runs inline with a status update + a single completion
    dialog.
    """
    if not ide._require_open_project():
        return
    output_dir = ide._ask_export_dir('_aseba')
    if not output_dir:
        return

    from .aseba_exporter import AsebaExporter
    project_file = str(Path(ide.current_project_path) / "project.json")

    ide.update_status(ide.tr("Exporting Aseba code..."))
    try:
        success = AsebaExporter().export(project_file, output_dir)
    except Exception as e:
        logger.error(f"Aseba export failed: {e}", exc_info=True)
        QMessageBox.critical(
            ide,
            ide.tr("Aseba Export Failed"),
            ide.tr("Failed to export Aseba code:\n\n{0}").format(str(e))
        )
        ide.update_status(ide.tr("Aseba export failed"))
        return

    if not success:
        QMessageBox.warning(
            ide,
            ide.tr("Aseba Export"),
            ide.tr(
                "No Thymio objects found in this project, so no Aseba "
                "code was generated. Add a Thymio object to the project "
                "and try again."
            )
        )
        ide.update_status(ide.tr("Aseba export: nothing to export"))
        return

    ide.update_status(ide.tr("Aseba export complete"))
    result = QMessageBox.information(
        ide,
        ide.tr("Aseba Export Complete"),
        ide.tr("Aseba .aesl files written to:\n{0}\n\n"
                "Would you like to open the output folder?").format(output_dir),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if result == QMessageBox.StandardButton.Yes:
        import os
        import platform
        import subprocess
        if platform.system() == 'Windows':
            os.startfile(output_dir)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', output_dir])
        else:  # Linux
            subprocess.run(['xdg-open', output_dir])


def import_roberta_xml(ide) -> None:
    """Import an Open Roberta Lab XML program as a new project."""
    file_path, _ = QFileDialog.getOpenFileName(
        ide,
        ide.tr("Import Open Roberta XML"),
        str(Path.home()),
        ide.tr("Open Roberta XML (*.xml)")
    )

    if not file_path:
        return

    # Ask user where to save the new project
    output_dir = QFileDialog.getExistingDirectory(
        ide,
        ide.tr("Select Output Directory for Imported Project"),
        str(Path.home())
    )

    if not output_dir:
        return

    from .roberta_importer import import_roberta_detailed, RobertaImportError

    ide.update_status(ide.tr("Importing Open Roberta program..."))

    try:
        result = import_roberta_detailed(file_path, output_dir)

        # Show warnings if any
        warning_text = ""
        if result.warnings:
            warning_text = ide.tr("\n\nWarnings:\n") + "\n".join(
                f"  - {w}" for w in result.warnings[:20])

        QMessageBox.information(
            ide,
            ide.tr("Import Successful"),
            ide.tr("Project '{0}' imported successfully!\n"
                    "Events: {1}, Actions: {2}{3}").format(
                result.project_name,
                result.events_imported,
                result.actions_imported,
                warning_text)
        )
        ide.update_status(ide.tr("Roberta import complete: {0}").format(result.project_name))

        # Open the newly imported project
        project_file = Path(output_dir) / "project.json"
        if project_file.exists():
            ide.load_project(Path(output_dir))

    except RobertaImportError as exc:
        QMessageBox.warning(
            ide,
            ide.tr("Import Failed"),
            ide.tr("Failed to import Open Roberta XML:\n{0}").format(str(exc))
        )
        ide.update_status(ide.tr("Roberta import failed"))

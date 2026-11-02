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

from PySide6.QtWidgets import QMessageBox, QFileDialog, QInputDialog

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


def _in_background(fn):
    """Run ``fn()`` in a worker thread while the IDE keeps repainting; return its result, or the exception it raised."""
    from PySide6.QtCore import QEventLoop, QThread, Signal

    class Worker(QThread):
        finished_with = Signal(object)

        def run(self):
            try:
                self.finished_with.emit(fn())
            except Exception as exc:                      # handed back to the caller
                self.finished_with.emit(exc)

    box, loop, worker = {}, QEventLoop(), Worker()
    worker.finished_with.connect(lambda result: (box.update(result=result), loop.quit()))
    worker.start()
    loop.exec()
    worker.wait()
    return box.get("result")


def send_to_thymio(ide) -> None:
    """Send one Thymio object's program straight to a connected robot, with no Aseba Studio.

    Talks to the Thymio Device Manager through ``tdmclient`` (see ``device.py``): finds the robots, compiles the
    object's Aseba source on the chosen one and runs it. The project is saved first when it has unsaved changes,
    because the export reads the files on disk (the same as File -> Export Aseba)."""
    from . import device
    from .aseba_exporter import AsebaExporter

    title = ide.tr("Send to Thymio")
    if not ide._require_open_project():
        return
    if not device.tdmclient_installed():
        QMessageBox.information(
            ide, title,
            ide.tr("Talking to the robot needs the 'tdmclient' package. Install it with:\n\n"
                   "pip install --user tdmclient\n\nand try again."))
        return

    if ide.project_manager.is_dirty():
        ide.save_project()
    project_file = Path(ide.current_project_path) / "project.json"
    exporter = AsebaExporter()
    try:
        names = exporter.thymio_object_names(project_file)
    except Exception as exc:
        logger.error(f"Could not read the project for the Thymio send: {exc}", exc_info=True)
        QMessageBox.critical(ide, title, str(exc))
        return
    if not names:
        QMessageBox.warning(ide, title, ide.tr(
            "No Thymio objects found in this project. Add one (name it starting with \"thymio\") and try again."))
        return
    object_name = names[0]
    if len(names) > 1:
        object_name, ok = QInputDialog.getItem(ide, title, ide.tr("Object to send:"), names, 0, False)
        if not ok:
            return

    ide.update_status(ide.tr("Looking for a Thymio robot..."))
    if _in_background(device.ensure_device_manager) is not True:
        QMessageBox.warning(ide, title, ide.tr(
            "Could not reach the Thymio device manager. Start Thymio Suite (or thymio-device-manager) and try again."))
        ide.update_status(ide.tr("Thymio send: no device manager"))
        return
    robots = _in_background(device.list_robots)
    if isinstance(robots, Exception):
        QMessageBox.warning(ide, title, str(robots))
        return
    if not robots:
        QMessageBox.warning(ide, title, ide.tr(
            "No Thymio robot found. Check the USB cable (or the wireless dongle) and that the robot is switched on."))
        ide.update_status(ide.tr("Thymio send: no robot found"))
        return
    robot = robots[0]
    if len(robots) > 1:
        labels = [f"{r.name} ({r.status_name})" for r in robots]
        choice, ok = QInputDialog.getItem(ide, title, ide.tr("Robot:"), labels, 0, False)
        if not ok:
            return
        robot = robots[labels.index(choice)]

    try:
        source = exporter.generate_source(project_file, object_name)
    except Exception as exc:
        logger.error(f"Aseba source for {object_name} failed: {exc}", exc_info=True)
        QMessageBox.critical(ide, title, str(exc))
        return
    ide.update_status(ide.tr("Sending {0} to {1}...").format(object_name, robot.name))
    result = _in_background(lambda: device.send_program(source, node_id=robot.id))
    if isinstance(result, Exception):
        QMessageBox.warning(ide, title, str(result))
        ide.update_status(ide.tr("Thymio send failed"))
        return
    if result.ok:
        ide.update_status(ide.tr("{0} is now running on {1}.").format(object_name, robot.name))
        QMessageBox.information(ide, title, ide.tr("{0} is now running on {1}.").format(object_name, robot.name))
    elif result.stage == "lock":
        QMessageBox.warning(ide, title, ide.tr(
            "The robot is in use by another program (for example Aseba Studio). Close it there and try again."))
    else:
        QMessageBox.warning(ide, title, ide.tr("The robot did not accept the program ({0}):\n\n{1}").format(
            result.stage, result.message))
        ide.update_status(ide.tr("Thymio send failed"))


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

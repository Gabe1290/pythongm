#!/usr/bin/env python3
"""MicroPython export for micro:bit objects (Stage X).

``micropython_exporter.py`` holds the generator; ``device.py`` copies a
generated ``main.py`` onto a connected board; this module is the IDE-menu
File-menu handler (``export_microbit_code``, modeled on
``extensions/thymio/export``'s ``export_aseba_code`` -- same project-open
check, output-dir picker, try/except with a critical dialog, no-boards-
found warning, success dialog naming any warnings and offering to open
the output folder).
"""
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QInputDialog

from core.logger import get_logger

from .micropython_exporter import MicropythonExporter, export

logger = get_logger(__name__)

__all__ = ["MicropythonExporter", "export", "export_microbit_code"]


def _ask_board_version(ide):
    """O6: a per-export choice (not a per-project setting), so a
    classroom with mixed V1/V2 boards doesn't need two project copies.
    Returns "v1"/"v2", or ``None`` if the user cancelled. Compares the
    result against this same ``choices`` list (not a separately
    translated "V1" substring, which a differently-worded translation
    isn't guaranteed to start with)."""
    choices = [ide.tr("V2 (2020 or later)"), ide.tr("V1 (original, 2016-2020)")]
    choice, ok = QInputDialog.getItem(
        ide, ide.tr("micro:bit Version"),
        ide.tr("Which micro:bit do you have?"), choices, 0, False,
    )
    if not ok:
        return None
    return "v1" if choice == choices[1] else "v2"


def _warning_text(ide, export_warnings: dict) -> str:
    """The same shape Open Roberta import's warning_text uses: a short
    bulleted list, built from MicropythonExporter.export_warnings rather
    than re-reading every generated file's own trailing comment."""
    lines = []
    for obj_name, detail in sorted(export_warnings.items()):
        names = detail.get("unsupported", []) + detail.get("v1_incompatible", [])
        if names:
            lines.append(f"  - {obj_name}: " + ", ".join(names))
    if not lines:
        return ""
    return ide.tr("\n\nNot exported (unsupported or needs a V2 board):\n") + "\n".join(lines)


def export_microbit_code(ide) -> None:
    """Export micro:bit objects from the project as MicroPython code,
    one ``main.py`` per object. Offers to copy it straight onto a
    connected board afterwards when exactly one object was exported --
    with more than one, which board to target is ambiguous, so the
    files are written and the offer is skipped."""
    if not ide._require_open_project():
        return
    board_version = _ask_board_version(ide)
    if board_version is None:
        return
    output_dir = ide._ask_export_dir('_microbit')
    if not output_dir:
        return

    project_file = str(Path(ide.current_project_path) / "project.json")
    exporter = MicropythonExporter()

    ide.update_status(ide.tr("Exporting micro:bit code..."))
    try:
        success = exporter.export(project_file, output_dir, board_version)
    except Exception as e:
        logger.error(f"micro:bit export failed: {e}", exc_info=True)
        QMessageBox.critical(
            ide,
            ide.tr("micro:bit Export Failed"),
            ide.tr("Failed to export micro:bit code:\n\n{0}").format(str(e))
        )
        ide.update_status(ide.tr("micro:bit export failed"))
        return

    if not success:
        QMessageBox.warning(
            ide,
            ide.tr("micro:bit Export"),
            ide.tr(
                "No micro:bit objects found in this project, so no "
                "MicroPython code was generated. Add a micro:bit object "
                "(name it starting with \"microbit\", or set "
                "is_microbit) and try again."
            )
        )
        ide.update_status(ide.tr("micro:bit export: nothing to export"))
        return

    ide.update_status(ide.tr("micro:bit export complete"))
    warning_text = _warning_text(ide, exporter.export_warnings)

    result = QMessageBox.information(
        ide,
        ide.tr("micro:bit Export Complete"),
        ide.tr("main.py written for {0} micro:bit object(s) to:\n{1}{2}\n\n"
                "Would you like to open the output folder?").format(
            len(exporter.exported_files), output_dir, warning_text),
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

    if len(exporter.exported_files) == 1:
        _offer_copy_to_device(ide, next(iter(exporter.exported_files.values())))


def _offer_copy_to_device(ide, main_py_path) -> None:
    result = QMessageBox.question(
        ide,
        ide.tr("Copy to micro:bit?"),
        ide.tr("Copy main.py to a connected micro:bit now?\n\n"
                "The board must already be plugged in via USB and "
                "running MicroPython."),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if result != QMessageBox.StandardButton.Yes:
        return

    from .device import copy_main_py

    ide.update_status(ide.tr("Copying to micro:bit..."))
    try:
        copy_main_py(main_py_path)
    except Exception as e:
        logger.error(f"micro:bit device copy failed: {e}", exc_info=True)
        QMessageBox.critical(
            ide,
            ide.tr("Copy Failed"),
            ide.tr("Couldn't copy to the micro:bit:\n\n{0}").format(str(e))
        )
        ide.update_status(ide.tr("micro:bit copy failed"))
        return

    ide.update_status(ide.tr("Copied to micro:bit"))
    QMessageBox.information(
        ide,
        ide.tr("Copied"),
        ide.tr("main.py copied to the micro:bit. It will run automatically.")
    )

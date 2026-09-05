#!/usr/bin/env python3
"""Game export for :class:`PyGameMakerIDE`: the Export Game dialog, the
per-platform export shells (Windows exe, Linux, macOS, Android, iOS,
Aseba), the shared progress-dialog/background-thread export runner, and
Build Game / Build and Run (F7/F8).

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2, the biggest of the remaining clusters). A mixin -- ``self`` /
``self.tr()`` / siblings resolve on the concrete window. ``ExportThread``
and ``_ExportProgressDialog`` are module-level helper classes used only by
this cluster's ``_run_export_with_progress`` and move here with it.

``_unsupported_actions_note`` (used by the success-message text) lives in
``_project_actions.py``; ``_show_validation_warnings`` (used by
``export_game``) lives in ``_test_game.py`` -- both resolve via ``self.``
across the mixin chain, unaffected by this move.

Patch-target moves, all in test_build_game.py / test_export_progress_dialog.py:
``mock.patch('core.ide_window.QMessageBox')`` /
``'core.ide_window.ExportThread'`` / ``'core.ide_window.os.startfile'`` now
target ``core.ide._export.QMessageBox`` / ``core.ide._export.ExportThread``
/ ``core.ide._export.os.startfile`` -- ``os`` moved here too (it's no
longer used anywhere in ``ide_window.py``, so the module-level import was
removed there as dead-code cleanup, not just left in place; a patch
targeting ``core.ide_window.os`` now has no such attribute to find).
``from core.ide_window import _ExportProgressDialog`` in
test_export_progress_dialog.py now targets ``core.ide._export``.
"""

import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QMessageBox, QFileDialog,
)

from core.logger import get_logger
logger = get_logger(__name__)


class ExportThread(QThread):
    """Run an exporter's ``export_project`` on a background thread.

    All five platform exports (exe, linux, macOS, android, ios) drive the
    same exporter contract, so they share one thread class.
    """

    def __init__(self, exporter, project_path, output_path, settings):
        super().__init__()
        self.exporter = exporter
        self.project_path = project_path
        self.output_path = output_path
        self.settings = settings

    def run(self):
        self.exporter.export_project(
            self.project_path,
            self.output_path,
            self.settings,
        )


class _ExportProgressDialog(QDialog):
    """Modal progress dialog that refuses to close while the export thread
    is still running.

    A plain QDialog can be dismissed with Esc or the window-close button
    (default reject), which returned from exec() while the export thread
    was still building — the old code then called export_thread.wait() on
    the GUI thread with no event loop, hard-freezing the whole IDE for the
    multi-minute PyInstaller/buildozer run (audit M9/M10). Here Esc and
    close are suppressed until ``allow_close`` is set (when the export
    actually finishes); an optional ``on_escape`` callback lets a
    cancel-enabled target route Esc to its cooperative cancel.
    """

    def __init__(self, parent=None, on_escape=None):
        super().__init__(parent)
        self.allow_close = False
        self._on_escape = on_escape

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and not self.allow_close:
            if self._on_escape is not None:
                self._on_escape()
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if not self.allow_close:
            if self._on_escape is not None:
                self._on_escape()
            event.ignore()
            return
        super().closeEvent(event)

    def reject(self):
        # Esc / window-close funnel through reject(); swallow it until the
        # export has finished so exec() can't return with the thread alive.
        if not self.allow_close:
            if self._on_escape is not None:
                self._on_escape()
            return
        super().reject()


class ExportMixin:

    def export_html5(self):
        """Export project as HTML5 - delegated to exporters module"""
        self.exporters.export_html5()

    def export_kivy(self):
        """Export a raw Kivy/buildozer source project (no APK build)."""
        self.exporters.export_kivy_project()

    def export_project(self):
        """File → Export Project… (Ctrl+E): the unified export dialog.

        Historically this opened ExportProjectDialog — a SECOND export UI
        with a different, overlapping target list (and a "Mobile (APK)"
        entry that never built an APK). Both entry points now open the
        same registry-driven dialog; the old dialog's distinct targets
        (raw Kivy project, source zip) are registry entries.
        """
        self.export_game()

    def export_project_zip(self):
        """Export current project as a .zip file - delegated to exporters module"""
        self.exporters.export_project_zip()

    def export_game(self):
        """Export game - shows dialog with export options"""
        # Check if project is open
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first before exporting a game.")
            )
            return

        # Validate project and show warnings
        self._show_validation_warnings()

        # Create export options dialog
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QRadioButton

        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Export Game"))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(self.tr("<h3>Export Game</h3>")))
        layout.addWidget(QLabel(self.tr("Choose export format:")))

        # Export format options — one radio per registry target
        # (export/registry.py, the single source of truth for targets:
        # order, availability text, and which method runs the export).
        # Unavailable targets stay selectable on purpose: their exporters
        # explain what's missing (e.g. the Android WSL setup steps).
        from export.registry import EXPORT_TARGETS

        button_group = QButtonGroup(dialog)
        for index, target in enumerate(EXPORT_TARGETS):
            # Guard each probe: one probe raising must not blank the WHOLE
            # dialog and hide every export target. No probe raises today
            # (the Android/WSL one is internally try/excepted), but a future
            # probe that does would otherwise leave the user with no options.
            try:
                _available, label = target.probe()
            except Exception:
                label = target.id
            radio = QRadioButton(self.tr(label))
            if index == 0:
                radio.setChecked(True)  # html5 — available on every host
            button_group.addButton(radio, index)
            layout.addWidget(radio)

        # Export options (from the retired ExportProjectDialog, audit L9:
        # user choices must actually reach the exporters — the runner
        # shells used to hardcode this dict). Consumed by the desktop
        # exporters (include_debug → console/debug build, optimize → UPX)
        # and Android (include_debug keeps the build directory).
        from PySide6.QtWidgets import QCheckBox, QGroupBox
        options_group = QGroupBox(self.tr("Export Options"))
        options_layout = QVBoxLayout(options_group)
        include_assets_check = QCheckBox(self.tr("Include Assets"))
        include_assets_check.setChecked(True)
        optimize_check = QCheckBox(self.tr("Optimize for Release"))
        optimize_check.setChecked(True)
        include_debug_check = QCheckBox(self.tr("Include Debug Info"))
        include_debug_check.setChecked(False)
        for check in (include_assets_check, optimize_check, include_debug_check):
            options_layout.addWidget(check)
        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton(self.tr("Export"))
        export_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.Accepted:
            index = button_group.checkedId()
            if 0 <= index < len(EXPORT_TARGETS):
                # Stash the options for the runner (audit L9 lineage: the
                # checkbox states must reach the exporter settings).
                self._export_options = {
                    'include_assets': include_assets_check.isChecked(),
                    'optimize': optimize_check.isChecked(),
                    'include_debug': include_debug_check.isChecked(),
                }
                try:
                    # Dispatch via the registry's runner method name —
                    # stable ids, no translated-text or magic-number
                    # routing (M13).
                    getattr(self, EXPORT_TARGETS[index].runner)()
                finally:
                    self._export_options = None

    # ------------------------------------------------------------------
    # Platform export methods — thin shells delegating to the shared
    # _run_export_with_progress helper below. Each shell only picks the
    # exporter class, the per-target settings dict, and the user-facing
    # labels that differ between targets.
    # ------------------------------------------------------------------

    def _current_export_options(self):
        """The Export Options chosen in the export dialog, or the historical
        defaults when a runner is invoked directly (audit L9 lineage: user
        checkbox states must reach the exporter settings — the shells used
        to hardcode this dict)."""
        options = getattr(self, '_export_options', None)
        options = dict(options) if isinstance(options, dict) else {
            'include_assets': True, 'optimize': True, 'include_debug': False}
        # Language to bake authored <param>_translations into. The author's
        # language is their students' language, and the export engines cannot
        # read translation dicts themselves -- see export/message_localizer.py.
        # Module-level, not a method: several tests drive this unbound on a
        # stub object, and the language lookup has no need of `self`.
        from core.language_manager import current_language_code
        options.setdefault('language', current_language_code())
        return options

    def export_windows_exe(self):
        """Handle Windows EXE export with progress dialog."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_exe')
        if not output_dir:
            return
        from export.exe.exe_exporter import ExeExporter
        self._run_export_with_progress(
            exporter_class=ExeExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                **self._current_export_options(),
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
        )

    def export_linux_binary(self):
        """Handle Linux binary export with progress dialog."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_linux')
        if not output_dir:
            return
        from export.linux.linux_exporter import LinuxExporter
        self._run_export_with_progress(
            exporter_class=LinuxExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                **self._current_export_options(),
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
        )

    def export_macos_app(self):
        """Handle macOS .app export with progress dialog."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_macos')
        if not output_dir:
            return
        from export.macos.macos_exporter import MacOSExporter
        self._run_export_with_progress(
            exporter_class=MacOSExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                **self._current_export_options(),
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
        )

    def export_android_apk(self):
        """Handle Android APK export with progress dialog (Cancel supported)."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_android')
        if not output_dir:
            return
        from export.android.android_exporter import AndroidExporter
        self._run_export_with_progress(
            exporter_class=AndroidExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                **self._current_export_options(),
            },
            dialog_title=self.tr("Exporting Game"),
            status_text=self.tr("Preparing export..."),
            dialog_size=(500, 150),
            success_title=self.tr("Export Complete"),
            failure_title=self.tr("Export Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=True,
            cancel_status_message=self.tr("Export cancelled"),
        )

    def export_ios_app(self):
        """Handle iOS IPA export with progress dialog (macOS + free Apple ID)."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_ios')
        if not output_dir:
            return
        from export.ios.ios_exporter import iOSExporter
        # iOS deliberately omits 'optimize' from the settings dict — the
        # iOSExporter does not currently consume it. Preserve this so the
        # exporter sees the same payload shape as before consolidation.
        ios_options = self._current_export_options()
        ios_options.pop('optimize', None)
        self._run_export_with_progress(
            exporter_class=iOSExporter,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                **ios_options,
            },
            dialog_title=self.tr("Building iOS App"),
            status_text=self.tr("Preparing iOS export..."),
            dialog_size=(520, 160),
            success_title=self.tr("iOS Export Complete"),
            failure_title=self.tr("iOS Export Failed"),
            open_folder_prompt=self.tr("Open the output folder?"),
            show_cancel=True,
            cancel_status_message=self.tr("iOS export cancelled"),
        )

    def export_aseba_code(self):
        """Export Thymio objects from the project as Aseba AESL code.

        Aseba export is synchronous and fast (it just writes text files),
        so it bypasses the progress-dialog helper used by the platform
        binary exporters and runs inline with a status update + a single
        completion dialog.
        """
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_aseba')
        if not output_dir:
            return

        from export.Aseba.aseba_exporter import AsebaExporter
        project_file = str(Path(self.current_project_path) / "project.json")

        self.update_status(self.tr("Exporting Aseba code..."))
        try:
            success = AsebaExporter().export(project_file, output_dir)
        except Exception as e:
            logger.error(f"Aseba export failed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Aseba Export Failed"),
                self.tr("Failed to export Aseba code:\n\n{0}").format(str(e))
            )
            self.update_status(self.tr("Aseba export failed"))
            return

        if not success:
            QMessageBox.warning(
                self,
                self.tr("Aseba Export"),
                self.tr(
                    "No Thymio objects found in this project, so no Aseba "
                    "code was generated. Add a Thymio object to the project "
                    "and try again."
                )
            )
            self.update_status(self.tr("Aseba export: nothing to export"))
            return

        self.update_status(self.tr("Aseba export complete"))
        result = QMessageBox.information(
            self,
            self.tr("Aseba Export Complete"),
            self.tr("Aseba .aesl files written to:\n{0}\n\n"
                    "Would you like to open the output folder?").format(output_dir),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            import platform
            if platform.system() == 'Windows':
                os.startfile(output_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', output_dir])

    def build_game(self):
        """Build → Build Game... (F7): build a native desktop artifact for
        the current host, without going through the multi-target Export
        Game dialog. Uses the same PyInstaller-based exporter class the
        dialog's own platform entries pick via
        export.registry.desktop_exporter_for_host (Windows exe, macOS
        .app, or Linux ELF binary, chosen by host OS since PyInstaller
        can't cross-compile)."""
        self._build_desktop(run_after=False)

    def build_and_run(self):
        """Build → Build and Run (F8): same build as build_game, then
        launch the resulting executable."""
        self._build_desktop(run_after=True)

    # ------------------------------------------------------------------
    # Helpers backing the shells above.
    # ------------------------------------------------------------------

    def _require_open_project(self) -> bool:
        """Show the standard "no project" warning and return False when
        no project is currently open. Centralises the guard that all five
        platform-export methods used to inline.
        """
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first.")
            )
            return False
        return True

    def _ask_export_dir(self, suffix: str) -> str:
        """Prompt the user for an output directory, defaulting to
        ``<localised-Desktop>/<sanitised-project-name><suffix>``.
        Returns the absolute path string or "" if cancelled.

        Uses ``utils.desktop_dir()`` instead of ``Path.home() / "Desktop"``
        so the default works on Linux locales whose desktop is "Bureau",
        "Schreibtisch", etc., and on Windows where the desktop may be
        OneDrive-redirected.
        """
        from utils import desktop_dir
        default_name = self.current_project_data.get('name', 'Game').replace(' ', '_')
        return QFileDialog.getExistingDirectory(
            self,
            self.tr("Choose Export Location"),
            str(desktop_dir() / f"{default_name}{suffix}"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

    def _run_export_with_progress(
        self,
        *,
        exporter_class,
        output_dir: str,
        export_settings: dict,
        dialog_title: str,
        status_text: str,
        dialog_size: tuple,
        success_title: str,
        failure_title: str,
        open_folder_prompt: str,
        show_cancel: bool = False,
        cancel_status_message: str = "",
        on_success=None,
    ):
        """Drive an exporter to completion behind a modal progress dialog.

        Centralises the construction of the progress UI and the
        success/failure/cancel handlers that all five platform export
        methods previously inlined. Behaviour is identical to those
        per-method implementations; the only variation between targets
        is encoded in this function's keyword arguments.

        Note: ``exporter_class`` is a *class* (not an instance) so the
        helper can instantiate it AFTER the progress dialog is built,
        matching the construction order of the original per-method
        implementations. Caller-side ``ExporterClass()`` would invert
        the order because keyword arguments are evaluated before the
        call.

        ``on_success``, if given, is called (no args) after a successful
        build, regardless of whether the user answered the "open output
        folder?" prompt — used by ``build_and_run`` (F8) to launch the
        freshly-built executable without duplicating the whole
        progress-dialog/thread machinery.
        """
        # cancel_export is defined below; route Esc/close to it for
        # cancel-enabled targets so the dialog can't be dismissed in a way
        # that strands the running thread (audit M9/M10).
        _on_escape_ref = {"fn": None}
        progress_dialog = _ExportProgressDialog(
            self, on_escape=lambda: _on_escape_ref["fn"] and _on_escape_ref["fn"]()
        )
        progress_dialog.setWindowTitle(dialog_title)
        progress_dialog.setModal(True)
        progress_dialog.resize(*dialog_size)

        layout = QVBoxLayout(progress_dialog)

        status_label = QLabel(status_text)
        layout.addWidget(status_label)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        layout.addWidget(progress_bar)

        cancel_btn = None
        if show_cancel:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            cancel_btn = QPushButton(self.tr("Cancel"))
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

        # Construct the exporter AFTER the dialog widgets, to preserve
        # the construction order observable by code review tooling.
        exporter = exporter_class()
        _export_cancelled = False

        def update_progress(percent, message):
            progress_bar.setValue(percent)
            status_label.setText(message)

        def export_finished(success, message):
            # The thread has signalled completion — now the dialog may close.
            progress_dialog.allow_close = True
            progress_dialog.accept()
            if show_cancel and _export_cancelled:
                self.update_status(cancel_status_message)
                return
            if success:
                result = QMessageBox.information(
                    self,
                    success_title,
                    message + self._unsupported_actions_note() + "\n\n" + open_folder_prompt,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if result == QMessageBox.StandardButton.Yes:
                    import os
                    import platform
                    if platform.system() == 'Windows':
                        os.startfile(output_dir)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_dir])
                    else:  # Linux
                        subprocess.run(['xdg-open', output_dir])
                if on_success is not None:
                    on_success()
            else:
                QMessageBox.critical(self, failure_title, message)

        def cancel_export():
            nonlocal _export_cancelled
            if _export_cancelled:
                return
            _export_cancelled = True
            if cancel_btn is not None:
                cancel_btn.setEnabled(False)
            status_label.setText(self.tr("Cancelling..."))
            exporter.cancel_requested = True

        # Only cancel-enabled targets route Esc to a cooperative cancel; for
        # targets without a Cancel button Esc is simply swallowed (the build
        # keeps running behind the still-open, still-painting dialog).
        if show_cancel:
            _on_escape_ref["fn"] = cancel_export

        exporter.progress_update.connect(update_progress)
        exporter.export_complete.connect(export_finished)
        if show_cancel and cancel_btn is not None:
            cancel_btn.clicked.connect(cancel_export)

        export_thread = ExportThread(
            exporter,
            str(self.current_project_path),
            output_dir,
            export_settings
        )

        # Safety net: if the thread ends without export_complete ever firing
        # (e.g. the exporter raised), still release the dialog so exec() can
        # return — otherwise the modal would stay open forever.
        def _on_thread_finished():
            if not progress_dialog.allow_close:
                progress_dialog.allow_close = True
                progress_dialog.accept()
        export_thread.finished.connect(_on_thread_finished)

        export_thread.start()
        progress_dialog.exec()
        # exec() only returns once the export has finished (Esc/close are
        # suppressed until allow_close), so this wait() is now effectively
        # instant rather than the multi-minute GUI-thread freeze of the old
        # early-dismiss path (audit M9/M10). It also joins the thread cleanly.
        export_thread.wait()

    def _build_desktop(self, run_after: bool):
        """Shared body of build_game/build_and_run: build via the
        host-appropriate desktop exporter, optionally launching the result
        afterward."""
        if not self._require_open_project():
            return
        output_dir = self._ask_export_dir('_build')
        if not output_dir:
            return
        import platform
        from export.registry import desktop_exporter_for_host
        exporter_class = desktop_exporter_for_host(platform.system())
        self._run_export_with_progress(
            exporter_class=exporter_class,
            output_dir=output_dir,
            export_settings={
                'output_path': output_dir,
                **self._current_export_options(),
            },
            dialog_title=self.tr("Building Game"),
            status_text=self.tr("Preparing build..."),
            dialog_size=(500, 150),
            success_title=self.tr("Build Complete"),
            failure_title=self.tr("Build Failed"),
            open_folder_prompt=self.tr("Would you like to open the output folder?"),
            show_cancel=False,
            on_success=(lambda: self._launch_built_game(output_dir)) if run_after else None,
        )

    def _launch_built_game(self, output_dir: str):
        """Locate and launch the executable build_and_run just produced in
        output_dir. Mirrors the exporters' own naming convention exactly
        (export/{exe,linux,macos}_exporter.py's _create_spec_file: the
        project name run through the same
        re.sub(r'[^A-Za-z0-9_]', '_', name) sanitizer, suffixed .exe / no
        suffix / .app for Windows/Linux/macOS respectively) rather than
        scanning output_dir, since PyInstaller's onefile dist/ can contain
        incidental extra files (e.g. debug builds)."""
        import platform
        import re
        import subprocess as _subprocess

        raw_name = (self.current_project_data or {}).get('name', 'Game')
        game_name = re.sub(r'[^A-Za-z0-9_]', '_', raw_name) or 'Game'
        system = platform.system()
        output_path = Path(output_dir)

        try:
            if system == 'Windows':
                exe_path = output_path / f"{game_name}.exe"
                if exe_path.exists():
                    os.startfile(str(exe_path))
                else:
                    logger.warning(f"Build and Run: {exe_path} not found")
            elif system == 'Darwin':
                app_path = output_path / f"{game_name}.app"
                if app_path.exists():
                    _subprocess.Popen(['open', str(app_path)])
                else:
                    logger.warning(f"Build and Run: {app_path} not found")
            else:
                bin_path = output_path / game_name
                if bin_path.exists():
                    _subprocess.Popen([str(bin_path)])
                else:
                    logger.warning(f"Build and Run: {bin_path} not found")
        except Exception:
            logger.warning("Build and Run: failed to launch the built game", exc_info=True)
